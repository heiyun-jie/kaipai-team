import argparse
import os
import re
import shlex
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_OPERATOR = "codex"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
DEFAULT_SOURCE_DATABASE = "kaipai_dev"
DEFAULT_TARGET_DATABASE = "kaipai_prod"
DEFAULT_MYSQL_CONTAINER = "kaipai-mysql"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"
PROVIDER_CODE = "tencent-hunyuan"
EXPECTED_ENDPOINT = "https://aiart.tencentcloudapi.com"
EXPECTED_MODEL = "hunyuan-image-3.0"


@dataclass
class Context:
    mode: str
    run_id: str
    operator: str
    host: str
    user: str
    identity_file: Path
    mysql_database: str
    mysql_container: str
    source_database: str


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


def run_process(command: list[str], *, capture_output: bool = False, check: bool = True) -> subprocess.CompletedProcess[str]:
    log(f"local> {' '.join(command)}")
    result = subprocess.run(
        command,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
    )
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
    return result


def ssh_base(context: Context) -> list[str]:
    return [
        resolve_executable("ssh"),
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


def scp_base(context: Context) -> list[str]:
    return [
        resolve_executable("scp"),
        "-i",
        str(context.identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]


def run_ssh(context: Context, remote_command: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(context) + [remote_command], capture_output=True, check=check)


def sql_identifier(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        raise RuntimeError(f"unsafe SQL identifier: {value}")
    return value


def command_token(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
        raise RuntimeError(f"unsafe command token: {value}")
    return value


def sql_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "''")


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
    result: dict[str, str] = {}
    for field in fields:
        begin = f"__{field}_BEGIN__"
        end = f"__{field}_END__"
        start = output.find(begin)
        stop = output.find(end)
        if start == -1 or stop == -1 or stop < start:
            raise RuntimeError(f"missing helper output section: {field}")
        result[field] = output[start + len(begin):stop].strip("\r\n")
    return result


def parse_markers(mysql_result: str) -> dict[str, str]:
    markers: dict[str, str] = {}
    for raw_line in mysql_result.splitlines():
        line = raw_line.strip().strip("|").strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if re.fullmatch(r"[A-Z0-9_]+", key):
            markers[key] = value.strip()
    return markers


def validate_helper_status(summary: dict[str, str]) -> list[str]:
    if summary.get("FINAL_STATUS") == "passed":
        return []
    reason = "; ".join(line.strip() for line in summary.get("FAIL_REASON", "").splitlines() if line.strip())
    return [f"remote helper failed: {reason or summary.get('FINAL_STATUS', 'unknown')}"]


def validate_expected(markers: dict[str, str], expected: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for key, expected_value in expected.items():
        actual = markers.get(key)
        if actual != expected_value:
            errors.append(f"{key} expected={expected_value} actual={actual}")
    return errors


def validate_precheck_markers(markers: dict[str, str]) -> list[str]:
    return validate_expected(markers, {
        "SOURCE_PROVIDER_COUNT": "1",
        "SOURCE_ENABLED": "1",
        "SOURCE_ACTIVE": "1",
        "SOURCE_ENDPOINT": EXPECTED_ENDPOINT,
        "SOURCE_MODEL": EXPECTED_MODEL,
        "SOURCE_HAS_SECRET": "1",
        "SOURCE_LAST_TEST_STATUS": "success",
        "TARGET_CONFIG_COUNT": "0",
        "TARGET_ACTIVE_COUNT": "0",
        "TARGET_TENCENT_COUNT": "0",
        "PRECHECK_PASSED": "1",
    })


def validate_verify_markers(markers: dict[str, str], *, require_test_success: bool) -> list[str]:
    errors = validate_expected(markers, {
        "TARGET_TENCENT_COUNT": "1",
        "TARGET_ACTIVE_COUNT": "1",
        "ACTIVE_PROVIDER": PROVIDER_CODE,
        "ENDPOINT": EXPECTED_ENDPOINT,
        "MODEL": EXPECTED_MODEL,
        "HAS_SECRET": "1",
        "VERIFY_PASSED": "1",
    })
    try:
        audit_count = int(markers.get("MIGRATION_AUDIT_COUNT", "0"))
    except ValueError:
        audit_count = 0
    if audit_count < 1:
        errors.append(f"MIGRATION_AUDIT_COUNT expected>=1 actual={markers.get('MIGRATION_AUDIT_COUNT')}")
    if require_test_success and markers.get("LAST_TEST_STATUS") != "success":
        errors.append(f"LAST_TEST_STATUS expected=success actual={markers.get('LAST_TEST_STATUS')}")
    return errors


def require_remote_ready(context: Context) -> None:
    if not context.identity_file.exists():
        raise RuntimeError(f"identity file not found: {context.identity_file}")
    auth_probe = run_ssh(context, "printf 'key-auth-ok'")
    if auth_probe.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe failed")
    helper_probe = run_ssh(context, f"sudo -n {REMOTE_HELPER_PATH} --healthcheck")
    if helper_probe.stdout.strip() != "helper-ok":
        raise RuntimeError("remote helper healthcheck failed")


def upload_and_run_sql(context: Context, sql_content: str, helper_flag: str, remote_stem: str) -> dict[str, str]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".sql", delete=False) as handle:
        handle.write(sql_content)
        local_sql_path = Path(handle.name)

    remote_dir = f"/home/{context.user}/provider-migration-uploads/{context.run_id}"
    remote_sql_path = f"{remote_dir}/{remote_stem}.sql"
    try:
        run_ssh(context, f"mkdir -p {shlex.quote(remote_dir)}")
        run_process(scp_base(context) + [str(local_sql_path), f"{context.user}@{context.host}:{remote_sql_path}"])
        helper_command = (
            f"sudo -n {REMOTE_HELPER_PATH} "
            f"{helper_flag} "
            f"--mysql-script-path {shlex.quote(remote_sql_path)} "
            f"--mysql-database {sql_identifier(context.mysql_database)} "
            f"--mysql-container {command_token(context.mysql_container)}"
        )
        remote_result = run_ssh(context, helper_command, check=False)
        if remote_result.stderr and remote_result.stderr.strip():
            log(f"remote stderr> {remote_result.stderr.strip()}")
        if not remote_result.stdout:
            raise RuntimeError(f"remote helper returned no output, exit={remote_result.returncode}")
        return parse_helper_output(remote_result.stdout)
    finally:
        local_sql_path.unlink(missing_ok=True)
        try:
            run_ssh(context, f"rm -f {shlex.quote(remote_sql_path)}")
            run_ssh(context, f"rmdir --ignore-fail-on-non-empty {shlex.quote(remote_dir)}")
        except Exception as error:
            log(f"warning: failed to clean remote SQL file: {error}")


def build_precheck_calculation_sql(context: Context) -> str:
    source = sql_identifier(context.source_database)
    target = sql_identifier(context.mysql_database)
    return f"""
SELECT
  COUNT(*),
  COALESCE(MAX(`enabled`), 0),
  COALESCE(MAX(`active`), 0),
  COALESCE(MAX(JSON_UNQUOTE(JSON_EXTRACT(`public_config_json`, '$.endpoint'))), ''),
  COALESCE(MAX(JSON_UNQUOTE(JSON_EXTRACT(`public_config_json`, '$.model'))), ''),
  COALESCE(MAX(CASE WHEN `secret_config_ciphertext` IS NULL OR TRIM(`secret_config_ciphertext`) = '' THEN 0 ELSE 1 END), 0),
  COALESCE(MAX(`last_test_status`), 'NULL')
INTO
  @source_provider_count,
  @source_enabled,
  @source_active,
  @source_endpoint,
  @source_model,
  @source_has_secret,
  @source_last_test_status
FROM `{source}`.`ai_image_provider_config`
WHERE provider_code = '{PROVIDER_CODE}' AND deleted = 0;

SELECT COUNT(*) INTO @target_config_count
FROM `{target}`.`ai_image_provider_config`
WHERE deleted = 0;

SELECT COUNT(*) INTO @target_active_count
FROM `{target}`.`ai_image_provider_config`
WHERE active = 1 AND enabled = 1 AND deleted = 0;

SELECT COUNT(*) INTO @target_tencent_count
FROM `{target}`.`ai_image_provider_config`
WHERE provider_code = '{PROVIDER_CODE}' AND deleted = 0;

SET @precheck_passed = IF(
  @source_provider_count = 1
  AND @source_enabled = 1
  AND @source_active = 1
  AND @source_endpoint = '{EXPECTED_ENDPOINT}'
  AND @source_model = '{EXPECTED_MODEL}'
  AND @source_has_secret = 1
  AND @source_last_test_status = 'success'
  AND @target_config_count = 0
  AND @target_active_count = 0
  AND @target_tencent_count = 0,
  1,
  0
);
""".strip()


def build_precheck_marker_sql() -> str:
    return """
SELECT CONCAT('SOURCE_PROVIDER_COUNT=', @source_provider_count);
SELECT CONCAT('SOURCE_ENABLED=', @source_enabled);
SELECT CONCAT('SOURCE_ACTIVE=', @source_active);
SELECT CONCAT('SOURCE_ENDPOINT=', @source_endpoint);
SELECT CONCAT('SOURCE_MODEL=', @source_model);
SELECT CONCAT('SOURCE_HAS_SECRET=', @source_has_secret);
SELECT CONCAT('SOURCE_LAST_TEST_STATUS=', @source_last_test_status);
SELECT CONCAT('TARGET_CONFIG_COUNT=', @target_config_count);
SELECT CONCAT('TARGET_ACTIVE_COUNT=', @target_active_count);
SELECT CONCAT('TARGET_TENCENT_COUNT=', @target_tencent_count);
SELECT CONCAT('PRECHECK_PASSED=', @precheck_passed);
""".strip()


def build_precheck_sql(context: Context) -> str:
    return build_precheck_calculation_sql(context) + "\n\n" + build_precheck_marker_sql() + "\n"


def backup_table_names(context: Context) -> tuple[str, str]:
    suffix = re.sub(r"[^0-9A-Za-z]", "", context.run_id)[:20]
    if not suffix:
        raise RuntimeError("run_id cannot produce a safe backup suffix")
    return f"zz197_aipcfg_{suffix}", f"zz197_aipaud_{suffix}"


def build_apply_sql(context: Context) -> tuple[str, list[str]]:
    source = sql_identifier(context.source_database)
    target = sql_identifier(context.mysql_database)
    operator = sql_string(context.operator)
    backup_config, backup_audit = backup_table_names(context)
    calculation_sql = build_precheck_calculation_sql(context)

    sql = f"""
USE `{target}`;

{calculation_sql}

SET @signal_sql = IF(
  @precheck_passed = 1,
  'DO 0',
  "SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '00-197 provider migration precheck failed'"
);
PREPARE guard_stmt FROM @signal_sql;
EXECUTE guard_stmt;
DEALLOCATE PREPARE guard_stmt;

CREATE TABLE `{backup_config}` LIKE `{target}`.`ai_image_provider_config`;
INSERT INTO `{backup_config}` SELECT * FROM `{target}`.`ai_image_provider_config`;
CREATE TABLE `{backup_audit}` LIKE `{target}`.`ai_image_provider_config_audit`;
INSERT INTO `{backup_audit}` SELECT * FROM `{target}`.`ai_image_provider_config_audit`;

START TRANSACTION;

UPDATE `{target}`.`ai_image_provider_config`
SET `active` = 0,
    `update_user_name` = '{operator}',
    `last_update` = NOW()
WHERE `active` = 1;

INSERT INTO `{target}`.`ai_image_provider_config` (
  `config_id`, `provider_code`, `display_name`, `enabled`, `active`, `priority`,
  `public_config_json`, `secret_config_ciphertext`, `secret_mask_json`,
  `secret_updated_by`, `secret_updated_by_name`, `secret_updated_at`,
  `last_test_status`, `last_test_message`, `last_test_at`,
  `version`, `deleted`, `rid`,
  `create_user_id`, `create_user_name`, `create_time`,
  `update_user_id`, `update_user_name`, `last_update`
)
SELECT
  source.`config_id`, source.`provider_code`, source.`display_name`, 1, 1, source.`priority`,
  source.`public_config_json`, source.`secret_config_ciphertext`, source.`secret_mask_json`,
  source.`secret_updated_by`, source.`secret_updated_by_name`, source.`secret_updated_at`,
  NULL, '00-197 migrated; pending production provider test', NULL,
  0, 0, source.`rid`,
  source.`create_user_id`, source.`create_user_name`, source.`create_time`,
  0, '{operator}', NOW()
FROM `{source}`.`ai_image_provider_config` AS source
WHERE source.`provider_code` = '{PROVIDER_CODE}'
  AND source.`deleted` = 0;

INSERT INTO `{target}`.`ai_image_provider_config_audit` (
  `config_id`, `provider_code`, `action_code`,
  `before_public_config_json`, `after_public_config_json`,
  `before_secret_mask_json`, `after_secret_mask_json`,
  `operator_id`, `operator_name`, `result_status`, `message`,
  `version`, `deleted`, `rid`,
  `create_user_id`, `create_user_name`, `create_time`,
  `update_user_id`, `update_user_name`, `last_update`
)
SELECT
  config.`config_id`, config.`provider_code`, 'migration_restore',
  NULL, config.`public_config_json`,
  NULL, config.`secret_mask_json`,
  0, '{operator}', 'success', '00-197 restore active Tencent Hunyuan provider from kaipai_dev',
  0, 0, CONCAT('00-197-', config.`config_id`, '-', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s')),
  0, '{operator}', NOW(),
  0, '{operator}', NOW()
FROM `{target}`.`ai_image_provider_config` AS config
WHERE config.`provider_code` = '{PROVIDER_CODE}'
  AND config.`deleted` = 0;

COMMIT;

SELECT COUNT(*) INTO @post_tencent_count
FROM `{target}`.`ai_image_provider_config`
WHERE `provider_code` = '{PROVIDER_CODE}' AND `deleted` = 0;
SELECT COUNT(*) INTO @post_active_count
FROM `{target}`.`ai_image_provider_config`
WHERE `enabled` = 1 AND `active` = 1 AND `deleted` = 0;
SELECT COALESCE(MAX(`provider_code`), '') INTO @post_active_provider
FROM `{target}`.`ai_image_provider_config`
WHERE `enabled` = 1 AND `active` = 1 AND `deleted` = 0;
SELECT COALESCE(MAX(JSON_UNQUOTE(JSON_EXTRACT(`public_config_json`, '$.endpoint'))), '') INTO @post_endpoint
FROM `{target}`.`ai_image_provider_config`
WHERE `provider_code` = '{PROVIDER_CODE}' AND `deleted` = 0;
SELECT COALESCE(MAX(JSON_UNQUOTE(JSON_EXTRACT(`public_config_json`, '$.model'))), '') INTO @post_model
FROM `{target}`.`ai_image_provider_config`
WHERE `provider_code` = '{PROVIDER_CODE}' AND `deleted` = 0;
SELECT COALESCE(MAX(CASE WHEN `secret_config_ciphertext` IS NULL OR TRIM(`secret_config_ciphertext`) = '' THEN 0 ELSE 1 END), 0) INTO @post_has_secret
FROM `{target}`.`ai_image_provider_config`
WHERE `provider_code` = '{PROVIDER_CODE}' AND `deleted` = 0;
SELECT COUNT(*) INTO @post_migration_audit_count
FROM `{target}`.`ai_image_provider_config_audit`
WHERE `provider_code` = '{PROVIDER_CODE}' AND `action_code` = 'migration_restore' AND `deleted` = 0;
SELECT COALESCE(MAX(`last_test_status`), 'NULL') INTO @post_last_test_status
FROM `{target}`.`ai_image_provider_config`
WHERE `provider_code` = '{PROVIDER_CODE}' AND `deleted` = 0;
SET @post_verify_passed = IF(
  @post_tencent_count = 1
  AND @post_active_count = 1
  AND @post_active_provider = '{PROVIDER_CODE}'
  AND @post_endpoint = '{EXPECTED_ENDPOINT}'
  AND @post_model = '{EXPECTED_MODEL}'
  AND @post_has_secret = 1
  AND @post_migration_audit_count >= 1,
  1,
  0
);

SELECT CONCAT('BACKUP_CONFIG_TABLE=', '{backup_config}');
SELECT CONCAT('BACKUP_AUDIT_TABLE=', '{backup_audit}');
SELECT CONCAT('TARGET_TENCENT_COUNT=', @post_tencent_count);
SELECT CONCAT('TARGET_ACTIVE_COUNT=', @post_active_count);
SELECT CONCAT('ACTIVE_PROVIDER=', @post_active_provider);
SELECT CONCAT('ENDPOINT=', @post_endpoint);
SELECT CONCAT('MODEL=', @post_model);
SELECT CONCAT('HAS_SECRET=', @post_has_secret);
SELECT CONCAT('MIGRATION_AUDIT_COUNT=', @post_migration_audit_count);
SELECT CONCAT('LAST_TEST_STATUS=', @post_last_test_status);
SELECT CONCAT('VERIFY_PASSED=', @post_verify_passed);
SELECT CONCAT('MIGRATION_APPLIED=', @post_verify_passed);
""".strip() + "\n"
    return sql, [backup_config, backup_audit]


def build_verify_sql(context: Context) -> str:
    target = sql_identifier(context.mysql_database)
    calculation_sql = f"""
SELECT COUNT(*) INTO @target_tencent_count
FROM `{target}`.`ai_image_provider_config`
WHERE `provider_code` = '{PROVIDER_CODE}' AND `deleted` = 0;
SELECT COUNT(*) INTO @target_active_count
FROM `{target}`.`ai_image_provider_config`
WHERE `enabled` = 1 AND `active` = 1 AND `deleted` = 0;
SELECT COALESCE(MAX(`provider_code`), '') INTO @active_provider
FROM `{target}`.`ai_image_provider_config`
WHERE `enabled` = 1 AND `active` = 1 AND `deleted` = 0;
SELECT COALESCE(MAX(JSON_UNQUOTE(JSON_EXTRACT(`public_config_json`, '$.endpoint'))), '') INTO @endpoint
FROM `{target}`.`ai_image_provider_config`
WHERE `provider_code` = '{PROVIDER_CODE}' AND `deleted` = 0;
SELECT COALESCE(MAX(JSON_UNQUOTE(JSON_EXTRACT(`public_config_json`, '$.model'))), '') INTO @model
FROM `{target}`.`ai_image_provider_config`
WHERE `provider_code` = '{PROVIDER_CODE}' AND `deleted` = 0;
SELECT COALESCE(MAX(CASE WHEN `secret_config_ciphertext` IS NULL OR TRIM(`secret_config_ciphertext`) = '' THEN 0 ELSE 1 END), 0) INTO @has_secret
FROM `{target}`.`ai_image_provider_config`
WHERE `provider_code` = '{PROVIDER_CODE}' AND `deleted` = 0;
SELECT COUNT(*) INTO @migration_audit_count
FROM `{target}`.`ai_image_provider_config_audit`
WHERE `provider_code` = '{PROVIDER_CODE}' AND `action_code` = 'migration_restore' AND `deleted` = 0;
SELECT COALESCE(MAX(`last_test_status`), 'NULL') INTO @last_test_status
FROM `{target}`.`ai_image_provider_config`
WHERE `provider_code` = '{PROVIDER_CODE}' AND `deleted` = 0;
SET @verify_passed = IF(
  @target_tencent_count = 1
  AND @target_active_count = 1
  AND @active_provider = '{PROVIDER_CODE}'
  AND @endpoint = '{EXPECTED_ENDPOINT}'
  AND @model = '{EXPECTED_MODEL}'
  AND @has_secret = 1
  AND @migration_audit_count >= 1,
  1,
  0
);
""".strip()
    marker_sql = """
SELECT CONCAT('TARGET_TENCENT_COUNT=', @target_tencent_count);
SELECT CONCAT('TARGET_ACTIVE_COUNT=', @target_active_count);
SELECT CONCAT('ACTIVE_PROVIDER=', @active_provider);
SELECT CONCAT('ENDPOINT=', @endpoint);
SELECT CONCAT('MODEL=', @model);
SELECT CONCAT('HAS_SECRET=', @has_secret);
SELECT CONCAT('MIGRATION_AUDIT_COUNT=', @migration_audit_count);
SELECT CONCAT('LAST_TEST_STATUS=', @last_test_status);
SELECT CONCAT('VERIFY_PASSED=', @verify_passed);
""".strip()
    return calculation_sql + "\n\n" + marker_sql + "\n"


def execute_sql_mode(
    context: Context,
    sql: str,
    helper_flag: str,
    remote_stem: str,
    validator,
) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    summary = upload_and_run_sql(context, sql, helper_flag, remote_stem)
    errors = validate_helper_status(summary)
    markers = parse_markers(summary.get("MYSQL_RESULT", "")) if not errors else {}
    if not errors:
        errors.extend(validator(markers))
    return not errors, markers, errors, summary


def execute_precheck(context: Context) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    return execute_sql_mode(
        context,
        build_precheck_sql(context),
        "--mysql-validation",
        "tencent-provider-precheck",
        validate_precheck_markers,
    )


def execute_apply(context: Context) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    sql, _backup_tables = build_apply_sql(context)

    def validate(markers: dict[str, str]) -> list[str]:
        errors = validate_verify_markers(markers, require_test_success=False)
        if markers.get("MIGRATION_APPLIED") != "1":
            errors.append(f"MIGRATION_APPLIED expected=1 actual={markers.get('MIGRATION_APPLIED')}")
        if not markers.get("BACKUP_CONFIG_TABLE", "").startswith("zz197_"):
            errors.append("BACKUP_CONFIG_TABLE missing or invalid")
        if not markers.get("BACKUP_AUDIT_TABLE", "").startswith("zz197_"):
            errors.append("BACKUP_AUDIT_TABLE missing or invalid")
        return errors

    return execute_sql_mode(
        context,
        sql,
        "--mysql-apply",
        "tencent-provider-apply",
        validate,
    )


def execute_verify(
    context: Context,
    *,
    require_test_success: bool,
) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    return execute_sql_mode(
        context,
        build_verify_sql(context),
        "--mysql-validation",
        "tencent-provider-verify",
        lambda markers: validate_verify_markers(markers, require_test_success=require_test_success),
    )


def print_result(ok: bool, markers: dict[str, str], errors: list[str], summary: dict[str, str]) -> None:
    print(f"REMOTE_DATE={summary.get('REMOTE_DATE', '')}")
    print(f"MYSQL_DATABASE={summary.get('MYSQL_DATABASE', '')}")
    for key in sorted(markers):
        print(f"{key}={markers[key]}")
    if errors:
        for error in errors:
            print(f"ERROR={error}")
    print(f"RESULT={'passed' if ok else 'failed'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate the active Tencent Hunyuan provider config into production.")
    parser.add_argument("--mode", choices=["precheck", "apply", "verify"], required=True)
    parser.add_argument("--operator", default=DEFAULT_OPERATOR)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--identity-file", default=str(DEFAULT_IDENTITY_FILE))
    parser.add_argument("--source-database", default=DEFAULT_SOURCE_DATABASE)
    parser.add_argument("--mysql-database", default=DEFAULT_TARGET_DATABASE)
    parser.add_argument("--mysql-container", default=DEFAULT_MYSQL_CONTAINER)
    parser.add_argument("--require-test-success", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = Context(
        mode=args.mode,
        run_id=f"{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}-{args.mode}",
        operator=args.operator,
        host=args.host,
        user=args.user,
        identity_file=Path(args.identity_file),
        mysql_database=sql_identifier(args.mysql_database),
        mysql_container=command_token(args.mysql_container),
        source_database=sql_identifier(args.source_database),
    )
    require_remote_ready(context)

    if context.mode == "precheck":
        ok, markers, errors, summary = execute_precheck(context)
    elif context.mode == "apply":
        ok, markers, errors, summary = execute_apply(context)
    else:
        ok, markers, errors, summary = execute_verify(
            context,
            require_test_success=args.require_test_success,
        )
    print_result(ok, markers, errors, summary)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
