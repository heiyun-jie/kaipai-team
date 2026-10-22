import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"
MIGRATION_DIR = ROOT / "kaipaile-server" / "src" / "main" / "resources" / "db" / "migration"

DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_OPERATOR = "codex"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"
SCHEMA_HISTORY_RELEASE_ID_MAX_LENGTH = 64
SCHEMA_HISTORY_RELEASE_ID_HASH_LENGTH = 16
SCHEMA_HISTORY_RELEASE_ID_PREFIX_LENGTH = (
    SCHEMA_HISTORY_RELEASE_ID_MAX_LENGTH - SCHEMA_HISTORY_RELEASE_ID_HASH_LENGTH - 1
)

SCHEMA_HISTORY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `schema_release_history` (
  `schema_release_history_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'pk',
  `script` VARCHAR(255) NOT NULL COMMENT 'migration script name',
  `checksum` CHAR(64) NOT NULL COMMENT 'sha256 checksum',
  `applied_mode` VARCHAR(32) NOT NULL COMMENT 'apply, baseline',
  `applied_by` VARCHAR(64) NOT NULL DEFAULT '' COMMENT 'operator',
  `release_id` VARCHAR(64) NOT NULL DEFAULT '' COMMENT 'release batch id',
  `notes` VARCHAR(255) DEFAULT NULL COMMENT 'notes',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created time',
  PRIMARY KEY (`schema_release_history_id`),
  UNIQUE KEY `uk_schema_release_history_script` (`script`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='backend schema release history';
""".strip()


@dataclass
class MigrationFile:
    path: Path
    script_name: str
    checksum: str


@dataclass
class MigrationContext:
    release_id: str
    release_time: str
    label: str
    operator: str
    mode: str
    host: str
    user: str
    identity_file: Path
    mysql_database: str
    mysql_container: str
    history_release_id: str


def log(message: str) -> None:
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    print(f"[{timestamp}] {message}", flush=True)


def resolve_executable(name: str) -> str:
    if os.name == "nt":
        resolved = shutil.which(f"{name}.exe") or shutil.which(f"{name}.cmd") or shutil.which(name)
    else:
        resolved = shutil.which(name)
    if not resolved:
        raise RuntimeError(f"required executable not found: {name}")
    return resolved


def run_process(command: list[str], *, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    log(f"local> {' '.join(command)}")
    return subprocess.run(
        command,
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
    )


def ssh_base(context: MigrationContext) -> list[str]:
    ssh = resolve_executable("ssh")
    return [
        ssh,
        "-i",
        str(context.identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{context.user}@{context.host}",
    ]


def scp_base(context: MigrationContext) -> list[str]:
    scp = resolve_executable("scp")
    return [
        scp,
        "-i",
        str(context.identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]


def run_ssh(context: MigrationContext, remote_command: str) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(context) + [remote_command], capture_output=True)


def require_key_auth(context: MigrationContext) -> None:
    result = run_ssh(context, "printf 'key-auth-ok'")
    if result.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe returned unexpected output")
    log("native ssh key auth verified")


def require_helper(context: MigrationContext) -> None:
    result = run_ssh(context, f"sudo -n {REMOTE_HELPER_PATH} --healthcheck")
    if result.stdout.strip() != "helper-ok":
        raise RuntimeError("backend helper healthcheck returned unexpected output")
    log("remote backend helper and sudoers verified")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def normalize_schema_history_release_id(release_id: str) -> str:
    if len(release_id) <= SCHEMA_HISTORY_RELEASE_ID_MAX_LENGTH:
        return release_id
    digest = hashlib.md5(release_id.encode("utf-8")).hexdigest()[:SCHEMA_HISTORY_RELEASE_ID_HASH_LENGTH]
    normalized = release_id[:SCHEMA_HISTORY_RELEASE_ID_PREFIX_LENGTH] + "-" + digest
    log(
        "schema history release_id exceeded "
        f"{SCHEMA_HISTORY_RELEASE_ID_MAX_LENGTH} chars, normalized to {normalized}"
    )
    return normalized


def sql_string(value: str) -> str:
    return value.replace("'", "''")


def parse_helper_output(output: str) -> dict[str, str]:
    fields = [
        "REMOTE_DATE",
        "MYSQL_MODE",
        "MYSQL_DATABASE",
        "MYSQL_CONTAINER",
        "MYSQL_RESULT",
        "FINAL_STATUS",
        "FAIL_REASON",
    ]
    summary: dict[str, str] = {}
    for field in fields:
        begin = f"__{field}_BEGIN__"
        end = f"__{field}_END__"
        start = output.find(begin)
        stop = output.find(end)
        if start == -1 or stop == -1 or stop < start:
            raise RuntimeError(f"missing helper output section: {field}")
        content_start = start + len(begin)
        summary[field] = output[content_start:stop].strip("\r\n")
    return summary


def upload_and_run_mysql_script(
    context: MigrationContext,
    *,
    sql_content: str,
    remote_stem: str,
    mysql_mode: str,
) -> dict[str, str]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".sql", delete=False) as handle:
        handle.write(sql_content)
        local_sql_path = Path(handle.name)
    try:
        remote_dir = f"/home/{context.user}/backend-schema-uploads/{context.release_id}"
        remote_sql_path = f"{remote_dir}/{remote_stem}.sql"
        run_ssh(context, f"mkdir -p {remote_dir}")
        run_process(scp_base(context) + [str(local_sql_path), f"{context.user}@{context.host}:{remote_sql_path}"])
        helper_flag = "--mysql-apply" if mysql_mode == "apply" else "--mysql-validation"
        helper_command = (
            f"sudo -n {REMOTE_HELPER_PATH} "
            f"{helper_flag} "
            f"--mysql-script-path {remote_sql_path} "
            f"--mysql-database {context.mysql_database} "
            f"--mysql-container {context.mysql_container}"
        )
        result = run_ssh(context, helper_command)
        if result.stderr and result.stderr.strip():
            log(f"remote stderr> {result.stderr.strip()}")
        summary = parse_helper_output(result.stdout)
        if summary["FINAL_STATUS"] != "passed":
            raise RuntimeError(f"remote mysql {mysql_mode} failed: {summary['FAIL_REASON']}")
        return summary
    finally:
        try:
            local_sql_path.unlink(missing_ok=True)
        except UnboundLocalError:
            pass


def resolve_migration_file(value: str) -> MigrationFile:
    candidate = Path(value)
    if not candidate.is_absolute():
        first_try = ROOT / candidate
        if first_try.exists():
            candidate = first_try
        else:
            candidate = MIGRATION_DIR / value
    candidate = candidate.resolve()
    if not candidate.exists():
        raise RuntimeError(f"migration file not found: {value}")
    if candidate.suffix.lower() != ".sql":
        raise RuntimeError(f"migration file must be .sql: {candidate}")
    checksum = sha256_file(candidate)
    return MigrationFile(path=candidate, script_name=candidate.name, checksum=checksum)


def validate_candidate_manifest(
    manifest_path: Path,
    candidate_id: str,
    migrations: list[MigrationFile],
) -> dict[str, Any]:
    if not manifest_path.exists():
        raise RuntimeError(f"candidate manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("candidateId") != candidate_id:
        raise RuntimeError("candidate manifest id mismatch")

    entries = manifest.get("migrations")
    if not isinstance(entries, list):
        raise RuntimeError("candidate manifest migrations are missing")
    expected = [
        (str(entry.get("fileName", "")), str(entry.get("sha256", "")).upper())
        for entry in entries
    ]
    actual = [(migration.script_name, migration.checksum.upper()) for migration in migrations]
    if actual != expected:
        raise RuntimeError("migration order or checksum does not match candidate manifest")
    if any(not bool(entry.get("exists")) for entry in entries):
        raise RuntimeError("candidate manifest contains a missing migration")
    if any(not bool(entry.get("gitTracked")) for entry in entries):
        raise RuntimeError("candidate manifest contains an untracked migration")
    return manifest


NON_IDEMPOTENT_MIGRATIONS = {
    "V20260724_001__ai_profile_import_request_scene.sql",
    "V20260726_001__ai_profile_import_prompt_template_governance.sql",
    "V20260731_001__actor_card_tables.sql",
    "V20260731_002__actor_card_background_seed.sql",
    "V20260810_001__actor_card_attachment_asset_binding.sql",
}


def build_migration_preflight_sql(script_name: str) -> str:
    if script_name == "V20260724_001__ai_profile_import_request_scene.sql":
        return """
SET @request_table = (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'ai_profile_import_request_audit');
SET @scene_column = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'ai_profile_import_request_audit' AND column_name = 'scene');
SET @scene_not_null = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'ai_profile_import_request_audit' AND column_name = 'scene' AND is_nullable = 'NO');
SELECT CONCAT('PREFLIGHT_STATE=', CASE
  WHEN @request_table = 1 AND @scene_column = 0 THEN 'CLEAN_NOT_APPLIED'
  WHEN @request_table = 1 AND @scene_column = 1 AND @scene_not_null = 1 THEN 'FULLY_APPLIED'
  ELSE 'PARTIAL_OR_AMBIGUOUS'
END);
""".strip()

    if script_name == "V20260726_001__ai_profile_import_prompt_template_governance.sql":
        return """
SET @prompt_tables = (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name IN ('ai_profile_import_prompt_template', 'ai_profile_import_prompt_version', 'ai_profile_import_prompt_audit'));
SET @lineage_columns = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'ai_profile_import_request_audit' AND column_name IN ('prompt_template_code', 'prompt_version_id', 'prompt_version_no', 'prompt_schema_version', 'prompt_contract_version', 'prompt_runtime_sha256'));
SET @prompt_fks = (SELECT COUNT(*) FROM information_schema.table_constraints WHERE constraint_schema = DATABASE() AND constraint_type = 'FOREIGN KEY' AND constraint_name IN ('fk_ai_profile_import_prompt_version_template', 'fk_ai_profile_import_prompt_audit_template', 'fk_ai_profile_import_prompt_template_active', 'fk_ai_profile_import_prompt_template_draft'));
SET @prompt_templates = 0;
SET @prompt_versions = 0;
SET @prompt_count_sql = IF(@prompt_tables = 3, 'SELECT COUNT(*) INTO @prompt_templates FROM ai_profile_import_prompt_template WHERE deleted=0 AND template_code IN (''full_profile'',''works_only'')', 'DO 0');
PREPARE prompt_count_stmt FROM @prompt_count_sql; EXECUTE prompt_count_stmt; DEALLOCATE PREPARE prompt_count_stmt;
SET @version_count_sql = IF(@prompt_tables = 3, 'SELECT COUNT(*) INTO @prompt_versions FROM ai_profile_import_prompt_version WHERE deleted=0 AND version_no=1', 'DO 0');
PREPARE version_count_stmt FROM @version_count_sql; EXECUTE version_count_stmt; DEALLOCATE PREPARE version_count_stmt;
SELECT CONCAT('PREFLIGHT_STATE=', CASE
  WHEN @prompt_tables = 0 AND @lineage_columns = 0 AND @prompt_fks = 0 THEN 'CLEAN_NOT_APPLIED'
  WHEN @prompt_tables = 3 AND @lineage_columns = 6 AND @prompt_fks = 4 AND @prompt_templates = 2 AND @prompt_versions >= 2 THEN 'FULLY_APPLIED'
  ELSE 'PARTIAL_OR_AMBIGUOUS'
END);
""".strip()

    if script_name == "V20260731_001__actor_card_tables.sql":
        return """
SET @actor_card_tables = (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name IN ('actor_card', 'actor_card_work', 'actor_card_background'));
SELECT CONCAT('PREFLIGHT_STATE=', CASE
  WHEN @actor_card_tables = 0 THEN 'CLEAN_NOT_APPLIED'
  WHEN @actor_card_tables = 3 THEN 'FULLY_APPLIED'
  ELSE 'PARTIAL_OR_AMBIGUOUS'
END);
""".strip()

    if script_name == "V20260731_002__actor_card_background_seed.sql":
        return """
SET @background_table = (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'actor_card_background');
SET @background_rows = 0;
SET @background_count_sql = IF(@background_table = 1, 'SELECT COUNT(*) INTO @background_rows FROM actor_card_background WHERE id BETWEEN 1 AND 10', 'DO 0');
PREPARE background_count_stmt FROM @background_count_sql; EXECUTE background_count_stmt; DEALLOCATE PREPARE background_count_stmt;
SELECT CONCAT('PREFLIGHT_STATE=', CASE
  WHEN @background_table = 1 AND @background_rows = 0 THEN 'CLEAN_NOT_APPLIED'
  WHEN @background_table = 1 AND @background_rows = 10 THEN 'FULLY_APPLIED'
  ELSE 'PARTIAL_OR_AMBIGUOUS'
END);
""".strip()

    if script_name == "V20260810_001__actor_card_attachment_asset_binding.sql":
        return """
SET @actor_card_table = (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'actor_card');
SET @attachment_column = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'actor_card' AND column_name = 'attachment_asset_id');
SET @attachment_index = (SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name = 'actor_card' AND index_name = 'idx_actor_card_attachment_asset');
SELECT CONCAT('PREFLIGHT_STATE=', CASE
  WHEN @actor_card_table = 1 AND @attachment_column = 0 AND @attachment_index = 0 THEN 'CLEAN_NOT_APPLIED'
  WHEN @actor_card_table = 1 AND @attachment_column = 1 AND @attachment_index > 0 THEN 'FULLY_APPLIED'
  ELSE 'PARTIAL_OR_AMBIGUOUS'
END);
""".strip()

    raise RuntimeError(f"no preflight is defined for migration: {script_name}")


def parse_preflight_state(mysql_result: str) -> str:
    marker = "PREFLIGHT_STATE="
    for line in mysql_result.splitlines():
        if marker in line:
            state = line.split(marker, 1)[1].strip(" |")
            if state in {"CLEAN_NOT_APPLIED", "FULLY_APPLIED", "PARTIAL_OR_AMBIGUOUS"}:
                return state
    raise RuntimeError("migration preflight state is missing")


def run_migration_preflight(context: MigrationContext, migration: MigrationFile) -> str:
    summary = upload_and_run_mysql_script(
        context,
        sql_content=build_migration_preflight_sql(migration.script_name) + "\n",
        remote_stem=migration.script_name.replace(".sql", "-preflight"),
        mysql_mode="validation",
    )
    return parse_preflight_state(summary["MYSQL_RESULT"])


def build_global_schema_assertion_sql(migrations: list[MigrationFile]) -> str:
    checksum_rows = " UNION ALL ".join(
        "SELECT "
        f"'{sql_string(migration.script_name)}' AS script, "
        f"'{migration.checksum.upper()}' AS checksum"
        for migration in migrations
    )
    return f"""
SET @target_tables = (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name IN (
  'actor_profile', 'actor_experience', 'actor_profile_representative_work',
  'actor_media_asset', 'actor_profile_asset', 'share_card_asset', 'share_card_favorite',
  'ai_profile_import_config', 'ai_profile_import_config_audit', 'ai_profile_import_request_audit',
  'ai_profile_import_prompt_template', 'ai_profile_import_prompt_version', 'ai_profile_import_prompt_audit',
  'actor_card', 'actor_card_work', 'actor_card_background',
  'actor_card_media_set', 'actor_card_media_item', 'schema_release_history'
));
SET @profile_columns = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'actor_profile' AND column_name IN ('avatar_asset_id','current_resume_asset_id','birth_year','birth_month','birth_day','birth_precision','origin_place','school_name','major_name','language_tags_json','specialty_tags_json','role_type_tags_json','professional_ability_tags_json','work_library_version'));
SET @experience_columns = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'actor_experience' AND column_name IN ('publish_status','work_type_code','role_level_code','sync_sound_status','collaborators_json','achievement_text','normalized_drama_name','normalized_role_name','dedupe_key','source_type'));
SET @request_columns = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'ai_profile_import_request_audit' AND column_name IN ('scene','prompt_template_code','prompt_version_id','prompt_version_no','prompt_schema_version','prompt_contract_version','prompt_runtime_sha256'));
SET @attachment_columns = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'actor_card' AND column_name = 'attachment_asset_id');
SET @background_rows = (SELECT COUNT(*) FROM actor_card_background WHERE id BETWEEN 1 AND 10);
SET @prompt_templates = (SELECT COUNT(*) FROM ai_profile_import_prompt_template WHERE deleted=0 AND template_code IN ('full_profile','works_only'));
SET @candidate_history = (SELECT COUNT(*) FROM schema_release_history WHERE script IN ({','.join(repr(m.script_name) for m in migrations)}));
SET @checksum_mismatch = (SELECT COUNT(*) FROM schema_release_history h JOIN ({checksum_rows}) expected ON expected.script = h.script WHERE h.checksum <> expected.checksum);
SELECT CONCAT('ASSERT_TARGET_TABLES=', @target_tables);
SELECT CONCAT('ASSERT_PROFILE_COLUMNS=', @profile_columns);
SELECT CONCAT('ASSERT_EXPERIENCE_COLUMNS=', @experience_columns);
SELECT CONCAT('ASSERT_REQUEST_COLUMNS=', @request_columns);
SELECT CONCAT('ASSERT_ATTACHMENT_COLUMNS=', @attachment_columns);
SELECT CONCAT('ASSERT_BACKGROUND_ROWS=', @background_rows);
SELECT CONCAT('ASSERT_PROMPT_TEMPLATES=', @prompt_templates);
SELECT CONCAT('ASSERT_CANDIDATE_HISTORY=', @candidate_history);
SELECT CONCAT('ASSERT_CHECKSUM_MISMATCH=', @checksum_mismatch);
""".strip()


def parse_assertion_markers(mysql_result: str) -> dict[str, int]:
    markers: dict[str, int] = {}
    for line in mysql_result.splitlines():
        match = re.search(r"(ASSERT_[A-Z_]+)=(\d+)", line)
        if match:
            markers[match.group(1)] = int(match.group(2))
    return markers


def assert_global_schema(context: MigrationContext, migrations: list[MigrationFile]) -> dict[str, int]:
    summary = upload_and_run_mysql_script(
        context,
        sql_content=build_global_schema_assertion_sql(migrations) + "\n",
        remote_stem="candidate-global-schema-assertions",
        mysql_mode="validation",
    )
    markers = parse_assertion_markers(summary["MYSQL_RESULT"])
    expected = {
        "ASSERT_TARGET_TABLES": 19,
        "ASSERT_PROFILE_COLUMNS": 14,
        "ASSERT_EXPERIENCE_COLUMNS": 10,
        "ASSERT_REQUEST_COLUMNS": 7,
        "ASSERT_ATTACHMENT_COLUMNS": 1,
        "ASSERT_BACKGROUND_ROWS": 7,
        "ASSERT_PROMPT_TEMPLATES": 2,
        "ASSERT_CANDIDATE_HISTORY": len(migrations),
        "ASSERT_CHECKSUM_MISMATCH": 0,
    }
    failures = {
        name: {"expected": value, "actual": markers.get(name)}
        for name, value in expected.items()
        if markers.get(name) != value
    }
    if failures:
        raise RuntimeError(f"global schema assertions failed: {json.dumps(failures, sort_keys=True)}")
    return markers


def ensure_schema_history_table(context: MigrationContext) -> dict[str, str]:
    return upload_and_run_mysql_script(
        context,
        sql_content=SCHEMA_HISTORY_TABLE_SQL + "\n",
        remote_stem="schema-history-bootstrap",
        mysql_mode="apply",
    )


def load_applied_scripts(context: MigrationContext) -> dict[str, dict[str, str]]:
    query_sql = """
SELECT CONCAT(
  'APPLIED_RECORD=',
  `script`, '|', `checksum`, '|', `applied_mode`, '|', `release_id`
)
FROM `schema_release_history`
ORDER BY `script`;
""".strip()
    summary = upload_and_run_mysql_script(
        context,
        sql_content=query_sql + "\n",
        remote_stem="schema-history-query",
        mysql_mode="validation",
    )
    return parse_applied_records(summary["MYSQL_RESULT"])


def parse_applied_records(mysql_result: str) -> dict[str, dict[str, str]]:
    applied: dict[str, dict[str, str]] = {}
    for line in mysql_result.splitlines():
        marker = "APPLIED_RECORD="
        if marker in line:
            record = line.split(marker, 1)[1].strip(" |")
            parts = record.split("|", 3)
            if len(parts) != 4 or not re.fullmatch(r"[0-9A-Fa-f]{64}", parts[1]):
                continue
            script, checksum, applied_mode, release_id = parts
            applied[script] = {
                "checksum": checksum.upper(),
                "applied_mode": applied_mode,
                "release_id": release_id,
            }
    return applied


def build_history_insert_sql(context: MigrationContext, migration: MigrationFile, applied_mode: str) -> str:
    notes = "baseline existing schema state" if applied_mode == "baseline" else "executed via run-backend-schema-migration.py"
    return f"""
INSERT INTO `schema_release_history` (
  `script`,
  `checksum`,
  `applied_mode`,
  `applied_by`,
  `release_id`,
  `notes`
) VALUES (
  '{sql_string(migration.script_name)}',
  '{migration.checksum}',
  '{applied_mode}',
  '{sql_string(context.operator)}',
  '{sql_string(context.history_release_id)}',
  '{sql_string(notes)}'
);
""".strip()


def build_apply_sql(context: MigrationContext, migration: MigrationFile) -> str:
    migration_sql = migration.path.read_text(encoding="utf-8", errors="replace").strip()
    history_sql = build_history_insert_sql(context, migration, "apply")
    return "\n\n".join([SCHEMA_HISTORY_TABLE_SQL, migration_sql, history_sql]) + "\n"


def build_baseline_sql(context: MigrationContext, migration: MigrationFile) -> str:
    history_sql = build_history_insert_sql(context, migration, "baseline")
    return "\n\n".join([SCHEMA_HISTORY_TABLE_SQL, history_sql]) + "\n"


def write_record(context: MigrationContext, results: list[dict[str, str]]) -> Path:
    record_path = RECORDS_DIR / f"{context.release_id}.md"
    if record_path.exists():
        raise RuntimeError(f"record already exists: {record_path}")

    file_lines = []
    for item in results:
        file_lines.extend(
            [
                f"- `{item['script_name']}`",
                f"  - mode: `{item['result_mode']}`",
                f"  - checksum: `{item['checksum']}`",
                f"  - status: `{item['status']}`",
                f"  - remote date: `{item['remote_date']}`",
            ]
        )

    content = f"""# 后端 Schema 发布记录

## 1. 基本信息

- 发布批次号：`{context.release_id}`
- Schema History 发布批次号：`{context.history_release_id}`
- 发布时间：`{datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")}`
- 发布范围：`backend-schema`
- 操作人：`{context.operator}`
- 执行模式：`{context.mode}`
- 关联 Spec / 需求：
  - `00-29 backend-admin-release-governance`
  - `05-09 identity-verification`

## 2. 目标环境

- 远端主机：`{context.host}`
- MySQL 容器：`{context.mysql_container}`
- MySQL 数据库：`{context.mysql_database}`
- 远端 helper：`{REMOTE_HELPER_PATH}`

## 3. 执行文件

{chr(10).join(file_lines)}

## 4. 结论

- 最终结论：`完成`
- 后续动作：
  - 若本批包含后端代码发布，必须在 schema 完成后再执行标准 `backend-only`
  - 后续所有涉及 `db/migration` 的后端发布，必须先走本脚本或由 `backend-only` 前置门禁拦截
"""
    record_path.write_text(content, encoding="utf-8")
    return record_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply or baseline backend schema migration scripts through the standard helper.")
    parser.add_argument("--label", required=True, help="release label suffix")
    parser.add_argument("--operator", default=DEFAULT_OPERATOR, help="operator name written to release record")
    parser.add_argument("--mode", choices=["apply", "baseline-existing"], default="apply")
    parser.add_argument("--migration-file", action="append", required=True, help="migration .sql file path or filename; repeatable")
    parser.add_argument("--host", default=os.getenv("KAIPAI_RELEASE_HOST", DEFAULT_HOST))
    parser.add_argument("--user", default=os.getenv("KAIPAI_RELEASE_USER", DEFAULT_USER))
    parser.add_argument("--identity-file", default=os.getenv("KAIPAI_RELEASE_IDENTITY_FILE", str(DEFAULT_IDENTITY_FILE)))
    parser.add_argument("--mysql-database", default="kaipai_dev")
    parser.add_argument("--mysql-container", default="kaipai-mysql")
    parser.add_argument("--candidate-manifest", help="frozen candidate manifest JSON")
    parser.add_argument("--candidate-id", help="candidate id expected in the manifest")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    release_time = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    release_id = f"{release_time}-backend-schema-{args.label}"
    context = MigrationContext(
        release_id=release_id,
        release_time=release_time,
        label=args.label,
        operator=args.operator,
        mode=args.mode,
        host=args.host,
        user=args.user,
        identity_file=Path(args.identity_file),
        mysql_database=args.mysql_database,
        mysql_container=args.mysql_container,
        history_release_id=normalize_schema_history_release_id(release_id),
    )

    if not context.identity_file.exists():
        raise RuntimeError(
            f"identity file not found: {context.identity_file}. Run "
            "`python .sce/runbooks/backend-admin-release/scripts/bootstrap-admin-release.py --operator <name>` first."
        )

    migrations = [resolve_migration_file(item) for item in args.migration_file]
    if bool(args.candidate_manifest) != bool(args.candidate_id):
        raise RuntimeError("candidate-manifest and candidate-id must be supplied together")
    manifest_sha256 = ""
    if args.candidate_manifest:
        manifest_path = Path(args.candidate_manifest).resolve()
        validate_candidate_manifest(manifest_path, args.candidate_id, migrations)
        manifest_sha256 = sha256_file(manifest_path)

    require_key_auth(context)
    require_helper(context)
    ensure_schema_history_table(context)
    applied_scripts = load_applied_scripts(context)

    results: list[dict[str, str]] = []
    for migration in migrations:
        applied_record = applied_scripts.get(migration.script_name)
        if applied_record:
            if applied_record["checksum"] != migration.checksum.upper():
                raise RuntimeError(
                    "schema history checksum mismatch for "
                    f"{migration.script_name}: recorded={applied_record['checksum']} "
                    f"candidate={migration.checksum.upper()}"
                )
            results.append(
                {
                    "script_name": migration.script_name,
                    "checksum": migration.checksum,
                    "result_mode": "skip-same-checksum",
                    "status": "skipped",
                    "remote_date": "",
                    "preflight_state": "HISTORY_CHECKSUM_MATCH",
                }
            )
            continue

        preflight_state = "NOT_REQUIRED"
        if migration.script_name in NON_IDEMPOTENT_MIGRATIONS:
            preflight_state = run_migration_preflight(context, migration)
            if preflight_state == "PARTIAL_OR_AMBIGUOUS":
                raise RuntimeError(
                    f"partial or ambiguous migration state: {migration.script_name}"
                )

        if context.mode == "baseline-existing":
            if migration.script_name in NON_IDEMPOTENT_MIGRATIONS and preflight_state != "FULLY_APPLIED":
                raise RuntimeError(
                    f"baseline requires fully applied state: {migration.script_name}={preflight_state}"
                )
            summary = upload_and_run_mysql_script(
                context,
                sql_content=build_baseline_sql(context, migration),
                remote_stem=migration.script_name.replace(".sql", "-baseline"),
                mysql_mode="apply",
            )
            result_mode = "baseline"
        else:
            if migration.script_name in NON_IDEMPOTENT_MIGRATIONS and preflight_state != "CLEAN_NOT_APPLIED":
                raise RuntimeError(
                    f"apply requires clean state: {migration.script_name}={preflight_state}"
                )
            summary = upload_and_run_mysql_script(
                context,
                sql_content=build_apply_sql(context, migration),
                remote_stem=migration.script_name.replace(".sql", "-apply"),
                mysql_mode="apply",
            )
            result_mode = "apply"

        applied_scripts[migration.script_name] = {
            "checksum": migration.checksum.upper(),
            "applied_mode": result_mode,
            "release_id": context.history_release_id,
        }
        results.append(
            {
                "script_name": migration.script_name,
                "checksum": migration.checksum,
                "result_mode": result_mode,
                "status": "applied",
                "remote_date": summary["REMOTE_DATE"],
                "preflight_state": preflight_state,
            }
        )

    assertions = assert_global_schema(context, migrations) if args.candidate_manifest else {}
    record_path = write_record(context, results)
    print(
        json.dumps(
            {
                "release_id": context.release_id,
                "record_path": str(record_path),
                "mode": context.mode,
                "candidate_id": args.candidate_id or "",
                "manifest_sha256": manifest_sha256,
                "assertions": assertions,
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
