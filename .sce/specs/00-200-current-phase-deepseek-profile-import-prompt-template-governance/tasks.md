# 00-200 DeepSeek 资料识别 Prompt 模板治理 - 任务清单

> 状态：书面 Spec 已审阅确认，三份详细实施计划已完成，等待按 Phase A 后端、管理端与发布、Phase B 接管顺序执行
>
> 执行方式：每个生产行为先写失败测试并确认失败原因，再写最小实现。

## 详细实施计划

1. `docs/superpowers/plans/2026-07-26-00-200-prompt-governance-backend.md`
2. `docs/superpowers/plans/2026-07-26-00-200-admin-phase-a-rollout.md`
3. `docs/superpowers/plans/2026-07-26-00-200-runtime-phase-b-cutover.md`

必须严格按上述顺序执行。Phase A 未完成两个 bootstrap v1 的真实固定样例试运行、正常发布和目标状态核验前，不得开始 Phase B。

## T1 Spec 与基线

- [x] 调查现有 DeepSeek 模型配置、硬编码 Prompt、Schema validator、调用审计和后台页面。
- [x] 确认首期只治理 full_profile、works_only 和 Repair，不扩展其他 AI Prompt。
- [x] 比较直接配置字段、独立版本治理和全平台 Prompt 中心三种方案。
- [x] 用户确认独立版本治理、现有配置页内管理和安全合同代码持有方案。
- [x] 编写 requirements.md、design.md 和 tasks.md。
- [x] 用户审阅并确认书面 Spec。
- [x] 编写并审校 Phase A 后端、管理端与发布、Phase B 接管三份详细实施计划。

**Validates: Requirements R1-R72**

## T2 数据库与持久化

- [ ] 先扩展 AiProfileImportPersistenceShapeTest，断言 V001 三张新表、publish 完整绑定审计快照列、reason_code、调用审计谱系列、复合指针外键、开放草稿唯一索引和隐私禁列；运行并确认 RED。
- [ ] 新增 V20260726_001__ai_profile_import_prompt_template_governance.sql。
- [ ] 创建 template、version、audit 实体和 Mapper。
- [ ] 种入 full_profile v1 与 works_only v1 两个 untested bootstrap 草稿，回填 draft_version_id，active_version_id 保持为空。
- [ ] 扩展 AiProfileImportRequestAudit 谱系字段。
- [ ] 运行持久化形状测试并确认 GREEN。
- [ ] 先新增 ProfileImportPromptGovernanceMySqlIntegrationTest，覆盖 bootstrap 草稿、复合指针归属、跨模板指针拒绝和单模板开放草稿唯一性；运行并确认 RED。
- [ ] 实现基础查询、SELECT FOR UPDATE 和条件更新 Mapper。
- [ ] 运行上述 schema/seed MySQL 集成测试并确认 GREEN。

**Validates: Requirements R7-R17, R43-R47, R58-R63, R66**

## T3 Prompt Policy、合同、渲染与运行时解析

- [ ] 先新增 ProfileImportPromptPolicyTest，覆盖长度、控制字符、变量语法、受支持场景和合同版本；运行并确认 RED。
- [ ] 实现 ProfileImportPromptPolicy。
- [ ] 先新增 ProfileImportPromptRendererTest，覆盖合同追加、works_only 空档案约束、Repair 不改事实后缀、LF 规范化和长度前缀 framing；证明跨字段换行组合不会产生相同哈希；运行并确认 RED。
- [ ] 实现 ProfileImportPromptContract、ProfileImportPromptRenderer 和 ProfileImportPromptRuntime。
- [ ] 运行 Policy/Renderer 测试并确认 GREEN。
- [ ] 先新增 ProfileImportPromptRuntimeResolverImplTest，覆盖当前版本读取、模板/版本归属、scene、released、deleted、缺失、哈希损坏和不支持合同；运行并确认 RED。
- [ ] 实现 ProfileImportPromptRuntimeResolverImpl，保持无缓存并 fail closed。
- [ ] 运行 Resolver 测试并确认 GREEN。

**Validates: Requirements R18-R26, R38-R45, R64-R65**

## T4 草稿、试运行、发布、恢复与审计服务

