# Spec ↔ 代码映射表

> Spec 到实际源文件的双向追溯。更新时间：2026-06-01

## 后端包结构迁移说明

`00-179 / 00-180` 之后，后端主源码当前结构以 `controller / service / model / mapper / integration` 为准。本文中早于 `00-179` 的 `kaipaile-server/src/main/java/com/kaipai/module/*` 路径若未单独更新，均视为迁移前历史路径记录；后续新开发和当前排障不得再按旧 `module` 主源码路径落代码。

当前主源码路径映射：

- `module/controller/admin/*` -> `controller/admin/*`
- `module/controller/{domain}/*` -> `controller/api/{domain}/*`
- `module/server/{domain}/service/*` -> `service/{domain}/*`
- `module/server/{domain}/mapper/*` -> `mapper/{domain}/*`
- `module/model/{domain}/*` -> `model/{domain}/*`
- 短信、实名、微信、AI provider、COS 等外部能力 -> `integration/*`

## 增量登记

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 00-12 admin-role-permission-tree | `kaipai-admin/src/constants/permission-registry.ts` | — | ✅ 已新增：权限 registry、树结构与三数组映射 |
| | `kaipai-admin/src/components/forms/PermissionTreeEditor.vue` | — | ✅ 已新增：树形权限编辑器 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已改造：角色编辑切换为树形权限编排，详情改为可读标签 |
| 00-13 admin-user-role-binding-guard | `kaipai-admin/src/views/system/AdminUsersView.vue` | — | ✅ 已改造：角色目录权限提示、禁用角色绑定警示与提交保护 |
| 00-14 admin-user-form-guard | `kaipai-admin/src/views/system/AdminUsersView.vue` | — | ✅ 已改造：创建/编辑表单校验、绑定角色/重置密码/启停用原因约束 |
| 00-15 finance-date-range-filters | `kaipai-admin/src/views/payment/OrdersView.vue` | — | ✅ 已改造：创建时间/支付时间范围筛选 |
| | `kaipai-admin/src/views/payment/TransactionsView.vue` | — | ✅ 已改造：回调时间范围筛选 |
| | `kaipai-admin/src/views/refund/OrdersView.vue` | — | ✅ 已改造：支付单号、创建/审核时间范围筛选 |
| | `kaipai-admin/src/views/refund/LogsView.vue` | — | ✅ 已改造：日志时间范围筛选 |
| | `kaipai-admin/src/types/refund.ts` | — | ✅ 已扩展：退款单查询类型字段 |
| 00-178 current-phase-tencent-cloud-realname-two-factor-enablement | `.sce/specs/00-178-current-phase-tencent-cloud-realname-two-factor-enablement/requirements.md` | — | ✅ 已新增：腾讯云身份证二要素实名认证实现需求 |
| | `.sce/specs/00-178-current-phase-tencent-cloud-realname-two-factor-enablement/design.md` | — | ✅ 已新增：后端 provider、状态机、DB 字段与后台回看设计 |
| | `.sce/specs/00-178-current-phase-tencent-cloud-realname-two-factor-enablement/tasks.md` | — | ✅ 已新增：实现与验证任务 |
| | `.sce/specs/00-178-current-phase-tencent-cloud-realname-two-factor-enablement/execution.md` | — | ✅ 已新增：执行记录与验证结果 |
| | `kaipaile-server/src/main/java/com/kaipai/integration/verify/*` | — | ✅ 已迁移：实名 provider、腾讯云二要素调用、人工兜底与身份证加密 helper |
| | `kaipaile-server/src/main/java/com/kaipai/service/verify/impl/IdentityVerificationServiceImpl.java` | — | ✅ 已迁移：submit 接入二要素自动通过 / 拒绝 / 人工兜底状态机 |
| | `kaipaile-server/src/main/java/com/kaipai/model/verify/entity/IdentityVerification.java` | — | ✅ 已迁移：脱敏身份证与 provider 结果字段 |
| | `kaipaile-server/src/main/java/com/kaipai/model/verify/dto/IdentityVerificationDetailRespDTO.java` | — | ✅ 已迁移：后台详情回看 provider 结果 |
| | `kaipaile-server/src/main/resources/application.yml` | — | ✅ 已新增：`kaipai.realname` 与身份证密钥配置入口 |
| | `kaipaile-server/src/main/resources/db/migration/V20260529_001__tencent_realname_two_factor.sql` | — | ✅ 已新增：identity_verification provider 字段与脱敏字段 |
| | `kaipaile-server/src/test/java/com/kaipai/module/server/verify/realname/TencentRealNameVerificationProviderTest.java` | — | ⚠️ 测试树历史路径：腾讯云 provider 单测，主源码迁移后见 `integration/verify` |
| | `kaipaile-server/src/test/java/com/kaipai/module/server/verify/service/impl/IdentityVerificationServiceImplTest.java` | — | ⚠️ 测试树历史路径：submit 状态机单测，主源码迁移后见 `service/verify` |
| | `kaipai-admin/src/types/verify.ts` | — | ✅ 已扩展：后台 verify provider 字段类型 |
| | `kaipai-admin/src/views/verify/VerificationBoard.vue` | — | ✅ 已改造：详情抽屉展示服务商核验摘要 |
| 00-74 current-phase-admin-reference-ui-architecture-rebuild | `.sce/specs/00-74-current-phase-admin-reference-ui-architecture-rebuild/requirements.md` | — | ✅ 已新增：固化后台 reference-driven 的 8 页 UI / IA 二次重构需求 |
| | `.sce/specs/00-74-current-phase-admin-reference-ui-architecture-rebuild/design.md` | — | ✅ 已新增：后台正式导航、reference 页面映射与 capability 重组设计 |
| | `.sce/specs/00-74-current-phase-admin-reference-ui-architecture-rebuild/tasks.md` | — | ✅ 已新增：后台 reference-driven 二次重构任务 |
| | `.sce/specs/00-74-current-phase-admin-reference-ui-architecture-rebuild/execution.md` | — | ✅ 已新增：后台运行态对比、`/admin/users` 事实源与机构缺口记录 |
| | `kaipai-admin/src/router/index.ts` | — | 🟡 已建档：后续需恢复 reference 正式页路由分层 |
| | `kaipai-admin/src/constants/menus.ts` | — | 🟡 已建档：后续需从 shrink-phase 侧栏投影回收为 reference 正式导航 |
| | `kaipai-admin/src/stores/permission.ts` | — | 🟡 已建档：后续需按新正式导航投影继续过滤权限 |
| | `kaipai-admin/src/components/layout/AdminSidebar.vue` | — | 🟡 已建档：后续需恢复 `OVERVIEW / GROWTH / OPERATE` 正式侧栏结构 |
| | `kaipai-admin/src/components/layout/AdminTopbar.vue` | — | 🟡 已建档：后续需回到 reference 顶部控制条语义 |
| | `kaipai-admin/src/constants/admin-information-architecture.ts` | — | 🟡 已建档：后续需从 `dashboard-analytics + user-center + tooling` 收口口径切换到 reference 正式页分层 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | 🟡 已建档：后续需从 shrink-phase 说明页回收为 reference 仪表盘 |
| | `kaipai-admin/src/views/user/UserCenterView.vue` | — | 🟡 已建档：当前仍是占位页，后续需回接 `/admin/users` 成为正式用户管理页 |
| | `kaipai-admin/src/api/user-center.ts` | — | ✅ 已核实：已接通 `/admin/users` 真实业务用户中心接口 |
| | `kaipai-admin/src/types/user-center.ts` | — | ✅ 已核实：已具备业务用户中心列表 / 详情类型 |
| | `kaipaile-server/src/main/java/com/kaipai/controller/admin/user/AdminUserController.java` | — | ✅ 已迁移：后台业务用户中心接口真实存在 |
| 00-16 admin-operator-copy-optimization | `kaipai-admin/src/components/layout/AdminTopbar.vue` | — | ✅ 已改造：顶部服务提示与通用说明切换为运营话术 |
| | `kaipai-admin/src/views/auth/LoginView.vue` | — | ✅ 已改造：登录页改为运营工作台定位文案 |
| | `kaipai-admin/src/views/shared/PlaceholderView.vue` | — | ✅ 已改造：占位页移除路由/权限技术信息 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已改造：工作台描述、模块状态和最近事项改为运营说明 |
| | `kaipai-admin/src/views/verify/VerificationBoard.vue` | — | ✅ 已改造：实名认证审核页改为任务导向描述 |
| | `kaipai-admin/src/views/referral/RiskView.vue` | — | ✅ 已改造：异常邀请审核页改为复核导向描述 |
| | `kaipai-admin/src/views/membership/ProductsView.vue` | — | ✅ 已改造：会员产品页改为配置导向描述 |
| | `kaipai-admin/src/views/membership/AccountsView.vue` | — | ✅ 已改造：会员账户页改为运营动作导向描述 |
| | `kaipai-admin/src/views/payment/OrdersView.vue` | — | ✅ 已改造：支付订单页改为订单回看导向描述 |
| | `kaipai-admin/src/views/payment/TransactionsView.vue` | — | ✅ 已改造：支付流水页改为交易核对导向描述 |
| | `kaipai-admin/src/views/refund/OrdersView.vue` | — | ✅ 已改造：退款单页改为退款处理导向描述 |
| | `kaipai-admin/src/views/refund/LogsView.vue` | — | ✅ 已改造：退款日志页改为处理回看导向描述 |
| | `kaipai-admin/src/views/content/TemplatesView.vue` | — | ✅ 已改造：模板页筛选说明改为配置维护导向描述 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已改造：角色管理页改为权限治理导向描述 |
| | `kaipai-admin/src/views/system/AdminUsersView.vue` | — | ✅ 已改造：后台账号页改为团队管理导向描述 |
| | `kaipai-admin/src/views/system/OperationLogsView.vue` | — | ✅ 已改造：操作日志页改为追踪与复盘导向描述 |
| 00-17 admin-dashboard-hierarchy-optimization | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已改造：工作台概览卡、模块卡与主操作层级重排 |
| | `kaipai-admin/src/components/layout/AdminTopbar.vue` | — | ✅ 已改造：顶部账号区与服务状态提示层级重排 |
| | `kaipai-admin/src/components/business/StatusTag.vue` | — | ✅ 已改造：状态标签增强辨识度与稳定视觉锚点 |
| 00-18 admin-page-style-alignment | `kaipai-admin/src/components/business/PageContainer.vue` | — | ✅ 已改造：统一后台页头面板与操作区节奏 |
| | `kaipai-admin/src/components/business/FilterPanel.vue` | — | ✅ 已改造：筛选区升级为工具面板，强化表单与动作分层 |
| | `kaipai-admin/src/styles/index.scss` | — | ✅ 已改造：表格主卡、详情卡、抽屉弹窗与标签组共享视觉壳层 |
| 00-20 admin-filter-inline-alignment | `kaipai-admin/src/components/business/FilterPanel.vue` | — | ✅ 已改造：统一行内筛选项标签与输入同一行、垂直居中 |
| | `kaipai-admin/src/views/verify/VerificationBoard.vue` | — | ✅ 已改造：实名认证审核页筛选区回收为与其他后台页一致的 inline 结构 |
| 00-19 admin-verify-page-refinement | `kaipai-admin/src/views/verify/VerificationBoard.vue` | — | ✅ 已改造：实名认证审核页补齐概览卡、上置筛选、空态和详情语义 |
| 00-21 admin-filter-control-reuse | `kaipai-admin/src/components/business/FilterPanel.vue` | — | ✅ 已改造：复用 `/verify/pending` 输入框、下拉框和占位文本外观 |
| | `kaipai-admin/src/views/verify/VerificationBoard.vue` | — | ✅ 已清理重复输入私有样式，仅保留页面宽度控制 |
| 00-22 admin-table-action-overflow-fix | `kaipai-admin/src/styles/index.scss` | — | ✅ 已改造：新增后台表格操作列共享按钮组换行容器 |
| | `kaipai-admin/src/views/system/AdminUsersView.vue` | — | ✅ 已改造：后台账号 fixed 操作列接入共享容器，修复按钮穿透 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已改造：角色管理 fixed 操作列接入共享容器 |
| | `kaipai-admin/src/views/content/TemplatesView.vue` | — | ✅ 已改造：模板列表 fixed 操作列接入共享容器 |
| | `kaipai-admin/src/views/membership/AccountsView.vue` | — | ✅ 已改造：会员账户 fixed 操作列接入共享容器 |
| | `kaipai-admin/src/views/referral/RiskView.vue` | — | ✅ 已改造：异常邀请审核 fixed 操作列接入共享容器 |
| | `kaipai-admin/src/views/verify/VerificationBoard.vue` | — | ✅ 已改造：实名认证审核 fixed 操作列接入共享容器 |
| | `kaipai-admin/src/views/refund/OrdersView.vue` | — | ✅ 已改造：退款单 fixed 操作列接入共享容器 |
| 00-23 admin-fixed-column-layer-fix | `kaipai-admin/src/styles/index.scss` | — | ✅ 已改造：补齐后台 fixed 右列背景层、分隔边界与 hover 同步，消除底层内容穿透 |
| 00-24 admin-fixed-column-hover-layer-fix | `kaipai-admin/src/styles/index.scss` | — | ✅ 已改造：修复 fixed-right wrapper / patch / hover 层级，保证操作按钮不被悬浮层压住 |
| 00-25 admin-fixed-column-sticky-cell-fix | `kaipai-admin/src/styles/index.scss` | — | 🟡 待复核：已收敛 fixed sticky 单元格与 inner cell 层级，等待页面确认 hover 态操作区遮挡是否消失 |
| 00-27 mini-program-frontend-architecture | `.sce/specs/00-27-mini-program-frontend-architecture/requirements.md` | — | ✅ 已新增：小程序前端整体架构总纲 |
| | `.sce/specs/00-27-mini-program-frontend-architecture/design.md` | — | ✅ 已新增：页面信息架构、模块分层、数据流与分包决策矩阵 |
| 00-28 architecture-driven-delivery-governance | `.sce/specs/00-28-architecture-driven-delivery-governance/requirements.md` | — | ✅ 已新增：按整体架构推进项目的治理基线 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/design.md` | — | ✅ 已新增：工作流分组、能力切片模板、优先级路线与闭环定义 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md` | — | ✅ 已新增：推进入口、优先级维护与切片回填任务 |
| 00-29 backend-admin-release-governance | `.sce/specs/00-29-backend-admin-release-governance/requirements.md` | — | ✅ 已新增：后端与管理端发布治理规则 |
| | `.sce/specs/00-29-backend-admin-release-governance/design.md` | — | ✅ 已新增：发布阶段、运行时集合、smoke 与回滚设计 |
| | `.sce/specs/00-29-backend-admin-release-governance/tasks.md` | — | ✅ 已新增：发布治理与 runbook 建设任务 |
| | `.sce/runbooks/backend-admin-release/backend-admin-standard-release.md` | — | ✅ 已新增：独立运维发布手册 |
| | `.sce/runbooks/backend-admin-release/backend-admin-release-evidence-template.md` | — | ✅ 已新增：发布证据模板 |
| 00-30 admin-referral-governance-structure-alignment | `.sce/specs/00-30-admin-referral-governance-structure-alignment/requirements.md` | — | ✅ 已新增：后台邀请治理结构优化需求 |
| | `.sce/specs/00-30-admin-referral-governance-structure-alignment/design.md` | — | ✅ 已新增：治理摘要卡与时间窗口筛查设计 |
| | `.sce/specs/00-30-admin-referral-governance-structure-alignment/tasks.md` | — | ✅ 已新增：后台 referral 结构优化任务 |
| | `.sce/specs/00-30-admin-referral-governance-structure-alignment/execution.md` | — | ✅ 已新增：后台 referral 结构优化执行记录 |
| | `kaipai-admin/src/components/business/GovernanceOverviewCards.vue` | — | ✅ 已新增：后台治理摘要共享卡片组件 |
| | `kaipai-admin/src/views/referral/RecordsView.vue` | — | ✅ 已完成：补治理摘要卡与注册 / 生效时间窗口筛查 |
| | `kaipai-admin/src/views/referral/RiskView.vue` | — | ✅ 已完成：补治理摘要卡与注册时间窗口筛查 |
| | `kaipai-admin/src/views/referral/EligibilityView.vue` | — | ✅ 已完成：补生效时间窗口筛查 |
| 00-31 admin-referral-policies-governance-refinement | `.sce/specs/00-31-admin-referral-policies-governance-refinement/requirements.md` | — | ✅ 已新增：后台邀请规则治理页优化需求 |
| | `.sce/specs/00-31-admin-referral-policies-governance-refinement/design.md` | — | ✅ 已新增：规则态势摘要与列表语义设计 |
| | `.sce/specs/00-31-admin-referral-policies-governance-refinement/tasks.md` | — | ✅ 已新增：后台邀请规则治理页优化任务 |
| | `.sce/specs/00-31-admin-referral-policies-governance-refinement/execution.md` | — | ✅ 已新增：后台邀请规则治理页优化执行记录 |
| | `kaipai-admin/src/views/referral/PoliciesView.vue` | — | ✅ 已完成：补规则治理摘要卡、规则清单语义头与治理空态 |
| 00-32 admin-dashboard-referral-governance-entry-alignment | `.sce/specs/00-32-admin-dashboard-referral-governance-entry-alignment/requirements.md` | — | ✅ 已新增：后台工作台邀请治理入口对齐需求 |
| | `.sce/specs/00-32-admin-dashboard-referral-governance-entry-alignment/design.md` | — | ✅ 已新增：dashboard referral 入口链设计 |
| | `.sce/specs/00-32-admin-dashboard-referral-governance-entry-alignment/tasks.md` | — | ✅ 已新增：dashboard referral 入口对齐任务 |
| | `.sce/specs/00-32-admin-dashboard-referral-governance-entry-alignment/execution.md` | — | ✅ 已新增：dashboard referral 入口对齐执行记录 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成：工作台 referral 模块升级为邀请治理入口链，补齐四个 quick links |
| 00-33 admin-dashboard-recent-item-route-alignment | `.sce/specs/00-33-admin-dashboard-recent-item-route-alignment/requirements.md` | — | ✅ 已新增：后台工作台最近事项路由对齐需求 |
| | `.sce/specs/00-33-admin-dashboard-recent-item-route-alignment/design.md` | — | ✅ 已新增：最近事项 itemType 分发设计 |
| | `.sce/specs/00-33-admin-dashboard-recent-item-route-alignment/tasks.md` | — | ✅ 已新增：最近事项路由对齐任务 |
| | `.sce/specs/00-33-admin-dashboard-recent-item-route-alignment/execution.md` | — | ✅ 已新增：最近事项路由对齐执行记录 |
| | `kaipai-admin/src/types/dashboard.ts` | — | ✅ 已完成：收口 dashboard 最近事项 itemType 联合类型 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成：最近事项按 itemType 精分发，未知值回退到 bizLine 默认路由 |
| 00-34 admin-dashboard-overview-window-filter-alignment | `.sce/specs/00-34-admin-dashboard-overview-window-filter-alignment/requirements.md` | — | ✅ 已新增：后台工作台时间窗口筛查对齐需求 |
| | `.sce/specs/00-34-admin-dashboard-overview-window-filter-alignment/design.md` | — | ✅ 已新增：overview 时间窗口与 bizLine 筛查设计 |
| | `.sce/specs/00-34-admin-dashboard-overview-window-filter-alignment/tasks.md` | — | ✅ 已新增：overview 筛查对齐任务 |
| | `.sce/specs/00-34-admin-dashboard-overview-window-filter-alignment/execution.md` | — | ✅ 已新增：overview 筛查对齐执行记录 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成：补时间窗口与 bizLine 筛查，并明确 bizLine 仅作用于最近事项 |
| 00-35 admin-dashboard-filter-scope-clarity | `.sce/specs/00-35-admin-dashboard-filter-scope-clarity/requirements.md` | — | ✅ 已新增：后台工作台筛查范围可见化需求 |
| | `.sce/specs/00-35-admin-dashboard-filter-scope-clarity/design.md` | — | ✅ 已新增：overview 范围摘要与空态提示设计 |
| | `.sce/specs/00-35-admin-dashboard-filter-scope-clarity/tasks.md` | — | ✅ 已新增：overview 范围可见化任务 |
| | `.sce/specs/00-35-admin-dashboard-filter-scope-clarity/execution.md` | — | ✅ 已新增：overview 范围可见化执行记录 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成：显式展示统计范围与最近事项范围，并让空态感知当前筛查条件 |
| 00-36 admin-dashboard-payment-window-copy-alignment | `.sce/specs/00-36-admin-dashboard-payment-window-copy-alignment/requirements.md` | — | ✅ 已新增：后台工作台支付时间窗口文案对齐需求 |
| | `.sce/specs/00-36-admin-dashboard-payment-window-copy-alignment/design.md` | — | ✅ 已新增：支付卡与支付最近事项时间窗口文案设计 |
| | `.sce/specs/00-36-admin-dashboard-payment-window-copy-alignment/tasks.md` | — | ✅ 已新增：支付时间窗口文案对齐任务 |
| | `.sce/specs/00-36-admin-dashboard-payment-window-copy-alignment/execution.md` | — | ✅ 已新增：支付时间窗口文案对齐执行记录 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成：支付统计卡与支付最近事项标题按时间窗口动态切换展示语义 |
| 00-37 admin-dashboard-context-carry-route-alignment | `.sce/specs/00-37-admin-dashboard-context-carry-route-alignment/requirements.md` | — | ✅ 已新增：后台工作台上下文带参跳转对齐需求 |
| | `.sce/specs/00-37-admin-dashboard-context-carry-route-alignment/design.md` | — | ✅ 已新增：dashboard 到 risk/refund/payment 的时间窗口映射设计 |
| | `.sce/specs/00-37-admin-dashboard-context-carry-route-alignment/tasks.md` | — | ✅ 已新增：上下文带参跳转对齐任务 |
| | `.sce/specs/00-37-admin-dashboard-context-carry-route-alignment/execution.md` | — | ✅ 已新增：上下文带参跳转对齐执行记录 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成：dashboard 按目标页真实字段透传时间窗口 query |
| | `kaipai-admin/src/views/referral/RiskView.vue` | — | ✅ 已完成：读取 dashboard query 并回填注册时间筛查 |
| | `kaipai-admin/src/views/refund/OrdersView.vue` | — | ✅ 已完成：读取 dashboard query 并回填创建时间筛查 |
| | `kaipai-admin/src/views/payment/OrdersView.vue` | — | ✅ 已完成：读取 dashboard query 并回填创建时间筛查 |
| 00-38 admin-dashboard-verify-window-alignment | `.sce/specs/00-38-admin-dashboard-verify-window-alignment/requirements.md` | — | ✅ 已新增：后台工作台 verify 时间窗口对齐需求 |
| | `.sce/specs/00-38-admin-dashboard-verify-window-alignment/design.md` | — | ✅ 已新增：verify 提交时间筛查与 dashboard 跳转设计 |
| | `.sce/specs/00-38-admin-dashboard-verify-window-alignment/tasks.md` | — | ✅ 已新增：verify 时间窗口对齐任务 |
| | `.sce/specs/00-38-admin-dashboard-verify-window-alignment/execution.md` | — | ✅ 已新增：verify 时间窗口对齐执行记录 |
| | `kaipaile-server/src/main/java/com/kaipai/model/verify/dto/IdentityVerificationListReqDTO.java` | — | ✅ 已迁移：verify 列表新增 submitTime 时间窗口字段 |
| | `kaipaile-server/src/main/java/com/kaipai/service/verify/impl/IdentityVerificationServiceImpl.java` | — | ✅ 已迁移：verify 列表按 create_time 执行提交时间窗口筛查 |
| | `kaipai-admin/src/types/verify.ts` | — | ✅ 已完成：verify 查询类型补齐 submitTime 字段 |
| | `kaipai-admin/src/views/verify/VerificationBoard.vue` | — | ✅ 已完成：verify 页补提交时间筛查与 route query 回填 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成：dashboard 到 verify/pending 带 submitTime query 跳转 |
| 00-39 admin-dashboard-recent-item-precise-filter-routing | `.sce/specs/00-39-admin-dashboard-recent-item-precise-filter-routing/requirements.md` | — | ✅ 已新增：后台工作台最近事项精确筛查跳转需求 |
| | `.sce/specs/00-39-admin-dashboard-recent-item-precise-filter-routing/design.md` | — | ✅ 已新增：最近事项精确字段透传与目标页回填设计 |
| | `.sce/specs/00-39-admin-dashboard-recent-item-precise-filter-routing/tasks.md` | — | ✅ 已新增：最近事项精确筛查跳转任务 |
| | `.sce/specs/00-39-admin-dashboard-recent-item-precise-filter-routing/execution.md` | — | ✅ 已新增：最近事项精确筛查跳转执行记录 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成：最近事项跳转可附带当前事项的精确筛查字段 |
| | `kaipai-admin/src/views/referral/RiskView.vue` | — | ✅ 已完成：承接 inviteCode / inviteeUserId 路由筛查 |
| | `kaipai-admin/src/views/refund/OrdersView.vue` | — | ✅ 已完成：承接 refundNo / userId 路由筛查 |
| | `kaipai-admin/src/views/payment/OrdersView.vue` | — | ✅ 已完成：承接 orderNo / userId 路由筛查 |
| | `kaipai-admin/src/views/verify/VerificationBoard.vue` | — | ✅ 已完成：承接 userId 路由筛查 |
| 00-40 admin-dashboard-recent-item-context-visibility | `.sce/specs/00-40-admin-dashboard-recent-item-context-visibility/requirements.md` | — | ✅ 已新增：后台工作台最近事项上下文可见化需求 |
| | `.sce/specs/00-40-admin-dashboard-recent-item-context-visibility/design.md` | — | ✅ 已新增：来源标记、提示条与清空动作设计 |
| | `.sce/specs/00-40-admin-dashboard-recent-item-context-visibility/tasks.md` | — | ✅ 已新增：最近事项上下文可见化任务 |
| | `.sce/specs/00-40-admin-dashboard-recent-item-context-visibility/execution.md` | — | ✅ 已新增：最近事项上下文可见化执行记录 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成：最近事项跳转追加 dashboard_recent_item 来源标记 |
| | `kaipai-admin/src/views/verify/VerificationBoard.vue` | — | ✅ 已完成：显示最近事项上下文提示并支持清空 |
| | `kaipai-admin/src/views/referral/RiskView.vue` | — | ✅ 已完成：显示最近事项上下文提示并支持清空 |
| | `kaipai-admin/src/views/refund/OrdersView.vue` | — | ✅ 已完成：显示最近事项上下文提示并支持清空 |
| | `kaipai-admin/src/views/payment/OrdersView.vue` | — | ✅ 已完成：显示最近事项上下文提示并支持清空 |
| 00-41 admin-dashboard-referral-quick-link-window-carry | `.sce/specs/00-41-admin-dashboard-referral-quick-link-window-carry/requirements.md` | — | ✅ 已新增：后台工作台 referral 快捷入口时间窗口承接需求 |
| | `.sce/specs/00-41-admin-dashboard-referral-quick-link-window-carry/design.md` | — | ✅ 已新增：records / eligibility 主时间轴映射设计 |
| | `.sce/specs/00-41-admin-dashboard-referral-quick-link-window-carry/tasks.md` | — | ✅ 已新增：referral 快捷入口时间窗口承接任务 |
| | `.sce/specs/00-41-admin-dashboard-referral-quick-link-window-carry/execution.md` | — | ✅ 已新增：referral 快捷入口时间窗口承接执行记录 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成：referral records / eligibility 入口透传当前时间窗口 |
| | `kaipai-admin/src/views/referral/RecordsView.vue` | — | ✅ 已完成：读取 registeredAt route query 并自动查询 |
| | `kaipai-admin/src/views/referral/EligibilityView.vue` | — | ✅ 已完成：读取 effectiveTime route query 并自动查询 |
| 00-42 admin-dashboard-scope-context-visibility | `.sce/specs/00-42-admin-dashboard-scope-context-visibility/requirements.md` | — | ✅ 已新增：后台工作台筛查上下文可见化需求 |
| | `.sce/specs/00-42-admin-dashboard-scope-context-visibility/design.md` | — | ✅ 已新增：dashboard scope 来源透传与目标页提示设计 |
| | `.sce/specs/00-42-admin-dashboard-scope-context-visibility/tasks.md` | — | ✅ 已新增：dashboard scope 上下文可见化任务 |
| | `.sce/specs/00-42-admin-dashboard-scope-context-visibility/execution.md` | — | ✅ 已新增：dashboard scope 上下文可见化执行记录 |
| | `kaipai-admin/src/utils/dashboard-context.ts` | — | ✅ 已新增：工作台来源识别、标题与兜底文案共享 helper |
| | `kaipai-admin/src/types/dashboard.ts` | — | ✅ 已新增：DashboardRouteSource 类型 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成：模块入口与快捷入口统一透传 dashboard_scope 来源 |
| | `kaipai-admin/src/views/verify/VerificationBoard.vue` | — | ✅ 已完成：支持 dashboard_scope / dashboard_recent_item 两类来源提示 |
| | `kaipai-admin/src/views/referral/RiskView.vue` | — | ✅ 已完成：支持 dashboard_scope / dashboard_recent_item 两类来源提示 |
| | `kaipai-admin/src/views/referral/RecordsView.vue` | — | ✅ 已完成：支持 dashboard_scope 来源提示与清空上下文 |
| | `kaipai-admin/src/views/referral/EligibilityView.vue` | — | ✅ 已完成：支持 dashboard_scope 来源提示与清空上下文 |
| | `kaipai-admin/src/views/refund/OrdersView.vue` | — | ✅ 已完成：支持 dashboard_scope / dashboard_recent_item 两类来源提示 |
| | `kaipai-admin/src/views/payment/OrdersView.vue` | — | ✅ 已完成：支持 dashboard_scope / dashboard_recent_item 两类来源提示 |
| 00-43 admin-dashboard-source-boundary-alignment | `.sce/specs/00-43-admin-dashboard-source-boundary-alignment/requirements.md` | — | ✅ 已新增：后台工作台来源标记边界对齐需求 |
| | `.sce/specs/00-43-admin-dashboard-source-boundary-alignment/design.md` | — | ✅ 已新增：dashboard source 路由白名单与 policies 提示设计 |
| | `.sce/specs/00-43-admin-dashboard-source-boundary-alignment/tasks.md` | — | ✅ 已新增：dashboard source 边界对齐任务 |
| | `.sce/specs/00-43-admin-dashboard-source-boundary-alignment/execution.md` | — | ✅ 已新增：dashboard source 边界对齐执行记录 |
| | `kaipai-admin/src/utils/dashboard-context.ts` | — | ✅ 已补充：dashboard 来源承接路由白名单判断 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成：只对白名单治理主链页面透传 dashboard source |
| | `kaipai-admin/src/views/referral/PoliciesView.vue` | — | ✅ 已完成：补齐 dashboard 来源提示与清空上下文 |
| 00-44 admin-referral-governance-cross-nav-context-carry | `.sce/specs/00-44-admin-referral-governance-cross-nav-context-carry/requirements.md` | — | ✅ 已新增：referral 治理页切换与上下文续接需求 |
| | `.sce/specs/00-44-admin-referral-governance-cross-nav-context-carry/design.md` | — | ✅ 已新增：统一治理导航与 query 续接设计 |
| | `.sce/specs/00-44-admin-referral-governance-cross-nav-context-carry/tasks.md` | — | ✅ 已新增：referral 跨页治理导航任务 |
| | `.sce/specs/00-44-admin-referral-governance-cross-nav-context-carry/execution.md` | — | ✅ 已新增：referral 跨页治理导航执行记录 |
| | `kaipai-admin/src/components/business/ReferralGovernanceNav.vue` | — | ✅ 已新增：referral 四页统一治理导航组件 |
| | `kaipai-admin/src/utils/dashboard-context.ts` | — | ✅ 已补充：referral 跨页治理 query 续接 helper |
| | `kaipai-admin/src/views/referral/RiskView.vue` | — | ✅ 已接入：页内治理导航 |
| | `kaipai-admin/src/views/referral/RecordsView.vue` | — | ✅ 已接入：页内治理导航 |
| | `kaipai-admin/src/views/referral/EligibilityView.vue` | — | ✅ 已接入：页内治理导航 |
| | `kaipai-admin/src/views/referral/PoliciesView.vue` | — | ✅ 已接入：页内治理导航 |
| 00-45 admin-referral-eligibility-governance-structure-alignment | `.sce/specs/00-45-admin-referral-eligibility-governance-structure-alignment/requirements.md` | — | ✅ 已新增：邀请资格治理页结构对齐需求 |
| | `.sce/specs/00-45-admin-referral-eligibility-governance-structure-alignment/design.md` | — | ✅ 已新增：EligibilityView 结构分层与概览卡设计 |
| | `.sce/specs/00-45-admin-referral-eligibility-governance-structure-alignment/tasks.md` | — | ✅ 已新增：EligibilityView 结构对齐任务 |
| | `.sce/specs/00-45-admin-referral-eligibility-governance-structure-alignment/execution.md` | — | ✅ 已新增：EligibilityView 结构对齐执行记录 |
| | `kaipai-admin/src/views/referral/EligibilityView.vue` | — | ✅ 已完成：补治理概览卡并把手工发放提升为页级主操作 |
| 00-46 admin-page-container-intro-removal | `.sce/specs/00-46-admin-page-container-intro-removal/requirements.md` | — | ✅ 已新增：后台页面介绍模块移除需求 |
| | `.sce/specs/00-46-admin-page-container-intro-removal/design.md` | — | ✅ 已新增：PageContainer 统一移除介绍模块设计 |
| | `.sce/specs/00-46-admin-page-container-intro-removal/tasks.md` | — | ✅ 已新增：PageContainer 介绍模块移除任务 |
| | `.sce/specs/00-46-admin-page-container-intro-removal/execution.md` | — | ✅ 已新增：PageContainer 介绍模块移除执行记录 |
| | `kaipai-admin/src/components/business/PageContainer.vue` | — | ✅ 已完成：统一移除顶部介绍模块，仅保留轻量 actions 行 |
| 00-47 admin-page-container-intro-prop-cleanup | `.sce/specs/00-47-admin-page-container-intro-prop-cleanup/requirements.md` | — | ✅ 已新增：后台 PageContainer 死参清理需求 |
| | `.sce/specs/00-47-admin-page-container-intro-prop-cleanup/design.md` | — | ✅ 已新增：PageContainer 调用点死参清理设计 |
| | `.sce/specs/00-47-admin-page-container-intro-prop-cleanup/tasks.md` | — | ✅ 已新增：PageContainer 死参清理任务 |
| | `.sce/specs/00-47-admin-page-container-intro-prop-cleanup/execution.md` | — | ✅ 已新增：PageContainer 死参清理执行记录 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题与描述传参 |
| | `kaipai-admin/src/views/payment/OrdersView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题与描述传参 |
| | `kaipai-admin/src/views/payment/TransactionsView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题与描述传参 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题与描述传参 |
| | `kaipai-admin/src/views/system/OperationLogsView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题与描述传参 |
| | `kaipai-admin/src/views/system/AiResumeGovernanceView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题、eyebrow 与描述传参 |
| | `kaipai-admin/src/views/system/AdminUsersView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题与描述传参 |
| | `kaipai-admin/src/views/membership/ProductsView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题与描述传参 |
| | `kaipai-admin/src/views/membership/AccountsView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题与描述传参 |
| | `kaipai-admin/src/views/refund/OrdersView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题与描述传参 |
| | `kaipai-admin/src/views/refund/LogsView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题与描述传参 |
| | `kaipai-admin/src/views/referral/EligibilityView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题、eyebrow 与描述传参 |
| | `kaipai-admin/src/views/referral/PoliciesView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题、eyebrow 与描述传参 |
| | `kaipai-admin/src/views/referral/RecordsView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题、eyebrow 与描述传参 |
| | `kaipai-admin/src/views/referral/RiskView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题、eyebrow 与描述传参 |
| | `kaipai-admin/src/views/recruit/AppliesView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题、eyebrow 与描述传参 |
| | `kaipai-admin/src/views/recruit/RolesView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题、eyebrow 与描述传参 |
| | `kaipai-admin/src/views/recruit/ProjectsView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题、eyebrow 与描述传参 |
| | `kaipai-admin/src/views/shared/PlaceholderView.vue` | — | ✅ 已完成：删除仅服务于 PageContainer 标题区的无用导入和路由文案 |
| | `kaipai-admin/src/views/verify/VerificationBoard.vue` | — | ✅ 已完成：删除仅服务于 PageContainer 标题区的无用文案依赖 |
| | `kaipai-admin/src/views/content/TemplatesView.vue` | — | ✅ 已完成：移除 PageContainer 残留标题与描述传参 |
| 00-48 current-phase-wechat-capability-deferral | `.sce/specs/00-48-current-phase-wechat-capability-deferral/requirements.md` | — | ✅ 已新增：当前阶段微信能力降级出主阻塞需求 |
| | `.sce/specs/00-48-current-phase-wechat-capability-deferral/design.md` | — | ✅ 已新增：微信能力降级与路线图回写设计 |
| | `.sce/specs/00-48-current-phase-wechat-capability-deferral/tasks.md` | — | ✅ 已新增：微信能力降级任务 |
| | `.sce/specs/00-48-current-phase-wechat-capability-deferral/execution.md` | — | ✅ 已新增：微信能力降级执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md` | — | ✅ 已完成：移除 invite/login-auth 微信门禁作为当前阶段第一优先级 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将微信能力改写为后续能力批次，当前主风险切回 membership/AI/verify |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/invite-status.md` | — | ✅ 已完成：将 `wxacode` 从当前阶段主阻塞降级为后续能力批次 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/login-auth-status.md` | — | ✅ 已完成：将微信登录从当前阶段主阻塞降级为后续能力批次 |
| | `.sce/runbooks/backend-admin-release/wechat-config-gate-runbook.md` | — | ✅ 已完成：明确仅在显式推进微信能力批次时启用 |
| 00-49 membership-preview-overlay-fact-source-boundary | `.sce/specs/00-49-membership-preview-overlay-fact-source-boundary/requirements.md` | — | ✅ 已新增：membership `preview overlay` 事实源边界需求 |
| | `.sce/specs/00-49-membership-preview-overlay-fact-source-boundary/design.md` | — | ✅ 已新增：后端事实层与前端 session 预览层双层模型设计 |
| | `.sce/specs/00-49-membership-preview-overlay-fact-source-boundary/tasks.md` | — | ✅ 已新增：membership 事实源边界任务 |
| | `.sce/specs/00-49-membership-preview-overlay-fact-source-boundary/execution.md` | — | ✅ 已新增：membership 事实源边界执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md` | — | ✅ 已完成：将 membership 第一优先级正式挂到 `00-49` 入口 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/membership-status.md` | — | ✅ 已完成：将 preview overlay 风险明确绑定到 `00-49` 事实源边界 |
| 00-50 ai-resume-governance-collaboration-upgrade | `.sce/specs/00-50-ai-resume-governance-collaboration-upgrade/requirements.md` | — | ✅ 已新增：AI 简历治理协同升级需求 |
| | `.sce/specs/00-50-ai-resume-governance-collaboration-upgrade/design.md` | — | ✅ 已新增：通知回执、自动催办与 SLA 升级设计 |
| | `.sce/specs/00-50-ai-resume-governance-collaboration-upgrade/tasks.md` | — | ✅ 已新增：AI 治理协同升级任务 |
| | `.sce/specs/00-50-ai-resume-governance-collaboration-upgrade/execution.md` | — | ✅ 已新增：AI 治理协同升级执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/ai-resume-status.md` | — | ✅ 已完成：将 AI 治理剩余 blocker 明确绑定到 `00-50` 协同升级入口 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/execution/ai-resume/README.md` | — | ✅ 已完成：将 AI 协同后续实现入口显式收口到 `00-50` |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将 AI 治理协同主风险提升为独立治理入口 |
| 00-51 current-phase-formal-sms-capability-deferral | `.sce/specs/00-51-current-phase-formal-sms-capability-deferral/requirements.md` | — | ✅ 已新增：当前阶段正式短信能力降级出主阻塞需求 |
| | `.sce/specs/00-51-current-phase-formal-sms-capability-deferral/design.md` | — | ✅ 已新增：当前阶段 / 未来全量双层闭环设计 |
| | `.sce/specs/00-51-current-phase-formal-sms-capability-deferral/tasks.md` | — | ✅ 已新增：正式短信能力降级任务 |
| | `.sce/specs/00-51-current-phase-formal-sms-capability-deferral/execution.md` | — | ✅ 已新增：正式短信能力降级执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/slices/login-auth-capability-slice.md` | — | ✅ 已完成：将 login-auth 完成定义拆成“当前阶段闭环完成 / 未来全量闭环完成” |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/login-auth-status.md` | — | ✅ 已完成：将 login-auth 当前判定推进为“当前阶段闭环完成”，正式短信转为未来批次 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/execution/login-auth/real-env-validation-checklist.md` | — | ✅ 已完成：将验证清单改写为“当前阶段闭环 / 未来正式短信批次”双层口径 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将登录链路剩余正式短信风险提升为 `00-51` 独立入口 |
| 00-52 current-phase-invite-record-page-boundary-alignment | `.sce/specs/00-52-current-phase-invite-record-page-boundary-alignment/requirements.md` | — | ✅ 已新增：当前阶段 invite 记录页边界校正需求 |
| | `.sce/specs/00-52-current-phase-invite-record-page-boundary-alignment/design.md` | — | ✅ 已新增：当前阶段 invite 页面分工与历史兼容设计 |
| | `.sce/specs/00-52-current-phase-invite-record-page-boundary-alignment/tasks.md` | — | ✅ 已新增：invite 当前阶段边界校正任务 |
| | `.sce/specs/00-52-current-phase-invite-record-page-boundary-alignment/execution.md` | — | ✅ 已新增：invite 当前阶段边界校正执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md` | — | ✅ 已完成：将 invite 第三优先级改写为 `00-52` 记录页边界治理 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md` | — | ✅ 已完成：新增 `00-52` 回填记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/slices/invite-referral-capability-slice.md` | — | ✅ 已完成：明确 invite 当前阶段为“记录页 + 登录承接邀请码 + 分享入口分散在 actor-card/membership” |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/invite-status.md` | — | ✅ 已完成：移除 invite 页仍承担分享闭环的旧口径 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将 invite 当前主缺口改写为页面边界与历史兼容治理 |
| | `.sce/specs/05-12-share-invite-code-consolidation/requirements.md` | — | ✅ 已完成：标记 05-12 为历史收口 Spec，当前阶段以 `00-52` 为准 |
| | `.sce/specs/05-12-share-invite-code-consolidation/design.md` | — | ✅ 已完成：标记 05-12 为历史收口 Spec，当前阶段以 `00-52` 为准 |
| | `.sce/specs/05-12-share-invite-code-consolidation/tasks.md` | — | ✅ 已完成：标记 05-12 为历史收口 Spec，当前阶段以 `00-52` 为准 |
| | `.sce/specs/05-12-share-invite-code-consolidation/execution.md` | — | ✅ 已完成：标记 05-12 为历史收口 Spec，当前阶段以 `00-52` 为准 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/card/support/CurrentPhaseShareArtifactSupport.java` | — | ✅ 已新增：后端当前阶段 artifact 单一口径 helper |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorPersonalizationServiceImpl.java` | — | ✅ 已完成：`/api/card/personalization` 仅返回当前阶段两种分享产物 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java` | — | ✅ 已完成：保存偏好时把 `preferredArtifact` 归一化到当前阶段口径 |
| | `kaipai-frontend/src/types/personalization.ts` | — | ✅ 已完成：当前阶段 `ShareArtifactType` 仅保留 `miniProgramCard / poster` |
| | `kaipai-frontend/src/utils/personalization.ts` | — | ✅ 已完成：真接口返回的 legacy artifacts 已在前端收口为当前阶段两种分享产物 |
| 00-63 current-phase-share-card-latest-state-alignment | `.sce/specs/00-63-current-phase-share-card-latest-state-alignment/requirements.md` | — | ✅ 已新增：分享页最新态对齐需求 |
| | `.sce/specs/00-63-current-phase-share-card-latest-state-alignment/design.md` | — | ✅ 已新增：分享页 latest snapshot 单一读取链设计 |
| | `.sce/specs/00-63-current-phase-share-card-latest-state-alignment/tasks.md` | — | ✅ 已新增：分享页最新态对齐任务 |
| | `.sce/specs/00-63-current-phase-share-card-latest-state-alignment/execution.md` | — | ✅ 已新增：分享页最新态对齐执行记录 |
| | `kaipai-frontend/src/utils/share-card-latest.ts` | — | ✅ 已新增：`shareCardId -> personalization -> actor detail` 共享 latest snapshot loader |
| | `kaipai-frontend/src/pages/actor-profile/detail.vue` | — | ✅ 已完成：公开分享页改为消费共享 latest snapshot |
| | `kaipai-frontend/src/pkg-card/actor-card/index.vue` | — | ✅ 已完成：编辑页加载、onShow 刷新与保存后刷新改为消费共享 latest snapshot |
| 00-64 current-phase-actor-card-editor-boundary-alignment | `.sce/specs/00-64-current-phase-actor-card-editor-boundary-alignment/requirements.md` | — | ✅ 已新增：分享卡编辑页边界对齐需求 |
| | `.sce/specs/00-64-current-phase-actor-card-editor-boundary-alignment/design.md` | — | ✅ 已新增：单卡编辑页边界收口与最小编辑能力设计 |
| | `.sce/specs/00-64-current-phase-actor-card-editor-boundary-alignment/tasks.md` | — | ✅ 已新增：编辑页边界收口任务 |
| | `.sce/specs/00-64-current-phase-actor-card-editor-boundary-alignment/execution.md` | — | ✅ 已新增：编辑页边界收口执行记录 |
| | `kaipai-frontend/src/pkg-card/actor-card/index.vue` | — | ✅ 已完成首轮：移除旧会员/命理/受众视角噪音，并补齐代表照片、高亮经历与预览公开页入口 |
| | `kaipai-frontend/src/components/KpColorPalettePicker.vue` | — | ✅ 已完成：默认文案改为“保存后同步到公开名片”的当前阶段口径 |
| | `kaipai-frontend/src/pages/actor-profile/detail.vue` | — | ✅ 已复用：作为真实公开预览落点继续承接 `shareCardId` 跳转 |
| 00-65 current-phase-share-card-multi-instance-refactor | `.sce/specs/00-65-current-phase-share-card-multi-instance-refactor/requirements.md` | — | ✅ 已新增：分享卡多实例模型重构需求 |
| | `.sce/specs/00-65-current-phase-share-card-multi-instance-refactor/design.md` | — | ✅ 已新增：模板资格与卡片实例解耦设计 |
| | `.sce/specs/00-65-current-phase-share-card-multi-instance-refactor/tasks.md` | — | ✅ 已新增：多实例模型重构任务 |
| | `.sce/specs/00-65-current-phase-share-card-multi-instance-refactor/execution.md` | — | ✅ 已新增：多实例模型重构执行记录 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/UserShareCardServiceImpl.java` | — | 🟡 待执行：`createCard()` 从 ensure 语义改为真实新建实例 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java` | — | 🟡 待执行：默认卡、实例配置绑定与最新配置读写适配多实例模型 |
| | `kaipai-frontend/src/pkg-card/card-list/index.vue` | — | 🟡 待执行：列表从按风格唯一视角调整为真实卡片实例列表 |
| | `kaipai-admin/src/views/content/ShareCardsView.vue` | — | 🟡 待执行：后台治理页适配同模板多实例视角 |
| 00-66 current-phase-share-theme-request-fact-investigation | `.sce/specs/00-66-current-phase-share-theme-request-fact-investigation/requirements.md` | — | ✅ 已新增：分享主题映射请求事实调查需求 |
| | `.sce/specs/00-66-current-phase-share-theme-request-fact-investigation/design.md` | — | ✅ 已新增：保存链 / 聚合链 / 页面消费链调查设计 |
| | `.sce/specs/00-66-current-phase-share-theme-request-fact-investigation/tasks.md` | — | ✅ 已新增：请求事实调查任务 |
| | `.sce/specs/00-66-current-phase-share-theme-request-fact-investigation/execution.md` | — | ✅ 已新增：请求事实调查执行记录 |
| 00-67 current-phase-share-theme-semantic-alignment | `.sce/specs/00-67-current-phase-share-theme-semantic-alignment/requirements.md` | — | ✅ 已新增：分享主题语义对齐需求 |
| | `.sce/specs/00-67-current-phase-share-theme-semantic-alignment/design.md` | — | ✅ 已新增：三色语义、单一主题事实源与页面消费设计 |
| | `.sce/specs/00-67-current-phase-share-theme-semantic-alignment/tasks.md` | — | ✅ 已新增：主题语义对齐任务 |
| | `.sce/specs/00-67-current-phase-share-theme-semantic-alignment/execution.md` | — | ✅ 已新增：主题语义对齐执行记录 |
| 00-68 current-phase-share-runtime-and-poster-capability-alignment | `.sce/specs/00-68-current-phase-share-runtime-and-poster-capability-alignment/requirements.md` | — | ✅ 已新增：分享运行时断裂与海报能力口径对齐需求 |
| | `.sce/specs/00-68-current-phase-share-runtime-and-poster-capability-alignment/design.md` | — | ✅ 已新增：分享公开链事实源与海报能力统一设计 |
| | `.sce/specs/00-68-current-phase-share-runtime-and-poster-capability-alignment/tasks.md` | — | ✅ 已新增：运行时与海报能力整改任务 |
| | `.sce/specs/00-68-current-phase-share-runtime-and-poster-capability-alignment/execution.md` | — | ✅ 已新增：运行时与海报能力整改执行记录 |
| 00-69 current-phase-share-analytics-architecture-refactor | `.sce/specs/00-69-current-phase-share-analytics-architecture-refactor/requirements.md` | — | ✅ 已新增：分享与数据分析架构重构需求 |
| | `.sce/specs/00-69-current-phase-share-analytics-architecture-refactor/design.md` | — | ✅ 已新增：前端/后台/后端 active 架构与旧代码删除边界设计 |
| | `.sce/specs/00-69-current-phase-share-analytics-architecture-refactor/tasks.md` | — | ✅ 已新增：整体重构与旧代码盘点任务 |
| | `.sce/specs/00-69-current-phase-share-analytics-architecture-refactor/execution.md` | — | ✅ 已新增：整体重构首轮调查执行记录 |
| 00-70 current-phase-share-prototype-ui-implementation | `.sce/specs/00-70-current-phase-share-prototype-ui-implementation/requirements.md` | — | ✅ 已新增：按 `_-_.html` 落地当前阶段分享原型 UI 需求 |
| | `.sce/specs/00-70-current-phase-share-prototype-ui-implementation/design.md` | — | ✅ 已新增：7 页原型与真实路由映射、视觉系统与分阶段实现设计 |
| | `.sce/specs/00-70-current-phase-share-prototype-ui-implementation/tasks.md` | — | ✅ 已新增：原型 UI 落地任务拆分 |
| | `.sce/specs/00-70-current-phase-share-prototype-ui-implementation/execution.md` | — | ✅ 已新增：首轮 7 页落地与验证执行记录 |
| | `kaipai-frontend/src/pages/login/index.vue` | — | ✅ 已落首轮原型 UI：登录 / 注册页 |
| | `kaipai-frontend/src/pages/home/index.vue` | — | ✅ 已落首轮原型 UI：首页 |
| | `kaipai-frontend/src/pages/history/index.vue` | — | ✅ 已落首轮原型 UI：记录页 |
| | `kaipai-frontend/src/pages/mine/index.vue` | — | ✅ 已落首轮原型 UI：我的页 |
| | `kaipai-frontend/src/pkg-card/card-list/index.vue` | — | ✅ 已落首轮原型 UI：创建分享页 |
| | `kaipai-frontend/src/pages/actor-profile/detail.vue` | — | ✅ 已落首轮原型 UI：卡片预览页 |
| | `kaipai-frontend/src/pkg-card/actor-card/index.vue` | — | ✅ 已落首轮原型 UI：海报预览 / 分享预览页 |
| | `kaipai-frontend/src/pages/actor-profile/edit.vue` | — | ✅ 已完成：原型外但当前 active 的档案编辑页视觉系统收口 |
| | `kaipai-frontend/src/pkg-card/verify/index.vue` | — | ✅ 已完成：原型外但当前兼容支撑的实名认证页视觉系统收口 |
| | `kaipai-frontend/src/pages/role-select/index.vue` | — | ✅ 已完成：历史兼容身份落位页视觉系统收口 |
| | `kaipai-frontend/src/pkg-tools/webview/index.vue` | — | ✅ 已完成：原型外但当前 active 的协议说明工具页视觉系统收口 |
| | `kaipai-frontend/src/pkg-tools/video-player/index.vue` | — | ✅ 已完成：原型外但当前 active 的视频预览工具页视觉系统收口 |
| | `kaipai-frontend/src/pages/actor-profile/components/ProfileCompletionBar.vue` | — | ✅ 已完成：档案编辑页完整度卡视觉系统收口 |
| | `kaipai-frontend/src/pages/actor-profile/components/BasicInfoSection.vue` | — | ✅ 已完成：档案编辑页基础信息区视觉系统收口 |
| | `kaipai-frontend/src/pages/actor-profile/components/SkillTagSection.vue` | — | ✅ 已完成：档案编辑页擅长与介绍区视觉系统收口 |
| | `kaipai-frontend/src/pages/actor-profile/components/AppearanceTagSection.vue` | — | ✅ 已完成：档案编辑页形象标签区视觉系统收口 |
| | `kaipai-frontend/src/pages/actor-profile/components/PhotoCategorySection.vue` | — | ✅ 已完成：档案编辑页照片分类区视觉系统收口 |
| | `kaipai-frontend/src/pages/actor-profile/components/WorkExperienceSection.vue` | — | ✅ 已完成：档案编辑页拍摄经历区视觉系统收口 |
| | `kaipai-frontend/src/pages/actor-profile/components/VideoResumeSection.vue` | — | ✅ 已完成：档案编辑页视频简历区视觉系统收口 |
| | `kaipai-frontend/src/components/KpIdentityStatusCard.vue` | — | ✅ 已完成：实名认证状态卡视觉系统收口 |
| | `kaipai-frontend/src/pages.json` | — | ✅ 已完成：tabBar 文案与浅色底收口到原型口径 |
| 00-71 admin-console-reference-ui-implementation | `.sce/specs/00-71-admin-console-reference-ui-implementation/requirements.md` | — | ✅ 已新增：按 `_-_1.html` 落地后台控制台 UI 需求，并固化“只承接已有功能”边界 |
| | `.sce/specs/00-71-admin-console-reference-ui-implementation/design.md` | — | ✅ 已新增：后台壳层、工作台结构与实现边界设计 |
| | `.sce/specs/00-71-admin-console-reference-ui-implementation/tasks.md` | — | ✅ 已新增：后台控制台参考稿 UI 落地任务拆分 |
| | `.sce/specs/00-71-admin-console-reference-ui-implementation/execution.md` | — | ✅ 已新增：后台控制台首轮落地与验证执行记录 |
| | `kaipai-admin/src/stores/permission.ts` | — | ✅ 已改造：侧栏直接承接权限过滤后的真实菜单，避免只展示局部入口 |
| | `kaipai-admin/src/layouts/AdminLayout.vue` | — | ✅ 已改造：后台主内容壳层升级为参考稿控制台画布 |
| | `kaipai-admin/src/components/layout/AdminSidebar.vue` | — | ✅ 已改造：窄侧栏、分组导航与账号区对齐参考稿控制台结构 |
| | `kaipai-admin/src/components/layout/AdminTopbar.vue` | — | ✅ 已改造：轻量状态条、日期 / 角色 / 账号信息重排 |
| | `kaipai-admin/src/styles/index.scss` | — | ✅ 已改造：背景、表单与全局面板节奏对齐新的控制台基线 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已改造：工作台按参考稿重组为数据看板式结构，仍只使用当前已有 dashboard 字段 |
| 00-72 current-phase-admin-information-architecture-alignment | `.sce/specs/00-72-current-phase-admin-information-architecture-alignment/requirements.md` | — | ✅ 已新增：固化后台登录后主架构只保留“控制台 / 渠道分析 + 用户中心”，并定义旧业务域退出边界 |
| | `.sce/specs/00-72-current-phase-admin-information-architecture-alignment/design.md` | — | ✅ 已新增：后台主导航、页面分类矩阵与 tooling 保留边界设计 |
| | `.sce/specs/00-72-current-phase-admin-information-architecture-alignment/tasks.md` | — | ✅ 已新增：后台信息架构收口任务拆分 |
| | `.sce/specs/00-72-current-phase-admin-information-architecture-alignment/execution.md` | — | ✅ 已新增：记录主导航收口、顶部语义调整与工作台主入口清理执行结果 |
| | `.sce/specs/00-72-current-phase-admin-information-architecture-alignment/route-audit-matrix.md` | — | ✅ 已新增：登录后路由首轮审计矩阵，区分主架构保留、tooling 保留与删除候选 |
| | `kaipai-admin/src/constants/admin-information-architecture.ts` | — | ✅ 已改造：统一后台主架构路径语义，并把 tooling 顶部文案细分为治理工具语义 |
| | `kaipai-admin/src/constants/menus.ts` | — | ✅ 已改造：保留原始能力库存与 `adminSidebarMenus` 主导航投影分层，并补充更明确的 tooling 菜单语义 |
| | `kaipai-admin/src/stores/permission.ts` | — | ✅ 已改造：侧栏菜单改为消费 `adminSidebarMenus`，并补 `getAccessMode()` 区分 direct / fallback / denied |
| | `kaipai-admin/src/utils/permission.ts` | — | ✅ 已改造：新增 `getPermissionAccessMode()`，统一 direct / fallback / denied 判断 |
| | `kaipai-admin/src/router/index.ts` | — | ✅ 已补主架构分层，并按 tooling / mainline 语义收口 route title；已根据依赖审计删除 `verify/history`、`payment/transactions`、`refund/logs` 运行时路由 |
| | `kaipai-admin/src/views/auth/LoginView.vue` | — | ✅ 已改造：登录后默认跳转改为优先使用当前账号 `landingPath` |
| | `kaipai-admin/src/views/common/ForbiddenView.vue` | — | ✅ 已改造：无权限页支持返回可用页面或退出重新登录 |
| | `kaipai-admin/src/components/layout/AdminSidebar.vue` | — | ✅ 已改造：左侧主导航只表达当前阶段两类顶层语义 |
| | `kaipai-admin/src/components/layout/AdminTopbar.vue` | — | ✅ 已改造：顶部眉标与说明改为“控制台 / 用户中心 / 治理工具”三类语义 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已改造：dashboard 快捷入口、趋势和动态区切回当前主架构与治理工具双层表达 |
| | `kaipai-admin/src/router/guard.ts` | — | ✅ 已删除：移除未被 `main.ts` 安装的旧路由守卫，避免双轨逻辑漂移 |
| | `kaipai-admin/src/views/content/TemplatesView.vue` | — | ✅ 已确认：模板治理页继续维护 `sceneKey / requiredInviteCount / membershipRequired / baseThemeJson / artifactPresetJson` 等当前 runtime 配置 |
| | `kaipai-admin/src/views/content/DefaultGeneralCardView.vue` | — | ✅ 已确认：默认普通卡治理页继续承接策略摘要、单用户检查与补偿动作 |
| | `kaipai-admin/src/views/recruit/ProjectsView.vue` | — | ✅ 已改造：页面内显式提示项目页 / 状态处置是否仍通过 `page.system.admin-users` fallback 兼容访问 |
| | `kaipai-admin/src/views/recruit/RolesView.vue` | — | ✅ 已改造：页面内显式提示角色页 / 状态处置是否仍通过 `page.system.admin-users` fallback 兼容访问 |
| | `kaipai-admin/src/views/recruit/AppliesView.vue` | — | ✅ 已改造：页面内显式提示投递链路页是否仍通过 `page.system.admin-users` fallback 兼容访问 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/system/dto/AdminRoleRecruitGovernanceMatrixItemDTO.java` | — | ✅ 已改造：补充 page/action ready 与 page/action fallback 字段，作为招募矩阵后端事实源 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/system/dto/AdminRoleRecruitGovernanceMatrixRespDTO.java` | — | ✅ 已改造：补充 page/action ready/fallback 聚合计数与 `canRetirePageFallback / canRetireActionFallback` 双 gating 信号 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/system/service/impl/AdminRoleServiceImpl.java` | — | ✅ 已改造：招募矩阵改按 `page.recruit.*` / `action.recruit.*` 计算 ready 与 missing，`menu.recruit` 降级为历史登记信息 |
| | `kaipaile-server/src/main/java/com/kaipai/common/auth/RecruitGovernanceFallbackGate.java` | — | ✅ 已改造：按招募矩阵 gating 动态决定是否继续允许 legacy page/action fallback |
| | `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/recruit/AdminRecruitController.java` | — | ✅ 已改造：列表接口与状态处置接口都改为优先独立 page/action 权限，仅在 gating 允许时继续接受 `page.system.admin-users` fallback |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/adminauth/dto/AdminSessionInfoDTO.java` | — | ✅ 已改造：补充 `allowLegacyRecruitPageFallback / allowLegacyRecruitActionFallback` 会话级 gating 字段 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/adminauth/service/impl/AdminAuthServiceImpl.java` | — | ✅ 已改造：后台会话生成时同步下发招募 page/action fallback gating 信号 |
| | `kaipai-admin/src/types/admin.ts` | — | ✅ 已改造：补充后台会话中的招募 fallback gating 字段 |
| | `kaipai-admin/src/stores/permission.ts` | — | ✅ 已改造：根据后台会话动态解析 recruit page/action fallback，菜单/路由守卫/landing path 共享同一 gating 口径 |
| | `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java` | — | ✅ 已确认：模板治理与默认普通卡治理接口仍在当前后台运行时开放 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/CardSceneTemplateServiceImpl.java` | — | ✅ 已确认：模板 `requiredInviteCount / baseThemeJson / artifactPresetJson` 仍直接进入分享卡 runtime |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/UserShareCardServiceImpl.java` | — | ✅ 已确认：分享卡创建仍受模板邀请门槛 gating，默认普通卡不能视为历史废弃工具 |
| | `kaipai-admin/src/views/verify/HistoryView.vue` | — | 🗑 已删除：实名认证历史独立页已回收到待审页内的状态筛选回看模式 |
| | `kaipai-admin/src/views/verify/VerifyListView.vue` | — | 🗑 已删除：未被路由引用的历史包装页已一并清理 |
| | `kaipai-admin/src/views/verify/VerificationBoard.vue` | — | ✅ 已改造：待审页可在同一页承接历史回看语义，替代独立 history 路由 |
| | `kaipai-admin/src/views/payment/TransactionsView.vue` | — | 🗑 已删除：支付流水独立页已退场，关联流水回看改由订单详情承接 |
| | `kaipai-admin/src/views/refund/LogsView.vue` | — | 🗑 已删除：退款日志独立页已退场，操作日志回看改由退款详情承接 |
| | `kaipai-admin/src/api/payment.ts` | — | ✅ 已清理：删除仅支付流水独立页使用的查询/详情函数 |
| | `kaipai-admin/src/api/refund.ts` | — | ✅ 已清理：删除仅退款日志独立页使用的查询函数 |
| | `kaipai-admin/src/types/payment.ts` | — | ✅ 已清理：删除仅支付流水独立页使用的 query/detail 类型，保留订单详情所需流水列表结构 |
| | `kaipai-admin/src/types/refund.ts` | — | ✅ 已清理：删除仅退款日志独立页使用的 query/pageResult 类型，保留退款详情所需日志项结构 |
| | `kaipai-admin/src/api/membership.ts` | — | 🗑 已删除：membership 域前端接口已退场 |
| | `kaipai-admin/src/types/membership.ts` | — | 🗑 已删除：membership 域前端类型已退场 |
| | `kaipai-admin/src/views/membership/ProductsView.vue` | — | 🗑 已删除：会员产品页已退出当前后台运行时 |
| | `kaipai-admin/src/views/membership/AccountsView.vue` | — | 🗑 已删除：会员账户页已退出当前后台运行时 |
| | `kaipai-admin/src/constants/status.ts` | — | ✅ 已清理：移除仅 membership 页面使用的状态与层级常量 |
| | `kaipai-admin/README.md` | — | ✅ 已同步：移除已退场 membership 页面能力描述 |
| | `kaipai-admin/src/views/content/ShareCardsView.vue` | — | 📝 已归类：作为当前用户中心主保留页之一 |
| | `kaipai-admin/src/views/content/ContactRequestsView.vue` | — | 📝 已归类：作为当前用户中心主保留页之一 |
| | `kaipai-frontend/src/pages/login/index.vue` | — | ✅ 已落首轮原型 UI：登录 / 注册页 |
| | `kaipai-frontend/src/pages/home/index.vue` | — | ✅ 已落首轮原型 UI：首页 |
| | `kaipai-frontend/src/pages/history/index.vue` | — | ✅ 已落首轮原型 UI：记录页 |
| | `kaipai-frontend/src/pages/mine/index.vue` | — | ✅ 已落首轮原型 UI：我的页 |
| | `kaipai-frontend/src/pkg-card/card-list/index.vue` | — | ✅ 已落首轮原型 UI：创建分享页 |
| | `kaipai-frontend/src/pages.json` | — | ✅ 已完成：tabBar 文案与浅色底收口到原型口径 |
| | `kaipai-frontend/src/pkg-card/actor-card/index.vue` | — | 🟡 待调查：`/api/card/config` 请求体与保存链映射事实 |
| | `kaipai-frontend/src/pages/actor-profile/detail.vue` | — | 🟡 待调查：公开页页面消费链事实 |
| | `kaipai-frontend/src/utils/personalization.ts` | — | 🟡 待调查：前端 personalization 转换事实 |
| | `kaipai-frontend/src/utils/theme-resolver.ts` | — | 🟡 待调查：前端 theme token 生成事实 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java` | — | 🟡 待调查：`/api/card/config` 保存/回包事实 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorPersonalizationServiceImpl.java` | — | 🟡 待调查：`/api/card/personalization` 聚合事实 |
| | `kaipai-frontend/src/utils/share-artifact.ts` | — | ✅ 已完成：当前阶段 artifact helper 仅暴露两种分享产物，并保留公开名片 path helper 供 detail 页内部使用 |
| 00-73 current-phase-reference-ui-architecture-rebuild | `.sce/specs/00-73-current-phase-reference-ui-architecture-rebuild/requirements.md` | — | ✅ 已新增：固化前台 reference-driven 的 frame-level UI / 架构二次重构需求 |
| | `.sce/specs/00-73-current-phase-reference-ui-architecture-rebuild/design.md` | — | ✅ 已新增：7 屏 flow、shared visual contract 与 creator chain 路由职责设计 |
| | `.sce/specs/00-73-current-phase-reference-ui-architecture-rebuild/tasks.md` | — | ✅ 已新增：前台 reference 二次重构任务拆分 |
| | `.sce/specs/00-73-current-phase-reference-ui-architecture-rebuild/execution.md` | — | ✅ 已新增：reference 证据、当前 active 路由事实与本轮 handoff 记录 |
| | `kaipai-frontend/src/pages/login/index.vue` | — | 📝 待按本 Spec 收口：frame-level 对齐 `LoginScreen` |
| | `kaipai-frontend/src/pages/home/index.vue` | — | 📝 待按本 Spec 收口：frame-level 对齐 `HomeScreen` |
| | `kaipai-frontend/src/pages/history/index.vue` | — | 📝 待按本 Spec 收口：frame-level 对齐 `RecordsScreen` |
| | `kaipai-frontend/src/pages/mine/index.vue` | — | 📝 待按本 Spec 收口：frame-level 对齐 `MyScreen` |
| | `kaipai-frontend/src/pkg-card/card-list/index.vue` | — | 📝 待按本 Spec 收口：承接 `CreateScreen` 而不是旧列表管理桌面语义 |
| | `kaipai-frontend/src/pkg-card/actor-card/index.vue` | — | 📝 待按本 Spec 收口：统一承接 `CardPreviewScreen / PosterPreviewScreen` |
| | `kaipai-frontend/src/pages/actor-profile/detail.vue` | — | 📝 待按本 Spec 回收：退出 internal creator preview，改回公开 / 兼容详情页 |
| | `kaipai-frontend/src/pages/actor-profile/edit.vue` | — | 📝 待按本 Spec 收口：作为 support route 继承 reference visual contract |
| | `kaipai-frontend/src/pkg-card/verify/index.vue` | — | 📝 待按本 Spec 收口：作为 support route 继承 reference visual contract |
| | `kaipai-frontend/src/pages/role-select/index.vue` | — | 📝 待按本 Spec 收口：作为 support route 继承 reference visual contract |
| | `kaipai-frontend/src/pkg-tools/webview/index.vue` | — | 📝 待按本 Spec 收口：作为 support route 继承 reference visual contract |
| | `kaipai-frontend/src/pkg-tools/video-player/index.vue` | — | 📝 待按本 Spec 收口：作为 support route 继承 reference visual contract |
| | `kaipai-frontend/src/styles/_tokens.scss` | — | 📝 待按本 Spec 收口：补 reference `studio` token 与 serif display fallback |
| | `kaipai-frontend/src/styles/index.scss` | — | 📝 待按本 Spec 收口：统一 safe-area / tabbar / shared visual grammar |
| | `kaipai-frontend/src/components/KpButton.vue` | — | 📝 待按本 Spec 收口：统一 primary / accent / ghost / light 合同 |
| | `kaipai-frontend/src/components/KpPillSelector.vue` | — | 📝 待按本 Spec 收口：统一 filter / mode pill 合同 |
| | `kaipai-frontend/src/components/KpSectionHead.vue` | — | 📝 待按本 Spec 收口：统一 serif title + mono side label 语法 |
| | `kaipai-frontend/src/pages.json` | — | 📝 待按本 Spec 收口：active 路由语义、creator chain 与 support route 边界 |
| 00-74 current-phase-admin-reference-ui-architecture-rebuild | `.sce/specs/00-74-current-phase-admin-reference-ui-architecture-rebuild/requirements.md` | — | ✅ 已新增：固化后台 reference-driven 的 8 页 UI / IA 二次重构需求 |
| | `.sce/specs/00-74-current-phase-admin-reference-ui-architecture-rebuild/design.md` | — | ✅ 已新增：后台正式导航、reference 页面映射与 capability 重组设计 |
| | `.sce/specs/00-74-current-phase-admin-reference-ui-architecture-rebuild/tasks.md` | — | ✅ 已新增：后台 reference-driven 二次重构任务 |
| | `.sce/specs/00-74-current-phase-admin-reference-ui-architecture-rebuild/execution.md` | — | ✅ 已新增：后台运行态对比、`/admin/users` 事实源与机构缺口记录 |
| | `kaipai-admin/src/router/index.ts` | — | ✅ 已完成首轮：补正式路由骨架，并将 `/users/orgs` 从 placeholder route 回接到真实机构目录页 |
| | `kaipai-admin/src/constants/menus.ts` | — | ✅ 已完成首轮：正式侧栏投影恢复到 `OVERVIEW / GROWTH / OPERATE`，并纳入 reference 的 8 个页面状态 |
| | `kaipai-admin/src/types/admin.ts` | — | ✅ 已完成：`AdminMenuItem` 补 section 字段，支撑正式侧栏按 reference 分组 |
| | `kaipai-admin/src/constants/permission-registry.ts` | — | ✅ 已完成首轮：补 `users` 模块与 `page.users.index / page.users.detail` 登记，避免用户管理继续落入未知权限 |
| | `kaipai-admin/src/stores/permission.ts` | — | ✅ 已复用：继续沿用现有权限过滤逻辑承接新的正式侧栏投影，无需新增第二套菜单过滤链 |
| | `kaipai-admin/src/layouts/AdminLayout.vue` | — | ✅ 已完成最新壳层收紧：主区 padding、content shell padding/radius/shadow 已压缩，并通过 `dashboard-index-shell-verify.png` 做浏览器取证 |
| | `kaipai-admin/src/components/layout/AdminSidebar.vue` | — | ✅ 已完成首轮：恢复 `OVERVIEW / GROWTH / OPERATE` 正式侧栏结构 |
| | `kaipai-admin/src/components/layout/AdminSidebar.vue` | — | ✅ 已完成第二轮：footer 已收紧为 reference 风格的身份徽记 + 角色文案 + 轻量尾按钮结构 |
| | `kaipai-admin/src/components/layout/AdminSidebar.vue` | — | ✅ 已完成最新壳层复核：侧栏宽度、折叠宽度、brand、菜单项与 footer 留白已收紧，运行态未出现文字拥挤或破版 |
| | `kaipai-admin/src/components/layout/AdminTopbar.vue` | — | ✅ 已完成首轮：补回 reference 顶控里的搜索 / 窗口 / 通知 / 导出语义；dashboard 窗口已通过 route query 真实联动，搜索 / 导出仍显式降级 |
| | `kaipai-admin/src/constants/admin-information-architecture.ts` | — | ✅ 已完成首轮：从 `dashboard-analytics + user-center + tooling` 切换到 `overview / growth / operate / tooling` 分层，并细化 `机构管理 / 用户管理 / 风格模板 / 运营动作 / 系统设置` 顶部语义 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成首轮：从 shrink-phase 说明页回收为 reference 仪表盘，并显式标注留存 / 渠道事实缺口；页内重复时间工具条已上移至顶控 route query |
| | `kaipai-admin/src/views/user/UserCenterView.vue` | — | ✅ 已完成首轮：从占位页升级为真实 `/admin/users` 业务用户管理页，并接入详情抽屉 |
| | `kaipai-admin/src/views/user/OrganizationsView.vue` | — | ✅ 已完成首轮：从占位页升级为真实机构目录页，只承接已进入招募链路的机构 / 剧组样本 |
| | `kaipai-admin/src/views/content/ShareCardsView.vue` | — | ✅ 已完成首轮：默认改成内容卡片墙表达，治理字段与 legacy 修复下沉为辅助区域 |
| | `kaipai-admin/src/views/content/TemplatesView.vue` | — | ✅ 已完成首轮：默认改成模板库卡片网格，保留真实编辑 / 启停用 / 发布 / 回滚链路 |
| | `kaipai-admin/src/views/dashboard/DashboardAnalyticsView.vue` | — | ✅ 已完成首轮：`/dashboard/analytics` 回接为真实数据分析页，并显式说明渠道块当前仅由 scene 分布近似承接；日期窗口改由顶控 route query 控制，tabs 壳层已轻量化 |
| | `kaipai-admin/src/views/operate/ActionsView.vue` | — | ✅ 已完成首轮：回接为真实运营动作页，只重组现有统计与治理入口 |
| | `kaipai-admin/src/views/system/SettingsView.vue` | — | ✅ 已完成首轮：回接为真实系统设置聚合页，并对缺失事实源与异常接口做降级承接 |
| | `kaipai-admin/src/api/content.ts` | — | ✅ 已完成首轮：补模板启用 / 停用接口装配，支撑模板库卡片动作 |
| | `kaipai-admin/src/api/company.ts` | — | ✅ 已新增：补公司 / 剧组档案读取接口装配，支撑机构管理详情抽屉 |
| | `kaipai-admin/src/api/user-center.ts` | — | ✅ 已核实：已接通 `/admin/users` 真实业务用户中心接口 |
| | `kaipai-admin/src/types/company.ts` | — | ✅ 已新增：补机构档案类型，承接 `/company/{userId}` 返回字段 |
| | `kaipai-admin/src/types/user-center.ts` | — | ✅ 已核实：已具备业务用户中心列表 / 详情类型 |
| | `kaipaile-server/src/main/java/com/kaipai/controller/admin/user/AdminUserController.java` | — | ✅ 已迁移：后台业务用户中心接口真实存在 |
| 00-75 current-phase-admin-reference-shell-density-alignment | `.sce/specs/00-75-current-phase-admin-reference-shell-density-alignment/requirements.md` | — | ✅ 已新增：固化后台桌面主线页标题换行与顶控换行问题，避免继续混入 `00-74` 的 IA 主线 |
| | `.sce/specs/00-75-current-phase-admin-reference-shell-density-alignment/design.md` | — | ✅ 已新增：把桌面壳层密度问题收口为 `AdminTopbar.vue` 的单行对齐与密度收紧设计 |
| | `.sce/specs/00-75-current-phase-admin-reference-shell-density-alignment/tasks.md` | — | ✅ 已新增：后台桌面壳层密度对齐任务链 |
| | `.sce/specs/00-75-current-phase-admin-reference-shell-density-alignment/execution.md` | — | ✅ 已新增：记录修复前运行态截图、问题归因与后续验证证据 |
| | `kaipai-admin/src/components/layout/AdminTopbar.vue` | — | ✅ 已完成首轮：桌面主线页标题与顶控已恢复单行表达，并完成 dashboard / analytics / users / templates 四页浏览器复核 |
| 00-76 current-phase-admin-dashboard-first-screen-density-alignment | `.sce/specs/00-76-current-phase-admin-dashboard-first-screen-density-alignment/requirements.md` | — | ✅ 已新增：固化 dashboard 首屏 `3 + 1` KPI 与双卡密度问题，避免无证据外溢成全局 `page-overview` 重构 |
| | `.sce/specs/00-76-current-phase-admin-dashboard-first-screen-density-alignment/design.md` | — | ✅ 已新增：把 dashboard 首屏密度问题收口为 `OverviewView.vue` 的局部布局覆盖 |
| | `.sce/specs/00-76-current-phase-admin-dashboard-first-screen-density-alignment/tasks.md` | — | ✅ 已新增：dashboard 首屏 page-level 精修任务链 |
| | `.sce/specs/00-76-current-phase-admin-dashboard-first-screen-density-alignment/execution.md` | — | ✅ 已新增：记录修复前 reference 对比与局部覆盖边界 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成首轮：dashboard 首屏已恢复 4 KPI 单行与更紧的双卡密度，并完成真实浏览器复核 |
| 00-77 current-phase-admin-dashboard-secondary-block-alignment | `.sce/specs/00-77-current-phase-admin-dashboard-secondary-block-alignment/requirements.md` | — | ✅ 已新增：固化 dashboard `留存 / 风格偏好 / 渠道分布` 的残余差异，避免回退到共享样式重构 |
| | `.sce/specs/00-77-current-phase-admin-dashboard-secondary-block-alignment/design.md` | — | ✅ 已新增：把次级三块问题收口为 `OverviewView.vue` 的局部结构与样式调整 |
| | `.sce/specs/00-77-current-phase-admin-dashboard-secondary-block-alignment/tasks.md` | — | ✅ 已新增：dashboard 次级三块精修任务链 |
| | `.sce/specs/00-77-current-phase-admin-dashboard-secondary-block-alignment/execution.md` | — | ✅ 已新增：记录修复前 full-page 对比与局部收口边界 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成第二轮：`留存承接 / 风格偏好 / 渠道分布` 已完成局部收口，并完成真实浏览器 full-page 复核 |
| 00-78 current-phase-admin-dashboard-bottom-block-alignment | `.sce/specs/00-78-current-phase-admin-dashboard-bottom-block-alignment/requirements.md` | — | ✅ 已新增：固化 dashboard `正式页面矩阵 / 治理动态` 的残余差异，并明确不能伪造 `TOP CONTENT` |
| | `.sce/specs/00-78-current-phase-admin-dashboard-bottom-block-alignment/design.md` | — | ✅ 已新增：把 dashboard 底部两块收口为 ledger + 轻量 feed 的局部表达 |
| | `.sce/specs/00-78-current-phase-admin-dashboard-bottom-block-alignment/tasks.md` | — | ✅ 已新增：dashboard 底部两块精修任务链 |
| | `.sce/specs/00-78-current-phase-admin-dashboard-bottom-block-alignment/execution.md` | — | ✅ 已新增：记录修复前 full-page 对比、TOP CONTENT 边界与局部收口证据 |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已完成第三轮：`正式页面矩阵 / 治理动态` 已完成局部收口，并完成真实浏览器 full-page 复核 |
| 00-79 current-phase-admin-user-management-first-screen-density-alignment | `.sce/specs/00-79-current-phase-admin-user-management-first-screen-density-alignment/requirements.md` | — | ✅ 已新增：固化 `users/index` 首屏 KPI、segment/快筛与筛选区密度问题 |
| | `.sce/specs/00-79-current-phase-admin-user-management-first-screen-density-alignment/design.md` | — | ✅ 已新增：把用户管理首屏问题收口为 `UserCenterView.vue` 的局部样式与结构密度调整 |
| | `.sce/specs/00-79-current-phase-admin-user-management-first-screen-density-alignment/tasks.md` | — | ✅ 已新增：用户管理首屏精修任务链 |
| | `.sce/specs/00-79-current-phase-admin-user-management-first-screen-density-alignment/execution.md` | — | ✅ 已新增：记录修复前运行态、computed style 证据与局部收口结果 |
| | `kaipai-admin/src/views/user/UserCenterView.vue` | — | ✅ 已完成第二轮：`users/index` KPI 单行 4 卡、segment/快筛与筛选区局部密度已完成收口，并完成真实浏览器复核 |
| 00-80 current-phase-admin-user-management-table-density-alignment | `.sce/specs/00-80-current-phase-admin-user-management-table-density-alignment/requirements.md` | — | ✅ 已新增：固化 `users/index` 主表行高、cell 层级与固定操作列密度问题 |
| | `.sce/specs/00-80-current-phase-admin-user-management-table-density-alignment/design.md` | — | ✅ 已新增：把用户管理表格区问题收口为 `UserCenterView.vue` 的局部表格样式调整 |
| | `.sce/specs/00-80-current-phase-admin-user-management-table-density-alignment/tasks.md` | — | ✅ 已新增：用户管理表格区精修任务链 |
| | `.sce/specs/00-80-current-phase-admin-user-management-table-density-alignment/execution.md` | — | ✅ 已新增：记录修复前运行态量化、修复后量化与局部收口结果 |
| | `kaipai-admin/src/views/user/UserCenterView.vue` | — | ✅ 已完成第三轮：`users/index` 表格区行高、cell 层级与固定操作列已完成局部收口，并完成真实浏览器复核 |
| 00-81 current-phase-admin-template-library-first-screen-alignment | `.sce/specs/00-81-current-phase-admin-template-library-first-screen-alignment/requirements.md` | — | ✅ 已新增：固化 `content/templates` 默认模板库首屏的 shell、筛选区与卡片区密度问题 |
| | `.sce/specs/00-81-current-phase-admin-template-library-first-screen-alignment/design.md` | — | ✅ 已新增：把模板库首屏问题收口为 `TemplatesView.vue` 的局部密度与卡片比例调整 |
| | `.sce/specs/00-81-current-phase-admin-template-library-first-screen-alignment/tasks.md` | — | ✅ 已新增：模板库首屏精修任务链 |
| | `.sce/specs/00-81-current-phase-admin-template-library-first-screen-alignment/execution.md` | — | ✅ 已新增：记录修复前运行态、卡片高度量化与局部收口结果 |
| | `kaipai-admin/src/views/content/TemplatesView.vue` | — | ✅ 已完成第二轮：默认模板库首屏已完成局部收口，并完成真实浏览器复核 |
| 00-82 current-phase-admin-template-library-list-density-alignment | `.sce/specs/00-82-current-phase-admin-template-library-list-density-alignment/requirements.md` | — | ✅ 已新增：固化 `content/templates` 列表视图表格区的行高、编码列与操作区密度问题 |
| | `.sce/specs/00-82-current-phase-admin-template-library-list-density-alignment/design.md` | — | ✅ 已新增：把模板库列表视图问题收口为 `TemplatesView.vue` 的局部表格密度与操作区调整 |
| | `.sce/specs/00-82-current-phase-admin-template-library-list-density-alignment/tasks.md` | — | ✅ 已新增：模板库列表视图精修任务链 |
| | `.sce/specs/00-82-current-phase-admin-template-library-list-density-alignment/execution.md` | — | ✅ 已新增：记录修复前运行态量化、修复后量化与局部收口结果 |
| | `kaipai-admin/src/views/content/TemplatesView.vue` | — | ✅ 已完成第三轮：列表视图表格区已完成局部收口，并完成真实浏览器复核 |
| 00-83 current-phase-admin-share-content-first-screen-alignment | `.sce/specs/00-83-current-phase-admin-share-content-first-screen-alignment/requirements.md` | — | ✅ 已新增：固化 `content/share-cards` 默认卡片墙首屏的 shell、筛选区与卡片比例问题 |
| | `.sce/specs/00-83-current-phase-admin-share-content-first-screen-alignment/design.md` | — | ✅ 已新增：把分享内容首屏问题收口为 `ShareCardsView.vue` 的局部密度与卡片比例调整 |
| | `.sce/specs/00-83-current-phase-admin-share-content-first-screen-alignment/tasks.md` | — | ✅ 已新增：分享内容首屏精修任务链 |
| | `.sce/specs/00-83-current-phase-admin-share-content-first-screen-alignment/execution.md` | — | ✅ 已新增：记录修复前运行态、卡片高度量化与局部收口结果 |
| | `kaipai-admin/src/views/content/ShareCardsView.vue` | — | ✅ 已完成第二轮：默认卡片墙首屏已完成局部收口，并完成真实浏览器复核 |
| 00-84 current-phase-admin-share-content-list-density-alignment | `.sce/specs/00-84-current-phase-admin-share-content-list-density-alignment/requirements.md` | — | ✅ 已新增：固化 `content/share-cards` 列表视图表格区的行高、stacked cell 与操作区密度问题 |
| | `.sce/specs/00-84-current-phase-admin-share-content-list-density-alignment/design.md` | — | ✅ 已新增：把分享内容列表视图问题收口为 `ShareCardsView.vue` 的局部表格密度与操作区调整 |
| | `.sce/specs/00-84-current-phase-admin-share-content-list-density-alignment/tasks.md` | — | ✅ 已回填：列表视图精修任务链已完成 |
| | `.sce/specs/00-84-current-phase-admin-share-content-list-density-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/content/ShareCardsView.vue` | — | ✅ 已完成第三轮：列表视图表格区已完成局部收口，并完成真实浏览器复核 |
| 00-85 current-phase-admin-share-content-detail-drawer-density-alignment | `.sce/specs/00-85-current-phase-admin-share-content-detail-drawer-density-alignment/requirements.md` | — | ✅ 已新增：固化 `content/share-cards` 详情抽屉的壳层、hero 与字段块密度问题 |
| | `.sce/specs/00-85-current-phase-admin-share-content-detail-drawer-density-alignment/design.md` | — | ✅ 已新增：把分享内容详情抽屉问题收口为 `ShareCardsView.vue` 的局部详情密度调整 |
| | `.sce/specs/00-85-current-phase-admin-share-content-detail-drawer-density-alignment/tasks.md` | — | ✅ 已回填：详情抽屉精修任务链已完成 |
| | `.sce/specs/00-85-current-phase-admin-share-content-detail-drawer-density-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/content/ShareCardsView.vue` | — | ✅ 已完成第四轮：详情抽屉已完成局部收口，并完成真实浏览器复核 |
| 00-86 current-phase-admin-operate-actions-first-screen-alignment | `.sce/specs/00-86-current-phase-admin-operate-actions-first-screen-alignment/requirements.md` | — | ✅ 已新增：固化 `operate/actions` 首屏的工具卡、动作推荐和辅助摘要层级问题 |
| | `.sce/specs/00-86-current-phase-admin-operate-actions-first-screen-alignment/design.md` | — | ✅ 已新增：把运营动作首屏问题收口为 `ActionsView.vue` 的局部结构与密度调整 |
| | `.sce/specs/00-86-current-phase-admin-operate-actions-first-screen-alignment/tasks.md` | — | ✅ 已回填：运营动作首屏精修任务链已完成 |
| | `.sce/specs/00-86-current-phase-admin-operate-actions-first-screen-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/operate/ActionsView.vue` | — | ✅ 已完成第二轮：运营动作首屏已完成局部收口，并完成真实浏览器复核 |
| 00-87 current-phase-admin-operate-actions-governance-ledger-alignment | `.sce/specs/00-87-current-phase-admin-operate-actions-governance-ledger-alignment/requirements.md` | — | ✅ 已新增：固化 `operate/actions` 下方治理动态区的 ledger 化收口需求 |
| | `.sce/specs/00-87-current-phase-admin-operate-actions-governance-ledger-alignment/design.md` | — | ✅ 已新增：把治理动态区问题收口为 `ActionsView.vue` 的轻量台账表达调整 |
| | `.sce/specs/00-87-current-phase-admin-operate-actions-governance-ledger-alignment/tasks.md` | — | ✅ 已回填：治理动态区精修任务链已完成 |
| | `.sce/specs/00-87-current-phase-admin-operate-actions-governance-ledger-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/operate/ActionsView.vue` | — | ✅ 已完成第三轮：运营动作治理动态区已完成局部收口，并完成真实浏览器复核 |
| 00-88 current-phase-admin-system-settings-first-screen-alignment | `.sce/specs/00-88-current-phase-admin-system-settings-first-screen-alignment/requirements.md` | — | ✅ 已新增：固化 `system/settings` 首屏 overview 退场与设置列表密度问题 |
| | `.sce/specs/00-88-current-phase-admin-system-settings-first-screen-alignment/design.md` | — | ✅ 已新增：把系统设置首屏问题收口为 `SettingsView.vue` 的局部结构与密度调整 |
| | `.sce/specs/00-88-current-phase-admin-system-settings-first-screen-alignment/tasks.md` | — | ✅ 已回填：系统设置首屏精修任务链已完成 |
| | `.sce/specs/00-88-current-phase-admin-system-settings-first-screen-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/system/SettingsView.vue` | — | ✅ 已完成第二轮：系统设置首屏已完成局部收口，并完成真实浏览器复核 |
| 00-89 current-phase-admin-organization-directory-first-screen-alignment | `.sce/specs/00-89-current-phase-admin-organization-directory-first-screen-alignment/requirements.md` | — | ✅ 已新增：固化 `users/orgs` 首屏 KPI、前置说明区与目录区表达的局部收口需求 |
| | `.sce/specs/00-89-current-phase-admin-organization-directory-first-screen-alignment/design.md` | — | ✅ 已新增：把机构页问题收口为 `OrganizationsView.vue` 的首屏结构与目录 ledger 调整 |
| | `.sce/specs/00-89-current-phase-admin-organization-directory-first-screen-alignment/tasks.md` | — | ✅ 已回填：机构页首屏精修任务链已完成 |
| | `.sce/specs/00-89-current-phase-admin-organization-directory-first-screen-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/user/OrganizationsView.vue` | — | ✅ 已完成第二轮：机构页首屏与目录区已完成局部收口，并完成真实浏览器复核 |
| 00-90 current-phase-admin-analytics-channel-first-screen-alignment | `.sce/specs/00-90-current-phase-admin-analytics-channel-first-screen-alignment/requirements.md` | — | ✅ 已新增：固化 `dashboard/analytics` 默认渠道分析首屏的 tabs、渠道 board 与 donut mix 收口需求 |
| | `.sce/specs/00-90-current-phase-admin-analytics-channel-first-screen-alignment/design.md` | — | ✅ 已新增：把数据分析首屏问题收口为 `DashboardAnalyticsView.vue` 的默认 channel tab 局部结构与密度调整 |
| | `.sce/specs/00-90-current-phase-admin-analytics-channel-first-screen-alignment/tasks.md` | — | ✅ 已回填：数据分析渠道首屏精修任务链已完成 |
| | `.sce/specs/00-90-current-phase-admin-analytics-channel-first-screen-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/dashboard/DashboardAnalyticsView.vue` | — | ✅ 已完成第二轮：数据分析默认渠道分析首屏已完成局部收口，并完成真实浏览器复核 |
| 00-91 current-phase-admin-analytics-retention-matrix-alignment | `.sce/specs/00-91-current-phase-admin-analytics-retention-matrix-alignment/requirements.md` | — | ✅ 已新增：固化 `dashboard/analytics` 留存分析 tab 的单板矩阵收口需求 |
| | `.sce/specs/00-91-current-phase-admin-analytics-retention-matrix-alignment/design.md` | — | ✅ 已新增：把留存分析问题收口为 `DashboardAnalyticsView.vue` 的 retention tab 代理矩阵调整 |
| | `.sce/specs/00-91-current-phase-admin-analytics-retention-matrix-alignment/tasks.md` | — | ✅ 已回填：数据分析留存矩阵精修任务链已完成 |
| | `.sce/specs/00-91-current-phase-admin-analytics-retention-matrix-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/dashboard/DashboardAnalyticsView.vue` | — | ✅ 已完成第三轮：数据分析留存分析 tab 已完成单板代理矩阵收口，并完成真实浏览器复核 |
| 00-92 current-phase-admin-analytics-funnel-board-alignment | `.sce/specs/00-92-current-phase-admin-analytics-funnel-board-alignment/requirements.md` | — | ✅ 已新增：固化 `dashboard/analytics` 转化漏斗 tab 的单张全宽漏斗板收口需求 |
| | `.sce/specs/00-92-current-phase-admin-analytics-funnel-board-alignment/design.md` | — | ✅ 已新增：把转化漏斗问题收口为 `DashboardAnalyticsView.vue` 的 funnel tab 全宽板与内联摘要调整 |
| | `.sce/specs/00-92-current-phase-admin-analytics-funnel-board-alignment/tasks.md` | — | ✅ 已回填：数据分析漏斗板精修任务链已完成 |
| | `.sce/specs/00-92-current-phase-admin-analytics-funnel-board-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/dashboard/DashboardAnalyticsView.vue` | — | ✅ 已完成第四轮：数据分析转化漏斗 tab 已完成单张全宽漏斗板收口，并完成真实浏览器复核 |
| 00-93 current-phase-admin-analytics-segment-board-alignment | `.sce/specs/00-93-current-phase-admin-analytics-segment-board-alignment/requirements.md` | — | ✅ 已新增：固化 `dashboard/analytics` 用户分群 tab 的全宽分群板收口需求 |
| | `.sce/specs/00-93-current-phase-admin-analytics-segment-board-alignment/design.md` | — | ✅ 已新增：把用户分群问题收口为 `DashboardAnalyticsView.vue` 的 segment tab 全宽卡阵列与内联边界说明调整 |
| | `.sce/specs/00-93-current-phase-admin-analytics-segment-board-alignment/tasks.md` | — | ✅ 已回填：数据分析用户分群板精修任务链已完成 |
| | `.sce/specs/00-93-current-phase-admin-analytics-segment-board-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/dashboard/DashboardAnalyticsView.vue` | — | ✅ 已完成第五轮：数据分析用户分群 tab 已完成全宽分群板收口，并完成真实浏览器复核 |
| 00-94 current-phase-admin-system-settings-grouped-row-detail-alignment | `.sce/specs/00-94-current-phase-admin-system-settings-grouped-row-detail-alignment/requirements.md` | — | ✅ 已新增：固化 `system/settings` grouped-row header、子入口行高、右侧 affordance 与文案细节的收口需求 |
| | `.sce/specs/00-94-current-phase-admin-system-settings-grouped-row-detail-alignment/design.md` | — | ✅ 已新增：把系统设置问题收口为 `SettingsView.vue` 的分组行表达和子入口细节调整 |
| | `.sce/specs/00-94-current-phase-admin-system-settings-grouped-row-detail-alignment/tasks.md` | — | ✅ 已回填：系统设置 grouped-row 精修任务链已完成 |
| | `.sce/specs/00-94-current-phase-admin-system-settings-grouped-row-detail-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/system/SettingsView.vue` | — | ✅ 已完成第三轮：系统设置 grouped rows / 子入口细节已完成局部收口，并完成真实浏览器复核 |
| 00-95 current-phase-admin-system-account-governance-first-screen-alignment | `.sce/specs/00-95-current-phase-admin-system-account-governance-first-screen-alignment/requirements.md` | — | ✅ 已新增：固化 `system/admin-users` 首屏 summary、筛选区和表格首屏关系的收口需求 |
| | `.sce/specs/00-95-current-phase-admin-system-account-governance-first-screen-alignment/design.md` | — | ✅ 已新增：把后台账号治理问题收口为 `AdminUsersView.vue` 的轻量 shell card、筛选区和 table header 调整 |
| | `.sce/specs/00-95-current-phase-admin-system-account-governance-first-screen-alignment/tasks.md` | — | ✅ 已回填：后台账号治理首屏精修任务链已完成 |
| | `.sce/specs/00-95-current-phase-admin-system-account-governance-first-screen-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/system/AdminUsersView.vue` | — | ✅ 已完成首轮：后台账号治理页首屏已完成局部收口，并完成真实浏览器复核 |
| 00-96 current-phase-admin-system-account-governance-table-density-alignment | `.sce/specs/00-96-current-phase-admin-system-account-governance-table-density-alignment/requirements.md` | — | ✅ 已新增：固化 `system/admin-users` 主表行高、联系方式 cell、角色 tag 与操作列密度收口需求 |
| | `.sce/specs/00-96-current-phase-admin-system-account-governance-table-density-alignment/design.md` | — | ✅ 已新增：把后台账号治理剩余问题收口为 `AdminUsersView.vue` 的 table-density 局部调整 |
| | `.sce/specs/00-96-current-phase-admin-system-account-governance-table-density-alignment/tasks.md` | — | ✅ 已回填：后台账号治理表格密度精修任务链已完成 |
| | `.sce/specs/00-96-current-phase-admin-system-account-governance-table-density-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/system/AdminUsersView.vue` | — | ✅ 已完成第二轮：后台账号治理页主表密度已完成局部收口，并完成真实浏览器复核 |
| 00-97 current-phase-admin-system-account-governance-detail-drawer-density-alignment | `.sce/specs/00-97-current-phase-admin-system-account-governance-detail-drawer-density-alignment/requirements.md` | — | ✅ 已新增：固化 `system/admin-users` 详情抽屉宽度、hero、字段块与角色绑定区密度收口需求 |
| | `.sce/specs/00-97-current-phase-admin-system-account-governance-detail-drawer-density-alignment/design.md` | — | ✅ 已新增：把后台账号治理剩余问题收口为 `AdminUsersView.vue` 的 detail-drawer 局部调整 |
| | `.sce/specs/00-97-current-phase-admin-system-account-governance-detail-drawer-density-alignment/tasks.md` | — | ✅ 已回填：后台账号治理详情抽屉精修任务链已完成 |
| | `.sce/specs/00-97-current-phase-admin-system-account-governance-detail-drawer-density-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/system/AdminUsersView.vue` | — | ✅ 已完成第三轮：后台账号治理页详情抽屉已完成局部收口，并完成真实浏览器复核 |
| 00-98 current-phase-admin-system-account-governance-maintenance-dialog-density-alignment | `.sce/specs/00-98-current-phase-admin-system-account-governance-maintenance-dialog-density-alignment/requirements.md` | — | ✅ 已新增：固化 `system/admin-users` 新建 / 编辑、绑定角色、重置密码三个维护弹窗密度收口需求 |
| | `.sce/specs/00-98-current-phase-admin-system-account-governance-maintenance-dialog-density-alignment/design.md` | — | ✅ 已新增：把后台账号治理剩余问题收口为 `AdminUsersView.vue` 的 maintenance-dialog 局部调整 |
| | `.sce/specs/00-98-current-phase-admin-system-account-governance-maintenance-dialog-density-alignment/tasks.md` | — | ✅ 已回填：后台账号治理维护弹窗精修任务链已完成 |
| | `.sce/specs/00-98-current-phase-admin-system-account-governance-maintenance-dialog-density-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/system/AdminUsersView.vue` | — | ✅ 已完成第四轮：后台账号治理页维护弹窗已完成局部收口，并完成真实浏览器复核 |
| 00-99 current-phase-admin-system-account-governance-status-confirm-dialog-alignment | `.sce/specs/00-99-current-phase-admin-system-account-governance-status-confirm-dialog-alignment/requirements.md` | — | ✅ 已新增：固化 `system/admin-users` 启用 / 禁用确认弹窗、meta 区与原因输入区密度收口需求 |
| | `.sce/specs/00-99-current-phase-admin-system-account-governance-status-confirm-dialog-alignment/design.md` | — | ✅ 已新增：把后台账号治理剩余问题收口为 `AuditConfirmDialog.vue + AdminUsersView.vue` 的 status-confirm 局部调整 |
| | `.sce/specs/00-99-current-phase-admin-system-account-governance-status-confirm-dialog-alignment/tasks.md` | — | ✅ 已回填：后台账号治理状态确认弹窗精修任务链已完成 |
| | `.sce/specs/00-99-current-phase-admin-system-account-governance-status-confirm-dialog-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/components/dialogs/AuditConfirmDialog.vue` | — | ✅ 已完成：为复用确认弹窗增加可选 `dialogClass / width` 扩展入口，默认行为不变 |
| | `kaipai-admin/src/views/system/AdminUsersView.vue` | — | ✅ 已完成第五轮：后台账号治理页状态确认弹窗已完成局部收口，并完成真实浏览器复核 |
| 00-100 current-phase-admin-system-roles-first-screen-alignment | `.sce/specs/00-100-current-phase-admin-system-roles-first-screen-alignment/requirements.md` | — | ✅ 已新增：固化 `system/roles` 首屏结构、筛选区与首张 AI 授权矩阵壳层收口需求 |
| | `.sce/specs/00-100-current-phase-admin-system-roles-first-screen-alignment/design.md` | — | ✅ 已新增：把角色治理页问题收口为 `RolesView.vue` 的首屏 shell、筛选区与首张矩阵壳层调整 |
| | `.sce/specs/00-100-current-phase-admin-system-roles-first-screen-alignment/tasks.md` | — | ✅ 已回填：后台角色治理首屏精修任务链已完成 |
| | `.sce/specs/00-100-current-phase-admin-system-roles-first-screen-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已完成首轮：后台角色治理页首屏与首张 AI 矩阵壳层已完成局部收口，并完成真实浏览器复核 |
| 00-101 current-phase-admin-system-roles-ai-matrix-table-density-alignment | `.sce/specs/00-101-current-phase-admin-system-roles-ai-matrix-table-density-alignment/requirements.md` | — | ✅ 已新增：固化 `system/roles` 首张 AI 授权矩阵的行高、tag list 与操作列密度收口需求 |
| | `.sce/specs/00-101-current-phase-admin-system-roles-ai-matrix-table-density-alignment/design.md` | — | ✅ 已新增：把角色治理页剩余问题收口为 `RolesView.vue` 第一张 AI 矩阵表格密度调整 |
| | `.sce/specs/00-101-current-phase-admin-system-roles-ai-matrix-table-density-alignment/tasks.md` | — | ✅ 已回填：后台角色治理 AI 矩阵表格密度精修任务链已完成 |
| | `.sce/specs/00-101-current-phase-admin-system-roles-ai-matrix-table-density-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已完成第二轮：后台角色治理页首张 AI 授权矩阵表格已完成局部收口，并完成真实浏览器复核 |
| 00-102 current-phase-admin-system-roles-recruit-matrix-card-alignment | `.sce/specs/00-102-current-phase-admin-system-roles-recruit-matrix-card-alignment/requirements.md` | — | ✅ 已新增：固化 `system/roles` 第二张招募治理授权矩阵的 card shell、长标签与表格密度收口需求 |
| | `.sce/specs/00-102-current-phase-admin-system-roles-recruit-matrix-card-alignment/design.md` | — | ✅ 已新增：把角色治理页剩余问题收口为 `RolesView.vue` 第二张招募矩阵卡片与长标签调整 |
| | `.sce/specs/00-102-current-phase-admin-system-roles-recruit-matrix-card-alignment/tasks.md` | — | ✅ 已回填：后台角色治理招募矩阵卡片精修任务链已完成 |
| | `.sce/specs/00-102-current-phase-admin-system-roles-recruit-matrix-card-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与 AI 矩阵补权限运行态修补 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已完成第三轮：后台角色治理页第二张招募治理授权矩阵卡片已完成局部收口，并修正 AI 矩阵补权限传参 |
| 00-103 current-phase-admin-system-roles-directory-table-density-alignment | `.sce/specs/00-103-current-phase-admin-system-roles-directory-table-density-alignment/requirements.md` | — | ✅ 已新增：固化 `system/roles` 底部角色清单的 header、表格首行、权限概览 cell、fixed 操作列与分页区密度收口需求 |
| | `.sce/specs/00-103-current-phase-admin-system-roles-directory-table-density-alignment/design.md` | — | ✅ 已新增：把角色治理页剩余问题收口为 `RolesView.vue` 底部角色清单的 table-density 调整 |
| | `.sce/specs/00-103-current-phase-admin-system-roles-directory-table-density-alignment/tasks.md` | — | ✅ 已回填：后台角色治理角色清单表格密度精修任务链已完成 |
| | `.sce/specs/00-103-current-phase-admin-system-roles-directory-table-density-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已完成第四轮：后台角色治理页底部角色清单已完成局部收口，并完成真实浏览器复核 |
| 00-104 current-phase-admin-system-roles-detail-drawer-density-alignment | `.sce/specs/00-104-current-phase-admin-system-roles-detail-drawer-density-alignment/requirements.md` | — | ✅ 已新增：固化 `system/roles` 角色详情抽屉的 shell、hero、字段块与权限 tag 密度收口需求 |
| | `.sce/specs/00-104-current-phase-admin-system-roles-detail-drawer-density-alignment/design.md` | — | ✅ 已新增：把角色治理页剩余问题收口为 `RolesView.vue` 详情抽屉的 shell、字段块与权限 tag 调整 |
| | `.sce/specs/00-104-current-phase-admin-system-roles-detail-drawer-density-alignment/tasks.md` | — | ✅ 已回填：后台角色治理详情抽屉精修任务链已完成 |
| | `.sce/specs/00-104-current-phase-admin-system-roles-detail-drawer-density-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与完整权限 title 追溯验证 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已完成第五轮：后台角色治理页详情抽屉已完成局部收口，并完成真实浏览器复核 |
| 00-105 current-phase-admin-system-roles-maintenance-dialog-density-alignment | `.sce/specs/00-105-current-phase-admin-system-roles-maintenance-dialog-density-alignment/requirements.md` | — | ✅ 已新增：固化 `system/roles` 新建 / 编辑 / 复制维护弹窗的 shell、intro、表单项、权限包与权限树区域密度收口需求 |
| | `.sce/specs/00-105-current-phase-admin-system-roles-maintenance-dialog-density-alignment/design.md` | — | ✅ 已新增：把角色治理页剩余问题收口为 `RolesView.vue` 维护弹窗的 shell、权限包、权限树与 body 滚动策略调整 |
| | `.sce/specs/00-105-current-phase-admin-system-roles-maintenance-dialog-density-alignment/tasks.md` | — | ✅ 已回填：后台角色治理维护弹窗精修任务链已完成 |
| | `.sce/specs/00-105-current-phase-admin-system-roles-maintenance-dialog-density-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与状态确认调查边界 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已完成第六轮：后台角色治理页新建 / 编辑 / 复制维护弹窗已完成局部收口，并完成真实浏览器复核 |
| 00-106 current-phase-admin-system-roles-status-confirm-dialog-alignment | `.sce/specs/00-106-current-phase-admin-system-roles-status-confirm-dialog-alignment/requirements.md` | — | ✅ 已新增：固化 `system/roles` 启用 / 禁用确认弹窗的 shell、intro、meta 与原因输入区密度收口需求 |
| | `.sce/specs/00-106-current-phase-admin-system-roles-status-confirm-dialog-alignment/design.md` | — | ✅ 已新增：把角色治理页剩余问题收口为 `RolesView.vue` 状态确认弹窗的 page-local dialog 调整 |
| | `.sce/specs/00-106-current-phase-admin-system-roles-status-confirm-dialog-alignment/tasks.md` | — | ✅ 已回填：后台角色治理状态确认弹窗精修任务链已完成 |
| | `.sce/specs/00-106-current-phase-admin-system-roles-status-confirm-dialog-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已完成第七轮：后台角色治理页状态确认弹窗已完成局部收口，并完成真实浏览器复核 |
| 00-107 current-phase-admin-system-roles-permission-orchestration-density-alignment | `.sce/specs/00-107-current-phase-admin-system-roles-permission-orchestration-density-alignment/requirements.md` | — | ✅ 已新增：固化 `system/roles` 创建 / 编辑弹窗中的 alert、权限包、toolbar 与权限树区域密度收口需求 |
| | `.sce/specs/00-107-current-phase-admin-system-roles-permission-orchestration-density-alignment/design.md` | — | ✅ 已新增：把角色治理页剩余问题收口为 `RolesView.vue` 与 `PermissionTreeEditor.vue` 的权限编排区内部密度调整 |
| | `.sce/specs/00-107-current-phase-admin-system-roles-permission-orchestration-density-alignment/tasks.md` | — | ✅ 已回填：后台角色治理权限编排区精修任务链已完成 |
| | `.sce/specs/00-107-current-phase-admin-system-roles-permission-orchestration-density-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果与构建验证 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已完成第八轮：后台角色治理页权限编排区已完成局部收口，并完成真实浏览器复核 |
| | `kaipai-admin/src/components/forms/PermissionTreeEditor.vue` | — | ✅ 已完成：权限树编辑器 toolbar、tree 与 node 内部密度收口 |
| 00-108 current-phase-admin-system-ai-resume-failure-table-density-alignment | `.sce/specs/00-108-current-phase-admin-system-ai-resume-failure-table-density-alignment/requirements.md` | — | ✅ 已新增：固化 `system/ai-resume-governance` 失败样本双表的宽表容器、责任协同 cell、最近处置与操作列密度收口需求 |
| | `.sce/specs/00-108-current-phase-admin-system-ai-resume-failure-table-density-alignment/design.md` | — | ✅ 已新增：把 AI 简历治理页剩余问题收口为 `Failure Samples / Sensitive Hits` 双表的容器与 cell 级密度调整 |
| | `.sce/specs/00-108-current-phase-admin-system-ai-resume-failure-table-density-alignment/tasks.md` | — | ✅ 已回填：后台 AI 简历治理失败样本双表精修任务链已完成 |
| | `.sce/specs/00-108-current-phase-admin-system-ai-resume-failure-table-density-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、量化结果、运行态边界与构建验证 |
| | `kaipai-admin/src/views/system/AiResumeGovernanceView.vue` | — | ✅ 已完成本轮：失败样本双表已改为宽表承载，责任协同 compact cell 与有限高度表体已通过真实浏览器复核 |
| 00-109 current-phase-admin-system-operation-logs-degraded-state-alignment | `.sce/specs/00-109-current-phase-admin-system-operation-logs-degraded-state-alignment/requirements.md` | — | ✅ 已新增：固化 `system/operation-logs` 的接口失败降级、overview 事实源状态与表格空态语义收口需求 |
| | `.sce/specs/00-109-current-phase-admin-system-operation-logs-degraded-state-alignment/design.md` | — | ✅ 已新增：把操作留痕审计页剩余问题收口为 `OperationLogsView.vue` 的 runtime degradation 与 empty-state 调整 |
| | `.sce/specs/00-109-current-phase-admin-system-operation-logs-degraded-state-alignment/tasks.md` | — | ✅ 已回填：后台操作留痕审计降级态精修任务链已完成 |
| | `.sce/specs/00-109-current-phase-admin-system-operation-logs-degraded-state-alignment/execution.md` | — | ✅ 已回填：记录修复前后截图、console 对比、量化结果与构建验证 |
| | `kaipai-admin/src/views/system/OperationLogsView.vue` | — | ✅ 已完成本轮：操作留痕审计页已显式承接事实源异常，不再把接口失败伪装成默认空数据，并通过真实浏览器复核 |
| 00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit | `.sce/specs/00-110-current-phase-admin-legacy-route-and-fallback-retirement-audit/requirements.md` | — | ✅ 已新增：固化隐藏治理路由、候删文件、fallback 兼容依赖与正式页后端绑定审计需求 |
| | `.sce/specs/00-110-current-phase-admin-legacy-route-and-fallback-retirement-audit/design.md` | — | ✅ 已新增：把删除前审计收口为四象限 legacy inventory 与正式页后端绑定矩阵 |
| | `.sce/specs/00-110-current-phase-admin-legacy-route-and-fallback-retirement-audit/tasks.md` | — | ✅ 已回填：旧路由 / 旧代码 / fallback 审计任务链已完成 |
| | `.sce/specs/00-110-current-phase-admin-legacy-route-and-fallback-retirement-audit/execution.md` | — | ✅ 已回填：记录当前隐藏路由、候删文件、fallback、正式页后端绑定与删除前门禁口径 |
| | `.sce/specs/00-110-current-phase-admin-legacy-route-and-fallback-retirement-audit/legacy-inventory-matrix.md` | — | ✅ 已新增：固化正式主线、隐藏治理页、compat fallback 与 retire candidate 的审计矩阵 |
| | `.sce/specs/00-110-current-phase-admin-legacy-route-and-fallback-retirement-audit/formal-page-backend-binding-matrix.md` | — | ✅ 已新增：固化正式 8 页前端 API、后端接口与 controller 绑定矩阵 |
| | `kaipai-admin/src/router/index.ts` | — | 🟡 已建档：00-110 将核实正式 8 页之外仍保留的 hidden tooling routes |
| | `kaipai-admin/src/constants/menus.ts` | — | 🟡 已建档：00-110 将核实 full capability inventory 与正式侧栏投影的差集 |
| | `kaipai-admin/src/stores/permission.ts` | — | 🟡 已建档：00-110 将核实 fallbackPermissions 仍保留的运行态依赖 |
| | `kaipai-admin/src/constants/admin-information-architecture.ts` | — | 🟡 已建档：00-110 将核实 tooling / retire-candidate / formal active 的分类边界 |
| | `kaipai-admin/src/views/dashboard/DashboardView.vue` | — | ✅ 已核销：已在 `00-111` 删除，删除前仅包裹 `OverviewView.vue` |
| | `kaipai-admin/src/views/referral/ReferralRiskView.vue` | — | ✅ 已核销：已在 `00-111` 删除，删除前仅包裹 `RiskView.vue` |
| | `kaipai-admin/src/views/shared/PlaceholderView.vue` | — | ✅ 已核销：已在 `00-112` 删除，删除前确认无 router / menu / import 依赖 |
| | `kaipai-admin/src/api/dashboard.ts` | — | ✅ 已审计：已纳入正式 8 页后端绑定矩阵 |
| | `kaipai-admin/src/api/user-center.ts` | — | ✅ 已审计：已纳入正式 8 页后端绑定矩阵 |
| | `kaipai-admin/src/api/content.ts` | — | ✅ 已审计：已纳入正式 8 页后端绑定矩阵 |
| | `kaipai-admin/src/api/recruit.ts` | — | ✅ 已审计：已纳入正式 8 页后端绑定矩阵 |
| | `kaipai-admin/src/api/company.ts` | — | ✅ 已审计：已纳入正式 8 页后端绑定矩阵 |
| | `kaipai-admin/src/api/system.ts` | — | ✅ 已审计：已纳入系统设置聚合与隐藏治理页接口矩阵 |
| 00-111 current-phase-admin-legacy-wrapper-retirement-first-pass | `.sce/specs/00-111-current-phase-admin-legacy-wrapper-retirement-first-pass/requirements.md` | — | ✅ 已新增：固化第一批低风险历史 wrapper 退场需求 |
| | `.sce/specs/00-111-current-phase-admin-legacy-wrapper-retirement-first-pass/design.md` | — | ✅ 已新增：把 wrapper 退场范围收口为 `DashboardView.vue` 与 `ReferralRiskView.vue` |
| | `.sce/specs/00-111-current-phase-admin-legacy-wrapper-retirement-first-pass/tasks.md` | — | ✅ 已回填：第一批历史 wrapper 退场任务链已完成 |
| | `.sce/specs/00-111-current-phase-admin-legacy-wrapper-retirement-first-pass/execution.md` | — | ✅ 已回填：记录删除前搜索证据、删除结果与构建验证 |
| | `kaipai-admin/src/views/dashboard/DashboardView.vue` | — | ✅ 已删除：历史薄包装文件，当前已由 `OverviewView.vue` 直接承接 |
| | `kaipai-admin/src/views/referral/ReferralRiskView.vue` | — | ✅ 已删除：历史薄包装文件，当前已由 `RiskView.vue` 直接承接 |
| 00-112 current-phase-admin-placeholder-view-retirement-verification | `.sce/specs/00-112-current-phase-admin-placeholder-view-retirement-verification/requirements.md` | — | ✅ 已新增：固化 `PlaceholderView.vue` 单文件退场核销需求 |
| | `.sce/specs/00-112-current-phase-admin-placeholder-view-retirement-verification/design.md` | — | ✅ 已新增：明确 `PlaceholderView.vue` 只剩文档追溯引用，不再承担运行态职责 |
| | `.sce/specs/00-112-current-phase-admin-placeholder-view-retirement-verification/tasks.md` | — | ✅ 已回填：PlaceholderView 退场任务链已完成 |
| | `.sce/specs/00-112-current-phase-admin-placeholder-view-retirement-verification/execution.md` | — | ✅ 已回填：记录核查范围、删除动作与构建验证 |
| | `kaipai-admin/src/views/shared/PlaceholderView.vue` | — | ✅ 已删除：历史占位容器文件，当前无 router / menu / import / auto-register 依赖 |
| 00-113 current-phase-admin-recruit-fallback-direct-permission-first-pass | `.sce/specs/00-113-current-phase-admin-recruit-fallback-direct-permission-first-pass/requirements.md` | — | ✅ 已新增：固化当前 dev 运行库招募 fallback 直授权前提对齐需求 |
| | `.sce/specs/00-113-current-phase-admin-recruit-fallback-direct-permission-first-pass/design.md` | — | ✅ 已新增：明确当前 fallback 阻塞只集中在 `ADMIN` 角色，且本轮不删除代码只补运行时前提 |
| | `.sce/specs/00-113-current-phase-admin-recruit-fallback-direct-permission-first-pass/tasks.md` | — | ✅ 已回填：招募 fallback 直授权首轮任务链已完成 |
| | `.sce/specs/00-113-current-phase-admin-recruit-fallback-direct-permission-first-pass/execution.md` | — | ✅ 已回填：记录执行前后 fallback 计数与 `ADMIN` 角色权限补齐结果 |
| | `kaipaile-server/src/main/resources/db/migration/V20260422_008__admin_recruit_direct_permission_alignment.sql` | — | ✅ 已新增：为 `ADMIN` 角色补齐 `page.recruit.* / action.recruit.*` 的幂等增量 migration |
| 00-114 current-phase-admin-recruit-fallback-code-retirement-first-pass | `.sce/specs/00-114-current-phase-admin-recruit-fallback-code-retirement-first-pass/requirements.md` | — | ✅ 已新增：固化 recruit runtime fallback 第一批代码退场需求 |
| | `.sce/specs/00-114-current-phase-admin-recruit-fallback-code-retirement-first-pass/design.md` | — | ✅ 已新增：明确本轮先删 runtime fallback、保留矩阵 DTO 字段结构 |
| | `.sce/specs/00-114-current-phase-admin-recruit-fallback-code-retirement-first-pass/tasks.md` | — | ✅ 已回填：recruit fallback 代码退场第一批任务链已完成 |
| | `.sce/specs/00-114-current-phase-admin-recruit-fallback-code-retirement-first-pass/execution.md` | — | ✅ 已回填：记录代码退场范围、编译验证与当前发布前提 |
| | `kaipai-admin/src/stores/permission.ts` | — | ✅ 已改造：移除对 `page.recruit.* / action.recruit.*` 的自动 fallback 注入 |
| | `kaipai-admin/src/views/recruit/ProjectsView.vue` | — | ✅ 已改造：移除招募项目页 fallback 提示与动作 fallback 透传 |
| | `kaipai-admin/src/views/recruit/RolesView.vue` | — | ✅ 已改造：移除招募角色页 fallback 提示与动作 fallback 透传 |
| | `kaipai-admin/src/views/recruit/AppliesView.vue` | — | ✅ 已改造：移除投递页 fallback 提示 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已改造：招募矩阵用户可见文案切到历史后台账号页耦合 / 直授权缺口口径 |
| | `kaipai-admin/src/types/admin.ts` | — | ✅ 已改造：移除 `allowLegacyRecruit*` 会话字段 |
| | `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/recruit/AdminRecruitController.java` | — | ✅ 已改造：招募治理接口改为 direct authority only |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/adminauth/service/impl/AdminAuthServiceImpl.java` | — | ✅ 已改造：移除招募 fallback session 装配 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/adminauth/dto/AdminSessionInfoDTO.java` | — | ✅ 已改造：移除 `allowLegacyRecruit*` DTO 字段 |
| | `kaipaile-server/src/main/java/com/kaipai/common/auth/RecruitGovernanceFallbackGate.java` | — | ✅ 已删除：recruit runtime fallback gate |
| 00-115 current-phase-admin-recruit-matrix-schema-cleanup | `.sce/specs/00-115-current-phase-admin-recruit-matrix-schema-cleanup/requirements.md` | — | ✅ 已新增：固化招募矩阵 schema 命名清理需求 |
| | `.sce/specs/00-115-current-phase-admin-recruit-matrix-schema-cleanup/design.md` | — | ✅ 已新增：明确本轮只清理招募矩阵 `fallback` 命名，不扩大到 AI 矩阵 |
| | `.sce/specs/00-115-current-phase-admin-recruit-matrix-schema-cleanup/tasks.md` | — | ✅ 已回填：招募矩阵 schema 清理任务链已完成 |
| | `.sce/specs/00-115-current-phase-admin-recruit-matrix-schema-cleanup/execution.md` | — | ✅ 已回填：记录旧字段命名、重命名结果与编译验证 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/system/dto/AdminRoleRecruitGovernanceMatrixRespDTO.java` | — | ✅ 已改造：招募矩阵响应字段从 `fallback*` 切到后台账号页耦合 / 直授权缺口命名 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/system/dto/AdminRoleRecruitGovernanceMatrixItemDTO.java` | — | ✅ 已改造：招募矩阵明细字段从 `reliesOnFallback` 切到后台账号页耦合命名 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/system/service/impl/AdminRoleServiceImpl.java` | — | ✅ 已改造：招募矩阵装配与统计变量同步切到后台账号页耦合命名 |
| | `kaipai-admin/src/types/system.ts` | — | ✅ 已改造：招募矩阵前端类型同步切到后台账号页耦合命名 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已改造：招募矩阵字段消费与统计 helper 同步切到后台账号页耦合命名 |
| 00-116 current-phase-admin-ai-matrix-schema-cleanup | `.sce/specs/00-116-current-phase-admin-ai-matrix-schema-cleanup/requirements.md` | — | ✅ 已新增：固化 AI 矩阵 schema 命名清理需求 |
| | `.sce/specs/00-116-current-phase-admin-ai-matrix-schema-cleanup/design.md` | — | ✅ 已新增：明确本轮只清理 AI 矩阵 `fallback` 命名，不处理 operation-logs 事实源 |
| | `.sce/specs/00-116-current-phase-admin-ai-matrix-schema-cleanup/tasks.md` | — | ✅ 已回填：AI 矩阵 schema 清理任务链已完成 |
| | `.sce/specs/00-116-current-phase-admin-ai-matrix-schema-cleanup/execution.md` | — | ✅ 已回填：记录旧字段命名、重命名结果与编译验证 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/system/dto/AdminRoleAiGovernanceMatrixRespDTO.java` | — | ✅ 已改造：AI 矩阵响应字段从 `fallback*` 切到操作日志页耦合命名 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/system/dto/AdminRoleAiGovernanceMatrixItemDTO.java` | — | ✅ 已改造：AI 矩阵明细字段从 `reliesOnFallback` 切到操作日志页耦合命名 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/system/service/impl/AdminRoleServiceImpl.java` | — | ✅ 已改造：AI 矩阵装配与统计变量同步切到操作日志页耦合命名 |
| | `kaipai-admin/src/types/system.ts` | — | ✅ 已改造：AI 矩阵前端类型同步切到操作日志页耦合命名 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已改造：AI 矩阵字段消费与用户可见文案同步切到操作日志页耦合命名 |
| | `kaipai-admin/src/views/system/SettingsView.vue` | — | ✅ 已改造：系统设置 AI 治理入口摘要同步消费 `operationLogsCouplingRoleCount` |
| 00-117 current-phase-admin-ai-operation-logs-detachment-audit | `.sce/specs/00-117-current-phase-admin-ai-operation-logs-detachment-audit/requirements.md` | — | ✅ 已新增：固化 AI / operation-logs 脱钩审计需求 |
| | `.sce/specs/00-117-current-phase-admin-ai-operation-logs-detachment-audit/design.md` | — | ✅ 已新增：明确当前应区分 AI runtime、AI 历史耦合展示与 operation-logs hidden tooling |
| | `.sce/specs/00-117-current-phase-admin-ai-operation-logs-detachment-audit/tasks.md` | — | ✅ 已回填：AI / operation-logs 脱钩审计任务链已完成 |
| | `.sce/specs/00-117-current-phase-admin-ai-operation-logs-detachment-audit/execution.md` | — | ✅ 已回填：记录 AI 主链脱钩事实、operation-logs hidden tooling 边界与下一手门禁 |
| | `.sce/specs/00-117-current-phase-admin-ai-operation-logs-detachment-audit/ai-operation-logs-detachment-matrix.md` | — | ✅ 已新增：固化 AI runtime / AI 历史耦合展示 / operation-logs hidden tooling 的三层边界矩阵 |
| | `kaipai-admin/src/views/system/OperationLogsView.vue` | — | ✅ 已审计：当前继续承担事实源异常下的降级承接，不属于 AI 主链 |
| | `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/ai/AdminAiResumeController.java` | — | ✅ 已审计：当前直接使用 AI 页面 / 动作权限，不依赖 operation-logs |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已审计：当前只把 operation-logs 保留为 AI 历史耦合展示维度 |
| | `kaipai-admin/src/views/system/SettingsView.vue` | — | ✅ 已审计：当前分别保留 AI 治理与操作留痕两个独立 hidden tooling 聚合入口 |
| 00-118 current-phase-admin-operation-logs-fact-source-recovery-audit | `.sce/specs/00-118-current-phase-admin-operation-logs-fact-source-recovery-audit/requirements.md` | — | ✅ 已新增：固化 operation-logs 列表事实源恢复需求 |
| | `.sce/specs/00-118-current-phase-admin-operation-logs-fact-source-recovery-audit/design.md` | — | ✅ 已新增：明确根因是列表分页查询选列过宽，不是详情链路损坏 |
| | `.sce/specs/00-118-current-phase-admin-operation-logs-fact-source-recovery-audit/tasks.md` | — | ✅ 已回填：operation-logs 事实源恢复任务链已完成 |
| | `.sce/specs/00-118-current-phase-admin-operation-logs-fact-source-recovery-audit/execution.md` | — | ✅ 已回填：记录接口复现、8011 日志根因、修复范围与运行态验证 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/system/service/impl/AdminOperationLogServiceImpl.java` | — | ✅ 已改造：operation-logs 列表查询改为按需选列，避免分页排序携带 JSON 快照大字段 |
| 00-119 current-phase-admin-operation-logs-runtime-reenable-and-summary-cleanup | `.sce/specs/00-119-current-phase-admin-operation-logs-runtime-reenable-and-summary-cleanup/requirements.md` | — | ✅ 已新增：固化 operation-logs 运行态恢复后的系统设置摘要清理需求 |
| | `.sce/specs/00-119-current-phase-admin-operation-logs-runtime-reenable-and-summary-cleanup/design.md` | — | ✅ 已新增：明确系统设置页 operation-logs 摘要应区分加载中 / 成功 / 异常三态 |
| | `.sce/specs/00-119-current-phase-admin-operation-logs-runtime-reenable-and-summary-cleanup/tasks.md` | — | ✅ 已回填：operation-logs 摘要清理任务链已完成 |
| | `.sce/specs/00-119-current-phase-admin-operation-logs-runtime-reenable-and-summary-cleanup/execution.md` | — | ✅ 已回填：记录修复前旧摘要口径、三态实现与前端验证 |
| 00-120 current-phase-admin-operation-logs-runtime-refresh-and-browser-revalidation | `.sce/specs/00-120-current-phase-admin-operation-logs-runtime-refresh-and-browser-revalidation/requirements.md` | — | ✅ 已新增：固化 operation-logs 运行态刷新与浏览器复核需求 |
| | `.sce/specs/00-120-current-phase-admin-operation-logs-runtime-refresh-and-browser-revalidation/design.md` | — | ✅ 已新增：明确先刷新本机 `8010` 再做真实浏览器复核 |
| | `.sce/specs/00-120-current-phase-admin-operation-logs-runtime-refresh-and-browser-revalidation/tasks.md` | — | ✅ 已回填：运行态刷新与浏览器复核任务链已完成 |
| | `.sce/specs/00-120-current-phase-admin-operation-logs-runtime-refresh-and-browser-revalidation/execution.md` | — | ✅ 已回填：记录本机 `8010` 新实例启动、登录态 API 复核与浏览器证据 |
| | `output/runtime/00-120/backend-8010.out.log` | — | ✅ 已验证：本机 `8010` 新实例已在 `dev` profile 下启动成功 |
| | `output/runtime/00-120/backend-8010.err.log` | — | ✅ 已验证：当前无后端启动报错输出 |
| | `output/playwright/00-120/settings-operation-logs-summary-after.png` | — | ✅ 已新增：系统设置页 operation-logs 摘要显示 `2305 条记录` |
| | `output/playwright/00-120/operation-logs-list-after.png` | — | ✅ 已新增：operation-logs 列表页恢复运行态截图 |
| | `output/playwright/00-120/operation-logs-detail-after.png` | — | ✅ 已新增：operation-logs 详情抽屉恢复运行态截图 |
| 00-121 current-phase-admin-permission-fallback-infra-retirement | `.sce/specs/00-121-current-phase-admin-permission-fallback-infra-retirement/requirements.md` | — | ✅ 已新增：固化前端权限 fallback 基础设施退场需求 |
| | `.sce/specs/00-121-current-phase-admin-permission-fallback-infra-retirement/design.md` | — | ✅ 已新增：明确只删除无人消费的前端 fallback 管线，并保留 hidden tooling 页面 |
| | `.sce/specs/00-121-current-phase-admin-permission-fallback-infra-retirement/tasks.md` | — | ✅ 已回填：权限 fallback 基础设施退场任务链已完成 |
| | `.sce/specs/00-121-current-phase-admin-permission-fallback-infra-retirement/execution.md` | — | ✅ 已回填：记录 dead infra 核销、direct-only 权限实现与浏览器 smoke |
| | `kaipai-admin/src/utils/permission.ts` | — | ✅ 已改造：权限判断已收口为 open / direct，不再保留 fallback 模式 |
| | `kaipai-admin/src/stores/permission.ts` | — | ✅ 已改造：permission store 已删除 fallback 解析与无引用 access mode 透传 |
| | `kaipai-admin/src/router/index.ts` | — | ✅ 已改造：路由守卫不再读取 `pagePermissionFallbacks` |
| | `kaipai-admin/src/types/admin.ts` | — | ✅ 已改造：`AdminMenuItem` 已删除 `pagePermissionFallbacks` |
| | `kaipai-admin/src/types/router.d.ts` | — | ✅ 已改造：`RouteMeta` 已删除 `pagePermissionFallbacks` |
| | `kaipai-admin/src/components/business/PermissionButton.vue` | — | ✅ 已改造：按钮权限判断不再承接 `fallbackPermissions` |
| | `kaipai-admin/src/constants/admin-information-architecture.ts` | — | ✅ 已改造：招募治理 tooling 描述已切到 direct-authority 口径 |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已改造：AI / 招募矩阵清零提示已收口为独立页面 / 动作权限口径 |
| | `output/playwright/00-121/system-settings-direct-after.png` | — | ✅ 已新增：正式页 direct-authority smoke 截图 |
| | `output/playwright/00-121/recruit-projects-direct-after.png` | — | ✅ 已新增：hidden tooling 页 direct-authority smoke 截图 |
| 00-122 current-phase-admin-membership-legacy-menu-retirement | `.sce/specs/00-122-current-phase-admin-membership-legacy-menu-retirement/requirements.md` | — | ✅ 已新增：固化 `menu.membership` 历史菜单退场需求 |
| | `.sce/specs/00-122-current-phase-admin-membership-legacy-menu-retirement/design.md` | — | ✅ 已新增：明确只删除 membership 历史菜单，不处理页面 / 动作权限和矩阵阶段枚举 |
| | `.sce/specs/00-122-current-phase-admin-membership-legacy-menu-retirement/tasks.md` | — | ✅ 已回填：membership 历史菜单退场任务链已完成 |
| | `.sce/specs/00-122-current-phase-admin-membership-legacy-menu-retirement/execution.md` | — | ✅ 已回填：记录源码/运行库核销、构建验证与浏览器 smoke |
| | `kaipai-admin/src/constants/permission-registry.ts` | — | ✅ 已改造：删除 `legacyMenuRegistry` 与 `menu.membership` 残留，保留 membership 页面 / 动作权限 |
| | `output/playwright/00-122/roles-directory-after.png` | — | ✅ 已新增：角色治理页 smoke 截图 |
| | `output/playwright/00-122/roles-edit-dialog-after.png` | — | ✅ 已新增：角色编辑权限编排区 smoke 截图 |
| 00-123 current-phase-admin-membership-permission-registry-alignment | `.sce/specs/00-123-current-phase-admin-membership-permission-registry-alignment/requirements.md` | — | ✅ 已新增：固化 membership 页面 / 动作权限 registry 对齐需求 |
| | `.sce/specs/00-123-current-phase-admin-membership-permission-registry-alignment/design.md` | — | ✅ 已新增：明确以 `AdminMembershipController.java` 为唯一权限事实源，并把 membership 模块纳入 permission tree |
| | `.sce/specs/00-123-current-phase-admin-membership-permission-registry-alignment/tasks.md` | — | ✅ 已回填：membership 权限 registry 对齐任务链已完成 |
| | `.sce/specs/00-123-current-phase-admin-membership-permission-registry-alignment/execution.md` | — | ✅ 已回填：记录 registry 缺口、构建验证与浏览器复核 |
| | `kaipai-admin/src/constants/permission-registry.ts` | — | ✅ 已改造：补齐 membership 页面 / 动作权限，并把 membership 模块纳入 permission tree |
| | `output/playwright/00-123/roles-membership-tree-after.png` | — | ✅ 已新增：角色编辑弹窗中 membership 模块入树且不再误报 unknown 的截图 |
| 00-124 current-phase-admin-content-permission-registry-alignment | `.sce/specs/00-124-current-phase-admin-content-permission-registry-alignment/requirements.md` | — | ✅ 已新增：固化 content 权限 registry 对齐需求 |
| | `.sce/specs/00-124-current-phase-admin-content-permission-registry-alignment/design.md` | — | ✅ 已新增：明确以 `AdminContentController.java` 为唯一 content 权限事实源，并保留 `menu.recruit` 到下一条切片 |
| | `.sce/specs/00-124-current-phase-admin-content-permission-registry-alignment/tasks.md` | — | ✅ 已回填：content 权限 registry 对齐任务链已完成 |
| | `.sce/specs/00-124-current-phase-admin-content-permission-registry-alignment/execution.md` | — | ✅ 已回填：记录 content 权限缺口、常量收口、构建验证与浏览器复核 |
| | `kaipai-admin/src/constants/permission-registry.ts` | — | ✅ 已改造：补齐 content 页面 / 动作权限文案 |
| | `kaipai-admin/src/constants/permission.ts` | — | ✅ 已改造：补齐最小范围 content 权限常量 |
| | `kaipai-admin/src/views/content/TemplatesView.vue` | — | ✅ 已改造：启停用模板动作已切到 `PERMISSIONS` 常量 |
| | `output/playwright/00-124/roles-content-registry-after.png` | — | ✅ 已新增：角色编辑弹窗中 content unknown 清零后的截图 |
| 00-125 current-phase-admin-recruit-legacy-menu-registry-alignment | `.sce/specs/00-125-current-phase-admin-recruit-legacy-menu-registry-alignment/requirements.md` | — | ✅ 已新增：固化 `menu.recruit` 历史菜单 registry 对齐需求 |
| | `.sce/specs/00-125-current-phase-admin-recruit-legacy-menu-registry-alignment/design.md` | — | ✅ 已新增：明确 `menu.recruit` 仅作为历史登记展示，不恢复 runtime 放通 |
| | `.sce/specs/00-125-current-phase-admin-recruit-legacy-menu-registry-alignment/tasks.md` | — | ✅ 已回填：recruit 历史菜单 registry 对齐任务链已完成 |
| | `.sce/specs/00-125-current-phase-admin-recruit-legacy-menu-registry-alignment/execution.md` | — | ✅ 已回填：记录运行时边界、构建验证与浏览器复核 |
| | `kaipai-admin/src/constants/permission-registry.ts` | — | ✅ 已改造：新增 `menu.recruit` 历史菜单登记项 |
| | `output/playwright/00-125/roles-recruit-legacy-menu-after.png` | — | ✅ 已新增：角色编辑弹窗中 unknown 清零后的截图 |
| 00-126 current-phase-admin-recruit-legacy-menu-runtime-retirement | `.sce/specs/00-126-current-phase-admin-recruit-legacy-menu-runtime-retirement/requirements.md` | — | ✅ 已新增：固化 `menu.recruit` 运行库退场需求 |
| | `.sce/specs/00-126-current-phase-admin-recruit-legacy-menu-runtime-retirement/design.md` | — | ✅ 已新增：明确只清 dev 运行库中的历史菜单数据，不改招募 runtime 放通边界 |
| | `.sce/specs/00-126-current-phase-admin-recruit-legacy-menu-runtime-retirement/tasks.md` | — | ✅ 已回填：`menu.recruit` 运行库退场任务链已完成 |
| | `.sce/specs/00-126-current-phase-admin-recruit-legacy-menu-runtime-retirement/execution.md` | — | ✅ 已回填：记录 migration、运行库对齐、运行态刷新与浏览器复核 |
| | `kaipaile-server/src/main/resources/db/migration/V20260423_009__admin_recruit_legacy_menu_runtime_retirement.sql` | — | ✅ 已新增：幂等清理已满足招募直授权门禁角色上的 `menu.recruit` |
| | `output/runtime/00-126/backend-8010.out.log` | — | ✅ 已新增：本机 `8010` 新实例启动日志 |
| | `output/runtime/00-126/backend-8010.err.log` | — | ✅ 已验证：当前无启动报错输出 |
| | `output/playwright/00-126/roles-recruit-runtime-after.png` | — | ✅ 已新增：招募矩阵已不再显示 `历史 menu.recruit`、角色目录菜单数降为 6 的截图 |
| | `kaipai-admin/src/views/system/SettingsView.vue` | — | ✅ 已改造：operation-logs 摘要新增加载中 / 成功 / 异常三态，不再默认显示事实源异常 |
| 00-127 current-phase-admin-recruit-legacy-menu-display-retirement | `.sce/specs/00-127-current-phase-admin-recruit-legacy-menu-display-retirement/requirements.md` | — | ✅ 已新增：固化招募矩阵 `hasRecruitMenu` 历史展示合同退场需求 |
| | `.sce/specs/00-127-current-phase-admin-recruit-legacy-menu-display-retirement/design.md` | — | ✅ 已新增：明确只退招募矩阵过期展示合同，保留 registry 历史登记兼容层 |
| | `.sce/specs/00-127-current-phase-admin-recruit-legacy-menu-display-retirement/tasks.md` | — | ✅ 已回填：`hasRecruitMenu` 展示合同退场任务链已完成 |
| | `.sce/specs/00-127-current-phase-admin-recruit-legacy-menu-display-retirement/execution.md` | — | ✅ 已回填：记录删除前 live contract、代码收口、运行态刷新与浏览器复核 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/system/dto/AdminRoleRecruitGovernanceMatrixItemDTO.java` | — | ✅ 已改造：移除招募矩阵 `hasRecruitMenu` 历史字段 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/system/service/impl/AdminRoleServiceImpl.java` | — | ✅ 已改造：招募矩阵装配不再读取 / 回填 `menu.recruit` |
| | `kaipai-admin/src/types/system.ts` | — | ✅ 已改造：前端招募矩阵类型移除 `hasRecruitMenu` |
| | `kaipai-admin/src/views/system/RolesView.vue` | — | ✅ 已改造：移除招募矩阵 `历史 menu.recruit` 标签与对应提示分支 |
| | `kaipai-admin/src/constants/permission.ts` | — | ✅ 已改造：删除已无消费者的 `PERMISSIONS.menu.recruit` 死常量 |
| | `output/runtime/00-127/backend-8010.out.log` | — | ✅ 已新增：本机 `8010` 新实例已在 `dev` profile 下启动成功 |
| | `output/runtime/00-127/backend-8010.err.log` | — | ✅ 已验证：当前无启动报错输出 |
| | `output/playwright/00-127/roles-recruit-display-after.png` | — | ✅ 已新增：招募矩阵不再显示 `历史 menu.recruit` 的浏览器截图 |
| 00-128 current-phase-admin-recruit-legacy-menu-registry-retirement | `.sce/specs/00-128-current-phase-admin-recruit-legacy-menu-registry-retirement/requirements.md` | — | ✅ 已新增：固化前端 permission registry 最后一条 `menu.recruit` 历史登记退场需求 |
| | `.sce/specs/00-128-current-phase-admin-recruit-legacy-menu-registry-retirement/design.md` | — | ✅ 已新增：明确只删除本机 runtime 已不再需要的 registry 历史登记残留 |
| | `.sce/specs/00-128-current-phase-admin-recruit-legacy-menu-registry-retirement/tasks.md` | — | ✅ 已回填：`menu.recruit` registry 残留退场任务链已完成 |
| | `.sce/specs/00-128-current-phase-admin-recruit-legacy-menu-registry-retirement/execution.md` | — | ✅ 已回填：记录删除前 API 证据、单文件退场与浏览器复核 |
| | `kaipai-admin/src/constants/permission-registry.ts` | — | ✅ 已改造：删除 `historicalMenuRegistry` 与 `menu.recruit` 历史登记项 |
| | `output/playwright/00-128/roles-edit-dialog-recruit-tree-after.png` | — | ✅ 已新增：角色编辑弹窗中 unknown 仍为 0、招募模块只剩页面/动作树的截图 |
| 00-129 current-phase-admin-verify-pending-wrapper-retirement | `.sce/specs/00-129-current-phase-admin-verify-pending-wrapper-retirement/requirements.md` | — | ✅ 已新增：固化 `/verify/pending` 薄包装路由壳退场需求 |
| | `.sce/specs/00-129-current-phase-admin-verify-pending-wrapper-retirement/design.md` | — | ✅ 已新增：明确用 router `props` 直连 `VerificationBoard.vue`，不改 verify 业务逻辑 |
| | `.sce/specs/00-129-current-phase-admin-verify-pending-wrapper-retirement/tasks.md` | — | ✅ 已回填：`PendingView.vue` 退场任务链已完成 |
| | `.sce/specs/00-129-current-phase-admin-verify-pending-wrapper-retirement/execution.md` | — | ✅ 已回填：记录删除前 wrapper 证据、router 改造与浏览器复核 |
| | `kaipai-admin/src/router/index.ts` | — | ✅ 已改造：`/verify/pending` 已直接承接 `VerificationBoard.vue + props` |
| | `kaipai-admin/src/views/verify/PendingView.vue` | — | ✅ 已删除：verify 待审核历史薄包装路由壳 |
| | `output/playwright/00-129/verify-pending-after.png` | — | ✅ 已新增：`/verify/pending` 仍保持 pending 队列语义的浏览器截图 |
| 00-130 current-phase-admin-contact-requests-ia-metadata-alignment | `.sce/specs/00-130-current-phase-admin-contact-requests-ia-metadata-alignment/requirements.md` | — | ✅ 已新增：固化 `/content/contact-requests` mainline/tooling 元数据失真对齐需求 |
| | `.sce/specs/00-130-current-phase-admin-contact-requests-ia-metadata-alignment/design.md` | — | ✅ 已新增：明确只修 route meta 与 tooling 描述，不改页面业务逻辑 |
| | `.sce/specs/00-130-current-phase-admin-contact-requests-ia-metadata-alignment/tasks.md` | — | ✅ 已回填：IA 元数据对齐任务链已完成 |
| | `.sce/specs/00-130-current-phase-admin-contact-requests-ia-metadata-alignment/execution.md` | — | ✅ 已回填：记录 IA 冲突证据、route meta 修正与浏览器复核 |
| | `kaipai-admin/src/router/index.ts` | — | ✅ 已改造：`/content/contact-requests` 已切回 tooling route meta |
| | `kaipai-admin/src/constants/admin-information-architecture.ts` | — | ✅ 已改造：补齐联系方式申请页的明确 tooling 描述 |
| | `output/playwright/00-130/contact-requests-ia-after.png` | — | ✅ 已新增：联系方式申请页已按 tooling 壳层显示的浏览器截图 |
| 00-131 current-phase-admin-verify-history-route-alignment | `.sce/specs/00-131-current-phase-admin-verify-history-route-alignment/requirements.md` | — | ✅ 已新增：固化 `/verify/history` hidden tooling 路由补齐需求 |
| | `.sce/specs/00-131-current-phase-admin-verify-history-route-alignment/design.md` | — | ✅ 已新增：明确复用 `VerificationBoard.vue + mode='history'`，不新增重复页面组件 |
| | `.sce/specs/00-131-current-phase-admin-verify-history-route-alignment/tasks.md` | — | ✅ 已回填：verify history 路由对齐任务链已完成 |
| | `.sce/specs/00-131-current-phase-admin-verify-history-route-alignment/execution.md` | — | ✅ 已回填：记录权限合同证据、route 补齐与浏览器复核 |
| | `kaipai-admin/src/router/index.ts` | — | ✅ 已改造：新增 `/verify/history`，并以 `page.verify.history` 门禁直连 `VerificationBoard.vue` |
| | `output/playwright/00-131/verify-history-after.png` | — | ✅ 已新增：`/verify/history` 已进入 history 回看语义的浏览器截图 |
| 00-132 current-phase-admin-content-publish-logs-route-alignment | `.sce/specs/00-132-current-phase-admin-content-publish-logs-route-alignment/requirements.md` | — | ✅ 已新增：固化 `/content/publish-logs` hidden tooling 路由与容器补齐需求 |
| | `.sce/specs/00-132-current-phase-admin-content-publish-logs-route-alignment/design.md` | — | ✅ 已新增：明确只补 publish-logs，只读承接模板发布台账 |
| | `.sce/specs/00-132-current-phase-admin-content-publish-logs-route-alignment/tasks.md` | — | ✅ 已回填：publish-logs 路由对齐任务链已完成 |
| | `.sce/specs/00-132-current-phase-admin-content-publish-logs-route-alignment/execution.md` | — | ✅ 已回填：记录角色授权、live API 证据、页面补齐与浏览器复核 |
| | `kaipai-admin/src/views/content/PublishLogsView.vue` | — | ✅ 已新增：模板发布记录 hidden tooling 页面容器 |
| | `kaipai-admin/src/types/content.ts` | — | ✅ 已改造：新增模板发布记录 query/item/page result 类型 |
| | `kaipai-admin/src/api/content.ts` | — | ✅ 已改造：新增 `fetchTemplatePublishLogs(...)` API 装配 |
| | `kaipai-admin/src/constants/menus.ts` | — | ✅ 已改造：`adminMenus.content` 新增 `/content/publish-logs` 能力库存登记 |
| | `kaipai-admin/src/constants/admin-information-architecture.ts` | — | ✅ 已改造：补齐 `/content/publish-logs` tooling 前缀与治理说明 |
| | `kaipai-admin/src/router/index.ts` | — | ✅ 已改造：新增 `/content/publish-logs` hidden tooling route |
| | `output/playwright/00-132/publish-logs-after.png` | — | ✅ 已新增：模板发布记录页面真实运行态截图 |
| 00-133 current-phase-admin-content-theme-tokens-route-alignment | `.sce/specs/00-133-current-phase-admin-content-theme-tokens-route-alignment/requirements.md` | — | ✅ 已新增：固化 `/content/theme-tokens` hidden tooling 路由与最小编辑页面补齐需求 |
| | `.sce/specs/00-133-current-phase-admin-content-theme-tokens-route-alignment/design.md` | — | ✅ 已新增：明确补齐 theme-tokens 的列表、详情与最小 JSON 编辑 |
| | `.sce/specs/00-133-current-phase-admin-content-theme-tokens-route-alignment/tasks.md` | — | ✅ 已回填：theme-tokens 路由对齐任务链已完成 |
| | `.sce/specs/00-133-current-phase-admin-content-theme-tokens-route-alignment/execution.md` | — | ✅ 已回填：记录角色授权、live API 证据、页面补齐与浏览器复核 |
| | `kaipai-admin/src/views/content/ThemeTokensView.vue` | — | ✅ 已新增：主题 Token hidden tooling 页面容器 |
| | `kaipai-admin/src/types/content.ts` | — | ✅ 已改造：新增主题 Token query/item/page result/update payload 类型 |
| | `kaipai-admin/src/api/content.ts` | — | ✅ 已改造：新增 `fetchThemeTokens(...)` 与 `updateThemeTokens(...)` API 装配 |
| | `kaipai-admin/src/constants/menus.ts` | — | ✅ 已改造：`adminMenus.content` 新增 `/content/theme-tokens` 能力库存登记 |
| | `kaipai-admin/src/constants/admin-information-architecture.ts` | — | ✅ 已改造：补齐 `/content/theme-tokens` tooling 前缀与治理说明 |
| | `kaipai-admin/src/router/index.ts` | — | ✅ 已改造：新增 `/content/theme-tokens` hidden tooling route |
| | `output/playwright/00-133/theme-tokens-after.png` | — | ✅ 已新增：主题 Token 页面真实运行态截图 |
| 00-134 current-phase-admin-content-share-artifacts-route-alignment | `.sce/specs/00-134-current-phase-admin-content-share-artifacts-route-alignment/requirements.md` | — | ✅ 已新增：固化 `/content/share-artifacts` hidden tooling 路由与最小编辑页面补齐需求 |
| | `.sce/specs/00-134-current-phase-admin-content-share-artifacts-route-alignment/design.md` | — | ✅ 已新增：明确补齐 share-artifacts 的列表、详情与最小 JSON 编辑 |
| | `.sce/specs/00-134-current-phase-admin-content-share-artifacts-route-alignment/tasks.md` | — | ✅ 已回填：share-artifacts 路由对齐任务链已完成 |
| | `.sce/specs/00-134-current-phase-admin-content-share-artifacts-route-alignment/execution.md` | — | ✅ 已回填：记录后端合同、前端缺口、页面补齐与浏览器复核 |
| | `kaipai-admin/src/views/content/ShareArtifactsView.vue` | — | ✅ 已新增：分享产物配置 hidden tooling 页面容器 |
| | `kaipai-admin/src/types/content.ts` | — | ✅ 已改造：新增分享产物 query/item/page result/update payload 类型 |
| | `kaipai-admin/src/api/content.ts` | — | ✅ 已改造：新增 `fetchShareArtifacts(...)` 与 `updateShareArtifacts(...)` API 装配 |
| | `kaipai-admin/src/constants/menus.ts` | — | ✅ 已改造：`adminMenus.content` 新增 `/content/share-artifacts` 能力库存登记 |
| | `kaipai-admin/src/constants/admin-information-architecture.ts` | — | ✅ 已改造：补齐 `/content/share-artifacts` tooling 前缀与治理说明 |
| | `kaipai-admin/src/router/index.ts` | — | ✅ 已改造：新增 `/content/share-artifacts` hidden tooling route |
| | `output/playwright/00-134/share-artifacts-after.png` | — | ✅ 已新增：分享产物配置页面真实运行态截图 |
| 00-135 current-phase-admin-router-static-routes-retirement | `.sce/specs/00-135-current-phase-admin-router-static-routes-retirement/requirements.md` | — | ✅ 已新增：固化 `src/router/static-routes.ts` 的单文件退场需求 |
| | `.sce/specs/00-135-current-phase-admin-router-static-routes-retirement/design.md` | — | ✅ 已新增：明确只处理未消费的历史静态路由表，不扩到其它候选 |
| | `.sce/specs/00-135-current-phase-admin-router-static-routes-retirement/tasks.md` | — | ✅ 已回填：static-routes 单文件退场任务链已完成 |
| | `.sce/specs/00-135-current-phase-admin-router-static-routes-retirement/execution.md` | — | ✅ 已回填：记录静态路由职责、无 consumer 证据、删除动作与构建验证 |
| | `kaipai-admin/src/router/static-routes.ts` | — | ✅ 已删除：未被消费的历史静态路由表已完成退场 |
| 00-136 current-phase-admin-audit-confirm-dialog-compat-wrapper-retirement | `.sce/specs/00-136-current-phase-admin-audit-confirm-dialog-compat-wrapper-retirement/requirements.md` | — | ✅ 已新增：固化 `src/components/AuditConfirmDialog.vue` 的单文件退场需求 |
| | `.sce/specs/00-136-current-phase-admin-audit-confirm-dialog-compat-wrapper-retirement/design.md` | — | ✅ 已新增：明确只处理顶层 compat wrapper，不扩到 canonical dialog |
| | `.sce/specs/00-136-current-phase-admin-audit-confirm-dialog-compat-wrapper-retirement/tasks.md` | — | ✅ 已回填：AuditConfirmDialog compat wrapper 退场任务链已完成 |
| | `.sce/specs/00-136-current-phase-admin-audit-confirm-dialog-compat-wrapper-retirement/execution.md` | — | ✅ 已回填：记录 compat wrapper 职责、consumer 搜索证据、删除动作与构建验证 |
| | `kaipai-admin/src/components/AuditConfirmDialog.vue` | — | ✅ 已删除：未被消费的顶层 compat wrapper 已完成退场 |
| 00-137 current-phase-admin-business-component-canonical-takeover-retirement-first-pass | `.sce/specs/00-137-current-phase-admin-business-component-canonical-takeover-retirement-first-pass/requirements.md` | — | ✅ 已新增：固化 business canonical 接管后的旧组件入口第一批退场需求 |
| | `.sce/specs/00-137-current-phase-admin-business-component-canonical-takeover-retirement-first-pass/design.md` | — | ✅ 已新增：明确只处理被 `components/business/*` 接管的旧组件入口，`SearchTableLayout` 不纳入本轮 |
| | `.sce/specs/00-137-current-phase-admin-business-component-canonical-takeover-retirement-first-pass/tasks.md` | — | ✅ 已回填：business canonical 接管旧组件退场任务链已完成 |
| | `.sce/specs/00-137-current-phase-admin-business-component-canonical-takeover-retirement-first-pass/execution.md` | — | ✅ 已回填：记录旧入口无 consumer 证据、删除动作与构建验证 |
| | `kaipai-admin/src/components/PageContainer.vue` | — | ✅ 已删除：旧页面容器入口已被 business canonical 接管后退场 |
| | `kaipai-admin/src/components/PermissionButton.vue` | — | ✅ 已删除：旧权限按钮入口已被 business canonical 接管后退场 |
| | `kaipai-admin/src/components/StatusTag.vue` | — | ✅ 已删除：旧状态标签入口已被 business canonical 接管后退场 |
| | `kaipai-admin/src/components/layout/PageContainer.vue` | — | ✅ 已删除：layout 目录旧页面容器入口已完成退场 |
| | `kaipai-admin/src/components/layout/FilterPanel.vue` | — | ✅ 已删除：layout 目录旧筛选面板入口已完成退场 |
| 00-138 current-phase-admin-search-table-layout-dual-version-retirement | `.sce/specs/00-138-current-phase-admin-search-table-layout-dual-version-retirement/requirements.md` | — | ✅ 已新增：固化 SearchTableLayout 双版本退场需求 |
| | `.sce/specs/00-138-current-phase-admin-search-table-layout-dual-version-retirement/design.md` | — | ✅ 已新增：明确只处理双版本历史列表壳层，不扩到其它组件 |
| | `.sce/specs/00-138-current-phase-admin-search-table-layout-dual-version-retirement/tasks.md` | — | ✅ 已回填：SearchTableLayout 双版本退场任务链已完成 |
| | `.sce/specs/00-138-current-phase-admin-search-table-layout-dual-version-retirement/execution.md` | — | ✅ 已回填：记录双版本职责、零 consumer 证据、删除动作与构建验证 |
| | `kaipai-admin/src/components/SearchTableLayout.vue` | — | ✅ 已删除：顶层 SearchTableLayout 历史实现已完成退场 |
| | `kaipai-admin/src/components/tables/SearchTableLayout.vue` | — | ✅ 已删除：tables 目录 SearchTableLayout 历史实现已完成退场 |
| 00-139 current-phase-admin-missing-backend-notice-retirement | `.sce/specs/00-139-current-phase-admin-missing-backend-notice-retirement/requirements.md` | — | ✅ 已新增：固化 MissingBackendNotice 单文件退场需求 |
| | `.sce/specs/00-139-current-phase-admin-missing-backend-notice-retirement/design.md` | — | ✅ 已新增：明确只处理零 consumer 的独立提示组件 |
| | `.sce/specs/00-139-current-phase-admin-missing-backend-notice-retirement/tasks.md` | — | ✅ 已回填：MissingBackendNotice 退场任务链已完成 |
| | `.sce/specs/00-139-current-phase-admin-missing-backend-notice-retirement/execution.md` | — | ✅ 已回填：记录组件职责、零 consumer 证据、删除动作与构建验证 |
| | `kaipai-admin/src/components/business/MissingBackendNotice.vue` | — | ✅ 已删除：未被消费的提示组件已完成退场 |
| 00-140 current-phase-admin-shell-ia-and-template-config-alignment | `.sce/specs/00-140-current-phase-admin-shell-ia-and-template-config-alignment/requirements.md` | — | ✅ 已新增：固化侧栏固定高度、机构管理退场与模板可视化配置的联合需求 |
| | `.sce/specs/00-140-current-phase-admin-shell-ia-and-template-config-alignment/design.md` | — | ✅ 已新增：明确只做机构正式架构退场与模板配置第一批，不删机构页面本体 |
| | `.sce/specs/00-140-current-phase-admin-shell-ia-and-template-config-alignment/tasks.md` | — | ✅ 已回填：壳层 / IA / 模板配置对齐任务链已完成 |
| | `.sce/specs/00-140-current-phase-admin-shell-ia-and-template-config-alignment/execution.md` | — | ✅ 已回填：记录侧栏问题根因、机构模块来源链、模板可视化配置落地与验证结果 |
| | `kaipai-admin/src/components/layout/AdminSidebar.vue` | — | ✅ 已改造：左侧菜单固定视口高度并内部滚动 |
| | `kaipai-admin/src/constants/menus.ts` | — | ✅ 已改造：正式侧栏已移除机构管理 |
| | `kaipai-admin/src/constants/admin-information-architecture.ts` | — | ✅ 已改造：机构管理已退出 growth mainline IA |
| | `kaipai-admin/src/router/index.ts` | — | ✅ 已改造：`/users/orgs` 已降为 `retire-candidate` |
| | `kaipai-admin/src/views/dashboard/OverviewView.vue` | — | ✅ 已改造：正式页面矩阵已移除机构管理 |
| | `kaipai-admin/src/components/layout/AdminTopbar.vue` | — | ✅ 已改造：主线搜索文案已移除机构口径 |
| | `kaipai-admin/src/views/content/TemplatesView.vue` | — | ✅ 已改造：模板编辑弹窗已切到主题配置、产物配置与小程序预览，并生成 JSON 保存 |
| 00-141 current-phase-admin-organization-page-runtime-retirement | `.sce/specs/00-141-current-phase-admin-organization-page-runtime-retirement/requirements.md` | — | ✅ 已新增：固化后台机构管理页面本体退场需求与删除门禁 |
| | `.sce/specs/00-141-current-phase-admin-organization-page-runtime-retirement/design.md` | — | ✅ 已新增：明确只删除后台机构管理页面本体，不扩展到小程序端和后端 company 接口 |
| | `.sce/specs/00-141-current-phase-admin-organization-page-runtime-retirement/tasks.md` | — | ✅ 已回填：机构管理页面本体退场任务链已完成 |
| | `.sce/specs/00-141-current-phase-admin-organization-page-runtime-retirement/execution.md` | — | ✅ 已回填：记录删除前证据、删除动作、构建验证与 `/users/orgs` 404 浏览器复核 |
| | `kaipai-admin/src/router/index.ts` | — | ✅ 已改造：已删除 `/users/orgs` route，旧直达地址不再进入机构管理页 |
| | `kaipai-admin/src/views/user/OrganizationsView.vue` | — | ✅ 已删除：后台机构管理页面本体已退场 |
| | `kaipai-admin/src/api/company.ts` | — | ✅ 已删除：机构管理页面专用 company API 装配已退场 |
| | `kaipai-admin/src/types/company.ts` | — | ✅ 已删除：机构管理页面专用 company 类型已退场 |
| 00-142 current-phase-admin-template-visual-configurator-deepening | `.sce/specs/00-142-current-phase-admin-template-visual-configurator-deepening/requirements.md` | — | ✅ 已新增：固化模板可视化配置深化需求与小程序页面配置边界 |
| | `.sce/specs/00-142-current-phase-admin-template-visual-configurator-deepening/design.md` | — | ✅ 已新增：明确 pageConfig、phone shell 预览与 JSON 生成策略 |
| | `.sce/specs/00-142-current-phase-admin-template-visual-configurator-deepening/tasks.md` | — | ✅ 已回填：模板可视化配置深化任务链已完成 |
| | `.sce/specs/00-142-current-phase-admin-template-visual-configurator-deepening/execution.md` | — | ✅ 已回填：记录页面配置器深化、构建验证与真实浏览器复核 |
| 00-143 current-phase-template-page-config-runtime-alignment | `.sce/specs/00-143-current-phase-template-page-config-runtime-alignment/requirements.md` | — | ✅ 已新增：固化 pageConfig 从后台配置器透传到后端 DTO 与小程序运行时的闭环需求 |
| | `.sce/specs/00-143-current-phase-template-page-config-runtime-alignment/design.md` | — | ✅ 已新增：明确 pageConfig、layoutPreset 与旧 layoutVariant 的兼容边界 |
| | `.sce/specs/00-143-current-phase-template-page-config-runtime-alignment/tasks.md` | — | ✅ 已回填：pageConfig 运行时闭环任务链已完成 |
| | `.sce/specs/00-143-current-phase-template-page-config-runtime-alignment/execution.md` | — | ✅ 已回填：记录后端编译修复、后台兼容映射与验证结果 |
| | `kaipai-admin/src/views/content/TemplatesView.vue` | 00-142, 00-143 | ✅ 已完成：新增 `layoutPreset -> layoutVariant` 兼容映射，后台不再把 `portfolio / casting` 直接写入旧运行时字段 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/CardSceneTemplateServiceImpl.java` | 00-143 | ✅ 已完成：修正 pageConfig layoutPreset 到 runtime layoutVariant 的兼容归一调用，后端编译恢复通过 |
| | `kaipaile-server/src/main/resources/db/migration/V20260424_010__share_card_runtime_instance_backfill.sql` | 00-143, 00-145 | ✅ 已新增：补 share-card runtime follow-up migration，回填缺失的 `share_card_id` 实例绑定 |
| 00-144 current-phase-miniapp-framework-refactor-and-ui-review | `.sce/specs/00-144-current-phase-miniapp-framework-refactor-and-ui-review/requirements.md` | — | ✅ 已新增：固化前台框架重构与 UI 审查评分模型、95 分阈值与继续修改规则 |
| | `.sce/specs/00-144-current-phase-miniapp-framework-refactor-and-ui-review/design.md` | — | ✅ 已新增：明确审查对象、评分维度、扣分规则与验证链 |
| | `.sce/specs/00-144-current-phase-miniapp-framework-refactor-and-ui-review/tasks.md` | — | ✅ 已回填：本轮审查、修改、构建与文档回填任务已完成 |
| | `kaipai-frontend/src/pages/home/index.vue` | 00-73, 00-144 | ✅ 已完成：移除 home 内的 crew 退场可见分支，恢复统一 HomeScreen 壳层并将 crew 降级收口到动作层 |
| | `.sce/specs/00-144-current-phase-miniapp-framework-refactor-and-ui-review/execution.md` | — | ✅ 已回填：记录初始 92 分、home 收口修改与复评分 95 分的证据链 |
| 00-145 current-phase-backend-admin-database-review | `.sce/specs/00-145-current-phase-backend-admin-database-review/requirements.md` | — | ✅ 已新增：固化后端 API / 后台管理 / 数据库三条评分线与 95 分阈值 |
| | `.sce/specs/00-145-current-phase-backend-admin-database-review/design.md` | — | ✅ 已新增：明确并行取证、分线评分与最小补改策略 |
| | `.sce/specs/00-145-current-phase-backend-admin-database-review/tasks.md` | — | ✅ 已新增：跨后端 / 后台 / 数据库审查任务链 |
| | `.sce/specs/00-145-current-phase-backend-admin-database-review/execution.md` | — | ✅ 已回填：记录三条线初始评分、修复项、验证结果与复评分 |
| | `kaipai-admin/src/views/content/TemplatesView.vue` | — | ✅ 已深化：新增 `pageConfig`、布局预设 / 背景质感 / 视觉密度 / Hero 形式 / 模块显隐 / 行动区配置，并写入 `artifactPresetJson.pageConfig` |
| 00-53 current-phase-crew-recruit-mock-retirement | `.sce/specs/00-53-current-phase-crew-recruit-mock-retirement/requirements.md` | — | ✅ 已新增：当前阶段剧组招募链路前端 Mock 退场需求 |
| | `.sce/specs/00-53-current-phase-crew-recruit-mock-retirement/design.md` | — | ✅ 已新增：当前阶段剧组招募链路前端 Mock 退场设计 |
| | `.sce/specs/00-53-current-phase-crew-recruit-mock-retirement/tasks.md` | — | ✅ 已新增：当前阶段剧组招募链路前端 Mock 退场任务 |
| | `.sce/specs/00-53-current-phase-crew-recruit-mock-retirement/execution.md` | — | ✅ 已新增：当前阶段剧组招募链路前端 Mock 退场执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md` | — | ✅ 已完成：补充 recruit 当前阶段前端 mock 退场已由 `00-53` 接管 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md` | — | ✅ 已完成：新增 `00-53` 回填记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/crew-company-project-status.md` | — | ✅ 已完成：明确 `company/project/role` 前端已不再保留 mock 分支 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/recruit-role-apply-status.md` | — | ✅ 已完成：明确 `role/apply` 前端已不再保留 mock 分支 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将 recruit 前端 mock 退场提升为 `00-53` 独立 Spec |
| | `kaipai-frontend/src/api/company.ts` | — | ✅ 已完成：移除 company API mock 分支，统一走真实接口 |
| | `kaipai-frontend/src/api/project.ts` | — | ✅ 已完成：移除 project API mock 分支，统一走真实接口 |
| | `kaipai-frontend/src/api/role.ts` | — | ✅ 已完成：移除 role API mock 分支，保留 query sanitization 后统一走真实接口 |
| | `kaipai-frontend/src/api/apply.ts` | — | ✅ 已完成：移除 apply API mock 分支，统一走真实接口 |
| | `kaipai-frontend/src/utils/runtime.ts` | — | ✅ 已完成：删除无使用方的 `company/project/role/roleRead/apply` capability |
| | `kaipai-frontend/src/mock/service.ts` | — | ✅ 已完成：删除无入口的 company / project / role / apply mock 服务 |
| | `kaipai-frontend/src/mock/database.ts` | — | ✅ 已完成：删除已无引用的剧组招募 mock 数据 |
| 00-54 current-phase-actor-mainline-mock-retirement | `.sce/specs/00-54-current-phase-actor-mainline-mock-retirement/requirements.md` | — | ✅ 已新增：当前阶段演员主线前端 Mock 退场需求 |
| | `.sce/specs/00-54-current-phase-actor-mainline-mock-retirement/design.md` | — | ✅ 已新增：当前阶段演员主线前端 Mock 退场设计 |
| | `.sce/specs/00-54-current-phase-actor-mainline-mock-retirement/tasks.md` | — | ✅ 已新增：当前阶段演员主线前端 Mock 退场任务 |
| | `.sce/specs/00-54-current-phase-actor-mainline-mock-retirement/execution.md` | — | ✅ 已新增：当前阶段演员主线前端 Mock 退场执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md` | — | ✅ 已完成：补充演员主线前端 mock 退场已由 `00-54` 接管 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md` | — | ✅ 已完成：新增 `00-54` 回填记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/recruit-role-apply-status.md` | — | ✅ 已完成：明确演员首页与 actor 主线前端已不再保留 mock 分支 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将 actor 主线前端 mock 退场提升为 `00-54` 独立 Spec |
| | `kaipai-frontend/src/api/actor.ts` | — | ✅ 已完成：移除 actor API mock 分支，统一走真实接口 |
| | `kaipai-frontend/src/utils/runtime.ts` | — | ✅ 已完成：删除无使用方的 `actor` capability |
| | `kaipai-frontend/src/mock/service.ts` | — | ✅ 已完成：删除无入口 actor API mock 函数 |
| 00-55 current-phase-invite-verify-fortune-mock-retirement | `.sce/specs/00-55-current-phase-invite-verify-fortune-mock-retirement/requirements.md` | — | ✅ 已新增：当前阶段邀请 / 实名 / 命理前端 Mock 退场需求 |
| | `.sce/specs/00-55-current-phase-invite-verify-fortune-mock-retirement/design.md` | — | ✅ 已新增：当前阶段邀请 / 实名 / 命理前端 Mock 退场设计 |
| | `.sce/specs/00-55-current-phase-invite-verify-fortune-mock-retirement/tasks.md` | — | ✅ 已新增：当前阶段邀请 / 实名 / 命理前端 Mock 退场任务 |
| | `.sce/specs/00-55-current-phase-invite-verify-fortune-mock-retirement/execution.md` | — | ✅ 已新增：当前阶段邀请 / 实名 / 命理前端 Mock 退场执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md` | — | ✅ 已完成：补充 invite / verify / fortune 前端 mock 退场已由 `00-55` 接管 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md` | — | ✅ 已完成：新增 `00-55` 回填记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/invite-status.md` | — | ✅ 已完成：明确 invite 前端已不再保留 mock 分支 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/verify-status.md` | — | ✅ 已完成：明确 verify 前端已不再保留 mock 分支 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/membership-status.md` | — | ✅ 已完成：明确 `/fortune/*` 前端已不再保留 mock 分支 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将 invite / verify / fortune 前端 mock 退场提升为 `00-55` 独立 Spec |
| | `kaipai-frontend/src/api/invite.ts` | — | ✅ 已完成：移除 invite API mock 分支，统一走真实接口 |
| | `kaipai-frontend/src/api/verify.ts` | — | ✅ 已完成：移除 verify API mock 分支，统一走真实接口 |
| | `kaipai-frontend/src/api/fortune.ts` | — | ✅ 已完成：移除 fortune API mock 分支，统一走真实接口 |
| | `kaipai-frontend/src/utils/runtime.ts` | — | ✅ 已完成：删除无使用方的 `invite / verify / fortune` capability |
| | `kaipai-frontend/src/mock/service.ts` | — | ✅ 已完成：删除无入口 invite / verify / fortune API mock 函数 |
| | `kaipai-frontend/src/mock/database.ts` | — | ✅ 已完成：删除已无引用的 verify / fortune mock 数据 |
| | `kaipai-frontend/src/pkg-card/actor-card/index.vue` | — | ✅ 已完成：分享产物 query 仅接受当前阶段两种类型，旧 artifact 自动归一化 |
| | `kaipai-frontend/src/pkg-card/membership/index.vue` | — | ✅ 已完成：邀请概览文案已改为“邀请记录页”口径 |
| | `kaipai-frontend/src/pages/actor-profile/detail.vue` | — | ✅ 已完成：公开名片分享态不再依赖后端 `publicCardPage` artifact 才能恢复 |
| 00-56 current-phase-level-card-ai-runtime-mock-retirement | `.sce/specs/00-56-current-phase-level-card-ai-runtime-mock-retirement/requirements.md` | — | ✅ 已新增：当前阶段等级 / 名片 / AI 运行时 Mock 退场需求 |
| | `.sce/specs/00-56-current-phase-level-card-ai-runtime-mock-retirement/design.md` | — | ✅ 已新增：当前阶段等级 / 名片 / AI 运行时 Mock 退场设计 |
| | `.sce/specs/00-56-current-phase-level-card-ai-runtime-mock-retirement/tasks.md` | — | ✅ 已新增：当前阶段等级 / 名片 / AI 运行时 Mock 退场任务 |
| | `.sce/specs/00-56-current-phase-level-card-ai-runtime-mock-retirement/execution.md` | — | ✅ 已新增：当前阶段等级 / 名片 / AI 运行时 Mock 退场执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md` | — | ✅ 已完成：补充 `level / card / ai` 前端 mock 退场已由 `00-56` 接管 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md` | — | ✅ 已完成：新增 `00-56` 回填记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/membership-status.md` | — | ✅ 已完成：membership 状态页补充 `00-56` 对 `level / card` 双轨退场的影响 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/ai-resume-status.md` | — | ✅ 已完成：AI 状态页补充 `00-56` 对 `/ai/*` 前端 mock 退场的影响 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将 `level / card / ai` 前端 mock 退场提升为 `00-56` 独立 Spec |
| | `kaipai-frontend/src/api/level.ts` | — | ✅ 已完成：`level / card / ai quota` 接口统一只认真实请求 |
| | `kaipai-frontend/src/api/ai.ts` | — | ✅ 已完成：AI 主链接口统一只认真实 `/api/ai/*` |
| | `kaipai-frontend/src/api/personalization.ts` | — | ✅ 已完成：删除只服务于本地 fallback 的 helper |
| | `kaipai-frontend/src/utils/personalization.ts` | — | ✅ 已完成：删除 personalization 本地拼装 fallback，统一只认 `/api/card/personalization` |
| | `kaipai-frontend/src/utils/runtime.ts` | — | ✅ 已完成：删除 `level / card / ai` capability |
| | `kaipai-frontend/src/mock/service.ts` | — | ✅ 已完成：删除无入口 `level / card / ai` mock 函数与 helper |
| | `kaipai-frontend/src/mock/database.ts` | — | ✅ 已完成：删除已无引用的 `level / card / ai` mock 数据 |
| 00-57 current-phase-session-upload-runtime-boundary-alignment | `.sce/specs/00-57-current-phase-session-upload-runtime-boundary-alignment/requirements.md` | — | ✅ 已新增：当前阶段会话摘要 / 身份切换 / 上传运行时边界对齐需求 |
| | `.sce/specs/00-57-current-phase-session-upload-runtime-boundary-alignment/design.md` | — | ✅ 已新增：当前阶段会话摘要 / 身份切换 / 上传运行时边界对齐设计 |
| | `.sce/specs/00-57-current-phase-session-upload-runtime-boundary-alignment/tasks.md` | — | ✅ 已新增：当前阶段会话摘要 / 身份切换 / 上传运行时边界对齐任务 |
| | `.sce/specs/00-57-current-phase-session-upload-runtime-boundary-alignment/execution.md` | — | ✅ 已新增：当前阶段会话摘要 / 身份切换 / 上传运行时边界对齐执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md` | — | ✅ 已完成：补充 session / upload 运行时边界收口已由 `00-57` 接管 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md` | — | ✅ 已完成：新增 `00-57` 回填记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/login-auth-status.md` | — | ✅ 已完成：明确 `/user/me / user/role` 已不再保留独立 runtime capability |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/crew-company-project-status.md` | — | ✅ 已完成：明确 upload 已不再保留独立 runtime capability |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/membership-status.md` | — | ✅ 已完成：同步更新 runtime capability 剩余口径 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将 session / upload runtime boundary 收口提升为 `00-57` 独立 Spec |
| | `kaipai-frontend/src/api/auth.ts` | — | ✅ 已完成：`getUserInfo / updateUserRole` 收口为显式 mock 演示态或真实 `/api/user/*` |
| | `kaipai-frontend/src/utils/upload.ts` | — | ✅ 已完成：上传收口为显式 mock 演示态或真实 `/api/file/upload/*` |
| | `kaipai-frontend/src/utils/runtime.ts` | — | ✅ 已完成：删除 `userInfo / roleSwitch / upload` capability |
| 00-58 current-phase-auth-runtime-boundary-alignment | `.sce/specs/00-58-current-phase-auth-runtime-boundary-alignment/requirements.md` | — | ✅ 已新增：当前阶段鉴权运行时边界对齐需求 |
| | `.sce/specs/00-58-current-phase-auth-runtime-boundary-alignment/design.md` | — | ✅ 已新增：当前阶段鉴权运行时边界对齐设计 |
| | `.sce/specs/00-58-current-phase-auth-runtime-boundary-alignment/tasks.md` | — | ✅ 已新增：当前阶段鉴权运行时边界对齐任务 |
| | `.sce/specs/00-58-current-phase-auth-runtime-boundary-alignment/execution.md` | — | ✅ 已新增：当前阶段鉴权运行时边界对齐执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md` | — | ✅ 已完成：补充 auth runtime capability 表退场已由 `00-58` 接管 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md` | — | ✅ 已完成：新增 `00-58` 回填记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/login-auth-status.md` | — | ✅ 已完成：明确 auth runtime capability 表已退场 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/membership-status.md` | — | ✅ 已完成：同步更新 runtime 表退场后的口径 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将 auth runtime capability 表退场提升为 `00-58` 独立 Spec |
| | `kaipai-frontend/src/utils/runtime.ts` | — | ✅ 已完成：删除 `ApiCapability / REMOTE_CAPABILITIES / useApiMock` |
| | `kaipai-frontend/src/api/auth.ts` | — | ✅ 已完成：`auth / wechatAuth` 收口为显式 mock 演示态或真实 `/api/auth/*` |
| 00-61 current-phase-auth-explicit-mock-retirement | `.sce/specs/00-61-current-phase-auth-explicit-mock-retirement/requirements.md` | — | ✅ 已新增：当前阶段鉴权显式 Mock 退场需求 |
| | `.sce/specs/00-61-current-phase-auth-explicit-mock-retirement/design.md` | — | ✅ 已新增：当前阶段鉴权显式 Mock 退场设计 |
| | `.sce/specs/00-61-current-phase-auth-explicit-mock-retirement/tasks.md` | — | ✅ 已新增：当前阶段鉴权显式 Mock 退场任务 |
| | `.sce/specs/00-61-current-phase-auth-explicit-mock-retirement/execution.md` | — | ✅ 已新增：当前阶段鉴权显式 Mock 退场执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md` | — | ✅ 已完成：补充 auth 显式 mock 退场已由 `00-61` 接管 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md` | — | ✅ 已完成：新增 `00-61` 回填记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/execution/login-auth/README.md` | — | ✅ 已完成：补充 `00-61` 后的 login-auth 运行时门禁口径 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/login-auth-status.md` | — | ✅ 已完成：明确 auth 显式 mock 与 mock 文件已退场 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将 auth 显式 mock 退场提升为 `00-61` 独立 Spec |
| | `kaipai-frontend/src/api/auth.ts` | — | ✅ 已完成：auth 主链统一只认真实 `/api/auth/*` 与 `/api/user/*` |
| | `kaipai-frontend/src/stores/user.ts` | — | ✅ 已完成：删除 mock 会话恢复分支，统一以 `/api/user/me` 恢复会话 |
| | `kaipai-frontend/src/utils/runtime.ts` | — | ✅ 已完成：`VITE_USE_MOCK=true` 且缺少 baseUrl 时显式阻塞 auth 域 |
| | `kaipai-frontend/src/pages/login/index.vue` | — | ✅ 已完成：验证码弹窗与微信门禁改按真实 auth 语义展示 |
| 00-62 current-phase-minimal-share-card-mvp-alignment | `.sce/specs/00-62-current-phase-minimal-share-card-mvp-alignment/requirements.md` | — | ✅ 已新增：当前阶段最小分享名片 MVP 需求 |
| | `.sce/specs/00-62-current-phase-minimal-share-card-mvp-alignment/design.md` | — | ✅ 已新增：当前阶段最小分享名片 MVP 设计 |
| | `.sce/specs/00-62-current-phase-minimal-share-card-mvp-alignment/tasks.md` | — | ✅ 已新增：当前阶段最小分享名片 MVP 任务 |
| | `.sce/specs/00-62-current-phase-minimal-share-card-mvp-alignment/execution.md` | — | ✅ 已新增：当前阶段最小分享名片 MVP 执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md` | — | ✅ 已完成：新增 `00-62` 回填记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md` | — | ✅ 已完成：将当前产品第一优先级切换到 `00-62` |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将当前主风险修正为 `00-62` 已落位第一批真实结构，但仍未完全闭环 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/project-structure-map.md` | — | ✅ 已完成：新增 `00-62` 作为当前 MVP 主线定位入口 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/share-card-mvp-status.md` | — | ✅ 已新增：`00-62` 当前阶段独立状态卡 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/execution/share-card-mvp/README.md` | — | ✅ 已新增：`00-62` 最小执行资产目录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/execution/share-card-mvp/samples/20260404-local-share-card-mvp-governance-smoke/summary.md` | — | ✅ 已新增：`00-62` 最小治理样本 |
| | `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java` | — | ✅ 已完成：新增后台联系方式申请治理接口 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ShareCardContactRequestServiceImpl.java` | — | ✅ 已完成：补齐后台联系方式申请列表 / 详情聚合 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/card/dto/AdminContactRequestQueryDTO.java` | — | ✅ 已新增：后台联系方式申请查询 DTO |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/card/dto/AdminContactRequestItemDTO.java` | — | ✅ 已新增：后台联系方式申请列表 DTO |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/card/dto/AdminContactRequestDetailDTO.java` | — | ✅ 已新增：后台联系方式申请详情 DTO |
| | `kaipai-admin/src/views/content/ContactRequestsView.vue` | — | ✅ 已新增：后台联系方式申请治理页 |
| | `kaipai-admin/src/api/content.ts` | — | ✅ 已扩展：后台联系方式申请治理 API |
| | `kaipai-admin/src/types/content.ts` | — | ✅ 已扩展：后台联系方式申请治理类型 |
| | `kaipai-admin/src/constants/menus.ts` | — | ✅ 已完成：新增“联系方式申请”后台菜单 |
| | `kaipai-admin/src/router/index.ts` | — | ✅ 已完成：新增“联系方式申请”后台路由 |
| | `kaipai-admin/src/constants/permission-registry.ts` | — | ✅ 已完成：新增 `page.content.contact-requests` 权限登记 |
| 00-59 current-phase-ai-governance-scheduled-sweep | `.sce/specs/00-59-current-phase-ai-governance-scheduled-sweep/requirements.md` | — | ✅ 已新增：AI 治理定时 sweep 需求 |
| | `.sce/specs/00-59-current-phase-ai-governance-scheduled-sweep/design.md` | — | ✅ 已新增：调度开关、Redis 锁与统一请求标识设计 |
| | `.sce/specs/00-59-current-phase-ai-governance-scheduled-sweep/tasks.md` | — | ✅ 已新增：AI 定时 sweep 任务 |
| | `.sce/specs/00-59-current-phase-ai-governance-scheduled-sweep/execution.md` | — | ✅ 已新增：AI 定时 sweep 执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/ai-resume-status.md` | — | ✅ 已完成：同步更新 AI 治理“后台定时调度任务”状态口径 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：同步更新 AI 剩余主阻塞为真实通知渠道 / 回执与真实 LLM |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md` | — | ✅ 已完成：将 AI 定时 sweep 收口到 `00-59` |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/execution/ai-resume/README.md` | — | ✅ 已完成：将 AI 定时调度后续入口显式绑定到 `00-59` |
| | `kaipaile-server/src/main/java/com/kaipai/KaipaiApplication.java` | — | ✅ 已完成：启用 Spring Scheduling |
| | `kaipaile-server/src/main/java/com/kaipai/common/auth/AdminOperationLogCommand.java` | — | ✅ 已完成：支持显式 requestId 透传 |
| | `kaipaile-server/src/main/java/com/kaipai/common/auth/AdminOperationLogger.java` | — | ✅ 已完成：优先使用命令侧 requestId，保证定时 sweep 审计归并 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/ai/dto/AdminAiResumeGovernanceSweepRequestDTO.java` | — | ✅ 已完成：新增定时 sweep requestId 透传位 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/ai/dto/AdminAiResumeGovernanceSweepResultDTO.java` | — | ✅ 已完成：补齐 sweep 结果请求标识与触发来源摘要 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/config/AiResumeGovernanceSchedulerProperties.java` | — | ✅ 已完成：新增 AI 定时 sweep 配置模型 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/job/AiResumeGovernanceSweepScheduler.java` | — | ✅ 已完成：新增 AI 定时 sweep 任务与 Redis 防重入锁 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/impl/AdminAiResumeGovernanceServiceImpl.java` | — | ✅ 已完成：治理 sweep 支持系统操作者与统一 requestId |
| | `kaipaile-server/src/main/resources/application.yml` | — | ✅ 已完成：新增 AI 定时 sweep 默认配置 |
| 00-60 current-phase-ai-governance-real-notification-foundation | `.sce/specs/00-60-current-phase-ai-governance-real-notification-foundation/requirements.md` | — | ✅ 已新增：AI 治理真实通知基础设施需求 |
| | `.sce/specs/00-60-current-phase-ai-governance-real-notification-foundation/design.md` | — | ✅ 已新增：真实通知基础设施、人工补录与回执采集边界设计 |
| | `.sce/specs/00-60-current-phase-ai-governance-real-notification-foundation/tasks.md` | — | ✅ 已新增：AI 真实通知基础设施任务 |
| | `.sce/specs/00-60-current-phase-ai-governance-real-notification-foundation/execution.md` | — | ✅ 已新增：AI 真实通知基础设施执行记录 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/ai-resume-status.md` | — | ✅ 已完成：将 AI 当前剩余主阻塞从泛化协同缺口收口到 `00-60` |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将 AI 当前结构性风险改写为真实通知基础设施缺口 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md` | — | ✅ 已完成：将 AI 第一优先级改写为 `00-60` |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/execution/ai-resume/README.md` | — | ✅ 已完成：将 AI 执行入口显式收口到 `00-60` |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java` | — | ✅ 已确认：`sendCode` 仅为 login-auth 开发态验证码能力，不可复用为 AI 通知基础设施 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/system/entity/AdminUser.java` | — | ✅ 已确认：当前仅存在后台账号候选联系字段，尚无独立治理通知接收地址模型 |
| | `kaipaile-server/src/main/resources/db/migration/V20260404_002__ai_resume_notification_delivery.sql` | — | ✅ 已完成：新增 AI 治理通知投递长期事实表 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/ai/entity/AiResumeNotificationDelivery.java` | — | ✅ 已完成：新增 AI 治理通知投递实体 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/mapper/AiResumeNotificationDeliveryMapper.java` | — | ✅ 已完成：新增 AI 治理通知投递 mapper |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/AiResumeNotificationDeliveryService.java` | — | ✅ 已完成：新增 AI 治理通知投递服务接口 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/impl/AiResumeNotificationDeliveryServiceImpl.java` | — | ✅ 已完成：新增人工补录写 delivery 长期事实的服务实现 |
| | `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/ai/AdminAiResumeController.java` | — | ✅ 已完成：后台人工通知/回执入口已接入统一通知主链与长期 delivery 摘要 |
| | `kaipaile-server/src/main/java/com/kaipai/module/controller/ai/AiResumeNotificationReceiptController.java` | — | ✅ 已完成：新增 provider callback 入站接口 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/config/AiResumeNotificationProperties.java` | — | ✅ 已完成：新增 AI 通知 provider / callback / http bridge 配置模型 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/provider/AiResumeNotificationProvider.java` | — | ✅ 已完成：新增 AI 通知 provider 抽象 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/provider/ManualAiResumeNotificationProvider.java` | — | ✅ 已完成：新增 manual provider 骨架 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/provider/HttpAiResumeNotificationProvider.java` | — | ✅ 已完成：新增通用 http bridge provider，实现固定 JSON 契约出站 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/AiResumeNotificationDispatchService.java` | — | ✅ 已完成：新增统一 dispatch / receipt ingest 服务接口 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/impl/AiResumeNotificationDispatchServiceImpl.java` | — | ✅ 已完成：统一 dispatch、delivery 摘要回填与 provider callback 归并 |
| | `.sce/runbooks/backend-admin-release/scripts/ai_notification_secret_inputs.py` | — | ✅ 已完成：AI 通知 provider-aware 本地输入门禁 |
| | `.sce/runbooks/backend-admin-release/scripts/run-backend-ai-notification-config-sync-pipeline.py` | — | ✅ 已完成：AI 通知 Nacos 总控支持 http provider 输入位 |
| | `.sce/config/ai-resume-notification.env.example` | — | ✅ 已完成：本地 secret 模板补齐 http provider 输入位 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/execution/ai-resume/run-ai-resume-notification-foundation-validation.py` | — | ✅ 已完成：通知基础设施验证脚本支持 provider-code 可切换 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/execution/ai-resume/run-ai-notification-http-bridge-mock.py` | — | ✅ 已完成：新增 http bridge mock gateway 标准样本入口，并支持 callbackUrl 自动回调 smoke |
| | `.sce/config/ai-notification-http-bridge.env.example` | — | ✅ 已完成：新增 `provider=http` bridge 输入模板 |
| | `.sce/runbooks/backend-admin-release/scripts/ai_notification_http_bridge_inputs.py` | — | ✅ 已完成：新增 bridge 输入解析与派生 runtime 值工具 |
| | `.sce/runbooks/backend-admin-release/scripts/init-local-ai-notification-http-bridge-secret-file.py` | — | ✅ 已完成：新增 bridge gitignored secret 初始化入口 |
| | `.sce/runbooks/backend-admin-release/scripts/read-local-ai-notification-http-bridge-inputs.py` | — | ✅ 已完成：新增 bridge 本地门禁与 blocked 证据入口 |
| | `.sce/runbooks/backend-admin-release/scripts/run-ai-notification-http-provider-rollout.py` | — | ✅ 已完成：新增 `provider=http` 标准总控，固定 bridge-input -> config-sync -> backend-only -> validation |
| | `.sce/runbooks/backend-admin-release/ai-notification-http-provider-rollout-runbook.md` | — | ✅ 已完成：新增 `provider=http` 发布 runbook |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/config/AiResumeNotificationProperties.java` | — | ✅ 已完成：新增 AI 通知 provider / callback 配置属性 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/provider/AiResumeNotificationProvider.java` | — | ✅ 已完成：新增 AI 通知 provider 适配层接口 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/provider/ManualAiResumeNotificationProvider.java` | — | ✅ 已完成：新增默认 manual provider，占位真实商用通知适配层 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/AiResumeNotificationDispatchService.java` | — | ✅ 已完成：新增 AI 通知统一 dispatch / receipt ingest 服务接口 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/impl/AiResumeNotificationDispatchServiceImpl.java` | — | ✅ 已完成：新增 AI 通知统一 dispatch、delivery 落库、callback 归并与审计实现 |
| | `kaipaile-server/src/main/java/com/kaipai/module/controller/ai/AiResumeNotificationReceiptController.java` | — | ✅ 已完成：新增 provider callback 入站控制器与 header token 校验 |
| | `kaipaile-server/src/main/resources/application.yml` | — | ✅ 已完成：新增 `kaipai.ai.resume.notification.*` 配置块 |
| | `kaipaile-server/src/main/java/com/kaipai/common/config/SecurityConfig.java` | — | ✅ 已完成：放通 AI provider callback 白名单路径 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/impl/AdminAiResumeGovernanceServiceImpl.java` | — | ✅ 已完成第二批：`record-notification` 正常发送分支与 `governance-sweep auto_remind` 已切到统一 dispatch service，人工 `send_failed` 继续保留补录口径 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/ai/dto/AiResumeFailureRecordDTO.java` | — | ✅ 已完成：failure record 补充最新 delivery 摘要字段 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/ai/dto/AiResumeFailureHandlingNoteDTO.java` | — | ✅ 已完成：治理时间线补充最新 delivery 摘要字段 |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/ai/dto/AdminAiResumeFailureItemDTO.java` | — | ✅ 已完成：后台 failure item 补充 delivery 摘要字段 |
| | `kaipai-admin/src/types/ai.ts` | — | ✅ 已完成：后台类型补充 AI 治理 delivery 摘要字段 |
| | `kaipai-admin/src/views/system/AiResumeGovernanceView.vue` | — | ✅ 已完成第二批：后台列表、详情抽屉与动作弹窗已显式展示通知主链 / 回执主链 / provider / 接收人状态 / 当前排障结论；后续仍需补完整来源筛选与真实 vendor 样本联动排障 |
| | `.sce/config/ai-resume-notification.env.example` | — | ✅ 已完成：新增 AI 通知本地 secret 模板 |
| | `.sce/runbooks/backend-admin-release/scripts/ai_notification_secret_inputs.py` | — | ✅ 已完成：新增 AI 通知本地 secret 解析与合法性门禁工具 |
| | `.sce/runbooks/backend-admin-release/scripts/init-local-ai-notification-secret-file.py` | — | ✅ 已完成：新增 AI 通知 gitignored secret 初始化入口 |
| | `.sce/runbooks/backend-admin-release/scripts/read-local-ai-notification-config-inputs.py` | — | ✅ 已完成：新增 AI 通知本地输入只读检查入口 |
| | `.sce/runbooks/backend-admin-release/scripts/run-backend-ai-notification-config-sync-pipeline.py` | — | ✅ 已完成：新增 AI 通知配置同步总控，固定 `local-input -> remote nacos precheck -> nacos sync` 顺序 |
| | `.sce/runbooks/backend-admin-release/ai-notification-config-gate-runbook.md` | — | ✅ 已完成：新增 AI 通知配置门禁单页 runbook |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/execution/ai-resume/run-ai-resume-notification-foundation-validation.py` | — | ✅ 已完成：新增 `00-60` 通知基础设施标准验证脚本入口，固化 dispatch / callback / manual failure 样本 |
| | `.sce/specs/00-28-architecture-driven-delivery-governance/execution/ai-resume/README.md` | — | ✅ 已完成：补 AI 通知基础设施脚本入口与环境变量说明 |

## 00 — 全局基础

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 00-01 global-style-system | `src/styles/_tokens.scss` | — | ✅ 已实现 |
| | `src/styles/_mixins.scss` | — | ✅ 已实现 |
| | `src/styles/_page-layout.scss` | — | ✅ 已实现 |
| | `src/styles/_reset.scss` | — | ✅ 已实现 |
| | `src/styles/index.scss` | — | ✅ 已实现 |
| | `src/uni.scss` | — | ✅ 已实现 |
| 00-02 shared-components | `src/components/Kp*.vue`（31 个） | — | ✅ 已实现 |
| | `src/components/KpIdentityStatusCard.vue` | — | ✅ 已新增：实名认证状态卡片 |
| | `src/components/KpInviteSummaryCard.vue` | — | ✅ 已新增：邀请裂变概览卡片 |
| | `src/components/KpLevelProgressCard.vue` | — | ✅ 已新增：等级进度卡片 |
| | `src/components/KpColorPalettePicker.vue` | — | ✅ 已新增：色盘选择器 |
| | `src/components/KpShareArtifactTabs.vue` | — | ✅ 已新增：分享产物切换组件 |
| | `src/components/KpThemePreviewCard.vue` | — | ✅ 已新增：主题预览卡片 |
| | `src/components/KpCapabilityMatrixCard.vue` | — | ✅ 已新增：能力矩阵卡片 |
| 00-03 shared-utils-api | `src/types/*.ts`（12 个） | — | ✅ 已实现 |
| | `src/utils/*.ts`（17 个） | — | ✅ 已实现 |
| | `src/stores/user.ts` | — | ✅ 已实现 |
| | `src/api/*.ts`（11 个） | — | ✅ 已实现 |
| 00-04 document-governance | `docs/product-design.md` | — | ✅ 已切换为当前主线文档 |
| | `docs/archive/product-design-v1.2-2026-03-23.md` | — | ✅ 已归档历史版本 |
| | `docs/dev-playbook.md` | — | ✅ 已补充文档治理基线 |
| 00-05 mini-program-package-governance | `kaipai-frontend/scripts/audit-mp-package.ps1` | — | ✅ 已新增，按构建产物审计主包 / 分包体积 |
| | `kaipai-frontend/package.json` | — | ✅ 已补充 `audit:mp-package` 命令 |
| 00-06 bundle-size-first-pass | `src/pages/apply-confirm/index.vue` | — | ✅ 已移除 barrel 组件引用 |
| | `src/pages/home/index.vue` | — | ✅ 已移除 barrel 组件引用 |
| | `src/pages/mine/index.vue` | 660 | ✅ 已移除 barrel 组件引用 |
| | `src/pages/actor-profile/edit.vue` | 677 | ✅ 已移除 barrel 组件引用 |
| | `src/pages/actor-profile/detail.vue` | 361 | ✅ 已移除 barrel 组件引用 |
| | `src/pages/my-applies/index.vue` | — | ✅ 已移除 barrel 组件引用 |
| | `src/pages/login/index.vue` | — | ✅ 已移除 barrel 组件引用 |
| | `src/pkg-card/actor-card/index.vue` | 878 | ✅ 已移除 barrel 组件引用 |
| | `src/pkg-card/membership/index.vue` | 279 | ✅ 已移除 barrel 组件引用 |
| | `src/pkg-tools/video-player/index.vue` | 27 | ✅ 已移除 barrel 组件引用 |
| | `src/components/index.ts` | — | ✅ 已删除失效聚合入口 |
| 00-07 first-subpackage-migration | `src/pages.json` | — | ✅ 已新增 `pkg-card` / `pkg-tools` 分包配置 |
| | `src/pkg-card/actor-card/index.vue` | 878 | ✅ 已迁入演员增强主线分包 |
| | `src/pkg-card/membership/index.vue` | 279 | ✅ 已迁入演员增强主线分包 |
| | `src/pkg-card/verify/index.vue` | — | ✅ 已纳入演员增强主线分包 |
| | `src/pkg-card/invite/index.vue` | — | ✅ 已纳入演员增强主线分包 |
| | `src/pkg-card/fortune/index.vue` | — | 历史记录：曾纳入演员增强分包，当前由 `00-149` 物理退场 |
| | `src/pkg-tools/webview/index.vue` | 604 | ✅ 已迁入工具分包 |
| | `src/pkg-tools/video-player/index.vue` | 27 | ✅ 已迁入工具分包 |
| | `src/utils/actor-card.ts` | — | ✅ 已更新分享路径到新分包页面 |
| | `kaipai-frontend/scripts/audit-mp-package.ps1` | 117 | ✅ 已修复 `subPackages` 识别逻辑 |
| 00-08 style-system-governance | `src/styles/_inject.scss` | — | ✅ 已新增样式注入桥接层 |
| | `src/styles/_mixins.scss` | — | ✅ 已切换到 `@use './tokens' as *` |
| | `src/styles/_reset.scss` | — | ✅ 已切换到 `@use './inject' as *` |
| | `src/styles/_page-layout.scss` | — | ✅ 已切换到 `@use './inject' as *` |
| | `src/styles/index.scss` | — | ✅ 已切换到 `@use` 样式入口 |
| | `src/App.vue` | — | ✅ 已切换到 `@use '@/styles/index.scss' as *` |
| | `vite.config.ts` | — | ✅ 已切换全局注入到 `@use "@/styles/_inject.scss" as *` |
| 00-09 shared-style-shells | `src/styles/_mixins.scss` | — | ✅ 已新增返回按钮 / 固定操作栏公共 mixin |
| | `src/pages/apply-confirm/index.vue` | — | ✅ 已回接返回按钮与底部操作栏 mixin |
| | `src/pages/apply-detail/index.vue` | — | ✅ 已回接返回按钮与底部操作栏 mixin |
| | `src/pages/role-detail/index.vue` | — | ✅ 已回接返回按钮与底部操作栏 mixin |
| | `src/pages/project/create.vue` | — | ✅ 已回接返回按钮与底部操作栏 mixin |
| | `src/pages/project/role-create.vue` | — | ✅ 已回接返回按钮与底部操作栏 mixin |
| | `src/pages/company-profile/edit.vue` | — | ✅ 已回接返回按钮与底部操作栏 mixin |
| | `src/pages/my-applies/index.vue` | — | ✅ 已回接返回按钮 mixin |
| | `src/pages/apply-manage/index.vue` | — | ✅ 已回接返回按钮 mixin |
| | `src/pages/actor-profile/edit.vue` | — | ✅ 已回接返回按钮与底部操作栏 mixin |
| | `src/pkg-tools/webview/index.vue` | — | ✅ 已回接返回按钮 mixin |
| | `src/pkg-card/actor-card/index.vue` | — | ✅ 已回接返回按钮与底部操作栏 mixin |

## 01 — 公共页面

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 01-01 page-login | `src/pages/login/index.vue` | 526 | ✅ 已实现 |
| 01-02 page-role-select | `src/pages/role-select/index.vue` | 222 | ✅ 已实现 |

## 02 — 首页

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 02-01 page-home-actor | `src/pages/home/index.vue`（演员视角） | 1,030 | ✅ 已实现 |
| 02-02 page-home-crew | `src/pages/home/index.vue`（剧组视角） | 同上 | ✅ 已实现 |

## 03 — 演员端页面

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 03-01 page-role-detail | `src/pages/role-detail/index.vue` | 600 | ✅ 已实现 |
| 03-02 page-apply-confirm | `src/pages/apply-confirm/index.vue` | 677 | ✅ 已实现 |
| 03-03 page-my-applies | `src/pages/my-applies/index.vue` | 568 | ✅ 已实现 |
| 03-04 page-actor-profile-edit | `src/pages/actor-profile/edit.vue` | 673 | ✅ 已实现 |
| 03-05 page-mine | `src/pages/mine/index.vue` | 696 | ✅ 已实现 |

## 04 — 剧组端页面（代码保留，业务主线已迁移后台）

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 04-01 page-project-create | `src/pages/project/create.vue` | 695 | ✅ 已实现 |
| 04-02 page-role-create | `src/pages/project/role-create.vue` | 981 | ✅ 已实现 |
| 04-03 page-apply-manage | `src/pages/apply-manage/index.vue` | 580 | ✅ 已实现 |
| 04-04 page-actor-profile-detail | `src/pages/actor-profile/detail.vue` | 361 | ✅ 已增强为公开详情页 |
| 04-05 page-company-profile-edit | `src/pages/company-profile/edit.vue` | 1,094 | ✅ 已实现 |

## 无独立 Spec 页面

| 源文件 | 行数 | 说明 |
|--------|------|------|
| `src/pkg-tools/video-player/index.vue` | 27 | 视频播放工具页（已迁入分包） |
| `src/pkg-tools/webview/index.vue` | 604 | 内嵌网页容器（已迁入分包） |
| `src/pages/apply-detail/index.vue` | 496 | 申请详情页 |

## 05 — 演员增强功能（进行中）

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 05-01 actor-card | `src/pkg-card/actor-card/index.vue` | — | 🗂 历史方案，当前主线由 05-05 接管 |
| 05-02 actor-profile-enhance | `src/pages/actor-profile/edit.vue`（增强目标页） | 673 | ✅ 已在单页中增强落地 |
| | `src/pages/actor-profile/profile-enhance.ts` | — | ✅ 已新增（供档案增强 / 名片逻辑复用） |
| | `src/types/actor.ts`（扩展字段） | — | ✅ 已扩展 |
| 05-03 credit-score | `src/pages/credit-score/index.vue` | — | ⏸ 当前产品阶段搁置，当前分支已删除 |
| | `src/pages/credit-record/index.vue` | — | ⏸ 当前产品阶段搁置，当前分支已删除 |
| | `src/pages/credit-rank/index.vue` | — | ⏸ 当前产品阶段搁置，当前分支已删除 |
| | `src/types/credit.ts` | — | ⏸ 当前产品阶段搁置，当前分支已删除 |
| | `src/api/credit.ts` | — | ⏸ 当前产品阶段搁置，当前分支已删除 |
| | `src/utils/credit.ts` | — | ⏸ 当前产品阶段搁置，当前分支已删除 |
| 05-04 ai-resume-polish | `src/pages/actor-profile/edit.vue`（AI 编辑页与 patch 应用主入口） | 677 | ✅ 已完成：AI 面板、patch 预览、应用、历史与回滚 UI |
| | `src/pages/actor-profile/ai-resume.ts` | — | ✅ 已新增：AI 上下文组装、fieldKey 解析与表单写回 helper |
| | `src/api/ai.ts` | — | ✅ 已新增：quota / polish / history / rollback 接口装配 |
| | `src/types/ai.ts` | — | ✅ 已新增：AI patch、历史、失败样本与治理模型 |
| | `src/pkg-card/actor-card/index.vue` | 878 | ✅ 已完成：名片页 AI 入口跳转编辑页并在返回后刷新本人档案 |
| | `kaipai-admin/src/views/system/AiResumeGovernanceView.vue` | — | ✅ 已完成：AI 治理页 overview / histories / failures / sensitive-hits / collaboration |
| | `kaipaile-server/src/main/java/com/kaipai/module/controller/ai/AiController.java` | — | ✅ 已完成：actor 侧 quota / polish / history / rollback 接口 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/impl/AiResumeServiceImpl.java` | — | ✅ 已完成：patch 草稿、历史与回滚服务链 |
| 05-05 card-share-membership (v2) | `src/pkg-card/actor-card/index.vue` | — | ✅ 已重构：场景名片 + 等级权限 + 配色定制 |
| | `src/pkg-card/membership/index.vue` | — | ✅ 已重写为等级中心页 |
| | `src/pages/actor-profile/detail.vue` | 361 | ✅ 已调整为公开详情页 |
| | `src/types/membership.ts` | — | ✅ 已删除，由 `types/level.ts` 替代 |
| | `src/utils/membership.ts` | — | ✅ 已删除，由 `utils/level.ts` 替代 |
| | `src/types/level.ts` | — | ✅ 已新增：等级枚举、场景模板、定制配置类型 |
| | `src/utils/level.ts` | — | ✅ 已新增：等级计算、能力矩阵 |
| | `src/api/level.ts` | — | ✅ 已新增：等级/模板/定制/配额接口 |
| | `src/utils/actor-card.ts` | — | ✅ 已改造：scene 分享参数、场景摘要、主题合并 |
| | `src/pages/mine/index.vue` | 720 | ✅ 已适配新等级体系入口 |
| 05-06 mainline-residual-cleanup | `src/pages/mine/index.vue` | 706 | ✅ 已清理旧英文身份文案与 fake 统计 |
| | `src/pages/actor-profile/edit.vue` | 677 | ✅ 已收敛为中文档案状态文案 |
| 05-07 mainline-component-refactor | `src/utils/floating-back-nav.ts` | — | ✅ 已新增，统一浮动返回导航定位逻辑 |
| | `src/utils/media-picker.ts` | — | ✅ 已新增，统一图片 / 视频选择逻辑 |
| | `src/components/KpSectionHead.vue` | 58 | ✅ 已新增，收敛主线段落头展示壳层 |
| | `src/components/KpPillSelector.vue` | 79 | ✅ 已新增，收敛主线胶囊选择器展示壳层 |
| | `src/components/KpMineMenuItem.vue` | 77 | ✅ 已新增，收敛我的页菜单项外壳 |
| | `src/pkg-card/actor-card/index.vue` | 878 | ✅ 已接入浮动返回导航 + 段落头 / 胶囊选择器组件 |
| | `src/pages/actor-profile/edit.vue` | 677 | ✅ 已接入浮动返回导航 + 媒体选择工具 |
| | `src/pages/company-profile/edit.vue` | 1094 | ✅ 已接入浮动返回导航 + 媒体选择工具 |
| | `src/pages/mine/index.vue` | 660 | ✅ 已接入菜单项外壳组件 |
| | `src/pages/role-detail/index.vue` | 600 | ✅ 已接入浮动返回导航工具 |
| | `src/pkg-tools/webview/index.vue` | 604 | ✅ 已接入浮动返回导航工具 |

| 00-149 current-phase-fortune-domain-physical-retirement | `.sce/specs/00-149-current-phase-fortune-domain-physical-retirement/requirements.md` | — | ✅ 已新增：旧 fortune / 命理 / 幸运色域物理退场需求 |
| | `.sce/specs/00-149-current-phase-fortune-domain-physical-retirement/design.md` | — | ✅ 已新增：后端、数据库、小程序、文档删除策略 |
| | `.sce/specs/00-149-current-phase-fortune-domain-physical-retirement/tasks.md` | — | ✅ 已新增：删除、构建、发布、线上审查任务清单 |
| | `.sce/specs/00-149-current-phase-fortune-domain-physical-retirement/execution.md` | — | ✅ 已新增：执行记录，当前未完成前不得收尾 |
| 00-172 current-phase-ai-profile-card-pdf-resume-flow-alignment | `.sce/specs/00-172-current-phase-ai-profile-card-pdf-resume-flow-alignment/requirements.md` | — | ✅ 已新增：AI 分享图详情页 PDF 简历展示范围同步需求 |
| | `.sce/specs/00-172-current-phase-ai-profile-card-pdf-resume-flow-alignment/design.md` | — | ✅ 已新增：AI 详情页 PDF 内容流设计 |
| | `.sce/specs/00-172-current-phase-ai-profile-card-pdf-resume-flow-alignment/tasks.md` | — | ✅ 已新增：实现与验证任务 |
| | `.sce/specs/00-172-current-phase-ai-profile-card-pdf-resume-flow-alignment/execution.md` | — | ✅ 已新增：执行记录与验证结果 |
| | `src/pkg-card/ai-profile-card-detail/index.vue` | — | ✅ 已改造：主题内容流新增 PDF 简历图片页 section，展示资格复用 `ActorProfile.resumePdfPageImageUrls` |
| 00-173 current-phase-wechat-phone-login-enablement | `.sce/specs/00-173-current-phase-wechat-phone-login-enablement/requirements.md` | — | ✅ 已新增：微信后台能力开通后的真实一键登录启用需求 |
| | `.sce/specs/00-173-current-phase-wechat-phone-login-enablement/design.md` | — | ✅ 已新增：小程序 getPhoneNumber 与后端 wechat-login 设计 |
| | `.sce/specs/00-173-current-phase-wechat-phone-login-enablement/tasks.md` | — | ✅ 已新增：前后端实现与验证任务 |
| | `.sce/specs/00-173-current-phase-wechat-phone-login-enablement/execution.md` | — | ✅ 已新增：执行记录 |
| | `kaipai-frontend/src/utils/runtime.ts` | — | ✅ 已改造：微信登录入口默认启用，显式 `VITE_ENABLE_WECHAT_AUTH=false` 时关闭 |
| | `kaipai-frontend/src/pages/login/index.vue` | — | ✅ 已改造：校验 getPhoneNumber code 后调用后端 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java` | — | ✅ 已改造：微信首次自动注册默认演员身份 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/wechat/service/WechatMiniProgramService.java` | — | ✅ 已改造：新增手机号授权 code 换手机号服务合同 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/wechat/service/impl/WechatMiniProgramServiceImpl.java` | — | ✅ 已改造：集中调用微信 `getuserphonenumber` |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/auth/dto/LoginRespDTO.java` | — | ✅ 已改造：登录响应补齐手机号，避免微信登录用户态缺少 phone |
| | `kaipaile-server/src/main/java/com/kaipai/module/model/auth/dto/WechatLoginReqDTO.java` | — | ✅ 已改造：补充微信手机号授权 code 合同说明 |
| | `kaipaile-server/src/test/java/com/kaipai/module/server/auth/service/impl/AuthServiceImplTest.java` | — | ✅ 已新增：覆盖微信首次注册默认演员身份 |
| 00-174 current-phase-login-sms-review-gate | `.sce/specs/00-174-current-phase-login-sms-review-gate/requirements.md` | — | ✅ 已新增：验证码审核前登录页只开放微信一键登录需求 |
| | `.sce/specs/00-174-current-phase-login-sms-review-gate/design.md` | — | ✅ 已新增：登录页短信表单模板级门禁设计 |
| | `.sce/specs/00-174-current-phase-login-sms-review-gate/tasks.md` | — | ✅ 已新增：实现与验证任务 |
| | `.sce/specs/00-174-current-phase-login-sms-review-gate/execution.md` | — | ✅ 已新增：执行记录 |
| | `kaipai-frontend/src/pages/login/index.vue` | — | ✅ 已改造：移除验证码登录表单可见层，只保留微信一键登录 |
| 05-08 fortune-personalization | `src/pkg-card/fortune/index.vue` | — | 历史记录：旧命理画像展示页，当前由 `00-149` 物理退场，不作为实现依据 |
| | `src/types/fortune.ts` | — | 历史记录：旧命理类型，当前由 `00-149` 删除 |
| | `src/utils/fortune.ts` | — | 历史记录：旧生肖 / 星座 / 兜底报告工具，当前由 `00-149` 删除 |
| | `src/api/fortune.ts` | — | 历史记录：旧报告查询与幸运色接口，当前由 `00-149` 删除 |
| | `src/pages/mine/index.vue` | — | 历史记录：曾移除独立“我的命理”入口，不证明 fortune 属于当前主线 |
| | `src/pkg-card/actor-card/index.vue` | — | 历史记录：旧命理主题联动入口，当前不得保留 |
| 05-09 identity-verification | `src/pkg-card/verify/index.vue` | — | ✅ 已新增：实名认证提交页 |
| | `src/types/verify.ts` | — | ✅ 已新增 |
| | `src/api/verify.ts` | — | ✅ 已新增 |
| | `src/utils/verify.ts` | — | ✅ 已新增：身份证校验 / 脱敏 / 状态映射 |
| | `src/components/KpIdentityStatusCard.vue` | — | ✅ 已用于实名认证页 / 等级中心 / 名片页 |
| | `src/stores/user.ts` | — | ✅ 已集成认证状态同步 |
| | `src/pages/mine/index.vue` | — | ✅ 已新增认证入口与状态展示 |
| | `src/pkg-card/membership/index.vue` | — | ✅ 已新增认证入口与状态展示 |
| | `src/pkg-card/actor-card/index.vue` | — | ✅ 已新增未认证拦截与引导 |
| 05-10 invite-referral | `src/pkg-card/invite/index.vue` | — | ✅ 已新增：邀请记录页 + 海报 |
| | `src/types/invite.ts` | — | ✅ 已新增 |
| | `src/utils/invite.ts` | — | ✅ 已新增：邀请码 / 分享参数 / 脱敏规则 |
| | `src/api/invite.ts` | — | ✅ 已新增 |
| | `src/components/KpInviteSummaryCard.vue` | — | ✅ 已新增：邀请概览共享组件 |
| | `src/pages/login/index.vue` | 526 | ✅ 已改造：支持 inviteCode 参数 |
| | `src/stores/user.ts` | — | ✅ 已集成邀请统计 / 邀请码同步 |
| | `src/pkg-card/membership/index.vue` | — | ✅ 已新增邀请入口与概览卡 |
| | `src/pkg-card/actor-card/index.vue` | — | ✅ 已新增邀请引导入口 |
| 05-11 fortune-driven-share-personalization | `src/types/personalization.ts` | — | 历史记录：个性化模型曾包含 fortune 字段，当前由 `00-149` 清理旧字段 |
| | `src/api/personalization.ts` | — | 历史记录：当前接口装配层不得继续传 `loadFortune` |
| | `src/utils/personalization.ts` | — | 历史记录：旧聚合曾包含命理，当前聚合只保留等级 / 能力 / 模板配置 |
| | `src/utils/personalization-copy.ts` | — | 历史记录：旧页面文案不得继续出现命理驱动主题 |
| | `src/utils/verify.ts` | 05-09 | ✅ 已复用：认证 CTA 文案场景化变体，供 actor-card / invite / actor-profile/edit 共用 |
| | `src/utils/theme-resolver.ts` | — | ✅ 已新增：统一页面 / 海报 / 分享卡片主题解析 |
| | `src/utils/share-artifact.ts` | — | ✅ 已新增：统一分享产物解析 |
| | `src/components/KpDualActionRow.vue` | — | ✅ 已新增：双按钮分享动作行组件，收口 actor-card / membership CTA |
| | `src/pkg-card/actor-card/index.vue` | — | ✅ 已接入：主题预览 / 产物 tabs / 会员 gating |
| | `src/pkg-card/membership/index.vue` | — | ✅ 已接入：能力中心化与等级 / 会员拆分 |
| | `src/pkg-card/fortune/index.vue` | — | 历史记录：旧命理解释页当前由 `00-149` 删除 |
| | `src/pkg-card/invite/index.vue` | — | ✅ 已接入：邀请链路并入统一分享产物体系 |
| | `src/pages/actor-profile/detail.vue` | 361 | ✅ 已接入：按分享场景恢复公开页主题 |
| 05-12 share-invite-code-consolidation | `src/pkg-card/actor-card/index.vue` | — | ✅ 已完成：移除分享页 raw invite code 与复制邀请码动作，统一跳转邀请页 |
| | `src/pkg-card/membership/index.vue` | — | ✅ 已完成：收口为邀请统计与分享入口，不再展示 raw invite code |
| | `src/pkg-card/invite/index.vue` | — | ✅ 历史记录：05-12 曾按“邀请码 / 链接 / 海报 / 记录操作页”验收，当前阶段已由 `00-52` 改写为邀请记录页边界 |
| | `src/components/KpInviteSummaryCard.vue` | — | ✅ 已完成：新增 `showInviteCode`，默认分享态不展示邀请码 |
| | `src/utils/invite.ts` | — | ✅ 已验证：继续作为邀请码与邀请路径单一来源 |
| | `src/utils/share-artifact.ts` | — | ✅ 历史记录：05-12 曾承接 `inviteCard` 路径收口；当前阶段 runtime 口径已由 `00-52` 收口为两种分享产物 |
| | `kaipai-admin/src/views/referral/RiskView.vue` | — | ✅ 已验证：后台治理域保留邀请码筛选、列表与详情展示 |
| | `kaipai-admin/src/views/referral/RecordsView.vue` | — | ✅ 已验证：后台治理域保留邀请码与邀请码 ID 详情 |
| | `kaipai-admin/src/views/referral/EligibilityView.vue` | — | ✅ 已验证：后台治理域保留资格码筛选与治理动作 |
| | `kaipai-admin/src/views/referral/PoliciesView.vue` | — | ✅ 已验证：后台治理域保留邀请资格规则配置语义 |
| | `kaipai-admin/src/constants/menus.ts` | — | ✅ 已完成：顶级菜单从“邀请裂变”收口为“邀请治理” |
| | `kaipai-admin/src/constants/permission-registry.ts` | — | ✅ 已完成：权限树模块标签同步收口为“邀请治理” |
| | `kaipai-admin/src/constants/status.ts` | — | ✅ 已完成：工作台业务线口径同步收口为“邀请治理” |
| | `kaipai-admin/src/types/referral.ts` | — | ✅ 已验证：`inviteCode` / `inviteCodeId` / `grantCode` 类型仍完整存在 |
| | `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/referral/AdminReferralController.java` | — | ✅ 已验证：后台 referral 治理接口完整保留 |
| | `.sce/specs/05-12-share-invite-code-consolidation/admin-referral-retain-refactor-retire-matrix.md` | — | ✅ 已新增：后台邀请模块保留 / 改造 / 下线矩阵 |
| | `.sce/specs/05-12-share-invite-code-consolidation/execution.md` | — | ✅ 已新增：本轮执行、验证与产物证据记录 |

## 关注项

- `video-player / webview / apply-detail` 目前仍无独立 Spec，如继续演进应补建或并入既有 Spec
- 05-03 信用积分方案已转为历史保留，若后续重启必须另起 spec 校准当前产品模型
- 05-05 当前只接入前端会员态与本地 AI 文案优化规则，真实会员支付和真实 AI 接口仍待后续接入
- 05-11 第一轮骨架已落地；后续还需继续清理历史页面内散落判断，逐步把业务规则继续从页面层下沉到 resolver
- 00-27 已补为前端总纲；后续页面分组、共享边界和分包策略变化需先回写 00-27
- 00-62 已把当前阶段产品主线改写为“可分享卡片 / 查看历史 / 个人中心”最小 MVP；后续首页、公开详情、个人中心和分享主线改造需优先对齐 00-62
- AI 简历主链代码、样本和页面证据已收口；当前剩余高优先级缺口已切到 `00-60 current-phase-ai-governance-real-notification-foundation`，并与真实 LLM 接入保持并行但独立推进
- `docs/product-design.md` 已切到当前主线；旧综合产品文档已归档到 `docs/archive/`
- 当前已完成第一批真实分包迁移；后续若页面或资源继续膨胀，应继续按 spec 分批迁移，而不是回退到全部堆主包
- 当前已补充 `audit:mp-package` 审计脚本，可在每次 `build:mp-weixin` 后执行，持续跟踪主包 / 分包体积
