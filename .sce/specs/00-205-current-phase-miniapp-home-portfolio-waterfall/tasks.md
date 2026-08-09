# 00-205 任务拆解 - 首页已创建作品瀑布流

> **状态：已降级为历史 Spec（`00-210` 轮次，用户裁决）。以下任务与验收标准不再执行。**
>
> `pages/home/index.vue` 已被 `00-206 T7` 整体替换，本 Spec 的瀑布流与其 `00-201` 舞台前置条件
> 均已不在运行态。`scripts/verify-miniapp-home-portfolio-waterfall.mjs` 的 `19` 项断言恒红，
> 保留为历史证据，不接入 `package.json`、不作为门禁执行。
>
> 下方勾选状态是降级前的历史记录，不代表当前运行态。

## T1. 建立 Spec 与红灯门禁

**文件：**
- 新建：`.sce/specs/00-205-current-phase-miniapp-home-portfolio-waterfall/requirements.md`
- 新建：`.sce/specs/00-205-current-phase-miniapp-home-portfolio-waterfall/design.md`
- 新建：`.sce/specs/00-205-current-phase-miniapp-home-portfolio-waterfall/tasks.md`
- 新建：`.sce/specs/00-205-current-phase-miniapp-home-portfolio-waterfall/scripts/verify-miniapp-home-portfolio-waterfall.mjs`
- 修改：`.sce/specs/README.md`
- 修改：`.sce/specs/spec-code-mapping.md`

- [x] 写入 `00-205` 范围、身份边界、真实数据、AI 去重、手动回退、双列和路由合同。
- [x] 编写源级静态门禁：保护 `00-201` 的 Hero 文案、`480rpx`、阴阳鱼背景与两个创建处理器 / 路由；同时要求新的 waterfall、适配器、去重、回退与详情契约。
- [x] 运行：

```powershell
node .sce/specs/00-205-current-phase-miniapp-home-portfolio-waterfall/scripts/verify-miniapp-home-portfolio-waterfall.mjs
```

预期：当前 `pages/home/index.vue` 还没有作品瀑布流，因此命令以非零状态退出；`00-201` 保护项为 `PASS`，`00-205` 新增项为 `FAIL`。

验证记录（`2026-07-28`）：命令以退出码 `1` 红灯结束；`00-201` 保护合同 `6 / 6 PASS`，待实现的 `00-205` 合同 `13 / 13 FAIL`，失败原因均指向当前尚不存在的瀑布流、演员适配和详情逻辑。

**Validates: Requirements 3.1-3.4, 4**

## T2. 只在首页实现本地作品适配

**文件：**
- 修改：`kaipai-frontend/src/pages/home/index.vue`

- [x] 在现有 `hydratePage()` 中先递增本地请求版本并清空 `portfolioItems`，再完成 `bootstrapSession()`；空用户或 `user.role === 2` 时直接返回，不进入任何个人作品 API。
- [x] 只为通过身份边界的演员调用 `getMyShareCards()`、`listAiProfileCardArtifacts()`、`listAiProfileCardTasks()`；让各数据源失败返回空集合，读取过程不新增可见 loading、Toast、错误或空态。
- [x] 在同一首页文件内新增 `HomePortfolioItem`、`loadHomePortfolioItems`、AI 合格性判断和 `taskId` 去重。官方 artifact 先入列，合格任务仅作未表示 `taskId` 的兜底；不使用 `shareCardId` 排除手动卡。
- [x] 把 `getMyShareCards().cards` 全量映射为 manual 项。每项用 `getActorCardConfig` 读取 `highlightedPhotos`，取第一个 `trim()` 后非空 URL；读取失败或无图时保留项目并交给 `KpShareSceneCover`。
- [x] 在 `home-page__creation-stage` 后放置由 `portfolioItems.length` 控制的无文字双列瀑布流。用 `portfolioColumns` 固定分为两列，图片为 `widthFix`；不添加标题、空态、样例、统计、额外按钮或跨页 UI。
- [x] AI 点击进入 `/pkg-card/ai-profile-card-detail/index` 并传 `shareCardId / detailTaskId`（query 仍名 `taskId`；官方 item 的值优先 `artifactId`）；manual 点击调用 `buildShareCardDetailPath({ shareCardId })`。保留 `goAiProfileCard()`、`goCardList()`、Hero、舞台与 TabBar 行为不变。

**Validates: Requirements 3.1-3.4**

## T3. 实现后验证与范围审查

**文件：**
- 验证：`.sce/specs/00-205-current-phase-miniapp-home-portfolio-waterfall/scripts/verify-miniapp-home-portfolio-waterfall.mjs`
- 验证：`kaipai-frontend/src/pages/home/index.vue`

- [x] 运行 00-205 门禁，全部 `19 / 19 PASS`（其中 `00-201` 保护合同 `6 / 6 PASS`）。
- [x] 运行：

```powershell
cd kaipai-frontend
npm run type-check
npm run build:mp-weixin
npm run audit:steering
npm run audit:mp-package
```

- [x] 重跑 `00-187` 与 `00-192` 会话门禁并通过；`00-199` 源码与 build/dev 产物门禁通过，最终仅被既有包体 URL 门禁阻塞。构建后 `src`、`dist/build/mp-weixin`、`dist/dev/mp-weixin` 首页均包含真实瀑布流，且 build/dev 首页四个文件 SHA256 一致。
- [x] 检查最终范围：本需求没有修改 portfolio 页、详情页、路由、Store、共享 API 或后端；首页外只新增 / 更新 00-205 治理文件、两份索引与实施计划。

验证记录（`2026-07-28`）：`npm run type-check`、`npm run build:mp-weixin`、`npm run audit:steering`、`00-187`、`00-192` 与 `00-205` 均退出码 `0`。`npm run audit:mp-package` 退出码 `1`，唯一报告为既有 `dist/build/mp-weixin/api/actor-asset.js:1` 含 `http://127.0.0.1:8010`；按本需求边界未修改该运行时配置。

**Validates: Requirements 3.1-3.4, 4**
