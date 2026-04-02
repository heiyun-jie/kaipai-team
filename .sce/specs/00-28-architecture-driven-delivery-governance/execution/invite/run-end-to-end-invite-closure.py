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
DEFAULT_INVITER_PHONE = "13800138000"

SCRIPT_DIR = Path(__file__).resolve().parent
CAPTURE_ROOT = SCRIPT_DIR / "captures"
VALIDATION_SCRIPT = SCRIPT_DIR / "run-invite-validation.ps1"


def normalize_root_base_url(base_url: str) -> str:
    trimmed = base_url.strip().rstrip("/")
    return trimmed[:-4] if trimmed.endswith("/api") else trimmed


def api_base_url(base_url: str) -> str:
    return f"{normalize_root_base_url(base_url)}/api"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def parse_json_response(response: requests.Response) -> dict:
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"unexpected json from {response.request.method} {response.url}")
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
    if isinstance(data, dict) and isinstance(data.get("list"), list):
        return [item for item in data["list"] if isinstance(item, dict)]
    return []


def run_validation(context: dict, output_dir: Path) -> None:
    command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(VALIDATION_SCRIPT),
        "-SampleName",
        context["sampleLabel"],
        "-ApiBaseUrl",
        context["baseUrl"],
        "-EnvironmentName",
        context["environment"],
        "-ActorToken",
        context["actorToken"],
        "-AdminToken",
        context["adminToken"],
        "-InviteCode",
        context["inviteCode"],
        "-InviterUserId",
        str(context["inviterUserId"]),
        "-InviteeUserId",
        str(context["inviteeUserId"]),
        "-ReferralId",
        str(context["referralId"]),
        "-GrantId",
        str(context["grantId"]),
        "-PolicyId",
        str(context["policyId"]),
        "-OutputDir",
        str(output_dir),
    ]
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a fresh invitee sample and drive it through profile, verify, approve, and auto-grant."
    )
    parser.add_argument("--label", default="remote-invite-e2e-closure")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--environment", default="dev")
    parser.add_argument("--admin-account", default=DEFAULT_ADMIN_ACCOUNT)
    parser.add_argument("--admin-password", default=DEFAULT_ADMIN_PASSWORD)
    parser.add_argument("--inviter-phone", default=DEFAULT_INVITER_PHONE)
    args = parser.parse_args()

    now = datetime.now()
    sample_id = f"invite-{now.strftime('%Y%m%d-%H%M%S')}-{args.label}"
    output_dir = CAPTURE_ROOT / sample_id
    ensure_dir(output_dir)

    base_url = normalize_root_base_url(args.base_url)
    api_url = api_base_url(args.base_url)
    session = requests.Session()
    session.headers.update({"User-Agent": "codex-invite-e2e-closure/1.0"})

    admin_login = session.post(
        f"{api_url}/admin/auth/login",
        json={"account": args.admin_account, "password": args.admin_password},
        timeout=30,
    )
    admin_payload = require_success(admin_login, label="admin login")
    admin_token = admin_payload["data"]["accessToken"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    inviter_send_code = session.post(
        f"{api_url}/auth/sendCode",
        json={"phone": args.inviter_phone},
        timeout=30,
    )
    inviter_code = str(require_success(inviter_send_code, label="inviter sendCode")["data"])
    inviter_login = session.post(
        f"{api_url}/auth/login",
        json={"phone": args.inviter_phone, "code": inviter_code},
        timeout=30,
    )
    inviter_payload = require_success(inviter_login, label="inviter login")
    actor_token = inviter_payload["data"]["token"]
    actor_headers = {"Authorization": f"Bearer {actor_token}"}

    inviter_me = require_success(
        session.get(f"{api_url}/user/me", headers=actor_headers, timeout=30),
        label="inviter me",
    )
    inviter_user_id = inviter_me["data"]["userId"]
    invite_info = require_success(
        session.get(f"{api_url}/invite/code", headers=actor_headers, timeout=30),
        label="invite info",
    )
    invite_code = invite_info["data"]["inviteCode"]

    phone_suffix = now.strftime("%d%H%M%S")
    invitee_phone = f"139{phone_suffix}"
    invitee_send_code = session.post(
        f"{api_url}/auth/sendCode",
        json={"phone": invitee_phone},
        timeout=30,
    )
    invitee_code = str(require_success(invitee_send_code, label="invitee sendCode")["data"])

    register_payload = require_success(
        session.post(
            f"{api_url}/auth/register",
            json={
                "phone": invitee_phone,
                "code": invitee_code,
                "userType": 1,
                "nickName": f"Spec{phone_suffix}",
                "inviteCode": invite_code,
                "deviceFingerprint": f"invite-e2e-{sample_id}",
            },
            timeout=30,
        ),
        label="invitee register",
    )
    invitee_token = register_payload["data"]["token"]
    invitee_user_id = register_payload["data"]["userId"]
    invitee_headers = {"Authorization": f"Bearer {invitee_token}"}

    profile_payload = {
        "name": f"Spec{phone_suffix}",
        "gender": "male",
        "age": 25,
        "height": 180,
        "weight": 68,
        "city": "Shanghai",
        "birthday": "1999-01-01",
        "birthHour": "zi",
        "avatar": "https://example.com/avatar.jpg",
        "intro": "This actor profile exists for invite end to end validation.",
        "photos": [
            "https://example.com/photo-1.jpg",
            "https://example.com/photo-2.jpg",
        ],
        "photoCategories": {
            "portrait": ["https://example.com/photo-1.jpg"],
            "lifestyle": ["https://example.com/photo-2.jpg"],
            "production": [],
        },
        "videoUrl": "https://example.com/video.mp4",
        "skillTypes": ["acting", "martial"],
        "workExperiences": [
            {
                "projectName": "Spec Invite Closure",
                "roleName": "Lead",
                "shootDate": "2025-08",
                "photos": [],
                "description": "Validated profile completion for invite entitlement auto grant.",
            }
        ],
        "bodyType": "athletic",
        "hairStyle": "short",
        "languages": ["mandarin"],
        "contactPhone": invitee_phone,
    }
    require_success(
        session.put(f"{api_url}/actor/profile", headers=invitee_headers, json=profile_payload, timeout=30),
        label="invitee save profile",
    )

    id_card_no = f"11010119900101{phone_suffix[-4:]}"
    require_success(
        session.post(
            f"{api_url}/verify/submit",
            headers=invitee_headers,
            json={"realName": f"测试{phone_suffix[-4:]}", "idCardNo": id_card_no},
            timeout=30,
        ),
        label="invitee submit verify",
    )

    verify_list = require_success(
        session.get(
            f"{api_url}/admin/verify/list",
            headers=admin_headers,
            params={"pageNo": 1, "pageSize": 20, "userId": invitee_user_id},
            timeout=30,
        ),
        label="admin verify list",
    )
    verify_items = get_list(verify_list)
    if not verify_items:
        raise RuntimeError("no verification record found for invitee")
    verification_id = verify_items[0]["verificationId"]

    require_success(
        session.post(
            f"{api_url}/admin/verify/{verification_id}/approve",
            headers=admin_headers,
            json={"remark": "spec invite e2e approve"},
            timeout=30,
        ),
        label="admin verify approve",
    )

    invitee_login_code = str(
        require_success(
            session.post(f"{api_url}/auth/sendCode", json={"phone": invitee_phone}, timeout=30),
            label="invitee relogin sendCode",
        )["data"]
    )
    require_success(
        session.post(
            f"{api_url}/auth/login",
            json={"phone": invitee_phone, "code": invitee_login_code},
            timeout=30,
        ),
        label="invitee relogin",
    )

    record_list = require_success(
        session.get(
            f"{api_url}/admin/referral/records",
            headers=admin_headers,
            params={"pageNo": 1, "pageSize": 20, "inviteeUserId": invitee_user_id},
            timeout=30,
        ),
        label="admin referral records by invitee",
    )
    records = get_list(record_list)
    if not records:
        raise RuntimeError("no referral record found for new invitee")
    referral = records[0]
    referral_id = referral["referralId"]

    policy_list = require_success(
        session.get(
            f"{api_url}/admin/referral/policies",
            headers=admin_headers,
            params={"pageNo": 1, "pageSize": 20, "enabled": 1},
            timeout=30,
        ),
        label="admin policy list",
    )
    policy_items = get_list(policy_list)
    if not policy_items:
        raise RuntimeError("no active referral policy found")
    policy_id = policy_items[0]["policyId"]

    eligibility_list = require_success(
        session.get(
            f"{api_url}/admin/referral/eligibility",
            headers=admin_headers,
            params={
                "pageNo": 1,
                "pageSize": 20,
                "userId": invitee_user_id,
                "sourceType": "referral",
                "sourceRefId": referral_id,
            },
            timeout=30,
        ),
        label="admin eligibility by referral chain",
    )
    grants = get_list(eligibility_list)
    if not grants:
        raise RuntimeError("auto grant not created for new invitee sample")
    grant_id = grants[0]["grantId"]

    context = {
        "sampleLabel": args.label,
        "baseUrl": base_url,
        "environment": args.environment,
        "adminToken": admin_token,
        "actorToken": actor_token,
        "inviterUserId": inviter_user_id,
        "inviteeUserId": invitee_user_id,
        "inviteCode": invite_code,
        "referralId": referral_id,
        "grantId": grant_id,
        "policyId": policy_id,
    }
    (output_dir / "closure-context.json").write_text(
        json.dumps(
            {
                "generatedAt": now.isoformat(),
                "inviteePhone": invitee_phone,
                "verificationId": verification_id,
                "context": context,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    run_validation(context, output_dir)

    print(
        f"invite e2e closure sample prepared: {output_dir}\n"
        f"context: inviterUserId={inviter_user_id}, inviteCode={invite_code}, "
        f"inviteeUserId={invitee_user_id}, referralId={referral_id}, grantId={grant_id}, policyId={policy_id}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
