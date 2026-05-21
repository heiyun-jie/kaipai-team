# 00-72 路由审计矩阵

> 目的：为 `00-72 / T4` 提供当前登录后路由的首轮分类、入口依赖和去留建议。
> 审计口径：只基于 **当前仓库快照** 能直接核实到的事实；凡无法从当前代码直接证明“仍有强运营依赖”的页面，一律标记为“待运营确认”或“删除候选”，不把猜测写成既定事实。

## 1. 审计结论摘要

### 1.1 当前主架构保留页

- `/dashboard/index`
- `/content/share-cards`
- `/content/contact-requests`

### 1.2 明确保留为 tooling 页

- `/verify/pending`
- `/referral/records`
- `/referral/risk`
- `/referral/eligibility`
- `/referral/policies`
- `/payment/orders`
- `/refund/orders`
- `/content/templates`
- `/content/default-general-card`
- `/system/admin-users`
- `/system/roles`
- `/system/operation-logs`
- `/system/ai-resume-governance`

### 1.3 删除候选（保留 direct route，待运营确认后再删）

当前轮已无仍保留 direct route 的删除候选域。

### 1.4 已退场域

- `/verify/history`
- `/payment/transactions`
- `/refund/logs`
- `/membership/products`
- `/membership/accounts`

## 2. 路由级矩阵

| 路由 | 当前层级 | 当前代码可核实入口依赖 | 权限 / 直达情况 | 当前建议 |
|------|----------|------------------------|-----------------|----------|
| `/dashboard/index` | mainline | 左侧主导航、登录后 landing path、工作台自身 | `page.dashboard.index`；可直达 | 主架构保留 |
| `/content/share-cards` | mainline | 左侧主导航、dashboard KPI / 模块入口 | `page.content.share-cards`；可直达 | 主架构保留 |
| `/content/contact-requests` | mainline | 左侧主导航、dashboard KPI / 模块入口 | `page.content.contact-requests`；可直达 | 主架构保留 |
| `/verify/pending` | tooling | dashboard `recentItems` 跳转、`dashboard-context.ts` carry 规则 | `page.verify.pending`；可直达 | 兼容治理保留 |
| `/referral/risk` | tooling | dashboard `recentItems` 跳转、`dashboard-context.ts`、`ReferralGovernanceNav.vue` | `page.referral.risk`；可直达 | 兼容治理保留 |
| `/referral/records` | tooling | `dashboard-context.ts`、`ReferralGovernanceNav.vue` | `page.referral.records`；可直达 | 兼容治理保留 |
| `/referral/eligibility` | tooling | `dashboard-context.ts`、`ReferralGovernanceNav.vue` | `page.referral.eligibility`；可直达 | 兼容治理保留 |
| `/referral/policies` | tooling | `dashboard-context.ts`、`ReferralGovernanceNav.vue` | `page.referral.policies`；可直达 | 兼容治理保留 |
| `/payment/orders` | tooling | dashboard `recentItems` 跳转、`dashboard-context.ts` carry 规则 | `page.payment.orders`；可直达 | 兼容治理保留 |
| `/refund/orders` | tooling | dashboard `recentItems` 跳转、`dashboard-context.ts` carry 规则 | `page.refund.orders`；可直达 | 兼容治理保留 |
| `/content/templates` | tooling | `AdminContentController` / `CardSceneTemplateServiceImpl` 仍承接模板治理，且 `sceneKey / requiredInviteCount / baseThemeJson / artifactPresetJson` 直接影响当前分享卡 runtime | `page.content.templates`；可直达 | 长期 tooling 保留 |
| `/content/default-general-card` | tooling | `AdminContentController` 仍提供默认普通卡策略、用户检查与补偿接口，且与当前 `config/card` 绑定一致性治理直接相关 | `page.content.default-general-card`；可直达 | 长期 tooling 保留 |
| `/system/admin-users` | tooling | `AdminUsersView.vue` 仍承接账号创建、启停用、重置密码、绑定角色；且 `recruit/*` 仍依赖其 fallback permission | `page.system.admin-users`；可直达 | 长期 tooling 保留 |
| `/system/roles` | tooling | `RolesView.vue` 仍承接角色 CRUD、权限树、AI / 招募授权矩阵与 fallback 退场判断 | `page.system.roles`；可直达 | 长期 tooling 保留 |
| `/system/operation-logs` | tooling | `OperationLogsView.vue` 提供审计留痕回看；`AiResumeGovernanceView.vue` 还会直接拉取同一日志接口作为治理动作日志 | `page.system.operation-logs`；可直达 | 长期 tooling 保留 |
| `/system/ai-resume-governance` | tooling | `AdminAiResumeController` 与 `AiResumeGovernanceView.vue` 仍提供失败样本、敏感命中、协同与处置动作 | `page.system.ai-resume-governance`；可直达 | 长期 tooling 保留 |
| `/recruit/projects` | tooling | `AdminRecruitController` 仍提供项目列表与状态校准；页面 fallback 已改为按会话信号与后端 GET 接口动态关停，状态处置 fallback 也已按矩阵信号动态关停 | `page.recruit.projects` + session-gated page fallback；可直达 | 兼容过渡 tooling |
| `/recruit/roles` | tooling | `AdminRecruitController` 仍提供角色列表与状态校准；页面 fallback 已改为按会话信号与后端 GET 接口动态关停，状态处置 fallback 也已按矩阵信号动态关停 | `page.recruit.roles` + session-gated page fallback；可直达 | 兼容过渡 tooling |
| `/recruit/applies` | tooling | `AdminRecruitController` 仍提供投递链路列表；页面 fallback 已改为按会话信号与后端 GET 接口动态关停 | `page.recruit.applies` + session-gated page fallback；可直达 | 兼容过渡 tooling |

