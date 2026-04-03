# 00-34 后台工作台时间窗口筛查对齐（Admin Dashboard Overview Window Filter Alignment）

> 状态：进行中 | 优先级：P1 | 依赖：00-33 admin-dashboard-recent-item-route-alignment
> 记录目的：为工作台概览补齐时间窗口筛查，并按后端真实边界接入 bizLine 筛查。

## 1. 背景

经后端核对，`/admin/dashboard/overview` 当前真实支持：

- `dateFrom`
- `dateTo`
- `bizLine`

但支持边界不是完全对称：

- `dateFrom/dateTo` 同时作用于上方统计和最近事项
- `bizLine` 仅作用于最近事项列表，不作用于上方统计卡

当前前端工作台还没有把这组能力暴露出来，导致运营无法按时间窗口回看工作台状态，也无法只看单业务线最近事项。

## 2. 范围

### 2.1 本轮必须处理

- `kaipai-admin/src/views/dashboard/OverviewView.vue`

### 2.2 本轮不处理

- dashboard 后端接口
- 统计卡口径重算
- recent items 字段结构

## 3. 需求

### 3.1 时间窗口

- **R1** 工作台必须补齐时间窗口筛查。
- **R2** 时间窗口应映射到 `dateFrom/dateTo`。
- **R3** 重置操作必须清空时间窗口。

### 3.2 业务线筛查

- **R4** 工作台必须补齐 `bizLine` 筛查。
- **R5** 页面说明必须明确：业务线筛查当前只影响最近事项，不影响上方统计卡。

### 3.3 交互边界

- **R6** 前端不得伪造“bizLine 会收窄统计卡”的假象。
- **R7** 查询动作和刷新动作都应基于当前筛查条件重新请求 overview。

## 4. 验收标准

- [ ] 已新增独立 Spec 并登记索引与代码映射
- [ ] 工作台已支持时间窗口筛查
- [ ] 工作台已支持 bizLine 筛查，并清楚标明只影响最近事项
- [ ] `npm run build` 在 `kaipai-admin` 通过
