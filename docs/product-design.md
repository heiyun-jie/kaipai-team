# 「开拍了」当前产品设计文档

> 版本：v1.7 | 更新日期：2026-08-09
> 当前主线：AI 演员卡创建向导 + 名片夹 + 素材库
> 治理依据：`00-206`（首页与向导替换）、`00-208`（可达性调查）、`00-209`（剧组退场与孤儿路由删除）、`00-210`（首页后端对接与文档校正）
> 历史版本归档：`docs/archive/product-design-v1.2-2026-03-23.md`

## 一、文档定位

本文档只描述**当前运行态**的产品模型、页面与验收重点。所有页面路径均以 `kaipai-frontend/src/pages.json` 为唯一权威。

以下内容已退场，不再作为当前实现依据：

- 信用积分主页、积分记录、排行榜
- basic / pro 二元会员旧方案
- 已退场的外部个性化输入域及其驱动分享主题方案
- **剧组端小程序全部功能**（`00-209` 已物理删除运行态页面与守卫）
- 通告浏览 / 投递链路（角色详情、投递确认、我的投递、投递管理页面均已删除）

查看历史方案请进入归档文档或历史 Spec，不要与当前主线混写。

## 二、产品定位

小程序端是**演员侧单角色工具**。当前主线为「上传素材 → AI 生成演员卡 → 发布进名片夹」。

已核实事实：`utils/navigation.ts` 的 `getHomePath()` 忽略传入 role，恒定返回 `/pages/home/index`；角色分流已不存在。`UserRole.Crew`（值 `2`）枚举成员仍保留在 `types/user.ts`，原因是后端仍会返回该字段，但前端已无任何剧组分支。

## 三、当前范围与非范围

### 3.1 当前范围

- 演员档案编辑：`pages/actor-profile/edit`
- AI 演员卡创建向导：`pkg-actor-card/*`（9 页，见 §5.2）
- 名片夹：`pages/card-list/index`
- 素材库：`pages/assets/index`、`pkg-profile/assets/index`
- 个人中心：`pages/mine/index`
- 实名认证：`pkg-card/verify/index`
- 资料智能导入复核：`pkg-profile/import-review/index`

### 3.2 当前不在范围

- 信用积分体系、排行榜体系
- 真实会员支付、扣费、订单闭环
- 剧组端小程序功能（已退场，非「暂不扩展」）
- 通告与投递链路（已退场）
- **小程序内分享卡片、海报、公开名片落地页**：见 §7 的核实结论

## 四、当前用户与角色

### 4.1 小程序用户

- 演员：完善档案、上传素材、创建并发布演员卡、管理名片夹、完成实名认证

### 4.2 非小程序角色

- 平台运营：通过 `kaipai-admin` 后台维护审核、模板、会员、邀请规则与数据
- 剧组：**已退场**。后端 `/crew`、`/project`、`/role`、`/apply` 控制器仍在，但小程序端已无调用方；`/admin/recruit/*` 与 `/admin/system/roles/recruit-governance-matrix` 仍为 `kaipai-admin` 工具层在用接口（详见 §11）

## 五、当前页面信息架构

权威来源：`kaipai-frontend/src/pages.json`。当前注册 **20 页**（主包 6 + 分包 14）。

### 5.1 主包页面（6）

- `pages/home/index` — 首页（tabBar，开启 `enablePullDownRefresh`）
- `pages/login/index` — 登录 / 注册
- `pages/actor-profile/edit` — 演员档案编辑
- `pages/mine/index` — 个人中心（tabBar）
- `pages/card-list/index` — 名片夹（tabBar）
- `pages/assets/index` — 素材库（tabBar）

### 5.2 分包页面（14）

`pkg-actor-card`（9）— AI 演员卡创建向导：

- `pkg-actor-card/create/index` — 向导入口，接收 `?style=` 与 `?cardId=`
- `pkg-actor-card/step-visual/index` — 风格与背景图、AI 首图扩图
- `pkg-actor-card/step-profile/index`
- `pkg-actor-card/step-works/index`
- `pkg-actor-card/step-photos/index`
- `pkg-actor-card/step-video/index`
- `pkg-actor-card/step-attachment/index`
- `pkg-actor-card/step-settings/index`
- `pkg-actor-card/generate/index` — AI 生成与发布

