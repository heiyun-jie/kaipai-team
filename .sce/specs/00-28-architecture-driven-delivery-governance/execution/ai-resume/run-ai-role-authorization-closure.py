import json
import sys
from datetime import datetime
from pathlib import Path

import requests


BASE_URL = "http://101.43.57.62/api"
ADMIN_ACCOUNT = "admin"
ADMIN_PASSWORD = "admin123"
SAMPLE_ROOT = Path(__file__).resolve().parent / "samples"

AI_MENU_PERMISSION = "menu.system"
AI_PAGE_PERMISSION = "page.system.ai-resume-governance"
AI_REVIEW_ACTION = "action.system.ai-resume.review"
AI_RESOLVE_ACTION = "action.system.ai-resume.resolve"


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


def add_check(checks: list, name: str, passed: bool, detail: str) -> None:
    checks.append({
        "name": name,
        "passed": passed,
        "detail": detail,
    })


def login_admin(session: requests.Session, results: list, name: str) -> dict:
    item = record_request(
        results,
        session,
        name,
        "POST",
        f"{BASE_URL}/admin/auth/login",
        json={"account": ADMIN_ACCOUNT, "password": ADMIN_PASSWORD},
    )
    return require_success(item)["data"]


def unique(values: list[str]) -> list[str]:
    seen = set()
    ordered = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def write_summary(sample_root: Path, results: dict) -> None:
    summary = results["summary"]
    lines = [
        f"# AI Role Authorization Closure {results['sampleId']}",
        "",
        f"- Generated At: `{results['generatedAt']}`",
        f"- Base URL: `{results['baseUrl']}`",
        f"- Sample Label: `{results['sampleLabel']}`",
        "",
        "## Target",
        "",
        f"- Role ID: `{summary.get('roleId')}`",
        f"- Role Code: `{summary.get('roleCode')}`",
        f"- Stage Before: `{summary.get('stageBefore')}`",
        f"- Stage After: `{summary.get('stageAfter')}`",
        "",
        "## Checks",
        "",
    ]
    for check in summary["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        lines.append(f"- `{status}` {check['name']}: {check['detail']}")
    lines.extend(["", "## Artifacts", "", "- `results.json`"])
    (sample_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def find_role(matrix: dict, role_code: str) -> dict | None:
    normalized = role_code.strip().lower()
    for item in matrix.get("list") or []:
        if str(item.get("roleCode") or "").strip().lower() == normalized:
            return item
    return None


def main() -> int:
    label = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else "ai-role-closure"
    role_code = sys.argv[2].strip() if len(sys.argv) > 2 and sys.argv[2].strip() else "ADMIN"
    now = datetime.now()
    sample_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{label}"
    sample_root = SAMPLE_ROOT / sample_id
    ensure_dir(sample_root)

    session = requests.Session()
    session.headers.update({"User-Agent": "codex-ai-role-authorization-closure/1.0"})

    results = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "baseUrl": BASE_URL,
        "sampleId": sample_id,
        "sampleLabel": label,
        "requests": [],
        "summary": {
            "roleId": None,
            "roleCode": role_code,
            "stageBefore": None,
            "stageAfter": None,
            "checks": [],
        },
    }
    checks = results["summary"]["checks"]

    try:
        first_login = login_admin(session, results["requests"], "admin-login-before")
        admin_token = first_login["accessToken"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        session_permissions_before = set(first_login["adminUserInfo"].get("pagePermissions") or []) | set(
            first_login["adminUserInfo"].get("actionPermissions") or []
        )

        matrix_before_payload = require_success(record_request(
            results["requests"],
            session,
            "matrix-before",
            "GET",
            f"{BASE_URL}/admin/system/roles/ai-governance-matrix",
            headers=admin_headers,
        ))
        matrix_before = matrix_before_payload["data"]
        role_before = find_role(matrix_before, role_code)
        if role_before is None:
            raise RuntimeError(f"role not found in AI matrix: {role_code}")
        results["summary"]["roleId"] = role_before.get("adminRoleId")
        results["summary"]["stageBefore"] = role_before.get("rolloutStage")
        add_check(
            checks,
            "matrix-before-detected",
            True,
            f"role={role_code}, stage={role_before.get('rolloutStage')}, missing={role_before.get('missingPermissions')}",
        )

        role_detail_payload = require_success(record_request(
            results["requests"],
            session,
            "role-detail-before",
            "GET",
            f"{BASE_URL}/admin/system/roles/{role_before['adminRoleId']}",
            headers=admin_headers,
        ))
        role_detail = role_detail_payload["data"]

        merged_menu_permissions = unique([*(role_detail.get("menuPermissions") or []), AI_MENU_PERMISSION])
        merged_page_permissions = unique([*(role_detail.get("pagePermissions") or []), AI_PAGE_PERMISSION])
        merged_action_permissions = unique(
            [*(role_detail.get("actionPermissions") or []), AI_REVIEW_ACTION, AI_RESOLVE_ACTION]
        )
        update_payload = {
            "roleCode": role_detail["roleCode"],
            "roleName": role_detail["roleName"],
            "status": role_detail.get("status"),
            "remark": role_detail.get("remark"),
            "menuPermissions": merged_menu_permissions,
            "pagePermissions": merged_page_permissions,
            "actionPermissions": merged_action_permissions,
        }
        update_request_id = f"{sample_id}-update-role"
        require_success(record_request(
            results["requests"],
            session,
            "role-update",
            "PUT",
            f"{BASE_URL}/admin/system/roles/{role_before['adminRoleId']}",
            headers={"Authorization": f"Bearer {admin_token}", "X-Request-Id": update_request_id},
            json=update_payload,
        ))

        role_detail_after_payload = require_success(record_request(
            results["requests"],
            session,
            "role-detail-after",
            "GET",
            f"{BASE_URL}/admin/system/roles/{role_before['adminRoleId']}",
            headers=admin_headers,
        ))
        role_detail_after = role_detail_after_payload["data"]
        add_check(
            checks,
            "role-detail-updated",
            AI_PAGE_PERMISSION in (role_detail_after.get("pagePermissions") or [])
            and AI_REVIEW_ACTION in (role_detail_after.get("actionPermissions") or [])
            and AI_RESOLVE_ACTION in (role_detail_after.get("actionPermissions") or []),
            f"page={AI_PAGE_PERMISSION in (role_detail_after.get('pagePermissions') or [])}, "
            f"review={AI_REVIEW_ACTION in (role_detail_after.get('actionPermissions') or [])}, "
            f"resolve={AI_RESOLVE_ACTION in (role_detail_after.get('actionPermissions') or [])}",
        )

        matrix_after_payload = require_success(record_request(
            results["requests"],
            session,
            "matrix-after",
            "GET",
            f"{BASE_URL}/admin/system/roles/ai-governance-matrix",
            headers=admin_headers,
        ))
        matrix_after = matrix_after_payload["data"]
        role_after = find_role(matrix_after, role_code)
        if role_after is None:
            raise RuntimeError(f"role missing after update: {role_code}")
        results["summary"]["stageAfter"] = role_after.get("rolloutStage")
        add_check(
            checks,
            "matrix-after-ai-ready",
            bool(role_after.get("aiReady")) and role_after.get("rolloutStage") == "ai_ready",
            f"stage={role_after.get('rolloutStage')}, fallback={role_after.get('reliesOnFallback')}, missing={role_after.get('missingPermissions')}",
        )
        add_check(
            checks,
            "fallback-retired",
            bool(matrix_after.get("canRetireFallback")),
            f"aiReadyRoleCount={matrix_after.get('aiReadyRoleCount')}, fallbackRoleCount={matrix_after.get('fallbackRoleCount')}, canRetireFallback={matrix_after.get('canRetireFallback')}",
        )

        second_login = login_admin(session, results["requests"], "admin-login-after")
        second_permissions = set(second_login["adminUserInfo"].get("pagePermissions") or []) | set(
            second_login["adminUserInfo"].get("actionPermissions") or []
        )
        add_check(
            checks,
            "session-permissions-refreshed",
            AI_PAGE_PERMISSION in second_permissions
            and AI_REVIEW_ACTION in second_permissions
            and AI_RESOLVE_ACTION in second_permissions,
            f"beforeHasPage={AI_PAGE_PERMISSION in session_permissions_before}, afterHasPage={AI_PAGE_PERMISSION in second_permissions}, "
            f"afterHasReview={AI_REVIEW_ACTION in second_permissions}, afterHasResolve={AI_RESOLVE_ACTION in second_permissions}",
        )

        second_admin_headers = {"Authorization": f"Bearer {second_login['accessToken']}"}
        require_success(record_request(
            results["requests"],
            session,
            "ai-overview-after-closure",
            "GET",
            f"{BASE_URL}/admin/ai/resume/overview",
            headers=second_admin_headers,
        ))

        operation_log_payload = require_success(record_request(
            results["requests"],
            session,
            "role-update-operation-log",
            "GET",
            f"{BASE_URL}/admin/system/operation-logs",
            headers=second_admin_headers,
            params={
                "pageNo": 1,
                "pageSize": 20,
                "targetType": "admin_role",
                "operationCode": "edit",
                "requestId": update_request_id,
            },
        ))
        add_check(
            checks,
            "role-update-operation-log-visible",
            (operation_log_payload["data"].get("total") or 0) >= 1,
            f"total={operation_log_payload['data'].get('total')}, requestId={update_request_id}",
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
