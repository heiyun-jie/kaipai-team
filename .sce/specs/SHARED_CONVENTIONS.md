# 全局开发约定

> 所有 Spec 共享的技术约束、非功能需求和设计规范。各 Spec 的"约束条件"和"非功能需求"仅需补充页面特有项，通用部分引用本文档。

## 技术栈

- **框架**: uni-app 3.0 + Vue 3.4 Composition API (`<script setup lang="ts">`)
- **语言**: TypeScript（严格模式）
- **样式**: SCSS，所有视觉属性引用 `$kp-*` Design Tokens（00-01-global-style-system），禁止硬编码
- **UI 库**: `tdesign-miniprogram@1.16.0`，页面按需声明并由受控脚本生成微信原生组件闭包；自定义业务组合组件统一 `Kp` 前缀（00-02、00-226）
- **状态管理**: Pinia，Store 命名 `use{Name}Store`
- **API 层**: 统一请求封装 `utils/request.ts`，所有接口通过 `api/*.ts` 调用（00-03-shared-utils-api）
- **平台**: 微信小程序（主要）、H5（辅助）

## 页面结构模式 - 3.0 蓝白 UI

`00-221` 起，小程序页面统一迁移到蓝白、专业、清晰的演员作品集风格：

- 页面以白色画布和浅灰分组为默认结构，不再新增深色 Hero + 米色内容叠层。
- 品牌蓝只用于主操作、进度、链接和选中态；普通内容使用中性色层级。
- 四个 Tab 根页直接渲染自己的内容，并使用原生 TabBar；禁止用中间重定向页代替根页。
- 标题型页面使用 `KpPageNav` 适配微信胶囊；历史 `KpNavBar` 已在 `00-209` 退场。
- 旧页面迁移范围、临时 legacy 白名单和最终删除门禁以 `00-221` 与 `docs/ui-style-guide-v3.md` 为准。
- 通用按钮、输入、图片、选择、Tab、开关、弹窗和 ActionSheet 使用 TDesign；禁止 app 级全局注册整套组件。`KpPageNav`、`KpFloatingBackButton`、`KpCreateProgress` 等微信胶囊或业务流程组合组件继续保留。
- 导航、系统文件/媒体选择、图片预览、视频播放、WebView 和短时平台 Toast 属于微信 / uni-app 平台能力，不为组件库纯度增加脆弱桥接；但页面不得继续使用 `uni.showModal` / `uni.showActionSheet` 代替受控 TDesign 浮层。

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
- UI 核验必须遵守桌面非干扰：不得置顶、强制前台、抢占焦点、控制整屏或使用桌面级截图 / 坐标 / 键鼠自动化；优先使用源码 / `dist/build` / `dist/dev` 产物核验、不会抬起窗口的内部模拟器接口或用户提供截图。确需打开可见微信开发者工具窗口时，必须先获得用户明确授权。
- 对外公开内容生成入口（如 AI 分享图、对外名片首图）必须做「先实名、后生成」门禁：后端在创建任务前强制校验为安全闸（实名未通过即拒绝，不消耗生图资源），前端在发起请求前判断为体验闸（未实名先提示并引导去 `/pkg-card/verify/index`，不发无效请求）。实名「已通过」判定统一以 `realAuthStatus == 2`（前端 `userStore.isCertified`）为唯一事实源，不得新增并行字段或专用校验接口。

## 通用间距节奏

所有页面和共享组件必须复用统一 spacing 节奏，禁止页面内临时发明一套新距离。

- **页面左右边距**：默认使用 `$kp-spacing-page`（24rpx）
- **卡片与卡片之间**：默认使用 `$kp-spacing-gap`（16rpx）
- **文字区块到主按钮 / 主 CTA**：默认使用 `$kp-spacing-lg`（32rpx）
- **同一卡片内的小型信息组**：默认使用 `$kp-spacing-sm`（16rpx）
- **大段内容与底部悬浮操作栏之间**：页面内容区必须预留底部安全空间，避免被固定按钮遮挡
- **页面级固定操作**：使用页面底部悬浮操作栏时，卡片内部不得再复制同一组主操作按钮

