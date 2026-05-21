# 00-122 设计说明

## 1. 设计目标

`00-122` 只处理一个问题：

1. 当前前端权限 registry 中残留的 `menu.membership` 是否已成为 dead registry；若是，则最小退场

## 2. 已核实事实

### 2.1 `menu.membership` 当前只在前端 registry 残留

当前已确认：

- `permission-registry.ts` 仍保留 `legacyMenuRegistry`
- 后端 membership controller 只认：
  - `page.membership.*`
  - `action.membership.*`
- 当前本机运行库角色未携带 `menu.membership`

因此：

- `menu.membership` 当前更像历史菜单残留

### 2.2 阶段枚举清理暂不属于最小切片

当前后端 `AdminRoleServiceImpl.java` 仍会主动计算：

- `compat_transition`
- `fallback_only`
- `partial_ai`
- `partial_recruit`

因此：

- 阶段枚举若要继续清理，需要改动前后端合同
- 不适合与本轮 membership 历史菜单退场绑在一起

### 2.3 当前浏览器复核补充发现

本轮打开 `/system/roles` 的编辑弹窗时确认：

- `menu.membership` 已不是当前角色权限的一部分
- `page.membership.* / action.membership.*` 仍被列为“未登记权限”

因此：

- 本轮只删除 `menu.membership`
- 会员页面 / 动作权限是否需要重新纳入 permission tree，应另起后续 spec 处理

## 3. 设计策略

### 3.1 只删除 dead registry

本轮只处理：

- `permission-registry.ts` 中的 `legacyMenuRegistry`
- `permissionRegistry` 拼接里的该段残留

### 3.2 保持 membership 页面 / 动作权限不变

继续保留：

- `page.membership.*`
- `action.membership.*`

原因：

- 后端 controller 仍真实消费这些权限

### 3.3 最小验证

由于改的是权限 registry，浏览器 smoke 只需确认：

- `/system/roles` 可正常访问
- 权限编排区可正常渲染

## 4. 风险与边界

### 4.1 已确认

- `menu.membership` 当前不是后端鉴权必需项
- 当前本机运行库角色未携带该权限

### 4.2 当前边界

- 本轮不修正 membership 模块是否应该重新进入 permission tree
- 本轮只做 dead registry 退场
