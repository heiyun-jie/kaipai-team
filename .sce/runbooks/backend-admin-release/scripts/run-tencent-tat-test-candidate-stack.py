#!/usr/bin/env python3
"""Deploy one frozen Candidate backend and migration to the isolated test stack."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
COMMON_PATH = Path(__file__).with_name("run-tencent-tat-test-wechat-config.py")
RECORDS = ROOT / ".sce" / "runbooks" / "backend-admin-release" / "records"
MIGRATION_NAME = "V20260901_001__actor_card_internal_auto_expand.sql"
MIGRATION_PATH = ROOT / "kaipaile-server" / "src" / "main" / "resources" / "db" / "migration" / MIGRATION_NAME
DEFAULT_SECRET_FILE = ROOT / ".sce" / "config" / "local-secrets" / "tencent-cloud-console.env"
DEFAULT_PUBLIC_IP = "101.43.57.62"
CANDIDATE_PATTERN = re.compile(r"[0-9]{8}-[0-9]{4,6}-v3-draft")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def load_common():
    spec = importlib.util.spec_from_file_location("kaipai_tat_common", COMMON_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


COMMON = load_common()


def sha256_file(path: Path) -> str:
    digest = COMMON.hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_candidate(candidate_id: str) -> dict[str, str | Path]:
    if CANDIDATE_PATTERN.fullmatch(candidate_id) is None:
        raise RuntimeError("invalid Candidate ID")
    record = RECORDS / candidate_id / "00-231"
    manifest_path = record / "candidate-manifest.json"
    evidence_path = record / "artifact-evidence.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    backend = next(
        (item for item in evidence.get("artifacts", []) if item.get("name") == "backend-jar"),
        None,
    )
    if not isinstance(backend, dict):
        raise RuntimeError("Candidate backend artifact is missing")
    jar_path = (record / str(backend["relativePath"])).resolve()
    jar_sha256 = sha256_file(jar_path)
    if jar_sha256 != backend.get("sha256"):
        raise RuntimeError("Candidate backend JAR hash mismatch")
    migration_sha256 = sha256_file(MIGRATION_PATH)
    return {
        "candidateId": candidate_id,
        "jarPath": jar_path,
        "jarSha256": jar_sha256,
        "migrationPath": MIGRATION_PATH,
        "migrationSha256": migration_sha256,
        "manifestSha256": sha256_file(manifest_path),
        "evidenceSha256": sha256_file(evidence_path),
    }


REMOTE_TEMPLATE = r"""#!/usr/bin/env bash
set -Eeuo pipefail

candidate_id=__CANDIDATE_ID__
expected_jar_sha256=__JAR_SHA256__
expected_migration_sha256=__MIGRATION_SHA256__
candidate_root="/home/kaipaile/test-release/$candidate_id"
candidate_jar="$candidate_root/kaipai-backend-1.0.0-SNAPSHOT.jar"
migration_sql="$candidate_root/V20260901_001__actor_card_internal_auto_expand.sql"
runtime_root=/opt/kaipai/test
runtime_jar="$runtime_root/backend/app.jar"
compose_file="$runtime_root/docker-compose.yml"
test_service=kaipai-test
test_container=kaipai-backend-test
prod_container=kaipai-backend
mysql_container=kaipai-mysql
test_database=kaipai_test
timestamp="$(date '+%Y%m%d-%H%M%S')"
backup_root="/opt/kaipai/backups/releases/$candidate_id/00-247/$timestamp"
rollback_needed=false

if docker compose version >/dev/null 2>&1; then
  compose_cmd=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  compose_cmd=(docker-compose)
else
  echo 'FINAL_STATUS=failed'
  echo 'FAIL_REASON=docker compose is unavailable'
  exit 1
fi

rollback_on_error() {
  local exit_code=$?
  set +e
  if [[ "$rollback_needed" == "true" ]]; then
    if [[ -f "$backup_root/kaipai_test.before.sql.gz" ]]; then
      mysql_root_password="$(docker exec "$mysql_container" sh -lc 'printf "%s" "${MYSQL_ROOT_PASSWORD:-}"' 2>/dev/null)"
      docker exec -e MYSQL_PWD="$mysql_root_password" "$mysql_container" mysql -uroot \
        -e "DROP DATABASE IF EXISTS kaipai_test; CREATE DATABASE kaipai_test CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"
      gzip -dc "$backup_root/kaipai_test.before.sql.gz" \
        | docker exec -i -e MYSQL_PWD="$mysql_root_password" "$mysql_container" mysql -uroot "$test_database"
    fi
    if [[ -f "$backup_root/app.jar.before" ]]; then
      install -m 0644 "$backup_root/app.jar.before" "$runtime_jar"
      "${compose_cmd[@]}" -f "$compose_file" up -d --build --force-recreate "$test_service" >/dev/null 2>&1
    fi
  fi
  echo 'FINAL_STATUS=failed'
  echo 'ROLLBACK_STATUS=attempted_test_only'
  exit "$exit_code"
}
trap rollback_on_error EXIT

