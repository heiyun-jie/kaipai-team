# 后台账号角色绑定联动校验 - 技术设计

_Requirements: 00-13 全部_

## 1. 设计目标

让后台账号页在“角色目录不可读”和“已绑定禁用角色”两类场景下都能按真实后端契约工作，避免静默失败和错误提交。

## 2. 契约基线

后端契约已确认：

1. `GET /admin/system/roles` 需要 `page.system.roles`
2. `POST /admin/system/admin-users/{id}/bind-roles` 需要 `action.system.admin-user.bind-roles`
3. `bind-roles` 与 `create user` 的 `roleCodes` 最终都走服务端 `loadActiveRoles`，只接受启用角色

因此前端必须区分：

- “是否有权限执行绑定动作”
- “是否有权限读取角色目录”

## 3. 页面策略

### 3.1 角色目录读取状态

引入两个布尔状态：

- `canReadRoleCatalog`
- `canOperateRoleBinding`

当 `canReadRoleCatalog = false` 时：

- 不请求角色列表
- 保持角色选项为空
- 在创建账号和绑定角色弹窗中展示明确说明
- 角色选择器禁用

### 3.2 禁用角色处理

`currentRow.roles` 或详情数据中若存在 `status !== 1` 的角色，视为“禁用角色绑定”。

绑定弹窗打开时：

- 可编辑选中项只保留当前启用角色的 `roleCode`
- 单独展示禁用角色列表
- 提示本次保存会移除这些禁用角色，因为后端不接受其继续提交

提交时：

- 仅提交可编辑选择器中的启用角色编码

## 4. 组件与交互

优先在现有 `AdminUsersView.vue` 内实现，不新增复杂通用组件。

建议 UI：

- `el-alert` 展示角色目录依赖说明
- `el-alert` 展示禁用角色移除提示
- `el-select` 在角色目录不可读时禁用

## 5. 验证方式

1. 模拟无 `page.system.roles` 时，创建账号 / 绑定角色弹窗可见说明且选择器禁用
2. 模拟账号含禁用角色时，绑定弹窗能显示风险提示
3. 提交 payload 不再包含禁用角色编码
4. 运行 `npm run type-check`
5. 运行 `npm run build`
