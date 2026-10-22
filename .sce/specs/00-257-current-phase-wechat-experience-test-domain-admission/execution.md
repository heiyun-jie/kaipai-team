# 微信体验版测试域名准入修复 - 执行记录

## 2026-09-02

- Candidate：`20260902-145540-v3-draft`。
- 用户真机体验版、未登录状态进入素材库，页面显示 `request:fail url not in domain list`。
- 判定：请求被微信合法域名门禁拦截，尚未到达测试 API；本地 `urlCheck=false` 不能覆盖真机体验版。
- 当前状态：`BLOCKED_BY_WECHAT_DOMAIN_ADMISSION / IMPLEMENTING`。
- 目标变更：仅向共享 AppID 增加 `https://test-api.kplyyk.com` 的 request/upload/download 准入，保留全部已有域名。
- 正式发布：`NOT_AUTHORIZED`；生产运行时变更：`NONE`。
