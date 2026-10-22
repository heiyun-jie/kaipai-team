# 3.0 小程序最终 UI 与操作体系深度调查 - 技术设计

_Requirements: ALL_

## 1. 调查方法与证据源

本轮按以下顺序交叉核对：

1. 读取 `pages.json`，统计真实页面与分包。
2. 逐页读取 `src/pages`、`src/pkg-actor-card`、`src/pkg-card`、`src/pkg-profile`、`src/pkg-tools` 的模板、脚本和样式。
3. 扫描页面、组件和全局 SCSS 的颜色字面量与 `$kp-*` Token 使用。
4. 扫描 `@click`、`open-type`、`uni.navigate*`、上传、预览、删除、排序和空态 handler。
5. 将源码行为与桌面视觉参考目录的五张 PNG 逐张对照。
6. 回看 00-206、00-210、00-212、00-213、00-214、00-215、00-218、00-219，区分已经收口的问题与仍然有效的缺口。

## 2. 参考图逐页对照矩阵

| 参考图 | 路由 | 当前视觉 | 当前操作 | 调查结论 | 优先级 |
|---|---|---|---|---|---|
| `01-新版首页.png` | `pages/home/index` | 蓝白结构已接近；Hero 右侧仍是 CSS 简化插画，TabBar 位图为旧橙色 | 草稿、风格 Tab、模板网格可点；模板点击只传 style，不传具体背景 id | **部分完成**：需补模板选择语义、Token、TabBar 和插画资产策略 | P0 |
| `02-AI创建流程.png` | `pkg-actor-card/create/index` | 白底、蓝色进度和底部 CTA 已接近；步骤图标仍为数字圆点 | 7 步可跳转，完成度和生成门禁已有合同 | **部分完成**：需要最终图标、状态、空态、错误与返回规范 | P0 |
| `03-参演作品.png` | `pkg-actor-card/step-works/index` | 蓝白卡片结构已接近；缺少图稿中的「管理剧照」视觉入口 | 真实经历读取、新增、选择、添加、删除和保存已有；无排序，替换需手动删后重加 | **部分完成**：需把剧照管理、封面、替换、排序交互明确化 | P0 |
| `04-生活照片.png` | `pkg-actor-card/step-photos/index` | 网格、数量提示、删除和下一步已接近 | 只有手机上传；素材库入口被移除；排序未实现 | **功能未闭合**：图稿承诺的素材库选择和排序必须决策并实现或重新设计 | P0 |
| `05-个人中心.png` | `pages/mine/index` | 卡片层级和蓝色进度已接近；图标使用 Emoji，非图稿线性图标 | 资料入口、实名认证、退出可操作；帮助与反馈、设置只弹「即将开放」；统计项仅演员卡可点 | **部分完成**：需统一图标、处理死控件、补统计入口语义 | P0 |

## 3. 全路由主题与完成度矩阵

### 3.1 主包

| 路由 | 文件 | 主题扫描 | 3.0 状态 | 主要问题 |
|---|---|---|---|---|
| `pages/home/index` | `src/pages/home/index.vue` | 蓝白硬编码 | 部分完成 | 模板点击未携带具体背景；Hero 插画为 CSS 占位；TabBar 图标橙色 |
| `pages/login/index` | `src/pages/login/index.vue` | 旧棕米色 | 未调整 | 与参考蓝白主题断裂；需保留手机号、验证码、微信授权和协议流程 |
| `pages/actor-profile/edit` | `src/pages/actor-profile/edit.vue` | 旧 Token 棕米色 | 未调整 | 表单信息密度和导航风格未统一；`?tab=experience/intro` 查询参数未被 `onLoad` 消费 |
| `pages/mine/index` | `src/pages/mine/index.vue` | 蓝白硬编码 | 部分完成 | Emoji 图标、死控件、统计交互不完整 |
| `pages/card-list/index` | `src/pages/card-list/index.vue` | 蓝白硬编码 | 未纳入参考图 | 已发布/草稿操作可用，但草稿没有删除；卡片操作布局需 3.0 定稿 |
| `pages/assets/index` | `src/pages/assets/index.vue` | 无独立 UI | 结构风险 | 只有 `redirectTo('/pkg-profile/assets/index')`，进入素材库后可能失去原生 Tab 壳层 |

### 3.2 演员卡分包

