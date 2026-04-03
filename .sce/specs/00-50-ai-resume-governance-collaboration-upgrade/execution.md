# 00-50 执行记录

## 1. 调查结论

- AI 简历当前真正未闭环的，不再是接口、角色矩阵、页面证据或最小协同动作
- 现有执行记录已经证明：`assign -> acknowledge / remind`、协同状态筛选、审计回看和目标环境业务回归都已成立
- 当前缺的是一张独立 Spec，把“通知回执 / 自动催办 / SLA 规则”从状态描述升级为后续推进门禁

## 2. 本轮落地

- 新增 `00-50` Spec，正式记录 AI 简历治理协同升级入口
- 明确通知回执、自动催办与 SLA 的后续实现边界
- 明确后端、后台、验证脚本和审计链的下一轮落点
- 回写 `phase-01-roadmap.md`、`ai-resume-status.md`、`overall-architecture-assessment.md`、`execution/ai-resume/README.md`、`tasks.md`
- 完成 Spec 索引与映射登记
- 已落第一批代码切片，把“通知 / 回执 / 催办 / SLA”从纯文档 blocker 推进到可查询、可展示的派生治理字段：
  - 后端 `AdminAiResumeGovernanceServiceImpl` 基于既有 `assign / acknowledge / remind` 事实，派生 `notificationStatus / notificationSentAt / notificationReceiptStatus / notificationReceiptAt / autoRemindStage / slaStatus`
  - `GET /admin/ai/resume/failures` 与 `/sensitive-hits` 已支持按 `notificationStatus / notificationReceiptStatus / autoRemindStage / slaStatus` 筛选
  - 后台 `AiResumeGovernanceView.vue` 已补通知状态、回执状态、催办阶段与 SLA 状态筛选，并在失败样本 / 敏感命中列表、处置详情与动作弹窗里显示这些治理标签
  - 标准脚本 `run-ai-resume-collaboration-validation.py` 已扩展为同时校验派生字段与新增筛选口径
- 已落第二批代码切片，把 `00-50` 里定义的“手工接管 / 跳过自动催办”补成真实治理动作：
  - 后端已新增 `POST /admin/ai/resume/failures/{failureId}/manual-takeover` 与 `/skip-auto-remind`
  - 失败样本记录、时间线 note 与后台返回 DTO 已补 `manualTakeover*`、`autoRemindSkipped*` 元数据
  - `autoRemindStage` 已能显式区分 `manual_takeover` 与 `skipped`
  - 后台 AI 治理页已补“手工接管 / 跳过催办”动作按钮、详情回看与审计筛选
  - 标准脚本已扩展 `manual_takeover`、`skip_auto_remind` 两类动作与日志命中校验
- 已落第三批代码切片，把“通知发送 / 通知回执”补成显式治理动作，而不是继续只靠 `assign / remind / acknowledge` 派生：
  - 后端已新增 `POST /admin/ai/resume/failures/{failureId}/record-notification` 与 `/record-notification-receipt`
  - 失败样本记录与时间线已补 `notificationStatus / notificationSentAt / notificationFailureReason / notificationReceiptStatus / notificationReceiptAt / notificationReceiptFailureReason`
  - `assign` 当前只代表责任分派，不再默认等于“通知已发送成功”；显式通知动作成为真正的通知事实源
  - 后台 AI 治理页已补“记录通知 / 记录回执”动作、发送成功/失败与送达/回执失败结果选择，以及异常原因回看
  - 标准脚本已改成校验 `assign -> pending_send`、`record_notification -> sent`、`record_notification_receipt -> delivered`、`acknowledge -> received` 的显式通知链
