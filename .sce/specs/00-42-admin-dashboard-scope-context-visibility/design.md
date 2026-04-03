# 00-42 设计说明

## 1. 设计原则

- 来源可见性优先，先让运营明确“当前列表为什么长这样”
- `dashboard_recent_item` 与 `dashboard_scope` 共享同一套来源 helper
- 不改变既有筛查字段映射，只补来源标记和可视提示

## 2. 设计策略

### 2.1 dashboard 来源透传

`OverviewView.buildRouteQuery()` 统一产出：

- 最近事项：`source=dashboard_recent_item`
- 模块入口 / 快捷入口：`source=dashboard_scope`

并继续复用既有时间窗口映射：

- `verify -> submitTimeFrom/submitTimeTo`
- `referral/risk -> registeredAtFrom/registeredAtTo`
- `referral/records -> registeredAtFrom/registeredAtTo`
- `referral/eligibility -> effectiveFrom/effectiveTo`
- `refund/orders -> createdAtFrom/createdAtTo`
- `payment/orders -> createdAtFrom/createdAtTo`

### 2.2 目标页提示收口

新增 `src/utils/dashboard-context.ts`，提供：

- route query string 读取
- dashboard 来源识别
- 来源标题文案
- 默认兜底文案

各目标页只保留本页特有的摘要拼接逻辑，例如：

- verify：用户 ID、提交时间
- risk：邀请码、被邀请人、注册时间
- records：注册时间
- eligibility：生效时间
- refund：退款单号、用户 ID、创建时间
- payment：支付订单号、用户 ID、创建时间

当页面没有拼出特有摘要时，退回 helper 内统一兜底文案。

### 2.3 清空上下文

所有目标页继续统一使用：

- `router.replace({ path: route.path })`

依赖现有 `watch(route.fullPath)` 机制重新回填默认筛选并自动查询。

## 3. 影响文件

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/verify/VerificationBoard.vue`
- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/referral/RecordsView.vue`
- `kaipai-admin/src/views/referral/EligibilityView.vue`
- `kaipai-admin/src/views/refund/OrdersView.vue`
- `kaipai-admin/src/views/payment/OrdersView.vue`
- `kaipai-admin/src/utils/dashboard-context.ts`
- `kaipai-admin/src/types/dashboard.ts`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
