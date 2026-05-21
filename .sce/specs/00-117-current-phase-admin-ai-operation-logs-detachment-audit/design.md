# 00-117 设计说明

## 1. 设计目标

`00-117` 只处理一个问题：

1. 明确 AI 主链已经与 `operation-logs` 运行时脱钩
2. 明确 `operation-logs` 当前仍是独立 hidden tooling
3. 给后续工作提供“不要误删 / 不要误修”的边界

## 2. 已核实事实

### 2.1 当前 AI runtime 直接权限

后端 AI 管理接口当前直接使用：

- `page.system.ai-resume-governance`
- `action.system.ai-resume.review`
- `action.system.ai-resume.resolve`

当前没有任何类似 recruit 的 fallback gate。

### 2.2 当前 dev 运行库 AI 矩阵已清零

当前 dev 运行库核查结果：

- `enabled_role_count = 1`
- `operation_logs_coupling_role_count = 0`
- `operation_logs_coupling_bound_user_count = 0`
- `ai_ready_role_count = 1`
- `pending_role_count = 0`

因此：

- AI 矩阵里的 operation-logs 只剩历史耦合审计意义

### 2.3 当前 operation-logs 仍是独立 hidden tooling

当前仍有明确独立职责：

- router 保留 `/system/operation-logs`
- menus 保留 `system-operation-logs`
- `SettingsView.vue` 仍单独聚合操作留痕入口
- `OperationLogsView.vue` 仍承担降级承接

同时 `00-109` 已确认：

- 该页事实源当前返回 500

因此：

- `operation-logs` 当前不能当作 AI 主链能力
- 但也不能因为 AI 已脱钩就删掉

## 3. 设计策略

### 3.1 本轮只做审计，不做实现

原因：

1. AI 主链方向的运行时代码已经在 `00-116` 前基本收口
2. 当前剩余问题是“边界识别”，不是“继续删代码”
3. `operation-logs` 事实源异常，使其后续走向必须单独判定

### 3.2 审计输出

本轮输出一张矩阵，把对象分成三类：

- AI runtime direct dependency
- AI historical coupling display
- Operation-logs independent hidden tooling

这样后续如果继续推进：

- 修 AI，不会误打到 operation-logs hidden tooling
- 修 operation-logs，也不会误以为在修 AI 主链

## 4. 风险与边界

### 4.1 已确认

- AI 主链已经脱钩
- `operation-logs` 当前仍独立保留

### 4.2 当前不确定边界

- `operation-logs` 后续是“修事实源后保留”还是“长期降级并最终退场”，当前证据不足

因此下一手应先围绕 `operation-logs` 自身做独立切片，而不是继续从 AI 主链扩展。
