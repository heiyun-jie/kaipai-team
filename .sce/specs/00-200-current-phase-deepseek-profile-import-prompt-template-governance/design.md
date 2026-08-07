# 00-200 DeepSeek 资料识别 Prompt 模板治理 - 技术设计

> 日期：2026-07-26
>
> 状态：书面设计已审阅确认，三份详细实施计划已完成；尚未实施 00-200 生产代码
>
> Requirements：requirements.md R1-R72

## 1. 设计决策

### 1.1 采用方案

采用“独立模板定义 + 版本行 + 专用审计 + 现有配置页内治理”：

    ai_profile_import_prompt_template
      -> active_version_id
      -> draft_version_id
      -> ai_profile_import_prompt_version

    管理动作
      -> ai_profile_import_prompt_audit

    用户识别
      -> ai_profile_import_request_audit 中的 Prompt 谱系

不把 Prompt 放入 ai_profile_import_config，也不放入 ai_image_provider_config.public_config_json。模型配置属于 provider/runtime，Prompt 属于 profile-import capability，两者具有不同的版本、权限和发布语义。

### 1.2 被拒绝方案

| 方案 | 拒绝原因 |
|---|---|
| 在 ai_profile_import_config 增加 Prompt 字段并保存即生效 | 无草稿、不可变版本、精确试运行绑定和可靠恢复 |
| 复用分享内容风格模板 | 视觉模板与系统 Prompt 的事实源、权限和发布合同不同 |
| 首期建立全平台 Prompt 中心 | 会把资料识别、分享图、生图和润色的安全边界混为一体 |
| 继续只用 Java 常量 | 无后台治理、版本追溯和运行时恢复能力 |
| 首期增加本地或 Redis 缓存 | 发布后多实例一致性复杂度大于一次主键查询收益 |

_Requirements: R1-R3, R38-R42_

## 2. 总体架构

    AdminAiProfileImportPromptController
      -> ProfileImportPromptManagementService
         -> ProfileImportPromptPolicy
         -> ProfileImportPromptTester
         -> template/version/audit mapper
         -> AdminOperationLogger

    ProfileImportServiceImpl
      -> ProfileImportConfigService.runtimeConfig()
      -> ProfileImportPromptRuntimeResolver.resolve(scene)
      -> DeepSeekProfileTextExtractor.extract(config, promptRuntime, rawText, requestId)
      -> ProfileImportSchemaValidator
      -> ai_profile_import_request_audit

核心边界：

- ManagementService 负责草稿、试运行、发布、恢复和审计事务。
- RuntimeResolver 只读取当前有效发布版本，不承担后台写操作。
- PromptPolicy 只校验后台可编辑正文及受支持合同，不替代 SchemaValidator。
- PromptContract 由代码生成强制后缀，后台不可修改。
- PromptRenderer 组合可编辑正文与代码合同，不读取环境变量或其他用户数据。
- DeepSeekProfileTextExtractor 在 Phase B 完成后不再持有或回退到生产 SYSTEM_PROMPT 常量；Phase A 期间明确继续使用 legacy-code-v1，模板表只服务治理、试运行和发布准备。

_Requirements: R18-R26, R35-R45_

## 3. 数据模型

### 3.1 模板定义表

表：ai_profile_import_prompt_template

| 列 | 类型 | 说明 |
|---|---|---|
| template_id | BIGINT | 主键 |
| template_code | VARCHAR(64) | 稳定编码 |
| scene | VARCHAR(32) | full_profile / works_only |
| display_name | VARCHAR(128) | 展示名称 |
| active_version_id | BIGINT NULL | 当前发布版本 |
| draft_version_id | BIGINT NULL | 当前开放草稿 |
| version | INT | MyBatis 乐观锁 |
| BaseEntity 列 | - | deleted、rid、创建更新审计列 |

约束：

- UNIQUE(template_code, deleted)
- UNIQUE(scene, deleted)
- active_version_id 与 draft_version_id 普通索引
- 表创建完成后增加复合外键 (template_id, active_version_id) 与 (template_id, draft_version_id)，共同引用版本表的 (template_id, prompt_version_id)，阻止悬空或跨模板指针
- 业务服务使用 SELECT FOR UPDATE 锁定模板行

### 3.2 模板版本表

表：ai_profile_import_prompt_version

