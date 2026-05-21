# 00-82 设计说明

## 1. 设计目标

`00-82` 只解决模板库列表视图表格区：

1. **row density**：表格行高与 header padding 收紧
2. **cell readability**：模板编码列与文本层级更稳定
3. **action rail**：固定操作列更紧但仍可用

## 2. 已核实的事实

### 2.1 当前问题仍只在 `TemplatesView.vue`

当前运行态截图与量化只覆盖：

- `content/templates` 列表视图

因此本轮继续只改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\content\TemplatesView.vue`

### 2.2 当前已有运行态量化

通过真实浏览器已核实：

- 列表首行高度约 `77px`
- 操作区宽度约 `236px`

这已经足够证明表格区还存在进一步压缩空间。

## 3. 设计策略

### 3.1 只加本地 class

为列表卡和列表表格增加本地 class，例如：

- `template-table-card`
- `template-table`

以保证改动不外溢到 gallery 或其他页面。

### 3.2 header / row

本轮收紧：

- card body 顶底 padding
- table header margin / hint 行高
- th / td padding
- cell 行高

### 3.3 编码列与操作区

模板编码当前容易断行，本轮允许：

- 增大编码列最小宽度
- 或对编码列使用更稳定的 no-wrap/mono 表达

固定操作列当前过宽，本轮允许：

- 收窄 `min-width`
- 收紧 `.table-actions` gap
- 适当收紧 link button 字号

但仍需保持按钮可点击与文案可读。

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及列表视图表格区
- 不影响真实模板动作能力
- 风险低、可逆

### 4.2 待验证

- 编码列收紧后是否仍避免断行
- 操作列收窄后是否仍不挤压正文

因此本轮必须结合：

- 运行态量化
- 浏览器截图

一起验证。
