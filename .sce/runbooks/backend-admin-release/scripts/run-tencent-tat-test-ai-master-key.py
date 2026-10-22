import argparse
import base64
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
COMMON_PATH = Path(__file__).with_name("run-tencent-tat-test-wechat-config.py")
COMMON_SPEC = importlib.util.spec_from_file_location("tat_common", COMMON_PATH)
if COMMON_SPEC is None or COMMON_SPEC.loader is None:
    raise RuntimeError("TAT common module is unavailable")
COMMON = importlib.util.module_from_spec(COMMON_SPEC)
COMMON_SPEC.loader.exec_module(COMMON)

DEFAULT_SECRET_FILE = ROOT / ".sce" / "config" / "local-secrets" / "ai-provider-runtime.env"
DEFAULT_CONSOLE_SECRET_FILE = ROOT / ".sce" / "config" / "local-secrets" / "tencent-cloud-console.env"
DEFAULT_PUBLIC_IP = "101.43.57.62"
DEFAULT_REGIONS = COMMON.DEFAULT_REGIONS
TAT_VERSION = COMMON.TAT_VERSION


def load_master_key(path: Path) -> str:
    if not path.exists():
        raise RuntimeError(f"local AI provider runtime secret file is missing: {path}")
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    value = values.get("AI_PROVIDER_CONFIG_MASTER_KEY", "").strip()
    if len(value) != 64 or any(char not in "0123456789abcdefABCDEF" for char in value):
        raise RuntimeError("local AI_PROVIDER_CONFIG_MASTER_KEY must be a 64-character hex value")
    return value


def sha256_hex(value: str | bytes) -> str:
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(raw).hexdigest().upper()


def build_remote_script(release_id: str, master_key: str) -> str:
    if not release_id.startswith("test-ai-key-") or not release_id.replace("-", "").isalnum():
        raise RuntimeError("invalid release id")
    encoded_key = base64.b64encode(master_key.encode("ascii")).decode("ascii")
    return f"""#!/usr/bin/env bash
set -Eeuo pipefail

release_id={release_id!r}
runtime_root=/opt/kaipai/test
compose_file="$runtime_root/docker-compose.yml"
secret_env="$runtime_root/test-secrets.env"
test_service=kaipai-test
test_container=kaipai-backend-test
prod_container=kaipai-backend
backup_root="$runtime_root/backups/ai-master-key/$release_id"
candidate_env="$(mktemp /run/kaipai-test-ai-env.XXXXXX)"
local_key_file="$(mktemp /run/kaipai-test-ai-key.XXXXXX)"
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
  rm -f "$candidate_env" "$local_key_file"
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

base64 -d >"$local_key_file" <<'KEYDATA'
{encoded_key}
KEYDATA
local_key="$(cat "$local_key_file")"
[[ "${{#local_key}}" -eq 64 ]] || {{ echo 'FINAL_STATUS=failed'; echo 'FAIL_REASON=local key length mismatch'; exit 1; }}
local_key_sha="$(printf '%s' "$local_key" | sha256sum | awk '{{print toupper($1)}}')"

[[ -f "$compose_file" && -f "$secret_env" ]] || {{ echo 'FINAL_STATUS=failed'; echo 'FAIL_REASON=test runtime files missing'; exit 1; }}
prod_before="$(docker inspect --format '{{{{.Id}}}}|{{{{.State.StartedAt}}}}|{{{{.RestartCount}}}}' "$prod_container")"
prod_key="$(grep 'AI_PROVIDER_CONFIG_MASTER_KEY' /opt/kaipai/docker-compose.yml | head -1 | cut -d= -f2-)"
[[ -n "$prod_key" ]] || {{ echo 'FINAL_STATUS=failed'; echo 'FAIL_REASON=production source key missing'; exit 1; }}
prod_key_sha="$(printf '%s' "$prod_key" | sha256sum | awk '{{print toupper($1)}}')"
[[ "$prod_key_sha" == "$local_key_sha" ]] || {{ echo 'FINAL_STATUS=failed'; echo 'FAIL_REASON=local key does not match production source digest'; exit 1; }}

mkdir -p "$backup_root"
cp -a "$secret_env" "$backup_root/test-secrets.env.before"
grep -Ev '^AI_PROVIDER_CONFIG_MASTER_KEY=' "$secret_env" >"$candidate_env" || true
printf 'AI_PROVIDER_CONFIG_MASTER_KEY=%s\\n' "$local_key" >>"$candidate_env"
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
runtime_key="$(printf '%s\\n' "$test_env" | sed -n 's/^AI_PROVIDER_CONFIG_MASTER_KEY=//p' | head -1)"
[[ "$runtime_key" == "$local_key" ]] || {{ echo 'FINAL_STATUS=failed'; echo 'FAIL_REASON=test runtime key digest mismatch'; exit 1; }}
printf '%s\\n' "$test_env" | grep -qx 'SPRING_PROFILES_ACTIVE=test'
printf '%s\\n' "$test_env" | grep -qx 'SERVER_PORT=18080'
printf '%s\\n' "$test_env" | grep '^SPRING_DATASOURCE_URL=' | grep -q 'kaipai_test'
printf '%s\\n' "$test_env" | grep -qx 'SPRING_DATA_REDIS_DATABASE=1'

prod_after="$(docker inspect --format '{{{{.Id}}}}|{{{{.State.StartedAt}}}}|{{{{.RestartCount}}}}' "$prod_container")"
[[ "$prod_after" == "$prod_before" ]] || {{ echo 'FINAL_STATUS=failed'; echo 'FAIL_REASON=production container changed'; exit 1; }}

rollback_needed=false
trap - EXIT
cleanup
echo 'FINAL_STATUS=passed'
echo "PROD_BEFORE=$prod_before"
echo "PROD_AFTER=$prod_after"
echo "TEST_DATABASE=kaipai_test"
echo "TEST_REDIS_DATABASE=1"
echo "KEY_LENGTH=${{#local_key}}"
echo "KEY_SHA256=$local_key_sha"
echo "SECRET_FILE_MODE=$(stat -c '%a|%U|%G' "$secret_env")"
echo "BACKUP_ROOT=$backup_root"
"""


