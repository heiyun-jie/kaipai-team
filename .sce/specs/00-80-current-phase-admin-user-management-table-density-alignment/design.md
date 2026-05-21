# 00-80 设计说明

## 1. 设计目标

`00-80` 只解决 `users/index` 表格区：

1. **row density**：行高与 cell padding 收紧
2. **cell hierarchy**：用户 / stacked cell 信息层级更紧
3. **fixed action column**：固定操作列更轻

## 2. 已核实的事实

### 2.1 当前问题仍然只在 `UserCenterView.vue`

已核实：

- 证据只覆盖 `users/index`
- 当前问题不需要回到共享样式

因此本轮仍只改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\user\UserCenterView.vue`

### 2.2 当前已有运行态量化

通过真实浏览器已核实：

- 首行高度约为 `81px`
- 固定操作列单元格宽度约为 `120px`

这足够说明本轮表格区仍可继续压缩。

## 3. 设计策略

### 3.1 主表卡局部覆盖

继续依赖 `user-table-card`，只在用户页内补局部样式：

- table header padding
- table row padding
- pager 间距

### 3.2 单元格层级

为以下本地结构补齐样式：

- `.user-cell`
- `.user-avatar`
- `.user-cell__copy`
- `.stack-cell`

目标：

- 头像略缩
- 主副文本更紧
- stacked cell 的 strong / span 层级清晰但不松散

### 3.3 固定操作列

当前操作列最小宽度为 `120px`，本轮允许：

- 适度收窄列宽
- 适度收紧 fixed-right 背景壳层观感

但：

- 不改成图标按钮
- 不缩到影响点击和可读

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及表格展示密度
- 不影响真实业务数据与详情链路
- 风险低、可逆

### 4.2 待验证

- 行高压缩后是否仍足够可读
- 固定列收窄后是否仍不遮挡正文

因此本轮必须同时做：

- 运行态量化
- 浏览器截图复核
