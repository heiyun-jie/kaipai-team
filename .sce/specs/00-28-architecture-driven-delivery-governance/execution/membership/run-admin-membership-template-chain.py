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
    item = {
        "name": name,
        "method": method,
        "url": url,
    }
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


def login_admin(session: requests.Session, results: list) -> str:
    item = record_request(
        results,
        session,
        "admin-login",
        "POST",
        f"{BASE_URL}/admin/auth/login",
        json={"account": ADMIN_ACCOUNT, "password": ADMIN_PASSWORD},
    )
    payload = require_ok(item)
    return payload["data"]["accessToken"]


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
    payload = require_ok(login)
    return payload["data"]["token"]


def remote_mysql(sql: str) -> str:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(REMOTE_HOST, username=REMOTE_USER, password=REMOTE_PASSWORD, timeout=20)
    compact_sql = " ".join(line.strip() for line in sql.splitlines() if line.strip())
    command = (
        f"echo '{REMOTE_PASSWORD}' | sudo -S "
        f"docker exec kaipai-mysql mysql --default-character-set=utf8mb4 -uroot -proot123456 -e {shlex.quote(compact_sql)}"
    )
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
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


def choose_next_theme(before_theme: dict) -> dict:
    current_primary = (before_theme.get("primary") or "").upper()
    if current_primary == "#2F6B5F":
        return {
            "themeColors": {
                "primary": "#7A3E2B",
                "accent": "#F3DDD2",
                "background": "#2D1812",
                "text": "#FFF6F1",
                "heroText": "#FFFFFF",
            }
        }
    return {
        "themeColors": {
            "primary": "#2F6B5F",
            "accent": "#D6EAD9",
            "background": "#102A26",
            "text": "#F3F7F6",
            "heroText": "#FFFFFF",
        }
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: run-admin-membership-template-chain.py <sample-root>")
        return 1

    sample_root = os.path.abspath(sys.argv[1])
    capture_root = os.path.join(sample_root, "captures")
    ensure_dir(capture_root)

    now = datetime.now()
    publish_version = f"SMOKE_V2_ADMIN_{now.strftime('%Y%m%d_%H%M%S')}"
    open_effective_time = now.replace(second=0, microsecond=0).isoformat()
    open_expire_time = "2026-05-31T23:59:00"
    session = requests.Session()
    session.headers.update({"User-Agent": "codex-admin-membership-template-chain/1.0"})

    results = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "baseUrl": BASE_URL,
        "actorUserId": ACTOR_USER_ID,
        "templateId": TEMPLATE_ID,
        "publishVersion": publish_version,
        "requests": [],
        "payloads": {
            "membershipClose": {
                "remark": "spec-admin-membership-template-chain-close"
            },
            "membershipOpen": {
                "tier": 1,
                "effectiveTime": open_effective_time,
                "expireTime": open_expire_time,
                "sourceType": "admin",
                "sourceRefId": TEMPLATE_ID,
                "remark": "spec-admin-membership-template-chain-open",
            },
            "publish": {
                "templateId": TEMPLATE_ID,
                "publishVersion": publish_version,
                "publishNote": "spec admin membership/template chain publish",
            },
        },
    }

    admin_token = login_admin(session, results["requests"])
    user_token = login_user(session, results["requests"])
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}

    before_calls = [
        ("before-admin-membership-account", "GET", f"{BASE_URL}/admin/membership/accounts/{ACTOR_USER_ID}", admin_headers, None),
        ("before-admin-template-detail", "GET", f"{BASE_URL}/admin/content/templates/{TEMPLATE_ID}", admin_headers, None),
        ("before-admin-publish-logs", "GET", f"{BASE_URL}/admin/content/publish-logs?pageNo=1&pageSize=20&templateId={TEMPLATE_ID}", admin_headers, None),
        ("before-admin-theme-tokens", "GET", f"{BASE_URL}/admin/content/theme-tokens?pageNo=1&pageSize=20&templateId={TEMPLATE_ID}", admin_headers, None),
        ("before-user-me", "GET", f"{BASE_URL}/user/me", user_headers, None),
        ("before-level-info", "GET", f"{BASE_URL}/level/info", user_headers, None),
        ("before-fortune-report", "GET", f"{BASE_URL}/fortune/report", user_headers, None),
        ("before-card-personalization", "GET", f"{BASE_URL}/card/personalization?actorId={ACTOR_USER_ID}&scene=general&loadFortune=true", user_headers, None),
        ("before-card-scene-templates", "GET", f"{BASE_URL}/card/scene-templates", user_headers, None),
    ]
    for name, method, url, headers, body in before_calls:
        item = record_request(results["requests"], session, name, method, url, headers=headers, json=body)
        require_ok(item)

    before_template_detail = find_request(results["requests"], "before-admin-template-detail")["responseJson"]["data"]
    theme_before = extract_theme_node(before_template_detail.get("baseThemeJson"))
    theme_after = choose_next_theme(theme_before)
    results["payloads"]["themeUpdate"] = {
        "baseThemeJson": json.dumps(theme_after, ensure_ascii=False),
    }
    results["payloads"]["themeBeforeReference"] = theme_before

    close_item = record_request(
        results["requests"],
        session,
        "admin-membership-close",
        "POST",
        f"{BASE_URL}/admin/membership/accounts/{ACTOR_USER_ID}/close",
        headers=admin_headers,
        json=results["payloads"]["membershipClose"],
    )
    require_ok(close_item)

    after_close_calls = [
        ("after-close-admin-membership-account", "GET", f"{BASE_URL}/admin/membership/accounts/{ACTOR_USER_ID}", admin_headers, None),
        ("after-close-level-info", "GET", f"{BASE_URL}/level/info", user_headers, None),
        ("after-close-card-personalization", "GET", f"{BASE_URL}/card/personalization?actorId={ACTOR_USER_ID}&scene=general&loadFortune=true", user_headers, None),
    ]
    for name, method, url, headers, body in after_close_calls:
        item = record_request(results["requests"], session, name, method, url, headers=headers, json=body)
        require_ok(item)

    open_item = record_request(
        results["requests"],
        session,
        "admin-membership-open",
        "POST",
        f"{BASE_URL}/admin/membership/accounts/{ACTOR_USER_ID}/open",
        headers=admin_headers,
        json=results["payloads"]["membershipOpen"],
    )
    require_ok(open_item)

    after_open_calls = [
        ("after-open-admin-membership-account", "GET", f"{BASE_URL}/admin/membership/accounts/{ACTOR_USER_ID}", admin_headers, None),
        ("after-open-level-info", "GET", f"{BASE_URL}/level/info", user_headers, None),
        ("after-open-card-personalization", "GET", f"{BASE_URL}/card/personalization?actorId={ACTOR_USER_ID}&scene=general&loadFortune=true", user_headers, None),
    ]
    for name, method, url, headers, body in after_open_calls:
        item = record_request(results["requests"], session, name, method, url, headers=headers, json=body)
        require_ok(item)

    theme_update_item = record_request(
        results["requests"],
        session,
        "admin-theme-update",
        "PUT",
        f"{BASE_URL}/admin/content/theme-tokens/{TEMPLATE_ID}",
        headers=admin_headers,
        json=results["payloads"]["themeUpdate"],
    )
    require_ok(theme_update_item)

    publish_item = record_request(
        results["requests"],
        session,
        "admin-template-publish",
        "POST",
        f"{BASE_URL}/admin/content/templates/{TEMPLATE_ID}/publish",
        headers=admin_headers,
        json=results["payloads"]["publish"],
    )
    require_ok(publish_item)

    after_publish_calls = [
        ("after-publish-admin-template-detail", "GET", f"{BASE_URL}/admin/content/templates/{TEMPLATE_ID}", admin_headers, None),
        ("after-publish-admin-publish-logs", "GET", f"{BASE_URL}/admin/content/publish-logs?pageNo=1&pageSize=20&templateId={TEMPLATE_ID}", admin_headers, None),
        ("after-publish-admin-theme-tokens", "GET", f"{BASE_URL}/admin/content/theme-tokens?pageNo=1&pageSize=20&templateId={TEMPLATE_ID}", admin_headers, None),
        ("after-publish-card-scene-templates", "GET", f"{BASE_URL}/card/scene-templates", user_headers, None),
        ("after-publish-card-personalization", "GET", f"{BASE_URL}/card/personalization?actorId={ACTOR_USER_ID}&scene=general&loadFortune=true", user_headers, None),
    ]
    for name, method, url, headers, body in after_publish_calls:
        item = record_request(results["requests"], session, name, method, url, headers=headers, json=body)
        require_ok(item)

    db_sql = f"""
USE kaipai_dev;
SELECT membership_id,user_id,tier,status,effective_time,expire_time,source_type,source_ref_id,last_update
FROM membership_account
WHERE user_id={ACTOR_USER_ID};
SELECT change_log_id,user_id,before_tier,after_tier,change_reason,source_type,source_ref_id,remark,create_time
FROM membership_change_log
WHERE user_id={ACTOR_USER_ID}
ORDER BY change_log_id DESC
LIMIT 6;
SELECT template_id,template_code,scene_key,status,base_theme_json,artifact_preset_json,last_update
FROM card_scene_template
WHERE template_id={TEMPLATE_ID};
SELECT publish_log_id,template_id,publish_version,source_version,target_version,action_type,published_by,publish_note,published_at
FROM template_publish_log
WHERE template_id={TEMPLATE_ID}
ORDER BY publish_log_id DESC
LIMIT 6;
SELECT operation_log_id,admin_user_id,admin_user_name,module_code,operation_code,target_type,target_id,operation_result,create_time
FROM admin_operation_log
WHERE module_code IN ('membership','content')
ORDER BY operation_log_id DESC
LIMIT 12;
""".strip()
    db_output = remote_mysql(db_sql)

    before_level = find_request(results["requests"], "before-level-info")["responseJson"]["data"]
    after_close_level = find_request(results["requests"], "after-close-level-info")["responseJson"]["data"]
    after_open_level = find_request(results["requests"], "after-open-level-info")["responseJson"]["data"]
    before_personalization = find_request(results["requests"], "before-card-personalization")["responseJson"]["data"]
    after_close_personalization = find_request(results["requests"], "after-close-card-personalization")["responseJson"]["data"]
    after_open_personalization = find_request(results["requests"], "after-open-card-personalization")["responseJson"]["data"]
    after_publish_template = find_request(results["requests"], "after-publish-admin-template-detail")["responseJson"]["data"]
    after_publish_personalization = find_request(results["requests"], "after-publish-card-personalization")["responseJson"]["data"]
    after_publish_logs = find_request(results["requests"], "after-publish-admin-publish-logs")["responseJson"]["data"]["list"]

    results["summary"] = {
        "membershipBefore": {
            "membershipTier": before_level.get("membershipTier"),
            "reasonCodes": ((before_level.get("shareCapability") or {}).get("reasonCodes") or []),
            "canUsePersonalizedTheme": ((before_level.get("shareCapability") or {}).get("canUsePersonalizedTheme")),
        },
        "membershipAfterClose": {
            "membershipTier": after_close_level.get("membershipTier"),
            "reasonCodes": ((after_close_level.get("shareCapability") or {}).get("reasonCodes") or []),
            "canUsePersonalizedTheme": ((after_close_level.get("shareCapability") or {}).get("canUsePersonalizedTheme")),
            "artifactCount": len(after_close_personalization.get("artifacts") or []),
        },
        "membershipAfterOpen": {
            "membershipTier": after_open_level.get("membershipTier"),
            "reasonCodes": ((after_open_level.get("shareCapability") or {}).get("reasonCodes") or []),
            "canUsePersonalizedTheme": ((after_open_level.get("shareCapability") or {}).get("canUsePersonalizedTheme")),
            "artifactCount": len(after_open_personalization.get("artifacts") or []),
        },
        "templateBefore": {
            "themeId": (before_personalization.get("theme") or {}).get("themeId"),
            "primary": (before_personalization.get("theme") or {}).get("primary"),
            "accent": (before_personalization.get("theme") or {}).get("accent"),
            "background": (before_personalization.get("theme") or {}).get("background"),
        },
        "templateAfterPublish": {
            "publishLogId": after_publish_logs[0]["publishLogId"] if after_publish_logs else None,
            "publishVersion": after_publish_logs[0]["publishVersion"] if after_publish_logs else None,
            "themeId": (after_publish_personalization.get("theme") or {}).get("themeId"),
            "primary": (after_publish_personalization.get("theme") or {}).get("primary"),
            "accent": (after_publish_personalization.get("theme") or {}).get("accent"),
            "background": (after_publish_personalization.get("theme") or {}).get("background"),
            "templateBaseThemeJson": after_publish_template.get("baseThemeJson"),
        },
    }

    json_path = os.path.join(capture_root, "admin-membership-template-chain-results.json")
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)

    db_path = os.path.join(capture_root, "admin-membership-template-chain-db.txt")
    with open(db_path, "w", encoding="utf-8", newline="\n") as file:
        file.write(db_output)

    summary_lines = [
        "# Admin Membership Template Chain Summary",
        "",
        f"- Generated At: {results['generatedAt']}",
        f"- Base URL: {BASE_URL}",
        f"- Actor User ID: {ACTOR_USER_ID}",
        f"- Template ID: {TEMPLATE_ID}",
        f"- Publish Version: {publish_version}",
        "",
        "## Membership Action Chain",
        "",
        f"- Before membershipTier: {results['summary']['membershipBefore']['membershipTier']}",
        f"- After close membershipTier: {results['summary']['membershipAfterClose']['membershipTier']}",
        f"- After close reasonCodes: {', '.join(results['summary']['membershipAfterClose']['reasonCodes'])}",
        f"- After open membershipTier: {results['summary']['membershipAfterOpen']['membershipTier']}",
        f"- After open reasonCodes: {', '.join(results['summary']['membershipAfterOpen']['reasonCodes'])}",
        "",
        "## Template Publish Chain",
        "",
        f"- Before theme primary: {results['summary']['templateBefore']['primary']}",
        f"- After publish theme primary: {results['summary']['templateAfterPublish']['primary']}",
        f"- After publish theme accent: {results['summary']['templateAfterPublish']['accent']}",
        f"- After publish theme background: {results['summary']['templateAfterPublish']['background']}",
        f"- Latest publishLogId: {results['summary']['templateAfterPublish']['publishLogId']}",
        f"- Latest publishVersion: {results['summary']['templateAfterPublish']['publishVersion']}",
        "",
        "## Evidence Files",
        "",
        "- captures/admin-membership-template-chain-results.json",
        "- captures/admin-membership-template-chain-db.txt",
        "- runtime-summary.md",
        "- validation-report.md",
        "",
        "## Pending Evidence",
        "",
        "- Mini-program screenshots are still pending in this sample directory.",
    ]
    summary_path = os.path.join(sample_root, "admin-membership-template-chain-summary.md")
    with open(summary_path, "w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(summary_lines) + "\n")

    print(json.dumps({
        "sampleRoot": sample_root,
        "summary": results["summary"],
        "dbCapture": db_path,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
