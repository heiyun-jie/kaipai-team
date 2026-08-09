# 00-201 当前阶段小程序首页 AI 优先简化与阴阳鱼双入口

> **状态：已降级为历史 Spec（`00-210` 轮次，用户裁决）。不再作为当前功能范围或验收基线。**
>
> 降级依据：本 Spec 的实现载体 `pages/home/index.vue` 已被 `00-206 T7` 整体替换为 2.0 演员卡首页。
> 阴阳鱼创建舞台、`480rpx` 舞台高度、`1316x960` 位图、AI / 手动双透明入口均已不在运行态存在。
> 其验收断言绑定的是已被替换的旧首页结构，因此恒红，且**不可能**通过 —— 这是设计上的过期，不是缺陷。
>
> 当前首页事实源见 `00-206`（结构）与 `00-210`（模板区后端对接）。
> 历史结论、`600rpx → 540rpx → 480rpx` 的幅度调整过程与当时证据继续保留在本目录，仅作追溯用。

## 1. 概述

用户反馈现有 `pages/home/index`（首页）「看着不够简单、操作也不够简单」，希望降低首屏认知负担、明确唯一主动作。

排查现状（`kaipai-frontend/src/pages/home/index.vue`）确认存在三处并列「创建」入口、主 CTA 沉在首屏之下、以及一段重型操作指南视频：

1. `home-page__stats-strip` 内的黑色 `AI生成分享图 ›` pill（`goAiProfileCard`）。
2. `home-page__section--guide` 底部主 CTA `开始创建分享页`（`goCardList`）。
3. `home-page__section--styles` 内可点击的风格卡（`handleTemplateClick` → `style-detail`）。

三者视觉权重接近、去向不同，用户无法一眼判断「先点哪个」。同时 `操作指南` 区包含一段 `HOW-TO · 02:34` 视频封面（`openGuideVideo`），占据大量首屏纵向空间，把真正的行动入口继续下压。

经核实，AI 出图链路为**真实生产能力**（后端 `AiProfileCardController` + `AiProfileCardServiceImpl` + 异步生成 + 腾讯混元 / OpenAI / kplyyk 多 provider + 腾讯 OCR 质检；前端 `pkg-card/ai-profile-card/index` 全实现），具备作为首屏主推入口的资格。

本 Spec 按用户选定的「AI 优先」方向，把首页收口为**单一主动作 = AI 生成分享图**，并移除重型指南视频，降低首屏高度与决策分叉。首轮简化后首页仍保留「手动选风格」三卡区域；用户在 `2026-07-28` 进一步明确要求删除该区域，改为一张视觉权重更低的「手动创建分享」入口，统一进入既有创建分享页流程。

> **诚实语义边界（关键）**：AI 出图链路本身有三道前置门槛——实名认证、已有演员档案、必须上传一张分析图，且生成为**异步**（回执为「约 10 分钟后到已创建分享查看」）。因此首页主入口是「进入 AI 生成流程」的清晰引导，**不得承诺「一键即时出图」**。文案需如实预告前置条件，避免新用户点击后连撞实名 / 档案 / 上传三道墙而体验更差。

## 2. 用户故事

作为首次进入首页的用户，我一眼就能看到唯一的主行动「AI 生成分享图」，并明白它需要先实名并上传一张照片，不会被多个并列按钮干扰。

作为想手动创建分享页的用户，我能在统一阴阳鱼画面的右下区域找到「手动创建分享」次级入口，并从统一创建流程中选择风格和作品。

作为未登录用户，我可以先浏览首页，不会被自动拉去登录；只有主动点击 AI 生成或手动创建分享等账号入口时才跳登录。

## 3. 功能需求

### 3.1 AI 生成分享图作为首屏唯一主动作

**描述**：首页首屏（hero 之后、无需滚动即可见）提供唯一视觉主入口「AI 生成分享图」，点击进入 `pkg-card/ai-profile-card/index`。移除与之并列竞争的第二主 CTA（原 `开始创建分享页` 独立黑按钮）与 `stats-strip` 内的 `AI生成分享图 ›` pill，避免同屏出现两个及以上等权重「创建」按钮。

**验收标准**：

