# 00-68 执行记录

## 1. 当前状态

- 已完成 share 公开链事实源整改：`shareCard -> personalization -> actor detail` 断裂风险已由后端 `actorSnapshot` / fallback 与前端共享 loader 收口
- 已完成当前阶段海报能力口径整改：后端 `poster` capability / artifact、前端首页 / 卡片列表 / 编辑页 active 入口与用户文案已统一到“当前阶段可用”
- 已完成 00-28 状态卡、执行记录、证据入口与 runbook 回填；当前剩余外部阻塞只在小程序页面复验：WeChat DevTools 登录账号尚未获得目标 appid 开发者授权，`9421` automation endpoint 仍未恢复

## 2. 已固定的运行时事实

### 2.1 分享链断裂样本

`2026-04-13` 线上实测已确认：

- `GET /api/card/personalization?shareCardId=2&loadFortune=false` -> `200`
- 返回 `profile.actorId=10025`
- 继续 `GET /api/actor/10025` -> `500`
- message=`演员档案不存在`

同类样本还可在：

- `shareCardId=3 -> actorId=10026`
- `shareCardId=5 -> actorId=10007`

上重复出现。

### 2.2 海报门禁样本

`2026-04-13` 线上实测已确认：

- `shareCardId=2`
- `capability.canUseCustomPoster=false`
- `poster.locked=true`
- `poster.lockReason=会员可生成定制海报`

而前端首页、卡片列表、卡片编辑页当前仍展示“分享海报”按钮。

## 3. 下一步

- 按本 Spec 先整改事实源，再整改按钮与能力口径

## 4. 已完成整改

### 4.1 后端分享公开链

已在个性化聚合返回中补充最小持卡人快照：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\model\card\dto\ActorPersonalizationRespDTO.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\card\service\impl\ActorPersonalizationServiceImpl.java`

当前 `/api/card/personalization` 会直接返回：

- `actorSnapshot`

该快照通过 `ActorProfileService.profile(...)` 生成，允许在分享链使用最小 fallback 资料，不再强依赖 `/api/actor/{actorId}` 必须成功。

### 4.2 前端 latest loader

已将分享卡 latest loader 调整为优先消费聚合返回的 `actorSnapshot`：

- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-card-latest.ts`
- `D:\XM\kaipai-team\kaipai-frontend\src\types\personalization.ts`

当前逻辑为：

```text
优先 personalization.actorSnapshot
缺失时才 fallback 到 /api/actor/{actorId}
```

因此在后端新返回已就绪后，分享公开链将不再继续走脆弱二跳。

### 4.3 海报能力口径

已把当前阶段 poster 能力从“会员专属”调整为“可分享卡片用户可用”：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\membership\service\impl\MembershipAccountServiceImpl.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\card\service\impl\ActorPersonalizationServiceImpl.java`
- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-artifact.ts`

已完成调整：

- `canUseCustomPoster` 不再按会员态计算
- `poster.lockReason` 不再返回“会员可生成定制海报”
- 前端本地 fallback capability 也同步放开 poster

### 4.4 前端文案同步

已同步清理当前主链中的会员海报旧文案：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\utils\personalization-copy.ts`

### 4.5 前端 active 海报入口收口

已继续把当前 active 主链中的海报入口统一到同一份 capability 判断：

- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-artifact.ts`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

当前结果为：

- 首页与卡片列表的“分享海报”按钮已改为按共享 capability 显示，不再先展示、点击后再报锁定
- 卡片编辑页在 `shareMode=1&artifact=poster` 下也会先按 capability 规范化入口，不再保留旧 `locked -> toast` 分支
- 当前 active 主链已无 `海报暂不可用` / `当前海报能力暂不可用` 这类旧门禁提示

## 5. 验证记录

### 5.1 后端编译

- `cd D:\XM\kaipai-team\kaipaile-server && mvn -q -DskipTests compile`
- 结果：通过

### 5.2 前端类型检查

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- 结果：通过

