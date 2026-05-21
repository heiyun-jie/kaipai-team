# 00-84 设计说明

## 1. 设计目标

`00-84` 只解决分享内容列表视图表格区：

1. **row density**：行高与 header padding 收紧
2. **stacked hierarchy**：stacked cell 主副文本更紧
3. **fixed action column**：固定操作列更轻

## 2. 已核实的事实

### 2.1 当前问题仍只在 `ShareCardsView.vue`

当前运行态主线与代码事实已经明确：

- `content/share-cards` 的主表达是 gallery
- 列表视图只是治理排查兜底

因此本轮继续只改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\content\ShareCardsView.vue`

### 2.2 当前详情抽屉与底部治理区不应混入

当前已有：

- 详情抽屉：真实内容详情 carrier
- 底部治理补充动作：legacy 修复入口

它们都不是当前列表视图表格区最主要的视觉瓶颈，所以本轮不碰。

## 3. 设计策略

### 3.1 只加本地 class

为列表卡和列表表格增加本地 class，例如：

- `content-table-card`
- `content-table`

以保证改动只作用于 share-cards 列表视图，不外溢到 gallery。

### 3.2 header / row

本轮收紧：

- card body 顶底 padding
- table header margin / hint 行高
- th / td padding
- cell 行高

### 3.3 stacked cell 与操作区

补本地样式：

- `.stack-cell`
  - strong / span 层级更清楚
  - gap、字号、行高收紧

固定操作列当前只保留 `查看详情`，本轮允许：

- 收窄 `min-width`
- 收紧 link button 字号
- 收轻 fixed-right 背景

但仍需保持按钮可点击与文案可读。

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及列表视图表格区
- 不影响真实分享卡详情与治理能力
- 风险低、可逆

### 4.2 待验证

- row density 收紧后是否仍足够可读
- fixed-right 收窄后是否不压正文

因此本轮必须结合：

- 运行态量化
- 浏览器截图

一起验证。
