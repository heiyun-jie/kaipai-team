# 00-115 设计说明

## 1. 设计目标

`00-115` 只做一件事：

1. 把招募矩阵中仍沿用 `fallback` 命名的 schema，统一重命名为“后台账号页历史耦合 / 直授权缺口”。

## 2. 已核实事实

### 2.1 runtime fallback 已在上一轮退场

`00-114` 已让以下对象退场：

- 前端 `stores/permission.ts` 自动注入
- 招募 hidden tooling 页 fallback 提示与传参
- 后端 `AdminRecruitController` fallback `@PreAuthorize`
- `RecruitGovernanceFallbackGate.java`
- session 中的 `allowLegacyRecruit*`

因此：

- 当前招募矩阵里的 `fallback*` 字段已经不再对应 runtime 行为

### 2.2 当前残留问题是 schema 语义失真

后端 DTO 与前端类型仍使用：

- `fallbackRoleCount`
- `pageFallbackRoleCount`
- `actionFallbackRoleCount`
- `fallbackBoundUserCount`
- `canRetirePageFallback`
- `canRetireActionFallback`
- `canRetireFallback`
- `pageReliesOnFallback`
- `actionReliesOnFallback`
- `reliesOnFallback`

但当前真实语义已经变成：

- 角色是否仍保留 `page.system.admin-users` 历史耦合
- 页面直授权是否仍待补
- 动作直授权是否仍待补

## 3. 设计策略

### 3.1 新命名

后端 DTO / 前端类型统一切为：

- `fallbackRoleCount` -> `adminUsersCouplingRoleCount`
- `pageFallbackRoleCount` -> `pageAdminUsersCouplingRoleCount`
- `actionFallbackRoleCount` -> `actionAdminUsersCouplingRoleCount`
- `fallbackBoundUserCount` -> `adminUsersCouplingBoundUserCount`
- `canRetirePageFallback` -> `pageAdminUsersCouplingCleared`
- `canRetireActionFallback` -> `actionAdminUsersCouplingCleared`
- `canRetireFallback` -> `adminUsersCouplingCleared`
- `pageReliesOnFallback` -> `pageRetainsAdminUsersCoupling`
- `actionReliesOnFallback` -> `actionRetainsAdminUsersCoupling`
- `reliesOnFallback` -> `retainsAdminUsersCoupling`

### 3.2 为什么不改 API path

当前问题不是 API 职责变化，而是字段语义清理。

因此：

- `GET /admin/system/roles/recruit-governance-matrix` 继续保留
- 只改响应体字段命名与前端消费

### 3.3 为什么不动 AI 矩阵

AI 矩阵仍真实表达 `page.system.operation-logs` 旧日志兜底，因此其 `fallback*` 命名当前仍与运行态一致。

因此：

- 本轮只清理招募矩阵
- AI 矩阵继续保持原状

## 4. 风险与边界

### 4.1 已确认

- 招募矩阵消费者当前集中在：
  - 后端 DTO
  - `AdminRoleServiceImpl`
  - 前端 `types/system.ts`
  - 前端 `RolesView.vue`

### 4.2 当前边界

- 本轮若只重命名字段，不改数据库、不改权限逻辑，风险主要在前后端字段对齐

因此本轮主验证手段就是：

- 前端 type-check / build
- 后端 compile
