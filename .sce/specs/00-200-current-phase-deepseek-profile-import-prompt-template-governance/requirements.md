# 00-200 DeepSeek 资料识别 Prompt 模板治理

> 状态：书面 Spec 已审阅确认，三份详细实施计划已完成；尚未修改 00-200 生产代码
>
> 优先级：P0
>
> 日期：2026-07-26
>
> 上游依赖：00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import

## 1. 背景

00-199 已实现 DeepSeek 资料导入的模型、Endpoint、API Key、超时、配额、连接测试、启停与审计配置，但生产识别 Prompt 仍硬编码在后端 Java 常量中。管理员无法在后台创建草稿、验证修改、发布版本、追溯某次识别使用的 Prompt，或在识别质量下降时恢复历史版本。

本 Spec 将 DeepSeek 资料识别 Prompt 纳入后台治理，同时保持 00-199 R95 的安全边界：字段白名单、枚举、证据校验、防幻觉规则、候选签名、数据库映射和 apply 事务不得由自由文本 Prompt 放宽或绕过。

## 2. 目标

建立以下闭环：

    后台创建场景草稿
      -> 编辑可调 Prompt 正文
      -> 后端静态合同校验
      -> 使用固定脱敏样例真实试运行
      -> 管理员确认发布
      -> 运行时按场景选择当前版本
      -> 调用审计记录模板谱系
      -> 必要时恢复历史发布版本

## 3. 范围

### 3.1 本期范围

- DeepSeek 资料识别 full_profile 场景。
- DeepSeek 资料识别 works_only 场景。
- 两个场景各自的 System Prompt 和 Repair Prompt。
- 草稿、试运行、发布、历史恢复、放弃草稿、权限和审计。
- 识别请求对 Prompt 版本、Schema 版本和安全合同版本的运行时追溯。
- 在现有“系统设置 -> DeepSeek 资料导入”页面内完成治理。

### 3.2 非目标

- AI 分享图 Prompt。
- AI 简历润色 Prompt。
- 生图 provider 测试 Prompt 或连接探针。
- 全平台通用 Prompt 中台。
- 允许后台修改字段白名单、枚举或数据库映射。
- 本期切换 DeepSeek provider 的 response_format 为 json_schema。
- 修改小程序页面、候选复核 UI 或 apply 请求合同。
- 顺带核销 00-199 的作品数据库唯一门禁、素材迁移或 T6/T9。

## 4. 术语

- 模板定义：一个稳定场景入口，首期固定为 full_profile 和 works_only。
- 模板版本：某一场景下的一份可追溯 Prompt 正文。
- 开放草稿：尚未发布且允许编辑的唯一草稿版本。
- 发布版本：已经通过发布门禁、正文不可再修改的版本。
- 当前版本：模板定义通过 active_version_id 指向的运行版本。
- 安全合同：后端代码持有、后台只读的字段、枚举、证据与防幻觉规则。
- Schema 版本：服务端结构化输出合同版本。
- 运行时哈希：后台正文与当前代码安全合同渲染出的完整 System/Repair Prompt 经无歧义 framing 后得到的 SHA-256。

## 5. 功能需求

### 5.1 信息架构与场景

- R1 后台入口必须继续归属“系统设置 -> DeepSeek 资料导入”，不得增加第 8 个一级导航。
- R2 模板治理不得复用分享内容域的“风格模板”页面或数据表。
- R3 首期模板场景只允许 full_profile 和 works_only。
- R4 full_profile 允许返回个人档案候选与作品候选。
- R5 works_only 必须从模型调用阶段要求 profileCandidates 为空数组，不得先生成档案候选后再丢弃。
- R6 两个场景继续使用相同顶层 Envelope，避免破坏现有提取响应和小程序复核合同。

### 5.2 版本与草稿

