import json
import os
import shlex
import subprocess
import sys
from datetime import datetime
import argparse
import hashlib

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
WS_ENDPOINT = "ws://127.0.0.1:9421"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MINI_PROGRAM_CAPTURE_SCRIPT = os.path.join(SCRIPT_DIR, "capture-mini-program-screenshots.js")


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


def load_json_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def run_mini_program_capture(sample_root: str, capture_label: str) -> dict:
    manifest_name = f"mini-program-screenshot-capture-{capture_label}.json"
    command = [
        "node",
        MINI_PROGRAM_CAPTURE_SCRIPT,
        sample_root,
        WS_ENDPOINT,
        BASE_URL,
        USER_PHONE,
        "0",
        str(ACTOR_USER_ID),
        SCENE_KEY,
        capture_label,
        manifest_name,
    ]
    completed = subprocess.run(
        command,
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
        timeout=420,
        check=False,
    )
    result = {
        "captureLabel": capture_label,
        "command": command,
        "returnCode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "manifestName": manifest_name,
    }
    if completed.returncode != 0:
        raise RuntimeError(
            "mini program capture failed: "
            f"label={capture_label}, returnCode={completed.returncode}, stderr={completed.stderr.strip()}"
        )

    manifest_path = os.path.join(sample_root, "captures", manifest_name)
    result["manifestPath"] = manifest_path
    result["manifest"] = load_json_file(manifest_path)
    return result


def stage_capture_summary(capture: dict) -> dict:
    manifest = capture.get("manifest") or {}
    personalization = manifest.get("personalization") or {}
    actor_card_capture = next((item for item in (manifest.get("captures") or []) if item.get("name") == "actor-card"), {})
    detail_capture = next((item for item in (manifest.get("captures") or []) if item.get("name") == "actor-profile-detail"), {})
    invite_capture = next((item for item in (manifest.get("captures") or []) if item.get("name") == "invite-card"), {})
    return {
        "captureLabel": manifest.get("captureLabel"),
        "themeId": personalization.get("themeId"),
        "themePrimary": personalization.get("themePrimary"),
        "reasonCodes": personalization.get("reasonCodes") or [],
        "actorCardPath": actor_card_capture.get("path"),
        "actorCardQuery": actor_card_capture.get("actualQuery"),
        "detailPath": detail_capture.get("path"),
        "detailQuery": detail_capture.get("actualQuery"),
        "invitePath": invite_capture.get("path"),
        "inviteQuery": invite_capture.get("actualQuery"),
        "manifestName": capture.get("manifestName"),
    }


def sha256_file(path: str | None) -> str | None:
    if not path or not os.path.exists(path):
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        while True:
            chunk = file.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest().upper()


def screenshot_hash_map(capture: dict) -> dict:
    manifest = capture.get("manifest") or {}
    mapping = {}
    for item in manifest.get("captures") or []:
        mapping[item.get("name")] = {
            "fileName": item.get("fileName"),
            "sha256": sha256_file(item.get("screenshotPath")),
            "pageDataFileName": item.get("pageDataFileName"),
            "pageDataPath": item.get("pageDataPath"),
        }
    return mapping


def page_data_artifact_lines(results_summary: dict) -> list[str]:
    lines: list[str] = []
    stages = [
        ("before", "Before Rollback"),
        ("afterRollback", "After Rollback"),
        ("afterRestore", "After Restore"),
    ]
    pages = [
        ("actor-card", "actor-card"),
        ("actor-profile-detail", "actor-profile-detail"),
        ("invite-card", "invite-card"),
    ]
    for stage_key, stage_label in stages:
        lines.append(f"- {stage_label}:")
        stage_payload = results_summary["miniProgramScreenshotHashes"].get(stage_key) or {}
        for page_key, page_label in pages:
            page_payload = stage_payload.get(page_key) or {}
            lines.append(
                f"  - `{page_label}` -> `{page_payload.get('pageDataFileName') or 'missing'}`"
            )
    return lines


def fetch_card_runtime_state(session: requests.Session, results: list, user_headers: dict, prefix: str) -> tuple[dict, dict]:
    config_item = record_request(
        results,
        session,
        f"{prefix}-card-config",
        "GET",
        f"{BASE_URL}/card/config?actorId={ACTOR_USER_ID}&scene={SCENE_KEY}",
        headers=user_headers,
    )
    personalization_item = record_request(
        results,
        session,
        f"{prefix}-card-personalization",
        "GET",
        f"{BASE_URL}/card/personalization?actorId={ACTOR_USER_ID}&scene={SCENE_KEY}&loadFortune=true",
        headers=user_headers,
    )
    return require_ok(config_item), require_ok(personalization_item)


