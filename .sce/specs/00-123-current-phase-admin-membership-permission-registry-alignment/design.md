# 00-123 设计说明

## 1. 设计目标

`00-123` 只处理一个问题：

1. 把后端真实存在的 membership 页面 / 动作权限重新纳入前端 permission registry 和 permission tree

## 2. 已核实事实

### 2.1 问题根因不是运行时鉴权，而是前端 registry 缺口

当前已确认：

- 后端 membership controller 真实消费对应权限
- 角色编辑弹窗把这批权限显示为“未登记权限”
- `PermissionTreeEditor.vue` 的“未登记权限”来源是 `getUnknownPermissionCodes(...)`

因此：

- 当前主问题是 registry / tree 不完整
- 不是运行时 permission 判断异常

### 2.2 membership 模块当前未进入 permission tree

当前 `permissionTreeData` 的 `moduleOrder` 仍来自 `adminMenus.map(...)`。

因此：

- 即使 registry 已有部分 membership 权限
- 由于 `adminMenus` 不含 membership 模块，membership 仍不会出现在权限树里

### 2.3 当前运行态已验证对齐结果

本轮已再次核实：

- `/system/roles` 编辑弹窗中的 unknown list 已不再包含 membership 页面 / 动作权限
- permission tree 已出现 `会员中心` 模块

因此：

- 当前问题已证明是 registry / tree 对齐缺口，而不是运行时权限判断问题

## 3. 设计策略

### 3.1 以 controller 为准补齐 registry

本轮按 `AdminMembershipController.java` 补齐：

- 页面权限：
  - `page.membership.benefits`
  - `page.membership.logs`
- 动作权限：
  - `action.membership.benefit.create`
  - `action.membership.benefit.edit`
  - `action.membership.benefit.enable`
  - `action.membership.benefit.disable`
  - `action.membership.product.edit`
  - `action.membership.product.enable`
  - `action.membership.product.disable`
  - `action.membership.product.sort`

### 3.2 将 membership 模块纳入 permission tree

本轮只做 permission tree 可见化：

- 让 `moduleOrder` 包含 `membership`
- 不恢复 `menu.membership`
- permission tree 中 membership 模块只出现 page / action 两组即可

### 3.3 浏览器只验证角色编辑弹窗

由于问题暴露点明确在 `/system/roles` 编辑弹窗，本轮浏览器复核只围绕这里：

- membership 权限是否仍出现在 unknown list
- membership 模块是否进入 tree

## 4. 风险与边界

### 4.1 已确认

- 本轮不需要恢复 membership 正式菜单
- 本轮不需要新增 membership 页面路由

### 4.2 当前边界

- 只改前端 registry / tree
- 不修改后端 controller
- 不修改运行库角色
