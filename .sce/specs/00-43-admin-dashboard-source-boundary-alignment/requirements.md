# 00-43 后台工作台来源标记边界对齐（Admin Dashboard Source Boundary Alignment）

> 状态：进行中 | 优先级：P1 | 依赖：00-42 admin-dashboard-scope-context-visibility
> 记录目的：让工作台来源标记只落在当前治理主链页面，同时补齐 `/referral/policies` 的来源可见化，避免无意义透传。

## 1. 背景

`00-42` 已完成 dashboard scope 来源可见化，但当前 `OverviewView.buildRouteQuery()` 对所有模块入口都统一追加了 `source=dashboard_scope`，带来两个边界问题：

- `/referral/policies` 已属于 referral 治理主链，但还没有来源提示
- `/membership/products`、`/content/templates` 这类非当前工作台筛查主链页面，不应被附带 `dashboard_scope`

这会导致工作台来源标记语义扩散，不利于运营理解当前页面是否真的承接了工作台筛查上下文。

## 2. 范围

### 2.1 本轮必须处理

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/referral/PoliciesView.vue`
- `kaipai-admin/src/utils/dashboard-context.ts`

### 2.2 本轮不处理

- dashboard 卡片和筛查字段口径调整
- membership / content 页面新增工作台上下文能力
- policies 页面新增 dashboard 筛查字段回填

## 3. 需求

### 3.1 来源透传边界

- **R1** `OverviewView` 只有在目标路由属于当前工作台治理主链时，才能透传 `dashboard_scope`。
- **R2** 非治理主链页面，如会员产品、模板配置，不得再附带 `dashboard_scope`。
- **R3** 最近事项进入目标页时，继续保持 `dashboard_recent_item` 透传，不受本轮边界收口影响。

### 3.2 governance 路由覆盖

- **R4** `/referral/policies` 作为 referral 治理链入口，必须允许接收 `dashboard_scope`。
- **R5** `PoliciesView` 必须显示工作台来源提示，并支持清空上下文。

### 3.3 单一来源约束

- **R6** 哪些路由允许承接 dashboard 来源，应尽量收口到共享 helper，而不是散落在页面内硬编码。
- **R7** 本轮不得破坏 `00-42` 已完成的 verify / risk / records / eligibility / refund / payment 上下文行为。

## 4. 验收标准

- [ ] 已新增独立 Spec 并登记索引与代码映射
- [ ] 仅治理主链页面继续携带 dashboard 来源标记
- [ ] `PoliciesView` 已显示 dashboard 来源提示并支持清空
- [ ] `npm run build` 在 `kaipai-admin` 通过
