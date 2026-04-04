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
- 已落第三批可扩展 provider 切片，继续把“商用 vendor 后续接入”往前推进，但仍不绑定具体厂商账号：
  - 新增 `HttpAiResumeNotificationProvider`，支持通过固定 JSON 契约把 failure / recipient / requestId / callback header/token 投递到外部桥接服务
  - `AiResumeNotificationProperties` 与 `application.yml` 已扩展 `kaipai.ai.resume.notification.callback-url`，以及 `kaipai.ai.resume.notification.http.endpoint / auth-header / auth-token / connect-timeout-ms / read-timeout-ms`
  - `00-29` 本地 secret 模板、provider-aware 门禁与 Nacos 总控当前也已同步纳入 `AI_RESUME_NOTIFICATION_CALLBACK_URL / AI_RESUME_NOTIFICATION_HTTP_*` 输入位，避免代码支持 `provider-code=http`，但发布链路不会校验或下发 callbackUrl/endpoint/auth
  - `run-ai-resume-notification-foundation-validation.py` 当前也已支持 `AI_NOTIFICATION_PROVIDER_CODE`，不再把 provider callback 样本硬编码为 `manual`
  - 新增 `execution/ai-resume/run-ai-notification-http-bridge-mock.py`，可在缺真实厂商账号时提供固定 JSON 契约的 mock gateway，并落盘请求证据
  - `2026-04-04 08:32 +0800` 已本地实跑 `run-ai-notification-http-bridge-mock.py --max-requests 1`，样本目录为 `execution/ai-resume/samples/20260404-083225-local-http-bridge-smoke/`；已固定一条真实请求证据：返回 `providerCode=http / channelCode=sms / providerMessageId=mock-http-20260404083227-0001 / sendStatus=sent`
  - `2026-04-04 08:36 +0800` 又已本地实跑带 `callbackUrl / callbackHeader / callbackToken` 的自动回调样本 `execution/ai-resume/samples/20260404-083643-local-http-bridge-autocallback-smoke/`；summary 已固定 `callbackSuccessCount=1 / callbackFailureCount=0`，证明 bridge 当前不仅能返回 send 成功，还能自动回打 delivered 回执
  - 当前结论：`00-60` 后续剩余工作已从“还没有可扩展 provider 适配层”继续收口为“缺真实 vendor endpoint/credential 与对应回执联调样本”
- 已落第四批发布侧收口，把 `provider-code=http` 从“代码可配”继续推进到“没有真实 bridge 输入就必须 blocked 留档”的标准流程：
  - 新增 `.sce/config/ai-notification-http-bridge.env.example` 与本地 gitignored secret 初始化脚本 `init-local-ai-notification-http-bridge-secret-file.py`
  - 新增 `ai_notification_http_bridge_inputs.py` 与 `read-local-ai-notification-http-bridge-inputs.py`，把 bridge endpoint / callback base url / callback path / auth 输入位固化成独立本地门禁
  - 新增 `run-ai-notification-http-provider-rollout.py`，固定 `bridge-input -> ai-notification-config-sync -> backend-only -> run-ai-resume-notification-foundation-validation.py` 顺序
  - `00-29` 当前也已新增 `ai-notification-http-provider-rollout-runbook.md`，并回写 `backend-admin-standard-release.md` 与 `ai-notification-config-gate-runbook.md`
  - `2026-04-04 08:54 +0800` 已按标准入口执行 `read-local-ai-notification-http-bridge-inputs.py --label continue-http-provider-bridge-gate`，诊断目录为 `../../runbooks/backend-admin-release/records/diagnostics/20260404-085414-continue-http-provider-bridge-gate/`；结果已把根因固定为 `AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT=missing`
  - 同时又已执行 `run-ai-notification-http-provider-rollout.py --label continue-http-provider-bridge-gate --operator codex --dry-run`，记录为 `../../runbooks/backend-admin-release/records/20260404-085414-backend-ai-notification-http-provider-rollout-continue-http-provider-bridge-gate.md`；标准结论为 `bridge_input_not_ready`
  - 当前结论继续收口为：若没有真实 bridge endpoint，本轮允许产出 blocked 记录，但不允许伪造“provider=http 已可联调”
