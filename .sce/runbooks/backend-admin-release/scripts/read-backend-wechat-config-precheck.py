import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
DIAGNOSTICS_DIR = RUNBOOK_DIR / "records" / "diagnostics"

DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
DEFAULT_CONTAINER = "kaipai-backend"
DEFAULT_SINCE = "15m"
DEFAULT_TAIL = 200
DEFAULT_NACOS_SERVER_ADDR = "127.0.0.1:8848"
DEFAULT_NACOS_DATA_IDS = ["kaipai-backend", "kaipai-backend.yml", "kaipai-backend-dev.yml"]
DEFAULT_NACOS_GROUP = "DEFAULT_GROUP"
DEFAULT_NACOS_NAMESPACE = ""
DEFAULT_NACOS_GREP = "WECHAT_MINIAPP|wechat\\.miniapp"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"
REQUIRED_COMPOSE_ENV_KEYS = ["WECHAT_MINIAPP_APP_ID", "WECHAT_MINIAPP_APP_SECRET"]
REQUIRED_NACOS_KEYS = ["app-id", "app-secret"]


@dataclass
class PrecheckContext:
    capture_id: str
    label: str
    host: str
    user: str
    identity_file: Path
    container: str
    since: str
    tail: int
    nacos_server_addr: str
    data_ids: list[str]
    group: str
    namespace: str
    nacos_grep: str
    fail_on_missing: bool
    output_dir: Path


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


def ssh_base(context: PrecheckContext) -> list[str]:
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


def run_ssh(context: PrecheckContext, remote_command: str) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(context) + [remote_command], capture_output=True)


def require_key_auth(context: PrecheckContext) -> None:
    result = run_ssh(context, "printf 'key-auth-ok'")
    if result.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe returned unexpected output")
    log("native ssh key auth verified")


def require_helper(context: PrecheckContext) -> None:
    result = run_ssh(context, f"sudo -n {REMOTE_HELPER_PATH} --healthcheck")
    if result.stdout.strip() != "helper-ok":
        raise RuntimeError("backend helper healthcheck returned unexpected output")
    log("remote backend helper and sudoers verified")


def sanitize_label(label: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in label.strip())
    collapsed = "-".join(part for part in normalized.split("-") if part)
    return collapsed or "backend-wechat-config-precheck"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def parse_helper_output(output: str, fields: list[str]) -> dict[str, str]:
    summary: dict[str, str] = {}
    for field in fields:
        begin = f"__{field}_BEGIN__"
        end = f"__{field}_END__"
        match = re.search(rf"{re.escape(begin)}\n(.*?)\n{re.escape(end)}", output, re.S)
        if not match:
            raise RuntimeError(f"missing helper output section: {field}")
        summary[field] = match.group(1).strip()
    return summary


def collect_runtime(context: PrecheckContext) -> dict[str, str]:
    helper_command = (
        f"sudo -n {REMOTE_HELPER_PATH} "
        f"--runtime-diagnostics "
        f"--container {shlex.quote(context.container)} "
        f"--since {shlex.quote(context.since)} "
        f"--tail {context.tail}"
    )
    result = run_ssh(context, helper_command)
    if result.stderr and result.stderr.strip():
        log(f"remote stderr> {result.stderr.strip()}")
    summary = parse_helper_output(
        result.stdout,
        [
            "REMOTE_DATE",
            "DOCKER_PS",
            "DOCKER_INSPECT_ENV",
            "DOCKER_LOGS_TAIL",
            "COMPOSE_BACKEND_SOURCE",
            "COMPOSE_RENDERED_BACKEND",
            "FINAL_STATUS",
            "FAIL_REASON",
        ],
    )
    if summary["FINAL_STATUS"] != "passed":
        raise RuntimeError(f"runtime diagnostic helper failed: {summary['FAIL_REASON']}")
    return summary


