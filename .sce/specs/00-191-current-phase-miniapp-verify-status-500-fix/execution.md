# 00-191 当前阶段小程序实名状态 500 修复 - 执行记录

## 执行摘要

已针对用户在 `pages/mine/index` 看到的生产接口错误完成本地代码修复：

```text
GET https://api.kplyyk.com/api/verify/status
{"code":500,"message":"操作失败","data":null}
```

本轮同时修复两层：

- 后端 `/api/verify/status`：最新实名记录查询失败时返回用户表实名默认状态，不再让附属记录读取导致 500。
- 小程序个人中心：登录会话恢复后先展示账号头部，实名 / 邀请 / 等级同步失败只影响数据区错误提示。
- 后端实名 provider：清理 00-178 后残留的旧 `TencentIdCardVerificationClient` 二次调用，统一回到 `RealNameVerificationProvider` 与 canonical provider 字段。

注意：`https://api.kplyyk.com` 是生产域名，本地修复只有在后端完成发布并执行兼容迁移后才会作用到该地址。

## 根因记录

请求链路：

```text
pages/mine/index
  -> hydrateMinePage()
  -> userStore.bootstrapSession()
  -> userStore.syncActorRuntimeState()
  -> syncVerificationStatus()
  -> getVerifyStatus()
  -> GET /api/verify/status
```

后端链路：

```text
VerifyController.currentStatus()
  -> IdentityVerificationServiceImpl.currentStatus(userId)
  -> selectLatestByUserId(userId)
  -> identity_verification selectOne
```

`currentStatus()` 原逻辑虽然在“无记录”时会返回 `status=0`，但它必须先成功查询 `identity_verification`。当生产库存在历史迁移缺列、字段半迁移、索引缺失或最新记录读取异常时，异常会在默认响应前抛出，并被全局异常处理成 `code=500,message=操作失败`。

前端同时存在体验问题：`pages/mine/index` 在账号头部渲染前先等待 `syncActorRuntimeState()`。因此实名状态接口一旦失败，页面仍可能显示「未登录用户」，与真实登录态不一致。

后续复查又发现一处遗留风险：

```text
IdentityVerificationServiceImpl.submit()
  -> verifyRealName(...) / RealNameVerificationProvider
  -> applyProviderResult(...)
  -> applyProviderVerification(...) / TencentIdCardVerificationClient
```

旧 `TencentIdCardVerificationClient` 使用 `IdCardVerification`，并写入 `verifyProvider/providerDescription` 旧字段；而 `00-178` 之后的迁移和后台回看已经以 `provider_code/provider_result_message/provider_verified_at` 为 canonical schema。若继续保留旧二次调用，要么生产库缺旧列导致写入失败，要么补旧列重新固化历史合同。最终处理策略是删除旧调用链和旧字段映射，不再补 `verify_provider/provider_description`。

## 红灯记录

实现前执行：

```powershell
node .sce\specs\00-191-current-phase-miniapp-verify-status-500-fix\scripts\verify-miniapp-verify-status-500-fix.mjs
```

结果：失败，符合预期。

失败项：

- `verify status service has default response helper`
- `verify status service catches latest record query failure`
- `mine page applies account header before actor runtime sync`
- `mine page catches actor runtime sync failure locally`

旧 provider 残留补充红灯：

```powershell
node .sce\specs\00-191-current-phase-miniapp-verify-status-500-fix\scripts\verify-miniapp-verify-status-500-fix.mjs
```

结果：失败，符合预期。

失败项：

- `verify submit uses the canonical realname provider only`
- `verify backend has no retired provider column mapping`

## 实现记录

后端修改：

- `kaipaile-server/src/main/java/com/kaipai/service/verify/impl/IdentityVerificationServiceImpl.java`
  - `currentStatus(Long userId)` 先读取 `userMapper.selectById(userId)`。
  - 新增 `buildDefaultStatusResp(User user)`。
  - `selectLatestByUserId(userId)` 包裹 `try/catch`，查询异常直接返回默认响应。
  - 查询成功且有实名记录时，继续返回 `toStatusResp(latestRecord)`，不改变已提交 / 已通过 / 已拒绝状态语义。
  - 删除旧 `applyProviderVerification(...)` 二次调用，`submit()` 只保留 `RealNameVerificationProvider` 状态机。
  - 后台列表 provider 字段改为 `record.getProviderCode()`。

旧 provider 残留清理：

- 删除：
  - `kaipaile-server/src/main/java/com/kaipai/integration/verify/TencentIdCardVerificationClient.java`
  - `kaipaile-server/src/main/java/com/kaipai/integration/verify/TencentIdCardVerificationProperties.java`
  - `kaipaile-server/src/main/java/com/kaipai/integration/verify/TencentIdCardVerificationResult.java`
