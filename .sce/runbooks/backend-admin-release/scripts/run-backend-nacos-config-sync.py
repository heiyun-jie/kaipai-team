import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from wechat_secret_inputs import DEFAULT_SECRET_FILE, resolve_secret_values, validate_required_secret_values


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"

DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_OPERATOR = "codex"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
DEFAULT_NACOS_SERVER_ADDR = "127.0.0.1:8848"
DEFAULT_NACOS_GROUP = "DEFAULT_GROUP"
DEFAULT_NACOS_NAMESPACE = ""
DEFAULT_NACOS_DATA_ID = "kaipai-backend-dev.yml"
DEFAULT_GREP = "WECHAT_MINIAPP|wechat\\.miniapp"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"
NACOS_ENV_KEY_MAP = {
    "WECHAT_MINIAPP_APP_ID": "wechat.miniapp.app-id",
    "WECHAT_MINIAPP_APP_SECRET": "wechat.miniapp.app-secret",
    "WECHAT_MINIAPP_ENV_VERSION": "wechat.miniapp.env-version",
}
SECRET_PATTERNS = [
    re.compile(r"SECRET", re.I),
    re.compile(r"TOKEN", re.I),
    re.compile(r"PASSWORD", re.I),
]


@dataclass
class NacosSyncContext:
    release_id: str
    host: str
    user: str
    operator: str
    identity_file: Path
    secret_file: Path
    nacos_server_addr: str
    group: str
    namespace: str
    data_id: str
    grep: str
    remote_upload_path: str
    updates: OrderedDict[str, str]
    dry_run: bool
    publish_current: bool


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