| 列 | 类型 | 说明 |
|---|---|---|
| prompt_version_id | BIGINT | 主键 |
| template_id | BIGINT | 模板定义 |
| version_no | INT | 场景内递增版本号 |
| version_label | VARCHAR(128) | 管理员可编辑的版本名称 |
| lifecycle_status | VARCHAR(32) | draft / released / abandoned |
| system_prompt_body | MEDIUMTEXT | 可编辑 System Prompt 正文 |
| repair_prompt_body | TEXT | 可编辑 Repair Prompt 正文 |
| schema_version | VARCHAR(64) | 只读结构合同版本 |
| contract_version | VARCHAR(64) | 只读安全合同版本 |
| content_sha256 | CHAR(64) | 两段正文和只读版本组合哈希 |
| change_summary | VARCHAR(500) | 变更说明 |
| test_status | VARCHAR(32) | untested / success / failed / stale |
| tested_content_sha256 | CHAR(64) NULL | 试运行对应正文哈希 |
| tested_runtime_sha256 | CHAR(64) NULL | 包含实际代码合同正文的运行时哈希 |
| test_fixture_code | VARCHAR(64) NULL | 固定样例编码 |
| test_fixture_version | VARCHAR(64) NULL | 固定样例版本 |
| test_fixture_sha256 | CHAR(64) NULL | 固定样例正文哈希 |
| tested_model_name | VARCHAR(128) NULL | 试运行模型 |
| tested_config_version | INT NULL | 试运行模型配置版本 |
| test_candidate_count | INT | 脱敏结果计数 |
| test_work_count | INT | 脱敏结果计数 |
| test_elapsed_ms | BIGINT NULL | 耗时 |
| test_error_code | VARCHAR(64) NULL | 稳定错误码 |
| tested_by / tested_at | BIGINT / DATETIME | 测试操作者和时间 |
| released_by / released_at | BIGINT / DATETIME | 发布操作者和时间 |
| open_draft_template_id | BIGINT GENERATED | draft 且未删除时等于 template_id，否则为 null |
| version | INT | 草稿乐观锁 |
| BaseEntity 列 | - | 通用审计列 |

约束：

- UNIQUE(template_id, version_no, deleted)
- UNIQUE(template_id, prompt_version_id)，供模板指针复合外键验证归属
- UNIQUE(open_draft_template_id)，从数据库层阻止同一模板存在多个开放草稿
- INDEX(template_id, lifecycle_status, deleted)
- FOREIGN KEY(template_id) REFERENCES ai_profile_import_prompt_template(template_id)
- released 和 abandoned 版本禁止 update 正文
- active 指针必须指向同模板、未删除的 released 版本；draft 指针必须指向同模板、未删除的 draft 版本，该状态语义由服务写门禁和运行时断言双重保证

### 3.3 模板审计表

表：ai_profile_import_prompt_audit

| 列 | 类型 | 说明 |
|---|---|---|
| prompt_audit_id | BIGINT | 主键 |
| template_id | BIGINT | 模板 |
| prompt_version_id | BIGINT NULL | 操作版本 |
| action_code | VARCHAR(64) | draft_create/update/abandon/test/publish/restore |
| from_version_id | BIGINT NULL | 原当前版本 |
| to_version_id | BIGINT NULL | 新当前版本 |
| content_sha256 | CHAR(64) NULL | 操作正文哈希 |
| runtime_sha256 | CHAR(64) NULL | 发布时完整运行时哈希 |
| schema_version | VARCHAR(64) NULL | 发布时 Schema 版本快照 |
| contract_version | VARCHAR(64) NULL | 发布时安全合同版本快照 |
| fixture_code | VARCHAR(64) NULL | 发布时 fixture 编码 |
| fixture_version | VARCHAR(64) NULL | 发布时 fixture 版本 |
| fixture_sha256 | CHAR(64) NULL | 发布时 fixture 哈希 |
| model_name | VARCHAR(128) NULL | 发布时试运行模型 |
| config_version | INT NULL | 发布时模型配置版本 |
| test_operator_id | BIGINT NULL | 发布所依据的试运行操作者 |
| tested_at | DATETIME NULL | 发布所依据的试运行时间 |
| operator_id / operator_name | - | 服务端当前管理员 |
| reason_code | VARCHAR(64) | 服务端固定动作原因编码 |
| result_status | VARCHAR(32) | success / failed |
| error_code | VARCHAR(64) NULL | 稳定错误码 |
| message | VARCHAR(255) NULL | 服务端稳定摘要，不拼接请求值或外部异常正文 |
| BaseEntity 列 | - | 通用审计列 |

该表不保存完整 Prompt、用户正文、模型完整响应、自由文本 reason、changeSummary 或任何密钥。publish 成功行必须固化上述完整试运行绑定；审计 Mapper 不提供 update/delete，已发布版本后续重新试运行只能刷新版本表 tested_* 字段，不得覆盖原 publish 审计快照。

