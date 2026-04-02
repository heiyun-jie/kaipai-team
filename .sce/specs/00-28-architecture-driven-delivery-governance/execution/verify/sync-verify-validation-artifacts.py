import argparse
import json
import re
from pathlib import Path
from typing import Any


VERIFY_STATUS_LABELS = {
    "0": "unsubmitted",
    "1": "pending",
    "2": "approved",
    "3": "rejected",
}

EXPECTED_HEADERS = [
    "schema_release_history_id\tscript\tchecksum\tapplied_mode\tapplied_by\trelease_id\tnotes\tcreated_at",
    "INDEX_NAME\tNON_UNIQUE\tSEQ_IN_INDEX\tCOLUMN_NAME",
    "user_id\tphone\tuser_name\treal_auth_status\tcreate_time\tlast_update",
    "actor_profile_id\tuser_id\treal_name\tis_certified\tcreate_time\tlast_update",
    "verification_id\tuser_id\treal_name\tid_card_no_cipher\tstatus\treject_reason\treviewer_id\treviewed_at\tsnapshot_profile_completion\tcreate_time\tlast_update",
    "verification_id\tuser_id\treal_name\tid_card_no_cipher\tstatus\treject_reason\treviewer_id\treviewed_at\tsnapshot_profile_completion\tcreate_time\tlast_update",
    "verification_id\tuser_id\treal_name\tid_card_no_cipher\tstatus\treject_reason\treviewer_id\treviewed_at\tsnapshot_profile_completion\tcreate_time\tlast_update",
    "owner_id\tid_card_hash\tuser_id\tcreate_time\tlast_update",
    "operation_log_id\tadmin_user_id\tadmin_user_name\tmodule_code\toperation_code\ttarget_type\ttarget_id\toperation_result\textra_context_json\tcreate_time",
]

