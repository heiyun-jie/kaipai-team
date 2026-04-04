# AI 简历润色闭环执行卡

本目录用于承接 `slices/ai-resume-polish-capability-slice.md` 的下一层拆分。

## 目标

把“AI 简历润色闭环”从能力切片继续拆成可分派、可并行推进、可单独验收的 4 张执行卡，并补一份角色授权收口说明：

1. 前端执行卡
2. 后端执行卡
3. 后台执行卡
4. 联调执行卡
5. 角色授权收口说明

## 使用方式

每张执行卡都只负责一个交付面，但必须引用同一张能力切片卡：

- `../../slices/ai-resume-polish-capability-slice.md`
- `role-authorization-closure.md`

## 本轮规则

- 每张卡都要写清楚负责范围，不得跨层级抢活
- 每张卡都要标明依赖项和交付物
- 联调卡不负责补做功能，只负责收口验证、问题清单和回归要求
- 当前必须承认真实现状：编辑页 patch 流程、后台治理页、治理动作审计、角色页授权矩阵与建议授权包都已落地，且目标环境角色矩阵已通过标准样本收口；仓内与目标环境后台静态入口也都已移除 `operation-logs` 对 AI 治理的权限兜底，最小责任协同也已通过标准样本复验，但真实 LLM 与更完整治理协同仍未完成

## 当前标准样本入口

- 真实联调脚本：`run-ai-resume-validation.py`
- 治理协同脚本：`run-ai-resume-collaboration-validation.py`
- 通知基础设施脚本：`run-ai-resume-notification-foundation-validation.py`
- HTTP bridge mock 脚本：`run-ai-notification-http-bridge-mock.py`
- 业务回归汇总脚本：`run-ai-resume-business-regression-summary.py`
- 角色收口脚本：`run-ai-role-authorization-closure.py`
- 小程序页面证据脚本：`run-ai-mini-program-page-evidence.py`
- 后台页面证据脚本：`run-ai-admin-page-evidence.py`
- 最新主链样本：`samples/20260403-071241-continue-rerun/summary.md`
- 最新协同样本：`samples/20260403-164135-continue-ai-collaboration-closure/summary.md`
- 最新业务回归样本：`samples/20260403-165026-continue-ai-business-regression-summary/summary.md`
- 最新角色收口样本：`samples/20260403-072120-continue-ai-role-closure/summary.md`
- 最新小程序页面样本：`samples/20260403-162122-ai-mini-program-page-evidence-rerun/summary.md`
- 最新后台页面样本：`samples/20260403-161131-ai-admin-page-evidence/summary.md`
- 最新 DevTools 恢复样本：`samples/20260403-161755-ai-mini-program-devtools-replay/cli-auto-output.txt`
- 最新目标环境发布复验记录：`../../../../runbooks/backend-admin-release/records/20260403-162902-admin-only-ai-fallback-retirement-static-sync.md`
- 最新 `00-59` 目标环境代码发布记录：`../../../../runbooks/backend-admin-release/records/20260404-045135-backend-only-ai-resume-governance-scheduled-sweep.md`
- 最新 `00-59` Nacos 配置同步记录：`../../../../runbooks/backend-admin-release/records/20260404-045734-backend-nacos-ai-resume-governance-scheduler-enable.md`
- 最新 `00-59` 运行时重建记录：`../../../../runbooks/backend-admin-release/records/20260404-045811-backend-only-ai-resume-governance-scheduler-reload.md`
- 最新 `00-60` 配置同步记录：`../../../../runbooks/backend-admin-release/records/20260404-072827-backend-ai-notification-config-pipeline-continue-ai-notification-random-token.md`
- 最新 `00-60` schema 记录：`../../../../runbooks/backend-admin-release/records/20260404-073019-backend-schema-continue-ai-notification-random-token.md`
- 最新 `00-60` backend-only 记录：`../../../../runbooks/backend-admin-release/records/20260404-073310-backend-only-continue-ai-notification-random-token.md`
- 最新 `00-60` 首轮阻塞样本：`samples/20260404-073450-continue-ai-notification-random-token/summary.md`
- 最新 `00-60` 通过样本：`samples/20260404-073638-continue-ai-notification-random-token-after-admin-contact/summary.md`
- 当前已固定的真实链路：
  - actor `quota -> polish-resume -> actor/profile save(aiResumeApplyMeta) -> history -> rollback`
  - admin `overview -> histories -> failures -> sensitive-hits -> review -> close -> operation-logs`
  - collaboration `collaboration-catalog -> assign -> acknowledge / remind -> operation-logs`
  - notification foundation `assign -> dispatch sent/send_failed -> provider callback(delivered/receipt_failed) -> failure summary refresh`
  - regression-summary `validation sample -> mini-program page evidence -> business regression summary`
