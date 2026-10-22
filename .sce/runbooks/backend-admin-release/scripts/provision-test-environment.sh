#!/usr/bin/env bash
set -Eeuo pipefail

# Provision only the isolated test runtime. Run on the target host as root.

candidate_id=""
candidate_root=""
test_api_host="test-api.kplyyk.com"
test_admin_host="test.kplyyk.com"
test_bucket_name="${KAIPAI_TEST_COS_BUCKET_NAME:-kaipai-test-1412601014}"
runtime_root="/opt/kaipai/test"
test_html_root="/opt/kaipai/nginx/html-test"
nginx_conf="/etc/nginx/conf.d/kaipai-test.conf"
acme_conf="/etc/nginx/conf.d/kaipai-test-acme.conf"
acme_root="/var/www/letsencrypt"
cert_name="kaipai-test-kplyyk"
network_name="kaipai_default"
dry_run="false"

usage() {
  cat <<'EOF'
Usage: provision-test-environment.sh --candidate-id ID [options]

Options:
  --candidate-root PATH    Candidate staging root (default: /home/kaipaile/test-release/ID)
  --test-api-host HOST     Test API hostname
  --test-admin-host HOST   Test admin hostname
  --dry-run                Print the bounded plan without touching the host
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --candidate-id) candidate_id="${2:-}"; shift 2 ;;
    --candidate-root) candidate_root="${2:-}"; shift 2 ;;
    --test-api-host) test_api_host="${2:-}"; shift 2 ;;
    --test-admin-host) test_admin_host="${2:-}"; shift 2 ;;
    --dry-run) dry_run="true"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$candidate_id" || ! "$candidate_id" =~ ^[0-9]{8}-[0-9]{4,6}-v3-draft$ ]]; then
  echo "candidate-id must match YYYYMMDD-HHMM-v3-draft" >&2
  exit 1
fi

candidate_root="${candidate_root:-/home/kaipaile/test-release/$candidate_id}"
jar_path="$candidate_root/kaipai-backend-1.0.0-SNAPSHOT.jar"
admin_source="$candidate_root/admin"
compose_file="$runtime_root/docker-compose.yml"
dockerfile="$runtime_root/Dockerfile"
test_secret_env="$runtime_root/test-secrets.env"
backup_root="/opt/kaipai/backups/releases/$candidate_id/test-environment"

if [[ "$dry_run" == "true" ]]; then
  printf 'PLAN=TEST_ONLY\nCANDIDATE=%s\nCANDIDATE_ROOT=%s\nTEST_CONTAINER=kaipai-backend-test\nTEST_PORT=18080\nTEST_DATABASE=kaipai_test\nTEST_REDIS_DATABASE=1\nTEST_BUCKET=%s\nTEST_ADMIN_ROOT=%s\nTEST_API_HOST=%s\nTEST_ADMIN_HOST=%s\nNGINX_CONFIG=%s\nPRODUCTION_MUTATION=FORBIDDEN\n' \
    "$candidate_id" "$candidate_root" "$test_bucket_name" "$test_html_root" "$test_api_host" "$test_admin_host" "$nginx_conf"
  exit 0
fi

if (( EUID != 0 )); then
  echo "root is required; invoke this script through the approved root entry" >&2
  exit 1
fi

for value in "$test_api_host" "$test_admin_host"; do
  if [[ ! "$value" =~ ^[A-Za-z0-9.-]+$ ]]; then
    echo "invalid test hostname" >&2
    exit 1
  fi
done

for required in "$jar_path" "$admin_source/index.html"; do
  [[ -f "$required" ]] || { echo "candidate file missing: $required" >&2; exit 1; }
done

command -v docker >/dev/null || { echo "docker is required" >&2; exit 1; }
command -v nginx >/dev/null || { echo "host nginx is required" >&2; exit 1; }

if docker compose version >/dev/null 2>&1; then
  compose_cmd=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  compose_cmd=(docker-compose)
else
  echo "docker compose is required" >&2
  exit 1
fi

prod_id="$(docker inspect --format '{{.Id}}' kaipai-backend 2>/dev/null || true)"
prod_status="$(docker inspect --format '{{.State.Status}}' kaipai-backend 2>/dev/null || true)"
prod_ports="$(docker inspect --format '{{json .HostConfig.PortBindings}}' kaipai-backend 2>/dev/null || true)"
[[ -n "$prod_id" && "$prod_status" == "running" ]] || { echo "production container is not running" >&2; exit 1; }
printf '%s\n' "$prod_ports" | grep -q '8080' || { echo "production port 8080 was not observed" >&2; exit 1; }
docker network inspect "$network_name" >/dev/null 2>&1 || { echo "required docker network is missing: $network_name" >&2; exit 1; }

