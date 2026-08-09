# 00-205 当前阶段小程序首页已创建作品瀑布流

> **状态：已降级为历史 Spec（`00-210` 轮次，用户裁决）。不再作为当前功能范围或门禁基线。**
>
> 降级原因：本 Spec 的实现载体 `pages/home/index.vue` 已被 `00-206 T7` 整体替换。首页现由
> Hero 卡 + `模板创建` 4 tab 网格构成，不存在本 Spec 描述的「阴阳鱼舞台之后的双列作品瀑布流」，
> 其依赖的 `00-201` 舞台前置条件同样已不存在。
> `scripts/verify-miniapp-home-portfolio-waterfall.mjs` 的 `19` 项断言因此恒红，已标注为历史脚本、
> 不接入 `package.json`、不作为门禁执行。
>
> 当前首页事实源：`00-206`（向导与首页改版）、`00-210`（模板区后端对接）。
> 历史边界：包体审计当时受既有 `actor-asset.js` 本地 URL 阻塞，该阻塞与首页无关，仍由 `00-204` 记录。

## 1. 概述

`pages/home/index` 已由 `00-201` 收口为 Hero、单张 `480rpx` 阴阳鱼创建舞台和两个既有创建入口。该页面目前在阴阳鱼舞台后结束，没有让演员快速看见自己已经真实创建的作品。

本 Spec 仅在当前阴阳鱼舞台**之后**增加一个低噪声的已创建作品双列瀑布流。它只显示当前已登录演员的真实手动分享卡和真实 AI 分享图；它不是新的作品集页面、创建入口、统计区或运营展示区。

`00-205` 仅取代 `00-201` 中“首页内容区在阴阳鱼舞台后结束”的边界。`00-201` 的 Hero、`480rpx` 舞台、阴阳鱼本地位图、AI / 手动双入口、身份跳转、原生 TabBar 与视觉合同继续有效。

## 2. 用户故事

作为已登录演员，我希望在首页创建舞台下方直接看到自己真实创建的 AI 分享图和手动分享卡，点击后进入各自已有详情页，而不是再看到虚构示例或多余说明。

作为游客或剧组账号，我希望首页保持可浏览且安静，不因这个私人作品区触发任何个人作品请求，也不显示其他演员的数据。

## 3. 功能需求

### 3.1 首页位置与既有结构

- WHEN 渲染 `pages/home/index` THEN 已创建作品区只能位于 `home-page__creation-stage` 之后，不能插入 Hero 内、阴阳鱼舞台内、两个创建入口之间或 TabBar 前的其它页面区域。
- WHEN 本轮实现首页 THEN 必须保留 Hero 文案「为每一次相遇 / 留下光影」与「用 AI 快速生成你的分享图」、`480rpx` 舞台高度、`/static/home/yin-yang-creation.png` 背景，以及 `goAiProfileCard()` / `goCardList()` 的既有身份分支和目标路由。
- WHEN 首页没有可展示的真实作品、正在读取、读取失败、游客或剧组账号进入 THEN 不渲染该区域，不出现标题、数量、空态、骨架屏、加载提示、重试按钮、示例卡、营销文案或其它新 UI。
- 本区域不得增加创建、编辑、删除、筛选、分享、跳转作品集或账号授权等新操作；唯一交互是点击真实卡片进入已有详情。

### 3.2 演员身份与个人数据边界

- WHEN `bootstrapSession()` 返回空用户或 `role === 2` 的剧组用户 THEN 首页必须立即清空本地作品数组，并在此边界之后不调用 `getMyShareCards()`、`getActorCardConfig()`、`listAiProfileCardArtifacts()` 或 `listAiProfileCardTasks()`。
- WHEN 当前用户是已登录演员 THEN 首页可调用既有只读前端 API：`GET /api/card/my-cards`、`GET /api/card/config`、`GET /api/ai/profile-card/artifacts` 和 `GET /api/ai/profile-card/tasks`。
- WHEN 页面重新显示、下拉刷新、身份变化或较旧异步请求在较新请求之后返回 THEN 旧作品数据不得继续留在页面或覆盖较新的结果；开始新一轮读取、游客 / 剧组分支和当前轮读取失败时均保持数组为空。
- 本轮不得修改 `pkg-card/portfolio/index.vue`、`pkg-card/ai-profile-card-detail/index.vue`、手动分享详情页、API 层、Store、路由注册、TabBar、后端接口、数据库、权限或真实作品的持久化数据。

