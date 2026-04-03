import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests


BASE_URL = "http://101.43.57.62/api"
ADMIN_ACCOUNT = "admin"
ADMIN_PASSWORD = "admin123"
USER_PHONE = "13800138000"
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
    checks.append({
        "name": name,
        "passed": passed,
        "detail": detail,
    })


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


def certification_status(profile: dict) -> str:
    return "verified" if profile.get("isCertified") else "unverified"


def resolve_level_label(profile: dict) -> str | None:
    capability = profile.get("capabilitySummary") or {}
    if capability.get("levelLabel"):
        return str(capability["levelLabel"])
    if capability.get("levelName"):
        return str(capability["levelName"])
    if capability.get("level") is not None:
        return f"Lv{capability['level']}"
    return None


def build_context(profile: dict) -> dict:
    editable_fields = [{
        "fieldType": "intro",
        "fieldKey": "intro",
        "label": "自我介绍",
        "currentValue": (profile.get("intro") or "").strip(),
    }]
    for item in profile.get("workExperiences") or []:
        experience_id = item.get("id")
        if experience_id is None:
            continue
        editable_fields.append({
            "fieldType": "work_experience_description",
            "fieldKey": f"work_experience:{experience_id}:description",
            "label": f"{(item.get('projectName') or '拍摄经历').strip()} - 经历描述",
            "targetId": str(experience_id),
            "projectName": (item.get("projectName") or "").strip(),
            "roleName": (item.get("roleName") or "").strip(),
            "shootDate": (item.get("shootDate") or "").strip(),
            "currentValue": (item.get("description") or "").strip(),
        })

    context = {
        "actorId": profile.get("userId"),
        "certificationStatus": certification_status(profile),
        "name": (profile.get("name") or "").strip(),
        "gender": profile.get("gender") or "unknown",
        "age": int(profile.get("age") or 0),
        "height": int(profile.get("height") or 0),
        "city": (profile.get("city") or "").strip(),
        "bodyType": profile.get("bodyType"),
        "hairStyle": profile.get("hairStyle"),
        "languages": list(profile.get("languages") or []),
        "skillTypes": list(profile.get("skillTypes") or []),
        "editableFields": editable_fields,
    }
    level_label = resolve_level_label(profile)
    if level_label:
        context["levelLabel"] = level_label
    return context


def first_failure_item(items: list, keyword: str) -> dict | None:
    for item in items:
        instruction = str(item.get("instruction") or "")
        if keyword in instruction:
            return item
    return None


def find_handling_note(item: dict, action_type: str) -> dict | None:
    for note in item.get("handlingNotes") or []:
        if note.get("actionType") == action_type:
            return note
    return None


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
            "context": build_context(profile),
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
    failure_items = failures_payload["data"] or []
    failure_item = first_failure_item(failure_items, marker)
    if failure_item is None:
        raise RuntimeError(f"failure item not found for marker={marker}")

    sensitive_payload = require_success(record_request(
        requests_log,
        session,
        f"admin-ai-sensitive-hits-by-keyword-{chain_key}",
        "GET",
        f"{BASE_URL}/admin/ai/resume/sensitive-hits",
        headers=admin_headers,
        params={"keyword": marker, "limit": 10},
    ))
    sensitive_items = sensitive_payload["data"] or []
    if first_failure_item(sensitive_items, marker) is None:
        raise RuntimeError(f"sensitive hit item not found for marker={marker}")
    return failure_item, marker


def verify_operation_log(
    session: requests.Session,
    requests_log: list,
    admin_headers: dict,
    request_id: str,
    operation_code: str,
    check_name: str,
    checks: list,
) -> None:
    payload = require_success(record_request(
        requests_log,
        session,
        f"admin-operation-logs-{operation_code}",
        "GET",
        f"{BASE_URL}/admin/system/operation-logs",
        headers=admin_headers,
        params={
            "pageNo": 1,
            "pageSize": 20,
            "targetType": "ai_resume_failure",
            "operationCode": operation_code,
            "requestId": request_id,
        },
    ))
    log_list = payload["data"].get("list") or []
    add_check(checks, check_name, len(log_list) >= 1, f"requestId={request_id}, list={len(log_list)}")


