# 00-117 当前阶段后台 AI / operation-logs 脱钩审计（Current Phase Admin AI Operation Logs Detachment Audit）

> 状态：已完成 | 优先级：高 | 依赖：00-109 current-phase-admin-system-operation-logs-degraded-state-alignment、00-116 current-phase-admin-ai-matrix-schema-cleanup
> 记录目的：在 `00-116` 已完成 AI 矩阵 schema 清理后，继续把 AI 主链与 `operation-logs` hidden tooling 的剩余关系做成独立审计，明确哪些是已脱钩、哪些仍是历史耦合展示、哪些不能顺手删除。

## 1. 背景

截至 `2026-04-23`：

- `00-109` 已确认：
  - `/admin/system/operation-logs` 当前事实源异常
  - `OperationLogsView.vue` 已做降级承接
- `00-114` 已确认：
  - recruit runtime fallback 已退场
- `00-116` 已确认：
  - AI 矩阵字段已从 `fallback` 命名切到“操作日志页历史耦合”命名

当前剩余问题不再是 schema 命名，而是：

1. AI 主链是否还在运行态依赖 `operation-logs`
2. `operation-logs` 是否仍应保留为独立 hidden tooling
3. AI 权限编辑、系统设置聚合和矩阵展示里，哪些地方只是历史耦合提示，哪些地方还是主链依赖

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-117`
- 审计以下对象：
  - AI 管理后端 controller / service
  - AI 矩阵与 AI 权限包
  - `OperationLogsView.vue`
  - 系统设置聚合页中的 AI / operation-logs 入口
  - hidden tooling 菜单 / 路由中的 `operation-logs`
- 形成 AI / operation-logs 脱钩矩阵
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不修 `operation-logs` 事实源 500
- 不删除 `page.system.operation-logs`
- 不删除 `OperationLogsView.vue`
- 不改 AI runtime 权限或接口

## 3. 需求

### 3.1 审计合同

- **R1** 必须区分：
  - AI runtime 直接依赖
  - AI 历史耦合展示
  - operation-logs 独立 hidden tooling
- **R2** 若某对象只承担“历史耦合提示”或“独立审计工具”职责，不得误判为 AI 主链依赖。
- **R3** 若某对象仍承担独立审计工具职责，不得因为 AI 主链已脱钩就顺手删除。

### 3.2 结论合同

- **R4** 必须明确 AI runtime 当前是否仍依赖 `page.system.operation-logs`。
- **R5** 必须明确 `operation-logs` 当前是否仍应保留为 hidden tooling。
- **R6** 必须明确下一手若继续推进，应优先进入：
  - operation-logs 事实源修复
  - 或 operation-logs hidden tooling 保留审计
  - 而不是继续从 AI 主链方向盲删代码

## 4. 验收标准

- [x] 已新增独立 `00-117`
- [x] 已形成 AI / operation-logs 脱钩矩阵
- [x] 已明确 AI runtime 当前不再依赖 `page.system.operation-logs`
- [x] 已明确 `operation-logs` 当前仍属于 hidden tooling，不能顺手删除
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
