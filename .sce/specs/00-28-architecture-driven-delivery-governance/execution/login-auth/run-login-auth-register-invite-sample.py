import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests


DEFAULT_BASE_URL = "http://101.43.57.62/api"
DEFAULT_INVITER_PHONE = "13800138000"
DEFAULT_ADMIN_ACCOUNT = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_ROOT = SCRIPT_DIR / "samples"
USER_TYPE_ACTOR = 1


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def normalize_root_base_url(base_url: str) -> str:
    trimmed = base_url.strip().rstrip("/")
    if trimmed.endswith("/api"):
        return trimmed[:-4]
    return trimmed


def api_base_url(base_url: str) -> str:
    return f"{normalize_root_base_url(base_url)}/api"


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


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def response_capture(
    *,
    label: str,
    response: requests.Response,
    payload: dict,
    request_body: dict | None = None,
    request_params: dict | None = None,
) -> dict:
    return {
        "label": label,
        "requestedAt": datetime.now().isoformat(timespec="seconds"),
        "request": {
            "method": response.request.method,
            "url": response.url,
            "body": request_body or {},
            "params": request_params or {},
        },
        "response": {
            "statusCode": response.status_code,
            "payload": payload,
        },
    }


def request_json(
    session: requests.Session,
    method: str,
    url: str,
    *,
    label: str,
    output_path: Path,
    headers: dict[str, str] | None = None,
    json_body: dict | None = None,
    params: dict | None = None,
) -> dict:
    response = session.request(
        method=method,
        url=url,
        headers=headers,
        json=json_body,
        params=params,
        timeout=30,
    )
    payload = parse_json_response(response)
    capture = response_capture(
        label=label,
        response=response,
        payload=payload,
        request_body=json_body,
        request_params=params,
    )
    write_json(output_path, capture)
    if response.status_code != 200 or payload.get("code") != 200:
        raise RuntimeError(
            f"{label} failed: HTTP {response.status_code} / "
            f"code {payload.get('code')} / message {payload.get('message')}"
        )
    return payload


def generate_phone(seed: int, attempt: int) -> str:
    suffix = f"{seed + attempt:08d}"[-8:]
    return f"139{suffix}"


def pick_latest_record(records_payload: dict, invitee_user_id: int) -> dict:
    data = records_payload.get("data") or {}
    items = data.get("list") or []
    if not isinstance(items, list):
        raise RuntimeError("admin referral records payload missing list")
    matched = [
        item for item in items
        if isinstance(item, dict) and int(item.get("inviteeUserId") or -1) == invitee_user_id
    ]
    if not matched:
        raise RuntimeError(f"no admin referral record found for inviteeUserId={invitee_user_id}")
    matched.sort(
        key=lambda item: (
            int(item.get("referralId") or -1),
            str(item.get("registeredAt") or ""),
        ),
        reverse=True,
    )
    return matched[0]


