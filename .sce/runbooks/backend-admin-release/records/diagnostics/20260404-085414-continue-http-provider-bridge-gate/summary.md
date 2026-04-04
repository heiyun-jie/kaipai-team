# 本地 AI 通知 HTTP Bridge 输入检查

- Capture ID: `20260404-085414-continue-http-provider-bridge-gate`
- Secret File: `D:\XM\kaipai-team\.sce\config\local-secrets\ai-notification-http-bridge.env`
- Exists: `yes`
- Release Ready: `no`

## Resolved Inputs

- `AI_NOTIFICATION_HTTP_BRIDGE_EXPECTED_PROVIDER_CODE`: `http`
- `AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT`: `--`
- `AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_BASE_URL`: `http://101.43.57.62/api`
- `AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_PATH`: `/internal/ai/resume/notification-receipts/provider`
- `AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER`: `Authorization`
- `AI_NOTIFICATION_HTTP_BRIDGE_AUTH_TOKEN`: `--`

## Derived Runtime Values

- `AI_RESUME_NOTIFICATION_CALLBACK_URL`: `http://101.43.57.62/api/internal/ai/resume/notification-receipts/provider`
- `AI_RESUME_NOTIFICATION_HTTP_AUTH_HEADER`: `Authorization`
- `AI_RESUME_NOTIFICATION_PROVIDER_CODE`: `http`

## Validation

- `AI_NOTIFICATION_HTTP_BRIDGE_EXPECTED_PROVIDER_CODE`: `passed`
- `AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT`: `missing`
- `AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_BASE_URL`: `passed`
- `AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_PATH`: `passed`
- `AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER`: `passed`
- `AI_NOTIFICATION_HTTP_BRIDGE_AUTH_TOKEN`: `passed`

## Conclusion

- 当前没有可用的 bridge endpoint / callback base url 输入，不能把 `provider-code=http` 推进到目标环境验证
