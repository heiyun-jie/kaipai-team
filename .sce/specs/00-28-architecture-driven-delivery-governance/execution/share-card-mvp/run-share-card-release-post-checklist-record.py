import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_ROOT = SCRIPT_DIR / "samples"
LOGIN_AUTH_SAMPLES_ROOT = SCRIPT_DIR.parent / "login-auth" / "samples"
CHECKLIST_SOURCE = SCRIPT_DIR / "release-post-checklist.md"
RELEASE_RECORDS_ROOT = SCRIPT_DIR.parents[3] / "runbooks" / "backend-admin-release" / "records"
WS_ENDPOINT = "ws://127.0.0.1:9421"
AUTO_LATEST_SAMPLE_WAIT_SECONDS = 30.0
AUTO_LATEST_SAMPLE_POLL_INTERVAL_SECONDS = 0.25
AUTO_LATEST_SAMPLE_STABILIZATION_WINDOW_SECONDS = 30.0


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def list_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        [item for item in root.iterdir() if item.is_dir()],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )


def wait_for_latest_matching_sample(root: Path, name_hint: str, required_file: str) -> None:
    deadline = time.monotonic() + AUTO_LATEST_SAMPLE_WAIT_SECONDS
    while True:
        matching_candidates = [item for item in list_dirs(root) if name_hint in item.name]
        if not matching_candidates:
            return
        newest_candidate = matching_candidates[0]
        if (newest_candidate / required_file).exists():
            return
        candidate_age_seconds = time.time() - newest_candidate.stat().st_mtime
        if candidate_age_seconds > AUTO_LATEST_SAMPLE_STABILIZATION_WINDOW_SECONDS:
            return
        if time.monotonic() >= deadline:
            return
        time.sleep(AUTO_LATEST_SAMPLE_POLL_INTERVAL_SECONDS)


def resolve_sample_with_auto_preferred_files_and_selection(
    root: Path,
    explicit: str | None,
    name_hint: str,
    explicit_required_file: str,
    auto_preferred_required_files: list[str],
) -> tuple[Path, str]:
    if explicit:
        candidate = root / explicit
        if not candidate.exists():
            raise RuntimeError(f"sample not found: {candidate}")
        if not (candidate / explicit_required_file).exists():
            raise RuntimeError(f"sample missing required file `{explicit_required_file}`: {candidate}")
        return candidate, "explicit_arg"

    for required_file in auto_preferred_required_files:
        wait_for_latest_matching_sample(root, name_hint, required_file)
        for candidate in list_dirs(root):
            if name_hint not in candidate.name:
                continue
            if (candidate / required_file).exists():
                return candidate, "auto_latest"

    required_files_display = " / ".join(f"`{item}`" for item in auto_preferred_required_files)
    raise RuntimeError(
        f"no sample found under {root} matching `{name_hint}` with any of {required_files_display}"
    )


def resolve_sample_with_auto_preferred_files(
    root: Path,
    explicit: str | None,
    name_hint: str,
    explicit_required_file: str,
    auto_preferred_required_files: list[str],
) -> Path:
    candidate, _ = resolve_sample_with_auto_preferred_files_and_selection(
        root,
        explicit,
        name_hint,
        explicit_required_file,
        auto_preferred_required_files,
    )
    return candidate


def resolve_optional_sample_with_auto_preferred_files(
    root: Path,
    explicit: str | None,
    name_hint: str,
    explicit_required_file: str,
    auto_preferred_required_files: list[str],
) -> tuple[Path | None, str]:
    if explicit:
        candidate = root / explicit
        if not candidate.exists():
            raise RuntimeError(f"sample not found: {candidate}")
        if not (candidate / explicit_required_file).exists():
            raise RuntimeError(f"sample missing required file `{explicit_required_file}`: {candidate}")
        return candidate, "explicit_arg"

    for required_file in auto_preferred_required_files:
        wait_for_latest_matching_sample(root, name_hint, required_file)
        for candidate in list_dirs(root):
            if name_hint not in candidate.name:
                continue
            if (candidate / required_file).exists():
                return candidate, "auto_latest"
    return None, "missing"


def resolve_sample(root: Path, explicit: str | None, name_hint: str, required_file: str) -> Path:
    return resolve_sample_with_auto_preferred_files(
        root,
        explicit,
        name_hint,
        required_file,
        [required_file],
    )


def resolve_optional_sample(root: Path, explicit: str | None, name_hint: str, required_file: str) -> tuple[Path | None, str]:
    return resolve_optional_sample_with_auto_preferred_files(
        root,
        explicit,
        name_hint,
        required_file,
        [required_file],
    )


def build_optional_sample_selection_note(selection_mode: str, name_hint: str, required_file: str) -> str:
    if selection_mode == "explicit_arg":
        return "本轮通过 `--mini-blocker-sample` 显式指定 blocker 样本。"
    if selection_mode == "auto_latest":
        return f"未显式传 `--mini-blocker-sample`，已自动选择最新且匹配 `{name_hint}` / `{required_file}` 的 blocker 样本。"
    return f"当前未找到匹配 `{name_hint}` / `{required_file}` 的 blocker 样本。"


def build_optional_sample_selection_display(selection_mode: str) -> str:
    if selection_mode == "explicit_arg":
        return "显式指定 blocker 样本"
    if selection_mode == "auto_latest":
        return "自动命中最新 blocker 样本"
    return "未命中 blocker 样本"


def build_required_sample_selection_note(
    selection_mode: str,
    cli_flag: str,
    name_hint: str,
    preferred_required_file: str,
    sample_display_name: str,
) -> str:
    if selection_mode == "explicit_arg":
        return f"本轮通过 `{cli_flag}` 显式指定{sample_display_name}。"
    if selection_mode == "auto_latest":
        return f"未显式传 `{cli_flag}`，已自动选择最新且匹配 `{name_hint}` / `{preferred_required_file}` 的{sample_display_name}。"
    return f"当前未命中{sample_display_name}。"


def build_required_sample_selection_display(selection_mode: str, sample_display_name: str) -> str:
    if selection_mode == "explicit_arg":
        return f"显式指定{sample_display_name}"
    if selection_mode == "auto_latest":
        return f"自动命中最新{sample_display_name}"
    return f"未命中{sample_display_name}"


def resolve_release_record(explicit: str | None, required_tokens: list[str]) -> Path | None:
    if explicit:
        candidate = RELEASE_RECORDS_ROOT / explicit
        if not candidate.exists():
            raise RuntimeError(f"release record not found: {candidate}")
        return candidate

    if not RELEASE_RECORDS_ROOT.exists():
        return None

    candidates = sorted(RELEASE_RECORDS_ROOT.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True)
    for candidate in candidates:
        name = candidate.name.lower()
        if all(token in name for token in required_tokens):
            return candidate
    return None


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text_if_exists(path: Path | None) -> str:
    if not path or not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def to_relpath(path: Path, start: Path) -> str:
    return os.path.relpath(path, start).replace("/", "\\")


def parse_status_code(text: str) -> int | None:
    if not text:
        return None
    if "status=" in text:
        suffix = text.split("status=", 1)[1].strip()
        digits = "".join(ch for ch in suffix if ch.isdigit())
        return int(digits) if digits else None
    if "HTTP/1.1" in text:
        suffix = text.split("HTTP/1.1", 1)[1].strip()
        digits = suffix.split()[0] if suffix else ""
        return int(digits) if digits.isdigit() else None
    if "->" in text:
        suffix = text.rsplit("->", 1)[1].replace("`", "").strip()
        digits = "".join(ch for ch in suffix if ch.isdigit())
        return int(digits) if digits else None
    return None


def find_status_for_marker(lines: list[str], marker: str) -> tuple[str, int | None]:
    for index, raw_line in enumerate(lines):
        normalized_line = raw_line.strip().replace("`", "")
        if marker not in normalized_line:
            continue
        if "->" in normalized_line or normalized_line.startswith("status=") or normalized_line.startswith("HTTP/1.1"):
            return normalized_line, parse_status_code(normalized_line)
        for follow_raw_line in lines[index + 1 : index + 12]:
            follow_line = follow_raw_line.strip().replace("`", "")
            if not follow_line or follow_line in {"```text", "```json", "```html"}:
                continue
            if follow_line == "```":
                break
            if follow_line.startswith("- "):
                break
            if follow_line.startswith("status=") or follow_line.startswith("HTTP/1.1"):
                return f"{normalized_line} | {follow_line}", parse_status_code(follow_line)
    return "", None


def record_business_smoke_status(
    structured_smoke: dict,
    business_entry: str,
    status_line: str,
) -> None:
    if not business_entry:
        return

    combined_line = business_entry.replace("`", "")
    if status_line:
        combined_line = f"{combined_line} | {status_line}"
    status_code = parse_status_code(status_line or business_entry)

    details = structured_smoke.setdefault("businessSmokeDetails", [])
    details.append(
        {
            "entry": business_entry,
            "statusLine": status_line,
            "statusCode": status_code,
        }
    )

    if "/api/admin/auth/login" in business_entry:
        structured_smoke["adminLoginStatusLine"] = combined_line
        structured_smoke["adminLoginStatusCode"] = status_code
    elif "/api/v3/api-docs" in business_entry:
        structured_smoke["apiDocsStatusLine"] = combined_line
        structured_smoke["apiDocsStatusCode"] = status_code
    elif "/api/admin/recruit/roles" in business_entry:
        structured_smoke["adminRecruitRolesStatusLine"] = combined_line
        structured_smoke["adminRecruitRolesStatusCode"] = status_code
    elif "/api/role/search" in business_entry:
        structured_smoke["actorRoleSearchStatusLine"] = combined_line
        structured_smoke["actorRoleSearchStatusCode"] = status_code
    elif "/assets/" in business_entry:
        structured_smoke["staticAssetStatusLine"] = combined_line
        structured_smoke["staticAssetStatusCode"] = status_code
    elif "http://101.43.57.62/" in business_entry:
        structured_smoke["publicHomeStatusLine"] = combined_line
        structured_smoke["publicHomeStatusCode"] = status_code


