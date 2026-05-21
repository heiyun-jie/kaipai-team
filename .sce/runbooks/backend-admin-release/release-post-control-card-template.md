# 发布后总控卡通用模板

本模板用于把某个业务域的“发布后回归结果”收口成一套统一可读、可判定、可执行的总控卡结构。

目标不是替代业务回归样本，而是把：

- API / 页面 / 治理证据
- 发布记录 smoke
- blocker 判断
- 操作建议

压缩成一套标准字段，供 runbook、checklist 和后续业务域复用。

## 1. 推荐结构层次

### 1.1 样本 / 证据层

用于回答“实际发生了什么”：

- API / 治理样本
- 前端 / 小程序页面证据
- 后台页面证据
- backend / admin / schema 发布记录

### 1.2 字段 / 状态层

用于回答“每条 smoke 是否符合预期”：

- `StatusCode`
- `ExpectedStatusCode`
- `MatchesExpected`
- `Verdict`

推荐 verdict：

- `pass`
- `pass_expected_unauthorized`
- `mismatch`
- `missing`

### 1.3 发布记录层

用于回答“单份发布记录整体是否通过”：

- `overallVerdict`
- `failedKeys`
- `missingKeys`

### 1.4 总控判断层

用于回答“整轮发布后是否存在新的阻塞”：

- `blocker_judgment`
- `overall`
- `finalJudgment`
- `finalJudgmentReason`

### 1.5 阻塞项治理层

用于回答“阻塞是什么、来自哪里、如何处理”：

- `newBlockingIssues`
- `knownBlockingIssues`
- `blockingIssueSources`
- `blockingIssueMatrix`
- `blockingIssueSummary`
- `blockingIssueActionPlan`

### 1.6 聚合展示层

用于回答“运维现在应该怎么做”：

- `releaseDecisionCard`
- `blockingIssueDashboard`
- `releaseGoNoGoCard`
- `operatorRunCard`

## 2. 通用字段建议

### 2.1 `releaseDecisionCard`

最少包含：

- `finalJudgment`
- `releasable`
- `mainlineReleaseBlocked`
- `topRisk`
- `primaryOwner`
- `nextAction`
- `releaseImpact`
- `knownIssueCount`
- `newIssueCount`

### 2.2 `blockingIssueDashboard`

最少包含：

- `finalJudgment`
- `highestSeverity`
- `totalCount`
- `newCount`
- `knownCount`
- `sourceCounts`
- `owners`
- `releaseBlocked`

### 2.3 `releaseGoNoGoCard`

最少包含：

- `decision`
- `releasable`
- `mainlineReleaseBlocked`
- `needsBatchSwitch`
- `requiresRerunRelease`
- `owner`
- `nextAction`
- `reason`

推荐 decision：

- `GO`
- `GO_WITH_KNOWN_BLOCKER`
- `NO_GO`

### 2.4 `operatorRunCard`

最少包含：

- `mode`
- `owner`
- `decision`
- `followupBatch`
- `immediateSteps`
- `rerunRequired`

推荐 mode：

- `release_and_archive`
- `release_mainline_and_split_followup`
- `stop_and_fix`

## 3. 默认读法

发布后默认不要先翻所有明细，先按下面顺序读：

1. `releaseGoNoGoCard`
2. `operatorRunCard`
3. `blockingIssueDashboard`
4. `blockingIssueMatrix`
5. `blockingIssueActionPlan`

只有在需要继续追根溯源时，再展开：

- API / 治理主样本
- 前端 / 小程序页面证据
- 后台页面证据
- backend / admin / schema 发布记录原文

## 4. 通用动作映射建议

### 4.1 若 `decision = GO`

- 允许继续发布
- 归档本轮 checklist 结果
- 后续仅保留例行抽检

### 4.2 若 `decision = GO_WITH_KNOWN_BLOCKER`

- 允许主线继续发布
- 已知阻塞转入后续批次
- 按 `blockingIssueActionPlan` 跟踪处理

### 4.3 若 `decision = NO_GO`

- 停止继续发布
- 优先处理 `blockingIssueMatrix` 中的新增阻塞
- 修复后重跑标准 checklist 自动留档

## 5. 落地要求

1. 模板字段必须能由脚本自动生成，不接受只存在于口头说明。
2. 若业务域复用该模板，必须明确：
   - 当前默认总控基线版本
   - 当前默认读法
   - 当前 `GO / NO_GO` 的实际判定规则
3. 后续升级字段时，只允许向后兼容追加，不允许改变默认读法。

## 6. 当前 share-card 参考实现

参考样本：

- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-100449-share-card-release-post-checklist-record-auto-v21\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-115522-share-card-release-post-checklist-record-auto-v22\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-115911-share-card-release-post-checklist-record-auto-v23\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-120249-share-card-release-post-checklist-record-auto-v24\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-120724-share-card-release-post-checklist-record-auto-v25\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-121417-share-card-release-post-checklist-record-auto-v26\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-122017-share-card-release-post-checklist-record-auto-v27\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-130653-share-card-release-post-checklist-record-auto-v28\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-132553-share-card-release-post-checklist-record-auto-v29\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-133404-share-card-release-post-checklist-record-auto-v32\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-133727-share-card-release-post-checklist-record-auto-v33\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-141216-share-card-release-post-checklist-record-auto-v34\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-144215-share-card-release-post-checklist-record-auto-v35\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-151204-share-card-release-post-checklist-record-auto-v36\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-151220-share-card-release-post-checklist-record-auto-v37\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-151849-share-card-release-post-checklist-record-auto-v38\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-152539-share-card-release-post-checklist-record-auto-v39\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-152712-share-card-release-post-checklist-record-auto-v40\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-153508-share-card-release-post-checklist-record-auto-v41\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-154123-share-card-release-post-checklist-record-auto-v42\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-160130-share-card-release-post-checklist-record-auto-v43\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-161142-share-card-release-post-checklist-record-auto-v44\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-162643-share-card-release-post-checklist-record-auto-v45\summary.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-163835-share-card-release-post-checklist-record-auto-v46\summary.md`
- 对应最新 mini-program blocker 输入样本：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-161105-share-runtime-poster-page-evidence-r11\summary.md`
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-161105-share-runtime-poster-page-evidence-r11-preflight\summary.md`
- 对应当前最新后台页面输入样本：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-152642-share-card-admin-page-evidence-v7\summary.md`
- 同目录 `checklist-result.json`

当前 share-card 默认基线：

- `auto-v27`
- `auto-v28` 当前仅用于验证“最新 preflight blocker 样本进入自动总控后，默认读法与主风险排序仍保持一致”
- `auto-v29` 当前仅用于验证“未显式传 `--mini-blocker-sample` 时，默认解析行为也会自动命中最新 blocker 样本”
- `auto-v34` 当前用于验证：在不显式传 `--admin-sample` / `--mini-blocker-sample` 时，默认解析会自动命中当时的最新 blocker 样本 `r6` 与后台页面样本 `v4`
- `auto-v35` 当前用于验证：在不显式传 `--admin-sample` / `--mini-blocker-sample` 时，默认解析会自动命中当时的最新 blocker 样本 `r7` 与后台页面样本 `v5`
- `auto-v36` 当前仅保留为抢跑现场：脚本启动时 `r8` 尚未完全落盘，因此仍命中了 `r7`
- `auto-v37` 当前用于验证：在不显式传 `--admin-sample` / `--mini-blocker-sample` 时，默认解析会自动命中当时的最新 blocker 样本 `r8` 与当前后台页面样本 `v5`
- `auto-v38` 当前用于验证：在并发生成最新 blocker 样本 `r9` 的情况下，默认解析也会等待最新样本稳定并直接命中 `r9`，不再回退到旧 blocker 样本
- `auto-v39` 当前仅保留为 admin 抢跑现场：最新 admin 页面样本 `v6` 尚未完成摘要落盘时，自动总控仍命中了旧后台页面样本 `v5`
- `auto-v40` 当前用于验证：在把样本稳定等待窗口放宽到 30 秒后，默认解析会在并发生成最新 admin 页面样本 `v7` 时直接命中 `v7`
- `auto-v41` 当前用于验证：auto-latest 选样本规则已进一步收紧为“最终结果文件优先”，mini blocker 当前优先匹配 `page-evidence-result.json`
- `auto-v42` 当前用于验证：在维持当时 `r9 + v7` 默认口径不变的前提下，输出层已显式写出 `adminSampleSelectionMode / Display / Note`
- `auto-v43` 当前用于验证：在 probe stdout 扩成更完整结构化字段后，默认解析仍会自动命中最新 blocker 样本 `r10` 与后台页面样本 `v7`，且输出层继续显式写出 `adminSampleSelectionMode / Display / Note`
- `auto-v44` 当前用于验证：在 page-evidence blocked 分支新增 `preflightProbeResultPath` 后，默认解析仍会自动命中最新 blocker 样本 `r11` 与后台页面样本 `v7`，且输出层继续显式写出 `adminSampleSelectionMode / Display / Note`
- `auto-v45` 当前用于验证：自动总控层也已把 `Mini Program Blocker Preflight Summary / Result` 显式写入 summary 与 `checklist-result.json`，不必再回看 blocker 样本目录
- `auto-v46` 当前用于验证：自动总控层的 CLI stdout 也已实际带出 `Mini Program Blocker Preflight Summary / Result`；不再只是 summary / `checklist-result.json` 有这两个字段
- 其中 `auto-v46` 当前也是 share-card 这条线的最完整验证样本；若只保留一份“当前最完整验证口径”入口，应优先引用它

当前 share-card 默认读法：

- `releaseGoNoGoCard -> operatorRunCard -> blockingIssueDashboard -> blockingIssueMatrix`