prod_env="$(docker inspect kaipai-backend --format '{{range .Config.Env}}{{println .}}{{end}}')"
test_secret_id="$(printf '%s\n' "$prod_env" | sed -n 's/^TENCENT_CLOUD_SECRET_ID=//p' | head -1)"
test_secret_key="$(printf '%s\n' "$prod_env" | sed -n 's/^TENCENT_CLOUD_SECRET_KEY=//p' | head -1)"
prod_cos_region="$(printf '%s\n' "$prod_env" | sed -n 's/^TENCENT_COS_REGION=//p' | head -1)"
prod_cos_bucket="$(printf '%s\n' "$prod_env" | sed -n 's/^TENCENT_COS_BUCKET_NAME=//p' | head -1)"
test_wechat_app_id="$(printf '%s\n' "$prod_env" | sed -n 's/^WECHAT_MINIAPP_APP_ID=//p' | head -1)"
test_wechat_app_secret="$(printf '%s\n' "$prod_env" | sed -n 's/^WECHAT_MINIAPP_APP_SECRET=//p' | head -1)"
[[ -n "$test_secret_id" && -n "$test_secret_key" ]] || { echo "test COS credentials are unavailable from the approved runtime source" >&2; exit 1; }
if [[ -n "$prod_cos_region" && "$prod_cos_bucket" =~ -([0-9]+)$ ]]; then
  prod_cos_appid="${BASH_REMATCH[1]}"
else
  echo "production COS region or bucket appid is unavailable" >&2
  exit 1
