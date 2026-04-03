import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import error, request


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"
SERVER_DIR = ROOT / "kaipaile-server"
TARGET_JAR = SERVER_DIR / "target" / "kaipai-backend-1.0.0-SNAPSHOT.jar"
MIGRATION_DIR = SERVER_DIR / "src" / "main" / "resources" / "db" / "migration"
SCHEMA_RELEASE_SCRIPT = RUNBOOK_DIR / "scripts" / "run-backend-schema-migration.py"

DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_OPERATOR = "codex"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
DEFAULT_JAVA_HOME_HINT = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "tools" / "temurin17"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"
TMP_DIR = ROOT / "tmp" / "backend-release-snapshots"


@dataclass
class ReleaseContext:
    release_id: str
    release_time: str
    host: str
    user: str
    operator: str
    label: str
    identity_file: Path
    java_home: Path
    remote_upload_path: str
    local_jar_path: Path
    build_root: Path
    source_mode: str = "working_tree"
    snapshot_root: Path | None = None
    overlay_paths: list[str] = field(default_factory=list)
    dirty_paths: list[str] = field(default_factory=list)
    local_jar_sha: str = ""


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


def run_process(
    command: list[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    log(f"local> {' '.join(command)}")
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
        env=env,
    )


def git_base() -> list[str]:
    return [resolve_executable("git")]


def run_git(
    command: list[str],
    *,
    cwd: Path,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    return run_process(git_base() + command, cwd=cwd, capture_output=capture_output)


def normalize_sha(value: str) -> str:
    return value.strip().upper()


def release_file_major_version(java_home: Path) -> int:
    release_file = java_home / "release"
    if not release_file.exists():
        return 0
    content = release_file.read_text(encoding="utf-8", errors="replace")
    match = re.search(r'JAVA_VERSION="(\d+)(?:\.\d+)?', content)
    return int(match.group(1)) if match else 0


def resolve_java_home(cli_value: str | None) -> Path:
    candidates: list[Path] = []
    if cli_value:
        candidates.append(Path(cli_value))
    for env_name in ["KAIPAI_RELEASE_JAVA_HOME", "JAVA_HOME"]:
        env_value = os.environ.get(env_name)
        if env_value:
            candidates.append(Path(env_value))
    if DEFAULT_JAVA_HOME_HINT.exists():
        candidates.extend(sorted(DEFAULT_JAVA_HOME_HINT.glob("jdk-17*"), reverse=True))
    candidates.extend(
        sorted(Path(r"C:\Program Files\Eclipse Adoptium").glob("jdk-17*"), reverse=True)
        if Path(r"C:\Program Files\Eclipse Adoptium").exists()
        else []
    )
    for candidate in candidates:
        if (candidate / "bin" / "java.exe").exists() and release_file_major_version(candidate) >= 17:
            return candidate
    raise RuntimeError("no usable JDK 17 found; set --java-home or KAIPAI_RELEASE_JAVA_HOME first")


def build_env(java_home: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["JAVA_HOME"] = str(java_home)
    path_key = "Path" if "Path" in env else "PATH"
    env[path_key] = f"{java_home / 'bin'}{os.pathsep}{env.get(path_key, '')}"
    return env


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def ssh_base(context: ReleaseContext) -> list[str]:
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


def scp_base(context: ReleaseContext) -> list[str]:
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


def run_ssh(context: ReleaseContext, remote_command: str) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(context) + [remote_command], capture_output=True)


def require_key_auth(context: ReleaseContext) -> None:
    try:
        result = run_ssh(context, "printf 'key-auth-ok'")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "native ssh key auth is not ready; run "
            "`python .sce/runbooks/backend-admin-release/scripts/bootstrap-admin-release.py --operator <name>` first"
        ) from exc
    if result.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe returned unexpected output")
    log("native ssh key auth verified")


def require_helper(context: ReleaseContext) -> None:
    try:
        result = run_ssh(context, f"sudo -n {REMOTE_HELPER_PATH} --healthcheck")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "backend release helper is not ready; rerun "
            "`python .sce/runbooks/backend-admin-release/scripts/bootstrap-admin-release.py --operator <name>` first"
        ) from exc
    if result.stdout.strip() != "helper-ok":
        raise RuntimeError("backend helper healthcheck returned unexpected output")
    log("remote backend helper and sudoers verified")


