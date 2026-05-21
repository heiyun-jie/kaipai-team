# 00-103 设计说明

## 1. 设计目标

`00-103` 只解决 `system/roles` 底部 `角色清单` 的表格密度：

1. **header density**：收紧 `ROLE DIRECTORY / 角色目录` 的 header 节奏
2. **row density**：压低首行高度与 cell padding
3. **cell hierarchy**：收紧权限概览 stacked cell
4. **action column**：让 fixed 操作列和分页区更轻

## 2. 已核实的事实

### 2.1 当前问题已收窄到底部角色清单

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-103\roles-directory-before.png`

当前量化：

- role directory card：`1134 × 323`
- table header：`1084 × 53`
- 首个表格行：`1380 × 81`
- 权限概览 stacked cell：`196 × 50`
- 操作区：`256 × 28`
- fixed 操作列：`280 × 81`
- pager：`1084 × 49`

这说明当前 residual 不再是前两张矩阵，而是底部角色目录的局部 table-density 问题。

### 2.2 当前厚度主要来自三处

1. `角色清单` 仍使用默认 table card 与 header 节奏
2. 权限概览 stacked cell 沿用较松的主副文本间距
3. fixed 操作列仍保持较宽较高的 link action 组合

### 2.3 事实源边界不能被打破

当前真实来源仍包括：

- `/system/roles`
- 角色列表接口

因此本轮不能：

- 改角色模型
- 改权限模型
- 改分页行为和动作语义

## 3. 设计策略

### 3.1 为角色清单卡和表增加本地 class

为底部目录增加：

- `roles-directory-card`
- `roles-directory-table`
- `roles-directory-pager`

所有样式收口都通过本地 class 限定，避免影响前两张矩阵。

### 3.2 header 和表格密度同步收紧

本轮收紧：

- `table-header`
- `table-header__eyebrow`
- `table-header h3`
- `table-header__hint`
- `th.el-table__cell`
- `td.el-table__cell`
- `.cell`

目标：

- header 更轻
- 首个表格行明显下降

### 3.3 权限概览和操作列

本轮收紧：

- `.stack-cell`
- `.table-actions`
- link button 高度 / 字号 / 行高
- fixed 操作列最小宽度

目标：

- 权限概览更紧，不再主导行高
- 操作区仍保持单行，不发生遮挡或换行

### 3.4 pager

本轮收紧：

- pager 顶部间距
- pagination 垂直节奏

目标：

- 保持现有单行分页结构
- 降低 card 尾部占高

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及底部 `角色清单`
- 不影响前两张矩阵
- 不影响详情、编辑、复制和启停用动作语义

### 4.2 待验证

- 操作列收紧后是否仍单行可点
- fixed 列是否会与更新时间列重新出现遮挡
- pager 收紧后是否仍对齐

因此本轮必须结合：

- 运行态量化
- 浏览器截图
- `type-check / build`

一起验证。