def apply_expected_statuses(structured_smoke: dict) -> None:
    expected_statuses = {
        "apiDocs": 200,
        "adminLogin": 200,
        "publicHome": 200,
        "staticAsset": 200,
        "adminRecruitRoles": 401,
        "actorRoleSearch": 401,
    }

    expectations = structured_smoke.setdefault("statusExpectations", {})
    for prefix, expected_status in expected_statuses.items():
        status_code_key = f"{prefix}StatusCode"
        if status_code_key not in structured_smoke:
            continue
        expected_key = f"{prefix}ExpectedStatusCode"
        matches_key = f"{prefix}MatchesExpected"
        structured_smoke[expected_key] = expected_status
        structured_smoke[matches_key] = structured_smoke[status_code_key] == expected_status
        expectations[prefix] = {
            "expectedStatusCode": expected_status,
            "actualStatusCode": structured_smoke[status_code_key],
            "matchesExpected": structured_smoke[matches_key],
        }


def build_status_verdict(expected_status_code: int, actual_status_code: int | None) -> str:
    if actual_status_code is None:
        return "missing"
    if actual_status_code != expected_status_code:
        return "mismatch"
    if actual_status_code == 401:
        return "pass_expected_unauthorized"
    return "pass"


def apply_status_verdicts(structured_smoke: dict) -> None:
    expectations = structured_smoke.get("statusExpectations") or {}
    verdicts = structured_smoke.setdefault("statusVerdicts", {})
    for prefix, payload in expectations.items():
        expected_status_code = payload.get("expectedStatusCode")
        actual_status_code = payload.get("actualStatusCode")
        verdict = build_status_verdict(expected_status_code, actual_status_code)
        structured_smoke[f"{prefix}Verdict"] = verdict
        verdicts[prefix] = verdict


def apply_release_overall_verdict(scope: str, structured_smoke: dict) -> None:
    failed_keys: list[str] = []
    missing_keys: list[str] = []

    if scope == "backend-schema":
        if "migrationApplied" not in structured_smoke:
            missing_keys.append("migrationApplied")
        elif not structured_smoke.get("migrationApplied"):
            failed_keys.append("migrationApplied")
    else:
        verdicts = structured_smoke.get("statusVerdicts") or {}
        for key, verdict in verdicts.items():
            if verdict == "missing":
                missing_keys.append(key)
            elif verdict == "mismatch":
                failed_keys.append(key)

    if failed_keys:
        overall_verdict = "failed"
    elif missing_keys:
        overall_verdict = "missing"
    else:
        overall_verdict = "pass"

    structured_smoke["overallVerdict"] = overall_verdict
    structured_smoke["failedKeys"] = failed_keys
    structured_smoke["missingKeys"] = missing_keys


def extract_release_summary(record_path: Path | None) -> dict | None:
    if not record_path or not record_path.exists():
        return None

    lines = record_path.read_text(encoding="utf-8").splitlines()
    summary = {
        "file": record_path.name,
        "releaseId": "",
        "releasedAt": "",
        "scope": "",
        "conclusion": "",
        "smoke": [],
        "structuredSmoke": {},
    }

    in_smoke = False
    current_section = ""
    current_business_entry = ""
    code_block_lines: list[str] = []
    in_code_block = False
    for raw_line in lines:
        line = raw_line.strip()
        normalized_line = line.replace("`", "")
        if line.startswith("- 发布批次号："):
            summary["releaseId"] = line.split("`")[1] if "`" in line else line
        elif line.startswith("- 发布时间："):
            summary["releasedAt"] = line.split("`")[1] if "`" in line else line
        elif line.startswith("- 发布范围："):
            summary["scope"] = line.split("`")[1] if "`" in line else line
        elif line.startswith("- 最终结论："):
            summary["conclusion"] = line.split("`")[1] if "`" in line else line
        elif line == "```text" or line == "```json" or line == "```html":
            in_code_block = True
            code_block_lines = []
            continue
        elif line == "```" and in_code_block:
            in_code_block = False
            if current_section == "backend_container_status" and code_block_lines:
                backend_line = next((item for item in code_block_lines if item.startswith("kaipai-backend")), "")
                summary["structuredSmoke"]["backendContainerStatusLine"] = backend_line
                summary["structuredSmoke"]["backendContainerUp"] = "Up" in backend_line
            elif current_section == "api_docs" and code_block_lines:
                first_line = next((item for item in code_block_lines if item.startswith("status=") or item.startswith("HTTP/1.1")), "")
                summary["structuredSmoke"]["apiDocsStatusLine"] = first_line
                summary["structuredSmoke"]["apiDocsStatusCode"] = parse_status_code(first_line)
            elif current_section == "static_index" and code_block_lines:
                first_line = next((item for item in code_block_lines if "<!doctype html>" in item.lower()), "")
                summary["structuredSmoke"]["staticIndexHtmlPresent"] = bool(first_line)
            elif current_section == "business_entry" and code_block_lines:
                first_line = next((item for item in code_block_lines if item.startswith("status=") or item.startswith("HTTP/1.1")), "")
                if current_business_entry:
                    record_business_smoke_status(
                        summary["structuredSmoke"],
                        current_business_entry,
                        first_line,
                    )
            current_business_entry = ""
            continue
        elif in_code_block:
            code_block_lines.append(line)
            continue
        elif line == "## 5. smoke 结果":
            in_smoke = True
            continue
        elif line.startswith("## ") and in_smoke:
            in_smoke = False
        elif in_smoke and line.startswith("- "):
            summary["smoke"].append(line[2:])
            title = line[2:]
            normalized_title = title.replace("`", "")
            if normalized_title.startswith("后端容器状态"):
                current_section = "backend_container_status"
            elif "/api/v3/api-docs" in normalized_title:
                current_section = "api_docs"
            elif normalized_title.startswith("公网首页 HTML"):
                current_section = "static_index"
            elif normalized_title.startswith("业务接口 smoke"):
                current_section = "business_smoke"
            elif normalized_title.startswith("管理端首页"):
                current_section = "admin_home_smoke"
            else:
                current_section = ""
        elif in_smoke and current_section == "business_smoke" and line.startswith("- 公网："):
            business = summary["structuredSmoke"].setdefault("businessSmoke", [])
            business.append(line[2:])
            record_business_smoke_status(summary["structuredSmoke"], line[2:], "")
            current_section = "business_entry"
            current_business_entry = line[2:]
        elif in_smoke and current_section == "business_smoke" and line.startswith("- 内网："):
            business = summary["structuredSmoke"].setdefault("businessSmoke", [])
            business.append(line[2:])
            current_section = "business_entry"
            current_business_entry = line[2:]
        elif in_smoke and current_section == "admin_home_smoke" and line.startswith("- 公网："):
            admin_home = summary["structuredSmoke"].setdefault("adminHomeSmoke", [])
            admin_home.append(line[2:])
            if "http://101.43.57.62/ ->" in line:
                summary["structuredSmoke"]["publicHomeStatusLine"] = line[2:]
                summary["structuredSmoke"]["publicHomeStatusCode"] = parse_status_code(line[2:])
            if "/assets/" in line and "->" in line:
                summary["structuredSmoke"]["staticAssetStatusLine"] = line[2:]
                summary["structuredSmoke"]["staticAssetStatusCode"] = parse_status_code(line[2:])
        elif "公网首页 HTML" in normalized_line:
            current_section = "static_index"
        elif current_section == "static_index" and "<!doctype html>" in normalized_line.lower():
            summary["structuredSmoke"]["staticIndexHtmlPresent"] = True
        elif summary["scope"] == "backend-schema" and line.startswith("- `V") and "__" in line:
            summary["structuredSmoke"]["schemaMigrationFile"] = line.split("`")[1] if "`" in line else line
        elif summary["scope"] == "backend-schema" and line.startswith("- status:"):
            summary["structuredSmoke"]["schemaMigrationStatus"] = line.split("`")[1] if "`" in line else line.replace("- status:", "").strip()
            summary["structuredSmoke"]["migrationApplied"] = "applied" in summary["structuredSmoke"]["schemaMigrationStatus"].lower()

    structured_smoke = summary["structuredSmoke"]
    structured_smoke["staticIndexHtmlPresent"] = bool(
        structured_smoke.get("staticIndexHtmlPresent")
        or any("<!doctype html>" in line.lower() for line in lines)
    )

    if "apiDocsStatusLine" not in structured_smoke:
        api_docs_line, api_docs_code = find_status_for_marker(lines, "/api/v3/api-docs")
        if api_docs_line:
            structured_smoke["apiDocsStatusLine"] = api_docs_line
            structured_smoke["apiDocsStatusCode"] = api_docs_code

    if "adminLoginStatusLine" not in structured_smoke:
        admin_login_line, admin_login_code = find_status_for_marker(lines, "/api/admin/auth/login")
        if admin_login_line:
            structured_smoke["adminLoginStatusLine"] = admin_login_line
            structured_smoke["adminLoginStatusCode"] = admin_login_code

    if "publicHomeStatusLine" not in structured_smoke:
        public_home_line, public_home_code = find_status_for_marker(lines, "http://101.43.57.62/ ->")
        if public_home_line:
            structured_smoke["publicHomeStatusLine"] = public_home_line
            structured_smoke["publicHomeStatusCode"] = public_home_code

    if "staticAssetStatusLine" not in structured_smoke:
        static_asset_line, static_asset_code = find_status_for_marker(lines, "/assets/")
        if static_asset_line:
            structured_smoke["staticAssetStatusLine"] = static_asset_line
            structured_smoke["staticAssetStatusCode"] = static_asset_code

    if "adminRecruitRolesStatusLine" not in structured_smoke:
        recruit_roles_line, recruit_roles_code = find_status_for_marker(lines, "/api/admin/recruit/roles")
        if recruit_roles_line:
            structured_smoke["adminRecruitRolesStatusLine"] = recruit_roles_line
            structured_smoke["adminRecruitRolesStatusCode"] = recruit_roles_code

    if "actorRoleSearchStatusLine" not in structured_smoke:
        actor_role_search_line, actor_role_search_code = find_status_for_marker(lines, "/api/role/search")
        if actor_role_search_line:
            structured_smoke["actorRoleSearchStatusLine"] = actor_role_search_line
            structured_smoke["actorRoleSearchStatusCode"] = actor_role_search_code

    if "publicHomeStatusCode" in structured_smoke:
        structured_smoke["publicHomeUp"] = structured_smoke["publicHomeStatusCode"] == 200
    if "staticAssetStatusCode" in structured_smoke:
        structured_smoke["staticAssetUp"] = structured_smoke["staticAssetStatusCode"] == 200
    if "adminLoginStatusCode" in structured_smoke:
        structured_smoke["adminLoginSuccess"] = structured_smoke["adminLoginStatusCode"] == 200
    if "adminRecruitRolesStatusCode" in structured_smoke:
        structured_smoke["adminRecruitRolesUnauthorized"] = structured_smoke["adminRecruitRolesStatusCode"] == 401
    if "actorRoleSearchStatusCode" in structured_smoke:
        structured_smoke["actorRoleSearchUnauthorized"] = structured_smoke["actorRoleSearchStatusCode"] == 401
    apply_expected_statuses(structured_smoke)
    apply_status_verdicts(structured_smoke)
    apply_release_overall_verdict(summary["scope"], structured_smoke)

    return summary