def run_process(command: list[str], *, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    log(f"local> {' '.join(command)}")
    return subprocess.run(
        command,
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
    )


def ssh_base(context: NacosSyncContext) -> list[str]:
    ssh = resolve_executable("ssh")
    return [
        ssh,
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


def scp_base(context: NacosSyncContext) -> list[str]:
    scp = resolve_executable("scp")
    return [
        scp,
        "-i",
        str(context.identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]


def run_ssh(context: NacosSyncContext, remote_command: str) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(context) + [remote_command], capture_output=True)


def require_key_auth(context: NacosSyncContext) -> None:
    result = run_ssh(context, "printf 'key-auth-ok'")
    if result.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe returned unexpected output")
    log("native ssh key auth verified")


def require_helper(context: NacosSyncContext) -> None:
    result = run_ssh(context, f"sudo -n {REMOTE_HELPER_PATH} --healthcheck")
    if result.stdout.strip() != "helper-ok":
        raise RuntimeError("backend helper healthcheck returned unexpected output")
    log("remote backend helper and sudoers verified")


def parse_arg_kv(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise RuntimeError(f"invalid --set entry: {raw}")
    key, value = raw.split("=", 1)
    key = key.strip()
    if not key:
        raise RuntimeError(f"empty config key in --set entry: {raw}")
    return key, value


def build_updates(args: argparse.Namespace) -> OrderedDict[str, str]:
    updates: OrderedDict[str, str] = OrderedDict()
    resolved_secret_values = resolve_secret_values(Path(args.secret_file), args.from_local_env or [])
    for raw in args.set or []:
        key, value = parse_arg_kv(raw)
        updates[key] = value
    for env_name in args.from_local_env or []:
        value = os.environ.get(env_name) or resolved_secret_values.get(env_name)
        if value is None:
            raise RuntimeError(
                f"local env not found: {env_name}. Also checked secret file: {args.secret_file}"
            )
        config_key = NACOS_ENV_KEY_MAP.get(env_name, env_name)
        updates[config_key] = value
    if not updates and not args.publish_current:
        raise RuntimeError("at least one --set or --from-local-env entry is required")
    validation_input = {
        "WECHAT_MINIAPP_APP_ID": os.environ.get("WECHAT_MINIAPP_APP_ID") or resolved_secret_values.get("WECHAT_MINIAPP_APP_ID"),
        "WECHAT_MINIAPP_APP_SECRET": os.environ.get("WECHAT_MINIAPP_APP_SECRET") or resolved_secret_values.get("WECHAT_MINIAPP_APP_SECRET"),
    }
    validation = validate_required_secret_values(validation_input, ["WECHAT_MINIAPP_APP_ID", "WECHAT_MINIAPP_APP_SECRET"])
    invalid = {key: issues for key, issues in validation.items() if issues and key in (args.from_local_env or [])}
    if invalid:
        joined = ", ".join(f"{key}={'+'.join(issues)}" for key, issues in invalid.items())
        raise RuntimeError(f"wechat nacos sync rejected invalid local inputs: {joined}")
    return updates


def parse_helper_sections(output: str, fields: list[str]) -> dict[str, str]:
    summary: dict[str, str] = {}
    for field in fields:
        begin = f"__{field}_BEGIN__"
        end = f"__{field}_END__"
        match = re.search(rf"{re.escape(begin)}\n(.*?)\n{re.escape(end)}", output, re.S)
        if not match:
            raise RuntimeError(f"missing helper output section: {field}")
        summary[field] = match.group(1).strip()
    return summary


def export_remote_config(context: NacosSyncContext) -> str:
    command = (
        f"sudo -n {REMOTE_HELPER_PATH} "
        f"--nacos-config-export "
        f"--nacos-server-addr {context.nacos_server_addr} "
        f"--nacos-group {context.group} "
        f"--nacos-namespace '{context.namespace}' "
        f"--nacos-data-id {context.data_id}"
    )
    result = run_ssh(context, command)
    if result.stderr and result.stderr.strip():
        log(f"remote stderr> {result.stderr.strip()}")
    summary = parse_helper_sections(
        result.stdout,
        ["REMOTE_DATE", "NACOS_SERVER_ADDR", "NACOS_DATA_ID", "NACOS_RAW_CONFIG", "NACOS_LOGIN_OUTPUT", "FINAL_STATUS", "FAIL_REASON"],
    )
    if summary["FINAL_STATUS"] != "passed":
        raise RuntimeError(f"nacos export failed: {summary['FAIL_REASON']}")
    return summary["NACOS_RAW_CONFIG"]


def parse_properties(text: str) -> OrderedDict[str, str]:
    values: OrderedDict[str, str] = OrderedDict()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def update_properties_config(text: str, updates: OrderedDict[str, str]) -> tuple[str, OrderedDict[str, str], OrderedDict[str, str]]:
    lines = text.splitlines()
    current = parse_properties(text)
    merged = OrderedDict(current)
    for key, value in updates.items():
        merged[key] = value

    output_lines: list[str] = []
    seen_keys: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in line:
            key, _ = line.split("=", 1)
            normalized_key = key.strip()
            if normalized_key in updates:
                output_lines.append(f"{normalized_key}={merged[normalized_key]}")
                seen_keys.add(normalized_key)
            else:
                output_lines.append(line)
        else:
            output_lines.append(line)
    for key, value in updates.items():
        if key not in seen_keys:
            output_lines.append(f"{key}={value}")
    return "\n".join(output_lines).rstrip() + "\n", current, merged


def find_top_level_block(lines: list[str], key: str) -> tuple[int | None, int | None]:
    start = None
    for index, line in enumerate(lines):
        if re.match(rf"^{re.escape(key)}:\s*$", line):
            start = index
            break
    if start is None:
        return None, None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if not line.strip():
            continue
        if re.match(r"^[A-Za-z0-9_.-]+:\s*$", line):
            end = index
            break
    return start, end


def find_nested_block(lines: list[str], start: int, end: int, indent: int, key: str) -> tuple[int | None, int | None]:
    pattern = re.compile(rf"^{' ' * indent}{re.escape(key)}:\s*$")
    block_start = None
    for index in range(start + 1, end):
        if pattern.match(lines[index]):
            block_start = index
            break
    if block_start is None:
        return None, None
    block_end = end
    for index in range(block_start + 1, end):
        line = lines[index]
        if not line.strip():
            continue
        current_indent = len(line) - len(line.lstrip(" "))
        if current_indent <= indent:
            block_end = index
            break
    return block_start, block_end


def parse_yaml_miniapp(text: str) -> OrderedDict[str, str]:
    values: OrderedDict[str, str] = OrderedDict()
    lines = text.splitlines()
    wechat_start, wechat_end = find_top_level_block(lines, "wechat")
    if wechat_start is None:
        return values
    mini_start, mini_end = find_nested_block(lines, wechat_start, wechat_end, 2, "miniapp")
    if mini_start is None:
        return values
    for line in lines[mini_start + 1 : mini_end]:
        match = re.match(r"^\s{4}([A-Za-z0-9_.-]+):\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip().strip('"').strip("'")
    return values


def update_yaml_config(text: str, updates: OrderedDict[str, str]) -> tuple[str, OrderedDict[str, str], OrderedDict[str, str]]:
    lines = text.splitlines()
    current = parse_yaml_miniapp(text)
    merged = OrderedDict(current)
    for full_key, value in updates.items():
        leaf_key = full_key.split(".")[-1]
        merged[leaf_key] = value

    wechat_start, wechat_end = find_top_level_block(lines, "wechat")
    mini_block_lines = ["  miniapp:"]
    for leaf_key, value in merged.items():
        escaped = value.replace('"', '\\"')
        mini_block_lines.append(f'    {leaf_key}: "{escaped}"')

    if wechat_start is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend(["wechat:"] + mini_block_lines)
        return "\n".join(lines).rstrip() + "\n", current, merged

    mini_start, mini_end = find_nested_block(lines, wechat_start, wechat_end, 2, "miniapp")
    if mini_start is None:
        updated_lines = lines[:wechat_end] + mini_block_lines + lines[wechat_end:]
        return "\n".join(updated_lines).rstrip() + "\n", current, merged

    updated_lines = lines[:mini_start] + mini_block_lines + lines[mini_end:]
    return "\n".join(updated_lines).rstrip() + "\n", current, merged


def update_nacos_config(text: str, data_id: str, updates: OrderedDict[str, str]) -> tuple[str, OrderedDict[str, str], OrderedDict[str, str], str]:
    if data_id.endswith(".yml") or data_id.endswith(".yaml") or ":" in text:
        updated_text, current, merged = update_yaml_config(text, updates)
        return updated_text, current, merged, "yaml"
    updated_text, current, merged = update_properties_config(text, updates)
    return updated_text, current, merged, "properties"


def validate_miniapp_keys(merged: OrderedDict[str, str]) -> None:
    required = ["wechat.miniapp.app-id", "wechat.miniapp.app-secret"]
    present = set()
    for key in merged:
        present.add(key)
        if key in {"app-id", "app-secret"}:
            present.add(f"wechat.miniapp.{key}")
    missing = [key for key in required if key not in present or not next((v for k, v in merged.items() if k == key or k == key.split(".")[-1]), "")]
    if missing:
        raise RuntimeError(f"miniapp nacos update is incomplete, missing values for: {', '.join(missing)}")


def redact_value(key: str, value: str) -> str:
    if any(pattern.search(key) for pattern in SECRET_PATTERNS):
        return "[REDACTED]"
    return value


def write_candidate(context: NacosSyncContext, content: str) -> Path:
    temp_dir = ROOT / "tmp" / "backend-nacos-config-sync"
    temp_dir.mkdir(parents=True, exist_ok=True)
    safe_name = context.data_id.replace("/", "_")
    path = temp_dir / f"{context.release_id}.{safe_name}"
    path.write_text(content, encoding="utf-8")
    return path


def upload_candidate(context: NacosSyncContext, local_path: Path) -> None:
    run_ssh(context, f"mkdir -p {Path(context.remote_upload_path).parent.as_posix()}")
    run_process(scp_base(context) + [str(local_path), f"{context.user}@{context.host}:{context.remote_upload_path}"])
    log(f"uploaded nacos candidate to {context.remote_upload_path}")


def run_nacos_sync(context: NacosSyncContext, content_type: str) -> dict[str, str]:
    command = (
        f"sudo -n {REMOTE_HELPER_PATH} "
        f"--nacos-config-sync "
        f"--release-id {context.release_id} "
        f"--nacos-server-addr {context.nacos_server_addr} "
        f"--nacos-group {context.group} "
        f"--nacos-namespace '{context.namespace}' "
        f"--nacos-data-id {context.data_id} "
        f"--nacos-content-type {content_type} "
        f"--nacos-grep '{context.grep}' "
        f"--nacos-upload-path {context.remote_upload_path}"
    )
    result = run_ssh(context, command)
    if result.stderr and result.stderr.strip():
        log(f"remote stderr> {result.stderr.strip()}")
    summary = parse_helper_sections(
        result.stdout,
        [
            "REMOTE_DATE",
            "BACKUP_PATH",
            "RELEASE_ROOT",
            "NACOS_SERVER_ADDR",
            "NACOS_DATA_ID",
            "NACOS_GROUP",
            "NACOS_NAMESPACE",
            "NACOS_LOGIN_OUTPUT",
            "BEFORE_CONFIG",
            "AFTER_CONFIG",
            "BEFORE_FILTERED",
            "AFTER_FILTERED",
            "PUBLISH_OUTPUT",
            "FINAL_STATUS",
            "FAIL_REASON",
        ],
    )
    if summary["FINAL_STATUS"] != "passed":
        raise RuntimeError(f"nacos config sync failed: {summary['FAIL_REASON']}")
    return summary


def write_record(
    context: NacosSyncContext,
    *,
    current: OrderedDict[str, str],
    merged: OrderedDict[str, str],
    content_type: str,
    remote: dict[str, str] | None,
) -> Path:
    record_path = RECORDS_DIR / f"{context.release_id}.md"
    if record_path.exists():
        raise RuntimeError(f"record already exists: {record_path}")

    changed_items = []
    for key, value in context.updates.items():
        lookup_keys = [key, key.split(".")[-1]]
        before_value = "<missing>"
        for lookup in lookup_keys:
            if lookup in current:
                before_value = current[lookup]
                break
        changed_items.append(f"- `{key}`: `{redact_value(key, before_value)}` -> `{redact_value(key, value)}`")

    if not changed_items:
        changed_items.append("- 无字段变更，本次为原文回写验证")

    preview_items = []
    for key in context.updates:
        lookup = key.split(".")[-1]
        final_value = merged.get(key, merged.get(lookup, "<missing>"))
        preview_items.append(f"- `{key}` => `{redact_value(key, final_value)}`")
    if not preview_items:
        preview_items.append("- 保持当前 dataId 原文不变")

    content = f"""# 后端 Nacos 配置来源同步记录

## 1. 基本信息

- 配置批次号：`{context.release_id}`
- 执行时间：`{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`
- 操作人：`{context.operator}`
- 范围：`backend-nacos-config-sync`
- dry-run：`{'是' if context.dry_run else '否'}`
- publish-current：`{'是' if context.publish_current else '否'}`
- Nacos dataId：`{context.data_id}`
- content type：`{content_type}`

## 2. 变更项

{chr(10).join(changed_items)}

## 3. 目标值预览

{chr(10).join(preview_items)}

## 4. 当前结论

- 当前运行时是否已生效：`{'否，当前仅做 dry-run 预演' if context.dry_run else '否，当前仅写入 Nacos，仍需后续 backend-only 发布 / 重建并回读'}`
- 后续必须动作：
  - 若 compose 侧仍缺同组变量，先按 `run-backend-compose-env-sync.py` 补齐
  - 再执行标准 `backend-only` 发布
  - 发布后重新执行 `read-backend-nacos-config.py` 与 `read-backend-runtime-logs.py`

"""

    if remote:
        content += f"""## 5. 远端回读

- 远端备份路径：`{remote['BACKUP_PATH']}`
- 远端归档目录：`{remote['RELEASE_ROOT']}`
- Nacos 服务：`{remote['NACOS_SERVER_ADDR']}`
- Nacos group：`{remote['NACOS_GROUP']}`
- Nacos namespace：`{remote['NACOS_NAMESPACE']}`

### 5.1 发布前过滤视图

```text
{remote['BEFORE_FILTERED']}
```

### 5.2 发布后过滤视图

```text
{remote['AFTER_FILTERED']}
```

### 5.3 发布接口返回

```text
{remote['PUBLISH_OUTPUT']}
```
"""
    else:
        content += """## 5. 远端回读

- 本次为 dry-run，本地仅完成候选配置预演，未写入远端 Nacos
"""

    record_path.write_text(content, encoding="utf-8")
    return record_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synchronize backend Nacos config sources through the standard runbook.")
    parser.add_argument("--label", required=True)
    parser.add_argument("--operator", default=DEFAULT_OPERATOR)
    parser.add_argument("--host", default=os.getenv("KAIPAI_RELEASE_HOST", DEFAULT_HOST))
    parser.add_argument("--user", default=os.getenv("KAIPAI_RELEASE_USER", DEFAULT_USER))
    parser.add_argument("--identity-file", default=os.getenv("KAIPAI_RELEASE_IDENTITY_FILE", str(DEFAULT_IDENTITY_FILE)))
    parser.add_argument("--nacos-server-addr", default=DEFAULT_NACOS_SERVER_ADDR)
    parser.add_argument("--nacos-group", default=DEFAULT_NACOS_GROUP)
    parser.add_argument("--nacos-namespace", default=DEFAULT_NACOS_NAMESPACE)
    parser.add_argument("--nacos-data-id", default=DEFAULT_NACOS_DATA_ID)
    parser.add_argument("--grep", default=DEFAULT_GREP)
    parser.add_argument("--set", action="append")
    parser.add_argument("--from-local-env", action="append")
    parser.add_argument(
        "--secret-file",
        default=str(DEFAULT_SECRET_FILE),
        help="optional local secret file used when --from-local-env keys are not found in the current shell",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--publish-current", action="store_true", help="republish the current raw config unchanged")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    release_time = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    release_id = f"{release_time}-backend-nacos-{args.label}"
    remote_upload_path = f"/home/{args.user}/backend-nacos-uploads/{release_id}/{args.nacos_data_id}"
    context = NacosSyncContext(
        release_id=release_id,
        host=args.host,
        user=args.user,
        operator=args.operator,
        identity_file=Path(args.identity_file),
        secret_file=Path(args.secret_file),
        nacos_server_addr=args.nacos_server_addr,
        group=args.nacos_group,
        namespace=args.nacos_namespace,
        data_id=args.nacos_data_id,
        grep=args.grep,
        remote_upload_path=remote_upload_path,
        updates=build_updates(args),
        dry_run=args.dry_run,
        publish_current=args.publish_current,
    )

    if not context.identity_file.exists():
        raise RuntimeError(
            f"identity file not found: {context.identity_file}. Run "
            "`python .sce/runbooks/backend-admin-release/scripts/bootstrap-admin-release.py --operator <name>` first."
        )

    require_key_auth(context)
    require_helper(context)
    current_raw = export_remote_config(context)
    if context.publish_current and not context.updates:
        updated_content = current_raw
        current = OrderedDict()
        merged = OrderedDict()
        content_type = "yaml" if context.data_id.endswith((".yml", ".yaml")) else "properties"
    else:
        updated_content, current, merged, content_type = update_nacos_config(current_raw, context.data_id, context.updates)
        validate_miniapp_keys(merged)
    candidate_path = write_candidate(context, updated_content)

    remote_summary = None
    if not context.dry_run:
        upload_candidate(context, candidate_path)
        remote_summary = run_nacos_sync(context, content_type)

    record_path = write_record(context, current=current, merged=merged, content_type=content_type, remote=remote_summary)
    print(
        json.dumps(
            {
                "release_id": context.release_id,
                "record_path": str(record_path),
                "candidate_path": str(candidate_path),
                "dry_run": context.dry_run,
                "data_id": context.data_id,
                "updated_keys": list(context.updates.keys()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
