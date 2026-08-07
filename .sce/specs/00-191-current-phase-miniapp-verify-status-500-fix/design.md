# 00-191 当前阶段小程序实名状态 500 修复 - 技术设计

## 1. 设计结论

历史修复已发布后，2026-07-27 又收到至少三次相同的通用 500 响应。由于用户未提供 URI、时间或请求关联码，本设计不把它直接归因为历史 `/api/verify/status` schema 问题；本轮在保留历史实名默认态修复的基础上，补齐“可关联、少请求、可重试”的防复发闭环。

本轮做五处窄改：

```text
kaipaile-server IdentityVerificationServiceImpl.currentStatus()
  -> 先读取 user.realAuthStatus 形成默认响应
  -> 查询最新 identity_verification 记录
  -> 查询成功且有记录：返回记录态
  -> 查询失败或无记录：返回默认响应，不抛出 500

kaipaile-server GlobalExceptionHandler
  -> 未处理异常生成 INTERNAL_ERROR_<32 uppercase hex>
  -> ERROR 日志使用同一关联码记录 method / URI / throwable
  -> 响应只返回非敏感关联码，不泄露根因

kaipai-frontend stores/user + pkg-card/verify/index
  -> Store 读取实名状态后返回同一 status，并提供 applyVerificationStatus(status)
  -> 实名页 hydration 只经 Store 读取一次，关闭请求层默认 toast
  -> 页面拥有 loading / local error / retry；成功提交直接应用 submit 响应

kaipai-frontend pages/mine/index
  -> 当前 00-199 结构直接用 hasStoredSession / currentUser 渲染账号头部
  -> 任何附属请求只进入页面局部错误态，不得改变登录身份

kaipaile-server verify provider cleanup
  -> submit 只保留 RealNameVerificationProvider
  -> 删除旧 TencentIdCardVerificationClient 二次调用
  -> DTO / Entity 统一使用 providerCode/providerResultMessage 等 canonical 字段
```

runbook runtime diagnostics
  -> 远端 helper 与本地落盘均按安全白名单脱敏
  -> Docker 时间窗把 d 归一化为 h，grep 使用正则并保留失败时的部分证据

_Requirements: 3.1, 3.2, 3.4, 3.5, 3.6_

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

该容错只覆盖“读取最新实名记录”这一层，避免历史表结构或记录异常把状态查询打成 500。catch 使用 WARN 记录 `userId` 与 throwable，不记录真实姓名、身份证号或记录全文。提交实名、审核实名仍保持原异常行为，不做吞错。

`toStatusResp()` 与 `adminDetail()` 的身份证展示值只接受 `IdCardCryptoSupport.mask()` 生成的 canonical 格式（前三位 + 11 个 `*` + 后四位）。缺失或格式异常时返回 `null`；禁止从 `idCardNoCipher` 回退，因为该字段可能是 AES-GCM 密文或 `sha256:` 稳定哈希。`IdentityVerificationDetailRespDTO` 与管理端 `VerifyDetail` 物理删除 `idCardNoCipher`，任何前端都不得承担密文脱敏职责。

_Requirements: 3.1_

### 2.4 全局未处理异常关联

`GlobalExceptionHandler.handleException(...)` 为每次未处理异常生成：

```text
INTERNAL_ERROR_<UUID 去掉连字符后转为大写>
```

日志必须使用结构化且固定的上下文：关联码、HTTP method、URI、throwable。响应继续复用 `R.fail(ResultCode.FAILED, errorCode)`，只暴露固定消息与关联码。

不把关联码塞入异常信息或根据用户数据派生，避免成为可猜测的身份标识。既有业务异常、参数异常和授权异常的既定响应不在本次改动范围内。

_Requirements: 3.5_

## 3. 前端设计

### 3.1 Mine 当前账号头部合同

