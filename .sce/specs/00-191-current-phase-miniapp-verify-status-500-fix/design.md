# 00-191 当前阶段小程序实名状态 500 修复 - 技术设计

## 1. 设计结论

本轮做三处窄改：

```text
kaipaile-server IdentityVerificationServiceImpl.currentStatus()
  -> 先读取 user.realAuthStatus 形成默认响应
  -> 查询最新 identity_verification 记录
  -> 查询成功且有记录：返回记录态
  -> 查询失败或无记录：返回默认响应，不抛出 500

kaipai-frontend pages/mine/index
  -> bootstrapSession 成功后立即渲染账号头部
  -> syncActorRuntimeState 作为附属同步，失败进入 analyticsError/toast
  -> 不让实名状态接口失败阻断个人中心基础展示

kaipaile-server verify provider cleanup
  -> submit 只保留 RealNameVerificationProvider
  -> 删除旧 TencentIdCardVerificationClient 二次调用
  -> DTO / Entity 统一使用 providerCode/providerResultMessage 等 canonical 字段
```

_Requirements: 3.1, 3.2, 3.4_

## 2. 后端设计

### 2.1 默认响应 helper

在 `IdentityVerificationServiceImpl` 新增：

```java
private IdentityVerificationStatusRespDTO buildDefaultStatusResp(User user)
```

逻辑：

- `status = user == null || user.getRealAuthStatus() == null ? 0 : user.getRealAuthStatus()`
- 其他字段保持空值。

_Requirements: 3.1_

### 2.3 旧 provider 残留清理

`IdentityVerificationServiceImpl.submit()` 原先同时执行：

```text
verifyRealName(...) -> RealNameVerificationProvider
applyProviderResult(...)
applyProviderVerification(...) -> TencentIdCardVerificationClient
```

这会让 00-178 后的 canonical provider 状态机和旧 `IdCardVerification` 客户端并存，并继续写 `verifyProvider/providerDescription` 旧字段。当前设计改为：

```text
verifyRealName(...) -> RealNameVerificationProvider
applyProviderResult(...)
save(record)
```

同步约束：

- 删除 `TencentIdCardVerificationClient / Properties / Result` 旧类。
- `IdentityVerification` 实体不再映射 `verifyProvider`、`providerDescription`。
- 列表 DTO 使用 `providerCode`，详情 DTO 只保留 `providerCode / providerRequestId / providerResultCode / providerResultMessage / providerVerifiedAt`。
- 不新增 `verify_provider`、`provider_description` 兼容列，避免把旧合同重新固化进生产 schema。

_Requirements: 3.4_

### 2.2 currentStatus 容错

`currentStatus(Long userId)` 改为：

```text
user = userMapper.selectById(userId)
defaultResp = buildDefaultStatusResp(user)
try latestRecord = selectLatestByUserId(userId)
catch RuntimeException -> return defaultResp
if latestRecord == null -> return defaultResp
return toStatusResp(latestRecord)
```

该容错只覆盖“读取最新实名记录”这一层，避免历史表结构或记录异常把状态查询打成 500。提交实名、审核实名仍保持原异常行为，不做吞错。

_Requirements: 3.1_

## 3. 前端设计

### 3.1 账号头部先渲染

在 `pages/mine/index.vue` 新增本地 helper：

```ts
function applyMineUserHeader(user: UserInfo): void
```

`hydrateMinePage()` 调整顺序：

```text
bootstrapSession()
  -> null: resetVisitorMinePage()
  -> user: applyMineUserHeader(user)
  -> crew: 清空数据后返回
  -> actor: try syncActorRuntimeState()
              catch set analyticsError + toast
            try 并行加载 profile/share/history/contact
```

_Requirements: 3.2_

### 3.2 附属同步失败归属

`syncActorRuntimeState()` 失败后：

- 不 throw 到 `hydrateMinePage()` 顶层。
- 设置 `analyticsError` 为接口错误文案，例如「操作失败」。
- 继续保留账号头部。
- 后续 profile/share/history/contact 是否继续请求以最小风险为准：可以在同步失败后直接返回，也可以继续加载；本轮优先避免额外请求风暴，采用“设置数据区错误后返回”。

_Requirements: 3.2_

## 4. 验证设计

新增脚本：

```text
.sce/specs/00-191-current-phase-miniapp-verify-status-500-fix/scripts/verify-miniapp-verify-status-500-fix.mjs
```

检查：

- `IdentityVerificationServiceImpl` 存在 `buildDefaultStatusResp(User user)`。
- `currentStatus()` 对 `selectLatestByUserId(userId)` 包裹 `try/catch`，异常返回默认响应。
- `pages/mine/index.vue` 存在 `applyMineUserHeader(...)`。
- `pages/mine/index.vue` 中账号头部更新出现在 `syncActorRuntimeState()` 之前。
- `pages/mine/index.vue` 的运行态同步有本地 `try/catch`，不再裸 `await userStore.syncActorRuntimeState()`。
- 后端主源码不再存在 `TencentIdCardVerificationClient / Properties / Result`。
- 后端 verify 实体 / DTO / 服务不再映射或读写 `verifyProvider/providerDescription`。

必须执行：

1. `node .sce/specs/00-191-current-phase-miniapp-verify-status-500-fix/scripts/verify-miniapp-verify-status-500-fix.mjs`
2. `cd kaipaile-server && mvn test "-Dtest=IdentityVerificationServiceImplTest,TencentRealNameVerificationProviderTest"`
3. `cd kaipaile-server && mvn -q -DskipTests compile`
4. `cd kaipai-frontend && npm run type-check`
5. `cd kaipai-frontend && npm run build:mp-weixin`
6. `cd kaipai-frontend && npm run audit:mp-package`

_Requirements: 3.3_
