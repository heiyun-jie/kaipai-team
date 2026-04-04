# 本地 AI 通知 HTTP Bridge 输入检查

- Capture ID: `20260404-091229-continue-http-provider-real-route-rerun2-bridge-input`
- Secret File: `D:\XM\kaipai-team\.sce\config\local-secrets\ai-notification-http-bridge.env`
- Exists: `yes`
- Release Ready: `yes`

## Resolved Inputs

- `AI_NOTIFICATION_HTTP_BRIDGE_EXPECTED_PROVIDER_CODE`: `http`
- `AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT`: `http://101.43.57.62/bridge/ai-notification/`
- `AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_BASE_URL`: `http://101.43.57.62/api`
- `AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_PATH`: `/internal/ai/resume/notification-receipts/provider`
- `AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER`: `Authorization`
- `AI_NOTIFICATION_HTTP_BRIDGE_AUTH_TOKEN`: `--`

## Derived Runtime Values

- `AI_RESUME_NOTIFICATION_CALLBACK_URL`: `http://101.43.57.62/api/internal/ai/resume/notification-receipts/provider`
- `AI_RESUME_NOTIFICATION_HTTP_AUTH_HEADER`: `Authorization`
- `AI_RESUME_NOTIFICATION_HTTP_ENDPOINT`: `http://101.43.57.62/bridge/ai-notification/`
- `AI_RESUME_NOTIFICATION_PROVIDER_CODE`: `http`

## Validation

- `AI_NOTIFICATION_HTTP_BRIDGE_EXPECTED_PROVIDER_CODE`: `passed`
- `AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT`: `passed`
- `AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_BASE_URL`: `passed`
- `AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_PATH`: `passed`
- `AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER`: `passed`
- `AI_NOTIFICATION_HTTP_BRIDGE_AUTH_TOKEN`: `passed`