def parse_mysql_helper_output(output: str) -> dict[str, str]:
    fields = [
        "REMOTE_DATE",
        "MYSQL_MODE",
        "MYSQL_DATABASE",
        "MYSQL_CONTAINER",
        "MYSQL_RESULT",
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


def list_local_migration_scripts() -> list[str]:
    if not MIGRATION_DIR.exists():
        return []
    return sorted(path.name for path in MIGRATION_DIR.glob("V*.sql") if path.is_file())


def parse_git_status_path(line: str) -> str:
    payload = line[3:]
    if " -> " in payload:
        return payload.split(" -> ", 1)[1].strip()
    return payload.strip()


def list_backend_dirty_paths() -> list[str]:
    result = run_git(["status", "--short", "--untracked-files=all"], cwd=SERVER_DIR, capture_output=True)
    dirty_paths: list[str] = []
    for raw_line in result.stdout.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        path = parse_git_status_path(line)
        if not path or path.startswith("target/"):
            continue
        dirty_paths.append(path.replace("\\", "/"))
    return sorted(set(dirty_paths))


def normalize_overlay_path(raw: str) -> str:
    normalized = raw.replace("\\", "/").strip().strip("/")
    if not normalized:
        raise RuntimeError("overlay path must not be empty")
    candidate = (SERVER_DIR / normalized).resolve()
    try:
        candidate.relative_to(SERVER_DIR.resolve())
    except ValueError as exc:
        raise RuntimeError(f"overlay path is outside server workspace: {raw}") from exc
    if not candidate.exists():
        raise RuntimeError(f"overlay path not found in server workspace: {raw}")
    return normalized


def prepare_release_source(context: ReleaseContext, overlay_paths: list[str]) -> None:
    context.dirty_paths = list_backend_dirty_paths()
    normalized_overlay_paths = sorted(set(normalize_overlay_path(path) for path in overlay_paths))
    if not context.dirty_paths:
        if normalized_overlay_paths:
            raise RuntimeError("overlay paths are only allowed when server worktree has non-target dirty changes")
        context.source_mode = "working_tree"
        context.build_root = SERVER_DIR
        context.local_jar_path = TARGET_JAR
        return

    if not normalized_overlay_paths:
        preview = "\n".join(f"  - {path}" for path in context.dirty_paths[:20])
        suffix = "\n  - ..." if len(context.dirty_paths) > 20 else ""
        raise RuntimeError(
            "backend-only release blocked: server worktree contains non-target dirty changes.\n"
            "Use repeated `--overlay-path <relative-path>` to declare the files that belong to this release.\n"
            "The script will then build from a clean HEAD snapshot plus those overlays.\n"
            f"Current dirty paths:\n{preview}{suffix}"
        )

    context.source_mode = "git_head_snapshot_with_overlay"
    context.overlay_paths = normalized_overlay_paths
    snapshot_root = TMP_DIR / context.release_id
    if snapshot_root.exists():
        shutil.rmtree(snapshot_root)
    snapshot_root.parent.mkdir(parents=True, exist_ok=True)
    run_git(["worktree", "add", "--detach", str(snapshot_root), "HEAD"], cwd=SERVER_DIR)
    for relative_path in normalized_overlay_paths:
        source_path = SERVER_DIR / relative_path
        target_path = snapshot_root / relative_path
        if source_path.is_dir():
            if target_path.exists():
                shutil.rmtree(target_path)
            shutil.copytree(source_path, target_path)
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target_path)
    context.snapshot_root = snapshot_root
    context.build_root = snapshot_root
    context.local_jar_path = snapshot_root / "target" / TARGET_JAR.name
    log("prepared clean backend release snapshot with overlays: " + ", ".join(context.overlay_paths))


def cleanup_release_source(context: ReleaseContext) -> None:
    if context.snapshot_root is None:
        return
    try:
        run_git(["worktree", "remove", "--force", str(context.snapshot_root)], cwd=SERVER_DIR)
    except subprocess.CalledProcessError:
        if context.snapshot_root.exists():
            shutil.rmtree(context.snapshot_root, ignore_errors=True)
    finally:
        context.snapshot_root = None


