# 00-41 后台工作台 referral 快捷入口时间窗口承接（Admin Dashboard Referral Quick Link Window Carry）

> 状态：进行中 | 优先级：P1 | 依赖：00-40 admin-dashboard-recent-item-context-visibility
> 记录目的：让 dashboard referral 模块里的快捷入口与主操作也承接当前时间窗口，避免从工作台进入治理页时断链。

## 1. 背景

当前 dashboard 已完成：

- 最近事项可把时间窗口带到目标页
- 最近事项还能精确带当前事项标识

但 referral 模块里的快捷入口和主操作仍未完整承接 dashboard 时间窗口，尤其：

- `/referral/records`
- `/referral/eligibility`

这会导致运营在工作台设定时间窗口后，从模块入口进入治理页时再次丢失上下文。

已核对后端真实筛查语义：

- `records` 同时支持 `registeredAt` 与 `validatedAt`
- `eligibility` 同时支持 `effective` 与 `expire`

按治理主时间轴，dashboard 时间窗口默认应映射：

- `records -> registeredAt`
- `eligibility -> effectiveTime`

## 2. 范围

### 2.1 本轮必须处理

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/referral/RecordsView.vue`
- `kaipai-admin/src/views/referral/EligibilityView.vue`

### 2.2 本轮不处理

- referral detail 抽屉直达
- validatedAt / expireTime 作为 dashboard 默认时间轴
- 最近事项逻辑调整

## 3. 需求

### 3.1 dashboard 入口透传

- **R1** dashboard 进入 `/referral/records` 时，应把当前时间窗口映射为 `registeredAtFrom/registeredAtTo`。
- **R2** dashboard 进入 `/referral/eligibility` 时，应把当前时间窗口映射为 `effectiveFrom/effectiveTo`。
- **R3** referral 模块主操作与快捷入口都应复用同一套透传规则。

### 3.2 目标页承接

- **R4** `RecordsView` 必须读取路由 query 并回填 `registeredAtFrom/registeredAtTo` 后自动查询。
- **R5** `EligibilityView` 必须读取路由 query 并回填 `effectiveFrom/effectiveTo` 后自动查询。

### 3.3 边界

- **R6** `records` 默认不得误映射到 `validatedAt`
- **R7** `eligibility` 默认不得误映射到 `expireTime`
- **R8** 只补当前工作台时间窗口承接，不扩展到更多筛查字段

## 4. 验收标准

- [ ] 已新增独立 Spec 并登记索引与代码映射
- [ ] dashboard referral 快捷入口与主操作已承接时间窗口
- [ ] `RecordsView` 与 `EligibilityView` 已自动回填并查询
- [ ] `npm run build` 在 `kaipai-admin` 通过
