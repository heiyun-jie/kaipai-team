#!/usr/bin/env bash
set -euo pipefail

release_id=""
upload_path=""
jar_sha=""
operator_user="kaipaile"
runtime_diagnostics="false"
diagnostic_container="kaipai-backend"
diagnostic_since="15m"
diagnostic_tail="400"
mysql_validation="false"
mysql_script_path=""
mysql_database="kaipai_dev"
mysql_container="kaipai-mysql"
compose_env_sync="false"
compose_upload_path=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --release-id)
      release_id="${2:-}"
      shift 2
      ;;
    --upload-path)
      upload_path="${2:-}"
      shift 2
      ;;
    --jar-sha)
      jar_sha="${2:-}"
      shift 2
      ;;
    --operator-user)
      operator_user="${2:-}"
      shift 2
      ;;
    --runtime-diagnostics)
      runtime_diagnostics="true"
      shift 1
      ;;
    --container)
      diagnostic_container="${2:-}"
      shift 2
      ;;
    --since)
      diagnostic_since="${2:-}"
      shift 2
      ;;
    --tail)
      diagnostic_tail="${2:-}"
      shift 2
      ;;
    --mysql-validation)
      mysql_validation="true"
      shift 1
      ;;
    --mysql-script-path)
      mysql_script_path="${2:-}"
      shift 2
      ;;
    --mysql-database)
      mysql_database="${2:-}"
      shift 2
      ;;
    --mysql-container)
      mysql_container="${2:-}"
      shift 2
      ;;
    --compose-env-sync)
      compose_env_sync="true"
      shift 1
      ;;
    --compose-upload-path)
      compose_upload_path="${2:-}"
      shift 2
      ;;
    --healthcheck)
      echo "helper-ok"
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

emit_section() {
  local name="$1"
  local value="$2"
  printf '__%s_BEGIN__\n%s\n__%s_END__\n' "$name" "$value" "$name"
}

redact_targeted_value() {
  sed -E 's/(WECHAT_MINIAPP_APP_SECRET[=:])[[:space:]]*[^[:space:]]+/\1[REDACTED]/gI'
}

collect_compose_backend_source() {
  local source_file="$1"
  if [[ ! -f "$source_file" ]]; then
    printf 'compose file not found: %s\n' "$source_file"
    return 1
  fi

  grep -nE '(^services:|^[[:space:]]{2}kaipai:|^[[:space:]]+(image:|container_name:|environment:|env_file:|ports:)|WECHAT_MINIAPP_|NACOS_ENABLED|SPRING_PROFILES_ACTIVE|SERVER_PORT)' "$source_file" 2>&1 \
    | redact_targeted_value
}

collect_compose_rendered_backend() {
  local runtime_root="$1"
  (
    cd "$runtime_root"
    "${compose_cmd[@]}" config 2>&1
  ) | grep -nE '(^services:|^[[:space:]]{2}kaipai:|^[[:space:]]{4}(image:|container_name:|environment:|env_file:|ports:)|WECHAT_MINIAPP_|NACOS_ENABLED|SPRING_PROFILES_ACTIVE|SERVER_PORT)' \
    | redact_targeted_value
}

if docker compose version >/dev/null 2>&1; then
  compose_cmd=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  compose_cmd=(docker-compose)
else
  echo "docker compose not available" >&2
  exit 1
fi