### 5.3 小程序构建

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- 结果：通过，且已同步到 `dist/dev/mp-weixin`

### 5.4 Active 入口残留文案复核

- `rg -n "当前海报能力暂不可用|海报暂不可用|lockReason" D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`
- 结果：无命中
- 结论：当前 active 主链已不再保留点击后才告知海报锁定的旧交互文案

### 5.5 页面级证据复跑阻塞

- `python D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\run-share-card-mini-program-page-evidence.py 20260405-224334-dev-remote-governance-sample-v2 share-runtime-poster-page-evidence`
- 结果：失败，初始失败现场样本已落到 `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-083603-share-runtime-poster-page-evidence\`
- `captures/mini-program-screenshot-capture.stderr.log` 明确报错：`Failed connecting to ws://127.0.0.1:9421, check if target project window is opened with automation enabled`
- 随后复用仓内历史同机命令：
  - `D:\AP\微信web开发者工具\cli.bat auto --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin --auto-port 9421`
  - 返回：`Error: 登录用户不是该小程序的开发者`
  - 端口探测：`Get-NetTCPConnection -LocalPort 9421` -> `NO_LISTENER`
- 结论：当前 00-68 页面级真机证据的主阻塞不是脚本或页面逻辑，而是本机微信开发者工具账号未通过 `wxd38339082a9cfa4e` 的开发者授权，导致 automator 端口未恢复
- 说明：该目录只保留首次失败现场；当前默认 blocker 入口已不是这个目录，而是后续标准 blocker 包与内置 preflight 样本

### 5.6 首个 Blocker 包标准化（历史样本）

- 已继续改造：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\run-share-card-mini-program-page-evidence.py`
- 当前脚本在 page evidence 失败时，也会自动补标准 blocker 包，而不再只留下 stderr：
  - `summary.md`
  - `captures/devtools-auth-blocker.txt`
  - `captures/devtools-cli-auto.stdout.log`
  - `captures/devtools-cli-auto.stderr.log`
  - `captures/port-check.txt`
- 已用同一条失败路径再次复跑验证，产出首个标准 blocker 包样本：
  - `python D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\run-share-card-mini-program-page-evidence.py 20260405-224334-dev-remote-governance-sample-v2 share-runtime-poster-page-evidence-r2`
  - 历史样本：`D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-090456-share-runtime-poster-page-evidence-r2\`
- 关键结论已在 blocker 包中固定：
  - 首层失败：`Failed connecting to ws://127.0.0.1:9421`
  - 官方 CLI replay：`登录用户不是该小程序的开发者`
  - 端口检查：`NO_LISTENER`
  - 结论：当前阻塞明确停在 DevTools 开发者授权，不在页面实现或 automator 脚本逻辑
- 说明：`r2` 当前只保留为“首个标准 blocker 包”历史样本；当前默认 blocker 入口已进一步升级到 `20260420-161105-share-runtime-poster-page-evidence-r11 + preflight`

### 5.6.1 独立 DevTools 授权探针

- 已新增：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\run-share-card-devtools-auth-probe.py`
- 已产出当前样本：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-164437-share-card-devtools-auth-probe-r6\summary.md`
- 当前探针可在不启动整套 page evidence 的情况下，先固定：
  - `AppID`
  - `cli auto --project ... --auto-port 9421` replay 结果
  - `9421` 端口监听状态
  - 当前是否仍卡在 DevTools 开发者授权
- 当前结论：
  - `probeResult=devtools_auth_gate`
  - `port-check=NO_LISTENER`
  - 当前阻塞继续停在 DevTools 开发者授权
- `2026-04-20 14:29:22 ~ 16:44:37 +0800` 已按 `share-card-devtools-auth-probe-r2 ~ r6` 连续复跑该探针；结果持续固定为 `probeResult=devtools_auth_gate` 与 `port-check=NO_LISTENER`。其中从 `r5` 起，探针 CLI stdout 与 `probe-result.json` 已同步显式带出 `sampleId / probeSummaryPath / resultPath / portCheckResult / cliReplay`；当前最新入口固定为 `r6`

