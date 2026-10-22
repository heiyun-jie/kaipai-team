import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SECRET_FILE = ROOT / ".sce" / "config" / "local-secrets" / "tencent-cloud-console.env"
DEFAULT_PUBLIC_IP = "101.43.57.62"
DEFAULT_REGIONS = (
    "ap-beijing",
    "ap-shanghai",
    "ap-guangzhou",
    "ap-chengdu",
    "ap-chongqing",
    "ap-nanjing",
)
TAT_VERSION = "2020-10-28"
CVM_VERSION = "2017-03-12"
LIGHTHOUSE_VERSION = "2020-03-24"


@dataclass(frozen=True)
class Credentials:
    secret_id: str
    secret_key: str


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_credentials(path: Path) -> Credentials:
    values = load_env_file(path)
    secret_id = os.environ.get("TENCENT_CLOUD_SECRET_ID") or values.get("TENCENT_CLOUD_SECRET_ID", "")
    secret_key = os.environ.get("TENCENT_CLOUD_SECRET_KEY") or values.get("TENCENT_CLOUD_SECRET_KEY", "")
    if not secret_id or not secret_key:
        raise RuntimeError("Tencent Cloud API credentials are missing")
    return Credentials(secret_id=secret_id, secret_key=secret_key)


def sha256_hex(value: str | bytes) -> str:
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(raw).hexdigest()


def sign(key: bytes, message: str) -> bytes:
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()