### 3.4 调用审计扩展

对 ai_profile_import_request_audit 增加 nullable 列：

- prompt_template_code VARCHAR(64)
- prompt_version_id BIGINT
- prompt_version_no INT
- prompt_schema_version VARCHAR(64)
- prompt_contract_version VARCHAR(64)
- prompt_runtime_sha256 CHAR(64)

历史行保持 null；新运行时在成功解析模板后必须填充完整谱系。

_Requirements: R7-R17, R31-R45, R58-R63_

## 4. 状态机

### 4.1 草稿

    无草稿
      -> create draft
      -> draft_version_id 指向 draft

    draft
      -> update draft
      -> test success/failed
      -> content change 后 test_status=stale
      -> 已有 active 版本时 abandon 后 lifecycle=abandoned 且 draft_version_id=null
      -> publish 后 lifecycle=released、draft_version_id=null、active_version_id=该版本

每个场景只允许一个开放草稿。创建草稿时锁定模板行；若 draft_version_id 非空，返回状态冲突并引导打开现有草稿。

Phase A 首次发布前 active_version_id 为空时，当前 bootstrap 草稿是唯一合法初始化来源。abandonDraft 必须在模板行锁内拒绝放弃该草稿并返回 PROFILE_IMPORT_PROMPT_STATE_CONFLICT；管理端隐藏或禁用放弃动作。禁止依赖人工 SQL 重建 bootstrap 草稿。

### 4.2 发布与历史恢复

发布版本的正文、Schema、合同版本和内容哈希不可修改；测试元数据允许通过受控试运行刷新。恢复历史版本不复制、不覆盖版本正文：

    active v3
      -> restore v1
      -> active_version_id=v1
      -> v3 仍为 released 历史版本
      -> 审计记录 from=v3 / to=v1

恢复操作不改变 draft_version_id。存在开放草稿时仍允许应急恢复，但恢复确认框必须提示草稿仍保留。

恢复事务在切换指针前必须重新读取并校验目标版本：

- prompt_version_id 属于当前锁定的 template_id。
- lifecycle_status=released 且 deleted=0。
- 按当前 framing 重算的 contentSha256 与存储值一致。
- schemaVersion 和 contractVersion 均受当前代码支持。
- 当前 ProfileImportPromptRenderer 可以生成完整 System Prompt 与 Repair Prompt，并通过长度和合同校验。

任一校验失败都返回稳定状态错误，不改变 active_version_id，也不写成功审计。恢复不强制再次调用 DeepSeek；恢复后的已发布版本可以另行受控试运行刷新测试元数据。

_Requirements: R8-R17, R34-R37_

## 5. Prompt 合同

### 5.1 运行时值对象

新增 ProfileImportPromptRuntime，字段：

- templateId
- templateCode
- scene
- promptVersionId
- versionNo
- schemaVersion
- contractVersion
- systemPrompt
- repairPrompt
- runtimeSha256

Runtime 对象的 toString 不输出正文，只输出编码、版本和哈希摘要。

### 5.2 内容哈希

contentSha256 和 runtimeSha256 禁止使用换行、分隔符或直接字符串拼接。实现复用项目 proof 的无歧义 framing 方式：

    DataOutputStream out
    for each field in fixed order:
      bytes = normalizeLf(field).getBytes(UTF_8)
      out.writeInt(bytes.length)
      out.write(bytes)
    sha256(out.toByteArray())

contentSha256 的固定字段顺序：

    profile-import-prompt-content-v1
    templateCode
    scene
    schemaVersion
    contractVersion
    systemPromptBody
    repairPromptBody

runtimeSha256 的固定字段顺序：

    profile-import-prompt-runtime-v1
    contentSha256
    renderedSystemPrompt
    renderedRepairPrompt

`renderedSystemPrompt` 和 `renderedRepairPrompt` 是后台正文追加当前代码合同后的实际完整模型输入，因此代码合同正文变化会改变 runtimeSha256。换行统一为 LF，正文不做 trim、Unicode 重排或其他不可见变换，避免管理员看见的内容与哈希内容不同。测试必须证明可跨字段制造相同拼接字节的换行组合会得到不同哈希。

### 5.3 可编辑正文限制

- system_prompt_body：200 至 16000 字符。
- repair_prompt_body：20 至 1000 字符。
- 最终 System Prompt 加安全合同不超过 20000 字符。
- 拒绝 NUL 和非法 Unicode 控制字符。
- 首期拒绝所有变量表达式和模板插值语法。
- 不从 Spring Environment、系统环境变量、密钥服务或用户档案注入模板变量。

### 5.4 代码持有合同

新增 ProfileImportPromptContract：

