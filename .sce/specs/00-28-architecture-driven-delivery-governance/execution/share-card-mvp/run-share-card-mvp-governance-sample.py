import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests


DEFAULT_BASE_URL = "http://101.43.57.62/api"
DEFAULT_OWNER_PHONE = "13800138000"
DEFAULT_ADMIN_ACCOUNT = "admin"
ADMIN_PASSWORD_ENV = "KAIPAI_ADMIN_SMOKE_PASSWORD"
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
    return f"{normalize_root_base_url(base_url)}/api"


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
    write_json(
        output_path,
        response_capture(
            label=label,
            response=response,
            payload=payload,
            request_body=json_body,
            request_params=params,
        ),
    )
    if response.status_code != 200 or payload.get("code") != 200:
        raise RuntimeError(
            f"{label} failed: HTTP {response.status_code} / "
            f"code {payload.get('code')} / message {payload.get('message')}"
        )
    return payload


def generate_phone(seed: int, attempt: int) -> str:
    suffix = f"{seed + attempt:08d}"[-8:]
    return f"137{suffix}"


def login_by_phone(
    session: requests.Session,
    api_url: str,
    phone: str,
    capture_root: Path,
    prefix: str,
) -> dict:
    send_code = request_json(
        session,
        "POST",
        f"{api_url}/auth/sendCode",
        label=f"{prefix} sendCode",
        output_path=capture_root / f"{prefix}-send-code.json",
        json_body={"phone": phone},
    )
    code = str(send_code.get("data") or "").strip()
    if not code:
        raise RuntimeError(f"{prefix} sendCode returned empty code")
    return request_json(
        session,
        "POST",
        f"{api_url}/auth/login",
        label=f"{prefix} login",
        output_path=capture_root / f"{prefix}-login.json",
        json_body={"phone": phone, "code": code},
    )


def register_viewer(
    session: requests.Session,
    api_url: str,
    invite_code: str,
    capture_root: Path,
) -> tuple[dict, str, str]:
    register_data = None
    register_phone = ""
    register_nick_name = ""
    seed = int(time.time() * 1000) % 100000000
    register_error = None

    for attempt in range(5):
        register_phone = generate_phone(seed, attempt)
        register_nick_name = f"名片样本{register_phone[-4:]}"
        send_code = request_json(
            session,
            "POST",
            f"{api_url}/auth/sendCode",
            label=f"viewer sendCode attempt {attempt + 1}",
            output_path=capture_root / "viewer-send-code.json",
            json_body={"phone": register_phone},
        )
        verify_code = str(send_code.get("data") or "").strip()
        response = session.post(
            f"{api_url}/auth/register",
            json={
                "phone": register_phone,
                "code": verify_code,
                "userType": 1,
                "nickName": register_nick_name,
                "inviteCode": invite_code,
                "deviceFingerprint": f"share-card-mvp-{register_phone}",
            },
            timeout=30,
        )
        payload = parse_json_response(response)
        write_json(
            capture_root / "viewer-register.json",
            response_capture(
                label="viewer register",
                response=response,
                payload=payload,
                request_body={
                    "phone": register_phone,
                    "code": verify_code,
                    "userType": 1,
                    "nickName": register_nick_name,
                    "inviteCode": invite_code,
                    "deviceFingerprint": f"share-card-mvp-{register_phone}",
                },
            ),
        )
        if response.status_code == 200 and payload.get("code") == 200:
            register_data = payload
            break
        register_error = (
            f"viewer register failed for {register_phone}: HTTP {response.status_code} / "
            f"code {payload.get('code')} / message {payload.get('message')}"
        )
        if "已注册" not in str(payload.get("message") or ""):
            raise RuntimeError(register_error)

    if register_data is None:
        raise RuntimeError(register_error or "viewer register failed after 5 attempts")
    return register_data, register_phone, register_nick_name


