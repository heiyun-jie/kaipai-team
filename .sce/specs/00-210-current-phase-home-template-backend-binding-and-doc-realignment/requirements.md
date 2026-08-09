# 00-210 首页模板区后端对接与历史文档校正 — Requirements

> 阶段：当前主线
> 上游：`00-206`（首页替换与向导主线）、`00-209`（剧组退场与孤儿路由删除）
> 关联：`00-110`（删除门禁）、`00-27`（前端架构）

## 1. 背景

用户提出三项要求：

1. 后端也需要进行整理
2. 首页以当前样式对接后端接口
3. 其他旧的文档需要更新

用户已就范围给出三项决策，本 Spec 以此为约束：

| 决策项 | 用户选择 |
|--------|---------|
| 后端 recruit / crew 范围 | **后端代码不动，只做文档标注** |
| 首页 tab 行为 | **tab 过滤网格** |
| 数据库 | **不动表，只退代码** |

## 2. 已核实的关键事实

### 2.1 系统内存在两套独立风格词表（本 Spec 最重要的前置结论）

这两套词表仅在 `classic` / `urban` 上重合，**不可互换**。混用会造成运行态数据错位。

| | 词表 A：演员卡风格 | 词表 B：分享卡场景码 |
|---|---|---|
| 取值 | `classic` / `urban` / `ancient` / `fresh` | `classic` / `costume` / `urban` / `commercial` / `artistic` |
| 权威依据 | `V20260731_001__actor_card_tables.sql` 中 `actor_card.style` 与 `actor_card_background.style` 的 DDL 注释均为 `classic\|urban\|ancient\|fresh`；`V20260731_002__actor_card_background_seed.sql` 实际种子行为 `classic`×3 / `urban`×3 / `ancient`×2 / `fresh`×2 | `TemplateSceneCodeValidator.ALLOWED_TEMPLATE_SCENE_CODES` |
| 后端出口 | `GET /api/actor-card/background-library?style=`（`ActorCardController`，`@Operation` 摘要明确写 `classic\|urban\|ancient\|fresh`） | `GET /api/card/scene-templates`（`CardController`） |
| 前端消费方 | `pages/home/index.vue` 的 `goCreateWithStyle`、`pkg-actor-card/step-visual`、`pages/card-list` | `utils/share-card-mvp.ts`、`utils/level.ts` |
| 落库字段 | `actor_card.style` | `card_scene_template.template_scene_code` |

**推论**：首页「模板创建」区点击后走 `?style=` → `initDraft(style)` → `saveStep({ style })` → 写入 `actor_card.style`，因此首页必须使用**词表 A**。`ancient` / `fresh` 是词表 A 的合法值，不是非法值。

> 修正记录：本 Spec 初版曾判定 `ancient` / `fresh` 为非法场景码并据此改用 `/api/card/scene-templates`。该判断错误——它把词表 B 的校验器套到了词表 A 的字段上。按初版实现会使首页向 `actor_card.style` 写入 `costume` 等值，导致 `step-visual` 挂载时 `loadBgLibrary('costume')` 命中 0 行种子数据、背景图库空白且无 tab 选中，即向导第一步被破坏。已回滚并按本文修正后的口径重做。

### 2.2 首页模板区确实未对接后端

`pages/home/index.vue` 的 `styles` 数组为硬编码 4 项且 `previewUrl` 恒为空字符串，因此运行态呈现 4 个空占位框——与用户截图一致。缺失的是**预览图数据**。

词表 A 的预览图数据源是 `actor_card_background` 表，通过 `GET /api/actor-card/background-library?style=` 读取，返回 `images[] = { id, imageUrl, thumbnailUrl, sortOrder }`。该封装在前端已存在：`src/api/actor-card.ts` 的 `getBackgroundLibrary(style)`。**不允许新建接口或新建 api 封装。**

### 2.3 背景图库需要鉴权

`SecurityConfig` 的 GET `permitAll()` 白名单与 `WHITE_LIST` 均不含 `background-library`，故该接口落入 `anyRequest().authenticated()`。游客无法读取。

（对比：`/api/card/scene-templates` 在白名单内，游客可读。但它属词表 B，不能用于首页。）

### 2.4 首页下拉刷新配置缺处理器

`pages.json` 中 `pages/home/index` 配置了 `enablePullDownRefresh: true`，但页面未注册 `onPullDownRefresh`，也无 `uni.stopPullDownRefresh()` 调用。微信不会自动收起加载圈。属既存缺陷，且正落在本次改动的加载链路上。

### 2.5 后端 recruit / crew 仍被后台在用

`kaipai-admin` 有 3 个在用视图（`views/recruit/ProjectsView.vue` / `RolesView.vue` / `AppliesView.vue`）、在用路由与在用菜单组「招募治理」，并调用 `/admin/recruit/*` 与 `/admin/system/roles/recruit-governance-matrix`。`/recruit` 位于 `adminToolingRoutePrefixes`（工具层），不在 7 页正式导航主线内——这与正式导航不含它是一致的，不是缺陷。

**因此这部分后端不是死代码，不得按「无引用即可删」处理。**