- `kaipaile-server/src/main/java/com/kaipai/model/verify/entity/IdentityVerification.java`
  - 删除 `verifyProvider`。
  - 删除 `providerDescription`。
- `kaipaile-server/src/main/java/com/kaipai/model/verify/dto/IdentityVerificationListItemDTO.java`
  - 将 `verifyProvider` 改为 `providerCode`。
- `kaipaile-server/src/main/java/com/kaipai/model/verify/dto/IdentityVerificationDetailRespDTO.java`
  - 删除 `verifyProvider`。
  - 删除 `providerDescription`。
  - 保留 `providerCode / providerRequestId / providerResultCode / providerResultMessage / providerVerifiedAt`。

后端测试：

- `kaipaile-server/src/test/java/com/kaipai/module/server/verify/service/impl/IdentityVerificationServiceImplTest.java`
  - 新增 `currentStatusShouldFallbackToUserRealAuthStatusWhenLatestRecordQueryFails()`。
  - 模拟 `identityVerificationMapper.selectOne(...)` 抛出异常。
  - 验证返回 `status=0`，不向外抛错。

数据库兼容迁移：

- `kaipaile-server/src/main/resources/db/migration/V20260705_001__identity_verification_status_compat.sql`
  - 条件补齐 `id_card_no_masked`、`provider_code`、`provider_request_id`、`provider_result_code`、`provider_result_message`、`provider_verified_at`。
  - 条件补齐 `idx_identity_verification_provider_code` 与 `idx_identity_verification_provider_verified_at`。
  - 回填历史记录的 `id_card_no_masked`。
  - 使用 `information_schema + PREPARE` 写法，避免重复执行或半迁移状态导致 DDL 中断。
- `kaipaile-server/src/main/resources/db/migration/README.md`
  - 已登记本轮 `V20260705_001__identity_verification_status_compat.sql`，避免发布执行时遗漏该增量迁移。

前端修改：

- `kaipai-frontend/src/pages/mine/index.vue`
  - 新增 `applyMineUserHeader(user: UserInfo)`。
  - `bootstrapSession()` 成功后立即设置昵称、头像和基础城市信息。
  - `syncActorRuntimeState()` 使用本地 `try/catch`，失败时设置 `analyticsError` 并 toast，不再让 `hydrateMinePage()` 整体 reject。
  - 游客态继续停留个人中心并展示完整页面内容，不触发实名状态接口。

## 验证记录

已执行：

```powershell
node .sce\specs\00-191-current-phase-miniapp-verify-status-500-fix\scripts\verify-miniapp-verify-status-500-fix.mjs
```

结果：通过。

已执行：

```powershell
cd D:\XM\kaipai-team\kaipaile-server
mvn test "-Dtest=IdentityVerificationServiceImplTest,TencentRealNameVerificationProviderTest"
```

结果：通过，`Tests run: 9, Failures: 0, Errors: 0, Skipped: 0`。

已执行：

```powershell
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -DskipTests compile
```

结果：通过。

已执行：

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check
```

结果：通过。

已执行：

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run build:mp-weixin
```

结果：通过，postbuild 已同步到 `dist/dev/mp-weixin`。输出包含 uni-app 新版本提示、既有 Sass legacy JS API warning 与 empty chunk `types/project` warning。

已执行：

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run audit:mp-package
```

结果：通过。

```text
Total build size: 763.72 KB
main      524.48 KB / 2 MB
pkg-card  211.01 KB / 2 MB
pkg-tools 28.23 KB / 2 MB
```

已执行：

```powershell
node .sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs
node .sce\specs\00-188-current-phase-miniapp-review-compliance-audit-fix\scripts\verify-miniapp-review-compliance-audit.mjs
node .sce\specs\00-190-current-phase-miniapp-login-back-and-mine-review-supplement\scripts\verify-miniapp-login-back-and-mine-supplement.mjs
```

结果：全部通过。

已执行：

```powershell
git diff --check
git -C kaipai-frontend diff --check
git -C kaipaile-server diff --check
```

结果：通过；仅保留 Windows 工作区既有 LF/CRLF 提示。

## 发布说明

- 生产域名 `https://api.kplyyk.com/api/verify/status` 需要后端发布后才会变更行为。
- 发布时需要包含后端 JAR 与 `V20260705_001__identity_verification_status_compat.sql`。
- 若生产库已经完整执行过 `V20260529_001__tencent_realname_two_factor.sql`，本轮兼容迁移会走 `DO 0`，不会重复添加字段或索引。
- 本轮不会补 `verify_provider / provider_description` 旧列；若生产库已经存在旧列，代码不再读写它们，可作为后续数据库物理清理候选。
