import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SPEC_DIR = ROOT / ".sce" / "specs" / "00-194-current-phase-production-linxia-test-account-phone-binding"
SAMPLES_DIR = SPEC_DIR / "samples"

DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_OPERATOR = "codex"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"
DEFAULT_SOURCE_DATABASE = "kaipai_dev"
DEFAULT_MIGRATION_SOURCE_USER_ID = "10007"
DEFAULT_PUBLIC_BASE_URL = "https://api.kplyyk.com"


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
    target_phone: str
    source_user_id: str | None
    output_dir: Path
    public_base_url: str = DEFAULT_PUBLIC_BASE_URL


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
    safe_command = ["[sql-file]" if item.endswith(".sql") and "Temp" in item else item for item in command]
    log(f"local> {' '.join(safe_command)}")
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


def mask_phone(phone: str) -> str:
    if len(phone) < 7:
        return "***"
    return f"{phone[:3]}****{phone[-4:]}"


def sql_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "''")


def sql_identifier(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        raise RuntimeError(f"unsafe SQL identifier: {value}")
    return value


def migration_source_user_id(context: Context) -> int:
    return int(context.source_user_id or DEFAULT_MIGRATION_SOURCE_USER_ID)


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


def validate_helper_status(helper_summary: dict[str, str]) -> list[str]:
    if helper_summary.get("FINAL_STATUS") == "passed":
        return []
    fail_reason = "；".join(
        line.strip()
        for line in helper_summary.get("FAIL_REASON", "").splitlines()
        if line.strip()
    )
    if not fail_reason:
        fail_reason = helper_summary.get("FINAL_STATUS", "unknown")
    return [f"remote helper failed: {fail_reason}"]


def parse_markers(mysql_result: str) -> dict[str, str]:
    markers: dict[str, str] = {}
    for raw_line in mysql_result.splitlines():
        line = raw_line.strip().strip("|").strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if re.fullmatch(r"[A-Z0-9_]+", key):
            marker_key = key
            duplicate_index = 2
            while marker_key in markers:
                marker_key = f"{key}_{duplicate_index}"
                duplicate_index += 1
            markers[marker_key] = value
    return markers


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

    remote_dir = f"/home/{context.user}/phone-binding-uploads/{context.run_id}"
    remote_sql_path = f"{remote_dir}/{remote_stem}.sql"
    try:
        run_ssh(context, f"mkdir -p {remote_dir}")
        run_process(scp_base(context) + [str(local_sql_path), f"{context.user}@{context.host}:{remote_sql_path}"])
        helper_command = (
            f"sudo -n {REMOTE_HELPER_PATH} "
            f"{helper_flag} "
            f"--mysql-script-path {remote_sql_path} "
            f"--mysql-database {context.mysql_database} "
            f"--mysql-container {context.mysql_container}"
        )
        remote_result = run_ssh(context, helper_command, check=False)
        if remote_result.stderr and remote_result.stderr.strip():
            log(f"remote stderr> {remote_result.stderr.strip()}")
        if remote_result.returncode != 0 and not remote_result.stdout:
            raise RuntimeError(f"remote helper failed with exit code {remote_result.returncode}")
        return parse_helper_output(remote_result.stdout)
    finally:
        local_sql_path.unlink(missing_ok=True)
        try:
            run_ssh(context, f"rm -f {remote_sql_path}")
        except Exception as error:
            log(f"warning: failed to remove remote sql file: {error}")


def api_request_json(context: Context, path: str, payload: dict[str, str] | None = None, token: str | None = None) -> dict:
    url = f"{context.public_base_url.rstrip('/')}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method="GET" if payload is None else "POST",
    )
    safe_url = url.replace(context.target_phone, mask_phone(context.target_phone))
    log(f"api> {request.method} {safe_url}")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"api request failed {error.code}: {redact_output(body, context.target_phone)}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"api request failed: {error.reason}") from error

    try:
        return json.loads(body)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"api response is not json: {body[:200]}") from error


def require_api_ok(response: dict, label: str) -> dict | str | int | None:
    if response.get("code") != 200:
        raise RuntimeError(f"{label} returned code={response.get('code')} message={response.get('message', '')}")
    return response.get("data")


def local_summary(context: Context, markers: dict[str, str]) -> dict[str, str]:
    mysql_result = "\n".join(f"{key}={value}" for key, value in markers.items())
    return {
        "REMOTE_DATE": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),
        "MYSQL_MODE": context.mode,
        "MYSQL_DATABASE": context.mysql_database,
        "MYSQL_CONTAINER": context.mysql_container,
        "MYSQL_RESULT": redact_output(mysql_result, context.target_phone),
        "FINAL_STATUS": "passed",
        "FAIL_REASON": "",
    }


def source_user_condition(context: Context) -> str:
    if context.source_user_id:
        return f"AND u.user_id = {int(context.source_user_id)}"
    return ""


def build_candidate_temp_sql(context: Context) -> str:
    return f"""
SET @target_phone = '{sql_string(context.target_phone)}';
SET @target_phone_mask = CONCAT(LEFT(@target_phone, 3), '****', RIGHT(@target_phone, 4));

DROP TEMPORARY TABLE IF EXISTS kp_linxia_candidates;
CREATE TEMPORARY TABLE kp_linxia_candidates AS
SELECT DISTINCT
  u.user_id,
  u.phone AS user_phone,
  u.account AS user_account,
  u.user_name,
  u.user_type,
  u.status,
  ap.actor_profile_id,
  ap.nick_name,
  ap.real_name,
  ap.phone AS actor_phone
FROM `user` u
JOIN `actor_profile` ap
  ON ap.user_id = u.user_id
 AND ap.deleted = 0
WHERE u.deleted = 0
  AND u.user_type = 1
  {source_user_condition(context)}
  AND (
    u.user_name = '林夏'
    OR ap.nick_name = '林夏'
    OR ap.real_name = '林夏'
  );

SET @candidate_count = (SELECT COUNT(*) FROM kp_linxia_candidates);
SET @source_user_id = IF(@candidate_count = 1, (SELECT MIN(user_id) FROM kp_linxia_candidates), NULL);
SET @source_old_phone = IF(@source_user_id IS NULL, NULL, (SELECT phone FROM `user` WHERE user_id = @source_user_id));
SET @source_old_phone_mask = IF(@source_old_phone IS NULL OR @source_old_phone = '', '', CONCAT(LEFT(@source_old_phone, 3), '****', RIGHT(@source_old_phone, 4)));
SET @target_other_user_count = (
  SELECT COUNT(*)
  FROM `user`
  WHERE deleted = 0
    AND phone = @target_phone
    AND (@source_user_id IS NULL OR user_id <> @source_user_id)
);
SET @active_actor_profile_count = IF(
  @source_user_id IS NULL,
  0,
  (SELECT COUNT(*) FROM actor_profile WHERE deleted = 0 AND user_id = @source_user_id)
);
SET @share_card_count = IF(
  @source_user_id IS NULL,
  0,
  (SELECT COUNT(*) FROM user_share_card WHERE deleted = 0 AND user_id = @source_user_id)
);
""".strip()


def build_precheck_sql(context: Context) -> str:
    return build_candidate_temp_sql(context) + """

SELECT CONCAT('TARGET_PHONE_MASK=', @target_phone_mask) AS marker;
SELECT CONCAT('SOURCE_CANDIDATE_COUNT=', @candidate_count) AS marker;
SELECT CONCAT('SOURCE_USER_ID=', IFNULL(@source_user_id, '')) AS marker;
SELECT CONCAT('SOURCE_OLD_PHONE_MASK=', @source_old_phone_mask) AS marker;
SELECT CONCAT('TARGET_PHONE_OTHER_USER_COUNT=', @target_other_user_count) AS marker;
SELECT CONCAT('ACTIVE_ACTOR_PROFILE_COUNT=', @active_actor_profile_count) AS marker;
SELECT CONCAT('USER_SHARE_CARD_COUNT=', @share_card_count) AS marker;

SELECT
  CONCAT(
    'CANDIDATE=',
    user_id,
    ',userName:', IFNULL(user_name, ''),
    ',nickName:', IFNULL(nick_name, ''),
    ',realName:', IFNULL(real_name, ''),
    ',userPhoneMask:', IFNULL(CONCAT(LEFT(user_phone, 3), '****', RIGHT(user_phone, 4)), ''),
    ',actorPhoneMask:', IFNULL(CONCAT(LEFT(actor_phone, 3), '****', RIGHT(actor_phone, 4)), '')
  ) AS marker
FROM kp_linxia_candidates
ORDER BY user_id
LIMIT 20;
""".strip() + "\n"