### 2.6 文档漂移已量化

| 文档 | 提及页面路径 | 有效 | 失效 | 未记录的真实页面 |
|------|------------|------|------|----------------|
| `docs/product-design.md` | 22 | 7 | **15** | **13** |
| `docs/dev-playbook.md` | 6 | 3 | **3** | — |

`docs/product-design.md` 另有事实性错误：§5.3 称「当前底部 Tab 只有两个」，真实为 4 个。

真实注册态权威值（`kaipai-frontend/src/pages.json`）：**20 页 / 4 tab**。主包 6 页；`pkg-actor-card` 9 页、`pkg-card` 1 页、`pkg-tools` 2 页、`pkg-profile` 2 页。tabBar 为 `首页 / 名片夹 / 素材库 / 个人`。

未记录的 13 个真实页面：`pages/assets/index`、`pages/card-list/index`、`pkg-actor-card/*` 全部 9 页、`pkg-profile/assets/index`、`pkg-profile/import-review/index`。

## 3. 需求

### 3.1 首页模板区对接后端

**用户故事**：作为演员，我希望首页「模板创建」区展示真实的风格预览图，而不是 4 个空白框。

- WHEN 已登录用户进入首页 THEN 模板区必须调用 `getBackgroundLibrary(activeStyle)` 并渲染返回的背景图。
- WHEN 未登录访客进入首页 THEN 因接口需鉴权，模板区必须给出可点击的登录引导，不得静默空白、不得报错。
- WHEN 请求失败 THEN 必须给出可重试入口，不得静默。
- WHEN 渲染卡片 THEN 图片优先取 `thumbnailUrl`，缺失时回退 `imageUrl`。

**验收标准**：产物中 `pages/home/index.js` 出现 `background-library` 调用链（`require api/actor-card` + `getBackgroundLibrary`）。

### 3.2 tab 过滤网格

**用户故事**：作为演员，我希望点击风格 tab 后网格只显示该风格的内容。

- WHEN 点击某 tab THEN 网格只渲染该风格的背景图集合。
- WHEN 同一风格返回多张 THEN 全部渲染（种子数据下为 2–3 张），不得假设固定 4 格。
- WHEN 重复点击当前 tab THEN 不重复发起请求。
- WHEN 已加载过某风格 THEN 切回时使用缓存，不重复请求。

**验收标准**：切换 tab 后网格渲染集合随之变化。

### 3.3 词表纯度

- WHEN 首页发出 `?style=` THEN 取值必须属于词表 A。
- WHEN 检查首页产物 THEN 不得出现词表 B 专有值（`costume` / `commercial` / `artistic`）。
- 首页、`step-visual`、`card-list` 三处标签词表必须一致。

**验收标准**：首页产物中词表 B 专有值 0 命中；`ancient` / `fresh` 存在（属词表 A，正确）。

### 3.4 下拉刷新闭合

- WHEN 用户下拉首页 THEN 必须重新拉取草稿与当前风格背景图，并在 `finally` 中显式 `uni.stopPullDownRefresh()`。

**验收标准**：产物中出现 `stopPullDownRefresh`。

### 3.5 视觉不变

- 现有 SCSS 类名与布局全部保留：`home-v2__style-tabs`、`__style-tab`、`--active`、`__style-grid`（`1fr 1fr` / `gap 16rpx`）、`__style-card`、`__style-img-wrap`（`aspect-ratio 3/2`）、`__style-img`、`--placeholder`、`__style-label`。
- 允许新增的仅为空态样式 `__style-empty` / `__style-empty-text`。
- 4 个 tab 文案保持 `经典 / 都市 / 古风 / 清新`。

**验收标准**：不得删除或重命名既有类名。

### 3.6 后端整理 = 仅文档标注

- WHEN 处理 recruit / crew 后端 THEN 不修改任何后端 Java 代码，不新增 / 不修改 / 不删除数据库表。
- 必须在文档中标注：小程序侧 `/crew`、`/project`、`/role`、`/apply` 已无小程序消费方（历史能力）；`/admin/recruit/*` 与 `/admin/system/roles/recruit-governance-matrix` 对 `kaipai-admin` 工具层**仍在用**。

**验收标准**：`kaipaile-server` 工作区无改动。

### 3.7 历史文档校正

- `docs/product-design.md`：清除 15 个失效路径、补齐 13 个真实页面、修正 tab 数量为 4、页面清单与真实注册态一致。
- `docs/dev-playbook.md`：清除 3 个失效路径。
- `.sce/steering/CURRENT_CONTEXT.md`：从停滞的 V7.7 推进到含 `00-206` 至 `00-210` 的基线。
- **不改写** `docs/archive/**` 与 `docs/superpowers/plans/**`（历史留档）。

**验收标准**：两份现行文档中失效路径 0 命中；`npm run audit:steering` 通过。

## 4. 非目标

- 不新建后端接口、不改后端代码、不动数据库表
- 不统一两套词表（属独立治理议题，需单独 Spec）
- 不改动 `step-visual` / `card-list`（它们词表已正确）
- 不改 tabBar 结构
- 不重写历史归档文档