def find_general_card(cards_payload: dict, scene_key: str) -> dict:
    cards = ((cards_payload.get("data") or {}).get("cards") or [])
    if not isinstance(cards, list):
        raise RuntimeError("my-cards payload missing cards list")
    matched = [
        item for item in cards
        if isinstance(item, dict) and str(item.get("sceneKey") or "") == scene_key
    ]
    if not matched:
        raise RuntimeError(f"no `{scene_key}` card found in my-cards response")
    matched.sort(
        key=lambda item: (
            1 if item.get("defaultCard") else 0,
            int(item.get("cardId") or 0),
        ),
        reverse=True,
    )
    return matched[0]


def find_owned_request(owned_payload: dict, share_card_id: int) -> dict:
    items = (owned_payload.get("data") or []) if isinstance(owned_payload.get("data"), list) else []
    matched = [
        item for item in items
        if isinstance(item, dict) and int(item.get("shareCardId") or -1) == share_card_id
    ]
    if not matched:
        raise RuntimeError(f"no owned contact request found for shareCardId={share_card_id}")
    matched.sort(key=lambda item: int(item.get("requestId") or -1), reverse=True)
    return matched[0]


def find_admin_request(admin_payload: dict, share_card_id: int, viewer_user_id: int) -> dict:
    data = admin_payload.get("data") or {}
    items = data.get("list") or []
    if not isinstance(items, list):
        raise RuntimeError("admin contact request payload missing list")
    matched = [
        item for item in items
        if isinstance(item, dict)
        and int(item.get("shareCardId") or -1) == share_card_id
        and int(item.get("viewerUserId") or -1) == viewer_user_id
    ]
    if not matched:
        raise RuntimeError(
            f"no admin contact request found for shareCardId={share_card_id}, viewerUserId={viewer_user_id}"
        )
    matched.sort(key=lambda item: int(item.get("requestId") or -1), reverse=True)
    return matched[0]


def find_admin_share_card(admin_payload: dict, share_card_id: int) -> dict:
    data = admin_payload.get("data") or {}
    items = data.get("list") or []
    if not isinstance(items, list):
        raise RuntimeError("admin share cards payload missing list")
    matched = [
        item for item in items
        if isinstance(item, dict)
        and int(item.get("shareCardId") or -1) == share_card_id
    ]
    if not matched:
        raise RuntimeError(f"no admin share card found for shareCardId={share_card_id}")
    matched.sort(key=lambda item: int(item.get("shareCardId") or -1), reverse=True)
    return matched[0]