def build_diagnose_sql(context: Context) -> str:
    return build_candidate_temp_sql(context) + """

SELECT CONCAT('TARGET_PHONE_MASK=', @target_phone_mask) AS marker;
SELECT
  CONCAT(
    'TARGET_USER=',
    u.user_id,
    ',PHONE_MASK=', @target_phone_mask,
    ',USER_NAME=', IFNULL(u.user_name, ''),
    ',USER_TYPE=', IFNULL(u.user_type, ''),
    ',STATUS=', IFNULL(u.status, ''),
    ',DELETED=', IFNULL(u.deleted, ''),
    ',ACTOR_PROFILE_COUNT=', (
      SELECT COUNT(*) FROM actor_profile ap WHERE ap.deleted = 0 AND ap.user_id = u.user_id
    ),
    ',SHARE_CARD_COUNT=', (
      SELECT COUNT(*) FROM user_share_card card WHERE card.deleted = 0 AND card.user_id = u.user_id
    ),
    ',IDENTITY_COUNT=', (
      SELECT COUNT(*) FROM identity_verification iv WHERE iv.deleted = 0 AND iv.user_id = u.user_id
    ),
    ',INVITE_CODE_COUNT=', (
      SELECT COUNT(*) FROM invite_code ic WHERE ic.deleted = 0 AND ic.user_id = u.user_id
    ),
    ',CAPABILITY_COUNT=', (
      SELECT COUNT(*) FROM capability_account ca WHERE ca.deleted = 0 AND ca.user_id = u.user_id
    )
  ) AS marker
FROM `user` u
WHERE u.deleted = 0
  AND u.phone = @target_phone
ORDER BY u.user_id
LIMIT 20;

SELECT
  CONCAT(
    'LINXIA_LIKE_USER=',
    u.user_id,
    ',USER_NAME=', IFNULL(u.user_name, ''),
    ',NICK_NAME=', IFNULL(ap.nick_name, ''),
    ',REAL_NAME=', IFNULL(ap.real_name, ''),
    ',USER_PHONE_MASK=', IFNULL(CONCAT(LEFT(u.phone, 3), '****', RIGHT(u.phone, 4)), ''),
    ',ACTOR_PHONE_MASK=', IFNULL(CONCAT(LEFT(ap.phone, 3), '****', RIGHT(ap.phone, 4)), ''),
    ',SHARE_CARD_COUNT=', (
      SELECT COUNT(*) FROM user_share_card card WHERE card.deleted = 0 AND card.user_id = u.user_id
    )
  ) AS marker
FROM `user` u
JOIN actor_profile ap
  ON ap.user_id = u.user_id
 AND ap.deleted = 0
WHERE u.deleted = 0
  AND u.user_type = 1
  AND (
    u.user_name LIKE '%林夏%'
    OR ap.nick_name LIKE '%林夏%'
    OR ap.real_name LIKE '%林夏%'
  )
ORDER BY u.user_id
LIMIT 20;

SELECT CONCAT('SOURCE_CANDIDATE_COUNT=', @candidate_count) AS marker;
SELECT CONCAT('TARGET_PHONE_OTHER_USER_COUNT=', @target_other_user_count) AS marker;
""".strip() + "\n"


def build_inventory_sql(context: Context) -> str:
    return f"""
SET @target_phone = '{sql_string(context.target_phone)}';
SET @target_phone_mask = CONCAT(LEFT(@target_phone, 3), '****', RIGHT(@target_phone, 4));

SELECT CONCAT('TARGET_PHONE_MASK=', @target_phone_mask) AS marker;

SELECT
  CONCAT(
    'ACTOR_WITH_CARDS=',
    u.user_id,
    ',USER_NAME=', IFNULL(u.user_name, ''),
    ',NICK_NAME=', IFNULL(ap.nick_name, ''),
    ',REAL_NAME=', IFNULL(ap.real_name, ''),
    ',USER_PHONE_MASK=', IFNULL(CONCAT(LEFT(u.phone, 3), '****', RIGHT(u.phone, 4)), ''),
    ',ACTOR_PHONE_MASK=', IFNULL(CONCAT(LEFT(ap.phone, 3), '****', RIGHT(ap.phone, 4)), ''),
    ',ACTOR_PROFILE_ID=', IFNULL(ap.actor_profile_id, ''),
    ',SHARE_CARD_COUNT=', COUNT(card.share_card_id),
    ',LATEST_CARD_TIME=', IFNULL(DATE_FORMAT(MAX(card.last_update), '%Y-%m-%d %H:%i:%s'), ''),
    ',USER_CREATE_TIME=', IFNULL(DATE_FORMAT(u.create_time, '%Y-%m-%d %H:%i:%s'), '')
  ) AS marker
FROM `user` u
JOIN actor_profile ap
  ON ap.user_id = u.user_id
 AND ap.deleted = 0
JOIN user_share_card card
  ON card.user_id = u.user_id
 AND card.deleted = 0
WHERE u.deleted = 0
  AND u.user_type = 1
GROUP BY
  u.user_id,
  u.user_name,
  u.phone,
  ap.actor_profile_id,
  ap.nick_name,
  ap.real_name,
  ap.phone,
  u.create_time
ORDER BY COUNT(card.share_card_id) DESC, MAX(card.last_update) DESC
LIMIT 30;

SELECT
  CONCAT(
    'ACTOR_PROFILE=',
    u.user_id,
    ',USER_NAME=', IFNULL(u.user_name, ''),
    ',NICK_NAME=', IFNULL(ap.nick_name, ''),
    ',REAL_NAME=', IFNULL(ap.real_name, ''),
    ',USER_PHONE_MASK=', IFNULL(CONCAT(LEFT(u.phone, 3), '****', RIGHT(u.phone, 4)), ''),
    ',ACTOR_PHONE_MASK=', IFNULL(CONCAT(LEFT(ap.phone, 3), '****', RIGHT(ap.phone, 4)), ''),
    ',ACTOR_PROFILE_ID=', IFNULL(ap.actor_profile_id, ''),
    ',SHARE_CARD_COUNT=', (
      SELECT COUNT(*) FROM user_share_card card WHERE card.deleted = 0 AND card.user_id = u.user_id
    ),
    ',USER_CREATE_TIME=', IFNULL(DATE_FORMAT(u.create_time, '%Y-%m-%d %H:%i:%s'), '')
  ) AS marker
FROM `user` u
JOIN actor_profile ap
  ON ap.user_id = u.user_id
 AND ap.deleted = 0
WHERE u.deleted = 0
  AND u.user_type = 1
ORDER BY u.last_update DESC, u.user_id DESC
LIMIT 50;

SELECT
  CONCAT(
    'TARGET_USER=',
    u.user_id,
    ',PHONE_MASK=', @target_phone_mask,
    ',USER_NAME=', IFNULL(u.user_name, ''),
    ',USER_TYPE=', IFNULL(u.user_type, ''),
    ',ACTOR_PROFILE_COUNT=', (
      SELECT COUNT(*) FROM actor_profile ap WHERE ap.deleted = 0 AND ap.user_id = u.user_id
    ),
    ',SHARE_CARD_COUNT=', (
      SELECT COUNT(*) FROM user_share_card card WHERE card.deleted = 0 AND card.user_id = u.user_id
    )
  ) AS marker
FROM `user` u
WHERE u.deleted = 0
  AND u.phone = @target_phone
ORDER BY u.user_id
LIMIT 20;
""".strip() + "\n"


