# 00-210 任务 — 首页模板区后端对接 + 文档口径归位

## 状态总表

| 编号 | 任务 | 状态 | 产出 / 依据 |
|------|------|------|------------|
| T0 | 数据源与词表判定纠正 | 已完成 | 词表 A/B 边界确认，初稿判定作废 |
| T1 | 首页模板区对接 `background-library` | 已完成 | `src/pages/home/index.vue` |
| T2 | tab 过滤网格 | 已完成 | 4 固定 tab + 按风格取图 |
| T3 | 词表隔离（不跨域发值） | 已完成 | home 产物 VocabB 命中 0 |
| T4 | 下拉刷新缺陷修复 | 已完成 | `onPullDownRefresh` + `stopPullDownRefresh` |
| T5 | 类型 + 构建 + 产物核对 | 已完成 | 见 T5 记录 |
| T6 | `product-design.md` 归位 | 待执行 | — |
| T7 | `dev-playbook.md` 归位 | 待执行 | — |
| T8 | 后端历史端点文档标注 | 待执行 | — |
| T9 | `CURRENT_CONTEXT.md` 刷新 | 待执行 | — |
| T10 | Spec 注册 + `audit:steering` | 待执行 | — |

## T0 — 数据源与词表判定纠正（已完成）

初稿判定：首页模板区应对接 `/api/card/scene-templates`；`ancient` / `fresh` 为非法场景码。

**该判定错误。** 纠正依据：

- `V20260731_001__actor_card_tables.sql:11` `actor_card.style` 注释 `classic|urban|ancient|fresh`
- 同文件 `:64` `actor_card_background.style` 同一注释
- `V20260731_002__actor_card_background_seed.sql` 种子 style 分布 `classic`×3 / `urban`×3 / `ancient`×2 / `fresh`×2
- `ActorCardController:85` `@Operation` 摘要「按风格加载背景图库（classic|urban|ancient|fresh）」

系统内并存两套词表，仅在 `classic` / `urban` 重合；且词表 A 的 `ancient` 与词表 B 的 `costume` 中文标签都是「古风」，仅看文案无法区分。详见 `design.md` §1。

初稿实现（发词表 B 的值）已构成 `step-visual` 回归，已 `git checkout` 回退，并回退了当时为此在 `utils/share-card-mvp.ts` 新增的导出。

验收：`git status` 显示 `share-card-mvp.ts` 无改动；本期仅 `src/pages/home/index.vue` 一个文件变更。**已达成。**

## T1 — 首页模板区对接（已完成）

`styles` 数组去掉恒空的 `previewUrl`；网格数据改由 `getBackgroundLibrary(activeStyle)` 提供。

按登录态分流（`background-library` 不在 `SecurityConfig` 白名单，需鉴权）：

- 未登录 → tab 正常显示，网格区「登录后查看模板预览」，点击跳登录
- 已登录 → 骨架 / 数据 / 空 / 失败四态

`bgCache` 按风格缓存；写回前校验 `activeStyle.value === style` 防切 tab 竞态。

验收：产物 `getBackgroundLibrary` 命中 1，`api/actor-card` require 命中 1。**已达成。**

## T2 — tab 过滤网格（已完成）

tab 固定 4 项（词表 A 类目），网格渲染该风格的 N 张背景图。

tab 不由数据推导：类目由词表定义，不由图库存量定义。否则后台停用某风格全部背景图会让该 tab 消失，而该风格仍可创建。

验收：切 tab 后网格集合随 `activeStyle` 变化。**已达成**（`activeStyle` 在产物中作为过滤键使用）。

## T3 — 词表隔离（已完成）

首页出参恒为词表 A 合法值。`goCreateWithStyle` 入参只来自 `styles[].key`。

不复用 `share-card-mvp.ts` 的场景名解析器——那是词表 B 的解析器。

验收（门禁方向与初稿相反）：

- home 产物**必须含** `ancient` / `fresh` → 双树各命中 1
- home 产物**必须不含** `costume` / `commercial` / `artistic` / `scene-templates` / `resolveSceneDisplayName` → 双树全 0

