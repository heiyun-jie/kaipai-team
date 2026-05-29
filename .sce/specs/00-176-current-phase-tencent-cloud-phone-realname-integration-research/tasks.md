# 00-176 任务

## Phase 1: Existing Specs

- [x] 阅读 `.sce/README.md`、`CURRENT_CONTEXT.md`、`.sce/specs/README.md`。
- [x] 阅读 `00-51` 正式短信能力降级 Spec。
- [x] 阅读 `00-173` 微信手机号一键登录 Spec。
- [x] 阅读 `00-174` 验证码登录页审核门禁 Spec。
- [x] 阅读 `05-09` 实名认证 Spec。

## Phase 2: Current Code Facts

- [x] 核对 `/api/auth/sendCode` 当前实现。
- [x] 核对 `/api/verify/status` 与 `/api/verify/submit` 当前实现。
- [x] 核对后台实名认证审核接口当前实现。
- [x] 核对实名认证表结构与身份证哈希 / 脱敏存储现状。

## Phase 3: Tencent Cloud Research

- [x] 查询腾讯云短信 SMS 官方文档。
- [x] 查询腾讯云实名核身身份证二要素 / 手机号三要素官方文档。
- [x] 查询腾讯云实名核身小程序 / 人脸核身官方文档。
- [x] 区分 SMS、号码认证、实名核身手机号要素核验的适用边界。

## Phase 4: Documentation

- [x] 生成 `requirements.md`。
- [x] 生成 `design.md`。
- [x] 生成 `tasks.md`。
- [x] 生成 `tencent-cloud-phone-realname-investigation.md`。
- [x] 生成 `execution.md`。

## Acceptance

- [x] 文档说明当前项目事实与腾讯云能力之间的对应关系。
- [x] 文档列出推荐接入路线。
- [x] 文档列出配置、数据安全、合规和验证门禁。
- [x] 本轮不改运行时代码。

