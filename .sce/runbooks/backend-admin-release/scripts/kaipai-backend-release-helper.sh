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
mysql_apply="false"
mysql_dump="false"
mysql_script_path=""
mysql_database="kaipai_dev"
mysql_container="kaipai-mysql"
compose_env_sync="false"
compose_upload_path=""
nacos_config_scan="false"
nacos_data_ids=""
nacos_server_addr="127.0.0.1:8848"
nacos_username="nacos"
nacos_password="${KAIPAI_RELEASE_NACOS_PASSWORD:-${NACOS_PASSWORD:-}}"
nacos_group="DEFAULT_GROUP"
nacos_namespace=""
nacos_grep=""
nacos_config_export="false"
nacos_config_sync="false"
nacos_data_id=""
nacos_upload_path=""
nacos_content_type="yaml"
bridge_proxy_sync="false"
bridge_proxy_location=""
bridge_proxy_pass_url=""
domain_api_proxy_sync="false"
domain_api_proxy_api_only="false"
domain_api_proxy_domain="kplyyk.com"
domain_api_proxy_api_domain="api.kplyyk.com"
domain_api_proxy_backend_url="http://127.0.0.1:8080"
domain_api_proxy_nginx_conf="/etc/nginx/sites-available/default"
domain_api_proxy_nginx_enabled="/etc/nginx/sites-enabled/default"
domain_api_proxy_acme_root="/var/www/letsencrypt"
compose_service_recreate="false"
compose_service=""

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
    --mysql-apply)
      mysql_apply="true"
      shift 1
      ;;
    --mysql-dump)
      mysql_dump="true"
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
    --nacos-config-scan)
      nacos_config_scan="true"
      shift 1
      ;;
    --nacos-data-ids)
      nacos_data_ids="${2:-}"
      shift 2
      ;;
    --nacos-server-addr)
      nacos_server_addr="${2:-}"
      shift 2
      ;;
    --nacos-username)
      nacos_username="${2:-}"
      shift 2
      ;;
    --nacos-password)
      nacos_password="${2:-}"
      shift 2
      ;;
    --nacos-group)
      nacos_group="${2:-}"
      shift 2
      ;;
    --nacos-namespace)
      nacos_namespace="${2:-}"
      shift 2
      ;;
    --nacos-grep)
      nacos_grep="${2:-}"
      shift 2
      ;;
    --nacos-config-export)
      nacos_config_export="true"
      shift 1
      ;;
    --nacos-config-sync)
      nacos_config_sync="true"
      shift 1
      ;;
    --nacos-data-id)
      nacos_data_id="${2:-}"
      shift 2
      ;;
    --nacos-upload-path)
      nacos_upload_path="${2:-}"
      shift 2
      ;;
    --nacos-content-type)
      nacos_content_type="${2:-}"
      shift 2
      ;;
    --bridge-proxy-sync)
      bridge_proxy_sync="true"
      shift 1
      ;;
    --bridge-proxy-location)
      bridge_proxy_location="${2:-}"
      shift 2
      ;;
    --bridge-proxy-pass-url)
      bridge_proxy_pass_url="${2:-}"
      shift 2
      ;;
    --domain-api-proxy-sync)
      domain_api_proxy_sync="true"
      shift 1
      ;;
    --domain-api-proxy-api-only)
      domain_api_proxy_api_only="true"
      shift 1
      ;;
    --domain-api-proxy-domain)
      domain_api_proxy_domain="${2:-}"
      shift 2
      ;;
    --domain-api-proxy-api-domain)
      domain_api_proxy_api_domain="${2:-}"
      shift 2
      ;;
    --domain-api-proxy-backend-url)
      domain_api_proxy_backend_url="${2:-}"
      shift 2
      ;;
    --domain-api-proxy-nginx-conf)
      domain_api_proxy_nginx_conf="${2:-}"
      shift 2
      ;;
    --domain-api-proxy-nginx-enabled)
      domain_api_proxy_nginx_enabled="${2:-}"
      shift 2
      ;;
    --domain-api-proxy-acme-root)
      domain_api_proxy_acme_root="${2:-}"
      shift 2
      ;;
    --healthcheck)
      echo "helper-ok"
      exit 0
      ;;
    --compose-service-recreate)
      compose_service_recreate="true"
      shift 1
      ;;
    --compose-service)
      compose_service="${2:-}"
      shift 2
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
  sed -E \
    -e 's/(WECHAT_MINIAPP_APP_SECRET[=:])[[:space:]]*[^[:space:]]+/\1[REDACTED]/gI' \
    -e 's/(TENCENT_CLOUD_SECRET_ID[=:])[[:space:]]*[^[:space:]]+/\1[REDACTED]/gI' \
    -e 's/(TENCENT_CLOUD_SECRET_KEY[=:])[[:space:]]*[^[:space:]]+/\1[REDACTED]/gI' \
    -e 's/(TENCENT_SMS_APP_KEY[=:])[[:space:]]*[^[:space:]]+/\1[REDACTED]/gI' \
    -e 's/(app-secret[[:space:]]*:[[:space:]]*)[^[:space:]]+/\1[REDACTED]/gI' \
    -e 's/(accessToken[=:])[[:space:]]*[^[:space:]]+/\1[REDACTED]/gI'
}

# Only these runtime values are needed to verify the backend's effective profile.
declare -Ar SAFE_ENV_VALUE_KEYS=(
  ["SPRING_PROFILES_ACTIVE"]="1"
  ["NACOS_ENABLED"]="1"
  ["SERVER_PORT"]="1"
)

is_safe_environment_key() {
  local key="${1:-}"
  [[ -n "$key" ]] || return 1
  [[ -n "${SAFE_ENV_VALUE_KEYS[$key]:-}" ]]
}

is_safe_environment_value() {
  local key="${1:-}"
  local value="${2:-}"
  local first_character
  local last_character
  [[ -n "$value" ]] || return 1

  if [[ ${#value} -ge 2 ]]; then
    first_character="${value:0:1}"
    last_character="${value:${#value}-1:1}"
    if { [[ "$first_character" == '"' && "$last_character" == '"' ]] || [[ "$first_character" == "'" && "$last_character" == "'" ]]; }; then
      value="${value:1:${#value}-2}"
    fi
  fi

  case "$key" in
    SPRING_PROFILES_ACTIVE)
      [[ "$value" == "dev" || "$value" == "prod" || "$value" == "test" ]]
      ;;
    NACOS_ENABLED)
      [[ "$value" == "true" || "$value" == "false" ]]
      ;;
    SERVER_PORT)
      [[ "$value" =~ ^[1-9][0-9]{0,4}$ ]] && (( value <= 65535 ))
      ;;
    *)
      return 1
      ;;
  esac
}

