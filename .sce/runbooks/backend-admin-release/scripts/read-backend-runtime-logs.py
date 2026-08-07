import argparse
import json
import os
import re
import shutil
import shlex
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
DEFAULT_TAIL = 400
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"

SAFE_ENV_VALUE_KEYS = frozenset(
    {
        "SPRING_PROFILES_ACTIVE",
        "NACOS_ENABLED",
        "SERVER_PORT",
    }
)
SAFE_SPRING_PROFILE_VALUES = frozenset({"dev", "prod", "test"})
SAFE_DOCKER_LOGGING_VALUE_KEYS = frozenset({"max-size", "max-file", "compress", "mode"})
SAFE_DOCKER_LOGGING_DRIVERS = frozenset(
    {
        "awslogs",
        "etwlogs",
        "fluentd",
        "gcplogs",
        "gelf",
        "journald",
        "json-file",
        "local",
        "none",
        "splunk",
        "syslog",
    }
)
ENVIRONMENT_ENTRY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
LOGGING_ENTRY_RE = re.compile(r"^([A-Za-z0-9_.-]+)=(.*)$")
COMPOSE_ENV_ENTRY_RE = re.compile(
    r"^(?P<prefix>(?:[0-9]+:)?\s*(?:-\s*)?)(?P<opening_quote>['\"]?)"
    r"(?P<key>[A-Za-z_][A-Za-z0-9_.-]*)(?P<closing_quote>['\"]?)"
    r"(?P<separator>\s*[:=]\s*)(?P<value>.*)$"
)
SAFE_COMPOSE_STRUCTURE_RE = re.compile(
    r"^[0-9]+:\s*(?:services:|kaipai:|environment:|ports:)$"
)
DAY_WINDOW_RE = re.compile(
    r"^(?P<days>[0-9]+)d(?P<suffix>(?:[0-9]+(?:ms|us|\N{MICRO SIGN}s|ns|h|m|s))*)$"
)
DOCKER_DURATION_RE = re.compile(r"^(?:[0-9]+(?:ms|us|\N{MICRO SIGN}s|ns|h|m|s))+$")
NOT_CAPTURED = "not-captured"


@dataclass
class DiagnosticContext:
    capture_id: str
    host: str
    user: str
    identity_file: Path
    container: str
    since: str
    tail: int
    grep: str | None
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
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
    )


def ssh_base(context: DiagnosticContext) -> list[str]:
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


def run_ssh(context: DiagnosticContext, remote_command: str) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(context) + [remote_command], capture_output=True)


def require_key_auth(context: DiagnosticContext) -> None:
    result = run_ssh(context, "printf 'key-auth-ok'")
    if result.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe returned unexpected output")
    log("native ssh key auth verified")


def require_helper(context: DiagnosticContext) -> None:
    result = run_ssh(context, f"sudo -n {REMOTE_HELPER_PATH} --healthcheck")
    if result.stdout.strip() != "helper-ok":
        raise RuntimeError("backend helper healthcheck returned unexpected output")
    log("remote backend helper and sudoers verified")


def run_remote_bash(context: DiagnosticContext, command: str) -> str:
    result = run_ssh(context, command)
    if result.stderr and result.stderr.strip():
        log("remote command returned stderr; details omitted")
    return result.stdout


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def sanitize_label(label: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in label.strip())
    collapsed = "-".join(part for part in normalized.split("-") if part)
    return collapsed or "backend-runtime-diagnostic"


def normalize_docker_since(value: str) -> str:
    match = DAY_WINDOW_RE.fullmatch(value)
    normalized = value
    if match:
        hours = int(match.group("days")) * 24
        suffix = match.group("suffix")
        hours_match = re.match(r"^(?P<hours>[0-9]+)h(?P<rest>.*)$", suffix)
        if hours_match:
            hours += int(hours_match.group("hours"))
            suffix = hours_match.group("rest")
        normalized = f"{hours}h{suffix}"

    if not DOCKER_DURATION_RE.fullmatch(normalized):
        raise ValueError(f"invalid --since duration: {value}")
    return normalized


def compile_log_pattern(grep: str | None) -> re.Pattern[str] | None:
    if not grep:
        return None
    try:
        return re.compile(grep, re.IGNORECASE)
    except re.error as exc:
        raise ValueError(f"invalid --grep regular expression: {exc}") from exc


def filter_logs(content: str, grep: str | None) -> str:
    pattern = compile_log_pattern(grep)
    if pattern is None:
        return ""
    return "\n".join(line for line in content.splitlines() if pattern.search(line))


def sanitize_environment_output(content: str) -> str:
    sanitized_lines: list[str] = []
    for line in content.splitlines():
        match = ENVIRONMENT_ENTRY_RE.fullmatch(line)
        if not match:
            sanitized_lines.append("[REDACTED]")
            continue
        key, value = match.groups()
        sanitized_lines.append(f"{key}={redact_environment_value(key, value)}")
    return "\n".join(sanitized_lines)


