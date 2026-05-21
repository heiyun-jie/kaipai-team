# 00-124 设计说明

## 1. 设计目标

`00-124` 只处理一个问题：

1. 把后端真实存在的 content 页面 / 动作权限补齐到前端 permission registry，消除角色编辑弹窗中的 content unknown 权限误报

## 2. 已核实事实

### 2.1 剩余 unknown 中的 content 权限都是真实合同

当前已确认：

- `AdminContentController.java` 真实消费了：
  - `page.content.publish-logs`
  - `page.content.theme-tokens`
  - `page.content.share-artifacts`
  - `action.content.theme.edit`
  - `action.content.artifact.edit`
  - `action.content.template.enable`
  - `action.content.template.disable`
  - `action.content.template.sort`

因此：

- 这批权限不应继续待在 unknown list 中

### 2.2 前端已有真实使用点

当前已确认：

- `TemplatesView.vue` 已直接使用：
  - `action.content.template.enable`
  - `action.content.template.disable`

因此：

- 本轮不仅要补 registry
- 还应按最小范围收口已真实使用的 content 权限常量

### 2.3 `menu.recruit` 不属于本轮

当前剩余 unknown 中仍有：

- `menu.recruit`

但当前它属于“历史菜单登记是否继续保留”的单独问题，不应和 content 真实权限 registry 对齐绑在一起。

## 3. 设计策略

### 3.1 补齐 registry

本轮在 `permission-registry.ts` 中补齐：

- content 页面权限标签
- content 动作权限标签

### 3.2 最小补齐常量

本轮在 `permission.ts` 中按最小范围补齐：

- `page.content.publish-logs`
- `page.content.share-artifacts`
- `page.content.theme-tokens`
- `action.content.artifact.edit`
- `action.content.template.enable`
- `action.content.template.disable`
- `action.content.template.sort`
- `action.content.theme.edit`

并只在当前已经直接使用裸字符串的页面里改成常量引用。

### 3.3 浏览器验证

继续只复核 `/system/roles` 编辑弹窗：

- unknown list 中不再出现上述 content 权限
- unknown 总量进一步下降

## 4. 风险与边界

### 4.1 已确认

- 本轮不涉及后端变更
- 本轮不涉及新页面开发

### 4.2 当前边界

- 只改前端权限合同层
- `menu.recruit` 留给下一条独立切片

## 5. 已完成验证补充

本轮已再次核实：

- `/system/roles` 编辑弹窗中的 unknown list 已不再包含 content 权限
- unknown 总量已从 `9` 进一步降到 `1`
- 当前仅剩：
  - `menu.recruit`