def extract_mini_program_blocker_summary(sample_dir: Path | None) -> dict | None:
    if not sample_dir:
        return None

    summary_text = read_text_if_exists(sample_dir / "summary.md")
    result_path = sample_dir / "page-evidence-result.json"
    blocker_text = read_text_if_exists(sample_dir / "captures" / "devtools-auth-blocker.txt")
    cli_stdout_text = read_text_if_exists(sample_dir / "captures" / "devtools-cli-auto.stdout.log")
    cli_stderr_text = read_text_if_exists(sample_dir / "captures" / "devtools-cli-auto.stderr.log")
    port_check_text = read_text_if_exists(sample_dir / "captures" / "port-check.txt")
    stderr_text = read_text_if_exists(sample_dir / "captures" / "mini-program-screenshot-capture.stderr.log")
    result_payload = read_json(result_path) if result_path.exists() else {}

    combined_text = "\n".join(
        text
        for text in [
            summary_text,
            blocker_text,
            cli_stdout_text,
            cli_stderr_text,
            port_check_text,
            stderr_text,
        ]
        if text
    )

    return {
        "sampleId": sample_dir.name,
        "summaryPath": str(sample_dir / "summary.md"),
        "resultPath": str(result_path),
        "summaryPresent": bool(summary_text),
        "blockerPackagePresent": (sample_dir / "captures" / "devtools-auth-blocker.txt").exists(),
        "statusBlocked": "Status: `blocked`" in summary_text,
        "wsEndpointUnavailable": f"Failed connecting to {WS_ENDPOINT}" in combined_text,
        "devtoolsAuthGate": "登录用户不是该小程序的开发者" in combined_text,
        "portNoListener": "NO_LISTENER" in port_check_text,
        "preflightProbeSample": str(result_payload.get("preflightProbeSample") or ""),
        "preflightProbeResult": str(result_payload.get("preflightProbeResult") or ""),
        "preflightPortCheck": str(result_payload.get("preflightPortCheck") or ""),
        "preflightProbeSummaryPath": str(result_payload.get("preflightProbeSummaryPath") or ""),
        "preflightProbeResultPath": str(result_payload.get("preflightProbeResultPath") or ""),
    }


def sort_known_blockers(known_blockers: list[dict]) -> list[dict]:
    priority = {
        "mini_program_devtools_auth_gate": 30,
        "send_code_dev_mode": 40,
    }
    return sorted(
        known_blockers,
        key=lambda item: (
            priority.get(str(item.get("key") or ""), 999),
            str(item.get("key") or ""),
        ),
    )


def build_checks(
    *,
    api_summary: dict,
    mini_manifest: dict,
    mini_blocker_summary: dict | None,
    admin_manifest: dict,
    admin_share_cards_page_data: dict,
    sms_bridge_summary_text: str,
    release_summaries: dict,
) -> dict:
    api_chain = api_summary.get("chain") or {}
    admin_legacy_pending_total = api_chain.get("adminLegacyPendingTotal")
    api_checks = {
        "my_cards_general": bool(api_chain.get("defaultCard")),
        "personalization_by_share_card_id": bool(api_chain.get("personalizationScene")),
        "view_histories_roundtrip": int(api_chain.get("historyCountAfterRecord") or 0) > 0,
        "contact_request_pending_to_approved": api_chain.get("statusAfterApprove") == "approved",
        "admin_share_cards_list": int(api_chain.get("adminShareCardTotal") or 0) > 0,
        "admin_share_card_detail": "bindingConsistent=true" in sms_bridge_summary_text or bool(
            (((admin_share_cards_page_data.get("apiData") or {}).get("detail") or {}).get("responseJson") or {})
            .get("data", {})
            .get("bindingInfo", {})
            .get("bindingConsistent")
        ),
        "admin_legacy_summary": admin_legacy_pending_total is not None,
        "legacy_pending_zero": int(admin_legacy_pending_total if admin_legacy_pending_total is not None else -1) == 0,
        "binding_consistent": bool(
            (((admin_share_cards_page_data.get("apiData") or {}).get("detail") or {}).get("responseJson") or {})
            .get("data", {})
            .get("bindingInfo", {})
            .get("bindingConsistent")
        ),
    }

    mini_capture_names = {item.get("name"): item for item in mini_manifest.get("captures") or []}
    mini_checks = {
        "owner_home": "owner-home-share-cards" in mini_capture_names,
        "owner_card_list": "owner-card-list" in mini_capture_names,
        "owner_card_editor": "owner-card-editor-general" in mini_capture_names,
        "owner_share_mini_program": "owner-share-action-mini-program" in mini_capture_names,
        "owner_share_poster": "owner-share-action-poster" in mini_capture_names,
        "viewer_reentry_mini_program": "viewer-shared-reentry-mini-program" in mini_capture_names,
        "viewer_reentry_poster": "viewer-shared-reentry-poster" in mini_capture_names,
        "owner_mine": "owner-mine" in mini_capture_names,
        "viewer_public_card_detail": "viewer-public-card-detail" in mini_capture_names,
        "viewer_history": "viewer-history" in mini_capture_names,
        "share_payload_captured": bool(
            (mini_capture_names.get("owner-share-action-mini-program") or {}).get("sharePayload")
        ) and bool((mini_capture_names.get("owner-share-action-poster") or {}).get("sharePayload")),
        "reentry_query_captured": bool(
            ((mini_capture_names.get("viewer-shared-reentry-mini-program") or {}).get("actualQuery") or {}).get("shared")
        ) and bool(
            ((mini_capture_names.get("viewer-shared-reentry-poster") or {}).get("actualQuery") or {}).get("shared")
        ),
        "blocker_sample_recorded": bool(mini_blocker_summary and mini_blocker_summary.get("blockerPackagePresent")),
        "blocker_is_devtools_auth_gate": bool(mini_blocker_summary and mini_blocker_summary.get("devtoolsAuthGate")),
        "blocker_port_no_listener": bool(mini_blocker_summary and mini_blocker_summary.get("portNoListener")),
    }

    admin_capture_names = {item.get("name"): item for item in admin_manifest.get("captures") or []}
    admin_checks = {
        "contact_requests": "admin-share-card-contact-requests" in admin_capture_names,
        "repair_legacy_action": bool(
            (admin_capture_names.get("admin-share-card-share-cards") or {}).get("actionScreenshotPath")
        ),
        "share_cards": "admin-share-card-share-cards" in admin_capture_names,
        "default_general_card": "admin-share-card-default-general-card" in admin_capture_names,
    }

    backend_structured = ((release_summaries.get("backend") or {}).get("structuredSmoke") or {})
    admin_structured = ((release_summaries.get("admin") or {}).get("structuredSmoke") or {})
    schema_structured = ((release_summaries.get("schema") or {}).get("structuredSmoke") or {})
    release_records_all_pass = all(
        structured.get("overallVerdict") == "pass"
        for structured in (backend_structured, admin_structured, schema_structured)
        if structured
    )

    blockers = api_summary.get("blockers") or []
    blocker_checks = {
        "no_new_4xx_5xx": all(
            verdict not in {"mismatch", "missing"}
            for verdict in [
                backend_structured.get("apiDocsVerdict"),
                backend_structured.get("adminLoginVerdict"),
                backend_structured.get("adminRecruitRolesVerdict"),
                backend_structured.get("actorRoleSearchVerdict"),
                admin_structured.get("apiDocsVerdict"),
                admin_structured.get("adminLoginVerdict"),
                admin_structured.get("publicHomeVerdict"),
                admin_structured.get("staticAssetVerdict"),
            ]
            if verdict is not None
        ),
        "no_new_permission_gap": (
            api_checks["admin_share_cards_list"]
            and api_checks["admin_share_card_detail"]
            and admin_checks["contact_requests"]
            and admin_checks["share_cards"]
            and admin_structured.get("overallVerdict") == "pass"
        ),
        "no_new_schema_gap": schema_structured.get("overallVerdict") == "pass",
        "release_records_all_pass": release_records_all_pass,
        "send_code_dev_mode_recorded": any("`sendCode`" in str(item) for item in blockers),
        "mini_program_blocker_recorded": bool(mini_blocker_summary and mini_blocker_summary.get("blockerPackagePresent")),
    }

    return {
        "api": api_checks,
        "mini_program": mini_checks,
        "admin": admin_checks,
        "blocker_judgment": blocker_checks,
    }