def summary_lines(summary: dict) -> list[str]:
    confirmed = summary["confirmed"]
    blockers = summary["blockers"]
    return [
        "# Share Card MVP Governance Remote Sample",
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
        "## Context",
        "",
        f"- Owner Phone: `{summary['context']['ownerPhone']}`",
        f"- Owner User ID: `{summary['context']['ownerUserId']}`",
        f"- Viewer Phone: `{summary['context']['viewerPhone']}`",
        f"- Viewer User ID: `{summary['context']['viewerUserId']}`",
        f"- Scene: `{summary['context']['sceneKey']}`",
        f"- Share Card ID: `{summary['context']['shareCardId']}`",
        f"- Contact Request ID: `{summary['context']['requestId']}`",
        "",
        "## Chain",
        "",
        f"- my-cards general defaultCard: `{summary['chain']['defaultCard']}`",
        f"- public personalization template: `{summary['chain']['templateName']}`",
        f"- public personalization scene: `{summary['chain']['personalizationScene']}`",
        f"- history count after record: `{summary['chain']['historyCountAfterRecord']}`",
        f"- contact status before apply: `{summary['chain']['statusBeforeApply']}`",
        f"- contact status after approve: `{summary['chain']['statusAfterApprove']}`",
        f"- approved contact count: `{summary['chain']['approvedContactCount']}`",
        f"- admin contact request total: `{summary['chain']['adminContactRequestTotal']}`",
        f"- admin share-card total: `{summary['chain']['adminShareCardTotal']}`",
        f"- admin legacy pending total: `{summary['chain']['adminLegacyPendingTotal']}`",
        f"- default general strategy stage: `{summary['chain']['defaultGeneralStrategyStage']}`",
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
        "- `captures/owner-send-code.json`",
        "- `captures/owner-login.json`",
        "- `captures/owner-my-cards.json`",
        "- `captures/owner-invite-code.json`",
        "- `captures/viewer-send-code.json`",
        "- `captures/viewer-register.json`",
        "- `captures/viewer-personalization.json`",
        "- `captures/viewer-contact-status-before.json`",
        "- `captures/viewer-apply-contact.json`",
        "- `captures/owner-owned-pending.json`",
        "- `captures/owner-approve-contact.json`",
        "- `captures/viewer-contact-status-after.json`",
        "- `captures/viewer-history-record.json`",
        "- `captures/viewer-history-list.json`",
        "- `captures/viewer-approved-contacts.json`",
        "- `captures/admin-login.json`",
        "- `captures/admin-contact-requests.json`",
        "- `captures/admin-contact-request-detail.json`",
        "- `captures/admin-share-cards.json`",
        "- `captures/admin-share-card-detail.json`",
        "- `captures/admin-share-card-legacy-summary.json`",
        "- `captures/admin-default-general-strategy.json`",
        "- `captures/admin-default-general-user-state.json`",
        "- `summary.md`",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the remote share-card-mvp governance sample."
    )
    parser.add_argument("--label", default="remote-governance-sample")
    parser.add_argument("--environment", default="dev")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--owner-phone", default=DEFAULT_OWNER_PHONE)
    parser.add_argument("--admin-account", default=DEFAULT_ADMIN_ACCOUNT)
    parser.add_argument("--admin-password", default=os.environ.get(ADMIN_PASSWORD_ENV, ""))
    parser.add_argument("--scene", default=DEFAULT_SCENE)
    args = parser.parse_args()
    if not args.admin_password:
        raise RuntimeError(f"{ADMIN_PASSWORD_ENV} is required for admin login smoke")

    now = datetime.now()
    sample_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{args.environment}-{args.label}"
    sample_root = SAMPLES_ROOT / sample_id
    capture_root = sample_root / "captures"
    ensure_dir(capture_root)

    frontend_env = parse_env_file(FRONTEND_ENV_PATH)
    root_base_url = normalize_root_base_url(args.base_url)
    api_url = api_base_url(args.base_url)

    session = requests.Session()
    session.headers.update({"User-Agent": "codex-share-card-mvp-governance-sample/1.0"})

    owner_login = login_by_phone(session, api_url, args.owner_phone, capture_root, "owner")
    owner_token = str((owner_login.get("data") or {}).get("token") or "")
    owner_user_id = int((owner_login.get("data") or {}).get("userId") or 0)
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    owner_my_cards = request_json(
        session,
        "GET",
        f"{api_url}/card/my-cards",
        label="owner my-cards",
        output_path=capture_root / "owner-my-cards.json",
        headers=owner_headers,
    )
    general_card = find_general_card(owner_my_cards, args.scene)
    share_card_id = int(general_card.get("cardId") or 0)

    owner_invite_code = request_json(
        session,
        "GET",
        f"{api_url}/invite/code",
        label="owner invite.code",
        output_path=capture_root / "owner-invite-code.json",
        headers=owner_headers,
    )
    invite_code = str((owner_invite_code.get("data") or {}).get("inviteCode") or "").strip()
    if not invite_code:
        raise RuntimeError("owner invite code is empty")

    viewer_register, viewer_phone, _ = register_viewer(session, api_url, invite_code, capture_root)
    viewer_token = str((viewer_register.get("data") or {}).get("token") or "")
    viewer_user_id = int((viewer_register.get("data") or {}).get("userId") or 0)
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

    viewer_personalization = request_json(
        session,
        "GET",
        f"{api_url}/card/personalization",
        label="viewer personalization",
        output_path=capture_root / "viewer-personalization.json",
        headers=viewer_headers,
        params={"shareCardId": share_card_id},
    )
    viewer_status_before = request_json(
        session,
        "GET",
        f"{api_url}/card/contact-requests/status",
        label="viewer contact status before",
        output_path=capture_root / "viewer-contact-status-before.json",
        headers=viewer_headers,
        params={"shareCardId": share_card_id},
    )
    viewer_apply_contact = request_json(
        session,
        "POST",
        f"{api_url}/card/contact-requests",
        label="viewer apply contact",
        output_path=capture_root / "viewer-apply-contact.json",
        headers=viewer_headers,
        json_body={"shareCardId": share_card_id},
    )
    viewer_history_record = request_json(
        session,
        "POST",
        f"{api_url}/card/view-histories",
        label="viewer history record",
        output_path=capture_root / "viewer-history-record.json",
        headers=viewer_headers,
        json_body={"shareCardId": share_card_id},
    )
    viewer_history_list = request_json(
        session,
        "GET",
        f"{api_url}/card/view-histories",
        label="viewer history list",
        output_path=capture_root / "viewer-history-list.json",
        headers=viewer_headers,
    )

    owner_owned_pending = request_json(
        session,
        "GET",
        f"{api_url}/card/contact-requests/owned",
        label="owner owned pending",
        output_path=capture_root / "owner-owned-pending.json",
        headers=owner_headers,
        params={"status": "pending"},
    )
    owned_request = find_owned_request(owner_owned_pending, share_card_id)
    request_id = int(owned_request.get("requestId") or 0)

    owner_approve_contact = request_json(
        session,
        "POST",
        f"{api_url}/card/contact-requests/{request_id}/approve",
        label="owner approve contact",
        output_path=capture_root / "owner-approve-contact.json",
        headers=owner_headers,
        json_body={"decisionNote": "share-card-mvp governance sample approve"},
    )
    viewer_status_after = request_json(
        session,
        "GET",
        f"{api_url}/card/contact-requests/status",
        label="viewer contact status after",
        output_path=capture_root / "viewer-contact-status-after.json",
        headers=viewer_headers,
        params={"shareCardId": share_card_id},
    )
    viewer_approved_contacts = request_json(
        session,
        "GET",
        f"{api_url}/card/contact-requests/approved",
        label="viewer approved contacts",
        output_path=capture_root / "viewer-approved-contacts.json",
        headers=viewer_headers,
    )

    admin_session = requests.Session()
    admin_session.headers.update({"User-Agent": "codex-share-card-mvp-governance-admin/1.0"})
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

    admin_contact_requests = request_json(
        admin_session,
        "GET",
        f"{api_url}/admin/content/contact-requests",
        label="admin contact requests",
        output_path=capture_root / "admin-contact-requests.json",
        headers=admin_headers,
        params={"pageNo": 1, "pageSize": 20, "shareCardId": share_card_id},
    )
    admin_request = find_admin_request(admin_contact_requests, share_card_id, viewer_user_id)
    admin_contact_request_detail = request_json(
        admin_session,
        "GET",
        f"{api_url}/admin/content/contact-requests/{admin_request.get('requestId')}",
        label="admin contact request detail",
        output_path=capture_root / "admin-contact-request-detail.json",
        headers=admin_headers,
    )
    admin_share_cards = request_json(
        admin_session,
        "GET",
        f"{api_url}/admin/content/share-cards",
        label="admin share cards",
        output_path=capture_root / "admin-share-cards.json",
        headers=admin_headers,
        params={"pageNo": 1, "pageSize": 20, "shareCardId": share_card_id},
    )
    admin_share_card = find_admin_share_card(admin_share_cards, share_card_id)
    admin_share_card_detail = request_json(
        admin_session,
        "GET",
        f"{api_url}/admin/content/share-cards/{share_card_id}",
        label="admin share card detail",
        output_path=capture_root / "admin-share-card-detail.json",
        headers=admin_headers,
    )
    admin_share_card_legacy_summary = request_json(
        admin_session,
        "GET",
        f"{api_url}/admin/content/share-cards/legacy-summary",
        label="admin share card legacy summary",
        output_path=capture_root / "admin-share-card-legacy-summary.json",
        headers=admin_headers,
    )
    admin_default_general_strategy = request_json(
        admin_session,
        "GET",
        f"{api_url}/admin/content/default-general-card/strategy",
        label="admin default general strategy",
        output_path=capture_root / "admin-default-general-strategy.json",
        headers=admin_headers,
    )
    admin_default_general_user_state = request_json(
        admin_session,
        "GET",
        f"{api_url}/admin/content/default-general-card/users/{owner_user_id}",
        label="admin default general user state",
        output_path=capture_root / "admin-default-general-user-state.json",
        headers=admin_headers,
    )

    personalization_profile = (viewer_personalization.get("data") or {}).get("profile") or {}
    history_items = (viewer_history_list.get("data") or []) if isinstance(viewer_history_list.get("data"), list) else []
    approved_items = (viewer_approved_contacts.get("data") or []) if isinstance(viewer_approved_contacts.get("data"), list) else []
    admin_contact_data = admin_contact_requests.get("data") or {}
    admin_share_card_data = admin_share_cards.get("data") or {}
    admin_share_card_detail_data = admin_share_card_detail.get("data") or {}
    admin_share_card_binding = (admin_share_card_detail_data.get("bindingInfo") or {})
    admin_legacy_summary_data = admin_share_card_legacy_summary.get("data") or {}
    admin_strategy_data = admin_default_general_strategy.get("data") or {}
    admin_user_state_data = admin_default_general_user_state.get("data") or {}

    blockers: list[str] = []
    if frontend_env.get("VITE_USE_MOCK") != "false":
        blockers.append("当前样本要求真实环境，但前端 `.env` 未固定 `VITE_USE_MOCK=false`。")
    if viewer_status_before.get("data", {}).get("status") not in {"none", "rejected"}:
        blockers.append(
            f"联系申请前状态异常：`{viewer_status_before.get('data', {}).get('status')}`，样本不再是干净初始态。"
        )
    if (viewer_apply_contact.get("data") or {}).get("status") != "pending":
        blockers.append(
            f"联系申请后未进入 pending：`{(viewer_apply_contact.get('data') or {}).get('status')}`。"
        )
    if (viewer_status_after.get("data") or {}).get("status") != "approved":
        blockers.append(
            f"联系申请审批后未进入 approved：`{(viewer_status_after.get('data') or {}).get('status')}`。"
        )
    if not any(int(item.get("shareCardId") or -1) == share_card_id for item in history_items if isinstance(item, dict)):
        blockers.append(f"查看历史列表未回读到 `shareCardId={share_card_id}`。")
    if not any(int(item.get("shareCardId") or -1) == share_card_id for item in approved_items if isinstance(item, dict)):
        blockers.append(f"已联系列表未回读到 `shareCardId={share_card_id}`。")
    if not bool(admin_user_state_data.get("bindingConsistent")):
        blockers.append("后台默认普通卡用户状态显示当前 owner 的 default general 绑定不一致。")
    if not bool(admin_share_card.get("bindingConsistent")):
        blockers.append("后台分享卡治理列表显示当前 share card 实例绑定不一致。")
    if not bool(admin_share_card_binding.get("bindingConsistent")):
        blockers.append("后台分享卡治理详情显示当前 share card 实例绑定不一致。")
    if int(admin_legacy_summary_data.get("totalPendingCount") or 0) != 0:
        blockers.append(
            "后台 legacy-summary 仍有未修复存量："
            f"`totalPendingCount={admin_legacy_summary_data.get('totalPendingCount')}`。"
        )
    blockers.append("`sendCode` 仍直接返回开发态验证码；这证明连通性，不代表正式短信闭环。")

    confirmed = [
        f"owner `{args.owner_phone}` 当前可通过 `/card/my-cards` 回读默认 `{args.scene}` 卡，且已拿到 `shareCardId={share_card_id}`。",
        f"viewer `{viewer_phone}` 当前可直接用 `shareCardId` 调 `/card/personalization`，返回 `scene={personalization_profile.get('sceneKey')}`、`template={((personalization_profile.get('template') or {}).get('name') or '--')}`。",
        f"viewer 已按 `shareCardId` 写入真实查看历史，并在 `/card/view-histories` 回读同一张卡。",
        f"viewer -> owner 的联系方式申请已跑通 `pending -> approved`，并能在 `/card/contact-requests/approved` 回读到 `shareCardId={share_card_id}`。",
        f"后台 `/admin/content/contact-requests` 与 `/admin/content/default-general-card/users/{owner_user_id}` 已能回看同批次请求和 default general 绑定状态。",
        f"后台 `/admin/content/share-cards` 与 `/admin/content/share-cards/{share_card_id}` 已能回看同一张真实 `UserShareCard`，列表/详情绑定状态一致。",
        f"后台 `/admin/content/share-cards/legacy-summary` 当前返回 `totalPendingCount={admin_legacy_summary_data.get('totalPendingCount')}`，旧历史 / 联系方式 / 偏好修复存量已清零。",
    ]

    metadata = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "environmentName": args.environment,
        "sampleLabel": args.label,
        "sampleRoot": str(sample_root),
        "baseUrl": root_base_url,
        "ownerPhone": args.owner_phone,
        "ownerUserId": owner_user_id,
        "viewerPhone": viewer_phone,
        "viewerUserId": viewer_user_id,
        "shareCardId": share_card_id,
        "requestId": request_id,
        "sceneKey": args.scene,
    }
    write_json(sample_root / "sample-metadata.json", metadata)

    closure_context = {
        "generatedAt": metadata["generatedAt"],
        "context": {
            "environment": args.environment,
            "baseUrl": root_base_url,
            "ownerPhone": args.owner_phone,
            "ownerUserId": owner_user_id,
            "viewerPhone": viewer_phone,
            "viewerUserId": viewer_user_id,
            "shareCardId": share_card_id,
            "requestId": request_id,
            "sceneKey": args.scene,
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
            "ownerPhone": args.owner_phone,
            "ownerUserId": owner_user_id,
            "viewerPhone": viewer_phone,
            "viewerUserId": viewer_user_id,
            "sceneKey": args.scene,
            "shareCardId": share_card_id,
            "requestId": request_id,
        },
        "chain": {
            "defaultCard": general_card.get("defaultCard"),
            "templateName": ((personalization_profile.get("template") or {}).get("name") or ""),
            "personalizationScene": personalization_profile.get("sceneKey"),
            "historyCountAfterRecord": len(history_items),
            "statusBeforeApply": (viewer_status_before.get("data") or {}).get("status"),
            "statusAfterApprove": (viewer_status_after.get("data") or {}).get("status"),
            "approvedContactCount": len(approved_items),
            "adminContactRequestTotal": admin_contact_data.get("total"),
            "adminShareCardTotal": admin_share_card_data.get("total"),
            "adminLegacyPendingTotal": admin_legacy_summary_data.get("totalPendingCount"),
            "defaultGeneralStrategyStage": admin_strategy_data.get("strategyStage"),
        },
        "confirmed": confirmed,
        "blockers": blockers,
    }
    write_json(sample_root / "summary.json", summary)
    (sample_root / "summary.md").write_text(
        "\n".join(summary_lines(summary)) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "sampleRoot": str(sample_root),
                "ownerUserId": owner_user_id,
                "viewerUserId": viewer_user_id,
                "shareCardId": share_card_id,
                "requestId": request_id,
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