00-191 的旧 `applyMineUserHeader` 结构已由 00-199 退场。当前 `pages/mine/index.vue` 直接依赖全局 `hasStoredSession / currentUser` 判断并渲染账号头部；`hydrateMinePage()` 只负责职业资料摘要等页面数据。

```text
hasStoredSession + currentUser
  -> 已登录账号头部
hydrateMinePage()
  -> 附属资料请求
  -> 本地 catch：设置局部错误，不清空 session
```

_Requirements: 3.2_

### 3.2 附属同步失败归属

当前 Mine 页面不调用 `syncActorRuntimeState()`。若未来重新引入附属同步，则它必须被页面局部 catch 包裹，且不能修改 `hasStoredSession / currentUser`、调用 `logout()` 或将头部切换为游客态。

_Requirements: 3.2_

### 3.3 实名页单次状态读取

`stores/user.ts` 增加两个明确的职责：

```ts
function captureActorSession(): ActorSessionSnapshot | null
function applyVerificationStatus(status: IdentityVerification, expectedSession: ActorSessionSnapshot): boolean
async function syncVerificationStatus(options?: ActorRuntimeSyncOptions): Promise<IdentityVerification | null>
async function syncLevelInfo(options?: ActorRuntimeSyncOptions): Promise<UserLevelInfo | null>
```

`syncVerificationStatus()` 只负责读取并调用 `applyVerificationStatus()`；无会话或非演员返回 `null`。请求选项允许透传 `showLoading / showError`，以便页面在自己拥有局部状态时关闭全局 UI。

所有会把异步响应写回用户态的实名页链路共享演员会话快照：请求发出前捕获 `token + userId`，响应返回后再次校验 token、userId 与 Actor 角色。`applyVerificationStatus(status, expectedSession)` 只有在快照仍有效时才写 Store 并返回 `true`；`syncVerificationStatus()` 与 `syncLevelInfo()` 在无会话或响应过期时返回 `null`。实名提交也必须携带同一快照，先通过 Store 的条件应用，再更新页面本地状态。这样账号 A 的 GET/POST 不会在账号 B 登录后落入 B 的持久化用户态。

Store 会话快照同时包含单调递增的 `sessionRevision`，并校验持久化 token。登录、显式退出、Storage hydration 与自动 401 清理都会推进 revision，避免并发成功响应在 401 后重新持久化旧用户。

请求层另在 `utils/auth.ts` 维护 `AuthSessionSnapshot(token + auth revision)`。每个请求发出时捕获该快照；401 只有在快照仍属于当前 auth session 时才通过 `clearSession(expectedSession)` 同步清空 Storage 与 Pinia，并在清理成功后跳转登录。账号 A 的旧 401 晚于账号 B 登录到达时，token 或 auth revision 已变化，清理返回 `false`，不得影响 B。Store revision 管理异步数据写回所有权，auth revision 管理请求层 401 副作用所有权，两者职责独立。

`bootstrapSession()` 的共享 Promise 与发起时的 token + revision 绑定；响应或异常返回时若会话已经变化则静默丢弃。只有仍属于发起会话的成功响应才能以原 request token 调用 `setUserData()`，不得读取响应时刻的 `token.value`。

`pkg-card/verify/index.vue` 的状态流：

```text
onShow -> hydratePage()
  -> loading = true; loadError = ''
  -> ensureUserSessionReady()
  -> syncVerificationStatus({ showLoading: false, showError: false })  [唯一 GET]
  -> 返回 status：页面表单 / 状态卡复用它
  -> syncLevelInfo({ showLoading: false, showError: false })
  -> catch：loadError = 含非敏感关联码的页面文案
  -> finally：loading = false

submitVerify()
  -> 请求前捕获 actor session snapshot
  -> 返回 submit status
  -> applyVerificationStatus(status, snapshot) [无第二个 GET]
  -> snapshot 失效：不写 Store、不写页面，显示会话变化后的重载状态
```