### 5.6.2 page evidence 内置 preflight 收口

- 已继续改造：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\run-share-card-mini-program-page-evidence.py`
- 当前脚本会先内置执行同一套 DevTools auth probe，再决定是否进入 `capture-mini-program-screenshots.js`
- 已复跑验证：
  - `python D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\run-share-card-mini-program-page-evidence.py 20260405-224334-dev-remote-governance-sample-v2 share-runtime-poster-page-evidence-r3`
  - 新 page-evidence blocker 样本：`D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-130633-share-runtime-poster-page-evidence-r3\`
  - 同步落下的 preflight 样本：`D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-130633-share-runtime-poster-page-evidence-r3-preflight\`
- 当前验证结果：
  - page evidence 在 preflight 阶段即被拦截，未再启动大截图链路
  - blocker 摘要已显式回链 preflight 样本
  - preflight 仍固定出 `probeResult=devtools_auth_gate`
  - `9421` 端口仍为 `NO_LISTENER`
  - 因此当前阻塞仍明确停在 DevTools 开发者授权，而不是页面实现或截图脚本逻辑

- 已继续验证自动总控兼容：
  - `python D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\run-share-card-release-post-checklist-record.py --label share-card-release-post-checklist-record-auto-v28 --mini-blocker-sample 20260420-130633-share-runtime-poster-page-evidence-r3`
  - 新样本：`D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-130653-share-card-release-post-checklist-record-auto-v28\`
  - 结论：`ReleaseDecisionCard / BlockingIssueDashboard / ReleaseGoNoGoCard / OperatorRunCard` 仍一致收口到 `mini_program_devtools_auth_gate`

### 5.7 自动总控接入 blocker 样本

- 已继续改造：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\run-share-card-release-post-checklist-record.py`
- 当前自动总控已可同时消费：
  - 成功的小程序页面样本 `share-card-mini-program-page-evidence-v3`
  - 首个失败但标准化留档的 blocker 样本 `share-runtime-poster-page-evidence-r2`（历史）
  - 最新默认 blocker 样本 `share-runtime-poster-page-evidence-r11`（当前）
- 近期关键里程碑已收口为：
  - `auto-v29`：在不显式传 `--mini-blocker-sample` 时，脚本会自动命中执行当时的最新 blocker 样本；后续又由 `auto-v38 / auto-v43 / auto-v44 / auto-v45 / auto-v46` 持续验证，当前最新 blocker 样本为 `r11`
  - `auto-v32 ~ auto-v33`：已把 blocker 样本选择结果收口为 `SelectionMode + SelectionDisplay + SelectionNote`，并同步写入 summary、`checklist-result.json` 与 CLI stdout
  - `auto-v36 ~ auto-v40`：已把“等待最新样本稳定”窗口分别验证到 blocker 并发场景与 admin 并发场景；当前在放宽等待窗口后，默认解析会直接命中最新 admin 页面样本 `v7`
  - `auto-v41`：已把 auto-latest 选样本规则收紧为“最终结果文件优先”，mini blocker 当前优先匹配 `page-evidence-result.json`，admin 页面当前优先匹配 `admin-page-evidence-result.json`
  - `auto-v42`：已把 `adminSampleSelectionMode / adminSampleSelectionDisplay / adminSampleSelectionNote` 同步写入 summary、`checklist-result.json` 与 CLI stdout
  - `auto-v43 ~ auto-v44`：在继续自动命中当时最新 blocker / admin 样本的同时，验证 `r10 -> r11` 的默认口径前移与 `preflightProbeResultPath` 引入后没有破坏自动总控默认读法
  - `auto-v45`：已把 `Mini Program Blocker Preflight Summary / Result` 明确带入 summary 与 `checklist-result.json`
  - `auto-v46`：再把同一组 blocker preflight 字段补齐到 CLI stdout；当前最完整验证样本也前移到 `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-163835-share-card-release-post-checklist-record-auto-v46\`
- 已继续补齐脚本帮助入口：
  - `python D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\run-share-card-devtools-auth-probe.py --help`
  - `python D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\run-share-card-mini-program-page-evidence.py --help`
  - `python D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\run-share-card-admin-page-evidence.py --help`
  - 结论：三支脚本当前都已切到 `argparse`；`--help` 会直接输出帮助并退出，不会再误把 `--help` 当样本标签创建目录。同步核验时 `samples/` 目录数量保持 `76 -> 76`，且未新增 `*help*` 目录。
  - 补充结论：PowerShell 下空字符串占位参数会被吞掉，因此 mini/admin 两支脚本当前又已补成“一参 label-only 自动兼容”的调用入口，不必再依赖 `'' <label>` 形式
  - 帮助文案当前也已同步为真实口径：`source_sample` 现写明“省略即自动选最新 source sample；PowerShell 下一参未知 positional 会按 label 解释”，不再继续提示空字符串占位
- 已生成新的自动总控样本：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-100449-share-card-release-post-checklist-record-auto-v21\summary.md`
- 当前 `auto-v21` 已新增：
  - `Mini Program Blocker Sample`
  - `mini_program.blocker_*` 检查项
  - 已知阻塞 `mini_program_devtools_auth_gate`