def build_final_judgment(checks: dict, known_blockers: list[dict]) -> dict:
    blocker_judgment = checks["blocker_judgment"]
    new_blocking_issues: list[dict] = []
    issue_sources = {
        "releaseRecordIssues": [],
        "apiChainIssues": [],
        "uiEvidenceIssues": [],
        "knownIssues": [],
    }

    def append_new_issue(key: str, message: str, source: str) -> None:
        issue = {
            "key": key,
            "message": message,
            "reason": message,
            "source": source,
            "severity": "high",
            "relatedChecks": [key],
        }
        new_blocking_issues.append(issue)
        issue_sources[source].append(issue)

    if not blocker_judgment.get("no_new_4xx_5xx", False):
        append_new_issue("no_new_4xx_5xx", "当前出现新的 4xx / 5xx 主链接口错误", "apiChainIssues")
    if not blocker_judgment.get("no_new_permission_gap", False):
        append_new_issue("no_new_permission_gap", "当前出现新的权限缺失", "apiChainIssues")
    if not blocker_judgment.get("no_new_schema_gap", False):
        append_new_issue("no_new_schema_gap", "当前出现新的 schema 缺列 / 漏迁移", "releaseRecordIssues")
    if not blocker_judgment.get("release_records_all_pass", False):
        append_new_issue(
            "release_records_all_pass",
            "backend / admin / schema 发布记录总判定未全部通过",
            "releaseRecordIssues",
        )

    known_issue_related_checks = {
        "send_code_dev_mode": ["send_code_dev_mode_recorded"],
        "mini_program_devtools_auth_gate": ["mini_program_blocker_recorded"],
    }

    known_blocking_issues = [
        {
            "key": item.get("key", ""),
            "message": item.get("message", ""),
            "reason": item.get("message", ""),
            "source": "knownIssues",
            "severity": "medium",
            "relatedChecks": known_issue_related_checks.get(item.get("key", ""), ["known_issue_recorded"]),
        }
        for item in known_blockers
    ]
    issue_sources["knownIssues"] = known_blocking_issues.copy()

    blocking_issue_matrix = [
        {
            "key": item["key"],
            "reason": item["reason"],
            "source": item["source"],
            "severity": item["severity"],
            "relatedChecks": item["relatedChecks"],
            "isKnown": False,
        }
        for item in new_blocking_issues
    ] + [
        {
            "key": item["key"],
            "reason": item["reason"],
            "source": item["source"],
            "severity": item["severity"],
            "relatedChecks": item["relatedChecks"],
            "isKnown": True,
        }
        for item in known_blocking_issues
    ]

    if new_blocking_issues:
        final_judgment = "failed"
        final_judgment_reason = "存在新的发布后阻塞项：" + "；".join(
            item["message"] for item in new_blocking_issues
        )
    elif known_blocking_issues:
        final_judgment = "pass_with_known_blocker"
        final_judgment_reason = "发布后主链与发布记录检查通过，但仍保留已知阻塞：" + "；".join(
            item["message"] for item in known_blocking_issues
        )
    else:
        final_judgment = "pass"
        final_judgment_reason = "发布后主链与发布记录检查通过，当前未发现阻塞项"

    return {
        "finalJudgment": final_judgment,
        "finalJudgmentReason": final_judgment_reason,
        "newBlockingIssues": new_blocking_issues,
        "newBlockingIssueKeys": [item["key"] for item in new_blocking_issues],
        "newBlockingIssueReasons": [item["reason"] for item in new_blocking_issues],
        "knownBlockingIssues": known_blocking_issues,
        "knownBlockingIssueKeys": [item["key"] for item in known_blocking_issues],
        "knownBlockingIssueReasons": [item["reason"] for item in known_blocking_issues],
        "blockingIssueSources": issue_sources,
        "blockingIssueMatrix": blocking_issue_matrix,
    }


def build_blocking_issue_summary(blocking_issue_matrix: list[dict]) -> dict:
    severity_rank = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }
    source_counts = {
        "releaseRecordIssues": 0,
        "apiChainIssues": 0,
        "uiEvidenceIssues": 0,
        "knownIssues": 0,
    }
    total_count = len(blocking_issue_matrix)
    new_count = 0
    known_count = 0
    highest_severity = ""
    highest_rank = 0

    for item in blocking_issue_matrix:
        source = str(item.get("source") or "")
        if source in source_counts:
            source_counts[source] += 1
        if item.get("isKnown"):
            known_count += 1
        else:
            new_count += 1

        severity = str(item.get("severity") or "")
        rank = severity_rank.get(severity, 0)
        if rank > highest_rank:
            highest_rank = rank
            highest_severity = severity

    return {
        "totalCount": total_count,
        "newCount": new_count,
        "knownCount": known_count,
        "highestSeverity": highest_severity or "--",
        "sourceCounts": source_counts,
        "hasNewIssues": new_count > 0,
        "hasKnownIssues": known_count > 0,
    }


def build_blocking_issue_action_plan(blocking_issue_matrix: list[dict]) -> list[dict]:
    action_map = {
        "send_code_dev_mode": {
            "owner": "login-auth / sms-capability",
            "suggestedNextAction": "转入 00-51 formal sms 批次，完成真实短信能力验证样本。",
            "releaseImpact": "does_not_block_share_card_mainline",
            "priority": 40,
        },
        "mini_program_devtools_auth_gate": {
            "owner": "wechat-devtools / automation-auth",
            "suggestedNextAction": "切换或授权目标 appid 开发者账号后，重跑 run-share-card-mini-program-page-evidence.py。",
            "releaseImpact": "does_not_block_share_card_mainline",
            "priority": 30,
        },
        "no_new_4xx_5xx": {
            "owner": "backend / api-governance",
            "suggestedNextAction": "定位异常接口并重跑 API 治理样本，确认主链接口恢复。",
            "releaseImpact": "blocks_release",
            "priority": 10,
        },
        "no_new_permission_gap": {
            "owner": "admin / rbac",
            "suggestedNextAction": "补齐权限配置并重新验证后台页面与接口访问链路。",
            "releaseImpact": "blocks_release",
            "priority": 10,
        },
        "no_new_schema_gap": {
            "owner": "backend / schema",
            "suggestedNextAction": "补齐 migration 后重新执行 schema 发布与 backend 发布校验。",
            "releaseImpact": "blocks_release",
            "priority": 10,
        },
        "release_records_all_pass": {
            "owner": "release-governance",
            "suggestedNextAction": "检查 failedKeys / missingKeys 并重跑对应发布记录校验。",
            "releaseImpact": "blocks_release",
            "priority": 10,
        },
    }

    plan: list[dict] = []
    for item in blocking_issue_matrix:
        mapped = action_map.get(
            str(item.get("key") or ""),
            {
                "owner": "share-card-governance",
                "suggestedNextAction": "根据阻塞项原因补齐证据或修复后重新跑 checklist 自动留档。",
                "releaseImpact": "needs_manual_review",
            },
        )
        plan.append(
            {
                "key": item.get("key"),
                "reason": item.get("reason"),
                "source": item.get("source"),
                "severity": item.get("severity"),
                "isKnown": item.get("isKnown"),
                "priority": mapped["priority"],
                "owner": mapped["owner"],
                "suggestedNextAction": mapped["suggestedNextAction"],
                "releaseImpact": mapped["releaseImpact"],
                "relatedChecks": item.get("relatedChecks") or [],
            }
        )
    return plan


def select_primary_issue(blocking_issue_action_plan: list[dict]) -> dict:
    if not blocking_issue_action_plan:
        return {}

    release_impact_rank = {
        "blocks_release": 0,
        "needs_manual_review": 1,
        "does_not_block_share_card_mainline": 2,
    }
    severity_rank = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    return min(
        blocking_issue_action_plan,
        key=lambda item: (
            release_impact_rank.get(str(item.get("releaseImpact") or ""), 9),
            int(item.get("priority") or 999),
            severity_rank.get(str(item.get("severity") or ""), 9),
            1 if item.get("isKnown") else 0,
        ),
    )


def build_release_decision_card(
    *,
    final_judgment: dict,
    blocking_issue_summary: dict,
    blocking_issue_action_plan: list[dict],
) -> dict:
    primary_issue = select_primary_issue(blocking_issue_action_plan)
    has_blocks_release = any(
        item.get("releaseImpact") == "blocks_release"
        for item in blocking_issue_action_plan
    )
    releasable = not has_blocks_release
    if final_judgment.get("finalJudgment") == "failed":
        releasable = False

    return {
        "finalJudgment": final_judgment.get("finalJudgment"),
        "releasable": releasable,
        "mainlineReleaseBlocked": has_blocks_release,
        "primaryIssueKey": primary_issue.get("key") or "--",
        "topRisk": primary_issue.get("reason") or "当前未识别到阻塞项",
        "primaryOwner": primary_issue.get("owner") or "--",
        "nextAction": primary_issue.get("suggestedNextAction") or "继续按标准 checklist 回归即可",
        "releaseImpact": primary_issue.get("releaseImpact") or "none",
        "knownIssueCount": blocking_issue_summary.get("knownCount", 0),
        "newIssueCount": blocking_issue_summary.get("newCount", 0),
    }


