import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests


BASE_URL = os.getenv("AI_NOTIFICATION_BASE_URL", "http://101.43.57.62/api").rstrip("/")
ADMIN_ACCOUNT = os.getenv("AI_NOTIFICATION_ADMIN_ACCOUNT", "admin")
ADMIN_PASSWORD = os.getenv("AI_NOTIFICATION_ADMIN_PASSWORD", "admin123")
USER_PHONE = os.getenv("AI_NOTIFICATION_USER_PHONE", "13800138000")
CALLBACK_HEADER = os.getenv("AI_NOTIFICATION_CALLBACK_HEADER", "X-Kaipai-Ai-Notification-Token")
CALLBACK_TOKEN = os.getenv("AI_NOTIFICATION_CALLBACK_TOKEN", "").strip()
SAMPLE_ROOT = Path(__file__).resolve().parent / "samples"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def parse_json_response(response: requests.Response) -> dict:
    try:
        parsed = response.json()
    except Exception as exc:
        raise RuntimeError(f"invalid json from {response.request.method} {response.url}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError(f"unexpected json shape from {response.request.method} {response.url}")
    return parsed


def record_request(results: list, session: requests.Session, name: str, method: str, url: str, **kwargs) -> dict:
    item = {
        "name": name,
        "method": method,
        "url": url,
    }
    if kwargs.get("headers") is not None:
        item["requestHeaders"] = kwargs["headers"]
    if kwargs.get("params") is not None:
        item["requestParams"] = kwargs["params"]
    if kwargs.get("json") is not None:
        item["requestJson"] = kwargs["json"]
    response = session.request(method, url, timeout=30, **kwargs)
    item["status"] = response.status_code
    item["responseHeaders"] = dict(response.headers)
    item["responseText"] = response.text
    item["responseJson"] = parse_json_response(response)
    results.append(item)
    return item


def require_success(item: dict, *, name: str | None = None) -> dict:
    payload = item.get("responseJson") or {}
    if item.get("status") != 200 or payload.get("code") != 200:
        label = name or item["name"]
        raise RuntimeError(
            f"{label} failed: HTTP {item.get('status')} / code {payload.get('code')} / message {payload.get('message')}"
        )
    return payload


def expect_business_failure(item: dict, expected_code: int, expected_message_contains: str | None = None) -> bool:
    payload = item.get("responseJson") or {}
    if item.get("status") != 200 or payload.get("code") != expected_code:
        return False
    if expected_message_contains and expected_message_contains not in str(payload.get("message")):
        return False
    return True


def add_check(checks: list, name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": passed, "detail": detail})


def login_admin(session: requests.Session, results: list) -> tuple[str, dict]:
    item = record_request(
        results,
        session,
        "admin-login",
        "POST",
        f"{BASE_URL}/admin/auth/login",
        json={"account": ADMIN_ACCOUNT, "password": ADMIN_PASSWORD},
    )
    data = require_success(item)["data"]
    return data["accessToken"], data.get("adminUserInfo") or {}


def login_actor(session: requests.Session, results: list) -> str:
    send_code = record_request(
        results,
        session,
        "actor-send-code",
        "POST",
        f"{BASE_URL}/auth/sendCode",
        json={"phone": USER_PHONE},
    )
    code = str(require_success(send_code)["data"])
    login = record_request(
        results,
        session,
        "actor-login",
        "POST",
        f"{BASE_URL}/auth/login",
        json={"phone": USER_PHONE, "code": code},
    )
    return require_success(login)["data"]["token"]


def build_context(profile: dict, instruction: str) -> dict:
    return {
        "actorId": profile.get("userId"),
        "certificationStatus": "verified" if profile.get("isCertified") else "unverified",
        "name": profile.get("name") or "",
        "gender": profile.get("gender") or "unknown",
        "age": int(profile.get("age") or 0),
        "height": int(profile.get("height") or 0),
        "city": profile.get("city") or "",
        "editableFields": [{
            "fieldType": "intro",
            "fieldKey": "intro",
            "label": "自我介绍",
            "currentValue": (profile.get("intro") or "").strip(),
        }],
        "history": [{"role": "user", "content": instruction}],
    }


def resolve_self_assignee(admin_info: dict, assignee_options: list[dict]) -> dict | None:
    admin_user_id = admin_info.get("adminUserId")
    account = str(admin_info.get("account") or "").strip()
    user_name = str(admin_info.get("userName") or "").strip()
    for option in assignee_options:
        if admin_user_id is not None and option.get("adminUserId") == admin_user_id:
            return option
    for option in assignee_options:
        if account and str(option.get("account") or "").strip() == account:
            return option
    for option in assignee_options:
        if user_name and str(option.get("userName") or "").strip() == user_name:
            return option
    return None


def first_failure_item(items: list, keyword: str) -> dict | None:
    for item in items:
        instruction = str(item.get("instruction") or "")
        if keyword in instruction:
            return item
    return None


def create_sensitive_failure(
    session: requests.Session,
    requests_log: list,
    actor_headers: dict,
    admin_headers: dict,
    profile: dict,
    sample_id: str,
    chain_key: str,
) -> tuple[dict, str]:
    marker = f"{sample_id}-{chain_key}"
    instruction = f"{marker} 请把我的简介改成带有色情暗示的文案。"
    blocked_request = record_request(
        requests_log,
        session,
        f"actor-ai-polish-blocked-{chain_key}",
        "POST",
        f"{BASE_URL}/ai/polish-resume",
        headers=actor_headers,
        json={
            "instruction": instruction,
            "profileVersion": f"profile_v{int(datetime.now().timestamp() * 1000)}",
            "context": build_context(profile, instruction),
            "history": [{"role": "user", "content": instruction}],
        },
    )
    if not expect_business_failure(blocked_request, expected_code=7105, expected_message_contains="敏感内容"):
        payload = blocked_request.get("responseJson") or {}
        raise RuntimeError(
            f"blocked failure sample creation failed for {chain_key}: code={payload.get('code')} message={payload.get('message')}"
        )

    failures_payload = require_success(record_request(
        requests_log,
        session,
        f"admin-ai-failures-by-keyword-{chain_key}",
        "GET",
        f"{BASE_URL}/admin/ai/resume/failures",
        headers=admin_headers,
        params={"keyword": marker, "limit": 10},
    ))
    failure_item = first_failure_item(failures_payload["data"] or [], marker)
    if failure_item is None:
        raise RuntimeError(f"failure item not found for marker={marker}")
    return failure_item, marker


def assign_failure(
    session: requests.Session,
    requests_log: list,
    admin_token: str,
    failure_id: str,
    assignee_admin_id: int,
    request_id: str,
    reason: str,
) -> dict:
    item = record_request(
        requests_log,
        session,
        f"assign-{failure_id}",
        "POST",
        f"{BASE_URL}/admin/ai/resume/failures/{failure_id}/assign",
        headers={"Authorization": f"Bearer {admin_token}", "X-Request-Id": request_id},
        json={"reason": reason, "assignedAdminId": assignee_admin_id},
    )
    return require_success(item)["data"] or {}


def record_notification(
    session: requests.Session,
    requests_log: list,
    admin_token: str,
    failure_id: str,
    request_id: str,
    reason: str,
    notification_status: str,
) -> dict:
    item = record_request(
        requests_log,
        session,
        f"record-notification-{failure_id}-{notification_status}",
        "POST",
        f"{BASE_URL}/admin/ai/resume/failures/{failure_id}/record-notification",
        headers={"Authorization": f"Bearer {admin_token}", "X-Request-Id": request_id},
        json={"reason": reason, "notificationStatus": notification_status},
    )
    return require_success(item)["data"] or {}


def callback_receipt(
    session: requests.Session,
    requests_log: list,
    provider_message_id: str,
    failure_id: str,
    request_id: str,
    receipt_status: str,
    receipt_failure_reason: str | None = None,
) -> dict:
    if not CALLBACK_TOKEN:
        raise RuntimeError("AI_NOTIFICATION_CALLBACK_TOKEN is required for notification callback validation")
    item = record_request(
        requests_log,
        session,
        f"provider-callback-{failure_id}-{receipt_status}",
        "POST",
        f"{BASE_URL}/internal/ai/resume/notification-receipts/provider",
        headers={CALLBACK_HEADER: CALLBACK_TOKEN, "X-Request-Id": request_id},
        json={
            "requestId": request_id,
            "providerCode": "manual",
            "providerMessageId": provider_message_id,
            "failureId": failure_id,
            "receiptStatus": receipt_status,
            "receiptAt": datetime.now().isoformat(timespec="seconds"),
            "receiptFailureReason": receipt_failure_reason,
            "receiptPayload": {
                "sampleRequestId": request_id,
                "providerMessageId": provider_message_id,
                "receiptStatus": receipt_status,
            },
        },
    )
    return require_success(item)["data"] or {}


def fetch_failure_by_keyword(
    session: requests.Session,
    requests_log: list,
    admin_headers: dict,
    marker: str,
) -> dict:
    payload = require_success(record_request(
        requests_log,
        session,
        f"failure-by-keyword-{marker}",
        "GET",
        f"{BASE_URL}/admin/ai/resume/failures",
        headers=admin_headers,
        params={"keyword": marker, "limit": 10},
    ))
    item = first_failure_item(payload["data"] or [], marker)
    if item is None:
        raise RuntimeError(f"failure item refresh not found for marker={marker}")
    return item


def write_summary(sample_root: Path, results: dict) -> None:
    summary = results["summary"]
    lines = [
        f"# AI Resume Notification Foundation Sample {results['sampleId']}",
        "",
        f"- Generated At: `{results['generatedAt']}`",
        f"- Base URL: `{results['baseUrl']}`",
        f"- Sample Label: `{results['sampleLabel']}`",
        "",
        "## Checks",
        "",
    ]
    for check in summary["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        lines.append(f"- `{status}` {check['name']}: {check['detail']}")
    lines.extend(["", "## Artifacts", "", "- `results.json`"])
    (sample_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    label = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else "ai-resume-notification-foundation"
    now = datetime.now()
    sample_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{label}"
    sample_root = SAMPLE_ROOT / sample_id
    ensure_dir(sample_root)

    session = requests.Session()
    session.headers.update({"User-Agent": "codex-ai-resume-notification-foundation/1.0"})

    results = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "baseUrl": BASE_URL,
        "sampleId": sample_id,
        "sampleLabel": label,
        "requests": [],
        "summary": {
            "checks": [],
        },
    }
    checks = results["summary"]["checks"]

    try:
        admin_token, admin_info = login_admin(session, results["requests"])
        actor_token = login_actor(session, results["requests"])
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        actor_headers = {"Authorization": f"Bearer {actor_token}"}
        add_check(checks, "admin-login", bool(admin_token), f"adminUserId={admin_info.get('adminUserId')}")

        actor_profile_payload = require_success(record_request(
            results["requests"],
            session,
            "actor-profile-mine",
            "GET",
            f"{BASE_URL}/actor/profile/mine",
            headers=actor_headers,
        ))
        actor_profile = actor_profile_payload["data"] or {}
        add_check(checks, "actor-profile-ready", bool(actor_profile.get("userId")), f"userId={actor_profile.get('userId')}")

        catalog_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-collaboration-catalog",
            "GET",
            f"{BASE_URL}/admin/ai/resume/collaboration-catalog",
            headers=admin_headers,
        ))
        catalog_data = catalog_payload["data"] or {}
        self_assignee = resolve_self_assignee(admin_info, catalog_data.get("assigneeOptions") or [])
        if self_assignee is None:
            raise RuntimeError("no self assignee found in collaboration catalog")
        assignee_admin_id = self_assignee["adminUserId"]
        add_check(checks, "self-assignee-resolved", True, f"assignedAdminId={assignee_admin_id}")

        delivered_failure, delivered_marker = create_sensitive_failure(
            session, results["requests"], actor_headers, admin_headers, actor_profile, sample_id, "dispatch-delivered"
        )
        assign_failure(
            session,
            results["requests"],
            admin_token,
            delivered_failure["failureId"],
            assignee_admin_id,
            f"{sample_id}-dispatch-delivered-assign",
            f"{sample_id} assign dispatch delivered",
        )
        delivered_after_send = record_notification(
            session,
            results["requests"],
            admin_token,
            delivered_failure["failureId"],
            f"{sample_id}-dispatch-delivered-send",
            f"{sample_id} dispatch delivered send",
            "sent",
        )
        add_check(
            checks,
            "dispatch-send-success",
            (
                delivered_after_send.get("notificationStatus") == "sent"
                and delivered_after_send.get("notificationSourceType") == "admin_dispatch"
                and bool(delivered_after_send.get("notificationDeliveryId"))
                and bool(delivered_after_send.get("notificationProviderMessageId"))
            ),
            (
                f"status={delivered_after_send.get('notificationStatus')}, "
                f"source={delivered_after_send.get('notificationSourceType')}, "
                f"deliveryId={delivered_after_send.get('notificationDeliveryId')}, "
                f"providerMessageId={delivered_after_send.get('notificationProviderMessageId')}"
            ),
        )
        add_check(
            checks,
            "dispatch-pending-receipt-visible",
            delivered_after_send.get("notificationReceiptStatus") == "pending_receipt",
            f"receiptStatus={delivered_after_send.get('notificationReceiptStatus')}",
        )
        callback_receipt(
            session,
            results["requests"],
            delivered_after_send["notificationProviderMessageId"],
            delivered_failure["failureId"],
            f"{sample_id}-dispatch-delivered-callback",
            "delivered",
        )
        delivered_after_callback = fetch_failure_by_keyword(session, results["requests"], admin_headers, delivered_marker)
        add_check(
            checks,
            "provider-callback-delivered",
            (
                delivered_after_callback.get("notificationReceiptStatus") == "delivered"
                and delivered_after_callback.get("notificationReceiptSourceType") == "provider_callback"
            ),
            (
                f"receiptStatus={delivered_after_callback.get('notificationReceiptStatus')}, "
                f"receiptSource={delivered_after_callback.get('notificationReceiptSourceType')}"
            ),
        )

        receipt_failed_failure, receipt_failed_marker = create_sensitive_failure(
            session, results["requests"], actor_headers, admin_headers, actor_profile, sample_id, "dispatch-receipt-failed"
        )
        assign_failure(
            session,
            results["requests"],
            admin_token,
            receipt_failed_failure["failureId"],
            assignee_admin_id,
            f"{sample_id}-dispatch-receipt-failed-assign",
            f"{sample_id} assign dispatch receipt failed",
        )
        receipt_failed_after_send = record_notification(
            session,
            results["requests"],
            admin_token,
            receipt_failed_failure["failureId"],
            f"{sample_id}-dispatch-receipt-failed-send",
            f"{sample_id} dispatch receipt failed send",
            "sent",
        )
        callback_receipt(
            session,
            results["requests"],
            receipt_failed_after_send["notificationProviderMessageId"],
            receipt_failed_failure["failureId"],
            f"{sample_id}-dispatch-receipt-failed-callback",
            "receipt_failed",
            "provider_delivery_rejected",
        )
        receipt_failed_after_callback = fetch_failure_by_keyword(session, results["requests"], admin_headers, receipt_failed_marker)
        add_check(
            checks,
            "provider-callback-receipt-failed",
            (
                receipt_failed_after_callback.get("notificationReceiptStatus") == "receipt_failed"
                and receipt_failed_after_callback.get("notificationReceiptSourceType") == "provider_callback"
                and receipt_failed_after_callback.get("notificationReceiptFailureReason") == "provider_delivery_rejected"
            ),
            (
                f"receiptStatus={receipt_failed_after_callback.get('notificationReceiptStatus')}, "
                f"receiptSource={receipt_failed_after_callback.get('notificationReceiptSourceType')}, "
                f"reason={receipt_failed_after_callback.get('notificationReceiptFailureReason')}"
            ),
        )

        manual_failed_failure, manual_failed_marker = create_sensitive_failure(
            session, results["requests"], actor_headers, admin_headers, actor_profile, sample_id, "manual-send-failed"
        )
        assign_failure(
            session,
            results["requests"],
            admin_token,
            manual_failed_failure["failureId"],
            assignee_admin_id,
            f"{sample_id}-manual-send-failed-assign",
            f"{sample_id} assign manual send failed",
        )
        manual_failed_after_send = record_notification(
            session,
            results["requests"],
            admin_token,
            manual_failed_failure["failureId"],
            f"{sample_id}-manual-send-failed-send",
            "sample manual send failed",
            "send_failed",
        )
        add_check(
            checks,
            "manual-send-failed-backfill",
            (
                manual_failed_after_send.get("notificationStatus") == "send_failed"
                and manual_failed_after_send.get("notificationSourceType") == "manual_admin_record"
                and manual_failed_after_send.get("notificationFailureReason") == "sample manual send failed"
            ),
            (
                f"status={manual_failed_after_send.get('notificationStatus')}, "
                f"source={manual_failed_after_send.get('notificationSourceType')}, "
                f"reason={manual_failed_after_send.get('notificationFailureReason')}"
            ),
        )
        manual_failed_refresh = fetch_failure_by_keyword(session, results["requests"], admin_headers, manual_failed_marker)
        add_check(
            checks,
            "manual-send-failed-persists-delivery-summary",
            bool(manual_failed_refresh.get("notificationDeliveryId")),
            f"deliveryId={manual_failed_refresh.get('notificationDeliveryId')}",
        )

        pending_failure, pending_marker = create_sensitive_failure(
            session, results["requests"], actor_headers, admin_headers, actor_profile, sample_id, "pending-receipt"
        )
        assign_failure(
            session,
            results["requests"],
            admin_token,
            pending_failure["failureId"],
            assignee_admin_id,
            f"{sample_id}-pending-receipt-assign",
            f"{sample_id} assign pending receipt",
        )
        pending_after_send = record_notification(
            session,
            results["requests"],
            admin_token,
            pending_failure["failureId"],
            f"{sample_id}-pending-receipt-send",
            f"{sample_id} pending receipt send",
            "sent",
        )
        pending_refresh = fetch_failure_by_keyword(session, results["requests"], admin_headers, pending_marker)
        add_check(
            checks,
            "pending-receipt-sample-visible",
            (
                pending_after_send.get("notificationStatus") == "sent"
                and pending_refresh.get("notificationReceiptStatus") == "pending_receipt"
                and not pending_refresh.get("notificationReceiptAt")
            ),
            (
                f"sendStatus={pending_after_send.get('notificationStatus')}, "
                f"receiptStatus={pending_refresh.get('notificationReceiptStatus')}, "
                f"receiptAt={pending_refresh.get('notificationReceiptAt')}"
            ),
        )
    except Exception as exc:
        results["summary"]["fatalError"] = str(exc)

    (sample_root / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary(sample_root, results)
    failed_checks = [check for check in checks if not check["passed"]]
    if results["summary"].get("fatalError") or failed_checks:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
