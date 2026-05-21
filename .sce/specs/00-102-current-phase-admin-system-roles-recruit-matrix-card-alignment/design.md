# 00-102 设计说明

## 1. 设计目标

`00-102` 只解决 `system/roles` 第二张 `招募治理授权矩阵` 卡片的密度问题：

1. **card shell**：收紧 card header / body、alert 和 table 进入关系
2. **row density**：压低首行高度与 cell padding
3. **tag strategy**：让权限覆盖与待补权限标签不再主导整行高度
4. **action stability**：保持 `查看详情 / 补权限` 的动作语义不变

## 2. 已核实的事实

### 2.1 当前问题已从首张 AI 矩阵转到第二张招募矩阵

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-102\roles-recruit-matrix-before.png`

当前量化：

- second card：`1134 × 567`
- 首个矩阵行：`1500 × 213`
- 角色 stacked cell：`196 × 50`
- 权限覆盖 tag list：`396 × 106`
- 待补权限 tag list：`296 × 182`
- 操作区：`146 × 28`

这说明当前 residual 不再是整页 IA 或首屏结构问题，而是第二张矩阵卡的局部 density 问题。

### 2.2 当前厚度主要来自三处

1. 第二张矩阵卡仍走默认 `el-card` header / body padding
2. 招募矩阵表格未接入首张 AI 矩阵的局部 table density 规则
3. 待补权限直接复用 `getPermissionDisplayText` 的长文案，导致 5 个标签被堆成约 `182px` 的高列

### 2.3 事实源边界不能被打破

当前真实来源仍包括：

- `/system/roles`
- 招募治理授权矩阵接口

因此本轮不能：

- 改角色模型
- 改权限模型
- 改招募矩阵字段语义

## 3. 设计策略

### 3.1 为第二张招募矩阵增加本地 class

为第二张矩阵卡和表分别增加：

- `roles-recruit-matrix-card`
- `roles-recruit-matrix-table`

所有卡片和表格密度收口通过这两个 class 限定，避免影响底部 `角色清单`。

### 3.2 复用首张矩阵的 card shell 密度

第二张矩阵卡收紧：

- `el-card__header`
- `el-card__body`
- `el-alert`

目标：

- 让第二张矩阵卡与首张 AI 矩阵在 card shell 上对称
- 让角色清单更早进入页面

### 3.3 表格行高与标签收紧

第二张矩阵表收紧：

- `th.el-table__cell`
- `td.el-table__cell`
- `.cell`
- `.stack-cell`
- `.tag-list`
- `.el-tag`
- `.table-actions`

目标：

- 首个矩阵行明显降高
- 权限覆盖与待补权限标签不再成为表格主高度来源

### 3.4 待补权限使用页面内紧凑标签文案

第二张矩阵的待补权限标签改为页面内紧凑表达：

- `page.recruit.projects` -> `剧组项目页`
- `page.recruit.roles` -> `招募角色页`
- `page.recruit.applies` -> `投递记录页`
- `action.recruit.project.status` -> `项目处置`
- `action.recruit.role.status` -> `角色处置`

只在矩阵视图内使用该映射；未命中的权限仍回退到 `getPermissionDisplayText`。

这样做的原因是：

- 当前卡片的目标是展示 ready / missing 的治理态势
- 全量权限码已在角色详情和权限树中保留
- 只要页面内语义仍可追溯，就没有必要让矩阵首屏承受过长标签的布局成本

### 3.5 运行态顺手修复同文件点击错误

在真实浏览器验证中，首张 AI 矩阵的 `补权限` 按钮会把整行对象传给 `openEditFromMatrix(id)`，导致：

- 请求路径命中 `/api/admin/system/roles/[object Object]`
- 返回 `400`

该问题与当前卡片验证处于同一文件、同一路径，且修复只需把参数改为 `row.adminRoleId`，因此一并收口。

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及 `RolesView.vue`
- 第二张矩阵的视觉收口不会影响底部角色清单
- 紧凑标签只作用于第二张矩阵的待补权限视图

### 4.2 待验证

- 标签收紧后是否仍可读
- 操作列收紧后是否仍可点击
- 第二张矩阵卡高度是否实际下降
- 首张 AI 矩阵 `补权限` 是否可正常打开编辑弹窗

因此本轮必须结合：

- 运行态量化
- 浏览器截图
- `type-check / build`

一起验证。
