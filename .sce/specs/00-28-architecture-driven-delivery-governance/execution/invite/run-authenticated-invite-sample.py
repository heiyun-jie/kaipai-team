import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import requests


DEFAULT_BASE_URL = "http://101.43.57.62/api"
DEFAULT_ADMIN_ACCOUNT = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_USER_PHONE = "13800138000"

SCRIPT_DIR = Path(__file__).resolve().parent
CAPTURE_ROOT = SCRIPT_DIR / "captures"
VALIDATION_SCRIPT = SCRIPT_DIR / "run-invite-validation.ps1"


def normalize_root_base_url(base_url: str) -> str:
    trimmed = base_url.strip().rstrip("/")
    if trimmed.endswith("/api"):
        return trimmed[:-4]
    return trimmed


def api_base_url(base_url: str) -> str:
    root = normalize_root_base_url(base_url)
    return f"{root}/api"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def parse_json_response(response: requests.Response) -> dict:
    try:
        payload = response.json()
    except Exception as exc:
        raise RuntimeError(
            f"invalid json from {response.request.method} {response.url}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise RuntimeError(
            f"unexpected json shape from {response.request.method} {response.url}"
        )
    return payload


def require_success(response: requests.Response, *, label: str) -> dict:
    payload = parse_json_response(response)
    if response.status_code != 200 or payload.get("code") != 200:
        raise RuntimeError(
            f"{label} failed: HTTP {response.status_code} / "
            f"code {payload.get('code')} / message {payload.get('message')}"
        )
    return payload


def get_list(payload: dict) -> list[dict]:
    data = payload.get("data")
    if not isinstance(data, dict):
        return []
    items = data.get("list")
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def sort_records_desc(records: list[dict]) -> list[dict]:
    def sort_key(item: dict) -> tuple[int, str]:
        referral_id = item.get("referralId")
        try:
            referral_value = int(referral_id)
        except Exception:
            referral_value = -1
        registered_at = str(item.get("registeredAt") or "")
        return referral_value, registered_at

    return sorted(records, key=sort_key, reverse=True)


def choose_referral_record(records: list[dict], preferred_referral_id: str | None) -> dict:
    ordered = sort_records_desc(records)
    if preferred_referral_id:
        for item in ordered:
            if str(item.get("referralId") or "") == str(preferred_referral_id):
                return item
    valid_records = [item for item in ordered if item.get("status") == 1]
    if valid_records:
        return valid_records[0]
    if ordered:
        return ordered[0]
    raise RuntimeError("no referral record found for current invite sample")


def choose_grant_record(grants: list[dict], referral_id: str | None) -> dict | None:
    if referral_id:
        for item in grants:
            if str(item.get("sourceRefId") or "") == str(referral_id):
                return item
    return grants[0] if grants else None


def choose_policy_record(policies: list[dict], preferred_policy_id: str | None) -> dict | None:
    if preferred_policy_id:
        for item in policies:
            if str(item.get("policyId") or "") == str(preferred_policy_id):
                return item
    for item in policies:
        if item.get("enabled") == 1:
            return item
    return policies[0] if policies else None


