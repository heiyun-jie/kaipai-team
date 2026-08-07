# v2.0 小程序演员卡创建向导 - 任务清单

> 执行顺序：Phase 1 → Phase 2 → Phase 3 → Phase 4，每个 Phase 完成后执行验收再进入下一 Phase。

---

## Phase 1 — 后端基础（先行，前端依赖此 Phase）

- [ ] **T1** 新增数据库表：`actor_card`、`actor_card_work`、`actor_card_background`，编写 Flyway migration 脚本
  **Validates: 3.2（draftId）, 3.5（剧照快照）, 8（DB）**

- [ ] **T2** 实现草稿 CRUD API（`/api/actor-card/draft/*`），包含创建、按步骤保存、读取、列表、删除
  **Validates: 3.2（自动保存）, 4（非功能需求）**

- [ ] **T3** 实现背景图库 API（`/api/actor-card/background-library`），按风格返回图片列表，数据从 `actor_card_background` 读取
  **Validates: 3.3（背景库不进素材库）**

- [ ] **T4** 新增演员卡扩图端点（`POST /api/actor-card/ai/expand-image` + 轮询接口），**复用** `TencentHunyuanProfileImageProvider` 现有的 `callTencent` / `pollJob` 基础设施，新增扩图专用 prompt（保留人物 + 四周自然延伸），返回 `{ originalUrl, expandedUrl }`。无需重新接入腾讯 API，只需新增 Service 方法 + Controller 端点。
  **Validates: 3.3（AI 扩图）, 约束条件（AI 由后端封装）**

- [ ] **T5** 实现演员卡生成异步接口（`POST /actor-card/generate` + `GET /actor-card/generate/:taskId`），生成完整长页预览并存储
  **Validates: 3.10（AI 生成）**

- [ ] **T6** 实现发布、名片夹列表、删除接口；实现资料完整度接口（`/api/actor/profile/completeness`）
  **Validates: 3.10（发布）, 3.11（名片夹）, 3.12（个人中心统计）**

---

## Phase 2 — 入口页改版

- [ ] **T7** 改版 `pages/home/index.vue`：AI 创建横幅 + 草稿恢复区 + 模板创建区（4风格 Tab + 2×2 网格）
  **Validates: 3.1**

- [ ] **T8** `pages.json` 更新底部导航：第二 Tab 改为「名片夹」（`pages/card-list/index`），图标与标签对齐设计稿
  **Validates: 3.13**

- [ ] **T9** 新增 `pages/card-list/index.vue` 名片夹页面：「已发布」/「草稿」Tab，卡片列表，操作菜单
  **Validates: 3.11**

- [ ] **T10** 改版 `pages/mine/index.vue` 个人中心：资料完整度进度条 + 统计数字行 + 演员资料分组 + 账户与服务分组
  **Validates: 3.12**

---

## Phase 3 — 创建向导 7 步

- [ ] **T11** 新增分包 `pkg-actor-card`，配置 `pages.json` subpackages；新增 `stores/actor-card-draft.ts` 全局草稿 Store
  **Validates: 3.2（draftId 生命周期）, 非功能需求（分包约束）**

- [ ] **T12** 实现 `pkg-actor-card/create/index.vue` 向导 Hub 页：7 步状态列表、顶部进度条、「继续下一项」按钮
  **Validates: 3.2**

- [ ] **T13** 实现步骤 1（`step-visual`）：风格选择 Tab、背景图库网格、首图选择、AI 扩图轮询（2s poll，60s 超时）、主视觉预览
  **Validates: 3.3**

- [ ] **T14** 实现步骤 2（`step-profile`）：自动读取个人资料预填、缺失字段跳转入口、同步选项开关（默认关）
  **Validates: 3.4**

- [ ] **T15** 实现步骤 3（`step-works`）：演艺经历 Tab / 新增作品 Tab、`StillsManager.vue` 子组件（剧照 1—3 张、封面badge、排序/替换/删除）、剧照空校验门禁
  **Validates: 3.5**

- [ ] **T16** 实现步骤 4（`step-photos`）：素材库 / 手机上传双入口、超 12 张软提示 Banner、`SortablePhotoGrid`（长按拖拽）
  **Validates: 3.6**

- [ ] **T17** 实现步骤 5（`step-video`）和步骤 6（`step-attachment`）：可选态、跳过逻辑、预览/替换/删除
  **Validates: 3.7, 3.8**

- [ ] **T18** 实现步骤 7（`step-settings`）：展示开关（联系方式/视频/附件）+ 拖拽顺序调整
  **Validates: 3.9**

---

## Phase 4 — 生成预览与发布

- [ ] **T19** 实现 `pkg-actor-card/generate/index.vue`：必填校验 → 生成进度态 → 成功预览（长页滚动）→ 发布 / 保存草稿，预览页支持返回各步骤修改
  **Validates: 3.10**

- [ ] **T20** 端到端验收：完整走通创建 → 生成 → 发布流程；验证草稿恢复；验证全局规则（换背景不清空资料、换首图必重新扩图）
  **Validates: 3.1—3.13, 第 6 章全局规则**

- [ ] **T21** 包体审计：`npm run audit:mp-package`，确认新分包未超包体约束；更新 `00-05` 分包治理记录
  **Validates: 非功能需求（2MB 约束）**