- WHEN 演员用户进入首页 THEN 首屏可见唯一主 CTA「AI 生成分享图」，点击调用 `goAiProfileCard()` 进入 `/pkg-card/ai-profile-card/index`。
- WHEN 首页渲染 THEN 不再存在原 `home-page__ai-link`（stats-strip 内 AI pill）与 `home-page__guide-cta`（`开始创建分享页` 按钮）两个并列创建入口同时出现。
- WHEN 统计首屏「创建 / 生成」类主按钮 THEN 数量为 1。

### 3.2 主入口诚实前置提示

**描述**：主 CTA 附带一句如实说明前置条件的辅助文案，明确「实名 + 上传一张照片 + AI 生成」的预期，不使用「即时」「秒出」「一键出图」等承诺即时结果的措辞。

**验收标准**：

- WHEN 主 CTA 展示 THEN 同屏存在前置提示文案，语义包含「实名」与「上传照片」两项前置条件（如「实名后上传一张照片，AI 为你生成分享图」）。
- WHEN 主 CTA 文案渲染 THEN 不包含「秒出」「即时」「一键出图」等承诺即时出图的措辞。

### 3.3 删除手动选风格区域，新增阴阳鱼双入口

**描述**：完整删除首页 `home-page__section--styles`「手动选风格」标题、英文副标题、三张 `KpShareSceneCard` 及其加载 / 空态展示。在 Hero 下方新增一个完整、统一的「阴阳鱼」背景舞台，而不是继续展示上下两张卡。阴阳鱼的曲线、鱼身、鱼眼与纸张质感全部固化在项目内 PNG 位图背景中：黑鱼位于左上，米白鱼位于右下。页面元素只叠放左上 AI 文案 / 透明点击区和右下手动创建文案 / 透明点击区，不得再用 `view`、伪元素、圆形、`clip-path` 或背景色拼接鱼身。左上入口复用 `goAiProfileCard()`；右下入口标题明确为「手动创建分享」，复用 `goCardList()` 进入 `/pkg-card/card-list/index`。

**验收标准**：

- WHEN 首页渲染 THEN 不再存在「手动选风格」/ `SELECT A STYLE`、`home-page__section--styles`、`home-page__style-grid` 或 `KpShareSceneCard`。
- WHEN 首页渲染 THEN 双入口视觉上只有一张完整背景图，不出现上下两张独立卡片、分隔边框或卡片间距；阴阳鱼黑色主体位于左上、米白主体位于右下。
- WHEN 核对首页源码与构建产物 THEN 阴阳曲线、鱼身和鱼眼来自 `/static/home/yin-yang-creation.png` 背景图，不存在 `home-page__ai-fish-lobe`、`home-page__manual-fish-lobe`、独立阴阳圆章、圆形徽记或其它 CSS 拼形节点。
- WHEN 用户点击背景舞台的左上 AI 区 / 右下手动区 THEN 分别命中对应透明点击区；两区不重叠、无第三个点击处理器，分别调用 `goAiProfileCard()` / `goCardList()`。
- WHEN 两组文案渲染 THEN AI 内容位于左上黑色安全区并使用浅色文字，手动内容位于右下米白安全区并使用深色文字，不压住背景图中的鱼眼或 S 形主体。
- WHEN 首页在标准 `750rpx` 画布渲染 THEN 阴阳鱼舞台高度固定为 `480rpx`；背景位图为 `1316x960`，与 `658rpx x 480rpx` 可见舞台保持同一宽高比，不得通过纵向拉伸压扁鱼身。
- WHEN 舞台高度收紧 THEN 左上 / 右下透明点击区仍各占 `240rpx` 且互不重叠，入口文字保持完整可读、点击范围不因压缩失效。
- WHEN 首页渲染 THEN 手动入口标题为「手动创建分享」，辅助文案表达选择风格与作品，右下透明点击区具备完整且稳定的触达范围。
- WHEN 已登录演员用户点击手动创建入口 THEN 调用 `goCardList()` 并进入 `/pkg-card/card-list/index`。
- WHEN 未登录用户点击手动创建入口 THEN 走 `goLogin()`；WHEN 剧组用户点击手动创建入口 THEN 走 `goMine()`（继承 `00-187` 与既有账号边界）。

### 3.4 移除重型操作指南视频

**描述**：移除 `操作指南` 区的 `HOW-TO · 02:34` 视频封面（`home-page__guide-stage` / `openGuideVideo` 入口），减少首屏纵向占用。流程说明分别收进统一阴阳鱼画面的两个内容区：左上 AI 区展示「选风格 · 传照片 · AI 生成」，右下手动区展示「选风格 · 传作品 · 保存分享」，不再承载视频播放入口。

