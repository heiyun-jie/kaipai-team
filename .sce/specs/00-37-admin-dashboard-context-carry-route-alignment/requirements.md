# 00-37 后台工作台上下文带参跳转对齐（Admin Dashboard Context Carry Route Alignment）

> 状态：进行中 | 优先级：P1 | 依赖：00-36 admin-dashboard-payment-window-copy-alignment
> 记录目的：让工作台筛查后的时间窗口在跳转到已支持的治理页时继续生效，避免运营切页后丢失上下文。

## 1. 背景

当前工作台已支持 `dateFrom/dateTo` 筛查，但从工作台进入目标页时，筛查上下文会丢失。

已核对目标页能力边界：

- `referral/risk` 已支持 `registeredAtFrom/registeredAtTo`
- `refund/orders` 已支持 `createdAtFrom/createdAtTo`
- `payment/orders` 已支持 `createdAtFrom/createdAtTo`
- `verify/pending` 当前后端仍只支持 `userId/status/page`，尚不支持时间窗口

因此本轮不能把四个入口混成一条规则，只能先让已支持时间窗口的目标页接住来自 dashboard 的时间窗口上下文。

## 2. 范围

### 2.1 本轮必须处理

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/refund/OrdersView.vue`
- `kaipai-admin/src/views/payment/OrdersView.vue`

### 2.2 本轮不处理

- `verify/pending` 时间窗口能力
- 目标页详情页直达
- 业务线之外的额外筛查参数透传

## 3. 需求

### 3.1 工作台跳转

- **R1** 工作台跳转到 `referral/risk` 时，应把当前时间窗口映射为 `registeredAtFrom/registeredAtTo`。
- **R2** 工作台跳转到 `refund/orders` 时，应把当前时间窗口映射为 `createdAtFrom/createdAtTo`。
- **R3** 工作台跳转到 `payment/orders` 时，应把当前时间窗口映射为 `createdAtFrom/createdAtTo`。

### 3.2 目标页回填

- **R4** `RiskView` 必须读取路由参数并回填时间窗口筛查，再按该条件请求列表。
- **R5** `Refund OrdersView` 必须读取路由参数并回填创建时间筛查，再按该条件请求列表。
- **R6** `Payment OrdersView` 必须读取路由参数并回填创建时间筛查，再按该条件请求列表。

### 3.3 边界

- **R7** `verify/pending` 当前不得伪装支持时间窗口带参。
- **R8** 只透传目标页真实支持的字段，不得注入无效 query。

## 4. 验收标准

- [ ] 已新增独立 Spec 并登记索引与代码映射
- [ ] 工作台进入 `risk/refund/payment` 时可携带当前时间窗口
- [ ] 目标页可自动回填对应时间窗口筛查并据此查询
- [ ] `verify` 不被误标为已支持该能力
- [ ] `npm run build` 在 `kaipai-admin` 通过
