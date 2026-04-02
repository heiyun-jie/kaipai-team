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


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"

DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_OPERATOR = "codex"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"
REMOTE_RUNTIME_COMPOSE = "/opt/kaipai/docker-compose.yml"

SECRET_KEY_PATTERNS = [
    re.compile(r"SECRET", re.I),
    re.compile(r"TOKEN", re.I),
    re.compile(r"PASSWORD", re.I),
]


@dataclass
class EnvSyncContext:
    release_id: str
    release_time: str
    host: str
    user: str
    operator: str
    label: str
    identity_file: Path
    remote_upload_path: str
    updates: OrderedDict[str, str]
    dry_run: bool


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


def ssh_base(context: EnvSyncContext) -> list[str]:
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


def scp_base(context: EnvSyncContext) -> list[str]:
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


def run_ssh(context: EnvSyncContext, remote_command: str) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(context) + [remote_command], capture_output=True)


def require_key_auth(context: EnvSyncContext) -> None:
    result = run_ssh(context, "printf 'key-auth-ok'")
    if result.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe returned unexpected output")
    log("native ssh key auth verified")


def require_helper(context: EnvSyncContext) -> None:
    result = run_ssh(context, f"sudo -n {REMOTE_HELPER_PATH} --healthcheck")
    if result.stdout.strip() != "helper-ok":
        raise RuntimeError("backend helper healthcheck returned unexpected output")
    log("remote backend helper and sudoers verified")


def fetch_remote_compose(context: EnvSyncContext) -> str:
    result = run_ssh(context, f"cat {REMOTE_RUNTIME_COMPOSE}")
    if result.stderr and result.stderr.strip():
        log(f"remote stderr> {result.stderr.strip()}")
    return result.stdout


