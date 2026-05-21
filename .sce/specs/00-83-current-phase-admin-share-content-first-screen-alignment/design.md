# 00-83 设计说明

## 1. 设计目标

`00-83` 只解决 `content/share-cards` 默认卡片墙首屏：

1. **shell density**：顶部 tabs、切换、汇总卡、筛选区更紧
2. **card proportion**：内容卡封面与卡体比例更接近 reference
3. **grid density**：多卡并列时首屏可见信息量提升

## 2. 已核实的事实

### 2.1 当前问题仍只在 `ShareCardsView.vue`

最新运行态截图已确认：

- 默认分享内容页的 shell / filter / gallery 是当前主要问题来源
- 暂时不需要回到全局样式或其他页面

因此本轮只改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\content\ShareCardsView.vue`

### 2.2 当前列表视图与详情抽屉不应混入

当前已有：

- 列表视图：治理排查兜底
- 详情抽屉：真实内容详情 carrier
- legacy 修复动作：底部治理补充区

这些都不是当前首屏最主要的视觉瓶颈，所以本轮不碰。

## 3. 设计策略

### 3.1 shell 区

对 `content-shell-card` 做首屏密度压缩：

- toolbar gap 收紧
- tab / view button 高度收紧
- stats gap 与 padding 收紧

### 3.2 filter 区

与模板页做法一致，不改全局 `FilterPanel.vue`，只给分享内容页局部 class 覆盖：

- body padding 收紧
- header / form gap 收紧
- 控件高度收紧

### 3.3 gallery 区

当前内容卡：

- cover 偏高
- body gap 偏大
- 多卡并列时首屏纵向密度不足

本轮改为：

- 降低 cover 高度
- 收紧 body、summary、metrics、foot 的间距
- 将 grid 表达改成稳定卡宽的 auto-fit 上限

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及分享内容首屏密度
- 不影响真实分享卡详情与治理动作
- 风险低、可逆

### 4.2 待验证

- 卡片收紧后是否仍保持内容卡片墙的正式感
- 多卡样本下首屏可见信息量是否明显提升

因此本轮必须用真实浏览器 full-page 再复核一次。
