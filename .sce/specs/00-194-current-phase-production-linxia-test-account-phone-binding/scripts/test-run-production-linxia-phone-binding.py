import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("run-production-linxia-phone-binding.py")
spec = importlib.util.spec_from_file_location("linxia_phone_binding", SCRIPT_PATH)
binding = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(binding)


def make_context() -> binding.Context:
    return binding.Context(
        mode="precheck",
        run_id="test-run",
        operator="test",
        host="127.0.0.1",
        user="kaipaile",
        identity_file=Path("id"),
        mysql_database="kaipai_prod",
        mysql_container="kaipai-mysql",
        source_database="kaipai_dev",
        target_phone="13700000000",
        source_user_id=None,
        output_dir=Path("out"),
    )


class LinxiaPhoneBindingScriptTest(unittest.TestCase):
    def test_precheck_blocks_when_remote_helper_failed(self) -> None:
        original_upload = binding.upload_and_run_sql
        try:
            binding.upload_and_run_sql = lambda *_args, **_kwargs: {
                "REMOTE_DATE": "2026-07-09 12:00:00 +0800",
                "MYSQL_MODE": "validation",
                "MYSQL_DATABASE": "kaipai_prod",
                "MYSQL_CONTAINER": "kaipai-mysql",
                "MYSQL_RESULT": "ERROR 1146 (42S02): Table 'kaipai_prod.user' doesn't exist",
                "FINAL_STATUS": "failed",
                "FAIL_REASON": "mysql validation failed",
            }

            ok, markers, errors, _summary = binding.execute_precheck(make_context())

            self.assertFalse(ok)
            self.assertEqual({}, markers)
            self.assertIn("remote helper failed: mysql validation failed", errors)
        finally:
            binding.upload_and_run_sql = original_upload

    def test_apply_guard_runs_before_backup_tables_are_created(self) -> None:
        sql, _user_backup, _actor_backup = binding.build_apply_sql(make_context())

        signal_index = sql.index("PREPARE guard_stmt FROM @signal_sql;")
        backup_index = sql.index("CREATE TABLE IF NOT EXISTS `zz_bak_194_linxia_user_")

        self.assertLess(signal_index, backup_index)

    def test_diagnose_sql_outputs_only_masked_target_phone(self) -> None:
        context = make_context()
        sql = binding.build_diagnose_sql(context)

        self.assertIn(context.target_phone, sql)
        output_sql = sql[sql.index("'TARGET_USER='") :]

        self.assertNotIn(context.target_phone, output_sql)
        self.assertIn("@target_phone_mask", output_sql)
        self.assertIn("PHONE_MASK=", output_sql)

    def test_parse_markers_keeps_repeated_marker_rows(self) -> None:
        markers = binding.parse_markers(
            "TARGET_USER=1,PHONE_MASK=137****0000\n"
            "TARGET_USER=2,PHONE_MASK=137****0000\n"
        )

        self.assertEqual("1,PHONE_MASK=137****0000", markers["TARGET_USER"])
        self.assertEqual("2,PHONE_MASK=137****0000", markers["TARGET_USER_2"])

    def test_inventory_sql_lists_actor_assets_without_raw_phone_output(self) -> None:
        context = make_context()
        sql = binding.build_inventory_sql(context)

        self.assertIn(context.target_phone, sql)
        output_sql = sql[sql.index("'ACTOR_WITH_CARDS='") :]

        self.assertNotIn(context.target_phone, output_sql)
        self.assertIn("USER_PHONE_MASK=", output_sql)
        self.assertIn("SHARE_CARD_COUNT=", output_sql)

    def test_roster_sql_lists_users_without_raw_phone_output(self) -> None:
        context = make_context()
        sql = binding.build_roster_sql(context)

        self.assertIn(context.target_phone, sql)
        output_sql = sql[sql.index("'USER_ROSTER='") :]

        self.assertNotIn(context.target_phone, output_sql)
        self.assertIn("PHONE_MASK=", output_sql)
        self.assertIn("ACTOR_PROFILE_COUNT=", output_sql)

    def test_migration_precheck_uses_source_and_target_databases(self) -> None:
        context = make_context()
        sql = binding.build_migration_precheck_sql(context)

        self.assertIn("`kaipai_dev`.`user`", sql)
        self.assertIn("`kaipai_prod`.`user`", sql)
        self.assertIn("SET @source_user_id = 10007", sql)
        self.assertIn("SOURCE_USER_ID=", sql)
        self.assertIn("TARGET_EMPTY_USER_ASSET_COUNT=", sql)

    def test_migration_apply_soft_deletes_target_empty_user_before_inserting_source_user(self) -> None:
        context = make_context()
        sql, backup_tables = binding.build_migration_apply_sql(context)

        soft_delete_index = sql.index("UPDATE `kaipai_prod`.`user`")
        insert_source_user_index = sql.index("CALL kp_194_insert_common_columns('kaipai_prod', 'kaipai_dev', 'user'")

        self.assertLess(soft_delete_index, insert_source_user_index)
        self.assertIn("account = CONCAT('archived-00-194-', user_id, '-', @target_phone)", sql)
        self.assertIn("user_share_card", sql)
        self.assertIn("actor_card_config", sql)
        self.assertIn("identity_verification", sql)
        self.assertTrue(backup_tables)

    def test_migration_backup_table_names_fit_mysql_identifier_limit(self) -> None:
        _sql, backup_tables = binding.build_migration_apply_sql(make_context())

        self.assertTrue(backup_tables)
        self.assertTrue(all(len(name) <= 64 for name in backup_tables))

    def test_migration_apply_uses_explicit_common_columns_for_cross_database_inserts(self) -> None:
        sql, _backup_tables = binding.build_migration_apply_sql(make_context())

        self.assertIn("information_schema.COLUMNS", sql)
        self.assertNotIn("INSERT INTO `kaipai_prod`.`user`\nSELECT * FROM `kaipai_dev`.`user`", sql)
        self.assertIn("CALL kp_194_insert_common_columns", sql)

    def test_cleanup_sql_drops_migration_helper_procedure(self) -> None:
        sql = binding.build_cleanup_sql()

        self.assertIn("DROP PROCEDURE IF EXISTS kp_194_insert_common_columns", sql)
        self.assertIn("MIGRATION_HELPER_PROCEDURE_DROPPED=1", sql)

    def test_execute_cleanup_uses_mysql_apply(self) -> None:
        calls: list[tuple[str, str, str]] = []
        original_upload = binding.upload_and_run_sql
        try:
            def fake_upload(_context, sql_content: str, helper_flag: str, remote_stem: str) -> dict[str, str]:
                calls.append((sql_content, helper_flag, remote_stem))
                return {
                    "REMOTE_DATE": "2026-07-09 12:00:00 +0800",
                    "MYSQL_MODE": "apply",
                    "MYSQL_DATABASE": "kaipai_prod",
                    "MYSQL_CONTAINER": "kaipai-mysql",
                    "MYSQL_RESULT": "MIGRATION_HELPER_PROCEDURE_DROPPED=1",
                    "FINAL_STATUS": "passed",
                    "FAIL_REASON": "",
                }

            binding.upload_and_run_sql = fake_upload

            ok, markers, errors, _summary = binding.execute_cleanup(make_context())

            self.assertTrue(ok)
            self.assertEqual([], errors)
            self.assertEqual("1", markers["MIGRATION_HELPER_PROCEDURE_DROPPED"])
            self.assertEqual("--mysql-apply", calls[0][1])
            self.assertEqual("linxia-account-migration-cleanup", calls[0][2])
        finally:
            binding.upload_and_run_sql = original_upload

    def test_execute_send_code_outputs_only_masked_phone(self) -> None:
        calls: list[tuple[str, dict[str, str] | None, str | None]] = []
        original_api_request = binding.api_request_json
        try:
            def fake_api_request(context, path: str, payload=None, token=None):
                calls.append((path, payload, token))
                return {"code": 200, "message": "验证码发送成功", "data": None}

            binding.api_request_json = fake_api_request

            ok, markers, errors, summary = binding.execute_send_code(make_context())

            self.assertTrue(ok)
            self.assertEqual([], errors)
            self.assertEqual("1", markers["SEND_CODE_REQUESTED"])
            self.assertEqual("137****0000", markers["TARGET_PHONE_MASK"])
            self.assertNotIn("13700000000", summary["MYSQL_RESULT"])
            self.assertEqual(("/api/auth/sendCode", {"phone": "13700000000"}, None), calls[0])
        finally:
            binding.api_request_json = original_api_request

    def test_execute_api_verify_keeps_token_out_of_summary(self) -> None:
        context = make_context()
        original_api_request = binding.api_request_json
        original_code = binding.os.environ.get("KP_BIND_LOGIN_CODE")
        try:
            binding.os.environ["KP_BIND_LOGIN_CODE"] = "123456"

            def fake_api_request(_context, path: str, payload=None, token=None):
                if path == "/api/auth/login":
                    return {
                        "code": 200,
                        "data": {
                            "token": "jwt-secret-token",
                            "userId": 10007,
                            "phone": "13700000000",
                            "userType": 1,
                        },
                    }
                if path == "/api/user/me":
                    self.assertEqual("jwt-secret-token", token)
                    return {"code": 200, "data": {"userId": 10007, "phone": "13700000000", "userType": 1}}
                if path == "/api/actor/profile/mine":
                    self.assertEqual("jwt-secret-token", token)
                    return {"code": 200, "data": {"userId": 10007, "name": "林夏", "realName": "林夏"}}
                if path == "/api/card/my-cards":
                    self.assertEqual("jwt-secret-token", token)
                    return {"code": 200, "data": {"cards": [{"cardId": 1}, {"cardId": 2}, {"cardId": 3}]}}
                raise AssertionError(f"unexpected path {path}")

            binding.api_request_json = fake_api_request

            ok, markers, errors, summary = binding.execute_api_verify(context)

            self.assertTrue(ok)
            self.assertEqual([], errors)
            self.assertEqual("10007", markers["LOGIN_USER_ID"])
            self.assertEqual("1", markers["LOGIN_TOKEN_PRESENT"])
            self.assertEqual("3", markers["API_CARD_COUNT"])
            self.assertNotIn("jwt-secret-token", summary["MYSQL_RESULT"])
            self.assertNotIn("13700000000", summary["MYSQL_RESULT"])
        finally:
            binding.api_request_json = original_api_request
            if original_code is None:
                binding.os.environ.pop("KP_BIND_LOGIN_CODE", None)
            else:
                binding.os.environ["KP_BIND_LOGIN_CODE"] = original_code


if __name__ == "__main__":
    unittest.main()
