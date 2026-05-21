# share-card 当前阶段执行卡

本目录当前承接 `00-68 current-phase-share-runtime-and-poster-capability-alignment` 在 `00-28` 体系下的执行资产；`00-62 current-phase-minimal-share-card-mvp-alignment` 作为 share-card 基础盘继续保留在同一执行目录下。

统一证据索引：

- `evidence-index.md`
- `evidence-bundle-index.md`
- `release-post-checklist.md`
- `sms-capability-bridge.md`
- `run-share-card-devtools-auth-probe.py`
- `run-share-card-release-post-checklist-record.py`

当前发布后总控卡的通用结构模板：

- `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`
- 当前 share-card 默认总控结构基线版本：`auto-v27`
- 当前最完整验证样本：`samples/20260420-163835-share-card-release-post-checklist-record-auto-v46/summary.md`
- 当前外部 blocker 探针：`samples/20260420-164437-share-card-devtools-auth-probe-r6/summary.md`
- 当前默认读法固定为：`releaseGoNoGoCard -> operatorRunCard -> blockingIssueDashboard -> blockingIssueMatrix`
- 后续其它业务域若要复制发布后总控结构，默认按该模板扩展，不再另起一套读法

## 目标

把当前 share-card 主线从“00-62 基础盘”推进到“00-68 当前阶段运行时 / 海报能力对齐”的可持续治理对象，至少沉淀：

1. 当前 probe / blocker / admin / auto-checklist 四类默认入口
2. 当前运行时事实、外部 blocker 与最小可复跑证据
3. 让 Spec / 状态卡 / runbook / 自动总控默认读取同一套样本口径

## 当前范围

- 分享公开链事实源对齐
- 分享海报 capability / artifact / 文案 / active 入口对齐
- DevTools probe / page-evidence blocker / admin page evidence / auto checklist 统一证据链
- 发布后总控结构、runbook 与 evidence index 同步回填
- `00-62` 历史基础样本继续保留，但不再把它当作当前阶段唯一入口

## 本轮规则

- 样本可以先从“本地构建 + 结构验证”起步，但不得把这类样本误写成“真实环境三端闭环”
- 若样本涉及 `shareCardId`、默认普通卡、联系方式审批，必须明确记录当前仍处于兼容过渡期还是已完全切主键
- 后续真实环境样本必须能同时回答三个问题：
  - 小程序公开卡是否已走真实链路
  - 后台治理页是否能回看同一批联系方式申请
  - 后端运行时是否与样本中的数据结构一致

## 当前最小样本

### 当前默认入口

- API / 治理主样本：`samples/20260405-224334-dev-remote-governance-sample-v2/summary.md`
- 当前 probe：`samples/20260420-164437-share-card-devtools-auth-probe-r6/summary.md`
- 当前小程序 blocker：`samples/20260420-161105-share-runtime-poster-page-evidence-r11/summary.md`
- 当前后台页面样本：`samples/20260420-152642-share-card-admin-page-evidence-v7/summary.md`
- 当前最完整验证样本：`samples/20260420-163835-share-card-release-post-checklist-record-auto-v46/summary.md`

### 关键历史里程碑

- 本地 smoke 起点：`samples/20260404-local-share-card-mvp-governance-smoke/summary.md`
- 首个远端治理样本：`samples/20260405-005740-dev-remote-governance-sample/summary.md`
- 当前稳定远端治理基线：`samples/20260405-224334-dev-remote-governance-sample-v2/summary.md`
- 小程序页面基线三连：
  - `samples/20260405-011454-share-card-mini-program-page-evidence/summary.md`
  - `samples/20260405-231337-share-card-mini-program-page-evidence-v2/summary.md`
  - `samples/20260405-232141-share-card-mini-program-page-evidence-v3/summary.md`
- 后台页面基线三连：
  - `samples/20260405-012644-share-card-admin-page-evidence/summary.md`
  - `samples/20260405-225535-share-card-admin-page-evidence-v2/summary.md`
  - `samples/20260405-230757-share-card-admin-page-evidence-v3/summary.md`
- 发布后总控默认基线：`samples/20260420-122017-share-card-release-post-checklist-record-auto-v27/summary.md`
- 最新 blocker 演进里程碑：
  - 首个标准 blocker 包：`samples/20260420-090456-share-runtime-poster-page-evidence-r2/summary.md`
  - 首个内置 preflight blocker：`samples/20260420-130633-share-runtime-poster-page-evidence-r3/summary.md`
  - 当前 blocker：`samples/20260420-161105-share-runtime-poster-page-evidence-r11/summary.md`
