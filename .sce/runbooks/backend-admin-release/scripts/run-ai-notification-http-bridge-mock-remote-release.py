import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"
BRIDGE_SCRIPT = (
    ROOT
    / ".sce"
    / "specs"
    / "00-28-architecture-driven-delivery-governance"
    / "execution"
    / "ai-resume"
    / "run-ai-notification-http-bridge-mock.py"
)
LOCAL_BRIDGE_SECRET_FILE = ROOT / ".sce" / "config" / "local-secrets" / "ai-notification-http-bridge.env"

DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_OPERATOR = "codex"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
DEFAULT_REMOTE_ROOT = f"/home/{DEFAULT_USER}/ai-notification-http-bridge"
DEFAULT_BIND_HOST = "0.0.0.0"
DEFAULT_BIND_PORT = 19081
DEFAULT_AUTH_HEADER = "Authorization"
DEFAULT_CALLBACK_BASE_URL = "http://101.43.57.62/api"
DEFAULT_CALLBACK_PATH = "/internal/ai/resume/notification-receipts/provider"


@dataclass
class RemoteBridgeContext:
    release_id: str
    host: str
    user: str
    operator: str
    identity_file: Path
    remote_root: str
    bind_host: str
    bind_port: int
    auth_header: str
    auth_token: str
    public_base_url: str
    sync_local_secret: bool
    dry_run: bool

    @property
    def public_endpoint(self) -> str:
        return f"{self.public_base_url.rstrip('/')}:{self.bind_port}/"

    @property
    def release_root(self) -> str:
        return f"{self.remote_root}/releases/{self.release_id}"

    @property
    def current_root(self) -> str:
        return f"{self.remote_root}/current"

    @property
    def remote_script_path(self) -> str:
        return f"{self.release_root}/run-ai-notification-http-bridge-mock.py"

    @property
    def remote_log_path(self) -> str:
        return f"{self.release_root}/bridge.log"

    @property
    def remote_pid_path(self) -> str:
        return f"{self.current_root}/bridge.pid"

    @property
    def remote_current_script_path(self) -> str:
        return f"{self.current_root}/run-ai-notification-http-bridge-mock.py"


def log(message: str) -> None:
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    print(f"[{timestamp}] {message}", flush=True)


def resolve_executable(name: str) -> str:
    if os.name == "nt":
        resolved = shutil.which(f"{name}.exe") or shutil.which(f"{name}.cmd") or shutil.which(name)
    else:
        resolved = shutil.which(name)
    if not resolved:
        raise RuntimeError(f"required executable not found: {name}")
    return resolved