redact_environment_output() {
  local line
  local key
  local value
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
      key="${BASH_REMATCH[1]}"
      value="${BASH_REMATCH[2]}"
      if is_safe_environment_key "$key" && is_safe_environment_value "$key" "$value"; then
        printf '%s\n' "$line"
      else
        printf '%s=[REDACTED]\n' "$key"
      fi
    elif [[ -n "$line" ]]; then
      printf '[REDACTED]\n'
    fi
  done
}

redact_compose_environment_output() {
  local line
  local compose_env_pattern
  local prefix
  local opening_quote
  local key
  local closing_quote
  local separator
  local value
  compose_env_pattern="^(([0-9]+:)?[[:space:]]*(-[[:space:]]*)?)([\"']?)([A-Za-z_][A-Za-z0-9_.-]*)([\"']?)([[:space:]]*[:=][[:space:]]*)(.*)$"
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^[0-9]+:[[:space:]]*(services:|kaipai:|environment:|ports:)$ ]]; then
      printf '%s\n' "$line"
    elif [[ "$line" =~ $compose_env_pattern ]]; then
      prefix="${BASH_REMATCH[1]}"
      opening_quote="${BASH_REMATCH[4]}"
      key="${BASH_REMATCH[5]}"
      closing_quote="${BASH_REMATCH[6]}"
      separator="${BASH_REMATCH[7]}"
      value="${BASH_REMATCH[8]}"
      if is_safe_environment_key "$key" && is_safe_environment_value "$key" "$value"; then
        printf '%s\n' "$line"
      else
        printf '%s%s%s%s%s[REDACTED]\n' "$prefix" "$opening_quote" "$key" "$closing_quote" "$separator"
      fi
    else
      printf '[REDACTED]\n'
    fi
  done
}

declare -Ar SAFE_DOCKER_LOGGING_VALUE_KEYS=(
  ["max-size"]="1"
  ["max-file"]="1"
  ["compress"]="1"
  ["mode"]="1"
)

declare -Ar SAFE_DOCKER_LOGGING_DRIVERS=(
  ["awslogs"]="1"
  ["etwlogs"]="1"
  ["fluentd"]="1"
  ["gcplogs"]="1"
  ["gelf"]="1"
  ["journald"]="1"
  ["json-file"]="1"
  ["local"]="1"
  ["none"]="1"
  ["splunk"]="1"
  ["syslog"]="1"
)

is_safe_docker_logging_value() {
  local key="$1"
  local value="$2"
  [[ -n "${SAFE_DOCKER_LOGGING_VALUE_KEYS[$key]:-}" ]] || return 1
  case "$key" in
    max-size)
      [[ "$value" =~ ^[0-9]+[kKmMgG]?$ ]]
      ;;
    max-file)
      [[ "$value" =~ ^[0-9]+$ ]]
      ;;
    compress)
      [[ "$value" == "true" || "$value" == "false" ]]
      ;;
    mode)
      [[ "$value" == "blocking" || "$value" == "non-blocking" ]]
      ;;
    *)
      return 1
      ;;
  esac
}

is_safe_docker_logging_driver() {
  local driver="${1:-}"
  [[ -n "$driver" ]] || return 1
  [[ -n "${SAFE_DOCKER_LOGGING_DRIVERS[$driver]:-}" ]]
}

redact_docker_logging_output() {
  local line
  local key
  local value
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^([A-Za-z0-9_.-]+)=(.*)$ ]]; then
      key="${BASH_REMATCH[1]}"
      value="${BASH_REMATCH[2]}"
      if [[ "$key" == "driver" ]] && is_safe_docker_logging_driver "$value"; then
        printf '%s\n' "$line"
      elif is_safe_docker_logging_value "$key" "$value"; then
        printf '%s\n' "$line"
      else
        printf '%s=[REDACTED]\n' "$key"
      fi
    elif [[ -n "$line" ]]; then
      printf '[REDACTED]\n'
    fi
  done
}

resolve_mysql_root_password() {
  local resolved_password="${KAIPAI_RELEASE_MYSQL_ROOT_PASSWORD:-${MYSQL_ROOT_PASSWORD:-}}"
  if [[ -z "$resolved_password" ]]; then
    resolved_password="$(docker exec "$mysql_container" sh -lc 'printf "%s" "${MYSQL_ROOT_PASSWORD:-}"' 2>/dev/null || true)"
  fi
  printf '%s' "$resolved_password"
}

domain_api_proxy_probe() {
  local method="$1"
  local url="$2"
  local host_header="${3:-}"
  local body="${4:-}"
  local body_file
  local err_file
  local curl_status
  body_file="$(mktemp)"
  err_file="$(mktemp)"
  local code
  set +e
  if [[ -n "$body" ]]; then
    if [[ -n "$host_header" ]]; then
      code="$(curl -sS --max-time 10 -o "$body_file" -w '%{http_code}' -X "$method" -H "Host: ${host_header}" -H 'Content-Type: application/json' -d "$body" "$url" 2>"$err_file")"
    else
      code="$(curl -sS --max-time 10 -o "$body_file" -w '%{http_code}' -X "$method" -H 'Content-Type: application/json' -d "$body" "$url" 2>"$err_file")"
    fi
  elif [[ -n "$host_header" ]]; then
    code="$(curl -sS --max-time 10 -o "$body_file" -w '%{http_code}' -X "$method" -H "Host: ${host_header}" "$url" 2>"$err_file")"
  else
    code="$(curl -sS --max-time 10 -o "$body_file" -w '%{http_code}' -X "$method" "$url" 2>"$err_file")"
  fi
  curl_status=$?
  set -e
  printf 'status=%s\n' "$code"
  if [[ "$curl_status" -ne 0 ]]; then
    printf 'curl_error=%s\n' "$(tr '\n' ' ' <"$err_file" | sed 's/[[:space:]]\+/ /g' | sed 's/[[:space:]]*$//')"
  fi
  head -c 2000 "$body_file"
  if [[ "$(wc -c <"$body_file")" -gt 2000 ]]; then
    printf '\n[truncated]\n'
  fi
  rm -f "$body_file" "$err_file"
}

domain_api_proxy_resolved_https_probe() {
  local method="$1"
  local url="$2"
  local resolve_host="$3"
  local resolve_ip="$4"
  local body="${5:-}"
  local body_file
  local err_file
  local curl_status
  body_file="$(mktemp)"
  err_file="$(mktemp)"
  local code
  set +e
  if [[ -n "$body" ]]; then
    code="$(curl -k -sS --max-time 10 --resolve "${resolve_host}:443:${resolve_ip}" -o "$body_file" -w '%{http_code}' -X "$method" -H 'Content-Type: application/json' -d "$body" "$url" 2>"$err_file")"
  else
    code="$(curl -k -sS --max-time 10 --resolve "${resolve_host}:443:${resolve_ip}" -o "$body_file" -w '%{http_code}' -X "$method" "$url" 2>"$err_file")"
  fi
  curl_status=$?
  set -e
  printf 'status=%s\n' "$code"
  if [[ "$curl_status" -ne 0 ]]; then
    printf 'curl_error=%s\n' "$(tr '\n' ' ' <"$err_file" | sed 's/[[:space:]]\+/ /g' | sed 's/[[:space:]]*$//')"
  fi
  head -c 2000 "$body_file"
  if [[ "$(wc -c <"$body_file")" -gt 2000 ]]; then
    printf '\n[truncated]\n'
  fi
  rm -f "$body_file" "$err_file"
}

