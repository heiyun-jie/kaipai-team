import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[5]
RUNNER_PATH = REPO_ROOT / ".sce" / "runbooks" / "backend-admin-release" / "scripts" / "run-backend-schema-migration.py"
SPEC = importlib.util.spec_from_file_location("schema_migration_runner", RUNNER_PATH)
RUNNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RUNNER
SPEC.loader.exec_module(RUNNER)


class SchemaMigrationSafetyGateTest(unittest.TestCase):
    def setUp(self):
        self.manifest_path = (
            REPO_ROOT
            / ".sce"
            / "runbooks"
            / "backend-admin-release"
            / "records"
            / "20260826-1625-v3-draft"
            / "00-231"
            / "candidate-manifest.json"
        )
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.migrations = [
            RUNNER.resolve_migration_file(item["fileName"])
            for item in self.manifest["migrations"]
        ]

    def test_frozen_manifest_matches_all_fourteen_migrations(self):
        result = RUNNER.validate_candidate_manifest(
            self.manifest_path,
            "20260826-1625-v3-draft",
            self.migrations,
        )

        self.assertEqual(len(result["migrations"]), 14)

    def test_manifest_checksum_drift_fails_before_remote_execution(self):
        changed = json.loads(json.dumps(self.manifest))
        changed["migrations"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "manifest.json"
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "order or checksum"):
                RUNNER.validate_candidate_manifest(
                    path,
                    "20260826-1625-v3-draft",
                    self.migrations,
                )

    def test_history_insert_never_overwrites_a_recorded_checksum(self):
        context = RUNNER.MigrationContext(
            release_id="test-release",
            release_time="20260827-090000",
            label="test",
            operator="test",
            mode="apply",
            host="HOST",
            user="USER",
            identity_file=pathlib.Path("identity"),
            mysql_database="kaipai_test",
            mysql_container="kaipai-mysql",
            history_release_id="test-release",
        )
        sql = RUNNER.build_history_insert_sql(context, self.migrations[0], "apply")

        self.assertIn("INSERT INTO `schema_release_history`", sql)
        self.assertNotIn("ON DUPLICATE KEY UPDATE", sql)

    def test_history_parser_ignores_mysql_expression_header(self):
        checksum = "a" * 64
        output = "\n".join(
            [
                "CONCAT('APPLIED_RECORD=', `script`, '|', `checksum`)",
                f"APPLIED_RECORD=V1__one.sql|{checksum}|apply|release-1",
            ]
        )

        records = RUNNER.parse_applied_records(output)

        self.assertEqual(list(records), ["V1__one.sql"])
        self.assertEqual(records["V1__one.sql"]["checksum"], checksum.upper())

    def test_all_non_idempotent_migrations_have_state_preflights(self):
        for script_name in RUNNER.NON_IDEMPOTENT_MIGRATIONS:
            sql = RUNNER.build_migration_preflight_sql(script_name)
            self.assertIn("PREFLIGHT_STATE=", sql)
            self.assertIn("PARTIAL_OR_AMBIGUOUS", sql)

    def test_preflight_parser_rejects_missing_or_unknown_state(self):
        self.assertEqual(
            RUNNER.parse_preflight_state("PREFLIGHT_STATE=CLEAN_NOT_APPLIED"),
            "CLEAN_NOT_APPLIED",
        )
        with self.assertRaisesRegex(RuntimeError, "state is missing"):
            RUNNER.parse_preflight_state("PREFLIGHT_STATE=UNKNOWN")

    def test_global_assertions_bind_history_to_manifest_checksums(self):
        sql = RUNNER.build_global_schema_assertion_sql(self.migrations)

        self.assertIn("ASSERT_TARGET_TABLES", sql)
        self.assertIn("ASSERT_CHECKSUM_MISMATCH", sql)
        for migration in self.migrations:
            self.assertIn(migration.script_name, sql)
            self.assertIn(migration.checksum.upper(), sql)


if __name__ == "__main__":
    unittest.main()
