import json
import os
import shlex
import sys
from datetime import datetime, timedelta

import paramiko
import requests


BASE_URL = "http://101.43.57.62/api"
USER_PHONE = "13800138000"
ACTOR_USER_ID = 10000
TARGET_VALID_INVITES = 8
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
    item = {
        "name": name,
        "method": method,
        "url": url,
    }
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
            payload = require_ok(login)
            return payload["data"]["token"]
        except RuntimeError as exc:
            last_error = exc
    raise RuntimeError(f"user login failed after {MAX_USER_LOGIN_ATTEMPTS} attempts: {last_error}")


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
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    client.close()
    return out, err


def remote_query_json(sql: str) -> list[dict]:
    out, err = remote_mysql(sql, batch=True)
    if err.strip() and "Warning" not in err:
        raise RuntimeError(err.strip())
    rows = []
    for line in out.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        rows.append(json.loads(stripped))
    return rows


def remote_execute(sql: str) -> None:
    out, err = remote_mysql(sql, batch=False)
    err_text = err.strip()
    if err_text and "Warning" not in err_text:
        raise RuntimeError(err_text)
    if "ERROR" in out.upper():
        raise RuntimeError(out)


def query_inviter_state() -> dict:
    inviter = remote_query_json(
        f"""
USE {DB_NAME};
SELECT JSON_OBJECT(
  'userId', user_id,
  'phone', phone,
  'userName', user_name,
  'realAuthStatus', real_auth_status,
  'invitedByUserId', invited_by_user_id,
  'validInviteCount', valid_invite_count,
  'createTime', DATE_FORMAT(create_time, '%Y-%m-%d %H:%i:%s')
)
FROM user
WHERE user_id = {ACTOR_USER_ID}
LIMIT 1;
"""
    )
    invite_code = remote_query_json(
        f"""
USE {DB_NAME};
SELECT JSON_OBJECT(
  'inviteCodeId', invite_code_id,
  'userId', user_id,
  'code', code,
  'status', status,
  'createTime', DATE_FORMAT(create_time, '%Y-%m-%d %H:%i:%s')
)
FROM invite_code
WHERE user_id = {ACTOR_USER_ID}
LIMIT 1;
"""
    )
    referrals = remote_query_json(
        f"""
USE {DB_NAME};
SELECT JSON_OBJECT(
  'referralId', referral_id,
  'inviterUserId', inviter_user_id,
  'inviteeUserId', invitee_user_id,
  'inviteCodeSnapshot', invite_code_snapshot,
  'status', status,
  'riskFlag', risk_flag,
  'riskReason', risk_reason,
  'registeredAt', DATE_FORMAT(registered_at, '%Y-%m-%d %H:%i:%s'),
  'validatedAt', DATE_FORMAT(validated_at, '%Y-%m-%d %H:%i:%s')
)
FROM referral_record
WHERE inviter_user_id = {ACTOR_USER_ID}
ORDER BY referral_id;
"""
    )
    max_user = remote_query_json(
        f"""
USE {DB_NAME};
SELECT JSON_OBJECT('maxUserId', COALESCE(MAX(user_id), {ACTOR_USER_ID})) FROM user;
"""
    )
    share_preferences = remote_query_json(
        f"""
USE {DB_NAME};
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
"""
    )
    return {
        "inviter": inviter[0] if inviter else None,
        "inviteCode": invite_code[0] if invite_code else None,
        "referrals": referrals,
        "maxUserId": (max_user[0] if max_user else {}).get("maxUserId"),
        "sharePreference": share_preferences[0] if share_preferences else None,
    }


