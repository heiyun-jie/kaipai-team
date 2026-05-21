# 00-90 设计说明

## 1. 设计目标

`00-90` 只解决 `dashboard/analytics` 默认 `渠道分析` 首屏：

1. **tabs strip**：把 tabs 壳层收口为更轻的切换条
2. **channel board**：把左侧厚表格收口为更接近 reference 的 ledger / progress board
3. **mix compactness**：把右侧 donut + legend + insight 收成更紧凑的统计卡

## 2. 已核实的事实

### 2.1 当前问题集中在默认 `channel` tab 的首屏结构

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-90\analytics-current-authenticated.png`
- reference：`D:\XM\kaipai-team\output\playwright\00-90\analytics-reference.png`

当前量化：

- tabs shell：`488 × 94`
- 左表：`621 × 283`
- 右卡：`447 × 571`

当前问题不是接口断裂，而是 page-level 首屏结构和信息密度问题。

### 2.2 reference 的核心语义

reference 已确认：

- 顶部是轻量 tabs strip
- 首屏核心是左侧渠道表现 + 右侧流量构成
- 左侧更像 ledger + progress 的分析板
- 右侧 donut 卡高度更紧，洞察区更短

### 2.3 事实源边界不能被打破

当前 `DashboardAnalyticsView.vue` 真实来源为：

- `/admin/dashboard/overview`

当前可用的真实字段只覆盖：

- `shareViewCount`
- `convertedViewerCount`
- `classicSceneViewCount`
- `urbanSceneViewCount`
- `costumeSceneViewCount`

因此本轮不能伪造：

- 微信好友 / 朋友圈 / 企业微信真实渠道
- reference 原型里的高体量渠道数字
- 独立渠道转化接口

## 3. 设计策略

### 3.1 tabs strip 收紧

不改 tabs 逻辑，只改默认壳层：

- 收紧 `analytics-toolbar-card`
- 收紧 `analytics-tabs`
- 收紧 `analytics-tab`

让 tabs 更像 reference 的分析切换条，而不是厚工具卡。

### 3.2 左侧 channel 区改为 ledger / board

保留 `channelRows` 数据，但不再使用 `el-table`。

改为：

- 渠道列
- 分享访问列
- 查看后成卡列
- 成卡占比 progress 列

这样既不伪造事实，又能更接近 reference 的统计面板表达。

### 3.3 右侧 mix 区压缩

保留：

- donut
- legend
- insight

但会：

- 缩短 header hint
- 缩短 insight 文案
- 收紧 chart / legend / note 之间的间距
- 避免右卡高度继续把左卡拉出大块空白

### 3.4 高度关系修复

当前最关键的一手是：

- 让 `analytics-grid` 不再默认 stretch 子卡高度

否则左卡即便内容收紧，仍会被右卡高度拉伸，继续产生首屏空白。

## 4. 风险与边界

### 4.1 已确认

- 这是 `DashboardAnalyticsView.vue` 默认首屏结构问题
- 不需要新增接口
- 不应伪造成熟渠道系统

### 4.2 待验证

- ledger / progress board 是否比 `el-table` 更接近 reference 且仍清晰可读
- 右侧 donut 卡压缩后是否还能保持可读
- tabs strip 收紧后是否仍有足够可点击面积

因此本轮必须结合：

- 浏览器截图
- 运行态量化
- `type-check / build`

一起验证。