- 生成通用顶层 Envelope 合同。
- 生成 profile 字段白名单。
- 生成 work 字段白名单与枚举。
- 生成 sourceText、数字保真、籍贯、生日和性别推断合同。
- 生成媒体占位忽略合同。
- 对 works_only 追加 profileCandidates 必须为空数组。
- 为 Repair 追加只修 JSON、不得改变事实合同。

后台正文可以调整任务表达、字段解释和示例，但最终合同始终追加在最后。即使后台正文要求放宽字段，SchemaValidator 仍拒绝不合法响应。

### 5.5 Provider 输出模式

首期保留：

    response_format = { type: json_object }
    temperature = 0

schemaVersion 初始为 profile-import-json-v1，contractVersion 初始为 profile-import-contract-v1。未来切换 provider json_schema 必须新建独立 Spec 和 Schema 兼容迁移。

_Requirements: R18-R26_

## 6. 固定试运行

### 6.1 测试样例

新增受版本控制的主资源：

- src/main/resources/ai/profile-import/prompt-fixtures/full-profile-v1.txt
- src/main/resources/ai/profile-import/prompt-fixtures/works-only-v1.txt

样例使用虚构信息，不包含真实用户姓名、手机号、身份证号、URL 或密钥。

### 6.2 测试流程

    load current ProfileImportRuntimeConfig
      -> verify config ready
      -> render exact draft + code contract
      -> call DeepSeek without Redis rate limiter
      -> parse JSON
      -> run ProfileImportSchemaValidator
      -> assert scene-specific contract
      -> persist only counts/status/content+runtime hash/fixture lineage/model/configVersion

ProfileImportRuntimeConfig 增加 configVersion，供精确测试绑定。每个 fixture 在代码中声明稳定 fixtureCode 和 fixtureVersion；fixtureSha256 按同一长度前缀 framing 依次写入 `profile-import-prompt-fixture-v1`、fixtureCode、fixtureVersion 和规范化正文后计算。测试服务不调用 ProfileImportServiceImpl，避免用户请求审计、用户版本读取和配额副作用。

试运行允许针对开放草稿和已发布版本执行。已发布版本只更新版本表测试元数据，不修改正文、Schema、合同、内容哈希或既有 publish 审计快照；只有开放草稿的成功结果能够满足后续发布门禁。

### 6.3 发布时测试有效性

发布要求：

- test_status=success
- tested_content_sha256 等于当前 content_sha256
- tested_runtime_sha256 等于使用当前代码合同重新渲染得到的 runtimeSha256
- test_fixture_code、test_fixture_version 和 test_fixture_sha256 等于当前场景固定 fixture
- tested_model_name 等于当前模型名
- tested_config_version 等于当前配置行 version
- 当前模型配置仍 ready

任何正文、代码合同、Schema/合同版本、fixture、模型名或模型配置版本变化都会使绑定失效，并返回 PROFILE_IMPORT_PROMPT_TEST_STALE。

_Requirements: R27-R37_

## 7. 后台管理服务

### 7.1 服务与持久化文件

新增：

- model/ai/entity/AiProfileImportPromptTemplate.java
- model/ai/entity/AiProfileImportPromptVersion.java
- model/ai/entity/AiProfileImportPromptAudit.java
- mapper/ai/AiProfileImportPromptTemplateMapper.java
- mapper/ai/AiProfileImportPromptVersionMapper.java
- mapper/ai/AiProfileImportPromptAuditMapper.java
- service/ai/ProfileImportPromptManagementService.java
- service/ai/ProfileImportPromptRuntimeResolver.java
- service/ai/profileimport/ProfileImportPromptPolicy.java
- service/ai/profileimport/ProfileImportPromptContract.java
- service/ai/profileimport/ProfileImportPromptRenderer.java
- service/ai/impl/ProfileImportPromptManagementServiceImpl.java
- service/ai/impl/ProfileImportPromptRuntimeResolverImpl.java
- service/ai/impl/ProfileImportPromptTesterImpl.java
- controller/admin/ai/AdminAiProfileImportPromptController.java

DTO 按 list/detail/write 分开，不向列表响应暴露正文。

### 7.2 事务、锁与审计

createDraft、updateDraft、abandonDraft、publish 和 restore 使用 `@Transactional(rollbackFor = Exception.class)`。所有需要多行锁的写路径使用相同顺序：

    1. SELECT template ... FOR UPDATE
    2. SELECT prompt_version ... FOR UPDATE
    3. SELECT ai_profile_import_config ... FOR UPDATE