`pkg-card`（1）：

- `pkg-card/verify/index` — 实名认证

`pkg-tools`（2）：

- `pkg-tools/webview/index`
- `pkg-tools/video-player/index`

`pkg-profile`（2）：

- `pkg-profile/import-review/index` — 资料智能导入复核
- `pkg-profile/assets/index` — 素材库（分包侧）

### 5.3 TabBar

当前底部 Tab 为 **4 个**：

| 顺序 | 文案 | 页面 |
|---|---|---|
| 1 | 首页 | `pages/home/index` |
| 2 | 名片夹 | `pages/card-list/index` |
| 3 | 素材库 | `pages/assets/index` |
| 4 | 个人 | `pages/mine/index` |

不存在排行榜 Tab。

## 六、当前核心链路

### 6.1 演员卡主链路

```text
登录 / 进入小程序
  → 首页选择风格（经典 / 都市 / 古风 / 清新）
  → 进入创建向导（step-visual 起）
  → 选背景图 / AI 首图扩图
  → 逐步填档案、作品、照片、视频、附件、设置
  → AI 生成演员卡
  → 发布
  → 进入名片夹「已发布」
```

### 6.2 草稿续编链路

```text
首页「继续编辑」（最多 2 条草稿）
  → /pkg-actor-card/create/index?cardId=<id>
  → 恢复到 current_step
```

名片夹「草稿」页签同样可续编；「已发布」项进入 `generate/index?cardId=<id>&preview=1` 预览。

## 七、分享能力的当前真实状态

**已核实事实（不得再按旧口径描述）**：

- 全前端 `src` 目录 `onShareAppMessage` / `onShareTimeline` 命中 **0**
- 全前端「海报」相关实现命中 **0**，前端 48 个接口中无海报接口
- 后端控制器无任何 `/public` 映射，不存在公开名片落地页接口
- `pkg-card/actor-card/index`（旧名片主预览页）、`pkg-card/invite/index`、`pkg-card/style-detail/index`、`pkg-card/membership/index` 已于 `00-209` 物理删除

因此本文旧版 §7「名片分享主线」描述的**小程序分享卡片、海报、公开名片页、邀请卡片四类分享产物，在当前运行态均不存在**。

仍然存在的相关残留：

- `utils/share-card-mvp.ts` 仍在产物中，唯一调用方是 `api/contact.ts` 的 `resolveShareCardSceneTitle`
- `/api/card/scene-templates`、`/api/card/my-cards`、`/api/referral/*` 接口封装仍在前端，但首页与向导均未消费 `scene-templates`
- 后端 `CardController` 的 `{shareCardId}/favorite` 系列、`AiProfileCardController` 的 `share-cards/{shareCardId}/artifact` 仍在

上述残留的退场与否，由 `00-110` 删除门禁另行裁定，本文不预先宣称其已退场。

## 八、风格词表（两套，不可互换）

这是当前最易出错的地方，单列一节。

| | 词表 A：演员卡风格 | 词表 B：分享卡场景码 |
|---|---|---|
| 取值 | `classic` / `urban` / `ancient` / `fresh` | `classic` / `urban` / `costume` / `commercial` / `artistic` |
| 中文 | 经典 / 都市 / 古风 / 清新 | 经典 / 都市 / 古风 / 商业 / 艺术 |
| 权威定义 | `actor_card.style` 与 `actor_card_background.style` 的 DDL 注释；`V20260731_002` 背景图种子数据 | `TemplateSceneCodeValidator.ALLOWED_TEMPLATE_SCENE_CODES` |
| 消费方 | 首页风格 tab、`step-visual` 选择器、`card-list` 标签、`/api/actor-card/background-library?style=` | `/api/card/scene-templates`、`utils/share-card-mvp.ts` |

两套仅在 `classic` / `urban` 上重合。**写入 `actor_card.style` 的一切链路必须用词表 A**；把词表 B 的值写进去会导致 `step-visual` 的背景图库查询命中 0 行（`listByStyle` 是裸 `eq` 查询，无校验、无异常，静默返回空列表）。

背景图种子数据分布：`classic` 3 张、`urban` 3 张、`ancient` 2 张、`fresh` 2 张。

## 九、首页模板区的后端对接

首页「模板创建」区当前由 `GET /api/actor-card/background-library?style=<词表A>` 驱动：

