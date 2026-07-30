# 00-191 当前阶段小程序实名状态 500 修复 - 执行记录

> **分期说明**：从“执行摘要”到“发布说明”记录 2026-07-05/06 的首次 `/api/verify/status` schema 兼容、代码修复与生产发布闭环，其中 Mine helper 和当时的全绿结果属于历史运行态。2026-07-27 的同类通用 500 复发、当前 00-199 后 Mine 结构、本轮实现和最新验证矩阵见文末；不得用历史结果替代当前工作树结论。

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

## 2026-07-27 同类通用 500 复发标记

### 已有记录核对

本次没有创建新的重复 Spec。用户提供的响应与本 Spec 的历史现象一致：

```json
{"code":500,"message":"操作失败","errorCode":null,"data":null}
```

历史 `/api/verify/status` 根因、兼容迁移和回归链路仍由 00-191 管理；以下发布记录证明当时不是“只改本地未发布”：

- `.sce/runbooks/backend-admin-release/records/20260706-100844-backend-schema-verify-status-compat.md`
- `.sce/runbooks/backend-admin-release/records/20260706-101421-backend-only-verify-status-500-fix-manual-completion.md`

记录显示 2026-07-06 已完成 schema / 后端发布，登录态生产 smoke 返回 `code=200`。

### 本次状态

- **复发次数标记**：用户确认至少 3 次。
- **当前归因状态**：待关联码确认。用户没有提供请求 URI、发生时间、HTTP method 或服务端关联码，不能严谨地把本次响应直接认定为 `/api/verify/status` 的历史 schema 根因复发。
- **已定位的系统性缺口**：`GlobalExceptionHandler` 将所有未处理异常统一转换为 `R.fail(ResultCode.FAILED)`，该重载不填 `errorCode`，所以不同端点和根因都会返回同一个不可追溯 JSON。
- **本轮处理目标**：新增非敏感关联码和服务端日志关联；收口实名页重复 `/api/verify/status` 请求；把运行时诊断的环境变量输出改为双层脱敏并保证失败时仍保留安全证据。

### 运行时只读诊断边界

本轮曾按 00-29 的只读诊断入口请求最近时间窗日志。Docker 对 `--since 30d` 不接受 `d` 单位，`1h / 15m` 可以执行但返回日志为空，未能还原用户本次错误。未修改远端任何配置、容器、数据库或发布状态。

原诊断 helper 会原样输出容器环境变量，存在敏感配置泄露风险；本轮后续改为仅在本地代码和测试中修复，任何新的诊断证据必须经远端和本地双层脱敏后才可落档。

## 2026-07-27 本轮实现与防复发闭环

### 当前 Mine 边界

00-199 重构后，`pages/mine/index.vue` 已不再调用 `syncActorRuntimeState()`，也不再维护 `profileUser / applyMineUserHeader / analyticsError`：

- `isVisitor = !userStore.hasStoredSession`、`currentUser = userStore.currentUser` 直接派生账号头部。
- `displayName / avatar / accountMeta` 均为 computed，不保存页面级账号副本。
- `openAccountCapability()` 负责游客和角色门禁。
- `hydrateMinePage()` 只加载职业资料摘要；失败只写 `hubError`，不清空或覆盖全局 session。

因此本轮没有恢复 2026-07-05/06 的旧 Mine helper，只把当前等价语义纳入 00-191 / 00-192 门禁。

### 后端可定位与窄范围降级

- `GlobalExceptionHandler` 对每次未处理异常返回 `INTERNAL_ERROR_<32 位大写十六进制>`，响应仍固定为 `code=500 / message=操作失败 / data=null`。
- ERROR 日志使用同一关联码记录 HTTP method、无 query 的 URI 与原始 throwable；响应不暴露异常类名、SQL、堆栈或隐私字段。
- `IdentityVerificationServiceImpl.currentStatus()` 仅对最新实名记录查询异常回落到 `user.realAuthStatus`，并以 WARN 记录 `userId / fallbackStatus / throwable`；用户查询、提交和审核异常仍交由全局处理。
- `toStatusResp()` 与 `adminDetail()` 只接受 canonical masked 身份证号；缺失、`sha256:`、cipher 或非法 masked 值返回 `null`。后端详情 DTO、管理端类型和页面均已删除 `idCardNoCipher` 展示合同。
- `IdentityVerificationServiceImplTest` 已修正错误 Mapper 重载 mock，并覆盖非零 fallback、无记录默认态和正常记录完整映射；`GlobalExceptionHandlerTest` 覆盖关联码格式、唯一性、固定响应与日志同码。

### 实名页请求与跨会话保护

