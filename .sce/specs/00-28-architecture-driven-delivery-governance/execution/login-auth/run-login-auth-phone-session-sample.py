import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import requests


DEFAULT_BASE_URL = "http://101.43.57.62/api"
DEFAULT_PHONE = "13800138000"
DEFAULT_SCENE = "general"
SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_ROOT = SCRIPT_DIR / "samples"
FRONTEND_ENV_PATH = Path(r"D:\XM\kaipai-team\kaipai-frontend\.env")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def normalize_root_base_url(base_url: str) -> str:
    trimmed = base_url.strip().rstrip("/")
    if trimmed.endswith("/api"):
        return trimmed[:-4]
    return trimmed


def api_base_url(base_url: str) -> str:
    root = normalize_root_base_url(base_url)
    return f"{root}/api"


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#") or "=" not in trimmed:
            continue
        key, value = trimmed.split("=", 1)
        values[key.strip()] = value.strip()
    return values


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
    payload = require_success(response, label=label)
    capture = response_capture(
        label=label,
        response=response,
        payload=payload,
        request_body=json_body,
        request_params=params,
    )
    write_json(output_path, capture)
    return payload


def compare_equal(label: str, left: object, right: object, findings: list[str]) -> None:
    if left != right:
        findings.append(f"{label} mismatch: `{left}` vs `{right}`")