- 当前页面级证据入口：
  - `run-ai-mini-program-page-evidence.py` 会基于最新 AI 样本回放 `actor-card -> actor-profile/edit -> actor-profile/edit?aiResume=1 -> actor-profile/detail`
  - `run-ai-admin-page-evidence.py` 会基于最新 AI 样本回放 `/system/ai-resume-governance` 的 overview、history detail、failure detail
- 当前未闭环边界：
  - 目标环境 AI 角色矩阵已收口为 `aiReadyRoleCount=1 / fallbackRoleCount=0 / canRetireFallback=true`
  - `2026-04-03 16:17` 已通过官方 `cli auto --project ... --auto-port 9421` 恢复 DevTools 自动化；`16:22` 又已通过 `run-ai-mini-program-page-evidence.py` 产出 `actor-card -> actor-profile/edit -> actor-profile/edit?aiResume=1 -> actor-profile/detail` 四页真机页面证据，当前前后台页面级证据均已补齐
  - `2026-04-03 16:29` 已按 `00-29` 标准 `admin-only` 脚本完成目标环境后台静态资源发布，发布记录为 `../../../../runbooks/backend-admin-release/records/20260403-162902-admin-only-ai-fallback-retirement-static-sync.md`；公网首页已切到 `index-bd3NuCPI.js`，且 bundle 内不再包含 `pagePermissionFallbacks:["page.system.operation-logs"]`
  - `2026-04-03 16:41` 已通过 `run-ai-resume-collaboration-validation.py` 固定最小协同样本：当前真实环境已可复验 `assign -> acknowledge`、`assign -> remind`、协同状态筛选与 `ai_resume_assign / acknowledge / remind` 审计回看
  - `2026-04-03 16:50` 已通过 `run-ai-resume-business-regression-summary.py` 固定一条标准业务回归记录：同一轮样本已串起 `quota -> polish -> save -> history -> rollback` 与 `actor-card / actor-profile-edit / actor-profile-edit?aiResume=1 / actor-profile-detail` 四页真机页面证据
