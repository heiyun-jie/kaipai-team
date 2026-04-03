# 00-44 执行记录

## 1. 调查结论

- referral 四页虽然都能从 dashboard 进入，但页面内部没有统一治理导航
- 从 dashboard 进入某一 referral 页后，若想切去另一页，必须依赖侧边菜单或回工作台
- 现有 dashboard 来源提示仅停留在单页内，没有 referral 页间的治理上下文续接规则

## 2. 本轮落地

已新增：

- `kaipai-admin/src/components/business/ReferralGovernanceNav.vue`
  - 提供异常邀请、邀请记录、邀请资格、邀请规则四个统一入口
  - 显示当前页激活态

已在 `kaipai-admin/src/utils/dashboard-context.ts` 补充：

- referral 治理路径判断
- referral 跨页治理 query 续接 helper
- 当前页有 dashboard 来源时，跨页切换统一降级为 `dashboard_scope`
- 时间窗口映射规则：
  - risk / records -> `registeredAtFrom/registeredAtTo`
  - eligibility -> `effectiveFrom/effectiveTo`
  - policies -> 仅保留来源标记

已接入以下页面：

- `RiskView.vue`
- `RecordsView.vue`
- `EligibilityView.vue`
- `PoliciesView.vue`

## 3. 边界保持

- 未改动 dashboard 直接进入 referral 页时的既有 query 回填规则
- 未把 `dashboard_recent_item` 语义错误延续到其他 referral 页面
- 未扩展到 membership / content 页面

## 4. 验证

- 构建验证：`cd D:\XM\kaipai-team\kaipai-admin && npm run build`
- 结果：通过
- 备注：仍保留 Vite chunk size warning 与 Sass legacy JS API deprecation warning，不阻塞本轮收口

## 5. Spec 回填

- 已登记 `.sce/specs/README.md`
- 已登记 `.sce/specs/spec-code-mapping.md`
- 已完成本 spec `tasks.md` 勾选
