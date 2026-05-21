# 00-110 Legacy Inventory Matrix

> 目的：把当前后台 reference-driven 8 页主导航之外仍保留的运行态能力、fallback 依赖与候删文件统一分层，作为后续删除前的审计基线。

## A. Formal active（正式主线页）

| 对象 | 路径 | 代码入口 | 依据 | 当前判断 | 后续口径 |
|------|------|----------|------|----------|----------|
| 仪表盘 | `/dashboard/index` | `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue` | `adminSidebarMenus` 正式 8 页；router `mainline` | **Retain** | 继续作为正式主线页，不进入删代码范围 |
| 数据分析 | `/dashboard/analytics` | `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardAnalyticsView.vue` | `adminSidebarMenus` 正式 8 页；router `mainline` | **Retain** | 继续作为正式主线页，不进入删代码范围 |
| 用户管理 | `/users/index` | `D:\XM\kaipai-team\kaipai-admin\src\views\user\UserCenterView.vue` | `adminSidebarMenus` 正式 8 页；router `mainline` | **Retain** | 继续作为正式主线页，不进入删代码范围 |
| 机构管理 | `/users/orgs` | `D:\XM\kaipai-team\kaipai-admin\src\views\user\OrganizationsView.vue` | `adminSidebarMenus` 正式 8 页；router `mainline` | **Retain** | 保留，但业务边界继续限定为招募链路机构目录 |
| 分享内容 | `/content/share-cards` | `D:\XM\kaipai-team\kaipai-admin\src\views\content\ShareCardsView.vue` | `adminSidebarMenus` 正式 8 页；router `mainline` | **Retain** | 继续作为正式主线页，不进入删代码范围 |
| 风格模板 | `/content/templates` | `D:\XM\kaipai-team\kaipai-admin\src\views\content\TemplatesView.vue` | `adminSidebarMenus` 正式 8 页；router `mainline` | **Retain** | 继续作为正式主线页，不进入删代码范围 |
| 运营动作 | `/operate/actions` | `D:\XM\kaipai-team\kaipai-admin\src\views\operate\ActionsView.vue` | `adminSidebarMenus` 正式 8 页；router `mainline` | **Retain** | 继续作为正式主线页，不进入删代码范围 |
| 系统设置 | `/system/settings` | `D:\XM\kaipai-team\kaipai-admin\src\views\system\SettingsView.vue` | `adminSidebarMenus` 正式 8 页；router `mainline` | **Retain** | 继续作为正式主线页，不进入删代码范围 |

## B. Hidden tooling（隐藏治理页）

> 这些对象不在正式 8 页侧栏中，但仍在 router 或 `adminMenus` 中保留，当前不能按“废代码”处理。

