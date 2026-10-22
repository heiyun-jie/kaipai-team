#!/usr/bin/env bash
set -Eeuo pipefail

candidate_id=""
backup_root=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --candidate-id) candidate_id="${2:-}"; shift 2 ;;
    --backup-root) backup_root="${2:-}"; shift 2 ;;
    -h|--help) echo 'Usage: rollback-test-production-copy.sh --candidate-id ID --backup-root PATH'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done

if (( EUID != 0 )); then echo "root is required" >&2; exit 1; fi
if [[ ! "$candidate_id" =~ ^[0-9]{8}-[0-9]{4,6}-v3-draft$ ]]; then echo "invalid candidate-id" >&2; exit 1; fi

allowed_root="/opt/kaipai/backups/releases/$candidate_id/test-prod-copy"
resolved_backup="$(readlink -f "$backup_root" 2>/dev/null || true)"
resolved_allowed="$(readlink -f "$allowed_root" 2>/dev/null || true)"
[[ -n "$resolved_backup" && -n "$resolved_allowed" && "$resolved_backup" == "$resolved_allowed"/* ]] || { echo "backup root is outside candidate scope" >&2; exit 1; }

old_test_dump="$resolved_backup/kaipai-test-before.sql.gz"
[[ -f "$old_test_dump" ]] || { echo "old test backup is missing" >&2; exit 1; }
gzip -t "$old_test_dump"

mysql_container="kaipai-mysql"
test_container="kaipai-backend-test"
prod_container="kaipai-backend"
test_database="kaipai_test"
prod_id="$(docker inspect --format '{{.Id}}' "$prod_container")"
prod_status="$(docker inspect --format '{{.State.Status}}' "$prod_container")"
[[ "$prod_status" == "running" ]] || { echo "production container is not running" >&2; exit 1; }

mysql_root_password="$(docker exec "$mysql_container" sh -lc 'printf "%s" "${MYSQL_ROOT_PASSWORD:-}"' 2>/dev/null || true)"
[[ -n "$mysql_root_password" ]] || { echo "mysql root password is unavailable" >&2; exit 1; }
mysql_exec() { docker exec -i -e MYSQL_PWD="$mysql_root_password" "$mysql_container" mysql --default-character-set=utf8mb4 -uroot "$@"; }

docker stop "$test_container" >/dev/null 2>&1 || true
mysql_exec -e "DROP DATABASE IF EXISTS \`$test_database\`; CREATE DATABASE \`$test_database\` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"
gzip -dc "$old_test_dump" | mysql_exec -D "$test_database"
docker start "$test_container" >/dev/null

ready="false"
for ((attempt = 1; attempt <= 60; attempt++)); do
  if curl -fsS --max-time 5 -o /dev/null http://127.0.0.1:18080/api/v3/api-docs 2>/dev/null; then ready="true"; break; fi
  sleep 2
done
[[ "$ready" == "true" ]] || { echo "test backend did not recover after rollback" >&2; exit 1; }

post_prod_id="$(docker inspect --format '{{.Id}}' "$prod_container")"
post_prod_status="$(docker inspect --format '{{.State.Status}}' "$prod_container")"
[[ "$post_prod_id" == "$prod_id" && "$post_prod_status" == "running" ]] || { echo "production container identity changed" >&2; exit 1; }
printf 'FINAL_STATUS=rolled-back\nCANDIDATE=%s\nTEST_DATABASE=kaipai_test\nTEST_BACKEND_STATUS=ready\nPRODUCTION_CONTAINER_UNCHANGED=true\n' "$candidate_id"
