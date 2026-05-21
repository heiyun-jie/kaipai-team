# 00-119 当前阶段后台 operation-logs 运行态恢复与摘要清理（Current Phase Admin Operation Logs Runtime Re-enable and Summary Cleanup）

> 状态：已完成 | 优先级：中高 | 依赖：00-118 current-phase-admin-operation-logs-fact-source-recovery-audit
> 记录目的：在 `00-118` 已恢复 operation-logs 列表事实源后，继续回收系统设置页中仍把 operation-logs 默认显示为“事实源异常”的旧降级摘要口径。

## 1. 背景

截至 `2026-04-23`：

- `00-118` 已确认：
  - `/admin/system/operation-logs?pageNo=1&pageSize=1` 已在临时运行态恢复 `code=200`
  - 当前直接 500 根因是列表查询选列过宽
  - 后端已改为列表按需选列
- 当前 `OperationLogsView.vue` 本身已经按成功 / 失败两条分支显示，不需要删除 degraded 兜底
- 但 `SettingsView.vue` 的系统设置摘要仍存在旧口径：
  - 初始态 `operationLogLoaded=false` 时直接显示 `事实源异常`
  - 没有区分“加载中 / 未请求完成”和“真实异常”

当前判断：

- 后端事实源恢复后，系统设置页不应在初始加载阶段默认显示异常
- 应保留异常分支，但只在请求失败时显示

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-119`
- 修改 `SettingsView.vue` 的 operation-logs 摘要状态：
  - 初始 / 加载中：显示 `正在核对`
  - 成功：显示 `${operationLogTotal} 条记录`
  - 失败：显示 `事实源异常`
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不删除 `OperationLogsView.vue` 的 degraded 兜底
- 不改 operation-logs 后端查询
- 不新增数据库 migration
- 不改变 hidden tooling 路由 / 菜单

## 3. 需求

### 3.1 摘要状态合同

- **R1** 系统设置页不能在请求尚未完成时把 operation-logs 显示成“事实源异常”。
- **R2** 请求成功后必须显示真实日志总数。
- **R3** 请求失败时必须继续显示“事实源异常”，保留降级承接。

### 3.2 验证合同

- **R4** 本轮必须至少通过：
  - `kaipai-admin` 的 `npm run type-check`
  - `kaipai-admin` 的 `npm run build`

## 4. 验收标准

- [x] 已新增独立 `00-119`
- [x] `SettingsView.vue` 已区分 operation-logs 的加载中 / 成功 / 异常状态
- [x] 前端 type-check / build 通过
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
