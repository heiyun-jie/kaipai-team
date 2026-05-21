# 00-107 设计说明

## 1. 设计目标

`00-107` 只解决 `system/roles` 创建 / 编辑弹窗中的权限编排区密度：

1. **permission-stack density**：压低 alert、权限包卡片和内部 gap
2. **editor density**：压低 `PermissionTreeEditor` 的 toolbar、tags 和 unknown-list
3. **tree density**：压低 `permission-tree` padding、node height 和 code 展示

## 2. 已核实的事实

### 2.1 当前残余已收窄到权限编排区内部

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-107\roles-permission-tree-before.png`

当前量化：

- `权限编排` form item：`782 × 1000`
- permission editor：`782 × 424`
- toolbar：`782 × 86`
- alerts：`84 / 84`
- bundle cards：`172 / 172 / 172 / 172`
- tree：`782 × 328`
- first node：`756 × 34`

这说明当前残余已不在 dialog shell，而在权限编排区内部节奏。

### 2.2 当前组件使用边界已核实

`PermissionTreeEditor.vue` 当前只在：

- `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue`

中被使用。

因此本轮可以直接改组件，而不会误伤其它页面。

## 3. 设计策略

### 3.1 RolesView.vue

本轮继续收紧：

- `.permission-stack`
- `.permission-stack .el-alert`
- `.ai-governance-bundle-grid`
- `.ai-governance-bundle-card`
- `.bundle-actions`

### 3.2 PermissionTreeEditor.vue

本轮收紧：

- `.permission-editor`
- `.toolbar`
- `.toolbar-actions`
- `.unknown-list`
- `.permission-tree`
- `.tree-node`
- `el-tree-node__content`

并为：

- toolbar tags
- unknown-list tags
- tree node code

继续使用更轻的密度。

### 3.3 不做的事

本轮不改：

- 权限树数据模型
- filter / expand / collapse 逻辑
- 未知权限保留逻辑
- 复制弹窗结构

## 4. 风险与边界

### 4.1 已确认

- 当前改动只影响 `system/roles` 创建 / 编辑弹窗中的权限编排区
- `PermissionTreeEditor` 当前无其它使用方
- 风险低、可逆

### 4.2 待验证

- tree node 更紧后是否仍容易点击
- toolbar 更紧后是否仍单行可读
- 权限编排区高度是否实际下降

因此本轮必须结合：

- 运行态量化
- 浏览器截图
- `type-check / build`

一起验证。
