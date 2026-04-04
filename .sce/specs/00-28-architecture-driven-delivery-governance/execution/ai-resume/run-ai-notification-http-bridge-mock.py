import argparse
import json
import signal
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request


SAMPLE_ROOT = Path(__file__).resolve().parent / "samples"


def sanitize_label(label: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in label.strip())
    collapsed = "-".join(part for part in normalized.split("-") if part)
    return collapsed or "ai-notification-http-bridge-mock"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


class BridgeMockState:
    def __init__(self, output_dir: Path, auth_header: str, auth_token: str, message_prefix: str, max_requests: int | None) -> None:
        self.output_dir = output_dir
        self.auth_header = auth_header
        self.auth_token = auth_token
        self.message_prefix = message_prefix
        self.max_requests = max_requests
        self.lock = threading.Lock()
        self.request_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.callback_success_count = 0
        self.callback_failure_count = 0
        self.started_at = datetime.now().astimezone().isoformat()
        self.events_path = output_dir / "requests.jsonl"
        self.summary_json_path = output_dir / "summary.json"
        self.summary_md_path = output_dir / "summary.md"

    def next_request_id(self) -> int:
        with self.lock:
            self.request_count += 1
            return self.request_count

    def record_event(self, event: dict) -> None:
        with self.lock:
            if event.get("response", {}).get("success"):
                self.success_count += 1
            else:
                self.failure_count += 1
            with self.events_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def record_callback_result(self, success: bool) -> None:
        with self.lock:
            if success:
                self.callback_success_count += 1
            else:
                self.callback_failure_count += 1

    def build_summary(self) -> dict:
        return {
            "outputDir": str(self.output_dir),
            "startedAt": self.started_at,
            "generatedAt": datetime.now().astimezone().isoformat(),
            "requestCount": self.request_count,
            "successCount": self.success_count,
            "failureCount": self.failure_count,
            "callbackSuccessCount": self.callback_success_count,
            "callbackFailureCount": self.callback_failure_count,
            "authHeader": self.auth_header,
            "authTokenConfigured": bool(self.auth_token),
            "messagePrefix": self.message_prefix,
            "maxRequests": self.max_requests,
        }

    def write_summary(self) -> None:
        summary = self.build_summary()
        self.summary_json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        lines = [
            "# AI Notification HTTP Bridge Mock Summary",
            "",
            f"- Started At: `{summary['startedAt']}`",
            f"- Generated At: `{summary['generatedAt']}`",
            f"- Request Count: `{summary['requestCount']}`",
            f"- Success Count: `{summary['successCount']}`",
            f"- Failure Count: `{summary['failureCount']}`",
            f"- Callback Success Count: `{summary['callbackSuccessCount']}`",
            f"- Callback Failure Count: `{summary['callbackFailureCount']}`",
            f"- Auth Header: `{summary['authHeader'] or '--'}`",
            f"- Auth Token Configured: `{'yes' if summary['authTokenConfigured'] else 'no'}`",
            f"- Message Prefix: `{summary['messagePrefix']}`",
            f"- Max Requests: `{summary['maxRequests'] if summary['maxRequests'] is not None else '--'}`",
            "",
            "## Artifacts",
            "",
            "- `requests.jsonl`",
            "- `summary.json`",
        ]
        self.summary_md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def resolve_channel_code(payload: dict | None) -> str:
    recipient = payload.get("recipient") if isinstance(payload, dict) else None
    if isinstance(recipient, dict):
        phone = str(recipient.get("phone") or "").strip()
        email = str(recipient.get("email") or "").strip()
        if phone:
            return "sms"
        if email:
            return "email"
    return "http"


def resolve_force_status(headers, payload: dict | None) -> str | None:
    header_value = str(headers.get("X-Mock-Force-Status") or "").strip().lower()
    if header_value in {"send_failed", "sent"}:
        return header_value
    if isinstance(payload, dict):
        direct_value = str(payload.get("mockSendStatus") or "").strip().lower()
        if direct_value in {"send_failed", "sent"}:
            return direct_value
        reason = str(payload.get("reason") or "").lower()
        failure = payload.get("failure") or {}
        instruction = str(failure.get("instruction") or "").lower() if isinstance(failure, dict) else ""
        if "[mock-http-send-failed]" in reason or "[mock-http-send-failed]" in instruction:
            return "send_failed"
    return None