**已达成。**

## T4 — 下拉刷新缺陷修复（已完成）

既存缺陷：`pages.json` 中 `pages/home/index` 配了 `enablePullDownRefresh: true`，但改动前全项目 `onPullDownRefresh` / `stopPullDownRefresh` 命中数为 0——下拉圈无处理器且不会自动收起。

修复：注册 `onPullDownRefresh`，清缓存后并发重取草稿与背景图，`finally` 中 `uni.stopPullDownRefresh()`。

验收：双树 `stopPullDownRefresh` 命中 1。**已达成。**

## T5 — 验证记录（已完成）

| 项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit`（cwd = kaipai-frontend，tsconfig.json 在位） | `TSC_EXIT=0`，0 行输出 |
| `npm run build:mp-weixin` | `BUILD_EXIT=0`，postbuild 同步 dev 成功 |
| 产物必含（双树） | `getBackgroundLibrary`=1 / `ancient`=1 / `fresh`=1 / `stopPullDownRefresh`=1 / wxml `style-empty`=1 / wxss `style-empty`=2 |
| 产物必不含（双树） | `costume`=0 / `commercial`=0 / `artistic`=0 / `scene-templates`=0 / `resolveSceneDisplayName`=0 |
| 主包 | 453,130 B = 442.5 KB（限 2048 KB，余量 1605.5 KB） |
| 分包 | pkg-actor-card 81.3 KB / pkg-card 31.6 KB / pkg-tools 39.2 KB / pkg-profile 80.7 KB |
| 全量 | 691,513 B = 675.3 KB |
| `pages/home` 产物 | 13,957 B（js 6,390 / json 154 / wxml 2,705 / wxss 4,708） |

## T6 — `product-design.md` 归位（待执行）

真实注册表（唯一权威）：20 页 / 4 tab。

- 主包 6：`pages/home/index`、`pages/login/index`、`pages/actor-profile/edit`、`pages/mine/index`、`pages/card-list/index`、`pages/assets/index`
- `pkg-actor-card` 9：`create` + `step-visual` / `step-profile` / `step-works` / `step-photos` / `step-video` / `step-attachment` / `step-settings` + `generate`
- `pkg-card` 1：`verify/index`
- `pkg-tools` 2：`webview/index`、`video-player/index`
- `pkg-profile` 2：`import-review/index`、`assets/index`
- tabBar 4：首页 / 名片夹 / 素材库 / 个人

需修：15 条死路径、13 个未记录页面、§5.3「底部 Tab 只有两个」（实为 4）、§3.1 与 §5.1/§5.2 页面清单、剧组端口径（「不作为当前主线继续扩展」→「已下线」）。

另需核实后再落笔：文档 §7.2 声称分享产物含「小程序分享卡片 / 海报」，但全前端 `onShareAppMessage` 命中 0、海报相关命中 0。该节需按运行态实况改写，不得照抄。

## T7 — `dev-playbook.md` 归位（待执行）

3 条死路径：`pages/company-profile/edit`（L51）、`pages/role-detail/index`（L102）、`pages/role-select/index`（L127）。另 L100 剧组视觉表述需归位。

## T8 — 后端历史端点文档标注（待执行）

**不改后端代码、不改表。**

- 标为历史（小程序端无消费者）：`/crew`、`/project`、`/role`、`/apply`
- 标为在役（kaipai-admin 工具层消费）：`/admin/recruit/*`、`/admin/system/roles/recruit-governance-matrix`

在役证据：`kaipai-admin/src/api/recruit.ts`、`src/router/index.ts:128,139,150`、`src/constants/menus.ts:80,87,94`。

## T9 — `CURRENT_CONTEXT.md` 刷新（待执行）

V7.7 停留在 00-199/00-200，需推进到 00-207 / 00-208 / 00-209 / 00-210 基线。

## T10 — 注册与治理（待执行）

`.sce/specs/README.md`（条目 + 索引表两处）、`spec-code-mapping.md`；随后 `npm run audit:steering`。