def build_roster_sql(context: Context) -> str:
    return f"""
SET @target_phone = '{sql_string(context.target_phone)}';
SET @target_phone_mask = CONCAT(LEFT(@target_phone, 3), '****', RIGHT(@target_phone, 4));

SELECT CONCAT('TARGET_PHONE_MASK=', @target_phone_mask) AS marker;
SELECT CONCAT('USER_TOTAL=', COUNT(*)) AS marker FROM `user` WHERE deleted = 0;
SELECT CONCAT('ACTOR_USER_TOTAL=', COUNT(*)) AS marker FROM `user` WHERE deleted = 0 AND user_type = 1;
SELECT CONCAT('ACTOR_PROFILE_TOTAL=', COUNT(*)) AS marker FROM actor_profile WHERE deleted = 0;
SELECT CONCAT('SHARE_CARD_TOTAL=', COUNT(*)) AS marker FROM user_share_card WHERE deleted = 0;

SELECT
  CONCAT(
    'USER_ROSTER=',
    u.user_id,
    ',PHONE_MASK=', IFNULL(CONCAT(LEFT(u.phone, 3), '****', RIGHT(u.phone, 4)), ''),
    ',USER_NAME=', IFNULL(u.user_name, ''),
    ',USER_TYPE=', IFNULL(u.user_type, ''),
    ',STATUS=', IFNULL(u.status, ''),
    ',ACTOR_PROFILE_COUNT=', (
      SELECT COUNT(*) FROM actor_profile ap WHERE ap.deleted = 0 AND ap.user_id = u.user_id
    ),
    ',SHARE_CARD_COUNT=', (
      SELECT COUNT(*) FROM user_share_card card WHERE card.deleted = 0 AND card.user_id = u.user_id
    ),
    ',USER_CREATE_TIME=', IFNULL(DATE_FORMAT(u.create_time, '%Y-%m-%d %H:%i:%s'), '')
  ) AS marker
FROM `user` u
WHERE u.deleted = 0
ORDER BY u.user_id DESC
LIMIT 50;
""".strip() + "\n"


def build_migration_common_sql(context: Context) -> str:
    source_db = sql_identifier(context.source_database)
    target_db = sql_identifier(context.mysql_database)
    source_user_id = migration_source_user_id(context)
    return f"""
SET @target_phone = '{sql_string(context.target_phone)}';
SET @target_phone_mask = CONCAT(LEFT(@target_phone, 3), '****', RIGHT(@target_phone, 4));
SET @source_user_id = {source_user_id};
SET @source_actor_profile_id = (
  SELECT MIN(actor_profile_id)
  FROM `{source_db}`.`actor_profile`
  WHERE deleted = 0
    AND user_id = @source_user_id
);
DROP TEMPORARY TABLE IF EXISTS kp_194_source_share_cards;
CREATE TEMPORARY TABLE kp_194_source_share_cards AS
SELECT share_card_id
FROM `{source_db}`.`user_share_card`
WHERE deleted = 0
  AND user_id = @source_user_id;

SET @source_user_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`user`
  WHERE deleted = 0
    AND user_id = @source_user_id
    AND phone = @target_phone
    AND user_type = 1
);
SET @source_linxia_name_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`user` u
  JOIN `{source_db}`.`actor_profile` ap
    ON ap.user_id = u.user_id
   AND ap.deleted = 0
  WHERE u.deleted = 0
    AND u.user_id = @source_user_id
    AND (
      u.user_name = '林夏'
      OR ap.nick_name = '林夏'
      OR ap.real_name = '林夏'
    )
);
SET @source_actor_profile_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`actor_profile`
  WHERE deleted = 0
    AND user_id = @source_user_id
);
SET @source_share_card_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`user_share_card`
  WHERE deleted = 0
    AND user_id = @source_user_id
);
SET @source_actor_config_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`actor_card_config`
  WHERE deleted = 0
    AND share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)
);
SET @source_share_preference_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`actor_share_preference`
  WHERE deleted = 0
    AND share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)
);
SET @source_identity_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`identity_verification`
  WHERE deleted = 0
    AND user_id = @source_user_id
);
SET @source_identity_owner_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`identity_verification_owner`
  WHERE deleted = 0
    AND user_id = @source_user_id
);
SET @source_invite_code_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`invite_code`
  WHERE deleted = 0
    AND user_id = @source_user_id
);
SET @source_referral_record_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`referral_record`
  WHERE deleted = 0
    AND (inviter_user_id = @source_user_id OR invitee_user_id = @source_user_id)
);
SET @source_capability_account_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`capability_account`
  WHERE deleted = 0
    AND user_id = @source_user_id
);
SET @source_capability_change_log_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`capability_change_log`
  WHERE deleted = 0
    AND user_id = @source_user_id
);
SET @source_user_entitlement_grant_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`user_entitlement_grant`
  WHERE deleted = 0
    AND user_id = @source_user_id
);
SET @source_ai_task_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`actor_ai_profile_card_task`
  WHERE deleted = 0
    AND user_id = @source_user_id
);
SET @source_ai_page_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`actor_ai_profile_card_page`
  WHERE deleted = 0
    AND (
      share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)
      OR task_id IN (
        SELECT task_id
        FROM `{source_db}`.`actor_ai_profile_card_task`
        WHERE deleted = 0
          AND user_id = @source_user_id
      )
    )
);
SET @source_contact_request_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`share_card_contact_request`
  WHERE deleted = 0
    AND share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)
);
SET @source_view_history_count = (
  SELECT COUNT(*)
  FROM `{source_db}`.`share_card_view_history`
  WHERE deleted = 0
    AND share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)
);

SET @target_phone_user_count = (
  SELECT COUNT(*)
  FROM `{target_db}`.`user`
  WHERE deleted = 0
    AND phone = @target_phone
);
SET @target_empty_user_id = (
  SELECT MIN(user_id)
  FROM `{target_db}`.`user`
  WHERE deleted = 0
    AND phone = @target_phone
);
SET @target_empty_user_asset_count = IF(
  @target_empty_user_id IS NULL,
  0,
  (
    SELECT
      (SELECT COUNT(*) FROM `{target_db}`.`actor_profile` WHERE deleted = 0 AND user_id = @target_empty_user_id)
      + (SELECT COUNT(*) FROM `{target_db}`.`user_share_card` WHERE deleted = 0 AND user_id = @target_empty_user_id)
      + (SELECT COUNT(*) FROM `{target_db}`.`identity_verification` WHERE deleted = 0 AND user_id = @target_empty_user_id)
      + (SELECT COUNT(*) FROM `{target_db}`.`invite_code` WHERE deleted = 0 AND user_id = @target_empty_user_id)
      + (SELECT COUNT(*) FROM `{target_db}`.`capability_account` WHERE deleted = 0 AND user_id = @target_empty_user_id)
      + (SELECT COUNT(*) FROM `{target_db}`.`user_entitlement_grant` WHERE deleted = 0 AND user_id = @target_empty_user_id)
  )
);
SET @target_source_user_pk_count = (
  SELECT COUNT(*)
  FROM `{target_db}`.`user`
  WHERE user_id = @source_user_id
);
SET @target_source_actor_pk_count = (
  SELECT COUNT(*)
  FROM `{target_db}`.`actor_profile`
  WHERE actor_profile_id = @source_actor_profile_id
);
SET @target_source_share_card_pk_count = (
  SELECT COUNT(*)
  FROM `{target_db}`.`user_share_card`
  WHERE share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)
);
SET @target_source_identity_pk_count = (
  SELECT COUNT(*)
  FROM `{target_db}`.`identity_verification` target_iv
  JOIN `{source_db}`.`identity_verification` source_iv
    ON source_iv.verification_id = target_iv.verification_id
  WHERE source_iv.deleted = 0
    AND source_iv.user_id = @source_user_id
);
SET @target_source_invite_code_pk_count = (
  SELECT COUNT(*)
  FROM `{target_db}`.`invite_code` target_ic
  JOIN `{source_db}`.`invite_code` source_ic
    ON source_ic.invite_code_id = target_ic.invite_code_id
  WHERE source_ic.deleted = 0
    AND source_ic.user_id = @source_user_id
);
SET @target_source_capability_pk_count = (
  SELECT COUNT(*)
  FROM `{target_db}`.`capability_account` target_ca
  JOIN `{source_db}`.`capability_account` source_ca
    ON source_ca.capability_id = target_ca.capability_id
  WHERE source_ca.deleted = 0
    AND source_ca.user_id = @source_user_id
);
SET @target_phone_other_after_count = (
  SELECT COUNT(*)
  FROM `{target_db}`.`user`
  WHERE deleted = 0
    AND phone = @target_phone
    AND user_id <> @source_user_id
);
""".strip()