- `2026-04-04 07:36 +0800` 已按 `00-29` 标准链路在目标环境跑通 `manual provider + shared callback secret` 的真实通知基础设施样本；当前未闭环的已不再是基础设施本身，而是商用通知 vendor 实发链与真实 LLM
- 同轮后续第三批又已补通用 `http` provider adapter 与 `AI_RESUME_NOTIFICATION_HTTP_*` provider-aware 配置位；当前后端已允许通过固定 JSON 契约把通知发送桥接到外部网关/厂商适配服务，但真实 vendor endpoint/credential 仍未固化
- 同轮又已补 `run-ai-notification-http-bridge-mock.py` 与 provider-aware 的 `run-ai-resume-notification-foundation-validation.py`；当前即使缺真实厂商账号，也可先按 spec 固化 `provider-code=http` 的桥接样本入口
- `2026-04-04 08:32 +0800` 已本地实跑 `run-ai-notification-http-bridge-mock.py --max-requests 1`，并在 `samples/20260404-083225-local-http-bridge-smoke/` 固定一条桥接请求样本：返回 `providerCode=http / channelCode=sms / providerMessageId=mock-http-20260404083227-0001 / sendStatus=sent`
- `2026-04-04 08:36 +0800` 又已本地实跑带 `callbackUrl / callbackHeader / callbackToken` 的自动回调样本，并在 `samples/20260404-083643-local-http-bridge-autocallback-smoke/` 固定 `callbackSuccessCount=1 / callbackFailureCount=0`
- 同轮后续又已补 `provider=http` 的 bridge 输入契约、本地门禁和标准总控 `run-ai-notification-http-provider-rollout.py`；当前若没有真实 bridge endpoint，本轮标准结论应为 blocked，而不是继续手工改 Nacos
- `2026-04-04 08:54 +0800` 已按标准入口固定一条 blocked 证据：`read-local-ai-notification-http-bridge-inputs.py --label continue-http-provider-bridge-gate` 的诊断目录为 `../../../../runbooks/backend-admin-release/records/diagnostics/20260404-085414-continue-http-provider-bridge-gate/`，`run-ai-notification-http-provider-rollout.py --dry-run` 的记录为 `../../../../runbooks/backend-admin-release/records/20260404-085414-backend-ai-notification-http-provider-rollout-continue-http-provider-bridge-gate.md`；当前根因已明确收口为 `AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT` 缺失
- `2026-04-04 09:01 +0800` 已通过 `../../../../runbooks/backend-admin-release/scripts/run-ai-notification-http-bridge-mock-remote-release.py` 在目标环境启动 remote mock bridge，并在 `../../../../runbooks/backend-admin-release/records/20260404-090124-ai-notification-http-bridge-remote-continue-http-provider-remote-bridge.md` 固定远端证据
- `2026-04-04 09:05 +0800` 又已通过 `../../../../runbooks/backend-admin-release/scripts/run-ai-notification-http-bridge-proxy-sync.py` 把公网 `http://101.43.57.62/bridge/ai-notification/` 代理到目标环境 bridge 进程，对应记录为 `../../../../runbooks/backend-admin-release/records/20260404-090551-ai-notification-http-bridge-proxy-continue-http-provider-bridge-proxy.md`
- 首轮 `provider=http` rerun 暴露两条真实缺口都已收口：一是 provider callback 路径仍被统一未登录链拦截，现已改为在 `JwtFilter` 内直接识别共享 callback header/token；二是总控脚本未把 `AI_NOTIFICATION_CALLBACK_TOKEN` 别名传给验证脚本，现已在 `run-ai-notification-http-provider-rollout.py` 内统一映射
- `2026-04-04 09:30 +0800` 已按同一总控在目标环境跑通 `provider=http`，记录为 `../../../../runbooks/backend-admin-release/records/20260404-092818-backend-ai-notification-http-provider-rollout-continue-http-provider-real-route-rerun6.md`，最新通过样本为 `samples/20260404-093013-continue-http-provider-real-route-rerun6/summary.md`
  - 其中“真实通知基础设施 / 回执事实源”后续统一以 `../../00-60-current-phase-ai-governance-real-notification-foundation/` 为直接推进入口；`../../00-50-ai-resume-governance-collaboration-upgrade/` 继续保留为已完成的协同模型升级上位 Spec
  - “后台定时调度任务”当前阶段已由 `../../00-59-current-phase-ai-governance-scheduled-sweep/` 收口为服务端内建入口，且 `2026-04-04 05:01:40 +0800` 已在目标环境捕获首轮运行样本；后续只剩真实通知基础设施 / 回执事实源与真实 LLM

## `run-ai-resume-notification-foundation-validation.py` 使用说明

- 用途：固定 `00-60` 的四类标准样本
  - dispatch 发送成功
  - dispatch 发送后 pending_receipt
  - provider callback delivered
  - provider callback receipt_failed
  - 人工 `send_failed` 补录
- 关键环境变量：
  - `AI_NOTIFICATION_BASE_URL`
  - `AI_NOTIFICATION_ADMIN_ACCOUNT`
  - `AI_NOTIFICATION_ADMIN_PASSWORD`
  - `AI_NOTIFICATION_USER_PHONE`
  - `AI_NOTIFICATION_PROVIDER_CODE`（默认 `manual`，切到 `http` 时会把 callback sample 的 `providerCode` 同步改成 `http`）
  - `AI_NOTIFICATION_CALLBACK_HEADER`
  - `AI_NOTIFICATION_CALLBACK_TOKEN`
