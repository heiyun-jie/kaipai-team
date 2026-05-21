# 00-93 设计说明

## 1. 设计目标

`00-93` 只解决 `dashboard/analytics` 的 `segment` tab：

1. **single board**：把当前双栏结构收口为单张全宽分群板
2. **3x2 grid**：把当前近似分群卡扩成 reference 风格 3×2 阵列
3. **inline boundary**：把当前右侧大说明盒收为板内边界说明

## 2. 已核实的事实

### 2.1 当前问题集中在布局宽度和说明卡

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-93\analytics-segment-current.png`
- reference：`D:\XM\kaipai-team\output\playwright\00-93\analytics-segment-reference.png`

当前量化：

- 第一张卡：`559 × 447`
- 第二张说明卡：`559 × 344`
- `segment-grid`：`509 × 315`
- 首张 `segment-card`：`160 × 140`
- `analytics-insight--spacious`：`509 × 220`

当前问题是 page-level 首屏结构问题：

- reference 是全宽分群卡阵列
- 当前是左卡 + 右说明盒

### 2.2 reference 的核心语义

reference 已确认：

- 顶部仍是 tabs strip
- 主体是一张分群板
- 板内是 6 张分群卡
- 每张卡有标签、标题、简短说明、人数和 CTA

### 2.3 事实源边界不能被打破

当前 `segment` tab 真实可用来源仍只有：

- `/admin/dashboard/overview`

当前可用的真实字段包括：

- `activeShareOwnerCount`
- `uniqueViewerCount`
- `convertedViewerCount`
- `approvedContactRequestCount`
- `pendingContactRequestCount`
- `todayPaymentOrderCount`

因此本轮不能伪造：

- VIP 机构用户
- 沉睡机构用户
- 传播达人
- 新注册活跃
- 回流用户
- 创作停滞

这些 reference 卡名只能被“当前主链近似分群”所替代，不能直接照搬为真实业务事实。

## 3. 设计策略

### 3.1 双栏改单板

把当前：

- 左侧 `segment-grid`
- 右侧 `analytics-insight--spacious`

合并为单张：

- `analytics-card--segment`

让首屏直接进入完整分群板。

### 3.2 卡阵列升级

保留 `segmentRows` 数据，但扩成更接近 reference 的卡阵列：

- 分群标签 badge
- 分群标题
- 简短说明
- 当前人数
- CTA 行

### 3.3 边界说明内联

将原来的右侧说明盒压到分群板底部，明确：

- 当前是主链近似分群
- 真实用户标签 / 来源 / 机构归属 / 活跃等级仍待后续补齐

### 3.4 风险控制

- 不改 tabs 逻辑
- 不动其他三个 tab
- 不改接口
- 只重组模板和局部样式

## 4. 风险与边界

### 4.1 已确认

- 这是 `DashboardAnalyticsView.vue` segment tab 的 page-level 问题
- 不需要新增接口
- 不应伪造成熟用户画像系统

### 4.2 待验证

- 单张分群板是否比当前双栏结构更接近 reference
- 3×2 卡阵列是否仍清晰可读
- 内联边界说明是否足够表达事实限制

因此本轮必须结合：

- 浏览器截图
- 运行态量化
- `type-check / build`

一起验证。