- `2026-04-20 11:55:22 +0800` 又已生成 `auto-v22`：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-115522-share-card-release-post-checklist-record-auto-v22\summary.md`
- 当前 `auto-v22` 已继续把操作卡主风险收口到 `00-68` 当前 blocker：
  - `ReleaseDecisionCard.topRisk` 已改为 DevTools 开发者授权阻塞
  - `ReleaseGoNoGoCard.owner / nextAction` 已优先指向 `wechat-devtools / automation-auth`
  - `OperatorRunCard.immediateSteps` 已显式加入“恢复 DevTools 开发者授权后，重跑 share-card mini-program page evidence”
- `2026-04-20 11:59:11 +0800` 又已生成 `auto-v23`：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-115911-share-card-release-post-checklist-record-auto-v23\summary.md`
- 当前 `auto-v23` 已继续把已知 blocker 的展示顺序也对齐到当前主风险：
  - `FinalJudgmentReason` 先写 DevTools 授权 blocker，再写 `sendCode`
  - `Known Blocking Issue Keys` 已改为 `mini_program_devtools_auth_gate -> send_code_dev_mode`
  - `Known Blocker / Blocking Issue Matrix / Action Plan` 顺序也已同步
- `2026-04-20 12:02:49 +0800` 又已生成 `auto-v24`：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-120249-share-card-release-post-checklist-record-auto-v24\summary.md`
- 当前 `auto-v24` 已继续把 `operatorRunCard` 的批次字段也收口到当前主风险：
  - `primaryIssueKey=mini_program_devtools_auth_gate`
  - `followupBatch=wechat-devtools authorization`
  - 不再在主风险是 DevTools blocker 时继续把 `followupBatch` 写成 `00-51 formal sms`
- `2026-04-20 12:07:24 +0800` 又已生成 `auto-v25`：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-120724-share-card-release-post-checklist-record-auto-v25\summary.md`
- 当前 `auto-v25` 已继续把 `releaseGoNoGoCard` 的批次开关字段也收口到当前主风险：
  - `primaryIssueKey=mini_program_devtools_auth_gate`
  - `needsBatchSwitch=False`
  - 不再在主风险是 DevTools blocker 时继续把 `needsBatchSwitch` 维持为 `True`
