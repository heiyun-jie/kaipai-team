# 00-39 后台工作台最近事项精确筛查跳转（Admin Dashboard Recent Item Precise Filter Routing）

> 状态：进行中 | 优先级：P1 | 依赖：00-38 admin-dashboard-verify-window-alignment
> 记录目的：让工作台最近事项跳转后直接落到对应记录的筛查结果，而不是只进入泛列表。

## 1. 背景

当前 dashboard 已实现：

- 按 `itemType` 精分发到对应业务页
- 时间窗口上下文可带到目标页

但最近事项的“查看页面”仍只会进入对应列表页，不能把当前事项的唯一标识一并带过去。结果是运营仍需要在目标页二次输入：

- 支付单号
- 退款单号
- 邀请码 / 用户
- 用户 ID

这使最近事项的“继续处理”仍然不够闭环。

## 2. 范围

### 2.1 本轮必须处理

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/refund/OrdersView.vue`
- `kaipai-admin/src/views/payment/OrdersView.vue`
- `kaipai-admin/src/views/verify/VerificationBoard.vue`

### 2.2 本轮不处理

- 列表页直接打开详情抽屉
- dashboard summary / module 区块跳转
- 后端接口结构变更

## 3. 需求

### 3.1 dashboard 最近事项跳转

- **R1** referral 最近事项跳转时，应尽量携带可精确定位记录的筛查字段。
- **R2** refund 最近事项跳转时，应携带退款单号等精确筛查字段。
- **R3** payment 最近事项跳转时，应携带支付订单号等精确筛查字段。
- **R4** verify 最近事项跳转时，应至少携带用户 ID，用于缩小筛查范围。

### 3.2 目标页承接

- **R5** `RiskView` 必须支持读取 dashboard 携带的精确筛查字段并自动回填。
- **R6** `Refund OrdersView` 必须支持读取 dashboard 携带的精确筛查字段并自动回填。
- **R7** `Payment OrdersView` 必须支持读取 dashboard 携带的精确筛查字段并自动回填。
- **R8** `VerificationBoard` 必须支持读取 dashboard 携带的用户 ID 并自动回填。

### 3.3 边界

- **R9** 只透传目标页真实已支持的筛查字段。
- **R10** 不得因为精确筛查跳转破坏现有时间窗口透传能力。

## 4. 验收标准

- [ ] 已新增独立 Spec 并登记索引与代码映射
- [ ] 最近事项点击后可在目标页自动回填更精确的筛查字段
- [ ] 时间窗口透传能力继续有效
- [ ] `npm run build` 在 `kaipai-admin` 通过
