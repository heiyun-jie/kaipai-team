import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "read-backend-runtime-logs.py"
HELPER_PATH = Path(__file__).resolve().parents[1] / "kaipai-backend-release-helper.sh"
COMPOSE_SYNC_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "run-backend-compose-env-sync.py"


def load_module():
    spec = importlib.util.spec_from_file_location("read_backend_runtime_logs", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_compose_sync_module():
    spec = importlib.util.spec_from_file_location("run_backend_compose_env_sync", COMPOSE_SYNC_SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    script_dir = str(COMPOSE_SYNC_SCRIPT_PATH.parent)
    sys.path.insert(0, script_dir)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(script_dir)
    return module


def resolve_bash() -> str | None:
    program_files = os.environ.get("ProgramFiles")
    if program_files:
        git_bash = Path(program_files) / "Git" / "bin" / "bash.exe"
        if git_bash.is_file():
            return str(git_bash)
    return shutil.which("bash")


def helper_output(*, final_status: str = "passed") -> str:
    return "\n".join(
        [
            "__REMOTE_DATE_BEGIN__",
            "2026-07-27 20:00:00 +0800",
            "__REMOTE_DATE_END__",
            "__DOCKER_PS_BEGIN__",
            "NAMES",
            "kaipai-backend",
            "__DOCKER_PS_END__",
            "__DOCKER_INSPECT_STATE_BEGIN__",
            "status=running",
            "__DOCKER_INSPECT_STATE_END__",
            "__DOCKER_INSPECT_ENV_BEGIN__",
            "SPRING_PROFILES_ACTIVE=prod",
            "NACOS_ENABLED=true",
            "DATABASE_PASSWORD=super-secret-password",
            "UNEXPECTED_VALUE=must-not-be-written",
            "__DOCKER_INSPECT_ENV_END__",
            "__DOCKER_INSPECT_LOGGING_BEGIN__",
            "driver=json-file",
            "max-size=20m",
            "tag=must-not-be-written",
            "__DOCKER_INSPECT_LOGGING_END__",
            "__DOCKER_LOGS_TAIL_BEGIN__",
            "2026-07-27 WARN verification status unavailable",
            "__DOCKER_LOGS_TAIL_END__",
            "__COMPOSE_BACKEND_SOURCE_BEGIN__",
            "10:services:",
            "20:      SPRING_PROFILES_ACTIVE=prod",
            "21:      WECHAT_MINIAPP_APP_SECRET=compose-source-secret",
            "__COMPOSE_BACKEND_SOURCE_END__",
            "__COMPOSE_RENDERED_BACKEND_BEGIN__",
            "10:services:",
            "20:      NACOS_ENABLED=true",
            "21:      UNKNOWN_RUNTIME_SECRET=rendered-compose-secret",
            "__COMPOSE_RENDERED_BACKEND_END__",
            "__FINAL_STATUS_BEGIN__",
            final_status,
            "__FINAL_STATUS_END__",
            "__FAIL_REASON_BEGIN__",
            "docker logs failed for kaipai-backend" if final_status == "failed" else "",
            "__FAIL_REASON_END__",
        ]
    )


class BackendRuntimeDiagnosticsTests(unittest.TestCase):
    def test_normalize_docker_since_converts_day_windows_to_hours(self):
        module = load_module()

        self.assertEqual(module.normalize_docker_since("30d"), "720h")
        self.assertEqual(module.normalize_docker_since("1d12h"), "36h")
        self.assertEqual(module.normalize_docker_since("15m"), "15m")
        with self.assertRaisesRegex(ValueError, r"invalid --since duration"):
            module.normalize_docker_since("30days")

    def test_filter_logs_uses_case_insensitive_regular_expressions(self):
        module = load_module()
        logs = "INFO healthy\nWARN Verify status failed\nERROR another failure\n"

        self.assertEqual(
            module.filter_logs(logs, r"warn|error"),
            "WARN Verify status failed\nERROR another failure",
        )

    def test_filter_logs_rejects_invalid_regular_expression_clearly(self):
        module = load_module()

        with self.assertRaisesRegex(ValueError, r"invalid --grep regular expression"):
            module.filter_logs("INFO healthy", r"[unterminated")

    def test_invalid_cli_grep_exits_before_any_remote_probe(self):
        module = load_module()
        stderr = io.StringIO()

        with patch("sys.argv", [str(SCRIPT_PATH), "--grep", "[unterminated"]), patch.object(
            module, "require_key_auth"
        ) as require_key_auth, contextlib.redirect_stderr(stderr):
            with self.assertRaisesRegex(SystemExit, "2"):
                module.main()

        require_key_auth.assert_not_called()
        self.assertIn("invalid --grep regular expression", stderr.getvalue())

    def test_invalid_cli_since_exits_before_any_remote_probe(self):
        module = load_module()
        stderr = io.StringIO()

        with patch("sys.argv", [str(SCRIPT_PATH), "--since", "30days"]), patch.object(
            module, "require_key_auth"
        ) as require_key_auth, contextlib.redirect_stderr(stderr):
            with self.assertRaisesRegex(SystemExit, "2"):
                module.main()

        require_key_auth.assert_not_called()
        self.assertIn("invalid --since duration", stderr.getvalue())

    def test_local_environment_sanitizer_uses_allowlist_and_redacts_everything_else(self):
        module = load_module()
        raw_environment = "\n".join(
            [
                "SPRING_PROFILES_ACTIVE=prod",
                "NACOS_ENABLED=true",
                "SERVER_PORT=8080",
                "SPRING_PROFILES_ACTIVE=prod should-not-leak",
                "NACOS_ENABLED=true should-not-leak",
                "SERVER_PORT=8080 should-not-leak",
                "DATABASE_PASSWORD=super-secret-password",
                "UNEXPECTED_VALUE=must-not-be-written",
                "not-an-environment-entry secret-value",
            ]
        )

        sanitized = module.sanitize_environment_output(raw_environment)

        self.assertIn("SPRING_PROFILES_ACTIVE=prod", sanitized)
        self.assertIn("NACOS_ENABLED=true", sanitized)
        self.assertIn("SERVER_PORT=8080", sanitized)
        self.assertIn("SPRING_PROFILES_ACTIVE=[REDACTED]", sanitized)
        self.assertIn("NACOS_ENABLED=[REDACTED]", sanitized)
        self.assertIn("SERVER_PORT=[REDACTED]", sanitized)
        self.assertIn("DATABASE_PASSWORD=[REDACTED]", sanitized)
        self.assertIn("UNEXPECTED_VALUE=[REDACTED]", sanitized)
        self.assertIn("[REDACTED]", sanitized)
        self.assertNotIn("super-secret-password", sanitized)
        self.assertNotIn("must-not-be-written", sanitized)
        self.assertNotIn("not-an-environment-entry", sanitized)
        self.assertNotIn("should-not-leak", sanitized)

    def test_local_compose_sanitizer_preserves_structure_and_safe_runtime_values_only(self):
        module = load_module()
        raw_compose = "\n".join(
            [
                "10:services:",
                "12:  kaipai:",
                "15:    image: kaipai-backend:latest",
                "20:      SPRING_PROFILES_ACTIVE=prod",
                "21:      SERVER_PORT: 8080",
                "22:      WECHAT_MINIAPP_APP_SECRET=super-secret-password",
                "23:      UNKNOWN_RUNTIME_SECRET: must-not-be-written",
                '24:      "KAIPAI_SMS_FUTURE_SECRET": quoted-secret',
                "25:      custom_secret: lower-secret SERVER_PORT=8080",
                '26:      - "KAIPAI_SMS_FUTURE_SECRET=list-secret"',
                "27:      image: should-not-leak",
                "28:      container_name: should-not-leak",
                "29:      env_file: should-not-leak",
                "30:      ports: should-not-leak",
                "31:      SPRING_PROFILES_ACTIVE=prod should-not-leak",
                "32:      NACOS_ENABLED=true should-not-leak",
                "33:      SERVER_PORT=8080 should-not-leak",
                '34:      SPRING_PROFILES_ACTIVE: "dev"',
                '35:      NACOS_ENABLED: "true"',
                '36:      SERVER_PORT: "18080"',
                "unstructured secret-value",
            ]
        )

        sanitized = module.sanitize_compose_output(raw_compose)

        self.assertIn("10:services:", sanitized)
        self.assertIn("15:    image: [REDACTED]", sanitized)
        self.assertIn("20:      SPRING_PROFILES_ACTIVE=prod", sanitized)
        self.assertIn("21:      SERVER_PORT: 8080", sanitized)
        self.assertIn("22:      WECHAT_MINIAPP_APP_SECRET=[REDACTED]", sanitized)
        self.assertIn("23:      UNKNOWN_RUNTIME_SECRET: [REDACTED]", sanitized)
        self.assertIn('24:      "KAIPAI_SMS_FUTURE_SECRET": [REDACTED]', sanitized)
        self.assertIn("25:      custom_secret: [REDACTED]", sanitized)
        self.assertIn('26:      - "KAIPAI_SMS_FUTURE_SECRET=[REDACTED]', sanitized)
        self.assertIn("27:      image: [REDACTED]", sanitized)
        self.assertIn("28:      container_name: [REDACTED]", sanitized)
        self.assertIn("29:      env_file: [REDACTED]", sanitized)
        self.assertIn("30:      ports: [REDACTED]", sanitized)
        self.assertIn("31:      SPRING_PROFILES_ACTIVE=[REDACTED]", sanitized)
        self.assertIn("32:      NACOS_ENABLED=[REDACTED]", sanitized)
        self.assertIn("33:      SERVER_PORT=[REDACTED]", sanitized)
        self.assertIn('34:      SPRING_PROFILES_ACTIVE: "dev"', sanitized)
        self.assertIn('35:      NACOS_ENABLED: "true"', sanitized)
        self.assertIn('36:      SERVER_PORT: "18080"', sanitized)
        self.assertNotIn("super-secret-password", sanitized)
        self.assertNotIn("must-not-be-written", sanitized)
        self.assertNotIn("quoted-secret", sanitized)
        self.assertNotIn("lower-secret", sanitized)
        self.assertNotIn("list-secret", sanitized)
        self.assertNotIn("unstructured", sanitized)
        self.assertNotIn("should-not-leak", sanitized)

    def test_compose_sync_records_reapply_the_same_allowlist(self):
        module = load_compose_sync_module()
        remote = {
            "DOCKER_INSPECT_ENV": "SPRING_PROFILES_ACTIVE=prod\nDATABASE_PASSWORD=runtime-secret",
            "COMPOSE_BACKEND_SOURCE": (
                "10:services:\n20:      SERVER_PORT=8080\n"
                '21:      FUTURE_PROVIDER_SECRET=source-secret\n'
                '22:      "KAIPAI_SMS_FUTURE_SECRET": quoted-source-secret\n'
                "27:      image: should-not-leak\n"
                "28:      container_name: should-not-leak\n"
                "29:      env_file: should-not-leak\n"
                "30:      ports: should-not-leak\n"
                "31:      SPRING_PROFILES_ACTIVE=prod should-not-leak"
            ),
            "COMPOSE_RENDERED_BACKEND": (
                "10:services:\n20:      NACOS_ENABLED=true\n"
                "21:      UNKNOWN_RUNTIME_VALUE=rendered-secret\n"
                "22:      custom_secret: lower-source-secret SERVER_PORT=8080\n"
                "32:      NACOS_ENABLED=true should-not-leak\n"
                "33:      SERVER_PORT=8080 should-not-leak"
            ),
            "CANDIDATE_VALIDATE_OUTPUT": "full rendered config with candidate-secret",
        }

        sanitized = module.sanitize_remote_record_values(remote)

        self.assertEqual(module.redact_value("SPRING_PROFILES_ACTIVE", "prod"), "prod")
        self.assertEqual(module.redact_value("UNEXPECTED_VALUE", "must-not-be-written"), "[REDACTED]")
        self.assertIn("SPRING_PROFILES_ACTIVE=prod", sanitized["DOCKER_INSPECT_ENV"])
        self.assertIn("DATABASE_PASSWORD=[REDACTED]", sanitized["DOCKER_INSPECT_ENV"])
        self.assertIn("SERVER_PORT=8080", sanitized["COMPOSE_BACKEND_SOURCE"])
        self.assertIn("FUTURE_PROVIDER_SECRET=[REDACTED]", sanitized["COMPOSE_BACKEND_SOURCE"])
        self.assertIn('"KAIPAI_SMS_FUTURE_SECRET": [REDACTED]', sanitized["COMPOSE_BACKEND_SOURCE"])
        self.assertIn("image: [REDACTED]", sanitized["COMPOSE_BACKEND_SOURCE"])
        self.assertIn("container_name: [REDACTED]", sanitized["COMPOSE_BACKEND_SOURCE"])
        self.assertIn("env_file: [REDACTED]", sanitized["COMPOSE_BACKEND_SOURCE"])
        self.assertIn("ports: [REDACTED]", sanitized["COMPOSE_BACKEND_SOURCE"])
        self.assertIn("SPRING_PROFILES_ACTIVE=[REDACTED]", sanitized["COMPOSE_BACKEND_SOURCE"])
        self.assertIn("NACOS_ENABLED=true", sanitized["COMPOSE_RENDERED_BACKEND"])
        self.assertIn("UNKNOWN_RUNTIME_VALUE=[REDACTED]", sanitized["COMPOSE_RENDERED_BACKEND"])
        self.assertIn("custom_secret: [REDACTED]", sanitized["COMPOSE_RENDERED_BACKEND"])
        self.assertIn("NACOS_ENABLED=[REDACTED]", sanitized["COMPOSE_RENDERED_BACKEND"])
        self.assertIn("SERVER_PORT=[REDACTED]", sanitized["COMPOSE_RENDERED_BACKEND"])
        self.assertEqual(sanitized["CANDIDATE_VALIDATE_OUTPUT"], "[REDACTED]")
        self.assertNotIn("runtime-secret", "\n".join(sanitized.values()))
        self.assertNotIn("source-secret", "\n".join(sanitized.values()))
        self.assertNotIn("rendered-secret", "\n".join(sanitized.values()))
        self.assertNotIn("candidate-secret", "\n".join(sanitized.values()))
        self.assertNotIn("quoted-source-secret", "\n".join(sanitized.values()))
        self.assertNotIn("lower-source-secret", "\n".join(sanitized.values()))
        self.assertNotIn("should-not-leak", "\n".join(sanitized.values()))

    def test_failed_helper_preserves_sanitized_partial_evidence(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory) / "capture"
            context = module.DiagnosticContext(
                capture_id="20260727-failed-helper",
                host="127.0.0.1",
                user="kaipaile",
                identity_file=Path("/tmp/id"),
                container="kaipai-backend",
                since="30d",
                tail=100,
                grep=r"warn|error",
                output_dir=output_dir,
            )
            commands = []

            def failing_run_ssh(_context, command):
                commands.append(command)
                raise subprocess.CalledProcessError(
                    1,
                    command,
                    output=helper_output(final_status="failed"),
                    stderr="helper exited after collecting partial evidence",
                )

            with patch.object(module, "run_ssh", side_effect=failing_run_ssh):
                with self.assertRaisesRegex(RuntimeError, r"runtime diagnostic helper failed"):
                    module.collect(context)

            self.assertEqual(len(commands), 1)
            self.assertIn("--since 720h", commands[0])
            inspect_environment = (output_dir / "docker-inspect-env.txt").read_text(encoding="utf-8")
            logging_config = (output_dir / "docker-inspect-logging.txt").read_text(encoding="utf-8")
            compose_backend_source = (output_dir / "compose-backend-source.txt").read_text(encoding="utf-8")
            compose_rendered_backend = (output_dir / "compose-rendered-backend.txt").read_text(encoding="utf-8")
            summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
            filtered_logs = (output_dir / "docker-logs.filtered.txt").read_text(encoding="utf-8")

            self.assertIn("SPRING_PROFILES_ACTIVE=prod", inspect_environment)
            self.assertIn("DATABASE_PASSWORD=[REDACTED]", inspect_environment)
            self.assertNotIn("super-secret-password", inspect_environment)
            self.assertIn("driver=json-file", logging_config)
            self.assertIn("tag=[REDACTED]", logging_config)
            self.assertNotIn("must-not-be-written", logging_config)
            self.assertEqual(summary["helperStatus"], "failed")
            self.assertEqual(summary["since"], "720h")
            self.assertEqual(filtered_logs.strip(), "2026-07-27 WARN verification status unavailable")
            self.assertIn("SPRING_PROFILES_ACTIVE=prod", compose_backend_source)
            self.assertIn("WECHAT_MINIAPP_APP_SECRET=[REDACTED]", compose_backend_source)
            self.assertIn("NACOS_ENABLED=true", compose_rendered_backend)
            self.assertIn("UNKNOWN_RUNTIME_SECRET=[REDACTED]", compose_rendered_backend)
            self.assertNotIn("compose-source-secret", compose_backend_source)
            self.assertNotIn("rendered-compose-secret", compose_rendered_backend)

    def test_remote_helper_redacts_environment_sections_and_emits_logging_summary(self):
        helper = HELPER_PATH.read_text(encoding="utf-8")

        self.assertIn("SAFE_ENV_VALUE_KEYS", helper)
        self.assertIn("redact_environment_output()", helper)
        self.assertIn("redact_compose_environment_output()", helper)
        self.assertIn('emit_section "DOCKER_INSPECT_LOGGING"', helper)
        self.assertEqual(helper.count("docker_inspect_env_raw="), 3)
        self.assertEqual(helper.count('docker_inspect_env="$(printf'), 3)
        self.assertNotIn('emit_section "DOCKER_INSPECT_ENV" "$docker_inspect_env_raw"', helper)
        self.assertIn('candidate_validate_output="docker compose config validation passed"', helper)
        self.assertNotIn('emit_section "CANDIDATE_VALIDATE_OUTPUT" "$candidate_validate_output_raw"', helper)

        bash = resolve_bash()
        if not bash:
            self.skipTest("bash is not available for helper sanitizer verification")

        sanitizer_start = helper.index("# Only these runtime values")
        sanitizer_end = helper.index("\nresolve_mysql_root_password()")
        sanitizer_probe = "set -euo pipefail\n" + helper[sanitizer_start:sanitizer_end] + r"""
printf '%s\n' 'SPRING_PROFILES_ACTIVE=prod' 'NACOS_ENABLED=true' 'SERVER_PORT=8080' 'SPRING_PROFILES_ACTIVE=prod should-not-leak' 'NACOS_ENABLED=true should-not-leak' 'SERVER_PORT=8080 should-not-leak' 'DATABASE_PASSWORD=super-secret-password' 'UNEXPECTED_VALUE=must-not-be-written' 'unstructured secret-value' | redact_environment_output
printf '%s\n' 'driver=json-file' 'max-size=20m' 'tag=must-not-be-written' | redact_docker_logging_output
printf '%s\n' '10:services:' '20:      SPRING_PROFILES_ACTIVE=prod' '21:      WECHAT_MINIAPP_APP_SECRET=compose-source-secret' '22:      UNKNOWN_RUNTIME_SECRET=rendered-compose-secret SERVER_PORT=9999' '23:      "KAIPAI_SMS_FUTURE_SECRET": quoted-secret' '24:      custom_secret: lower-secret SERVER_PORT=8080' '25:      - "KAIPAI_SMS_FUTURE_SECRET=list-secret"' '27:      image: should-not-leak' '28:      container_name: should-not-leak' '29:      env_file: should-not-leak' '30:      ports: should-not-leak' '31:      SPRING_PROFILES_ACTIVE=prod should-not-leak' '32:      NACOS_ENABLED=true should-not-leak' '33:      SERVER_PORT=8080 should-not-leak' '34:      SPRING_PROFILES_ACTIVE: "dev"' '35:      NACOS_ENABLED: "true"' '36:      SERVER_PORT: "18080"' | redact_compose_environment_output
"""
        result = subprocess.run(
            [bash, "-c", sanitizer_probe],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SPRING_PROFILES_ACTIVE=prod", result.stdout)
        self.assertIn("DATABASE_PASSWORD=[REDACTED]", result.stdout)
        self.assertIn("UNEXPECTED_VALUE=[REDACTED]", result.stdout)
        self.assertIn("SPRING_PROFILES_ACTIVE=[REDACTED]", result.stdout)
        self.assertIn("NACOS_ENABLED=[REDACTED]", result.stdout)
        self.assertIn("SERVER_PORT=[REDACTED]", result.stdout)
        self.assertIn("driver=json-file", result.stdout)
        self.assertIn("max-size=20m", result.stdout)
        self.assertIn("tag=[REDACTED]", result.stdout)
        self.assertIn("WECHAT_MINIAPP_APP_SECRET=[REDACTED]", result.stdout)
        self.assertIn("UNKNOWN_RUNTIME_SECRET=[REDACTED]", result.stdout)
        self.assertIn("image: [REDACTED]", result.stdout)
        self.assertIn("container_name: [REDACTED]", result.stdout)
        self.assertIn("env_file: [REDACTED]", result.stdout)
        self.assertIn("ports: [REDACTED]", result.stdout)
        self.assertIn('SPRING_PROFILES_ACTIVE: "dev"', result.stdout)
        self.assertIn('NACOS_ENABLED: "true"', result.stdout)
        self.assertIn('SERVER_PORT: "18080"', result.stdout)
        self.assertNotIn("super-secret-password", result.stdout)
        self.assertNotIn("must-not-be-written", result.stdout)
        self.assertNotIn("unstructured", result.stdout)
        self.assertNotIn("compose-source-secret", result.stdout)
        self.assertNotIn("rendered-compose-secret", result.stdout)
        self.assertNotIn("quoted-secret", result.stdout)
        self.assertNotIn("lower-secret", result.stdout)
        self.assertNotIn("list-secret", result.stdout)
        self.assertNotIn("should-not-leak", result.stdout)


if __name__ == "__main__":
    unittest.main()
