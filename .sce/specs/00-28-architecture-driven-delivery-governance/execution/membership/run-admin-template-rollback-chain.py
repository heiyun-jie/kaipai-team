import json
import os
import shlex
import sys
from datetime import datetime

import paramiko
import requests


BASE_URL = "http://101.43.57.62/api"
ADMIN_ACCOUNT = "admin"
ADMIN_PASSWORD = "admin123"
USER_PHONE = "13800138000"
ACTOR_USER_ID = 10000
TEMPLATE_ID = 1
SCENE_KEY = "general"
REMOTE_HOST = "101.43.57.62"
REMOTE_USER = "kaipaile"
REMOTE_PASSWORD = "kaipaile888"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def parse_json_response(response: requests.Response) -> dict:
    try:
        return response.json()
    except Exception as exc:
        raise RuntimeError(f"invalid json from {response.request.method} {response.url}: {exc}") from exc


def record_request(results: list, session: requests.Session, name: str, method: str, url: str, **kwargs) -> dict:
    item = {"name": name, "method": method, "url": url}
    if "headers" in kwargs and kwargs["headers"] is not None:
        item["requestHeaders"] = kwargs["headers"]
    if "json" in kwargs and kwargs["json"] is not None:
        item["requestJson"] = kwargs["json"]
    response = session.request(method, url, timeout=30, **kwargs)
    item["status"] = response.status_code
    item["responseHeaders"] = dict(response.headers)
    item["responseText"] = response.text
    item["responseJson"] = parse_json_response(response)
    results.append(item)
    return item


def require_ok(item: dict) -> dict:
    payload = item.get("responseJson") or {}
    if item.get("status") != 200 or payload.get("code") != 200:
        raise RuntimeError(f"request failed: {item['name']} -> HTTP {item.get('status')} / code {payload.get('code')}")
    return payload


def login_admin(session: requests.Session, results: list) -> tuple[str, dict]:
    item = record_request(
        results,
        session,
        "admin-login",
        "POST",
        f"{BASE_URL}/admin/auth/login",
        json={"account": ADMIN_ACCOUNT, "password": ADMIN_PASSWORD},
    )
    payload = require_ok(item)["data"]
    return payload["accessToken"], payload["adminUserInfo"]


def login_user(session: requests.Session, results: list) -> str:
    send_code = record_request(
        results,
        session,
        "user-send-code",
        "POST",
        f"{BASE_URL}/auth/sendCode",
        json={"phone": USER_PHONE},
    )
    code = require_ok(send_code)["data"]
    login = record_request(
        results,
        session,
        "user-login",
        "POST",
        f"{BASE_URL}/auth/login",
        json={"phone": USER_PHONE, "code": str(code)},
    )
    return require_ok(login)["data"]["token"]


def remote_mysql(sql: str) -> str:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(REMOTE_HOST, username=REMOTE_USER, password=REMOTE_PASSWORD, timeout=20)
    compact_sql = " ".join(line.strip() for line in sql.splitlines() if line.strip())
    command = (
        f"echo '{REMOTE_PASSWORD}' | sudo -S "
        f"docker exec kaipai-mysql mysql --default-character-set=utf8mb4 -uroot -proot123456 -e {shlex.quote(compact_sql)}"
    )
    stdin, stdout, stderr = client.exec_command(command, timeout=120)
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    client.close()
    return out if not err.strip() else out + "\n[stderr]\n" + err


def find_request(results: list, name: str) -> dict:
    for item in results:
        if item["name"] == name:
            return item
    raise KeyError(name)


def parse_json_text(raw: str) -> dict:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except Exception:
        return {}
    return value if isinstance(value, dict) else {}


def extract_theme_node(raw: str) -> dict:
    parsed = parse_json_text(raw)
    if isinstance(parsed.get("themeColors"), dict):
        return dict(parsed["themeColors"])
    return dict(parsed)


