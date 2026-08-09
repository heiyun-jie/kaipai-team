# 00-210 设计 — 首页模板区后端对接 + 文档口径归位

## 0. 本设计的前置纠正

本 Spec 初稿把首页模板区的数据源判定为 `/api/card/scene-templates`（分享卡场景模板），并把 `ancient` / `fresh` 判定为「非法场景码」。**该判定错误，已作废。**

作废依据（全部为已核实事实）：

| 证据 | 位置 | 内容 |
|------|------|------|
| DDL 注释 | `V20260731_001__actor_card_tables.sql:11` | `` `style` VARCHAR(30) ... COMMENT '风格: classic\|urban\|ancient\|fresh' `` |
| DDL 注释 | `V20260731_001__actor_card_tables.sql:64` | `actor_card_background.style` 同样注释为 `classic\|urban\|ancient\|fresh` |
| 种子数据 | `V20260731_002__actor_card_background_seed.sql` | style 取值分布：`classic`×3 / `urban`×3 / `ancient`×2 / `fresh`×2 |
| 后端接口注释 | `ActorCardController:85` `@Operation` | 「按风格加载背景图库（classic\|urban\|ancient\|fresh）」 |

结论：`ancient` / `fresh` 是**演员卡风格词表（词表 A）的合法成员**，不是脏数据。

## 1. 两套词表

系统内并存两套独立词表，仅在 `classic` / `urban` 上重合。重合是误判的直接来源。

| | 词表 A：演员卡风格 | 词表 B：分享卡场景码 |
|---|---|---|
| 取值 | `classic \| urban \| ancient \| fresh` | `classic \| costume \| urban \| commercial \| artistic` |
| 权威定义 | `actor_card.style` / `actor_card_background.style` DDL 注释 + 背景图库种子数据 | `TemplateSceneCodeValidator.ALLOWED_TEMPLATE_SCENE_CODES` |
| 数据接口 | `GET /api/actor-card/background-library?style=` | `GET /api/card/scene-templates` |
| 前端消费者 | `pages/home`（`goCreateWithStyle`）、`pkg-actor-card/step-visual`、`pages/card-list` | `utils/share-card-mvp.ts`、`api/contact.ts` |
| 中文标签 | 经典 / 都市 / **古风** / 清新 | 经典 / **古风** / 都市 / 商业 / 艺术 |

标签层还有一个陷阱：词表 A 的 `ancient` 和词表 B 的 `costume` **都显示为「古风」**。仅凭界面文案无法区分两套词表，必须回到 scene code 本身判断。因此首页不复用 `share-card-mvp.ts` 的场景名解析——那是词表 B 的解析器，跨域复用会写出错值。

## 2. 首页必须用词表 A 的理由

首页模板卡点击链路（已逐跳核实）：

```text
goCreateWithStyle(style)
  → /pkg-actor-card/create/index?style=<style>
  → create/index.vue defineProps<{ style?: string }>()   (:56)
  → draftStore.initDraft(props.style)                    (:98)
  → saveStep({ style, currentStep: 1 })                  (stores/actor-card-draft.ts:29)
  → 写入 actor_card.style
```

终点是 `actor_card.style`，即词表 A 的列。所以首页只能发词表 A 的值。

若发词表 B 的值（初稿实现即如此），下游后果链：

```text
actor_card.style = 'costume'
  → 用户进入 step-visual
  → onMounted: activeStyle = c.style = 'costume'         (step-visual:178)
  → loadBgLibrary('costume')
  → SELECT ... WHERE style='costume' AND enabled=1        (ActorCardBackgroundService:23-28)
  → 背景图库种子无 costume 行 → 返回空数组
  → 背景选择区空白，且 4 个风格 tab 无一高亮（activeStyle 不在 tab 列表内）
```

`listByStyle` 是裸 `eq` 查询，无枚举校验、无异常，**静默返回空**。所以这条错误不会报错，只会让向导第一步变成空白页——比抛异常更难发现。初稿实现已构成该回归，现已回退。

## 3. 数据源选择

首页模板区当前缺的是**预览图**（`previewUrl: ''` 恒为空 → 4 个空占位框）。系统内提供风格预览图的唯一后端来源是 `actor_card_background`。

| 项 | 结论 | 依据 |
|---|---|---|
| 接口 | `GET /api/actor-card/background-library?style=` | `ActorCardController:85-89` |
| 前端封装 | `getBackgroundLibrary(style)` 已存在 | `api/actor-card.ts:20-21` |
| 返回结构 | `{ style, images: [{ id, imageUrl, thumbnailUrl, sortOrder }] }` | `ActorCardBackgroundLibraryRespDTO` |
| 排序 | `ORDER BY sort_order ASC`，后端已排 | `ActorCardBackgroundService:28` |
| 鉴权 | **需要登录**。`SecurityConfig` 白名单与 `permitAll` GET 列表均无 `background-library` | `SecurityConfig:40-57, 69-86` |

**不新建接口、不新建 api 封装、不改后端。**

## 4. 鉴权约束带来的设计取舍

`background-library` 需要登录，而首页是 tabBar 首屏，游客可达。两者冲突。

已否决方案：

- 把接口加进 `permitAll` 白名单 —— 需改后端，违反本期「后端代码不动」决策
- 游客也发请求 —— 必然 401，且首屏出现无意义失败

采用方案：**按登录态分流**。