- R7 每个场景必须存在一个稳定模板定义。
- R8 每个场景同时最多存在一个开放草稿，并由 draft_version_id 与数据库 active-draft 唯一门禁共同保证。
- R9 新建草稿默认复制当前发布版本；管理员也可从指定历史发布版本创建草稿。
- R10 草稿允许编辑版本名称、System Prompt 正文、Repair Prompt 正文和变更说明；场景模板编码与场景展示名称保持稳定。
- R11 草稿更新必须携带 expectedVersion，并在并发覆盖时返回稳定版本冲突。
- R12 草稿正文改变后，之前的试运行结果必须立即失效。
- R13 已发布版本正文、Schema 版本、安全合同版本和内容哈希不可原地修改。
- R14 已存在当前发布版本时，放弃草稿必须将版本标记为 abandoned、清空 draft_version_id 并记录固定 reasonCode，不得物理删除版本；Phase A 首次发布前 active_version_id 为空时，禁止放弃唯一 bootstrap 草稿并返回稳定状态冲突。
- R15 从某场景首次正常发布开始，模板定义必须通过 active_version_id 指向唯一当前版本；Phase A bootstrap 草稿尚未发布时 active_version_id 必须为空。
- R16 历史恢复必须只允许选择已发布版本，并原子切换 active_version_id。
- R17 历史恢复和已发布版本重新试运行不得篡改旧版本正文、旧调用审计或发布时固化的完整试运行绑定审计快照。

### 5.3 Prompt 与安全合同

- R18 最终 System Prompt 必须由后台可编辑正文与后端固定安全合同组合生成。
- R19 最终 Repair Prompt 必须追加后端固定的“只修合法 JSON、不改变事实”合同。
- R20 用户复制原文必须继续作为独立 user message 发送，不得插值进后台模板正文。
- R21 后台模板不得插入 API Key、加密主密钥、候选签名密钥、其他用户数据或任意服务端环境变量。
- R22 后端必须限制模板正文长度、字符编码和允许变量；首期模板正文不支持自由变量插值。
- R23 字段白名单、枚举、sourceText 证据、数字保真、生日精度、籍贯隔离、性别推断和媒体占位规则继续由后端校验器最终裁决。
- R24 后台不得修改 Schema 版本、安全合同版本、字段白名单或枚举。
- R25 首期继续使用 response_format=json_object，并由 ProfileImportSchemaValidator 执行完整结构和事实校验。
- R26 首次提取与当次 Repair 重试必须绑定同一模板版本、Schema 版本和安全合同版本。

### 5.4 试运行、发布与恢复

- R27 模板试运行必须使用后端固定、脱敏且版本受控的测试样例。
- R28 full_profile 样例必须覆盖个人档案与作品；works_only 样例必须验证 profileCandidates 为空。
- R29 试运行必须调用当前已配置、连接测试成功且启用条件满足的 DeepSeek 模型。
- R30 试运行不得写个人档案、作品、素材、用户调用审计正文、Redis 用户配额或普通用户请求记录。
- R31 试运行只允许持久化模板版本、内容哈希、完整运行时哈希、测试 fixture 编码/版本/哈希、模型名、模型配置版本、结果状态、候选计数、作品计数、耗时和稳定错误码。
- R32 试运行成功必须绑定 contentSha256、runtimeSha256、fixtureCode、fixtureVersion、fixtureSha256、modelName 和 configVersion。
- R33 草稿内容、代码安全合同正文、Schema/合同版本、固定 fixture、模型名或模型配置版本变化后，原试运行结果必须被判定为 stale。
- R34 发布必须要求与当前完整运行时 Prompt、当前 fixture 和当前模型配置精确绑定的试运行结果成功且未失效。
- R35 发布必须在单事务内按固定锁顺序锁定模板定义、草稿版本和模型配置行，校验 expectedVersion 与条件冻结结果、切换 active_version_id，并写入包含 content/runtime hash、fixture code/version/hash、Schema/合同版本、modelName、configVersion、testedBy/testedAt 的不可变发布绑定审计快照和脱敏管理员操作日志。
- R36 发布任一步失败时，草稿状态、当前版本指针和审计必须整体回滚。
- R37 历史恢复属于应急动作，不强制重新调用 DeepSeek，但必须选择非空固定 reasonCode，并重新校验目标归属当前模板、状态为已发布、内容哈希正确、Schema/合同版本受当前代码支持且完整 Prompt 可渲染；任一失败不得切换 active_version_id。