def collect_nacos(context: PrecheckContext) -> dict[str, str]:
    data_ids_value = ",".join(context.data_ids)
    helper_command = (
        f"sudo -n {REMOTE_HELPER_PATH} "
        f"--nacos-config-scan "
        f"--nacos-server-addr {shlex.quote(context.nacos_server_addr)} "
        f"--nacos-data-ids {shlex.quote(data_ids_value)} "
        f"--nacos-group {shlex.quote(context.group)} "
        f"--nacos-namespace {shlex.quote(context.namespace)} "
        f"--nacos-grep {shlex.quote(context.nacos_grep)}"
    )
    result = run_ssh(context, helper_command)
    if result.stderr and result.stderr.strip():
        log(f"remote stderr> {result.stderr.strip()}")
    summary = parse_helper_output(
        result.stdout,
        [
            "REMOTE_DATE",
            "NACOS_SERVER_ADDR",
            "NACOS_DATA_IDS",
            "NACOS_LOGIN_OUTPUT",
            "NACOS_CONFIG_PRESENCE_SUMMARY",
            "NACOS_FILTERED_CONFIGS",
            "FINAL_STATUS",
            "FAIL_REASON",
        ],
    )
    if summary["FINAL_STATUS"] != "passed":
        raise RuntimeError(f"nacos config scan failed: {summary['FAIL_REASON']}")
    return summary


def find_present_keys(text: str, keys: list[str]) -> list[str]:
    present: list[str] = []
    for key in keys:
        if re.search(rf"(?im)\b{re.escape(key)}\b", text):
            present.append(key)
    return present


def find_missing_keys(text: str, keys: list[str]) -> list[str]:
    present = set(find_present_keys(text, keys))
    return [key for key in keys if key not in present]


def parse_nacos_presence(summary_text: str, data_ids: list[str]) -> dict[str, dict[str, list[str]]]:
    results: dict[str, dict[str, list[str]]] = {}
    lines = [line.strip() for line in summary_text.splitlines() if line.strip()]
    for data_id in data_ids:
        results[data_id] = {"missing": [], "present": []}

    missing_pattern = re.compile(r"^- (?P<data_id>.+?): missing (?P<key>.+)$")
    for line in lines:
        match = missing_pattern.match(line)
        if not match:
            continue
        data_id = match.group("data_id")
        key = match.group("key")
        if data_id not in results:
            results[data_id] = {"missing": [], "present": []}
        results[data_id]["missing"].append(key)

    for data_id, detail in results.items():
        missing = set(detail["missing"])
        detail["present"] = [key for key in REQUIRED_NACOS_KEYS if key not in missing]
    return results


def build_gate_result(
    *,
    compose_source: str,
    compose_rendered: str,
    inspect_env: str,
    nacos_presence_summary: str,
    data_ids: list[str],
) -> dict[str, object]:
    compose_source_missing = find_missing_keys(compose_source, REQUIRED_COMPOSE_ENV_KEYS)
    compose_rendered_missing = find_missing_keys(compose_rendered, REQUIRED_COMPOSE_ENV_KEYS)
    container_env_missing = find_missing_keys(inspect_env, REQUIRED_COMPOSE_ENV_KEYS)
    nacos_by_data_id = parse_nacos_presence(nacos_presence_summary, data_ids)

    failing_checks: list[str] = []
    if compose_source_missing:
        failing_checks.append("compose_source")
    if compose_rendered_missing:
        failing_checks.append("compose_rendered")
    if container_env_missing:
        failing_checks.append("container_env")
    for data_id, detail in nacos_by_data_id.items():
        if detail["missing"]:
            failing_checks.append(f"nacos:{data_id}")

    return {
        "status": "passed" if not failing_checks else "blocked",
        "requiredComposeEnvKeys": REQUIRED_COMPOSE_ENV_KEYS,
        "requiredNacosKeys": REQUIRED_NACOS_KEYS,
        "checks": {
            "composeSource": {
                "present": [key for key in REQUIRED_COMPOSE_ENV_KEYS if key not in compose_source_missing],
                "missing": compose_source_missing,
            },
            "composeRendered": {
                "present": [key for key in REQUIRED_COMPOSE_ENV_KEYS if key not in compose_rendered_missing],
                "missing": compose_rendered_missing,
            },
            "containerEnv": {
                "present": [key for key in REQUIRED_COMPOSE_ENV_KEYS if key not in container_env_missing],
                "missing": container_env_missing,
            },
            "nacosDataIds": nacos_by_data_id,
        },
        "failingChecks": failing_checks,
    }


