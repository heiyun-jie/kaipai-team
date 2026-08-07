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

## T8 2026-07-27 同类通用 500 复发建档

**Validates: Requirements 3.2, 3.3, 3.5, 3.6**

- [x] 核对已有 Spec，确认 `00-191` 已精确记录历史 `GET /api/verify/status -> {code:500,message:操作失败}`，不重复创建同类 Spec。
- [x] 核对 2026-07-06 schema / 后端发布记录与登录态 smoke，标记历史修复已发布且当时返回 `code=200`。
- [x] 标记本次用户确认“至少 3 次”的同类通用响应；由于未提供 URI、时间或关联码，状态为“待关联码确认”，不把它直接归因为历史 schema 根因。
- [x] 定位通用响应来自 `GlobalExceptionHandler` 的 `R.fail(ResultCode.FAILED)`，确认 `errorCode=null` 是跨接口不可追溯的根因。

## T9 红灯回归与门禁更新

**Validates: Requirements 3.1, 3.2, 3.3, 3.5, 3.6**

- [x] 新增 `GlobalExceptionHandlerTest`，覆盖未处理异常返回非空、格式正确且每次不同的关联码，并验证同一关联码、method、URI 与 throwable 已进入 ERROR 日志。
- [x] 扩展 `IdentityVerificationServiceImplTest`：查询异常保留非零 `realAuthStatus`、无记录返回默认态、正常记录完整映射；同时修正旧用例对错误 Mapper 重载的 mock。
- [x] 更新 00-191 静态脚本：采用 00-199 当前 Mine 会话语义，新增实名页单次读取 / 局部错误态 / Store 复用检查。

## T10 后端与实名页复发收口

**Validates: Requirements 3.1, 3.5, 3.6**

- [x] `GlobalExceptionHandler` 生成非敏感关联码并以关联码、method、URI 和 throwable 记录 ERROR。
- [x] `IdentityVerificationServiceImpl.currentStatus()` 的既有查询回落增加不含实名信息的 WARN 日志。
- [x] `stores/user.ts` 新增 `applyVerificationStatus()`，使 `syncVerificationStatus()` 返回同一次读取的状态并支持页面关闭全局 loading / toast。
- [x] `pkg-card/verify/index.vue` 删除直接 `getVerifyStatus()`，一次 hydration 仅读取一次状态，补 loading / local error / retry，并在提交成功后直接应用响应。

## T11 运行时诊断防泄露与证据可靠性

**Validates: 00-29 R14.6, R16.2.1, R16.2.2, R16.2.3, R16.2.4**

- [x] 在远端 helper 和本地诊断入口同时实施环境变量白名单脱敏。
- [x] 对 `Nd` 时间窗正规化为 Docker 支持的 `Nh`，并让 `--grep` 使用可验证的正则匹配。
- [x] helper 失败时保留已脱敏的部分证据；记录安全的 Docker logging config 摘要。
- [x] 新增 Python 回归测试，防止 secret 值再次进入诊断产物或发布 helper 输出。

## T12 本轮验证与文档状态回填

**Validates: Requirements 3.1, 3.2, 3.3, 3.5, 3.6**

- [x] 执行 00-191 静态验收、后端定向测试、编译、小程序 type-check / 构建和诊断 Python 测试。
- [ ] 使 `npm run audit:mp-package` 通过；本轮已执行，但当前被既有 `src/api/actor-asset.ts` 构建出的 `http://127.0.0.1:8010` 命中阻断，本轮不覆盖该并行工作。
- [x] 复核 `dist/build` 与 `dist/dev` 均包含实名页局部状态区生成产物，且对应 WXML / WXSS 哈希一致。
- [x] 更新 execution、Spec 索引和 Spec-代码映射，记录实际验证结果和未执行的远端运行态边界。

## T13 异步响应跨账号写入防护

**Validates: Requirements 3.6**

- [x] 将 token、userId 和 Actor 角色组成统一的请求会话快照，实名 GET、等级 GET 和实名提交 POST 响应落地前均复核该快照。
- [x] `syncLevelInfo()` 返回 `UserLevelInfo | null`，跳过或 stale 响应不写 Store；实名页不再把现有缓存误当成本次完成度请求结果。
- [x] 扩展 00-191 静态门禁，覆盖实名提交和档案完成度的跨会话保护，并完成红绿验证。

## T14 终审竞态与身份证展示边界

**Validates: Requirements 3.1, 3.6**

- [x] 将 `bootstrapSession()` Promise 绑定发起 token + session revision，旧响应或旧异常不得覆盖 / 退出新会话。
- [x] 统一 401 session invalidation，同步清空 Storage 与 Pinia 内存；请求层额外绑定 auth token + revision，旧账号晚到 401 不得清理或重定向新账号。
- [x] 为 hydration、completion、submit 增加页面 generation 所有权，旧回调不得失效或报错到新页面。
- [x] `toStatusResp()` 与后台详情只返回 canonical masked 身份证号；缺失、cipher/hash 或异常值返回 `null`，DTO / 管理端物理删除 cipher 展示合同并补充后端回归测试。
- [x] 扩展 00-191 门禁并完成红绿验证、类型检查、构建和两轮独立终审。
