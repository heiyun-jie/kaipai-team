import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[4]
SCRIPTS = ROOT / "runbooks" / "backend-admin-release" / "scripts"


class TestProductionCopyScriptsTest(unittest.TestCase):
    def test_prepare_script_has_exact_target_and_production_guards(self):
        script = (SCRIPTS / "prepare-test-production-copy.sh").read_text(encoding="utf-8")

        self.assertIn('test_database="kaipai_test"', script)
        self.assertIn('prod_database="kaipai_prod"', script)
        self.assertIn('[[ "$test_database" == "kaipai_test" ]]', script)
        self.assertIn('[[ "$prod_database" == "kaipai_prod"', script)
        self.assertIn('docker stop "$test_container"', script)
        self.assertNotIn('docker stop "$prod_container"', script)
        self.assertNotIn('DROP DATABASE IF EXISTS `kaipai_prod`', script)

    def test_prepare_script_requires_verified_backups_before_drop(self):
        script = (SCRIPTS / "prepare-test-production-copy.sh").read_text(encoding="utf-8")
        drop_position = script.index('DROP DATABASE IF EXISTS')

        self.assertLess(script.index('gzip -t "$prod_sql.gz"'), drop_position)
        self.assertLess(script.index('old_test_dump_sha='), drop_position)
        self.assertIn('restored canonical dump checksum does not match production snapshot', script)
        self.assertIn('restored table counts do not match production snapshot', script)
        self.assertIn("canonical_dump_sha()", script)

    def test_rollback_is_scoped_to_candidate_backup_root(self):
        script = (SCRIPTS / "rollback-test-production-copy.sh").read_text(encoding="utf-8")

        self.assertIn('resolved_backup="$(readlink -f "$backup_root"', script)
        self.assertIn('"$resolved_backup" == "$resolved_allowed"/*', script)
        self.assertIn('kaipai-test-before.sql.gz', script)
        self.assertNotIn('DROP DATABASE IF EXISTS `kaipai_prod`', script)


if __name__ == "__main__":
    unittest.main()