def parse_arg_kv(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise RuntimeError(f"invalid --set entry: {raw}")
    key, value = raw.split("=", 1)
    key = key.strip()
    if not key:
        raise RuntimeError(f"empty env key in --set entry: {raw}")
    return key, value


def build_updates(args: argparse.Namespace) -> OrderedDict[str, str]:
    updates: OrderedDict[str, str] = OrderedDict()
    for raw in args.set or []:
        key, value = parse_arg_kv(raw)
        updates[key] = value
    for key in args.from_local_env or []:
        value = os.environ.get(key)
        if value is None:
            raise RuntimeError(f"local env not found: {key}")
        updates[key] = value
    if not updates:
        raise RuntimeError("at least one --set or --from-local-env entry is required")
    return updates


def leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def is_mapping_key_at_indent(line: str, indent: int) -> bool:
    if not line.strip():
        return False
    return re.match(rf"^ {' ' * (indent - 1)}", "") is None


def find_service_block(lines: list[str], service_name: str) -> tuple[int, int, int]:
    service_pattern = re.compile(rf"^(?P<indent>\s*){re.escape(service_name)}:\s*$")
    service_start = -1
    service_indent = 0
    for index, line in enumerate(lines):
        match = service_pattern.match(line)
        if match:
            service_start = index
            service_indent = len(match.group("indent"))
            break
    if service_start == -1:
        raise RuntimeError(f"service not found in compose file: {service_name}")

    service_end = len(lines)
    for index in range(service_start + 1, len(lines)):
        line = lines[index]
        if not line.strip():
            continue
        if leading_spaces(line) <= service_indent and re.match(r"^\s*[^#\s][^:]*:\s*$", line):
            service_end = index
            break
    return service_start, service_end, service_indent


def parse_environment_block(
    lines: list[str],
    service_start: int,
    service_end: int,
    service_indent: int,
) -> tuple[int | None, int | None, str, OrderedDict[str, str]]:
    env_indent = service_indent + 2
    env_pattern = re.compile(rf"^{' ' * env_indent}environment:\s*$")
    env_start = None
    for index in range(service_start + 1, service_end):
        if env_pattern.match(lines[index]):
            env_start = index
            break

    if env_start is None:
        return None, None, "list", OrderedDict()

    env_end = service_end
    for index in range(env_start + 1, service_end):
        line = lines[index]
        if not line.strip():
            continue
        if leading_spaces(line) <= env_indent:
            env_end = index
            break

    child_lines = [line for line in lines[env_start + 1 : env_end] if line.strip()]
    style = "list"
    if child_lines:
        first_child = child_lines[0].lstrip()
        if first_child.startswith("- "):
            style = "list"
        else:
            style = "mapping"

    env_values: OrderedDict[str, str] = OrderedDict()
    if style == "list":
        item_pattern = re.compile(r"^\s*-\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
        for line in child_lines:
            match = item_pattern.match(line)
            if match:
                env_values[match.group(1)] = match.group(2)
    else:
        item_pattern = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")
        for line in child_lines:
            match = item_pattern.match(line)
            if match:
                env_values[match.group(1)] = match.group(2).strip().strip("'").strip('"')

    return env_start, env_end, style, env_values


def rebuild_environment_block(
    *,
    env_indent: int,
    style: str,
    env_values: OrderedDict[str, str],
) -> list[str]:
    block = [f"{' ' * env_indent}environment:"]
    child_indent = env_indent + 2
    if style == "mapping":
        for key, value in env_values.items():
            escaped_value = value.replace('"', '\\"')
            block.append(f"{' ' * child_indent}{key}: \"{escaped_value}\"")
    else:
        for key, value in env_values.items():
            block.append(f"{' ' * child_indent}- {key}={value}")
    return block


def update_compose_backend_env(compose_text: str, updates: OrderedDict[str, str]) -> tuple[str, OrderedDict[str, str], OrderedDict[str, str]]:
    lines = compose_text.splitlines()
    service_start, service_end, service_indent = find_service_block(lines, "kaipai")
    env_start, env_end, style, current_env = parse_environment_block(lines, service_start, service_end, service_indent)

    merged_env = OrderedDict(current_env)
    for key, value in updates.items():
        merged_env[key] = value

    miniapp_keys = {"WECHAT_MINIAPP_APP_ID", "WECHAT_MINIAPP_APP_SECRET"}
    if miniapp_keys & set(updates):
        missing = [key for key in miniapp_keys if not merged_env.get(key)]
        if missing:
            raise RuntimeError(f"miniapp env update is incomplete, missing values for: {', '.join(missing)}")

    env_indent = service_indent + 2
    rebuilt_block = rebuild_environment_block(env_indent=env_indent, style=style, env_values=merged_env)
    if env_start is None:
        updated_lines = lines[:service_end] + rebuilt_block + lines[service_end:]
    else:
        updated_lines = lines[:env_start] + rebuilt_block + lines[env_end:]

    updated_text = "\n".join(updated_lines) + "\n"
    return updated_text, current_env, merged_env


def is_secret_key(key: str) -> bool:
    return any(pattern.search(key) for pattern in SECRET_KEY_PATTERNS)


def redact_value(key: str, value: str) -> str:
    if is_secret_key(key):
        return "[REDACTED]"
    return value


def upload_compose(context: EnvSyncContext, local_path: Path) -> None:
    run_ssh(context, f"mkdir -p {Path(context.remote_upload_path).parent.as_posix()}")
    run_process(scp_base(context) + [str(local_path), f"{context.user}@{context.host}:{context.remote_upload_path}"])
    log(f"uploaded compose candidate to {context.remote_upload_path}")


def parse_helper_output(output: str) -> dict[str, str]:
    fields = [
        "REMOTE_DATE",
        "BACKUP_PATH",
        "RELEASE_ROOT",
        "COMPOSE_FILE",
        "ARCHIVED_COMPOSE_FILE",
        "DOCKER_INSPECT_ENV",
        "COMPOSE_BACKEND_SOURCE",
        "COMPOSE_RENDERED_BACKEND",
        "CANDIDATE_VALIDATE_OUTPUT",
        "FINAL_STATUS",
        "FAIL_REASON",
    ]
    summary: dict[str, str] = {}
    for field in fields:
        begin = f"__{field}_BEGIN__"
        end = f"__{field}_END__"
        match = re.search(rf"{re.escape(begin)}\n(.*?)\n{re.escape(end)}", output, re.S)
        if not match:
            raise RuntimeError(f"missing helper output section: {field}")
        summary[field] = match.group(1).strip()
    return summary


def run_helper_sync(context: EnvSyncContext) -> dict[str, str]:
    helper_command = (
        f"sudo -n {REMOTE_HELPER_PATH} "
        f"--compose-env-sync "
        f"--release-id {context.release_id} "
        f"--compose-upload-path {context.remote_upload_path} "
        f"--operator-user {context.user}"
    )
    result = run_ssh(context, helper_command)
    if result.stderr and result.stderr.strip():
        log(f"remote stderr> {result.stderr.strip()}")
    summary = parse_helper_output(result.stdout)
    if summary["FINAL_STATUS"] != "passed":
        raise RuntimeError(f"compose env sync failed: {summary['FAIL_REASON']}")
    return summary


def write_local_candidate(context: EnvSyncContext, compose_text: str) -> Path:
    temp_dir = ROOT / "tmp" / "backend-compose-env-sync"
    temp_dir.mkdir(parents=True, exist_ok=True)
    local_path = temp_dir / f"{context.release_id}.docker-compose.yml"
    local_path.write_text(compose_text, encoding="utf-8")
    return local_path


def write_record(
    context: EnvSyncContext,
    *,
    current_env: OrderedDict[str, str],
    merged_env: OrderedDict[str, str],
    remote: dict[str, str] | None,
) -> Path:
    record_path = RECORDS_DIR / f"{context.release_id}.md"
    if record_path.exists():
        raise RuntimeError(f"record already exists: {record_path}")

    changed_items = []
    for key, value in context.updates.items():
        before_value = current_env.get(key, "<missing>")
        changed_items.append(
            f"- `{key}`: `{redact_value(key, before_value)}` -> `{redact_value(key, value)}`"
        )

    final_preview = []
    for key in context.updates:
        final_preview.append(f"- `{key}` => `{redact_value(key, merged_env.get(key, '<missing>'))}`")

    content = f"""# 后端运行时配置来源同步记录

## 1. 基本信息

- 配置批次号：`{context.release_id}`
- 执行时间：`{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`
- 操作人：`{context.operator}`
- 范围：`backend-compose-env-sync`
- dry-run：`{'是' if context.dry_run else '否'}`
- 关联 Spec：
  - `00-29 backend-admin-release-governance`
  - `00-28 invite wxacode execution card`

## 2. 目标

- 将后端 compose / env source 的运行时变量变更收口到标准脚本
- 本次仅同步 `docker-compose.yml` 的后端环境变量来源，不执行后端发版与容器重建

## 3. 变更项

{chr(10).join(changed_items)}

## 4. 目标值预览

{chr(10).join(final_preview)}

## 5. 当前结论

- 当前容器运行时是否已生效：`{'否，当前仅做 dry-run 预览' if context.dry_run else '否，已更新 compose 来源，仍需后续 backend-only 发布/重建'}`
- 后续必须动作：
  - 通过标准 `backend-only` 脚本重建后端容器
  - 再通过标准诊断确认 compose 来源摘录与容器 env 都包含目标变量

"""

    if remote:
        content += f"""## 6. 远端回读

- 远端备份路径：`{remote['BACKUP_PATH']}`
- 远端构建归档目录：`{remote['RELEASE_ROOT']}`
- 运行时 compose 文件：`{remote['COMPOSE_FILE']}`
- 归档 compose 文件：`{remote['ARCHIVED_COMPOSE_FILE']}`

### 6.1 当前容器环境变量

```text
{remote['DOCKER_INSPECT_ENV']}
```

### 6.2 compose 后端来源摘录

```text
{remote['COMPOSE_BACKEND_SOURCE']}
```

### 6.3 compose 渲染后后端定义摘录

```text
{remote['COMPOSE_RENDERED_BACKEND']}
```

### 6.4 compose 候选文件校验输出

```text
{remote['CANDIDATE_VALIDATE_OUTPUT']}
```
"""
    else:
        content += """## 6. 远端回读

- 本次为 dry-run，本地仅完成 compose 更新预演，未写入远端
"""

    record_path.write_text(content, encoding="utf-8")
    return record_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synchronize backend compose environment source through the standard runbook.")
    parser.add_argument("--label", required=True, help="env sync label suffix")
    parser.add_argument("--operator", default=DEFAULT_OPERATOR)
    parser.add_argument("--host", default=os.getenv("KAIPAI_RELEASE_HOST", DEFAULT_HOST))
    parser.add_argument("--user", default=os.getenv("KAIPAI_RELEASE_USER", DEFAULT_USER))
    parser.add_argument(
        "--identity-file",
        default=os.getenv("KAIPAI_RELEASE_IDENTITY_FILE", str(DEFAULT_IDENTITY_FILE)),
        help="OpenSSH private key path used for native ssh/scp",
    )
    parser.add_argument("--set", action="append", help="explicit KEY=VALUE entry to sync")
    parser.add_argument(
        "--from-local-env",
        action="append",
        help="read KEY value from the current local environment instead of command line",
    )
    parser.add_argument("--dry-run", action="store_true", help="preview compose updates locally without writing remote files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    release_time = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    release_id = f"{release_time}-backend-env-{args.label}"
    remote_upload_path = f"/home/{args.user}/backend-env-uploads/{release_id}/docker-compose.yml"
    context = EnvSyncContext(
        release_id=release_id,
        release_time=release_time,
        host=args.host,
        user=args.user,
        operator=args.operator,
        label=args.label,
        identity_file=Path(args.identity_file),
        remote_upload_path=remote_upload_path,
        updates=build_updates(args),
        dry_run=args.dry_run,
    )

    if not context.identity_file.exists():
        raise RuntimeError(
            f"identity file not found: {context.identity_file}. Run "
            "`python .sce/runbooks/backend-admin-release/scripts/bootstrap-admin-release.py --operator <name>` first."
        )

    require_key_auth(context)
    require_helper(context)
    current_compose = fetch_remote_compose(context)
    updated_compose, current_env, merged_env = update_compose_backend_env(current_compose, context.updates)
    candidate_path = write_local_candidate(context, updated_compose)

    remote_summary = None
    if not context.dry_run:
        upload_compose(context, candidate_path)
        remote_summary = run_helper_sync(context)

    record_path = write_record(context, current_env=current_env, merged_env=merged_env, remote=remote_summary)
    print(
        json.dumps(
            {
                "release_id": context.release_id,
                "record_path": str(record_path),
                "candidate_path": str(candidate_path),
                "dry_run": context.dry_run,
                "updated_keys": list(context.updates.keys()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