createDraft 和 abandonDraft 只取得实际需要的前缀锁。updateDraft 使用 `prompt_version_id + template_id + lifecycle_status=draft + deleted=0 + expectedVersion` 条件更新并检查受影响行数，保存正文后同步重算 contentSha256，并把既有试运行状态标记为 stale。

test 先读取版本、fixture 和模型配置快照，执行远程 DeepSeek 调用，再在短事务中按上述顺序锁定实际涉及的版本和配置行；只有 contentSha256、runtimeSha256、fixture 谱系、modelName 和 configVersion 仍与快照一致时才写入结果。远程调用期间不得持有数据库行锁。

publish 在同一事务中锁定模板定义行、当前 draft_version 行和 ai_profile_import_config 行，再校验完整试运行绑定。冻结草稿必须执行一条包含以下条件的更新并要求 affected rows=1：

- prompt_version_id、template_id、lifecycle_status=draft、deleted=0。
- expectedVersion 和当前 contentSha256。
- test_status=success。
- tested_content_sha256、tested_runtime_sha256、fixture code/version/hash、tested_model_name、tested_config_version 均等于锁内当前值。

条件冻结成功后才切换 active_version_id、清空 draft_version_id，并把锁内校验通过的完整试运行绑定写入不可变 publish 审计快照。并发草稿保存、试运行写回、另一管理员发布或模型配置更新，只能有一个提交路径成功；任一条件变化都整体回滚。模型配置写路径依赖同一配置行的数据库行锁，不允许绕过配置行 version 更新。

draft_create、draft_update、draft_abandon、test、publish 和 restore 六类动作都写 ai_profile_import_prompt_audit。publish 和 restore 另外同步调用 `AdminOperationLogger.logRequired`；该新增强制方法必须加入调用方当前事务并检查底层 save 返回值，异常或 `false`/0 rows 都抛出并回滚调用事务，禁止异步或 REQUIRES_NEW，现有其他调用方的 best-effort `log` 语义不在本期改动。全局日志固定使用 `moduleCode=ai-profile-import`、`operationCode=prompt-publish|prompt-restore`、`targetType=ai_profile_import_prompt_template`、`targetId=templateId`、`operationResult=1`；`beforeSnapshot`、`afterSnapshot`、`failReason`、`confirmToken` 均为 null，唯一 JSON payload 放在 `extraContext`。该 payload 必须是专用脱敏日志值对象，并且只能含 `templateId`、`promptVersionId`、`versionNo`、`scene`、`contentSha256`、`runtimeSha256`、`lifecycleStatus`、`reasonCode`、`candidateCount`、`workCount` 十个字段，禁止传入实体、详情 DTO、System/Repair Prompt、changeSummary 或任意用户/模型正文。专用版本/审计表是长期事实源，admin_operation_log 只承担全局操作留痕。

所有治理动作的 reason 使用服务端固定枚举，不接受自由文本。外部动作集合精确为：发布 `INITIAL_RELEASE / QUALITY_ADJUSTMENT / CONFIG_ALIGNMENT`，恢复 `QUALITY_REGRESSION / INCIDENT_ROLLBACK`，放弃 `DRAFT_SUPERSEDED / DRAFT_INVALID`。内部动作集合精确为 `DRAFT_CREATED_CURRENT / DRAFT_CREATED_HISTORY / DRAFT_UPDATED / TEST_EXECUTED`，由服务端生成，客户端不得提交。Controller 根据动作校验对应子集。API Key、当前 Prompt、fixture/用户样本文本等任意非枚举值必须在 DTO 绑定或服务校验阶段拒绝，且拒绝值本身不得写入失败审计、稳定错误响应或异常日志。

_Requirements: R8-R17, R32-R37, R50-R57_

## 8. 管理 API

Controller 映射根路径如下；通过项目全局 `/api` 前缀后，对外路径为 `/api/admin/ai/profile-import/prompt-templates`：

    /admin/ai/profile-import/prompt-templates

接口：

| Method | Path | 权限 | 作用 |
|---|---|---|---|
| GET | / | page + template-read | 两个场景摘要 |
| GET | /{templateCode}/versions | page + template-read | 版本列表 |
| GET | /versions/{versionId} | page + template-read | 正文详情 |
| POST | /{templateCode}/drafts | template-update | 从当前或 sourceVersionId 新建草稿 |
| PUT | /versions/{versionId} | template-update | 保存草稿 |
| POST | /versions/{versionId}/abandon | template-update | 放弃草稿 |
| POST | /versions/{versionId}/test | template-test | 固定样例试运行 |
| POST | /versions/{versionId}/publish | template-publish | 发布草稿 |
| POST | /{templateCode}/versions/{versionId}/restore | template-restore | 将目标历史发布版本恢复为当前版本 |
| GET | /audits | audit | 最近 50 条模板审计 |

