# 本地微信配置输入检查

- Capture ID: `20260403-062919-invite-login-local-input-gate`
- Label: `invite-login-local-input-gate`
- Project appId: `wxd38339082a9cfa4e`
- Release Ready: `no`

## Local Env

- `WECHAT_MINIAPP_APP_ID` present: `no`
- `WECHAT_MINIAPP_APP_ID` preview: `--`
- `WECHAT_MINIAPP_APP_SECRET` present: `no`
- `WECHAT_MINIAPP_APP_SECRET` preview: `--`

## Dotenv Candidates

- `kaipai-frontend\.env`
  - `WECHAT_MINIAPP_APP_ID` present: `no`
  - `WECHAT_MINIAPP_APP_ID` preview: `--`
  - `WECHAT_MINIAPP_APP_SECRET` present: `no`
  - `WECHAT_MINIAPP_APP_SECRET` preview: `--`
- `kaipai-frontend\.env.example`
  - `WECHAT_MINIAPP_APP_ID` present: `no`
  - `WECHAT_MINIAPP_APP_ID` preview: `--`
  - `WECHAT_MINIAPP_APP_SECRET` present: `no`
  - `WECHAT_MINIAPP_APP_SECRET` preview: `--`
- `kaipai-admin\.env.development`
  - `WECHAT_MINIAPP_APP_ID` present: `no`
  - `WECHAT_MINIAPP_APP_ID` preview: `--`
  - `WECHAT_MINIAPP_APP_SECRET` present: `no`
  - `WECHAT_MINIAPP_APP_SECRET` preview: `--`

## Conclusion

- current result: local machine still does not provide a complete `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET` input pair
- extra fact: frontend project config already fixes the mini-program appId, but this is not enough to open the backend WeChat gate
- next step: obtain the legal appSecret source first, then export local env vars and continue `00-29` sync flow