def build_migration_marker_sql() -> str:
    return """
SELECT CONCAT('TARGET_PHONE_MASK=', @target_phone_mask) AS marker;
SELECT CONCAT('SOURCE_USER_ID=', @source_user_id) AS marker;
SELECT CONCAT('SOURCE_ACTOR_PROFILE_ID=', IFNULL(@source_actor_profile_id, '')) AS marker;
SELECT CONCAT('SOURCE_USER_COUNT=', @source_user_count) AS marker;
SELECT CONCAT('SOURCE_LINXIA_NAME_COUNT=', @source_linxia_name_count) AS marker;
SELECT CONCAT('SOURCE_ACTOR_PROFILE_COUNT=', @source_actor_profile_count) AS marker;
SELECT CONCAT('SOURCE_SHARE_CARD_COUNT=', @source_share_card_count) AS marker;
SELECT CONCAT('SOURCE_ACTOR_CONFIG_COUNT=', @source_actor_config_count) AS marker;
SELECT CONCAT('SOURCE_SHARE_PREFERENCE_COUNT=', @source_share_preference_count) AS marker;
SELECT CONCAT('SOURCE_IDENTITY_COUNT=', @source_identity_count) AS marker;
SELECT CONCAT('SOURCE_IDENTITY_OWNER_COUNT=', @source_identity_owner_count) AS marker;
SELECT CONCAT('SOURCE_INVITE_CODE_COUNT=', @source_invite_code_count) AS marker;
SELECT CONCAT('SOURCE_REFERRAL_RECORD_COUNT=', @source_referral_record_count) AS marker;
SELECT CONCAT('SOURCE_CAPABILITY_ACCOUNT_COUNT=', @source_capability_account_count) AS marker;
SELECT CONCAT('SOURCE_CAPABILITY_CHANGE_LOG_COUNT=', @source_capability_change_log_count) AS marker;
SELECT CONCAT('SOURCE_USER_ENTITLEMENT_GRANT_COUNT=', @source_user_entitlement_grant_count) AS marker;
SELECT CONCAT('SOURCE_AI_TASK_COUNT=', @source_ai_task_count) AS marker;
SELECT CONCAT('SOURCE_AI_PAGE_COUNT=', @source_ai_page_count) AS marker;
SELECT CONCAT('SOURCE_CONTACT_REQUEST_COUNT=', @source_contact_request_count) AS marker;
SELECT CONCAT('SOURCE_VIEW_HISTORY_COUNT=', @source_view_history_count) AS marker;
SELECT CONCAT('TARGET_PHONE_USER_COUNT=', @target_phone_user_count) AS marker;
SELECT CONCAT('TARGET_EMPTY_USER_ID=', IFNULL(@target_empty_user_id, '')) AS marker;
SELECT CONCAT('TARGET_EMPTY_USER_ASSET_COUNT=', @target_empty_user_asset_count) AS marker;
SELECT CONCAT('TARGET_SOURCE_USER_PK_COUNT=', @target_source_user_pk_count) AS marker;
SELECT CONCAT('TARGET_SOURCE_ACTOR_PK_COUNT=', @target_source_actor_pk_count) AS marker;
SELECT CONCAT('TARGET_SOURCE_SHARE_CARD_PK_COUNT=', @target_source_share_card_pk_count) AS marker;
SELECT CONCAT('TARGET_SOURCE_IDENTITY_PK_COUNT=', @target_source_identity_pk_count) AS marker;
SELECT CONCAT('TARGET_SOURCE_INVITE_CODE_PK_COUNT=', @target_source_invite_code_pk_count) AS marker;
SELECT CONCAT('TARGET_SOURCE_CAPABILITY_PK_COUNT=', @target_source_capability_pk_count) AS marker;
SELECT CONCAT('TARGET_PHONE_OTHER_AFTER_COUNT=', @target_phone_other_after_count) AS marker;
""".strip()


def build_common_column_insert_procedure_sql() -> str:
    return """
DROP PROCEDURE IF EXISTS kp_194_insert_common_columns;
DELIMITER //
CREATE PROCEDURE kp_194_insert_common_columns(
  IN p_target_db VARCHAR(64),
  IN p_source_db VARCHAR(64),
  IN p_table_name VARCHAR(64),
  IN p_where_clause TEXT,
  OUT p_affected_rows INT
)
BEGIN
  SET @kp_194_columns = NULL;
  SELECT GROUP_CONCAT(CONCAT('`', target_cols.COLUMN_NAME, '`') ORDER BY target_cols.ORDINAL_POSITION SEPARATOR ', ')
    INTO @kp_194_columns
  FROM information_schema.COLUMNS target_cols
  JOIN information_schema.COLUMNS source_cols
    ON source_cols.TABLE_SCHEMA = p_source_db
   AND source_cols.TABLE_NAME = p_table_name
   AND source_cols.COLUMN_NAME = target_cols.COLUMN_NAME
  WHERE target_cols.TABLE_SCHEMA = p_target_db
    AND target_cols.TABLE_NAME = p_table_name;

  IF @kp_194_columns IS NULL OR @kp_194_columns = '' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'no common columns for migration insert';
  END IF;

  SET @kp_194_sql = CONCAT(
    'INSERT INTO `', p_target_db, '`.`', p_table_name, '` (', @kp_194_columns, ') ',
    'SELECT ', @kp_194_columns, ' FROM `', p_source_db, '`.`', p_table_name, '` ',
    p_where_clause
  );
  PREPARE kp_194_stmt FROM @kp_194_sql;
  EXECUTE kp_194_stmt;
  SET p_affected_rows = ROW_COUNT();
  DEALLOCATE PREPARE kp_194_stmt;
END//
DELIMITER ;
""".strip()


def build_cleanup_sql() -> str:
    return """
DROP PROCEDURE IF EXISTS kp_194_insert_common_columns;
SELECT 'MIGRATION_HELPER_PROCEDURE_DROPPED=1' AS marker;
""".strip() + "\n"


def build_migration_precheck_sql(context: Context) -> str:
    return build_migration_common_sql(context) + "\n\n" + build_migration_marker_sql() + "\n"