- 自动总控关键里程碑：
  - 并发命中最新 blocker：`samples/20260420-151849-share-card-release-post-checklist-record-auto-v38/summary.md`
  - 并发命中最新 admin：`samples/20260420-152712-share-card-release-post-checklist-record-auto-v40/summary.md`
  - 最终结果文件优先：`samples/20260420-153508-share-card-release-post-checklist-record-auto-v41/summary.md`
  - admin 来源显式输出：`samples/20260420-154123-share-card-release-post-checklist-record-auto-v42/summary.md`
  - blocker preflight 进入 summary/json：`samples/20260420-162643-share-card-release-post-checklist-record-auto-v45/summary.md`
  - blocker preflight 进入 CLI stdout：`samples/20260420-163835-share-card-release-post-checklist-record-auto-v46/summary.md`

### 统一入口

- 当前推荐统一入口：`evidence-index.md`
- 当前推荐发布总入口：`evidence-bundle-index.md`
- 当前推荐发布检查清单：`release-post-checklist.md`
- 当前默认总控基线版本：`auto-v27`
- 当前总控结构复用模板：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`

## 2026-04-05 真实环境结论

- 已按 `00-29` 标准链路补齐 share-card 相关 schema：
  - `.sce/runbooks/backend-admin-release/records/20260405-004324-backend-schema-share-card-mvp-governance.md`
- 已按 `00-29` 标准链路连续完成两次 backend 发布：
  - `.sce/runbooks/backend-admin-release/records/20260405-004721-backend-only-share-card-mvp-runtime-align.md`
  - `.sce/runbooks/backend-admin-release/records/20260405-005313-backend-only-share-card-register-fix.md`
- 已按 `00-29` 标准链路完成管理端静态页发布：
  - `.sce/runbooks/backend-admin-release/records/20260405-010104-admin-only-share-card-governance-pages.md`
- 真实问题链已固定为：
  - 初始远端缺失 `V20260404_003 ~ 006` schema，导致 `/card/my-cards` 无法落到新表
  - schema 补齐后，运行时日志仍显示 `No static resource card/my-cards.`，证明线上仍在跑旧 jar
  - backend 发布后，新注册用户又暴露 `actor_profile_id` 非空冲突；已通过“无 `actor_profile` 时先只补 `user_share_card`”兼容修复
  - admin 侧最后暴露的是角色数据缺权限，而非接口逻辑异常；已通过后台角色更新接口补入 `page.content.contact-requests`、`page.content.default-general-card` 与 `action.content.default-general-card.compensate`
- 当前最新真实样本已跑通：
  - owner `/card/my-cards`
  - viewer register + `/card/personalization`
  - `/card/view-histories`
  - `/card/contact-requests` apply/approve/approved
  - admin `/admin/content/contact-requests`
  - admin `/admin/content/share-cards` + `/admin/content/share-cards/{shareCardId}`
  - admin `/admin/content/share-cards/legacy-summary`
  - admin `/admin/content/default-general-card/*`
- `2026-04-05 22:43:34 +0800` 已通过 `run-share-card-mvp-governance-sample.py --label remote-governance-sample-v2` 产出样本 `samples/20260405-224334-dev-remote-governance-sample-v2/summary.md`，补齐分享卡治理列表 / 详情与 legacy-summary 零存量校验，并把状态查询样本请求收口到只传 `shareCardId`
- `2026-04-05 01:16:31 +0800` 已通过 `run-share-card-mini-program-page-evidence.py` 产出样本 `samples/20260405-011454-share-card-mini-program-page-evidence/summary.md`，补齐 owner 首页 / 我的名片 / 卡片编辑 / 个人中心，以及 viewer 公开名片 / 查看历史六张小程序页面证据
- `2026-04-05 23:15:24 +0800` 已通过 `run-share-card-mini-program-page-evidence.py 20260405-224334-dev-remote-governance-sample-v2 share-card-mini-program-page-evidence-v2` 产出样本 `samples/20260405-231337-share-card-mini-program-page-evidence-v2/summary.md`，把 owner 小程序卡片 / 分享海报终态截图与 `onShareAppMessage / onShareTimeline` payload 补入小程序页面证据
- `2026-04-05 23:23:43 +0800` 已通过 `run-share-card-mini-program-page-evidence.py 20260405-224334-dev-remote-governance-sample-v2 share-card-mini-program-page-evidence-v3` 产出样本 `samples/20260405-232141-share-card-mini-program-page-evidence-v3/summary.md`，把 viewer 从真实分享 path 再次进入小程序卡片 / 海报页的回流证据补入小程序页面基线
- `2026-04-20 09:04:56 +0800` 已把 `run-share-card-mini-program-page-evidence.py` 补成“失败也自动产 blocker 包”的标准入口，并通过复跑样本 `samples/20260420-090456-share-runtime-poster-page-evidence-r2/summary.md` 产出首个标准 blocker 包，固定当前 DevTools 阻塞事实：
  - 首层失败：`Failed connecting to ws://127.0.0.1:9421`
  - 官方 CLI replay：`登录用户不是该小程序的开发者`
  - 端口探测：`NO_LISTENER`
  - 当前结论：阻塞停在微信开发者工具账号未获 `wxd38339082a9cfa4e` 开发者授权，而不是 share-card 页面逻辑或截图脚本参数
- `2026-04-05 23:32:15 +0800` 已新增样本 `samples/20260405-233215-share-card-release-post-checklist-record/summary.md`，把当前发布后检查清单的执行结果按 API / 小程序 / 后台 / blocker 四组核对项留档
- `2026-04-05 23:33:50 +0800` 已通过 `execution/login-auth/run-login-auth-phone-session-sample.py --label share-card-sms-bridge` 产出桥接样本，并新增 `sms-capability-bridge.md`，把 share-card 域内剩余的 `sendCode` 口径显式桥接到 `00-51 + login-auth`
- `2026-04-05 23:49:12 +0800` 已通过 `run-share-card-release-post-checklist-record.py` 产出样本 `samples/20260405-234912-share-card-release-post-checklist-record-auto-v2/summary.md`，把发布后检查清单执行结果改为可重复自动生成
- `2026-04-05 23:53:48 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v3` 产出样本 `samples/20260405-235348-share-card-release-post-checklist-record-auto-v3/summary.md`，并把 backend / admin / schema 发布记录也自动关联进 checklist 留档
- `2026-04-05 23:57:56 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v4` 产出样本 `samples/20260405-235756-share-card-release-post-checklist-record-auto-v4/summary.md`，并把 backend / admin / schema 发布记录中的关键 smoke 摘要一并抽取进 checklist 留档
- `2026-04-06 00:05:25 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v5` 产出样本 `samples/20260406-000525-share-card-release-post-checklist-record-auto-v5/summary.md`，并把发布记录中的 smoke 结果进一步收口为结构化字段写入 `checklist-result.json`
- `2026-04-06 00:11:53 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v6` 产出样本 `samples/20260406-001153-share-card-release-post-checklist-record-auto-v6/summary.md`，并把 `backendContainerUp / apiDocsStatusCode / migrationApplied` 等状态字段补入结构化 smoke
- `2026-04-06 00:19:55 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v7` 产出样本 `samples/20260406-001955-share-card-release-post-checklist-record-auto-v7/summary.md`，并把 `adminLoginStatusCode / publicHomeStatusCode / staticAssetStatusCode / publicHomeUp / staticAssetUp` 等发布后冒烟字段稳定写入结构化 smoke
- `2026-04-06 00:25:43 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v8` 产出样本 `samples/20260406-002543-share-card-release-post-checklist-record-auto-v8/summary.md`，并把 backend 发布记录里的 `adminRecruitRolesStatusCode / actorRoleSearchStatusCode` 以及对应 `401` 预期态判断补入结构化 smoke
- `2026-04-06 00:30:21 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v9` 产出样本 `samples/20260406-003021-share-card-release-post-checklist-record-auto-v9/summary.md`，并把 `ExpectedStatusCode / MatchesExpected` 判定扩展到 backend 与 admin 的主要 smoke URL，发布后留档开始显式区分“实际状态码”和“是否符合预期”
- `2026-04-06 00:35:38 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v10` 产出样本 `samples/20260406-003538-share-card-release-post-checklist-record-auto-v10/summary.md`，并把主要 smoke URL 的统一 `Verdict` 字段补入结构化 smoke，发布后留档开始显式区分 `pass / pass_expected_unauthorized / mismatch / missing`
- `2026-04-06 00:41:24 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v11` 产出样本 `samples/20260406-004124-share-card-release-post-checklist-record-auto-v11/summary.md`，并把 release-level `overallVerdict / failedKeys / missingKeys` 汇总补入结构化 smoke，backend / admin / schema 三类发布记录开始具备单份留档级总判定
- `2026-04-06 00:46:24 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v12` 产出样本 `samples/20260406-004624-share-card-release-post-checklist-record-auto-v12/summary.md`，并把 `release_records_all_pass` 接入 blocker judgment 与 overall 汇总，发布后检查清单开始显式消费 release-level 总判定
- `2026-04-06 00:53:08 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v13` 产出样本 `samples/20260406-005308-share-card-release-post-checklist-record-auto-v13/summary.md`，并把 `finalJudgment / finalJudgmentReason / newBlockingIssues / knownBlockingIssues` 补入总控结果区，发布后检查清单开始显式解释“为什么是这个最终结论”
- `2026-04-06 00:59:20 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v14` 产出样本 `samples/20260406-005920-share-card-release-post-checklist-record-auto-v14/summary.md`，并把 `newBlockingIssueKeys / newBlockingIssueReasons / knownBlockingIssueKeys / knownBlockingIssueReasons / blockingIssueSources` 补入结果区，发布后检查清单开始显式标记阻塞项来源
- `2026-04-06 01:07:17 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v15` 产出样本 `samples/20260406-010717-share-card-release-post-checklist-record-auto-v15/summary.md`，并把 `blockingIssueMatrix` 补入结果区，发布后检查清单开始显式输出阻塞项矩阵（`key / reason / source / severity / relatedChecks`）
- `2026-04-06 01:11:57 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v16` 产出样本 `samples/20260406-011157-share-card-release-post-checklist-record-auto-v16/summary.md`，并把 `blockingIssueSummary` 补入结果区，发布后检查清单开始显式输出阻塞项聚合摘要（`totalCount / newCount / knownCount / highestSeverity / sourceCounts`）
- `2026-04-06 01:18:28 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v17` 产出样本 `samples/20260406-011828-share-card-release-post-checklist-record-auto-v17/summary.md`，并把 `blockingIssueActionPlan` 补入结果区，发布后检查清单开始显式输出阻塞项处置建议（`owner / suggestedNextAction / releaseImpact`）
- `2026-04-06 01:25:33 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v18` 产出样本 `samples/20260406-012533-share-card-release-post-checklist-record-auto-v18/summary.md`，并把 `releaseDecisionCard / blockingIssueDashboard` 补入结果区，发布后检查清单开始显式输出聚合展示层
- `2026-04-06 01:33:02 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v19` 产出样本 `samples/20260406-013302-share-card-release-post-checklist-record-auto-v19/summary.md`，并把 `releaseGoNoGoCard / operatorRunCard` 补入结果区，发布后检查清单开始显式输出最终操作卡
- `2026-04-06` 当前已把 `auto-v19` 固化为 share-card 发布后总控默认基线版本；后续新增字段只允许向后兼容追加，不再改变 `releaseGoNoGoCard / operatorRunCard` 的默认读法
- `2026-04-20 10:04:49 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v21` 产出样本 `samples/20260420-100449-share-card-release-post-checklist-record-auto-v21/summary.md`，并把 `miniProgramBlockerSample`、DevTools 授权 blocker、`blocker_sample_recorded` 相关检查项接入自动总控结果。
- `2026-04-20 11:55:22 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v22` 产出样本 `samples/20260420-115522-share-card-release-post-checklist-record-auto-v22/summary.md`，并把 `ReleaseDecisionCard.topRisk`、`ReleaseGoNoGoCard.owner / nextAction` 与 `OperatorRunCard.immediateSteps` 优先对齐到当前 DevTools 授权 blocker。
- `2026-04-20 11:59:11 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v23` 产出样本 `samples/20260420-115911-share-card-release-post-checklist-record-auto-v23/summary.md`，并把 `FinalJudgmentReason / Known Blocking Issue Keys / Known Blocker / Blocking Issue Matrix / Action Plan` 的已知 blocker 顺序统一改为 DevTools 授权 blocker 优先。
- `2026-04-20 12:02:49 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v24` 产出样本 `samples/20260420-120249-share-card-release-post-checklist-record-auto-v24/summary.md`，并把 `operatorRunCard.primaryIssueKey / followupBatch` 收口到当前 DevTools 授权 blocker。
- `2026-04-20 12:07:24 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v25` 产出样本 `samples/20260420-120724-share-card-release-post-checklist-record-auto-v25/summary.md`，并把 `releaseGoNoGoCard.primaryIssueKey / needsBatchSwitch` 继续收口到当前 DevTools 授权 blocker。
- `2026-04-20 12:14:17 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v26` 产出样本 `samples/20260420-121417-share-card-release-post-checklist-record-auto-v26/summary.md`，并把 `blockingIssueDashboard.primaryIssueKey / topRisk / primaryOwner / nextAction` 与 `Notes` 顺序继续对齐到当前 DevTools 授权 blocker。
- `2026-04-20 12:20:17 +0800` 已通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v27` 产出样本 `samples/20260420-122017-share-card-release-post-checklist-record-auto-v27/summary.md`，并把 `OperatorRunCard.primaryIssueKey` 与 `Blocker Judgment` 顺序继续对齐到当前 DevTools 授权 blocker。
- `2026-04-20 12:25:26 +0800` 已新增独立脚本 `run-share-card-devtools-auth-probe.py`，并产出样本 `samples/20260420-122501-share-card-devtools-auth-probe/summary.md`。当前该探针可在不启动整套 page evidence 的情况下，先固定：
  - 目标 `AppID`
  - `cli auto --project ... --auto-port 9421` replay 结果
  - `9421` 端口监听状态
  - 当前是否仍卡在 DevTools 开发者授权
- `2026-04-20 14:29:22 ~ 16:44:37 +0800` 已按 `share-card-devtools-auth-probe-r2 ~ r6` 连续复跑同一探针；当前口径继续固定为：
  - `AppID=wxd38339082a9cfa4e`
  - `probeResult=devtools_auth_gate`
  - `port-check=NO_LISTENER`
  - 截至最新样本 `samples/20260420-164437-share-card-devtools-auth-probe-r6/summary.md`，外部 DevTools 授权 blocker 仍未解除
  - 从 `r5` 起，探针 `probe-result.json` 与 CLI stdout 也已同步显式带出 `sampleId / probeSummaryPath / resultPath / portCheckResult / cliReplay`
- `2026-04-20 13:06:35 +0800` 已把 `run-share-card-mini-program-page-evidence.py` 接入 `run-share-card-devtools-auth-probe.py` 作为内置 preflight，并通过样本 `samples/20260420-130633-share-runtime-poster-page-evidence-r3/summary.md` 验证：当 preflight 仍返回 `devtools_auth_gate` 且 `9421=NO_LISTENER` 时，脚本不再启动 `capture-mini-program-screenshots.js`，而是直接生成 blocker 摘要并回链 `samples/20260420-130633-share-runtime-poster-page-evidence-r3-preflight/summary.md`
- `2026-04-20 13:06:53 +0800` 已用新 blocker 样本复跑 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v28`，验证自动总控仍保持 DevTools 授权 blocker 为主风险，且 `releaseGoNoGoCard / operatorRunCard` 默认读法不变
- `2026-04-20 13:25:53 +0800` 又直接执行 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v29`（不再显式传 `--mini-blocker-sample`），新样本 `samples/20260420-132553-share-card-release-post-checklist-record-auto-v29/summary.md` 已验证脚本当前会自动命中最新 blocker 样本 `samples/20260420-130633-share-runtime-poster-page-evidence-r3/summary.md`
- `2026-04-20 13:34:04 +0800` 又通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v32` 产出样本 `samples/20260420-133404-share-card-release-post-checklist-record-auto-v32/summary.md`，并验证脚本当前会把 `miniProgramBlockerSampleSelectionMode / miniProgramBlockerSampleSelectionNote` 同步写入 summary、`checklist-result.json` 与 CLI stdout，后续不必再额外读源码确认 blocker 样本是显式传入还是自动命中
- `2026-04-20 13:37:27 +0800` 又通过 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v33` 产出样本 `samples/20260420-133727-share-card-release-post-checklist-record-auto-v33/summary.md`，并把 blocker 样本选择输出进一步收口为“raw mode + 中文展示 + 中文说明”三层结果；后续确认 blocker 样本来源时，不必再额外翻英文 mode 值或源码
- `2026-04-20 13:57:18 +0800` 又通过历史调用形式 `run-share-card-mini-program-page-evidence.py '' share-runtime-poster-page-evidence-r5` 产出样本 `samples/20260420-135717-share-runtime-poster-page-evidence-r5/summary.md`，并验证 page-evidence 脚本即使在 blocked 分支也会先输出结构化 JSON 到 stdout，显式带出 `sourceSampleSelectionMode / sourceSampleSelectionDisplay / sourceSampleSelectionNote / preflightProbe*`；后续当前若仍卡在 DevTools preflight，也不必再额外读源码确认 source sample 来源
- `2026-04-20 14:04:52 +0800` 又通过历史调用形式 `run-share-card-mini-program-page-evidence.py '' share-runtime-poster-page-evidence-r6` 产出样本 `samples/20260420-140451-share-runtime-poster-page-evidence-r6/summary.md`，并验证 page-evidence 脚本当前已统一落盘 `page-evidence-result.json`；即使 blocked 分支也会把 `summaryPath / resultPath / sourceSampleSelection* / preflightProbe* / blockerCapture` 写入结果文件，后续脚本不必只靠 stdout 或 summary 再次解析
- `2026-04-20 14:12:16 +0800` 又直接执行 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v34`，新样本 `samples/20260420-141216-share-card-release-post-checklist-record-auto-v34/summary.md` 已验证当前默认解析行为会自动命中最新 blocker 样本 `r6` 与最新后台页面样本 `share-card-admin-page-evidence-v4`
- `2026-04-20 14:33 +0800` 又已把 `run-share-card-devtools-auth-probe.py`、`run-share-card-mini-program-page-evidence.py` 与 `run-share-card-admin-page-evidence.py` 的参数入口统一补成 `argparse`；当前执行 `--help` 会直接输出帮助并正常退出，不会再误把 `--help` 当样本标签落目录。同步核验时 `samples/` 目录数量保持 `76 -> 76`，且未新增 `*help*` 样本目录。
- 同轮又已把 mini/admin 两支脚本的帮助文案同步改成当前真实行为：`source_sample` 现已明确写成“省略即自动选最新 source sample；PowerShell 下一参未知 positional 会按 label 解释”，不再继续提示“传空字符串占位”。
- `2026-04-20 14:41:39 +0800` 又直接用一参 label-only 方式执行 `run-share-card-mini-program-page-evidence.py share-runtime-poster-page-evidence-r7`，产出样本 `samples/20260420-144138-share-runtime-poster-page-evidence-r7/summary.md`。这次继续确认：PowerShell 下即使空字符串占位被吞掉，脚本当前也会自动把单个未知参数解释为 label，并继续按 `auto_latest_closure_context` 命中 source sample；同时 blocked 分支仍会统一落盘 `page-evidence-result.json` 与配套 `-preflight` 样本。
- `2026-04-20 14:42:04 +0800` 又直接用一参 label-only 方式执行 `run-share-card-admin-page-evidence.py share-card-admin-page-evidence-v5`，产出样本 `samples/20260420-144150-share-card-admin-page-evidence-v5/summary.md`，并验证 admin 脚本当前也会把单个未知参数解释为 label，同时按 `auto_latest_sample_metadata` 自动命中最新 source sample。
- `2026-04-20 14:42:15 +0800` 又直接执行 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v35`，新样本 `samples/20260420-144215-share-card-release-post-checklist-record-auto-v35/summary.md` 已验证当前默认解析行为会自动命中最新 blocker 样本 `r7` 与最新后台页面样本 `share-card-admin-page-evidence-v5`
- `2026-04-20 15:12:05 +0800` 又直接用一参 label-only 方式执行 `run-share-card-mini-program-page-evidence.py share-runtime-poster-page-evidence-r8`，产出样本 `samples/20260420-151204-share-runtime-poster-page-evidence-r8/summary.md`。这次继续固定：当前最新 blocker 样本已前移到 `r8`，其配套 `-preflight` 仍为 `probeResult=devtools_auth_gate / port-check=NO_LISTENER`，blocked 分支继续统一落盘 `page-evidence-result.json`。
- `2026-04-20 15:12:05 +0800` 同秒触发的 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v36` 抢在 `r8` 样本完全落盘前启动，因此仍命中了上一份 blocker 样本 `r7`；该样本只保留为一次抢跑现场，不作为当前默认验证口径。
- `2026-04-20 15:12:20 +0800` 又立即补跑 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v37`，新样本 `samples/20260420-151220-share-card-release-post-checklist-record-auto-v37/summary.md` 已验证当前默认解析行为会自动命中最新 blocker 样本 `r8` 与最新后台页面样本 `share-card-admin-page-evidence-v5`
- `2026-04-20 15:18:47 +0800` 又继续用一参 label-only 方式执行 `run-share-card-mini-program-page-evidence.py share-runtime-poster-page-evidence-r9`，产出样本 `samples/20260420-151847-share-runtime-poster-page-evidence-r9/summary.md`。这次继续固定：当前最新 blocker 样本已前移到 `r9`，其配套 `-preflight` 仍为 `probeResult=devtools_auth_gate / port-check=NO_LISTENER`，blocked 分支继续统一落盘 `page-evidence-result.json`。
- `2026-04-20 15:18:49 +0800` 又并发启动 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v38`，新样本 `samples/20260420-151849-share-card-release-post-checklist-record-auto-v38/summary.md` 已验证：在并发生成最新 blocker 样本的情况下，脚本当前也会直接命中最新 blocker 样本 `r9`，不再回退到前一份 blocker 样本。
- `2026-04-20 15:25:29 +0800` 又并发启动 `run-share-card-admin-page-evidence.py share-card-admin-page-evidence-v6` 与 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v39`；由于 admin 页面样本实际写出 `summary.md` 的耗时显著长于 5 秒，`auto-v39` 仍命中了旧后台页面样本 `v5`。这次现场进一步证明：自动总控脚本原先的“等待最新样本稳定”窗口对 admin 并发场景仍然不足。
- `2026-04-20 15:26:42 +0800` 又并发启动 `run-share-card-admin-page-evidence.py share-card-admin-page-evidence-v7` 与 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v40`。在把自动总控脚本的样本稳定等待窗口放宽后，新样本 `samples/20260420-152712-share-card-release-post-checklist-record-auto-v40/summary.md` 已验证：当前默认解析行为会在并发生成最新 admin 页面样本时直接命中 `share-card-admin-page-evidence-v7`，不再回退到旧后台页面样本。
- 同轮又已把自动总控的 auto-latest 解析进一步收紧为“优先选已产出最终结果文件的样本”：mini blocker 当前优先看 `page-evidence-result.json`，admin 页面当前优先看 `admin-page-evidence-result.json`；只有在仓内不存在这类最终结果文件样本时，才继续向旧的 `devtools-auth-blocker.txt / summary.md` 兼容回退。
- `2026-04-20 15:35:08 +0800` 又直接执行 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v41`，新样本 `samples/20260420-153508-share-card-release-post-checklist-record-auto-v41/summary.md` 已验证：blocker 样本选择说明当前已改成“匹配 `page-evidence` / `page-evidence-result.json`”，说明自动总控当前已把“最终结果文件优先”写进结构化输出，而不再只是代码内部实现。
- `2026-04-20 15:41:23 +0800` 又直接执行 `run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v42`，新样本 `samples/20260420-154123-share-card-release-post-checklist-record-auto-v42/summary.md` 已验证：在维持当前 `r9 + v7` 默认口径不变的前提下，脚本当前已把 `adminSampleSelectionMode / adminSampleSelectionDisplay / adminSampleSelectionNote` 同步写入 summary、`checklist-result.json` 与 CLI stdout；后续确认后台页面样本来源时，不必再回看源码。
- `2026-04-20 16:01:03 ~ 16:38:35 +0800` 又继续收口最近一轮 page-evidence / auto checklist：
  - `r10`：验证在 probe CLI stdout 扩成 `sampleId / probeSummaryPath / resultPath / portCheckResult / cliReplay` 后，page-evidence 内置 preflight 仍稳定消费同一份 probe 结果
  - `r11`：验证 page-evidence blocked 分支新增 `preflightProbeResultPath` 后，`summary.md / page-evidence-result.json / skip log / blocker capture` 都能显式回链 preflight `probe-result.json`
  - `auto-v43 ~ auto-v46`：验证自动总控在维持当前 `r11 + v7` 默认口径不变前提下，继续自动命中最新 blocker / admin 样本，并把 blocker preflight `summary / result` 逐步显式带入 summary、`checklist-result.json` 与 CLI stdout
  - 其中当前最完整验证样本为 `samples/20260420-163835-share-card-release-post-checklist-record-auto-v46/summary.md`
- `2026-04-20` 当前已把 `auto-v27` 升为 share-card 发布后总控默认基线版本；默认读法仍保持 `releaseGoNoGoCard / operatorRunCard`，只是在总控中继续向后兼容追加了 page-evidence blocker 读法、当前主风险排序、followupBatch、batch-switch、dashboard/notes 与摘要层一致性。
- `2026-04-06` 当前已把 share-card 的发布后总控结构抽取为通用模板 `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`，后续其它业务域如需复制总控卡，默认沿用 `releaseGoNoGoCard / operatorRunCard` 读法，再向后兼容追加展示层
- `2026-04-05 01:26:54 +0800` 已通过 `run-share-card-admin-page-evidence.py` 产出样本 `samples/20260405-012644-share-card-admin-page-evidence/summary.md`，补齐“联系方式申请”列表 / 详情与“默认普通卡”治理页后台证据
- `2026-04-05 22:55:50 +0800` 已通过 `run-share-card-admin-page-evidence.py 20260405-224334-dev-remote-governance-sample-v2 share-card-admin-page-evidence-v2` 产出样本 `samples/20260405-225535-share-card-admin-page-evidence-v2/summary.md`，把“分享卡治理”列表 / 详情补入后台页面证据基线
- `2026-04-05 23:08:13 +0800` 已通过 `run-share-card-admin-page-evidence.py 20260405-224334-dev-remote-governance-sample-v2 share-card-admin-page-evidence-v3` 产出样本 `samples/20260405-230757-share-card-admin-page-evidence-v3/summary.md`，把“分享卡治理 -> 执行 legacy 修复”动作截图也补入后台页面证据
- `2026-04-20 14:11:21 +0800` 已通过 `run-share-card-admin-page-evidence.py 20260405-224334-dev-remote-governance-sample-v2 share-card-admin-page-evidence-v4` 产出样本 `samples/20260420-141106-share-card-admin-page-evidence-v4/summary.md`，并验证后台页面证据脚本当前也会统一落盘 `admin-page-evidence-result.json`，同时在 summary / stdout 显式带出 `sourceSampleSelection*`
- `2026-04-20 14:42:04 +0800` 又已通过 `run-share-card-admin-page-evidence.py share-card-admin-page-evidence-v5` 产出样本 `samples/20260420-144150-share-card-admin-page-evidence-v5/summary.md`，并验证在 PowerShell 空字符串占位不保留的情况下，脚本当前也支持直接按一参 label-only 调用，同时仍会按 `auto_latest_sample_metadata` 自动选最新 source sample
- `2026-04-20 15:26:58 +0800` 又已通过 `run-share-card-admin-page-evidence.py share-card-admin-page-evidence-v7` 产出样本 `samples/20260420-152642-share-card-admin-page-evidence-v7/summary.md`，并验证在并发生成最新 admin 页面样本的情况下，自动总控经过“等待最新样本稳定”修正后也能直接命中 `v7`
- `2026-04-05` 已新增 `evidence-index.md`，把 API 回归样本、小程序页面证据与后台页面证据聚合为统一入口
- `2026-04-05` 已新增 `evidence-bundle-index.md`，把当前发布回归使用的 API / 小程序 / 后台三类基线样本再聚合成总包入口
- `2026-04-05` 已新增 `release-post-checklist.md`，把发布后必须逐项确认的 API / 小程序 / 后台 / blocker 核对项固化为标准检查清单
- `2026-04-05` 已把 `.sce/runbooks/backend-admin-release/README.md` 与 `backend-admin-standard-release.md` 显式串到 `evidence-bundle-index.md + release-post-checklist.md`，后续 share-card 发版后默认按 runbook 执行这套回归
- 当前剩余主 blocker 已固定为：
  - `DevTools` 开发者授权未恢复，`9421` automation endpoint 未监听
- 未来批次提醒：
  - `sendCode` 仍是开发态直返验证码，但正式短信能力继续归 `00-51` 跟踪，不混入当前 `00-68` blocker 判定

## 下一步

- 先恢复当前 WeChat DevTools 登录账号对 appid `wxd38339082a9cfa4e` 的开发者授权，并优先复跑 `run-share-card-devtools-auth-probe.py`
- 只有探针不再返回 `devtools_auth_gate / NO_LISTENER`，再复跑 `run-share-card-mini-program-page-evidence.py` 与自动总控
- 若后续要把 API / 小程序 / 后台证据彻底打成单目录整包，可在当前三份样本基础上再做一层聚合索引，不必重跑业务链
- 若后续再跑同类样本，优先复用 `run-share-card-mvp-governance-sample.py`、`run-share-card-mini-program-page-evidence.py`、`run-share-card-admin-page-evidence.py`，并继续通过 `00-29` 标准发布/诊断脚本处理 runtime 问题
- 若小程序 page evidence 再次因 DevTools 未授权失败，优先直接查看：
  - `summary.md`
  - `captures/devtools-auth-blocker.txt`
  - `captures/devtools-cli-auto.stdout.log`
  - `captures/devtools-cli-auto.stderr.log`
  - `captures/port-check.txt`
  不再只看 `mini-program-screenshot-capture.stderr.log`
- 若只是想先确认 DevTools 授权是否已恢复，优先执行：
  - `run-share-card-devtools-auth-probe.py`
  再决定是否进入 `run-share-card-mini-program-page-evidence.py`
- 若直接执行 `run-share-card-mini-program-page-evidence.py`，脚本也会先落同名 `-preflight` 样本；若探针仍返回 `devtools_auth_gate / NO_LISTENER`，则直接产出 blocker 摘要，不再启动整套截图链路
