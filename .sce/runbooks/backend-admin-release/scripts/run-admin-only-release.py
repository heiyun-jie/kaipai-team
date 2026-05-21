import argparse
import ipaddress
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import error, parse, request


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"
TMP_DIR = ROOT / "tmp"
ADMIN_DIR = ROOT / "kaipai-admin"

DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_OPERATOR = "codex"
DEFAULT_PUBLIC_BASE_URL = "https://kplyyk.com"
ADMIN_SMOKE_PASSWORD_ENV = "KAIPAI_ADMIN_SMOKE_PASSWORD"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-admin-release-helper.sh"
REMOTE_BARE_REPO_PATH = f"/home/{DEFAULT_USER}/kaipai-admin-release.git"


@dataclass
class ReleaseContext:
    release_id: str
    release_time: str
    host: str
    user: str
    operator: str
    label: str
    public_base_url: str
    identity_file: Path
    snapshot_root: Path
    git_branch: str = ""
    git_commit: str = ""
    asset_path: str = ""


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


def copy_admin_snapshot(snapshot_root: Path) -> None:
    include_names = [
        ".env.production",
        ".gitignore",
        "index.html",
        "package-lock.json",
        "package.json",
        "public",
        "scripts",
        "src",
        "tsconfig.app.json",
        "tsconfig.json",
        "tsconfig.node.json",
        "vite.config.ts",
    ]
    if snapshot_root.exists():
        shutil.rmtree(snapshot_root)
    snapshot_root.mkdir(parents=True, exist_ok=True)
    for name in include_names:
        source = ADMIN_DIR / name
        if not source.exists():
            raise RuntimeError(f"required admin source path missing: {source}")
        target = snapshot_root / name
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def prepare_snapshot_repo(context: ReleaseContext) -> None:
    log(f"prepare git snapshot repo for release {context.release_id}")
    copy_admin_snapshot(context.snapshot_root)
    git = resolve_executable("git")
    run_process([git, "init", "--initial-branch=release"], cwd=context.snapshot_root)
    run_process([git, "config", "user.name", "Codex Release"], cwd=context.snapshot_root)
    run_process([git, "config", "user.email", "codex-release@local"], cwd=context.snapshot_root)
    run_process([git, "config", "core.autocrlf", "false"], cwd=context.snapshot_root)
    run_process([git, "config", "core.safecrlf", "false"], cwd=context.snapshot_root)
    run_process([git, "add", "."], cwd=context.snapshot_root)
    run_process([git, "commit", "-m", f"release {context.release_id}"], cwd=context.snapshot_root)
    context.git_commit = run_process([git, "rev-parse", "HEAD"], cwd=context.snapshot_root, capture_output=True).stdout.strip()
    if not context.git_commit:
        raise RuntimeError("failed to resolve snapshot commit")
    context.git_branch = f"release/{context.release_id}"
    log(f"snapshot commit ready: {context.git_commit} branch={context.git_branch}")


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


def git_ssh_command(context: ReleaseContext) -> str:
    ssh = resolve_executable("ssh")
    return (
        f'"{ssh}" -i "{context.identity_file}" -o BatchMode=yes -o IdentitiesOnly=yes '
        "-o StrictHostKeyChecking=accept-new"
    )


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


