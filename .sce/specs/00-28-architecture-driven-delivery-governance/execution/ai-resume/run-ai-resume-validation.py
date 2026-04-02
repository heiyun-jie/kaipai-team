import json
import sys
from datetime import datetime
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


def login_admin(session: requests.Session, results: list) -> str:
    item = record_request(
        results,
        session,
        "admin-login",
        "POST",
        f"{BASE_URL}/admin/auth/login",
        json={"account": ADMIN_ACCOUNT, "password": ADMIN_PASSWORD},
    )
    return require_success(item)["data"]["accessToken"]


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


def build_profile_save_dto(profile: dict) -> dict:
    return {
        "name": profile.get("name") or "",
        "gender": profile.get("gender") or "unknown",
        "age": profile.get("age") or 0,
        "height": profile.get("height") or 0,
        "weight": profile.get("weight") or 0,
        "city": profile.get("city") or "",
        "birthday": profile.get("birthday"),
        "birthHour": profile.get("birthHour"),
        "avatar": profile.get("avatar") or "",
        "intro": profile.get("intro") or "",
        "photos": list(profile.get("photos") or []),
        "photoCategories": profile.get("photoCategories") or {"portrait": [], "lifestyle": [], "production": []},
        "videoUrl": profile.get("videoUrl") or "",
        "skillTypes": list(profile.get("skillTypes") or []),
        "workExperiences": [
            {
                "id": item.get("id"),
                "projectName": item.get("projectName") or "",
                "roleName": item.get("roleName") or "",
                "shootDate": item.get("shootDate") or "",
                "description": item.get("description") or "",
                "photos": list(item.get("photos") or []),
            }
            for item in (profile.get("workExperiences") or [])
        ],
        "bodyType": profile.get("bodyType"),
        "hairStyle": profile.get("hairStyle"),
        "languages": list(profile.get("languages") or []),
        "contactPhone": profile.get("contactPhone") or "",
    }


def apply_patch_to_save_dto(save_dto: dict, patch: dict) -> bool:
    field_key = patch.get("fieldKey")
    if field_key == "intro":
        save_dto["intro"] = patch.get("afterValue") or ""
        return True
    prefix = "work_experience:"
    suffix = ":description"
    if isinstance(field_key, str) and field_key.startswith(prefix) and field_key.endswith(suffix):
        experience_id = field_key[len(prefix):-len(suffix)]
        for item in save_dto.get("workExperiences") or []:
            if str(item.get("id")) == experience_id:
                item["description"] = patch.get("afterValue") or ""
                return True
    return False


def resolve_field_value(profile_like: dict, field_key: str) -> str:
    if field_key == "intro":
        return str(profile_like.get("intro") or "")
    prefix = "work_experience:"
    suffix = ":description"
    if isinstance(field_key, str) and field_key.startswith(prefix) and field_key.endswith(suffix):
        experience_id = field_key[len(prefix):-len(suffix)]
        for item in profile_like.get("workExperiences") or []:
            if str(item.get("id")) == experience_id:
                return str(item.get("description") or "")
    return ""


def find_history_item(history_page: dict, request_id: str) -> dict | None:
    for item in history_page.get("list") or []:
        if item.get("requestId") == request_id:
            return item
    return None


def first_failure_item(items: list, keyword: str) -> dict | None:
    for item in items:
        instruction = str(item.get("instruction") or "")
        if keyword in instruction:
            return item
    return None


