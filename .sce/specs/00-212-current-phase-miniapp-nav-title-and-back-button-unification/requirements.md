# 00-212 当前阶段小程序导航标题与返回按钮统一收口

> 状态：Spec 先行。本 Spec 在实现之前建立书面合同。
> 触发证据：用户截图标注 `pkg-actor-card/step-visual` 顶部 `‹ 主视觉照片` 一行，指出标题位置错位；随后要求「把关于这个标题或者返回按钮加标题的问题都进行修正」。
> 范围锚点：`00-207 §3.1` 已在 `home` / `card-list` / `mine` 三个 Tab 页建立「标题行绝对定位对齐胶囊」的做法。本 Spec 把该做法收口为全站唯一合同，并处理 `00-207` 未覆盖的 16 个页面。

## 1. 概述

当前小程序 `20` 个登记页面中，`19` 个渲染页共存**三套互不兼容的顶部导航实现**，且没有任何共享组件承载该契约。这是本轮缺陷的真实根因：`00-207` 只修了三个 Tab 页，同样的错位在其余页面原样留存。

三套实现现状：

| 模式 | 实现方式 | 页面数 | 页面 |
|------|---------|--------|------|
| **A · 胶囊带绝对定位**（`00-207` 已修，目标态） | `KpCapsuleSpacer` + 标题行 `position: absolute` 绑定 `backButtonStyle.top/height`，父级 `position: relative` | 3 | `home` / `card-list` / `mine` |
| **B · 悬浮返回 + 居中标题** | `KpFloatingBackButton`（内部 `position: fixed`）+ `__nav-title` 绝对居中，`left/right: 160rpx` | 3 | `actor-profile/edit` / `pkg-profile/import-review` / `pkg-profile/assets` |
| **C · 深色 Hero 页** | `KpFloatingBackButton` + 标题在 Hero 正文内，导航行不承载标题 | 3 | `pkg-card/verify` / `pkg-tools/webview` / `pkg-tools/video-player` |
| **D · 流式导航行（缺陷态）** | `KpCapsuleSpacer` 之后紧跟**普通流式** `__nav` 行 | 9 | `pkg-actor-card` 全部 9 页 |

**缺陷本体（模式 D）**：`KpCapsuleSpacer` 已按 `getFloatingBackNavStyles().navStyle` 撑出胶囊高度的占位块，但 `__nav` 行排在它**之后**走正常文档流。结果是胶囊那条水平带被整块空置，返回箭头与标题一起被下推到正文起始位置，与正文自身的 `__h1` 标题贴在一起。用户截图中 `‹ 主视觉照片` 与其正下方正文 `主视觉照片` 的挤压感，就是这一条同时造成的位置错位与标题重复。

**次生缺陷**：模式 D 的 9 页里，7 页在导航行与正文各写了一次标题。其中 5 页完全重复（`主视觉照片` / `个人资料` / `视频简历` / `生成设置` / `附件简历`），2 页为改写措辞（导航 `参演作品` vs 正文 `选择参演作品`；导航 `生活照片` vs 正文 `添加生活照片`）。导航行提升进胶囊带后，重复只会更显眼。

本 Spec 不改变任何页面的路由注册、数据来源、后端合同、跳转关系或 tabBar 结构。

## 2. 用户故事

作为演员用户，我希望所有页面的返回按钮和页面标题都与右上角微信胶囊在同一水平带上，顶部不出现标题偏下、和正文标题挤在一起的错位感。

作为演员用户，我希望同一个页面标题不要连续出现两次。

作为开发者，我希望顶部导航只有一处权威实现，改一次全站生效，而不是每加一个页面就手抄一遍样式、再漏掉一遍。

作为开发者，我希望有一条自动门禁能拦住「新页面又手写流式导航行」这类回归，而不是等用户截图才发现。

## 3. 功能需求

### 3.1 `pkg-actor-card` 9 页导航行提升至胶囊带

**描述**：9 个页面的 `__nav` 行统一改为相对页面 header 绝对定位，纵向位置与高度取自 `getFloatingBackNavStyles().backButtonStyle`，与 `00-207 §3.1` 的三个 Tab 页完全同构。

**适用页面**：`create` / `step-visual` / `step-profile` / `step-works` / `step-photos` / `step-video` / `step-attachment` / `step-settings` / `generate`

**验收标准**：
- WHEN 渲染上述任一页 THEN `__nav` 容器必须绑定 `:style="{ top: backButtonStyle.top, height: backButtonStyle.height }"`，样式为 `position: absolute` 且 `display: flex; align-items: center`。
- WHEN `__nav` 改为绝对定位 THEN 其父级 `__header` 必须显式声明 `position: relative`。
- WHEN `__nav` 脱离文档流 THEN 原先由其 `padding` 撑开的垂直间距必须由紧随其后的可见元素补回，不得出现正文上移贴顶。
- `__nav` 右边界必须留出胶囊避让宽度 `200rpx`，左边界与页面内容对齐 `32rpx`。
- WHEN 页面存在返回箭头 THEN 箭头必须位于 `__nav` 行内、与标题同一水平带，不得独立浮动。
- 9 页的 `KpCapsuleSpacer` 存在与位置不得改变；导航标题文案不得改变。

### 3.2 消除导航与正文的标题重复