SECTION_NAMES = [
    "schema_release_history",
    "identity_verification_index",
    "user",
    "actor_profile",
    "identity_verification_all",
    "identity_verification_first",
    "identity_verification_retry",
    "identity_verification_owner",
    "admin_operation_log",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return repair_value(json.loads(read_text(path)))


def repair_value(value: Any) -> Any:
    if isinstance(value, str):
        return repair_text(value)
    if isinstance(value, list):
        return [repair_value(item) for item in value]
    if isinstance(value, dict):
        return {key: repair_value(item) for key, item in value.items()}
    return value


def repair_text(value: str) -> str:
    if not value:
        return value
    if any("\u4e00" <= char <= "\u9fff" for char in value):
        return value
    suspicious = sum(
        1
        for char in value
        if ord(char) >= 128 or char in {"\x81", "\x8d", "\x8f", "\x90", "\x9d"}
    )
    if suspicious == 0:
        return value
    try:
        candidate = value.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value
    if score_text(candidate) > score_text(value):
        return candidate
    return value


def score_text(value: str) -> int:
    cjk_count = sum(1 for char in value if "\u4e00" <= char <= "\u9fff")
    replacement_penalty = value.count("\ufffd") * 5
    suspicious_penalty = sum(1 for char in value if ord(char) >= 128 and not ("\u4e00" <= char <= "\u9fff"))
    return cjk_count * 4 - replacement_penalty - suspicious_penalty


def get_api_data(payload: Any) -> Any:
    if isinstance(payload, dict) and "data" in payload:
        return payload.get("data")
    return payload


def get_capture_payload(sample_dir: Path, filename: str) -> Any:
    return get_api_data(load_json(sample_dir / "captures" / filename))


def dash(value: Any) -> str:
    if value is None:
        return "--"
    text = str(value).strip()
    if not text or text.upper() == "NULL":
        return "--"
    return repair_text(text)


def status_label(value: Any) -> str:
    if value is None:
        return "--"
    return VERIFY_STATUS_LABELS.get(str(value), dash(value))


def to_int(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() == "NULL":
        return None
    try:
        return int(text)
    except ValueError:
        return None


def truthy(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip()
    if not text or text.upper() == "NULL":
        return None
    if text in {"1", "true", "True", "YES", "yes", "是", "\x01"}:
        return True
    if text in {"0", "false", "False", "NO", "no", "否", "\x00"}:
        return False
    return None


def yes_no(value: bool | None) -> str:
    if value is None:
        return "--"
    return "是" if value else "否"


def format_boolish(value: Any) -> str:
    normalized = truthy(value)
    if normalized is None:
        return dash(value)
    return "True" if normalized else "False"


def normalize_datetime_text(value: Any) -> str:
    text = dash(value)
    if text == "--":
        return text
    normalized = text.replace("T", " ")
    if len(normalized) >= 19:
        normalized = normalized[:19]
    return normalized


def set_ledger_field(content: str, label: str, value: str) -> str:
    pattern = rf"(?m)^- {re.escape(label)}：.*$"
    return re.sub(pattern, f"- {label}：{value}", content)


def ensure_ledger_field(content: str, label: str, value: str, *, after_label: str | None = None) -> str:
    if re.search(rf"(?m)^- {re.escape(label)}：.*$", content):
        return set_ledger_field(content, label, value)
    new_line = f"- {label}：{value}\n"
    if after_label and re.search(rf"(?m)^- {re.escape(after_label)}：.*$", content):
        return re.sub(rf"(?m)^- {re.escape(after_label)}：.*$", lambda match: f"{match.group(0)}\n{new_line.rstrip()}", content)
    return content.rstrip() + "\n" + new_line


def set_block_field(content: str, label: str, value: str) -> str:
    pattern = rf"(?m)^- {re.escape(label)}：\n(?:  - [^\n]*\n)*"
    replacement = f"- {label}：{value}\n"
    if re.search(pattern, content):
        return re.sub(pattern, replacement, content)
    return set_ledger_field(content, label, value)


def format_log_row(row: dict[str, str] | None) -> str:
    if not row:
        return "--"
    return ", ".join(
        [
            f"operation_log_id={dash(row.get('operation_log_id'))}",
            f"target_id={dash(row.get('target_id'))}",
            f"operation_result={dash(row.get('operation_result'))}",
            f"create_time={dash(row.get('create_time'))}",
        ]
    )


def parse_validation_result(result_path: Path) -> dict[str, list[dict[str, str]]]:
    if not result_path.exists():
        return {}

    lines = [
        repair_text(line.rstrip("\r"))
        for line in result_path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip() and not line.startswith("mysql: [Warning]")
    ]
    positions: list[int] = []
    cursor = 0
    for header in EXPECTED_HEADERS:
        for index in range(cursor, len(lines)):
            if lines[index] == header:
                positions.append(index)
                cursor = index + 1
                break
        else:
            raise RuntimeError(f"validation-result header not found: {header}")

    sections: dict[str, list[dict[str, str]]] = {}
    for offset, name in enumerate(SECTION_NAMES):
        header_line = lines[positions[offset]]
        headers = header_line.split("\t")
        start = positions[offset] + 1
        end = positions[offset + 1] if offset + 1 < len(positions) else len(lines)
        rows: list[dict[str, str]] = []
        for line in lines[start:end]:
            values = line.split("\t")
            if len(values) < len(headers):
                values.extend([""] * (len(headers) - len(values)))
            if len(values) > len(headers):
                values = values[: len(headers) - 1] + ["\t".join(values[len(headers) - 1 :])]
            rows.append({header: repair_text(value) for header, value in zip(headers, values)})
        sections[name] = rows
    return sections


def load_context(sample_dir: Path) -> dict[str, Any]:
    metadata = load_json(sample_dir / "sample-metadata.json") or {}
    capture_results = load_json(sample_dir / "captures" / "capture-results.json") or []
    validation_result = parse_validation_result(sample_dir / "validation-result.txt")

    status_final = get_capture_payload(sample_dir, "actor_verify_status_final.json")
    level_final = get_capture_payload(sample_dir, "actor_level_info_final.json")
    user_final = get_capture_payload(sample_dir, "actor_user_me_final.json")
    list_final = get_capture_payload(sample_dir, "admin_verify_list_final.json")
    detail_first = get_capture_payload(sample_dir, "admin_verify_detail_first.json")
    detail_retry = get_capture_payload(sample_dir, "admin_verify_detail_retry.json")

    list_items = []
    if isinstance(list_final, dict) and isinstance(list_final.get("list"), list):
        list_items = list_final["list"]

    ok_count = sum(1 for item in capture_results if item.get("status") == "ok")
    error_count = sum(1 for item in capture_results if item.get("status") != "ok")

    db_schema = first_row(validation_result.get("schema_release_history"))
    db_indexes = validation_result.get("identity_verification_index", [])
    db_user = first_row(validation_result.get("user"))
    db_profile = first_row(validation_result.get("actor_profile"))
    db_first = first_row(validation_result.get("identity_verification_first"))
    db_retry = first_row(validation_result.get("identity_verification_retry"))
    db_owner = first_row(validation_result.get("identity_verification_owner"))
    db_logs = validation_result.get("admin_operation_log", [])
    db_reject_log = first_matching_row(db_logs, "operation_code", "reject")
    db_approve_log = first_matching_row(db_logs, "operation_code", "approve")

    first_rejected = str(detail_first.get("status")) == "3" if isinstance(detail_first, dict) else False
    retry_approved = str(detail_retry.get("status")) == "2" if isinstance(detail_retry, dict) else False
    verification_id = str(metadata.get("verificationId") or "")
    retry_verification_id = str(metadata.get("retryVerificationId") or "")
    record_ids_different = bool(verification_id and retry_verification_id and verification_id != retry_verification_id)
    actor_approved = str(status_final.get("status")) == "2" if isinstance(status_final, dict) else False
    level_certified = truthy(level_final.get("isCertified")) if isinstance(level_final, dict) else None
    user_real_auth_status_matches = (
        str(status_final.get("status")) == str(db_user.get("real_auth_status"))
        if isinstance(status_final, dict) and db_user
        else None
    )
    actor_profile_matches = (
        actor_approved == truthy(db_profile.get("is_certified"))
        if isinstance(status_final, dict) and db_profile and truthy(db_profile.get("is_certified")) is not None
        else None
    )
    admin_db_consistent = check_admin_db_consistency(detail_first, detail_retry, db_first, db_retry)

    schema_present = db_schema is not None
    owner_present = db_owner is not None
    index_summary = summarize_index_rows(db_indexes)

    all_checks = all(
        value is True
        for value in [
            first_rejected,
            retry_approved,
            record_ids_different,
            actor_approved,
            level_certified,
            user_real_auth_status_matches,
            actor_profile_matches,
            admin_db_consistent,
            schema_present,
            owner_present,
        ]
    )
    has_any_evidence = ok_count > 0 or bool(validation_result)
    verdict = "闭环完成" if all_checks else ("局部完成" if has_any_evidence else "未开始")
    conclusion = build_conclusion(
        verdict=verdict,
        metadata=metadata,
        phone=(user_final or {}).get("phone"),
        db_schema=db_schema,
        db_owner=db_owner,
        db_first=db_first,
        db_retry=db_retry,
        first_rejected=first_rejected,
        retry_approved=retry_approved,
    )

    return {
        "metadata": metadata,
        "status_final": status_final or {},
        "level_final": level_final or {},
        "user_final": user_final or {},
        "detail_first": detail_first or {},
        "detail_retry": detail_retry or {},
        "list_items": list_items,
        "ok_count": ok_count,
        "error_count": error_count,
        "validation_result": validation_result,
        "db_schema": db_schema,
        "db_user": db_user,
        "db_profile": db_profile,
        "db_first": db_first,
        "db_retry": db_retry,
        "db_owner": db_owner,
        "db_reject_log": db_reject_log,
        "db_approve_log": db_approve_log,
        "first_rejected": first_rejected,
        "retry_approved": retry_approved,
        "record_ids_different": record_ids_different,
        "actor_approved": actor_approved,
        "level_certified": level_certified,
        "user_real_auth_status_matches": user_real_auth_status_matches,
        "actor_profile_matches": actor_profile_matches,
        "admin_db_consistent": admin_db_consistent,
        "schema_present": schema_present,
        "owner_present": owner_present,
        "index_summary": index_summary,
        "verdict": verdict,
        "conclusion": conclusion,
        "capture_directory": str(sample_dir / "captures"),
    }


def first_row(rows: list[dict[str, str]] | None) -> dict[str, str] | None:
    if rows:
        return rows[0]
    return None


def first_matching_row(rows: list[dict[str, str]], key: str, expected: str) -> dict[str, str] | None:
    for row in rows:
        if row.get(key) == expected:
            return row
    return None


def summarize_index_rows(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "--"
    parts = []
    for row in rows:
        parts.append(
            f"{dash(row.get('INDEX_NAME'))}(non_unique={dash(row.get('NON_UNIQUE'))}, column={dash(row.get('COLUMN_NAME'))})"
        )
    return "; ".join(parts)


def check_admin_db_consistency(
    detail_first: dict[str, Any],
    detail_retry: dict[str, Any],
    db_first: dict[str, str] | None,
    db_retry: dict[str, str] | None,
) -> bool | None:
    if not detail_first or not detail_retry or not db_first or not db_retry:
        return None
    first_match = (
        str(detail_first.get("status")) == str(db_first.get("status"))
        and dash(detail_first.get("rejectReason")) == dash(db_first.get("reject_reason"))
    )
    retry_match = (
        str(detail_retry.get("status")) == str(db_retry.get("status"))
        and normalize_datetime_text(detail_retry.get("reviewedAt")) == normalize_datetime_text(db_retry.get("reviewed_at"))
    )
    return first_match and retry_match


def build_conclusion(
    *,
    verdict: str,
    metadata: dict[str, Any],
    phone: Any,
    db_schema: dict[str, str] | None,
    db_owner: dict[str, str] | None,
    db_first: dict[str, str] | None,
    db_retry: dict[str, str] | None,
    first_rejected: bool,
    retry_approved: bool,
) -> str:
    user_id = dash(metadata.get("userId"))
    phone_text = dash(phone)
    phone_suffix = phone_text[-4:] if phone_text != "--" else "--"
    release_id = dash(db_schema.get("release_id")) if db_schema else "--"
    owner_user_id = dash(db_owner.get("user_id")) if db_owner else "--"
    first_id = dash(db_first.get("verification_id")) if db_first else dash(metadata.get("verificationId"))
    retry_id = dash(db_retry.get("verification_id")) if db_retry else dash(metadata.get("retryVerificationId"))
    if verdict == "闭环完成":
        return (
            f"同一样本 userId={user_id}（尾号 {phone_suffix}）已完成拒绝后重提再通过闭环；"
            f"DB 已回读 release_id={release_id}、owner.user_id={owner_user_id}、verification_id={first_id}/{retry_id}，"
            f"首单拒绝={yes_no(first_rejected)}，重提通过={yes_no(retry_approved)}。"
        )
    return (
        f"当前样本 userId={user_id} 已生成接口侧证据；"
        f"DB 回读 release_id={release_id}、owner.user_id={owner_user_id}、verification_id={first_id}/{retry_id}，"
        f"需继续按检查项完成闭环判定。"
    )


def update_ledger(sample_dir: Path, context: dict[str, Any]) -> None:
    ledger_path = sample_dir / "sample-ledger.md"
    content = read_text(ledger_path)

    metadata = context["metadata"]
    status_final = context["status_final"]
    level_final = context["level_final"]
    user_final = context["user_final"]
    detail_first = context["detail_first"]
    detail_retry = context["detail_retry"]
    db_schema = context["db_schema"]
    db_user = context["db_user"]
    db_profile = context["db_profile"]
    db_first = context["db_first"]
    db_retry = context["db_retry"]
    db_owner = context["db_owner"]
    db_reject_log = context["db_reject_log"]
    db_approve_log = context["db_approve_log"]

    replacements = {
        "phone": dash(user_final.get("phone")),
        "首次提交返回状态": status_label(detail_first.get("status")),
        "拒绝后 `verify/status`": status_label(detail_first.get("status")),
        "二次提交返回状态": status_label(detail_retry.get("status")),
        "最终 `verify/status`": status_label(status_final.get("status")),
        "最终 `rejectReason`": dash(status_final.get("rejectReason")),
        "最终 `level/info.isCertified`": dash(level_final.get("isCertified")),
        "最终 `profileCompletion`": dash(level_final.get("profileCompletion")),
        "首次申请单是否查到": yes_no(bool(detail_first)),
        "首次申请单状态": status_label(detail_first.get("status")),
        "首次拒绝备注": dash(detail_first.get("rejectReason")),
        "重提申请单是否查到": yes_no(bool(detail_retry)),
        "重提申请单状态": status_label(detail_retry.get("status")),
        "申请单总数": str(len(context["list_items"])),
        "是否保留首条拒绝记录": yes_no(context["first_rejected"]),
        "是否生成新申请单": yes_no(context["record_ids_different"]),
        "`V20260403_001__identity_verification_resubmit_history.sql` 是否存在": yes_no(context["schema_present"]),
        "schema 发布记录 `release_id`": dash(db_schema.get("release_id") if db_schema else None),
        "`user_id`": dash(db_user.get("user_id") if db_user else metadata.get("userId")),
        "`real_auth_status`": dash(db_user.get("real_auth_status") if db_user else None),
        "`real_name`": dash(db_profile.get("real_name") if db_profile else None),
        "`is_certified`": format_boolish(db_profile.get("is_certified") if db_profile else None),
        "首次申请单 `verification_id`": dash(db_first.get("verification_id") if db_first else metadata.get("verificationId")),
        "首次申请单 `status`": dash(db_first.get("status") if db_first else None),
        "首次申请单 `reject_reason`": dash(db_first.get("reject_reason") if db_first else None),
        "重提申请单 `verification_id`": dash(db_retry.get("verification_id") if db_retry else metadata.get("retryVerificationId")),
        "重提申请单 `status`": dash(db_retry.get("status") if db_retry else None),
        "重提申请单 `reviewed_at`": normalize_datetime_text(db_retry.get("reviewed_at") if db_retry else None),
        "`owner_id`": dash(db_owner.get("owner_id") if db_owner else None),
        "`id_card_hash`": dash(db_owner.get("id_card_hash") if db_owner else None),
        "`reject` 日志": format_log_row(db_reject_log),
        "`approve` 日志": format_log_row(db_approve_log),
        "首次申请单已拒绝": yes_no(context["first_rejected"]),
        "重提申请单已通过": yes_no(context["retry_approved"]),
        "两条申请单主键不同": yes_no(context["record_ids_different"]),
        "actor 最终状态 = `user.real_auth_status`": yes_no(context["user_real_auth_status_matches"]),
        "actor 最终状态 = `actor_profile.is_certified`": yes_no(context["actor_profile_matches"]),
        "后台详情与 DB 是否一致": yes_no(context["admin_db_consistent"]),
        "一句话结论": context["conclusion"],
    }

    for label, value in replacements.items():
        content = set_ledger_field(content, label, value)

    content = set_block_field(content, "当前判定", context["verdict"])
    content = ensure_ledger_field(content, "一句话结论", context["conclusion"], after_label="当前判定")
    write_text(ledger_path, content)


def generate_report(sample_dir: Path, context: dict[str, Any]) -> None:
    metadata = context["metadata"]
    status_final = context["status_final"]
    level_final = context["level_final"]
    detail_first = context["detail_first"]
    detail_retry = context["detail_retry"]
    db_schema = context["db_schema"]
    db_user = context["db_user"]
    db_profile = context["db_profile"]
    db_first = context["db_first"]
    db_retry = context["db_retry"]
    db_owner = context["db_owner"]

    lines = [
        "# Verify Validation Report",
        "",
        "## Sample",
        "",
        f"- SampleName: {dash(metadata.get('sampleName'))}",
        f"- Environment: {dash(metadata.get('environmentName'))}",
        f"- ApiBaseUrl: {dash(metadata.get('apiBaseUrl'))}",
        f"- UserId: {dash(metadata.get('userId'))}",
        f"- FirstVerificationId: {dash(metadata.get('verificationId'))}",
        f"- RetryVerificationId: {dash(metadata.get('retryVerificationId'))}",
        "",
        "## Extracted Facts",
        "",
        "### Final Actor Snapshot",
        "",
        f"- status: {status_label(status_final.get('status'))}",
        f"- realName: {dash(status_final.get('realName'))}",
        f"- rejectReason: {dash(status_final.get('rejectReason'))}",
        f"- submittedAt: {dash(status_final.get('submittedAt'))}",
        f"- reviewedAt: {dash(status_final.get('reviewedAt'))}",
        "",
        "### Final Level Snapshot",
        "",
        f"- isCertified: {dash(level_final.get('isCertified'))}",
        f"- level: {dash(level_final.get('level'))}",
        f"- profileCompletion: {dash(level_final.get('profileCompletion'))}",
        f"- membershipTier: {dash(level_final.get('membershipTier'))}",
        "",
        "### Admin Record Snapshot",
        "",
        f"- verifyRecordCount: {len(context['list_items'])}",
        f"- firstRecordStatus: {status_label(detail_first.get('status'))}",
        f"- firstRejectReason: {dash(detail_first.get('rejectReason'))}",
        f"- retryRecordStatus: {status_label(detail_retry.get('status'))}",
        f"- retryReviewedAt: {dash(detail_retry.get('reviewedAt'))}",
        "",
        "### Database Snapshot",
        "",
        f"- schemaMigrationPresent: {yes_no(context['schema_present'])}",
        f"- schemaReleaseId: {dash(db_schema.get('release_id') if db_schema else None)}",
        f"- identityVerificationIndex: {context['index_summary']}",
        f"- user.real_auth_status: {dash(db_user.get('real_auth_status') if db_user else None)}",
        f"- actor_profile.real_name: {dash(db_profile.get('real_name') if db_profile else None)}",
        f"- actor_profile.is_certified: {format_boolish(db_profile.get('is_certified') if db_profile else None)}",
        f"- firstDbRecordStatus: {dash(db_first.get('status') if db_first else None)}",
        f"- firstDbRejectReason: {dash(db_first.get('reject_reason') if db_first else None)}",
        f"- retryDbRecordStatus: {dash(db_retry.get('status') if db_retry else None)}",
        f"- retryDbReviewedAt: {normalize_datetime_text(db_retry.get('reviewed_at') if db_retry else None)}",
        f"- owner.user_id: {dash(db_owner.get('user_id') if db_owner else None)}",
        f"- owner.id_card_hash: {dash(db_owner.get('id_card_hash') if db_owner else None)}",
        f"- rejectLog: {format_log_row(context['db_reject_log'])}",
        f"- approveLog: {format_log_row(context['db_approve_log'])}",
        "",
        "## Cross Checks",
        "",
        f"- First record rejected: {yes_no(context['first_rejected'])}",
        f"- Retry record approved: {yes_no(context['retry_approved'])}",
        f"- Two verification IDs differ: {yes_no(context['record_ids_different'])}",
        f"- Final actor status is approved: {yes_no(context['actor_approved'])}",
        f"- Final level/info isCertified: {yes_no(context['level_certified'])}",
        f"- Actor status equals user.real_auth_status: {yes_no(context['user_real_auth_status_matches'])}",
        f"- Actor approval equals actor_profile.is_certified: {yes_no(context['actor_profile_matches'])}",
        f"- Admin detail matches DB records: {yes_no(context['admin_db_consistent'])}",
        "",
        "## Capture Summary",
        "",
        f"- OK endpoints: {context['ok_count']}",
        f"- Error endpoints: {context['error_count']}",
        f"- Validation result file: {yes_no(bool(context['validation_result']))}",
        f"- Capture directory: {context['capture_directory']}",
        "",
        "## Conclusion",
        "",
        f"- Verdict: {context['verdict']}",
        f"- Summary: {context['conclusion']}",
    ]

    write_text(sample_dir / "validation-report.md", "\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill verify sample ledger and validation report from captures and validation-result.")
    parser.add_argument("--sample-dir", required=True)
    args = parser.parse_args()

    sample_dir = Path(args.sample_dir).resolve()
    context = load_context(sample_dir)
    update_ledger(sample_dir, context)
    generate_report(sample_dir, context)
    print(f"verify artifacts synced: {sample_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