关键请求：

CreateDraftReq：

- sourceVersionId，可空；为空时复制当前版本
- expectedTemplateVersion，必填

draft_create 的 reasonCode 由服务端根据 sourceVersionId 是否为空生成，客户端不提交。

UpdateDraftReq：

- versionLabel
- systemPromptBody
- repairPromptBody
- changeSummary
- expectedVersion

VersionActionReq（publish / abandon）：

- reasonCode，服务端按 publish/restore/abandon 动作校验允许子集
- expectedTemplateVersion
- expectedVersion

RestoreReq：

- 路径 versionId 是目标 prompt_version_id，不是乐观锁 version
- reasonCode，服务端按 restore 动作校验允许子集
- expectedTemplateVersion

restore 先用 templateCode 定位并锁定模板，再读取路径 versionId 对应目标版本并执行归属、released/deleted、哈希、合同和渲染校验。expectedTemplateVersion 只用于拒绝 active 指针并发变化，绝不能作为目标版本 ID 使用。

客户端不得提交自由文本 reason、lifecycleStatus、activeVersionId、draftVersionId、schemaVersion、contractVersion、contentSha256、operatorId 或测试结果。changeSummary 只进入版本表，不复制到专用动作审计或 admin_operation_log。

_Requirements: R48-R57_

## 9. 权限

保留页面权限：

- page.system.ai-profile-import

新增动作：

- action.system.ai-profile-import.template-read
- action.system.ai-profile-import.template-update
- action.system.ai-profile-import.template-test
- action.system.ai-profile-import.template-publish
- action.system.ai-profile-import.template-restore

复用：

- action.system.ai-profile-import.audit

权限迁移只向当前有效系统管理员角色追加权限，不用前端 fallback。模型公共配置 update 权限不推导模板发布权限。

_Requirements: R52-R55_

## 10. 错误合同

运行时小程序继续使用：

- 46002 / PROFILE_IMPORT_UNAVAILABLE

新增后台治理错误：

| code | errorCode | 场景 |
|---|---|---|
| 46018 | PROFILE_IMPORT_PROMPT_VERSION_CONFLICT | expectedVersion 已过期 |
| 46019 | PROFILE_IMPORT_PROMPT_INVALID | 正文或合同无效 |
| 46020 | PROFILE_IMPORT_PROMPT_TEST_REQUIRED | 尚未成功试运行 |
| 46021 | PROFILE_IMPORT_PROMPT_TEST_STALE | 正文或模型配置已变化 |
| 46022 | PROFILE_IMPORT_PROMPT_STATE_CONFLICT | 草稿、发布或恢复状态冲突 |

管理端按 errorCode 显示稳定状态。非法 reasonCode 按 PROFILE_IMPORT_PROMPT_INVALID 处理且不得回显原始非法值；版本冲突不得清空本地编辑正文。

_Requirements: R40-R42, R56-R57_

## 11. 运行时接入

Phase A 不把 Resolver 接入用户识别链路，生产调用明确继续使用 legacy-code-v1。Phase B 切换后，ProfileImportServiceImpl 在消耗 Redis 用户配额前完成：

    validate request
      -> runtimeConfig()
      -> promptRuntimeResolver.resolve(scene)
      -> validate raw length
      -> consume daily quota
      -> model call

RuntimeResolver 必须联表读取 scene 对应模板和 active_version，并逐项确认 template.deleted=0、templateId 归属、scene 匹配、version.deleted=0、lifecycle_status=released、内容哈希正确以及 Schema/合同版本受支持。模板不可用不得消耗用户配额，也不得读取任意历史版本或 legacy-code-v1。

Phase B 中 DeepSeekProfileTextExtractor 的 extract 方法新增 ProfileImportPromptRuntime 参数，并物理删除生产调用对 Java SYSTEM_PROMPT/REPAIR_PROMPT 常量的依赖。首次请求使用 runtime.systemPrompt；Repair 使用同一 runtime.systemPrompt 与 runtime.repairPrompt。requestId 不进入 Prompt 正文。

SchemaValidator 继续执行最终校验。works_only 即使模型违规返回 profile 候选，也必须判定响应无效，而不是静默接收。

调用审计在模板解析成功后记录谱系；模板解析前失败时谱系列允许为 null，但 errorCode 必须为 PROFILE_IMPORT_UNAVAILABLE。

_Requirements: R4-R6, R26, R38-R45_

## 12. 管理端 UI

现有路由 /system/ai-profile-import 保持不变。AiProfileImportConfigView.vue 增加独立组件：