- [ ] 先新增 ProfileImportPromptManagementServiceImplTest，覆盖新建唯一草稿、指定历史来源、乐观锁、保存失效测试、首次发布前禁止放弃 bootstrap、已有 active 后允许放弃草稿、不可变发布版本、动作限定 reasonCode，以及 draft_create/update/abandon 专用审计；使用 API Key、用户/fixture/Prompt 正文作为非法 reasonCode 并证明持久化前拒绝；运行并确认 RED。
- [ ] 实现草稿生命周期事务与对应专用审计。
- [ ] 先新增 ProfileImportPromptTesterImplTest，覆盖固定样例 code/version/hash、content/runtime hash、当前模型/configVersion 绑定、无用户配额/业务写入、Schema 校验、脱敏结果和 test 专用审计；运行并确认 RED。
- [ ] 扩展 ProfileImportRuntimeConfig 的 configVersion，新增两个脱敏固定样例资源并实现 ProfileImportPromptTesterImpl。
- [ ] 先增加发布单元测试，覆盖未测试、测试失败、content/runtime/fixture 变化、模型配置变化、锁顺序、条件冻结 affected rows=1、完整发布绑定快照、已发布重测不覆盖快照、专用审计失败回滚和并发冲突；运行并确认 RED。
- [ ] 先扩展 AdminOperationLoggerTest，覆盖新增 logRequired 在异常与 save=false/0-row 时抛出；运行并确认 RED。
- [ ] 实现发布事务、active/draft 指针切换、条件冻结、不可变发布绑定审计，以及只接收脱敏日志值对象并检查写入结果的 AdminOperationLogger.logRequired。
- [ ] 先增加历史恢复测试，覆盖路径 targetVersionId 与 expectedTemplateVersion 分离、目标归属、released/deleted、内容哈希、受支持 Schema/合同、完整渲染、动作限定非空 reasonCode、开放草稿保留和审计失败回滚；运行并确认 RED。
- [ ] 实现历史恢复。
- [ ] 先扩展 ProfileImportPromptGovernanceMySqlIntegrationTest 并确认 RED：首次发布前 bootstrap 放弃拒绝、发布绑定快照不可变、专用/全局审计异常及 save=false/0-row 原子回滚、两管理员并发发布、并发草稿保存/试运行写回、模型配置并发更新、隔离 fixture 的 v2 -> v1 历史恢复、六类动作审计、非法敏感 reasonCode 持久化前拒绝，以及新增表和 admin_operation_log 隐私禁写。
- [ ] 补齐真实 MySQL 所需的锁定、条件更新和事务实现；运行管理服务与 MySQL 事务测试并确认 GREEN。

**Validates: Requirements R8-R17, R27-R37, R50-R57, R65-R66**

## T5 管理 API、权限与错误合同

- [ ] 先扩展 ProfileImportErrorContractTest，加入 46018 至 46022 稳定错误；运行并确认 RED。
- [ ] 实现 Prompt 管理错误码。
- [ ] 先写 Controller 权限合同测试，覆盖 read/update/test/publish/restore/audit 分离、restore 路径 targetVersionId 与 expectedTemplateVersion 分离、动作限定 reasonCode 和自由文本/敏感值拒绝且不回显；运行并确认 RED。
- [ ] 新增 AdminAiProfileImportPromptController 和 list/detail/write DTO。
- [ ] 先扩展 AiProfileImportPersistenceShapeTest，断言 V002 权限注册与系统管理员授权；运行并确认 RED。
- [ ] 新增 V20260726_002__ai_profile_import_prompt_permission_alignment.sql。
- [ ] 更新后台 permission.ts 和 permission-registry.ts。
- [ ] 运行错误、Controller 和权限迁移测试并确认 GREEN。

**Validates: Requirements R48-R57, R64-R65**

## T6 管理端模板治理 UI

- [ ] 先扩展 e2e-ai-profile-import-config.mjs mock 和断言，覆盖两个场景、草稿、测试、发布、恢复、首次发布前禁止放弃 bootstrap、正常放弃、冲突和审计；逐项验证 read/update/test/publish/restore/audit 权限；运行开发态 E2E 并确认 RED。
- [ ] 增加无 template-read 负向断言：不发 detail 请求、列表响应不含正文、DOM/表单值/browser storage 均无正文。
- [ ] 在 types/ai.ts 增加模板摘要、详情、版本、动作和审计类型。
- [ ] 在 api/ai.ts 增加模板管理 API。
- [ ] 新增 ProfileImportPromptTemplatePanel.vue，承担场景 Tab、版本表、编辑 Dialog 和动作确认。
- [ ] 修改 AiProfileImportConfigView.vue 挂载 Panel，并将审计区分为模型配置与模板审计。
- [ ] 修改 SettingsView.vue 的 DeepSeek 资料导入摘要，不新增路由或 sidebar 项。
- [ ] 处理 loading、empty、error、权限隐藏、冲突保留草稿和无布局溢出状态。
- [ ] 发布、恢复和放弃确认使用动作限定 reasonCode 下拉选项，不增加自由文本原因输入。
- [ ] 运行开发态 E2E 并确认 GREEN。
- [ ] 为现有 E2E 增加 --dist 模式，使用 vite preview/等价静态服务器读取真实 dist；先运行并确认因缺少 dist 模式或产物而 RED。
- [ ] 运行 npm run type-check、npm run build 和 dist sanitizer，再运行 --dist E2E，覆盖入口、配置路由、Prompt Panel、按需正文和懒加载资源并确认 GREEN。

**Validates: Requirements R1-R2, R46-R57, R69-R70**

## T7 Phase A 治理面上线与 bootstrap 正常发布