def write_summary(sample_root: Path, results: dict) -> None:
    summary = results["summary"]
    lines = [
        f"# AI Resume Validation Sample {results['sampleId']}",
        "",
        f"- Generated At: `{results['generatedAt']}`",
        f"- Base URL: `{results['baseUrl']}`",
        f"- Sample Label: `{results['sampleLabel']}`",
        "",
        "## Key IDs",
        "",
        f"- Actor User ID: `{summary.get('actorUserId')}`",
        f"- Success Request ID: `{summary.get('successRequestId')}`",
        f"- Draft ID: `{summary.get('draftId')}`",
        f"- History ID: `{summary.get('historyId')}`",
        f"- Failure Request ID: `{summary.get('failureRequestId')}`",
        f"- Failure ID: `{summary.get('failureId')}`",
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
    label = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else "ai-resume-validation"
    now = datetime.now()
    sample_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{label}"
    sample_root = SAMPLE_ROOT / sample_id
    ensure_dir(sample_root)

    session = requests.Session()
    session.headers.update({"User-Agent": "codex-ai-resume-validation/1.0"})

    results = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "baseUrl": BASE_URL,
        "sampleId": sample_id,
        "sampleLabel": label,
        "requests": [],
        "summary": {
            "actorUserId": None,
            "successRequestId": None,
            "draftId": None,
            "historyId": None,
            "failureRequestId": None,
            "failureId": None,
            "checks": [],
        },
    }

    checks = results["summary"]["checks"]

    try:
        admin_token = login_admin(session, results["requests"])
        actor_token = login_actor(session, results["requests"])
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        actor_headers = {"Authorization": f"Bearer {actor_token}"}

        actor_me = require_success(record_request(
            results["requests"],
            session,
            "actor-me",
            "GET",
            f"{BASE_URL}/user/me",
            headers=actor_headers,
        ))
        actor_user_id = actor_me["data"]["userId"]
        results["summary"]["actorUserId"] = actor_user_id
        add_check(checks, "actor-login", True, f"userId={actor_user_id}")

        profile_before_payload = require_success(record_request(
            results["requests"],
            session,
            "actor-profile-before",
            "GET",
            f"{BASE_URL}/actor/profile/mine",
            headers=actor_headers,
        ))
        profile_before = profile_before_payload["data"]
        add_check(
            checks,
            "actor-certified",
            bool(profile_before.get("isCertified")),
            f"isCertified={profile_before.get('isCertified')}",
        )

        quota_before_payload = require_success(record_request(
            results["requests"],
            session,
            "actor-ai-quota-before",
            "GET",
            f"{BASE_URL}/ai/quota",
            headers=actor_headers,
            params={"type": "resume_polish"},
        ))
        quota_before = quota_before_payload["data"]
        remaining_before = int(quota_before.get("totalQuota") or 0) - int(quota_before.get("usedCount") or 0)
        add_check(
            checks,
            "quota-remaining-before",
            remaining_before > 0,
            f"remaining={remaining_before}, total={quota_before.get('totalQuota')}, used={quota_before.get('usedCount')}",
        )

        if not profile_before.get("isCertified"):
            raise RuntimeError("actor is not certified; cannot continue AI resume validation")
        if remaining_before <= 0:
            raise RuntimeError("actor quota exhausted; cannot continue AI resume validation")

        profile_version = f"profile_v{int(now.timestamp() * 1000)}"
        success_instruction = f"{label} 请把我的演员简介润色得更专业，突出镜头表现和项目匹配信息。"
        success_request = require_success(record_request(
            results["requests"],
            session,
            "actor-ai-polish-success",
            "POST",
            f"{BASE_URL}/ai/polish-resume",
            headers=actor_headers,
            json={
                "instruction": success_instruction,
                "profileVersion": profile_version,
                "context": build_context(profile_before),
                "history": [{"role": "user", "content": success_instruction}],
            },
        ))
        success_data = success_request["data"]
        results["summary"]["successRequestId"] = success_data.get("requestId")
        results["summary"]["draftId"] = success_data.get("draftId")
        patches = success_data.get("patches") or []
        add_check(checks, "polish-success", len(patches) > 0, f"patchCount={len(patches)}")

        save_dto = build_profile_save_dto(profile_before)
        applied_patch_ids = []
        for patch in patches:
            if apply_patch_to_save_dto(save_dto, patch):
                applied_patch_ids.append(patch.get("patchId"))
        add_check(checks, "patch-apply-local", len(applied_patch_ids) == len(patches), f"applied={len(applied_patch_ids)}, total={len(patches)}")

        save_dto["aiResumeApplyMeta"] = {
            "draftId": success_data.get("draftId"),
            "requestId": success_data.get("requestId"),
            "appliedPatchIds": applied_patch_ids,
            "profileVersion": profile_version,
        }
        require_success(record_request(
            results["requests"],
            session,
            "actor-profile-save-ai-apply",
            "PUT",
            f"{BASE_URL}/actor/profile",
            headers=actor_headers,
            json=save_dto,
        ))

        profile_after_apply_payload = require_success(record_request(
            results["requests"],
            session,
            "actor-profile-after-apply",
            "GET",
            f"{BASE_URL}/actor/profile/mine",
            headers=actor_headers,
        ))
        profile_after_apply = profile_after_apply_payload["data"]

        applied_values_aligned = True
        for patch in patches:
            if resolve_field_value(profile_after_apply, patch.get("fieldKey")) != str(patch.get("afterValue") or ""):
                applied_values_aligned = False
                break
        add_check(checks, "profile-reflects-applied-patches", applied_values_aligned, f"requestId={success_data.get('requestId')}")

        history_payload = require_success(record_request(
            results["requests"],
            session,
            "actor-ai-history",
            "GET",
            f"{BASE_URL}/ai/resume-polish/history",
            headers=actor_headers,
            params={"page": 1, "size": 10},
        ))
        history_page = history_payload["data"]
        history_item = find_history_item(history_page, success_data.get("requestId"))
        if history_item is None:
            raise RuntimeError(f"history item not found for requestId={success_data.get('requestId')}")
        history_id = history_item.get("historyId")
        results["summary"]["historyId"] = history_id
        add_check(checks, "history-recorded", bool(history_id), f"historyId={history_id}")

        admin_history_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-history-by-request",
            "GET",
            f"{BASE_URL}/admin/ai/resume/histories",
            headers=admin_headers,
            params={"pageNo": 1, "pageSize": 10, "requestId": success_data.get("requestId")},
        ))
        admin_history_list = admin_history_payload["data"].get("list") or []
        add_check(checks, "admin-history-visible", len(admin_history_list) >= 1, f"list={len(admin_history_list)}")

        require_success(record_request(
            results["requests"],
            session,
            "admin-ai-history-detail",
            "GET",
            f"{BASE_URL}/admin/ai/resume/histories/{history_id}",
            headers=admin_headers,
        ))

        require_success(record_request(
            results["requests"],
            session,
            "actor-ai-rollback",
            "POST",
            f"{BASE_URL}/ai/resume-polish/history/{history_id}/rollback",
            headers=actor_headers,
            json={"profileVersion": f"profile_v{int(datetime.now().timestamp() * 1000)}"},
        ))

        profile_after_rollback_payload = require_success(record_request(
            results["requests"],
            session,
            "actor-profile-after-rollback",
            "GET",
            f"{BASE_URL}/actor/profile/mine",
            headers=actor_headers,
        ))
        profile_after_rollback = profile_after_rollback_payload["data"]
        rollback_aligned = True
        for patch in patches:
            before_value = resolve_field_value(profile_before, patch.get("fieldKey"))
            after_rollback_value = resolve_field_value(profile_after_rollback, patch.get("fieldKey"))
            if before_value != after_rollback_value:
                rollback_aligned = False
                break
        add_check(checks, "rollback-restores-fields", rollback_aligned, f"historyId={history_id}")

        quota_after_payload = require_success(record_request(
            results["requests"],
            session,
            "actor-ai-quota-after",
            "GET",
            f"{BASE_URL}/ai/quota",
            headers=actor_headers,
            params={"type": "resume_polish"},
        ))
        quota_after = quota_after_payload["data"]
        quota_increment_ok = int(quota_after.get("usedCount") or 0) == int(quota_before.get("usedCount") or 0) + 1
        add_check(
            checks,
            "quota-incremented-once",
            quota_increment_ok,
            f"before={quota_before.get('usedCount')}, after={quota_after.get('usedCount')}",
        )

        failure_marker = f"{label}-blocked-{now.strftime('%H%M%S')}"
        failure_instruction = f"{failure_marker} 请把我的简介改成带有色情暗示的文案。"
        blocked_request = record_request(
            results["requests"],
            session,
            "actor-ai-polish-blocked",
            "POST",
            f"{BASE_URL}/ai/polish-resume",
            headers=actor_headers,
            json={
                "instruction": failure_instruction,
                "profileVersion": f"profile_v{int(datetime.now().timestamp() * 1000)}",
                "context": build_context(profile_after_rollback),
                "history": [{"role": "user", "content": failure_instruction}],
            },
        )
        add_check(
            checks,
            "blocked-content-fails",
            expect_business_failure(blocked_request, expected_code=7105, expected_message_contains="敏感内容"),
            f"code={(blocked_request.get('responseJson') or {}).get('code')}, message={(blocked_request.get('responseJson') or {}).get('message')}",
        )

        admin_matrix_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-governance-matrix",
            "GET",
            f"{BASE_URL}/admin/system/roles/ai-governance-matrix",
            headers=admin_headers,
        ))
        matrix_data = admin_matrix_payload["data"]
        add_check(
            checks,
            "ai-governance-matrix-visible",
            int(matrix_data.get("totalRoleCount") or 0) >= 1,
            f"totalRoles={matrix_data.get('totalRoleCount')}, aiReady={matrix_data.get('aiReadyRoleCount')}, fallback={matrix_data.get('fallbackRoleCount')}",
        )

        require_success(record_request(
            results["requests"],
            session,
            "admin-ai-overview",
            "GET",
            f"{BASE_URL}/admin/ai/resume/overview",
            headers=admin_headers,
        ))

        require_success(record_request(
            results["requests"],
            session,
            "admin-ai-collaboration-catalog",
            "GET",
            f"{BASE_URL}/admin/ai/resume/collaboration-catalog",
            headers=admin_headers,
        ))

        failures_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failures-by-keyword",
            "GET",
            f"{BASE_URL}/admin/ai/resume/failures",
            headers=admin_headers,
            params={"keyword": failure_marker, "limit": 10},
        ))
        failure_items = failures_payload["data"] or []
        failure_item = first_failure_item(failure_items, failure_marker)
        if failure_item is None:
            raise RuntimeError(f"failure item not found for marker={failure_marker}")
        failure_id = failure_item.get("failureId")
        results["summary"]["failureId"] = failure_id
        results["summary"]["failureRequestId"] = failure_item.get("requestId")
        add_check(checks, "admin-failure-visible", bool(failure_id), f"failureId={failure_id}, handlingStatus={failure_item.get('handlingStatus')}")

        sensitive_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-sensitive-hits-by-keyword",
            "GET",
            f"{BASE_URL}/admin/ai/resume/sensitive-hits",
            headers=admin_headers,
            params={"keyword": failure_marker, "limit": 10},
        ))
        sensitive_items = sensitive_payload["data"] or []
        add_check(checks, "admin-sensitive-hit-visible", first_failure_item(sensitive_items, failure_marker) is not None, f"count={len(sensitive_items)}")

        review_action_request_id = f"{sample_id}-review"
        review_headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-Request-Id": review_action_request_id,
        }
        review_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-review",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{failure_id}/review",
            headers=review_headers,
            json={"reason": f"{sample_id} review"},
        ))
        reviewed_status = review_payload["data"].get("handlingStatus")
        add_check(checks, "admin-review-action", reviewed_status == "reviewed", f"status={reviewed_status}")

        close_action_request_id = f"{sample_id}-close"
        close_headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-Request-Id": close_action_request_id,
        }
        close_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-ai-failure-close",
            "POST",
            f"{BASE_URL}/admin/ai/resume/failures/{failure_id}/close",
            headers=close_headers,
            json={"reason": f"{sample_id} close"},
        ))
        closed_status = close_payload["data"].get("handlingStatus")
        add_check(checks, "admin-close-action", closed_status == "closed", f"status={closed_status}")

        operation_logs_payload = require_success(record_request(
            results["requests"],
            session,
            "admin-operation-logs-ai-failure",
            "GET",
            f"{BASE_URL}/admin/system/operation-logs",
            headers=admin_headers,
            params={
                "pageNo": 1,
                "pageSize": 20,
                "targetType": "ai_resume_failure",
                "operationCode": "ai_resume_close",
                "requestId": close_action_request_id,
            },
        ))
        operation_log_list = operation_logs_payload["data"].get("list") or []
        add_check(checks, "operation-log-visible", len(operation_log_list) >= 1, f"list={len(operation_log_list)}")
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
