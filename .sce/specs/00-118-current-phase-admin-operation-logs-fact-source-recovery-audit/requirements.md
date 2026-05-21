# 00-118 当前阶段后台 operation-logs 事实源恢复审计（Current Phase Admin Operation Logs Fact Source Recovery Audit）

> 状态：已完成 | 优先级：高 | 依赖：00-109 current-phase-admin-system-operation-logs-degraded-state-alignment、00-117 current-phase-admin-ai-operation-logs-detachment-audit
> 记录目的：在 `00-117` 已明确 `operation-logs` 仍是独立 hidden tooling 后，继续定位列表接口 500 的真实根因，并以最小修复恢复事实源。

## 1. 背景

截至 `2026-04-23`：

- `00-109` 已确认：
  - `OperationLogsView.vue` 当前通过 degraded view 承接 `operation-logs` 事实源异常
- `00-117` 已确认：
  - `operation-logs` 当前仍是独立 hidden tooling，不能顺手删除

本轮新增运行时核查已确认：

1. `/admin/system/operation-logs/{id}` 详情接口在登录态下可成功返回
2. `/admin/system/operation-logs?pageNo=1&pageSize=1&result=1` 成功
3. `/admin/system/operation-logs?pageNo=1&pageSize=1&result=0` 成功
4. `/admin/system/operation-logs?pageNo=1&pageSize=1` 返回 `code=500`
5. 在临时 `8011` 后端实例上复现实验后，日志明确报错：
   - `java.sql.SQLException: Out of sort memory, consider increasing server sort buffer size`
6. 当前出错 SQL 是列表查询对 `admin_operation_log` 做分页时仍 `SELECT *`，把 `before_snapshot_json / after_snapshot_json / extra_context_json` 这些 JSON/BLOB 一并带入排序和分页路径

当前判断：

- 当前 root cause 不是表不存在，也不是详情接口坏掉
- 而是**列表查询选列过宽**，导致无结果筛选的分页查询在 MySQL 上触发排序内存问题

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-118`
- 固化运行时复现证据与根因
- 对 `AdminOperationLogServiceImpl#adminOperationLogList` 做最小修复：
  - 列表查询只选择清单所需字段
  - 保留详情接口继续读取完整快照 JSON
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不修改 `OperationLogsView.vue` 的 degraded 兜底逻辑
- 不删除 `operation-logs` hidden tooling
- 不做数据库 migration
- 不处理更广泛的 MySQL sort buffer 配置

## 3. 需求

### 3.1 根因合同

- **R1** 本轮必须基于真实运行态复现和后端日志确认根因，不能只凭静态猜测下结论。
- **R2** 必须明确区分：
  - 列表接口失败
  - 详情接口成功
  - 根因来自列表查询选列过宽

### 3.2 修复合同

- **R3** 列表查询必须只选择清单页实际需要的字段，不再把 JSON 快照列带入分页查询。
- **R4** 详情接口必须继续返回完整快照 JSON，不能因列表优化而丢失详情能力。
- **R5** 本轮优先做最小修复，不引入数据库 migration 或额外索引。

### 3.3 验证合同

- **R6** 本轮必须至少通过：
  - `kaipai-admin` 的 `npm run type-check`
  - `kaipai-admin` 的 `npm run build`
  - `kaipaile-server` 的 `mvn -q -DskipTests compile`
- **R7** 本轮必须通过临时后端实例或等价运行时验证，确认 `/admin/system/operation-logs?pageNo=1&pageSize=1` 恢复成功。

## 4. 验收标准

- [x] 已新增独立 `00-118`
- [x] 已通过运行时日志确认列表 500 的根因
- [x] `AdminOperationLogServiceImpl` 已完成最小修复
- [x] operation-logs 列表接口在运行态已恢复成功
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