collect_compose_backend_source() {
  local source_file="$1"
  if [[ ! -f "$source_file" ]]; then
    printf 'compose file not found: %s\n' "$source_file"
    return 1
  fi

  grep -nE '(^services:|^[[:space:]]{2}kaipai:|^[[:space:]]+(image:|container_name:|environment:|env_file:|ports:)|WECHAT_MINIAPP_|KAIPAI_SMS_|TENCENT_CLOUD_|TENCENT_SMS_|NACOS_ENABLED|SPRING_PROFILES_ACTIVE|SERVER_PORT)' "$source_file" 2>&1 \
    | redact_compose_environment_output
}

collect_compose_rendered_backend() {
  local runtime_root="$1"
  (
    cd "$runtime_root"
    "${compose_cmd[@]}" config 2>&1
  ) | grep -nE '(^services:|^[[:space:]]{2}kaipai:|^[[:space:]]{4}(image:|container_name:|environment:|env_file:|ports:)|WECHAT_MINIAPP_|KAIPAI_SMS_|TENCENT_CLOUD_|TENCENT_SMS_|NACOS_ENABLED|SPRING_PROFILES_ACTIVE|SERVER_PORT)' \
    | redact_compose_environment_output
}

nacos_login_request() {
  if [[ -z "$nacos_password" ]]; then
    printf 'nacos password is required via --nacos-password, KAIPAI_RELEASE_NACOS_PASSWORD, or NACOS_PASSWORD\n'
    return 1
  fi
  curl -sS -X POST "http://${nacos_server_addr}/nacos/v1/auth/login" \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "username=${nacos_username}" \
    --data-urlencode "password=${nacos_password}" 2>&1
}

nacos_extract_token() {
  sed -n 's/.*"accessToken"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p'
}

nacos_fetch_config() {
  local access_token="$1"
  local data_id_value="$2"
  curl -sS -G "http://${nacos_server_addr}/nacos/v1/cs/configs" \
    --data-urlencode "accessToken=${access_token}" \
    --data-urlencode "dataId=${data_id_value}" \
    --data-urlencode "group=${nacos_group}" \
    --data-urlencode "tenant=${nacos_namespace}" 2>&1
}

nacos_publish_config() {
  local access_token="$1"
  local data_id_value="$2"
  local upload_file="$3"
  curl -sS -X POST "http://${nacos_server_addr}/nacos/v1/cs/configs" \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "accessToken=${access_token}" \
    --data-urlencode "dataId=${data_id_value}" \
    --data-urlencode "group=${nacos_group}" \
    --data-urlencode "tenant=${nacos_namespace}" \
    --data-urlencode "type=${nacos_content_type}" \
    --data-urlencode "content@${upload_file}" 2>&1
}

if docker compose version >/dev/null 2>&1; then
  compose_cmd=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  compose_cmd=(docker-compose)
else
  echo "docker compose not available" >&2
  exit 1
fi