- 额外运行时配置输入：`AI_RESUME_NOTIFICATION_HTTP_ENDPOINT / AI_RESUME_NOTIFICATION_HTTP_AUTH_HEADER / AI_RESUME_NOTIFICATION_HTTP_AUTH_TOKEN`（仅当目标环境 `provider-code=http` 时需要通过 `00-29` 总控同步）
- 额外运行时配置输入：`AI_RESUME_NOTIFICATION_CALLBACK_URL / AI_RESUME_NOTIFICATION_HTTP_ENDPOINT / AI_RESUME_NOTIFICATION_HTTP_AUTH_HEADER / AI_RESUME_NOTIFICATION_HTTP_AUTH_TOKEN`（仅当目标环境 `provider-code=http` 时需要通过 `00-29` 总控同步；其中 callbackUrl 用于 bridge/vendor 自动回调）
- 注意：
  - 该脚本默认要求目标环境已经配置 `kaipai.ai.resume.notification.enabled=true`
  - callback 校验依赖 `AI_NOTIFICATION_CALLBACK_TOKEN`
  - `AI_NOTIFICATION_CALLBACK_TOKEN` 是 provider callback header 的共享密钥，不是后台 JWT，也不是手机号登录 token
  - 当目标环境 `provider-code=http` 时，还需要先通过 `00-29` 总控把 `kaipai.ai.resume.notification.http.endpoint`（及可选 auth）同步进 Nacos，再做样本验证
  - `run-ai-notification-http-provider-rollout.py` 当前会自动把本地 secret 中的 `AI_RESUME_NOTIFICATION_CALLBACK_HEADER / TOKEN` 映射成验证脚本读取的 `AI_NOTIFICATION_CALLBACK_HEADER / TOKEN`，不需要再手工临时补环境变量
  - 最新首轮失败样本 `samples/20260404-073450-continue-ai-notification-random-token/summary.md` 证明：当 callback token、Nacos、schema 与发布都已生效后，脚本会继续暴露真实运行时数据问题，本轮根因是 `adminUserId=2` 缺联系方式
  - 最新通过样本 `samples/20260404-073638-continue-ai-notification-random-token-after-admin-contact/summary.md` 已固定 `manual provider + enabled=true` 下的 dispatch / callback / manual backfill 五类标准样本
  - 最新通过样本 `samples/20260404-093013-continue-http-provider-real-route-rerun6/summary.md` 已固定 `provider=http + remote mock bridge + nginx public proxy` 下的同一套五类标准样本

## `run-ai-notification-http-bridge-mock.py` 使用说明

- 用途：在缺真实厂商账号时，为 `provider-code=http` 提供可复跑的固定 JSON 契约 mock gateway
- 启动示例：
  - `python .sce/specs/00-28-architecture-driven-delivery-governance/execution/ai-resume/run-ai-notification-http-bridge-mock.py --label ai-http-bridge --host 0.0.0.0 --port 19081 --auth-token <token>`
- 返回契约：
  - 成功：`success=true`、`providerCode=http`、`providerMessageId`、`channelCode`、`sendStatus=sent`
  - 失败：支持通过 `X-Mock-Force-Status: send_failed`、`mockSendStatus=send_failed` 或 reason/instruction 包含 `[mock-http-send-failed]` 强制返回失败
- 自动回调：
  - 若请求体里带 `callbackUrl / callbackHeader / callbackToken`，mock bridge 会在 send 成功后自动回打一条 `providerCode=http / receiptStatus=delivered` 的回执
- 产物：
  - 会在 `samples/<capture-id>/` 下落 `requests.jsonl`、`summary.json`、`summary.md`
- 推荐用途：
  - 先把目标环境 `provider-code` 切到 `http`
  - 用 `00-29` 总控同步 `http.endpoint` 指向 mock gateway
  - 再跑 `run-ai-resume-notification-foundation-validation.py`，固化 bridge 样本

## `run-ai-notification-http-provider-rollout.py` 使用说明

- 用途：把 `provider-code=http` 的 bridge 输入门禁、Nacos 同步、`backend-only` 与通知样本验证固定成一条总控
- 前置输入：
  - `.sce/config/local-secrets/ai-resume-notification.env`
  - `.sce/config/local-secrets/ai-notification-http-bridge.env`
- dry-run：
  - `python .sce/runbooks/backend-admin-release/scripts/run-ai-notification-http-provider-rollout.py --label <label> --operator <name> --dry-run`
- 正式执行：
  - `python .sce/runbooks/backend-admin-release/scripts/run-ai-notification-http-provider-rollout.py --label <label> --operator <name>`
- blocked 语义：
  - 若 bridge endpoint / callback base url 缺失，脚本会直接输出 blocked 记录
  - blocked 代表“真实 bridge 输入未就绪”，不是“代码适配层仍未完成”