### 5.5 运行时与隐私审计

- R38 Phase B 识别运行时必须按 scene 读取对应模板定义和 active_version_id。
- R39 首期不得增加进程内或 Redis Prompt 缓存，避免多实例发布后读取不一致。
- R40 Phase B 中模板缺失、当前版本指针为空、指针跨模板、目标不是 released、正文损坏、哈希异常或合同版本不受支持时必须 fail closed。
- R41 Prompt 不可用时，小程序只接收稳定的 PROFILE_IMPORT_UNAVAILABLE，手动编辑继续可用。
- R42 Phase B 运行时不得静默退回 Java 硬编码 Prompt、任意历史版本或规则型 AI 润色。
- R43 Phase B 每次实际发起模型识别调用时，调用审计必须记录模板编码、版本 ID、版本号、Schema 版本、安全合同版本和运行时哈希；在模板解析前 fail closed 的请求允许谱系列为空，但必须记录稳定错误码。
- R44 原始剪贴板正文、完整模型响应、候选 sourceText、API Key、候选签名和完整 Prompt 不得进入模板审计、调用审计谱系列或 admin_operation_log。
- R45 模板正文历史由版本表承担；专用动作审计和 AdminOperationLogger 只能接收模板 ID、版本、场景、哈希、状态、固定枚举 reasonCode 与脱敏计数，不得接收实体、正文 DTO、自由文本 reason 或 changeSummary 快照。
- R46 模板正文详情只对具备 template-read 权限的管理员返回。
- R47 列表接口默认只返回状态、版本、哈希摘要、测试状态和操作人，不返回完整 Prompt。

### 5.6 管理 API、权限与错误

- R48 管理 API 必须归属 /api/admin/ai/profile-import/prompt-templates。
- R49 管理 API 必须支持模板列表、版本列表、版本详情、新建草稿、保存草稿、放弃草稿、试运行、发布、恢复和审计。
- R50 所有写操作必须使用当前管理员身份，客户端不得提交 operatorId 或 operatorName。
- R51 发布、恢复和放弃草稿必须要求非空且属于服务端动作白名单的 reasonCode；客户端不得提交自由文本 reason，API Key、用户原文、fixture 正文、Prompt 正文或任意其他文本均必须在 DTO/枚举绑定阶段被拒绝且不得落库或进入日志。
- R52 页面读取继续使用 page.system.ai-profile-import。
- R53 模板正文读取、草稿编辑、试运行、发布和恢复必须拆分独立动作权限。
- R54 模板审计继续受 action.system.ai-profile-import.audit 控制。
- R55 新权限必须通过独立数据库迁移授予现有系统管理员，不得依赖前端 fallback。
- R56 管理端必须按稳定 errorCode 处理模板无效、版本冲突、测试缺失、测试失效和状态冲突，不得猜测中文消息。
- R57 版本冲突后页面必须保留本地编辑内容并允许管理员重新加载服务端版本后人工处理。

### 5.7 数据迁移与兼容

- R58 必须新增模板定义、模板版本和模板审计表，为调用审计增加模板谱系列，并用数据库约束阻止跨模板指针及同场景多个开放草稿。
- R59 数据迁移必须种入 full_profile v1 和 works_only v1 两个 bootstrap 草稿，不得伪造 released、active 或真实试运行成功状态。
- R60 full_profile v1 必须保持现有 Prompt 的字段范围与防幻觉语义；works_only v1 必须保持相同顶层 Envelope并明确禁止生成档案候选。
- R61 上线必须分两阶段：Phase A 只部署模板治理、固定合同、试运行和审计能力，生产识别明确继续使用 legacy-code-v1；两个 v1 经真实试运行和正常发布后才允许进入 Phase B。
- R62 Phase B 切换前必须验证两个场景均有 released active version、精确试运行绑定、受支持合同和可渲染运行时；切换提交必须删除生产调用对 Java Prompt 常量的依赖，连接探针 Prompt 继续由代码持有。
- R63 Phase B 切换后，数据、指针或合同不完整必须阻断识别运行态，不得回退 legacy-code-v1、空模板、任意历史版本或默认字符串。