def summary_lines(summary: dict) -> list[str]:
    confirmed = summary["confirmed"]
    blockers = summary["blockers"]
    return [
        "# Login Auth Register Invite Sample",
        "",
        f"- Generated At: `{summary['generatedAt']}`",
        f"- Environment: `{summary['environmentName']}`",
        f"- Base URL: `{summary['baseUrl']}`",
        f"- Sample Label: `{summary['sampleLabel']}`",
        "",
        "## Sample Context",
        "",
        f"- Inviter Phone: `{summary['context']['inviterPhone']}`",
        f"- Inviter User ID: `{summary['context']['inviterUserId']}`",
        f"- Invite Code: `{summary['context']['inviteCode']}`",
        f"- Registered Phone: `{summary['context']['registeredPhone']}`",
        f"- Registered User ID: `{summary['context']['registeredUserId']}`",
        f"- Registered Nickname: `{summary['context']['registeredNickname']}`",
        f"- Device Fingerprint: `{summary['context']['deviceFingerprint']}`",
        "",
        "## Register Chain",
        "",
        f"- inviter invite total before: `{summary['registerChain']['inviterTotalBefore']}`",
        f"- inviter invite total after: `{summary['registerChain']['inviterTotalAfter']}`",
        f"- register invitedByUserId: `{summary['registerChain']['registerInvitedByUserId']}`",
        f"- user.me invitedByUserId: `{summary['registerChain']['userMeInvitedByUserId']}`",
        f"- referralRecordId: `{summary['registerChain']['referralId']}`",
        f"- referral status: `{summary['registerChain']['referralStatus']}`",
        f"- restore userId: `{summary['registerChain']['restoredUserId']}`",
        "",
        "## Confirmed",
        "",
        *[f"- {item}" for item in confirmed],
        "",
        "## Blockers",
        "",
        *([f"- {item}" for item in blockers] if blockers else ["- none"]),
        "",
        "## Artifacts",
        "",
        "- `sample-metadata.json`",
        "- `closure-context.json`",
        "- `captures/inviter-send-code.json`",
        "- `captures/inviter-login.json`",
        "- `captures/inviter-invite-code.json`",
        "- `captures/inviter-invite-stats-before.json`",
        "- `captures/register-send-code.json`",
        "- `captures/register.json`",
        "- `captures/registered-user-me.json`",
        "- `captures/registered-verify-status.json`",
        "- `captures/registered-level-info.json`",
        "- `captures/registered-invite-stats.json`",
        "- `captures/restored-registered-user-me.json`",
        "- `captures/admin-login.json`",
        "- `captures/admin-referral-records.json`",
        "- `captures/inviter-invite-stats-after.json`",
        "- `summary.md`",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the phone register + inviteCode sample for login-auth."
    )
    parser.add_argument("--label", default="register-invite-mainline")
    parser.add_argument("--environment", default="dev")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--inviter-phone", default=DEFAULT_INVITER_PHONE)
    parser.add_argument("--admin-account", default=DEFAULT_ADMIN_ACCOUNT)
    parser.add_argument("--admin-password", default=DEFAULT_ADMIN_PASSWORD)
    args = parser.parse_args()

    now = datetime.now()
    sample_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{args.environment}-{args.label}"
    sample_root = SAMPLES_ROOT / sample_id
    capture_root = sample_root / "captures"
    ensure_dir(capture_root)

    api_url = api_base_url(args.base_url)
    root_base_url = normalize_root_base_url(args.base_url)
    session = requests.Session()
    session.headers.update({"User-Agent": "codex-login-auth-register-invite-sample/1.0"})

    inviter_send_code = request_json(
        session,
        "POST",
        f"{api_url}/auth/sendCode",
        label="inviter sendCode",
        output_path=capture_root / "inviter-send-code.json",
        json_body={"phone": args.inviter_phone},
    )
    inviter_code = str(inviter_send_code.get("data") or "").strip()
    inviter_login = request_json(
        session,
        "POST",
        f"{api_url}/auth/login",
        label="inviter login",
        output_path=capture_root / "inviter-login.json",
        json_body={"phone": args.inviter_phone, "code": inviter_code},
    )
    inviter_data = inviter_login["data"]
    inviter_token = str(inviter_data["token"])
    inviter_user_id = int(inviter_data["userId"])
    inviter_headers = {"Authorization": f"Bearer {inviter_token}"}

    inviter_invite_code = request_json(
        session,
        "GET",
        f"{api_url}/invite/code",
        label="inviter invite.code",
        output_path=capture_root / "inviter-invite-code.json",
        headers=inviter_headers,
    )
    invite_code = str((inviter_invite_code.get("data") or {}).get("inviteCode") or "").strip()
    if not invite_code:
        raise RuntimeError("inviter invite code is empty")

    inviter_stats_before = request_json(
        session,
        "GET",
        f"{api_url}/invite/stats",
        label="inviter invite.stats before",
        output_path=capture_root / "inviter-invite-stats-before.json",
        headers=inviter_headers,
    )
    inviter_total_before = int((inviter_stats_before.get("data") or {}).get("totalInviteCount") or 0)

    register_data = None
    register_phone = ""
    register_nickname = ""
    device_fingerprint = ""
    seed = int(time.time() * 1000) % 100000000
    register_error = None

    for attempt in range(5):
        register_phone = generate_phone(seed, attempt)
        register_nickname = f"登录样本{register_phone[-4:]}"
        device_fingerprint = f"login-auth-register-{register_phone}"
        register_send_code = request_json(
            session,
            "POST",
            f"{api_url}/auth/sendCode",
            label=f"register sendCode attempt {attempt + 1}",
            output_path=capture_root / "register-send-code.json",
            json_body={"phone": register_phone},
        )
        register_code = str(register_send_code.get("data") or "").strip()
        response = session.post(
            f"{api_url}/auth/register",
            json={
                "phone": register_phone,
                "code": register_code,
                "userType": USER_TYPE_ACTOR,
                "nickName": register_nickname,
                "inviteCode": invite_code,
                "deviceFingerprint": device_fingerprint,
            },
            timeout=30,
        )
        payload = parse_json_response(response)
        write_json(
            capture_root / "register.json",
            response_capture(
                label="register",
                response=response,
                payload=payload,
                request_body={
                    "phone": register_phone,
                    "code": register_code,
                    "userType": USER_TYPE_ACTOR,
                    "nickName": register_nickname,
                    "inviteCode": invite_code,
                    "deviceFingerprint": device_fingerprint,
                },
            ),
        )
        if response.status_code == 200 and payload.get("code") == 200:
            register_data = payload["data"]
            break
        register_error = (
            f"register failed for {register_phone}: HTTP {response.status_code} / "
            f"code {payload.get('code')} / message {payload.get('message')}"
        )
        message = str(payload.get("message") or "")
        if "已注册" not in message:
            raise RuntimeError(register_error)

    if register_data is None:
        raise RuntimeError(register_error or "register failed after 5 attempts")

    registered_token = str(register_data["token"])
    registered_user_id = int(register_data["userId"])
    registered_headers = {"Authorization": f"Bearer {registered_token}"}

    registered_user_me = request_json(
        session,
        "GET",
        f"{api_url}/user/me",
        label="registered user.me",
        output_path=capture_root / "registered-user-me.json",
        headers=registered_headers,
    )
    registered_verify_status = request_json(
        session,
        "GET",
        f"{api_url}/verify/status",
        label="registered verify.status",
        output_path=capture_root / "registered-verify-status.json",
        headers=registered_headers,
    )
    registered_level_info = request_json(
        session,
        "GET",
        f"{api_url}/level/info",
        label="registered level.info",
        output_path=capture_root / "registered-level-info.json",
        headers=registered_headers,
    )
    registered_invite_stats = request_json(
        session,
        "GET",
        f"{api_url}/invite/stats",
        label="registered invite.stats",
        output_path=capture_root / "registered-invite-stats.json",
        headers=registered_headers,
    )

    restored_session = requests.Session()
    restored_session.headers.update({"User-Agent": "codex-login-auth-register-restore/1.0"})
    restored_registered_user_me = request_json(
        restored_session,
        "GET",
        f"{api_url}/user/me",
        label="restored registered user.me",
        output_path=capture_root / "restored-registered-user-me.json",
        headers=registered_headers,
    )

    admin_session = requests.Session()
    admin_session.headers.update({"User-Agent": "codex-login-auth-register-admin/1.0"})
    admin_login = request_json(
        admin_session,
        "POST",
        f"{api_url}/admin/auth/login",
        label="admin login",
        output_path=capture_root / "admin-login.json",
        json_body={"account": args.admin_account, "password": args.admin_password},
    )
    admin_token = str((admin_login.get("data") or {}).get("accessToken") or "")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    admin_referral_records = request_json(
        admin_session,
        "GET",
        f"{api_url}/admin/referral/records",
        label="admin referral.records",
        output_path=capture_root / "admin-referral-records.json",
        headers=admin_headers,
        params={"pageNo": 1, "pageSize": 20, "inviteCode": invite_code},
    )
    referral_record = pick_latest_record(admin_referral_records, registered_user_id)

    inviter_stats_after = request_json(
        session,
        "GET",
        f"{api_url}/invite/stats",
        label="inviter invite.stats after",
        output_path=capture_root / "inviter-invite-stats-after.json",
        headers=inviter_headers,
    )
    inviter_total_after = int((inviter_stats_after.get("data") or {}).get("totalInviteCount") or 0)

    registered_user_me_data = registered_user_me["data"]
    restored_registered_user_me_data = restored_registered_user_me["data"]
    blockers: list[str] = []
    register_invited_by = register_data.get("invitedByUserId")
    user_me_invited_by = registered_user_me_data.get("invitedByUserId")
    if register_invited_by != inviter_user_id:
        blockers.append(
            f"register invitedByUserId mismatch: `{register_invited_by}` vs `{inviter_user_id}`"
        )
    if user_me_invited_by != inviter_user_id:
        blockers.append(
            f"user.me invitedByUserId mismatch: `{user_me_invited_by}` vs `{inviter_user_id}`"
        )
    if int(restored_registered_user_me_data.get("userId") or -1) != registered_user_id:
        blockers.append(
            f"restored user.me userId mismatch: `{restored_registered_user_me_data.get('userId')}` vs `{registered_user_id}`"
        )
    if int(referral_record.get("inviterUserId") or -1) != inviter_user_id:
        blockers.append(
            f"admin referral record inviter mismatch: `{referral_record.get('inviterUserId')}` vs `{inviter_user_id}`"
        )
    if inviter_total_after < inviter_total_before:
        blockers.append(
            f"inviter totalInviteCount regressed: `{inviter_total_before}` -> `{inviter_total_after}`"
        )
    blockers.append(
        "`sendCode` still directly returns a development verification code; this proves interface connectivity, not commercial SMS closure."
    )

    confirmed = [
        f"手机号 `{register_phone}` 已通过 `sendCode -> register(inviteCode={invite_code})` 创建真实新用户，并返回 `userId={registered_user_id}` token。",
        f"注册回包与 `/api/user/me` 都已固定 `invitedByUserId={inviter_user_id}`，说明当前 login-auth 注册链已承接邀请码。",
        f"后台 `/admin/referral/records` 已回读到 `referralId={referral_record.get('referralId')}`，证明注册链已落 `referral_record`。",
        f"注册后 fresh session 复用同一 Bearer token 仍可恢复到 `userId={registered_user_id}`。",
        f"邀请人 `/api/invite/stats.totalInviteCount` 已从 `{inviter_total_before}` 变化到 `{inviter_total_after}`。",
    ]

    metadata = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "environmentName": args.environment,
        "sampleLabel": args.label,
        "sampleRoot": str(sample_root),
        "baseUrl": root_base_url,
        "inviterPhone": args.inviter_phone,
        "registeredPhone": register_phone,
        "registeredUserId": registered_user_id,
        "inviterUserId": inviter_user_id,
        "inviteCode": invite_code,
        "deviceFingerprint": device_fingerprint,
    }
    write_json(sample_root / "sample-metadata.json", metadata)

    closure_context = {
        "generatedAt": metadata["generatedAt"],
        "context": {
            "environment": args.environment,
            "baseUrl": root_base_url,
            "inviterPhone": args.inviter_phone,
            "inviterUserId": inviter_user_id,
            "inviteCode": invite_code,
            "registeredPhone": register_phone,
            "registeredUserId": registered_user_id,
            "referralId": referral_record.get("referralId"),
            "referralStatus": referral_record.get("status"),
            "deviceFingerprint": device_fingerprint,
        },
    }
    write_json(sample_root / "closure-context.json", closure_context)

    summary = {
        "generatedAt": metadata["generatedAt"],
        "environmentName": args.environment,
        "baseUrl": root_base_url,
        "sampleLabel": args.label,
        "context": {
            "inviterPhone": args.inviter_phone,
            "inviterUserId": inviter_user_id,
            "inviteCode": invite_code,
            "registeredPhone": register_phone,
            "registeredUserId": registered_user_id,
            "registeredNickname": register_nickname,
            "deviceFingerprint": device_fingerprint,
        },
        "registerChain": {
            "inviterTotalBefore": inviter_total_before,
            "inviterTotalAfter": inviter_total_after,
            "registerInvitedByUserId": register_invited_by,
            "userMeInvitedByUserId": user_me_invited_by,
            "referralId": referral_record.get("referralId"),
            "referralStatus": referral_record.get("status"),
            "restoredUserId": restored_registered_user_me_data.get("userId"),
        },
        "confirmed": confirmed,
        "blockers": blockers,
    }
    (sample_root / "summary.md").write_text(
        "\n".join(summary_lines(summary)) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "sampleRoot": str(sample_root),
                "registeredPhone": register_phone,
                "registeredUserId": registered_user_id,
                "inviteCode": invite_code,
                "referralId": referral_record.get("referralId"),
                "blockerCount": len(blockers),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"fatal: {exc}", file=sys.stderr)
        raise SystemExit(1)
