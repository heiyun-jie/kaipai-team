# Login Auth Validation Report

- Generated At: 2026-04-03 12:29:32
- Environment: dev
- Sample Label: legal-secret-gate-aligned

## Local Runtime Scan

- Frontend baseURL: http://101.43.57.62
- Frontend mock flag: false
- Frontend WeChat flag: false
- Admin baseURL: /api
- Backend entry: http://101.43.57.62/api
- Server exposes WeChat placeholders: appId=是, appSecret=是

## Live Probe

- Probe baseURL: http://101.43.57.62
- sendCode: transport=200, code=200, message=验证码发送成功
- wechat-login: transport=200, code=500, message=微信登录未配置小程序 appId/appSecret

## Confirmed

- [x] Live probe confirms POST /api/auth/sendCode returns code=200 and still exposes a development verification code
- [x] 当前小程序运行时已显式关闭全局 mock，并指向真实后端入口。
- [x] 后端源码配置已暴露微信小程序 appId/appSecret 占位符。
- [x] sendCode live probe: transport=200, code=200, message=验证码发送成功
- [x] wechat-login live probe: transport=200, code=500, message=微信登录未配置小程序 appId/appSecret

## Blockers

- [ ] Frontend VITE_ENABLE_WECHAT_AUTH is not true; real WeChat path cannot be validated
- [ ] Local WeChat secret input is not ready; follow .sce/runbooks/backend-admin-release/wechat-config-gate-runbook.md and replace placeholder/fake secret in D:\XM\kaipai-team\.sce\config\local-secrets\wechat-miniapp.env
- [ ] Live probe confirms /api/auth/wechat-login is blocked by missing miniapp appId/appSecret: 微信登录未配置小程序 appId/appSecret

## Next Actions

- [ ] 在目标前端运行时启用并验证 `VITE_ENABLE_WECHAT_AUTH=true`。
- [ ] 按 `00-29` 标准流程补齐并验证远端 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`。
- [ ] 补一组真实微信老用户登录样本和一组自动注册 + inviteCode 样本。
- [ ] 正式闭环前替换开发态直返验证码口径，避免把开发态 sendCode 误判成正式短信能力。

## Output Files

- captures/capture-results.json
- captures/live-probe-sendCode.json (if live probe enabled)
- captures/live-probe-wechat-login.json (if live probe enabled)
- runtime-summary.md
- sample-ledger.md
- validation-report.md
