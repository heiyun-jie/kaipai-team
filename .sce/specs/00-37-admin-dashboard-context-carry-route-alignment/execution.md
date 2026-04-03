# 00-37 执行记录

## 1. 调查结论

- 已确认 dashboard 当前跳转会丢失时间窗口上下文。
- 已确认目标页能力边界：
  - `referral/risk` 支持 `registeredAtFrom/registeredAtTo`
  - `refund/orders` 支持 `createdAtFrom/createdAtTo`
  - `payment/orders` 支持 `createdAtFrom/createdAtTo`
  - `verify/pending` 当前后端仍不支持时间窗口查询

## 2. 本轮落地

已在 `kaipai-admin/src/views/dashboard/OverviewView.vue` 完成：

- dashboard 跳转改为统一经过 `openDashboardRoute()`
- `referral/risk` 自动映射 `registeredAtFrom/registeredAtTo`
- `refund/orders` 自动映射 `createdAtFrom/createdAtTo`
- `payment/orders` 自动映射 `createdAtFrom/createdAtTo`
- 无时间窗口时不附带无效 query

已在目标页完成：

- `RiskView` 读取路由 query，回填 `registeredAtFrom/registeredAtTo` 后自动查询
- `Refund OrdersView` 读取路由 query，回填 `createdAtFrom/createdAtTo` 与 `createdAtRange` 后自动查询
- `Payment OrdersView` 读取路由 query，回填 `createdAtFrom/createdAtTo` 与 `createdAtRange` 后自动查询

## 3. 边界保持

- 本轮未伪装 `verify/pending` 已支持时间窗口
- 本轮未扩展到详情页直达或更多 query 透传
- 仅透传目标页真实已支持的筛查字段

## 4. Spec 回填与验证

- 已登记 `.sce/specs/README.md`
- 已登记 `.sce/specs/spec-code-mapping.md`
- 已完成本 spec `tasks.md` 勾选
- 构建验证：`cd D:\XM\kaipai-team\kaipai-admin && npm run build`
- 结果：通过
- 备注：仍保留 Vite chunk size warning 与 Sass legacy JS API deprecation warning，不阻塞本轮收口。