def call_tat(credentials, region: str, action: str, payload: dict) -> dict:
    return COMMON.call_api(
        credentials,
        service="tat",
        version=TAT_VERSION,
        action=action,
        region=region,
        payload=payload,
    )


def run_command(credentials, region: str, instance_id: str, script: str) -> tuple[str, str]:
    response = call_tat(
        credentials,
        region,
        "RunCommand",
        {
            "Content": base64.b64encode(script.encode("utf-8")).decode("ascii"),
            "InstanceIds": [instance_id],
            "CommandName": "kaipai-test-ai-master-key",
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


def wait_for_invocation(credentials, region: str, invocation_id: str) -> dict:
    deadline = time.monotonic() + 360
    while time.monotonic() < deadline:
        response = call_tat(
            credentials,
            region,
            "DescribeInvocationTasks",
            {"Filters": [{"Name": "invocation-id", "Values": [invocation_id]}], "HideOutput": False, "Limit": 20},
        )
        tasks = response.get("InvocationTaskSet", [])
        if len(tasks) != 1:
            raise RuntimeError(f"expected one TAT invocation task; found {len(tasks)}")
        task = tasks[0]
        if task.get("TaskStatus") in {"SUCCESS", "FAILED", "TIMEOUT"}:
            return task
        time.sleep(5)
    raise RuntimeError("TAT invocation timed out while polling")


def decode_output(task: dict) -> str:
    output = task.get("TaskResult", {}).get("Output", "")
    return base64.b64decode(output).decode("utf-8", errors="replace") if output else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply the AI provider master key to the isolated test runtime only.")
    parser.add_argument("--secret-file", default=str(DEFAULT_SECRET_FILE))
    parser.add_argument("--console-secret-file", default=str(DEFAULT_CONSOLE_SECRET_FILE))
    parser.add_argument("--public-ip", default=DEFAULT_PUBLIC_IP)
    parser.add_argument("--region", action="append", dest="regions")
    parser.add_argument("--release-id", default="test-ai-key-20260901-01")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    if args.public_ip != DEFAULT_PUBLIC_IP:
        raise RuntimeError("only the approved test host is supported")
    master_key = load_master_key(Path(args.secret_file))
    credentials = COMMON.load_credentials(Path(args.console_secret_file))
    regions = tuple(args.regions or DEFAULT_REGIONS)
    region, instance_id, instance_type = COMMON.discover_instance(credentials, args.public_ip, regions)
    agent_status = COMMON.require_tat_online(credentials, region, instance_id)
    script = build_remote_script(args.release_id, master_key)
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
            "keyLength": len(master_key),
            "keySha256": sha256_hex(master_key),
            "scriptSha256": sha256_hex(script),
        }, ensure_ascii=False, indent=2))
        return 0

    invocation_id, command_id = run_command(credentials, region, instance_id, script)
    task = wait_for_invocation(credentials, region, invocation_id)
    output = decode_output(task)
    task_result = task.get("TaskResult", {})
    if task.get("TaskStatus") != "SUCCESS" or "FINAL_STATUS=passed" not in output:
        raise RuntimeError(
            f"TAT test-only command failed: status={task.get('TaskStatus')} exitCode={task_result.get('ExitCode')} "
            f"output={output[-2000:]}"
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
