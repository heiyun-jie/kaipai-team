# Spec ↔ 代码映射表

> Spec 到实际源文件的双向追溯。更新时间：2026-04-01

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
| | `src/utils/theme-resolver.ts` | — | ✅ 已新增：统一页面 / 海报 / 分享卡片主题解析 |
| | `src/utils/share-artifact.ts` | — | ✅ 已新增：统一分享产物解析 |
| | `src/pkg-card/actor-card/index.vue` | — | ✅ 已接入：主题预览 / 产物 tabs / 会员 gating |
| | `src/pkg-card/membership/index.vue` | — | ✅ 已接入：能力中心化与等级 / 会员拆分 |
| | `src/pkg-card/fortune/index.vue` | — | ✅ 已接入：命理解释页回收为个性化输入源展示 |
| | `src/pkg-card/invite/index.vue` | — | ✅ 已接入：邀请链路并入统一分享产物体系 |
| | `src/pages/actor-profile/detail.vue` | 361 | ✅ 已接入：按分享场景恢复公开页主题 |

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