- [ ] 运行 Phase A 后端专项、schema/事务 MySQL 集成测试、完整 Maven 构建、管理端 type-check/build、开发态 E2E 和 sanitizer 后 dist E2E。
- [ ] 应用 V001/V002，验证 full_profile v1 与 works_only v1 均为 draft/untested，draft 指针归属正确且 active 指针为空。
- [ ] 发布治理面后端与管理端，确认生产识别仍明确使用 legacy-code-v1，尚未接入 RuntimeResolver。
- [ ] 使用后台当前已连接成功且 ready 的 DeepSeek 配置分别试运行两个 bootstrap 草稿，核对 content/runtime/fixture/model/configVersion 完整绑定。
- [ ] 通过正常 publish API 发布两个 v1；核对 released 状态、active 指针、不可变完整发布绑定审计和脱敏 admin_operation_log。
- [ ] 保存 Phase A 数据库核对、试运行和发布证据；任一场景未完成不得开始 T8。

**Validates: Requirements R27-R37, R58-R63, R66, R71**

## T8 Phase B DeepSeek 运行时接管与调用审计

- [ ] 先扩展 DeepSeekProfileTextExtractorTest，证明 extractor 使用传入版本正文，首次提取与 Repair 使用同一版本，works_only 合同进入请求体；运行并确认 RED。
- [ ] 先扩展 ProfileImportServiceImplTest，覆盖 scene Resolver、模板/版本归属、模板不可用不消耗配额、works_only 违规档案候选拒绝和谱系审计；运行并确认 RED。
- [ ] 先扩展 ProfileImportPromptGovernanceMySqlIntegrationTest，覆盖真实用户识别调用谱系和用户原文、完整响应、完整 Prompt、密钥禁写；运行并确认 RED。
- [ ] 修改 ProfileImportServiceImpl 运行顺序、模板解析和审计。
- [ ] 修改 DeepSeekProfileTextExtractor，物理删除生产调用对 Java SYSTEM_PROMPT/REPAIR_PROMPT 常量的依赖；连接探针 Prompt 继续由代码持有。
- [ ] 增加 Phase B 启动/部署前检查，要求两个场景均有同模板 released active 版本、完整试运行绑定、受支持合同和可渲染运行时；确认不满足时 fail closed 且无 legacy fallback。
- [ ] 运行 extractor、service、schema validator、proof 和 apply 专项测试并确认 GREEN。
- [ ] 运行调用谱系 MySQL 集成、29 条作品 golden fixture 与 ProfileImportApplyMySqlIntegrationTest，确认不回归。

**Validates: Requirements R4-R6, R25-R26, R38-R45, R60-R68**

## T9 全量验证与发布门禁

- [ ] 运行后端 Prompt 专项单元测试。
- [ ] 运行相关 profile-import 全量单元测试。
- [ ] 运行 Prompt MySQL 集成测试和 apply MySQL 集成测试。
- [ ] 运行后端 Maven 构建。
- [ ] 运行管理端 type-check、build、开发态 e2e:ai-profile-import-config 和 sanitizer 后 --dist E2E。
- [ ] 在目标数据库检查两场景 released active v1、开放草稿数、复合指针归属和权限注册。
- [ ] 部署 Phase B 前重新验证两场景 content/runtime/fixture/model/configVersion 绑定仍有效。
- [ ] 发布并部署已删除生产 Java Prompt 依赖的 Phase B 运行时接管版本，记录部署版本与健康检查证据。
- [ ] 使用授权测试账号执行一笔 full_profile 和一笔 works_only smoke。
- [ ] 验证调用审计存在 Prompt 谱系且不存在用户原文、完整响应或密钥。
- [ ] 验证 publish 审计保留不可变完整测试绑定，后续 released 版本重测未覆盖该快照；验证 admin_operation_log 不含自由文本 reason、changeSummary 或 Prompt 正文。
- [ ] 复核隔离 MySQL fixture 的 v2 -> v1 恢复证据：新请求使用 v1、旧请求谱系未改变；首发目标环境只有 v1 时不得用 v1 -> v1 空操作或伪造第二个发布版本冒充恢复 smoke。

**Validates: Requirements R27-R45, R58-R71**

## T10 文档与收口

- [ ] 更新 .sce/specs/spec-code-mapping.md 为真实实现状态。
- [ ] 更新 .sce/steering/CURRENT_CONTEXT.md，不提前核销 00-199。
- [ ] 更新 docs/dev-playbook.md 的 Prompt 草稿、测试、发布和恢复规则。
- [ ] 新增 Prompt 发布、观察和历史恢复 runbook。
- [ ] 新增 execution.md，记录测试命令、退出码、数据库核对、管理端 E2E 和 smoke 证据。
- [ ] 对照 requirements.md R1-R72 逐条验收。
- [ ] 明确记录未纳入本期的其他 AI Prompt、provider json_schema 和 00-199 T6/T9。

**Validates: Requirements R1-R72**
