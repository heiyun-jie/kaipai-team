import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "run-tencent-tat-test-candidate-stack.py"
SPEC = importlib.util.spec_from_file_location("test_candidate_stack", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestCandidateStackScriptTests(unittest.TestCase):
    def test_remote_script_is_bounded_to_test_stack(self):
        script = MODULE.build_remote_script(
            "20260901-150906-v3-draft",
            "a" * 64,
            "b" * 64,
        )
        self.assertIn("test_database=kaipai_test", script)
        self.assertIn("test_container=kaipai-backend-test", script)
        self.assertIn("prod_container=kaipai-backend", script)
        self.assertIn('[[ "$prod_after" == "$prod_before" ]]', script)
        self.assertIn("PRODUCTION_MUTATION=NONE", script)
        self.assertNotIn("DROP DATABASE IF EXISTS kaipai_prod", script)
        self.assertNotIn("docker restart kaipai-backend", script)

    def test_invalid_candidate_id_is_rejected(self):
        with self.assertRaises(RuntimeError):
            MODULE.build_remote_script("../../prod", "a" * 64, "b" * 64)

    def test_invalid_hash_is_rejected(self):
        with self.assertRaises(RuntimeError):
            MODULE.build_remote_script("20260901-150906-v3-draft", "short", "b" * 64)


if __name__ == "__main__":
    unittest.main()
