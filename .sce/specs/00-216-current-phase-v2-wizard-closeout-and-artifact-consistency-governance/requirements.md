# 当前阶段 v2 向导流程收尾与产物一致性治理

## 1. 概述

本 Spec 收口 v2.0 演员卡创建向导（`00-206`）的**最后一公里流程**，并把 `2026-08-13` 多轮修复中暴露的**产物一致性缺陷**（scoped 样式哈希分叉复发）纳入治理。

**上游依赖**：`00-206`（v2.0 创建向导）、`00-212`（导航标题/返回按钮统一收口）、`00-214`（附件简历端到端）

**背景**：`00-213` 审计确认向导存在多处流转与数据缺陷；`2026-08-13` 用户在真机/工具联调中发现：①完成设置后返回首页而非直接生成；②生成页返回按钮回首页；③顶部进度条语义与期望不符（多轮澄清）；④生成页返回「修改」文案需删除；⑤顶部样式「回退」（scoped 哈希分叉，`00-212` 四之四同型缺陷**复发**，触发方由 sync 脚本换成微信开发者工具运行态回写）。

**核心路径**：向导最后一步「完成设置」→ 直接进入生成页 → 生成/发布；任一页顶部统一「创建进度 x/7」进度条；产物在 `dist/build` ↔ `dist/dev` 间哈希恒一致。

---

## 2. 用户故事

- 作为演员，我在步骤 7 点「完成设置」后应**直接开始生成演员卡**，而不是被送回首页
- 作为演员，我在生成页点返回（原来标「修改」）应回到**上一页**（设置页 / 创建中心 / 名片夹），而不是回首页
- 作为演员，我希望每个步骤页顶部显示「创建进度 x/7」，x = **当前第几步**（进第 3 步显示 3/7），create 中心页显示已完成步数
- 作为维护者，我希望 `dist/build` 与 `dist/dev` 的 scoped 样式哈希**恒一致**，微信开发者工具运行态**不得**把文件回写成旧哈希导致样式静默失效

---

## 3. 功能需求

### 3.1 「完成设置」直接进入生成页

**描述**：`pkg-actor-card/step-settings/index.vue` 的「完成设置」保存步骤 7 后，跳转生成页而非 `navigateBack`。

**验收标准**：
- WHEN 用户在步骤 7 点击「完成设置」 THEN 保存 `settingsJson` 后 `navigateTo` 到 `/pkg-actor-card/generate/index?cardId={id}`
- WHEN 生成页打开 THEN 自动触发 `submitGenerate` 开始生成（既有行为）
- WHEN `draftStore.cardId` 为空 THEN 提示「草稿未就绪」并阻断跳转
- 禁止恢复 `navigateBack({ delta: 10 })`（超出栈深会退回首页）

### 3.2 生成页返回回到上一页

**描述**：`pkg-actor-card/generate/index.vue` 的 `goBack` 从 `navigateBack({ delta: 10 })` 改为普通 `navigateBack()`。

**验收标准**：
- WHEN 从设置页进入生成页后点返回 THEN 回到设置页
- WHEN 从创建中心进入后点返回 THEN 回到创建中心
- WHEN 从名片夹（`?preview=1`）进入后点返回 THEN 回到名片夹
- 全仓 `navigateBack` 不得再出现超出栈深的 `delta` 值

### 3.3 顶部进度条统一「创建进度 x/7」

**描述**：向导顶部统一为 create 形态的「创建进度 x/7」+ 进度条，`x` 按页面区分；由 `KpCreateProgress`（纯展示组件）承载。

**验收标准**：
- WHEN 进入 7 个 step 页任一页 THEN 顶部显示「创建进度 N/7」，N = 该页步号（进第 3 步显示 3/7），进度条填充 N/7
- WHEN 进入 create 中心页 THEN 顶部显示「创建进度 x/7」，x = 已完成步数（后端派生 `stepStatuses` 的 done 计数）
- WHEN `x` 越界 THEN 进度条 clamp 在轨道内，不溢出
- `KpCreateProgress` 必须落在 `src/pkg-actor-card/components/`（分包目录，不进主包预算）
- `KpCreateProgress` 为**纯展示组件**（props `done`/`total`，不依赖 store，杜绝跨包 require）
- 旧 `KpStepProgress.vue`（第 N 步 / 共 7 步文案）已删除，不得复活

