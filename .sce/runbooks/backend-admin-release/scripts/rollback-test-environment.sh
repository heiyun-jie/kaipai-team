#!/usr/bin/env bash
set -Eeuo pipefail

candidate_id=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --candidate-id) candidate_id="${2:-}"; shift 2 ;;
    -h|--help) echo 'Usage: rollback-test-environment.sh --candidate-id YYYYMMDD-HHMM-v3-draft'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done

if (( EUID != 0 )); then echo "root is required" >&2; exit 1; fi
if [[ ! "$candidate_id" =~ ^[0-9]{8}-[0-9]{4,6}-v3-draft$ ]]; then echo "invalid candidate-id" >&2; exit 1; fi

runtime_root="/opt/kaipai/test"
compose_file="$runtime_root/docker-compose.yml"
nginx_conf="/etc/nginx/conf.d/kaipai-test.conf"
backup_base="/opt/kaipai/backups/releases/$candidate_id/test-environment"
latest_backup="$(find "$backup_base" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' 2>/dev/null | sort | tail -1)"
[[ -n "$latest_backup" ]] || { echo "test backup not found" >&2; exit 1; }
backup_root="$backup_base/$latest_backup"

prod_id="$(docker inspect --format '{{.Id}}' kaipai-backend 2>/dev/null || true)"
prod_status="$(docker inspect --format '{{.State.Status}}' kaipai-backend 2>/dev/null || true)"
[[ -n "$prod_id" && "$prod_status" == "running" ]] || { echo "production container is not running" >&2; exit 1; }

if docker compose version >/dev/null 2>&1; then
  compose_cmd=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  compose_cmd=(docker-compose)
else
  echo "docker compose is required" >&2
  exit 1
fi

if [[ -f "$compose_file" ]]; then "${compose_cmd[@]}" -f "$compose_file" down >/dev/null 2>&1 || true; fi
if [[ -f "$backup_root/kaipai-test.conf.before" ]]; then
  install -m 0644 "$backup_root/kaipai-test.conf.before" "$nginx_conf"
else
  rm -f "$nginx_conf"
fi
nginx -t -c /etc/nginx/nginx.conf >/dev/null
systemctl reload nginx
rm -rf "$runtime_root"
rm -rf /opt/kaipai/nginx/html-test

post_prod_id="$(docker inspect --format '{{.Id}}' kaipai-backend)"
post_prod_status="$(docker inspect --format '{{.State.Status}}' kaipai-backend)"
[[ "$post_prod_id" == "$prod_id" && "$post_prod_status" == "running" ]] || { echo "production container identity changed" >&2; exit 1; }
printf 'FINAL_STATUS=rolled-back\nCANDIDATE=%s\nTEST_RUNTIME_REMOVED=true\nTEST_NGINX_REMOVED_OR_RESTORED=true\nPRODUCTION_CONTAINER_UNCHANGED=true\n' "$candidate_id"
