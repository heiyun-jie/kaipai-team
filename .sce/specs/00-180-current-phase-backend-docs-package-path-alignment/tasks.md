# 当前阶段后端包结构迁移文档对齐 Tasks

## 1. 建档与审计

- [x] 创建 `00-180-current-phase-backend-docs-package-path-alignment` Spec。  
  **Validates: Requirements 6**
- [x] 审计旧 `module` 路径在 agent、SCE、runbook 记录中的分布。  
  **Validates: Requirements 3.1, 3.2, 3.4**
- [x] 记录活文档、近期能力文档、历史证据三层处理策略。  
  **Validates: Requirements 3.4**
- [x] 更新 `.sce/specs/README.md` 登记 `00-180`。  
  **Validates: Requirements 6**

## 2. P0 后端 agent 文档更新

- [x] 更新 `kaipaile-server/.agents/backend-conventions.md`，把当前包根从 `module` 改为 `controller / service / model / mapper / integration / common`。  
  **Validates: Requirements 3.1**
- [x] 更新 `kaipaile-server/.agents/project-architect.md`，按当前业务分区重写目录列表。  
  **Validates: Requirements 3.1**
- [x] 更新 `kaipaile-server/.agents/auth-security-agent.md`，对齐 auth / verify / sms / wechat 新路径。  
  **Validates: Requirements 3.1, 3.5**
- [x] 更新 `kaipaile-server/.agents/talent-profile-agent.md`，对齐 actor / crew / card / level 新路径。  
  **Validates: Requirements 3.1, 3.5**
- [x] 更新 `kaipaile-server/.agents/recruit-transaction-agent.md`，对齐 recruit / order / payment / refund 新路径。  
  **Validates: Requirements 3.1, 3.5**
- [x] 更新 `kaipaile-server/.agents/ai-governance-agent.md`，对齐 AI controller / service / integration 新路径。  
  **Validates: Requirements 3.1, 3.5**
- [x] 更新 `kaipaile-server/.agents/admin-operations-agent.md`，对齐 adminauth / system / referral 新路径。  
  **Validates: Requirements 3.1, 3.5**
- [x] 复核 `kaipaile-server/AGENTS.md` 是否需要补充当前包结构总入口说明。  
  **Validates: Requirements 3.1**

## 3. P0 / P1 SCE 当前文档更新

- [x] 更新 `.sce/steering/CURRENT_CONTEXT.md` 中当前后端代码基线旧路径。  
  **Validates: Requirements 3.2**
- [x] 更新 `.sce/specs/spec-code-mapping.md` 中当前事实源路径，历史条目加标注。  
  **Validates: Requirements 3.2, 3.4**
- [x] 更新 `00-176` 调研与执行文档，追加迁移后当前路径注记。  
  **Validates: Requirements 3.3**
- [x] 更新 `00-177` 设计与执行文档，追加短信 provider 当前 `integration/sms` 路径注记。  
  **Validates: Requirements 3.3**
- [x] 更新 `00-178` 设计与执行文档，追加实名 provider 当前 `integration/verify` 路径注记。  
  **Validates: Requirements 3.3**
- [x] 在 `00-179` 中追加 `00-180` 作为文档对齐承接项，避免后续只停留在调查结论。  
  **Validates: Requirements 3.2**

## 4. 历史证据保留

- [x] 抽样复核 `.sce/runbooks/backend-admin-release/records/*.md`，确认旧路径只作为历史执行记录保留。  
  **Validates: Requirements 3.4**
- [x] 对仍被当前入口引用的历史 Spec 文档，只追加迁移注记，不批量改写原执行事实。  
  **Validates: Requirements 3.4**

## 5. 验证

- [x] 执行 agent 文档旧路径搜索，确认 `.agents` 不再引用旧 `module` 路径。  
  **Validates: Requirements 3.6**
- [x] 执行 SCE 当前事实源旧路径搜索，确认 `CURRENT_CONTEXT` 无旧路径、`spec-code-mapping` 旧路径均有历史标注。  
  **Validates: Requirements 3.6**
- [x] 执行近期腾讯云 Spec 搜索，确认旧路径旁有迁移后当前路径注记。  
  **Validates: Requirements 3.6**
- [x] 记录验证命令和输出到本 Spec `execution.md`。  
  **Validates: Requirements 3.6**