## 3. 关键依据

### 3.1 主架构入口来源

- 左侧主导航当前只消费 `adminSidebarMenus`
- `adminSidebarMenus` 当前仅含：
  - `/dashboard/index`
  - `/content/share-cards`
  - `/content/contact-requests`

对应文件：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminSidebar.vue`

### 3.2 tooling 页的现有强依赖

- `verify / referral / payment / refund` 仍被 dashboard `recentItems` 与 `dashboard-context.ts` 使用
- `referral/*` 之间还存在 `ReferralGovernanceNav.vue` 的页内切换关系
- `system/admin-users` 仍被 `recruit/*` 的 `pagePermissionFallbacks` 依赖
- `content/templates` 仍直接治理当前分享卡模板 runtime；`content/default-general-card` 仍直接治理默认普通卡策略、单用户检查与补偿
- `system/roles` 仍直接维护 AI / 招募授权矩阵；`system/operation-logs` 仍被 AI 治理页作为动作日志源使用
- `recruit/*` 仍有真实后端列表 / 状态校准接口，不是纯前端残留

对应文件：

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\utils\dashboard-context.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\components\business\ReferralGovernanceNav.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\content\TemplatesView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\content\DefaultGeneralCardView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\AdminUsersView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\OperationLogsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\AiResumeGovernanceView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\ProjectsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\RolesView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\AppliesView.vue`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\content\AdminContentController.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\system\AdminSystemController.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\recruit\AdminRecruitController.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\ai\AdminAiResumeController.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\card\service\impl\CardSceneTemplateServiceImpl.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\card\service\impl\UserShareCardServiceImpl.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\system\service\impl\AdminRoleServiceImpl.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\recruit\service\impl\AdminRecruitGovernanceServiceImpl.java`

### 3.3 删除候选的当前依据

当前代码里没有找到 `membership/*` 继续被主导航、dashboard 快捷入口、dashboard recentItems、dashboard context 或跨页治理导航直接引用，因此它进入了 **删除候选池** 并已在当前轮物理退场。

但 `recruit/*` 不能按同一口径处理。当前仓库快照里仍有以下强依赖：

- `system/RolesView.vue` 明确展示“招募治理授权矩阵”
- `recruit-governance-read / operate` 权限包显式引用三张招募页面权限和两类招募动作
- `fetchAdminRoleRecruitGovernanceMatrix()` 仍从后端读取招募治理授权矩阵

因此当前阶段：

- `membership/*`：已退场
- `recruit/*`：兼容过渡 tooling

## 4. 当前边界说明

### 4.1 `verify/history`

- 已在当前轮物理退场
- 依据是它只是 `VerificationBoard` 的 `history` 模式包装页，与待审页复用同一组件和同一查询接口
- 当前待审页已支持通过状态筛选切换到历史回看语义，因此单独路由入口不再必要

### 4.2 `payment/transactions` 与 `refund/logs`

- 已在当前轮物理退场
- 依据是：
  - `payment/OrdersView.vue` 的订单详情已能回看关联流水
  - `refund/OrdersView.vue` 的退款详情已能回看操作日志
- 当前建议：继续观察是否还存在恢复独立入口的运营需求；若没有，就保持退场状态

### 4.3 `content/templates` 与 `content/default-general-card`

- 当前不是主架构入口，但已核实应继续长期保留为 tooling
- 依据：
  - `TemplatesView.vue` 当前仍直接维护模板 `sceneKey`、`requiredInviteCount`、`membershipRequired`、`baseThemeJson`、`artifactPresetJson`
  - `CardSceneTemplateServiceImpl.java` 仍将 `requiredInviteCount`、`baseThemeJson`、`artifactPresetJson` 合并进当前分享卡模板 runtime
  - `UserShareCardServiceImpl.java` 创建分享卡时仍按模板 `requiredInviteCount` 执行邀请门槛 gating
  - `DefaultGeneralCardView.vue` 仍执行默认普通卡策略摘要、单用户状态检查与手工补偿
  - `AdminContentController.java` 当前仍暴露默认普通卡策略、用户检查与补偿接口
- 当前建议：作为长期 tooling 保留，不纳入主导航，也不进入删除候选

### 4.4 `recruit/*`

- 虽然当前不在主导航，也没有 dashboard 快捷入口
- 但其权限、矩阵和角色治理说明仍在 `system/RolesView.vue` 中活跃使用
- 同时 `AdminRecruitController.java` 与 `AdminRecruitGovernanceServiceImpl.java` 仍提供项目 / 角色 / 投递列表与状态校准
- 当前仓库快照里，`adminMenus` 的 `recruit` 顶级分组未设置 `menuPermission`，因此 `menu.recruit` 不参与现有 runtime 菜单 gating
- 当前前端页内已补 fallback 可见化提示；当页面或动作仍通过 `page.system.admin-users` 访问时，会显式提醒当前仍处于兼容过渡
- 当前角色矩阵、权限包与提示文案已按上述事实修正为：以 `page.recruit.*` / `action.recruit.*` 作为 ready 口径，`menu.recruit` 仅保留为历史登记信息
- 当前招募矩阵 DTO 已进一步拆出 `pageReady / actionReady / pageReliesOnFallback / actionReliesOnFallback` 及对应聚合计数，后续应优先基于这组后端字段推进 fallback 退场
- 当前招募矩阵 summary 已补 `canRetirePageFallback / canRetireActionFallback`，可直接支撑“先退页面 fallback 还是先退动作 fallback”的下一轮判断
- 当前动作 fallback 已进入第一层真实落地：后端状态处置接口与前端状态按钮都已改为按 `canRetireActionFallback` 动态关闭 `page.system.admin-users` 动作兜底
- 当前 page/action fallback 开关已下沉到 `/admin/auth/me`：
  - `allowLegacyRecruitPageFallback`
  - `allowLegacyRecruitActionFallback`
  因此前端菜单、路由守卫、landing path 与招募页动作都能在无 `page.system.roles` 的情况下共享同一 gating 信号
- 当前页面 fallback 也已进入第一层真实落地：
  - `AdminRecruitController.java` 的 `GET /admin/recruit/*` 已改为按 `allowLegacyPageFallback()` 动态决定是否继续接受 `page.system.admin-users`
  - 前端 `permissionStore` 也会在 `allowLegacyRecruitPageFallback = false` 时同步让 `page.recruit.*` 的 fallback 失效
- 当前建议：保留为 **兼容过渡 tooling**，等角色治理矩阵与 `system/admin-users` fallback 都退出后再评估是否进入删除候选

### 4.5 `system/*`

- 当前不是主架构入口，但已核实不应再被表述为“纯兼容页”
- 依据：
  - `AdminUsersView.vue` + `AdminSystemController.java` 仍承接后台账号 CRUD、启停用、密码重置与角色绑定
  - `RolesView.vue` + `AdminRoleServiceImpl.java` 仍承接角色 CRUD、权限树、AI / 招募授权矩阵与 fallback 退场判断
  - `OperationLogsView.vue` + `AdminSystemController.java` 仍承接操作留痕、快照与请求链路回看
  - `AiResumeGovernanceView.vue` + `AdminAiResumeController.java` 仍承接 AI 失败样本、敏感命中、协同与处置动作
  - `AiResumeGovernanceView.vue` 当前还直接拉取 `fetchAdminOperationLogs()` 作为治理动作日志源
- 当前建议：作为 **长期 tooling 保留**，不纳入主导航，也不进入默认候删队列
