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
        raise RuntimeError(f"{label} failed: HTTP {item.get('status')} / code {payload.get('code')} / message {payload.get('message')}")
    return payload


def expect_business_failure(item: dict, *, expected_message_contains: str | None = None) -> bool:
    payload = item.get("responseJson") or {}
    if item.get("status") != 200 or payload.get("code") == 200:
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


def role_switch(session: requests.Session, results: list, actor_headers: dict, user_type: int, name: str) -> dict:
    item = record_request(
        results,
        session,
        name,
        "PUT",
        f"{BASE_URL}/user/role",
        headers=actor_headers,
        json={"userType": user_type},
    )
    return require_success(item)


def write_summary(sample_root: Path, results: dict) -> None:
    summary = results["summary"]
    lines = [
        f"# Recruit Authenticated Sample {results['sampleId']}",
        "",
        f"- Generated At: `{results['generatedAt']}`",
        f"- Base URL: `{results['baseUrl']}`",
        f"- Sample Label: `{results['sampleLabel']}`",
        "",
        "## Entity IDs",
        "",
        f"- Actor User ID: `{summary.get('actorUserId')}`",
        f"- Project ID: `{summary.get('projectId')}`",
        f"- Role ID: `{summary.get('roleId')}`",
        f"- Apply ID: `{summary.get('applyId')}`",
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
    label = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else "auth-recruit-sample"
    now = datetime.now()
    sample_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{label}"
    sample_root = SAMPLE_ROOT / sample_id
    ensure_dir(sample_root)

    session = requests.Session()
    session.headers.update({"User-Agent": "codex-recruit-authenticated-sample/1.0"})

    results = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "baseUrl": BASE_URL,
        "sampleId": sample_id,
        "sampleLabel": label,
        "requests": [],
        "summary": {
            "actorUserId": None,
            "projectId": None,
            "roleId": None,
            "applyId": None,
            "checks": [],
        },
    }

    checks = results["summary"]["checks"]
    actor_headers = {}
    admin_headers = {}

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

        role_switch(session, results["requests"], actor_headers, 2, "switch-to-crew")
        company_name = f"Spec剧组{now.strftime('%m%d%H%M%S')}"
        company_payload = {
            "avatar": "https://example.com/spec-recruit-avatar.png",
            "companyName": company_name,
            "contactName": "Spec Crew",
            "contactPhone": USER_PHONE,
            "remark": f"{label} company profile",
            "location": "上海",
            "companyType": "影视制作公司",
            "teamScale": "5-15人",
            "focusDirection": "都市短剧",
            "representativeWorks": f"{label} works",
            "cooperationNeed": f"{label} cooperation",
            "officeAddress": "上海徐汇",
        }
        company_save = record_request(
            results["requests"],
            session,
            "crew-save-company",
            "PUT",
            f"{BASE_URL}/company",
            headers=actor_headers,
            json=company_payload,
        )
        add_check(
            checks,
            "save-company",
            company_save["status"] == 200 and (company_save["responseJson"] or {}).get("code") == 200,
            f"message={(company_save['responseJson'] or {}).get('message')}",
        )
        company_mine = record_request(
            results["requests"],
            session,
            "crew-company-mine",
            "GET",
            f"{BASE_URL}/company/mine",
            headers=actor_headers,
        )
        require_success(company_mine)

        project_payload = {
            "title": label,
            "description": f"{label} description",
            "location": "上海",
            "status": 1,
            "type": "短剧项目",
            "shootingDate": "2026-04-10 - 2026-04-20",
            "coverImage": "https://example.com/spec-project-cover.png",
        }
        project_create = require_success(record_request(
            results["requests"],
            session,
            "crew-create-project",
            "POST",
            f"{BASE_URL}/project",
            headers=actor_headers,
            json=project_payload,
        ))
        project_id = project_create["data"]["id"]
        results["summary"]["projectId"] = project_id

        require_success(record_request(
            results["requests"],
            session,
            "crew-project-mine",
            "GET",
            f"{BASE_URL}/project/mine",
            headers=actor_headers,
            params={"page": 1, "size": 20, "keyword": label},
        ))

        role_payload = {
            "projectId": project_id,
            "roleName": f"{label}-role",
            "gender": "不限",
            "minAge": 18,
            "maxAge": 30,
            "requirement": f"{label} requirement",
            "fee": "300/天",
            "deadline": "2026-04-30",
            "coverImage": "https://example.com/spec-role-cover.png",
        }
        role_create = require_success(record_request(
            results["requests"],
            session,
            "crew-create-role",
            "POST",
            f"{BASE_URL}/role",
            headers=actor_headers,
            json=role_payload,
        ))
        role_id = role_create["data"]["id"]
        results["summary"]["roleId"] = role_id

        crew_roles = require_success(record_request(
            results["requests"],
            session,
            "crew-roles-by-project",
            "GET",
            f"{BASE_URL}/role/project/{project_id}",
            headers=actor_headers,
            params={"page": 1, "size": 20},
        ))
        add_check(
            checks,
            "roles-by-project",
            crew_roles["data"]["total"] >= 1,
            f"total={crew_roles['data']['total']}",
        )

        role_switch(session, results["requests"], actor_headers, 1, "switch-back-to-actor")

        actor_search_before = require_success(record_request(
            results["requests"],
            session,
            "actor-search-before-apply",
            "GET",
            f"{BASE_URL}/role/search",
            headers=actor_headers,
            params={"page": 1, "size": 20, "keyword": label},
        ))
        before_list = actor_search_before["data"]["list"]
        before_total = actor_search_before["data"]["total"]
        before_project_id = before_list[0].get("projectId") if before_list else None
        add_check(
            checks,
            "search-total-aligned",
            before_total >= len(before_list) and before_total > 0,
            f"total={before_total}, list={len(before_list)}",
        )
        add_check(
            checks,
            "search-project-id-aligned",
            before_project_id == project_id,
            f"expected={project_id}, actual={before_project_id}",
        )

        role_detail = require_success(record_request(
            results["requests"],
            session,
            "actor-role-detail",
            "GET",
            f"{BASE_URL}/role/{role_id}",
            headers=actor_headers,
        ))
        add_check(
            checks,
            "detail-project-id-aligned",
            role_detail["data"].get("projectId") == project_id,
            f"detailProjectId={role_detail['data'].get('projectId')}",
        )

        apply_submit = require_success(record_request(
            results["requests"],
            session,
            "actor-apply-submit",
            "POST",
            f"{BASE_URL}/apply",
            headers=actor_headers,
            json={"roleId": role_id, "remark": f"{label} apply"},
        ))
        apply_id = apply_submit["data"]["id"]
        results["summary"]["applyId"] = apply_id

        my_applies = require_success(record_request(
            results["requests"],
            session,
            "actor-my-applies",
            "GET",
            f"{BASE_URL}/apply/mine",
            headers=actor_headers,
            params={"page": 1, "size": 20},
        ))
        add_check(
            checks,
            "my-applies-total-aligned",
            my_applies["data"]["total"] >= len(my_applies["data"]["list"]) and my_applies["data"]["total"] > 0,
            f"total={my_applies['data']['total']}, list={len(my_applies['data']['list'])}",
        )

        admin_projects = require_success(record_request(
            results["requests"],
            session,
            "admin-projects",
            "GET",
            f"{BASE_URL}/admin/recruit/projects",
            headers=admin_headers,
            params={"pageNo": 1, "pageSize": 20, "keyword": label},
        ))
        admin_roles = require_success(record_request(
            results["requests"],
            session,
            "admin-roles",
            "GET",
            f"{BASE_URL}/admin/recruit/roles",
            headers=admin_headers,
            params={"pageNo": 1, "pageSize": 20, "keyword": label},
        ))
        admin_applies = require_success(record_request(
            results["requests"],
            session,
            "admin-applies",
            "GET",
            f"{BASE_URL}/admin/recruit/applies",
            headers=admin_headers,
            params={"pageNo": 1, "pageSize": 20, "keyword": label},
        ))
        add_check(checks, "admin-projects-visible", admin_projects["data"]["total"] >= 1, f"total={admin_projects['data']['total']}")
        add_check(checks, "admin-roles-visible", admin_roles["data"]["total"] >= 1, f"total={admin_roles['data']['total']}")
        add_check(checks, "admin-applies-visible", admin_applies["data"]["total"] >= 1, f"total={admin_applies['data']['total']}")

        require_success(record_request(
            results["requests"],
            session,
            "admin-pause-role",
            "POST",
            f"{BASE_URL}/admin/recruit/roles/{role_id}/status",
            headers=admin_headers,
            json={"status": "paused", "reason": f"{label} pause"},
        ))
        search_after_pause = require_success(record_request(
            results["requests"],
            session,
            "actor-search-after-role-pause",
            "GET",
            f"{BASE_URL}/role/search",
            headers=actor_headers,
            params={"page": 1, "size": 20, "keyword": label},
        ))
        add_check(checks, "pause-hides-role", len(search_after_pause["data"]["list"]) == 0, f"list={len(search_after_pause['data']['list'])}")

        require_success(record_request(
            results["requests"],
            session,
            "admin-resume-role",
            "POST",
            f"{BASE_URL}/admin/recruit/roles/{role_id}/status",
            headers=admin_headers,
            json={"status": "recruiting", "reason": f"{label} resume"},
        ))
        search_after_resume = require_success(record_request(
            results["requests"],
            session,
            "actor-search-after-role-resume",
            "GET",
            f"{BASE_URL}/role/search",
            headers=actor_headers,
            params={"page": 1, "size": 20, "keyword": label},
        ))
        add_check(checks, "resume-restores-role", len(search_after_resume["data"]["list"]) >= 1, f"list={len(search_after_resume['data']['list'])}")

        require_success(record_request(
            results["requests"],
            session,
            "admin-end-project",
            "POST",
            f"{BASE_URL}/admin/recruit/projects/{project_id}/status",
            headers=admin_headers,
            json={"status": 2, "reason": f"{label} end project"},
        ))
        search_after_project_end = require_success(record_request(
            results["requests"],
            session,
            "actor-search-after-project-end",
            "GET",
            f"{BASE_URL}/role/search",
            headers=actor_headers,
            params={"page": 1, "size": 20, "keyword": label},
        ))
        add_check(checks, "project-end-hides-role", len(search_after_project_end["data"]["list"]) == 0, f"list={len(search_after_project_end['data']['list'])}")

        resume_role_while_project_end = record_request(
            results["requests"],
            session,
            "admin-resume-role-while-project-ended",
            "POST",
            f"{BASE_URL}/admin/recruit/roles/{role_id}/status",
            headers=admin_headers,
            json={"status": "recruiting", "reason": f"{label} should fail"},
        )
        add_check(
            checks,
            "project-end-blocks-role-resume",
            expect_business_failure(resume_role_while_project_end, expected_message_contains="关联项目已结束"),
            f"message={(resume_role_while_project_end['responseJson'] or {}).get('message')}",
        )

        require_success(record_request(
            results["requests"],
            session,
            "admin-resume-project",
            "POST",
            f"{BASE_URL}/admin/recruit/projects/{project_id}/status",
            headers=admin_headers,
            json={"status": 1, "reason": f"{label} resume project"},
        ))
        search_after_project_resume = require_success(record_request(
            results["requests"],
            session,
            "actor-search-after-project-resume",
            "GET",
            f"{BASE_URL}/role/search",
            headers=actor_headers,
            params={"page": 1, "size": 20, "keyword": label},
        ))
        add_check(
            checks,
            "project-resume-does-not-auto-resume-role",
            len(search_after_project_resume["data"]["list"]) == 0,
            f"list={len(search_after_project_resume['data']['list'])}",
        )

        require_success(record_request(
            results["requests"],
            session,
            "admin-resume-role-after-project-resume",
            "POST",
            f"{BASE_URL}/admin/recruit/roles/{role_id}/status",
            headers=admin_headers,
            json={"status": "recruiting", "reason": f"{label} final resume"},
        ))
        search_after_final_resume = require_success(record_request(
            results["requests"],
            session,
            "actor-search-after-final-role-resume",
            "GET",
            f"{BASE_URL}/role/search",
            headers=actor_headers,
            params={"page": 1, "size": 20, "keyword": label},
        ))
        add_check(
            checks,
            "final-role-resume-restores-visibility",
            len(search_after_final_resume["data"]["list"]) >= 1,
            f"list={len(search_after_final_resume['data']['list'])}",
        )

        role_switch(session, results["requests"], actor_headers, 2, "switch-to-crew-for-apply-list")
        role_applies = require_success(record_request(
            results["requests"],
            session,
            "crew-role-applies",
            "GET",
            f"{BASE_URL}/apply/role/{role_id}",
            headers=actor_headers,
            params={"page": 1, "size": 20},
        ))
        add_check(
            checks,
            "role-applies-query-clean",
            role_applies["data"]["total"] >= 1,
            f"total={role_applies['data']['total']}",
        )
        role_switch(session, results["requests"], actor_headers, 1, "restore-actor-role")
    except Exception as exc:
        results["summary"]["fatalError"] = str(exc)
    finally:
        if actor_headers:
            try:
                role_switch(session, results["requests"], actor_headers, 1, "final-restore-actor-role")
            except Exception:
                pass

    results_path = sample_root / "results.json"
    results_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary(sample_root, results)

    failed_checks = [check for check in checks if not check["passed"]]
    if results["summary"].get("fatalError") or failed_checks:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
