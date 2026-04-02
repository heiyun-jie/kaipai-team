# Login Auth Validation Report

- Generated At: 2026-04-03T02:49:09
- Environment: dev

## Local Runtime Scan

- Frontend baseURL: http://101.43.57.62
- Frontend mock flag: false
- Frontend WeChat flag: false
- Admin baseURL: /api
- Server exposes WeChat placeholders: appId=True, appSecret=True

## Live Probe

- Probe baseURL: http://101.43.57.62
- sendCode: transport=200, code=200, message=验证码发送成功
- wechat-login: transport=200, code=500, message=微信登录未配置小程序 appId/appSecret

## Observations

- [x] Live probe confirms POST /api/auth/sendCode returns code=200 and still exposes a development verification code

## Blockers

- [ ] Frontend VITE_ENABLE_WECHAT_AUTH is not true; real WeChat path cannot be validated
- [ ] Live probe confirms /api/auth/wechat-login is blocked by missing miniapp appId/appSecret: 微信登录未配置小程序 appId/appSecret

## Manual Evidence To Add

- [ ] Login page screenshot
- [ ] Auth API capture
- [ ] user.me / verify / invite / level capture
- [ ] DB query result for user / referral_record
- [ ] WeChat error or success evidence when enabled

## Output Files

- captures/capture-results.json
- captures/live-probe-sendCode.json (if live probe enabled)
- captures/live-probe-wechat-login.json (if live probe enabled)
- runtime-summary.md
- sample-ledger.md
- validation-report.md
