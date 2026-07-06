# 00-191 当前阶段小程序实名状态 500 修复

## 1. 概述

用户在小程序 `pages/mine/index` 看到 toast「操作失败」，网络请求显示：

```text
GET https://api.kplyyk.com/api/verify/status
{"code":500,"message":"操作失败","data":null}
```

该接口属于登录后演员运行态同步的一部分，用于刷新实名状态。对于未提交实名、历史记录缺失、实名记录表迁移不完整等情况，接口不应返回 500；个人中心也不应因为附属运行态同步失败而把账号头部继续显示为「未登录用户」。

## 2. 用户故事

作为刚登录的小程序用户，我进入「我的」页面时，即使实名状态接口暂时异常，也应先看到我的账号身份和基础页面内容，而不是被误认为未登录用户。

作为未实名用户，我查询实名状态时应得到 `status=0` 的默认状态，而不是服务端 500。

作为开发者，我需要有回归脚本防止 `/api/verify/status` 的默认态和个人中心容错再次退化。

作为开发者，我还需要清理 00-178 接入后残留的旧实名 provider 二次调用，避免服务同时写新旧两套 provider 字段，继续制造数据库字段漂移。

## 3. 功能需求

### 3.1 实名状态接口默认态

**描述**：`GET /api/verify/status` 必须优先以用户表 `realAuthStatus` 作为可返回事实源。没有实名记录或实名记录查询异常时，应返回默认状态，不得让附属记录查询导致接口 500。

**验收标准**：

- WHEN 登录用户没有 `identity_verification` 记录 THEN `/api/verify/status` 返回 `code=200` 且 `data.status=0`。
- WHEN 用户表 `realAuthStatus` 有值 THEN 默认状态以用户表值为准。
- WHEN 查询最新实名记录失败 THEN 接口仍返回用户表实名状态默认值，不返回 `code=500`。
- WHEN 存在最新实名记录且查询成功 THEN 接口继续返回该记录的状态、姓名、脱敏身份证号、驳回原因和时间字段。

### 3.2 个人中心运行态同步容错

**描述**：`pages/mine/index` 的账号头部应先基于 `bootstrapSession()` 返回的用户信息渲染。实名 / 邀请 / 等级等附属同步失败时，个人中心只展示数据区错误提示，不得阻断基础账号显示。

**验收标准**：

- WHEN `bootstrapSession()` 成功 THEN `displayName/avatar/profileSubtitle` 先更新为登录用户信息。
- WHEN `syncActorRuntimeState()` 失败 THEN 不再让 `hydrateMinePage()` 整体 reject；页面保留账号头部并显示数据加载失败提示。
- WHEN 游客进入「我的」 THEN 仍展示完整游客态页面，不触发实名状态接口。

### 3.3 回归验证

**描述**：新增专项脚本检查后端和前端容错关键形态。

**验收标准**：

- WHEN `currentStatus()` 未对 `selectLatestByUserId()` 异常做兜底 THEN 脚本失败。
- WHEN `currentStatus()` 无记录默认态不是独立 helper THEN 脚本失败。
- WHEN `mine` 页面仍在设置账号头部前 `await userStore.syncActorRuntimeState()` THEN 脚本失败。
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

## 4. 非功能需求

- 不改变实名认证提交、审核、拒绝和通过的业务语义。
- 不新增 mock 实名状态。
- 不把后端 500 简单隐藏为前端静默失败；后端接口必须恢复默认态合同。
- 不继续补 `verify_provider` / `provider_description` 旧列；以 00-178 的 canonical provider 字段为准。

## 5. 约束条件

- 后端优先修改 `IdentityVerificationServiceImpl.currentStatus()` 的默认态和异常兜底。
- 前端优先修改 `pages/mine/index.vue` 的运行态同步顺序和错误归属。
- 必须保留其他需要强登录的页面门禁行为。
