# 首页作品瀑布流实施计划

> 日期：2026-07-28
> 范围：只在 `pages/home/index` 的阴阳鱼创建舞台下方展示“我的作品集”中已创建成功的作品；不调整首页既有 Hero、阴阳鱼舞台、创建入口、TabBar、作品集页或后端。

## 任务 1：建立 00-205 Spec 与失败门禁

1. 新建 `.sce/specs/00-205-current-phase-miniapp-home-portfolio-waterfall/requirements.md`，锁定真实数据、演员身份、无标题/空态、双列瀑布流、既有详情路由和不改动边界。
2. 新建 `design.md` 与 `tasks.md`，记录首页本地只读适配、AI 去重、手动封面回退和验证方式。
3. 新建 `scripts/verify-miniapp-home-portfolio-waterfall.mjs`，静态校验瀑布流结构、真实接口/过滤/路由，以及 00-201 Hero 和阴阳鱼合同未变。
4. 将 00-205 最小索引追加到 `.sce/specs/README.md` 与 `.sce/specs/spec-code-mapping.md`，保留文件内全部现有未提交修改。
5. 运行新门禁，确认首页尚未实现时失败。

## 任务 2：首页实现真实作品瀑布流

1. 只修改 `kaipai-frontend/src/pages/home/index.vue`。
2. 在 `home-page__creation-stage` 后新增无标题双列瀑布流；无真实作品时不渲染占位、提示或假数据。
3. 仅登录演员读取 `/api/card/my-cards`、AI artifacts、AI tasks 与手动卡配置；游客/剧组清空作品且不发个人作品请求。
4. 沿用作品集规则过滤 mock、source=generated 和失败任务；按 task ID 去重正式 artifact 与任务兜底；保留全部手动卡。
5. AI 图使用 `buildAiProfileCardDisplayImageUrl()`，手动卡优先使用 `highlightedPhotos` 首图，没有图片时使用既有 `KpShareSceneCover`。
6. AI 项进入现有 AI 详情路由；手动项使用 `buildShareCardDetailPath()`。
7. 图片使用稳定双列、`widthFix` 与限定圆角；不改变 Hero、阴阳鱼区域、两个入口及其样式。

## 任务 3：验证与产物核对

1. 运行 00-205 门禁并确认通过。
2. 运行 `npm run type-check` 与 `npm run build:mp-weixin`。
3. 运行相关 00-187、00-192、00-199 及 00-201/00-205 静态门禁。
4. 运行 `npm run audit:steering` 与 `npm run audit:mp-package`，如遇既有无关阻塞只记录，不扩改。
5. 核对 `src`、`dist/build/mp-weixin`、`dist/dev/mp-weixin` 的首页结构和样式，并比较 build/dev 首页文件哈希。
6. 检查最终 diff，确认除 00-205 Spec/计划/验证文件、两份 Spec 索引和首页外没有本需求产生的修改。