**验收标准**：

- WHEN 首页渲染 THEN 不再展示 `操作指南` 视频封面与 `▶` 播放触发（`openGuideVideo`）。
- WHEN 首页构建产物 THEN 首页不再包含跳转 `/pkg-tools/video-player/index?type=guide` 的引导视频入口。
- WHEN 首页展示两条三步流程说明 THEN 均以纯文字轻量形式呈现，不含视频播放态。

### 3.5 继承 00-187 未登录浏览与账号门禁，不得回归

**描述**：首页简化不得破坏 `00-187` 已建立的登录门禁边界：未登录用户可浏览首屏，不自动跳登录 / 不自动触发授权；仅在主动点击账号相关入口时跳登录。

**验收标准**：

- WHEN 未登录用户进入首页 THEN 不调用 `goLogin()` / `reLaunch('/pages/login/index')`（仅浏览态）。
- WHEN 未登录用户点击 AI 主 CTA / 手动创建分享入口 THEN 才跳登录。
- WHEN 已登录演员用户进入首页 THEN 继续 `bootstrapSession()` 与 `syncActorRuntimeState()` 同步；首页不再为已删除的风格区额外请求 `getMyShareCards()`。
- WHEN 剧组用户进入首页 THEN AI 主 CTA / 创建类入口继续走 `goMine()`（不进入 AI 生成）。
- WHEN 运行 `00-187` 既有验收脚本 THEN 仍通过（不回归）。

### 3.6 删除首页“我的数据”轻链接

**描述**：删除首页原统计条中的 `我的数据 ›` 轻链接，不再在 `pages/home/index` 重复提供个人数据入口。底部 TabBar 的“我的”入口与 `pages/mine/index` 页面保持不变；`goMine()` 继续供剧组账号动作分支复用。

**验收标准**：

- WHEN 首页渲染 THEN 不再展示 `我的数据 ›`。
- WHEN 首页构建产物生成 THEN `pages/home/index` 的 WXML / WXSS 不再包含原 `home-page__stats-link` / `home-page__stats-actions` 统计条入口结构。
- WHEN 用户点击底部 TabBar“我的” THEN 仍可进入 `pages/mine/index`。
- WHEN 剧组账号触发 AI 主 CTA 或手动创建分享入口 THEN 仍可通过 `goMine()` 进入“我的”页。

## 4. 非功能需求

- 不改动 `pkg-card/ai-profile-card/index` 页内生成逻辑与门禁（由 `00-168` / `00-182` 等治理），本轮只改首页入口与信息层级。
- 不改后端 AI 生成链路。
- 不新增 mock；未登录 / 访客态不得伪造用户卡片、邀请数、等级等个人数据。
- 不新增头像 / 昵称授权入口。
- 删除风格区后同步删除其专用 API 请求、状态、组件依赖和辅助函数，不保留不可见的模板加载副作用。
- 首页改动后必须执行 `npm run build:mp-weixin`，并核对 `dist/build/mp-weixin` 与 `dist/dev/mp-weixin` 关键字进入产物。
- `/static/home/yin-yang-creation.png` 必须是经过压缩的本地 `1316x960` 位图，不使用远程 URL、base64 或运行时下载；新增资源纳入 `00-05` 的单包 2MB 审计。

## 5. 约束条件

- 本轮仅修改 `kaipai-frontend/src/pages/home/index.vue`、`kaipai-frontend/src/static/home/yin-yang-creation.png` 及对应 SCE 文档，不外溢到其它页面。
- 阴阳鱼只能作为统一舞台的 CSS `background-image`；不得使用独立图片节点承载整图，不得用可见 `view` / 伪元素重画鱼身或鱼眼，也不得为两个透明点击区设置各自的卡片背景。
- 主入口去向复用既有 `goAiProfileCard()`，其 visitor→`goLogin` / crew→`goMine` / actor→`ai-profile-card` 分支保持不变。
- 手动创建分享入口复用既有 `goCardList()`，其 visitor→`goLogin` / crew→`goMine` / actor→`card-list` 分支保持不变。
- 删除 `handleTemplateClick()`、`templateItems`、三风格 meta 与首页 `getMyShareCards()` 消费；目标页内的选风格能力和数据来源不变。
- 默认全程在当前分支开发，不新建 / 切换分支。