def require_public_smoke_dns(context: ReleaseContext) -> None:
    host = parse.urlparse(context.public_base_url).hostname
    if not host:
        raise RuntimeError(f"invalid public base url: {context.public_base_url}")
    fake_proxy_net = ipaddress.ip_network("198.18.0.0/15")
    try:
        infos = socket.getaddrinfo(host, None, family=socket.AF_INET, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise RuntimeError(f"failed to resolve public smoke host {host}: {exc}") from exc
    addresses = sorted({item[4][0] for item in infos})
    blocked = []
    for raw in addresses:
        address = ipaddress.ip_address(raw)
        if address.is_loopback or address.is_link_local or address.is_unspecified or address in fake_proxy_net:
            blocked.append(raw)
    if blocked:
        raise RuntimeError(
            "public smoke DNS is polluted by local/proxy address; "
            f"host={host}, addresses={addresses}. Stop local proxy and remove hosts/DNS override before release."
        )
    log(f"public smoke DNS verified: {host} -> {', '.join(addresses)}")


def push_snapshot_repo(context: ReleaseContext) -> None:
    git = resolve_executable("git")
    remote_url = f"ssh://{context.user}@{context.host}{REMOTE_BARE_REPO_PATH}"
    run_process([git, "remote", "add", "origin", remote_url], cwd=context.snapshot_root)
    env = os.environ.copy()
    env["GIT_SSH_COMMAND"] = git_ssh_command(context)
    run_process(
        [git, "push", "--force", "origin", f"HEAD:refs/heads/{context.git_branch}"],
        cwd=context.snapshot_root,
        env=env,
    )
    log(f"pushed git snapshot to {remote_url} ref={context.git_branch}")


def parse_helper_output(output: str) -> dict[str, str]:
    fields = [
        "REMOTE_DATE",
        "PRE_INDEX_STATUS",
        "BACKUP_PATH",
        "REMOTE_REPO_PATH",
        "REMOTE_GIT_BRANCH",
        "REMOTE_GIT_COMMIT",
        "NODE_VERSION",
        "NPM_VERSION",
        "REMOTE_DIST_ARCHIVE_PATH",
        "REMOTE_DIST_SHA",
        "HTML_LISTING",
        "INDEX_HEAD",
        "INTERNAL_SMOKE",
        "DOCKER_PS",
        "BUILD_LOG_TAIL",
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


def deploy_admin_only(context: ReleaseContext) -> dict[str, str]:
    helper_command = (
        f"sudo -n {REMOTE_HELPER_PATH} "
        f"--release-id {context.release_id} "
        f"--git-branch {context.git_branch} "
        f"--git-commit {context.git_commit} "
        f"--operator-user {context.user}"
    )
    log("run remote admin release helper")
    result = run_ssh(context, helper_command)
    if result.stderr.strip():
        log(f"remote stderr> {result.stderr.strip()}")
    summary = parse_helper_output(result.stdout)
    log("remote admin release helper completed")
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


def extract_asset_path(index_html: str) -> str:
    matches = re.findall(r"""(?:src|href)=["'](/?assets/[^"'?#]+\.(?:js|css))["']""", index_html)
    if not matches:
        return ""
    for candidate in matches:
        if candidate.endswith(".js"):
            return candidate if candidate.startswith("/") else f"/{candidate}"
    candidate = matches[0]
    return candidate if candidate.startswith("/") else f"/{candidate}"


def public_smoke(base_url: str) -> dict[str, Any]:
    log(f"public smoke> GET {base_url}")
    index_status, index_headers, index_body = http_request(base_url)
    asset_path = extract_asset_path(index_body)
    if not asset_path:
        raise RuntimeError("failed to locate deployed asset entry from public index")
    log(f"public smoke> GET {base_url.rstrip('/')}{asset_path}")
    asset_status, asset_headers, _ = http_request(f"{base_url.rstrip('/')}{asset_path}")
    log(f"public smoke> GET {base_url.rstrip('/')}/api/v3/api-docs")
    docs_status, docs_headers, docs_body = http_request(f"{base_url.rstrip('/')}/api/v3/api-docs")
    smoke_password = os.environ.get(ADMIN_SMOKE_PASSWORD_ENV)
    if not smoke_password:
        raise RuntimeError(f"{ADMIN_SMOKE_PASSWORD_ENV} is required for admin login smoke")
    payload = json.dumps({"account": "admin", "password": smoke_password}).encode("utf-8")
    log(f"public smoke> POST {base_url.rstrip('/')}/api/admin/auth/login")
    login_status, _, login_body = http_request(
        f"{base_url.rstrip('/')}/api/admin/auth/login",
        method="POST",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    return {
        "index_status": index_status,
        "index_last_modified": index_headers.get("Last-Modified", ""),
        "index_body": index_body,
        "asset_path": asset_path,
        "asset_status": asset_status,
        "asset_last_modified": asset_headers.get("Last-Modified", ""),
        "docs_status": docs_status,
        "docs_last_modified": docs_headers.get("Last-Modified", ""),
        "docs_body": docs_body,
        "login_status": login_status,
        "login_body": login_body,
    }


def blocked_public_smoke(reason: str) -> dict[str, Any]:
    return {
        "index_status": "BLOCKED",
        "index_last_modified": "",
        "index_body": reason,
        "asset_path": "",
        "asset_status": "BLOCKED",
        "asset_last_modified": "",
        "docs_status": "BLOCKED",
        "docs_last_modified": "",
        "docs_body": reason,
        "login_status": "BLOCKED",
        "login_body": reason,
        "review_gate": "阻断",
        "final_conclusion": "远端静态替换完成，公网审查阻断",
        "review_rule": "远端 helper 完成静态替换，但公网业务域名 DNS/证书/入口未通过，禁止标记发布完成",
    }


def write_record(context: ReleaseContext, remote: dict[str, str], public: dict[str, Any]) -> Path:
    record_path = RECORDS_DIR / f"{context.release_id}.md"
    if record_path.exists():
        raise RuntimeError(f"record already exists: {record_path}")
    log(f"write release record {record_path}")
    final_conclusion = public.get("final_conclusion", "完成")
    review_gate = public.get("review_gate", "通过")
    review_rule = public.get(
        "review_rule",
        "远端 helper 完成静态替换、首页资源 smoke 通过、后台登录接口 smoke 通过、发布记录已写入 `records/`",
    )

    content = f"""# 后端与管理端发布记录

## 1. 基本信息

- 发布批次号：`{context.release_id}`
- 发布时间：`{remote["REMOTE_DATE"]}`
- 发布范围：`admin-only`
- 操作人：`{context.operator}`
- 关联 Spec / 需求：
  - `00-29 backend-admin-release-governance`
  - 使用标准发布脚本执行一次 `admin-only` 发布

## 2. 发布前检查

- 目标环境：
  - 远端主机：`{context.host}`
  - 公网审查域名：`{context.public_base_url}`
  - nginx 静态目录：`/opt/kaipai/nginx/html`
  - nginx `/api` 反代目标：`http://kaipai-backend:8080`
- 后端运行时集合核对：
  - 本轮不发布后端，仅要求 `/api/v3/api-docs` 正常
- 管理端运行时集合核对：
  - 本地快照源目录：`{ADMIN_DIR}`
  - 本地快照仓库：`{context.snapshot_root}`
  - 发布对象：`git snapshot commit {context.git_commit}`
  - 线上首页发布前状态：`{remote["PRE_INDEX_STATUS"]}`
  - 标准认证链路：`OpenSSH key auth`
  - 标准远端执行链路：`sudo -n {REMOTE_HELPER_PATH}`
  - 服务端构建运行时：`node {remote["NODE_VERSION"]} / npm {remote["NPM_VERSION"]}`
- 是否需要联合发布：`否`
- 中止门禁检查结果：`通过，进入 admin-only git snapshot 发布`

## 3. 产物信息

### 3.1 后端

- 本地 jar 路径：`N/A`
- 本地 jar SHA256：`N/A`
- 远端备份路径：`N/A`
- 远端落地路径：`N/A`
- 容器内 `/app/app.jar` SHA256：`N/A`

### 3.2 管理端

- 本地源码目录：`{ADMIN_DIR}`
- 本地快照仓库：`{context.snapshot_root}`
- 本地 release branch：`{context.git_branch}`
- 本地 release commit：`{context.git_commit}`
- 远端静态备份路径：`{remote["BACKUP_PATH"]}`
- 远端源码落地路径：`{remote["REMOTE_REPO_PATH"]}`
- 远端 bare repo：`{REMOTE_BARE_REPO_PATH}`
- 远端检出 branch：`{remote["REMOTE_GIT_BRANCH"]}`
- 远端检出 commit：`{remote["REMOTE_GIT_COMMIT"]}`
- 远端 dist 归档路径：`{remote["REMOTE_DIST_ARCHIVE_PATH"]}`
- 远端 dist 归档 SHA256：`{remote["REMOTE_DIST_SHA"]}`
- `index.html` 回读结果：

```html
{remote["INDEX_HEAD"]}
```

## 4. 执行摘要

- 后端执行命令摘要：`无`
- 管理端执行命令摘要：
  - 本地：`生成 kaipai-admin 临时 git snapshot 仓库`
  - 本地：`git push origin HEAD:refs/heads/{context.git_branch}`
  - 远端：`sudo -n {REMOTE_HELPER_PATH} --release-id {context.release_id} --git-branch {context.git_branch} --git-commit {context.git_commit} --operator-user {context.user}`
  - 远端：`git fetch && git checkout {context.git_commit} && npm ci && npm run build`
- 是否执行回滚：`否`

## 5. smoke 结果

- 后端容器状态：

```text
{remote["DOCKER_PS"]}
```

- `/api/v3/api-docs`：

```text
{remote["INTERNAL_SMOKE"]}
```

- 业务接口 smoke：
  - 公网：`GET {context.public_base_url}/api/v3/api-docs` -> `{public["docs_status"]}`
  - 公网：`POST {context.public_base_url}/api/admin/auth/login` -> `{public["login_status"]}`
- 管理端首页：
  - 公网：`{context.public_base_url}/ -> {public["index_status"]}`
  - 公网首页 `Last-Modified`：`{public["index_last_modified"]}`
  - 公网静态资源：`{context.public_base_url}{public["asset_path"]} -> {public["asset_status"]}`
- 后台页面人工验证：
  - 通过公网首页 HTML 回读确认已加载当前静态入口
  - 通过后台登录接口确认页面依赖接口可用
- 联合 smoke：`N/A`

## 6. 结论

- 最终结论：`{final_conclusion}`
- 发布后审查：
  - 公网审查域名：`{context.public_base_url}`
  - 审查门禁：`{review_gate}`
  - 判定规则：{review_rule}
- 问题与备注：
  - 本轮通过正式发布脚本执行，无人工逐条命令替换
  - 正式发布链路使用 `git snapshot -> push bare repo -> helper checkout/build`
- 后续动作：
  - 后续 `admin-only` 发布统一调用本脚本

## 7. 附加回读

### 7.1 远端静态目录

```text
{remote["HTML_LISTING"]}
```

### 7.2 公网首页 HTML

```html
{public["index_body"].strip()}
```

### 7.3 公网后台登录回包

```json
{public["login_body"].strip()}
```

### 7.4 公网 API Docs 回包

```json
{public["docs_body"].strip()}
```

### 7.5 服务端构建日志尾部

```text
{remote["BUILD_LOG_TAIL"]}
```
"""
    record_path.write_text(content, encoding="utf-8")
    return record_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the standard admin-only release flow.")
    parser.add_argument("--label", required=True, help="release label suffix")
    parser.add_argument("--operator", default=DEFAULT_OPERATOR, help="operator name written to release record")
    parser.add_argument("--host", default=os.getenv("KAIPAI_RELEASE_HOST", DEFAULT_HOST))
    parser.add_argument("--user", default=os.getenv("KAIPAI_RELEASE_USER", DEFAULT_USER))
    parser.add_argument(
        "--public-base-url",
        default=os.getenv("KAIPAI_PUBLIC_BASE_URL", DEFAULT_PUBLIC_BASE_URL),
        help="public domain used for post-release smoke and release record",
    )
    parser.add_argument(
        "--identity-file",
        default=os.getenv("KAIPAI_RELEASE_IDENTITY_FILE", str(DEFAULT_IDENTITY_FILE)),
        help="OpenSSH private key path used for native ssh/git release",
    )
    parser.add_argument(
        "--allow-domain-blocked-deploy",
        action="store_true",
        help="continue remote static replacement when public DNS is blocked, write a blocked record, and exit non-zero",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    release_time = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    release_id = f"{release_time}-admin-only-{args.label}"
    snapshot_root = TMP_DIR / f"admin-git-snapshot-{release_id}"
    context = ReleaseContext(
        release_id=release_id,
        release_time=release_time,
        host=args.host,
        user=args.user,
        operator=args.operator,
        label=args.label,
        public_base_url=args.public_base_url.rstrip("/"),
        identity_file=Path(args.identity_file),
        snapshot_root=snapshot_root,
    )

    if not context.identity_file.exists():
        raise RuntimeError(
            f"identity file not found: {context.identity_file}. Run "
            "`python .sce/runbooks/backend-admin-release/scripts/bootstrap-admin-release.py --operator <name>` first."
        )

    log(f"release start: {context.release_id}")
    domain_blocker = ""
    try:
        require_public_smoke_dns(context)
    except RuntimeError as exc:
        if not args.allow_domain_blocked_deploy:
            raise
        domain_blocker = str(exc)
        log(f"public smoke DNS blocked; continue deploy in blocked-record mode: {domain_blocker}")
    require_key_auth(context)
    prepare_snapshot_repo(context)
    push_snapshot_repo(context)
    remote = deploy_admin_only(context)
    if domain_blocker:
        public = blocked_public_smoke(domain_blocker)
        context.asset_path = ""
        log("admin-only remote deploy completed, public smoke blocked")
    else:
        public = public_smoke(f"{context.public_base_url}/")
        context.asset_path = public["asset_path"]
        if (
            public["index_status"] != 200
            or public["asset_status"] != 200
            or public["docs_status"] != 200
            or public["login_status"] != 200
        ):
            raise RuntimeError(f"public smoke failed: {public}")
        log("admin-only release smoke passed")
    record_path = write_record(context, remote, public)
    log(f"release completed: {context.release_id}")

    print(
        json.dumps(
            {
                "release_id": context.release_id,
                "record_path": str(record_path),
                "snapshot_root": str(context.snapshot_root),
                "git_branch": context.git_branch,
                "git_commit": context.git_commit,
                "public_base_url": context.public_base_url,
                "public_index_status": public["index_status"],
                "public_asset_status": public["asset_status"],
                "public_docs_status": public["docs_status"],
                "public_login_status": public["login_status"],
                "review_gate": public.get("review_gate", "通过"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 2 if domain_blocker else 0


if __name__ == "__main__":
    sys.exit(main())