def build_blocking_issue_dashboard(
    *,
    blocking_issue_summary: dict,
    blocking_issue_action_plan: list[dict],
    final_judgment: dict,
) -> dict:
    primary_issue = select_primary_issue(blocking_issue_action_plan)
    primary_owner = str(primary_issue.get("owner") or "")
    remaining_owners = sorted(
        {
            str(item.get("owner"))
            for item in blocking_issue_action_plan
            if item.get("owner") and str(item.get("owner")) != primary_owner
        }
    )
    owners = ([primary_owner] if primary_owner else []) + remaining_owners
    return {
        "finalJudgment": final_judgment.get("finalJudgment"),
        "highestSeverity": blocking_issue_summary.get("highestSeverity"),
        "totalCount": blocking_issue_summary.get("totalCount", 0),
        "newCount": blocking_issue_summary.get("newCount", 0),
        "knownCount": blocking_issue_summary.get("knownCount", 0),
        "sourceCounts": blocking_issue_summary.get("sourceCounts") or {},
        "primaryIssueKey": primary_issue.get("key") or "--",
        "topRisk": primary_issue.get("reason") or "当前未识别到阻塞项",
        "primaryOwner": primary_owner or "--",
        "nextAction": primary_issue.get("suggestedNextAction") or "继续按标准 checklist 回归即可",
        "owners": owners,
        "releaseBlocked": any(
            item.get("releaseImpact") == "blocks_release"
            for item in blocking_issue_action_plan
        ),
    }


def build_notes_focus_line(release_decision_card: dict, known_blocking_issue_keys: list[str]) -> str:
    primary_issue_key = str(release_decision_card.get("primaryIssueKey") or "")
    known_issue_order = [key for key in known_blocking_issue_keys if key != primary_issue_key]

    if primary_issue_key == "mini_program_devtools_auth_gate":
        if "send_code_dev_mode" in known_issue_order:
            return "当前最重要的未完成项已收口为：DevTools 开发者授权恢复后的 page evidence 复跑，其次是正式短信能力验证样本。"
        return "当前最重要的未完成项已收口为：DevTools 开发者授权恢复后的 page evidence 复跑。"

    if primary_issue_key == "send_code_dev_mode":
        if "mini_program_devtools_auth_gate" in known_issue_order:
            return "当前最重要的未完成项已收口为：正式短信能力验证样本，其次是 DevTools 开发者授权恢复后的 page evidence 复跑。"
        return "当前最重要的未完成项已收口为：正式短信能力验证样本。"

    return "当前最重要的未完成项已收口为：继续按当前主风险处理顺序完成剩余 blocker。"


def build_release_go_no_go_card(
    *,
    release_decision_card: dict,
    final_judgment: dict,
    blocking_issue_action_plan: list[dict],
) -> dict:
    releasable = bool(release_decision_card.get("releasable"))
    mainline_release_blocked = bool(release_decision_card.get("mainlineReleaseBlocked"))
    if not releasable:
        decision = "NO_GO"
    elif final_judgment.get("finalJudgment") == "pass_with_known_blocker":
        decision = "GO_WITH_KNOWN_BLOCKER"
    else:
        decision = "GO"

    primary_issue = select_primary_issue(blocking_issue_action_plan)
    primary_issue_key = str(primary_issue.get("key") or "")
    needs_batch_switch = primary_issue_key == "send_code_dev_mode"
    return {
        "decision": decision,
        "releasable": releasable,
        "mainlineReleaseBlocked": mainline_release_blocked,
        "primaryIssueKey": primary_issue_key or "--",
        "needsBatchSwitch": needs_batch_switch,
        "requiresRerunRelease": not releasable,
        "owner": release_decision_card.get("primaryOwner") or "--",
        "nextAction": release_decision_card.get("nextAction") or "--",
        "reason": final_judgment.get("finalJudgmentReason") or "--",
    }


def build_operator_run_card(
    *,
    release_go_no_go_card: dict,
    blocking_issue_action_plan: list[dict],
) -> dict:
    decision = str(release_go_no_go_card.get("decision") or "")
    if decision == "NO_GO":
        mode = "stop_and_fix"
        immediate_steps = [
            "停止继续发布，先处理阻塞项。",
            "按 blockingIssueActionPlan 修复后重跑 checklist 自动留档。",
        ]
    elif decision == "GO_WITH_KNOWN_BLOCKER":
        mode = "release_mainline_and_split_followup"
        immediate_steps = [
            "允许 share-card 主线继续按当前版本发布。",
            "将已知阻塞转入后续批次跟踪处理。",
        ]
    else:
        mode = "release_and_archive"
        immediate_steps = [
            "允许继续发布并归档本轮 checklist 结果。",
            "后续仅保留例行回归抽检。",
        ]

    primary_issue = select_primary_issue(blocking_issue_action_plan)
    primary_issue_key = str(primary_issue.get("key") or "")

    followup_batch_map = {
        "send_code_dev_mode": "00-51 formal sms",
        "mini_program_devtools_auth_gate": "wechat-devtools authorization",
    }
    followup_batch = followup_batch_map.get(primary_issue_key, "")
    if any(item.get("key") == "mini_program_devtools_auth_gate" for item in blocking_issue_action_plan):
        immediate_steps.append("恢复 DevTools 开发者授权后，重跑 share-card mini-program page evidence。")

    return {
        "mode": mode,
        "owner": release_go_no_go_card.get("owner") or "--",
        "decision": decision,
        "primaryIssueKey": primary_issue_key or "--",
        "followupBatch": followup_batch,
        "immediateSteps": immediate_steps,
        "rerunRequired": bool(release_go_no_go_card.get("requiresRerunRelease")),
    }


