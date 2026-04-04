# 本地 AI 通知配置输入检查

- Capture ID: `20260404-060304-continue-ai-notification-local-gate-local-input`
- Secret File: `D:\XM\kaipai-team\.sce\config\local-secrets\ai-resume-notification.env`
- Exists: `yes`
- Release Ready: `no`

## Resolved Inputs

- `AI_RESUME_NOTIFICATION_ENABLED`: `true`
- `AI_RESUME_NOTIFICATION_PROVIDER_CODE`: `manual`
- `AI_RESUME_NOTIFICATION_CALLBACK_HEADER`: `X-Kaipai-Ai-Notification-Token`
- `AI_RESUME_NOTIFICATION_CALLBACK_TOKEN`: `[REDACTED]`

## Validation

- `AI_RESUME_NOTIFICATION_ENABLED`: `passed`
- `AI_RESUME_NOTIFICATION_PROVIDER_CODE`: `passed`
- `AI_RESUME_NOTIFICATION_CALLBACK_HEADER`: `passed`
- `AI_RESUME_NOTIFICATION_CALLBACK_TOKEN`: `placeholder_callback_token`

## Conclusion

- 当前本地 AI 通知配置输入未就绪，不能继续进入 Nacos 同步或真实通知样本验证