def build_migration_apply_sql(context: Context) -> tuple[str, list[str]]:
    source_db = sql_identifier(context.source_database)
    target_db = sql_identifier(context.mysql_database)
    suffix = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    backup_aliases = {
        "user": "usr",
        "actor_profile": "ap",
        "user_share_card": "usc",
        "actor_card_config": "acc",
        "actor_share_preference": "asp",
        "identity_verification": "iv",
        "identity_verification_owner": "ivo",
        "invite_code": "ic",
        "referral_record": "rr",
        "capability_account": "ca",
        "capability_change_log": "ccl",
        "user_entitlement_grant": "ueg",
        "actor_ai_profile_card_task": "aipct",
        "actor_ai_profile_card_page": "aipcp",
        "share_card_contact_request": "sccr",
        "share_card_view_history": "scvh",
    }
    backups = {table: f"zz194_{alias}_{suffix}" for table, alias in backup_aliases.items()}

    create_backups_sql = "\n".join(
        f"CREATE TABLE IF NOT EXISTS `{target_db}`.`{backup}` LIKE `{target_db}`.`{table}`;"
        for table, backup in backups.items()
    )

    sql = build_migration_common_sql(context) + "\n\n" + build_common_column_insert_procedure_sql() + f"""

SET @guard_error = NULL;
SET @guard_error = IF(@source_user_count <> 1, CONCAT('source user count must be 1, got ', @source_user_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @source_linxia_name_count <> 1, CONCAT('source linxia name count must be 1, got ', @source_linxia_name_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @source_actor_profile_count <> 1, CONCAT('source actor profile count must be 1, got ', @source_actor_profile_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @source_share_card_count < 1, CONCAT('source share card count must be >= 1, got ', @source_share_card_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @target_phone_user_count <> 1, CONCAT('target phone user count must be 1 empty shell, got ', @target_phone_user_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @target_empty_user_asset_count <> 0, CONCAT('target empty user asset count must be 0, got ', @target_empty_user_asset_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @target_source_user_pk_count <> 0, CONCAT('target source user pk count must be 0, got ', @target_source_user_pk_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @target_source_actor_pk_count <> 0, CONCAT('target source actor pk count must be 0, got ', @target_source_actor_pk_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @target_source_share_card_pk_count <> 0, CONCAT('target source share card pk count must be 0, got ', @target_source_share_card_pk_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @target_source_identity_pk_count <> 0, CONCAT('target source identity pk count must be 0, got ', @target_source_identity_pk_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @target_source_invite_code_pk_count <> 0, CONCAT('target source invite code pk count must be 0, got ', @target_source_invite_code_pk_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @target_source_capability_pk_count <> 0, CONCAT('target source capability pk count must be 0, got ', @target_source_capability_pk_count), @guard_error);

SET @signal_sql = IF(@guard_error IS NULL, 'DO 0', CONCAT('SIGNAL SQLSTATE ''45000'' SET MESSAGE_TEXT = ''', REPLACE(@guard_error, '''', ''''''), ''''));
PREPARE guard_stmt FROM @signal_sql;
EXECUTE guard_stmt;
DEALLOCATE PREPARE guard_stmt;

{create_backups_sql}

START TRANSACTION;

INSERT INTO `{target_db}`.`{backups["user"]}`
SELECT * FROM `{target_db}`.`user`
WHERE user_id = @target_empty_user_id OR user_id = @source_user_id;

INSERT INTO `{target_db}`.`{backups["actor_profile"]}`
SELECT * FROM `{target_db}`.`actor_profile`
WHERE user_id IN (@target_empty_user_id, @source_user_id)
   OR actor_profile_id = @source_actor_profile_id;

INSERT INTO `{target_db}`.`{backups["user_share_card"]}`
SELECT * FROM `{target_db}`.`user_share_card`
WHERE user_id IN (@target_empty_user_id, @source_user_id)
   OR share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards);

INSERT INTO `{target_db}`.`{backups["actor_card_config"]}`
SELECT * FROM `{target_db}`.`actor_card_config`
WHERE share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards);

INSERT INTO `{target_db}`.`{backups["actor_share_preference"]}`
SELECT * FROM `{target_db}`.`actor_share_preference`
WHERE share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards);

INSERT INTO `{target_db}`.`{backups["identity_verification"]}`
SELECT * FROM `{target_db}`.`identity_verification`
WHERE user_id IN (@target_empty_user_id, @source_user_id);

INSERT INTO `{target_db}`.`{backups["identity_verification_owner"]}`
SELECT * FROM `{target_db}`.`identity_verification_owner`
WHERE user_id IN (@target_empty_user_id, @source_user_id);

INSERT INTO `{target_db}`.`{backups["invite_code"]}`
SELECT * FROM `{target_db}`.`invite_code`
WHERE user_id IN (@target_empty_user_id, @source_user_id);

INSERT INTO `{target_db}`.`{backups["referral_record"]}`
SELECT * FROM `{target_db}`.`referral_record`
WHERE inviter_user_id IN (@target_empty_user_id, @source_user_id)
   OR invitee_user_id IN (@target_empty_user_id, @source_user_id);

INSERT INTO `{target_db}`.`{backups["capability_account"]}`
SELECT * FROM `{target_db}`.`capability_account`
WHERE user_id IN (@target_empty_user_id, @source_user_id);

INSERT INTO `{target_db}`.`{backups["capability_change_log"]}`
SELECT * FROM `{target_db}`.`capability_change_log`
WHERE user_id IN (@target_empty_user_id, @source_user_id);

INSERT INTO `{target_db}`.`{backups["user_entitlement_grant"]}`
SELECT * FROM `{target_db}`.`user_entitlement_grant`
WHERE user_id IN (@target_empty_user_id, @source_user_id);

INSERT INTO `{target_db}`.`{backups["actor_ai_profile_card_task"]}`
SELECT * FROM `{target_db}`.`actor_ai_profile_card_task`
WHERE user_id IN (@target_empty_user_id, @source_user_id)
   OR share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)
   OR actor_profile_id = @source_actor_profile_id;

INSERT INTO `{target_db}`.`{backups["actor_ai_profile_card_page"]}`
SELECT * FROM `{target_db}`.`actor_ai_profile_card_page`
WHERE share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)
   OR task_id IN (
      SELECT task_id FROM `{source_db}`.`actor_ai_profile_card_task`
      WHERE deleted = 0 AND user_id = @source_user_id
   );

INSERT INTO `{target_db}`.`{backups["share_card_contact_request"]}`
SELECT * FROM `{target_db}`.`share_card_contact_request`
WHERE share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)
   OR viewer_user_id IN (@target_empty_user_id, @source_user_id);

INSERT INTO `{target_db}`.`{backups["share_card_view_history"]}`
SELECT * FROM `{target_db}`.`share_card_view_history`
WHERE share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)
   OR viewer_user_id IN (@target_empty_user_id, @source_user_id);

UPDATE `{target_db}`.`user`
SET
  deleted = 1,
  phone = CONCAT('archived-00-194-', user_id, '-', @target_phone),
  account = CONCAT('archived-00-194-', user_id, '-', @target_phone),
  update_user_name = '00-194-linxia-migration',
  last_update = NOW()
WHERE user_id = @target_empty_user_id
  AND deleted = 0
  AND user_id <> @source_user_id;
SET @archived_target_user_rows = ROW_COUNT();

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'user', CONCAT('WHERE user_id = ', @source_user_id, ' AND deleted = 0'), @inserted_user_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'actor_profile', CONCAT('WHERE deleted = 0 AND user_id = ', @source_user_id), @inserted_actor_profile_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'user_share_card', CONCAT('WHERE deleted = 0 AND user_id = ', @source_user_id), @inserted_share_card_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'actor_card_config', CONCAT('WHERE deleted = 0 AND share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)'), @inserted_actor_config_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'actor_share_preference', CONCAT('WHERE deleted = 0 AND share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)'), @inserted_share_preference_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'identity_verification', CONCAT('WHERE deleted = 0 AND user_id = ', @source_user_id), @inserted_identity_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'identity_verification_owner', CONCAT('WHERE deleted = 0 AND user_id = ', @source_user_id), @inserted_identity_owner_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'invite_code', CONCAT('WHERE deleted = 0 AND user_id = ', @source_user_id), @inserted_invite_code_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'referral_record', CONCAT('WHERE deleted = 0 AND (inviter_user_id = ', @source_user_id, ' OR invitee_user_id = ', @source_user_id, ')'), @inserted_referral_record_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'capability_account', CONCAT('WHERE deleted = 0 AND user_id = ', @source_user_id), @inserted_capability_account_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'capability_change_log', CONCAT('WHERE deleted = 0 AND user_id = ', @source_user_id), @inserted_capability_change_log_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'user_entitlement_grant', CONCAT('WHERE deleted = 0 AND user_id = ', @source_user_id), @inserted_user_entitlement_grant_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'actor_ai_profile_card_task', CONCAT('WHERE deleted = 0 AND user_id = ', @source_user_id), @inserted_ai_task_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'actor_ai_profile_card_page', CONCAT(
  'WHERE deleted = 0 AND (share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards) OR task_id IN (SELECT task_id FROM `{source_db}`.`actor_ai_profile_card_task` WHERE deleted = 0 AND user_id = ',
  @source_user_id,
  '))'
), @inserted_ai_page_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'share_card_contact_request', CONCAT('WHERE deleted = 0 AND share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)'), @inserted_contact_request_rows);

CALL kp_194_insert_common_columns('{target_db}', '{source_db}', 'share_card_view_history', CONCAT('WHERE deleted = 0 AND share_card_id IN (SELECT share_card_id FROM kp_194_source_share_cards)'), @inserted_view_history_rows);

SET @post_target_phone_user_count = (
  SELECT COUNT(*)
  FROM `{target_db}`.`user`
  WHERE deleted = 0
    AND phone = @target_phone
);
SET @post_source_actor_profile_count = (
  SELECT COUNT(*)
  FROM `{target_db}`.`actor_profile`
  WHERE deleted = 0
    AND user_id = @source_user_id
);
SET @post_source_share_card_count = (
  SELECT COUNT(*)
  FROM `{target_db}`.`user_share_card`
  WHERE deleted = 0
    AND user_id = @source_user_id
);

SET @post_guard_error = NULL;
SET @post_guard_error = IF(@archived_target_user_rows <> 1, CONCAT('archived target user rows must be 1, got ', @archived_target_user_rows), @post_guard_error);
SET @post_guard_error = IF(@post_guard_error IS NULL AND @inserted_user_rows <> 1, CONCAT('inserted user rows must be 1, got ', @inserted_user_rows), @post_guard_error);
SET @post_guard_error = IF(@post_guard_error IS NULL AND @inserted_actor_profile_rows <> @source_actor_profile_count, CONCAT('inserted actor profile rows mismatch ', @inserted_actor_profile_rows, '/', @source_actor_profile_count), @post_guard_error);
SET @post_guard_error = IF(@post_guard_error IS NULL AND @inserted_share_card_rows <> @source_share_card_count, CONCAT('inserted share card rows mismatch ', @inserted_share_card_rows, '/', @source_share_card_count), @post_guard_error);
SET @post_guard_error = IF(@post_guard_error IS NULL AND @post_target_phone_user_count <> 1, CONCAT('post target phone user count must be 1, got ', @post_target_phone_user_count), @post_guard_error);
SET @post_guard_error = IF(@post_guard_error IS NULL AND @post_source_actor_profile_count <> @source_actor_profile_count, CONCAT('post actor profile count mismatch ', @post_source_actor_profile_count, '/', @source_actor_profile_count), @post_guard_error);
SET @post_guard_error = IF(@post_guard_error IS NULL AND @post_source_share_card_count <> @source_share_card_count, CONCAT('post share card count mismatch ', @post_source_share_card_count, '/', @source_share_card_count), @post_guard_error);

SET @signal_sql = IF(@post_guard_error IS NULL, 'DO 0', CONCAT('SIGNAL SQLSTATE ''45000'' SET MESSAGE_TEXT = ''', REPLACE(@post_guard_error, '''', ''''''), ''''));
PREPARE post_guard_stmt FROM @signal_sql;
EXECUTE post_guard_stmt;
DEALLOCATE PREPARE post_guard_stmt;

COMMIT;

{build_migration_marker_sql()}
SELECT CONCAT('ARCHIVED_TARGET_USER_ROWS=', @archived_target_user_rows) AS marker;
SELECT CONCAT('INSERTED_USER_ROWS=', @inserted_user_rows) AS marker;
SELECT CONCAT('INSERTED_ACTOR_PROFILE_ROWS=', @inserted_actor_profile_rows) AS marker;
SELECT CONCAT('INSERTED_SHARE_CARD_ROWS=', @inserted_share_card_rows) AS marker;
SELECT CONCAT('INSERTED_ACTOR_CONFIG_ROWS=', @inserted_actor_config_rows) AS marker;
SELECT CONCAT('INSERTED_SHARE_PREFERENCE_ROWS=', @inserted_share_preference_rows) AS marker;
SELECT CONCAT('INSERTED_IDENTITY_ROWS=', @inserted_identity_rows) AS marker;
SELECT CONCAT('INSERTED_IDENTITY_OWNER_ROWS=', @inserted_identity_owner_rows) AS marker;
SELECT CONCAT('INSERTED_INVITE_CODE_ROWS=', @inserted_invite_code_rows) AS marker;
SELECT CONCAT('INSERTED_REFERRAL_RECORD_ROWS=', @inserted_referral_record_rows) AS marker;
SELECT CONCAT('INSERTED_CAPABILITY_ACCOUNT_ROWS=', @inserted_capability_account_rows) AS marker;
SELECT CONCAT('INSERTED_CAPABILITY_CHANGE_LOG_ROWS=', @inserted_capability_change_log_rows) AS marker;
SELECT CONCAT('INSERTED_USER_ENTITLEMENT_GRANT_ROWS=', @inserted_user_entitlement_grant_rows) AS marker;
SELECT CONCAT('INSERTED_AI_TASK_ROWS=', @inserted_ai_task_rows) AS marker;
SELECT CONCAT('INSERTED_AI_PAGE_ROWS=', @inserted_ai_page_rows) AS marker;
SELECT CONCAT('INSERTED_CONTACT_REQUEST_ROWS=', @inserted_contact_request_rows) AS marker;
SELECT CONCAT('INSERTED_VIEW_HISTORY_ROWS=', @inserted_view_history_rows) AS marker;
SELECT CONCAT('POST_TARGET_PHONE_USER_COUNT=', @post_target_phone_user_count) AS marker;
SELECT CONCAT('POST_SOURCE_ACTOR_PROFILE_COUNT=', @post_source_actor_profile_count) AS marker;
SELECT CONCAT('POST_SOURCE_SHARE_CARD_COUNT=', @post_source_share_card_count) AS marker;
SELECT CONCAT('BACKUP_TABLE_PREFIX=zz194_') AS marker;
""".strip() + "\n"
    return sql, list(backups.values())