- 4 个 tab 固定对应词表 A 的 4 个风格
- 点 tab 切换 → 网格渲染该风格的背景图（按 `sort_order`）
- 点任一图 → `/pkg-actor-card/create/index?style=<词表A>`
- 该接口**不在** `SecurityConfig` 白名单内，需登录。游客态展示占位与「登录后查看模板预览」引导
- 已按风格做内存缓存，切 tab 不重复请求；下拉刷新清缓存并强制重取

已修正的两处缺陷：模板预览图此前恒为空占位（`previewUrl: ''` 硬编码）；`pages.json` 开启了 `enablePullDownRefresh` 但页面无 `onPullDownRefresh` 处理器，下拉圈不会收起。

## 十、等级、会员与 AI 能力

### 10.1 等级与会员

等级体系承担成长节奏（能力解锁、邀请驱动、AI 配额）。会员体系承担高级定制。二者当前均无真实支付闭环。

### 10.2 AI 能力边界

当前已真实接入并在向导中使用：

- AI 首图扩图：`POST /api/actor-card/draft/{cardId}/expand-image` + 轮询
- AI 演员卡生成：`POST /api/actor-card/draft/{cardId}/generate` + 轮询
- 资料智能导入抽取：`POST /api/ai/profile-import/extract`
- AI 配额：`GET /api/ai/quota`

约束不变：AI 模型调用统一由后端封装，前端不直接调用模型；身份证号后端加密存储，前端只展示脱敏值。

## 十一、后端招募 / 剧组域的当前定位

`00-210` 决策：**后端代码不动，只做文档标注**。数据库表同样不动。

| 后端接口 | 小程序消费 | kaipai-admin 消费 | 定位 |
|---|---|---|---|
| `/crew`（`CrewProfileController`） | 无 | 无 | 历史遗留 |
| `/project`（`ProjectController`） | 无 | 无 | 历史遗留 |
| `/role`（`RecruitPostController`） | 无 | 无 | 历史遗留 |
| `/apply`（`RecruitApplyController`） | 无 | 无 | 历史遗留 |
| `/admin/recruit/projects` `/roles` `/applies` 及状态接口 | 无 | **在用** | 后台工具层，运行中 |
| `/admin/system/roles/recruit-governance-matrix` | 无 | **在用** | 后台工具层，运行中 |

已核实：`kaipai-admin` 的 `src/api/recruit.ts`、`src/router/index.ts`、`src/constants/menus.ts` 均有活跃引用，「招募治理」菜单组在线。`/recruit` 属于 `adminToolingRoutePrefixes` 工具层，不在 7 页正式导航（仪表盘 / 数据分析 / 用户管理 / 分享内容 / 风格模板 / 运营动作 / 系统设置）之内 —— 这与后台主线口径一致，不是矛盾。

**结论：招募后端不是死代码，不得按「无前端引用」推定删除。** 任何退场需走 `00-110` 门禁。

## 十二、当前验收重点

1. 首页模板区是否真实渲染后端背景图，游客态是否给出登录引导
2. 首页下拉刷新是否能正常收起
3. 首页点击风格进入向导后，`step-visual` 背景图库是否非空（词表一致性的端到端体现）
4. 向导 9 步是否可连续走通并发布进名片夹
5. 页面注册是否与 `pages.json` 的 20 页一致，无孤儿路由
6. 主包体积是否在 2 MB 约束内
7. 前端页面放置、分包、共享组件是否符合 `00-27`

## 十三、当前文档依据

- `.sce/specs/00-206-*`、`00-208-*`、`00-209-*`、`00-210-*`
- `.sce/specs/00-27-mini-program-frontend-architecture/*`
- `.sce/specs/00-110-*`（删除门禁）
- `.sce/specs/SHARED_CONVENTIONS.md`
- `.sce/steering/CURRENT_CONTEXT.md`
- `.sce/specs/spec-code-mapping.md`

## 十四、历史归档说明

以下仅作历史追溯，不得作为当前实现依据：

- `docs/archive/product-design-v1.2-2026-03-23.md`
- `.sce/specs/05-03-credit-score/*`、`.sce/specs/05-01-actor-card/*`
- `docs/superpowers/plans/*`
- 旧外部个性化输入源相关历史 Spec
