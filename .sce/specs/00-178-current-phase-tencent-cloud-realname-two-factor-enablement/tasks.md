# 当前阶段腾讯云身份证二要素实名认证接入 Tasks

## Phase 1: Spec

- [x] 创建实现型 Spec。
- [x] 固化身份证二要素范围，不纳入三要素和人脸核身。

## Phase 2: Backend Provider

- [x] 新增实名 provider 配置、命令和结果模型。
- [x] 新增腾讯云 `IdCardOCRVerification` provider。
- [x] 新增 provider 单测并先跑出失败。
- [x] 实现 provider 并跑通单测。

## Phase 3: Submit State Machine

- [x] 新增 `identity_verification` provider 字段与脱敏字段 migration。
- [x] 扩展 `IdentityVerification` entity 和详情 DTO。
- [x] `submit` 接入 provider 自动通过 / 拒绝 / 人工兜底。
- [x] 新增 service 单测并跑通。

## Phase 4: Admin Visibility

- [x] 后台 verify 类型补 provider 字段。
- [x] 后台详情抽屉展示 provider 摘要。
- [x] 前端不直连腾讯云。

## Phase 5: Verification

- [x] 后端 provider 单测通过。
- [x] 后端 service 单测通过。
- [x] 后端 compile 通过。
- [x] 后台 / 小程序 type-check 通过。
- [x] 更新 execution 记录。