def build_apply_sql(context: Context) -> tuple[str, str, str]:
    suffix = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    user_backup = f"zz_bak_194_linxia_user_{suffix}"
    actor_backup = f"zz_bak_194_linxia_actor_{suffix}"

    sql = build_candidate_temp_sql(context) + f"""

SET @guard_error = NULL;
SET @guard_error = IF(@candidate_count <> 1, CONCAT('source candidate count must be 1, got ', @candidate_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @target_other_user_count <> 0, CONCAT('target phone is used by other user count ', @target_other_user_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @active_actor_profile_count <> 1, CONCAT('active actor profile count must be 1, got ', @active_actor_profile_count), @guard_error);
SET @guard_error = IF(@guard_error IS NULL AND @source_user_id IS NULL, 'source user id is null', @guard_error);

SET @signal_sql = IF(@guard_error IS NULL, 'DO 0', CONCAT('SIGNAL SQLSTATE ''45000'' SET MESSAGE_TEXT = ''', REPLACE(@guard_error, '''', ''''''), ''''));
PREPARE guard_stmt FROM @signal_sql;
EXECUTE guard_stmt;
DEALLOCATE PREPARE guard_stmt;

CREATE TABLE IF NOT EXISTS `{user_backup}` LIKE `user`;
CREATE TABLE IF NOT EXISTS `{actor_backup}` LIKE `actor_profile`;

START TRANSACTION;

INSERT INTO `{user_backup}`
SELECT *
FROM `user`
WHERE user_id = @source_user_id
   OR phone = @target_phone;

INSERT INTO `{actor_backup}`
SELECT *
FROM `actor_profile`
WHERE deleted = 0
  AND user_id = @source_user_id;

SET @user_backup_count = (SELECT COUNT(*) FROM `{user_backup}`);
SET @actor_backup_count = (SELECT COUNT(*) FROM `{actor_backup}`);
SET @backup_guard_error = NULL;
SET @backup_guard_error = IF(@user_backup_count < 1, 'user backup is empty', @backup_guard_error);
SET @backup_guard_error = IF(@backup_guard_error IS NULL AND @actor_backup_count <> 1, CONCAT('actor backup count must be 1, got ', @actor_backup_count), @backup_guard_error);

SET @signal_sql = IF(@backup_guard_error IS NULL, 'DO 0', CONCAT('SIGNAL SQLSTATE ''45000'' SET MESSAGE_TEXT = ''', REPLACE(@backup_guard_error, '''', ''''''), ''''));
PREPARE backup_guard_stmt FROM @signal_sql;
EXECUTE backup_guard_stmt;
DEALLOCATE PREPARE backup_guard_stmt;

UPDATE `user`
SET
  phone = @target_phone,
  account = CASE
    WHEN account IS NULL OR account = '' OR account = @source_old_phone THEN @target_phone
    ELSE account
  END,
  update_user_name = '00-194-phone-binding',
  last_update = NOW()
WHERE user_id = @source_user_id
  AND deleted = 0;
SET @updated_user_rows = ROW_COUNT();

UPDATE `actor_profile`
SET
  phone = @target_phone,
  update_user_name = '00-194-phone-binding',
  last_update = NOW()
WHERE user_id = @source_user_id
  AND deleted = 0;
SET @updated_actor_rows = ROW_COUNT();

COMMIT;

SELECT CONCAT('TARGET_PHONE_MASK=', @target_phone_mask) AS marker;
SELECT CONCAT('SOURCE_USER_ID=', @source_user_id) AS marker;
SELECT CONCAT('SOURCE_OLD_PHONE_MASK=', @source_old_phone_mask) AS marker;
SELECT CONCAT('USER_BACKUP_TABLE={user_backup}') AS marker;
SELECT CONCAT('ACTOR_BACKUP_TABLE={actor_backup}') AS marker;
SELECT CONCAT('USER_BACKUP_COUNT=', @user_backup_count) AS marker;
SELECT CONCAT('ACTOR_BACKUP_COUNT=', @actor_backup_count) AS marker;
SELECT CONCAT('UPDATED_USER_ROWS=', @updated_user_rows) AS marker;
SELECT CONCAT('UPDATED_ACTOR_PROFILE_ROWS=', @updated_actor_rows) AS marker;
SELECT CONCAT('USER_SHARE_CARD_COUNT=', @share_card_count) AS marker;
""".strip() + "\n"
    return sql, user_backup, actor_backup


