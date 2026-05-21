# 00-125 设计说明

## 1. 设计目标

`00-125` 只处理一个问题：

1. 把 `menu.recruit` 从“最后一条 unknown”收口为“历史菜单登记可见项”

## 2. 已核实事实

### 2.1 `menu.recruit` 当前不参与 runtime 放通

当前已确认：

- `adminMenus.recruit` 没有 `menuPermission`
- 招募路由和后端 controller 全都按 `page.recruit.* / action.recruit.*` 放通

因此：

- `menu.recruit` 不能被重新解释成运行时必需权限

### 2.2 `menu.recruit` 当前仍是历史角色数据的一部分

当前已确认：

- 运行库 `ADMIN` 角色仍携带 `menu.recruit`
- 角色矩阵与角色编辑提示仍展示：
  - `hasRecruitMenu`
  - `历史 menu.recruit`

因此：

- 当前立即删运行库数据不是最小切片
- 更合理的是先把它纳入 registry，保证展示和编辑一致

## 3. 设计策略

### 3.1 只补历史菜单登记

本轮在 `permission-registry.ts` 中新增一条 recruit 历史菜单登记：

- `menu.recruit`

文案显式带“历史”语义。

### 3.2 不改变 tree 分组来源

由于 `moduleOrder` 已包含 `recruit`，只要 `menu.recruit` 进入 registry，就会自动进入 recruit 模块下的菜单组。

### 3.3 浏览器只验证角色编辑弹窗

本轮复核目标：

- unknown list 是否归零
- recruit 模块中是否出现历史菜单登记项

## 5. 已完成验证补充

本轮已再次核实：

- `/system/roles` 编辑弹窗中的 unknown list 已归零
- recruit 模块当前仍保留 `历史 menu.recruit` 展示
- 本轮未改变招募 runtime 放通边界

## 4. 风险与边界

### 4.1 已确认

- 本轮不涉及数据库变更
- 本轮不涉及后端鉴权逻辑

### 4.2 当前边界

- 只改前端 registry / tree 展示层
- 若后续要真正移除运行库角色中的 `menu.recruit`，需另起切片