def build_seed_rows(start_user_id: int, missing_count: int) -> list[dict]:
    rows = []
    base_time = datetime(2026, 4, 2, 22, 0, 0)
    for index in range(missing_count):
        user_id = start_user_id + index
        phone = f"139{user_id:08d}"
        registered_at = base_time + timedelta(hours=index)
        validated_at = registered_at + timedelta(minutes=30)
        rows.append(
            {
                "userId": user_id,
                "account": phone,
                "phone": phone,
                "password": f"spec-lv5-{user_id}",
                "userName": f"SpecLv5{user_id}",
                "userType": 1,
                "registerSource": 1,
                "realAuthStatus": 0,
                "status": 1,
                "remark": "spec-membership-level-unlock",
                "registerDeviceFingerprint": f"spec-lv5-device-{user_id}",
                "registeredAt": registered_at.strftime("%Y-%m-%d %H:%M:%S"),
                "validatedAt": validated_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    return rows


def seed_valid_invites(invite_code: dict, current_valid_count: int, max_user_id: int) -> list[dict]:
    missing_count = max(0, TARGET_VALID_INVITES - current_valid_count)
    if missing_count == 0:
        return []

    rows = build_seed_rows(max_user_id + 1, missing_count)
    statements = [f"USE {DB_NAME};"]
    for row in rows:
        statements.append(
            "INSERT INTO user "
            "(user_id, account, phone, password, user_name, user_type, register_source, real_auth_status, invited_by_user_id, "
            "valid_invite_count, register_device_fingerprint, status, remark, create_time, last_update, create_user_name, update_user_name) "
            "VALUES "
            f"({row['userId']}, '{row['account']}', '{row['phone']}', '{row['password']}', '{row['userName']}', {row['userType']}, "
            f"{row['registerSource']}, {row['realAuthStatus']}, {ACTOR_USER_ID}, 0, '{row['registerDeviceFingerprint']}', {row['status']}, "
            f"'{row['remark']}', '{row['registeredAt']}', '{row['registeredAt']}', 'spec-seeder', 'spec-seeder');"
        )
        statements.append(
            "INSERT INTO referral_record "
            "(inviter_user_id, invitee_user_id, invite_code_id, invite_code_snapshot, register_device_fingerprint, status, risk_flag, "
            "registered_at, validated_at, create_time, last_update, create_user_name, update_user_name) "
            "VALUES "
            f"({ACTOR_USER_ID}, {row['userId']}, {invite_code['inviteCodeId']}, '{invite_code['code']}', "
            f"'{row['registerDeviceFingerprint']}', 1, 0, '{row['registeredAt']}', '{row['validatedAt']}', "
            f"'{row['registeredAt']}', '{row['validatedAt']}', 'spec-seeder', 'spec-seeder');"
        )
    statements.append(f"UPDATE user SET valid_invite_count = {TARGET_VALID_INVITES}, last_update = NOW() WHERE user_id = {ACTOR_USER_ID};")
    remote_execute("\n".join(statements))
    return rows


def fetch_runtime_state(session: requests.Session, results: list, headers: dict) -> dict:
    calls = [
        ("user-me", "GET", f"{BASE_URL}/user/me", None),
        ("invite-stats", "GET", f"{BASE_URL}/invite/stats", None),
        ("level-info", "GET", f"{BASE_URL}/level/info", None),
        ("card-config", "GET", f"{BASE_URL}/card/config?actorId={ACTOR_USER_ID}&scene={SCENE_KEY}", None),
        ("fortune-report", "GET", f"{BASE_URL}/fortune/report", None),
        ("card-personalization", "GET", f"{BASE_URL}/card/personalization?actorId={ACTOR_USER_ID}&scene={SCENE_KEY}&loadFortune=true", None),
    ]
    snapshot = {}
    for name, method, url, body in calls:
        item = record_request(results, session, name, method, url, headers=headers, json=body)
        snapshot[name] = require_ok(item)["data"]
    return snapshot


def enable_fortune_theme(session: requests.Session, results: list, headers: dict, before_config: dict, before_personalization: dict) -> dict:
    share_preferences = (before_personalization.get("profile") or {}).get("sharePreferences") or {}
    payload = {
        "actorId": ACTOR_USER_ID,
        "sceneKey": SCENE_KEY,
        "layoutVariant": before_config.get("layoutVariant"),
        "primaryColor": before_config.get("primaryColor"),
        "accentColor": before_config.get("accentColor"),
        "backgroundColor": before_config.get("backgroundColor"),
        "highlightedExperiences": before_config.get("highlightedExperiences") or [],
        "highlightedPhotos": before_config.get("highlightedPhotos") or [],
        "tagOrder": before_config.get("tagOrder") or [],
        "preferredArtifact": share_preferences.get("preferredArtifact") or "miniProgramCard",
        "preferredTone": share_preferences.get("preferredTone"),
        "enableFortuneTheme": True,
    }
    item = record_request(
        results,
        session,
        "card-config-save-enable-fortune-theme",
        "POST",
        f"{BASE_URL}/card/config",
        headers=headers,
        json=payload,
    )
    require_ok(item)
    return payload


def write_db_capture(sample_root: str, seeded_rows: list[dict]) -> str:
    seeded_user_ids = ",".join(str(item["userId"]) for item in seeded_rows)
    user_filter = f"{ACTOR_USER_ID}" if not seeded_user_ids else f"{ACTOR_USER_ID}, {seeded_user_ids}"
    sql = f"""
USE {DB_NAME};
SELECT user_id, phone, user_name, real_auth_status, invited_by_user_id, valid_invite_count, create_time, register_device_fingerprint
FROM user
WHERE user_id IN ({user_filter})
ORDER BY user_id;
SELECT invite_code_id, user_id, code, status, create_time
FROM invite_code
WHERE user_id = {ACTOR_USER_ID};
SELECT referral_id, inviter_user_id, invitee_user_id, invite_code_snapshot, status, risk_flag, registered_at, validated_at
FROM referral_record
WHERE inviter_user_id = {ACTOR_USER_ID}
ORDER BY referral_id;
SELECT preference_id, user_id, scene_key, preferred_artifact, preferred_tone, enable_fortune_theme, last_update
FROM actor_share_preference
WHERE user_id = {ACTOR_USER_ID}
ORDER BY preference_id DESC;
SELECT config_id, user_id, actor_profile_id, scene_key, layout_variant, primary_color, accent_color, background_color, last_update
FROM actor_card_config
WHERE user_id = {ACTOR_USER_ID}
ORDER BY config_id DESC;
"""
    out, err = remote_mysql(sql, batch=False)
    db_path = os.path.join(sample_root, "captures", "membership-level-unlock-db.txt")
    with open(db_path, "w", encoding="utf-8", newline="\n") as file:
        file.write(out)
        if err.strip():
            file.write("\n[stderr]\n")
            file.write(err)
    return db_path


def summarize(snapshot: dict) -> dict:
    level_info = snapshot["level-info"]
    personalization = snapshot["card-personalization"]
    invite_stats = snapshot["invite-stats"]
    theme = personalization.get("theme") or {}
    capability = personalization.get("capability") or {}
    share_preferences = ((personalization.get("profile") or {}).get("sharePreferences")) or {}
    return {
        "level": level_info.get("level"),
        "inviteCount": level_info.get("inviteCount"),
        "nextLevelRequirement": level_info.get("nextLevelRequirement"),
        "membershipTier": level_info.get("membershipTier"),
        "reasonCodes": capability.get("reasonCodes") or [],
        "canApplyFortuneTheme": capability.get("canApplyFortuneTheme"),
        "themeId": theme.get("themeId"),
        "themePrimary": theme.get("primary"),
        "preferredArtifact": share_preferences.get("preferredArtifact"),
        "enableFortuneTheme": share_preferences.get("enableFortuneTheme"),
        "validInviteCountCached": snapshot["user-me"].get("validInviteCount"),
        "inviteStatsValidCount": invite_stats.get("validInviteCount"),
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: run-membership-level-unlock.py <sample-root>")
        return 1

    sample_root = os.path.abspath(sys.argv[1])
    capture_root = os.path.join(sample_root, "captures")
    ensure_dir(capture_root)

    now = datetime.now()
    session = requests.Session()
    session.headers.update({"User-Agent": "codex-membership-level-unlock/1.0"})

    results = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "baseUrl": BASE_URL,
        "actorUserId": ACTOR_USER_ID,
        "targetValidInviteCount": TARGET_VALID_INVITES,
        "sceneKey": SCENE_KEY,
        "requests": [],
        "db": {},
    }

    user_token = login_user(session, results["requests"])
    user_headers = {"Authorization": f"Bearer {user_token}"}

    before_state = query_inviter_state()
    if not before_state["inviter"]:
        raise RuntimeError(f"actor user not found: {ACTOR_USER_ID}")
    if not before_state["inviteCode"]:
        raise RuntimeError(f"invite code not found for user {ACTOR_USER_ID}")

    before_runtime = fetch_runtime_state(session, results["requests"], user_headers)
    seeded_rows = seed_valid_invites(
        before_state["inviteCode"],
        int(before_runtime["level-info"].get("inviteCount") or 0),
        int(before_state["maxUserId"] or ACTOR_USER_ID),
    )

    after_seed_state = query_inviter_state()
    after_seed_runtime = fetch_runtime_state(session, results["requests"], user_headers)

    save_payload = enable_fortune_theme(
        session,
        results["requests"],
        user_headers,
        after_seed_runtime["card-config"],
        after_seed_runtime["card-personalization"],
    )
    after_save_runtime = fetch_runtime_state(session, results["requests"], user_headers)

    if int(after_save_runtime["level-info"].get("level") or 0) < 5:
        raise RuntimeError("level unlock failed: actor level is still below Lv5")
    if not ((after_save_runtime["card-personalization"].get("capability") or {}).get("canApplyFortuneTheme")):
        raise RuntimeError("fortune theme unlock failed: personalization capability is still locked")

    results["db"]["before"] = before_state
    results["db"]["afterSeed"] = after_seed_state
    results["seededInvitees"] = seeded_rows
    results["payloads"] = {"saveConfig": save_payload}
    results["summary"] = {
        "before": summarize(before_runtime),
        "afterSeed": summarize(after_seed_runtime),
        "afterEnableFortuneTheme": summarize(after_save_runtime),
    }

    json_path = os.path.join(capture_root, "membership-level-unlock-results.json")
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)

    db_path = write_db_capture(sample_root, seeded_rows)

    summary_lines = [
        "# Membership Level Unlock Summary",
        "",
        f"- Generated At: {results['generatedAt']}",
        f"- Base URL: {BASE_URL}",
        f"- Actor User ID: {ACTOR_USER_ID}",
        f"- Scene Key: {SCENE_KEY}",
        f"- Target Valid Invite Count: {TARGET_VALID_INVITES}",
        "",
        "## Before",
        "",
        f"- Level: {results['summary']['before']['level']}",
        f"- Invite Count: {results['summary']['before']['inviteCount']}",
        f"- Reason Codes: {', '.join(results['summary']['before']['reasonCodes']) or '(none)'}",
        f"- Theme ID: {results['summary']['before']['themeId']}",
        f"- Enable Fortune Theme: {results['summary']['before']['enableFortuneTheme']}",
        "",
        "## After Unlock",
        "",
        f"- Level: {results['summary']['afterEnableFortuneTheme']['level']}",
        f"- Invite Count: {results['summary']['afterEnableFortuneTheme']['inviteCount']}",
        f"- Can Apply Fortune Theme: {results['summary']['afterEnableFortuneTheme']['canApplyFortuneTheme']}",
        f"- Theme ID: {results['summary']['afterEnableFortuneTheme']['themeId']}",
        f"- Theme Primary: {results['summary']['afterEnableFortuneTheme']['themePrimary']}",
        f"- Enable Fortune Theme: {results['summary']['afterEnableFortuneTheme']['enableFortuneTheme']}",
        "",
        "## Seeded Invitees",
        "",
    ]
    if seeded_rows:
        summary_lines.extend(
            [
                f"- {row['userId']} / {row['phone']} / {row['registeredAt']} / {row['registerDeviceFingerprint']}"
                for row in seeded_rows
            ]
        )
    else:
        summary_lines.append("- No new invitees were needed; current runtime already meets the Lv5 invite threshold.")
    summary_lines.extend(
        [
            "",
            "## Evidence Files",
            "",
            "- captures/membership-level-unlock-results.json",
            "- captures/membership-level-unlock-db.txt",
            "",
            "## Pending Evidence",
            "",
            "- Re-run mini-program screenshots against this sample to confirm the unlocked fortune theme on real pages.",
        ]
    )

    summary_path = os.path.join(sample_root, "membership-level-unlock-summary.md")
    with open(summary_path, "w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(summary_lines) + "\n")

    print(
        json.dumps(
            {
                "sampleRoot": sample_root,
                "seededInviteeCount": len(seeded_rows),
                "afterUnlock": results["summary"]["afterEnableFortuneTheme"],
                "dbCapture": db_path,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
