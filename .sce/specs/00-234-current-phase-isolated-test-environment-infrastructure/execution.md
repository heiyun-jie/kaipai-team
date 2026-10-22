# 00-234 隔离测试环境基础设施 - 执行记录

## 当前签收状态

- Candidate: `20260826-1625-v3-draft`
- Manifest SHA256: `7282a9bb75e8d05d80b299e91a96dfa8735854220b8ab48246f95937bc19b9a1`
- Status: `PASSED / INFRA_READY`
- Observed: `2026-08-27 10:51 +0800`
- Evidence: `.sce/evidence/20260827-test-full-access/dual-env-preflight.log`
- Switch verification: `.sce/evidence/20260827-test-full-access/VERIFICATION.txt`
- Evidence SHA256: `7fb71b574c2926f3b0e1aa1eaefaa06aff92fb1bef213cc6c58a3de31dbff0ad`

## 已验证运行态

1. `test-api.kplyyk.com` 与 `test.kplyyk.com` 均解析到 `101.43.57.62`，受信任 TLS 生效。
2. `https://test-api.kplyyk.com/api/v3/api-docs` 和 `https://test.kplyyk.com` 均返回 `HTTP 200`。
3. `kaipai-backend-test` 在 `18080` 运行，Nacos test dataId 指向 `kaipai_test`。
4. 正式 `kaipai-backend` 继续在 `8080` 运行，`restartCount=0`，本轮未停止、未重建、未迁移。
5. test/prod 分别使用 `kaipai_test` / `kaipai_prod`；测试数据库账号对生产 schema 权限计数为 `0`。
6. Redis 使用 DB `1`，COS 使用 `kaipai-test-1412601014`，测试短信采用开发态固定验证码能力。
7. 测试管理端来自独立 test 静态目录；小程序冻结测试产物只包含 test API。
8. 不带 `--allow-fail` 的 `check-dual-env-preflight.py` 返回 `passed=true`。

## 遗留人工确认

- 微信公众平台中的 request/upload/download 合法域名无法从当前服务器或仓库事实源独立回读，体验版发布前需由平台账号侧确认。
- 当前固定微信开发者工具工程可用于人工测试；2026-08-27 10:51 MCP 会话提示需要重新登录，登录后刷新即可，不需要重新构建或切换目录。

## 结论

`00-234` 已达到 `INFRA_READY`，并已进入 `00-235` 数据兼容验证。此结论不代表正式发布授权。