**描述**：导航行提升至胶囊带后，删除与导航标题**完全重复**的正文 `__h1`；措辞不同的正文标题保留。

**验收标准**：
- WHEN 导航标题与正文 `__h1` 文案完全一致 THEN 必须删除该 `__h1` 节点及其专用样式，仅保留导航标题。适用 5 页：`step-visual`（`主视觉照片`）、`step-profile`（`个人资料`）、`step-video`（`视频简历`）、`step-settings`（`生成设置`）、`step-attachment`（`附件简历`）。
- WHEN 正文标题与导航标题措辞不同 THEN 必须原样保留。适用 2 页：`step-works`（`选择参演作品`）、`step-photos`（`添加生活照片`）。
- WHEN 删除 `__h1` THEN 其下方 `__sub` 副标题必须保留，且必须补回原由 `__h1` 承担的顶部间距，不得出现副标题贴顶。
- WHEN 删除 `__h1` THEN 对应的 `&__h1` 样式规则不得成为死样式残留。

### 3.3 `step-visual` 进度条移出导航行

**描述**：`step-visual` 的步骤进度条当前位于 `__nav` 行内。导航行提升至胶囊带后，进度条会落入胶囊带并挤占标题宽度。改为独立成行，与同级页面 `create` 的 `__progress-row` 做法对齐。

**验收标准**：
- WHEN 渲染 `step-visual` THEN `__prog-bar` 不得再是 `__nav` 的子节点。
- WHEN 进度条独立成行 THEN 必须位于 `__header` 内、胶囊带下方、正文之上，且宽度与页面内容左右边界对齐。
- 进度值 `14.3%` 与进度条视觉样式（高度、圆角、底色、填充色）不得改变。
- WHEN 进度条移出 `__nav` THEN `__title` 不再需要 `flex: 1` 争抢剩余宽度，标题必须与其余 8 页表现一致。

### 3.4 抽取共享导航组件，消除三套实现并存

**描述**：新增 `KpPageNav` 组件承载「胶囊带对齐 + 返回按钮 + 标题」这一唯一契约，替换模式 A 与模式 D 共 12 页的手写导航行。

**验收标准**：
- WHEN 新增 `KpPageNav` THEN 必须内部调用 `getFloatingBackNavStyles()`，自行完成胶囊带定位与 `200rpx` 避让，调用方不得再手抄 `top` / `height` / `right` 数值。
- WHEN `KpPageNav` 提供接口 THEN 必须支持：`title`（标题文案）、`showBack`（是否显示返回箭头）、`back` 事件（点击返回）、默认插槽（导航行右侧附加内容）。
- WHEN 模式 A 的 3 页与模式 D 的 9 页改用 `KpPageNav` THEN 各页原有标题文案、返回行为、`KpCapsuleSpacer` 语义不得改变。
- WHEN 组件替换完成 THEN 全仓 `KpCapsuleSpacer` 与手写绝对定位标题行的组合不得再出现在页面层。
- 模式 B（`KpFloatingBackButton` + 居中标题，3 页）与模式 C（深色 Hero 页，3 页）**本轮不改**：模式 B 的 `left/right: 160rpx` 居中语义与 `sticky` 定位、模式 C 的「标题在 Hero 正文、导航行不承载标题」均属 `SHARED_CONVENTIONS.md` 已登记的页面类型策略，改动需独立评估。本条边界必须写入 `design.md` 并在索引中标注。

### 3.5 回归门禁

**描述**：新增可执行校验脚本，把 §3.1 ~ §3.4 的结构断言固化为自动门禁。

**验收标准**：
- WHEN 执行校验脚本 THEN 必须逐项断言 12 页导航实现已统一、9 页 `__nav` 不再走流式布局、5 页重复 `__h1` 已消除、`step-visual` 进度条已移出导航行。
- WHEN 任一断言失败 THEN 脚本必须打印全部失败项后再以非零码退出，不得首错即停（`00-211` 已记录该形态缺陷）。
- WHEN 脚本落地 THEN 必须接入 `package.json` 成为可调用命令；未接入的脚本不计入门禁（`00-205` 已记录该形态问题）。

## 4. 非功能需求

- 本轮为纯前端样式与结构收口，不得新增任何网络请求、不得改动 `pages.json` 登记、不得改动后端与数据库。
- 组件抽取后主包体积增量必须实测记录，仍需满足微信单包 `2 MB` 约束。
- `vue-tsc --noEmit` 必须 `0` 报错。

## 5. 约束条件

- 改前端 `src` 后必须执行 `npm run build:mp-weixin`，并 grep 核对关键字进入 `dist/build` 与 `dist/dev` 双层产物，否则不得声称完成。
- `KpCapsuleSpacer` 的 `navStyle` 语义（撑出胶囊高度占位）为既有契约，本轮复用不得改写。
- `SHARED_CONVENTIONS.md` 第 85 行「返回按钮实现规范」中「页面本地实现，不依赖共享导航组件」一句，在本 Spec 落地后与 §3.4 冲突。该约定必须同步更新为：深色 Hero 页（模式 C）维持本地悬浮返回；胶囊带对齐的标题型页面统一走 `KpPageNav`。
- `SHARED_CONVENTIONS.md` 第 22 行提及的 `KpNavBar` 在 `00-209` 组件退场后已不存在，本轮须一并校正该失效引用。