def summary_lines(summary: dict) -> list[str]:
    primary = summary["primary"]
    restored = summary["restored"]
    confirmed = summary["confirmed"]
    blockers = summary["blockers"]
    return [
        "# Login Auth Phone Session Sample",
        "",
        f"- Generated At: `{summary['generatedAt']}`",
        f"- Environment: `{summary['environmentName']}`",
        f"- Base URL: `{summary['baseUrl']}`",
        f"- Sample Label: `{summary['sampleLabel']}`",
        "",
        "## Runtime",
        "",
        f"- Frontend `.env` base URL: `{summary['runtime']['frontendBaseUrl'] or '--'}`",
        f"- Frontend `.env` mock flag: `{summary['runtime']['frontendUseMock'] or '--'}`",
        f"- Frontend `.env` WeChat flag: `{summary['runtime']['frontendWechatAuth'] or '--'}`",
        "",
        "## Sample Context",
        "",
        f"- Phone: `{summary['context']['phone']}`",
        f"- User ID: `{summary['context']['userId']}`",
        f"- Token Preview: `{summary['context']['tokenPreview']}`",
        f"- Membership Tier: `{primary['levelInfo'].get('membershipTier')}`",
        f"- Level: `{primary['levelInfo'].get('level')}`",
        f"- Invite Count: `{primary['inviteStats'].get('validInviteCount')}`",
        f"- Verify Status: `{primary['verifyStatus'].get('status')}`",
        "",
        "## Primary Chain",
        "",
        f"- sendCode message: `{primary['sendCode'].get('message')}`",
        f"- login userId: `{primary['login'].get('userId')}`",
        f"- user.me userId: `{primary['userMe'].get('userId')}`",
        f"- level.info inviteCount: `{primary['levelInfo'].get('inviteCount')}`",
        f"- personalization reasonCodes: `{json.dumps(primary['personalizationReasonCodes'], ensure_ascii=False)}`",
        "",
        "## Restored Session",
        "",
        f"- restored user.me userId: `{restored['userMe'].get('userId')}`",
        f"- restored level.info level: `{restored['levelInfo'].get('level')}`",
        f"- restored invite.stats validInviteCount: `{restored['inviteStats'].get('validInviteCount')}`",
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
        "- `captures/send-code.json`",
        "- `captures/login.json`",
        "- `captures/user-me.json`",
        "- `captures/verify-status.json`",
        "- `captures/invite-stats.json`",
        "- `captures/level-info.json`",
        "- `captures/card-personalization.json`",
        "- `captures/restored-user-me.json`",
        "- `captures/restored-verify-status.json`",
        "- `captures/restored-invite-stats.json`",
        "- `captures/restored-level-info.json`",
        "- `summary.md`",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the current-phase phone login / session restore sample for login-auth."
    )
    parser.add_argument("--label", default="phone-session-mainline")
    parser.add_argument("--environment", default="dev")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--phone", default=DEFAULT_PHONE)
    parser.add_argument("--scene", default=DEFAULT_SCENE)
    args = parser.parse_args()

    now = datetime.now()
    sample_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{args.environment}-{args.label}"
    sample_root = SAMPLES_ROOT / sample_id
    capture_root = sample_root / "captures"
    ensure_dir(capture_root)

    frontend_env = parse_env_file(FRONTEND_ENV_PATH)
    root_base_url = normalize_root_base_url(args.base_url)
    api_url = api_base_url(args.base_url)

    session = requests.Session()
    session.headers.update({"User-Agent": "codex-login-auth-phone-session-sample/1.0"})

    send_code_payload = request_json(
        session,
        "POST",
        f"{api_url}/auth/sendCode",
        label="sendCode",
        output_path=capture_root / "send-code.json",
        json_body={"phone": args.phone},
    )
    verify_code = str(send_code_payload.get("data") or "").strip()
    if not verify_code:
        raise RuntimeError("sendCode returned empty verification code; cannot continue sample")

    login_payload = request_json(
        session,
        "POST",
        f"{api_url}/auth/login",
        label="login",
        output_path=capture_root / "login.json",
        json_body={"phone": args.phone, "code": verify_code},
    )
    login_data = login_payload["data"]
    token = str(login_data["token"])
    user_id = int(login_data["userId"])
    auth_headers = {"Authorization": f"Bearer {token}"}

    user_me_payload = request_json(
        session,
        "GET",
        f"{api_url}/user/me",
        label="user.me",
        output_path=capture_root / "user-me.json",
        headers=auth_headers,
    )
    verify_status_payload = request_json(
        session,
        "GET",
        f"{api_url}/verify/status",
        label="verify.status",
        output_path=capture_root / "verify-status.json",
        headers=auth_headers,
    )
    invite_stats_payload = request_json(
        session,
        "GET",
        f"{api_url}/invite/stats",
        label="invite.stats",
        output_path=capture_root / "invite-stats.json",
        headers=auth_headers,
    )
    level_info_payload = request_json(
        session,
        "GET",
        f"{api_url}/level/info",
        label="level.info",
        output_path=capture_root / "level-info.json",
        headers=auth_headers,
    )
    personalization_payload = request_json(
        session,
        "GET",
        f"{api_url}/card/personalization",
        label="card.personalization",
        output_path=capture_root / "card-personalization.json",
        headers=auth_headers,
        params={"actorId": user_id, "scene": args.scene},
    )

    restored_session = requests.Session()
    restored_session.headers.update({"User-Agent": "codex-login-auth-phone-session-restore/1.0"})
    restored_user_me_payload = request_json(
        restored_session,
        "GET",
        f"{api_url}/user/me",
        label="restored user.me",
        output_path=capture_root / "restored-user-me.json",
        headers=auth_headers,
    )
    restored_verify_status_payload = request_json(
        restored_session,
        "GET",
        f"{api_url}/verify/status",
        label="restored verify.status",
        output_path=capture_root / "restored-verify-status.json",
        headers=auth_headers,
    )
    restored_invite_stats_payload = request_json(
        restored_session,
        "GET",
        f"{api_url}/invite/stats",
        label="restored invite.stats",
        output_path=capture_root / "restored-invite-stats.json",
        headers=auth_headers,
    )
    restored_level_info_payload = request_json(
        restored_session,
        "GET",
        f"{api_url}/level/info",
        label="restored level.info",
        output_path=capture_root / "restored-level-info.json",
        headers=auth_headers,
    )

    primary_user_me = user_me_payload["data"]
    primary_verify_status = verify_status_payload["data"]
    primary_invite_stats = invite_stats_payload["data"]
    primary_level_info = level_info_payload["data"]
    primary_personalization = personalization_payload["data"]

    restored_user_me = restored_user_me_payload["data"]
    restored_verify_status = restored_verify_status_payload["data"]
    restored_invite_stats = restored_invite_stats_payload["data"]
    restored_level_info = restored_level_info_payload["data"]

    blockers: list[str] = []
    compare_equal("login.userId vs user.me.userId", login_data.get("userId"), primary_user_me.get("userId"), blockers)
    compare_equal("verify.status vs user.me.realAuthStatus", primary_verify_status.get("status"), primary_user_me.get("realAuthStatus"), blockers)
    compare_equal("level.info.inviteCount vs invite.stats.validInviteCount", primary_level_info.get("inviteCount"), primary_invite_stats.get("validInviteCount"), blockers)
    compare_equal("restored user.me.userId", primary_user_me.get("userId"), restored_user_me.get("userId"), blockers)
    compare_equal("restored verify.status", primary_verify_status.get("status"), restored_verify_status.get("status"), blockers)
    compare_equal("restored invite.stats.validInviteCount", primary_invite_stats.get("validInviteCount"), restored_invite_stats.get("validInviteCount"), blockers)
    compare_equal("restored level.info.level", primary_level_info.get("level"), restored_level_info.get("level"), blockers)

    if frontend_env.get("VITE_ENABLE_WECHAT_AUTH") != "false":
        blockers.append("Current phone-session sample expects non-WeChat stage, but frontend `.env` no longer pins `VITE_ENABLE_WECHAT_AUTH=false`.")
    if frontend_env.get("VITE_USE_MOCK") != "false":
        blockers.append("Current phone-session sample expects real runtime, but frontend `.env` is not pinned to `VITE_USE_MOCK=false`.")
    if send_code_payload.get("data") is not None:
        blockers.append("`sendCode` still directly returns a development verification code; this proves interface connectivity, not commercial SMS closure.")

    reason_codes = (
        (((primary_personalization.get("capability") or {}).get("reasonCodes")) or [])
        if isinstance(primary_personalization, dict)
        else []
    )

    confirmed = [
        f"手机号 `{args.phone}` 可通过 `sendCode -> login` 获取真实 token，并命中 `userId={user_id}`。",
        "`/api/user/me`、`/api/verify/status`、`/api/invite/stats`、`/api/level/info`、`/api/card/personalization` 当前同一 token 下全部返回 `200/code=200`。",
        "fresh session 复用同一 Bearer token 后，`user.me / verify.status / invite.stats / level.info` 仍保持同一用户与同一等级摘要，说明当前会话恢复口径稳定。",
        f"`/api/card/personalization` 当前 `reasonCodes={json.dumps(reason_codes, ensure_ascii=False)}`。",
    ]

    metadata = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "environmentName": args.environment,
        "sampleLabel": args.label,
        "sampleRoot": str(sample_root),
        "baseUrl": root_base_url,
        "phone": args.phone,
        "scene": args.scene,
        "userId": user_id,
        "tokenPreview": f"{token[:12]}...{token[-8:]}",
    }
    write_json(sample_root / "sample-metadata.json", metadata)

    closure_context = {
        "generatedAt": metadata["generatedAt"],
        "context": {
            "environment": args.environment,
            "baseUrl": root_base_url,
            "phone": args.phone,
            "userId": user_id,
            "tokenPreview": metadata["tokenPreview"],
            "verifyStatus": primary_verify_status.get("status"),
            "inviteCount": primary_invite_stats.get("validInviteCount"),
            "level": primary_level_info.get("level"),
            "membershipTier": primary_level_info.get("membershipTier"),
            "profileCompletion": primary_level_info.get("profileCompletion"),
        },
    }
    write_json(sample_root / "closure-context.json", closure_context)

    summary = {
        "generatedAt": metadata["generatedAt"],
        "environmentName": args.environment,
        "baseUrl": root_base_url,
        "sampleLabel": args.label,
        "runtime": {
            "frontendBaseUrl": frontend_env.get("VITE_API_BASE_URL", ""),
            "frontendUseMock": frontend_env.get("VITE_USE_MOCK", ""),
            "frontendWechatAuth": frontend_env.get("VITE_ENABLE_WECHAT_AUTH", ""),
        },
        "context": {
            "phone": args.phone,
            "userId": user_id,
            "tokenPreview": metadata["tokenPreview"],
        },
        "primary": {
            "sendCode": {
                "message": send_code_payload.get("message"),
            },
            "login": login_data,
            "userMe": primary_user_me,
            "verifyStatus": primary_verify_status,
            "inviteStats": primary_invite_stats,
            "levelInfo": primary_level_info,
            "personalizationReasonCodes": reason_codes,
        },
        "restored": {
            "userMe": restored_user_me,
            "verifyStatus": restored_verify_status,
            "inviteStats": restored_invite_stats,
            "levelInfo": restored_level_info,
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
                "phone": args.phone,
                "userId": user_id,
                "level": primary_level_info.get("level"),
                "inviteCount": primary_invite_stats.get("validInviteCount"),
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
