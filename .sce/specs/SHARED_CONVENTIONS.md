# 全局开发约定

> 所有 Spec 共享的技术约束、非功能需求和设计规范。各 Spec 的"约束条件"和"非功能需求"仅需补充页面特有项，通用部分引用本文档。

## 技术栈

- **框架**: uni-app 3.0 + Vue 3.4 Composition API (`<script setup lang="ts">`)
- **语言**: TypeScript（严格模式）
- **样式**: SCSS，所有视觉属性引用 `$kp-*` Design Tokens（00-01-global-style-system），禁止硬编码
- **UI 库**: uview-plus，自定义组件统一 `Kp` 前缀（00-02-shared-components）
- **状态管理**: Pinia，Store 命名 `use{Name}Store`
- **API 层**: 统一请求封装 `utils/request.ts`，所有接口通过 `api/*.ts` 调用（00-03-shared-utils-api）
- **平台**: 微信小程序（主要）、H5（辅助）

## 页面结构模式 — Cinematic Glassmorphism

所有页面遵循「深-浅」双层结构：

- 深色头部 `#121214`（320-400rpx）：页面标题、核心信息、KpNavBar
- 浅色内容区 `#F8F9FA`：圆角 `32rpx 32rpx 0 0`，负边距 `-40rpx` 上移重叠
- 毛玻璃 TabBar（Tab 页）或固定底部操作按钮（非 Tab 页）
- 导航栏：全部页面使用 `navigationStyle: custom`；标题型页面用 `KpPageNav` 适配微信胶囊按钮（`00-212`）。历史文档提到的 `KpNavBar` 已在 `00-209` 组件退场中删除，不存在

## 通用非功能需求

| 维度 | 要求 |
|------|------|
| 兼容性 | 微信小程序基础库 >= 2.25.0；iOS 14+；Android 10+ |
| 适配 | iPhone SE ~ iPhone 15 Pro Max 全系列；状态栏高度自动适配 |
| 性能 | 页面首屏渲染 < 1s（含接口请求）；列表单次渲染 ≤ 10 条 |
| 防重复 | 提交类按钮 loading 状态锁定，防止重复点击 |
| 降级 | `backdrop-filter` 不支持时降级为纯色背景 |
| 校验 | 表单 blur 触发即时校验；提交前全量校验 |
| 可访问性 | 表单项支持 aria-label；按钮 disabled 有明确视觉反馈 |

## 通用约束条件

- 后端 API 前缀 `/api`，Base URL 通过 `VITE_API_BASE_URL` 配置
- 统一返回格式 `{ code: 200, message: "success", data: {} }`
- Token 传递 `Authorization: Bearer <token>`
- 文件上传：图片 ≤ 10MB，视频 ≤ 100MB，接口 `POST /api/upload`
- 所有颜色、间距、圆角引用 Design Tokens，禁止硬编码
- 非 Tab 页使用 `navigationStyle: custom`
- 对外公开内容生成入口（如 AI 分享图、对外名片首图）必须做「先实名、后生成」门禁：后端在创建任务前强制校验为安全闸（实名未通过即拒绝，不消耗生图资源），前端在发起请求前判断为体验闸（未实名先提示并引导去 `/pkg-card/verify/index`，不发无效请求）。实名「已通过」判定统一以 `realAuthStatus == 2`（前端 `userStore.isCertified`）为唯一事实源，不得新增并行字段或专用校验接口。

## 通用间距节奏

所有页面和共享组件必须复用统一 spacing 节奏，禁止页面内临时发明一套新距离。

- **卡片与卡片之间**：默认使用 `$kp-spacing-gap`（24rpx）
- **文字区块到主按钮 / 主 CTA**：默认使用 `$kp-spacing-page`（32rpx）
- **同一卡片内的小型信息组**：默认使用 `$kp-spacing-sm`（16rpx）
- **大段内容与底部悬浮操作栏之间**：页面内容区必须预留底部安全空间，避免被固定按钮遮挡
- **页面级固定操作**：使用页面底部悬浮操作栏时，卡片内部不得再复制同一组主操作按钮

执行规则：

- 页面内出现两张以上连续卡片时，优先用父级 `gap` 统一，不逐张单独写 `margin-bottom`
- 同类按钮组、邀请摘要、等级摘要等跨页面重复模块，统一抽到 `src/components/Kp*.vue`
- 当用户提出“要有一定距离”时，先判断属于哪一层：卡片间距、卡内信息组间距、文字到 CTA 间距，再调整对应 token

## 页面类型分类

所有页面按顶部策略分为三类：

