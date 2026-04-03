# 00-37 设计说明

## 1. 设计原则

- 严格按目标页真实筛查字段映射
- 不把 dashboard 的通用字段名直接硬塞进目标页
- 分层处理：已支持页先接入，未支持页留后续 spec

## 2. 设计策略

### 2.1 dashboard 出参

`OverviewView` 根据目标路由映射 query：

- `/referral/risk`
  - `registeredAtFrom=dateFrom`
  - `registeredAtTo=dateTo`
- `/refund/orders`
  - `createdAtFrom=dateFrom`
  - `createdAtTo=dateTo`
- `/payment/orders`
  - `createdAtFrom=dateFrom`
  - `createdAtTo=dateTo`

若工作台当前没有时间窗口，则不附带这些 query。

### 2.2 目标页入参

目标页在初始化时读取路由 query，并回填到各自已有筛查模型：

- `RiskView` 回填 `filters.registeredAtFrom/registerdAtTo`
- `Refund OrdersView` 回填 `filters.createdAtFrom/createdAtTo` 和 `createdAtRange`
- `Payment OrdersView` 回填 `filters.createdAtFrom/createdAtTo` 和 `createdAtRange`

完成回填后，再触发列表请求。

## 3. 影响文件

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/refund/OrdersView.vue`
- `kaipai-admin/src/views/payment/OrdersView.vue`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