- 已落第五批目标环境桥接实跑，把 `provider=http` 从“可 blocked 留档”继续推进到“目标环境 mock bridge 联调通过”：
  - `2026-04-04 09:01 +0800` 已通过 `../../runbooks/backend-admin-release/scripts/run-ai-notification-http-bridge-mock-remote-release.py` 在目标环境启动 remote mock bridge，记录为 `../../runbooks/backend-admin-release/records/20260404-090124-ai-notification-http-bridge-remote-continue-http-provider-remote-bridge.md`
  - `2026-04-04 09:05 +0800` 已通过 `../../runbooks/backend-admin-release/scripts/run-ai-notification-http-bridge-proxy-sync.py` 把 nginx 公网路由 `/bridge/ai-notification/` 代理到 `http://172.17.0.1:19081/`，记录为 `../../runbooks/backend-admin-release/records/20260404-090551-ai-notification-http-bridge-proxy-continue-http-provider-bridge-proxy.md`
  - 首轮真实 rerun 暴露的不是 bridge 不通，而是 provider callback 仍被统一未登录链拦截；现已把共享 callback header/token 鉴权并入 `JwtFilter`，不再依赖脆弱的 `permitAll` 路径匹配
  - 随后 rerun5 又继续暴露总控脚本只下发了 `AI_RESUME_NOTIFICATION_CALLBACK_TOKEN`，却没把验证脚本读取的 `AI_NOTIFICATION_CALLBACK_TOKEN` 别名同步过去；现已在 `run-ai-notification-http-provider-rollout.py` 内统一映射 callback header/token 别名
  - `2026-04-04 09:30 +0800` 已按同一总控正式跑通 `provider=http`，记录为 `../../runbooks/backend-admin-release/records/20260404-092818-backend-ai-notification-http-provider-rollout-continue-http-provider-real-route-rerun6.md`，样本为 `../00-28-architecture-driven-delivery-governance/execution/ai-resume/samples/20260404-093013-continue-http-provider-real-route-rerun6/summary.md`
  - 当前该样本已固定 `dispatch sent / pending_receipt / provider callback delivered / provider callback receipt_failed / manual send_failed` 五类标准检查全部通过，说明 `provider=http` 在目标环境的 mock bridge 路径已不再是阻塞项

## 3. 验证

- 后端在 `JDK 17` 下执行 `mvn -q -DskipTests compile` 通过
- 管理端执行 `npm run type-check` 通过
- `run-ai-resume-notification-foundation-validation.py continue-ai-notification-random-token` 已在真实环境实跑，首轮样本固定 `recipient_contact_missing` 根因为后台联系人数据缺失，而不是 callback token / Nacos / schema / 发布未生效
- `run-ai-resume-notification-foundation-validation.py continue-ai-notification-random-token-after-admin-contact` 已在同一目标环境复跑通过，固定 `manual provider + enabled=true + shared callback secret` 口径下的真实 dispatch / callback / manual backfill 基础设施样本
- 第三批 `http provider` 增量已在本机临时切到 `C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot` 后执行 `mvn -q -DskipTests compile` 通过；对应 `00-29` provider-aware 配置脚本也已通过 `python -m py_compile`
- `run-ai-resume-notification-foundation-validation.py` 与 `run-ai-notification-http-bridge-mock.py` 已通过 `python -m py_compile`
- 第四批 `provider=http` bridge 输入门禁与总控脚本也已通过 `python -m py_compile`
- 第五批目标环境桥接实跑已固定三类记录：
  - blocked 门禁：`../../runbooks/backend-admin-release/records/20260404-085414-backend-ai-notification-http-provider-rollout-continue-http-provider-bridge-gate.md`
  - remote bridge / proxy：`../../runbooks/backend-admin-release/records/20260404-090124-ai-notification-http-bridge-remote-continue-http-provider-remote-bridge.md`、`../../runbooks/backend-admin-release/records/20260404-090551-ai-notification-http-bridge-proxy-continue-http-provider-bridge-proxy.md`
  - 最终通过：`../../runbooks/backend-admin-release/records/20260404-092818-backend-ai-notification-http-provider-rollout-continue-http-provider-real-route-rerun6.md` 与 `../00-28-architecture-driven-delivery-governance/execution/ai-resume/samples/20260404-093013-continue-http-provider-real-route-rerun6/summary.md`
- 当前验证结论：
  - AI 当前主阻塞继续统一收口为 `00-60`
  - login-auth `sendCode` 与 AI 通知基础设施已显式拆分
  - `00-60` 的基础设施层已经不再停留在“代码骨架 + dry-run”：当前已在真实环境完成配置同步、schema 发布、后端重建、`manual provider` 标准样本通过，以及 `provider=http + remote mock bridge + nginx public proxy` 标准样本通过；长期 delivery 事实层、统一 dispatch service、provider callback 主链和发布侧配置总控都已验证可用
  - 因此 `tasks.md` 中的 `T4/T5` 当前阶段父任务已可收口为完成；后续不再把“有没有真实通知基础设施”当成主阻塞
  - 当前剩余缺口已从“有没有真实通知基础设施”收口为“是否继续对接真实商用通知 vendor、真实 vendor credential 是否就绪，以及是否继续把 AI 生成器从规则适配器升级为真实 LLM”

## 4. 后续入口

- 后续 AI 治理真实通知相关实现，统一以 `00-60` 为直接入口
- `00-50` 继续作为“协同状态模型与治理动作升级”的已完成上位 Spec
- `00-59` 继续作为“服务端定时 sweep 调度入口”的已完成上位 Spec
- 商用通知 vendor 对接与更真实的 provider 回执链，继续作为 `00-60` 的后续批次推进，不再把 callback token 来源或发布门禁当作当前主阻塞
- 真实 LLM 接入继续保持并行但独立推进，不与 `00-60` 混写