[[ "$(sha256sum "$candidate_jar" | awk '{print $1}')" == "$expected_jar_sha256" ]]
[[ "$(sha256sum "$migration_sql" | awk '{print $1}')" == "$expected_migration_sha256" ]]
[[ -f "$compose_file" && -f "$runtime_jar" ]]

prod_before="$(docker inspect --format '{{.Id}}|{{.State.StartedAt}}|{{.RestartCount}}|{{.State.Status}}' "$prod_container")"
test_before="$(docker inspect --format '{{.Id}}|{{.State.StartedAt}}|{{.RestartCount}}|{{.State.Status}}' "$test_container")"
old_runtime_jar_sha256="$(sha256sum "$runtime_jar" | awk '{print $1}')"

mkdir -p "$backup_root"
install -m 0600 "$runtime_jar" "$backup_root/app.jar.before"
mysql_root_password="$(docker exec "$mysql_container" sh -lc 'printf "%s" "${MYSQL_ROOT_PASSWORD:-}"' 2>/dev/null)"
[[ -n "$mysql_root_password" ]]
docker exec -e MYSQL_PWD="$mysql_root_password" "$mysql_container" mysqldump \
  --default-character-set=utf8mb4 --single-transaction --routines --triggers -uroot "$test_database" \
  | gzip -9 >"$backup_root/kaipai_test.before.sql.gz"
test_database_backup_sha256="$(sha256sum "$backup_root/kaipai_test.before.sql.gz" | awk '{print $1}')"
[[ "$test_database_backup_sha256" =~ ^[0-9a-f]{64}$ ]]
rollback_needed=true

docker exec -i -e MYSQL_PWD="$mysql_root_password" "$mysql_container" mysql \
  --default-character-set=utf8mb4 -uroot -D "$test_database" <"$migration_sql"

source_nullable="$(docker exec -e MYSQL_PWD="$mysql_root_password" "$mysql_container" mysql -Nse \
  "SELECT IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='kaipai_test' AND TABLE_NAME='actor_ai_profile_card_task' AND COLUMN_NAME='source_image_url'" -uroot)"
task_source_columns="$(docker exec -e MYSQL_PWD="$mysql_root_password" "$mysql_container" mysql -Nse \
  "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='kaipai_test' AND TABLE_NAME='actor_ai_profile_card_task' AND COLUMN_NAME IN ('actor_card_id','source_asset_id','source_fingerprint')" -uroot)"
source_index_columns="$(docker exec -e MYSQL_PWD="$mysql_root_password" "$mysql_container" mysql -Nse \
  "SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA='kaipai_test' AND TABLE_NAME='actor_ai_profile_card_task' AND INDEX_NAME='uk_actor_card_expand_source' AND NON_UNIQUE=0" -uroot)"
card_fingerprint_columns="$(docker exec -e MYSQL_PWD="$mysql_root_password" "$mysql_container" mysql -Nse \
  "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='kaipai_test' AND TABLE_NAME='actor_card' AND COLUMN_NAME='expanded_source_fingerprint'" -uroot)"
[[ "$source_nullable" == "YES" && "$task_source_columns" == "3" && "$source_index_columns" == "4" && "$card_fingerprint_columns" == "1" ]]

install -m 0644 "$candidate_jar" "$runtime_jar"
"${compose_cmd[@]}" -f "$compose_file" up -d --build --force-recreate "$test_service" >"$backup_root/compose-up.log" 2>&1

ready=false
for _ in $(seq 1 90); do
  if curl -fsS --max-time 5 -o /dev/null http://127.0.0.1:18080/api/v3/api-docs; then
    ready=true
    break
  fi
  sleep 2
done
[[ "$ready" == "true" ]]

runtime_jar_sha256="$(docker exec "$test_container" sha256sum /app/app.jar | awk '{print $1}')"
[[ "$runtime_jar_sha256" == "$expected_jar_sha256" ]]
test_env="$(docker inspect "$test_container" --format '{{range .Config.Env}}{{println .}}{{end}}')"
printf '%s\n' "$test_env" | grep -qx 'SPRING_PROFILES_ACTIVE=test'
printf '%s\n' "$test_env" | grep '^SPRING_DATASOURCE_URL=' | grep -q 'kaipai_test'
if printf '%s\n' "$test_env" | grep -q 'kaipai_prod'; then
  echo 'test container references production database' >&2
  exit 1
fi