if [[ "$runtime_diagnostics" == "true" ]]; then
  failure_reasons=()
  remote_date="$(date '+%F %T %z')"
  docker_ps="$(docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>&1)" || failure_reasons+=("docker ps failed")
  docker_inspect_env="$(docker exec "$diagnostic_container" env 2>&1)" || failure_reasons+=("docker exec env failed for $diagnostic_container")
  docker_logs_tail="$(docker logs --since "$diagnostic_since" --tail "$diagnostic_tail" "$diagnostic_container" 2>&1)" || failure_reasons+=("docker logs failed for $diagnostic_container")
  compose_backend_source="$(collect_compose_backend_source '/opt/kaipai/docker-compose.yml' 2>&1)" || failure_reasons+=("compose source capture failed")
  compose_rendered_backend="$(collect_compose_rendered_backend '/opt/kaipai' 2>&1)" || failure_reasons+=("compose rendered config capture failed")
  final_status="passed"
  if [[ ${#failure_reasons[@]} -gt 0 ]]; then
    final_status="failed"
  fi
  fail_reason="$(printf '%s\n' "${failure_reasons[@]}")"

  emit_section "REMOTE_DATE" "$remote_date"
  emit_section "DOCKER_PS" "$docker_ps"
  emit_section "DOCKER_INSPECT_ENV" "$docker_inspect_env"
  emit_section "DOCKER_LOGS_TAIL" "$docker_logs_tail"
  emit_section "COMPOSE_BACKEND_SOURCE" "$compose_backend_source"
  emit_section "COMPOSE_RENDERED_BACKEND" "$compose_rendered_backend"
  emit_section "FINAL_STATUS" "$final_status"
  emit_section "FAIL_REASON" "$fail_reason"

  if [[ "$final_status" != "passed" ]]; then
    exit 1
  fi
  exit 0
fi

if [[ "$mysql_validation" == "true" ]]; then
  failure_reasons=()
  remote_date="$(date '+%F %T %z')"
  mysql_result=""
  if [[ -z "$mysql_script_path" ]]; then
    failure_reasons+=("mysql script path is required")
  elif [[ ! -f "$mysql_script_path" ]]; then
    failure_reasons+=("mysql script not found: $mysql_script_path")
  else
    mysql_result="$(
      docker exec -i "$mysql_container" mysql --default-character-set=utf8mb4 -uroot -proot123456 -D "$mysql_database" < "$mysql_script_path" 2>&1
    )" || failure_reasons+=("mysql validation failed")
  fi

  final_status="passed"
  if [[ ${#failure_reasons[@]} -gt 0 ]]; then
    final_status="failed"
  fi
  fail_reason="$(printf '%s\n' "${failure_reasons[@]}")"

  emit_section "REMOTE_DATE" "$remote_date"
  emit_section "MYSQL_DATABASE" "$mysql_database"
  emit_section "MYSQL_CONTAINER" "$mysql_container"
  emit_section "MYSQL_RESULT" "$mysql_result"
  emit_section "FINAL_STATUS" "$final_status"
  emit_section "FAIL_REASON" "$fail_reason"

  if [[ "$final_status" != "passed" ]]; then
    exit 1
  fi
  exit 0
fi

if [[ "$compose_env_sync" == "true" ]]; then
  if [[ -z "$release_id" || -z "$compose_upload_path" ]]; then
    echo "release-id and compose-upload-path are required" >&2
    exit 1
  fi

  if [[ ! "$release_id" =~ ^[0-9]{8}-[0-9]{6}-backend-env-[a-z0-9-]+$ ]]; then
    echo "invalid release-id: $release_id" >&2
    exit 1
  fi

  if [[ ! -f "$compose_upload_path" ]]; then
    echo "uploaded compose file not found: $compose_upload_path" >&2
    exit 1
  fi

  failure_reasons=()
  remote_date="$(date '+%F %T %z')"
  release_root="/opt/kaipai/builds/$release_id"
  backup_root="/opt/kaipai/backups/releases/$release_id/backend-env"
  runtime_root="/opt/kaipai"
  runtime_compose_file="$runtime_root/docker-compose.yml"
  candidate_runtime_file="$runtime_root/docker-compose.candidate.yml"
  archived_compose_file="$release_root/docker-compose.yml"

  mkdir -p "$release_root" "$backup_root"
  cp -a "$runtime_compose_file" "$backup_root/docker-compose.yml.before"
  install -m 0644 "$compose_upload_path" "$archived_compose_file"
  install -m 0644 "$archived_compose_file" "$candidate_runtime_file"

  candidate_validate_output="$(
    cd "$runtime_root"
    "${compose_cmd[@]}" -f "$candidate_runtime_file" config 2>&1
  )" || failure_reasons+=("compose candidate validation failed")

  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    install -m 0644 "$candidate_runtime_file" "$runtime_compose_file"
  fi

  docker_inspect_env="$(docker inspect kaipai-backend --format '{{range .Config.Env}}{{println .}}{{end}}' 2>&1 || true)"
  compose_backend_source="$(collect_compose_backend_source "$runtime_compose_file" 2>&1 || true)"
  compose_rendered_backend="$(collect_compose_rendered_backend "$runtime_root" 2>&1 || true)"
  rm -f "$compose_upload_path" "$candidate_runtime_file"

  final_status="passed"
  if [[ ${#failure_reasons[@]} -gt 0 ]]; then
    final_status="failed"
  fi
  fail_reason="$(printf '%s\n' "${failure_reasons[@]}")"

  emit_section "REMOTE_DATE" "$remote_date"
  emit_section "BACKUP_PATH" "$backup_root"
  emit_section "RELEASE_ROOT" "$release_root"
  emit_section "COMPOSE_FILE" "$runtime_compose_file"
  emit_section "ARCHIVED_COMPOSE_FILE" "$archived_compose_file"
  emit_section "DOCKER_INSPECT_ENV" "$docker_inspect_env"
  emit_section "COMPOSE_BACKEND_SOURCE" "$compose_backend_source"
  emit_section "COMPOSE_RENDERED_BACKEND" "$compose_rendered_backend"
  emit_section "CANDIDATE_VALIDATE_OUTPUT" "$candidate_validate_output"
  emit_section "FINAL_STATUS" "$final_status"
  emit_section "FAIL_REASON" "$fail_reason"

  if [[ "$final_status" != "passed" ]]; then
    exit 1
  fi
  exit 0
fi

if [[ -z "$release_id" || -z "$upload_path" || -z "$jar_sha" ]]; then
  echo "release-id, upload-path and jar-sha are required" >&2
  exit 1
fi

if [[ ! "$release_id" =~ ^[0-9]{8}-[0-9]{6}-backend-only-[a-z0-9-]+$ ]]; then
  echo "invalid release-id: $release_id" >&2
  exit 1
fi

if [[ ! -f "$upload_path" ]]; then
  echo "upload jar not found: $upload_path" >&2
  exit 1
fi

release_root="/opt/kaipai/builds/$release_id"
backup_root="/opt/kaipai/backups/releases/$release_id/backend"
runtime_root="/opt/kaipai"
runtime_jar="$runtime_root/kaipai-backend-1.0.0-SNAPSHOT.jar"
dockerfile_path="$runtime_root/Dockerfile"
compose_file="$runtime_root/docker-compose.yml"
nginx_conf="$runtime_root/nginx/conf/default.conf"
release_jar="$release_root/kaipai-backend-1.0.0-SNAPSHOT.jar"
container_name="kaipai-backend"

normalize_sha() {
  tr '[:lower:]' '[:upper:]'
}

http_probe() {
  local method="$1"
  local url="$2"
  local body="${3:-}"
  local body_file
  local err_file
  local curl_status
  body_file="$(mktemp)"
  err_file="$(mktemp)"
  local code
  set +e
  if [[ -n "$body" ]]; then
    code="$(curl -sS -o "$body_file" -w '%{http_code}' -X "$method" -H 'Content-Type: application/json' -d "$body" "$url" 2>"$err_file")"
  else
    code="$(curl -sS -o "$body_file" -w '%{http_code}' -X "$method" "$url" 2>"$err_file")"
  fi
  curl_status=$?
  set -e
  printf 'status=%s\n' "$code"
  if [[ "$curl_status" -ne 0 ]]; then
    printf 'curl_error=%s\n' "$(tr '\n' ' ' <"$err_file" | sed 's/[[:space:]]\+/ /g' | sed 's/[[:space:]]*$//')"
  fi
  cat "$body_file"
  rm -f "$body_file"
  rm -f "$err_file"
}

wait_for_docs_ready() {
  local url="$1"
  local attempts="${2:-15}"
  local sleep_seconds="${3:-3}"
  local probe_output=""
  local status=""
  for ((i = 1; i <= attempts; i++)); do
    probe_output="$(http_probe GET "$url")"
    status="$(printf '%s\n' "$probe_output" | sed -n '1s/^status=//p')"
    if [[ "$status" == "200" ]]; then
      printf '%s\n' "$probe_output"
      return 0
    fi
    sleep "$sleep_seconds"
  done
  printf '%s\n' "$probe_output"
}

failure_reasons=()

record_failure() {
  failure_reasons+=("$1")
}

ensure_non_500_probe() {
  local name="$1"
  local probe_output="$2"
  local status
  status="$(printf '%s\n' "$probe_output" | sed -n '1s/^status=//p')"
  if [[ -z "$status" ]]; then
    record_failure "probe missing status: $name"
    return
  fi
  if [[ "$status" -ge 500 ]]; then
    record_failure "probe http failed: $name status=$status"
    return
  fi
  if printf '%s\n' "$probe_output" | grep -q '"code":[[:space:]]*500'; then
    record_failure "probe business failed: $name returned code=500"
  fi
}

remote_date="$(date '+%F %T %z')"
uploaded_jar_sha="$(sha256sum "$upload_path" | awk '{print toupper($1)}')"
expected_jar_sha="$(printf '%s' "$jar_sha" | normalize_sha)"

if [[ "$uploaded_jar_sha" != "$expected_jar_sha" ]]; then
  echo "uploaded jar sha mismatch: $uploaded_jar_sha != $expected_jar_sha" >&2
  exit 1
fi

mkdir -p "$release_root" "$backup_root"
cp -a "$runtime_jar" "$backup_root/kaipai-backend-1.0.0-SNAPSHOT.jar.before"
cp -a "$dockerfile_path" "$backup_root/Dockerfile.before"
cp -a "$compose_file" "$backup_root/docker-compose.yml.before"
cp -a "$nginx_conf" "$backup_root/default.conf.before"
docker inspect "$container_name" >"$backup_root/docker-inspect.before.json" 2>&1 || true
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' >"$backup_root/docker-ps.before.txt" 2>&1 || true
docker logs --tail 200 "$container_name" >"$backup_root/docker-logs.before.txt" 2>&1 || true

install -m 0644 "$upload_path" "$release_jar"
install -m 0644 "$release_jar" "$runtime_jar"
rm -f "$upload_path"

(
  cd "$runtime_root"
  "${compose_cmd[@]}" build kaipai
  if docker ps -a --format '{{.Names}}' | grep -qx "$container_name"; then
    docker rm -f "$container_name" >/dev/null 2>&1 || true
  fi
  "${compose_cmd[@]}" up -d --force-recreate kaipai
) >"$release_root/docker-compose-redeploy.log" 2>&1

sleep 8

runtime_jar_sha="$(sha256sum "$runtime_jar" | awk '{print toupper($1)}')"
container_jar_sha="$(docker exec "$container_name" sh -lc "sha256sum /app/app.jar | awk '{print toupper(\$1)}'")"
docker_ps="$(docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}')"
docker_inspect_env="$(docker inspect "$container_name" --format '{{range .Config.Env}}{{println .}}{{end}}')"
docker_logs_tail="$(docker logs --tail 200 "$container_name" 2>&1 || true)"
compose_backend_source="$(collect_compose_backend_source "$compose_file" 2>&1 || true)"
compose_rendered_backend="$(collect_compose_rendered_backend "$runtime_root" 2>&1 || true)"
compose_version="$("${compose_cmd[@]}" version 2>&1)"
compose_ps="$(
  cd "$runtime_root"
  "${compose_cmd[@]}" ps
)"
nginx_proxy_block="$(grep -n -A 6 'location /api' "$nginx_conf" || true)"
docs_probe="$(wait_for_docs_ready 'http://127.0.0.1:8080/api/v3/api-docs' 20 3)"
admin_login_probe="$(http_probe POST 'http://127.0.0.1:8080/api/admin/auth/login' '{"account":"admin","password":"admin123"}')"
recruit_roles_probe="$(http_probe GET 'http://127.0.0.1:8080/api/admin/recruit/roles?pageNo=1&pageSize=1&keyword=')"
role_search_probe="$(http_probe GET 'http://127.0.0.1:8080/api/role/search?page=1&size=1&keyword=&gender=')"

if [[ "$runtime_jar_sha" != "$expected_jar_sha" ]]; then
  record_failure "runtime jar sha mismatch: $runtime_jar_sha != $expected_jar_sha"
fi

if [[ "$container_jar_sha" != "$expected_jar_sha" ]]; then
  record_failure "container jar sha mismatch: $container_jar_sha != $expected_jar_sha"
fi

if ! printf '%s\n' "$docs_probe" | sed -n '1s/^status=//p' | grep -qx '200'; then
  record_failure "docs probe failed"
fi

ensure_non_500_probe "admin-auth-login" "$admin_login_probe"
ensure_non_500_probe "admin-recruit-roles" "$recruit_roles_probe"
ensure_non_500_probe "role-search" "$role_search_probe"

final_status="passed"
if [[ ${#failure_reasons[@]} -gt 0 ]]; then
  final_status="failed"
fi
fail_reason="$(printf '%s\n' "${failure_reasons[@]}")"

emit_section "REMOTE_DATE" "$remote_date"
emit_section "BACKUP_PATH" "$backup_root"
emit_section "RELEASE_ROOT" "$release_root"
emit_section "REMOTE_RELEASE_JAR" "$release_jar"
emit_section "RUNTIME_JAR" "$runtime_jar"
emit_section "UPLOADED_JAR_SHA" "$uploaded_jar_sha"
emit_section "RUNTIME_JAR_SHA" "$runtime_jar_sha"
emit_section "CONTAINER_JAR_SHA" "$container_jar_sha"
emit_section "DOCKER_COMPOSE_VERSION" "$compose_version"
emit_section "DOCKER_COMPOSE_PS" "$compose_ps"
emit_section "DOCKER_PS" "$docker_ps"
emit_section "DOCKER_INSPECT_ENV" "$docker_inspect_env"
emit_section "DOCKER_LOGS_TAIL" "$docker_logs_tail"
emit_section "COMPOSE_BACKEND_SOURCE" "$compose_backend_source"
emit_section "COMPOSE_RENDERED_BACKEND" "$compose_rendered_backend"
emit_section "NGINX_API_PROXY" "$nginx_proxy_block"
emit_section "INTERNAL_DOCS" "$docs_probe"
emit_section "INTERNAL_ADMIN_LOGIN" "$admin_login_probe"
emit_section "INTERNAL_RECRUIT_ROLES" "$recruit_roles_probe"
emit_section "INTERNAL_ROLE_SEARCH" "$role_search_probe"
emit_section "FINAL_STATUS" "$final_status"
emit_section "FAIL_REASON" "$fail_reason"

if [[ "$final_status" != "passed" ]]; then
  exit 1
fi