def write_summary(sample_root: Path, results: dict) -> None:
    summary = results["summary"]
    lines = [
        f"# AI Resume Collaboration Validation Sample {results['sampleId']}",
        "",
        f"- Generated At: `{results['generatedAt']}`",
        f"- Base URL: `{results['baseUrl']}`",
        f"- Sample Label: `{results['sampleLabel']}`",
        "",
        "## Key IDs",
        "",
        f"- Admin User ID: `{summary.get('adminUserId')}`",
        f"- Assignee Admin ID: `{summary.get('assigneeAdminId')}`",
        f"- Assign/Acknowledge Failure ID: `{summary.get('assignAcknowledgeFailureId')}`",
        f"- Assign/Acknowledge Request ID: `{summary.get('assignAcknowledgeFailureRequestId')}`",
        f"- Assign/Remind Failure ID: `{summary.get('assignRemindFailureId')}`",
        f"- Assign/Remind Request ID: `{summary.get('assignRemindFailureRequestId')}`",
        f"- Auto Remind Sweep Failure ID: `{summary.get('autoRemindSweepFailureId')}`",
        f"- Timeout Escalation Failure ID: `{summary.get('timeoutEscalationFailureId')}`",
        "",
        "## Checks",
        "",
    ]
    for check in summary["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        lines.append(f"- `{status}` {check['name']}: {check['detail']}")
    lines.extend([
        "",
        "## Artifacts",
        "",
        "- `results.json`",
    ])
    (sample_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    label = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else "ai-resume-collaboration-validation"
    now = datetime.now()
    sample_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{label}"
    sample_root = SAMPLE_ROOT / sample_id
    ensure_dir(sample_root)

    session = requests.Session()
    session.headers.update({"User-Agent": "codex-ai-resume-collaboration-validation/1.0"})

    results = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "baseUrl": BASE_URL,
        "sampleId": sample_id,
        "sampleLabel": label,
        "requests": [],
        "summary": {
            "adminUserId": None,
            "assigneeAdminId": None,
            "assignAcknowledgeFailureId": None,
            "assignAcknowledgeFailureRequestId": None,
            "assignRemindFailureId": None,
            "assignRemindFailureRequestId": None,
            "autoRemindSweepFailureId": None,
            "timeoutEscalationFailureId": None,
            "checks": [],
        },
    }
    checks = results["summary"]["checks"]

    try:
        admin_token, admin_info = login_admin(session, results["requests"])
        actor_token = login_actor(session, results["requests"])
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        actor_headers = {"Authorization": f"Bearer {actor_token}"}

        results["summary"]["adminUserId"] = admin_info.get("adminUserId")
        add_check(
            checks,
            "admin-login",
            bool(admin_token and admin_info.get("adminUserId")),
            f"adminUserId={admin_info.get('adminUserId')}, account={admin_info.get('account')}",
        )

        admin_me_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-auth-me",
            "GET",
            f"{BASE_URL}/admin/auth/me",
            headers=admin_headers,
        ))
        admin_me = admin_me_payload["data"] or {}
        add_check(
            checks,
            "admin-session-visible",
            admin_me.get("adminUserId") == admin_info.get("adminUserId"),
            f"sessionAdminUserId={admin_me.get('adminUserId')}",
        )

        actor_profile_payload = require_success(record_request(
            results["requests"],
            session,
            "actor-profile-mine",
            "GET",
            f"{BASE_URL}/actor/profile/mine",
            headers=actor_headers,
        ))
        actor_profile = actor_profile_payload["data"] or {}
        add_check(
            checks,
            "actor-certified",
            bool(actor_profile.get("isCertified")),
            f"userId={actor_profile.get('userId')}, isCertified={actor_profile.get('isCertified')}",
        )

        catalog_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-collaboration-catalog",
            "GET",
            f"{BASE_URL}/admin/ai/resume/collaboration-catalog",
            headers=admin_headers,
        ))
        catalog_data = catalog_payload["data"] or {}
        assignee_options = catalog_data.get("assigneeOptions") or []
        escalation_role_options = catalog_data.get("escalationRoleOptions") or []
        self_assignee = resolve_self_assignee(admin_me, assignee_options)
        if self_assignee is None:
            raise RuntimeError("no self-assignable admin found in collaboration catalog for current admin session")
        results["summary"]["assigneeAdminId"] = self_assignee.get("adminUserId")
        add_check(
            checks,
            "collaboration-catalog-ready",
            len(assignee_options) >= 1,
            f"assigneeCount={len(assignee_options)}, escalationRoleCount={len(escalation_role_options)}",
        )
        add_check(
            checks,
            "self-assignee-resolved",
            self_assignee.get("adminUserId") == admin_me.get("adminUserId"),
            f"assigneeAdminId={self_assignee.get('adminUserId')}, account={self_assignee.get('account')}",
        )

        escalation_role_code = None
        if escalation_role_options:
            escalation_role_code = escalation_role_options[0].get("roleCode")

        assign_ack_failure, assign_ack_marker = create_sensitive_failure(
            session,
            results["requests"],
            actor_headers,
            admin_headers,
            actor_profile,
            sample_id,
            "assign-ack",
        )
        assign_ack_failure_id = assign_ack_failure.get("failureId")
        results["summary"]["assignAcknowledgeFailureId"] = assign_ack_failure_id
        results["summary"]["assignAcknowledgeFailureRequestId"] = assign_ack_failure.get("requestId")
        add_check(
            checks,
            "assign-ack-failure-created",
            bool(assign_ack_failure_id),
            f"failureId={assign_ack_failure_id}, requestId={assign_ack_failure.get('requestId')}",
        )

        assign_ack_request_id = f"{sample_id}-assign-ack"
        assign_ack_headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-Request-Id": assign_ack_request_id,
        }
        assign_ack_body = {
            "reason": f"{sample_id} assign acknowledge",
            "assignedAdminId": self_assignee.get("adminUserId"),
        }
        if escalation_role_code:
            assign_ack_body["escalationRoleCode"] = escalation_role_code
        assign_ack_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-assign-ack-chain",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{assign_ack_failure_id}/assign",
            headers=assign_ack_headers,
            json=assign_ack_body,
        ))
        assign_ack_item = assign_ack_payload["data"] or {}
        assign_note = find_handling_note(assign_ack_item, "assign")
        add_check(
            checks,
            "assign-action-updates-collaboration-fields",
            (
                assign_ack_item.get("assignedAdminId") == self_assignee.get("adminUserId")
                and bool(assign_ack_item.get("assignedAt"))
                and assign_ack_item.get("collaborationStatus") == "pending_ack"
                and bool(assign_ack_item.get("claimDeadlineAt"))
                and int(assign_ack_item.get("reminderCount") or 0) == 0
            ),
            (
                f"assignedAdminId={assign_ack_item.get('assignedAdminId')}, "
                f"collaborationStatus={assign_ack_item.get('collaborationStatus')}, "
                f"claimDeadlineAt={assign_ack_item.get('claimDeadlineAt')}"
            ),
        )
        add_check(
            checks,
            "assign-action-derives-notification-and-sla-fields",
            (
                assign_ack_item.get("notificationStatus") == "pending_send"
                and not assign_ack_item.get("notificationSentAt")
                and assign_ack_item.get("notificationReceiptStatus") == "not_sent"
                and assign_ack_item.get("autoRemindStage") == "idle"
                and assign_ack_item.get("slaStatus") == "not_started"
            ),
            (
                f"notificationStatus={assign_ack_item.get('notificationStatus')}, "
                f"receiptStatus={assign_ack_item.get('notificationReceiptStatus')}, "
                f"autoRemindStage={assign_ack_item.get('autoRemindStage')}, "
                f"slaStatus={assign_ack_item.get('slaStatus')}"
            ),
        )
        add_check(
            checks,
            "assign-action-handling-note-visible",
            assign_note is not None and assign_note.get("assignedAdminId") == self_assignee.get("adminUserId"),
            f"assignNoteFound={assign_note is not None}",
        )

        pending_ack_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failures-pending-ack-assign-ack",
            "GET",
            f"{BASE_URL}/admin/ai/resume/failures",
            headers=admin_headers,
            params={
                "keyword": assign_ack_marker,
                "assignedAdminId": self_assignee.get("adminUserId"),
                "collaborationStatus": "pending_ack",
                "limit": 10,
            },
        ))
        pending_ack_item = first_failure_item(pending_ack_payload["data"] or [], assign_ack_marker)
        add_check(
            checks,
            "pending-ack-filter-visible",
            pending_ack_item is not None,
            f"marker={assign_ack_marker}",
        )
        notification_pending_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failures-notification-pending-assign-ack",
            "GET",
            f"{BASE_URL}/admin/ai/resume/failures",
            headers=admin_headers,
            params={
                "keyword": assign_ack_marker,
                "notificationStatus": "pending_send",
                "notificationReceiptStatus": "not_sent",
                "autoRemindStage": "idle",
                "slaStatus": "not_started",
                "limit": 10,
            },
        ))
        notification_pending_item = first_failure_item(notification_pending_payload["data"] or [], assign_ack_marker)
        add_check(
            checks,
            "notification-and-sla-filter-visible-before-ack",
            notification_pending_item is not None,
            f"marker={assign_ack_marker}",
        )

        record_notification_request_id = f"{sample_id}-record-notification"
        record_notification_headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-Request-Id": record_notification_request_id,
        }
        record_notification_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-record-notification",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{assign_ack_failure_id}/record-notification",
            headers=record_notification_headers,
            json={"reason": f"{sample_id} record notification", "notificationStatus": "sent"},
        ))
        record_notification_item = record_notification_payload["data"] or {}
        add_check(
            checks,
            "record-notification-action-updates-fields",
            (
                record_notification_item.get("notificationStatus") == "sent"
                and bool(record_notification_item.get("notificationSentAt"))
                and record_notification_item.get("notificationReceiptStatus") == "pending_receipt"
                and record_notification_item.get("autoRemindStage") == "watching"
                and record_notification_item.get("slaStatus") == "active"
            ),
            (
                f"notificationStatus={record_notification_item.get('notificationStatus')}, "
                f"notificationSentAt={record_notification_item.get('notificationSentAt')}, "
                f"receiptStatus={record_notification_item.get('notificationReceiptStatus')}, "
                f"autoRemindStage={record_notification_item.get('autoRemindStage')}"
            ),
        )

        record_notification_filter_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failures-recorded-notification-assign-ack",
            "GET",
            f"{BASE_URL}/admin/ai/resume/failures",
            headers=admin_headers,
            params={
                "keyword": assign_ack_marker,
                "notificationStatus": "sent",
                "notificationReceiptStatus": "pending_receipt",
                "autoRemindStage": "watching",
                "slaStatus": "active",
                "limit": 10,
            },
        ))
        record_notification_filter_item = first_failure_item(record_notification_filter_payload["data"] or [], assign_ack_marker)
        add_check(
            checks,
            "record-notification-filter-visible",
            record_notification_filter_item is not None,
            f"marker={assign_ack_marker}",
        )

        record_receipt_request_id = f"{sample_id}-record-receipt"
        record_receipt_headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-Request-Id": record_receipt_request_id,
        }
        record_receipt_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-record-notification-receipt",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{assign_ack_failure_id}/record-notification-receipt",
            headers=record_receipt_headers,
            json={"reason": f"{sample_id} record receipt", "notificationReceiptStatus": "delivered"},
        ))
        record_receipt_item = record_receipt_payload["data"] or {}
        add_check(
            checks,
            "record-receipt-action-updates-fields",
            (
                record_receipt_item.get("notificationReceiptStatus") == "delivered"
                and bool(record_receipt_item.get("notificationReceiptAt"))
                and record_receipt_item.get("notificationStatus") == "sent"
            ),
            (
                f"receiptStatus={record_receipt_item.get('notificationReceiptStatus')}, "
                f"receiptAt={record_receipt_item.get('notificationReceiptAt')}, "
                f"notificationStatus={record_receipt_item.get('notificationStatus')}"
            ),
        )

        delivered_filter_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failures-delivered-assign-ack",
            "GET",
            f"{BASE_URL}/admin/ai/resume/failures",
            headers=admin_headers,
            params={
                "keyword": assign_ack_marker,
                "notificationReceiptStatus": "delivered",
                "limit": 10,
            },
        ))
        delivered_filter_item = first_failure_item(delivered_filter_payload["data"] or [], assign_ack_marker)
        add_check(
            checks,
            "delivered-filter-visible-before-ack",
            delivered_filter_item is not None,
            f"marker={assign_ack_marker}",
        )

        acknowledge_request_id = f"{sample_id}-acknowledge"
        acknowledge_headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-Request-Id": acknowledge_request_id,
        }
        acknowledge_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-acknowledge",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{assign_ack_failure_id}/acknowledge-assignment",
            headers=acknowledge_headers,
            json={"reason": f"{sample_id} acknowledge"},
        ))
        acknowledge_item = acknowledge_payload["data"] or {}
        acknowledge_note = find_handling_note(acknowledge_item, "acknowledge")
        add_check(
            checks,
            "acknowledge-action-updates-collaboration-fields",
            (
                acknowledge_item.get("assignmentAcknowledgedByAdminId") == admin_me.get("adminUserId")
                and bool(acknowledge_item.get("assignmentAcknowledgedAt"))
                and acknowledge_item.get("collaborationStatus") == "acknowledged"
            ),
            (
                f"ackBy={acknowledge_item.get('assignmentAcknowledgedByAdminId')}, "
                f"collaborationStatus={acknowledge_item.get('collaborationStatus')}"
            ),
        )
        add_check(
            checks,
            "acknowledge-action-derives-receipt-and-complete-states",
            (
                acknowledge_item.get("notificationReceiptStatus") == "received"
                and bool(acknowledge_item.get("notificationReceiptAt"))
                and acknowledge_item.get("autoRemindStage") == "completed"
                and acknowledge_item.get("slaStatus") in {"within_sla", "breached"}
            ),
            (
                f"receiptStatus={acknowledge_item.get('notificationReceiptStatus')}, "
                f"receiptAt={acknowledge_item.get('notificationReceiptAt')}, "
                f"autoRemindStage={acknowledge_item.get('autoRemindStage')}, "
                f"slaStatus={acknowledge_item.get('slaStatus')}"
            ),
        )
        add_check(
            checks,
            "acknowledge-action-handling-note-visible",
            acknowledge_note is not None and acknowledge_note.get("assignmentAcknowledgedByAdminId") == admin_me.get("adminUserId"),
            f"acknowledgeNoteFound={acknowledge_note is not None}",
        )

        acknowledged_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failures-acknowledged-assign-ack",
            "GET",
            f"{BASE_URL}/admin/ai/resume/failures",
            headers=admin_headers,
            params={
                "keyword": assign_ack_marker,
                "assignedAdminId": self_assignee.get("adminUserId"),
                "collaborationStatus": "acknowledged",
                "limit": 10,
            },
        ))
        acknowledged_item = first_failure_item(acknowledged_payload["data"] or [], assign_ack_marker)
        add_check(
            checks,
            "acknowledged-filter-visible",
            acknowledged_item is not None,
            f"marker={assign_ack_marker}",
        )
        receipt_done_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failures-receipt-complete-assign-ack",
            "GET",
            f"{BASE_URL}/admin/ai/resume/failures",
            headers=admin_headers,
            params={
                "keyword": assign_ack_marker,
                "notificationReceiptStatus": "received",
                "autoRemindStage": "completed",
                "limit": 10,
            },
        ))
        receipt_done_item = first_failure_item(receipt_done_payload["data"] or [], assign_ack_marker)
        add_check(
            checks,
            "receipt-filter-visible-after-ack",
            receipt_done_item is not None,
            f"marker={assign_ack_marker}",
        )

        assign_remind_failure, assign_remind_marker = create_sensitive_failure(
            session,
            results["requests"],
            actor_headers,
            admin_headers,
            actor_profile,
            sample_id,
            "assign-remind",
        )
        assign_remind_failure_id = assign_remind_failure.get("failureId")
        results["summary"]["assignRemindFailureId"] = assign_remind_failure_id
        results["summary"]["assignRemindFailureRequestId"] = assign_remind_failure.get("requestId")
        add_check(
            checks,
            "assign-remind-failure-created",
            bool(assign_remind_failure_id),
            f"failureId={assign_remind_failure_id}, requestId={assign_remind_failure.get('requestId')}",
        )

        assign_remind_request_id = f"{sample_id}-assign-remind"
        assign_remind_headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-Request-Id": assign_remind_request_id,
        }
        assign_remind_body = {
            "reason": f"{sample_id} assign remind",
            "assignedAdminId": self_assignee.get("adminUserId"),
        }
        if escalation_role_code:
            assign_remind_body["escalationRoleCode"] = escalation_role_code
        assign_remind_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-assign-remind-chain",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{assign_remind_failure_id}/assign",
            headers=assign_remind_headers,
            json=assign_remind_body,
        ))
        assign_remind_item = assign_remind_payload["data"] or {}
        add_check(
            checks,
            "assign-remind-chain-pending-ack",
            assign_remind_item.get("collaborationStatus") == "pending_ack",
            f"collaborationStatus={assign_remind_item.get('collaborationStatus')}",
        )

        remind_request_id = f"{sample_id}-remind"
        remind_headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-Request-Id": remind_request_id,
        }
        remind_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-remind",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{assign_remind_failure_id}/remind",
            headers=remind_headers,
            json={"reason": f"{sample_id} remind"},
        ))
        remind_item = remind_payload["data"] or {}
        remind_note = find_handling_note(remind_item, "remind")
        add_check(
            checks,
            "remind-action-updates-reminder-fields",
            (
                remind_item.get("assignedAdminId") == self_assignee.get("adminUserId")
                and int(remind_item.get("reminderCount") or 0) >= 1
                and remind_item.get("lastRemindedByAdminId") == admin_me.get("adminUserId")
                and bool(remind_item.get("lastRemindedAt"))
                and not remind_item.get("assignmentAcknowledgedAt")
                and remind_item.get("collaborationStatus") == "pending_ack"
            ),
            (
                f"reminderCount={remind_item.get('reminderCount')}, "
                f"lastRemindedByAdminId={remind_item.get('lastRemindedByAdminId')}, "
                f"collaborationStatus={remind_item.get('collaborationStatus')}"
            ),
        )
        add_check(
            checks,
            "remind-action-derives-resent-notification-state",
            (
                remind_item.get("notificationStatus") == "resent"
                and bool(remind_item.get("notificationSentAt"))
                and remind_item.get("notificationReceiptStatus") == "pending_receipt"
                and remind_item.get("autoRemindStage") in {"manual_intervened", "escalation_due"}
                and remind_item.get("slaStatus") == "active"
            ),
            (
                f"notificationStatus={remind_item.get('notificationStatus')}, "
                f"receiptStatus={remind_item.get('notificationReceiptStatus')}, "
                f"autoRemindStage={remind_item.get('autoRemindStage')}, "
                f"slaStatus={remind_item.get('slaStatus')}"
            ),
        )
        add_check(
            checks,
            "remind-action-handling-note-visible",
            remind_note is not None and int(remind_note.get("reminderCount") or 0) >= 1,
            f"remindNoteFound={remind_note is not None}",
        )

        remind_filter_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failures-pending-ack-assign-remind",
            "GET",
            f"{BASE_URL}/admin/ai/resume/failures",
            headers=admin_headers,
            params={
                "keyword": assign_remind_marker,
                "assignedAdminId": self_assignee.get("adminUserId"),
                "collaborationStatus": "pending_ack",
                "limit": 10,
            },
        ))
        remind_filter_item = first_failure_item(remind_filter_payload["data"] or [], assign_remind_marker)
        add_check(
            checks,
            "remind-pending-ack-filter-visible",
            remind_filter_item is not None and int((remind_filter_item or {}).get("reminderCount") or 0) >= 1,
            f"marker={assign_remind_marker}",
        )
        remind_state_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failures-resent-remind-stage",
            "GET",
            f"{BASE_URL}/admin/ai/resume/failures",
            headers=admin_headers,
            params={
                "keyword": assign_remind_marker,
                "notificationStatus": "resent",
                "notificationReceiptStatus": "pending_receipt",
                "autoRemindStage": "manual_intervened",
                "limit": 10,
            },
        ))
        remind_state_item = first_failure_item(remind_state_payload["data"] or [], assign_remind_marker)
        add_check(
            checks,
            "resent-filter-visible-after-remind",
            remind_state_item is not None,
            f"marker={assign_remind_marker}",
        )

        skip_auto_remind_request_id = f"{sample_id}-skip-auto-remind"
        skip_auto_remind_headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-Request-Id": skip_auto_remind_request_id,
        }
        skip_auto_remind_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-skip-auto-remind",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{assign_remind_failure_id}/skip-auto-remind",
            headers=skip_auto_remind_headers,
            json={"reason": f"{sample_id} skip auto remind"},
        ))
        skip_auto_remind_item = skip_auto_remind_payload["data"] or {}
        add_check(
            checks,
            "skip-auto-remind-action-updates-stage",
            (
                skip_auto_remind_item.get("autoRemindStage") == "skipped"
                and bool(skip_auto_remind_item.get("autoRemindSkippedAt"))
                and bool(skip_auto_remind_item.get("autoRemindSkippedByAdminId"))
            ),
            (
                f"autoRemindStage={skip_auto_remind_item.get('autoRemindStage')}, "
                f"autoRemindSkippedAt={skip_auto_remind_item.get('autoRemindSkippedAt')}"
            ),
        )
        skip_auto_remind_filter_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failures-skip-auto-remind-filter",
            "GET",
            f"{BASE_URL}/admin/ai/resume/failures",
            headers=admin_headers,
            params={
                "keyword": assign_remind_marker,
                "autoRemindStage": "skipped",
                "limit": 10,
            },
        ))
        skip_auto_remind_filter_item = first_failure_item(skip_auto_remind_filter_payload["data"] or [], assign_remind_marker)
        add_check(
            checks,
            "skip-auto-remind-filter-visible",
            skip_auto_remind_filter_item is not None,
            f"marker={assign_remind_marker}",
        )

        manual_takeover_failure, manual_takeover_marker = create_sensitive_failure(
            session,
            results["requests"],
            actor_headers,
            admin_headers,
            actor_profile,
            sample_id,
            "manual-takeover",
        )
        manual_takeover_failure_id = manual_takeover_failure.get("failureId")
        add_check(
            checks,
            "manual-takeover-failure-created",
            bool(manual_takeover_failure_id),
            f"failureId={manual_takeover_failure_id}, requestId={manual_takeover_failure.get('requestId')}",
        )

        manual_takeover_assign_request_id = f"{sample_id}-manual-takeover-assign"
        manual_takeover_assign_headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-Request-Id": manual_takeover_assign_request_id,
        }
        manual_takeover_assign_body = {
            "reason": f"{sample_id} manual takeover assign",
            "assignedAdminId": self_assignee.get("adminUserId"),
        }
        if escalation_role_code:
            manual_takeover_assign_body["escalationRoleCode"] = escalation_role_code
        require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-manual-takeover-assign",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{manual_takeover_failure_id}/assign",
            headers=manual_takeover_assign_headers,
            json=manual_takeover_assign_body,
        ))

        manual_takeover_request_id = f"{sample_id}-manual-takeover"
        manual_takeover_headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-Request-Id": manual_takeover_request_id,
        }
        manual_takeover_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-manual-takeover",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{manual_takeover_failure_id}/manual-takeover",
            headers=manual_takeover_headers,
            json={"reason": f"{sample_id} manual takeover"},
        ))
        manual_takeover_item = manual_takeover_payload["data"] or {}
        add_check(
            checks,
            "manual-takeover-action-updates-stage",
            (
                manual_takeover_item.get("autoRemindStage") == "manual_takeover"
                and bool(manual_takeover_item.get("manualTakeoverAt"))
                and manual_takeover_item.get("manualTakeoverByAdminId") == admin_me.get("adminUserId")
                and manual_takeover_item.get("assignmentAcknowledgedByAdminId") == admin_me.get("adminUserId")
            ),
            (
                f"autoRemindStage={manual_takeover_item.get('autoRemindStage')}, "
                f"manualTakeoverAt={manual_takeover_item.get('manualTakeoverAt')}, "
                f"ackBy={manual_takeover_item.get('assignmentAcknowledgedByAdminId')}"
            ),
        )
        manual_takeover_filter_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failures-manual-takeover-filter",
            "GET",
            f"{BASE_URL}/admin/ai/resume/failures",
            headers=admin_headers,
            params={
                "keyword": manual_takeover_marker,
                "autoRemindStage": "manual_takeover",
                "notificationReceiptStatus": "received",
                "limit": 10,
            },
        ))
        manual_takeover_filter_item = first_failure_item(manual_takeover_filter_payload["data"] or [], manual_takeover_marker)
        add_check(
            checks,
            "manual-takeover-filter-visible",
            manual_takeover_filter_item is not None,
            f"marker={manual_takeover_marker}",
        )

        sweep_evaluate_at = (datetime.now() + timedelta(hours=6)).isoformat(timespec="seconds")

        auto_remind_failure, auto_remind_marker = create_sensitive_failure(
            session,
            results["requests"],
            actor_headers,
            admin_headers,
            actor_profile,
            sample_id,
            "auto-remind-sweep",
        )
        auto_remind_failure_id = auto_remind_failure.get("failureId")
        results["summary"]["autoRemindSweepFailureId"] = auto_remind_failure_id
        add_check(
            checks,
            "auto-remind-sweep-failure-created",
            bool(auto_remind_failure_id),
            f"failureId={auto_remind_failure_id}, requestId={auto_remind_failure.get('requestId')}",
        )

        auto_remind_assign_request_id = f"{sample_id}-auto-remind-assign"
        auto_remind_assign_headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-Request-Id": auto_remind_assign_request_id,
        }
        auto_remind_assign_body = {
            "reason": f"{sample_id} auto remind assign",
            "assignedAdminId": self_assignee.get("adminUserId"),
        }
        if escalation_role_code:
            auto_remind_assign_body["escalationRoleCode"] = escalation_role_code
        require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-auto-remind-assign",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{auto_remind_failure_id}/assign",
            headers=auto_remind_assign_headers,
            json=auto_remind_assign_body,
        ))
        require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-auto-remind-record-notification",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{auto_remind_failure_id}/record-notification",
            headers={"Authorization": f"Bearer {admin_token}", "X-Request-Id": f"{sample_id}-auto-remind-notification"},
            json={"reason": f"{sample_id} auto remind record notification", "notificationStatus": "sent"},
        ))

        auto_remind_preview_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-governance-sweep-preview-auto-remind",
            "POST",
            f"{BASE_URL}/admin/ai/resume/governance-sweep/preview",
            headers=admin_headers,
            json={
                "failureIds": [auto_remind_failure_id],
                "evaluateAt": sweep_evaluate_at,
                "reason": f"{sample_id} sweep preview auto remind",
            },
        ))
        auto_remind_preview_data = auto_remind_preview_payload["data"] or {}
        auto_remind_preview_item = ((auto_remind_preview_data.get("items") or []) or [{}])[0]
        add_check(
            checks,
            "governance-sweep-preview-detects-auto-remind",
            (
                auto_remind_preview_data.get("dueCount") == 1
                and auto_remind_preview_item.get("actionType") == "auto_remind"
                and auto_remind_preview_item.get("actionStatus") == "ready"
            ),
            (
                f"dueCount={auto_remind_preview_data.get('dueCount')}, "
                f"actionType={auto_remind_preview_item.get('actionType')}, "
                f"actionStatus={auto_remind_preview_item.get('actionStatus')}"
            ),
        )

        auto_remind_execute_request_id = f"{sample_id}-auto-remind-execute"
        auto_remind_execute_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-governance-sweep-execute-auto-remind",
            "POST",
            f"{BASE_URL}/admin/ai/resume/governance-sweep/execute",
            headers={"Authorization": f"Bearer {admin_token}", "X-Request-Id": auto_remind_execute_request_id},
            json={
                "failureIds": [auto_remind_failure_id],
                "evaluateAt": sweep_evaluate_at,
                "reason": f"{sample_id} execute auto remind",
            },
        ))
        auto_remind_execute_data = auto_remind_execute_payload["data"] or {}
        auto_remind_execute_item = ((auto_remind_execute_data.get("items") or []) or [{}])[0]
        auto_remind_failure_after = auto_remind_execute_item.get("failure") or {}
        add_check(
            checks,
            "governance-sweep-executes-auto-remind",
            (
                auto_remind_execute_data.get("executedCount") == 1
                and auto_remind_execute_item.get("actionType") == "auto_remind"
                and auto_remind_execute_item.get("actionStatus") == "executed"
                and int(auto_remind_failure_after.get("reminderCount") or 0) >= 1
                and auto_remind_failure_after.get("notificationStatus") == "resent"
            ),
            (
                f"executedCount={auto_remind_execute_data.get('executedCount')}, "
                f"actionStatus={auto_remind_execute_item.get('actionStatus')}, "
                f"reminderCount={auto_remind_failure_after.get('reminderCount')}, "
                f"notificationStatus={auto_remind_failure_after.get('notificationStatus')}"
            ),
        )

        timeout_escalation_failure, timeout_escalation_marker = create_sensitive_failure(
            session,
            results["requests"],
            actor_headers,
            admin_headers,
            actor_profile,
            sample_id,
            "timeout-escalation",
        )
        timeout_escalation_failure_id = timeout_escalation_failure.get("failureId")
        results["summary"]["timeoutEscalationFailureId"] = timeout_escalation_failure_id
        add_check(
            checks,
            "timeout-escalation-failure-created",
            bool(timeout_escalation_failure_id),
            f"failureId={timeout_escalation_failure_id}, requestId={timeout_escalation_failure.get('requestId')}",
        )

        timeout_assign_body = {
            "reason": f"{sample_id} timeout escalation assign",
            "assignedAdminId": self_assignee.get("adminUserId"),
        }
        if escalation_role_code:
            timeout_assign_body["escalationRoleCode"] = escalation_role_code
        require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-timeout-escalation-assign",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{timeout_escalation_failure_id}/assign",
            headers={"Authorization": f"Bearer {admin_token}", "X-Request-Id": f"{sample_id}-timeout-escalation-assign"},
            json=timeout_assign_body,
        ))
        require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-timeout-escalation-record-notification",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{timeout_escalation_failure_id}/record-notification",
            headers={"Authorization": f"Bearer {admin_token}", "X-Request-Id": f"{sample_id}-timeout-escalation-notification"},
            json={"reason": f"{sample_id} timeout escalation record notification", "notificationStatus": "sent"},
        ))
        require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-timeout-escalation-remind-1",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{timeout_escalation_failure_id}/remind",
            headers={"Authorization": f"Bearer {admin_token}", "X-Request-Id": f"{sample_id}-timeout-escalation-remind-1"},
            json={"reason": f"{sample_id} timeout escalation remind 1"},
        ))
        require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-timeout-escalation-remind-2",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{timeout_escalation_failure_id}/remind",
            headers={"Authorization": f"Bearer {admin_token}", "X-Request-Id": f"{sample_id}-timeout-escalation-remind-2"},
            json={"reason": f"{sample_id} timeout escalation remind 2"},
        ))

        timeout_preview_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-governance-sweep-preview-timeout-escalation",
            "POST",
            f"{BASE_URL}/admin/ai/resume/governance-sweep/preview",
            headers=admin_headers,
            json={
                "failureIds": [timeout_escalation_failure_id],
                "evaluateAt": sweep_evaluate_at,
                "reason": f"{sample_id} sweep preview timeout escalation",
            },
        ))
        timeout_preview_data = timeout_preview_payload["data"] or {}
        timeout_preview_item = ((timeout_preview_data.get("items") or []) or [{}])[0]
        add_check(
            checks,
            "governance-sweep-preview-detects-timeout-escalation",
            (
                timeout_preview_data.get("timeoutEscalationCount") == 1
                and timeout_preview_item.get("actionType") == "timeout_escalation"
                and timeout_preview_item.get("actionStatus") == "ready"
            ),
            (
                f"timeoutEscalationCount={timeout_preview_data.get('timeoutEscalationCount')}, "
                f"actionType={timeout_preview_item.get('actionType')}, "
                f"actionStatus={timeout_preview_item.get('actionStatus')}"
            ),
        )

        timeout_execute_request_id = f"{sample_id}-timeout-escalation-execute"
        timeout_execute_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-governance-sweep-execute-timeout-escalation",
            "POST",
            f"{BASE_URL}/admin/ai/resume/governance-sweep/execute",
            headers={"Authorization": f"Bearer {admin_token}", "X-Request-Id": timeout_execute_request_id},
            json={
                "failureIds": [timeout_escalation_failure_id],
                "evaluateAt": sweep_evaluate_at,
                "reason": f"{sample_id} execute timeout escalation",
            },
        ))
        timeout_execute_data = timeout_execute_payload["data"] or {}
        timeout_execute_item = ((timeout_execute_data.get("items") or []) or [{}])[0]
        timeout_failure_after = timeout_execute_item.get("failure") or {}
        add_check(
            checks,
            "governance-sweep-executes-timeout-escalation",
            (
                timeout_execute_data.get("executedCount") == 1
                and timeout_execute_item.get("actionType") == "timeout_escalation"
                and timeout_execute_item.get("actionStatus") == "executed"
                and timeout_failure_after.get("handlingStatus") == "escalated"
                and timeout_failure_after.get("escalationRoleCode") == escalation_role_code
            ),
            (
                f"executedCount={timeout_execute_data.get('executedCount')}, "
                f"actionStatus={timeout_execute_item.get('actionStatus')}, "
                f"handlingStatus={timeout_failure_after.get('handlingStatus')}, "
                f"escalationRoleCode={timeout_failure_after.get('escalationRoleCode')}"
            ),
        )

        verify_operation_log(
            session,
            results["requests"],
            admin_headers,
            assign_ack_request_id,
            "ai_resume_assign",
            "assign-operation-log-visible",
            checks,
        )
        verify_operation_log(
            session,
            results["requests"],
            admin_headers,
            record_notification_request_id,
            "ai_resume_record_notification",
            "record-notification-operation-log-visible",
            checks,
        )
        verify_operation_log(
            session,
            results["requests"],
            admin_headers,
            record_receipt_request_id,
            "ai_resume_record_notification_receipt",
            "record-receipt-operation-log-visible",
            checks,
        )
        verify_operation_log(
            session,
            results["requests"],
            admin_headers,
            acknowledge_request_id,
            "ai_resume_acknowledge",
            "acknowledge-operation-log-visible",
            checks,
        )
        verify_operation_log(
            session,
            results["requests"],
            admin_headers,
            remind_request_id,
            "ai_resume_remind",
            "remind-operation-log-visible",
            checks,
        )
        verify_operation_log(
            session,
            results["requests"],
            admin_headers,
            skip_auto_remind_request_id,
            "ai_resume_skip_auto_remind",
            "skip-auto-remind-operation-log-visible",
            checks,
        )
        verify_operation_log(
            session,
            results["requests"],
            admin_headers,
            manual_takeover_request_id,
            "ai_resume_manual_takeover",
            "manual-takeover-operation-log-visible",
            checks,
        )
        verify_operation_log(
            session,
            results["requests"],
            admin_headers,
            auto_remind_execute_request_id,
            "ai_resume_auto_remind",
            "auto-remind-operation-log-visible",
            checks,
        )
        verify_operation_log(
            session,
            results["requests"],
            admin_headers,
            timeout_execute_request_id,
            "ai_resume_timeout_escalation",
            "timeout-escalation-operation-log-visible",
            checks,
        )
    except Exception as exc:
        results["summary"]["fatalError"] = str(exc)

    results_path = sample_root / "results.json"
    results_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary(sample_root, results)

    failed_checks = [check for check in checks if not check["passed"]]
    if results["summary"].get("fatalError") or failed_checks:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
