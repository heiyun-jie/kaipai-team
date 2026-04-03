# 00-43 设计说明

## 1. 设计原则

- 来源标记只服务于“真实承接 dashboard 治理上下文”的页面
- 把路由白名单收口，避免 `OverviewView` 继续无限扩散 `dashboard_scope`
- `PoliciesView` 作为 referral 治理链一环，补齐与其他治理页一致的提示体验

## 2. 设计策略

### 2.1 路由白名单

在 `src/utils/dashboard-context.ts` 新增允许承接 dashboard 来源的路由集合与判断函数，例如：

- `/verify/pending`
- `/referral/risk`
- `/referral/records`
- `/referral/eligibility`
- `/referral/policies`
- `/refund/orders`
- `/payment/orders`

`OverviewView.buildRouteQuery()` 规则：

- 最近事项：仍透传 `dashboard_recent_item`
- 模块主操作 / 快捷入口：仅当 path 命中白名单时透传 `dashboard_scope`
- 非白名单页面：不追加 `source`

### 2.2 PoliciesView 来源提示

`PoliciesView` 接入：

- `useRoute` / `useRouter`
- `resolveDashboardRouteSource`
- `getDashboardContextTitle`
- `getDashboardContextFallbackSummary`

并在筛选区后展示来源提示条，默认使用共享 helper 的兜底文案。

### 2.3 清空动作

`PoliciesView` 继续统一使用：

- `router.replace({ path: route.path })`

清掉 query 后隐藏来源提示，不引入额外筛查字段回填。

## 3. 影响文件

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/referral/PoliciesView.vue`
- `kaipai-admin/src/utils/dashboard-context.ts`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
