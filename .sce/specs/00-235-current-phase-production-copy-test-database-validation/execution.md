# 00-235 生产副本测试库迁移验证 - 执行记录

## 当前签收状态

- Candidate: `20260826-1625-v3-draft`
- Manifest SHA256: `7282a9bb75e8d05d80b299e91a96dfa8735854220b8ab48246f95937bc19b9a1`
- Status: `PASSED / TEST_DATA_READY`
- Observed: `2026-08-27 10:45 +0800`
- Evidence: `.sce/evidence/20260827-test-full-access/VERIFICATION.txt`
- Evidence SHA256: `7fb71b574c2926f3b0e1aa1eaefaa06aff92fb1bef213cc6c58a3de31dbff0ad`

## 数据与权限断言

- 测试运行账号：`USER_EXISTS=1`、`TEST_SCHEMA_PRIVILEGES=4`、`PROD_SCHEMA_PRIVILEGES=0`。
- 历史 URL：非空计数 `13`；迁移前后聚合 SHA256 保持 `52061548210b455002e137e3f682b65a2087ffac53108a8720763f23849f22b1`。
- 历史媒体 dry-run：扫描 `58`、可读 `58`、失败 `0`，生产来源桶指纹未变化。
- 首次回填：objects/assets/relations=`58/58/58`。
- 修复头像重复匹配后幂等重跑：objects/assets/relations 新建数均为 `0`。
- 最终迁移素材 `58`、普通资料关系 `55`、头像关系 `3`、孤儿素材 `0`。

## 合同与运行态

- 新账号自动 smoke 覆盖注册、会话、新资料、经历、素材、演员卡、背景库、分享、实名和导入能力，通过。
- 历史账号脱敏 smoke 覆盖登录、旧/新资料、经历、素材、演员卡与旧分享卡，通过。
- 后台全权限测试账号登录、session 和 7 页正式导航 API smoke 通过。
- `kaipai-backend-test` 回读运行端口为 `18080`，测试 API 公网 `HTTP 200`。
- 正式 `kaipai-backend` 继续在 `8080` 运行；本阶段未对 `kaipai_prod` 执行迁移或回填。

## 结论

`00-235` 达到 `TEST_DATA_READY`。数据兼容自动门禁已完成，下一阶段只允许人工验收；未获得用户明确 `GO` 前不得进入 `00-237`。