if [[ "$compose_service_recreate" == "true" ]]; then
  failure_reasons=()
  remote_date="$(date '+%F %T %z')"
  runtime_root="/opt/kaipai"
  case "$compose_service" in
    mysql|redis|nginx|kaipai)
      ;;
    "")
      failure_reasons+=("compose service is required")
      ;;
    *)
      failure_reasons+=("unsupported compose service: $compose_service")
      ;;
  esac

  compose_output=""
  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    compose_output="$(
      cd "$runtime_root"
      "${compose_cmd[@]}" up -d --force-recreate "$compose_service" 2>&1
    )" || failure_reasons+=("compose service recreate failed")
  fi

  docker_ps="$(docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>&1 || true)"
  compose_ps="$(
    cd "$runtime_root"
    "${compose_cmd[@]}" ps 2>&1 || true
  )"
  service_logs=""
  if [[ -n "$compose_service" ]]; then
    service_logs="$(
      cd "$runtime_root"
      "${compose_cmd[@]}" logs --tail 120 "$compose_service" 2>&1 || true
    )"
  fi

  final_status="passed"
  if [[ ${#failure_reasons[@]} -gt 0 ]]; then
    final_status="failed"
  fi
  fail_reason="$(printf '%s\n' "${failure_reasons[@]}")"

  emit_section "REMOTE_DATE" "$remote_date"
  emit_section "COMPOSE_SERVICE" "$compose_service"
  emit_section "COMPOSE_OUTPUT" "$compose_output"
  emit_section "DOCKER_PS" "$docker_ps"
  emit_section "COMPOSE_PS" "$compose_ps"
  emit_section "SERVICE_LOGS" "$service_logs"
  emit_section "FINAL_STATUS" "$final_status"
  emit_section "FAIL_REASON" "$fail_reason"

  if [[ "$final_status" != "passed" ]]; then
    exit 1
  fi
  exit 0
fi

if [[ "$runtime_diagnostics" == "true" ]]; then
  failure_reasons=()
  remote_date="$(date '+%F %T %z')"
  docker_ps="$(docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>&1)" || failure_reasons+=("docker ps failed")
  docker_inspect_state="$(docker inspect "$diagnostic_container" --format 'status={{.State.Status}} startedAt={{.State.StartedAt}} finishedAt={{.State.FinishedAt}} restartCount={{.RestartCount}} oomKilled={{.State.OOMKilled}} error={{.State.Error}} restartPolicy={{.HostConfig.RestartPolicy.Name}}' 2>&1)" || failure_reasons+=("docker inspect state failed for $diagnostic_container")
  docker_inspect_env_raw="$(docker exec "$diagnostic_container" env 2>&1)" || failure_reasons+=("docker exec env failed for $diagnostic_container")
  docker_inspect_env="$(printf '%s\n' "$docker_inspect_env_raw" | redact_environment_output)"
  docker_inspect_logging_raw="$(docker inspect "$diagnostic_container" --format '{{printf "driver=%s\n" .HostConfig.LogConfig.Type}}{{range $key, $value := .HostConfig.LogConfig.Config}}{{printf "%s=%s\n" $key $value}}{{end}}' 2>&1)" || failure_reasons+=("docker inspect logging config failed for $diagnostic_container")
  docker_inspect_logging="$(printf '%s\n' "$docker_inspect_logging_raw" | redact_docker_logging_output)"
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
  emit_section "DOCKER_INSPECT_STATE" "$docker_inspect_state"
  emit_section "DOCKER_INSPECT_ENV" "$docker_inspect_env"
  emit_section "DOCKER_INSPECT_LOGGING" "$docker_inspect_logging"
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

if [[ "$mysql_dump" == "true" ]]; then
  failure_reasons=()
  remote_date="$(date '+%F %T %z')"
  mysql_result=""
  mysql_dump_path=""
  mysql_dump_log=""
  mysql_dump_sha256=""
  mysql_dump_size=""
  mysql_root_password=""

  if [[ -z "$release_id" ]]; then
    failure_reasons+=("release id is required")
  elif [[ ! "$release_id" =~ ^[0-9]{8}-[0-9]{4,6}-mysql-dump-[a-z0-9-]+$ ]]; then
    failure_reasons+=("invalid release-id: $release_id")
  fi

  if [[ ! "$mysql_database" =~ ^[A-Za-z0-9_]+$ ]]; then
    failure_reasons+=("invalid mysql database: $mysql_database")
  fi

  if [[ ! "$mysql_container" =~ ^[A-Za-z0-9_.-]+$ ]]; then
    failure_reasons+=("invalid mysql container: $mysql_container")
  fi

  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    mysql_root_password="$(resolve_mysql_root_password)"
    if [[ -z "$mysql_root_password" ]]; then
      failure_reasons+=("mysql root password is required via KAIPAI_RELEASE_MYSQL_ROOT_PASSWORD, MYSQL_ROOT_PASSWORD, or container MYSQL_ROOT_PASSWORD")
    fi
  fi

  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    backup_root="/opt/kaipai/backups/releases/$release_id/mysql-dump"
    dump_file="$backup_root/${mysql_database}.sql"
    dump_log="$backup_root/${mysql_database}.dump.log"
    mysql_dump_path="${dump_file}.gz"
    mysql_dump_log="$dump_log"
    mkdir -p "$backup_root"
    mysql_result="$(
      docker exec -e MYSQL_PWD="$mysql_root_password" "$mysql_container" mysqldump --default-character-set=utf8mb4 -uroot \
        --single-transaction --routines --triggers --events --databases "$mysql_database" > "$dump_file" 2> "$dump_log"
      gzip -f "$dump_file"
      sha256sum "$mysql_dump_path"
    )" || failure_reasons+=("mysql dump failed")
    if [[ -f "$mysql_dump_path" ]]; then
      mysql_dump_sha256="$(sha256sum "$mysql_dump_path" | awk '{print toupper($1)}')"
      mysql_dump_size="$(wc -c < "$mysql_dump_path" | tr -d '[:space:]')"
    fi
  fi

  final_status="passed"
  if [[ ${#failure_reasons[@]} -gt 0 ]]; then
    final_status="failed"
  fi
  fail_reason="$(printf '%s\n' "${failure_reasons[@]}")"

  emit_section "REMOTE_DATE" "$remote_date"
  emit_section "MYSQL_MODE" "dump"
  emit_section "MYSQL_DATABASE" "$mysql_database"
  emit_section "MYSQL_CONTAINER" "$mysql_container"
  emit_section "MYSQL_RESULT" "$mysql_result"
  emit_section "MYSQL_DUMP_PATH" "$mysql_dump_path"
  emit_section "MYSQL_DUMP_LOG" "$mysql_dump_log"
  emit_section "MYSQL_DUMP_SHA256" "$mysql_dump_sha256"
  emit_section "MYSQL_DUMP_SIZE" "$mysql_dump_size"
  emit_section "FINAL_STATUS" "$final_status"
  emit_section "FAIL_REASON" "$fail_reason"

  if [[ "$final_status" != "passed" ]]; then
    exit 1
  fi
  exit 0
fi

if [[ "$mysql_validation" == "true" || "$mysql_apply" == "true" ]]; then
  failure_reasons=()
  remote_date="$(date '+%F %T %z')"
  mysql_mode="validation"
  if [[ "$mysql_apply" == "true" ]]; then
    mysql_mode="apply"
  fi
  mysql_result=""
  mysql_root_password=""
  if [[ -z "$mysql_script_path" ]]; then
    failure_reasons+=("mysql script path is required")
  elif [[ ! -f "$mysql_script_path" ]]; then
    failure_reasons+=("mysql script not found: $mysql_script_path")
  else
    mysql_root_password="$(resolve_mysql_root_password)"
    if [[ -z "$mysql_root_password" ]]; then
      failure_reasons+=("mysql root password is required via KAIPAI_RELEASE_MYSQL_ROOT_PASSWORD, MYSQL_ROOT_PASSWORD, or container MYSQL_ROOT_PASSWORD")
    else
      mysql_result="$(
        docker exec -i -e MYSQL_PWD="$mysql_root_password" "$mysql_container" mysql --default-character-set=utf8mb4 -uroot -D "$mysql_database" < "$mysql_script_path" 2>&1
      )" || failure_reasons+=("mysql validation failed")
    fi
  fi

  final_status="passed"
  if [[ ${#failure_reasons[@]} -gt 0 ]]; then
    final_status="failed"
  fi
  fail_reason="$(printf '%s\n' "${failure_reasons[@]}")"

  emit_section "REMOTE_DATE" "$remote_date"
  emit_section "MYSQL_MODE" "$mysql_mode"
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

  candidate_validate_output_raw=""
  if candidate_validate_output_raw="$(
    cd "$runtime_root"
    "${compose_cmd[@]}" -f "$candidate_runtime_file" config 2>&1
  )"; then
    candidate_validate_output="docker compose config validation passed"
  else
    failure_reasons+=("compose candidate validation failed")
    candidate_validate_output="docker compose config validation failed; raw output omitted"
  fi

  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    install -m 0644 "$candidate_runtime_file" "$runtime_compose_file"
  fi

  docker_inspect_env_raw="$(docker inspect kaipai-backend --format '{{range .Config.Env}}{{println .}}{{end}}' 2>&1 || true)"
  docker_inspect_env="$(printf '%s\n' "$docker_inspect_env_raw" | redact_environment_output)"
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

if [[ "$domain_api_proxy_sync" == "true" ]]; then
  if [[ -z "$release_id" || -z "$domain_api_proxy_domain" || -z "$domain_api_proxy_api_domain" || -z "$domain_api_proxy_backend_url" ]]; then
    echo "release-id, domain, api-domain and backend-url are required" >&2
    exit 1
  fi

  if [[ ! "$release_id" =~ ^[0-9]{8}-[0-9]{6}-domain-api-proxy-[a-z0-9-]+$ ]]; then
    echo "invalid release-id: $release_id" >&2
    exit 1
  fi

  failure_reasons=()
  blocked_reasons=()
  remote_date="$(date '+%F %T %z')"
  backup_root="/opt/kaipai/backups/releases/$release_id/domain-api-proxy"
  candidate_conf_file="${domain_api_proxy_nginx_conf}.candidate.${release_id}"
  root_cert_file="/etc/letsencrypt/live/${domain_api_proxy_domain}/fullchain.pem"
  root_cert_key_file="/etc/letsencrypt/live/${domain_api_proxy_domain}/privkey.pem"
  api_cert_file="/etc/letsencrypt/live/${domain_api_proxy_api_domain}/fullchain.pem"
  api_cert_key_file="/etc/letsencrypt/live/${domain_api_proxy_api_domain}/privkey.pem"
  root_cert_status="missing"
  api_cert_status="missing"

  mkdir -p "$backup_root" "$domain_api_proxy_acme_root"
  if [[ -f "$domain_api_proxy_nginx_conf" ]]; then
    cp -a "$domain_api_proxy_nginx_conf" "$backup_root/default.conf.before"
  else
    failure_reasons+=("nginx config not found: $domain_api_proxy_nginx_conf")
  fi
  if [[ -e "$domain_api_proxy_nginx_enabled" ]]; then
    cp -a "$domain_api_proxy_nginx_enabled" "$backup_root/default.enabled.before" || true
  fi

  if [[ "$domain_api_proxy_api_only" == "true" ]]; then
    root_dns_output="SKIPPED: api-only mode does not gate on ${domain_api_proxy_domain}"
  else
    root_dns_output="$(
      {
        echo "getent ahostsv4 ${domain_api_proxy_domain}"
        getent ahostsv4 "$domain_api_proxy_domain" || true
        if command -v dig >/dev/null 2>&1; then
          echo
          echo "dig @223.5.5.5 +short A ${domain_api_proxy_domain}"
          dig @223.5.5.5 +short A "$domain_api_proxy_domain" || true
        fi
      } 2>&1
    )"
  fi
  api_dns_output="$(
    {
      echo "getent ahostsv4 ${domain_api_proxy_api_domain}"
      getent ahostsv4 "$domain_api_proxy_api_domain" || true
      if command -v dig >/dev/null 2>&1; then
      echo
        echo "dig @223.5.5.5 +short A ${domain_api_proxy_api_domain}"
        dig @223.5.5.5 +short A "$domain_api_proxy_api_domain" || true
      fi
    } 2>&1
  )"
  dns_output="${root_dns_output}

${api_dns_output}"

  if [[ "$domain_api_proxy_api_only" != "true" ]] && ! printf '%s\n' "$root_dns_output" | grep -Eq '(^|[[:space:]])101\.43\.57\.62([[:space:]]|$)'; then
    blocked_reasons+=("${domain_api_proxy_domain} does not resolve to 101.43.57.62 on remote DNS")
  fi

  if [[ "$domain_api_proxy_api_only" == "true" ]]; then
    root_cert_status="skipped-api-only"
  elif [[ -f "$root_cert_file" && -f "$root_cert_key_file" ]]; then
    root_cert_status="present"
  else
    blocked_reasons+=("TLS certificate for ${domain_api_proxy_domain} is missing: ${root_cert_file}")
  fi

  if [[ -f "$api_cert_file" && -f "$api_cert_key_file" ]]; then
    api_cert_status="present"
  else
    failure_reasons+=("TLS certificate for ${domain_api_proxy_api_domain} is missing: ${api_cert_file}")
  fi

  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    python3 - \
      "$candidate_conf_file" \
      "$domain_api_proxy_domain" \
      "$domain_api_proxy_api_domain" \
      "$domain_api_proxy_backend_url" \
      "$domain_api_proxy_acme_root" \
      "$root_cert_status" \
      "$root_cert_file" \
      "$root_cert_key_file" \
      "$api_cert_file" \
      "$api_cert_key_file" \
      "$domain_api_proxy_api_only" <<'PY'
from pathlib import Path
import sys

target = Path(sys.argv[1])
domain = sys.argv[2]
api_domain = sys.argv[3]
backend_url = sys.argv[4].rstrip("/")
acme_root = sys.argv[5]
root_cert_status = sys.argv[6]
root_cert_file = sys.argv[7]
root_cert_key_file = sys.argv[8]
api_cert_file = sys.argv[9]
api_cert_key_file = sys.argv[10]
api_only = sys.argv[11] == "true"
static_root = "/opt/kaipai/nginx/html"
client_body_limit = "    client_max_body_size 120m;"

ssl_common = """    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;"""

proxy_headers = """        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;"""

root_static_locations = f"""    root {static_root};
    index index.html;

    location = /api {{
        proxy_pass {backend_url};
{proxy_headers}
    }}

    location ^~ /api/ {{
        proxy_pass {backend_url};
{proxy_headers}
    }}

    location ^~ /assets/ {{
        try_files $uri =404;
    }}

    location = /favicon.svg {{
        try_files $uri =404;
    }}

    location = /icons.svg {{
        try_files $uri =404;
    }}

    location = / {{
        return 302 /login?redirect=/dashboard/index;
    }}

    location / {{
        try_files $uri $uri/ /index.html;
    }}"""

root_http_location = (
    "    location / {\n"
    "        return 301 https://$host$request_uri;\n"
    "    }"
    if root_cert_status == "present"
    else
    root_static_locations
)

blocks = [
    f"""server {{
    listen 80;
    listen [::]:80;
    server_name {api_domain};
{client_body_limit}

    location ^~ /.well-known/acme-challenge/ {{
        root {acme_root};
        default_type \"text/plain\";
    }}

    location / {{
        return 301 https://$host$request_uri;
    }}
}}""",
]

if not api_only:
    blocks.append(f"""server {{
    listen 80;
    listen [::]:80;
    server_name {domain};
{client_body_limit}

    location ^~ /.well-known/acme-challenge/ {{
        root {acme_root};
        default_type \"text/plain\";
    }}

{root_http_location}
}}""")

blocks.append(f"""server {{
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name {api_domain};
{client_body_limit}

    ssl_certificate {api_cert_file};
    ssl_certificate_key {api_cert_key_file};

{ssl_common}

    location = / {{
        default_type application/json;
        return 200 '{{"code":200,"message":"api service ok","data":{{"service":"kaipai-api","docs":"/api/v3/api-docs"}}}}';
    }}

    location / {{
        proxy_pass {backend_url};
{proxy_headers}
    }}
}}""")

if not api_only and root_cert_status == "present":
    blocks.append(
        f"""server {{
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name {domain};
{client_body_limit}

    ssl_certificate {root_cert_file};
    ssl_certificate_key {root_cert_key_file};

{ssl_common}

{root_static_locations}
}}"""
    )

target.write_text("\n\n".join(blocks).rstrip() + "\n", encoding="utf-8")
PY
    candidate_generate_status=$?
    if [[ $candidate_generate_status -ne 0 ]]; then
      failure_reasons+=("candidate nginx config generation failed")
    fi
  fi

  candidate_preview="$(cat "$candidate_conf_file" 2>&1 || true)"
  nginx_test_output=""
  nginx_reload_output=""
  restore_test_output=""
  internal_http_docs_probe=""
  internal_http_send_code_probe=""
  internal_https_docs_probe=""
  internal_https_send_code_probe=""

  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    install -m 0644 "$candidate_conf_file" "$domain_api_proxy_nginx_conf"
    nginx_test_output="$(nginx -t 2>&1)" || failure_reasons+=("nginx config test failed")
    if [[ ${#failure_reasons[@]} -gt 0 ]]; then
      cp -a "$backup_root/default.conf.before" "$domain_api_proxy_nginx_conf" || true
      restore_test_output="$(nginx -t 2>&1 || true)"
    else
      if command -v systemctl >/dev/null 2>&1; then
        nginx_reload_output="$(systemctl reload nginx 2>&1)" || failure_reasons+=("system nginx reload failed")
      else
        nginx_reload_output="$(nginx -s reload 2>&1)" || failure_reasons+=("system nginx reload failed")
      fi
      sleep 1
    fi
  fi

  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    if [[ "$domain_api_proxy_api_only" == "true" ]]; then
      internal_http_docs_probe="SKIPPED: api-only mode uses ${domain_api_proxy_api_domain} HTTPS probes"
      internal_http_send_code_probe="SKIPPED: api-only mode uses ${domain_api_proxy_api_domain} HTTPS probes"
      internal_https_docs_probe="$(
        domain_api_proxy_resolved_https_probe GET "https://${domain_api_proxy_api_domain}/api/v3/api-docs" "$domain_api_proxy_api_domain" "127.0.0.1"
      )" || failure_reasons+=("internal api https docs probe failed")
      internal_https_send_code_probe="$(
        domain_api_proxy_resolved_https_probe POST "https://${domain_api_proxy_api_domain}/api/auth/sendCode" "$domain_api_proxy_api_domain" "127.0.0.1" '{"phone":"13800138000"}'
      )" || failure_reasons+=("internal api https sendCode probe failed")
      if ! printf '%s\n' "$internal_https_docs_probe" | sed -n '1s/^status=//p' | grep -qx '200'; then
        failure_reasons+=("internal api https docs probe did not return status=200")
      fi
      if ! printf '%s\n' "$internal_https_send_code_probe" | sed -n '1s/^status=//p' | grep -qx '200'; then
        failure_reasons+=("internal api https sendCode probe did not return status=200")
      fi
      if ! printf '%s\n' "$internal_https_send_code_probe" | grep -q '"code":[[:space:]]*200'; then
        failure_reasons+=("internal api https sendCode probe did not return business code=200")
      fi
    else
    internal_http_docs_probe="$(domain_api_proxy_probe GET 'http://127.0.0.1/api/v3/api-docs' "$domain_api_proxy_domain")" || failure_reasons+=("internal http docs probe failed")
    internal_http_send_code_probe="$(
      domain_api_proxy_probe POST 'http://127.0.0.1/api/auth/sendCode' "$domain_api_proxy_domain" '{"phone":"13800138000"}'
    )" || failure_reasons+=("internal http sendCode probe failed")
    if ! printf '%s\n' "$internal_http_docs_probe" | sed -n '1s/^status=//p' | grep -qx '200'; then
      failure_reasons+=("internal http docs probe did not return status=200")
    fi
    if ! printf '%s\n' "$internal_http_send_code_probe" | sed -n '1s/^status=//p' | grep -qx '200'; then
      failure_reasons+=("internal http sendCode probe did not return status=200")
    fi
    if ! printf '%s\n' "$internal_http_send_code_probe" | grep -q '"code":[[:space:]]*200'; then
      failure_reasons+=("internal http sendCode probe did not return business code=200")
    fi
    if [[ "$root_cert_status" == "present" ]]; then
      internal_https_docs_probe="$(curl -k -sS --max-time 10 --resolve "${domain_api_proxy_domain}:443:127.0.0.1" -i "https://${domain_api_proxy_domain}/api/v3/api-docs" 2>&1)" || failure_reasons+=("internal https docs probe failed")
    else
      internal_https_docs_probe="SKIPPED: root domain certificate is missing"
    fi
    fi
  fi

  final_status="passed"
  if [[ ${#failure_reasons[@]} -gt 0 ]]; then
    final_status="failed"
  elif [[ ${#blocked_reasons[@]} -gt 0 ]]; then
    final_status="blocked"
  fi
  fail_reason="$(printf '%s\n' "${failure_reasons[@]}")"
  block_reason="$(printf '%s\n' "${blocked_reasons[@]}")"
  rm -f "$candidate_conf_file"

  emit_section "REMOTE_DATE" "$remote_date"
  emit_section "BACKUP_PATH" "$backup_root"
  emit_section "NGINX_CONF_FILE" "$domain_api_proxy_nginx_conf"
  emit_section "DOMAIN" "$domain_api_proxy_domain"
  emit_section "API_DOMAIN" "$domain_api_proxy_api_domain"
  emit_section "BACKEND_URL" "$domain_api_proxy_backend_url"
  emit_section "DNS_OUTPUT" "$dns_output"
  emit_section "ROOT_CERT_STATUS" "$root_cert_status"
  emit_section "API_CERT_STATUS" "$api_cert_status"
  emit_section "CANDIDATE_PREVIEW" "$candidate_preview"
  emit_section "NGINX_TEST_OUTPUT" "$nginx_test_output"
  emit_section "NGINX_RELOAD_OUTPUT" "$nginx_reload_output"
  emit_section "RESTORE_TEST_OUTPUT" "$restore_test_output"
  emit_section "INTERNAL_HTTP_DOCS_PROBE" "$internal_http_docs_probe"
  emit_section "INTERNAL_HTTP_SEND_CODE_PROBE" "$internal_http_send_code_probe"
  emit_section "INTERNAL_HTTPS_DOCS_PROBE" "$internal_https_docs_probe"
  emit_section "INTERNAL_HTTPS_SEND_CODE_PROBE" "$internal_https_send_code_probe"
  emit_section "FINAL_STATUS" "$final_status"
  emit_section "FAIL_REASON" "$fail_reason"
  emit_section "BLOCK_REASON" "$block_reason"

  if [[ "$final_status" == "failed" ]]; then
    exit 1
  fi
  if [[ "$final_status" == "blocked" ]]; then
    exit 2
  fi
  exit 0
fi

if [[ "$bridge_proxy_sync" == "true" ]]; then
  if [[ -z "$release_id" || -z "$bridge_proxy_location" || -z "$bridge_proxy_pass_url" ]]; then
    echo "release-id, bridge-proxy-location and bridge-proxy-pass-url are required" >&2
    exit 1
  fi

  failure_reasons=()
  remote_date="$(date '+%F %T %z')"
  runtime_root="/opt/kaipai"
  nginx_conf_file="$runtime_root/nginx/conf/default.conf"
  candidate_conf_file="$runtime_root/nginx/conf/default.conf.candidate"
  backup_root="/opt/kaipai/backups/releases/$release_id/ai-http-bridge-proxy"
  mkdir -p "$backup_root"
  cp -a "$nginx_conf_file" "$backup_root/default.conf.before"

  python3 - "$nginx_conf_file" "$candidate_conf_file" "$bridge_proxy_location" "$bridge_proxy_pass_url" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1])
target = Path(sys.argv[2])
location = sys.argv[3].strip()
proxy_pass = sys.argv[4].strip()

text = source.read_text(encoding="utf-8")
begin = "    # AI_NOTIFICATION_HTTP_BRIDGE_PROXY_BEGIN"
end = "    # AI_NOTIFICATION_HTTP_BRIDGE_PROXY_END"
block = "\n".join(
    [
        begin,
        f"    location {location} {{",
        f"        proxy_pass {proxy_pass};",
        "        proxy_set_header Host $host;",
        "        proxy_set_header X-Real-IP $remote_addr;",
        "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
        "    }",
        end,
    ]
)

if begin in text and end in text:
    start = text.index(begin)
    stop = text.index(end) + len(end)
    updated = text[:start] + block + text[stop:]
else:
    marker = "    location / {"
    if marker in text:
        updated = text.replace(marker, block + "\n\n" + marker, 1)
    else:
        closing = text.rfind("}")
        if closing == -1:
            raise RuntimeError("failed to find server block closing brace")
        updated = text[:closing] + block + "\n" + text[closing:]

target.write_text(updated.rstrip() + "\n", encoding="utf-8")
PY
  candidate_generate_status=$?
  if [[ $candidate_generate_status -ne 0 ]]; then
    failure_reasons+=("candidate nginx config generation failed")
  fi

  candidate_preview="$(cat "$candidate_conf_file" 2>&1 || true)"
  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    install -m 0644 "$candidate_conf_file" "$nginx_conf_file"
  fi

  nginx_test_output="$(docker exec kaipai-nginx nginx -t 2>&1)" || failure_reasons+=("nginx config test failed")
  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    nginx_reload_output="$(docker exec kaipai-nginx nginx -s reload 2>&1)" || failure_reasons+=("nginx reload failed")
  else
    nginx_reload_output=""
  fi

  probe_output="$(
    curl -i -sS -X POST "http://127.0.0.1${bridge_proxy_location}" \
      -H 'Content-Type: application/json' \
      --data '{"requestId":"bridge-proxy-sync-probe","failure":{"failureId":"bridge-proxy-sync-probe"},"recipient":{"phone":"13800138000"}}' 2>&1
  )" || failure_reasons+=("bridge proxy probe failed")

  final_status="passed"
  if [[ ${#failure_reasons[@]} -gt 0 ]]; then
    final_status="failed"
  fi
  fail_reason="$(printf '%s\n' "${failure_reasons[@]}")"
  rm -f "$candidate_conf_file"

  emit_section "REMOTE_DATE" "$remote_date"
  emit_section "BACKUP_PATH" "$backup_root"
  emit_section "NGINX_CONF_FILE" "$nginx_conf_file"
  emit_section "BRIDGE_PROXY_LOCATION" "$bridge_proxy_location"
  emit_section "BRIDGE_PROXY_PASS_URL" "$bridge_proxy_pass_url"
  emit_section "CANDIDATE_PREVIEW" "$candidate_preview"
  emit_section "NGINX_TEST_OUTPUT" "$nginx_test_output"
  emit_section "NGINX_RELOAD_OUTPUT" "$nginx_reload_output"
  emit_section "PROBE_OUTPUT" "$probe_output"
  emit_section "FINAL_STATUS" "$final_status"
  emit_section "FAIL_REASON" "$fail_reason"

  if [[ "$final_status" != "passed" ]]; then
    exit 1
  fi
  exit 0
fi

if [[ "$nacos_config_scan" == "true" ]]; then
  failure_reasons=()
  remote_date="$(date '+%F %T %z')"

  if [[ -z "$nacos_data_ids" ]]; then
    failure_reasons+=("nacos data ids are required")
  fi

  nacos_login_output=""
  nacos_token=""
  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    nacos_login_output="$(nacos_login_request)" || failure_reasons+=("nacos login request failed")
    nacos_token="$(printf '%s' "$nacos_login_output" | nacos_extract_token)"
    if [[ -z "$nacos_token" ]]; then
      failure_reasons+=("nacos login did not return accessToken")
    fi
  fi

  combined_config_output=""
  config_presence_summary=""
  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    IFS=',' read -r -a data_id_array <<< "$nacos_data_ids"
    summary_lines=()
    for raw_data_id in "${data_id_array[@]}"; do
      data_id="$(printf '%s' "$raw_data_id" | xargs)"
      if [[ -z "$data_id" ]]; then
        continue
      fi
      config_text="$(
        curl -sS -G "http://${nacos_server_addr}/nacos/v1/cs/configs" \
          --data-urlencode "accessToken=${nacos_token}" \
          --data-urlencode "dataId=${data_id}" \
          --data-urlencode "group=${nacos_group}" \
          --data-urlencode "tenant=${nacos_namespace}" 2>&1
      )" || failure_reasons+=("nacos config fetch failed for ${data_id}")

      filtered_text="$config_text"
      if [[ -n "$nacos_grep" ]]; then
        filtered_text="$(printf '%s\n' "$config_text" | grep -ni "$nacos_grep" || true)"
      fi

      if [[ -z "$filtered_text" ]]; then
        filtered_text="[no matching lines]"
      fi
      filtered_text="$(printf '%s' "$filtered_text" | redact_targeted_value)"

      if printf '%s' "$config_text" | grep -qi 'WECHAT_MINIAPP_APP_ID\|wechat\.miniapp\.app-id'; then
        summary_lines+=("- ${data_id}: contains app-id")
      else
        summary_lines+=("- ${data_id}: missing app-id")
      fi
      if printf '%s' "$config_text" | grep -qi 'WECHAT_MINIAPP_APP_SECRET\|wechat\.miniapp\.app-secret'; then
        summary_lines+=("- ${data_id}: contains app-secret")
      else
        summary_lines+=("- ${data_id}: missing app-secret")
      fi

      combined_config_output="${combined_config_output}### ${data_id}
${filtered_text}

"
    done
    config_presence_summary="$(printf '%s\n' "${summary_lines[@]}")"
  fi

  final_status="passed"
  if [[ ${#failure_reasons[@]} -gt 0 ]]; then
    final_status="failed"
  fi
  fail_reason="$(printf '%s\n' "${failure_reasons[@]}")"

  emit_section "REMOTE_DATE" "$remote_date"
  emit_section "NACOS_SERVER_ADDR" "$nacos_server_addr"
  emit_section "NACOS_DATA_IDS" "$nacos_data_ids"
  emit_section "NACOS_LOGIN_OUTPUT" "$(printf '%s' "$nacos_login_output" | redact_targeted_value)"
  emit_section "NACOS_CONFIG_PRESENCE_SUMMARY" "$config_presence_summary"
  emit_section "NACOS_FILTERED_CONFIGS" "$combined_config_output"
  emit_section "FINAL_STATUS" "$final_status"
  emit_section "FAIL_REASON" "$fail_reason"

  if [[ "$final_status" != "passed" ]]; then
    exit 1
  fi
  exit 0
fi

if [[ "$nacos_config_export" == "true" ]]; then
  failure_reasons=()
  remote_date="$(date '+%F %T %z')"
  nacos_login_output=""
  nacos_token=""
  raw_config=""

  if [[ -z "$nacos_data_id" ]]; then
    failure_reasons+=("nacos data id is required")
  fi

  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    nacos_login_output="$(nacos_login_request)" || failure_reasons+=("nacos login request failed")
    nacos_token="$(printf '%s' "$nacos_login_output" | nacos_extract_token)"
    if [[ -z "$nacos_token" ]]; then
      failure_reasons+=("nacos login did not return accessToken")
    fi
  fi

  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    raw_config="$(nacos_fetch_config "$nacos_token" "$nacos_data_id")" || failure_reasons+=("nacos config fetch failed")
  fi

  final_status="passed"
  if [[ ${#failure_reasons[@]} -gt 0 ]]; then
    final_status="failed"
  fi
  fail_reason="$(printf '%s\n' "${failure_reasons[@]}")"

  emit_section "REMOTE_DATE" "$remote_date"
  emit_section "NACOS_SERVER_ADDR" "$nacos_server_addr"
  emit_section "NACOS_DATA_ID" "$nacos_data_id"
  emit_section "NACOS_RAW_CONFIG" "$(printf '%s' "$raw_config" | redact_targeted_value)"
  emit_section "NACOS_LOGIN_OUTPUT" "$(printf '%s' "$nacos_login_output" | redact_targeted_value)"
  emit_section "FINAL_STATUS" "$final_status"
  emit_section "FAIL_REASON" "$fail_reason"

  if [[ "$final_status" != "passed" ]]; then
    exit 1
  fi
  exit 0
fi

if [[ "$nacos_config_sync" == "true" ]]; then
  failure_reasons=()
  remote_date="$(date '+%F %T %z')"
  nacos_login_output=""
  nacos_token=""
  before_config=""
  after_config=""
  publish_output=""
  release_root="/opt/kaipai/builds/$release_id"
  backup_root="/opt/kaipai/backups/releases/$release_id/nacos-config"
  archived_upload_path="$release_root/${nacos_data_id}.candidate"

  if [[ -z "$release_id" || -z "$nacos_data_id" || -z "$nacos_upload_path" ]]; then
    failure_reasons+=("release-id, nacos-data-id and nacos-upload-path are required")
  fi

  if [[ ${#failure_reasons[@]} -eq 0 && ! "$release_id" =~ ^[0-9]{8}-[0-9]{6}-backend-nacos-[a-z0-9-]+$ ]]; then
    failure_reasons+=("invalid release-id: $release_id")
  fi

  if [[ ${#failure_reasons[@]} -eq 0 && ! -f "$nacos_upload_path" ]]; then
    failure_reasons+=("uploaded nacos candidate not found: $nacos_upload_path")
  fi

  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    mkdir -p "$release_root" "$backup_root"
    nacos_login_output="$(nacos_login_request)" || failure_reasons+=("nacos login request failed")
    nacos_token="$(printf '%s' "$nacos_login_output" | nacos_extract_token)"
    if [[ -z "$nacos_token" ]]; then
      failure_reasons+=("nacos login did not return accessToken")
    fi
  fi

  if [[ ${#failure_reasons[@]} -eq 0 ]]; then
    before_config="$(nacos_fetch_config "$nacos_token" "$nacos_data_id")" || failure_reasons+=("nacos config fetch before publish failed")
    printf '%s' "$before_config" > "$backup_root/${nacos_data_id}.before"
    install -m 0644 "$nacos_upload_path" "$archived_upload_path"
    publish_output="$(nacos_publish_config "$nacos_token" "$nacos_data_id" "$nacos_upload_path")" || failure_reasons+=("nacos publish request failed")
    after_config="$(nacos_fetch_config "$nacos_token" "$nacos_data_id")" || failure_reasons+=("nacos config fetch after publish failed")
    printf '%s' "$after_config" > "$release_root/${nacos_data_id}.after"
    rm -f "$nacos_upload_path"
  fi

  final_status="passed"
  if [[ ${#failure_reasons[@]} -gt 0 ]]; then
    final_status="failed"
  fi
  fail_reason="$(printf '%s\n' "${failure_reasons[@]}")"

  before_filtered="$before_config"
  after_filtered="$after_config"
  if [[ -n "$nacos_grep" ]]; then
    before_filtered="$(printf '%s\n' "$before_config" | grep -ni "$nacos_grep" || true)"
    after_filtered="$(printf '%s\n' "$after_config" | grep -ni "$nacos_grep" || true)"
    [[ -n "$before_filtered" ]] || before_filtered="[no matching lines]"
    [[ -n "$after_filtered" ]] || after_filtered="[no matching lines]"
  fi

  emit_section "REMOTE_DATE" "$remote_date"
  emit_section "BACKUP_PATH" "$backup_root"
  emit_section "RELEASE_ROOT" "$release_root"
  emit_section "NACOS_SERVER_ADDR" "$nacos_server_addr"
  emit_section "NACOS_DATA_ID" "$nacos_data_id"
  emit_section "NACOS_GROUP" "$nacos_group"
  emit_section "NACOS_NAMESPACE" "$nacos_namespace"
  emit_section "NACOS_LOGIN_OUTPUT" "$(printf '%s' "$nacos_login_output" | redact_targeted_value)"
  emit_section "BEFORE_CONFIG" "$(printf '%s' "$before_config" | redact_targeted_value)"
  emit_section "AFTER_CONFIG" "$(printf '%s' "$after_config" | redact_targeted_value)"
  emit_section "BEFORE_FILTERED" "$(printf '%s' "$before_filtered" | redact_targeted_value)"
  emit_section "AFTER_FILTERED" "$(printf '%s' "$after_filtered" | redact_targeted_value)"
  emit_section "PUBLISH_OUTPUT" "$(printf '%s' "$publish_output" | redact_targeted_value)"
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
docker_inspect_env_raw="$(docker inspect "$container_name" --format '{{range .Config.Env}}{{println .}}{{end}}')"
docker_inspect_env="$(printf '%s\n' "$docker_inspect_env_raw" | redact_environment_output)"
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
if [[ -z "${KAIPAI_ADMIN_SMOKE_PASSWORD:-}" ]]; then
  admin_login_probe="status=000
KAIPAI_ADMIN_SMOKE_PASSWORD is required for admin login smoke"
else
  admin_login_probe="$(http_probe POST 'http://127.0.0.1:8080/api/admin/auth/login' "$(python3 - <<'PY'
import json
import os

print(json.dumps({"account": "admin", "password": os.environ["KAIPAI_ADMIN_SMOKE_PASSWORD"]}))
PY
)")"
fi
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
