#!/usr/bin/env bash
set -Eeuo pipefail

candidate_id=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --candidate-id) candidate_id="${2:-}"; shift 2 ;;
    -h|--help) echo 'Usage: prepare-test-production-copy.sh --candidate-id YYYYMMDD-HHMM-v3-draft'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done

if (( EUID != 0 )); then echo "root is required" >&2; exit 1; fi
if [[ ! "$candidate_id" =~ ^[0-9]{8}-[0-9]{4,6}-v3-draft$ ]]; then echo "invalid candidate-id" >&2; exit 1; fi

prod_database="kaipai_prod"
test_database="kaipai_test"
mysql_container="kaipai-mysql"
prod_container="kaipai-backend"
test_container="kaipai-backend-test"
backup_root="/opt/kaipai/backups/releases/$candidate_id/test-prod-copy/$(date '+%Y%m%d-%H%M%S')"

[[ "$test_database" == "kaipai_test" ]] || { echo "destructive target guard failed" >&2; exit 1; }
[[ "$prod_database" == "kaipai_prod" && "$prod_database" != "$test_database" ]] || { echo "production database guard failed" >&2; exit 1; }
command -v docker >/dev/null || { echo "docker is required" >&2; exit 1; }
command -v gzip >/dev/null || { echo "gzip is required" >&2; exit 1; }

prod_id="$(docker inspect --format '{{.Id}}' "$prod_container" 2>/dev/null || true)"
prod_status="$(docker inspect --format '{{.State.Status}}' "$prod_container" 2>/dev/null || true)"
test_status="$(docker inspect --format '{{.State.Status}}' "$test_container" 2>/dev/null || true)"
[[ -n "$prod_id" && "$prod_status" == "running" ]] || { echo "production container is not running" >&2; exit 1; }
[[ "$test_status" == "running" ]] || { echo "test container must be running before the copy gate" >&2; exit 1; }

mysql_root_password="$(docker exec "$mysql_container" sh -lc 'printf "%s" "${MYSQL_ROOT_PASSWORD:-}"' 2>/dev/null || true)"
[[ -n "$mysql_root_password" ]] || { echo "mysql root password is unavailable" >&2; exit 1; }

mysql_exec() {
  docker exec -i -e MYSQL_PWD="$mysql_root_password" "$mysql_container" \
    mysql --default-character-set=utf8mb4 -uroot "$@"
}

dump_database() {
  local database="$1"
  local output="$2"
  docker exec -e MYSQL_PWD="$mysql_root_password" "$mysql_container" \
    mysqldump --default-character-set=utf8mb4 -uroot \
      --single-transaction --routines --triggers --hex-blob \
      --set-gtid-purged=OFF --skip-comments "$database" >"$output"
  [[ -s "$output" ]] || { echo "database dump is empty: $database" >&2; return 1; }
  grep -q '^CREATE TABLE' "$output" || { echo "database dump has no table DDL: $database" >&2; return 1; }
}