def run_remote_mysql_validation(context: ReleaseContext, sql_content: str, remote_stem: str) -> dict[str, str]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".sql", delete=False) as handle:
        handle.write(sql_content)
        local_sql_path = Path(handle.name)
    try:
        remote_dir = f"/home/{context.user}/backend-schema-checks/{context.release_id}"
        remote_sql_path = f"{remote_dir}/{remote_stem}.sql"
        run_ssh(context, f"mkdir -p {remote_dir}")
        run_process(scp_base(context) + [str(local_sql_path), f"{context.user}@{context.host}:{remote_sql_path}"])
        helper_command = (
            f"sudo -n {REMOTE_HELPER_PATH} "
            f"--mysql-validation "
            f"--mysql-script-path {remote_sql_path} "
            f"--mysql-database kaipai_dev "
            f"--mysql-container kaipai-mysql"
        )
        result = run_ssh(context, helper_command)
        if result.stderr and result.stderr.strip():
            log(f"remote stderr> {result.stderr.strip()}")
        summary = parse_mysql_helper_output(result.stdout)
        if summary.get("FINAL_STATUS") != "passed":
            raise RuntimeError(f"remote mysql validation failed: {summary.get('FAIL_REASON', 'unknown error')}")
        return summary
    finally:
        local_sql_path.unlink(missing_ok=True)


def fetch_remote_applied_schema_scripts(context: ReleaseContext) -> set[str]:
    history_exists_summary = run_remote_mysql_validation(
        context,
        "SELECT CONCAT('HISTORY_TABLE_EXISTS=', COUNT(*)) "
        "FROM information_schema.tables "
        "WHERE table_schema = DATABASE() AND table_name = 'schema_release_history';\n",
        "schema-history-exists",
    )
    if "HISTORY_TABLE_EXISTS=1" not in history_exists_summary["MYSQL_RESULT"]:
        raise RuntimeError("schema_release_history table is missing")

    history_scripts_summary = run_remote_mysql_validation(
        context,
        "SELECT CONCAT('APPLIED_SCRIPT=', `script`) FROM `schema_release_history` ORDER BY `script`;\n",
        "schema-history-list",
    )
    applied = set()
    for line in history_scripts_summary["MYSQL_RESULT"].splitlines():
        marker = "APPLIED_SCRIPT="
        if marker in line:
            applied.add(line.split(marker, 1)[1].strip(" |"))
    return applied


def require_schema_history_synced(context: ReleaseContext) -> None:
    local_scripts = list_local_migration_scripts()
    if not local_scripts:
        return
    try:
        remote_scripts = fetch_remote_applied_schema_scripts(context)
    except RuntimeError as exc:
        raise RuntimeError(
            "schema migration precheck failed: target DB is not enrolled in standard schema history yet. Run "
            f"`python {SCHEMA_RELEASE_SCRIPT} --label <label> --operator <name> --mode baseline-existing --migration-file <script>` "
            "for existing migrations, then apply missing migrations before backend-only release."
        ) from exc

    missing = [script for script in local_scripts if script not in remote_scripts]
    if missing:
        missing_args = " ".join(f"--migration-file {name}" for name in missing)
        raise RuntimeError(
            "pending schema migrations not yet applied to target DB: "
            + ", ".join(missing)
            + ". Run "
            + f"`python {SCHEMA_RELEASE_SCRIPT} --label <label> --operator <name> {missing_args}` "
            + "before backend-only release."
        )


def build_backend(context: ReleaseContext) -> None:
    env = build_env(context.java_home)
    mvn = resolve_executable("mvn")
    run_process([mvn, "-q", "-DskipTests", "clean", "package"], cwd=context.build_root, env=env)
    if not context.local_jar_path.exists():
        raise RuntimeError(f"backend jar not found after build: {context.local_jar_path}")
    context.local_jar_sha = sha256_file(context.local_jar_path)
    log(f"backend jar ready: {context.local_jar_path} sha256={context.local_jar_sha}")


def upload_jar(context: ReleaseContext) -> None:
    run_ssh(context, f"mkdir -p {Path(context.remote_upload_path).parent.as_posix()}")
    run_process(scp_base(context) + [str(context.local_jar_path), f"{context.user}@{context.host}:{context.remote_upload_path}"])
    log(f"uploaded backend jar to {context.remote_upload_path}")


