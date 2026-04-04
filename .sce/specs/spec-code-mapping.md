# Spec ↔ 代码映射表

> Spec 到实际源文件的双向追溯。更新时间：2026-04-04

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
| | `kaipaile-server/src/main/java/com/kaipai/module/model/verify/dto/IdentityVerificationListReqDTO.java` | — | ✅ 已完成：verify 列表新增 submitTime 时间窗口字段 |
| | `kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/impl/IdentityVerificationServiceImpl.java` | — | ✅ 已完成：verify 列表按 create_time 执行提交时间窗口筛查 |
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
| | `kaipai-frontend/src/utils/share-artifact.ts` | — | ✅ 已完成：当前阶段 artifact helper 仅暴露两种分享产物，并保留公开名片 path helper 供 detail 页内部使用 |
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
| | `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/ai/AdminAiResumeController.java` | — | 🟡 待继续：当前仍只有人工 `record-notification` / `record-notification-receipt` 入口，尚无真实回执入站接口 |
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
| | `src/pkg-card/fortune/index.vue` | — | ✅ 已纳入演员增强主线分包 |
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

| 05-08 fortune-personalization | `src/pkg-card/fortune/index.vue` | — | ✅ 已新增：命理画像展示页 |
| | `src/types/fortune.ts` | — | ✅ 已新增 |
| | `src/utils/fortune.ts` | — | ✅ 已新增：生肖 / 星座推算与月度兜底报告 |
| | `src/api/fortune.ts` | — | ✅ 已新增：报告查询与幸运色应用接口 |
| | `src/pages/mine/index.vue` | — | ✅ 已移除独立“我的命理”入口，统一回收至名片能力中心主线 |
| | `src/pkg-card/actor-card/index.vue` | — | ✅ 已新增命理主题预览与分享主线联动入口 |
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
| 05-11 fortune-driven-share-personalization | `src/types/personalization.ts` | — | ✅ 已新增：个性化主模型 / 分享产物 / 能力控制类型 |
| | `src/api/personalization.ts` | — | ✅ 已新增：个性化接口装配层 |
| | `src/utils/personalization.ts` | — | ✅ 已新增：聚合等级 / 会员 / 命理 / 模板配置 |
| | `src/utils/personalization-copy.ts` | — | ✅ 已新增：页面级会员文案与主题说明共享 helper |
| | `src/utils/verify.ts` | 05-09 | ✅ 已复用：认证 CTA 文案场景化变体，供 actor-card / invite / actor-profile/edit 共用 |
| | `src/utils/theme-resolver.ts` | — | ✅ 已新增：统一页面 / 海报 / 分享卡片主题解析 |
| | `src/utils/share-artifact.ts` | — | ✅ 已新增：统一分享产物解析 |
| | `src/components/KpDualActionRow.vue` | — | ✅ 已新增：双按钮分享动作行组件，收口 actor-card / membership CTA |
| | `src/pkg-card/actor-card/index.vue` | — | ✅ 已接入：主题预览 / 产物 tabs / 会员 gating |
| | `src/pkg-card/membership/index.vue` | — | ✅ 已接入：能力中心化与等级 / 会员拆分 |
| | `src/pkg-card/fortune/index.vue` | — | ✅ 已接入：命理解释页回收为个性化输入源展示 |
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
- AI 简历主链代码、样本和页面证据已收口；当前剩余高优先级缺口已切到 `00-60 current-phase-ai-governance-real-notification-foundation`，并与真实 LLM 接入保持并行但独立推进
- `docs/product-design.md` 已切到当前主线；旧综合产品文档已归档到 `docs/archive/`
- 当前已完成第一批真实分包迁移；后续若页面或资源继续膨胀，应继续按 spec 分批迁移，而不是回退到全部堆主包
- 当前已补充 `audit:mp-package` 审计脚本，可在每次 `build:mp-weixin` 后执行，持续跟踪主包 / 分包体积
