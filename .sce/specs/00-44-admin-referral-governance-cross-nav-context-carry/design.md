# 00-44 设计说明

## 1. 设计原则

- referral 四页之间切换必须在页内完成，不再要求用户退回 dashboard 或侧边菜单
- dashboard 来源下的跨页切换只续接“治理上下文”，不再把“最近事项”语义错误延续到别页
- 导航与 query 续接规则集中收口，避免四页散写

## 2. 设计策略

### 2.1 统一导航组件

新增 `src/components/business/ReferralGovernanceNav.vue`：

- 内置四个导航项
  - `/referral/risk`
  - `/referral/records`
  - `/referral/eligibility`
  - `/referral/policies`
- 使用当前路由决定激活态
- 点击时统一通过 helper 构建目标 query

### 2.2 dashboard query 续接

在 `src/utils/dashboard-context.ts` 增加 referral 专用 helper：

- 识别 referral 治理路径
- 从当前 query 中提取 dashboard 主时间窗口
  - 优先 `registeredAtFrom/registeredAtTo`
  - 否则 `effectiveFrom/effectiveTo`
- 按目标页重新映射
  - risk / records -> `registeredAtFrom/registeredAtTo`
  - eligibility -> `effectiveFrom/effectiveTo`
  - policies -> 无时间字段
- 若当前有 dashboard 来源，则目标页统一写入 `source=dashboard_scope`

### 2.3 页面接入

四个 referral 页面都在页面标题区下方接入 `ReferralGovernanceNav`，位于 overview/filter 之前，作为统一治理入口。

## 3. 影响文件

- `kaipai-admin/src/components/business/ReferralGovernanceNav.vue`
- `kaipai-admin/src/utils/dashboard-context.ts`
- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/referral/RecordsView.vue`
- `kaipai-admin/src/views/referral/EligibilityView.vue`
- `kaipai-admin/src/views/referral/PoliciesView.vue`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