- components/business/ProfileImportPromptTemplatePanel.vue

Panel 负责：

- full_profile / works_only 两个 Tab。
- 当前版本摘要。
- 开放草稿状态。
- 版本表。
- 宽屏编辑 Dialog。
- 发布、恢复、放弃确认。
- 发布、恢复、放弃确认中的原因使用动作限定下拉选项，只提交 reasonCode，不提供自由文本输入。
- 模板审计 Tab。

版本表列：

- 版本
- 状态
- 哈希摘要
- 测试模型
- 测试结果
- 更新人
- 更新时间
- 操作

组件复用 StatusTag、TableActions 和 AuditConfirmDialog。页面不新增营销说明、卡片画廊、Hero 或全局样式。完整 Prompt 只在具备 template-read 权限时按需加载。

错误状态：

- 首次加载失败：Panel 内错误状态和重试。
- 写操作 loading：锁定对应动作，其他场景仍可浏览。
- 版本冲突：保留 Dialog 草稿，刷新服务端 expectedVersion 后由管理员人工合并。
- 测试失败：保留测试错误码和草稿，不允许发布。
- 无权限：不渲染对应按钮，后端继续强制鉴权。
- 首次发布前：active_version_id 为空时不提供 bootstrap 草稿放弃动作，后端继续返回状态冲突兜底。

_Requirements: R1-R2, R46-R57, R69-R70_

## 13. 数据迁移

新增迁移：

- V20260726_001__ai_profile_import_prompt_template_governance.sql
- V20260726_002__ai_profile_import_prompt_permission_alignment.sql

V001：

1. 创建三张模板治理表。
2. 以 additive DDL 扩展调用审计。
3. 插入 full_profile 和 works_only 模板定义。
4. 插入两个 v1 bootstrap 草稿，lifecycle_status=draft、test_status=untested；正文来自现有硬编码语义，但不伪造 released、active 或真实模型测试成功。
5. 回填各模板 draft_version_id，active_version_id 保持 null。
6. 校验两个场景各有且只有一个未删除开放草稿、复合指针归属正确；失败时让外部 schema release / JDBC migration execution 失败且不记录 schema history。

初始只读版本：

- schemaVersion=profile-import-json-v1
- contractVersion=profile-import-contract-v1

V001 只建立 Phase A 治理事实源，不切换生产识别。Phase A 后端保留并明确使用 legacy-code-v1；管理员必须使用当前真实 DeepSeek 配置分别试运行两个 bootstrap 草稿，再通过普通 publish 事务生成 released v1 和 active 指针。Phase B 切换后的新后端不保留硬编码 fallback。旧后端应用回滚仍会忽略新增表和 nullable 列并继续使用旧 Java Prompt。

V002：

- 注册五个模板动作权限。
- 向有效系统管理员角色追加权限。
- 不修改正式 7 页导航。

_Requirements: R55, R58-R63_

## 14. 测试设计

### 14.1 后端单元测试

- ProfileImportPromptPolicyTest
- ProfileImportPromptRendererTest
- ProfileImportPromptRuntimeResolverImplTest
- ProfileImportPromptManagementServiceImplTest
- ProfileImportPromptTesterImplTest
- AdminOperationLoggerTest 扩展，覆盖 logRequired 的异常和 save=false/0-row 合同
- AdminAiProfileImportPromptController 权限合同测试
- DeepSeekProfileTextExtractorTest 扩展
- ProfileImportServiceImplTest 扩展
- ProfileImportErrorContractTest 扩展
- AiProfileImportPersistenceShapeTest 扩展

必须按 RED -> GREEN -> REFACTOR 执行。

### 14.2 MySQL 集成

扩展或新增 ProfileImportPromptGovernanceMySqlIntegrationTest，覆盖：

- Phase A 种子为两个未测试 bootstrap 草稿，active 指针为空。
- active/draft 复合指针归属和单场景开放草稿唯一性。
- active 指针为空时禁止放弃唯一 bootstrap 草稿，已有 active 后允许正常放弃开放草稿。
- 发布事务、条件冻结、不可变发布绑定快照，以及专用/全局审计异常和 save=false/0-row 回滚。
- 两管理员并发发布只有一个成功。
- 发布与草稿保存/试运行写回并发时未测试内容不能发布。
- 模型配置并发更新时旧绑定不能发布。
- 在隔离 fixture 中发布 v2 后执行 v2 -> v1 历史恢复，证明 active 指针切换、新请求使用 v1 且旧请求谱系不变；同时覆盖损坏、跨模板、不支持合同目标的拒绝。
- 调用审计谱系。
- API Key、用户原文、fixture/Prompt 正文作为非法 reasonCode 时在持久化前被拒绝；原文、完整响应、完整 Prompt、自由文本 reason、changeSummary 和密钥不落新增表或 admin_operation_log。

