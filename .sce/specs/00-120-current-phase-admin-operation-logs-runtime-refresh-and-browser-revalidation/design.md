# 00-120 设计说明

## 1. 设计目标

`00-120` 只处理一个问题：

1. 当前 `8010 / 5100` 运行态是否已经反映 `00-118 / 00-119` 的修复

## 2. 已核实事实

### 2.1 刷新前 `8010` 曾是旧实例

当前登录态 API 复核已确认：

- `operation-logs` 列表仍 `code=500`
- AI 矩阵仍返回旧字段 `fallbackRoleCount`
- 招募矩阵仍返回旧字段 `fallbackRoleCount / pageFallbackRoleCount / actionFallbackRoleCount`

刷新前这说明：

- 当前运行态仍是旧后端进程
- 不能直接做 `00-120` 浏览器验收，否则只会复核旧结果

### 2.2 前端 `5100` 大概率会直接读最新源码

当前 `5100` 是 Vite 开发服务，通常读取当前工作树源码。

因此：

- 当前更需要刷新的是 `8010` 后端

### 2.3 当前运行态已刷新

当前已再次核实：

- `8010` 当前新实例已在 `dev` profile 下启动并监听
- `GET /admin/system/operation-logs?pageNo=1&pageSize=1` 已恢复 `code=200`
- AI 矩阵已返回 `operationLogsCouplingRoleCount / operationLogsCouplingBoundUserCount / operationLogsCouplingCleared`
- 招募矩阵已返回 `adminUsersCouplingRoleCount / pageAdminUsersCouplingRoleCount / actionAdminUsersCouplingRoleCount`
- 真实浏览器已复核：
  - `/system/settings`
  - `/system/operation-logs`

## 3. 设计策略

### 3.1 先刷新运行态

1. 只停掉占用 `8010` 的旧进程
2. 用当前仓代码重新起 `8010`
3. 用 API 复核新实例已经吃到：
   - operation-logs 列表修复
   - AI / 招募矩阵新 schema

### 3.2 再做浏览器验收

刷新后用真实浏览器复核：

- `/system/settings`
- `/system/operation-logs`

并输出截图。

## 4. 风险与边界

### 4.1 已确认

- 当前不需要新增代码功能
- 只需要刷新旧实例并复核

### 4.2 当前边界

- 本轮仍只针对本机运行态
- 不扩大到其它环境部署
