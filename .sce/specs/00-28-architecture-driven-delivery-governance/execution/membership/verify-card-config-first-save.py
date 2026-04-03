import json
import os
import shlex
import sys
from datetime import datetime

import paramiko
import requests


BASE_URL = "http://101.43.57.62/api"
USER_PHONE = "13800138000"
ACTOR_USER_ID = 10000
SCENE_KEY = "general"
REMOTE_HOST = "101.43.57.62"
REMOTE_USER = "kaipaile"
REMOTE_PASSWORD = "kaipaile888"
DB_NAME = "kaipai_dev"
MAX_USER_LOGIN_ATTEMPTS = 3


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def parse_json_response(response: requests.Response) -> dict:
    try:
        return response.json()
    except Exception as exc:
        raise RuntimeError(f"invalid json from {response.request.method} {response.url}: {exc}") from exc


def record_request(results: list, session: requests.Session, name: str, method: str, url: str, **kwargs) -> dict:
    item = {"name": name, "method": method, "url": url}
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


def attempt_name(base_name: str, attempt: int) -> str:
    return base_name if attempt == 1 else f"{base_name}-retry-{attempt}"


def remote_mysql(sql: str, batch: bool = False) -> tuple[str, str]:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(REMOTE_HOST, username=REMOTE_USER, password=REMOTE_PASSWORD, timeout=20)
    compact_sql = " ".join(line.strip() for line in sql.splitlines() if line.strip())
    batch_flags = "--batch --raw --skip-column-names " if batch else ""
    command = (
        f"echo '{REMOTE_PASSWORD}' | sudo -S "
        f"docker exec kaipai-mysql mysql {batch_flags}--default-character-set=utf8mb4 "
        f"-uroot -proot123456 -e {shlex.quote(compact_sql)}"
    )
    stdin, stdout, stderr = client.exec_command(command, timeout=120)
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    client.close()
    return out, err


def remote_execute(sql: str) -> str:
    out, err = remote_mysql(sql, batch=False)
    err_text = err.strip()
    if err_text and "Warning" not in err_text:
        raise RuntimeError(err_text)
    if "ERROR" in out.upper():
        raise RuntimeError(out)
    return out


def remote_query_json(sql: str) -> list[dict]:
    out, err = remote_mysql(sql, batch=True)
    err_text = err.strip()
    if err_text and "Warning" not in err_text:
        raise RuntimeError(err_text)
    rows = []
    for line in out.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        rows.append(json.loads(stripped))
    return rows


def login_user(session: requests.Session, results: list) -> str:
    last_error = None
    for attempt in range(1, MAX_USER_LOGIN_ATTEMPTS + 1):
        try:
            send_code = record_request(
                results,
                session,
                attempt_name("user-send-code", attempt),
                "POST",
                f"{BASE_URL}/auth/sendCode",
                json={"phone": USER_PHONE},
            )
            code = require_ok(send_code)["data"]
            login = record_request(
                results,
                session,
                attempt_name("user-login", attempt),
                "POST",
                f"{BASE_URL}/auth/login",
                json={"phone": USER_PHONE, "code": str(code)},
            )
            return require_ok(login)["data"]["token"]
        except RuntimeError as exc:
            last_error = exc
    raise RuntimeError(f"user login failed after {MAX_USER_LOGIN_ATTEMPTS} attempts: {last_error}")


def reset_actor_rows() -> str:
    return remote_execute(
        f"""
USE {DB_NAME};
DELETE FROM actor_share_preference
WHERE user_id = {ACTOR_USER_ID}
  AND scene_key = '{SCENE_KEY}';
DELETE FROM actor_card_config
WHERE user_id = {ACTOR_USER_ID}
  AND scene_key = '{SCENE_KEY}';
SELECT 'config_count' AS label, COUNT(*) AS total
FROM actor_card_config
WHERE user_id = {ACTOR_USER_ID}
  AND scene_key = '{SCENE_KEY}';
SELECT 'preference_count' AS label, COUNT(*) AS total
FROM actor_share_preference
WHERE user_id = {ACTOR_USER_ID}
  AND scene_key = '{SCENE_KEY}';
"""
    )


def query_db_state() -> str:
    out, err = remote_mysql(
        f"""
USE {DB_NAME};
SELECT JSON_OBJECT(
  'configId', config_id,
  'userId', user_id,
  'sceneKey', scene_key,
  'templateId', template_id,
  'layoutVariant', layout_variant,
  'primaryColor', primary_color,
  'accentColor', accent_color,
  'backgroundColor', background_color,
  'lastUpdate', DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:%s')
)
FROM actor_card_config
WHERE user_id = {ACTOR_USER_ID}
  AND scene_key = '{SCENE_KEY}'
ORDER BY config_id DESC
LIMIT 1;
SELECT JSON_OBJECT(
  'preferenceId', preference_id,
  'userId', user_id,
  'sceneKey', scene_key,
  'preferredArtifact', preferred_artifact,
  'preferredTone', preferred_tone,
  'enableFortuneTheme', enable_fortune_theme,
  'lastUpdate', DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:%s')
)
FROM actor_share_preference
WHERE user_id = {ACTOR_USER_ID}
  AND scene_key = '{SCENE_KEY}'
ORDER BY preference_id DESC
LIMIT 1;
""",
        batch=True,
    )
    return out if not err.strip() else out + "\n[stderr]\n" + err