| 路由 | 文件 | 主题扫描 | 3.0 状态 | 主要问题 |
|---|---|---|---|---|
| `pkg-actor-card/create/index` | `src/pkg-actor-card/create/index.vue` | 蓝白硬编码 | 部分完成 | 缺少最终步骤图标；状态颜色、固定 CTA、错误态需统一 |
| `pkg-actor-card/step-visual/index` | `src/pkg-actor-card/step-visual/index.vue` | 蓝白硬编码 | 主题已迁移，未定稿 | 需要与最终视觉系统统一主视觉、背景库、扩图 loading/失败态 |
| `pkg-actor-card/step-profile/index` | `src/pkg-actor-card/step-profile/index.vue` | 蓝白硬编码 | 主题已迁移，未定稿 | 需要与个人档案编辑页统一字段、同步提示、校验和导航 |
| `pkg-actor-card/step-works/index` | `src/pkg-actor-card/step-works/index.vue` | 蓝白硬编码 | 参考图部分完成 | 无显式剧照管理/排序；需要确认新增作品与经历快照的最终反馈 |
| `pkg-actor-card/step-photos/index` | `src/pkg-actor-card/step-photos/index.vue` | 蓝白硬编码 | 参考图部分完成 | 素材库选择和排序缺失，图稿中的双入口未兑现 |
| `pkg-actor-card/step-video/index` | `src/pkg-actor-card/step-video/index.vue` | 蓝白硬编码 | 主题已迁移，未定稿 | 已上传只有删除，没有预览/替换，00-206 G6 仍有效 |
| `pkg-actor-card/step-attachment/index` | `src/pkg-actor-card/step-attachment/index.vue` | 蓝白硬编码 | 主题已迁移，能力已接通 | UI 文案必须继续以真实 PDF 合同为准，不恢复后端不支持的 PPT/PPTX；观看者消费仍需另立项 |
| `pkg-actor-card/step-settings/index` | `src/pkg-actor-card/step-settings/index.vue` | 蓝白硬编码 | 主题已迁移，未定稿 | 用上下箭头实现排序，非图稿语义中的拖拽；需确认 3.0 是否保留等效交互 |
| `pkg-actor-card/generate/index` | `src/pkg-actor-card/generate/index.vue` | 蓝白硬编码 | 主题已迁移，能力未完全定稿 | 后端 `ActorCardGenerateService` 仍以主视觉 URL 作为长页预览占位，最终 UI 不能把占位图当真实生成结果 |
| `pkg-actor-card/view/index` | `src/pkg-actor-card/view/index.vue` | 蓝白硬编码 | 未纳入参考图 | 公开观看页需补 3.0 阅读体验、附件/视频异常态和分享落地验证 |

### 3.3 其他分包

| 路由 | 文件 | 主题扫描 | 3.0 状态 | 主要问题 |
|---|---|---|---|---|
| `pkg-card/verify/index` | `src/pkg-card/verify/index.vue` | 旧棕米色 | 未调整 | 实名门禁是核心能力，但页面视觉和共享输入/按钮组件仍旧主题 |
| `pkg-card/ai-profile-card-detail/index` | `src/pkg-card/ai-profile-card-detail/index.vue` | 旧棕米色 | 历史页面待裁决 | 00-217 恢复的 1.0 分享详情仍可被旧链接访问；需决定 3.0 保留、重皮肤或退场 |
| `pkg-tools/webview/index` | `src/pkg-tools/webview/index.vue` | 旧棕米色 | 未调整 | 登录协议/帮助等 WebView 外壳仍使用旧主题，需与 3.0 导航和错误页统一 |
| `pkg-tools/video-player/index` | `src/pkg-tools/video-player/index.vue` | 旧棕米色 | 未调整 | 素材库视频预览可达，播放器外壳仍旧主题 |
| `pkg-profile/import-review/index` | `src/pkg-profile/import-review/index.vue` | 旧 Token 棕米色 | 未调整 | 智能导入复核流程可达，但表单、候选卡和导航未统一 |
| `pkg-profile/assets/index` | `src/pkg-profile/assets/index.vue` | 旧 Token 棕米色 | 未调整 | 素材库真实主体，当前由 Tab 空壳跳转进入；需要成为 3.0 的正式 Tab 根页 |

## 4. 主题残留证据

### 4.1 全局 Token 与 Mixin

`src/styles/_tokens.scss` 仍以 `#1D1814`、`#2A221D`、`#8C6F4F`、`#F5F3EE`、`#FBFAF6` 为主色；`_mixins.scss` 的品牌渐变、固定操作栏和主按钮 shell 仍引用棕色、砂金色和米色。只改 Token 会影响旧页，但不会替换 13 个蓝白页中的硬编码颜色，必须制定一次性迁移策略。

### 4.2 共享组件

以下组件存在旧主题字面量或旧 Token 依赖，属于全局视觉放大器：

- `KpButton.vue`
- `KpBottomActionBar.vue`
- `KpConfirmDialog.vue`
- `KpIdentityStatusCard.vue`
- `KpStatusTag.vue`
- `KpInput.vue`

`KpPageNav.vue` 已使用蓝白值，但仍应纳入统一 Token，而不是成为另一套硬编码例外。

### 4.3 TabBar 图标

