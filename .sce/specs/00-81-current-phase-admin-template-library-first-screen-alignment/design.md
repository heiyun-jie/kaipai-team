# 00-81 设计说明

## 1. 设计目标

`00-81` 只解决 `content/templates` 默认模板库首屏：

1. **shell density**：顶部 tabs、切换、汇总卡、筛选区更紧
2. **card proportion**：模板卡片封面与卡体比例更接近 reference
3. **grid stability**：模板样本较少时仍保持稳定卡宽

## 2. 已核实的事实

### 2.1 当前问题仍只在 `TemplatesView.vue`

最新运行态截图已确认：

- 默认模板库页的 tabs / stats / filter / gallery 是本轮问题来源
- 当前无需回到共享样式或其他页面

因此本轮只改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\content\TemplatesView.vue`

### 2.2 当前列表视图与弹窗不应混入

当前已有：

- 列表视图：治理排查辅助
- 编辑 / 发布 / 回滚弹窗：真实能力 carrier

这些都不是模板库首屏当前最主要的视觉瓶颈，所以本轮不碰。

## 3. 设计策略

### 3.1 shell 区

对 `template-shell-card` 做首屏密度压缩：

- toolbar gap 收紧
- tab / view button 高度收紧
- stats gap 与 padding 收紧

### 3.2 filter 区

与用户页做法一致，不改全局 `FilterPanel.vue`，只给模板页局部 class 覆盖：

- body padding 收紧
- header / form gap 收紧
- 控件高度收紧

### 3.3 gallery 区

当前模板卡：

- cover 偏高
- body gap 偏大
- 卡片在少量样本时过宽或过空

本轮改为：

- 减少 cover 高度
- 收紧 body、summary、meta、actions 的间距
- 将 grid 改成稳定卡宽的 auto-fit/固定上限表达

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及模板库首屏密度
- 不影响真实模板动作能力
- 风险低、可逆

### 4.2 待验证

- 卡片收紧后是否仍保留模板库的正式感
- 少量模板样本下首屏是否仍有过多空白

因此本轮必须用真实浏览器 full-page 再复核一次。
