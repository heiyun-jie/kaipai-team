# 本地 AI 通知配置输入检查

- Capture ID: `20260404-091020-continue-http-provider-real-route-local-input`
- Secret File: `D:\XM\kaipai-team\.sce\config\local-secrets\ai-resume-notification.env`
- Exists: `yes`
- Release Ready: `yes`

## Resolved Inputs

- `AI_RESUME_NOTIFICATION_ENABLED`: `true`
- `AI_RESUME_NOTIFICATION_PROVIDER_CODE`: `http`
- `AI_RESUME_NOTIFICATION_CALLBACK_HEADER`: `X-Kaipai-Ai-Notification-Token`
- `AI_RESUME_NOTIFICATION_CALLBACK_TOKEN`: `[REDACTED]`
- `AI_RESUME_NOTIFICATION_CALLBACK_URL`: `http://101.43.57.62/api/internal/ai/resume/notification-receipts/provider`
- `AI_RESUME_NOTIFICATION_HTTP_ENDPOINT`: `http://101.43.57.62/bridge/ai-notification/`
- `AI_RESUME_NOTIFICATION_HTTP_AUTH_HEADER`: `Authorization`
- `AI_RESUME_NOTIFICATION_HTTP_AUTH_TOKEN`: `--`

## Validation

- `AI_RESUME_NOTIFICATION_ENABLED`: `passed`
- `AI_RESUME_NOTIFICATION_PROVIDER_CODE`: `passed`
- `AI_RESUME_NOTIFICATION_CALLBACK_HEADER`: `passed`
- `AI_RESUME_NOTIFICATION_CALLBACK_TOKEN`: `passed`
- `AI_RESUME_NOTIFICATION_CALLBACK_URL`: `passed`
- `AI_RESUME_NOTIFICATION_HTTP_ENDPOINT`: `passed`
- `AI_RESUME_NOTIFICATION_HTTP_AUTH_HEADER`: `passed`
- `AI_RESUME_NOTIFICATION_HTTP_AUTH_TOKEN`: `passed`