| 对象 | 路径 | 代码入口 | 依据 | 当前判断 | 后续口径 |
|------|------|----------|------|----------|----------|
| 实名认证待审核 | `/verify/pending` | `D:\XM\kaipai-team\kaipai-admin\src\views\verify\PendingView.vue` | router `tooling`；`adminMenus.verify` | **Retain as hidden tooling** | 不在正式侧栏展示；若未来退场需先核销 verify 治理需求 |
| 邀请记录 | `/referral/records` | `D:\XM\kaipai-team\kaipai-admin\src\views\referral\RecordsView.vue` | router `tooling`；`adminMenus.referral` | **Retain as hidden tooling** | 邀请治理仍是后台保留域，当前不删 |
| 异常邀请 | `/referral/risk` | `D:\XM\kaipai-team\kaipai-admin\src\views\referral\RiskView.vue` | router `tooling`；`adminMenus.referral` | **Retain as hidden tooling** | 继续承接邀请治理异常复核 |
| 邀请规则 | `/referral/policies` | `D:\XM\kaipai-team\kaipai-admin\src\views\referral\PoliciesView.vue` | router `tooling`；`adminMenus.referral` | **Retain as hidden tooling** | 保留治理配置入口 |
| 邀请资格 | `/referral/eligibility` | `D:\XM\kaipai-team\kaipai-admin\src\views\referral\EligibilityView.vue` | router `tooling`；`adminMenus.referral` | **Retain as hidden tooling** | 保留资格治理入口 |
| 招募项目治理 | `/recruit/projects` | `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\ProjectsView.vue` | router `tooling`；`adminMenus.recruit` | **Retain as hidden tooling** | 当前仍是招募治理隐藏页，不删 |
| 招募角色治理 | `/recruit/roles` | `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\RolesView.vue` | router `tooling`；`adminMenus.recruit` | **Retain as hidden tooling** | 当前仍是招募治理隐藏页，不删 |
| 投递链路回看 | `/recruit/applies` | `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\AppliesView.vue` | router `tooling`；`adminMenus.recruit` | **Retain as hidden tooling** | 当前仍是招募治理隐藏页，不删 |
| 支付订单 | `/payment/orders` | `D:\XM\kaipai-team\kaipai-admin\src\views\payment\OrdersView.vue` | router `tooling`；`adminMenus.payment` | **Retain as hidden tooling** | 当前仍是后台治理页，不在正式 8 页 |
| 退款单 | `/refund/orders` | `D:\XM\kaipai-team\kaipai-admin\src\views\refund\OrdersView.vue` | router `tooling`；`adminMenus.refund` | **Retain as hidden tooling** | 当前仍是后台治理页，不在正式 8 页 |
| 联系方式申请 | `/content/contact-requests` | `D:\XM\kaipai-team\kaipai-admin\src\views\content\ContactRequestsView.vue` | router `mainline` area=`user-center` 但不在 `adminSidebarMenus` | **Retain as hidden tooling** | 已接真实后端，但仍未进入正式 8 页投影 |
| 默认普通卡治理 | `/content/default-general-card` | `D:\XM\kaipai-team\kaipai-admin\src\views\content\DefaultGeneralCardView.vue` | router `tooling`；`adminMenus.content` | **Retain as hidden tooling** | 当前仍是治理入口，不删 |
| AI 简历治理 | `/system/ai-resume-governance` | `D:\XM\kaipai-team\kaipai-admin\src\views\system\AiResumeGovernanceView.vue` | router `tooling`；`adminMenus.system` | **Retain as hidden tooling** | 当前仍是独立治理页，不删 |
| 后台账号治理 | `/system/admin-users` | `D:\XM\kaipai-team\kaipai-admin\src\views\system\AdminUsersView.vue` | router `tooling`；`adminMenus.system` | **Retain as hidden tooling** | 已从正式用户管理退场，但仍是系统治理页 |
| 角色权限治理 | `/system/roles` | `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue` | router `tooling`；`adminMenus.system` | **Retain as hidden tooling** | 当前仍是权限治理页，不删 |
| 操作留痕审计 | `/system/operation-logs` | `D:\XM\kaipai-team\kaipai-admin\src\views\system\OperationLogsView.vue` | router `tooling`；`adminMenus.system` | **Retain as hidden tooling** | 当前接口异常但页仍承担降级承接，不删 |

## C. Compat fallback（兼容 fallback 依赖）