def build_summary_lines(payload: dict) -> list[str]:
    blockers = payload["knownBlockers"]
    checks = payload["checks"]
    blocker_summary = payload.get("miniProgramBlockerSummary") or {}
    blocker_preflight_summary = blocker_summary.get("preflightProbeSummaryPath") or ""
    blocker_preflight_result = blocker_summary.get("preflightProbeResultPath") or ""
    return [
        f"# Share Card Release Post Checklist Record {payload['sampleId']}",
        "",
        f"- Generated At: `{payload['generatedAt']}`",
        f"- Environment: `{payload['environment']}`",
        f"- Checklist Source: `{payload['checklistSource']}`",
        f"- API Sample: `{payload['apiSample']}`",
        f"- Mini Program Sample: `{payload['miniProgramSample']}`",
        f"- Mini Program Blocker Sample: `{payload['miniProgramBlockerSample'] or '--'}`",
        f"- Mini Program Blocker Sample Selection: `{payload['miniProgramBlockerSampleSelectionMode']}`",
        f"- Mini Program Blocker Sample Selection Display: `{payload['miniProgramBlockerSampleSelectionDisplay']}`",
        f"- Mini Program Blocker Selection Note: {payload['miniProgramBlockerSampleSelectionNote']}",
        *(
            [f"- Mini Program Blocker Preflight Summary: `{blocker_preflight_summary}`"]
            if blocker_preflight_summary
            else []
        ),
        *(
            [f"- Mini Program Blocker Preflight Result: `{blocker_preflight_result}`"]
            if blocker_preflight_result
            else []
        ),
        f"- Admin Sample: `{payload['adminSample']}`",
        f"- Admin Sample Selection: `{payload['adminSampleSelectionMode']}`",
        f"- Admin Sample Selection Display: `{payload['adminSampleSelectionDisplay']}`",
        f"- Admin Sample Selection Note: {payload['adminSampleSelectionNote']}",
        f"- SMS Bridge Sample: `{payload['smsBridgeSample']}`",
        f"- Backend Release Record: `{payload['backendReleaseRecord'] or '--'}`",
        f"- Admin Release Record: `{payload['adminReleaseRecord'] or '--'}`",
        f"- Schema Release Record: `{payload['schemaReleaseRecord'] or '--'}`",
        "",
        "## Result",
        "",
        f"- Overall: `{payload['overallDisplay']}`",
        f"- Final Judgment: `{payload['finalJudgment']}`",
        f"- Final Judgment Reason: `{payload['finalJudgmentReason']}`",
        f"- New Blocking Issue Keys: `{payload['newBlockingIssueKeys']}`",
        f"- Known Blocking Issue Keys: `{payload['knownBlockingIssueKeys']}`",
        "- New Blocking Issues:",
        *(
            [f"  - `{item['message']}`" for item in payload["newBlockingIssues"]]
            if payload["newBlockingIssues"]
            else ["  - `--`"]
        ),
        "- Known Blocker:",
        *[f"  - `{item['message']}`" for item in blockers],
        "- Blocking Issue Sources:",
        f"  - releaseRecordIssues: `{payload['blockingIssueSources']['releaseRecordIssues']}`",
        f"  - apiChainIssues: `{payload['blockingIssueSources']['apiChainIssues']}`",
        f"  - uiEvidenceIssues: `{payload['blockingIssueSources']['uiEvidenceIssues']}`",
        f"  - knownIssues: `{payload['blockingIssueSources']['knownIssues']}`",
        "- Blocking Issue Matrix:",
        *(
            [
                "  - "
                + f"`key={item['key']}` / "
                + f"`source={item['source']}` / "
                + f"`severity={item['severity']}` / "
                + f"`isKnown={item['isKnown']}` / "
                + f"`relatedChecks={item['relatedChecks']}` / "
                + f"`reason={item['reason']}`"
                for item in payload["blockingIssueMatrix"]
            ]
            if payload["blockingIssueMatrix"]
            else ["  - `--`"]
        ),
        "- Blocking Issue Summary:",
        f"  - totalCount: `{payload['blockingIssueSummary']['totalCount']}`",
        f"  - newCount: `{payload['blockingIssueSummary']['newCount']}`",
        f"  - knownCount: `{payload['blockingIssueSummary']['knownCount']}`",
        f"  - highestSeverity: `{payload['blockingIssueSummary']['highestSeverity']}`",
        f"  - sourceCounts: `{payload['blockingIssueSummary']['sourceCounts']}`",
        "- Blocking Issue Action Plan:",
        *(
            [
                "  - "
                + f"`key={item['key']}` / "
                + f"`owner={item['owner']}` / "
                + f"`releaseImpact={item['releaseImpact']}` / "
                + f"`suggestedNextAction={item['suggestedNextAction']}`"
                for item in payload["blockingIssueActionPlan"]
            ]
            if payload["blockingIssueActionPlan"]
            else ["  - `--`"]
        ),
        "- Release Decision Card:",
        f"  - finalJudgment: `{payload['releaseDecisionCard']['finalJudgment']}`",
        f"  - releasable: `{payload['releaseDecisionCard']['releasable']}`",
        f"  - mainlineReleaseBlocked: `{payload['releaseDecisionCard']['mainlineReleaseBlocked']}`",
        f"  - primaryIssueKey: `{payload['releaseDecisionCard']['primaryIssueKey']}`",
        f"  - topRisk: `{payload['releaseDecisionCard']['topRisk']}`",
        f"  - primaryOwner: `{payload['releaseDecisionCard']['primaryOwner']}`",
        f"  - nextAction: `{payload['releaseDecisionCard']['nextAction']}`",
        f"  - releaseImpact: `{payload['releaseDecisionCard']['releaseImpact']}`",
        "- Blocking Issue Dashboard:",
        f"  - finalJudgment: `{payload['blockingIssueDashboard']['finalJudgment']}`",
        f"  - highestSeverity: `{payload['blockingIssueDashboard']['highestSeverity']}`",
        f"  - totalCount: `{payload['blockingIssueDashboard']['totalCount']}`",
        f"  - newCount: `{payload['blockingIssueDashboard']['newCount']}`",
        f"  - knownCount: `{payload['blockingIssueDashboard']['knownCount']}`",
        f"  - sourceCounts: `{payload['blockingIssueDashboard']['sourceCounts']}`",
        f"  - primaryIssueKey: `{payload['blockingIssueDashboard']['primaryIssueKey']}`",
        f"  - topRisk: `{payload['blockingIssueDashboard']['topRisk']}`",
        f"  - primaryOwner: `{payload['blockingIssueDashboard']['primaryOwner']}`",
        f"  - nextAction: `{payload['blockingIssueDashboard']['nextAction']}`",
        f"  - owners: `{payload['blockingIssueDashboard']['owners']}`",
        f"  - releaseBlocked: `{payload['blockingIssueDashboard']['releaseBlocked']}`",
        "- Release Go/No-Go Card:",
        f"  - decision: `{payload['releaseGoNoGoCard']['decision']}`",
        f"  - releasable: `{payload['releaseGoNoGoCard']['releasable']}`",
        f"  - mainlineReleaseBlocked: `{payload['releaseGoNoGoCard']['mainlineReleaseBlocked']}`",
        f"  - primaryIssueKey: `{payload['releaseGoNoGoCard']['primaryIssueKey']}`",
        f"  - needsBatchSwitch: `{payload['releaseGoNoGoCard']['needsBatchSwitch']}`",
        f"  - requiresRerunRelease: `{payload['releaseGoNoGoCard']['requiresRerunRelease']}`",
        f"  - owner: `{payload['releaseGoNoGoCard']['owner']}`",
        f"  - nextAction: `{payload['releaseGoNoGoCard']['nextAction']}`",
        "- Operator Run Card:",
        f"  - mode: `{payload['operatorRunCard']['mode']}`",
        f"  - owner: `{payload['operatorRunCard']['owner']}`",
        f"  - decision: `{payload['operatorRunCard']['decision']}`",
        f"  - primaryIssueKey: `{payload['operatorRunCard']['primaryIssueKey']}`",
        f"  - followupBatch: `{payload['operatorRunCard']['followupBatch'] or '--'}`",
        f"  - rerunRequired: `{payload['operatorRunCard']['rerunRequired']}`",
        *[
            f"  - immediateStep: `{item}`"
            for item in payload["operatorRunCard"]["immediateSteps"]
        ],
        "",
        "## API / Governance",
        "",
        f"- [{'x' if checks['api']['my_cards_general'] else ' '}] `/card/my-cards` 可返回默认 `general` 卡",
        f"- [{'x' if checks['api']['personalization_by_share_card_id'] else ' '}] `/card/personalization` 可按 `shareCardId` 正常返回",
        f"- [{'x' if checks['api']['view_histories_roundtrip'] else ' '}] `/card/view-histories` 可写入并回读",
        f"- [{'x' if checks['api']['contact_request_pending_to_approved'] else ' '}] 联系方式申请链 `pending -> approved` 正常",
        f"- [{'x' if checks['api']['admin_share_cards_list'] else ' '}] `/admin/content/share-cards` 列表正常",
        f"- [{'x' if checks['api']['admin_share_card_detail'] else ' '}] `/admin/content/share-cards/{{shareCardId}}` 详情正常",
        f"- [{'x' if checks['api']['admin_legacy_summary'] else ' '}] `/admin/content/share-cards/legacy-summary` 正常",
        f"- [{'x' if checks['api']['legacy_pending_zero'] else ' '}] `legacy-summary.totalPendingCount=0`",
        f"- [{'x' if checks['api']['binding_consistent'] else ' '}] `bindingConsistent=true`",
        "",
        "## Mini Program",
        "",
        f"- [{'x' if checks['mini_program']['owner_home'] else ' '}] owner 首页截图正常",
        f"- [{'x' if checks['mini_program']['owner_card_list'] else ' '}] owner 我的名片截图正常",
        f"- [{'x' if checks['mini_program']['owner_card_editor'] else ' '}] owner 卡片编辑截图正常",
        f"- [{'x' if checks['mini_program']['owner_share_mini_program'] else ' '}] owner 小程序卡片分享终态截图正常",
        f"- [{'x' if checks['mini_program']['owner_share_poster'] else ' '}] owner 分享海报终态截图正常",
        f"- [{'x' if checks['mini_program']['viewer_reentry_mini_program'] else ' '}] viewer 从分享 path 再次进入小程序卡片页正常",
        f"- [{'x' if checks['mini_program']['viewer_reentry_poster'] else ' '}] viewer 从分享 path 再次进入分享海报页正常",
        f"- [{'x' if checks['mini_program']['owner_mine'] else ' '}] owner 个人中心截图正常",
        f"- [{'x' if checks['mini_program']['viewer_public_card_detail'] else ' '}] viewer 公开名片截图正常",
        f"- [{'x' if checks['mini_program']['viewer_history'] else ' '}] viewer 查看历史截图正常",
        f"- [{'x' if checks['mini_program']['share_payload_captured'] else ' '}] 小程序卡片 / 海报终态 page-data 已记录 `onShareAppMessage / onShareTimeline`",
        f"- [{'x' if checks['mini_program']['reentry_query_captured'] else ' '}] viewer 回流再次进入 page-data 已记录 `shared=1 / shareCardId / artifact`",
        f"- [{'x' if checks['mini_program']['blocker_sample_recorded'] else ' '}] 若 page evidence 阻塞，标准 blocker 包已留档",
        f"- [{'x' if checks['mini_program']['blocker_is_devtools_auth_gate'] else ' '}] 当前 blocker 已明确定位为 DevTools 开发者授权缺失",
        f"- [{'x' if checks['mini_program']['blocker_port_no_listener'] else ' '}] `9421` automation endpoint 未监听已留档",
        "",
        "## Admin",
        "",
        f"- [{'x' if checks['admin']['contact_requests'] else ' '}] 联系方式申请列表 / 详情截图正常",
        f"- [{'x' if checks['admin']['repair_legacy_action'] else ' '}] 分享卡治理 `repair-legacy` 动作截图正常",
        f"- [{'x' if checks['admin']['share_cards'] else ' '}] 分享卡治理列表 / 详情截图正常",
        f"- [{'x' if checks['admin']['default_general_card'] else ' '}] 默认普通卡治理页截图正常",
        "",
        "## Blocker Judgment",
        "",
        f"- [{'x' if checks['blocker_judgment']['no_new_4xx_5xx'] else ' '}] 当前没有新的 4xx / 5xx 主链接口错误",
        f"- [{'x' if checks['blocker_judgment']['no_new_permission_gap'] else ' '}] 当前没有新的权限缺失",
        f"- [{'x' if checks['blocker_judgment']['no_new_schema_gap'] else ' '}] 当前没有新的 schema 缺列 / 漏迁移",
        f"- [{'x' if checks['blocker_judgment']['release_records_all_pass'] else ' '}] backend / admin / schema 发布记录总判定均为 `pass`",
        f"- [{'x' if checks['blocker_judgment']['mini_program_blocker_recorded'] else ' '}] 小程序 page evidence blocker 样本已进入标准读法",
        f"- [{'x' if checks['blocker_judgment']['send_code_dev_mode_recorded'] else ' '}] 已明确记录 `sendCode` 仍是开发态验证码，不能宣告正式短信闭环",
        "",
        "## Notes",
        "",
        "- 本次记录由标准脚本根据当前最新三类基线样本自动生成，不再手工整理清单结果。",
        "- " + build_notes_focus_line(payload["releaseDecisionCard"], payload["knownBlockingIssueKeys"]),
        "",
        "## Linked Release Summaries",
        "",
        *(
            [
                f"- Backend: `scope={payload['releaseSummaries']['backend']['scope']}` / `releasedAt={payload['releaseSummaries']['backend']['releasedAt']}` / `conclusion={payload['releaseSummaries']['backend']['conclusion']}`",
                f"  - overallVerdict: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('overallVerdict')}`",
                f"  - failedKeys: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('failedKeys')}`",
                f"  - missingKeys: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('missingKeys')}`",
                f"  - backendContainerStatusLine: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('backendContainerStatusLine') or '--'}`",
                f"  - apiDocsStatusLine: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('apiDocsStatusLine') or '--'}`",
                f"  - adminLoginStatusLine: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('adminLoginStatusLine') or '--'}`",
                f"  - adminRecruitRolesStatusLine: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('adminRecruitRolesStatusLine') or '--'}`",
                f"  - actorRoleSearchStatusLine: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('actorRoleSearchStatusLine') or '--'}`",
                f"  - backendContainerUp: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('backendContainerUp')}`",
                f"  - apiDocsStatusCode: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('apiDocsStatusCode')}`",
                f"  - apiDocsExpectedStatusCode: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('apiDocsExpectedStatusCode')}`",
                f"  - apiDocsMatchesExpected: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('apiDocsMatchesExpected')}`",
                f"  - apiDocsVerdict: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('apiDocsVerdict')}`",
                f"  - adminLoginStatusCode: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('adminLoginStatusCode')}`",
                f"  - adminLoginExpectedStatusCode: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('adminLoginExpectedStatusCode')}`",
                f"  - adminLoginMatchesExpected: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('adminLoginMatchesExpected')}`",
                f"  - adminLoginVerdict: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('adminLoginVerdict')}`",
                f"  - adminRecruitRolesStatusCode: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('adminRecruitRolesStatusCode')}`",
                f"  - adminRecruitRolesExpectedStatusCode: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('adminRecruitRolesExpectedStatusCode')}`",
                f"  - adminRecruitRolesMatchesExpected: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('adminRecruitRolesMatchesExpected')}`",
                f"  - adminRecruitRolesVerdict: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('adminRecruitRolesVerdict')}`",
                f"  - actorRoleSearchStatusCode: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('actorRoleSearchStatusCode')}`",
                f"  - actorRoleSearchExpectedStatusCode: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('actorRoleSearchExpectedStatusCode')}`",
                f"  - actorRoleSearchMatchesExpected: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('actorRoleSearchMatchesExpected')}`",
                f"  - actorRoleSearchVerdict: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('actorRoleSearchVerdict')}`",
                f"  - adminLoginSuccess: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('adminLoginSuccess')}`",
                f"  - adminRecruitRolesUnauthorized: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('adminRecruitRolesUnauthorized')}`",
                f"  - actorRoleSearchUnauthorized: `{payload['releaseSummaries']['backend'].get('structuredSmoke', {}).get('actorRoleSearchUnauthorized')}`",
                *[
                    f"  - {item}"
                    for item in payload["releaseSummaries"]["backend"]["smoke"][:4]
                ],
            ]
            if payload["releaseSummaries"].get("backend")
            else ["- Backend: `--`"]
        ),
        *(
            [
                f"- Admin: `scope={payload['releaseSummaries']['admin']['scope']}` / `releasedAt={payload['releaseSummaries']['admin']['releasedAt']}` / `conclusion={payload['releaseSummaries']['admin']['conclusion']}`",
                f"  - overallVerdict: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('overallVerdict')}`",
                f"  - failedKeys: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('failedKeys')}`",
                f"  - missingKeys: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('missingKeys')}`",
                f"  - apiDocsStatusLine: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('apiDocsStatusLine') or '--'}`",
                f"  - publicHomeStatusLine: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('publicHomeStatusLine') or '--'}`",
                f"  - staticAssetStatusLine: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('staticAssetStatusLine') or '--'}`",
                f"  - staticIndexHtmlPresent: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('staticIndexHtmlPresent')}`",
                f"  - apiDocsStatusCode: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('apiDocsStatusCode')}`",
                f"  - apiDocsExpectedStatusCode: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('apiDocsExpectedStatusCode')}`",
                f"  - apiDocsMatchesExpected: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('apiDocsMatchesExpected')}`",
                f"  - apiDocsVerdict: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('apiDocsVerdict')}`",
                f"  - adminLoginStatusCode: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('adminLoginStatusCode')}`",
                f"  - adminLoginExpectedStatusCode: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('adminLoginExpectedStatusCode')}`",
                f"  - adminLoginMatchesExpected: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('adminLoginMatchesExpected')}`",
                f"  - adminLoginVerdict: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('adminLoginVerdict')}`",
                f"  - publicHomeStatusCode: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('publicHomeStatusCode')}`",
                f"  - publicHomeExpectedStatusCode: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('publicHomeExpectedStatusCode')}`",
                f"  - publicHomeMatchesExpected: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('publicHomeMatchesExpected')}`",
                f"  - publicHomeVerdict: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('publicHomeVerdict')}`",
                f"  - staticAssetStatusCode: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('staticAssetStatusCode')}`",
                f"  - staticAssetExpectedStatusCode: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('staticAssetExpectedStatusCode')}`",
                f"  - staticAssetMatchesExpected: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('staticAssetMatchesExpected')}`",
                f"  - staticAssetVerdict: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('staticAssetVerdict')}`",
                f"  - publicHomeUp: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('publicHomeUp')}`",
                f"  - staticAssetUp: `{payload['releaseSummaries']['admin'].get('structuredSmoke', {}).get('staticAssetUp')}`",
                *[
                    f"  - {item}"
                    for item in payload["releaseSummaries"]["admin"]["smoke"][:4]
                ],
            ]
            if payload["releaseSummaries"].get("admin")
            else ["- Admin: `--`"]
        ),
        *(
            [
                f"- Schema: `scope={payload['releaseSummaries']['schema']['scope']}` / `releasedAt={payload['releaseSummaries']['schema']['releasedAt']}` / `conclusion={payload['releaseSummaries']['schema']['conclusion']}`",
                f"  - overallVerdict: `{payload['releaseSummaries']['schema'].get('structuredSmoke', {}).get('overallVerdict')}`",
                f"  - failedKeys: `{payload['releaseSummaries']['schema'].get('structuredSmoke', {}).get('failedKeys')}`",
                f"  - missingKeys: `{payload['releaseSummaries']['schema'].get('structuredSmoke', {}).get('missingKeys')}`",
                f"  - migrationFile: `{payload['releaseSummaries']['schema'].get('structuredSmoke', {}).get('schemaMigrationFile') or '--'}`",
                f"  - migrationStatus: `{payload['releaseSummaries']['schema'].get('structuredSmoke', {}).get('schemaMigrationStatus') or '--'}`",
                f"  - migrationApplied: `{payload['releaseSummaries']['schema'].get('structuredSmoke', {}).get('migrationApplied')}`",
                *[
                    f"  - {item}"
                    for item in payload["releaseSummaries"]["schema"]["smoke"][:4]
                ],
            ]
            if payload["releaseSummaries"].get("schema")
            else ["- Schema: `--`"]
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the share-card release post-checklist record from current baseline samples."
    )
    parser.add_argument("--label", default="share-card-release-post-checklist-record-auto")
    parser.add_argument("--environment", default="dev")
    parser.add_argument("--api-sample")
    parser.add_argument("--mini-sample")
    parser.add_argument("--mini-blocker-sample")
    parser.add_argument("--admin-sample")
    parser.add_argument("--sms-bridge-sample")
    parser.add_argument("--backend-release-record")
    parser.add_argument("--admin-release-record")
    parser.add_argument("--schema-release-record")
    args = parser.parse_args()

    api_sample_dir = resolve_sample(
        SAMPLES_ROOT,
        args.api_sample,
        "remote-governance-sample",
        "summary.json",
    )
    mini_sample_dir = resolve_sample(
        SAMPLES_ROOT,
        args.mini_sample,
        "share-card-mini-program-page-evidence",
        "summary.md",
    )
    mini_blocker_sample_dir, mini_blocker_sample_selection_mode = resolve_optional_sample_with_auto_preferred_files(
        SAMPLES_ROOT,
        args.mini_blocker_sample,
        "page-evidence",
        r"captures\devtools-auth-blocker.txt",
        ["page-evidence-result.json", r"captures\devtools-auth-blocker.txt"],
    )
    mini_blocker_sample_selection_note = build_optional_sample_selection_note(
        mini_blocker_sample_selection_mode,
        "page-evidence",
        "page-evidence-result.json",
    )
    mini_blocker_sample_selection_display = build_optional_sample_selection_display(
        mini_blocker_sample_selection_mode
    )
    admin_sample_dir, admin_sample_selection_mode = resolve_sample_with_auto_preferred_files_and_selection(
        SAMPLES_ROOT,
        args.admin_sample,
        "share-card-admin-page-evidence",
        "summary.md",
        ["admin-page-evidence-result.json", "summary.md"],
    )
    admin_sample_selection_note = build_required_sample_selection_note(
        admin_sample_selection_mode,
        "--admin-sample",
        "share-card-admin-page-evidence",
        "admin-page-evidence-result.json",
        "后台页面样本",
    )
    admin_sample_selection_display = build_required_sample_selection_display(
        admin_sample_selection_mode,
        "后台页面样本",
    )
    sms_bridge_sample_dir = resolve_sample(
        LOGIN_AUTH_SAMPLES_ROOT,
        args.sms_bridge_sample,
        "share-card-sms-bridge",
        "summary.md",
    )
    backend_release_record = resolve_release_record(
        args.backend_release_record,
        ["share-card", "backend-only"],
    )
    admin_release_record = resolve_release_record(
        args.admin_release_record,
        ["share-card", "admin-only"],
    )
    schema_release_record = resolve_release_record(
        args.schema_release_record,
        ["share-card", "backend-schema"],
    )
    release_summaries = {
        "backend": extract_release_summary(backend_release_record),
        "admin": extract_release_summary(admin_release_record),
        "schema": extract_release_summary(schema_release_record),
    }

    api_summary = read_json(api_sample_dir / "summary.json")
    mini_manifest = read_json(mini_sample_dir / "captures" / "mini-program-screenshot-capture.json")
    mini_blocker_summary = extract_mini_program_blocker_summary(mini_blocker_sample_dir)
    admin_manifest = read_json(admin_sample_dir / "captures" / "admin-share-card-screenshot-capture.json")
    admin_share_cards_page_data = read_json(
        admin_sample_dir / "captures" / "page-data-admin-share-card-share-cards.json"
    )
    sms_bridge_summary_text = (sms_bridge_sample_dir / "summary.md").read_text(encoding="utf-8")

    checks = build_checks(
        api_summary=api_summary,
        mini_manifest=mini_manifest,
        mini_blocker_summary=mini_blocker_summary,
        admin_manifest=admin_manifest,
        admin_share_cards_page_data=admin_share_cards_page_data,
        sms_bridge_summary_text=sms_bridge_summary_text,
        release_summaries=release_summaries,
    )

    now = datetime.now()
    sample_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{args.label}"
    sample_root = SAMPLES_ROOT / sample_id
    ensure_dir(sample_root)

    known_blockers = [
        {
            "key": "send_code_dev_mode",
            "message": "sendCode 仍是开发态验证码返回，不能据此宣告正式短信闭环",
        }
    ]
    if mini_blocker_summary and mini_blocker_summary.get("devtoolsAuthGate"):
        known_blockers.append(
            {
                "key": "mini_program_devtools_auth_gate",
                "message": "小程序 page evidence 当前受 DevTools 开发者授权阻塞，9421 automation endpoint 未恢复",
            }
        )
    known_blockers = sort_known_blockers(known_blockers)
    final_judgment = build_final_judgment(checks, known_blockers)
    blocking_issue_summary = build_blocking_issue_summary(final_judgment["blockingIssueMatrix"])
    blocking_issue_action_plan = build_blocking_issue_action_plan(final_judgment["blockingIssueMatrix"])
    release_decision_card = build_release_decision_card(
        final_judgment=final_judgment,
        blocking_issue_summary=blocking_issue_summary,
        blocking_issue_action_plan=blocking_issue_action_plan,
    )
    blocking_issue_dashboard = build_blocking_issue_dashboard(
        blocking_issue_summary=blocking_issue_summary,
        blocking_issue_action_plan=blocking_issue_action_plan,
        final_judgment=final_judgment,
    )
    release_go_no_go_card = build_release_go_no_go_card(
        release_decision_card=release_decision_card,
        final_judgment=final_judgment,
        blocking_issue_action_plan=blocking_issue_action_plan,
    )
    operator_run_card = build_operator_run_card(
        release_go_no_go_card=release_go_no_go_card,
        blocking_issue_action_plan=blocking_issue_action_plan,
    )
    overall = final_judgment["finalJudgment"]
    known_blocker_count = len(final_judgment["knownBlockingIssues"])
    overall_display = {
        "failed": "失败（存在新的发布后阻塞项）",
        "pass_with_known_blocker": f"通过（仍保留 {known_blocker_count} 个已知 blocker）",
        "pass": "通过（当前未发现阻塞项）",
    }.get(overall, overall)

    payload = {
        "sampleId": sample_id,
        "generatedAt": now.isoformat(timespec="seconds"),
        "environment": args.environment,
        "checklistSource": to_relpath(CHECKLIST_SOURCE, sample_root),
        "apiSample": to_relpath(api_sample_dir / "summary.md", sample_root),
        "miniProgramSample": to_relpath(mini_sample_dir / "summary.md", sample_root),
        "miniProgramBlockerSample": to_relpath(Path(mini_blocker_summary["summaryPath"]), sample_root) if mini_blocker_summary else "",
        "miniProgramBlockerSampleSelectionMode": mini_blocker_sample_selection_mode,
        "miniProgramBlockerSampleSelectionDisplay": mini_blocker_sample_selection_display,
        "miniProgramBlockerSampleSelectionNote": mini_blocker_sample_selection_note,
        "miniProgramBlockerPreflightSummary": (
            to_relpath(Path(mini_blocker_summary["preflightProbeSummaryPath"]), sample_root)
            if mini_blocker_summary and mini_blocker_summary.get("preflightProbeSummaryPath")
            else ""
        ),
        "miniProgramBlockerPreflightResult": (
            to_relpath(Path(mini_blocker_summary["preflightProbeResultPath"]), sample_root)
            if mini_blocker_summary and mini_blocker_summary.get("preflightProbeResultPath")
            else ""
        ),
        "adminSample": to_relpath(admin_sample_dir / "summary.md", sample_root),
        "adminSampleSelectionMode": admin_sample_selection_mode,
        "adminSampleSelectionDisplay": admin_sample_selection_display,
        "adminSampleSelectionNote": admin_sample_selection_note,
        "smsBridgeSample": to_relpath(sms_bridge_sample_dir / "summary.md", sample_root),
        "backendReleaseRecord": to_relpath(backend_release_record, sample_root) if backend_release_record else "",
        "adminReleaseRecord": to_relpath(admin_release_record, sample_root) if admin_release_record else "",
        "schemaReleaseRecord": to_relpath(schema_release_record, sample_root) if schema_release_record else "",
        "releaseSummaries": release_summaries,
        "miniProgramBlockerSummary": mini_blocker_summary,
        "overall": overall,
        "overallDisplay": overall_display,
        "knownBlockers": known_blockers,
        "finalJudgment": final_judgment["finalJudgment"],
        "finalJudgmentReason": final_judgment["finalJudgmentReason"],
        "newBlockingIssues": final_judgment["newBlockingIssues"],
        "newBlockingIssueKeys": final_judgment["newBlockingIssueKeys"],
        "newBlockingIssueReasons": final_judgment["newBlockingIssueReasons"],
        "knownBlockingIssues": final_judgment["knownBlockingIssues"],
        "knownBlockingIssueKeys": final_judgment["knownBlockingIssueKeys"],
        "knownBlockingIssueReasons": final_judgment["knownBlockingIssueReasons"],
        "blockingIssueSources": final_judgment["blockingIssueSources"],
        "blockingIssueMatrix": final_judgment["blockingIssueMatrix"],
        "blockingIssueSummary": blocking_issue_summary,
        "blockingIssueActionPlan": blocking_issue_action_plan,
        "releaseDecisionCard": release_decision_card,
        "blockingIssueDashboard": blocking_issue_dashboard,
        "releaseGoNoGoCard": release_go_no_go_card,
        "operatorRunCard": operator_run_card,
        "checks": checks,
    }

    (sample_root / "summary.md").write_text(
        "\n".join(build_summary_lines(payload)) + "\n",
        encoding="utf-8",
    )
    (sample_root / "checklist-result.json").write_text(
        json.dumps(
            {
                "generatedAt": payload["generatedAt"],
                "environment": payload["environment"],
                "checklistSource": payload["checklistSource"],
                "apiSample": payload["apiSample"],
                "miniProgramSample": payload["miniProgramSample"],
                "miniProgramBlockerSample": payload["miniProgramBlockerSample"],
                "miniProgramBlockerSampleSelectionMode": payload["miniProgramBlockerSampleSelectionMode"],
                "miniProgramBlockerSampleSelectionDisplay": payload["miniProgramBlockerSampleSelectionDisplay"],
                "miniProgramBlockerSampleSelectionNote": payload["miniProgramBlockerSampleSelectionNote"],
                "miniProgramBlockerPreflightSummary": payload["miniProgramBlockerPreflightSummary"],
                "miniProgramBlockerPreflightResult": payload["miniProgramBlockerPreflightResult"],
                "adminSample": payload["adminSample"],
                "adminSampleSelectionMode": payload["adminSampleSelectionMode"],
                "adminSampleSelectionDisplay": payload["adminSampleSelectionDisplay"],
                "adminSampleSelectionNote": payload["adminSampleSelectionNote"],
                "smsBridgeSample": payload["smsBridgeSample"],
                "backendReleaseRecord": payload["backendReleaseRecord"],
                "adminReleaseRecord": payload["adminReleaseRecord"],
                "schemaReleaseRecord": payload["schemaReleaseRecord"],
                "releaseSummaries": payload["releaseSummaries"],
                "miniProgramBlockerSummary": payload["miniProgramBlockerSummary"],
                "overall": payload["overall"],
                "overallDisplay": payload["overallDisplay"],
                "knownBlockers": payload["knownBlockers"],
                "finalJudgment": payload["finalJudgment"],
                "finalJudgmentReason": payload["finalJudgmentReason"],
                "newBlockingIssues": payload["newBlockingIssues"],
                "newBlockingIssueKeys": payload["newBlockingIssueKeys"],
                "newBlockingIssueReasons": payload["newBlockingIssueReasons"],
                "knownBlockingIssues": payload["knownBlockingIssues"],
                "knownBlockingIssueKeys": payload["knownBlockingIssueKeys"],
                "knownBlockingIssueReasons": payload["knownBlockingIssueReasons"],
                "blockingIssueSources": payload["blockingIssueSources"],
                "blockingIssueMatrix": payload["blockingIssueMatrix"],
                "blockingIssueSummary": payload["blockingIssueSummary"],
                "blockingIssueActionPlan": payload["blockingIssueActionPlan"],
                "releaseDecisionCard": payload["releaseDecisionCard"],
                "blockingIssueDashboard": payload["blockingIssueDashboard"],
                "releaseGoNoGoCard": payload["releaseGoNoGoCard"],
                "operatorRunCard": payload["operatorRunCard"],
                "checks": checks,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "sampleRoot": str(sample_root),
                "apiSample": api_sample_dir.name,
                "miniSample": mini_sample_dir.name,
                "miniBlockerSample": mini_blocker_sample_dir.name if mini_blocker_sample_dir else None,
                "miniBlockerSampleSelectionMode": mini_blocker_sample_selection_mode,
                "miniBlockerSampleSelectionDisplay": mini_blocker_sample_selection_display,
                "miniBlockerSampleSelectionNote": mini_blocker_sample_selection_note,
                "miniBlockerPreflightSummary": (
                    mini_blocker_summary.get("preflightProbeSummaryPath") if mini_blocker_summary else None
                ),
                "miniBlockerPreflightResult": (
                    mini_blocker_summary.get("preflightProbeResultPath") if mini_blocker_summary else None
                ),
                "adminSample": admin_sample_dir.name,
                "adminSampleSelectionMode": admin_sample_selection_mode,
                "adminSampleSelectionDisplay": admin_sample_selection_display,
                "adminSampleSelectionNote": admin_sample_selection_note,
                "smsBridgeSample": sms_bridge_sample_dir.name,
                "backendReleaseRecord": backend_release_record.name if backend_release_record else None,
                "adminReleaseRecord": admin_release_record.name if admin_release_record else None,
                "schemaReleaseRecord": schema_release_record.name if schema_release_record else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
