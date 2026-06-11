# 00-182 当前阶段 AI 分享图生成实名门禁

## 1. 概述

当前 AI 分享图生成入口 `POST /ai/profile-card/generate` 已具备鉴权、演员档案、源图三道前置校验，但没有任何实名认证门禁。任何已登录用户即使未完成实名认证，也能提交 AI 分享图生成任务并消耗后端生图资源。

AI 分享图作为对外公开的演员名片首图，属于需要真实身份背书的对外内容。本 Spec 负责在 AI 分享图生成链路上补齐「先实名、后生成」的门禁：后端在 `generate` 提交时强制校验实名状态作为安全闸；前端在生成前先判断实名状态作为体验闸，未实名时直接提示并引导用户去实名认证页，不发起无效请求。

本轮不新建独立的「实名校验接口」——后端实名状态事实源（`User.realAuthStatus` / `IdentityVerification.status`，`2 = 已认证通过`）与前端读取能力（`userStore.isCertified` / `GET /verify/status`）都已存在，本 Spec 只在 AI 生成链路上复用它们补门禁。

## 2. 用户故事

作为平台，我希望只有完成实名认证的用户才能生成对外公开的 AI 分享图，避免未经身份核验的用户产出冒充性名片内容。

作为已实名用户，我的 AI 分享图生成流程不受影响，门禁对我无感。

作为未实名用户，我点击生成时能立刻收到清晰提示，并被引导到实名认证页完成认证，而不是提交后才在后台被静默拒绝。

## 3. 功能需求

### 3.1 后端生成接口强制实名门禁

**描述**：`POST /ai/profile-card/generate` 在创建生成任务前，必须校验当前登录用户的实名状态为「已认证通过」。未实名（未提交 / 审核中 / 拒绝）一律拦截，不创建任务、不进入异步生图。

**验收标准**：

- WHEN 已实名通过（`realAuthStatus == 2`）用户提交 generate THEN 接口照常创建任务并返回 `taskId`。
- WHEN 未提交实名（`0`）用户提交 generate THEN 接口拒绝，不创建任务，返回业务错误码 `NOT_CERTIFIED (403)` 与可读提示。
- WHEN 实名审核中（`1`）用户提交 generate THEN 接口拒绝，不创建任务，返回审核中语义的可读提示。
- WHEN 实名被拒绝（`3`）用户提交 generate THEN 接口拒绝，不创建任务，返回需重新认证语义的可读提示。
- WHEN 实名校验未通过 THEN 不得调用 AI provider，不得写入 `actor_ai_profile_card_task` 记录。
- WHEN 实名校验插入到既有校验链 THEN 排在鉴权之后、档案 / 源图校验同级或之前，避免对未实名用户先做无意义的档案 / 源图加载。

### 3.2 前端生成前实名前置判断

**描述**：`pkg-card/ai-profile-card/index.vue` 的 `handleGenerate()` 在调用 `generateAiProfileCard` 之前，先用 `userStore` 判断实名状态，未实名直接拦截并引导，不发起请求。

**验收标准**：

- WHEN 用户点击「一键生成」且 `userStore.isCertified` 为 false THEN 不调用 `generateAiProfileCard` 接口。
- WHEN 用户未实名 THEN 弹出 `uni.showModal` 提示「生成 AI 分享图需先完成实名认证」。
- WHEN 用户在该弹窗点击确认 THEN `uni.navigateTo` 跳转 `/pkg-card/verify/index`。
- WHEN 用户在该弹窗点击取消 THEN 停留在当前页，不发起生成请求。
- WHEN 用户已实名通过 THEN 生成流程与现状一致，无新增拦截。
- WHEN 进入生成判断前 THEN 前端应保证实名状态为最新（必要时复用 `userStore.syncVerificationStatus()` 同步后再判断），避免用本地过期态误拦截已实名用户。

### 3.3 实名状态判定单一事实源

**描述**：前后端的「已实名通过」判定必须以现有事实源为准，不得新增并行的实名状态字段或新接口。

**验收标准**：

- WHEN 后端判定实名通过 THEN 以 `realAuthStatus == 2`（等价常量 `STATUS_APPROVED` / `REAL_AUTH_APPROVED`）为唯一标准。
- WHEN 前端判定实名通过 THEN 以 `userStore.isCertified`（`realAuthStatus === 2`）为唯一标准。
- WHEN 本轮实现 THEN 不新增「实名校验」专用接口，复用既有实名状态事实源与查询能力。

## 4. 非功能需求

- 不改动实名认证提交链路 `POST /verify/submit` 与腾讯云二要素核验逻辑（`00-178`）。
- 不改动 AI 生图 provider 选择、质量门禁与异步执行逻辑。
- 不引入前端 mock；不绕过后端门禁。
- 后端拦截须可被前端 `request.ts` 框架层统一错误处理识别并提示。

## 5. 约束条件

- 本轮只处理 AI 分享图生成入口（`generate`）的实名门禁，不波及简历润色（`/ai/polish-resume`）等其它 AI 入口。
- 后端门禁是安全闸、前端门禁是体验闸，二者都要落地；前端拦截不可替代后端强制校验。
- 实名状态可选值与含义沿用现状：`0 未提交 / 1 审核中 / 2 已通过 / 3 已拒绝`。
