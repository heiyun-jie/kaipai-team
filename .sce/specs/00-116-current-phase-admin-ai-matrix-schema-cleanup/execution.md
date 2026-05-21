# 00-116 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`README.md`、`spec-code-mapping.md`、`00-114`、`00-115`
- 已确认当前主线从“招募矩阵 schema 清理”转入“AI 矩阵 schema 清理”

## 2. 清理前证据

### 2.1 当前残留字段

后端 DTO / 前端类型 / 前端消费仍残留：

- `fallbackRoleCount`
- `fallbackBoundUserCount`
- `canRetireFallback`
- `reliesOnFallback`

### 2.2 当前 dev 运行库事实

已核实当前 dev 运行库：

- `enabled_role_count = 1`
- `fallback_role_count = 0`
- `fallback_bound_user_count = 0`
- `ai_ready_role_count = 1`
- `pending_role_count = 0`

当前判断：

- 当前 AI 矩阵的 `fallback*` 已不再描述 runtime fallback
- 只是在表达 `page.system.operation-logs` 历史耦合

## 3. 本轮实施

### 3.1 后端

已完成：

- `AdminRoleAiGovernanceMatrixRespDTO.java`
- `AdminRoleAiGovernanceMatrixItemDTO.java`
- `AdminRoleServiceImpl.java`

把 AI 矩阵字段统一改成：

- `operationLogsCouplingRoleCount`
- `operationLogsCouplingBoundUserCount`
- `operationLogsCouplingCleared`
- `retainsOperationLogsCoupling`

### 3.2 前端

已完成：

- `types/system.ts`
- `RolesView.vue`
- `SettingsView.vue`

同步改为消费新字段，并把用户可见文案切到“操作日志页历史耦合 / AI 直授权待补”口径。

### 3.3 用户可见标签

已补一处阶段标签收口：

- `fallback_only` 在 AI 矩阵中的用户可见标签改为 `仅操作日志页耦合`

## 4. 验证结果

### 4.1 前端

命令：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

保留告警：

- Sass legacy JS API deprecation
- Vite chunk size warning

### 4.2 后端

命令：

- `cd D:\XM\kaipai-team\kaipaile-server && mvn -q -DskipTests compile`

结果：

- `compile`：通过

## 5. 结论

`00-116` 已完成本轮目标：

- AI 矩阵 schema 命名已与当前运行态一致
- 当前“操作日志页历史耦合 / AI 直授权缺口”的语义已在前后端统一
- 本轮未触碰 operation-logs 事实源与数据库
