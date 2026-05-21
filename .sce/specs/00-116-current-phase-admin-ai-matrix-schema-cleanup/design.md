# 00-116 设计说明

## 1. 设计目标

`00-116` 只做一件事：

1. 把 AI 授权收口矩阵中仍沿用 `fallback` 命名的 schema，统一重命名为“操作日志页历史耦合 / AI 直授权缺口”。

## 2. 已核实事实

### 2.1 当前 AI runtime 不依赖 operation-logs 兜底

后端 AI 管理接口当前直接使用：

- `page.system.ai-resume-governance`
- `action.system.ai-resume.review`
- `action.system.ai-resume.resolve`

没有类似 recruit 的 runtime fallback gate。

### 2.2 当前 dev 运行库 AI 矩阵已清零

当前 dev 运行库核查结果：

- `fallback_role_count = 0`
- `fallback_bound_user_count = 0`
- `ai_ready_role_count = 1`

说明：

- 当前矩阵里的 `fallback*` 只剩历史耦合审计意义

### 2.3 为什么本轮不处理 operation-logs 事实源

`operation-logs` 当前真实接口仍异常，这已在 `00-109` 做过降级承接。

但这与当前 AI 矩阵 schema 清理是两件事：

- `00-116` 关注“角色授权矩阵的字段语义”
- 不是“operation-logs 页事实源恢复”

因此本轮不扩大到事实源修复。

## 3. 设计策略

### 3.1 新命名

后端 DTO / 前端类型统一切为：

- `fallbackRoleCount` -> `operationLogsCouplingRoleCount`
- `fallbackBoundUserCount` -> `operationLogsCouplingBoundUserCount`
- `canRetireFallback` -> `operationLogsCouplingCleared`
- `reliesOnFallback` -> `retainsOperationLogsCoupling`

### 3.2 用户可见文案

从：

- 旧日志 fallback
- 操作日志 fallback
- 仍靠 Fallback

切到：

- 操作日志页历史耦合
- AI 直授权待补
- 历史耦合残留

### 3.3 为什么不改 API path 与 stage enum

- `GET /admin/system/roles/ai-governance-matrix` 继续保留
- `rolloutStage='fallback_only'` 暂时保留内部枚举值，只改用户可见标签

理由：

- 当前目标是先清理 schema 主命名，不扩大到 API 或阶段枚举重构

## 4. 风险与边界

### 4.1 已确认

- AI 矩阵消费者当前集中在：
  - 后端 DTO
  - `AdminRoleServiceImpl`
  - 前端 `types/system.ts`
  - 前端 `RolesView.vue`
  - 前端 `SettingsView.vue`

### 4.2 当前边界

- 本轮若只重命名字段和文案，不改权限逻辑、不改数据库，风险主要在前后端字段对齐

因此本轮主验证手段就是：

- 前端 type-check / build
- 后端 compile