def parse_helper_output(output: str) -> dict[str, str]:
    fields = [
        "REMOTE_DATE",
        "BACKUP_PATH",
        "RELEASE_ROOT",
        "REMOTE_RELEASE_JAR",
        "RUNTIME_JAR",
        "UPLOADED_JAR_SHA",
        "RUNTIME_JAR_SHA",
        "CONTAINER_JAR_SHA",
        "DOCKER_COMPOSE_VERSION",
        "DOCKER_COMPOSE_PS",
        "DOCKER_PS",
        "DOCKER_INSPECT_ENV",
        "DOCKER_LOGS_TAIL",
        "COMPOSE_BACKEND_SOURCE",
        "COMPOSE_RENDERED_BACKEND",
        "NGINX_API_PROXY",
        "INTERNAL_DOCS",
        "INTERNAL_ADMIN_LOGIN",
        "INTERNAL_RECRUIT_ROLES",
        "INTERNAL_ROLE_SEARCH",
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


def deploy_backend_only(context: ReleaseContext) -> dict[str, str]:
    helper_command = (
        f"sudo -n {REMOTE_HELPER_PATH} "
        f"--release-id {context.release_id} "
        f"--upload-path {context.remote_upload_path} "
        f"--jar-sha {context.local_jar_sha} "
        f"--operator-user {context.user}"
    )
    log("run remote backend release helper")
    try:
        result = run_ssh(context, helper_command)
        stdout_text = result.stdout
        stderr_text = result.stderr
    except subprocess.CalledProcessError as exc:
        stdout_text = exc.stdout or ""
        stderr_text = exc.stderr or ""
        summary = parse_helper_output(stdout_text) if "__FINAL_STATUS_BEGIN__" in stdout_text else {}
        if stderr_text.strip():
            log(f"remote stderr> {stderr_text.strip()}")
        if summary:
            raise RuntimeError(f"remote backend release helper failed: {summary.get('FAIL_REASON', 'unknown error')}") from exc
        raise
    if stderr_text.strip():
        log(f"remote stderr> {stderr_text.strip()}")
    summary = parse_helper_output(stdout_text)
    if summary.get("FINAL_STATUS") != "passed":
        raise RuntimeError(f"remote backend release helper failed: {summary.get('FAIL_REASON', 'unknown error')}")
    log("remote backend release helper completed")
    return summary


def http_request(
    url: str,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, str], str]:
    req = request.Request(url, data=data, method=method)
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with request.urlopen(req, timeout=30) as response:
            return response.getcode(), dict(response.headers.items()), response.read().decode("utf-8", errors="replace")
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, dict(exc.headers.items()), body


def is_server_error(body: str, status: int) -> bool:
    if status >= 500:
        return True
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return False
    return str(payload.get("code")) == "500"


def public_smoke(base_url: str) -> dict[str, Any]:
    docs_status, docs_headers, docs_body = http_request(f"{base_url.rstrip('/')}/api/v3/api-docs")
    login_payload = json.dumps({"account": "admin", "password": "admin123"}).encode("utf-8")
    login_status, _, login_body = http_request(
        f"{base_url.rstrip('/')}/api/admin/auth/login",
        method="POST",
        data=login_payload,
        headers={"Content-Type": "application/json"},
    )
    recruit_status, _, recruit_body = http_request(f"{base_url.rstrip('/')}/api/admin/recruit/roles?pageNo=1&pageSize=1&keyword=")
    role_status, _, role_body = http_request(f"{base_url.rstrip('/')}/api/role/search?page=1&size=1&keyword=&gender=")
    return {
        "docs_status": docs_status,
        "docs_last_modified": docs_headers.get("Last-Modified", ""),
        "docs_body": docs_body,
        "login_status": login_status,
        "login_body": login_body,
        "recruit_status": recruit_status,
        "recruit_body": recruit_body,
        "role_status": role_status,
        "role_body": role_body,
    }