### 5.8 质量与验证

- R64 后端新增行为必须按 TDD 完成，先验证测试因缺少实现而失败，再写最小实现。
- R65 单元测试必须覆盖草稿唯一性、乐观锁、不可变发布版本、模板政策、渲染、试运行绑定、发布、恢复和失败回滚。
- R66 MySQL 集成测试必须证明 active/draft 指针归属、active-draft 唯一门禁、并发编辑/发布、配置并发更新、审计事务和恢复语义。
- R67 DeepSeek 提取测试必须证明两个场景、首次提取与 Repair 同版本、模板缺失 fail closed。
- R68 现有 Schema validator、防幻觉、候选 proof、apply 和 29 条作品 golden fixture 不得回归。
- R69 管理端必须扩展现有 ai-profile-import 配置 E2E，覆盖权限隔离、草稿生命周期、测试、发布、恢复、冲突和审计；无 template-read 权限时必须证明没有详情请求、正文 DOM、表单值或 browser storage 泄漏。
- R70 管理端必须通过 type-check、生产构建、dist URL sanitizer、开发态浏览器 E2E，以及对 sanitizer 后 dist 产物运行的浏览器 E2E。
- R71 后端必须通过专项单元测试、相关 MySQL 集成测试和 Maven 构建门禁。
- R72 实施完成后必须同步 Spec 映射、CURRENT_CONTEXT、开发手册、Prompt 发布/观察/恢复 runbook 和 execution 证据。

## 6. 验收清单

- [ ] 现有系统设置页面可以查看 full_profile 与 works_only 当前模板。
- [ ] 每个场景最多一个开放草稿，冲突更新不会覆盖他人修改。
- [ ] 保存草稿不会改变线上运行版本。
- [ ] 首次发布前不能放弃 active_version_id 为空时的唯一 bootstrap 草稿。
- [ ] 固定样例试运行成功前不能发布。
- [ ] 草稿或模型配置变化后旧测试结果自动失效。
- [ ] 已发布版本的正文与合同谱系不可修改，测试元数据可刷新，历史版本可受控恢复。
- [ ] 已发布版本重新试运行不会覆盖发布时固化的完整测试绑定审计快照。
- [ ] works_only 在模型阶段就要求 profileCandidates 为空。
- [ ] 字段、枚举、证据和防幻觉合同仍由后端强制。
- [ ] 原始用户正文、完整模型响应和密钥不进入新增表或日志。
- [ ] 发布、恢复和放弃只接受固定 reasonCode，自由文本和敏感内容 reason 在持久化前被拒绝。
- [ ] 每次识别可以追溯模板、Schema 和安全合同版本。
- [ ] 模板缺失或损坏时识别 fail closed，手动编辑可用。
- [ ] 模型配置权限不自动获得 Prompt 发布权限。
- [ ] Phase A 种入两个未发布 bootstrap 草稿，经真实试运行和正常发布后才进入 Phase B 运行时切换。
- [ ] 后端测试、MySQL 集成、管理端 type-check/build/E2E 全部形成新鲜证据。

## 7. 与 00-199 的关系

- 00-199 继续负责职业资料夹、作品库、素材库、DeepSeek 提取/apply 主链和模型连接配置。
- 00-200 接管 00-199 未覆盖的 Prompt 草稿、版本、发布、恢复和运行谱系治理。
- 00-200 不改变 00-199 已核销的 T4/T5 历史结论，也不代表 00-199 的 T6/T9 或整体完成。
