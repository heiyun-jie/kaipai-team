# 00-191 当前阶段小程序实名状态 500 修复 - 任务拆解

## T1 Spec 与根因定位

- [x] 新增 `00-191` requirements / design。
- [x] 定位 `pages/mine/index -> userStore.syncActorRuntimeState() -> getVerifyStatus() -> GET /api/verify/status` 请求链。
- [x] 定位后端 `IdentityVerificationServiceImpl.currentStatus()` 在查询最新实名记录时可能受 `identity_verification` 历史字段 / 迁移漂移影响而抛出 500。

## T2 红灯验收

**Validates: Requirements 3.1, 3.2, 3.3**

- [x] 新增 `scripts/verify-miniapp-verify-status-500-fix.mjs`。
- [x] 实现前执行脚本，确认后端默认态兜底和个人中心容错检查失败。
- [x] 新增 `IdentityVerificationServiceImplTest` 回归用例，覆盖最新实名记录查询异常时返回用户表实名默认状态。

## T3 后端接口修复

**Validates: Requirements 3.1**

- [x] 修改 `IdentityVerificationServiceImpl.currentStatus()`，先读取用户表并构造默认响应。
- [x] 新增 `buildDefaultStatusResp(User user)`，默认 `status` 来自 `user.realAuthStatus`，空值回落为 `0`。
- [x] 只对最新实名记录读取链路做 `RuntimeException` 兜底；提交、审核、通过、拒绝等写链路保持原异常行为。

## T4 数据库兼容补迁移

**Validates: Requirements 3.1**

- [x] 新增 `V20260705_001__identity_verification_status_compat.sql`。
- [x] 对 `identity_verification` 的脱敏身份证号、provider 结果字段和 provider 索引做 `information_schema` 条件补齐。
- [x] 回填 `id_card_no_masked`，兼容历史已存在记录。
- [x] 复查旧 `verify_provider / provider_description` 字段，确认不继续补旧列，改为清理旧 provider 代码残留。

## T5 个人中心容错

**Validates: Requirements 3.2**

- [x] 修改 `kaipai-frontend/src/pages/mine/index.vue`，`bootstrapSession()` 成功后立即渲染账号头部。
- [x] 将 `syncActorRuntimeState()` 失败归属到数据区错误提示，不再阻断已登录账号头部展示。
- [x] 保持游客态个人中心可浏览，不触发实名状态接口。

## T6 旧实名 provider 残留清理

**Validates: Requirements 3.4**

- [x] 将 00-191 验收脚本扩展为检查旧 `TencentIdCardVerification*` 和 `verifyProvider/providerDescription` 残留。
- [x] 先运行脚本并确认旧 provider 残留检查失败。
- [x] 删除 `IdentityVerificationServiceImpl.applyProviderVerification(...)` 旧二次调用链。
- [x] 删除 `TencentIdCardVerificationClient / Properties / Result` 三个旧类。
- [x] 删除 `IdentityVerification` 的 `verifyProvider / providerDescription` 映射。
- [x] 后台实名列表 DTO 改为 `providerCode`，详情 DTO 只保留 canonical provider 字段。

## T7 构建与验收

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [x] 执行 00-191 专项验收脚本。
- [x] 执行 `mvn test "-Dtest=IdentityVerificationServiceImplTest,TencentRealNameVerificationProviderTest"`。
- [x] 执行 `mvn -q -DskipTests compile`。
- [x] 执行 `npm run type-check`。
- [x] 执行 `npm run build:mp-weixin`。
- [x] 执行 `npm run audit:mp-package`。
- [x] 执行 00-187 / 00-188 / 00-190 小程序复审相关专项脚本。
- [x] 更新 `.sce/specs/README.md` 与 `.sce/specs/spec-code-mapping.md`。
