# 00-191 当前阶段小程序实名状态 500 修复

## 1. 概述

用户在小程序 `pages/mine/index` 看到 toast「操作失败」，网络请求显示：

```text
GET https://api.kplyyk.com/api/verify/status
{"code":500,"message":"操作失败","data":null}
```

该接口属于登录后演员运行态同步的一部分，用于刷新实名状态。对于未提交实名、历史记录缺失、实名记录表迁移不完整等情况，接口不应返回 500；个人中心也不应因为附属运行态同步失败而把账号头部继续显示为「未登录用户」。

> **复发标记（2026-07-27）**：用户再次提供 `{"code":500,"message":"操作失败","errorCode":null,"data":null}`，并确认同类问题已出现至少 3 次。`00-191` 的历史 `/api/verify/status` schema 兼容修复已于 2026-07-06 完成 schema 与后端发布，当时登录态生产 smoke 为 `code=200`；本次证据没有请求路径、发生时间或关联码，因此只能标记为“同类通用 500 再次出现，具体端点与原始异常待关联码确认”，不能直接认定历史 schema 根因复发。

## 2. 用户故事

作为刚登录的小程序用户，我进入「我的」页面时，即使实名状态接口暂时异常，也应先看到我的账号身份和基础页面内容，而不是被误认为未登录用户。

作为未实名用户，我查询实名状态时应得到 `status=0` 的默认状态，而不是服务端 500。

作为开发者，我需要有回归脚本防止 `/api/verify/status` 的默认态和个人中心容错再次退化。

作为开发者，我还需要清理 00-178 接入后残留的旧实名 provider 二次调用，避免服务同时写新旧两套 provider 字段，继续制造数据库字段漂移。

作为开发者，我需要每个未处理异常都返回非敏感关联码，并能用同一关联码在服务端日志中定位请求方法、路径和原始堆栈，避免不同根因继续折叠为完全相同的响应。

作为实名页用户，我进入页面时只应读取一次实名状态；若读取失败，页面应保留明确的局部错误态和重试入口，提交成功也不能因为一次额外状态查询失败而被误报为提交失败。

## 3. 功能需求

### 3.1 实名状态接口默认态

**描述**：`GET /api/verify/status` 必须优先以用户表 `realAuthStatus` 作为可返回事实源。没有实名记录或实名记录查询异常时，应返回默认状态，不得让附属记录查询导致接口 500。

**验收标准**：

- WHEN 登录用户没有 `identity_verification` 记录 THEN `/api/verify/status` 返回 `code=200` 且 `data.status=0`。
- WHEN 用户表 `realAuthStatus` 有值 THEN 默认状态以用户表值为准。
- WHEN 查询最新实名记录失败 THEN 接口仍返回用户表实名状态默认值，不返回 `code=500`。
- WHEN 存在最新实名记录且查询成功 THEN 接口继续返回该记录的状态、姓名、脱敏身份证号、驳回原因和时间字段。
- WHEN `idCardNoMasked` 缺失或不符合 canonical 脱敏格式 THEN `data.idCardNo=null`，不得回退返回 `idCardNoCipher`、`sha256:` 哈希或其他内部密码材料。
- WHEN 小程序状态或后台实名详情返回身份证展示值 THEN 响应 DTO 和前端类型只包含验证后的 masked 字段，不暴露 `idCardNoCipher` 合同。

### 3.2 个人中心运行态同步容错

**描述**：`pages/mine/index` 已在 00-199 重构为直接基于全局 `hasStoredSession / currentUser` 渲染账号头部。个人中心不得重新依赖实名 / 邀请 / 等级附属同步才能判断登录态；页面附属数据加载失败只能进入页面局部错误态，不得清空会话或切换为游客头部。

**验收标准**：

- WHEN Storage 中存在有效会话且 `currentUser` 可用 THEN Mine 账号头部直接按全局用户态渲染，不等待实名状态请求。
- WHEN Mine 页面附属数据加载失败 THEN 页面保留账号头部并显示局部错误，不清空全局会话。
- WHEN 游客进入「我的」 THEN 仍展示完整游客态页面，不触发实名状态接口。