fi
[[ "$test_wechat_app_id" =~ ^wx[A-Za-z0-9]{16}$ && ${#test_wechat_app_secret} -ge 16 ]] || {
  echo "test WeChat credentials are unavailable or invalid in the approved runtime source" >&2
  exit 1
}
[[ "$test_bucket_name" == "kaipai-test-$prod_cos_appid" ]] || { echo "test COS bucket does not match the approved appid" >&2; exit 1; }
[[ "$test_secret_id" != *$'\n'* && "$test_secret_id" != *$'\r'* && "$test_secret_key" != *$'\n'* && "$test_secret_key" != *$'\r'* ]] || {
  echo "test COS credentials contain invalid line breaks" >&2
  exit 1
}
[[ "$test_wechat_app_id" != *$'\n'* && "$test_wechat_app_id" != *$'\r'* && "$test_wechat_app_secret" != *$'\n'* && "$test_wechat_app_secret" != *$'\r'* ]] || {
  echo "test WeChat credentials contain invalid line breaks" >&2
  exit 1
}

if ss -ltn 2>/dev/null | grep -q ':18080 '; then
  existing_test="$(docker ps --format '{{.Names}}' | grep -x 'kaipai-backend-test' || true)"
  [[ -n "$existing_test" ]] || { echo "port 18080 is occupied by a non-test process" >&2; exit 1; }
fi

timestamp="$(date '+%Y%m%d-%H%M%S')"
backup_root="$backup_root/$timestamp"
mkdir -p "$backup_root" "$runtime_root/backend" "$test_html_root"
if [[ -f "$nginx_conf" ]]; then cp -a "$nginx_conf" "$backup_root/kaipai-test.conf.before"; fi
if [[ -d "$test_html_root" ]]; then tar -C "$test_html_root" -czf "$backup_root/html-test.before.tar.gz" .; fi
if [[ -f "$compose_file" ]]; then cp -a "$compose_file" "$backup_root/docker-compose.yml.before"; fi

install -m 0644 "$jar_path" "$runtime_root/backend/app.jar"
rm -rf "$test_html_root"/*
cp -a "$admin_source"/. "$test_html_root"/
umask 077
printf 'TENCENT_CLOUD_SECRET_ID=%s\nTENCENT_CLOUD_SECRET_KEY=%s\nWECHAT_MINIAPP_APP_ID=%s\nWECHAT_MINIAPP_APP_SECRET=%s\n' \
  "$test_secret_id" "$test_secret_key" "$test_wechat_app_id" "$test_wechat_app_secret" >"$test_secret_env"
chmod 0600 "$test_secret_env"

cat >"$dockerfile" <<'EOF'
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY backend/app.jar app.jar
EXPOSE 18080
ENTRYPOINT ["java", "-jar", "app.jar"]
EOF

cat >"$compose_file" <<EOF
services:
  kaipai-test:
    build:
      context: $runtime_root
      dockerfile: Dockerfile
    container_name: kaipai-backend-test
    restart: unless-stopped
    env_file:
      - $test_secret_env
    ports:
      - "18080:18080"
    mem_limit: 1g
    cpus: 1.0
    environment:
      NACOS_ENABLED: "true"
      SPRING_PROFILES_ACTIVE: test
      SERVER_PORT: "18080"
      SPRING_DATASOURCE_URL: jdbc:mysql://kaipai-mysql:3306/kaipai_test?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true&useSSL=false&connectTimeout=3000&socketTimeout=3000
      SPRING_DATASOURCE_USERNAME: root
      SPRING_DATA_REDIS_HOST: kaipai-redis
      SPRING_DATA_REDIS_PORT: "6379"
      SPRING_DATA_REDIS_DATABASE: "1"
      KAIPAI_SMS_PROVIDER_CODE: dev
      TENCENT_FACEID_ENABLED: "false"
      AI_PROFILE_CARD_PROVIDER_CODE: disabled
      TENCENT_COS_REGION: "$prod_cos_region"
      TENCENT_COS_BUCKET_NAME: "$test_bucket_name"
      TENCENT_COS_PRIVATE_BUCKET_NAME: "$test_bucket_name"
      COS_BUCKET_NAME: "$test_bucket_name"
    networks:
      - $network_name
networks:
  $network_name:
    external: true
    name: $network_name
EOF

if ! "${compose_cmd[@]}" -f "$compose_file" up -d --build kaipai-test >"$backup_root/compose-up.log" 2>&1; then
  echo "test compose startup failed; see $backup_root/compose-up.log" >&2
  exit 1
fi

test_container_id="$(docker inspect --format '{{.Id}}' kaipai-backend-test)"
test_status="$(docker inspect --format '{{.State.Status}}' kaipai-backend-test)"
[[ "$test_status" == "running" ]] || { echo "test container is not running" >&2; exit 1; }

test_env="$(docker inspect kaipai-backend-test --format '{{range .Config.Env}}{{println .}}{{end}}')"
printf '%s\n' "$test_env" | grep -qx 'SPRING_PROFILES_ACTIVE=test' || { echo "test profile missing" >&2; exit 1; }
printf '%s\n' "$test_env" | grep -qx 'NACOS_ENABLED=true' || { echo "Nacos is not enabled for test" >&2; exit 1; }
printf '%s\n' "$test_env" | grep -qx 'SERVER_PORT=18080' || { echo "test port missing" >&2; exit 1; }
printf '%s\n' "$test_env" | grep -qx "TENCENT_COS_REGION=$prod_cos_region" || { echo "test COS region missing" >&2; exit 1; }
printf '%s\n' "$test_env" | grep -qx "TENCENT_COS_PRIVATE_BUCKET_NAME=$test_bucket_name" || { echo "test COS bucket missing" >&2; exit 1; }
printf '%s\n' "$test_env" | grep -q '^TENCENT_CLOUD_SECRET_ID=.' || { echo "test COS secret id missing" >&2; exit 1; }
printf '%s\n' "$test_env" | grep -q '^TENCENT_CLOUD_SECRET_KEY=.' || { echo "test COS secret key missing" >&2; exit 1; }
printf '%s\n' "$test_env" | grep -q '^WECHAT_MINIAPP_APP_ID=.' || { echo "test WeChat appId missing" >&2; exit 1; }
printf '%s\n' "$test_env" | grep -q '^WECHAT_MINIAPP_APP_SECRET=.' || { echo "test WeChat appSecret missing" >&2; exit 1; }
if printf '%s\n' "$test_env" | grep -q 'kaipai_prod'; then
  echo "test container references production database" >&2
  exit 1
fi

test_api_ready="false"
for ((attempt = 1; attempt <= 60; attempt++)); do
  if curl -fsS --max-time 5 \
    -o "$backup_root/test-api-docs.json" \
    http://127.0.0.1:18080/api/v3/api-docs \
    2>"$backup_root/test-api-probe-last-error.log"; then
    test_api_ready="true"
    break
  fi
  sleep 2
done
if [[ "$test_api_ready" != "true" ]]; then
  docker logs --tail 120 kaipai-backend-test >"$backup_root/test-container.log" 2>&1 || true
  echo "test API docs probe failed" >&2
  exit 1
fi

mkdir -p "$acme_root/.well-known/acme-challenge"
cert_dir="/etc/letsencrypt/live/$cert_name"
if [[ ! -f "$cert_dir/fullchain.pem" || ! -f "$cert_dir/privkey.pem" ]]; then
  command -v certbot >/dev/null || { echo "test certificate missing and certbot is unavailable" >&2; exit 1; }
  cat >"$acme_conf" <<EOF
server {
    listen 80;
    server_name $test_api_host $test_admin_host;
    location ^~ /.well-known/acme-challenge/ { root $acme_root; default_type text/plain; }
    location / { return 404; }
}
EOF
  nginx -t >/dev/null
  systemctl reload nginx
  certbot certonly --webroot -w "$acme_root" --cert-name "$cert_name" -d "$test_api_host" -d "$test_admin_host" --non-interactive --agree-tos --register-unsafely-without-email >"$backup_root/certbot.log" 2>&1 || {
    rm -f "$acme_conf"
    nginx -t >/dev/null && systemctl reload nginx
    echo "test certificate issuance failed; see $backup_root/certbot.log" >&2
    exit 1
  }
  rm -f "$acme_conf"
fi

openssl x509 -in "$cert_dir/fullchain.pem" -noout -ext subjectAltName >"$backup_root/test-certificate-san.txt"
grep -q "$test_api_host" "$backup_root/test-certificate-san.txt" || { echo "certificate SAN missing test API host" >&2; exit 1; }
grep -q "$test_admin_host" "$backup_root/test-certificate-san.txt" || { echo "certificate SAN missing test admin host" >&2; exit 1; }

cat >"$nginx_conf.candidate" <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name $test_api_host $test_admin_host;
    location ^~ /.well-known/acme-challenge/ { root $acme_root; default_type text/plain; }
    location / { return 301 https://\$host\$request_uri; }
}
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name $test_api_host;
    ssl_certificate $cert_dir/fullchain.pem;
    ssl_certificate_key $cert_dir/privkey.pem;
    location / {
        proxy_pass http://127.0.0.1:18080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name $test_admin_host;
    ssl_certificate $cert_dir/fullchain.pem;
    ssl_certificate_key $cert_dir/privkey.pem;
    root $test_html_root;
    index index.html;
    location ^~ /api/ {
        proxy_pass http://127.0.0.1:18080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    location / { try_files \$uri \$uri/ /index.html; }
}
EOF

nginx -t -c /etc/nginx/nginx.conf >/dev/null
install -m 0644 "$nginx_conf.candidate" "$nginx_conf"
rm -f "$nginx_conf.candidate"
if ! nginx -t -c /etc/nginx/nginx.conf >"$backup_root/nginx-test.log" 2>&1; then
  if [[ -f "$backup_root/kaipai-test.conf.before" ]]; then install -m 0644 "$backup_root/kaipai-test.conf.before" "$nginx_conf"; else rm -f "$nginx_conf"; fi
  nginx -t -c /etc/nginx/nginx.conf >/dev/null && systemctl reload nginx || true
  echo "test nginx config failed; see $backup_root/nginx-test.log" >&2
  exit 1
fi
systemctl reload nginx

api_status="$(curl --fail --silent --show-error --max-time 20 -o "$backup_root/public-api-docs.json" -w '%{http_code}' "https://$test_api_host/api/v3/api-docs")"
admin_status="$(curl --fail --silent --show-error --max-time 20 -o "$backup_root/public-admin.html" -w '%{http_code}' "https://$test_admin_host/")"
[[ "$api_status" == "200" && "$admin_status" == "200" ]] || { echo "public test probes failed: api=$api_status admin=$admin_status" >&2; exit 1; }

post_prod_id="$(docker inspect --format '{{.Id}}' kaipai-backend)"
post_prod_status="$(docker inspect --format '{{.State.Status}}' kaipai-backend)"
[[ "$post_prod_id" == "$prod_id" && "$post_prod_status" == "running" ]] || { echo "production container identity changed" >&2; exit 1; }

printf 'FINAL_STATUS=passed\nCANDIDATE=%s\nTEST_CONTAINER=kaipai-backend-test\nTEST_CONTAINER_ID=%s\nTEST_PORT=18080\nTEST_DATABASE=kaipai_test\nTEST_REDIS_DATABASE=1\nTEST_BUCKET=%s\nTEST_API_STATUS=%s\nTEST_ADMIN_STATUS=%s\nCERT_SAN_FILE=%s\nBACKUP_ROOT=%s\nPRODUCTION_CONTAINER_UNCHANGED=true\n' \
  "$candidate_id" "$test_container_id" "$test_bucket_name" "$api_status" "$admin_status" "$backup_root/test-certificate-san.txt" "$backup_root"