def write_record(context: ReleaseContext, remote: dict[str, str], public: dict[str, Any]) -> Path:
    record_path = RECORDS_DIR / f"{context.release_id}.md"
    if record_path.exists():
        raise RuntimeError(f"record already exists: {record_path}")
    log(f"write release record {record_path}")

    content = f"""# 后端与管理端发布记录

## 1. 基本信息

- 发布批次号：`{context.release_id}`
- 发布时间：`{remote["REMOTE_DATE"]}`
- 发布范围：`backend-only`
- 操作人：`{context.operator}`
- 关联 Spec / 需求：
  - `00-29 backend-admin-release-governance`
  - 使用标准发布脚本执行一次 `backend-only` 发布

## 2. 发布前检查

- 目标环境：
  - 远端主机：`{context.host}`
  - 后端运行目录：`/opt/kaipai`
  - nginx `/api` 反代目标：`http://kaipai-backend:8080`
- 后端运行时集合核对：
  - 本地工程目录：`{SERVER_DIR}`
  - 本地发布源模式：`{context.source_mode}`
  - 本地构建根目录：`{context.build_root}`
  - 本地工作树非 target 脏改：`{', '.join(context.dirty_paths) if context.dirty_paths else 'none'}`
  - 本轮 overlay 文件：`{', '.join(context.overlay_paths) if context.overlay_paths else 'none'}`
  - 本地构建 JDK：`{context.java_home}`
  - 远端重建方式：`docker compose build kaipai && docker compose up -d --force-recreate kaipai`
  - 运行环境变量回读：见下方 `DOCKER_INSPECT_ENV`
- 管理端运行时集合核对：
  - 本轮不发布管理端，仅要求 `/api` 反代仍正常
- 是否需要联合发布：`否`
- 中止门禁检查结果：`通过，进入 backend-only 脚本发布`

## 3. 产物信息

### 3.1 后端

- 本地 jar 路径：`{context.local_jar_path}`
- 本地 jar SHA256：`{context.local_jar_sha}`
- 远端备份路径：`{remote["BACKUP_PATH"]}`
- 远端落地路径：`{remote["REMOTE_RELEASE_JAR"]}`
- 当前运行 jar：`{remote["RUNTIME_JAR"]}`
- 当前运行 jar SHA256：`{remote["RUNTIME_JAR_SHA"]}`
- 容器内 `/app/app.jar` SHA256：`{remote["CONTAINER_JAR_SHA"]}`

### 3.2 管理端

- 本地源码目录：`N/A`
- 本地快照仓库：`N/A`
- 本地 release branch：`N/A`
- 本地 release commit：`N/A`
- 远端静态备份路径：`N/A`
- 远端源码落地路径：`N/A`
- 远端 bare repo：`N/A`
- 远端检出 branch / commit：`N/A`
- 远端 dist 归档路径：`N/A`
- 远端 dist 归档 SHA256：`N/A`
- `index.html` 回读结果：`N/A`

## 4. 执行摘要

- 后端执行命令摘要：
  - 本地：`mvn -q -DskipTests clean package`
  - 本地：`scp {context.local_jar_path.name} {context.user}@{context.host}:{context.remote_upload_path}`
  - 远端：`sudo -n {REMOTE_HELPER_PATH} --release-id {context.release_id} --upload-path {context.remote_upload_path} --jar-sha {context.local_jar_sha} --operator-user {context.user}`
  - 远端：`docker compose build kaipai && docker compose up -d --force-recreate kaipai`
- 管理端执行命令摘要：`无`
- 是否执行回滚：`否`

## 5. smoke 结果

- 后端容器状态：

```text
{remote["DOCKER_PS"]}
```

- Docker Compose 状态：

```text
{remote["DOCKER_COMPOSE_PS"]}
```

- 运行时环境变量：

```text
{remote["DOCKER_INSPECT_ENV"]}
```

- Compose 后端来源摘录：

```text
{remote["COMPOSE_BACKEND_SOURCE"]}
```

- Compose 渲染后后端定义摘录：

```text
{remote["COMPOSE_RENDERED_BACKEND"]}
```

- `/api/v3/api-docs`：

```text
{remote["INTERNAL_DOCS"]}
```

- 业务接口 smoke：
  - 内网：`POST http://127.0.0.1:8080/api/admin/auth/login`

```text
{remote["INTERNAL_ADMIN_LOGIN"]}
```

  - 内网：`GET http://127.0.0.1:8080/api/admin/recruit/roles?pageNo=1&pageSize=1&keyword=`

```text
{remote["INTERNAL_RECRUIT_ROLES"]}
```

  - 内网：`GET http://127.0.0.1:8080/api/role/search?page=1&size=1&keyword=&gender=`

```text
{remote["INTERNAL_ROLE_SEARCH"]}
```

- 管理端首页：`N/A`
- 实际静态入口资源 smoke：`N/A`
- 后台页面人工验证：`N/A`
- 联合 smoke：`N/A`

## 6. 结论

- 最终结论：`完成`
- 问题与备注：
  - 本轮通过正式发布脚本执行，无人工逐条命令替换
  - 后端重建使用远端 compose 运行定义，避免手写 `docker run` 漂移
  - 若本地存在无关脏改，本脚本会改用 `HEAD clean snapshot + overlay` 构建，并把本轮 overlay 清单写入记录
- 后续动作：
  - 后续 `backend-only` 发布统一调用本脚本

## 7. 附加回读

### 7.1 nginx `/api` 反代块

```text
{remote["NGINX_API_PROXY"]}
```

### 7.2 公网 API Docs

```text
status={public["docs_status"]}
{public["docs_body"].strip()}
```

### 7.3 公网后台登录回包

```text
status={public["login_status"]}
{public["login_body"].strip()}
```

### 7.4 公网招聘角色回包

```text
status={public["recruit_status"]}
{public["recruit_body"].strip()}
```

### 7.5 公网演员角色回包

```text
status={public["role_status"]}
{public["role_body"].strip()}
```

### 7.6 服务端重建版本

```text
{remote["DOCKER_COMPOSE_VERSION"]}
```

### 7.7 容器日志尾部

```text
{remote["DOCKER_LOGS_TAIL"]}
```
"""
    record_path.write_text(content, encoding="utf-8")
    return record_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the standard backend-only release flow.")
    parser.add_argument("--label", required=True, help="release label suffix")
    parser.add_argument("--operator", default=DEFAULT_OPERATOR, help="operator name written to release record")
    parser.add_argument("--host", default=os.getenv("KAIPAI_RELEASE_HOST", DEFAULT_HOST))
    parser.add_argument("--user", default=os.getenv("KAIPAI_RELEASE_USER", DEFAULT_USER))
    parser.add_argument(
        "--identity-file",
        default=os.getenv("KAIPAI_RELEASE_IDENTITY_FILE", str(DEFAULT_IDENTITY_FILE)),
        help="OpenSSH private key path used for native ssh/scp release",
    )
    parser.add_argument(
        "--java-home",
        default=os.getenv("KAIPAI_RELEASE_JAVA_HOME"),
        help="JDK 17 home used for Maven package",
    )
    parser.add_argument(
        "--overlay-path",
        action="append",
        default=[],
        help="server-relative file/dir copied onto a clean HEAD snapshot when worktree has non-target dirty changes; repeatable",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    release_time = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    release_id = f"{release_time}-backend-only-{args.label}"
    remote_upload_path = f"/home/{args.user}/backend-release-uploads/{release_id}/kaipai-backend-1.0.0-SNAPSHOT.jar"
    context = ReleaseContext(
        release_id=release_id,
        release_time=release_time,
        host=args.host,
        user=args.user,
        operator=args.operator,
        label=args.label,
        identity_file=Path(args.identity_file),
        java_home=resolve_java_home(args.java_home),
        remote_upload_path=remote_upload_path,
        local_jar_path=TARGET_JAR,
        build_root=SERVER_DIR,
    )

    if not context.identity_file.exists():
        raise RuntimeError(
            f"identity file not found: {context.identity_file}. Run "
            "`python .sce/runbooks/backend-admin-release/scripts/bootstrap-admin-release.py --operator <name>` first."
        )

    log(f"release start: {context.release_id}")
    try:
        require_key_auth(context)
        require_helper(context)
        require_schema_history_synced(context)
        prepare_release_source(context, args.overlay_path)
        build_backend(context)
        upload_jar(context)
        remote = deploy_backend_only(context)
        public = public_smoke(f"http://{context.host}")
        if (
            public["docs_status"] != 200
            or is_server_error(public["login_body"], public["login_status"])
            or is_server_error(public["recruit_body"], public["recruit_status"])
            or is_server_error(public["role_body"], public["role_status"])
        ):
            raise RuntimeError(f"public smoke failed: {public}")
        log("backend-only release smoke passed")
        record_path = write_record(context, remote, public)
        log(f"release completed: {context.release_id}")
        print(
            json.dumps(
                {
                    "release_id": context.release_id,
                    "record_path": str(record_path),
                    "local_jar_path": str(context.local_jar_path),
                    "local_jar_sha": context.local_jar_sha,
                    "public_docs_status": public["docs_status"],
                    "public_login_status": public["login_status"],
                    "public_recruit_status": public["recruit_status"],
                    "public_role_status": public["role_status"],
                    "source_mode": context.source_mode,
                    "overlay_paths": context.overlay_paths,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    finally:
        cleanup_release_source(context)


if __name__ == "__main__":
    sys.exit(main())
