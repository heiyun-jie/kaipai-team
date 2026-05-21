# 00-78 设计说明

## 1. 设计目标

`00-78` 只解决 dashboard 底部两块：

1. **page matrix ledger**：把 8 页矩阵从厚卡片收成更紧的 table-like ledger
2. **governance feed**：把治理动态收成更接近 reference 的 activity feed 结构

## 2. 已核实的事实

### 2.1 当前不能做真实 `TOP CONTENT`

此前已核实：

- 当前分享卡接口缺少稳定榜单排序事实
- 当前没有真实进入率 / 内容热度 / 稳定排序字段

因此 dashboard 左下块只能继续是：

- 正式页面矩阵的事实入口

不能伪装成：

- reference 的真实 `TOP CONTENT` 榜单

### 2.2 当前问题仍只在 `OverviewView.vue`

最新证据：

- `D:\XM\kaipai-team\output\playwright\00-77\dashboard-index-secondary-full.png`

已确认：

- 中上区块已较稳定
- 剩余差异主要在底部两块的密度与结构语义
- 不需要回到共享壳层或其他页面

## 3. 设计策略

### 3.1 正式页面矩阵

当前 8 张卡片过厚、过松。

本轮改为：

- 表格化 ledger 行
- 每行保留：
  - 编号
  - 区域 / 页面名
  - 指标
  - 事实标签
  - 进入动作

这样既能：

- 保留正式 8 页入口语义
- 又更接近 reference 左侧块的高密度承载感

### 3.2 治理动态

当前治理动态已有摘要 + 空态，但块感偏重。

本轮改为：

- 轻量 4 摘要卡
- 下方 feed 壳层
- 当无 `recentItems` 时，空态放在 feed 主体内而不是大面积独立空块

### 3.3 仍然只改 dashboard 局部

继续只改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue`

不改：

- `src/styles/index.scss`
- `AdminTopbar.vue`
- 其他页面

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及 dashboard 局部结构与样式
- 不会改变事实源
- 风险低、可逆

### 4.2 待验证

- 页面矩阵收紧后，仍需保持“这是正式 8 页入口”而不是看起来像伪榜单
- 治理动态空态收轻后，仍需足够清楚地表达“当前没有 recentItems”

因此本轮在压缩密度时，必须继续保留明确的事实边界文案。