- 已落第四批代码切片，把“自动催办 / 超时升级”补成真实的服务端治理规则执行入口，而不再只是前端派生标签：
  - 后端已新增 `POST /admin/ai/resume/governance-sweep/preview` 与 `/execute`，支持对指定失败样本按服务端规则预览或执行治理 sweep
  - sweep 规则已显式固化 `签收 SLA 4h + 自动催办冷却 1h + 最大自动催办 2 次 + 超时后升级`，并以服务端计算结果返回 `auto_remind / timeout_escalation`
  - 真正执行时会写入 `ai_resume_auto_remind` 与 `ai_resume_timeout_escalation` 审计日志，失败样本时间线也会新增 `auto_remind / timeout_escalation` 动作
  - 后台 AI 治理页已补这些新动作的时间线标签与审计动作标签，避免重新退回显示原始 operation code
  - 标准脚本 `run-ai-resume-collaboration-validation.py` 已继续扩展，新增自动催办样本与 SLA 超时升级样本，并校验对应 operation log 命中
- `2026-04-04 01:37` 首轮真实总控样本 `execution/ai-resume/samples/20260404-013746-continue-ai-resume-governance-sweep/summary.md` 暴露出新的真实环境问题：`record-notification` 业务已成功，但 `admin_operation_log.request_id VARCHAR(64)` 被长 `X-Request-Id` 打爆，导致接口在审计插入阶段返回 `code=500`
- 同日已按 `00-29` 标准链路完成修复与回填：
  - 新增后端兜底：`AdminOperationLogger` 只在超出库宽时才归一化 `request_id`
  - 新增 schema migration：`V20260404_001__admin_operation_log_request_id_expand.sql`，把 `admin_operation_log.request_id` 扩到 `VARCHAR(128)`
  - 新增 `AdminOperationLoggerTest`，覆盖“库宽内保留原值 / 超宽时归一化”两类行为
  - 标准 schema 发布记录：`.sce/runbooks/backend-admin-release/records/20260404-014856-backend-schema-admin-operation-log-requestid-expand.md`
  - 标准 backend-only 发布记录：`.sce/runbooks/backend-admin-release/records/20260404-014954-backend-only-ai-resume-governance-requestid-expand.md`
  - 最新真实总控样本：`execution/ai-resume/samples/20260404-015141-continue-ai-resume-governance-requestid-expand/summary.md` 已重新通过，`assign / record_notification / record_receipt / acknowledge / remind / skip_auto_remind / manual_takeover / auto_remind / timeout_escalation` 均可按原始 `X-Request-Id` 命中审计日志

## 3. 验证

- 后端在临时切到 `C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot` 后执行 `mvn -q -DskipTests compile` 通过
- 后端执行 `mvn -q -Dtest=AdminOperationLoggerTest test` 通过
- 后台执行 `npm run type-check` 通过
- 后台执行 `npm run build` 通过
- 验证脚本执行 `python -m py_compile execution/ai-resume/run-ai-resume-collaboration-validation.py` 通过
- 当前已存在的真实样本继续作为本 Spec 的证据基线：
  - `execution/ai-resume/samples/20260403-164135-continue-ai-collaboration-closure/summary.md`
  - `execution/ai-resume/samples/20260403-165026-continue-ai-business-regression-summary/summary.md`
  - `execution/ai-resume/samples/20260403-161131-ai-admin-page-evidence/summary.md`
  - `execution/ai-resume/samples/20260403-162122-ai-mini-program-page-evidence-rerun/summary.md`
  - `execution/ai-resume/samples/20260404-015141-continue-ai-resume-governance-requestid-expand/summary.md`
- 这说明 `00-50` 已经不再只是“定义未来需求”，而是已经落下“显式通知事实 + 服务端治理 sweep + 标准样本”三批可验证代码口径；但真实通知送达渠道与后台定时调度任务仍未实现

## 4. 后续入口

- 后续 AI 简历的治理协同实现，统一以 `00-50` 为上位入口
- 当前治理 sweep 已能由服务端规则直接判定并执行自动催办 / 超时升级，但仍不等于真实通知通道或后台定时任务
- 当前已经具备通知回执样本、自动催办样本与 SLA 超时升级样本；后续闭环门禁改为“真实通知渠道回执 + 后台定时调度”
- 真实 LLM 接入仍保留为并行但独立的后续入口，不与本 Spec 混为同一实现批次
