# 00-126 设计说明

## 1. 设计目标

`00-126` 只处理一个问题：

1. 在不改变招募运行时鉴权边界的前提下，清掉 dev 运行库中已经失效的 `menu.recruit`

## 2. 已核实事实

### 2.1 `menu.recruit` 当前不参与 runtime 放通

当前已确认：

- 前端招募路由只认 `page.recruit.*`
- 后端招募 controller 只认 `page.recruit.* / action.recruit.*`
- `adminMenus.recruit` 无 `menuPermission`

因此：

- 移除运行库中的 `menu.recruit` 不会改变当前 runtime 放通边界

### 2.2 当前运行库仍残留 `menu.recruit`

当前已确认：

- dev 运行库当前仅有 `ADMIN` 一条角色数据
- `ADMIN` 已具备完整招募页面 / 动作直授权
- 但仍保留 `menu.recruit`

因此：

- 当前可以做“已满足直授权门禁角色”的最小清理

## 3. 设计策略

### 3.1 用 migration 清理运行库

本轮新增幂等 migration：

- 只在角色当前同时具备：
  - `page.recruit.projects`
  - `page.recruit.roles`
  - `page.recruit.applies`
  - `action.recruit.project.status`
  - `action.recruit.role.status`
  时，才从 `menu_permissions_json` 中移除 `menu.recruit`

### 3.2 刷新后端运行态

由于 migration 只有在后端启动时应用，本轮必须：

1. 停掉当前 `8010` 实例
2. 用当前仓代码重新启动 `8010`
3. 再做接口与浏览器复核

### 3.3 保持历史展示代码不删

本轮只清运行库数据，不删：

- `PERMISSIONS.menu.recruit`
- 矩阵中的 `hasRecruitMenu`
- 角色页的历史提示分支

等到运行库与用户可见结果稳定后，再决定是否需要下一条代码退场切片。

## 5. 已完成验证补充

本轮已再次核实：

- 登录态 session 已不再返回 `menu.recruit`
- 角色详情已不再返回 `menu.recruit`
- 招募矩阵中的 `hasRecruitMenu` 已变为 `false`
- `/system/roles` 浏览器运行态中：
  - 招募矩阵不再显示 `历史 menu.recruit`
  - 角色目录菜单数已从 `7` 收到 `6`
  - 编辑弹窗中的 unknown list 继续保持为 `0`

## 4. 风险与边界

### 4.1 已确认

- 当前不需要修改前端路由
- 当前不需要修改后端招募 controller

### 4.2 当前边界

- 只覆盖本机 dev 运行库
- 不外推到其它环境