def render_gate_markdown(context: PrecheckContext, gate: dict[str, object]) -> str:
    checks = gate["checks"]  # type: ignore[index]
    compose_source = checks["composeSource"]  # type: ignore[index]
    compose_rendered = checks["composeRendered"]  # type: ignore[index]
    container_env = checks["containerEnv"]  # type: ignore[index]
    nacos_data_ids = checks["nacosDataIds"]  # type: ignore[index]
    failing = gate["failingChecks"]  # type: ignore[index]

    lines = [
        "# 后端微信配置门禁预检查",
        "",
        f"- Capture ID: `{context.capture_id}`",
        f"- Label: `{context.label}`",
        f"- Host: `{context.host}`",
        f"- Container: `{context.container}`",
        f"- Gate Result: `{gate['status']}`",
        "",
        "## Compose / Runtime",
        "",
        f"- compose source present: `{', '.join(compose_source['present']) or '--'}`",
        f"- compose source missing: `{', '.join(compose_source['missing']) or '--'}`",
        f"- compose rendered present: `{', '.join(compose_rendered['present']) or '--'}`",
        f"- compose rendered missing: `{', '.join(compose_rendered['missing']) or '--'}`",
        f"- container env present: `{', '.join(container_env['present']) or '--'}`",
        f"- container env missing: `{', '.join(container_env['missing']) or '--'}`",
        "",
        "## Nacos",
        "",
    ]

    for data_id, detail in nacos_data_ids.items():  # type: ignore[union-attr]
        lines.append(f"- `{data_id}` present: `{', '.join(detail['present']) or '--'}`")
        lines.append(f"- `{data_id}` missing: `{', '.join(detail['missing']) or '--'}`")

    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            f"- failing checks: `{', '.join(failing) or '--'}`",
        ]
    )

    if gate["status"] == "passed":
        lines.append("- current result: compose source, rendered config, container env, and Nacos dataIds all contain the required WeChat keys")
    else:
        lines.append("- current result: required WeChat keys are still incomplete across compose/runtime and Nacos, so wxacode/login-auth real-environment gate is not open")
        lines.append("- next step: first补齐合法配置来源，再按 `backend-only` 标准发布重建，并复跑本预检查")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a combined readonly precheck for backend WeChat config sources across compose/runtime/Nacos.",
    )
    parser.add_argument("--label", default="backend-wechat-config-precheck")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--identity-file", default=str(DEFAULT_IDENTITY_FILE))
    parser.add_argument("--container", default=DEFAULT_CONTAINER)
    parser.add_argument("--since", default=DEFAULT_SINCE)
    parser.add_argument("--tail", type=int, default=DEFAULT_TAIL)
    parser.add_argument("--nacos-server-addr", default=DEFAULT_NACOS_SERVER_ADDR)
    parser.add_argument("--nacos-data-id", action="append", dest="data_ids")
    parser.add_argument("--nacos-group", default=DEFAULT_NACOS_GROUP)
    parser.add_argument("--nacos-namespace", default=DEFAULT_NACOS_NAMESPACE)
    parser.add_argument("--nacos-grep", default=DEFAULT_NACOS_GREP)
    parser.add_argument("--no-fail-on-missing", action="store_true")
    args = parser.parse_args()

    capture_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{sanitize_label(args.label)}"
    output_dir = DIAGNOSTICS_DIR / capture_id
    context = PrecheckContext(
        capture_id=capture_id,
        label=args.label,
        host=args.host,
        user=args.user,
        identity_file=Path(args.identity_file),
        container=args.container,
        since=args.since,
        tail=args.tail,
        nacos_server_addr=args.nacos_server_addr,
        data_ids=args.data_ids or list(DEFAULT_NACOS_DATA_IDS),
        group=args.nacos_group,
        namespace=args.nacos_namespace,
        nacos_grep=args.nacos_grep,
        fail_on_missing=not args.no_fail_on_missing,
        output_dir=output_dir,
    )

    ensure_dir(context.output_dir)
    require_key_auth(context)
    require_helper(context)

    runtime = collect_runtime(context)
    nacos = collect_nacos(context)

    write_text(context.output_dir / "docker-ps.txt", runtime["DOCKER_PS"])
    write_text(context.output_dir / "docker-inspect-env.txt", runtime["DOCKER_INSPECT_ENV"])
    write_text(context.output_dir / "docker-logs.txt", runtime["DOCKER_LOGS_TAIL"])
    write_text(context.output_dir / "compose-backend-source.txt", runtime["COMPOSE_BACKEND_SOURCE"])
    write_text(context.output_dir / "compose-rendered-backend.txt", runtime["COMPOSE_RENDERED_BACKEND"])
    write_text(context.output_dir / "nacos-config-presence-summary.txt", nacos["NACOS_CONFIG_PRESENCE_SUMMARY"])
    write_text(context.output_dir / "nacos-filtered-configs.txt", nacos["NACOS_FILTERED_CONFIGS"])
    write_text(context.output_dir / "nacos-login-output.txt", nacos["NACOS_LOGIN_OUTPUT"])

    gate = build_gate_result(
        compose_source=runtime["COMPOSE_BACKEND_SOURCE"],
        compose_rendered=runtime["COMPOSE_RENDERED_BACKEND"],
        inspect_env=runtime["DOCKER_INSPECT_ENV"],
        nacos_presence_summary=nacos["NACOS_CONFIG_PRESENCE_SUMMARY"],
        data_ids=context.data_ids,
    )
    summary_json = {
        "captureId": context.capture_id,
        "capturedAt": datetime.now().astimezone().isoformat(),
        "label": context.label,
        "host": context.host,
        "user": context.user,
        "container": context.container,
        "runtime": {
            "remoteDate": runtime["REMOTE_DATE"],
        },
        "nacos": {
            "remoteDate": nacos["REMOTE_DATE"],
            "serverAddr": nacos["NACOS_SERVER_ADDR"],
            "dataIds": context.data_ids,
            "group": context.group,
            "namespace": context.namespace,
        },
        "gate": gate,
        "files": {
            "dockerPs": "docker-ps.txt",
            "inspectEnv": "docker-inspect-env.txt",
            "dockerLogs": "docker-logs.txt",
            "composeBackendSource": "compose-backend-source.txt",
            "composeRenderedBackend": "compose-rendered-backend.txt",
            "nacosPresenceSummary": "nacos-config-presence-summary.txt",
            "nacosFilteredConfigs": "nacos-filtered-configs.txt",
            "nacosLoginOutput": "nacos-login-output.txt",
            "summaryMarkdown": "summary.md",
        },
    }
    write_text(context.output_dir / "summary.md", render_gate_markdown(context, gate))
    write_text(context.output_dir / "summary.json", json.dumps(summary_json, ensure_ascii=False, indent=2))
    log(f"wechat config precheck saved: {context.output_dir}")
    print(
        json.dumps(
            {
                "capture_id": context.capture_id,
                "output_dir": str(context.output_dir),
                "status": gate["status"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    if gate["status"] != "passed" and context.fail_on_missing:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