def main() -> None:
    sample_root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    captures_dir = os.path.join(sample_root, "captures")
    ensure_dir(captures_dir)

    results = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "baseUrl": BASE_URL,
        "actorUserId": ACTOR_USER_ID,
        "sceneKey": SCENE_KEY,
        "requests": [],
    }

    reset_output = reset_actor_rows()
    session = requests.Session()
    session.headers.update({"User-Agent": "spec-card-config-first-save/1.0"})
    token = login_user(session, results["requests"])
    headers = {"Authorization": f"Bearer {token}"}

    config_before = record_request(
        results["requests"],
        session,
        "card-config-before-save",
        "GET",
        f"{BASE_URL}/card/config?actorId={ACTOR_USER_ID}&scene={SCENE_KEY}",
        headers=headers,
    )
    personalization_before = record_request(
        results["requests"],
        session,
        "card-personalization-before-save",
        "GET",
        f"{BASE_URL}/card/personalization?actorId={ACTOR_USER_ID}&scene={SCENE_KEY}&loadFortune=true",
        headers=headers,
    )
    before_config_payload = require_ok(config_before)["data"]
    before_personalization_payload = require_ok(personalization_before)["data"]
    before_share_preferences = (before_personalization_payload.get("profile") or {}).get("sharePreferences") or {}

    save_payload = {
        "actorId": ACTOR_USER_ID,
        "sceneKey": SCENE_KEY,
        "layoutVariant": before_config_payload.get("layoutVariant"),
        "primaryColor": before_config_payload.get("primaryColor"),
        "accentColor": before_config_payload.get("accentColor"),
        "backgroundColor": before_config_payload.get("backgroundColor"),
        "highlightedExperiences": before_config_payload.get("highlightedExperiences") or [],
        "highlightedPhotos": before_config_payload.get("highlightedPhotos") or [],
        "tagOrder": before_config_payload.get("tagOrder") or [],
        "preferredArtifact": before_share_preferences.get("preferredArtifact") or "miniProgramCard",
        "preferredTone": before_share_preferences.get("preferredTone") or "warm",
        "enableFortuneTheme": True,
    }
    save_item = record_request(
        results["requests"],
        session,
        "card-config-first-save",
        "POST",
        f"{BASE_URL}/card/config",
        headers=headers,
        json=save_payload,
    )
    save_payload_response = require_ok(save_item)["data"]

    config_after = record_request(
        results["requests"],
        session,
        "card-config-after-save",
        "GET",
        f"{BASE_URL}/card/config?actorId={ACTOR_USER_ID}&scene={SCENE_KEY}",
        headers=headers,
    )
    personalization_after = record_request(
        results["requests"],
        session,
        "card-personalization-after-save",
        "GET",
        f"{BASE_URL}/card/personalization?actorId={ACTOR_USER_ID}&scene={SCENE_KEY}&loadFortune=true",
        headers=headers,
    )
    after_config_payload = require_ok(config_after)["data"]
    after_personalization_payload = require_ok(personalization_after)["data"]
    db_state = query_db_state()

    results["resetOutput"] = reset_output
    results["savePayload"] = save_payload
    results["summary"] = {
        "saveStatus": save_item["status"],
        "saveCode": (save_item.get("responseJson") or {}).get("code"),
        "savedLayoutVariant": save_payload_response.get("layoutVariant"),
        "savedPrimaryColor": save_payload_response.get("primaryColor"),
        "afterThemeId": ((after_personalization_payload.get("theme") or {}).get("themeId")),
        "afterThemePrimary": ((after_personalization_payload.get("theme") or {}).get("primary")),
        "afterEnableFortuneTheme": (((after_personalization_payload.get("profile") or {}).get("sharePreferences") or {}).get("enableFortuneTheme")),
    }

    summary_lines = [
        "# Card Config First Save Success Summary",
        "",
        f"- Generated At: {results['generatedAt']}",
        f"- Base URL: {BASE_URL}",
        f"- Actor User ID: {ACTOR_USER_ID}",
        f"- Scene Key: {SCENE_KEY}",
        f"- Save HTTP Status: {results['summary']['saveStatus']}",
        f"- Save Response Code: {results['summary']['saveCode']}",
        f"- Saved Layout Variant: {results['summary']['savedLayoutVariant']}",
        f"- Saved Primary Color: {results['summary']['savedPrimaryColor']}",
        f"- After Theme ID: {results['summary']['afterThemeId']}",
        f"- After Theme Primary: {results['summary']['afterThemePrimary']}",
        f"- After Enable Fortune Theme: {results['summary']['afterEnableFortuneTheme']}",
        "",
        "## Request Results",
        "",
    ]
    for item in results["requests"]:
        summary_lines.append(f"- {item['name']}: HTTP {item['status']}")
    summary_lines.extend(
        [
            "",
            "## Evidence Files",
            "",
            "- captures/card-config-first-save-success-results.json",
            "- captures/card-config-first-save-db.txt",
            "- card-config-first-save-success-summary.md",
            "",
        ]
    )

    with open(os.path.join(captures_dir, "card-config-first-save-success-results.json"), "w", encoding="utf-8") as handle:
        json.dump(results, handle, ensure_ascii=False, indent=2)
    with open(os.path.join(captures_dir, "card-config-first-save-db.txt"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(db_state)
    with open(os.path.join(sample_root, "card-config-first-save-success-summary.md"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(summary_lines) + "\n")

    print(json.dumps(results["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