### 3.3 回归验证

**描述**：新增专项脚本检查后端和前端容错关键形态。

**验收标准**：

- WHEN `currentStatus()` 未对 `selectLatestByUserId()` 异常做兜底 THEN 脚本失败。
- WHEN `currentStatus()` 无记录默认态不是独立 helper THEN 脚本失败。
- WHEN `mine` 页面不再基于 `hasStoredSession / currentUser` 渲染账号头部，或重新把 `syncActorRuntimeState()` 作为登录态前置条件 THEN 脚本失败。
- WHEN 实名页在一次 hydration 中存在两个 `/api/verify/status` 读取入口，或 `onShow` 触发的 Promise 没有页面局部异常闭环 THEN 脚本失败。
- WHEN 全局兜底异常仍返回空 `errorCode`，或服务端错误日志没有记录相同关联码与 HTTP method / URI THEN 脚本或后端测试失败。
- WHEN 后端仍保留 `TencentIdCardVerificationClient` / `verifyProvider` / `providerDescription` 旧 provider 映射 THEN 脚本失败。
- WHEN 代码修复完成 THEN 脚本通过。

### 3.4 旧实名 provider 残留清理

**描述**：`IdentityVerificationServiceImpl.submit()` 只能使用 `RealNameVerificationProvider` 这一条 canonical 二要素状态机，不得再调用旧 `TencentIdCardVerificationClient`。后端实体与 DTO 不再映射 `verify_provider` / `provider_description` 旧字段，统一使用 `provider_code`、`provider_result_code`、`provider_result_message`、`provider_request_id` 和 `provider_verified_at`。

**验收标准**：

- WHEN 提交实名认证 THEN 后端只调用 `RealNameVerificationProvider.verify(...)` 并由 `applyProviderResult(...)` 写入 canonical provider 字段。
- WHEN 查询后台实名列表 THEN provider 展示字段来自 `providerCode`，不再来自旧 `verifyProvider`。
- WHEN 查询后台实名详情 THEN provider 回看只暴露 canonical provider 字段。
- WHEN 全仓搜索后端主源码 THEN 不再存在 `TencentIdCardVerificationClient`、`TencentIdCardVerificationProperties`、`TencentIdCardVerificationResult` 旧类。
- WHEN 全仓搜索 verify 后端主源码 THEN 不再存在 `verifyProvider` / `providerDescription` 旧字段映射。

### 3.5 未处理异常关联码与窄范围降级可观测性

**描述**：全局 `Exception` 兜底不得再把所有原始异常折叠为 `errorCode=null`。每次未处理异常必须生成唯一、非敏感的关联码，并以同一值记录服务端错误日志。`currentStatus()` 对最新实名记录查询的既有窄范围降级仍保留，但降级发生时必须留下不含实名信息的 warn 日志。

**验收标准**：

- WHEN 任意未处理异常进入 `GlobalExceptionHandler` THEN 响应保持 `code=500,message=操作失败,data=null`，同时 `errorCode` 满足 `INTERNAL_ERROR_<32 位大写十六进制>`。
- WHEN 两个独立异常请求进入兜底处理 THEN 两次 `errorCode` 不相同。
- WHEN 服务端记录该异常 THEN ERROR 日志包含响应中的同一关联码、HTTP method、URI 和原始 throwable；响应不得包含异常类名、堆栈、SQL 或隐私字段。
- WHEN `selectLatestByUserId(userId)` 查询异常并回落到用户表状态 THEN WARN 日志包含 `userId` 和异常，不记录真实姓名或身份证号。
- WHEN `userMapper.selectById`、提交、审核等非既定可恢复链路异常 THEN 继续交由全局异常处理，不得统一伪装为“未实名”。

### 3.6 实名页单次读取与局部错误态

**描述**：`pkg-card/verify/index` 的页面 hydration 只能通过 Store 发起一次实名状态读取。页面负责加载态、错误态和重试；提交成功后直接把提交响应写回 Store，不得追加第二次状态 GET。

