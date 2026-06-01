# 当前阶段后端包结构迁移文档对齐 Execution

## 2026-06-01

### 建档背景

- 用户要求：根据本次后端迁移，更新所涉及文档，并先创建 Specs 来承接这件事。
- 已基于 `00-179` 的调查结论创建本 Spec：
  - `00-180-current-phase-backend-docs-package-path-alignment`
- 本轮只创建 SCE 文档，不执行批量文档替换。

### 已读取上下文

- `.sce/README.md`
- `.sce/steering/CURRENT_CONTEXT.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
- `kaipaile-server/AGENTS.md`
- `kaipaile-server/.agents/backend-conventions.md`
- `kaipaile-server/.agents/project-architect.md`
- `00-179-current-phase-backend-layered-package-refactor-investigation`

### 旧路径引用审计

搜索模式：

```text
com\.kaipai\.module
src/main/java/com/kaipai/module
module/server
module/controller
module/model
```

全仓文档层面命中文件数：

```text
99
```

其中：

```text
.sce/runbooks/backend-admin-release/records/*.md: 33
.sce/specs/**/*.md: 58
kaipaile-server/.agents/*.md: 7
```

说明：

- 旧路径大量存在于历史 Spec 和发布记录中。
- 不能把所有旧路径都当成当前错误，因为许多是历史执行证据。
- 必须先区分“活文档”和“历史证据”。

### 后端 agent 文档命中情况

```text
kaipaile-server/.agents/talent-profile-agent.md       11
kaipaile-server/.agents/recruit-transaction-agent.md  12
kaipaile-server/.agents/project-architect.md          28
kaipaile-server/.agents/backend-conventions.md         1
kaipaile-server/.agents/auth-security-agent.md         8
kaipaile-server/.agents/ai-governance-agent.md         4
kaipaile-server/.agents/admin-operations-agent.md      7
```

结论：

- `.agents` 是 P0 活文档，必须更新。
- `project-architect.md` 是命中最多的当前架构分派入口，应优先更新。

### SCE 当前事实源命中情况

```text
.sce/steering/CURRENT_CONTEXT.md                       1
.sce/specs/spec-code-mapping.md                       83
```

结论：

- `CURRENT_CONTEXT.md` 的旧路径应直接更新。
- `spec-code-mapping.md` 需要谨慎处理：当前事实源路径更新，历史条目加历史说明，不追求全文件旧路径清零。

### 近期腾讯云 Spec 命中情况

```text
.sce/specs/00-176-current-phase-tencent-cloud-phone-realname-integration-research/tencent-cloud-phone-realname-investigation.md  2
.sce/specs/00-176-current-phase-tencent-cloud-phone-realname-integration-research/execution.md                                  5
.sce/specs/00-177-current-phase-tencent-sms-login-enablement/design.md                                                          1
.sce/specs/00-177-current-phase-tencent-sms-login-enablement/execution.md                                                       8
.sce/specs/00-178-current-phase-tencent-cloud-realname-two-factor-enablement/design.md                                          1
.sce/specs/00-178-current-phase-tencent-cloud-realname-two-factor-enablement/execution.md                                       1
```

结论：

- `00-176 / 00-177 / 00-178` 属于近期会继续查阅的腾讯云能力文档。
- 这些文档应追加迁移后路径注记，而不是删除当时执行语境。

### 本轮交付

新增：

```text
.sce/specs/00-180-current-phase-backend-docs-package-path-alignment/requirements.md
.sce/specs/00-180-current-phase-backend-docs-package-path-alignment/design.md
.sce/specs/00-180-current-phase-backend-docs-package-path-alignment/tasks.md
.sce/specs/00-180-current-phase-backend-docs-package-path-alignment/execution.md
.sce/specs/00-180-current-phase-backend-docs-package-path-alignment/documentation-audit.md
```

更新：

```text
.sce/specs/README.md
```

### 待执行

后续按 `tasks.md` 执行：

1. 更新后端 `.agents` 活文档。
2. 更新 SCE 当前事实源。
3. 给近期腾讯云 Spec 追加迁移后当前路径注记。
4. 历史 runbook 记录保留原文。
5. 运行旧路径搜索验证。

## 2026-06-01 执行结果

- 已更新 `kaipaile-server/AGENTS.md`。
- 已更新 `kaipaile-server/.agents/backend-conventions.md`、`project-architect.md`、`auth-security-agent.md`、`talent-profile-agent.md`、`recruit-transaction-agent.md`、`ai-governance-agent.md`、`admin-operations-agent.md`。
- 已更新 `.sce/steering/CURRENT_CONTEXT.md`。
- 已更新 `.sce/specs/spec-code-mapping.md`。
- 已更新 `00-176`、`00-177`、`00-178` 的迁移后当前路径注记。
- 已在 `00-179` 中追加 `00-180` 作为后续文档对齐承接。
- 已抽样复核发布记录，确认历史 runbook 保留原始旧路径。

### 旧路径验证

`kaipaile-server/.agents` 与 `kaipaile-server/AGENTS.md`：

- 旧 `module` 路径搜索无命中。

`.sce/steering/CURRENT_CONTEXT.md`：

- 旧 `module` 路径搜索无命中。

`.sce/specs/00-176 / 00-177 / 00-178`：

- 旧路径仍存在，但都已追加迁移后当前路径注记。

`.sce/specs/spec-code-mapping.md`：

- 旧路径仍存在，顶部已新增后端包结构迁移说明。
- 现阶段命中数：`81`，其中大部分属于历史条目和测试树历史路径。

`.sce/runbooks/backend-admin-release/records`：

- 命中数：`47`
- 属于历史发布记录，按 00-180 约定保留原文。
