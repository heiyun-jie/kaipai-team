# 当前阶段后端包结构迁移文档对齐 Requirements

> 状态：待执行 | 优先级：P0 | 依赖：`00-179`

## 1. 概述

`00-179` 已确认后端从旧 `com.kaipai.module.*` 结构迁移到 `controller / service / model / mapper / integration` 顶层分层。当前仍有一批活文档、agent 文档、SCE 映射文档和近期腾讯云能力 Spec 引用旧 `module` 路径，后续开发如果继续按这些文档执行，会把代码写回已退出的旧结构。

本 Spec 用于承接“迁移后文档对齐”工作：先界定哪些文档必须更新、哪些历史记录只保留原始事实、哪些地方需要追加迁移注记，再给出执行和验收规则。本 Spec 只创建文档更新任务，不在本轮直接批量修改所有受影响文档。

## 2. 用户故事

- 作为后端开发者，我需要 backend agent 文档直接指向当前包结构，而不是旧 `module` 目录。
- 作为 SCE 维护者，我需要 `CURRENT_CONTEXT` 和 `spec-code-mapping` 不再把旧路径当作当前事实源。
- 作为实名 / 短信接入维护者，我需要 `00-176 / 00-177 / 00-178` 中的当前代码落点能反映迁移后的真实路径。
- 作为发布记录维护者，我需要历史 runbook 记录保留当时事实，不被批量改写成看似当时就存在的新路径。

## 3. 功能需求

### 3.1 更新后端 agent 活文档

**描述**：后端 `.agents/*.md` 是后续 AI 协作和任务分派的活文档，必须从旧 `module` 路径更新为当前分层结构。

**验收标准**：

1. WHEN 阅读 `kaipaile-server/.agents/backend-conventions.md` THEN 能看到当前顶层包职责：`controller`、`service`、`model`、`mapper`、`integration`、`common`。
2. WHEN 阅读 `kaipaile-server/.agents/project-architect.md` THEN 各业务分区的目录指向当前路径，不再指向 `src/main/java/com/kaipai/module/*`。
3. WHEN 阅读领域 agent 文档 THEN 对应域的 controller、service、model、mapper、integration 路径都按当前分层列出。
4. WHEN 搜索 `kaipaile-server/.agents` THEN 不应再出现把 `module/controller`、`module/server`、`module/model` 作为当前目录的描述。

### 3.2 更新 SCE 当前事实源

**描述**：SCE 中代表当前事实的文档必须同步后端包结构迁移。

**验收标准**：

1. WHEN 阅读 `.sce/steering/CURRENT_CONTEXT.md` THEN 当前后端代码基线不再引用旧 `module` 路径。
2. WHEN 阅读 `.sce/specs/spec-code-mapping.md` THEN 当前仍作为事实源或后续任务入口的后端路径应更新到新路径，或明确标注为历史路径。
3. WHEN 阅读 `.sce/specs/README.md` THEN 能看到本 Spec 登记为 `00-180`。

### 3.3 更新近期腾讯云能力 Spec 的当前路径

**描述**：`00-176 / 00-177 / 00-178` 是近期仍会被继续查阅的腾讯云手机号、短信、实名接入文档，应追加迁移后的当前代码落点。

**验收标准**：

1. WHEN 阅读 `00-178` 的设计和执行记录 THEN 可以直接找到当前实名 provider 的 `integration/verify` 路径。
2. WHEN 阅读 `00-177` 的设计和执行记录 THEN 可以直接找到当前短信 provider 的 `integration/sms` 路径。
3. WHEN 阅读 `00-176` 的调研和执行记录 THEN 可以看到旧路径是调研时点事实，迁移后路径以 `00-179 / 00-180` 为准。
4. WHEN 文档需要保留历史执行记录 THEN 不删除历史语境，只追加“迁移后当前路径”注记。

### 3.4 区分活文档与历史证据

**描述**：大量旧路径位于历史 Spec execution 或发布记录中。它们记录当时执行事实，不应被批量改写为新路径。

**验收标准**：

1. WHEN 旧路径位于 `.sce/runbooks/backend-admin-release/records/*.md` THEN 默认保留原文，不做批量替换。
2. WHEN 旧路径位于历史 Spec 的 `execution.md` THEN 默认保留原文，只在该文档仍被当作当前入口时追加迁移注记。
3. WHEN 旧路径位于活文档、agent 文档或当前映射表 THEN 必须更新或明确降级为历史引用。

### 3.5 建立路径替换规则

**描述**：本轮文档更新必须按 `00-179` 的迁移映射执行，不能凭感觉替换。

**验收标准**：

1. WHEN 旧路径是 `module/controller/admin/*` THEN 新路径写为 `controller/admin/*`。
2. WHEN 旧路径是 `module/controller/{domain}/*` THEN 新路径写为 `controller/api/{domain}/*`。
3. WHEN 旧路径是 `module/server/{domain}/service/*` THEN 新路径写为 `service/{domain}/*`。
4. WHEN 旧路径是 `module/server/{domain}/mapper/*` THEN 新路径写为 `mapper/{domain}/*`。
5. WHEN 旧路径是 `module/model/{domain}/*` THEN 新路径写为 `model/{domain}/*`。
6. WHEN 旧路径描述短信、实名、微信、AI provider、COS 等外部能力 THEN 新路径优先写入 `integration/*`。

### 3.6 验证旧路径残留不再误导

**描述**：完成文档更新后，需要用搜索命令验证活文档中旧路径不再作为当前事实出现。

**验收标准**：

1. WHEN 搜索 `kaipaile-server/.agents` THEN 不再出现旧 `src/main/java/com/kaipai/module` 路径。
2. WHEN 搜索 `.sce/steering/CURRENT_CONTEXT.md` 和 `.sce/specs/spec-code-mapping.md` THEN 旧路径要么消失，要么明确标注为历史路径。
3. WHEN 搜索近期腾讯云 Spec THEN 旧路径如果存在，必须紧邻迁移后当前路径注记。
4. WHEN 搜索历史 runbook 记录 THEN 允许保留旧路径，因为它们是归档证据。

## 4. 非功能需求

- 不修改后端业务代码、前端代码或数据库 migration。
- 不把真实 SecretId、SecretKey、身份证号、手机号等敏感信息写入任何文档。
- 不批量改写历史发布记录，避免破坏审计事实。
- 文档更新必须可审计：每类文档说明为什么更新或为什么保留。
- 路径映射必须与 `00-179` 保持一致。

## 5. 约束条件

- 不恢复旧 `src/main/java/com/kaipai/module` 目录。
- 不把历史 `execution.md` 伪装成当前事实；需要保留时间语境。
- 不触碰当前无关未跟踪文件。
- 不处理 `target/classes` 编译产物。
- 不在本 Spec 里直接执行全部文档迁移；实际修改应按 `tasks.md` 后续执行。

## 6. 验收总则

1. 新增 `00-180-current-phase-backend-docs-package-path-alignment` Spec 目录。
2. Spec 包含 `requirements.md`、`design.md`、`tasks.md`、`execution.md` 和 `documentation-audit.md`。
3. `.sce/specs/README.md` 已登记 `00-180`。
4. 文档明确活文档更新范围、历史证据保留策略、路径替换规则和验证命令。
5. 本轮不引入业务代码改动，不泄露敏感信息。
