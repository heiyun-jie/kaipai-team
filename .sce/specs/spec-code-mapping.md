# Spec ↔ 代码映射表

> Spec 到实际源文件的双向追溯。更新时间：2026-03-31

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

## 00 — 全局基础

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 00-01 global-style-system | `src/styles/_tokens.scss` | — | ✅ 已实现 |
| | `src/styles/_mixins.scss` | — | ✅ 已实现 |
| | `src/styles/_page-layout.scss` | — | ✅ 已实现 |
| | `src/styles/_reset.scss` | — | ✅ 已实现 |
| | `src/styles/index.scss` | — | ✅ 已实现 |
| | `src/uni.scss` | — | ✅ 已实现 |
| 00-02 shared-components | `src/components/Kp*.vue`（19 个） | 1,612 | ✅ 已实现 |
| 00-03 shared-utils-api | `src/types/*.ts`（7 个） | — | ✅ 已实现 |
| | `src/utils/*.ts`（7 个） | — | ✅ 已实现 |
| | `src/stores/user.ts` | — | ✅ 已实现 |
| | `src/api/*.ts`（6 个） | — | ✅ 已实现 |

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
| 03-04 page-actor-profile-edit | `src/pages/actor-profile/edit.vue` | 1,180 | ✅ 已实现 |
| 03-05 page-mine | `src/pages/mine/index.vue` | 699 | ✅ 已实现 |

## 04 — 剧组端页面（代码保留，业务主线已迁移后台）

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 04-01 page-project-create | `src/pages/project/create.vue` | 695 | ✅ 已实现 |
| 04-02 page-role-create | `src/pages/project/role-create.vue` | 981 | ✅ 已实现 |
| 04-03 page-apply-manage | `src/pages/apply-manage/index.vue` | 580 | ✅ 已实现 |
| 04-04 page-actor-profile-detail | `src/pages/actor-profile/detail.vue` | 365 | ✅ 已增强为公开详情页 |
| 04-05 page-company-profile-edit | `src/pages/company-profile/edit.vue` | 1,094 | ✅ 已实现 |

## 无独立 Spec 页面

| 源文件 | 行数 | 说明 |
|--------|------|------|
| `src/pages/video-player/index.vue` | 27 | 视频播放工具页 |
| `src/pages/webview/index.vue` | 589 | 内嵌网页容器 |
| `src/pages/apply-detail/index.vue` | 496 | 申请详情页 |

## 05 — 演员增强功能（进行中）

| Spec | 源文件 | 行数 | 状态 |
|------|--------|------|------|
| 05-01 actor-card | `src/pages/actor-card/index.vue` | 430 | ✅ 已创建（分享/海报/mock 小程序码） |
| | `src/pages/actor-profile/detail.vue`（公开落地页） | 365 | ✅ 已完成公开展示改造 |
| | `src/utils/actor-card.ts` | — | ✅ 已新增共用展示/分享逻辑 |
| | `src/components/KpCreditBadge.vue` | — | ✅ 已创建（mock 占位） |
| 05-02 actor-profile-enhance | `src/pages/actor-profile/edit.vue`（增强目标页） | 1,180 | ✅ 已在单页中增强落地 |
| | `src/pages/actor-profile/profile-enhance.ts` | — | ✅ 已新增（供档案增强/名片逻辑复用） |
| | `src/types/actor.ts`（扩展字段） | — | ✅ 已扩展 |
| 05-03 credit-score | `src/pages/credit-score/index.vue` | 214 | ✅ 已创建 |
| | `src/pages/credit-record/index.vue` | 171 | ✅ 已创建 |
| | `src/pages/credit-rank/index.vue` | 189 | ✅ 已创建 |
| | `src/types/credit.ts` | — | ✅ 已创建 |
| | `src/api/credit.ts` | — | ✅ 已创建 |
| | `src/utils/credit.ts` | — | ✅ 已创建 |
| | `src/components/KpCreditBadge.vue` | — | ✅ 已增强 |
| | `src/components/KpLevelTag.vue` | — | ✅ 已增强 |
| 05-04 ai-resume-polish | `src/pages/actor-profile/edit.vue`（AI 入口挂载位） | 1,180 | 📝 待实现 |
| | `src/pages/actor-profile/components/AiPolish*.vue`（规划） | — | 📝 待实现 |
| | `src/api/actor.ts` / `src/api/ai.ts`（AI 润色接口，规划） | — | 📝 待实现 |
| | `src/types/actor.ts`（AI patch / 对话状态，规划） | — | 📝 待实现 |

## 关注项

- `video-player / webview / apply-detail` 目前仍无独立 Spec，如继续演进应补建或并入既有 Spec
- 当前信用分仍为前端 mock 计算，后续需对接真实后端积分、记录与排行榜接口
- AI 简历润色 Spec 已建，尚未落代码；后续需确认前后端接口边界与 patch 返回格式