def call_api(
    credentials: Credentials,
    *,
    service: str,
    version: str,
    action: str,
    region: str,
    payload: dict,
) -> dict:
    host = f"{service}.tencentcloudapi.com"
    endpoint = f"https://{host}"
    timestamp = int(time.time())
    date = datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m-%d")
    body = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
    content_type = "application/json; charset=utf-8"
    canonical_headers = f"content-type:{content_type}\nhost:{host}\nx-tc-action:{action.lower()}\n"
    signed_headers = "content-type;host;x-tc-action"
    canonical_request = "\n".join(
        ["POST", "/", "", canonical_headers, signed_headers, sha256_hex(body)]
    )
    credential_scope = f"{date}/{service}/tc3_request"
    string_to_sign = "\n".join(
        ["TC3-HMAC-SHA256", str(timestamp), credential_scope, sha256_hex(canonical_request)]
    )
    secret_date = sign(("TC3" + credentials.secret_key).encode("utf-8"), date)
    secret_service = sign(secret_date, service)
    secret_signing = sign(secret_service, "tc3_request")
    signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    authorization = (
        "TC3-HMAC-SHA256 "
        f"Credential={credentials.secret_id}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )
    headers = {
        "Authorization": authorization,
        "Content-Type": content_type,
        "Host": host,
        "X-TC-Action": action,
        "X-TC-Timestamp": str(timestamp),
        "X-TC-Version": version,
        "X-TC-Region": region,
    }
    request = urllib.request.Request(endpoint, data=body.encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            parsed = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Tencent Cloud API HTTP {exc.code}: {error_body[:800]}") from exc
    response_payload = parsed.get("Response", {})
    if "Error" in response_payload:
        error = response_payload["Error"]
        raise RuntimeError(f"Tencent Cloud API {action} failed: {error.get('Code')}: {error.get('Message')}")
    return response_payload


def discover_instance(credentials: Credentials, public_ip: str, regions: tuple[str, ...]) -> tuple[str, str, str]:
    matches: list[tuple[str, str, str]] = []
    for region in regions:
        response = call_api(
            credentials,
            service="cvm",
            version=CVM_VERSION,
            action="DescribeInstances",
            region=region,
            payload={"Filters": [{"Name": "public-ip-address", "Values": [public_ip]}], "Limit": 20},
        )
        for instance in response.get("InstanceSet", []):
            if public_ip in instance.get("PublicIpAddresses", []):
                matches.append((region, instance["InstanceId"], "cvm"))
        lighthouse_response = call_api(
            credentials,
            service="lighthouse",
            version=LIGHTHOUSE_VERSION,
            action="DescribeInstances",
            region=region,
            payload={"Limit": 100},
        )
        for instance in lighthouse_response.get("InstanceSet", []):
            if public_ip in instance.get("PublicAddresses", []):
                matches.append((region, instance["InstanceId"], "lighthouse"))
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one Tencent Cloud instance for target IP; found {len(matches)}")
    return matches[0]


def require_tat_online(credentials: Credentials, region: str, instance_id: str) -> str:
    response = call_api(
        credentials,
        service="tat",
        version=TAT_VERSION,
        action="DescribeAutomationAgentStatus",
        region=region,
        payload={"InstanceIds": [instance_id]},
    )
    statuses = response.get("AutomationAgentSet", [])
    if len(statuses) != 1:
        raise RuntimeError(f"expected one TAT agent status; found {len(statuses)}")
    status = statuses[0].get("AgentStatus", "")
    if status.lower() != "online":
        raise RuntimeError(f"TAT agent is not online: {status or 'unknown'}")
    return status


def build_remote_script(release_id: str) -> str:
    if not release_id.startswith("test-wechat-") or not release_id.replace("-", "").isalnum():
        raise RuntimeError("invalid release id")
    return f"""#!/usr/bin/env bash
set -euo pipefail

release_id={release_id!r}
runtime_root=/opt/kaipai/test
compose_file="$runtime_root/docker-compose.yml"
secret_env="$runtime_root/test-secrets.env"
test_service=kaipai-test
test_container=kaipai-backend-test
prod_container=kaipai-backend
backup_root="$runtime_root/backups/wechat-login/$release_id"
candidate_env="$(mktemp /run/kaipai-test-env.XXXXXX)"
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

cleanup() {{
  rm -f "$candidate_env"
}}
rollback_on_error() {{
  local exit_code=$?
  if [[ "$rollback_needed" == "true" && -f "$backup_root/test-secrets.env.before" ]]; then
    install -o root -g root -m 0600 "$backup_root/test-secrets.env.before" "$secret_env"
    "${{compose_cmd[@]}}" -f "$compose_file" up -d --force-recreate "$test_service" >/dev/null 2>&1 || true
  fi
  cleanup
  exit "$exit_code"
}}
trap rollback_on_error EXIT

[[ -f "$compose_file" && -f "$secret_env" ]] || {{ echo 'FINAL_STATUS=failed'; echo 'FAIL_REASON=test runtime files missing'; exit 1; }}
prod_before="$(docker inspect --format '{{{{.Id}}}}|{{{{.State.StartedAt}}}}|{{{{.RestartCount}}}}' "$prod_container")"
test_before="$(docker inspect --format '{{{{.Id}}}}|{{{{.State.StartedAt}}}}|{{{{.RestartCount}}}}' "$test_container")"

prod_env="$(docker inspect "$prod_container" --format '{{{{range .Config.Env}}}}{{{{println .}}}}{{{{end}}}}')"
app_id="$(printf '%s\n' "$prod_env" | sed -n 's/^WECHAT_MINIAPP_APP_ID=//p' | head -1)"
app_secret="$(printf '%s\n' "$prod_env" | sed -n 's/^WECHAT_MINIAPP_APP_SECRET=//p' | head -1)"
[[ "$app_id" =~ ^wx[A-Za-z0-9]{{16}}$ ]] || {{ echo 'FINAL_STATUS=failed'; echo 'FAIL_REASON=invalid test app id'; exit 1; }}
[[ ${{#app_secret}} -ge 16 && "$app_secret" != *$'\n'* && "$app_secret" != *$'\r'* ]] || {{ echo 'FINAL_STATUS=failed'; echo 'FAIL_REASON=invalid test app secret'; exit 1; }}

mkdir -p "$backup_root"
cp -a "$secret_env" "$backup_root/test-secrets.env.before"
grep -Ev '^WECHAT_MINIAPP_(APP_ID|APP_SECRET)=' "$secret_env" >"$candidate_env"
printf 'WECHAT_MINIAPP_APP_ID=%s\nWECHAT_MINIAPP_APP_SECRET=%s\n' "$app_id" "$app_secret" >>"$candidate_env"
install -o root -g root -m 0600 "$candidate_env" "$secret_env"
rollback_needed=true

"${{compose_cmd[@]}}" -f "$compose_file" up -d --force-recreate "$test_service" >/dev/null
ready=false
for _ in $(seq 1 60); do
  if curl -fsS --max-time 5 -o /dev/null http://127.0.0.1:18080/api/v3/api-docs; then
    ready=true
    break
  fi
  sleep 2
done
[[ "$ready" == "true" ]] || {{ echo 'FINAL_STATUS=failed'; echo 'FAIL_REASON=test API did not become ready'; exit 1; }}

test_env="$(docker inspect "$test_container" --format '{{{{range .Config.Env}}}}{{{{println .}}}}{{{{end}}}}')"
runtime_app_id="$(printf '%s\n' "$test_env" | sed -n 's/^WECHAT_MINIAPP_APP_ID=//p' | head -1)"
runtime_app_secret="$(printf '%s\n' "$test_env" | sed -n 's/^WECHAT_MINIAPP_APP_SECRET=//p' | head -1)"
printf '%s\n' "$test_env" | grep -qx 'SPRING_PROFILES_ACTIVE=test'
printf '%s\n' "$test_env" | grep -qx 'SERVER_PORT=18080'
printf '%s\n' "$test_env" | grep -qx 'SPRING_DATA_REDIS_DATABASE=1'
printf '%s\n' "$test_env" | grep '^SPRING_DATASOURCE_URL=' | grep -q 'kaipai_test'
[[ "$runtime_app_id" == "$app_id" && "$runtime_app_secret" == "$app_secret" ]]

prod_after="$(docker inspect --format '{{{{.Id}}}}|{{{{.State.StartedAt}}}}|{{{{.RestartCount}}}}' "$prod_container")"
test_after="$(docker inspect --format '{{{{.Id}}}}|{{{{.State.StartedAt}}}}|{{{{.RestartCount}}}}' "$test_container")"
[[ "$prod_after" == "$prod_before" ]] || {{ echo 'FINAL_STATUS=failed'; echo 'FAIL_REASON=production container changed'; exit 1; }}

rollback_needed=false
trap - EXIT
cleanup
echo 'FINAL_STATUS=passed'
echo "PROD_BEFORE=$prod_before"
echo "PROD_AFTER=$prod_after"
echo "TEST_BEFORE=$test_before"
echo "TEST_AFTER=$test_after"
echo "APP_ID_SHA256=$(printf '%s' "$app_id" | sha256sum | cut -d' ' -f1 | tr '[:lower:]' '[:upper:]')"
echo "APP_SECRET_SHA256=$(printf '%s' "$app_secret" | sha256sum | cut -d' ' -f1 | tr '[:lower:]' '[:upper:]')"
echo "SECRET_FILE_MODE=$(stat -c '%a|%U|%G' "$secret_env")"
echo 'TEST_DATABASE=kaipai_test'
echo 'TEST_REDIS_DATABASE=1'
echo "BACKUP_ROOT=$backup_root"
"""


def run_command(credentials: Credentials, region: str, instance_id: str, script: str) -> tuple[str, str]:
    response = call_api(
        credentials,
        service="tat",
        version=TAT_VERSION,
        action="RunCommand",
        region=region,
        payload={
            "Content": base64.b64encode(script.encode("utf-8")).decode("ascii"),
            "InstanceIds": [instance_id],
            "CommandName": "kaipai-test-wechat-config",
            "CommandType": "SHELL",
            "WorkingDirectory": "/root",
            "Timeout": 300,
            "SaveCommand": False,
            "EnableParameter": False,
        },
    )
    invocation_id = response.get("InvocationId", "")
    command_id = response.get("CommandId", "")
    if not invocation_id:
        raise RuntimeError("TAT RunCommand returned no invocation id")
    return invocation_id, command_id


def read_invocation(credentials: Credentials, region: str, invocation_id: str) -> dict:
    return call_api(
        credentials,
        service="tat",
        version=TAT_VERSION,
        action="DescribeInvocationTasks",
        region=region,
        payload={
            "Filters": [{"Name": "invocation-id", "Values": [invocation_id]}],
            "HideOutput": False,
            "Limit": 20,
        },
    )


def wait_for_invocation(credentials: Credentials, region: str, invocation_id: str) -> dict:
    deadline = time.monotonic() + 360
    while time.monotonic() < deadline:
        response = read_invocation(credentials, region, invocation_id)
        tasks = response.get("InvocationTaskSet", [])
        if len(tasks) != 1:
            raise RuntimeError(f"expected one TAT invocation task; found {len(tasks)}")
        task = tasks[0]
        status = task.get("TaskStatus", "")
        if status in {"SUCCESS", "FAILED", "TIMEOUT"}:
            return task
        time.sleep(5)
    raise RuntimeError("TAT invocation timed out while polling")


def decode_task_output(task: dict) -> str:
    output = task.get("TaskResult", {}).get("Output", "")
    if not output:
        return ""
    try:
        return base64.b64decode(output).decode("utf-8", errors="replace")
    except Exception as exc:
        raise RuntimeError("TAT task output is not valid base64") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply test-only WeChat config through Tencent TAT.")
    parser.add_argument("--secret-file", default=str(DEFAULT_SECRET_FILE))
    parser.add_argument("--public-ip", default=DEFAULT_PUBLIC_IP)
    parser.add_argument("--region", action="append", dest="regions")
    parser.add_argument("--release-id", default="test-wechat-20260828-01")
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.public_ip != DEFAULT_PUBLIC_IP:
        raise RuntimeError("only the approved test host is supported")
    credentials = load_credentials(Path(args.secret_file))
    regions = tuple(args.regions or DEFAULT_REGIONS)
    region, instance_id, instance_type = discover_instance(credentials, args.public_ip, regions)
    agent_status = require_tat_online(credentials, region, instance_id)
    script = build_remote_script(args.release_id)
    if not args.execute:
        print(json.dumps({
            "status": "READY",
            "mode": "DRY_RUN",
            "region": region,
            "instanceId": instance_id,
            "instanceType": instance_type,
            "agentStatus": agent_status,
            "target": "kaipai-backend-test",
            "productionMutation": "FORBIDDEN",
            "scriptSha256": sha256_hex(script).upper(),
        }, ensure_ascii=False, indent=2))
        return 0
    invocation_id, command_id = run_command(credentials, region, instance_id, script)
    task = wait_for_invocation(credentials, region, invocation_id)
    output = decode_task_output(task)
    task_result = task.get("TaskResult", {})
    if task.get("TaskStatus") != "SUCCESS" or "FINAL_STATUS=passed" not in output:
        raise RuntimeError(
            f"TAT test-only command failed: status={task.get('TaskStatus')} exitCode={task_result.get('ExitCode')} "
            f"output={output[:2000]}"
        )
    print(json.dumps({
        "status": "PASSED",
        "mode": "EXECUTE",
        "region": region,
        "instanceId": instance_id,
        "instanceType": instance_type,
        "agentStatus": agent_status,
        "invocationId": invocation_id,
        "commandId": command_id,
        "taskStatus": task.get("TaskStatus"),
        "exitCode": task_result.get("ExitCode"),
        "output": output,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
