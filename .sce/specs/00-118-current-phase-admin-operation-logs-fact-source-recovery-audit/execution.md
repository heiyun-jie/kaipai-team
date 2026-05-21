# 00-118 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`README.md`、`spec-code-mapping.md`、`00-109`、`00-117`
- 已确认当前下一手应围绕 `operation-logs` 自身恢复，而不是继续从 AI 主链删代码

## 2. 修复前证据

### 2.1 登录态接口复现

已使用后台账号：

- `account = admin`
- `password = <REDACTED>`

对当前本机后端接口做登录态复现：

- `GET /admin/system/operation-logs?pageNo=1&pageSize=1` -> `code=500`
- `GET /admin/system/operation-logs?pageNo=1&pageSize=1&result=1` -> `code=200`
- `GET /admin/system/operation-logs?pageNo=1&pageSize=1&result=0` -> `code=200`
- `GET /admin/system/operation-logs/{id}` -> `code=200`

当前判断：

- 当前异常集中在“无结果筛选的列表分页查询”

### 2.2 数据表事实

已直查当前 dev 运行库：

- `admin_operation_log` 表存在
- 当前 `row_count = 2303`
- 最新数据可正常读取

### 2.3 临时 8011 后端实例日志

已启动临时后端实例：

- `server.port = 8011`

并在该实例上复现 `/admin/system/operation-logs?pageNo=1&pageSize=1`。

日志明确报错：

- `java.sql.SQLException: Out of sort memory, consider increasing server sort buffer size`

同时 MyBatis 输出已确认，列表查询仍在 `SELECT *`，把以下大字段一并带入：

- `before_snapshot_json`
- `after_snapshot_json`
- `extra_context_json`

## 3. 本轮实施

### 3.1 代码改动

文件：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\system\service\impl\AdminOperationLogServiceImpl.java`

已实施：

- 在 `adminOperationLogList` 的 wrapper 上增加 `select(...)`
- 列表查询现在只选择清单页实际需要字段
- 详情接口 `adminOperationLogDetail` 不变

### 3.2 改动边界

本轮未改：

- `OperationLogsView.vue`
- `OperationLogs` DTO 结构
- 数据库 migration
- hidden tooling 路由 / 菜单

## 4. 验证结果

### 4.1 编译验证

命令：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`
- `cd D:\XM\kaipai-team\kaipaile-server && mvn -q -DskipTests compile`

结果：

- `type-check`：通过
- `build`：通过
- `compile`：通过

保留告警：

- Sass legacy JS API deprecation
- Vite chunk size warning

### 4.2 运行时验证

已在临时 `8011` 后端实例上重新验证：

- `GET /admin/system/operation-logs?pageNo=1&pageSize=1` -> `code=200`
- `GET /admin/system/operation-logs?pageNo=1&pageSize=1&result=1` -> `code=200`
- `GET /admin/system/operation-logs?pageNo=1&pageSize=1&result=0` -> `code=200`

当前判断：

- 当前列表 500 已恢复

## 5. 结论

`00-118` 已完成本轮目标：

- 已定位并修复 operation-logs 列表事实源异常的直接根因
- 当前根因是列表分页查询选列过宽，而不是详情链路损坏
- 当前修复保持在最小范围内，恢复了 hidden tooling 列表能力