def maybe_send_callback(state: BridgeMockState, payload: dict | None, response: dict) -> None:
    if not isinstance(payload, dict):
        return
    callback_url = str(payload.get("callbackUrl") or "").strip()
    callback_header = str(payload.get("callbackHeader") or "").strip()
    callback_token = str(payload.get("callbackToken") or "").strip()
    if not callback_url or not callback_header or not callback_token:
        return

    failure = payload.get("failure") or {}
    callback_payload = {
        "requestId": str(payload.get("requestId") or "").strip(),
        "providerCode": "http",
        "providerMessageId": str(response.get("providerMessageId") or "").strip(),
        "failureId": str(failure.get("failureId") or "").strip(),
        "receiptStatus": "delivered",
        "receiptAt": datetime.now().isoformat(timespec="seconds"),
        "receiptPayload": {
            "mockBridge": True,
            "providerMessageId": str(response.get("providerMessageId") or "").strip(),
            "requestId": str(payload.get("requestId") or "").strip(),
            "receiptStatus": "delivered",
        },
    }
    body = json.dumps(callback_payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        callback_url,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            callback_header: callback_token,
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=10) as resp:
            callback_ok = 200 <= getattr(resp, "status", 200) < 300
    except (error.URLError, ValueError):
        callback_ok = False
    state.record_callback_result(callback_ok)


def build_handler(state: BridgeMockState):
    class Handler(BaseHTTPRequestHandler):
        server_version = "AiNotificationHttpBridgeMock/1.0"

        def do_POST(self) -> None:
            request_no = state.next_request_id()
            content_length = int(self.headers.get("Content-Length") or "0")
            raw_body = self.rfile.read(content_length) if content_length > 0 else b""
            body_text = raw_body.decode("utf-8", errors="replace")
            parsed_body = None
            if body_text:
                try:
                    parsed_body = json.loads(body_text)
                except json.JSONDecodeError:
                    parsed_body = None

            auth_ok = True
            auth_value = self.headers.get(state.auth_header) if state.auth_header else None
            if state.auth_token:
                auth_ok = auth_value == state.auth_token

            force_status = resolve_force_status(self.headers, parsed_body)
            channel_code = resolve_channel_code(parsed_body)
            provider_message_id = f"{state.message_prefix}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{request_no:04d}"
            if not auth_ok:
                status_code = 401
                response = {
                    "success": False,
                    "providerCode": "http",
                    "sendStatus": "send_failed",
                    "failureReason": "mock_http_auth_failed",
                }
            elif force_status == "send_failed":
                status_code = 200
                response = {
                    "success": False,
                    "providerCode": "http",
                    "channelCode": channel_code,
                    "providerMessageId": provider_message_id,
                    "sendStatus": "send_failed",
                    "failureReason": "mock_http_send_failed",
                }
            else:
                status_code = 200
                response = {
                    "success": True,
                    "providerCode": "http",
                    "channelCode": channel_code,
                    "providerMessageId": provider_message_id,
                    "sendStatus": "sent",
                }

            event = {
                "capturedAt": datetime.now().astimezone().isoformat(),
                "requestNo": request_no,
                "path": self.path,
                "method": self.command,
                "headers": dict(self.headers.items()),
                "authOk": auth_ok,
                "forceStatus": force_status,
                "requestJson": parsed_body,
                "requestText": body_text,
                "response": response,
                "statusCode": status_code,
            }
            state.record_event(event)
            if status_code == 200 and response.get("success"):
                maybe_send_callback(state, parsed_body, response)

            payload = json.dumps(response, ensure_ascii=False).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

            if state.max_requests is not None and state.request_count >= state.max_requests:
                threading.Thread(target=self.server.shutdown, daemon=True).start()

        def log_message(self, format: str, *args) -> None:
            return

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a mock HTTP bridge provider for AI notification validation.")
    parser.add_argument("--label", default="ai-notification-http-bridge-mock")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=19081)
    parser.add_argument("--auth-header", default="Authorization")
    parser.add_argument("--auth-token", default="")
    parser.add_argument("--message-prefix", default="mock-http")
    parser.add_argument("--max-requests", type=int)
    args = parser.parse_args()

    capture_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{sanitize_label(args.label)}"
    output_dir = SAMPLE_ROOT / capture_id
    ensure_dir(output_dir)
    state = BridgeMockState(
        output_dir=output_dir,
        auth_header=args.auth_header.strip(),
        auth_token=args.auth_token.strip(),
        message_prefix=args.message_prefix.strip() or "mock-http",
        max_requests=args.max_requests if args.max_requests and args.max_requests > 0 else None,
    )

    server = ThreadingHTTPServer((args.host, args.port), build_handler(state))

    def shutdown_handler(*_args) -> None:
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    print(
        json.dumps(
            {
                "capture_id": capture_id,
                "output_dir": str(output_dir),
                "listen_url": f"http://{args.host}:{args.port}",
                "auth_header": state.auth_header,
                "auth_token_configured": bool(state.auth_token),
                "max_requests": state.max_requests,
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    try:
        server.serve_forever()
    finally:
        state.write_summary()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