`pages.json` 的 `selectedColor` 已为蓝色，但 `src/static/tabbar/home-active.png`、`rank-active.png`、`mine-active.png` 的位图实际为橙色；`rank.png` 同时被“名片夹”和“素材库”复用。原图中的四项 Tab 是蓝色线性图标体系，3.0 需要四个独立的未选中 / 选中资源，不能依赖 `selectedColor` 重新着色 PNG。

### 4.4 页面级硬编码

13 个蓝白页面大量直接写入 `#2F6BFF`、`#EEF2FF`、`#F6F7F9` 等值，造成颜色已经“看起来一致”但无法被主题治理；首页仍有 `#8E8478`、草稿提示仍有独立米黄色值。3.0 实现必须先把这些值归入 Token，再继续调整视觉。

## 5. 操作风险矩阵

| 风险 | 证据 | 影响 | 3.0 处置 |
|---|---|---|---|
| 素材库 Tab 跳出 Tab 壳层 | `pages/assets/index.vue` 仅 `redirectTo` 分包页 | 用户返回和 Tab 状态不稳定 | 让素材库成为正式 Tab 根页，或建立可验证的 Tab 保持方案 |
| 模板点击语义丢失 | `home/index.vue` 调用 `handleTemplateCreate(activeStyle)`，未传 `img.id` | 点击任意模板可能复制任意同风格卡，用户选择不被保留 | 以背景 id / 模板 id 建立明确的创建合同 |
| 草稿管理不完整 | `card-list/index.vue` 只有预览、分享、复制创建，没有删除 | 草稿无法清理，名片夹操作不闭合 | 增加删除确认、失败重试和列表刷新 |
| 生活照片双入口与排序缺失 | `step-photos/index.vue` 只保留手机上传，排序文案改为现状陈述 | 参考图操作与实际能力不一致 | 实现素材库选择和排序，或正式改图并回填产品决策 |
| 剧照管理不完整 | `step-works/index.vue` 只有添加 / 删除，替换需要手工绕行 | 封面和剧照管理成本高 | 明确替换、排序、封面变更和空态反馈 |
| 视频预览 / 替换缺失 | `step-video/index.vue` 已上传卡只有删除 | 用户无法确认视频内容，替换不直观 | 增加预览、替换和上传失败恢复 |
| 个人页死控件 | `mine/index.vue` 的帮助与反馈、设置只显示“即将开放” | 违反最终 UI 的可操作性要求 | 建立真实页面或移除入口，不能保留假操作 |
| 个人资料子入口参数未消费 | `mine/index.vue` 传 `?tab=experience/intro`，`actor-profile/edit.vue` 的 `onLoad` 不读取参数 | 点击“演艺经历 / 自我介绍”仍落到默认位置 | 建立页内锚点 / Tab 合同或改为准确入口 |
| 生成结果仍为占位 | 后端 `ActorCardGenerateService` 注释明确写着真实长页引擎 TODO | 3.0 预览体验无法作为最终稿验收 | 将生成引擎与 UI 占位态分开验收，禁止以主视觉图冒充长页生成 |

## 6. 3.0 页面壳层设计原则

### 6.1 根页面

- 四项原生 Tab 固定为：首页、名片夹、素材库、个人。
- 每个 Tab 必须拥有可直接渲染的根页面，不用中间重定向页替代。
- 页面背景以白色为主，列表密集场景使用 `surface-muted`，不再使用深色 Hero + 米色内容的旧骨架。
- 顶部标题、胶囊避让、返回按钮继续复用 `KpPageNav`，但颜色和字重纳入 Token。

### 6.2 向导页面

- Hub 和 7 个步骤共用一套进度、导航、底部 CTA、安全区和错误反馈。
- 图稿中的大标题、描述、卡片和蓝色主 CTA 是视觉基线；功能差异必须在 Spec 中显式说明。
- 资源操作必须展示上传中、失败、重试、替换、删除和回读结果，不允许静默丢数据。

### 6.3 共享状态

- 完成、待确认、未添加、加载、失败、空态统一使用状态 Token 和 `KpStatusTag`。
- 所有固定底部操作预留安全区；页面内不得重复渲染同一组主 CTA。
- 所有按钮和可点击卡片必须定义按下态、loading 锁定和失败反馈。

## 7. 实施顺序

1. P0：主题 Token、共享组件、四项 TabBar 图标、Tab 壳层与素材库根页。
2. P0：五张参考图对应的首页、创建 Hub、参演作品、生活照片、个人中心。
3. P0：名片夹、向导剩余步骤、生成 / 观看者页面的操作闭环。
4. P1：登录、演员档案、实名认证、资料库、智能导入、视频播放器、WebView 统一皮肤。
5. P2：旧版分享详情页的保留 / 重皮肤 / 退场裁决，以及真实长页生成结果接入。

