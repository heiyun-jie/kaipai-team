# Login Auth Validation Sample Ledger

## Sample

- Environment: dev
- Sample Label: live-probe-ok3
- Validate At: 2026-04-03 02:49:09

## Runtime

- Backend Entry: http://101.43.57.62/api
- Spring Profile: dev
- NACOS_ENABLED: true
- WECHAT_MINIAPP_APP_ID: not verified on remote env; backend contract exists
- WECHAT_MINIAPP_APP_SECRET: not verified on remote env; backend contract exists
- Mini Program VITE_API_BASE_URL: http://101.43.57.62
- Mini Program VITE_USE_MOCK: false
- Mini Program VITE_ENABLE_WECHAT_AUTH: false
- Admin VITE_API_BASE_URL: /api

## Scenario

- Phone: 13800138000
- InviteCode: TESTINVITE
- Existing User: not verified in this sample
- Wechat Path: live probe only; no real WeChat authorization

## Evidence

- Login Page Screenshot:
- Runtime Blocker Screenshot:
- Auth Response Capture: captures/live-probe-sendCode.json, captures/live-probe-wechat-login.json
- user.me Capture:
- verify / invite / level Capture:
- DB Query Result:

## Conclusion

- Current Status: 局部完成
- Confirmed:
  - sendCode live probe returns transport 200 / payload code 200 and still exposes a development verification code
  - wechat-login live probe returns transport 200 / payload code 500 / message 微信登录未配置小程序 appId/appSecret
  - current mini-program runtime is not global mock fallback because VITE_USE_MOCK=false and the probe hits the real backend entry
- Blockers:
  - Mini-program runtime still sets VITE_ENABLE_WECHAT_AUTH=false, so the real WeChat button path is hidden
  - Remote runtime still lacks verified miniapp appId/appSecret, and wechat-login is blocked at business layer
  - No real WeChat existing-user / new-user sample has been captured yet
- Next Action:
  - enable and verify VITE_ENABLE_WECHAT_AUTH=true in the target runtime
  - configure and verify WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET on the remote environment
  - capture one real WeChat old-user login sample and one auto-register + inviteCode sample