| 状态 | 模板区表现 |
|------|-----------|
| 未登录 | 4 个 tab 正常显示；网格区显示「登录后查看模板预览」，点击跳登录页 |
| 已登录 · 加载中 | 骨架占位卡（复用 `--placeholder`） |
| 已登录 · 有数据 | 该风格背景图网格 |
| 已登录 · 空 | 「该风格暂无模板」 |
| 已登录 · 失败 | 「模板加载失败，点击重试」，点击重试 |

这与草稿区的既有约定一致（草稿同样依赖登录态）。

## 5. tab 与网格的关系

用户已选定「tab 过滤网格」。在真实数据模型下落地为：

```text
        4 个固定 tab（词表 A）
        经典 / 都市 / 古风 / 清新
                  │
          activeStyle（单选）
                  │
     getBackgroundLibrary(activeStyle)
                  │
        网格 = 该风格的背景图列表
```

tab 固定 4 项而非由数据推导，理由：tab 语义是「风格类目」，类目由词表 A 定义，不由某一时刻的图库存量定义。若按数据推导，后台停用某风格全部背景图会导致该 tab 消失，用户失去入口——而风格本身仍然合法可创建。

网格改为渲染 N 张背景图（非固定 4 格）。既有 SCSS `grid-template-columns: 1fr 1fr` 自动成行，2/3 张图布局不破。

卡片文案取 `styleLabel(activeStyle)`（风格中文名），与截图现状一致。点击任意卡片 → `goCreateWithStyle(activeStyle)`，出参恒为词表 A 合法值。

## 6. 缓存

`bgCache: Map<string, BgItem[]>` 按风格缓存，切 tab 命中缓存不重复请求。下拉刷新 `bgCache.clear()` 后强制重取。

竞态处理：`loadBackgrounds` 写回前校验 `activeStyle.value === style`，避免快速切 tab 时旧响应覆盖新风格数据。

## 7. 下拉刷新（既存缺陷修复）

`pages.json` 中 `pages/home/index` 已配置 `enablePullDownRefresh: true`，但页面从未注册 `onPullDownRefresh`。已核实：改动前全项目 `onPullDownRefresh` / `stopPullDownRefresh` 命中数为 0。

后果：下拉手势触发系统加载圈，但无任何处理器，且微信不会自动收起——加载圈持续显示。

修复：注册 `onPullDownRefresh`，`finally` 中显式 `uni.stopPullDownRefresh()`。这也顺带给模板区提供了第二条重试路径。

## 8. 视觉不变量

用户要求「以当前样式对接」。以下 SCSS 类名与几何全部保留，未新增或修改任何既有样式规则：

`home-v2__style-tabs` / `__style-tab` / `--active` / `__style-grid`（`1fr 1fr`, `gap 16rpx`）/ `__style-card` / `__style-img-wrap`（`aspect-ratio 3/2`）/ `__style-img` / `--placeholder` / `__style-label`

仅新增 `__style-empty` / `__style-empty-text` 两条规则，用于此前不存在的空态。

## 9. 后端处置

本期后端**只做文档标注，不改代码、不改表**（用户决策）。

| 端点 | 前缀 | 处置 |
|------|------|------|
| `CrewProfileController` | `/crew` | 标注为历史：小程序端已无消费者 |
| `ProjectController` | `/project` | 同上 |
| `RecruitPostController` | `/role` | 同上 |
| `RecruitApplyController` | `/apply` | 同上 |
| `AdminRecruitController` | `/admin/recruit/*` | **仍在服役**，kaipai-admin 工具层消费 |
| `AdminSystemController#recruitGovernanceMatrix` | `/admin/system/roles/recruit-governance-matrix` | **仍在服役** |

服役证据：`kaipai-admin/src/api/recruit.ts`、`src/router/index.ts:128,139,150`、`src/constants/menus.ts:80,87,94` 三处活跃引用。`/recruit` 归属 `adminToolingRoutePrefixes`（工具层），不在 7 页正式导航主线内——所以它不在正式导航里，不等于它已退场。

## 10. 文档修复

| 文件 | 处置 |
|------|------|
| `docs/product-design.md` | 15 条死路径按 20 页真实注册表重写；补 13 个未记录页面；修正 Tab 数（2 → 4）；剧组端口径由「不扩展」改为「已下线」 |
| `docs/dev-playbook.md` | 3 条死路径处置；剧组相关表述归位 |
| `.sce/steering/CURRENT_CONTEXT.md` | V7.7 → 当期基线（00-207 / 00-208 / 00-209 / 00-210） |
| `docs/archive/**`、`docs/superpowers/plans/**` | **不改**，历史留痕 |

真实注册表（`pages.json`，20 页 / 4 tab）为唯一权威口径。

## 11. 验证门禁

| 项 | 命令 / 判据 | 结果 |
|---|---|---|
| 类型 | `npx vue-tsc --noEmit` | 0 错误 |
| 构建 | `npm run build:mp-weixin` | EXIT=0 |
| 产物必含 | home 产物含 `getBackgroundLibrary`、`ancient`、`fresh`、`stopPullDownRefresh` | 双树命中 |
| 产物必不含 | home 产物不含 `costume` / `commercial` / `artistic` / `scene-templates` | 双树 0 |
| 词表隔离 | `share-card-mvp.ts` 保持原状（无跨域改动） | git diff 空 |
| 包体 | 主包 ≤ 2048 KB | 442.5 KB |
| 治理 | `npm run audit:steering` | passed |

注：产物门禁方向与初稿相反——初稿要求 `ancient`/`fresh` 为 0，现要求其必须存在。方向反转本身即前置纠正的体现。