def validate_precheck_markers(markers: dict[str, str]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if markers.get("SOURCE_CANDIDATE_COUNT") != "1":
        errors.append(f"SOURCE_CANDIDATE_COUNT expected 1, got {markers.get('SOURCE_CANDIDATE_COUNT', '')}")
    if not markers.get("SOURCE_USER_ID"):
        errors.append("SOURCE_USER_ID is empty")
    if markers.get("TARGET_PHONE_OTHER_USER_COUNT") != "0":
        errors.append(
            "TARGET_PHONE_OTHER_USER_COUNT expected 0, "
            f"got {markers.get('TARGET_PHONE_OTHER_USER_COUNT', '')}"
        )
    if markers.get("ACTIVE_ACTOR_PROFILE_COUNT") != "1":
        errors.append(
            "ACTIVE_ACTOR_PROFILE_COUNT expected 1, "
            f"got {markers.get('ACTIVE_ACTOR_PROFILE_COUNT', '')}"
        )
    return not errors, errors


def redact_output(value: str, target_phone: str) -> str:
    return value.replace(target_phone, mask_phone(target_phone))


def write_summary(context: Context, helper_summary: dict[str, str], markers: dict[str, str], status: str, errors: list[str]) -> Path:
    context.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = context.output_dir / "summary.md"
    raw_path = context.output_dir / "mysql-result-redacted.txt"
    raw_path.write_text(redact_output(helper_summary.get("MYSQL_RESULT", ""), context.target_phone) + "\n", encoding="utf-8")

    marker_lines = "\n".join(f"- `{key}`: `{value}`" for key, value in sorted(markers.items()))
    error_lines = "\n".join(f"- {item}" for item in errors) if errors else "- 无"
    content = f"""# 00-194 Phone Binding Run

## 基本信息

- run id: `{context.run_id}`
- mode: `{context.mode}`
- status: `{status}`
- operator: `{context.operator}`
- mysql database: `{context.mysql_database}`
- mysql container: `{context.mysql_container}`
- target phone: `{mask_phone(context.target_phone)}`
- source user override: `{context.source_user_id or ''}`
- remote date: `{helper_summary.get("REMOTE_DATE", "")}`

## Markers

{marker_lines}

## Errors

{error_lines}

## Raw Result

- redacted mysql result: `mysql-result-redacted.txt`
"""
    summary_path.write_text(content, encoding="utf-8")
    return summary_path


def execute_precheck(context: Context) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    helper_summary = upload_and_run_sql(
        context,
        build_precheck_sql(context),
        "--mysql-validation",
        "linxia-phone-binding-precheck",
    )
    markers = parse_markers(helper_summary["MYSQL_RESULT"])
    helper_errors = validate_helper_status(helper_summary)
    if helper_errors:
        return False, markers, helper_errors, helper_summary
    ok, errors = validate_precheck_markers(markers)
    return ok, markers, errors, helper_summary


def execute_diagnose(context: Context) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    helper_summary = upload_and_run_sql(
        context,
        build_diagnose_sql(context),
        "--mysql-validation",
        "linxia-phone-binding-diagnose",
    )
    markers = parse_markers(helper_summary["MYSQL_RESULT"])
    helper_errors = validate_helper_status(helper_summary)
    return not helper_errors, markers, helper_errors, helper_summary


def execute_inventory(context: Context) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    helper_summary = upload_and_run_sql(
        context,
        build_inventory_sql(context),
        "--mysql-validation",
        "linxia-phone-binding-inventory",
    )
    markers = parse_markers(helper_summary["MYSQL_RESULT"])
    helper_errors = validate_helper_status(helper_summary)
    return not helper_errors, markers, helper_errors, helper_summary


def execute_roster(context: Context) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    helper_summary = upload_and_run_sql(
        context,
        build_roster_sql(context),
        "--mysql-validation",
        "linxia-phone-binding-roster",
    )
    markers = parse_markers(helper_summary["MYSQL_RESULT"])
    helper_errors = validate_helper_status(helper_summary)
    return not helper_errors, markers, helper_errors, helper_summary


def validate_migration_precheck_markers(markers: dict[str, str]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    expected = {
        "SOURCE_USER_COUNT": "1",
        "SOURCE_LINXIA_NAME_COUNT": "1",
        "SOURCE_ACTOR_PROFILE_COUNT": "1",
        "TARGET_PHONE_USER_COUNT": "1",
        "TARGET_EMPTY_USER_ASSET_COUNT": "0",
        "TARGET_SOURCE_USER_PK_COUNT": "0",
        "TARGET_SOURCE_ACTOR_PK_COUNT": "0",
        "TARGET_SOURCE_SHARE_CARD_PK_COUNT": "0",
        "TARGET_SOURCE_IDENTITY_PK_COUNT": "0",
        "TARGET_SOURCE_INVITE_CODE_PK_COUNT": "0",
        "TARGET_SOURCE_CAPABILITY_PK_COUNT": "0",
    }
    for key, expected_value in expected.items():
        actual = markers.get(key, "")
        if actual != expected_value:
            errors.append(f"{key} expected {expected_value}, got {actual}")
    try:
        share_card_count = int(markers.get("SOURCE_SHARE_CARD_COUNT", "0"))
    except ValueError:
        share_card_count = 0
    if share_card_count < 1:
        errors.append(f"SOURCE_SHARE_CARD_COUNT expected >= 1, got {markers.get('SOURCE_SHARE_CARD_COUNT', '')}")
    if markers.get("SOURCE_USER_ID") != DEFAULT_MIGRATION_SOURCE_USER_ID and not markers.get("SOURCE_USER_ID"):
        errors.append("SOURCE_USER_ID is empty")
    return not errors, errors


def execute_migration_precheck(context: Context) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    helper_summary = upload_and_run_sql(
        context,
        build_migration_precheck_sql(context),
        "--mysql-validation",
        "linxia-account-migration-precheck",
    )
    markers = parse_markers(helper_summary["MYSQL_RESULT"])
    helper_errors = validate_helper_status(helper_summary)
    if helper_errors:
        return False, markers, helper_errors, helper_summary
    ok, errors = validate_migration_precheck_markers(markers)
    return ok, markers, errors, helper_summary


def execute_migration_apply(context: Context) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    precheck_ok, precheck_markers, precheck_errors, precheck_summary = execute_migration_precheck(context)
    write_summary(
        context,
        precheck_summary,
        precheck_markers,
        "migration-precheck-before-apply-passed" if precheck_ok else "blocked",
        precheck_errors,
    )
    if not precheck_ok:
        return False, precheck_markers, precheck_errors, precheck_summary

    apply_sql, _backup_tables = build_migration_apply_sql(context)
    helper_summary = upload_and_run_sql(
        context,
        apply_sql,
        "--mysql-apply",
        "linxia-account-migration-apply",
    )
    markers = parse_markers(helper_summary["MYSQL_RESULT"])
    errors: list[str] = validate_helper_status(helper_summary)
    if errors:
        return False, markers, errors, helper_summary
    expected_equal_markers = {
        "ARCHIVED_TARGET_USER_ROWS": "1",
        "INSERTED_USER_ROWS": "1",
        "POST_TARGET_PHONE_USER_COUNT": "1",
    }
    for key, expected_value in expected_equal_markers.items():
        if markers.get(key) != expected_value:
            errors.append(f"{key} expected {expected_value}, got {markers.get(key, '')}")
    if markers.get("INSERTED_ACTOR_PROFILE_ROWS") != markers.get("SOURCE_ACTOR_PROFILE_COUNT"):
        errors.append("INSERTED_ACTOR_PROFILE_ROWS does not match SOURCE_ACTOR_PROFILE_COUNT")
    if markers.get("INSERTED_SHARE_CARD_ROWS") != markers.get("SOURCE_SHARE_CARD_COUNT"):
        errors.append("INSERTED_SHARE_CARD_ROWS does not match SOURCE_SHARE_CARD_COUNT")
    if not markers.get("BACKUP_TABLE_PREFIX"):
        errors.append("backup table prefix marker is missing")
    return not errors, markers, errors, helper_summary


def execute_cleanup(context: Context) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    helper_summary = upload_and_run_sql(
        context,
        build_cleanup_sql(),
        "--mysql-apply",
        "linxia-account-migration-cleanup",
    )
    markers = parse_markers(helper_summary["MYSQL_RESULT"])
    errors: list[str] = validate_helper_status(helper_summary)
    if errors:
        return False, markers, errors, helper_summary
    if markers.get("MIGRATION_HELPER_PROCEDURE_DROPPED") != "1":
        errors.append("MIGRATION_HELPER_PROCEDURE_DROPPED marker is missing")
    return not errors, markers, errors, helper_summary


def execute_send_code(context: Context) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    response = api_request_json(context, "/api/auth/sendCode", {"phone": context.target_phone})
    require_api_ok(response, "sendCode")
    markers = {
        "TARGET_PHONE_MASK": mask_phone(context.target_phone),
        "SEND_CODE_REQUESTED": "1",
    }
    return True, markers, [], local_summary(context, markers)


def execute_api_verify(context: Context) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    login_code = os.environ.get("KP_BIND_LOGIN_CODE", "").strip()
    if not re.fullmatch(r"\d{6}", login_code):
        raise RuntimeError("KP_BIND_LOGIN_CODE must be set to the 6-digit SMS code before api-verify")

    expected_user_id = str(migration_source_user_id(context))
    login_data = require_api_ok(
        api_request_json(context, "/api/auth/login", {"phone": context.target_phone, "code": login_code}),
        "login",
    )
    if not isinstance(login_data, dict):
        raise RuntimeError("login response data must be an object")
    token = str(login_data.get("token") or "")
    if not token:
        raise RuntimeError("login response token is empty")

    me_data = require_api_ok(api_request_json(context, "/api/user/me", token=token), "user/me")
    profile_data = require_api_ok(api_request_json(context, "/api/actor/profile/mine", token=token), "actor/profile/mine")
    cards_data = require_api_ok(api_request_json(context, "/api/card/my-cards", token=token), "card/my-cards")
    if not isinstance(me_data, dict) or not isinstance(profile_data, dict) or not isinstance(cards_data, dict):
        raise RuntimeError("api verify response data must be objects")

    cards = cards_data.get("cards") or []
    templates = cards_data.get("templates") or []
    if not isinstance(cards, list):
        raise RuntimeError("card/my-cards data.cards must be a list")
    if not isinstance(templates, list):
        templates = []

    markers = {
        "TARGET_PHONE_MASK": mask_phone(context.target_phone),
        "LOGIN_TOKEN_PRESENT": "1",
        "LOGIN_USER_ID": str(login_data.get("userId") or ""),
        "LOGIN_USER_TYPE": str(login_data.get("userType") or ""),
        "LOGIN_PHONE_MASK": mask_phone(str(login_data.get("phone") or context.target_phone)),
        "ME_USER_ID": str(me_data.get("userId") or ""),
        "ME_USER_TYPE": str(me_data.get("userType") or ""),
        "ME_PHONE_MASK": mask_phone(str(me_data.get("phone") or context.target_phone)),
        "ACTOR_PROFILE_USER_ID": str(profile_data.get("userId") or ""),
        "ACTOR_PROFILE_NAME": str(profile_data.get("name") or ""),
        "ACTOR_PROFILE_REAL_NAME": str(profile_data.get("realName") or ""),
        "ACTOR_PROFILE_CERTIFIED": str(profile_data.get("isCertified")),
        "API_CARD_COUNT": str(len(cards)),
        "API_TEMPLATE_COUNT": str(len(templates)),
    }
    errors: list[str] = []
    for key in ("LOGIN_USER_ID", "ME_USER_ID", "ACTOR_PROFILE_USER_ID"):
        if markers.get(key) != expected_user_id:
            errors.append(f"{key} expected {expected_user_id}, got {markers.get(key, '')}")
    try:
        card_count = int(markers["API_CARD_COUNT"])
    except ValueError:
        card_count = 0
    if card_count < 3:
        errors.append(f"API_CARD_COUNT expected >= 3, got {markers['API_CARD_COUNT']}")
    return not errors, markers, errors, local_summary(context, markers)


def execute_apply(context: Context) -> tuple[bool, dict[str, str], list[str], dict[str, str]]:
    precheck_ok, precheck_markers, precheck_errors, precheck_summary = execute_precheck(context)
    write_summary(context, precheck_summary, precheck_markers, "precheck-before-apply-passed" if precheck_ok else "blocked", precheck_errors)
    if not precheck_ok:
        return False, precheck_markers, precheck_errors, precheck_summary

    apply_sql, _, _ = build_apply_sql(context)
    helper_summary = upload_and_run_sql(
        context,
        apply_sql,
        "--mysql-apply",
        "linxia-phone-binding-apply",
    )
    markers = parse_markers(helper_summary["MYSQL_RESULT"])
    errors: list[str] = validate_helper_status(helper_summary)
    if errors:
        return False, markers, errors, helper_summary
    if markers.get("UPDATED_USER_ROWS") not in {"0", "1"}:
        errors.append(f"UPDATED_USER_ROWS expected 0 or 1, got {markers.get('UPDATED_USER_ROWS', '')}")
    if markers.get("UPDATED_ACTOR_PROFILE_ROWS") not in {"0", "1"}:
        errors.append(
            "UPDATED_ACTOR_PROFILE_ROWS expected 0 or 1, "
            f"got {markers.get('UPDATED_ACTOR_PROFILE_ROWS', '')}"
        )
    if not markers.get("USER_BACKUP_TABLE") or not markers.get("ACTOR_BACKUP_TABLE"):
        errors.append("backup table marker is missing")
    return not errors, markers, errors, helper_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bind the production Linxia test actor account to the target promotion phone.")
    parser.add_argument(
        "--mode",
        choices=[
            "precheck",
            "diagnose",
            "inventory",
            "roster",
            "apply",
            "migration-precheck",
            "migration-apply",
            "cleanup",
            "send-code",
            "api-verify",
        ],
        required=True,
    )
    parser.add_argument("--operator", default=DEFAULT_OPERATOR)
    parser.add_argument("--host", default=os.getenv("KAIPAI_RELEASE_HOST", DEFAULT_HOST))
    parser.add_argument("--user", default=os.getenv("KAIPAI_RELEASE_USER", DEFAULT_USER))
    parser.add_argument("--identity-file", default=os.getenv("KAIPAI_RELEASE_IDENTITY_FILE", str(DEFAULT_IDENTITY_FILE)))
    parser.add_argument("--mysql-database", default="kaipai_prod")
    parser.add_argument("--mysql-container", default="kaipai-mysql")
    parser.add_argument("--source-database", default=os.getenv("KP_BIND_SOURCE_DATABASE", DEFAULT_SOURCE_DATABASE))
    parser.add_argument("--public-base-url", default=os.getenv("KP_BIND_API_BASE_URL", DEFAULT_PUBLIC_BASE_URL))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_phone = os.environ.get("KP_BIND_TARGET_PHONE", "").strip()
    if not re.fullmatch(r"1\d{10}", target_phone):
        raise RuntimeError("KP_BIND_TARGET_PHONE must be set to an 11-digit mainland China mobile number")

    source_user_id = os.environ.get("KP_BIND_SOURCE_USER_ID", "").strip() or None
    if source_user_id and not re.fullmatch(r"\d+", source_user_id):
        raise RuntimeError("KP_BIND_SOURCE_USER_ID must be numeric when provided")

    run_id = datetime.now().astimezone().strftime(f"%Y%m%d-%H%M%S-{args.mode}")
    context = Context(
        mode=args.mode,
        run_id=run_id,
        operator=args.operator,
        host=args.host,
        user=args.user,
        identity_file=Path(args.identity_file),
        mysql_database=args.mysql_database,
        mysql_container=args.mysql_container,
        source_database=args.source_database,
        target_phone=target_phone,
        source_user_id=source_user_id,
        output_dir=SAMPLES_DIR / run_id,
        public_base_url=args.public_base_url,
    )

    if context.mode not in {"send-code", "api-verify"}:
        require_remote_ready(context)
    if context.mode == "precheck":
        ok, markers, errors, helper_summary = execute_precheck(context)
    elif context.mode == "diagnose":
        ok, markers, errors, helper_summary = execute_diagnose(context)
    elif context.mode == "inventory":
        ok, markers, errors, helper_summary = execute_inventory(context)
    elif context.mode == "roster":
        ok, markers, errors, helper_summary = execute_roster(context)
    elif context.mode == "migration-precheck":
        ok, markers, errors, helper_summary = execute_migration_precheck(context)
    elif context.mode == "migration-apply":
        ok, markers, errors, helper_summary = execute_migration_apply(context)
    elif context.mode == "cleanup":
        ok, markers, errors, helper_summary = execute_cleanup(context)
    elif context.mode == "send-code":
        ok, markers, errors, helper_summary = execute_send_code(context)
    elif context.mode == "api-verify":
        ok, markers, errors, helper_summary = execute_api_verify(context)
    else:
        ok, markers, errors, helper_summary = execute_apply(context)

    summary_path = write_summary(context, helper_summary, markers, "passed" if ok else "blocked", errors)
    result = {
        "mode": context.mode,
        "status": "passed" if ok else "blocked",
        "targetPhoneMask": mask_phone(context.target_phone),
        "summaryPath": str(summary_path),
        "markers": markers,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps({"status": "failed", "error": str(error)}, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)
