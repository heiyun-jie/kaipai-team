# Share Card MVP 发布后检查清单

## 1. 目标

把当前 `share-card-mvp` 发布后的回归检查，固化成一套可重复执行的标准顺序：

`API / 治理主样本 -> 小程序页面证据 -> 后台页面证据 -> blocker 判断 -> status 回填`

目标不是重新描述架构，而是确保每次发布后都能快速回答：

- 主链是否正常
- `UserShareCard` 是否仍是事实源
- `legacy-summary` 是否仍为 0
- 小程序与后台 UI 是否仍消费同一条真实链路

## 2. 检查前置

### 2.1 运行时一致性

- 小程序、后台、后端必须确认同一环境
- 必查项：
  - `VITE_API_BASE_URL`
  - `VITE_USE_MOCK=false`
  - 小程序 dist 已同步到当前运行目录
  - 后台静态资源已切到当前发布版本
  - 后端 runtime 已切到当前 jar / 容器版本

### 2.2 当前标准入口

发布后默认从下面文件开始：

1. `evidence-bundle-index.md`
2. `evidence-index.md`
3. 具体 `samples/*`
4. 当前默认总控卡：`samples/20260420-122017-share-card-release-post-checklist-record-auto-v27/summary.md`
5. 当前默认总控基线版本：`auto-v27`

### 2.3 当前基线样本

- API / 治理：
  - `samples/20260405-224334-dev-remote-governance-sample-v2/summary.md`
- 小程序页面：
  - `samples/20260405-232141-share-card-mini-program-page-evidence-v3/summary.md`
- 后台页面：
  - `samples/20260420-152642-share-card-admin-page-evidence-v7/summary.md`
- 总控自动留档：
  - `samples/20260420-122017-share-card-release-post-checklist-record-auto-v27/summary.md`
  - 同目录 `checklist-result.json`
  - 若直接执行 `run-share-card-release-post-checklist-record.py` 且不显式传 `--mini-blocker-sample`，脚本当前会自动选最新 blocker 样本；`2026-04-20 13:25:53 +0800` 的验证样本 `samples/20260420-132553-share-card-release-post-checklist-record-auto-v29/summary.md` 已证明这条 `auto_latest` 解析路径成立（当时命中的是 `samples/20260420-130633-share-runtime-poster-page-evidence-r3/summary.md`）
  - `2026-04-20 13:37:27 +0800` 的验证样本 `samples/20260420-133727-share-card-release-post-checklist-record-auto-v33/summary.md` 又已证明：summary / checklist-result / CLI stdout 都会显式输出 blocker 样本选择模式、中文展示文案与选择说明，不必再额外读源码确认
  - `2026-04-20 15:41:23 +0800` 的验证样本 `samples/20260420-154123-share-card-release-post-checklist-record-auto-v42/summary.md` 又已证明：在不显式传样本时，脚本当前会自动命中最新 blocker 样本 `r9` 和最新后台页面样本 `share-card-admin-page-evidence-v7`，并在 summary / checklist-result / CLI stdout 里显式输出 `adminSampleSelectionMode / Display / Note`
  - `2026-04-20 16:01:30 +0800` 的验证样本 `samples/20260420-160130-share-card-release-post-checklist-record-auto-v43/summary.md` 又已证明：在 probe stdout 扩成更完整结构化字段后，默认解析行为仍会自动命中最新 blocker 样本 `r10` 与最新后台页面样本 `share-card-admin-page-evidence-v7`
  - `2026-04-20 16:11:42 +0800` 的验证样本 `samples/20260420-161142-share-card-release-post-checklist-record-auto-v44/summary.md` 又已证明：在 page-evidence blocked 分支新增 `preflightProbeResultPath` 后，默认解析行为仍会自动命中最新 blocker 样本 `r11` 与最新后台页面样本 `share-card-admin-page-evidence-v7`
  - `2026-04-20 16:26:43 +0800` 的验证样本 `samples/20260420-162643-share-card-release-post-checklist-record-auto-v45/summary.md` 又已证明：自动总控当前也已把 `Mini Program Blocker Preflight Summary / Result` 显式写入 summary 与 `checklist-result.json`，不必再回看 blocker 样本目录才能进入 preflight `probe-result.json`
  - `2026-04-20 16:38:35 +0800` 的验证样本 `samples/20260420-163835-share-card-release-post-checklist-record-auto-v46/summary.md` 又已证明：自动总控当前的 CLI stdout 也已显式写出 `Mini Program Blocker Preflight Summary / Result`，不再只有 summary / `checklist-result.json` 带出这两个字段

### 2.4 当前标准读法

每次发布后默认先看：

1. `releaseGoNoGoCard`
2. `operatorRunCard`
2.1 这两张卡是当前发布后标准默认读法；后续若继续升级自动留档，只允许向后兼容追加，不允许替换默认读法

只有在需要继续定位问题时，再展开：

3. `blockingIssueDashboard`
4. `blockingIssueMatrix`
5. `blockingIssueActionPlan`

## 3. 发布后标准检查顺序

### 3.1 API / 治理主样本

优先执行或核对：

- `run-share-card-mvp-governance-sample.py`

至少确认：

- owner `/card/my-cards` 正常
- viewer `/card/personalization` 正常
- viewer `/card/view-histories` 正常
- viewer `/card/contact-requests/*` 正常
- admin `/admin/content/contact-requests` 正常
- admin `/admin/content/share-cards` 正常
- admin `/admin/content/share-cards/{shareCardId}` 正常
- admin `/admin/content/share-cards/legacy-summary` 正常
- admin `/admin/content/default-general-card/*` 正常

关键判定：

