# 00-118 设计说明

## 1. 设计目标

`00-118` 只做一个最小修复：

1. 恢复 `operation-logs` 列表事实源
2. 不动详情接口
3. 不动页面降级兜底

## 2. 已核实事实

### 2.1 列表失败但详情成功

运行时核查已确认：

- `GET /admin/system/operation-logs/{id}`：成功
- `GET /admin/system/operation-logs?pageNo=1&pageSize=1`：失败

因此：

- `operation-logs` 表和详情读取链路都还活着
- 当前问题集中在“列表查询路径”

### 2.2 根因来自分页查询 `SELECT *`

临时 `8011` 后端实例日志已明确报错：

- `Out of sort memory, consider increasing server sort buffer size`

同时 MyBatis 输出已证明：

- 列表分页查询仍然 `SELECT operation_log_id, ... before_snapshot_json, after_snapshot_json, extra_context_json, ...`

也就是说：

- 清单页并不需要的 JSON/BLOB 列，被一起拖入排序和分页链路
- 无结果筛选的查询命中更多样本时，容易触发 MySQL 排序内存问题

### 2.3 为什么详情接口没坏

详情接口使用：

- `getById(operationLogId)`

这是主键精确读取，不需要对大 JSON 列做分页排序。

因此详情链路可以继续保留全字段读取。

## 3. 设计策略

### 3.1 列表接口最小修复

在 `AdminOperationLogServiceImpl#adminOperationLogList` 中对 wrapper 增加 `select(...)`，只保留列表页实际需要字段：

- `operationLogId`
- `adminUserId`
- `adminUserName`
- `moduleCode`
- `operationCode`
- `targetType`
- `targetId`
- `requestId`
- `operationResult`
- `failReason`
- `clientIp`
- `confirmedAt`
- `createTime`

### 3.2 详情接口保持不动

详情继续通过 `getById` 返回：

- `beforeSnapshotJson`
- `afterSnapshotJson`
- `extraContextJson`
- `userAgent`

### 3.3 为什么不先做数据库索引

虽然额外索引也可能进一步缓解排序压力，但当前已定位到更小、更直接的修复：

- 列表页本来就不该携带大 JSON 列排序

因此本轮优先：

- 先删冗余列
- 让查询回到与页面职责匹配的最小字段集

## 4. 风险与边界

### 4.1 已确认

- 修复只影响列表查询选列
- 不影响详情接口
- 不影响权限、路由与 hidden tooling 边界

### 4.2 当前边界

- 本轮不保证 `operation-logs` 事实源所有历史问题都已彻底清零
- 只修当前已复现的列表 500 根因