def powershell_argument(value: str | None) -> str:
    return value if value is not None else ""


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_summary(path: Path, summary: dict) -> None:
    lines = [
        "# Invite Authenticated Sample",
        "",
        f"- Generated At: `{summary['generatedAt']}`",
        f"- Environment: `{summary['environmentName']}`",
        f"- Base URL: `{summary['baseUrl']}`",
        f"- Sample Label: `{summary['sampleLabel']}`",
        "",
        "## Discovered Context",
        "",
        f"- Inviter User ID: `{summary['context']['inviterUserId']}`",
        f"- Invite Code: `{summary['context']['inviteCode']}`",
        f"- Referral ID: `{summary['context']['referralId']}`",
        f"- Invitee User ID: `{summary['context']['inviteeUserId']}`",
        f"- Grant ID: `{summary['context']['grantId'] or '--'}`",
        f"- Policy ID: `{summary['context']['policyId'] or '--'}`",
        "",
        "## Sample Notes",
        "",
        f"- Actor invite stats total: `{summary['context']['totalInviteCount']}`",
        f"- Eligibility rows for invitee: `{summary['context']['eligibilityCount']}`",
        f"- Selected record status: `{summary['context']['referralStatus']}`",
        "",
        "## Artifacts",
        "",
        "- `auto-discovery.json`",
        "- `validation-report.md`",
        "- `capture-results.json`",
        "- `sample-ledger.md`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Log in actor/admin, discover a live invite sample, and run the standard invite validation script."
    )
    parser.add_argument("--label", default="authenticated-invite-sample")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--environment", default="dev")
    parser.add_argument("--admin-account", default=DEFAULT_ADMIN_ACCOUNT)
    parser.add_argument("--admin-password", default=DEFAULT_ADMIN_PASSWORD)
    parser.add_argument("--user-phone", default=DEFAULT_USER_PHONE)
    parser.add_argument("--referral-id", default="")
    parser.add_argument("--policy-id", default="")
    args = parser.parse_args()

    now = datetime.now()
    sample_id = f"invite-{now.strftime('%Y%m%d-%H%M%S')}-{args.label}"
    output_dir = CAPTURE_ROOT / sample_id
    ensure_dir(output_dir)

    api_url = api_base_url(args.base_url)
    session = requests.Session()
    session.headers.update({"User-Agent": "codex-invite-authenticated-sample/1.0"})

    admin_login = session.post(
        f"{api_url}/admin/auth/login",
        json={"account": args.admin_account, "password": args.admin_password},
        timeout=30,
    )
    admin_payload = require_success(admin_login, label="admin login")
    admin_token = admin_payload["data"]["accessToken"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    send_code = session.post(
        f"{api_url}/auth/sendCode",
        json={"phone": args.user_phone},
        timeout=30,
    )
    send_code_payload = require_success(send_code, label="actor sendCode")
    verify_code = str(send_code_payload["data"])

    actor_login = session.post(
        f"{api_url}/auth/login",
        json={"phone": args.user_phone, "code": verify_code},
        timeout=30,
    )
    actor_payload = require_success(actor_login, label="actor login")
    actor_token = actor_payload["data"]["token"]
    actor_headers = {"Authorization": f"Bearer {actor_token}"}

    actor_me = session.get(f"{api_url}/user/me", headers=actor_headers, timeout=30)
    actor_me_payload = require_success(actor_me, label="actor me")
    inviter_user_id = str(actor_me_payload["data"]["userId"])

    actor_invite_code = session.get(f"{api_url}/invite/code", headers=actor_headers, timeout=30)
    actor_invite_payload = require_success(actor_invite_code, label="actor invite code")
    actor_invite_data = actor_invite_payload["data"]
    invite_code = str(actor_invite_data["inviteCode"])

    records_resp = session.get(
        f"{api_url}/admin/referral/records",
        headers=admin_headers,
        params={"pageNo": 1, "pageSize": 20, "inviteCode": invite_code},
        timeout=30,
    )
    records_payload = require_success(records_resp, label="admin referral records")
    record = choose_referral_record(get_list(records_payload), args.referral_id or None)

    referral_id = str(record["referralId"])
    invitee_user_id = str(record["inviteeUserId"])

    eligibility_resp = session.get(
        f"{api_url}/admin/referral/eligibility",
        headers=admin_headers,
        params={"pageNo": 1, "pageSize": 20, "userId": invitee_user_id},
        timeout=30,
    )
    eligibility_payload = require_success(eligibility_resp, label="admin referral eligibility")
    eligibility_items = get_list(eligibility_payload)
    grant = choose_grant_record(eligibility_items, referral_id)

    policies_resp = session.get(
        f"{api_url}/admin/referral/policies",
        headers=admin_headers,
        params={"pageNo": 1, "pageSize": 20},
        timeout=30,
    )
    policies_payload = require_success(policies_resp, label="admin referral policies")
    policy = choose_policy_record(get_list(policies_payload), args.policy_id or None)

    grant_id = str(grant.get("grantId")) if grant and grant.get("grantId") is not None else ""
    policy_id = str(policy.get("policyId")) if policy and policy.get("policyId") is not None else ""

    command = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(VALIDATION_SCRIPT),
        "-SampleName",
        args.label,
        "-EnvironmentName",
        args.environment,
        "-ApiBaseUrl",
        normalize_root_base_url(args.base_url),
        "-ActorToken",
        actor_token,
        "-AdminToken",
        admin_token,
        "-InviteCode",
        invite_code,
        "-InviterUserId",
        inviter_user_id,
        "-InviteeUserId",
        invitee_user_id,
        "-ReferralId",
        referral_id,
        "-GrantId",
        powershell_argument(grant_id),
        "-PolicyId",
        powershell_argument(policy_id),
        "-OutputDir",
        str(output_dir),
    ]

    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            "run-invite-validation.ps1 failed:\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )

    auto_discovery = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "environmentName": args.environment,
        "baseUrl": normalize_root_base_url(args.base_url),
        "sampleLabel": args.label,
        "context": {
            "inviterUserId": inviter_user_id,
            "inviteCode": invite_code,
            "referralId": referral_id,
            "inviteeUserId": invitee_user_id,
            "grantId": grant_id,
            "policyId": policy_id,
            "totalInviteCount": actor_invite_data.get("totalInviteCount"),
            "eligibilityCount": len(eligibility_items),
            "referralStatus": record.get("status"),
        },
        "script": {
            "name": VALIDATION_SCRIPT.name,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "returncode": completed.returncode,
        },
    }
    write_json(output_dir / "auto-discovery.json", auto_discovery)
    write_summary(output_dir / "auto-discovery-summary.md", auto_discovery)

    print(f"invite authenticated sample prepared: {output_dir}")
    print(
        "context:"
        f" inviterUserId={inviter_user_id}, inviteCode={invite_code},"
        f" referralId={referral_id}, inviteeUserId={invitee_user_id},"
        f" grantId={grant_id or '--'}, policyId={policy_id or '--'}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"fatal: {exc}", file=sys.stderr)
        raise SystemExit(1)
