# 00-116 当前阶段后台 AI 矩阵 schema 清理（Current Phase Admin AI Matrix Schema Cleanup）

> 状态：已完成 | 优先级：高 | 依赖：00-114 current-phase-admin-recruit-fallback-code-retirement-first-pass、00-115 current-phase-admin-recruit-matrix-schema-cleanup
> 记录目的：在 recruit runtime fallback 已退场且 recruit 矩阵 schema 已清理后，继续把 AI 授权收口矩阵中仍残留的 `fallback` 命名切到“操作日志页历史耦合 / AI 直授权缺口”口径。

## 1. 背景

截至 `2026-04-23`：

- 当前 AI runtime 已直接由：
  - `page.system.ai-resume-governance`
  - `action.system.ai-resume.review`
  - `action.system.ai-resume.resolve`
  承接
- 当前 dev 运行库核查结果：
  - `enabled_role_count = 1`
  - `fallback_role_count = 0`
  - `fallback_bound_user_count = 0`
  - `ai_ready_role_count = 1`
  - `pending_role_count = 0`
- 当前 AI 矩阵仍残留旧命名：
  - `fallbackRoleCount`
  - `fallbackBoundUserCount`
  - `canRetireFallback`
  - `reliesOnFallback`

当前判断：

- 这些字段名已不再准确描述当前运行态
- 它们当前表达的其实是：角色是否仍保留 `page.system.operation-logs` 历史耦合，而不是 runtime fallback 是否仍在生效

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-116`
- 清理后端 AI 矩阵 DTO 字段命名
- 清理 `AdminRoleServiceImpl` 中 AI 矩阵装配命名
- 清理前端 `types/system.ts`、`RolesView.vue`、`SettingsView.vue` 对 AI 矩阵字段的消费命名
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不修改 `operation-logs` 事实源 500 问题
- 不删除 `page.system.operation-logs`
- 不修改 AI 治理页本身的接口与权限
- 不改数据库

## 3. 需求

### 3.1 命名合同

- **R1** AI 矩阵字段必须从 `fallback` 语义切换到“操作日志页历史耦合 / AI 直授权缺口”语义。
- **R2** 字段重命名必须前后端一致。
- **R3** 本轮只清理 AI 矩阵相关 schema，不扩大到 operation-logs 页事实源修复。

### 3.2 口径合同

- **R4** 明细字段必须表达：角色是否仍保留 `page.system.operation-logs` 历史耦合。
- **R5** 汇总字段必须表达：当前启用角色中仍保留该历史耦合的角色数与绑定账号数。
- **R6** 用户可见文案必须从“旧日志 fallback”切到“操作日志页历史耦合 / AI 直授权待补”。

### 3.3 验证合同

- **R7** 本轮必须至少通过：
  - `kaipai-admin` 的 `npm run type-check`
  - `kaipai-admin` 的 `npm run build`
  - `kaipaile-server` 的 `mvn -q -DskipTests compile`

## 4. 验收标准

- [x] 已新增独立 `00-116`
- [x] AI 矩阵 schema 命名已从 `fallback` 切换到“操作日志页历史耦合”
- [x] 前端 `RolesView.vue` 与 `SettingsView.vue` 已同步消费新字段
- [x] 前端 type-check / build 与后端 compile 通过
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
