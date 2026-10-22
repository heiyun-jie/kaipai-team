import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[4]
SCRIPTS = ROOT / "runbooks" / "backend-admin-release" / "scripts"


class TestEnvironmentScriptsTest(unittest.TestCase):
    def test_provision_supports_compose_plugin_and_standalone_binary(self):
        script = (SCRIPTS / "provision-test-environment.sh").read_text(encoding="utf-8")

        self.assertIn("if docker compose version", script)
        self.assertIn("compose_cmd=(docker compose)", script)
        self.assertIn("command -v docker-compose", script)
        self.assertIn("compose_cmd=(docker-compose)", script)
        self.assertIn('"${compose_cmd[@]}" -f "$compose_file" up -d --build kaipai-test', script)
        self.assertNotIn('compose_cmd=(docker compose -f "$compose_file")', script)
        self.assertIn("for ((attempt = 1; attempt <= 60; attempt++))", script)
        self.assertIn('[[ "$test_api_ready" != "true" ]]', script)
        self.assertIn('test_secret_env="$runtime_root/test-secrets.env"', script)
        self.assertIn('chmod 0600 "$test_secret_env"', script)
        self.assertIn('env_file:', script)
        self.assertIn('test_bucket_name="${KAIPAI_TEST_COS_BUCKET_NAME:-kaipai-test-1412601014}"', script)
        self.assertIn('TENCENT_COS_REGION: "$prod_cos_region"', script)
        cos_match = script.index('if [[ -n "$prod_cos_region" && "$prod_cos_bucket" =~ -([0-9]+)$ ]]')
        cos_capture = script.index('prod_cos_appid="${BASH_REMATCH[1]}"')
        wechat_match = script.index('[[ "$test_wechat_app_id" =~ ^wx[A-Za-z0-9]{16}$')
        self.assertLess(cos_match, cos_capture)
        self.assertLess(cos_capture, wechat_match)
        self.assertIn("test_wechat_app_id=", script)
        self.assertIn("test_wechat_app_secret=", script)
        self.assertIn("WECHAT_MINIAPP_APP_ID=%s", script)
        self.assertIn("WECHAT_MINIAPP_APP_SECRET=%s", script)
        self.assertIn("test WeChat appId missing", script)
        self.assertIn("test WeChat appSecret missing", script)
        self.assertNotIn("TENCENT_CLOUD_SECRET_ID: ", script)
        self.assertNotIn("TENCENT_CLOUD_SECRET_KEY: ", script)
        self.assertNotIn("WECHAT_MINIAPP_APP_SECRET: ", script)

    def test_rollback_uses_the_same_compose_detection(self):
        script = (SCRIPTS / "rollback-test-environment.sh").read_text(encoding="utf-8")

        self.assertIn("if docker compose version", script)
        self.assertIn("compose_cmd=(docker compose)", script)
        self.assertIn("command -v docker-compose", script)
        self.assertIn("compose_cmd=(docker-compose)", script)
        self.assertIn('"${compose_cmd[@]}" -f "$compose_file" down', script)


if __name__ == "__main__":
    unittest.main()