def run_process(command: list[str], *, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    log(f"local> {' '.join(command)}")
    return subprocess.run(
        command,
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
    )


def ssh_base(context: RemoteBridgeContext) -> list[str]:
    ssh = resolve_executable("ssh")
    return [
        ssh,
        "-i",
        str(context.identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{context.user}@{context.host}",
    ]


def scp_base(context: RemoteBridgeContext) -> list[str]:
    scp = resolve_executable("scp")
    return [
        scp,
        "-i",
        str(context.identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]


def run_ssh(context: RemoteBridgeContext, remote_command: str) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(context) + [remote_command], capture_output=True)


def require_key_auth(context: RemoteBridgeContext) -> None:
    result = run_ssh(context, "printf 'key-auth-ok'")
    if result.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe returned unexpected output")
    log("native ssh key auth verified")


def remote_bash(context: RemoteBridgeContext, script: str) -> str:
    escaped = script.replace("'", "'\"'\"'")
    result = run_ssh(context, f"bash -lc '{escaped}'")
    if result.stderr and result.stderr.strip():
        log(f"remote stderr> {result.stderr.strip()}")
    return result.stdout.strip()


def upload_bridge_script(context: RemoteBridgeContext) -> None:
    remote_target = f"{context.user}@{context.host}:{context.remote_script_path}"
    run_process(scp_base(context) + [str(BRIDGE_SCRIPT), remote_target])
    remote_bash(
        context,
        (
            f"mkdir -p {shlex_quote(context.release_root)} {shlex_quote(context.current_root)} && "
            f"chmod 755 {shlex_quote(context.release_root)} {shlex_quote(context.current_root)} && "
            f"cp {shlex_quote(context.remote_script_path)} {shlex_quote(context.remote_current_script_path)}"
        ),
    )


def shlex_quote(value: str) -> str:
    import shlex

    return shlex.quote(value)


def stop_existing_bridge(context: RemoteBridgeContext) -> str:
    script = f"""
if [ -f {shlex_quote(context.remote_pid_path)} ]; then
  pid="$(cat {shlex_quote(context.remote_pid_path)} 2>/dev/null || true)"
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    sleep 1
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" 2>/dev/null || true
    fi
    echo "stopped:$pid"
  else
    echo "stale-pid"
  fi
  rm -f {shlex_quote(context.remote_pid_path)}
else
  echo "not-running"
fi
"""
    return remote_bash(context, script)


def start_bridge(context: RemoteBridgeContext) -> str:
    auth_args = ""
    if context.auth_header:
        auth_args += f" --auth-header {shlex_quote(context.auth_header)}"
    if context.auth_token:
        auth_args += f" --auth-token {shlex_quote(context.auth_token)}"
    script = f"""
mkdir -p {shlex_quote(context.release_root)} {shlex_quote(context.current_root)}
nohup python3 {shlex_quote(context.remote_current_script_path)} --label {shlex_quote(context.release_id)} --host {shlex_quote(context.bind_host)} --port {context.bind_port}{auth_args} > {shlex_quote(context.remote_log_path)} 2>&1 < /dev/null &
pid=$!
echo "$pid" > {shlex_quote(context.remote_pid_path)}
sleep 2
if ! kill -0 "$pid" 2>/dev/null; then
  echo "failed"
  exit 1
fi
echo "$pid"
"""
    return remote_bash(context, script)


def remote_probe(context: RemoteBridgeContext) -> dict[str, object]:
    auth_header_line = ""
    if context.auth_token:
        auth_header_line = f"-H {shlex_quote(f'{context.auth_header}: {context.auth_token}')} "
    remote_url = f"http://127.0.0.1:{context.bind_port}/"
    payload = json.dumps(
        {
            "requestId": f"{context.release_id}-remote-probe",
            "reason": "remote bridge smoke",
            "failure": {"failureId": "remote-probe-failure", "instruction": "remote bridge smoke"},
            "recipient": {"name": "mock user", "phone": "13800138000", "email": ""},
        },
        ensure_ascii=False,
    )
    script = f"""
status="$(curl -sS -o /tmp/{context.release_id}-remote-probe.json -w '%{{http_code}}' -X POST {auth_header_line}-H 'Content-Type: application/json' --data {shlex_quote(payload)} {shlex_quote(remote_url)})"
echo "status=$status"
cat /tmp/{context.release_id}-remote-probe.json
rm -f /tmp/{context.release_id}-remote-probe.json
"""
    output = remote_bash(context, script)
    lines = output.splitlines()
    status_line = next((line for line in lines if line.startswith("status=")), "status=000")
    status_code = int(status_line.split("=", 1)[1])
    response_text = "\n".join(line for line in lines if not line.startswith("status=")).strip()
    response_json = json.loads(response_text) if response_text else {}
    return {"status": status_code, "responseText": response_text, "responseJson": response_json}


def public_probe(context: RemoteBridgeContext) -> dict[str, object]:
    payload = json.dumps(
        {
            "requestId": f"{context.release_id}-public-probe",
            "reason": "public bridge smoke",
            "failure": {"failureId": "public-probe-failure", "instruction": "public bridge smoke"},
            "recipient": {"name": "mock user", "phone": "13800138000", "email": ""},
        },
        ensure_ascii=False,
    )
    auth_headers = {}
    if context.auth_token:
        auth_headers[context.auth_header] = context.auth_token

    command = [
        sys.executable,
        "-c",
        (
            "import json, sys, urllib.request;"
            "url=sys.argv[1];"
            "payload=sys.argv[2].encode('utf-8');"
            "headers=json.loads(sys.argv[3]);"
            "req=urllib.request.Request(url,data=payload,headers={**headers,'Content-Type':'application/json'},method='POST');"
            "resp=urllib.request.urlopen(req,timeout=15);"
            "print(json.dumps({'status':resp.status,'body':resp.read().decode('utf-8','replace')}))"
        ),
        context.public_endpoint,
        payload,
        json.dumps(auth_headers, ensure_ascii=False),
    ]
    result = run_process(command, capture_output=True)
    parsed = json.loads(result.stdout.strip())
    body_text = str(parsed.get("body") or "")
    return {
        "status": int(parsed.get("status") or 0),
        "responseText": body_text,
        "responseJson": json.loads(body_text) if body_text else {},
    }


def read_remote_log_tail(context: RemoteBridgeContext) -> str:
    return remote_bash(context, f"tail -n 80 {shlex_quote(context.remote_log_path)} || true")


def sync_local_secret(context: RemoteBridgeContext) -> Path:
    secret_path = LOCAL_BRIDGE_SECRET_FILE
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    if not secret_path.exists():
        secret_path.write_text(
            (
                "# Local AI notification HTTP bridge rollout inputs\n"
                "AI_NOTIFICATION_HTTP_BRIDGE_EXPECTED_PROVIDER_CODE=http\n"
                "AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT=\n"
                f"AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_BASE_URL={DEFAULT_CALLBACK_BASE_URL}\n"
                f"AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_PATH={DEFAULT_CALLBACK_PATH}\n"
                f"AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER={DEFAULT_AUTH_HEADER}\n"
                "AI_NOTIFICATION_HTTP_BRIDGE_AUTH_TOKEN=\n"
            ),
            encoding="utf-8",
        )

    text = secret_path.read_text(encoding="utf-8-sig")
    replacements = {
        "AI_NOTIFICATION_HTTP_BRIDGE_EXPECTED_PROVIDER_CODE": "http",
        "AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT": context.public_endpoint,
        "AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_BASE_URL": DEFAULT_CALLBACK_BASE_URL,
        "AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_PATH": DEFAULT_CALLBACK_PATH,
        "AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER": context.auth_header or DEFAULT_AUTH_HEADER,
        "AI_NOTIFICATION_HTTP_BRIDGE_AUTH_TOKEN": context.auth_token,
    }
    for key, value in replacements.items():
        pattern = re.compile(rf"(?m)^{re.escape(key)}=.*$")
        line = f"{key}={value}"
        if pattern.search(text):
            text = pattern.sub(line, text)
        else:
            if not text.endswith("\n"):
                text += "\n"
            text += line + "\n"
    secret_path.write_text(text, encoding="utf-8")
    return secret_path


def write_record(
    *,
    context: RemoteBridgeContext,
    stop_result: str,
    remote_pid: str | None,
    remote_probe_result: dict[str, object] | None,
    public_probe_result: dict[str, object] | None,
    log_tail: str,
    local_secret_path: Path | None,
    final_status: str,
    stop_reason: str,
) -> Path:
    record_path = RECORDS_DIR / f"{context.release_id}.md"
    if record_path.exists():
        raise RuntimeError(f"record already exists: {record_path}")

    lines = [
        "# AI 通知 HTTP Bridge Mock 远端发布记录",
        "",
        "## 1. 基本信息",
        "",
        f"- 发布批次号：`{context.release_id}`",
        f"- 执行时间：`{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`",
        f"- 操作人：`{context.operator}`",
        f"- 目标主机：`{context.host}`",
        f"- dry-run：`{'是' if context.dry_run else '否'}`",
        f"- 最终状态：`{final_status}`",
        f"- 中止/结束原因：`{stop_reason}`",
        "",
        "## 2. 远端进程",
        "",
        f"- 远端目录：`{context.release_root}`",
        f"- 当前脚本：`{context.remote_current_script_path}`",
        f"- 日志：`{context.remote_log_path}`",
        f"- PID 文件：`{context.remote_pid_path}`",
        f"- 启动前旧进程处理：`{stop_result}`",
        f"- 当前 PID：`{remote_pid or '--'}`",
        f"- 绑定地址：`http://{context.bind_host}:{context.bind_port}/`",
        f"- 公网地址：`{context.public_endpoint}`",
    ]

    lines.extend(["", "## 3. 探活结果", ""])
    if remote_probe_result:
        lines.append(f"- 远端本机探活：`HTTP {remote_probe_result.get('status')}`")
        lines.append(f"- 远端本机回包：`{remote_probe_result.get('responseText') or '--'}`")
    if public_probe_result:
        lines.append(f"- 公网探活：`HTTP {public_probe_result.get('status')}`")
        lines.append(f"- 公网回包：`{public_probe_result.get('responseText') or '--'}`")

    lines.extend(["", "## 4. 日志尾部", "", "```text", log_tail or "--", "```"])

    lines.extend(["", "## 5. 本地 bridge secret", ""])
    lines.append(f"- 已回写：`{'是' if local_secret_path else '否'}`")
    if local_secret_path:
        lines.append(f"- 文件：`{local_secret_path}`")

    record_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return record_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Release the AI notification HTTP bridge mock to the remote target host.")
    parser.add_argument("--label", required=True)
    parser.add_argument("--operator", default=DEFAULT_OPERATOR)
    parser.add_argument("--host", default=os.getenv("KAIPAI_RELEASE_HOST", DEFAULT_HOST))
    parser.add_argument("--user", default=os.getenv("KAIPAI_RELEASE_USER", DEFAULT_USER))
    parser.add_argument("--identity-file", default=os.getenv("KAIPAI_RELEASE_IDENTITY_FILE", str(DEFAULT_IDENTITY_FILE)))
    parser.add_argument("--remote-root", default=DEFAULT_REMOTE_ROOT)
    parser.add_argument("--bind-host", default=DEFAULT_BIND_HOST)
    parser.add_argument("--bind-port", type=int, default=DEFAULT_BIND_PORT)
    parser.add_argument("--auth-header", default=DEFAULT_AUTH_HEADER)
    parser.add_argument("--auth-token", default="")
    parser.add_argument("--public-base-url", default=f"http://{DEFAULT_HOST}")
    parser.add_argument("--sync-local-secret", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    release_id = f"{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}-ai-notification-http-bridge-remote-{args.label}"
    context = RemoteBridgeContext(
        release_id=release_id,
        host=args.host,
        user=args.user,
        operator=args.operator,
        identity_file=Path(args.identity_file),
        remote_root=args.remote_root,
        bind_host=args.bind_host,
        bind_port=args.bind_port,
        auth_header=args.auth_header.strip() or DEFAULT_AUTH_HEADER,
        auth_token=args.auth_token.strip(),
        public_base_url=args.public_base_url.strip() or f"http://{args.host}",
        sync_local_secret=args.sync_local_secret,
        dry_run=args.dry_run,
    )

    if not context.identity_file.exists():
        raise RuntimeError(f"identity file not found: {context.identity_file}")
    if not BRIDGE_SCRIPT.exists():
        raise RuntimeError(f"bridge script not found: {BRIDGE_SCRIPT}")

    require_key_auth(context)
    if context.dry_run:
        record_path = write_record(
            context=context,
            stop_result="not-executed",
            remote_pid=None,
            remote_probe_result=None,
            public_probe_result=None,
            log_tail="dry-run: no remote process started",
            local_secret_path=None,
            final_status="dry-run-completed",
            stop_reason="dry_run_finished",
        )
        print(json.dumps({"release_id": context.release_id, "status": "dry-run-completed", "record_path": str(record_path)}, ensure_ascii=False, indent=2))
        return 0

    remote_bash(context, f"mkdir -p {shlex_quote(context.release_root)} {shlex_quote(context.current_root)}")
    upload_bridge_script(context)
    stop_result = stop_existing_bridge(context)
    remote_pid = start_bridge(context)
    remote_probe_result = remote_probe(context)
    public_probe_result = None
    final_status = "completed"
    stop_reason = "bridge_mock_released"
    try:
        public_probe_result = public_probe(context)
    except subprocess.CalledProcessError as exc:
        final_status = "public_probe_failed"
        stop_reason = "public_probe_failed"
        public_probe_result = {"status": 0, "responseText": (exc.stdout or exc.stderr or "").strip(), "responseJson": {}}

    log_tail = read_remote_log_tail(context)
    local_secret_path = sync_local_secret(context) if context.sync_local_secret and final_status == "completed" else None
    record_path = write_record(
        context=context,
        stop_result=stop_result,
        remote_pid=remote_pid,
        remote_probe_result=remote_probe_result,
        public_probe_result=public_probe_result,
        log_tail=log_tail,
        local_secret_path=local_secret_path,
        final_status=final_status,
        stop_reason=stop_reason,
    )
    print(
        json.dumps(
            {
                "release_id": context.release_id,
                "status": final_status,
                "public_endpoint": context.public_endpoint,
                "record_path": str(record_path),
                "remote_pid": remote_pid,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if final_status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
