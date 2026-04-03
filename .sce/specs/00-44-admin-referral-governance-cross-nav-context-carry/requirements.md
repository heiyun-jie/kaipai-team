# 00-44 后台 referral 治理页切换与上下文续接（Admin Referral Governance Cross Nav Context Carry）

> 状态：进行中 | 优先级：P1 | 依赖：00-43 admin-dashboard-source-boundary-alignment
> 记录目的：让 referral 四个治理页在页内可直接切换，并在 dashboard 来源下继续承接治理时间窗口，避免从工作台进入后再次断链。

## 1. 背景

当前 dashboard referral 模块已提供四个入口：

- 异常邀请
- 邀请记录
- 邀请资格
- 邀请规则

且目标页也已能显示 dashboard 来源提示。但落到任一 referral 页后，页面内部仍缺少统一的治理页切换入口，导致运营要回到侧边菜单或工作台才能切去其他 referral 页面。

这会带来两类断链：

- referral 四页之间没有统一导航，治理链切换成本高
- 从 dashboard 来源进入某一页后，切去另一页时当前治理时间窗口也不会继续承接

## 2. 范围

### 2.1 本轮必须处理

- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/referral/RecordsView.vue`
- `kaipai-admin/src/views/referral/EligibilityView.vue`
- `kaipai-admin/src/views/referral/PoliciesView.vue`
- `kaipai-admin/src/components/business/ReferralGovernanceNav.vue`
- `kaipai-admin/src/utils/dashboard-context.ts`

### 2.2 本轮不处理

- dashboard 工作台模块视觉改版
- referral 页面业务筛选项调整
- membership / content 跨页导航

## 3. 需求

### 3.1 referral 页内统一切换

- **R1** risk / records / eligibility / policies 四页顶部都必须出现统一的 referral 治理导航入口。
- **R2** 当前所在页面必须有显性激活态。
- **R3** 导航项至少覆盖：异常邀请、邀请记录、邀请资格、邀请规则。

### 3.2 dashboard 来源续接

- **R4** 当当前 referral 页面来源于 dashboard 时，切换到其他 referral 页面必须继续承接 dashboard 治理上下文。
- **R5** 跨页切换后，来源统一使用 `dashboard_scope`，不得继续保留 `dashboard_recent_item`，因为已离开当前事项页。
- **R6** 风险页与记录页之间切换时，应继续承接 dashboard 时间窗口到 `registeredAtFrom/registeredAtTo`。
- **R7** 切换到资格页时，应继续承接 dashboard 时间窗口到 `effectiveFrom/effectiveTo`。
- **R8** 切换到规则页时，可仅保留来源标记，不要求承接额外时间字段。

### 3.3 单一来源约束

- **R9** referral 页间切换的 query 续接规则应尽量收口到共享 helper，不得在四个页面内各写一套。
- **R10** 本轮不得破坏已有 dashboard 直达 referral 页的 query 回填与提示逻辑。

## 4. 验收标准

- [ ] 已新增独立 Spec 并登记索引与代码映射
- [ ] referral 四页都已出现统一治理导航
- [ ] dashboard 来源下的 referral 跨页切换已续接治理上下文
- [ ] `npm run build` 在 `kaipai-admin` 通过
