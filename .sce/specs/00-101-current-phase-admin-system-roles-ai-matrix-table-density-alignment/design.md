# 00-101 设计说明

## 1. 设计目标

`00-101` 只解决 `system/roles` 首张 AI 授权矩阵的表格密度：

1. **row density**：压低首行高度与 cell padding
2. **cell hierarchy**：收紧角色 stacked cell 与权限 tag list 层级
3. **action column**：让固定操作列更轻

## 2. 已核实的事实

### 2.1 当前问题已从首屏结构转到首张矩阵表格区

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-101\roles-ai-matrix-before.png`

当前量化：

- 首个矩阵行：`1420 × 99`
- 角色 stacked cell：`196 × 50`
- 权限覆盖 tag list：`336 × 68`
- 待补权限 tag list：`276 × 23`
- 操作区：`146 × 28`

这说明当前 residual 不再是 shell 或 summary 问题，而是表格局部密度问题。

### 2.2 当前厚度主要来自三处

1. matrix table 继续使用共享表格 padding
2. 角色 stacked cell 主副文本纵向节奏偏松
3. 权限覆盖 tag list 换行后高度约 `68px`，成为首行高度主要来源

### 2.3 事实源边界不能被打破

当前真实来源仍包括：

- `/system/roles`
- AI 授权矩阵接口

因此本轮不能：

- 改角色模型
- 改权限模型
- 改 AI 矩阵字段语义

## 3. 设计策略

### 3.1 为首张 AI 矩阵表增加本地 class

为第一张矩阵表增加：

- `roles-ai-matrix-table`

所有表格密度收口通过该 class 限定，避免影响第二张招募矩阵和底部角色清单。

### 3.2 表格行高与单元格收紧

本轮收紧：

- `th.el-table__cell`
- `td.el-table__cell`
- `.cell`
- `.stack-cell`

目标：

- 首行高度明显下降
- 角色主副信息更紧

### 3.3 tag list 与操作列

本轮收紧：

- `.tag-list`
- `.el-tag`
- `.table-actions`
- link button 高度与字号

同时适度给 `权限覆盖` 列更稳定的宽度，让 4 个常用标签尽量减少换行占高。

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及首张 AI 授权矩阵表格区
- 不影响第二张招募矩阵和底部角色清单
- 不影响详情与补权限动作

### 4.2 待验证

- tag 收紧后是否仍可读
- 操作列收紧后是否仍可点击
- 首行高度是否实际下降

因此本轮必须结合：

- 运行态量化
- 浏览器截图
- `type-check / build`

一起验证。