api_status="$(curl -fsS --max-time 20 -o /dev/null -w '%{http_code}' https://test-api.kplyyk.com/api/v3/api-docs)"
[[ "$api_status" == "200" ]]
prod_after="$(docker inspect --format '{{.Id}}|{{.State.StartedAt}}|{{.RestartCount}}|{{.State.Status}}' "$prod_container")"
test_after="$(docker inspect --format '{{.Id}}|{{.State.StartedAt}}|{{.RestartCount}}|{{.State.Status}}' "$test_container")"
[[ "$prod_after" == "$prod_before" ]]

rollback_needed=false
trap - EXIT
echo 'FINAL_STATUS=passed'
echo "CANDIDATE=$candidate_id"
echo "CANDIDATE_BACKEND_JAR_SHA256=$expected_jar_sha256"
echo "RUNTIME_BACKEND_JAR_SHA256=$runtime_jar_sha256"
echo "MIGRATION_SHA256=$expected_migration_sha256"
echo "TEST_DATABASE_BACKUP_SHA256=$test_database_backup_sha256"
echo "TEST_DATABASE_BACKUP_PATH=$backup_root/kaipai_test.before.sql.gz"
echo 'SCHEMA_CONTRACT_PASSED=true'
echo "TEST_API_STATUS=$api_status"
echo "TEST_CONTAINER_BEFORE=$test_before"
echo "TEST_CONTAINER_AFTER=$test_after"
echo "OLD_RUNTIME_JAR_SHA256=$old_runtime_jar_sha256"
echo "PROD_BEFORE=$prod_before"
echo "PROD_AFTER=$prod_after"
echo 'PRODUCTION_CONTAINER_UNCHANGED=true'
echo 'PRODUCTION_MUTATION=NONE'
"""


def build_remote_script(candidate_id: str, jar_sha256: str, migration_sha256: str) -> str:
    if CANDIDATE_PATTERN.fullmatch(candidate_id) is None:
        raise RuntimeError("invalid Candidate ID")
    if SHA256_PATTERN.fullmatch(jar_sha256) is None or SHA256_PATTERN.fullmatch(migration_sha256) is None:
        raise RuntimeError("invalid artifact SHA256")
    return (
        REMOTE_TEMPLATE.replace("__CANDIDATE_ID__", candidate_id)
        .replace("__JAR_SHA256__", jar_sha256)
        .replace("__MIGRATION_SHA256__", migration_sha256)
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deploy one Candidate backend to the isolated KaiPai test stack.")
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--secret-file", type=Path, default=DEFAULT_SECRET_FILE)
    parser.add_argument("--public-ip", default=DEFAULT_PUBLIC_IP)
    parser.add_argument("--region", action="append", dest="regions")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.public_ip != DEFAULT_PUBLIC_IP:
        raise RuntimeError("only the approved dual-environment host is supported")
    candidate = resolve_candidate(args.candidate_id)
    credentials = COMMON.load_credentials(args.secret_file)
    regions = tuple(args.regions or COMMON.DEFAULT_REGIONS)
    region, instance_id, instance_type = COMMON.discover_instance(credentials, args.public_ip, regions)
    agent_status = COMMON.require_tat_online(credentials, region, instance_id)
    script = build_remote_script(
        str(candidate["candidateId"]),
        str(candidate["jarSha256"]),
        str(candidate["migrationSha256"]),
    )
    result = {
        "status": "READY",
        "mode": "DRY_RUN",
        "candidateId": candidate["candidateId"],
        "candidateBackendJarSha256": candidate["jarSha256"],
        "migrationSha256": candidate["migrationSha256"],
        "region": region,
        "instanceId": instance_id,
        "instanceType": instance_type,
        "agentStatus": agent_status,
        "target": "kaipai-backend-test/kaipai_test",
        "productionMutation": "FORBIDDEN",
        "scriptSha256": COMMON.sha256_hex(script),
    }
    if args.execute:
        invocation_id, command_id = COMMON.run_command(credentials, region, instance_id, script)
        task = COMMON.wait_for_invocation(credentials, region, invocation_id)
        output = COMMON.decode_task_output(task)
        task_result = task.get("TaskResult", {})
        if task.get("TaskStatus") != "SUCCESS" or "FINAL_STATUS=passed" not in output:
            raise RuntimeError(
                f"TAT test stack deployment failed: status={task.get('TaskStatus')} "
                f"exitCode={task_result.get('ExitCode')} output={output[:4000]}"
            )
        result.update({
            "status": "PASSED",
            "mode": "EXECUTE",
            "invocationId": invocation_id,
            "commandId": command_id,
            "taskStatus": task.get("TaskStatus"),
            "exitCode": task_result.get("ExitCode"),
            "output": output,
        })
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
