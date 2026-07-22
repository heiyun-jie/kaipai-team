import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("run-production-tencent-provider-migration.py")
spec = importlib.util.spec_from_file_location("tencent_provider_migration", SCRIPT_PATH)
migration = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(migration)


def make_context() -> migration.Context:
    return migration.Context(
        mode="precheck",
        run_id="20260721-160000-test",
        operator="test",
        host="127.0.0.1",
        user="kaipaile",
        identity_file=Path("id"),
        mysql_database="kaipai_prod",
        mysql_container="kaipai-mysql",
        source_database="kaipai_dev",
    )


class TencentProviderMigrationScriptTest(unittest.TestCase):
    def test_command_token_accepts_docker_container_hyphen_but_rejects_shell_syntax(self) -> None:
        self.assertEqual("kaipai-mysql", migration.command_token("kaipai-mysql"))

        with self.assertRaises(RuntimeError):
            migration.command_token("kaipai-mysql; whoami")

    def test_precheck_reads_source_and_target_without_outputting_ciphertext(self) -> None:
        sql = migration.build_precheck_sql(make_context())

        self.assertIn("`kaipai_dev`.`ai_image_provider_config`", sql)
        self.assertIn("`kaipai_prod`.`ai_image_provider_config`", sql)
        self.assertIn("provider_code = 'tencent-hunyuan'", sql)
        self.assertIn("SOURCE_HAS_SECRET=", sql)
        self.assertIn("TARGET_CONFIG_COUNT=", sql)
        self.assertIn("PRECHECK_PASSED=", sql)

        marker_output = sql[sql.index("'SOURCE_PROVIDER_COUNT='") :]
        self.assertNotIn("secret_config_ciphertext", marker_output)

    def test_precheck_validation_requires_verified_active_tencent_source_and_empty_target(self) -> None:
        valid = {
            "SOURCE_PROVIDER_COUNT": "1",
            "SOURCE_ENABLED": "1",
            "SOURCE_ACTIVE": "1",
            "SOURCE_ENDPOINT": "https://aiart.tencentcloudapi.com",
            "SOURCE_MODEL": "hunyuan-image-3.0",
            "SOURCE_HAS_SECRET": "1",
            "SOURCE_LAST_TEST_STATUS": "success",
            "TARGET_CONFIG_COUNT": "0",
            "TARGET_ACTIVE_COUNT": "0",
            "TARGET_TENCENT_COUNT": "0",
            "PRECHECK_PASSED": "1",
        }

        self.assertEqual([], migration.validate_precheck_markers(valid))

        invalid = dict(valid)
        invalid["SOURCE_ACTIVE"] = "0"
        invalid["TARGET_CONFIG_COUNT"] = "1"
        errors = migration.validate_precheck_markers(invalid)

        self.assertTrue(any("SOURCE_ACTIVE" in error for error in errors))
        self.assertTrue(any("TARGET_CONFIG_COUNT" in error for error in errors))

    def test_apply_guards_before_backup_and_copies_only_tencent(self) -> None:
        sql, backup_tables = migration.build_apply_sql(make_context())

        guard_index = sql.index("PREPARE guard_stmt FROM @signal_sql;")
        backup_index = sql.index("CREATE TABLE `zz197_")
        deactivate_index = sql.index("SET `active` = 0")
        insert_index = sql.index("INSERT INTO `kaipai_prod`.`ai_image_provider_config`")

        self.assertLess(guard_index, backup_index)
        self.assertLess(backup_index, deactivate_index)
        self.assertLess(deactivate_index, insert_index)
        self.assertIn("FROM `kaipai_dev`.`ai_image_provider_config` AS source", sql)
        self.assertIn("source.`provider_code` = 'tencent-hunyuan'", sql)
        self.assertIn("'migration_restore'", sql)
        self.assertNotIn("'kplyyk'", sql)
        self.assertEqual(2, len(backup_tables))
        self.assertTrue(all(name.startswith("zz197_") for name in backup_tables))
        self.assertTrue(all(len(name) <= 64 for name in backup_tables))

    def test_apply_keeps_secret_ciphertext_inside_database_copy(self) -> None:
        sql, _backup_tables = migration.build_apply_sql(make_context())

        self.assertIn("`secret_config_ciphertext`", sql)
        self.assertIn("source.`secret_config_ciphertext`", sql)
        marker_output = sql[sql.index("'BACKUP_CONFIG_TABLE='") :]
        self.assertNotIn("secret_config_ciphertext", marker_output)

    def test_verify_exposes_only_sanitized_runtime_markers(self) -> None:
        sql = migration.build_verify_sql(make_context())

        for marker in (
            "TARGET_TENCENT_COUNT=",
            "TARGET_ACTIVE_COUNT=",
            "ACTIVE_PROVIDER=",
            "ENDPOINT=",
            "MODEL=",
            "HAS_SECRET=",
            "MIGRATION_AUDIT_COUNT=",
            "LAST_TEST_STATUS=",
            "VERIFY_PASSED=",
        ):
            self.assertIn(marker, sql)

        marker_output = sql[sql.index("'TARGET_TENCENT_COUNT='") :]
        self.assertNotIn("secret_config_ciphertext", marker_output)

    def test_verify_validation_requires_tencent_as_single_active_provider(self) -> None:
        valid = {
            "TARGET_TENCENT_COUNT": "1",
            "TARGET_ACTIVE_COUNT": "1",
            "ACTIVE_PROVIDER": "tencent-hunyuan",
            "ENDPOINT": "https://aiart.tencentcloudapi.com",
            "MODEL": "hunyuan-image-3.0",
            "HAS_SECRET": "1",
            "MIGRATION_AUDIT_COUNT": "1",
            "LAST_TEST_STATUS": "NULL",
            "VERIFY_PASSED": "1",
        }

        self.assertEqual([], migration.validate_verify_markers(valid, require_test_success=False))

        valid["LAST_TEST_STATUS"] = "success"
        self.assertEqual([], migration.validate_verify_markers(valid, require_test_success=True))

        invalid = dict(valid)
        invalid["ACTIVE_PROVIDER"] = "kplyyk"
        errors = migration.validate_verify_markers(invalid, require_test_success=True)
        self.assertTrue(any("ACTIVE_PROVIDER" in error for error in errors))

    def test_parse_markers_reads_sanitized_key_value_lines(self) -> None:
        markers = migration.parse_markers(
            "SOURCE_PROVIDER_COUNT=1\n"
            "ACTIVE_PROVIDER=tencent-hunyuan\n"
            "LAST_TEST_STATUS=NULL\n"
        )

        self.assertEqual("1", markers["SOURCE_PROVIDER_COUNT"])
        self.assertEqual("tencent-hunyuan", markers["ACTIVE_PROVIDER"])
        self.assertEqual("NULL", markers["LAST_TEST_STATUS"])


if __name__ == "__main__":
    unittest.main()
