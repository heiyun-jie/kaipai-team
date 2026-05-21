# 00-120 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`README.md`、`spec-code-mapping.md`、`00-118`、`00-119`
- 已按 `00-120` 主线先验证本机 `8010` 运行态，再做真实浏览器复核

## 2. 运行态刷新与 API 证据

### 2.1 `8010` 当前已监听并加载新实例

本轮直接核对：

- `Get-NetTCPConnection -LocalPort 8010` 显示 `8010` 当前由新进程监听
- `D:\XM\kaipai-team\output\runtime\00-120\backend-8010.out.log` 已记录：
  - `The following 1 profile is active: "dev"`
  - `Tomcat started on port 8010 (http) with context path '/api'`
  - `Started KaipaiApplication`
- `D:\XM\kaipai-team\output\runtime\00-120\backend-8010.err.log` 当前为空

依据：

- 直接监听态
- 新启动日志

置信度：

- 高

不确定边界：

- 本结论只覆盖当前本机 `8010` dev 实例
- 不外推到其它环境或其它端口实例

### 2.2 登录态 API 已吃到 `00-118 / 00-119` 后的新后端代码

已使用后台账号：

- `account = admin`
- `password = <REDACTED>`

登录态接口复核结果：

- `POST /admin/auth/login` -> `code=200`
- `GET /admin/system/operation-logs?pageNo=1&pageSize=1` -> `code=200`
  - `total = 2305`
  - 首条记录 `operationLogId = 2305`
- `GET /admin/system/operation-logs/2305` -> `code=200`
  - `moduleCode = system`
  - `operationCode = ai_resume_timeout_escalation`
  - `beforeSnapshotJson / afterSnapshotJson` 均存在
- `GET /admin/system/roles/ai-governance-matrix` 已返回新字段：
  - `operationLogsCouplingRoleCount`
  - `operationLogsCouplingBoundUserCount`
  - `operationLogsCouplingCleared`
- `GET /admin/system/roles/recruit-governance-matrix` 已返回新字段：
  - `adminUsersCouplingRoleCount`
  - `pageAdminUsersCouplingRoleCount`
  - `actionAdminUsersCouplingRoleCount`

当前判断：

- 当前 `8010` 已不再是刷新前的旧实例
- `00-118` 的 operation-logs 列表修复与 `00-115 / 00-116` 的矩阵 schema 清理均已进入本机运行态

依据：

- 登录态接口直接返回
- 新 schema 字段已在当前 `8010` 可见

置信度：

- 高

不确定边界：

- 本轮只覆盖本机 `127.0.0.1:8010`
- 未扩展到生产、预发或其它部署节点

## 3. 真实浏览器复核

本轮已使用 Playwright CLI 真实登录 `http://127.0.0.1:5100/login`，随后复核以下页面：

### 3.1 `/system/settings`

当前已确认：

- `权限管理` 分组中的 `操作留痕审计` 摘要已显示 `2305 条记录`
- 页面不再停留在 `事实源异常`

截图证据：

- `D:\XM\kaipai-team\output\playwright\00-120\settings-operation-logs-summary-after.png`

### 3.2 `/system/operation-logs`

当前已确认：

- overview 主卡显示 `2305 条操作记录`
- 列表已正常渲染
- 首屏可见日志 `2305 / 2304 / 2303 ...`
- 已可打开详情抽屉，不再停留在 degraded default

截图证据：

- `D:\XM\kaipai-team\output\playwright\00-120\operation-logs-list-after.png`
- `D:\XM\kaipai-team\output\playwright\00-120\operation-logs-detail-after.png`

依据：

- 真实浏览器 DOM 快照
- 页面截图

置信度：

- 高

不确定边界：

- 当前截图只覆盖本机 `5100` Vite 运行态
- 未对全部筛选条件和分页场景做完整回归，本轮只验证 `00-120` 所要求的恢复主链

## 4. 文档回填

本轮已回填：

- `D:\XM\kaipai-team\.sce\specs\00-120-current-phase-admin-operation-logs-runtime-refresh-and-browser-revalidation\requirements.md`
- `D:\XM\kaipai-team\.sce\specs\00-120-current-phase-admin-operation-logs-runtime-refresh-and-browser-revalidation\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-120-current-phase-admin-operation-logs-runtime-refresh-and-browser-revalidation\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-120-current-phase-admin-operation-logs-runtime-refresh-and-browser-revalidation\execution.md`
- `D:\XM\kaipai-team\.sce\specs\README.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`
- `D:\XM\kaipai-team\.sce\steering\CURRENT_CONTEXT.md`

## 5. 结论

`00-120` 已完成本轮目标：

- 当前 `8010` 已成功刷新到新后端实例
- operation-logs 列表接口与详情接口已在本机运行态恢复
- AI / 招募矩阵当前已返回新 schema，不再是刷新前旧字段
- 系统设置页与 operation-logs 页已通过真实浏览器复核