def build_card_config_save_payload(config_payload: dict, personalization_payload: dict, enable_fortune_theme: bool) -> dict:
    share_preferences = (personalization_payload.get("profile") or {}).get("sharePreferences") or {}
    return {
        "actorId": ACTOR_USER_ID,
        "sceneKey": SCENE_KEY,
        "layoutVariant": config_payload.get("layoutVariant"),
        "primaryColor": config_payload.get("primaryColor"),
        "accentColor": config_payload.get("accentColor"),
        "backgroundColor": config_payload.get("backgroundColor"),
        "highlightedExperiences": config_payload.get("highlightedExperiences") or [],
        "highlightedPhotos": config_payload.get("highlightedPhotos") or [],
        "tagOrder": config_payload.get("tagOrder") or [],
        "preferredArtifact": share_preferences.get("preferredArtifact") or "miniProgramCard",
        "preferredTone": share_preferences.get("preferredTone"),
        "enableFortuneTheme": enable_fortune_theme,
    }


def save_card_config(
    session: requests.Session,
    results: list,
    user_headers: dict,
    name: str,
    payload: dict,
) -> dict:
    item = record_request(
        results,
        session,
        name,
        "POST",
        f"{BASE_URL}/card/config",
        headers=user_headers,
        json=payload,
    )
    return require_ok(item)["data"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("sample_root")
    parser.add_argument("--force-disable-fortune-theme", action="store_true")
    parser.add_argument("--restore-original-fortune-theme", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sample_root = os.path.abspath(args.sample_root)
    capture_root = os.path.join(sample_root, "captures")
    ensure_dir(capture_root)

    now = datetime.now()
    restore_publish_version = f"SMOKE_RESTORE_MP_{now.strftime('%Y%m%d_%H%M%S')}"
    rollback_note = f"spec rollback mini program verification {now.strftime('%Y-%m-%d %H:%M:%S')}"
    restore_note = f"spec restore after mini program verification {now.strftime('%Y-%m-%d %H:%M:%S')}"

    session = requests.Session()
    session.headers.update({"User-Agent": "codex-admin-template-rollback-mini-program-chain/1.0"})

    results = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "baseUrl": BASE_URL,
        "actorUserId": ACTOR_USER_ID,
        "templateId": TEMPLATE_ID,
        "sceneKey": SCENE_KEY,
        "wsEndpoint": WS_ENDPOINT,
        "restorePublishVersion": restore_publish_version,
        "requests": [],
        "payloads": {},
        "miniProgramCaptures": {},
    }

    admin_token, admin_session = login_admin(session, results["requests"])
    user_token = login_user(session, results["requests"])
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}
    results["adminSession"] = admin_session

    original_config = None
    original_personalization = None
    original_enable_fortune_theme = None
    if args.force_disable_fortune_theme:
        original_config, original_personalization = fetch_card_runtime_state(session, results["requests"], user_headers, "pre-override")
        original_enable_fortune_theme = (
            ((original_personalization.get("profile") or {}).get("sharePreferences") or {}).get("enableFortuneTheme")
        )
        override_payload = build_card_config_save_payload(original_config, original_personalization, False)
        results["payloads"]["forceDisableFortuneTheme"] = override_payload
        save_card_config(
            session,
            results["requests"],
            user_headers,
            "card-config-save-force-disable-fortune-theme",
            override_payload,
        )

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

    results["miniProgramCaptures"]["beforeRollback"] = run_mini_program_capture(sample_root, "before-rollback")

    rolled_back = False
    restored = False
    after_rollback_error: Exception | None = None
    override_restored = False

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
    rolled_back = True

    try:
        after_rollback_calls = [
            ("after-rollback-admin-template-detail", "GET", f"{BASE_URL}/admin/content/templates/{TEMPLATE_ID}", admin_headers, None),
            ("after-rollback-admin-publish-logs", "GET", f"{BASE_URL}/admin/content/publish-logs?pageNo=1&pageSize=20&templateId={TEMPLATE_ID}", admin_headers, None),
            ("after-rollback-level-info", "GET", f"{BASE_URL}/level/info", user_headers, None),
            ("after-rollback-card-scene-templates", "GET", f"{BASE_URL}/card/scene-templates", user_headers, None),
            ("after-rollback-card-personalization", "GET", f"{BASE_URL}/card/personalization?actorId={ACTOR_USER_ID}&scene={SCENE_KEY}&loadFortune=true", user_headers, None),
        ]
        for name, method, url, headers, body in after_rollback_calls:
            require_ok(record_request(results["requests"], session, name, method, url, headers=headers, json=body))

        results["miniProgramCaptures"]["afterRollback"] = run_mini_program_capture(sample_root, "after-rollback")
    except Exception as exc:
        after_rollback_error = exc
    finally:
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
        restored = True

    after_restore_calls = [
        ("after-restore-admin-template-detail", "GET", f"{BASE_URL}/admin/content/templates/{TEMPLATE_ID}", admin_headers, None),
        ("after-restore-admin-publish-logs", "GET", f"{BASE_URL}/admin/content/publish-logs?pageNo=1&pageSize=20&templateId={TEMPLATE_ID}", admin_headers, None),
        ("after-restore-level-info", "GET", f"{BASE_URL}/level/info", user_headers, None),
        ("after-restore-card-scene-templates", "GET", f"{BASE_URL}/card/scene-templates", user_headers, None),
        ("after-restore-card-personalization", "GET", f"{BASE_URL}/card/personalization?actorId={ACTOR_USER_ID}&scene={SCENE_KEY}&loadFortune=true", user_headers, None),
    ]
    for name, method, url, headers, body in after_restore_calls:
        require_ok(record_request(results["requests"], session, name, method, url, headers=headers, json=body))

    results["miniProgramCaptures"]["afterRestore"] = run_mini_program_capture(sample_root, "after-restore")

    if args.force_disable_fortune_theme and args.restore_original_fortune_theme and original_config and original_personalization:
        restore_preference_payload = build_card_config_save_payload(
            original_config,
            original_personalization,
            bool(original_enable_fortune_theme),
        )
        results["payloads"]["restoreFortuneThemePreference"] = restore_preference_payload
        save_card_config(
            session,
            results["requests"],
            user_headers,
            "card-config-save-restore-original-fortune-theme",
            restore_preference_payload,
        )
        override_restored = True

    if after_rollback_error is not None:
        raise after_rollback_error

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
        "forceDisableFortuneTheme": args.force_disable_fortune_theme,
        "restoreOriginalFortuneTheme": args.restore_original_fortune_theme,
        "originalEnableFortuneTheme": original_enable_fortune_theme,
        "before": before_summary,
        "afterRollback": after_rollback_summary,
        "afterRestore": after_restore_summary,
        "miniProgramBefore": stage_capture_summary(results["miniProgramCaptures"]["beforeRollback"]),
        "miniProgramAfterRollback": stage_capture_summary(results["miniProgramCaptures"]["afterRollback"]),
        "miniProgramAfterRestore": stage_capture_summary(results["miniProgramCaptures"]["afterRestore"]),
        "miniProgramScreenshotHashes": {
            "before": screenshot_hash_map(results["miniProgramCaptures"]["beforeRollback"]),
            "afterRollback": screenshot_hash_map(results["miniProgramCaptures"]["afterRollback"]),
            "afterRestore": screenshot_hash_map(results["miniProgramCaptures"]["afterRestore"]),
        },
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
        "rolledBack": rolled_back,
        "restored": restored,
        "overrideRestored": override_restored,
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
LIMIT 10;
SELECT operation_log_id,admin_user_id,admin_user_name,module_code,operation_code,target_type,target_id,operation_result,create_time
FROM admin_operation_log
WHERE module_code='content' AND target_id={TEMPLATE_ID}
ORDER BY operation_log_id DESC
LIMIT 14;
"""
    db_output = remote_mysql(db_sql.strip())

    with open(os.path.join(capture_root, "admin-template-rollback-mini-program-results.json"), "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)
    with open(os.path.join(capture_root, "admin-template-rollback-mini-program-db.txt"), "w", encoding="utf-8", newline="\n") as file:
        file.write(db_output)

    summary_lines = [
        "# Admin Template Rollback Mini Program Summary",
        "",
        f"- Generated At: {results['generatedAt']}",
        f"- Base URL: {BASE_URL}",
        f"- WS Endpoint: {WS_ENDPOINT}",
        f"- Actor User ID: {ACTOR_USER_ID}",
        f"- Template ID: {TEMPLATE_ID}",
        f"- Rollback Source Version: {source_version}",
        f"- Restore Publish Version: {restore_publish_version}",
        f"- Force Disable Fortune Theme: {args.force_disable_fortune_theme}",
        f"- Restore Original Fortune Theme: {args.restore_original_fortune_theme}",
        f"- Original Enable Fortune Theme: {original_enable_fortune_theme}",
        "",
        "## Before Rollback",
        "",
        f"- Template Name: {before_summary['templateName']}",
        f"- Template Theme Primary: {before_summary['templateThemePrimary']}",
        f"- Personalization Theme ID: {before_summary['personalizationThemeId']}",
        f"- Actor Card Query Theme ID: {((results['summary']['miniProgramBefore']['actorCardQuery'] or {}).get('themeId'))}",
        "",
        "## After Rollback",
        "",
        f"- Template Name: {after_rollback_summary['templateName']}",
        f"- Template Theme Primary: {after_rollback_summary['templateThemePrimary']}",
        f"- Personalization Theme ID: {after_rollback_summary['personalizationThemeId']}",
        f"- Scene Template Name: {results['summary']['afterRollbackSceneTemplates']['generalName']}",
        f"- Scene Template Primary: {results['summary']['afterRollbackSceneTemplates']['generalPrimary']}",
        f"- Actor Card Query Theme ID: {((results['summary']['miniProgramAfterRollback']['actorCardQuery'] or {}).get('themeId'))}",
        "",
        "## After Restore",
        "",
        f"- Template Name: {after_restore_summary['templateName']}",
        f"- Template Theme Primary: {after_restore_summary['templateThemePrimary']}",
        f"- Personalization Theme ID: {after_restore_summary['personalizationThemeId']}",
        f"- Scene Template Name: {results['summary']['afterRestoreSceneTemplates']['generalName']}",
        f"- Scene Template Primary: {results['summary']['afterRestoreSceneTemplates']['generalPrimary']}",
        f"- Actor Card Query Theme ID: {((results['summary']['miniProgramAfterRestore']['actorCardQuery'] or {}).get('themeId'))}",
        "",
        "## Observed Page Effect",
        "",
        f"- `actor-card` SHA before/rollback/restore: "
        f"{(((results['summary']['miniProgramScreenshotHashes']['before'].get('actor-card') or {}).get('sha256')))} / "
        f"{(((results['summary']['miniProgramScreenshotHashes']['afterRollback'].get('actor-card') or {}).get('sha256')))} / "
        f"{(((results['summary']['miniProgramScreenshotHashes']['afterRestore'].get('actor-card') or {}).get('sha256')))}",
        f"- `actor-profile-detail` SHA before/rollback/restore: "
        f"{(((results['summary']['miniProgramScreenshotHashes']['before'].get('actor-profile-detail') or {}).get('sha256')))} / "
        f"{(((results['summary']['miniProgramScreenshotHashes']['afterRollback'].get('actor-profile-detail') or {}).get('sha256')))} / "
        f"{(((results['summary']['miniProgramScreenshotHashes']['afterRestore'].get('actor-profile-detail') or {}).get('sha256')))}",
        f"- `invite-card` SHA before/rollback/restore: "
        f"{(((results['summary']['miniProgramScreenshotHashes']['before'].get('invite-card') or {}).get('sha256')))} / "
        f"{(((results['summary']['miniProgramScreenshotHashes']['afterRollback'].get('invite-card') or {}).get('sha256')))} / "
        f"{(((results['summary']['miniProgramScreenshotHashes']['afterRestore'].get('invite-card') or {}).get('sha256')))}",
        "",
        "## Page-Data Artifacts",
        "",
        *page_data_artifact_lines(results["summary"]),
        "",
        "## Evidence Files",
        "",
        "- captures/admin-template-rollback-mini-program-results.json",
        "- captures/admin-template-rollback-mini-program-db.txt",
        "- captures/mini-program-screenshot-capture-before-rollback.json",
        "- captures/mini-program-screenshot-capture-after-rollback.json",
        "- captures/mini-program-screenshot-capture-after-restore.json",
        "- screenshots/before-rollback-actor-card-mini-program-card.png",
        "- screenshots/after-rollback-actor-card-mini-program-card.png",
        "- screenshots/after-restore-actor-card-mini-program-card.png",
        "",
    ]
    with open(os.path.join(sample_root, "admin-template-rollback-mini-program-summary.md"), "w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(summary_lines) + "\n")

    print(
        json.dumps(
            {
                "sampleRoot": sample_root,
                "before": before_summary,
                "afterRollback": after_rollback_summary,
                "afterRestore": after_restore_summary,
                "miniProgramBefore": results["summary"]["miniProgramBefore"],
                "miniProgramAfterRollback": results["summary"]["miniProgramAfterRollback"],
                "miniProgramAfterRestore": results["summary"]["miniProgramAfterRestore"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
