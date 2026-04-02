# 后端微信配置门禁预检查

- Capture ID: `20260403-062424-invite-wxacode-wechat-config-gate`
- Label: `invite-wxacode-wechat-config-gate`
- Host: `101.43.57.62`
- Container: `kaipai-backend`
- Gate Result: `blocked`

## Compose / Runtime

- compose source present: `--`
- compose source missing: `WECHAT_MINIAPP_APP_ID, WECHAT_MINIAPP_APP_SECRET`
- compose rendered present: `--`
- compose rendered missing: `WECHAT_MINIAPP_APP_ID, WECHAT_MINIAPP_APP_SECRET`
- container env present: `--`
- container env missing: `WECHAT_MINIAPP_APP_ID, WECHAT_MINIAPP_APP_SECRET`

## Nacos

- `kaipai-backend` present: `--`
- `kaipai-backend` missing: `app-id, app-secret`
- `kaipai-backend.yml` present: `--`
- `kaipai-backend.yml` missing: `app-id, app-secret`
- `kaipai-backend-dev.yml` present: `--`
- `kaipai-backend-dev.yml` missing: `app-id, app-secret`

## Conclusion

- failing checks: `compose_source, compose_rendered, container_env, nacos:kaipai-backend, nacos:kaipai-backend.yml, nacos:kaipai-backend-dev.yml`
- current result: required WeChat keys are still incomplete across compose/runtime and Nacos, so wxacode/login-auth real-environment gate is not open
- next step: first补齐合法配置来源，再按 `backend-only` 标准发布重建，并复跑本预检查