write_count_inventory() {
  local database="$1"
  local output="$2"
  : >"$output"
  while IFS= read -r table_name; do
    [[ "$table_name" =~ ^[A-Za-z0-9_]+$ ]] || { echo "invalid table name in inventory" >&2; return 1; }
    table_count="$(mysql_exec -N -s -D "$database" -e "SELECT COUNT(*) FROM \`$table_name\`;" 2>/dev/null)"
    printf '%s=%s\n' "$table_name" "$table_count" >>"$output"
  done < <(mysql_exec -N -s -e "SELECT table_name FROM information_schema.tables WHERE table_schema='$database' AND table_type='BASE TABLE' ORDER BY table_name;" 2>/dev/null)
  [[ -s "$output" ]] || { echo "database inventory is empty: $database" >&2; return 1; }
}

canonical_dump_sha() {
  sed -E 's/ CHARACTER SET utf8mb4 COLLATE utf8mb4_bin/ COLLATE utf8mb4_bin/g' "$1" | sha256sum | awk '{print $1}'
}

mkdir -p "$backup_root"
chmod 0700 "$backup_root"

prod_sql="$backup_root/kaipai-prod.sql"
old_test_sql="$backup_root/kaipai-test-before.sql"
restored_sql="$backup_root/kaipai-test-restored.sql"

dump_database "$prod_database" "$prod_sql"
dump_database "$test_database" "$old_test_sql"
write_count_inventory "$prod_database" "$backup_root/kaipai-prod-counts.txt"
prod_dump_sha="$(sha256sum "$prod_sql" | awk '{print $1}')"
prod_canonical_dump_sha="$(canonical_dump_sha "$prod_sql")"
prod_counts_sha="$(sha256sum "$backup_root/kaipai-prod-counts.txt" | awk '{print $1}')"
old_test_dump_sha="$(sha256sum "$old_test_sql" | awk '{print $1}')"
gzip -n -c "$prod_sql" >"$prod_sql.gz"
gzip -n -c "$old_test_sql" >"$old_test_sql.gz"
gzip -t "$prod_sql.gz"
gzip -t "$old_test_sql.gz"

docker stop "$test_container" >/dev/null
stopped_status="$(docker inspect --format '{{.State.Status}}' "$test_container")"
[[ "$stopped_status" == "exited" ]] || { echo "test container did not stop" >&2; exit 1; }

test_connections="$(mysql_exec -N -s -e "SELECT COUNT(*) FROM information_schema.processlist WHERE db='$test_database';" 2>/dev/null)"
[[ "$test_connections" == "0" ]] || { echo "test database still has active connections" >&2; exit 1; }

mysql_exec -e "DROP DATABASE IF EXISTS \`$test_database\`; CREATE DATABASE \`$test_database\` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"
gzip -dc "$prod_sql.gz" | mysql_exec -D "$test_database"

dump_database "$test_database" "$restored_sql"
write_count_inventory "$test_database" "$backup_root/kaipai-test-restored-counts.txt"
restored_dump_sha="$(sha256sum "$restored_sql" | awk '{print $1}')"
restored_canonical_dump_sha="$(canonical_dump_sha "$restored_sql")"
restored_counts_sha="$(sha256sum "$backup_root/kaipai-test-restored-counts.txt" | awk '{print $1}')"
[[ "$restored_canonical_dump_sha" == "$prod_canonical_dump_sha" ]] || { echo "restored canonical dump checksum does not match production snapshot" >&2; exit 1; }
[[ "$restored_counts_sha" == "$prod_counts_sha" ]] || { echo "restored table counts do not match production snapshot" >&2; exit 1; }

rm -f "$prod_sql" "$old_test_sql" "$restored_sql"
chmod 0600 "$backup_root"/*

post_prod_id="$(docker inspect --format '{{.Id}}' "$prod_container")"
post_prod_status="$(docker inspect --format '{{.State.Status}}' "$prod_container")"
[[ "$post_prod_id" == "$prod_id" && "$post_prod_status" == "running" ]] || { echo "production container identity changed" >&2; exit 1; }

printf 'FINAL_STATUS=restored-for-migration\nCANDIDATE=%s\nBACKUP_ROOT=%s\nPROD_DUMP_SHA256=%s\nOLD_TEST_DUMP_SHA256=%s\nRESTORED_DUMP_SHA256=%s\nPROD_CANONICAL_DUMP_SHA256=%s\nRESTORED_CANONICAL_DUMP_SHA256=%s\nPROD_COUNTS_SHA256=%s\nRESTORED_COUNTS_SHA256=%s\nTEST_DATABASE=kaipai_test\nTEST_CONTAINER_STATUS=exited\nPRODUCTION_CONTAINER_UNCHANGED=true\n' \
  "$candidate_id" "$backup_root" "$prod_dump_sha" "$old_test_dump_sha" "$restored_dump_sha" "$prod_canonical_dump_sha" "$restored_canonical_dump_sha" "$prod_counts_sha" "$restored_counts_sha"
