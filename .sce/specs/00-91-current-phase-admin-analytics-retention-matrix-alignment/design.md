# 00-91 设计说明

## 1. 设计目标

`00-91` 只解决 `dashboard/analytics` 的 `retention` tab：

1. **single board**：把当前双卡结构收口为单张 retention matrix 板
2. **proxy matrix**：用当前真实 overview 字段构造“当前窗口代理矩阵”
3. **boundary note**：把当前右侧大说明盒压成矩阵内联边界说明

## 2. 已核实的事实

### 2.1 当前问题集中在结构而不是接口断裂

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-91\analytics-retention-current.png`
- reference：`D:\XM\kaipai-team\output\playwright\00-91\analytics-retention-reference-clicked.png`

当前量化：

- 第一张 retention 卡：`559 × 456`
- 第二张说明卡：`559 × 344`
- `retention-grid`：`509 × 336`
- 首张 retention-card：`160 × 161`
- `analytics-insight--spacious`：`509 × 220`

当前问题是 page-level 首屏结构问题：

- reference 是单板矩阵
- 当前是多卡片 + 大说明盒

### 2.2 reference 的核心语义

reference 已确认：

- 顶部是 tabs strip
- 主体是一张 retention matrix
- 重点在“矩阵承接”，不是多张摘要卡

### 2.3 事实源边界不能被打破

当前 `retention` tab 真实可用来源仍只有：

- `/admin/dashboard/overview`

当前可用的真实字段包括：

- `activeShareCardCount`
- `activeShareOwnerCount`
- `shareViewCount`
- `uniqueViewerCount`
- `convertedViewerCount`
- `approvedContactRequestCount`
- `pendingContactRequestCount`
- `refundPendingCount`
- `verifyPendingCount`

因此本轮不能伪造：

- `W-7 ~ W-1` 周 cohort
- `D1 / D7 / D14 / D30` 连续留存率
- 真正的 cohort line / heatmap 时间序列

## 3. 设计策略

### 3.1 双卡改单板

把当前：

- 左侧 `retention-grid`
- 右侧 `analytics-insight--spacious`

合并为单张：

- `retention-matrix-card`

让首屏先进入 retention 核心板。

### 3.2 代理矩阵表达

保留真实字段，但改表达方式：

- 行：真实代理指标
  - 活跃分享卡
  - 持卡用户
  - 分享访问
  - 唯一访客
  - 查看后成卡
  - 已同意联系
- 列：
  - 当前值
  - 对持卡用户占比
  - 对分享访问占比
  - 代理说明

再用热度深浅 / 进度块把它收口为更接近 reference 的矩阵感。

### 3.3 治理边界内联

把治理说明压进矩阵底部一条内联 note：

- 当前无 D1 / D7 / cohort 事实
- 退款待处理 / 实名待审只作为治理旁路，不并入正式 retention 矩阵

### 3.4 风险控制

- 不改 tabs 逻辑
- 不动其他三个 tab
- 不改接口
- 只重组模板和局部样式

## 4. 风险与边界

### 4.1 已确认

- 这是 `DashboardAnalyticsView.vue` retention tab 的 page-level 问题
- 不需要新增接口
- 不应伪造成熟留存系统

### 4.2 待验证

- 单张代理矩阵板是否比当前多卡结构更接近 reference
- 指标解释是否仍清晰可读
- 内联边界说明是否足够表达事实限制

因此本轮必须结合：

- 浏览器截图
- 运行态量化
- `type-check / build`

一起验证。
