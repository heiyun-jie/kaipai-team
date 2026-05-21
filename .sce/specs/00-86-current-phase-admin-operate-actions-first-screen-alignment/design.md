# 00-86 设计说明

## 1. 设计目标

`00-86` 只解决 `operate/actions` 首屏：

1. **toolbar density**：工具卡更轻
2. **action-first**：动作推荐成为首屏第一语义
3. **overview demotion**：overview 卡降为辅助层

## 2. 已核实的事实

### 2.1 reference 与当前运行态差异明确

reference：

- `D:\XM\kaipai-team\output\playwright\00-86\operate-actions-reference.png`

当前运行态：

- `D:\XM\kaipai-team\output\playwright\00-86\operate-actions-before.png`

当前浏览器量化：

- toolbar 高度：`192px`
- overview 卡：`367 × 161`，且首屏为 `3 + 1` 断行
- 首个动作卡顶部：约 `y=674`
- `action-recommendation`：约 `1134 × 147`
- 下方最近治理动态标题顶部：约 `y=1514`

### 2.2 当前不能照搬 campaign 模型

reference 的 `RECENT CAMPAIGNS` 是概念原型。当前运行态只能继续认：

- `fetchDashboardOverview()`
- `fetchContentShareCardLegacySummary()`
- 真实治理入口路由

因此本轮只能借 reference 的结构层级与节奏，不能伪造活动数据。

## 3. 设计策略

### 3.1 动作推荐前置

把 `action-recommendations` 提升到 overview 之前，使首屏优先看到推荐动作，而不是先看到 4 张大概览卡。

### 3.2 overview 降级

overview 继续保留，但降为辅助摘要区：

- 卡片更紧
- 字号更轻
- 位置后置

### 3.3 动作卡局部收口

本轮只在 `ActionsView.vue` 局部收紧：

- 卡片 padding
- icon 尺寸
- 标题字号
- target / hint 字号
- side metric / button
- list gap

### 3.4 工具卡收口

顶部工具卡保留：

- 标题
- 时间范围
- 重置 / 刷新

但不再维持当前偏厚的壳层节奏。

## 4. 风险与边界

### 4.1 已确认

- 这是 `ActionsView.vue` 的首屏结构问题
- 不是共享壳层问题
- 不需要触碰其它页面

### 4.2 待验证

- 推荐动作前置后，首屏是否更接近 reference
- overview 后置后是否仍足够可读
- 动作卡收紧后按钮是否仍稳定可点击

因此本轮必须结合：

- 运行态量化
- 浏览器截图
- `type-check / build`

一起验证。