### 3.4 生成页返回文案删除

**描述**：`pkg-actor-card/generate/index.vue` 的 `KpPageNav` 移除 `back-text="修改"`。

**验收标准**：
- WHEN 打开生成页 THEN 顶部仅显示返回箭头 + 「生成演员卡」标题，无「修改」文字
- 全仓 `back-text` 使用归零（无其他页面使用该 prop）

### 3.5 产物一致性治理（scoped 哈希分叉防复发）

**描述**：`dist/build` 与 `dist/dev` 的 scoped `data-v` 哈希必须恒一致；微信开发者工具运行态不得把文件回写成旧哈希。

**验收标准**：
- WHEN 构建完成 THEN `sync-mp-weixin.ps1` 双侧哈希断言通过（既有门禁）
- WHEN 微信开发者工具运行中文件被改写 THEN 重新同步后双侧哈希一致（防复发流程见 design §4）
- WHEN 用户反馈「样式回退/没变化」 THEN 修复者必须**先比对 `data-v` 哈希**（截图/工具元素面板 vs dist）再动源码，禁止直接猜改

---

## 4. 非功能需求

- `KpCreateProgress` / `KpPageNav` 等被分包页面引用的组件，**不得 require 外部业务模块**（微信端分包组件跨包 require 解析失败，见 design §3）
- 改前端 `src` 后必须 `npm run build:mp-weixin`，且核对 `dist/build` 与 `dist/dev` 双层产物
- `verify:nav-title`（00-212 门禁）保持全绿，含 `KpCreateProgress` 断言

---

## 5. 约束条件

- 进度条组件放分包目录，禁止放 `src/components/` 白占主包预算
- 完成后端 `/api/crew` 等历史接口不动、数据库不动（本 Spec 纯前端）
- 微信开发者工具固定打开 `kaipai-frontend/dist/dev/mp-weixin`

---

## 6. 全局规则

① 产物/缓存类问题**先比对哈希**，禁止凭视觉猜源码  
② 分包组件保持自包含，禁止跨包 require 业务模块  
③ 改 `src` 必构建、必核对双层产物，缺一不交付  
④ 进度条文案统一「创建进度 x/7」，step 页 x=当前步、create 页 x=完成数  
⑤ 涉及向导流转修改前先读 `00-206` / `00-212` / `00-213` / `00-216`

---

## 7. 边界与待定项

- 生成引擎仍是预览占位（`ActorCardGenerateService.runGenerate` TODO 长页渲染），本 Spec 只保证「完成设置 → 生成页 → 提交 → 轮询 → 预览/发布」链路可达，不实现真实长页渲染
- 00-213 登记的其余未裁决项（步骤 3 状态来源 / 枚举统一方向等）不属本 Spec 范围

---

## 8. 验收标准总览

### 前端

- [x] 完成设置直接进入生成页（3.1）
- [x] 生成页返回回到上一页（3.2）
- [x] 顶部进度条统一「创建进度 x/7」（3.3）
- [x] 生成页「修改」文案删除（3.4）
- [x] `vue-tsc --noEmit` 0 报错
- [x] `npm run build:mp-weixin` 成功，双侧产物核对通过
- [x] `verify:nav-title`（97 项）与 `verify:actor-card-attachment`（17 项）全绿

### 产物一致性

- [x] `dist/build` ↔ `dist/dev` scoped 哈希一致（含工具运行中改写后重同步）
- [x] 防复发流程（清缓存 → 重编译 / 关工具 → 重同步）已登记（design §4）
- [x] errorbook 新增「哈希分叉复发」与「跨包 require」条目

---

## 9. 依赖与前置

- `00-206` v2.0 创建向导（已完成）
- `00-212` 导航收口：`KpPageNav`（已完成）；本 Spec 复用其产物一致性门禁
- `00-214` 附件简历（已完成）
- 后端生成链路：`submit`/`status`/`publish`（已完成，`success→done` 归一化）

---

## 10. 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 微信开发者工具运行态再次回写旧哈希 | 防复发流程：先比对哈希 → 工具内清缓存 → 关工具后重同步（design §4.2） |
| 分包组件跨包 require 再次引入 | 组件自包含硬约束 + `verify:nav-title` 断言（纯展示、不含 store） |
| 进度条需求歧义反复 | 语义在 Spec 内固化：step 页 x=当前步、create 页 x=完成数 |