### 3.3 真实作品适配规则

- 手动分享卡来自 `getMyShareCards().cards`。WHEN 卡片属于当前演员 THEN 每张手动卡都必须保留为一个首页项目；不得因其场景、是否默认卡、是否同时存在 AI 产物或是否缺少代表图而过滤掉。
- 官方 AI 产物来自 `listAiProfileCardArtifacts()`。WHEN 产物有 `generatedImageUrl`、有效 `shareCardId`，提供商不是 `mock`，且生成图不是源图的同一媒体 THEN 显示为 AI 项目。
- AI 任务只作为官方产物缺失时的可用兜底。WHEN 任务 `status === 'success'`、有生成图、提供商不是 `mock`、生成图不是源图且能从 `task.shareCardId` 或当前手动卡的 `templateSceneCode` 映射解析出有效 `shareCardId` THEN 显示为 AI 项目；WHEN 同一 `taskId` 已被官方 AI 产物表示 THEN 不得重复添加该任务兜底。
- AI 图预览必须复用 `buildAiProfileCardDisplayImageUrl()`，不能自行拼接 COS 图片处理参数。
- 手动卡预览必须按 `highlightedPhotos` 顺序取**第一个非空白** URL；WHEN 没有可用代表图或读取配置失败 THEN 复用既有 `KpShareSceneCover` 作为可见回退，不伪造图片 URL。
- 不得引入 mock、静态假作品、示例图片、外部占位图或与当前账户无关的数据。

### 3.4 瀑布流呈现与详情跳转

- WHEN 至少有一个真实项目 THEN 首页渲染无标题、无卡片说明文字的稳定双列瀑布流。两列等宽、各项目按原图自然高度纵向排列，图片使用 `widthFix`，卡片间距和圆角保持局部一致，不能因加载文案或动态标签改变列宽。
- WHEN AI 项目被点击 THEN 进入既有 `/pkg-card/ai-profile-card-detail/index` 详情路由，并携带对应 `shareCardId` 和既有详情加载器可消费的标识；官方 artifact 优先传 `artifactId`、缺失时传 canonical `taskId`，任务兜底传任务 `taskId`，query 名继续保持 `taskId`。
- WHEN 手动分享卡被点击 THEN 复用 `buildShareCardDetailPath({ shareCardId })` 进入既有手动分享详情路由。
- 本轮不得把 AI 项导向手动详情，也不得把手动卡导向 AI 详情；不得重写详情页或改变其 query 合同。

## 4. 非功能需求

- 读取过程必须静默：作品读取不得增加全屏 loading、Toast、错误面板或空状态。单个 AI 数据源失败应只少显示该来源；单个手动卡配置失败应保留该卡并落入 `KpShareSceneCover` 回退。
- 首页适配逻辑保持页面本地、只读且可测试，不为这一处轻量展示把 portfolio 领域重构为新的共享 Store 或修改既有作品集页面。
- 继续遵循 `SHARED_CONVENTIONS.md`、`00-201`、`00-187` 和 `00-192` 的会话 / 访客边界。
- 实现前后的静态门禁不得采用整文件快照；必须检查可理解的模板、数据、身份、过滤、路由和样式合同。

## 5. 验收清单

- [ ] 瀑布流只出现在阴阳鱼舞台之后，Hero、舞台、双入口和 TabBar 没有改变。
- [ ] 游客 / 剧组清空本地项目，且不会发出任何个人作品请求。
- [ ] 已登录演员只展示真实 AI 产物、合格任务兜底和全部真实手动卡。
- [ ] 官方 AI 产物与任务兜底按 `taskId` 去重；失败、mock、源图回显和无效项目不展示。
- [ ] 手动卡优先显示首个非空 `highlightedPhotos`，无图时显示 `KpShareSceneCover`。
- [ ] 页面没有作品区标题、空态、加载态、假数据或额外操作。
- [ ] AI / 手动项目分别进入已有 AI / 手动详情路由。
- [ ] `verify-miniapp-home-portfolio-waterfall.mjs` 在实现后通过，并继续保护 `00-201` 关键合同。
