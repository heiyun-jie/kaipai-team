# Spec ↔ 代码映射表

> Spec 到实际源文件的双向追溯。更新时间：2026-04-03

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
| | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` | — | ✅ 已完成：将 membership 主风险提升为独立治理入口 |

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
| 05-04 ai-resume-polish | `src/pages/actor-profile/edit.vue`（AI 入口挂载位） | 673 | 📝 待实现 |
| | `src/api/ai.ts`（规划） | — | 📝 待实现 |
| | `src/types/actor.ts`（AI patch / 对话状态，规划） | — | 📝 待实现 |
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
| | `src/pkg-card/invite/index.vue` | — | ✅ 已验证：仍为前台唯一邀请码 / 邀请链接 / 海报 / 记录操作页 |
| | `src/components/KpInviteSummaryCard.vue` | — | ✅ 已完成：新增 `showInviteCode`，默认分享态不展示邀请码 |
| | `src/utils/invite.ts` | — | ✅ 已验证：继续作为邀请码与邀请路径单一来源 |
| | `src/utils/share-artifact.ts` | — | ✅ 已验证：继续收口 `inviteCard` 分享产物路径 |
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
- AI 简历润色 Spec 已建，尚未落代码；后续需确认前后端接口边界与 patch 返回格式
- `docs/product-design.md` 已切到当前主线；旧综合产品文档已归档到 `docs/archive/`
- 当前已完成第一批真实分包迁移；后续若页面或资源继续膨胀，应继续按 spec 分批迁移，而不是回退到全部堆主包
- 当前已补充 `audit:mp-package` 审计脚本，可在每次 `build:mp-weixin` 后执行，持续跟踪主包 / 分包体积
