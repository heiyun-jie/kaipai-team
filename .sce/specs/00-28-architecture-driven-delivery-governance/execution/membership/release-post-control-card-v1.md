# Membership 发布后控制卡 v1

本文件是 membership 第一版发布后控制卡。

当前定位：

- 这是**手工固化版**控制卡，不是脚本自动生成结果
- 字段结构显式复用：
  - `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`
- 当前目标不是替代样本，而是把 membership 当前发布后结论先压缩成：
  - `releaseDecisionCard`
  - `blockingIssueDashboard`
  - `releaseGoNoGoCard`
  - `operatorRunCard`

## 1. 当前判定依据

本卡当前基于以下证据：

- 总包入口：
  - `evidence-bundle-index.md`
- 正式样本：
  - `samples/20260403-234959-dev-post-release-membership-chain/validation-report.md`
  - `samples/20260403-234959-dev-post-release-membership-chain/sample-ledger.md`
  - `samples/20260403-234959-dev-post-release-membership-chain/admin-membership-template-chain-summary.md`
- 边界决策：
  - `preview-overlay-decision-record.md`
- 人工勾检入口：
  - `release-post-checklist.md`

## 2. 当前人工总控结论

### 2.1 releaseDecisionCard

- `finalJudgment`: `pass_with_known_blocker`
- `releasable`: `true`
- `mainlineReleaseBlocked`: `false`
- `topRisk`: `preview_overlay_not_backend_fact_source`
- `primaryOwner`: `membership-governance`
- `nextAction`: `release_mainline_and_continue_control_card_hardening`
- `releaseImpact`: `mainline_releasable_but_followup_required`
- `knownIssueCount`: `2`
- `newIssueCount`: `0`

### 2.2 blockingIssueDashboard

- `finalJudgment`: `pass_with_known_blocker`
- `highestSeverity`: `medium`
- `totalCount`: `2`
- `newCount`: `0`
- `knownCount`: `2`
- `sourceCounts`:
  - `fact_source_boundary`: `1`
  - `runtime_baseline_scope`: `1`
- `owners`:
  - `membership-governance`
  - `00-49 membership-preview-overlay-fact-source-boundary`
- `releaseBlocked`: `false`

### 2.3 blockingIssueMatrix

1. `preview_overlay_not_backend_fact_source`
   - `reason`: preview overlay 当前仍是 session-only 预览态，不是后端事实源
   - `source`: `00-49 membership-preview-overlay-fact-source-boundary`
   - `severity`: `medium`
   - `relatedChecks`:
     - `release-post-checklist -> blocker 判断`
     - `preview-overlay-decision-record.md`

2. `runtime_baseline_only_dev_nacos`
   - `reason`: 当前正式样本仍固定在 `dev + Nacos` 运行时，尚未扩展更多环境基线
   - `source`: `membership current evidence baseline`
   - `severity`: `medium`
   - `relatedChecks`:
     - `sample-ledger.md`
     - `validation-report.md`

## 3. 当前操作卡

### 3.1 releaseGoNoGoCard

- `decision`: `GO_WITH_KNOWN_BLOCKER`
- `releasable`: `true`
- `mainlineReleaseBlocked`: `false`
- `needsBatchSwitch`: `true`
- `requiresRerunRelease`: `false`
- `owner`: `membership-governance`
- `nextAction`: `release_mainline_and_continue_control_card_hardening`
- `reason`: 当前 membership 已具备“后端 API + DB + 后台 UI + 小程序页面”同包证据，主链可继续作为发布回归基线使用；但 `preview overlay` 事实源边界与 `dev + Nacos` 单环境样本范围仍是已知治理项，因此不应写成完全无阻塞。

### 3.2 operatorRunCard

- `mode`: `release_mainline_and_split_followup`
- `owner`: `membership-governance`
- `decision`: `GO_WITH_KNOWN_BLOCKER`
- `followupBatch`: `00-49 membership-preview-overlay-fact-source-boundary`
- `rerunRequired`: `false`
- `immediateSteps`:
  1. 按 `release-post-checklist.md` 完成 membership 当前发布后人工勾检
  2. 将本轮结果回填到 `status/membership-status.md`
  3. 保持 `20260403-234959-dev-post-release-membership-chain` 为当前默认总包
  4. 下一轮把本手工控制卡推进为可重复自动化字段，不再重新设计读法
  5. overlay 后续仍受 `00-49` 门禁约束，没有跨登录 / 跨设备新证据前不直接后端化

## 4. 当前 decision 说明

### 4.1 为什么不是 `GO`

因为当前仍有两个已知治理项：

1. preview overlay 不是后端事实源
2. 正式样本仍只固定在 `dev + Nacos`

这两项虽然没有阻断当前 membership 主链回归，但会影响“是否可宣告完全闭环”的判断。

### 4.2 为什么不是 `NO_GO`

因为当前已经有成组证据证明：

- 后端 API 正常
- DB 证据存在
- 后台 UI 证据存在
- 小程序 5 页证据存在
- 会员状态变更链 `member -> none -> member` 已固定
- 模板发布与回滚链已有同包证据

因此当前不属于“主线不可发”，而属于“主线可继续，但已知治理项必须显式挂账”。

## 5. 当前默认读法

从本文件开始，membership 第一版控制卡默认按下面顺序读：

1. `releaseGoNoGoCard`
2. `operatorRunCard`
3. `blockingIssueDashboard`
4. `blockingIssueMatrix`

只有在需要继续下钻时，再回看：

- `validation-report.md`
- `sample-ledger.md`
- `admin-membership-template-chain-summary.md`
- `preview-overlay-decision-record.md`

## 6. 下一步

按优先级：

1. 继续保持当前字段语义稳定，不重新发明 membership 的 Go/No-Go 读法
2. 把本文件中的字段逐步映射到可重复生成的数据输入
3. 后续如补第二份正式样本，再考虑把 v1 提升为脚本自动留档版