执行规则：

- 页面内出现两张以上连续卡片时，优先用父级 `gap` 统一，不逐张单独写 `margin-bottom`
- 同类按钮组、邀请摘要、等级摘要等跨页面重复模块，统一抽到 `src/components/Kp*.vue`
- 当用户提出“要有一定距离”时，先判断属于哪一层：卡片间距、卡内信息组间距、文字到 CTA 间距，再调整对应 token

## 页面类型分类

3.0 页面按导航与内容职责分为三类：

| 类型 | 特征 | 返回按钮 | 适用页面 |
|------|------|---------|---------|
| **A. Tab 根页** | 直接渲染主导航内容 | 不显示 | home, card-list, assets, mine |
| **B. 普通内容页** | 白色导航层 + 浅灰分组 | 显示 | 表单、工具、导入复核页 |
| **C. 创建 / 公开页** | 向导进度或作品阅读结构 | 按页面语义 | pkg-actor-card 向导、generate、view |

## 顶部三层结构

页面顶部拆分为三个独立层，开发时一次只改一层：

1. **导航层** — 返回按钮、胶囊对齐关系
2. **主视觉层** — 标题、副标题、进度、状态或媒体信息
3. **Content 层** — 白色内容区、表单卡片

用户描述映射：
- "返回按钮不对齐" → 导航层
- "顶部内容太高/太低" → 主视觉层
- "白色区域往上/下""内容区域" → Content 层

## 返回按钮实现规范

**标题型页面（胶囊带对齐）— 统一走 `KpPageNav`（`00-212` 起为唯一做法）：**
- `KpPageNav` 内部调用 `getFloatingBackNavStyles()` 自行完成占位、胶囊带定位与 `200rpx` 避让，并自持 `position: relative`
- 调用方**不得**再手写 `top` / `height` / `right: 200rpx`，也不得自行引 `KpCapsuleSpacer` 拼装标题行
- 接口：`title` / `showBack`（Tab 根页传 `false`）/ `backText`（如 `generate` 的「修改」）/ `back` 事件 / 默认插槽（标题右侧附加内容，或自定义标题字重时承载标题节点）
- 组件只 `emit('back')`，不自行 `navigateBack`，保留调用方「离开前确认」拦截能力
- 覆盖 13 页：`home` / `card-list` / `assets` / `mine` + `pkg-actor-card` 全 9 页
- 回归门禁：`npm run verify:nav-title`

**创建进度 - `KpCreateProgress`（`00-212` + `00-216`）：**
- 组件位置 `src/pkg-actor-card/components/KpCreateProgress.vue`。分包专用组件必须保持自包含，不依赖主包业务模块。
- 接口：`done` / `total`（默认 `7`）；百分比由计算值生成并收敛到 `[0, 1]`。
- 7 个 step 页的 `done` 表示当前步序 1..7；create Hub 的 `done` 表示已完成项数量 `doneCount`。
- 统一显示“创建进度 x/7”；调用页 `__header` 不得重复增加组件已持有的底部间距。
- `generate` 是终态页，不显示创建进度。

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
- 输入控件使用按需声明的 `t-input` / `t-textarea` / `t-picker`，事件值统一从 `event.detail` 提取并保留 maxlength、键盘类型、清空和校验语义
- 底部固定保存按钮

## 通用依赖引用

| 基础 Spec | 提供能力 |
|-----------|---------|
| 00-01-global-style-system | `$kp-*` 变量、`@mixin kp-*`、`.kp-page/.kp-header/.kp-content` 骨架 |
| 00-02-shared-components | 19 个 Kp 前缀组件（Props/Events/Slots 见该 Spec requirements.md） |
| 00-03-shared-utils-api | types/、utils/、stores/、api/ 全套工具和接口封装 |
