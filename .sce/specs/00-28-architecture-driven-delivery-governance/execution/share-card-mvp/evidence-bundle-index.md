# Share Card MVP 发布回归总包索引

本文件是 `share-card-mvp` 当前发布回归的 **总入口**。

与 `evidence-index.md` 的区别：

- `evidence-index.md` 偏向“按证据类型说明怎么用”
- `evidence-bundle-index.md` 偏向“这一次发布回归的完整包清单与阅读顺序”

配套检查清单：

- `release-post-checklist.md`
- `samples/20260420-122017-share-card-release-post-checklist-record-auto-v27/summary.md`
- `sms-capability-bridge.md`
- `run-share-card-release-post-checklist-record.py`
- `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`

当前默认总控基线版本：

- `auto-v27`
- 默认读法固定为：`releaseGoNoGoCard -> operatorRunCard -> blockingIssueDashboard -> blockingIssueMatrix`
- 结构复用模板：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`

## 1. 当前推荐总包

### 1.1 API / 治理主样本

- 样本：`samples/20260405-224334-dev-remote-governance-sample-v2/`
- 摘要：`samples/20260405-224334-dev-remote-governance-sample-v2/summary.md`
- 关键结论：
  - owner `/card/my-cards` 正常
  - viewer `/card/personalization`、`/card/view-histories`、`/card/contact-requests/*` 正常
  - admin `/admin/content/share-cards`、`/legacy-summary`、`/default-general-card/*` 正常
  - `bindingConsistent=true`
  - `legacy-summary.totalPendingCount=0`

### 1.2 小程序页面证据

- 样本：`samples/20260405-232141-share-card-mini-program-page-evidence-v3/`
- 摘要：`samples/20260405-232141-share-card-mini-program-page-evidence-v3/summary.md`
- 固定页面：
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

### 1.2.1 小程序阻塞样本

- 样本：`samples/20260420-161105-share-runtime-poster-page-evidence-r11/`
- 摘要：`samples/20260420-161105-share-runtime-poster-page-evidence-r11/summary.md`
- 配套 preflight：`samples/20260420-161105-share-runtime-poster-page-evidence-r11-preflight/summary.md`
- 适用场景：
  - `run-share-card-mini-program-page-evidence.py` 未进入截图阶段
  - 需要先判断 DevTools automation 是否可用
  - 需要区分“页面逻辑问题”与“开发者授权问题”
- 当前结论：
  - page evidence 当前会先走内置 preflight
  - 本轮 preflight：`probeResult=devtools_auth_gate`
  - 官方 CLI replay：`登录用户不是该小程序的开发者`
  - 端口探测：`NO_LISTENER`
  - 当前 blocker 停在 DevTools 开发者授权，不在 share-card 页面实现

### 1.3 后台页面证据

- 样本：`samples/20260420-152642-share-card-admin-page-evidence-v7/`
- 摘要：`samples/20260420-152642-share-card-admin-page-evidence-v7/summary.md`
- 固定页面：
  - 联系方式申请列表 / 详情
  - 分享卡治理 repair-legacy 动作截图
  - 分享卡治理列表 / 详情
  - 默认普通卡治理页
- 补充产物：
  - `admin-page-evidence-result.json`
  - `Source Share Card Sample Selection / Display / Note`

## 2. 推荐阅读顺序

每次发布后，按下面顺序看：

1. `samples/20260405-224334-dev-remote-governance-sample-v2/summary.md`
   - 先确认后端主链、治理接口、legacy-summary 是否正常
2. `samples/20260405-232141-share-card-mini-program-page-evidence-v3/summary.md`
   - 再确认小程序主页面与真实链路是否一致
2.1 若 page evidence 未产出截图，立即切到 `samples/20260420-161105-share-runtime-poster-page-evidence-r11/summary.md`
    - 先确认阻塞是否停在 DevTools 授权 / automation 端口，而不是前端页面逻辑
3. `samples/20260420-152642-share-card-admin-page-evidence-v7/summary.md`
   - 最后确认后台治理页 UI 是否仍和接口证据一致
4. `samples/20260420-122017-share-card-release-post-checklist-record-auto-v27/summary.md`
    - 最终确认本轮发布后检查清单是否已被完整勾检并留档
   - 若要确认最新 preflight blocker 样本已兼容进入自动总控，再补看 `samples/20260420-130653-share-card-release-post-checklist-record-auto-v28/summary.md`
   - 若要确认当前默认解析会自动命中最新 blocker 样本 `r11` 与最新后台页面样本 `share-card-admin-page-evidence-v7`，并且在输出层显式写出 `adminSampleSelectionMode / Display / Note`，再补看 `samples/20260420-163835-share-card-release-post-checklist-record-auto-v46/summary.md`
   - 其中 `auto-v46` 当前也是这条线的“最完整验证样本”：它同时覆盖最新 `r11 + v7` 默认命中结果、blocker preflight 结果文件路径显式输出，以及 admin 样本来源的显式输出字段
5. 若唯一剩余问题仍是 `sendCode` 口径，再看 `sms-capability-bridge.md`
    - 用于把 share-card 剩余短信能力缺口显式桥接到 `00-51 + login-auth`

如果只够看一份，优先看第 1 份 API / 治理主样本。

## 3. 当前总包回答的问题

这份总包当前可以直接回答：

### 3.1 小程序 - 后端 - 后台 是否仍然闭在一条主线上

可以。

因为当前已有：

- 小程序 owner / viewer 页面证据
- 后端 share-card 主链 API 样本
- 后台治理页截图证据

### 3.2 分享卡实例是否已经成为事实源

当前可以确认主路径是成立的。

直接证据：

- `/admin/content/share-cards/1` 返回 `bindingConsistent=true`
- 后台“分享卡治理”详情页也已固定这一状态

### 3.3 legacy 数据是否已退出主链

当前可以确认：

- `legacy-summary.totalPendingCount=0`
- admin 发布记录中的 `publicHomeStatusCode=200 / staticAssetStatusCode=200 / adminLoginStatusCode=200`
- backend 发布记录中的 `adminRecruitRolesStatusCode=401 / actorRoleSearchStatusCode=401`
- 上述主要 smoke URL 当前都已同时具备 `ExpectedStatusCode / MatchesExpected`
- 上述主要 smoke URL 当前都已同时具备统一 `Verdict`
- backend / admin / schema 当前都已同时具备 release-level `overallVerdict / failedKeys / missingKeys`
- blocker judgment 当前也已开始显式消费 release-level `overallVerdict`
- 总控结果区当前也已开始显式输出 `finalJudgment / finalJudgmentReason / newBlockingIssues / knownBlockingIssues`
- 总控结果区当前也已开始显式输出 `newBlockingIssueKeys / knownBlockingIssueKeys / blockingIssueSources`
- 总控结果区当前也已开始显式输出 `blockingIssueMatrix`
- 总控结果区当前也已开始显式输出 `blockingIssueSummary`
- 总控结果区当前也已开始显式输出 `blockingIssueActionPlan`
- 总控结果区当前也已开始显式输出 `releaseDecisionCard / blockingIssueDashboard`
- 总控结果区当前也已开始显式输出 `releaseGoNoGoCard / operatorRunCard`

这说明至少当前线上样本中的：

- 历史记录
- 联系方式申请
- 分享偏好

都已经没有待修存量。

## 4. 当前总包仍未覆盖的点

当前总包还没有覆盖：

1. `sendCode` 正式短信能力
2. 更长链路的“回流后再跳公开页”证据
3. 若后续还要继续做发布后脚本判定，可补更多业务 smoke URL 的预期状态

因此当前总包能证明：

- 主链正常
- 治理页正常
- 证据链完整

但还不能证明：

- 正式短信生产闭环

## 5. 与其它索引的关系

- 执行目录入口：`README.md`
- 证据类型索引：`evidence-index.md`
- 本文件：`evidence-bundle-index.md`
- 总控结构模板：`D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`

建议默认使用方式：

1. 先开 `evidence-bundle-index.md`
2. 按 `release-post-checklist.md` 逐项勾选发布后检查项
3. 需要细看某一类证据时，再跳 `evidence-index.md`
4. 需要看单样本原始产物时，再进入对应 `samples/*`

若后续其它业务域要照抄这套发布后总控结构，默认不要直接复制 share-card 明细字段，而是从模板开始：

1. 先按 `release-post-control-card-template.md` 建立 smoke / verdict / blocker / display 四层结构
2. 再把域内字段按向后兼容方式补进
3. 最终仍保持 `releaseGoNoGoCard -> operatorRunCard` 为默认第一读法

## 6. 下一轮补位建议

按优先级排序：

1. `sendCode` 正式短信能力验证样本
2. 回流后再跳公开页的更长链路证据
3. 若后续再扩充发布后留档，再把更多业务 smoke URL 的状态码、预期判定、统一 verdict、总判定与最终执行卡继续结构化
