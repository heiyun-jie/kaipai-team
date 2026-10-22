# 小程序 TDesign 组件体系整体迁移

> 状态：T0-T5 代码、构建与产物门禁已完成；桌面非干扰运行态截图待人工核验。
>
> 用户裁决：2026-08-19，采用 TDesign 小程序版，并创建 Spec 对当前小程序执行整体组件体系更换。
>
> 上游视觉合同：`00-221-current-phase-miniapp-v3-ui-style-system` 与 `docs/ui-style-guide-v3.md`。

## 1. 概述

当前小程序基于 uni-app Vue 3，通用 UI 同时由微信 / uni-app 原生标签、页面局部 SCSS 和少量 `Kp*` 共享组件承担。按钮、输入、图片、弹窗、反馈、加载与空态在 24 个登记页面中重复实现，状态和尺寸容易漂移。素材库已经暴露两个直接缺口：取消系统视频选择被误报为上传失败，素材列表只显示“图 / 视 / PDF”文字标记而没有真实媒体缩略图。

本 Spec 引入 `tdesign-miniprogram@1.16.0` 作为微信小程序通用基础组件库，以 3.0 蓝白 Token 覆盖其品牌、文字、边框、圆角和状态变量，并按页面、按组件迁移当前登记路由。TDesign 负责按钮、图片、图标、Tab、输入、选择、弹窗、ActionSheet、加载等页面通用控件；系统媒体选择、预览、播放器、WebView、导航与短时平台 Toast 继续使用微信 / uni-app 平台能力。`KpPageNav`、创建进度、演员卡媒体绑定等业务组合组件继续保留，不为“全部替换”牺牲微信胶囊定位、分包自包含和业务合同。

## 2. 目标与非目标

### 2.1 目标

1. 固定使用 `tdesign-miniprogram@1.16.0`，建立可重复的安装、按需声明、构建和包体审计流程。
2. 当前 `pages.json` 登记的 24 个页面逐批使用 TDesign 通用组件，不再新增页面级原生按钮、输入、图片占位、弹窗和反馈实现。
3. TDesign 默认视觉被 3.0 Token 接管，页面继续符合五张参考图的字体、密度、边距和蓝白风格，不直接套用组件库示例页外观。
4. 素材库作为第一批试点：取消选择不报错、不常驻；照片显示真实签名缩略图；加载 / 失败 / 占位 / 重试状态完整。
5. 每批迁移均验证 src、dist/build、dist/dev、`usingComponents`、scope hash、运行契约和 2 MB 包体门禁。
6. 迁移完成后，删除已经被 TDesign 取代的通用 `Kp*` 组件和页面局部重复样式；业务组合组件保留清晰边界。

### 2.2 非目标

- 不借 UI 迁移修改后端业务接口、数据库结构、演员卡字段、路由语义或导航流。
- 不把 TDesign 整库全局注册或整包复制进主包。
- 不强制删除 `KpPageNav`、`KpFloatingBackButton`、`KpCreateProgress` 等含微信胶囊或业务流程语义的组合组件。
- 不将临时签名 URL 持久化到数据库、Pinia 长期状态或演员卡历史 URL 字段。
- 不在本 Spec 恢复已经退场的页面或旧 uView / Cinematic Glassmorphism 风格。

## 3. 用户故事

- 作为用户，我希望所有页面的按钮、输入、图片、弹窗和反馈行为一致，取消系统选择不会被当成失败。
- 作为用户，我希望素材库直接展示照片缩略图和明确的视频 / PDF 状态，而不是只能依靠文件名和文字圆标识别。
- 作为设计验收人员，我希望组件库服务于 3.0 视觉稿，而不是引入一套新的默认字号、圆角和间距。
- 作为开发者，我希望通用组件有稳定 API、按需打包和统一状态，不在每个页面重复修复原生 button、图片错误态和底部弹窗。
- 作为发布维护者，我希望引入第三方组件后仍满足微信单包 2 MB、分包自包含和旧版本前后端兼容。

## 4. 功能需求

### 4.1 依赖与构建接入

**验收标准**：

- WHEN 安装依赖 THEN `package.json` 与 lockfile 固定 `tdesign-miniprogram` 精确版本，不使用浮动 `latest`。
- WHEN 页面使用组件 THEN 只在该页面或对应分包声明实际使用的 `usingComponents`；禁止在 app 全局登记完整 TDesign。
- WHEN 执行 uni-app 微信构建 THEN TDesign 组件、样式、WXS 和内部依赖必须进入可发布产物，不要求用户在 DevTools 手工点击“构建 npm”。
- WHEN 分包页面使用 TDesign THEN 组件依赖必须位于微信允许的包边界内，不从分包运行时代码 require 不可达的主包业务模块。
- WHEN 构建完成 THEN `audit:mp-package` 必须通过，每个单包小于 2 MB，并记录主包与各分包增量。

### 4.2 3.0 主题适配

**验收标准**：

- TDesign 品牌、成功、警告、危险、文本、背景、边框、圆角变量映射到 `_tokens.scss` 的 3.0 语义值。
- 页面标题、主体边距、卡片密度和固定 CTA 仍以 `docs/ui-style-guide-v3.md` 为准；TDesign 默认值只作为组件内部基线。
- 不新增旧橙色选中态、棕米色背景、Emoji 功能图标或大圆角营销卡片。
- disabled、loading、pressed、error、empty、retry 状态必须保持清晰且不改变布局尺寸。