### 14.3 既有回归

- DeepSeekProfileTextExtractorTest
- ProfileImportSchemaValidatorTest
- ProfileImportCandidateProofServiceTest
- ProfileImportApplyServiceImplTest
- ProfileImportApplyMySqlIntegrationTest
- 王火火 29 条作品 golden fixture

### 14.4 管理端

扩展 scripts/e2e-ai-profile-import-config.mjs：

- 两个场景渲染。
- 只读、编辑、测试、发布、恢复权限隔离。
- 新建、编辑、放弃草稿。
- 草稿不影响当前版本。
- 试运行失败和 stale 阻断发布。
- 发布与恢复确认。
- 发布、恢复、放弃使用动作限定 reasonCode 选项，不存在自由文本 reason 输入。
- 版本冲突保留正文。
- 模板审计刷新。
- 无 template-read 时不发详情请求，列表响应不含正文，正文不进入 DOM、表单值或 browser storage。
- read、update、test、publish、restore 和 audit 权限逐项独立门禁。
- 无未处理 mock、network、console 错误和明文密钥。

E2E 增加 `--dist` 模式。默认模式启动 Vite dev server；`--dist` 模式只能在 `npm run build` 和 dist sanitizer 成功后使用 `vite preview`/等价静态服务器加载真实 dist，至少覆盖登录入口、`/system/ai-profile-import` 路由、Prompt Panel、按需详情与懒加载资源。

验证命令：

    cd kaipai-admin
    npm run type-check
    npm run build
    npm run e2e:ai-profile-import-config
    npm run e2e:ai-profile-import-config -- --dist

后端验证命令在实施计划中按现有 Maven 测试选择器精确列出，并在收尾运行完整相关门禁。

_Requirements: R64-R71_

## 15. 发布与恢复

发布顺序分为两个不可合并的阶段：

Phase A：

1. 运行治理面后端专项、MySQL 集成测试、完整 Maven 构建，以及管理端开发态与 sanitizer 后 dist E2E。
2. 应用 V001/V002，验证两个 bootstrap v1 均为 draft/untested、draft 指针正确且 active 指针为空。
3. 发布治理面后端和管理端；生产识别继续明确使用 legacy-code-v1。
4. 在后台使用当前真实 DeepSeek 配置分别试运行 full_profile v1 与 works_only v1。
5. 通过正常 publish API 发布两个 v1，核对完整绑定、审计和 active 指针。

Phase B：

1. 部署前再次验证两个场景均存在同模板 released active version，内容/运行时/fixture/模型配置绑定有效，合同受支持且完整 Prompt 可渲染。
2. 运行 RuntimeResolver、extractor、service、Schema/proof/apply、MySQL 和 29 条 golden fixture 门禁。
3. 发布已删除生产 Java Prompt 依赖的运行时接管版本。
4. 使用授权测试账号执行一笔 full_profile 和一笔 works_only smoke，确认调用审计谱系完整。
5. 观察稳定错误码、Schema invalid 比率和模型耗时；数据或合同不完整时只允许 fail closed，不得应用内回退。

应用回滚：

- 回滚到旧后端时，旧代码忽略新增表和 nullable 列。
- 新后端运行异常时不得手工清空 active_version_id。
- Prompt 内容质量问题优先使用后台历史恢复。
- 数据迁移不做破坏性 down migration。

实施后新增 Prompt 发布、观察和历史恢复 runbook，并同步 docs/dev-playbook.md。

_Requirements: R37-R45, R58-R63, R72_

## 16. 文件变更边界

根仓库：

- 新增本 Spec 三件套。
- 更新 Spec 索引、Spec-代码映射和 CURRENT_CONTEXT。
- 实施完成后补 execution.md 与 runbook。

后端：

- 新增两份迁移、三实体、三 Mapper、管理服务、Resolver、Policy、Contract、Renderer、Tester、Controller 和 DTO。
- 修改 ProfileImportRuntimeConfig、DeepSeekProfileTextExtractor、ProfileImportServiceImpl、AdminOperationLogger、调用审计实体及相关测试。

管理端：

- 新增 ProfileImportPromptTemplatePanel.vue。
- 修改 AiProfileImportConfigView.vue、SettingsView.vue、api/ai.ts、types/ai.ts、权限常量/注册表和现有 E2E。
- 不修改正式 sidebar、风格模板页或小程序前端。

_Requirements: R1-R72_