**验收标准**：

- WHEN 登录演员进入实名页 THEN 一次 `hydratePage()` 最多调用一次 `/api/verify/status`。
- WHEN 状态读取进行中 THEN 不展示基于初始 `status=0` 的可提交表单。
- WHEN 状态读取失败 THEN 页面保留顶部与前置检查摘要，状态 / 表单区域显示局部错误和“重新加载”入口；不产生未处理 Promise rejection，也不重复弹出请求层和页面层两次错误提示。
- WHEN 错误响应带有关联码 THEN 局部错误文案展示该非敏感关联码，便于用户反馈。
- WHEN `submitVerify()` 成功 THEN 页面和 `userStore` 直接应用响应状态并提示提交成功，不再调用 `/api/verify/status`；后续无额外 GET，因此不得把成功提交误报为失败。
- WHEN 同步入口因无会话或非演员而跳过 THEN 返回 `null`；WHEN 已读取 THEN 返回 `IdentityVerification`，调用方可直接复用同一响应。
- WHEN 实名状态 GET、实名提交 POST 或档案完成度 GET 发出后账号发生退出、切换或角色变化 THEN 旧响应不得写入当前 Store，也不得覆盖当前页面状态。
- WHEN 档案完成度同步被跳过或响应已过期 THEN Store 返回 `null` 且不写入等级、邀请数、完成度或能力档位；实名页必须把它识别为会话已变化，而不是把当前 Store 缓存误认为本次请求成功。
- WHEN 账号 A 的 bootstrap、完成度或提交请求晚于账号 B 的新 hydration 返回 THEN A 的旧 generation 必须静默退出，不得隐藏、报错或覆盖 B 的新页面状态。
- WHEN 任一请求返回 401 并触发自动退出 THEN Storage 与 Pinia 内存 session 必须原子失效；随后到达的并发旧成功响应不得重新持久化旧用户。
- WHEN 账号 A 的旧请求在账号 B 登录后才返回 401 THEN 该 401 必须因请求发起 token + auth revision 已过期而被忽略，不得清理 B 或把 B 重定向到登录页。
- WHEN `/api/user/me` 请求期间 token 或 session revision 发生变化 THEN bootstrap 响应和异常都只属于发起会话，不得组成“旧 user + 新 token”或退出新账号。

## 4. 非功能需求

- 不改变实名认证提交、审核、拒绝和通过的业务语义。
- 不新增 mock 实名状态。
- 不把后端 500 简单隐藏为前端静默失败；后端接口必须恢复默认态合同。
- 不继续补 `verify_provider` / `provider_description` 旧列；以 00-178 的 canonical provider 字段为准。
- 关联码不得承载用户 ID、手机号、身份证号、SQL、异常消息或其他业务敏感信息。
- 页面局部错误态必须关闭请求层默认 toast，避免同一次失败重复提示；其他调用方的既有默认提示行为保持不变。
- 所有会写入全局用户态的异步实名页响应必须同时校验请求发起时的 token、userId 和演员角色；只校验请求发出前的登录态不满足要求。
- 页面异步流程除 Store session snapshot 外还必须校验页面 generation；旧 generation 只能静默结束，不能调用当前 generation 的失效或错误 UI。
- 自动 401 清理必须通过统一 session invalidation 入口同步 Storage 与内存，并推进 session revision；只有仍属于当前请求会话的 401 可以执行清理和登录跳转。
- 本轮只修改仓库并执行本地验证，不直接发布、重启或修改远端环境。

## 5. 约束条件

- 后端优先修改 `IdentityVerificationServiceImpl.currentStatus()` 的默认态和异常兜底。
- Mine 页以 00-199 当前全局会话渲染结构为准，不恢复已经退场的 `applyMineUserHeader / syncActorRuntimeState` 页面内实现。
- 前端复发收口优先修改 `stores/user.ts` 与 `pkg-card/verify/index.vue`，避免重复读取与成功提交后的额外 GET。
- 必须保留其他需要强登录的页面门禁行为。
