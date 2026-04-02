import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

import requests


DEFAULT_BASE_URL = "http://101.43.57.62/api"
DEFAULT_ADMIN_ACCOUNT = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_ROOT = SCRIPT_DIR / "samples"
VALIDATION_SCRIPT = SCRIPT_DIR / "run-verify-validation.ps1"


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


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_payload(path: Path, payload: dict) -> None:
    write_json(path, payload)


def choose_verification_id(items: list[dict], *, exclude: str | None = None) -> str:
    sorted_items = sorted(
        (item for item in items if isinstance(item, dict)),
        key=lambda item: int(item.get("verificationId") or 0),
        reverse=True,
    )
    for item in sorted_items:
        current_id = str(item.get("verificationId") or "")
        if exclude and current_id == exclude:
            continue
        if current_id:
            return current_id
    raise RuntimeError("verification id not found")


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
        "-EnvironmentName",
        context["environment"],
        "-ApiBaseUrl",
        context["baseUrl"],
        "-ActorToken",
        context["actorToken"],
        "-AdminToken",
        context["adminToken"],
        "-UserId",
        str(context["userId"]),
        "-VerificationId",
        str(context["verificationId"]),
        "-RetryVerificationId",
        str(context["retryVerificationId"]),
        "-OutputDir",
        str(output_dir),
    ]
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a fresh verify sample and drive it through submit, reject, resubmit, and approve."
    )
    parser.add_argument("--label", default="remote-verify-reject-retry-approve")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--environment", default="dev")
    parser.add_argument("--admin-account", default=DEFAULT_ADMIN_ACCOUNT)
    parser.add_argument("--admin-password", default=DEFAULT_ADMIN_PASSWORD)
    args = parser.parse_args()

    now = datetime.now()
    sample_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{args.environment}-{args.label}"
    output_dir = SAMPLES_ROOT / sample_id
    captures_dir = output_dir / "captures"
    ensure_dir(captures_dir)

    base_url = normalize_root_base_url(args.base_url)
    api_url = api_base_url(args.base_url)
    session = requests.Session()
    session.headers.update({"User-Agent": "codex-verify-e2e-closure/1.0"})

    admin_login = session.post(
        f"{api_url}/admin/auth/login",
        json={"account": args.admin_account, "password": args.admin_password},
        timeout=30,
    )
    admin_payload = require_success(admin_login, label="admin login")
    save_payload(captures_dir / "admin_login.json", admin_payload)
    admin_token = admin_payload["data"]["accessToken"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    phone_suffix = now.strftime("%d%H%M%S")
    actor_phone = f"139{phone_suffix}"

    actor_send_code = session.post(
        f"{api_url}/auth/sendCode",
        json={"phone": actor_phone},
        timeout=30,
    )
    actor_send_code_payload = require_success(actor_send_code, label="actor sendCode")
    save_payload(captures_dir / "actor_send_code_register.json", actor_send_code_payload)
    actor_code = str(actor_send_code_payload["data"])

    register_payload = require_success(
        session.post(
            f"{api_url}/auth/register",
            json={
                "phone": actor_phone,
                "code": actor_code,
                "userType": 1,
                "nickName": f"Verify{phone_suffix}",
                "deviceFingerprint": f"verify-e2e-{sample_id}",
            },
            timeout=30,
        ),
        label="actor register",
    )
    save_payload(captures_dir / "actor_register.json", register_payload)
    actor_token = register_payload["data"]["token"]
    actor_user_id = register_payload["data"]["userId"]
    actor_headers = {"Authorization": f"Bearer {actor_token}"}

    profile_payload = {
        "name": f"Verify{phone_suffix}",
        "gender": "male",
        "age": 26,
        "height": 181,
        "weight": 70,
        "city": "Shanghai",
        "birthday": "1998-01-01",
        "birthHour": "zi",
        "avatar": "https://example.com/avatar.jpg",
        "intro": "Verify reject retry approve closure sample.",
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
                "projectName": "Spec Verify Closure",
                "roleName": "Lead",
                "shootDate": "2025-08",
                "photos": [],
                "description": "Validated verify reject retry approve closure.",
            }
        ],
        "bodyType": "athletic",
        "hairStyle": "short",
        "languages": ["mandarin"],
        "contactPhone": actor_phone,
    }
    profile_result = require_success(
        session.put(
            f"{api_url}/actor/profile",
            headers=actor_headers,
            json=profile_payload,
            timeout=30,
        ),
        label="actor save profile",
    )
    save_payload(captures_dir / "actor_save_profile.json", profile_result)

    initial_status = require_success(
        session.get(f"{api_url}/verify/status", headers=actor_headers, timeout=30),
        label="actor verify status initial",
    )
    save_payload(captures_dir / "actor_verify_status_initial.json", initial_status)

    id_card_no = f"11010119900101{phone_suffix[-4:]}"
    real_name = f"测试{phone_suffix[-4:]}"
    submit_first = require_success(
        session.post(
            f"{api_url}/verify/submit",
            headers=actor_headers,
            json={"realName": real_name, "idCardNo": id_card_no},
            timeout=30,
        ),
        label="actor verify submit first",
    )
    save_payload(captures_dir / "actor_verify_submit_first.json", submit_first)

    list_after_first_submit = require_success(
        session.get(
            f"{api_url}/admin/verify/list",
            headers=admin_headers,
            params={"pageNo": 1, "pageSize": 20, "userId": actor_user_id},
            timeout=30,
        ),
        label="admin verify list after first submit",
    )
    save_payload(captures_dir / "admin_verify_list_after_first_submit.json", list_after_first_submit)
    first_items = list_after_first_submit.get("data", {}).get("list", [])
    first_verification_id = choose_verification_id(first_items)

    detail_first = require_success(
        session.get(f"{api_url}/admin/verify/{first_verification_id}", headers=admin_headers, timeout=30),
        label="admin verify detail first",
    )
    save_payload(captures_dir / "admin_verify_detail_first_before_reject.json", detail_first)

    reject_payload = require_success(
        session.post(
            f"{api_url}/admin/verify/{first_verification_id}/reject",
            headers=admin_headers,
            json={"remark": "spec verify reject first pass"},
            timeout=30,
        ),
        label="admin verify reject first",
    )
    save_payload(captures_dir / "admin_verify_reject_first.json", reject_payload)

    status_after_reject = require_success(
        session.get(f"{api_url}/verify/status", headers=actor_headers, timeout=30),
        label="actor verify status after reject",
    )
    save_payload(captures_dir / "actor_verify_status_after_reject.json", status_after_reject)

    submit_second = require_success(
        session.post(
            f"{api_url}/verify/submit",
            headers=actor_headers,
            json={"realName": real_name, "idCardNo": id_card_no},
            timeout=30,
        ),
        label="actor verify submit second",
    )
    save_payload(captures_dir / "actor_verify_submit_second.json", submit_second)

    list_after_resubmit = require_success(
        session.get(
            f"{api_url}/admin/verify/list",
            headers=admin_headers,
            params={"pageNo": 1, "pageSize": 20, "userId": actor_user_id},
            timeout=30,
        ),
        label="admin verify list after resubmit",
    )
    save_payload(captures_dir / "admin_verify_list_after_resubmit.json", list_after_resubmit)
    retry_items = list_after_resubmit.get("data", {}).get("list", [])
    retry_verification_id = choose_verification_id(retry_items, exclude=first_verification_id)

    detail_retry_before_approve = require_success(
        session.get(f"{api_url}/admin/verify/{retry_verification_id}", headers=admin_headers, timeout=30),
        label="admin verify detail retry before approve",
    )
    save_payload(captures_dir / "admin_verify_detail_retry_before_approve.json", detail_retry_before_approve)

    approve_payload = require_success(
        session.post(
            f"{api_url}/admin/verify/{retry_verification_id}/approve",
            headers=admin_headers,
            json={"remark": "spec verify approve retry pass"},
            timeout=30,
        ),
        label="admin verify approve retry",
    )
    save_payload(captures_dir / "admin_verify_approve_retry.json", approve_payload)

    final_status = require_success(
        session.get(f"{api_url}/verify/status", headers=actor_headers, timeout=30),
        label="actor verify status final",
    )
    save_payload(captures_dir / "actor_verify_status_final.json", final_status)

    final_level = require_success(
        session.get(f"{api_url}/level/info", headers=actor_headers, timeout=30),
        label="actor level info final",
    )
    save_payload(captures_dir / "actor_level_info_final.json", final_level)

    final_list = require_success(
        session.get(
            f"{api_url}/admin/verify/list",
            headers=admin_headers,
            params={"pageNo": 1, "pageSize": 20, "userId": actor_user_id},
            timeout=30,
        ),
        label="admin verify list final",
    )
    save_payload(captures_dir / "admin_verify_list_final.json", final_list)

    context = {
        "sampleLabel": args.label,
        "baseUrl": base_url,
        "environment": args.environment,
        "adminToken": admin_token,
        "actorToken": actor_token,
        "userId": actor_user_id,
        "verificationId": first_verification_id,
        "retryVerificationId": retry_verification_id,
        "phone": actor_phone,
        "realName": real_name,
        "idCardNo": id_card_no,
    }
    write_json(output_dir / "closure-context.json", {
        "generatedAt": now.isoformat(),
        "context": context,
    })

    run_validation(context, output_dir)

    summary_lines = [
        "# Verify End-to-End Closure Sample",
        "",
        f"- Generated At: `{now.isoformat(timespec='seconds')}`",
        f"- Environment: `{args.environment}`",
        f"- Base URL: `{base_url}`",
        f"- User ID: `{actor_user_id}`",
        f"- Phone: `{actor_phone}`",
        f"- First Verification ID: `{first_verification_id}`",
        f"- Retry Verification ID: `{retry_verification_id}`",
        "",
        "## Outcome",
        "",
        f"- Final verify status: `{final_status['data']['status']}`",
        f"- Final level isCertified: `{final_level['data']['isCertified']}`",
    ]
    (output_dir / "closure-summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(
        f"verify e2e closure sample prepared: {output_dir}\n"
        f"context: userId={actor_user_id}, phone={actor_phone}, "
        f"firstVerificationId={first_verification_id}, retryVerificationId={retry_verification_id}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