def stage_summary(level_info: dict, personalization: dict, template_detail: dict, publish_logs: list) -> dict:
    profile = personalization.get("profile") or {}
    template = profile.get("template") or {}
    theme = personalization.get("theme") or {}
    return {
        "membershipTier": level_info.get("membershipTier"),
        "level": level_info.get("level"),
        "reasonCodes": ((level_info.get("shareCapability") or {}).get("reasonCodes") or []),
        "templateStatus": template_detail.get("status"),
        "templateName": template.get("name"),
        "templateRequiredLevel": template.get("requiredLevel"),
        "templateThemePrimary": ((template.get("themeColors") or {}).get("primary")),
        "personalizationThemeId": theme.get("themeId"),
        "personalizationThemePrimary": theme.get("primary"),
        "artifactCount": len(personalization.get("artifacts") or []),
        "publishVersion": publish_logs[0].get("publishVersion") if publish_logs else None,
        "publishLogId": publish_logs[0].get("publishLogId") if publish_logs else None,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: run-admin-template-rollback-chain.py <sample-root>")
        return 1

    sample_root = os.path.abspath(sys.argv[1])
    capture_root = os.path.join(sample_root, "captures")
    ensure_dir(capture_root)

    now = datetime.now()
    restore_publish_version = f"SMOKE_RESTORE_{now.strftime('%Y%m%d_%H%M%S')}"
    rollback_note = f"spec rollback frontend verification {now.strftime('%Y-%m-%d %H:%M:%S')}"
    restore_note = f"spec restore after rollback verification {now.strftime('%Y-%m-%d %H:%M:%S')}"

    session = requests.Session()
    session.headers.update({"User-Agent": "codex-admin-template-rollback-chain/1.0"})

    results = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "baseUrl": BASE_URL,
        "actorUserId": ACTOR_USER_ID,
        "templateId": TEMPLATE_ID,
        "sceneKey": SCENE_KEY,
        "restorePublishVersion": restore_publish_version,
        "requests": [],
        "payloads": {},
    }

    admin_token, admin_session = login_admin(session, results["requests"])
    user_token = login_user(session, results["requests"])
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}
    results["adminSession"] = admin_session

    before_calls = [
        ("before-admin-template-detail", "GET", f"{BASE_URL}/admin/content/templates/{TEMPLATE_ID}", admin_headers, None),
        ("before-admin-publish-logs", "GET", f"{BASE_URL}/admin/content/publish-logs?pageNo=1&pageSize=20&templateId={TEMPLATE_ID}", admin_headers, None),
        ("before-level-info", "GET", f"{BASE_URL}/level/info", user_headers, None),
        ("before-card-scene-templates", "GET", f"{BASE_URL}/card/scene-templates", user_headers, None),
        ("before-card-personalization", "GET", f"{BASE_URL}/card/personalization?actorId={ACTOR_USER_ID}&scene={SCENE_KEY}&loadFortune=true", user_headers, None),
    ]
    for name, method, url, headers, body in before_calls:
        require_ok(record_request(results["requests"], session, name, method, url, headers=headers, json=body))

    before_publish_logs = (find_request(results["requests"], "before-admin-publish-logs")["responseJson"]["data"] or {}).get("list") or []
    if not before_publish_logs:
        raise RuntimeError("publish logs are empty; rollback sourceVersion cannot be resolved")
    source_version = before_publish_logs[0]["publishVersion"]
    results["payloads"]["rollback"] = {
        "templateId": TEMPLATE_ID,
        "sourceVersion": source_version,
        "publishNote": rollback_note,
    }
    results["payloads"]["restorePublish"] = {
        "templateId": TEMPLATE_ID,
        "publishVersion": restore_publish_version,
        "publishNote": restore_note,
    }

    rollback_item = record_request(
        results["requests"],
        session,
        "admin-template-rollback",
        "POST",
        f"{BASE_URL}/admin/content/templates/{TEMPLATE_ID}/rollback",
        headers=admin_headers,
        json=results["payloads"]["rollback"],
    )
    require_ok(rollback_item)

    after_rollback_calls = [
        ("after-rollback-admin-template-detail", "GET", f"{BASE_URL}/admin/content/templates/{TEMPLATE_ID}", admin_headers, None),
        ("after-rollback-admin-publish-logs", "GET", f"{BASE_URL}/admin/content/publish-logs?pageNo=1&pageSize=20&templateId={TEMPLATE_ID}", admin_headers, None),
        ("after-rollback-level-info", "GET", f"{BASE_URL}/level/info", user_headers, None),
        ("after-rollback-card-scene-templates", "GET", f"{BASE_URL}/card/scene-templates", user_headers, None),
        ("after-rollback-card-personalization", "GET", f"{BASE_URL}/card/personalization?actorId={ACTOR_USER_ID}&scene={SCENE_KEY}&loadFortune=true", user_headers, None),
    ]
    for name, method, url, headers, body in after_rollback_calls:
        require_ok(record_request(results["requests"], session, name, method, url, headers=headers, json=body))

    restore_item = record_request(
        results["requests"],
        session,
        "admin-template-restore-publish",
        "POST",
        f"{BASE_URL}/admin/content/templates/{TEMPLATE_ID}/publish",
        headers=admin_headers,
        json=results["payloads"]["restorePublish"],
    )
    require_ok(restore_item)

    after_restore_calls = [
        ("after-restore-admin-template-detail", "GET", f"{BASE_URL}/admin/content/templates/{TEMPLATE_ID}", admin_headers, None),
        ("after-restore-admin-publish-logs", "GET", f"{BASE_URL}/admin/content/publish-logs?pageNo=1&pageSize=20&templateId={TEMPLATE_ID}", admin_headers, None),
        ("after-restore-level-info", "GET", f"{BASE_URL}/level/info", user_headers, None),
        ("after-restore-card-scene-templates", "GET", f"{BASE_URL}/card/scene-templates", user_headers, None),
        ("after-restore-card-personalization", "GET", f"{BASE_URL}/card/personalization?actorId={ACTOR_USER_ID}&scene={SCENE_KEY}&loadFortune=true", user_headers, None),
    ]
    for name, method, url, headers, body in after_restore_calls:
        require_ok(record_request(results["requests"], session, name, method, url, headers=headers, json=body))

    before_template_detail = find_request(results["requests"], "before-admin-template-detail")["responseJson"]["data"]
    before_level_info = find_request(results["requests"], "before-level-info")["responseJson"]["data"]
    before_personalization = find_request(results["requests"], "before-card-personalization")["responseJson"]["data"]

    after_rollback_template_detail = find_request(results["requests"], "after-rollback-admin-template-detail")["responseJson"]["data"]
    after_rollback_publish_logs = (find_request(results["requests"], "after-rollback-admin-publish-logs")["responseJson"]["data"] or {}).get("list") or []
    after_rollback_level_info = find_request(results["requests"], "after-rollback-level-info")["responseJson"]["data"]
    after_rollback_personalization = find_request(results["requests"], "after-rollback-card-personalization")["responseJson"]["data"]
    after_rollback_scene_templates = find_request(results["requests"], "after-rollback-card-scene-templates")["responseJson"]["data"]

    after_restore_template_detail = find_request(results["requests"], "after-restore-admin-template-detail")["responseJson"]["data"]
    after_restore_publish_logs = (find_request(results["requests"], "after-restore-admin-publish-logs")["responseJson"]["data"] or {}).get("list") or []
    after_restore_level_info = find_request(results["requests"], "after-restore-level-info")["responseJson"]["data"]
    after_restore_personalization = find_request(results["requests"], "after-restore-card-personalization")["responseJson"]["data"]
    after_restore_scene_templates = find_request(results["requests"], "after-restore-card-scene-templates")["responseJson"]["data"]

    before_summary = stage_summary(before_level_info, before_personalization, before_template_detail, before_publish_logs)
    after_rollback_summary = stage_summary(after_rollback_level_info, after_rollback_personalization, after_rollback_template_detail, after_rollback_publish_logs)
    after_restore_summary = stage_summary(after_restore_level_info, after_restore_personalization, after_restore_template_detail, after_restore_publish_logs)

    results["summary"] = {
        "before": before_summary,
        "afterRollback": after_rollback_summary,
        "afterRestore": after_restore_summary,
        "afterRollbackSceneTemplates": {
            "count": len(after_rollback_scene_templates or []),
            "generalPrimary": next(
                (
                    ((item.get("themeColors") or {}).get("primary"))
                    for item in (after_rollback_scene_templates or [])
                    if item.get("sceneKey") == SCENE_KEY
                ),
                None,
            ),
            "generalName": next(
                (item.get("name") for item in (after_rollback_scene_templates or []) if item.get("sceneKey") == SCENE_KEY),
                None,
            ),
        },
        "afterRestoreSceneTemplates": {
            "count": len(after_restore_scene_templates or []),
            "generalPrimary": next(
                (
                    ((item.get("themeColors") or {}).get("primary"))
                    for item in (after_restore_scene_templates or [])
                    if item.get("sceneKey") == SCENE_KEY
                ),
                None,
            ),
            "generalName": next(
                (item.get("name") for item in (after_restore_scene_templates or []) if item.get("sceneKey") == SCENE_KEY),
                None,
            ),
        },
        "templateThemeBefore": extract_theme_node(before_template_detail.get("baseThemeJson")),
        "templateThemeAfterRollback": extract_theme_node(after_rollback_template_detail.get("baseThemeJson")),
        "templateThemeAfterRestore": extract_theme_node(after_restore_template_detail.get("baseThemeJson")),
    }

    db_sql = f"""
USE kaipai_dev;
SELECT template_id,template_code,template_name,scene_key,status,base_theme_json,last_update
FROM card_scene_template
WHERE template_id={TEMPLATE_ID};
SELECT publish_log_id,template_id,publish_version,source_version,target_version,action_type,publish_note,published_by,published_at
FROM template_publish_log
WHERE template_id={TEMPLATE_ID}
ORDER BY publish_log_id DESC
LIMIT 8;
SELECT operation_log_id,admin_user_id,admin_user_name,module_code,operation_code,target_type,target_id,operation_result,create_time
FROM admin_operation_log
WHERE module_code='content' AND target_id={TEMPLATE_ID}
ORDER BY operation_log_id DESC
LIMIT 12;
"""
    db_output = remote_mysql(db_sql.strip())

    with open(os.path.join(capture_root, "admin-template-rollback-chain-results.json"), "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)
    with open(os.path.join(capture_root, "admin-template-rollback-chain-db.txt"), "w", encoding="utf-8", newline="\n") as file:
        file.write(db_output)

    summary_lines = [
        "# Admin Template Rollback Chain Summary",
        "",
        f"- Generated At: {results['generatedAt']}",
        f"- Base URL: {BASE_URL}",
        f"- Actor User ID: {ACTOR_USER_ID}",
        f"- Template ID: {TEMPLATE_ID}",
        f"- Rollback Source Version: {source_version}",
        f"- Restore Publish Version: {restore_publish_version}",
        "",
        "## Before",
        "",
        f"- Template Status: {before_summary['templateStatus']}",
        f"- Template Name: {before_summary['templateName']}",
        f"- Template Theme Primary: {before_summary['templateThemePrimary']}",
        f"- Personalization Theme ID: {before_summary['personalizationThemeId']}",
        f"- Personalization Theme Primary: {before_summary['personalizationThemePrimary']}",
        "",
        "## After Rollback",
        "",
        f"- Template Status: {after_rollback_summary['templateStatus']}",
        f"- Template Name: {after_rollback_summary['templateName']}",
        f"- Template Theme Primary: {after_rollback_summary['templateThemePrimary']}",
        f"- Personalization Theme ID: {after_rollback_summary['personalizationThemeId']}",
        f"- Personalization Theme Primary: {after_rollback_summary['personalizationThemePrimary']}",
        f"- Scene Templates Count: {results['summary']['afterRollbackSceneTemplates']['count']}",
        f"- General Scene Name: {results['summary']['afterRollbackSceneTemplates']['generalName']}",
        f"- General Scene Primary: {results['summary']['afterRollbackSceneTemplates']['generalPrimary']}",
        "",
        "## After Restore",
        "",
        f"- Template Status: {after_restore_summary['templateStatus']}",
        f"- Template Name: {after_restore_summary['templateName']}",
        f"- Template Theme Primary: {after_restore_summary['templateThemePrimary']}",
        f"- Personalization Theme ID: {after_restore_summary['personalizationThemeId']}",
        f"- Personalization Theme Primary: {after_restore_summary['personalizationThemePrimary']}",
        f"- Scene Templates Count: {results['summary']['afterRestoreSceneTemplates']['count']}",
        f"- General Scene Name: {results['summary']['afterRestoreSceneTemplates']['generalName']}",
        f"- General Scene Primary: {results['summary']['afterRestoreSceneTemplates']['generalPrimary']}",
        "",
        "## Evidence Files",
        "",
        "- captures/admin-template-rollback-chain-results.json",
        "- captures/admin-template-rollback-chain-db.txt",
        "",
    ]
    with open(os.path.join(sample_root, "admin-template-rollback-chain-summary.md"), "w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(summary_lines) + "\n")

    print(
        json.dumps(
            {
                "sampleRoot": sample_root,
                "before": before_summary,
                "afterRollback": after_rollback_summary,
                "afterRestore": after_restore_summary,
                "afterRollbackSceneTemplates": results["summary"]["afterRollbackSceneTemplates"],
                "afterRestoreSceneTemplates": results["summary"]["afterRestoreSceneTemplates"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