- `pkg-card/verify/index.vue` 一次 hydration 只经 Store 发起一次实名状态 GET，页面拥有 loading、局部错误、关联码展示与重试。
- 实名状态成功后立即渲染；档案完成度由独立 `hydrateProfileCompletion()` 加载、报错和重试，等级接口失败不再遮蔽有效实名状态或重发实名 GET。
- 提交成功直接消费 POST 响应，不追加 `/api/verify/status` GET，也不会把后续读取失败误报成提交失败。
- `stores/user.ts` 通过 `ActorSessionSnapshot(token + userId + session revision)` 绑定请求发起会话，并同时校验 Pinia 与 Storage 的 token、userId、Actor 角色；实名 GET、等级 GET、邀请统计 GET 和实名提交 POST 的旧响应返回 `null` 或拒绝应用。
- `syncLevelInfo()` 返回 `UserLevelInfo | null`；页面直接消费本次返回值，不能把 Store 旧缓存误认为本次请求成功。stale 结果会隐藏旧账号实名内容并进入“登录状态已变化”的重载状态。
- `bootstrapSession()` 的共享 Promise 与发起 token + Store revision 绑定；旧成功不得形成“用户 A + token B”，旧异常不得退出新账号。
- `utils/auth.ts / utils/request.ts` 通过 `AuthSessionSnapshot(token + auth revision)` 条件执行 401 清理：当前请求的 401 先原子清 Storage 与 Pinia 再跳登录，账号 A 晚到的旧 401 不得清账号 B 或触发跳转。
- 实名页为 hydration、completion、submit 分别维护 generation；新 hydration 会使旧 generation 失效，旧成功、失败和 finally 均静默退出，不能修改新账号的 loading、错误或状态。

### 运行时诊断安全

- `read-backend-runtime-logs.py`、`run-backend-compose-env-sync.py` 和 `kaipai-backend-release-helper.sh` 对容器 env、Compose source/rendered 与本地记录执行等价白名单脱敏。
- 仅 `SPRING_PROFILES_ACTIVE / NACOS_ENABLED / SERVER_PORT` 可在严格值校验通过后保留；其他键统一输出 `[REDACTED]`，完整 `docker compose config` 不进入 stdout 或记录。
- `Nd` 时间窗正规化为 `Nh`；非法 duration / regex 在远端访问前失败；helper 非零退出时仍保存已脱敏的部分证据。
- Docker logging driver/options 只记录安全摘要。Bash 与 Python 两套 sanitizer 的未来漂移仍是残余维护风险。

## 2026-07-27 最新本地验证

先扩展 00-191 静态门禁，401 内存态清理、bootstrap 所有权、页面 generation 和身份证 cipher/hash 零暴露共出现 4 个预期红灯；身份证测试还明确得到 `expected null / actual sha256:stable-internal-identity-hash`。实现后又经独立终审发现“账号 A 旧 401 清理账号 B”的请求层副作用缺口，补入 auth snapshot 与延迟 Promise 交错回归后，专项门禁最终为 `17/17 PASS`。

当前绿灯：

- 后端定向 Maven：`GlobalExceptionHandlerTest + IdentityVerificationServiceImplTest + TencentRealNameVerificationProviderTest`，`16 tests / 0 failures / 0 errors`；新增用户查询异常不降级吞错与后台详情 masked-only 边界测试。
- 后端 `mvn -q -DskipTests compile`：通过。
- runbook unittest：`22/22 PASS`，其中 `test_backend_runtime_diagnostics.py` 为 10 个诊断脱敏与失败证据用例。
- Python `py_compile` 与 Bash helper `bash -n`：通过。
- 小程序 `npm run type-check` 与 `npm run build:mp-weixin`：通过；postbuild 已同步到固定 `dist/dev/mp-weixin`。
- 管理端 `npm run type-check`、`npm run build` 与 Admin dist URL sanitizer：通过。
- `00-191`：`17/17 PASS`；`00-192`：`10/10 PASS`；`00-187`：`15/15 PASS`；`npm run audit:steering`：通过。
- `dist/build/mp-weixin/pkg-card/verify` 与 `dist/dev/mp-weixin/pkg-card/verify` 均包含状态 loading/error/retry、档案完成度独立 error/retry、关联码和会话变化重载逻辑；对应 WXML、WXSS、JS 哈希逐项一致。

当前非绿门禁按最新工作树如实保留：

- `00-188`：1 项失败。`dist/build` 与源码为 `urlCheck=true`，但 postbuild 检测本地 API 后明确把固定 DevTools 目录的 `dist/dev/project.config.json` 改为 `urlCheck=false`。
- `00-190`：9 项失败。旧脚本仍断言已由 00-199 退场的 `requireLoginForMineAction / mine-page__login-card / showMineContent / analytics / quick-grid / settings` 结构；源码、build、dev 各 3 项。当前 Mine 等价语义已由 00-192 的 10 项门禁覆盖，不为旧脚本恢复退场结构。
- `npm run audit:mp-package`：在首个命中的 `dist/build/mp-weixin/api/actor-asset.js:1` 失败，原因是并行工作构建注入 `http://127.0.0.1:8010`。审计首错即停，因此这里只记录首个已知阻断，不宣称已穷尽其他外链。

### 未执行边界

- 本轮未发布、未重启、未修改远端配置或数据库，也未重新执行生产 helper / 生产 smoke。
- 2026-07-06 历史修复曾完成生产发布且当时 smoke 为 `code=200`；2026-07-27 新增关联码、页面收口与诊断防护仍只存在于当前本地工作树。
- 本次用户提供的 JSON 仍缺少 URI、时间、method 和关联码，具体端点与原始异常继续标记为“待未来关联码确认”，不能宣称生产问题已定位或已消失。