- `bindingConsistent=true`
- `legacy-summary.totalPendingCount=0`

### 3.2 小程序页面证据

优先执行或核对：

- `run-share-card-devtools-auth-probe.py`
- `run-share-card-mini-program-page-evidence.py`

若脚本失败，也必须保留并回读：

- `summary.md`
- `captures/devtools-auth-blocker.txt`
- `captures/devtools-cli-auto.stdout.log`
- `captures/devtools-cli-auto.stderr.log`
- `captures/port-check.txt`

建议顺序：

1. 先跑 `run-share-card-devtools-auth-probe.py`
2. 只有当前探针不再落到 `devtools_auth_gate / NO_LISTENER`，再跑 `run-share-card-mini-program-page-evidence.py`
3. 即使直接跑 `run-share-card-mini-program-page-evidence.py`，脚本也会先执行同一套 preflight；若仍被 `devtools_auth_gate / NO_LISTENER` 阻塞，只生成 blocker 摘要并回链 preflight 样本，不再先进入大截图链路

至少确认页面：

- owner 首页
- owner 我的名片
- owner 卡片编辑
- owner 小程序卡片分享终态
- owner 分享海报终态
- viewer 从分享 path 再次进入小程序卡片页
- viewer 从分享 path 再次进入分享海报页
- owner 个人中心
- viewer 公开名片
- viewer 查看历史

关键判定：

- `Unique Screenshot Hash Count` 与页面数量一致
- `Visual Did Not Refresh=False`
- 页面 query / page-data 与 API 样本中的 `shareCardId` 一致
- 小程序卡片 / 海报终态 page-data 已记录 `onShareAppMessage / onShareTimeline` payload
- viewer 回流再次进入 page-data 已记录 `shared=1`、`shareCardId` 与 `artifact` 终态 query
- 若未进入截图阶段，也必须能回答：
  - 是 `9421` automation endpoint 未监听
  - 还是 DevTools 账号未获目标 appid 开发者授权
  - 不得只留一份脚本 stderr 而无标准 blocker 包

### 3.3 后台页面证据

优先执行或核对：

- `run-share-card-admin-page-evidence.py`

至少确认页面：

- 联系方式申请列表 / 详情
- 分享卡治理列表 / 详情
- 默认普通卡治理页

关键判定：

- 分享卡治理列表里能看到目标 `shareCardId`
- 详情页显示 `bindingConsistent`
- 页面证据中的 `legacySummary.totalPendingCount=0`

## 4. 本次发布必须勾选的核对项

每次发布后至少逐项确认下面内容：

### 4.1 API / 治理

- [ ] `/card/my-cards` 可返回默认 `general` 卡
- [ ] `/card/personalization` 可按 `shareCardId` 正常返回
- [ ] `/card/view-histories` 可写入并回读
- [ ] 联系方式申请链 `pending -> approved` 正常
- [ ] `/admin/content/share-cards` 列表正常
- [ ] `/admin/content/share-cards/{shareCardId}` 详情正常
- [ ] `/admin/content/share-cards/legacy-summary` 正常
- [ ] `legacy-summary.totalPendingCount=0`
- [ ] `bindingConsistent=true`

### 4.2 小程序页面

- [ ] owner 首页截图正常
- [ ] owner 我的名片截图正常
- [ ] owner 卡片编辑截图正常
- [ ] owner 小程序卡片分享终态截图正常
- [ ] owner 分享海报终态截图正常
- [ ] owner 个人中心截图正常
- [ ] viewer 公开名片截图正常
- [ ] viewer 查看历史截图正常
- [ ] 小程序卡片 / 海报终态 page-data 已记录 `onShareAppMessage / onShareTimeline` payload
- [ ] 若页面证据失败，`devtools-auth-blocker.txt + devtools-cli-auto*.log + port-check.txt` 已同包留档

### 4.3 后台页面

- [ ] 联系方式申请列表 / 详情截图正常
- [ ] 分享卡治理 `repair-legacy` 动作截图正常
- [ ] 分享卡治理列表 / 详情截图正常
- [ ] 默认普通卡治理页截图正常

### 4.4 blocker 判断

- [ ] 当前没有新的 4xx / 5xx 主链接口错误
- [ ] 当前没有新的权限缺失
- [ ] 当前没有新的 schema 缺列 / 漏迁移
- [ ] `releaseGoNoGoCard.decision` 已被回读并记录
- [ ] `operatorRunCard.immediateSteps` 已被执行或明确转后续批次
- [ ] 若 `sendCode` 仍是开发态验证码，已明确记录“不能宣告正式短信闭环”

## 5. 当前不能误判的点

### 5.1 不能误把 API 连通当成正式短信闭环

- `sendCode` 当前仍可能只是开发态验证码返回
- 这只能证明登录接口接通，不能证明正式短信已完成

### 5.2 不能误把页面截图当成治理已闭环

- 页面截图只能证明当前 UI 与接口结果一致
- 是否真正闭环，仍要看：
  - `bindingConsistent`
  - `legacy-summary.totalPendingCount`
  - 联系方式申请链是否真实跑通

## 6. 发布后回填要求

每次检查完成后，至少更新以下其一：

- `evidence-bundle-index.md`
- `evidence-index.md`
- `status/share-card-mvp-status.md`

若本次发布涉及 runtime 或治理接口变更，必须同时更新：

- `status/share-card-mvp-status.md`
- `00-62 execution.md`

## 7. 下一步补位方向

按优先级：

1. `sendCode` 正式短信能力验证样本
2. checklist 的实际执行结果也沉淀成样本
3. 把回流证据继续补到真正“外部用户再跳公开页”的更长链
