# 恢复 1.0 分享落地页并接入首页模板区跳转

## 1. 概述

本 Spec 恢复**老版本分享者进入查看的分享落地页**（`pkg-card/ai-profile-card-detail`，`00-209` 删除，git `27d3bef^` 找回），并把首页「模板创建」区点击从「去创建」改为「跳转已创建好的分享页」。

**触发证据**：用户在 `pages/home/index` 反馈「底部的模板创建，点击应该是跳转已经创建好的分享页，而不是去创建」，并确认「老版本上面是有分享者进入查看的那个视角」。经核实：老版分享落地页存在且完整保留在 git 历史，后端公开接口与鉴权白名单均存活。

**与 00-215 的关系**：`00-215`（v2 观看者页 `pkg-actor-card/view/index`）仍为规划态、未开工；本 Spec 先用 1.0 分享落地页满足「分享者视角」诉求，不替代 00-215 的 v2 规划。

**核心路径**：首页模板区点击 → `GET /api/card/my-cards`（我的分享卡）→ 跳 `/pkg-card/ai-profile-card-detail/index?shareCardId={id}&shared=1`（分享者视图）

---

## 2. 用户故事

- 作为演员，我在首页「模板创建」区点击模板，应看到**已创建好的分享卡**（分享出去用户进入的页面），而不是被拉去创建
- 作为观看者，我通过分享链接进入该页，可无需登录查看分享卡（后端 personalization / artifact 接口在白名单内）

---

## 3. 功能需求

### 3.1 恢复分享落地页

**描述**：从 git 恢复 `00-209` 删除的 `pkg-card/ai-profile-card-detail`（页面 + 依赖模块），注册路由。

**验收标准**：
- WHEN 打开 `/pkg-card/ai-profile-card-detail/index?shareCardId={id}` THEN 展示分享卡（演员信息 / 分享图 / 布局预设）
- WHEN `shared=1` THEN 走分享者视图（`isSharedView`）
- WHEN 未登录观看者访问 THEN 核心数据（personalization / 分享图 artifact）可加载（后端白名单）
- `vue-tsc --noEmit` 0 报错，`build:mp-weixin` EXIT=0

### 3.2 首页模板区跳分享页

**描述**：`pages/home/index.vue` 模板卡片点击从 `goCreateWithStyle`（去创建）改为跳转已创建分享页。

**验收标准**：
- WHEN 已登录且存在分享卡 THEN 点击模板跳 `/pkg-card/ai-profile-card-detail/index?shareCardId={首张卡}&shared=1`
- WHEN 已登录但无分享卡 THEN toast「还没有已创建的分享卡」，不跳创建
- WHEN 未登录 THEN 提示登录（`requireLogin`）
- WHEN 接口失败 THEN toast「分享卡加载失败」，不跳转

### 3.3 数据来源与鉴权

**描述**：分享页数据来自 1.0 分享卡体系接口（后端存活，未改动）。

**验收标准**：
- `GET /api/card/my-cards`（我的分享卡列表，需登录）——首页跳转取首张卡
- `GET /api/card/personalization?shareCardId=`（白名单 permitAll）——分享页核心数据
- `GET /api/ai/profile-card/share-cards/{id}/artifact`（白名单 permitAll）——分享图
- 后端零改动

---

## 4. 非功能需求

- 恢复的页面/模块落在 `pkg-card` 分包，不占主包预算
- 从 git 恢复的文件保持 `00-209` 删除前原貌，不引入 v2 改造
- 产物核对：`dist/build` 与 `dist/dev` 双层均含分享页与新跳转

---

## 5. 约束条件

- 不新建 v2 观看者页（00-215 另行立项）
- 不恢复分享出口（`onShareAppMessage` 仍为 0，本 Spec 只恢复落地页）
- 后端 `/card/*` 历史接口按既有裁决只做文档标注，不改代码

---

## 6. 全局规则

① 恢复内容以 git `27d3bef^` 为权威来源  
② 首页跳转失败时给明确提示，不静默  
③ 产物一致性：改 `src` 后构建并核对双层产物（00-216 防复发流程）

---

## 7. 验收标准总览

- [x] 分享落地页恢复并注册路由
- [x] 首页模板区点击跳转分享页（不再去创建）
- [x] 无分享卡/未登录/接口失败均有明确反馈
- [x] `vue-tsc` 0 报错；`build:mp-weixin` EXIT=0；双侧产物核对通过
- [x] `verify:nav-title` 97/97、`verify:actor-card-attachment` 17/17
- [x] 文档同步（specs README / CURRENT_CONTEXT「分享面」章节）