| 对象 | 代码入口 | 证据 | 当前判断 | 删除前门禁 |
|------|----------|------|----------|------------|
| 招募页面权限 fallback | `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts` | `legacyRecruitPageFallbacks = ['page.system.admin-users']` | **Compat fallback** | 先核销 `page.recruit.*` 是否已全部 direct 授权 |
| 招募动作权限 fallback | `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts` | `legacyRecruitActionFallbacks = ['page.system.admin-users']` | **Compat fallback** | 先核销 `action.recruit.*` 是否已全部 direct 授权 |
| 权限访问模式 | `D:\XM\kaipai-team\kaipai-admin\src\utils\permission.ts` | `PermissionAccessMode = 'open' | 'direct' | 'fallback' | 'denied'` | **Compat fallback infrastructure** | 在所有 fallback 用途清零前不能删 |
| 招募项目页页面 fallback | `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\ProjectsView.vue` | `pageAccessMode === 'fallback'` + `当前页面正通过后台账号 fallback 兼容访问` | **Compat fallback consumer** | 需先确认 `page.recruit.projects` direct 授权完成 |
| 招募项目页动作 fallback | `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\ProjectsView.vue` | `actionAccessMode === 'fallback'` + `:fallback-permissions="effectiveActionFallbacks"` | **Compat fallback consumer** | 需先确认 `action.recruit.project.status` direct 授权完成 |
| 招募角色页页面 fallback | `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\RolesView.vue` | `pageAccessMode === 'fallback'` + `当前页面正通过后台账号 fallback 兼容访问` | **Compat fallback consumer** | 需先确认 `page.recruit.roles` direct 授权完成 |
| 招募角色页动作 fallback | `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\RolesView.vue` | `actionAccessMode === 'fallback'` + `:fallback-permissions="effectiveActionFallbacks"` | **Compat fallback consumer** | 需先确认 `action.recruit.role.status` direct 授权完成 |
| 招募投递页页面 fallback | `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\AppliesView.vue` | `pageAccessMode === 'fallback'` + `当前页面正通过后台账号 fallback 兼容访问` | **Compat fallback consumer** | 需先确认 `page.recruit.applies` direct 授权完成 |
| AI 治理旧日志 fallback 依赖 | `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue` | `操作日志 fallback`、`fallbackRoleCount`、`page.system.operation-logs` | **Compat fallback audit carrier** | 需先确认角色矩阵 `canRetireFallback=true` |
| 招募治理后台账号 fallback 依赖 | `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue` | `后台账号 fallback`、`pageFallbackRoleCount`、`actionFallbackRoleCount` | **Compat fallback audit carrier** | 需先确认招募矩阵页面 / 动作 fallback 全部清零 |

## D. Retire candidate（候删对象）

> 这些对象当前未发现 router / menu / import 命中，但还没有完成最终删除门禁核销，因此只能列为候删，不能直接删。

| 对象 | 文件 | 当前证据 | 当前判断 | 下一步 |
|------|------|----------|----------|--------|
| Dashboard legacy wrapper | `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardView.vue` | 当前 `rg -n "DashboardView"` 未命中源码引用；文件仅包一层 `OverviewView` | **Retire candidate** | 继续核销动态 import / 文档依赖，若无依赖可进入删除切片 |
| ReferralRisk legacy wrapper | `D:\XM\kaipai-team\kaipai-admin\src\views\referral\ReferralRiskView.vue` | 当前 `rg -n "ReferralRiskView"` 未命中源码引用；文件仅包一层 `RiskView` | **Retire candidate** | 继续核销动态 import / 文档依赖，若无依赖可进入删除切片 |
| Shared placeholder container | `D:\XM\kaipai-team\kaipai-admin\src\views\shared\PlaceholderView.vue` | 当前 `rg -n "PlaceholderView"` 未命中源码引用；router 404/403 已用其他文件 | **Verify-before-delete** | 先核销是否仍被文档、手工入口或未来补位预留依赖 |

## E. 当前删除前门禁

只有同时满足以下条件，才允许在后续实现型切片中删除：

1. 不在 `adminSidebarMenus`
2. 不在 `adminMenus`
3. 不在 `router/index.ts`
4. 无 `fallbackPermissions` 或 `PermissionAccessMode='fallback'` 依赖
5. 无源码 import / 动态 import / 文档引用
6. 不承担当前治理或降级承接职责

当前结论：

- hidden tooling：**保留，不删**
- compat fallback：**保留，待核销**
- retire candidate：**候删，但先验证**
