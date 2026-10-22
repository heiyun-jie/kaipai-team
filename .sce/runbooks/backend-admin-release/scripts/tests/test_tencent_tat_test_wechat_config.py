import base64
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "run-tencent-tat-test-wechat-config.py"


def load_module():
    spec = importlib.util.spec_from_file_location("run_tencent_tat_test_wechat_config", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TencentTatTestWechatConfigTests(unittest.TestCase):
    def test_remote_script_is_fixed_to_test_runtime_and_protects_production(self):
        module = load_module()

        script = module.build_remote_script("test-wechat-20260828-unit")

        self.assertIn("runtime_root=/opt/kaipai/test", script)
        self.assertIn("test_service=kaipai-test", script)
        self.assertIn("test_container=kaipai-backend-test", script)
        self.assertIn("prod_container=kaipai-backend", script)
        self.assertIn("SPRING_DATA_REDIS_DATABASE=1", script)
        self.assertIn("kaipai_test", script)
        self.assertIn('[[ "$prod_after" == "$prod_before" ]]', script)
        self.assertIn("compose_cmd=(docker compose)", script)
        self.assertIn("compose_cmd=(docker-compose)", script)
        self.assertNotIn("kaipai_prod?", script)
        self.assertNotRegex(script, r"WECHAT_MINIAPP_APP_SECRET=[A-Za-z0-9]{16,}")

    def test_remote_script_rejects_unapproved_release_id(self):
        module = load_module()

        with self.assertRaisesRegex(RuntimeError, "invalid release id"):
            module.build_remote_script("prod-release")

    def test_instance_discovery_finds_lighthouse_by_public_ip(self):
        module = load_module()

        def fake_call_api(_credentials, *, service, **_kwargs):
            if service == "cvm":
                return {"InstanceSet": []}
            return {
                "InstanceSet": [
                    {"InstanceId": "lhins-test", "PublicAddresses": [module.DEFAULT_PUBLIC_IP]}
                ]
            }

        with patch.object(module, "call_api", side_effect=fake_call_api):
            found = module.discover_instance(
                module.Credentials("id", "key"), module.DEFAULT_PUBLIC_IP, ("ap-shanghai",)
            )

        self.assertEqual(found, ("ap-shanghai", "lhins-test", "lighthouse"))

    def test_task_output_is_read_from_nested_task_result(self):
        module = load_module()
        expected = "FINAL_STATUS=passed\n"
        task = {"TaskResult": {"Output": base64.b64encode(expected.encode()).decode()}}

        self.assertEqual(module.decode_task_output(task), expected)


if __name__ == "__main__":
    unittest.main()
