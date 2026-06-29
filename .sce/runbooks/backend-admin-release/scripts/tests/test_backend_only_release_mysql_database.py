import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "run-backend-only-release.py"


def load_module():
    spec = importlib.util.spec_from_file_location("run_backend_only_release", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BackendOnlyReleaseMysqlDatabaseTests(unittest.TestCase):
    def test_remote_mysql_validation_uses_context_database(self):
        module = load_module()
        context = SimpleNamespace(
            user="kaipaile",
            host="101.43.57.62",
            release_id="20260629-170000-backend-only-prod-single-env-cutover",
            mysql_database="kaipai_prod",
        )
        remote_commands = []
        scp_commands = []

        def fake_run_ssh(_context, remote_command):
            remote_commands.append(remote_command)
            return SimpleNamespace(
                stdout=(
                    "__REMOTE_DATE_BEGIN__\n2026-06-29 17:00:00 +0800\n__REMOTE_DATE_END__\n"
                    "__MYSQL_MODE_BEGIN__\nvalidation\n__MYSQL_MODE_END__\n"
                    "__MYSQL_DATABASE_BEGIN__\nkaipai_prod\n__MYSQL_DATABASE_END__\n"
                    "__MYSQL_CONTAINER_BEGIN__\nkaipai-mysql\n__MYSQL_CONTAINER_END__\n"
                    "__MYSQL_RESULT_BEGIN__\nHISTORY_TABLE_EXISTS=1\n__MYSQL_RESULT_END__\n"
                    "__FINAL_STATUS_BEGIN__\npassed\n__FINAL_STATUS_END__\n"
                    "__FAIL_REASON_BEGIN__\n\n__FAIL_REASON_END__\n"
                ),
                stderr="",
            )

        def fake_run_process(command, **kwargs):
            scp_commands.append(command)
            return subprocess.CompletedProcess(command, 0, "", "")

        with patch.object(module, "run_ssh", side_effect=fake_run_ssh), patch.object(
            module, "run_process", side_effect=fake_run_process
        ), patch.object(module, "scp_base", return_value=["scp"]):
            summary = module.run_remote_mysql_validation(
                context,
                "SELECT 1;\n",
                "schema-history-exists",
            )

        self.assertEqual(summary["MYSQL_DATABASE"], "kaipai_prod")
        self.assertTrue(any("mkdir -p /home/kaipaile/backend-schema-checks/" in item for item in remote_commands))
        helper_calls = [item for item in remote_commands if "--mysql-validation" in item]
        self.assertEqual(len(helper_calls), 1)
        self.assertIn("--mysql-database kaipai_prod", helper_calls[0])
        self.assertEqual(len(scp_commands), 1)
        self.assertEqual(scp_commands[0][0], "scp")

    def test_parse_args_accepts_mysql_database_override(self):
        module = load_module()
        with patch(
            "sys.argv",
            [
                "run-backend-only-release.py",
                "--label",
                "prod-single-env-cutover",
                "--mysql-database",
                "kaipai_prod",
            ],
        ):
            args = module.parse_args()

        self.assertEqual(args.mysql_database, "kaipai_prod")

    def test_write_record_includes_mysql_database(self):
        module = load_module()
        context = SimpleNamespace(
            release_id="20260629-170000-backend-only-prod-single-env-cutover",
            release_time="20260629-170000",
            host="101.43.57.62",
            user="kaipaile",
            operator="codex",
            label="prod-single-env-cutover",
            public_base_url="https://api.kplyyk.com",
            mysql_database="kaipai_prod",
            identity_file=Path("/tmp/id"),
            java_home=Path("/tmp/jdk17"),
            remote_upload_path="/home/kaipaile/backend-release-uploads/demo.jar",
            local_jar_path=Path("/tmp/kaipai-backend-1.0.0-SNAPSHOT.jar"),
            build_root=Path("/tmp/server"),
            source_mode="working_tree",
            snapshot_root=None,
            overlay_paths=[],
            dirty_paths=[],
            local_jar_sha="ABC123",
        )
        remote = {
            "REMOTE_DATE": "2026-06-29 17:00:00 +0800",
            "BACKUP_PATH": "/opt/kaipai/backups/releases/demo/backend",
            "RELEASE_ROOT": "/opt/kaipai/builds/demo",
            "REMOTE_RELEASE_JAR": "/opt/kaipai/builds/demo/kaipai-backend-1.0.0-SNAPSHOT.jar",
            "RUNTIME_JAR": "/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar",
            "UPLOADED_JAR_SHA": "ABC123",
            "RUNTIME_JAR_SHA": "ABC123",
            "CONTAINER_JAR_SHA": "ABC123",
            "DOCKER_COMPOSE_VERSION": "docker compose version v2",
            "DOCKER_COMPOSE_PS": "compose ps",
            "DOCKER_PS": "docker ps",
            "DOCKER_INSPECT_ENV": "SPRING_PROFILES_ACTIVE=prod",
            "DOCKER_LOGS_TAIL": "logs",
            "COMPOSE_BACKEND_SOURCE": "source",
            "COMPOSE_RENDERED_BACKEND": "rendered",
            "NGINX_API_PROXY": "proxy",
            "INTERNAL_DOCS": "status=200\n{}",
            "INTERNAL_ADMIN_LOGIN": "status=200\n{}",
            "INTERNAL_RECRUIT_ROLES": "status=200\n{}",
            "INTERNAL_ROLE_SEARCH": "status=200\n{}",
            "FINAL_STATUS": "passed",
            "FAIL_REASON": "",
        }
        public = {
            "docs_status": 200,
            "docs_last_modified": "",
            "docs_body": "{}",
            "login_status": 200,
            "login_body": "{}",
            "recruit_status": 200,
            "recruit_body": "{}",
            "role_status": 200,
            "role_body": "{}",
        }

        record_path = module.write_record(context, remote, public)
        try:
            text = record_path.read_text(encoding="utf-8")
            self.assertIn("目标数据库：`kaipai_prod`", text)
            self.assertIn("远端 schema history 预检目标库：`kaipai_prod`", text)
        finally:
            record_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