### 4.3 通用组件迁移边界

| 现有能力 | 目标 TDesign 能力 | 裁决 |
|---|---|---|
| 原生 `button` / `KpButton` | `t-button` | 通用命令按钮迁移；`open-type=share/getPhoneNumber` 先验证事件透传 |
| 原生 `image` / 文字媒体占位 | `t-image` + `t-icon` | 图片必须有 loading/error；视频/PDF使用语义图标或封面 |
| 页面自制 Tab | `t-tabs` / `t-tab-panel` | 不改变已有选中值和切换业务状态 |
| 原生 input / textarea / picker | `t-input` / `t-textarea` / `t-picker` | 保留 v-model、maxlength、键盘类型和清空语义 |
| `uni.showActionSheet` / 页面自制弹层 | `t-action-sheet` / `t-popup` | 统一安全区、取消和滚动所有权 |
| `uni.showModal` / `KpConfirmDialog` | `t-dialog` | 不可逆操作必须确认，取消无副作用 |
| 平台短时 Toast / 常驻临时错误 | `uni.showToast` / 页面错误态 | 平台短反馈自动消失；可重试错误才进入页面状态，不为纯度增加跨包 `selectComponent` 桥接 |
| 页面 loading / empty | `t-loading` / `t-result` 或业务空态组合 | 空态必须提供下一步动作 |
| `KpPageNav` / `KpFloatingBackButton` | 保留业务组合组件 | 微信胶囊定位与分包自包含优先，不机械替换 |

### 4.4 素材库首批试点

**验收标准**：

- WHEN 用户取消照片、视频或 PDF 系统选择 THEN 页面不显示失败、不创建重试状态，既有列表保持不变。
- WHEN 真实选择或上传失败 THEN 只在存在可重试文件时显示重试按钮；选择阶段失败使用短反馈或可关闭反馈，不得常驻无效操作。
- WHEN 切换照片 / 视频 / PDF THEN 与上一类型相关的临时选择错误被清理，不污染当前 Tab。
- WHEN ready 照片进入列表 THEN 页面按 `assetId` 获取短期签名地址并使用 `t-image` 显示 1:1 缩略图，支持 lazy、loading、error 占位。
- WHEN 缩略图签发或加载失败 THEN 只降级该条目的媒体占位，不把整个素材列表置为失败。
- WHEN 用户点击照片 THEN 继续使用现签地址预览；签名 URL 只在页面会话内缓存，重新加载可刷新。
- 视频没有可用缩略图时使用 TDesign 视频图标，PDF 使用文档图标；不得用 Emoji。

### 4.5 全页面批次

1. T0：接入与素材库 `pages/assets/index` 试点。
2. T1：四个 Tab 根页 `home / card-list / assets / mine` 的按钮、图片、Tab、反馈和空态。
3. T2：`pkg-actor-card` 创建 Hub、七步骤、生成页、观看页。
4. T3：`actor-profile/edit`、`pkg-profile` 四页、登录和实名认证页。
5. T4：`pkg-card` 历史详情与 `pkg-tools` 两页，清理仍可达页面的通用原生控件。
6. T5：删除已无消费者的通用 Kp 控件和 legacy 样式，完成全路由截图与交互回归。

每一批必须在 tasks.md 逐项关闭。只有 T0-T5 全部关闭、24 页迁移矩阵无 pending、产物和运行态证据齐全，才能宣称“整体更换完成”。

## 5. 非功能需求

- 微信基础库继续要求 >= 2.25.0，高于 TDesign 1.16.0 的最低要求 2.6.5。
- 素材列表每页最多 10 条；缩略图签发并发有界，单条失败隔离，不阻塞正文渲染。
- 主包和每个分包均小于 2 MB；T0 记录引入前后 apparent bytes，不用 npm 解包大小代替微信产物实测。
- UI 迁移不得改变后端请求体、响应兼容、数据库或发布顺序；前端可独立回滚到迁移前组件实现。
- 不允许构建或核验流程关闭、置顶、抢焦点或整屏控制微信开发者工具。

## 6. 约束与风险

1. `tdesign-miniprogram` 解包约 1.63 MB，必须按需打包；全局注册是发布阻断项。
2. 当前项目存在分包引用主包共享组件导致 `module not defined` 的历史问题；TDesign 接入必须以生成产物 `usingComponents` 和真实模块闭包为证据。
3. `dist/dev` 曾被 DevTools 缓存写回导致 scope hash 分叉；仍按 00-216 / 00-219 三侧核验。
4. 原生小程序组件事件结构可能与 Vue 组件不同；迁移时必须验证 `event.detail`、disabled、loading、open-type 和表单值透传。
5. 发版兼容评估：本 Spec 默认仅增加前端依赖和渲染实现，接口/数据库零变更；若缩略图后续改为列表接口直接返回，须另行补后端兼容设计后再实施。

## 7. 追溯

- 视觉合同：00-221、00-223、`docs/ui-style-guide-v3.md`。
- 素材库行为与私有签名地址：00-222。
- 分包与包体：00-05、00-209。
- 产物和 DevTools 缓存：00-216、00-219、00-224。
- 导航壳层：00-212。
