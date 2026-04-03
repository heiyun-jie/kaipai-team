import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


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


def ensure_schema_history_table(context: MigrationContext) -> dict[str, str]:
    return upload_and_run_mysql_script(
        context,
        sql_content=SCHEMA_HISTORY_TABLE_SQL + "\n",
        remote_stem="schema-history-bootstrap",
        mysql_mode="apply",
    )


def load_applied_scripts(context: MigrationContext) -> set[str]:
    query_sql = """
SELECT CONCAT('APPLIED_SCRIPT=', `script`)
FROM `schema_release_history`
ORDER BY `script`;
""".strip()
    summary = upload_and_run_mysql_script(
        context,
        sql_content=query_sql + "\n",
        remote_stem="schema-history-query",
        mysql_mode="validation",
    )
    applied = set()
    for line in summary["MYSQL_RESULT"].splitlines():
        marker = "APPLIED_SCRIPT="
        if marker in line:
            applied.add(line.split(marker, 1)[1].strip(" |"))
    return applied


def build_history_upsert_sql(context: MigrationContext, migration: MigrationFile, applied_mode: str) -> str:
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
)
ON DUPLICATE KEY UPDATE
  `checksum` = VALUES(`checksum`),
  `applied_mode` = VALUES(`applied_mode`),
  `applied_by` = VALUES(`applied_by`),
  `release_id` = VALUES(`release_id`),
  `notes` = VALUES(`notes`);
""".strip()


def build_apply_sql(context: MigrationContext, migration: MigrationFile) -> str:
    migration_sql = migration.path.read_text(encoding="utf-8", errors="replace").strip()
    history_sql = build_history_upsert_sql(context, migration, "apply")
    return "\n\n".join([SCHEMA_HISTORY_TABLE_SQL, migration_sql, history_sql]) + "\n"


def build_baseline_sql(context: MigrationContext, migration: MigrationFile) -> str:
    history_sql = build_history_upsert_sql(context, migration, "baseline")
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
    require_key_auth(context)
    require_helper(context)
    ensure_schema_history_table(context)
    applied_scripts = load_applied_scripts(context)

    results: list[dict[str, str]] = []
    for migration in migrations:
        if migration.script_name in applied_scripts:
            results.append(
                {
                    "script_name": migration.script_name,
                    "checksum": migration.checksum,
                    "result_mode": "skip-already-recorded",
                    "status": "skipped",
                    "remote_date": "",
                }
            )
            continue

        if context.mode == "baseline-existing":
            summary = upload_and_run_mysql_script(
                context,
                sql_content=build_baseline_sql(context, migration),
                remote_stem=migration.script_name.replace(".sql", "-baseline"),
                mysql_mode="apply",
            )
            result_mode = "baseline"
        else:
            summary = upload_and_run_mysql_script(
                context,
                sql_content=build_apply_sql(context, migration),
                remote_stem=migration.script_name.replace(".sql", "-apply"),
                mysql_mode="apply",
            )
            result_mode = "apply"

        applied_scripts.add(migration.script_name)
        results.append(
            {
                "script_name": migration.script_name,
                "checksum": migration.checksum,
                "result_mode": result_mode,
                "status": "applied",
                "remote_date": summary["REMOTE_DATE"],
            }
        )

    record_path = write_record(context, results)
    print(
        json.dumps(
            {
                "release_id": context.release_id,
                "record_path": str(record_path),
                "mode": context.mode,
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