| 类型 | 特征 | 返回按钮 | 适用页面 |
|------|------|---------|---------|
| **A. 深色 Hero 页** | 大面积深色头图 + 白卡上浮叠层 | 悬浮返回（与胶囊同行） | role-detail, apply-confirm, my-applies |
| **B. 普通顶部页** | 深色头部 + 表单/列表内容区 | 普通顶部返回 | actor-profile/edit, company-profile/edit, project/create, role-create, apply-manage, actor-profile/detail |
| **C. 入口/Tab 根页** | 流程起点或主导航 | 不显示 | home, mine, login, role-select |

## 顶部三层结构

页面顶部拆分为三个独立层，开发时一次只改一层：

1. **导航层** — 返回按钮、胶囊对齐关系
2. **Hero 层** — 标题、副标题、金额、标签等主视觉信息
3. **Content 层** — 白色内容区、表单卡片

用户描述映射：
- "返回按钮不对齐" → 导航层
- "顶部内容太高/太低" → Hero 层
- "白色区域往上/下""内容区域" → Content 层

## 返回按钮实现规范

**标题型页面（胶囊带对齐）— 统一走 `KpPageNav`（`00-212` 起为唯一做法）：**
- `KpPageNav` 内部调用 `getFloatingBackNavStyles()` 自行完成占位、胶囊带定位与 `200rpx` 避让，并自持 `position: relative`
- 调用方**不得**再手写 `top` / `height` / `right: 200rpx`，也不得自行引 `KpCapsuleSpacer` 拼装标题行
- 接口：`title` / `showBack`（Tab 根页传 `false`）/ `backText`（如 `generate` 的「修改」）/ `back` 事件 / 默认插槽（标题右侧附加内容，或自定义标题字重时承载标题节点）
- 组件只 `emit('back')`，不自行 `navigateBack`，保留调用方「离开前确认」拦截能力
- 覆盖 12 页：`home` / `card-list` / `mine` + `pkg-actor-card` 全 9 页
- 回归门禁：`npm run verify:nav-title`

**线性向导步序进度条 — `KpStepProgress`（`00-212` 补充）：**
- 组件位置 `src/pkg-actor-card/components/KpStepProgress.vue`。**分包专用组件必须放分包目录**，放 `src/components/` 会计入主包 2048 KB 预算
- 接口：`step`（当前步序，从 1 起算）/ `total`（默认 `7`）。百分比由 `step / total` 计算并 clamp 到 `[0,1]`，不得回退成硬编码宽度
- 覆盖 7 个 step 页：`step-visual`(1) → `step-profile`(2) → `step-works`(3) → `step-photos`(4) → `step-video`(5) → `step-attachment`(6) → `step-settings`(7)
- 必带「第 N 步 / 共 M 步」文案：`step-visual` 副标题含「AI 自动扩图」，纯进度条会被误读成扩图/上传进度
- 间距由组件自持（`padding: 0 24rpx 16rpx`，左右与页面 `__body` 的 `24rpx` 对齐）。调用页 `__header` **不得**再写 `padding-bottom`，否则双份留白
- **不适用**：`create` 是中心页，展示完成度 `doneCount/7`（可跳任意步，语义是"做完几项"而非"第几步"），保留自有 `__progress-row`；`generate` 是终态页，无步序

**悬浮返回（深色 Hero 页，模式 C）：**
- 用 `uni.getMenuButtonBoundingClientRect()` 获取胶囊位置，返回按钮使用同组 `top/height`
- 标题在 Hero 正文内，导航行不承载标题；此类页维持 `KpFloatingBackButton` 本地实现，**不适用** `KpPageNav`
- 复用时必须整体复制：本地返回按钮 + header padding 清零 + Hero 起点（三件套）
- 适用：`pkg-card/verify` / `pkg-tools/webview` / `pkg-tools/video-player`

**普通返回（普通顶部页，模式 B）：**
- 返回与标题在同一顶部结构中，不浮在内容层上方
- 现为 `KpFloatingBackButton` + `__nav-title` 绝对居中（`left/right: 160rpx`）+ `__nav` `sticky` 吸顶；居中与吸顶语义与 `KpPageNav` 不同构，`00-212` 未合并
- 适用：`actor-profile/edit` / `pkg-profile/import-review` / `pkg-profile/assets`

## 表单页实现方式

- 不把全部字段塞进一张大卡片，拆为多张主题卡片（概览卡 + 基础信息卡 + 补充信息卡 + 展示卡）
- 输入控件优先使用原生 `input` / `textarea` / `picker`，保证小程序兼容性
- 底部固定保存按钮

## 通用依赖引用

| 基础 Spec | 提供能力 |
|-----------|---------|
| 00-01-global-style-system | `$kp-*` 变量、`@mixin kp-*`、`.kp-page/.kp-header/.kp-content` 骨架 |
| 00-02-shared-components | 19 个 Kp 前缀组件（Props/Events/Slots 见该 Spec requirements.md） |
| 00-03-shared-utils-api | types/、utils/、stores/、api/ 全套工具和接口封装 |
