# 00-77 设计说明

## 1. 设计目标

`00-77` 只解决 dashboard 次级三块本身：

1. **retention block**：从重堆叠卡改成轻量代理结构
2. **style block**：从下堆叠 donut 改成更接近 reference 的横向组织
3. **channel block**：在事实边界不变的前提下，从 bar board 改成 donut + legend

## 2. 已核实的事实

### 2.1 当前问题仍只在 `OverviewView.vue`

最新证据：

- `D:\XM\kaipai-team\output\playwright\00-76\dashboard-index-full.png`

已确认：

- dashboard 首屏 `4 KPI + 漏斗/趋势` 已较稳定
- 剩余主要差异落在 `dashboard-grid--secondary`
- 不需要回到共享顶控、共享卡片壳层或 IA

### 2.2 当前事实边界仍不可突破

- 留存：
  - 当前没有次日、7日、cohort 曲线事实源
- 渠道：
  - 当前没有真实微信好友 / 朋友圈 / 企业微信字段
  - 只能继续使用 scene 分布近似承接

因此本轮只能改**表达**，不能改**数据事实**。

## 3. 设计策略

### 3.1 留存区

当前 stacked retention cards 过重，且与 reference 差异大。

本轮改为：

- 轻量 retention canvas / placeholder 区
- 底部 4 个代理指标横向排列
- 说明区收成更轻的 footnote

这样可以：

- 减少纵向高度
- 保持“不伪造留存曲线”的边界
- 更接近 reference 的“空白留存板 + 底部指标”结构

### 3.2 风格偏好

继续沿用当前 donut，但调整为：

- 左 / 中为 donut 主体
- 右侧为纵向 legend
- 减少下方堆叠感

### 3.3 渠道分布

当前 bar board 虽然保守，但和 reference 差距过大。

本轮改为：

- 使用与 scene 一致的三类近似承接数据
- 转成 donut + legend 表达
- 保留边界说明文案，明确它依然只是近似承接

### 3.4 仅改 dashboard 局部

本轮仍只改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue`

不改：

- `src/styles/index.scss`
- `AdminTopbar.vue`
- 其他页面

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及视图结构与局部样式
- 仍可完全复用现有 `overview` 聚合数据
- 风险低、可逆

### 4.2 待验证

- 渠道改成 donut 后，是否会被误读成真实渠道事实源
- 留存轻量化后，是否仍然足够明确地表达“这里只是代理指标”

因此本轮必须在布局优化同时，保留明确的事实边界文案。
