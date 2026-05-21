# 00-92 设计说明

## 1. 设计目标

`00-92` 只解决 `dashboard/analytics` 的 `funnel` tab：

1. **single board**：把当前双栏结构收口为单张全宽漏斗板
2. **wide tracks**：增强漏斗横向进度条表达，更接近 reference 的全宽 funnel
3. **inline insight**：把当前右侧解读卡收为底部内联摘要

## 2. 已核实的事实

### 2.1 当前问题集中在双栏结构

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-92\analytics-funnel-current.png`
- reference：`D:\XM\kaipai-team\output\playwright\00-92\analytics-funnel-reference.png`

当前量化：

- 第一张漏斗卡：`671 × 366`
- 第二张解读卡：`447 × 434`
- `funnel-board`：`621 × 246`
- 首个 `funnel-board__row`：`621 × 38`
- `analytics-insight--stack`：`397 × 266`

当前问题是 page-level 首屏结构问题：

- reference 是单张全宽漏斗板
- 当前是左漏斗 + 右解读卡

### 2.2 reference 的核心语义

reference 已确认：

- 顶部是 tabs strip
- 主体是一张全宽 `CREATE FUNNEL` 漏斗板
- 每行横向进度条占据主要视觉空间
- 比例标签内联在行末，不再拆成右侧说明卡

### 2.3 事实源边界不能被打破

当前 `funnel` tab 真实可用来源仍只有：

- `/admin/dashboard/overview`

当前可用的真实字段包括：

- `shareViewCount`
- `uniqueViewerCount`
- `convertedViewerCount`
- `pendingContactRequestCount`
- `approvedContactRequestCount`

因此本轮不能伪造：

- 首页曝光
- 点击创建分享
- 选择风格
- 上传素材
- 完成生成
- 首次分享 / 二次分享

## 3. 设计策略

### 3.1 双栏改单板

把当前：

- 左侧 `funnel-board`
- 右侧 `analytics-insight--stack`

合并为单张：

- `analytics-card--funnel`

让首屏只呈现一张完整漏斗板。

### 3.2 宽轨道漏斗表达

保留 `funnelRows` 数据，但把行布局改为：

- 步骤编号
- 阶段文案
- 全宽 track
- 当前值与比例

增强横向进度关系。

### 3.3 解读内联

把：

- 查看后成卡率
- 联系方式通过率
- funnelInsight

收口到漏斗板底部 `funnel-summary`。

### 3.4 风险控制

- 不改 tabs 逻辑
- 不动其他三个 tab
- 不改接口
- 只重组模板和局部样式

## 4. 风险与边界

### 4.1 已确认

- 这是 `DashboardAnalyticsView.vue` funnel tab 的 page-level 问题
- 不需要新增接口
- 不应伪造 reference 的完整创建流程漏斗

### 4.2 待验证

- 单张漏斗板是否比当前双栏结构更接近 reference
- 宽进度条是否保持可读
- 内联解读是否足够表达真实事实边界

因此本轮必须结合：

- 浏览器截图
- 运行态量化
- `type-check / build`

一起验证。