- `2026-04-20 12:14:17 +0800` 又已生成 `auto-v26`：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-121417-share-card-release-post-checklist-record-auto-v26\summary.md`
- 当前 `auto-v26` 已继续把 `blockingIssueDashboard / Notes` 也收口到当前主风险：
  - `blockingIssueDashboard.primaryIssueKey=mini_program_devtools_auth_gate`
  - `blockingIssueDashboard.topRisk / primaryOwner / nextAction` 已与操作卡一致
  - `owners` 顺序已改为主风险 owner 在前
  - `Notes` 已改成“DevTools 开发者授权恢复后的 page evidence 复跑，其次是正式短信能力验证样本”
- `2026-04-20 12:20:17 +0800` 又已生成 `auto-v27`：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-122017-share-card-release-post-checklist-record-auto-v27\summary.md`
- 当前 `auto-v27` 已继续把摘要层剩余读法也收口到当前主风险：
  - `OperatorRunCard.primaryIssueKey` 已显示到 summary
  - `Blocker Judgment` 里 `mini_program_blocker_recorded` 已提到 `sendCode` 之前
- 结论：00-68 当前的 DevTools 授权阻塞已不再只存在于 execution 备注，而是已进入 share-card 默认自动总控读法，且当前总控卡会优先指向它

### 5.8 runbook / Spec 状态同步

- 已继续回填：
  - `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\README.md`
  - `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\backend-admin-standard-release.md`
  - `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`
  - `D:\XM\kaipai-team\.sce\specs\00-68-current-phase-share-runtime-and-poster-capability-alignment\requirements.md`
- 当前 runbook 层已统一：
  - 默认总控基线仍为 `auto-v27`
  - `auto-v28` 只作为“最新 preflight blocker 样本进入自动总控后仍兼容默认读法”的验证样本
  - 若 `primaryIssueKey=mini_program_devtools_auth_gate`，默认不再先翻旧 stderr，而是直接先看：
    - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-161105-share-runtime-poster-page-evidence-r11\summary.md`
    - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\samples\20260420-161105-share-runtime-poster-page-evidence-r11-preflight\summary.md`
  - 当前标准判断顺序也已固定为：先确认 `probeResult=devtools_auth_gate`，再确认 `portCheck=NO_LISTENER`，只有探针恢复后才继续重跑 page evidence
- 当前 `00-68 requirements.md` 也已同步升为：
  - `状态：已完成`
  - 验收项全部勾选完成
- 结论：00-68 当前已不仅完成代码、页面与样本层收口，也已把“默认总控读法 / blocker 阅读顺序 / Spec 状态”同步回填到运维手册与 Spec 本体；仓内剩余未完成项已只剩外部 DevTools 授权恢复后的复跑验证

## 6. 剩余动作

### 6.1 发布记录

本轮已按 `00-29` 标准 `backend-only` 连续发布两次：

1. 首轮发布：
   - `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\20260413-112203-backend-only-share-runtime-poster-align.md`
2. 二次修正发布：
   - `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\20260413-112542-backend-only-share-runtime-poster-align-r2.md`

二次修正原因：

- 首轮已补 `actorSnapshot` 和 poster 门禁口径，但旧前端仍会继续请求 `/api/actor/{actorId}`
- 因此又补了一刀后端公开详情 fallback，并把 poster 能力从“可分享卡片用户”进一步放宽为“当前阶段直接可用”

### 6.2 发布后线上验证

`2026-04-13` 发布后已复测：

1. `GET http://101.43.57.62/api/actor/10025`
   - 返回：`200`
   - 结论：旧前端继续走 `/api/actor/{actorId}` 时，也不再报“演员档案不存在”

2. `GET http://101.43.57.62/api/card/personalization?shareCardId=2&loadFortune=false`
   - 返回包含 `actorSnapshot`
   - `capability.canUseCustomPoster=true`
   - `poster.locked=false`
   - `poster.lockReason=null`
   - 结论：poster 当前阶段线上门禁已解除

### 6.3 当前结论

- 线上“演员档案不存在”主问题已通过后端 fallback 修复
- 线上 `poster` 会员门禁已解除
- 当前旧前端也可直接受益，不依赖小程序代码先上传后才能生效

## 7. 剩余动作

- 若要让本地小程序代码与线上后端口径完全一致，仍可继续使用已构建好的 `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- 页面级真机证据当前仍受 DevTools 开发者授权阻塞；待 `cli auto --project ... --auto-port 9421` 恢复后，可继续补“按钮可点击 -> 海报生成成功”样本
