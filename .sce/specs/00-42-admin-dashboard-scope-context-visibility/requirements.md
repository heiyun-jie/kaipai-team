# 00-42 后台工作台筛查上下文可见化（Admin Dashboard Scope Context Visibility）

> 状态：进行中 | 优先级：P1 | 依赖：00-40 admin-dashboard-recent-item-context-visibility、00-41 admin-dashboard-referral-quick-link-window-carry
> 记录目的：让工作台模块入口与快捷入口进入目标页时，也能显式展示“当前来自工作台筛查上下文”，避免只有最近事项才可见来源。

## 1. 背景

当前 dashboard 已完成：

- 最近事项进入目标页时，会透传精确 query
- 目标页会显示“当前来自工作台最近事项”并支持清空上下文
- referral 模块主操作与快捷入口已承接 dashboard 时间窗口

但工作台模块主操作与快捷入口虽然已能透传部分 query，目标页仍缺少统一的来源提示，导致运营从 dashboard 进入治理页后，无法判断当前列表是否仍处于工作台筛查上下文。

## 2. 范围

### 2.1 本轮必须处理

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/verify/VerificationBoard.vue`
- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/referral/RecordsView.vue`
- `kaipai-admin/src/views/referral/EligibilityView.vue`
- `kaipai-admin/src/views/refund/OrdersView.vue`
- `kaipai-admin/src/views/payment/OrdersView.vue`
- `kaipai-admin/src/utils/dashboard-context.ts`

### 2.2 本轮不处理

- dashboard 指标统计口径调整
- 新增更多 query 字段透传
- detail 抽屉级别的来源提示

## 3. 需求

### 3.1 dashboard 来源透传

- **R1** dashboard 最近事项进入目标页时，仍使用 `source=dashboard_recent_item`。
- **R2** dashboard 模块主操作与快捷入口进入目标页时，必须使用 `source=dashboard_scope` 标识来源。
- **R3** `OverviewView` 必须复用同一套路由 query 构建逻辑，不允许模块按钮和快捷入口各自维护一套来源标记。

### 3.2 目标页来源可见化

- **R4** `VerificationBoard`、`RiskView`、`RecordsView`、`EligibilityView`、退款单页、支付单页都必须识别 `dashboard_scope`。
- **R5** 当来源是 `dashboard_recent_item` 时，继续显示“当前来自工作台最近事项”。
- **R6** 当来源是 `dashboard_scope` 时，显示“当前来自工作台筛查上下文”。
- **R7** 上述页面都必须继续提供“清空上下文”，并清掉 query 后回到页面默认入口态。

### 3.3 单一来源约束

- **R8** 工作台来源识别、标题文案和默认兜底文案应尽量收口在共享 helper，避免在多个页面散落硬编码。
- **R9** 本轮不能破坏现有 query 回填与自动查询逻辑。

## 4. 验收标准

- [ ] 已新增独立 Spec 并登记索引与代码映射
- [ ] dashboard 模块主操作与快捷入口已透传 `dashboard_scope`
- [ ] 6 个目标页都能展示 dashboard scope / recent item 两类来源提示
- [ ] 工作台来源判断与兜底文案已收口到共享 helper
- [ ] `npm run build` 在 `kaipai-admin` 通过
