import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HELPER = ROOT / '.sce' / 'runbooks' / 'backend-admin-release' / 'scripts' / 'kaipai-backend-release-helper.sh'


class BackendHelperMysqlDumpTest(unittest.TestCase):
    def test_mysql_dump_mode_is_exposed_and_bounded(self):
        text = HELPER.read_text(encoding='utf-8')
        self.assertIn('mysql_dump="false"', text)
        self.assertIn('--mysql-dump)', text)
        self.assertIn('if [[ "$mysql_dump" == "true" ]]; then', text)
        self.assertIn('backup_root="/opt/kaipai/backups/releases/$release_id/mysql-dump"', text)
        self.assertIn('mysqldump --default-character-set=utf8mb4', text)
        self.assertIn('MYSQL_PWD="$mysql_root_password"', text)
        self.assertIn('MYSQL_DUMP_PATH', text)
        self.assertIn('MYSQL_DUMP_SHA256', text)

    def test_mysql_dump_keeps_stderr_out_of_sql_payload(self):
        text = HELPER.read_text(encoding='utf-8')
        self.assertNotIn('> "$dump_file" 2>&1', text)
        self.assertIn('dump_log="$backup_root/${mysql_database}.dump.log"', text)
        self.assertIn('2> "$dump_log"', text)
        self.assertIn('MYSQL_DUMP_LOG', text)

    def test_mysql_helper_does_not_hardcode_root_password(self):
        text = HELPER.read_text(encoding='utf-8')
        self.assertIn('resolve_mysql_root_password()', text)
        self.assertIn('KAIPAI_RELEASE_MYSQL_ROOT_PASSWORD', text)
        self.assertNotIn('root' + '123456', text)

    def test_nacos_helper_does_not_hardcode_password_default(self):
        text = HELPER.read_text(encoding='utf-8')
        self.assertIn('nacos_password="${KAIPAI_RELEASE_NACOS_PASSWORD:-${NACOS_PASSWORD:-}}"', text)
        self.assertIn('nacos password is required via --nacos-password', text)
        self.assertNotIn('kaipai' + 'nacos', text)


if __name__ == '__main__':
    unittest.main()
