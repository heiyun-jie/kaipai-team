# 本地微信配置输入检查

- Capture ID: `20260403-064541-fake-secret-full-dryrun-local-input`
- Label: `fake-secret-full-dryrun-local-input`
- Project appId: `wxd38339082a9cfa4e`
- Release Ready: `yes`

## Local Env

- `WECHAT_MINIAPP_APP_ID` present: `no`
- `WECHAT_MINIAPP_APP_ID` preview: `--`
- `WECHAT_MINIAPP_APP_SECRET` present: `no`
- `WECHAT_MINIAPP_APP_SECRET` preview: `--`

## Secret File

- path: `tmp\wechat-secret-smoke\wechat-miniapp.env`
- exists: `yes`
- `WECHAT_MINIAPP_APP_ID` present: `yes`
- `WECHAT_MINIAPP_APP_ID` preview: `wxd38339082a9cfa4e`
- `WECHAT_MINIAPP_APP_SECRET` present: `yes`
- `WECHAT_MINIAPP_APP_SECRET` preview: `fa***un`

## Resolved Inputs

- `WECHAT_MINIAPP_APP_ID` present: `yes`
- `WECHAT_MINIAPP_APP_ID` source: `secret-file`
- `WECHAT_MINIAPP_APP_ID` preview: `wxd38339082a9cfa4e`
- `WECHAT_MINIAPP_APP_SECRET` present: `yes`
- `WECHAT_MINIAPP_APP_SECRET` source: `secret-file`
- `WECHAT_MINIAPP_APP_SECRET` preview: `fa***un`

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

- current result: local machine already resolves both appId and appSecret, can proceed to standard compose/Nacos sync
