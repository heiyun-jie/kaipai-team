# 00-117 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`README.md`、`spec-code-mapping.md`、`00-109`、`00-116`
- 已确认当前最合理的下一手不是继续删 AI 代码，而是先做 AI / operation-logs 脱钩审计

## 2. 已核实证据

### 2.1 AI runtime 已直接授权

已核实：

- `AdminAiResumeController.java` 当前直接使用：
  - `page.system.ai-resume-governance`
  - `action.system.ai-resume.review`
  - `action.system.ai-resume.resolve`

当前判断：

- AI runtime 当前不依赖 `page.system.operation-logs`

### 2.2 AI 矩阵只剩历史耦合审计

已核实：

- 当前 dev 运行库：
  - `enabled_role_count = 1`
  - `operation_logs_coupling_role_count = 0`
  - `operation_logs_coupling_bound_user_count = 0`
  - `ai_ready_role_count = 1`
  - `pending_role_count = 0`

当前判断：

- AI 矩阵当前只是在提示“历史是否还保留 operation-logs 权限耦合”
- 不再是 runtime 兜底链

### 2.3 operation-logs 当前仍是独立 hidden tooling

已核实：

- router 保留 `/system/operation-logs`
- menus 保留 `system-operation-logs`
- `SettingsView.vue` 单独展示“操作留痕审计”
- `OperationLogsView.vue` 当前继续承担降级承接

### 2.4 operation-logs 事实源仍异常

已核实：

- `00-109` 已确认 operation-logs 当前事实源异常并已做降级承接
- 本轮直接请求 `http://127.0.0.1:8010/api/admin/system/operation-logs` 未登录态返回 `401`
- 当前未重新获取登录态 500 证据，但基于 `00-109` 与现有前端降级逻辑，事实源异常结论继续成立

## 3. 脱钩矩阵结论

详见：

- `D:\XM\kaipai-team\.sce\specs\00-117-current-phase-admin-ai-operation-logs-detachment-audit\ai-operation-logs-detachment-matrix.md`

核心结论：

1. AI runtime：**已脱钩**
2. AI 矩阵 / 权限编辑提示：**仅保留历史耦合展示**
3. operation-logs：**仍是独立 hidden tooling**

## 4. 本轮实施

本轮为 audit-only 切片：

- 新增 `00-117`
- 新增脱钩矩阵文档
- 回填 README / mapping / CURRENT_CONTEXT
- 不改运行时代码

## 5. 结论

`00-117` 已完成本轮目标：

- 已明确 AI 主链当前不再依赖 `page.system.operation-logs`
- 已明确 `operation-logs` 仍是独立 hidden tooling，不应顺手删除
- 下一步若继续推进，应优先围绕 `operation-logs` 自身做独立切片，而不是继续从 AI 主链方向删代码
