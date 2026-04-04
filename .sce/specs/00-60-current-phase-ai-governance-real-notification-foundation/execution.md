# 00-60 执行记录

## 1. 调查结论

- `00-50` 与 `00-59` 已经把 AI 治理的协同模型、自动催办规则与服务端调度入口补齐
- 当前 AI 治理真正未闭环的，不再是“有没有通知状态字段”或“有没有定时任务”
- 当前缺的是“真实通知基础设施 + 真实回执事实源”

仓内现状调查结果如下：

- `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java`
  - `sendCode(...)` 只是 login-auth 开发态验证码能力
  - 逻辑是生成验证码 -> 写 Redis -> 直接返回
  - 不具备 AI 治理通知基础设施的复用条件
- `kaipaile-server/src/main/java/com/kaipai/module/model/system/entity/AdminUser.java`
  - 当前仅能确认后台账号拥有 `phone / email` 这类候选联系方式
  - 但尚无独立“治理通知接收地址”模型
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/ai/AdminAiResumeController.java`
  - 当前只存在人工 `record-notification` / `record-notification-receipt`
  - 尚不存在真实回执采集入口
- `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/impl/AdminAiResumeGovernanceServiceImpl.java`
  - 当前 `governance-sweep` 仍基于 failure 上的手工通知事实推进
  - 尚未接入真实发送服务与真实回执归并
- `kaipai-admin/src/views/system/AiResumeGovernanceView.vue`
  - 当前后台治理页展示的是人工记录口径
  - 尚未显式区分“真实发送 / 真实回执 / 人工补录”

因此下一步不能再直接写“继续补通知”，而必须先把“真实通知基础设施”独立立项。

## 2. 本轮落地

- 新增 `00-60` Spec，正式记录 AI 治理真实通知基础设施入口
- 明确 `00-50` 已完成协同模型升级、`00-59` 已完成调度入口升级
- 明确剩余 blocker 收口为：
  - 真实通知发送主链
  - 真实回执采集主链
  - `governance-sweep` 消费真实通知事实
- 明确 `AuthServiceImpl.sendCode(...)` 不得被复用为 AI 治理通知能力
- 明确后台 `record-notification` / `record-notification-receipt` 只能保留为人工补录 / 应急修正入口
- 回写 `phase-01-roadmap.md`、`ai-resume-status.md`、`overall-architecture-assessment.md`、`execution/ai-resume/README.md`、`tasks.md`
- 完成 Spec 索引与映射登记
- 已落第一批代码切片，把“人工补录通知事实”和“长期投递事实”从结构上拆开：
  - 新增 schema migration `V20260404_002__ai_resume_notification_delivery.sql`
  - 后端新增 `AiResumeNotificationDelivery`、mapper、service，独立存储 AI 治理通知投递记录
  - `record-notification` / `record-notification-receipt` 当前会继续保留人工动作，但会同步写入 `ai_resume_notification_delivery`
  - AI failure DTO / handling note / admin failure item 已补 `notificationDeliveryId / notificationSourceType / notificationChannelCode / notificationRecipient / notificationProviderCode / notificationProviderMessageId / notificationReceiptSourceType`
  - `AdminAiResumeGovernanceServiceImpl` 已把最新 delivery 摘要同步回填到 failure record 与操作日志 extra context，后续真实 provider send / callback 接入时不需要再回头改模型骨架
  - 后台 `AiResumeGovernanceView.vue` 已补 read-only 展示：失败样本详情与动作弹窗元信息现在可直接看到 deliveryId、通知来源、回执来源、通道、接收人与 provider messageId，时间线也会带出 delivery 摘要
- 已落第二批代码切片，把“真实发送入口 / provider 回执入口 / 调度复用链”从设计推进到可编译骨架：
  - 新增 `AiResumeNotificationProperties`，在 `application.yml` 显式登记 `kaipai.ai.resume.notification.enabled / provider-code / callback-header / callback-token`
  - 新增 `AiResumeNotificationProvider` 与默认 `ManualAiResumeNotificationProvider`，先把 provider 适配层从 `AdminAiResumeGovernanceServiceImpl` 中剥离
  - 新增 `AiResumeNotificationDispatchService`，统一负责 dispatch 落库、provider 结果归并、审计写入与 provider callback 回写
  - 新增公开 callback 入口 `POST /internal/ai/resume/notification-receipts/provider`，并以独立 header token 做入站校验，不再要求后台 JWT 会话
  - `record-notification` 当前已改成双轨：`send_failed` 继续保留人工补录；正常发送则改走统一 dispatch service
  - `governance-sweep` 的 `executeAutoRemind(...)` 当前也已改走统一 dispatch service，后续接真实 vendor 时不需要再改调度入口
  - provider callback 当前已能按 `providerMessageId` 或 `failureId` 归并到 `ai_resume_notification_delivery`，并同步回写 Redis failure 上的 receipt 摘要字段
- 已落后台第二批可视化切片，避免“基础设施落了，但后台仍只显示原始 code 值”：
  - `AiResumeGovernanceView.vue` 的 failure 列表当前已显式展示通知主链 / 回执主链 tag、投递链上下文和当前排障结论
  - failure 详情抽屉当前已新增“通知诊断”卡片，直接显示通知主链、回执主链、provider、接收人状态、消息标识和排障结论
  - 动作弹窗元信息当前也已不再直接显示原始 `sourceType / channelCode / providerCode`，而是翻译成治理语义，方便运营区分“人工补录 / 系统 dispatch / provider callback / recipient_missing”
- 已补 `00-60` 的标准验证入口骨架：
  - 新增 `execution/ai-resume/run-ai-resume-notification-foundation-validation.py`
  - 当前脚本已固化五类目标样本：dispatch sent、manual send_failed、pending_receipt、provider callback delivered、provider callback receipt_failed
  - `2026-04-04 07:28 +0800` 已按 `00-29` 标准总控把合法 callback token 同步进目标环境；本轮已明确 `AI_NOTIFICATION_CALLBACK_TOKEN` 是 provider callback header 的共享密钥，不是后台 JWT 或手机号登录 token
  - 对应记录已落档到：
    - `../../runbooks/backend-admin-release/records/20260404-072827-backend-ai-notification-config-pipeline-continue-ai-notification-random-token.md`
    - `../../runbooks/backend-admin-release/records/20260404-072835-backend-nacos-continue-ai-notification-random-token.md`
    - `../../runbooks/backend-admin-release/records/20260404-073019-backend-schema-continue-ai-notification-random-token.md`
    - `../../runbooks/backend-admin-release/records/20260404-073310-backend-only-continue-ai-notification-random-token.md`
  - 首轮真实样本 `execution/ai-resume/samples/20260404-073450-continue-ai-notification-random-token/summary.md` 没有卡在 callback token 或 `enabled` 门禁，而是暴露真实运行时数据缺口：被分派后台账号 `adminUserId=2` 的 `phone / email` 都为空，发送阶段因此落为 `recipient_contact_missing`
  - 随后已通过既有后台账号更新接口把 `adminUserId=2` 联系方式修正为 `phone=13800138002`、`email=admin@kaipai.local`
  - `2026-04-04 07:36 +0800` 已复跑样本 `execution/ai-resume/samples/20260404-073638-continue-ai-notification-random-token-after-admin-contact/summary.md`，五类标准样本全部通过：dispatch sent、pending_receipt、provider callback delivered、provider callback receipt_failed、manual send_failed
- 已把 `00-60` 的发布侧配置来源入口并入 `00-29`：
  - 新增 `.sce/config/ai-resume-notification.env.example`
  - 新增 `init-local-ai-notification-secret-file.py`、`read-local-ai-notification-config-inputs.py`、`run-backend-ai-notification-config-sync-pipeline.py`
  - 当前固定顺序为：`init local secret -> local-input gate -> remote nacos precheck -> nacos sync -> backend-only -> notification foundation validation`
  - `2026-04-04 06:03 +0800` 已先按标准入口实跑一轮本地门禁与总控 dry-run，生成：
    - `records/diagnostics/20260404-060219-continue-ai-notification-local-gate/`
    - `records/20260404-060356-backend-ai-notification-config-pipeline-continue-ai-notification-local-gate.md`
  - 首轮 dry-run 已把“placeholder callback token”标准化固定为 `local_input_not_ready`；随后真实环境实跑又证明，一旦本地 secret 合法、Nacos 已同步、schema 已发布，剩余失败会继续收口到真实运行时数据，而不是继续混淆成发布链路门禁

## 3. 验证

- 后端在 `JDK 17` 下执行 `mvn -q -DskipTests compile` 通过
- 管理端执行 `npm run type-check` 通过
- `run-ai-resume-notification-foundation-validation.py continue-ai-notification-random-token` 已在真实环境实跑，首轮样本固定 `recipient_contact_missing` 根因为后台联系人数据缺失，而不是 callback token / Nacos / schema / 发布未生效
- `run-ai-resume-notification-foundation-validation.py continue-ai-notification-random-token-after-admin-contact` 已在同一目标环境复跑通过，固定 `manual provider + enabled=true + shared callback secret` 口径下的真实 dispatch / callback / manual backfill 基础设施样本
- 当前验证结论：
  - AI 当前主阻塞继续统一收口为 `00-60`
  - login-auth `sendCode` 与 AI 通知基础设施已显式拆分
  - `00-60` 的基础设施层已经不再停留在“代码骨架 + dry-run”：当前已在真实环境完成配置同步、schema 发布、后端重建与标准样本通过，长期 delivery 事实层、统一 dispatch service、provider callback 主链和发布侧配置总控都已验证可用
  - 当前剩余缺口已从“有没有真实通知基础设施”收口为“是否继续对接商用通知 vendor，以及是否继续把 AI 生成器从规则适配器升级为真实 LLM”

## 4. 后续入口

- 后续 AI 治理真实通知相关实现，统一以 `00-60` 为直接入口
- `00-50` 继续作为“协同状态模型与治理动作升级”的已完成上位 Spec
- `00-59` 继续作为“服务端定时 sweep 调度入口”的已完成上位 Spec
- 商用通知 vendor 对接与更真实的 provider 回执链，继续作为 `00-60` 的后续批次推进，不再把 callback token 来源或发布门禁当作当前主阻塞
- 真实 LLM 接入继续保持并行但独立推进，不与 `00-60` 混写
