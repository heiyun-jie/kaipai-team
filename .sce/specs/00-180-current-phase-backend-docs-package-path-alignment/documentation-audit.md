# 后端包结构迁移文档影响审计

## 1. 审计目标

基于 `00-179` 的后端包结构迁移结论，识别仍引用旧 `com.kaipai.module` / `src/main/java/com/kaipai/module` 路径的文档，并把它们分成：

- 必须更新的活文档。
- 需要追加迁移注记的近期能力文档。
- 默认保留原文的历史证据。

## 2. 搜索命令

```powershell
rg -n "com\.kaipai\.module|src/main/java/com/kaipai/module|module/server|module/controller|module/model" `
  AGENTS.md `
  .sce `
  docs `
  kaipaile-server/AGENTS.md `
  kaipaile-server/.agents `
  --glob "*.md"
```

全量命中文档数：`99`。

## 3. P0 活文档

### 3.1 Backend agents

| 文件 | 命中数 | 处理 |
|------|--------|------|
| `kaipaile-server/.agents/project-architect.md` | 28 | 重写业务分区路径 |
| `kaipaile-server/.agents/recruit-transaction-agent.md` | 12 | 更新交易撮合层路径 |
| `kaipaile-server/.agents/talent-profile-agent.md` | 11 | 更新供给资料层路径 |
| `kaipaile-server/.agents/auth-security-agent.md` | 8 | 更新身份、短信、实名、微信路径 |
| `kaipaile-server/.agents/admin-operations-agent.md` | 7 | 更新后台治理路径 |
| `kaipaile-server/.agents/ai-governance-agent.md` | 4 | 更新 AI 路径 |
| `kaipaile-server/.agents/backend-conventions.md` | 1 | 更新当前包结构总规范 |

这些文件会直接指导后续任务分派，因此必须更新旧路径。

### 3.2 SCE 当前事实源

| 文件 | 命中数 | 处理 |
|------|--------|------|
| `.sce/steering/CURRENT_CONTEXT.md` | 1 | 直接更新为新路径 |
| `.sce/specs/spec-code-mapping.md` | 83 | 当前事实源更新；历史条目标注历史语境 |

`spec-code-mapping.md` 不能机械清零旧路径。它同时承载历史追溯和当前映射，需要逐条判断。

## 4. P1 近期能力文档

| 文件 | 命中数 | 处理 |
|------|--------|------|
| `.sce/specs/00-176-current-phase-tencent-cloud-phone-realname-integration-research/tencent-cloud-phone-realname-investigation.md` | 2 | 追加迁移后路径注记 |
| `.sce/specs/00-176-current-phase-tencent-cloud-phone-realname-integration-research/execution.md` | 5 | 追加迁移后路径注记 |
| `.sce/specs/00-177-current-phase-tencent-sms-login-enablement/design.md` | 1 | 更新当前短信 provider 路径说明 |
| `.sce/specs/00-177-current-phase-tencent-sms-login-enablement/execution.md` | 8 | 保留历史执行记录，追加当前路径 |
| `.sce/specs/00-178-current-phase-tencent-cloud-realname-two-factor-enablement/design.md` | 1 | 更新当前实名 provider 路径说明 |
| `.sce/specs/00-178-current-phase-tencent-cloud-realname-two-factor-enablement/execution.md` | 1 | 保留历史执行记录，追加当前路径 |

这些 Spec 与当前腾讯云短信、实名能力直接相关，后续排障仍会查阅，必须避免旧路径成为当前入口。

## 5. P2 历史证据

### 5.1 发布记录

`.sce/runbooks/backend-admin-release/records/*.md` 中有 `33` 个文件命中旧路径。

处理策略：

- 默认不改。
- 这些文件记录发布时点工作树状态、overlay 文件和排障事实。
- 改写路径会破坏历史证据可信度。

### 5.2 其他历史 Spec

`.sce/specs/**/*.md` 中除当前事实源和近期腾讯云 Spec 外，还有大量历史 Spec 命中旧路径。

处理策略：

- 历史 `execution.md` 默认不改。
- 仍作为当前入口的 status、design 或 mapping 文档，需要追加迁移注记。
- 不追求所有历史文档旧路径清零。

## 6. 替换边界

允许保留旧路径的场景：

- `00-179 / 00-180` 这类迁移说明文档。
- 历史 runbook 发布记录。
- 历史 execution 记录。
- 明确标注“历史路径 / 迁移前路径”的说明。

必须更新旧路径的场景：

- backend agent 文档。
- 当前上下文文档。
- 当前代码映射表中的当前事实源行。
- 近期腾讯云能力文档中会被当作当前实现入口的路径。

## 7. 验证口径

后续执行完成后，不使用“全仓旧路径零命中”作为验收，因为历史证据会保留旧路径。

正确验收口径：

```powershell
rg -n "src/main/java/com/kaipai/module|com\.kaipai\.module|module/server|module/controller|module/model" kaipaile-server/.agents --glob "*.md"
```

期望：无输出。

```powershell
rg -n "src/main/java/com/kaipai/module|com\.kaipai\.module|module/server|module/controller|module/model" .sce/steering/CURRENT_CONTEXT.md --glob "*.md"
```

期望：无输出。

```powershell
rg -n "src/main/java/com/kaipai/module|com\.kaipai\.module|module/server|module/controller|module/model" .sce/specs/spec-code-mapping.md --glob "*.md"
```

期望：旧路径如仍存在，必须为历史条目并带迁移说明。