def safe_scalar(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def is_safe_environment_value(key: str, value: str) -> bool:
    scalar = safe_scalar(value)
    if key == "SPRING_PROFILES_ACTIVE":
        return scalar in SAFE_SPRING_PROFILE_VALUES
    if key == "NACOS_ENABLED":
        return scalar in {"true", "false"}
    if key == "SERVER_PORT":
        return re.fullmatch(r"[1-9][0-9]{0,4}", scalar) is not None and int(scalar) <= 65535
    return False


def redact_environment_value(key: str, value: str) -> str:
    if key in SAFE_ENV_VALUE_KEYS and is_safe_environment_value(key, value):
        return value
    return "[REDACTED]"


def is_safe_logging_value(key: str, value: str) -> bool:
    if key == "max-size":
        return re.fullmatch(r"[0-9]+[kKmMgG]?", value) is not None
    if key == "max-file":
        return value.isdecimal()
    if key == "compress":
        return value in {"true", "false"}
    if key == "mode":
        return value in {"blocking", "non-blocking"}
    return False


def sanitize_docker_logging_output(content: str) -> str:
    sanitized_lines: list[str] = []
    for line in content.splitlines():
        match = LOGGING_ENTRY_RE.fullmatch(line)
        if not match:
            sanitized_lines.append("[REDACTED]")
            continue
        key, value = match.groups()
        if key == "driver" and value in SAFE_DOCKER_LOGGING_DRIVERS:
            sanitized_lines.append(line)
        elif key in SAFE_DOCKER_LOGGING_VALUE_KEYS and is_safe_logging_value(key, value):
            sanitized_lines.append(line)
        else:
            sanitized_lines.append(f"{key}=[REDACTED]")
    return "\n".join(sanitized_lines)


def sanitize_compose_output(content: str) -> str:
    sanitized_lines: list[str] = []
    for line in content.splitlines():
        if SAFE_COMPOSE_STRUCTURE_RE.fullmatch(line):
            sanitized_lines.append(line)
            continue
        match = COMPOSE_ENV_ENTRY_RE.fullmatch(line)
        if match:
            key = match.group("key")
            if key in SAFE_ENV_VALUE_KEYS and is_safe_environment_value(key, match.group("value")):
                sanitized_lines.append(line)
            else:
                sanitized_lines.append(
                    f'{match.group("prefix")}{match.group("opening_quote")}{key}'
                    f'{match.group("closing_quote")}{match.group("separator")}[REDACTED]'
                )
        else:
            sanitized_lines.append("[REDACTED]")
    return "\n".join(sanitized_lines)


def extract_section(output: str, field: str) -> str | None:
    begin = f"__{field}_BEGIN__"
    end = f"__{field}_END__"
    start = output.find(begin)
    stop = output.find(end)
    if start == -1 or stop == -1 or stop < start:
        return None
    content_start = start + len(begin)
    return output[content_start:stop].strip("\r\n")


def parse_helper_output(output: str) -> dict[str, str]:
    capture_fields = [
        "REMOTE_DATE",
        "DOCKER_PS",
        "DOCKER_INSPECT_STATE",
        "DOCKER_INSPECT_ENV",
        "DOCKER_INSPECT_LOGGING",
        "DOCKER_LOGS_TAIL",
        "COMPOSE_BACKEND_SOURCE",
        "COMPOSE_RENDERED_BACKEND",
        "FINAL_STATUS",
        "FAIL_REASON",
    ]
    summary: dict[str, str] = {}
    missing_fields: list[str] = []
    for field in capture_fields:
        section = extract_section(output, field)
        if section is None:
            missing_fields.append(field)
            summary[field] = NOT_CAPTURED
        else:
            summary[field] = section

    if summary["FINAL_STATUS"] == NOT_CAPTURED:
        summary["FINAL_STATUS"] = "failed"
        summary["FAIL_REASON"] = "remote helper exited before reporting final status"
    elif summary["FAIL_REASON"] == NOT_CAPTURED:
        summary["FAIL_REASON"] = ""
    summary["MISSING_FIELDS"] = ",".join(missing_fields)
    return summary


def collect(context: DiagnosticContext) -> None:
    compile_log_pattern(context.grep)
    ensure_dir(context.output_dir)
    docker_since = normalize_docker_since(context.since)
    helper_command = (
        f"sudo -n {REMOTE_HELPER_PATH} "
        f"--runtime-diagnostics "
        f"--container {shlex.quote(context.container)} "
        f"--since {shlex.quote(docker_since)} "
        f"--tail {context.tail}"
    )
    try:
        result = run_ssh(context, helper_command)
        helper_stdout = result.stdout
        if result.stderr and result.stderr.strip():
            log("remote helper returned stderr; details omitted")
    except subprocess.CalledProcessError as exc:
        helper_stdout = exc.stdout or ""
        if exc.stderr and exc.stderr.strip():
            log("remote helper returned stderr; details omitted")
        if not helper_stdout.strip():
            raise

    summary = parse_helper_output(helper_stdout)

    remote_date = summary["REMOTE_DATE"]
    docker_ps = summary["DOCKER_PS"]
    inspect_state = summary["DOCKER_INSPECT_STATE"]
    inspect_env = (
        NOT_CAPTURED
        if summary["DOCKER_INSPECT_ENV"] == NOT_CAPTURED
        else sanitize_environment_output(summary["DOCKER_INSPECT_ENV"])
    )
    inspect_logging = (
        NOT_CAPTURED
        if summary["DOCKER_INSPECT_LOGGING"] == NOT_CAPTURED
        else sanitize_docker_logging_output(summary["DOCKER_INSPECT_LOGGING"])
    )
    docker_logs = summary["DOCKER_LOGS_TAIL"]
    compose_backend_source = (
        NOT_CAPTURED
        if summary["COMPOSE_BACKEND_SOURCE"] == NOT_CAPTURED
        else sanitize_compose_output(summary["COMPOSE_BACKEND_SOURCE"])
    )
    compose_rendered_backend = (
        NOT_CAPTURED
        if summary["COMPOSE_RENDERED_BACKEND"] == NOT_CAPTURED
        else sanitize_compose_output(summary["COMPOSE_RENDERED_BACKEND"])
    )
    filtered_logs = filter_logs(docker_logs, context.grep)

    metadata = {
        "captureId": context.capture_id,
        "capturedAt": datetime.now().astimezone().isoformat(),
        "remoteDate": remote_date,
        "host": context.host,
        "user": context.user,
        "container": context.container,
        "since": docker_since,
        "tail": context.tail,
        "grep": context.grep,
        "helperStatus": summary["FINAL_STATUS"],
        "failureReason": summary["FAIL_REASON"],
        "captureComplete": not bool(summary["MISSING_FIELDS"]),
        "missingSections": summary["MISSING_FIELDS"].split(",") if summary["MISSING_FIELDS"] else [],
        "files": {
            "dockerPs": "docker-ps.txt",
            "inspectState": "docker-inspect-state.txt",
            "inspectEnv": "docker-inspect-env.txt",
            "inspectLogging": "docker-inspect-logging.txt",
            "dockerLogs": "docker-logs.txt",
            "composeBackendSource": "compose-backend-source.txt",
            "composeRenderedBackend": "compose-rendered-backend.txt",
            "filteredLogs": "docker-logs.filtered.txt" if context.grep else None,
        },
    }

    write_text(context.output_dir / "docker-ps.txt", docker_ps)
    write_text(context.output_dir / "docker-inspect-state.txt", inspect_state)
    write_text(context.output_dir / "docker-inspect-env.txt", inspect_env)
    write_text(context.output_dir / "docker-inspect-logging.txt", inspect_logging)
    write_text(context.output_dir / "docker-logs.txt", docker_logs)
    write_text(context.output_dir / "compose-backend-source.txt", compose_backend_source)
    write_text(context.output_dir / "compose-rendered-backend.txt", compose_rendered_backend)
    if context.grep:
        write_text(context.output_dir / "docker-logs.filtered.txt", filtered_logs)
    write_text(context.output_dir / "summary.json", json.dumps(metadata, ensure_ascii=False, indent=2))

    log(f"diagnostic capture saved: {context.output_dir}")
    if summary["FINAL_STATUS"] != "passed":
        raise RuntimeError(f"runtime diagnostic helper failed: {summary['FAIL_REASON']}")
    if summary["MISSING_FIELDS"]:
        raise RuntimeError(f"runtime diagnostic helper output incomplete: {summary['MISSING_FIELDS']}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read backend runtime status and logs from the standard remote environment.",
    )
    parser.add_argument("--label", default="backend-runtime-diagnostic")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--identity-file", default=str(DEFAULT_IDENTITY_FILE))
    parser.add_argument("--container", default=DEFAULT_CONTAINER)
    parser.add_argument("--since", default=DEFAULT_SINCE)
    parser.add_argument("--tail", type=int, default=DEFAULT_TAIL)
    parser.add_argument("--grep")
    args = parser.parse_args()

    try:
        compile_log_pattern(args.grep)
        normalized_since = normalize_docker_since(args.since)
    except ValueError as exc:
        parser.error(str(exc))

    capture_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{sanitize_label(args.label)}"
    output_dir = DIAGNOSTICS_DIR / capture_id
    context = DiagnosticContext(
        capture_id=capture_id,
        host=args.host,
        user=args.user,
        identity_file=Path(args.identity_file),
        container=args.container,
        since=normalized_since,
        tail=args.tail,
        grep=args.grep,
        output_dir=output_dir,
    )

    require_key_auth(context)
    require_helper(context)
    collect(context)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