档案完成度读取独立调用 `syncLevelInfo()` 并直接消费其 `UserLevelInfo | null` 返回值；不能在 `null` 时继续读取 `userLevelInfo` 缓存并当作本次成功结果。完成度请求过期时，页面隐藏旧账号的实名状态并要求重新加载。

页面另维护 hydration、completion、submit 三类 generation。新 hydration 会使旧 generation 失效；每次本地状态写入、错误显示、loading 收尾和 session 失效 UI 前都先确认 generation 所有权。旧 generation 必须静默退出，不能影响已完成的新账号页面。

视觉边界：顶部 hero 和“认证前置检查”摘要固定；状态加载中或失败时，只有认证状态 / 表单区域被加载态或带“重新加载”命令的错误态替换。错误态显示关联码但不显示服务器异常细节。

_Requirements: 3.6_

### 3.4 运行时诊断证据安全

`read-backend-runtime-logs.py` 与 `kaipai-backend-release-helper.sh` 必须双层执行环境变量安全白名单：仅允许无敏感值的运行时键保留值，其他键只输出 `KEY=[REDACTED]`。即使远端 helper 出现缺段、非零退出或日志抓取失败，本地脚本也要先解析、再次脱敏并落盘已有部分证据，然后才返回失败。

Docker `--since` 只接受 Go duration，入口把合法 `Nd` 正规化成 `N*24h`；`--grep` 使用正则并对非法表达式明确失败。诊断摘要增加 Docker logging driver / options 的安全摘要，以区分“应用没有日志”和“日志驱动未保留”。

_Requirements: 00-29 R14.6, R16.2.1, R16.2.2, R16.2.3, R16.2.4_

## 4. 验证设计

新增脚本：

```text
.sce/specs/00-191-current-phase-miniapp-verify-status-500-fix/scripts/verify-miniapp-verify-status-500-fix.mjs
```

检查：

- `IdentityVerificationServiceImpl` 存在 `buildDefaultStatusResp(User user)`。
- `currentStatus()` 对 `selectLatestByUserId(userId)` 包裹 `try/catch`，异常返回默认响应。
- `pages/mine/index.vue` 使用 `hasStoredSession / currentUser` 渲染账号头部，且没有以 `syncActorRuntimeState()` 作为登录态前置。
- `pkg-card/verify/index.vue` 只通过 Store 读取实名状态，不再直接导入 `getVerifyStatus()`；`hydratePage()` 拥有 loading / catch / retry 形态。
- `stores/user.ts` 返回并应用一次读取到的实名状态，提交成功的页面路径不追加 status GET。
- `stores/user.ts` 对实名 GET、等级 GET 和实名提交应用统一执行请求前后演员会话校验；等级同步返回 `UserLevelInfo | null`。
- `GlobalExceptionHandler` 为兜底异常生成并记录非空关联码。
- `utils/auth.ts / utils/request.ts` 使用请求发起 auth snapshot 条件执行 401 清理；行为门禁覆盖旧账号 401 不清新账号，以及当前账号 401 正常清理。
- 后端主源码不再存在 `TencentIdCardVerificationClient / Properties / Result`。
- 后端 verify 实体 / DTO / 服务不再映射或读写 `verifyProvider/providerDescription`。

必须执行：

1. `node .sce/specs/00-191-current-phase-miniapp-verify-status-500-fix/scripts/verify-miniapp-verify-status-500-fix.mjs`
2. `cd kaipaile-server && mvn test "-Dtest=GlobalExceptionHandlerTest,IdentityVerificationServiceImplTest,TencentRealNameVerificationProviderTest"`
3. `cd kaipaile-server && mvn -q -DskipTests compile`
4. `cd kaipai-frontend && npm run type-check`
5. `cd kaipai-frontend && npm run build:mp-weixin`
6. `cd kaipai-frontend && npm run audit:mp-package`
7. `python -m unittest discover -s .sce/runbooks/backend-admin-release/scripts/tests -p "test_*.py" -v`

_Requirements: 3.3_
