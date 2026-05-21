# 00-72 执行记录

## 1. 当前轮次目标

本轮按 `00-72` 先做最小但高杠杆的一轮收口，目标不是立刻删除所有旧后台页面，而是先把：

- 主导航事实源
- 顶部语义
- 工作台正式入口表达

收口到当前阶段架构：

- 控制台 / 渠道分析
- 用户中心

## 2. 已核实事实

### 2.1 现有 Spec 边界

- `00-71` 已承接 `D:\XM\kaipai-team\_-_1.html` 的控制台视觉基线、壳层、工作台和登录页语言
- `00-69` 已把后台当前阶段主架构定义为“控制台 / 用户中心”
- 因此本轮问题已不是“是否缺 UI Spec”，而是“后台信息架构与现有路由库存不一致”

### 2.2 当前代码差距

- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
  - `adminMenus` 仍保留旧多业务域库存
  - `adminSidebarMenus` 已部分收口到两类导航，但之前未被主导航真正消费
- `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts`
  - 之前 `sidebarMenus` 直接等于全量 `menus`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminSidebar.vue`
  - 之前仍按 `OVERVIEW / CORE / OPERATION` 三组旧域键值拼装主导航
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminTopbar.vue`
  - 之前顶部眉标仍按 `BUSINESS / TRADE / CONTENT / OPERATION` 旧多业务域表达
- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue`
  - 之前“已有功能入口”和若干数据板块仍把实名 / 邀请 / 退款 / 支付当作默认正式入口暴露

## 3. 本轮已落地修改

### 3.1 新增信息架构常量

新增：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\admin-information-architecture.ts`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\route-audit-matrix.md`

作用：

- 统一定义当前阶段后台路径语义：
  - `dashboard-analytics`
  - `user-center`
  - `tooling`
- 为顶部语义、按钮文案和后续 dashboard/tooling 判断提供单一事实源
- 为 T4 提供首轮路由审计矩阵，显式列出：
  - 主架构保留页
  - 兼容治理页
  - 删除候选页

### 3.2 主导航事实源收口

已修改：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminSidebar.vue`

结果：

- `sidebarMenus` 不再直接等于全量 `adminMenus`
- `adminMenus` 与 `adminSidebarMenus` 的职责已在代码中显式区分为“能力库存”和“当前阶段主导航投影”
- 左侧主导航现已真正消费 `adminSidebarMenus`
- 主导航当前只保留：
  - `控制台 / 渠道分析`
  - `用户中心`
- 旧业务域不再作为登录后左侧主导航正式入口出现

### 3.3 顶部语义收口

已修改：

- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminTopbar.vue`

结果：

- 顶部眉标改为当前阶段三类语义：
  - `DASHBOARD / 控制台 · 渠道分析`
  - `USER CENTER / 用户中心`
  - `TOOLING / 兼容治理`
- 非主架构页面会被明确表达为兼容治理工具，不再伪装成当前正式业务域

### 3.4 工作台入口与文案收口

已修改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\auth\LoginView.vue`

结果：

- 工作台头部改为“当前阶段控制台 / 渠道分析”
- 筛选区只保留时间窗口，移除旧多业务域筛选 UI
- 工作台核心 KPI 与趋势板块改为围绕：
  - 分享访问
  - 唯一访客
  - 活跃分享卡
  - 持卡用户
  - 查看后成卡
  - 联系方式待处理 / 已同意
- “当前主架构入口”只保留：
  - `/dashboard/index`
  - `/content/share-cards`
  - `/content/contact-requests`
- 原先依然直接暴露旧治理域入口的模块卡已被移除
- `recentItems` 区块改名为“兼容治理动态”，旧路由跳转按钮文案会显式显示为“进入治理工具”
- 登录后路由 meta 已补首轮分类：
  - `dashboard / share-cards / contact-requests` 标记为 `mainline`
  - 其余当前保留页标记为 `tooling`
- 登录成功与无权限回退现在都优先走 `permissionStore.landingPath`，不再把所有账号强行打回 `/dashboard/index`
- `membership/*` 路由在退场前已标记过 `retire-candidate`，当前已从运行时移除

### 3.5 历史守卫漂移清理

已删除：

- `D:\XM\kaipai-team\kaipai-admin\src\router\guard.ts`

结果：

- 删除了一份当前 `main.ts` 并未安装使用的旧路由守卫实现
- 避免后续继续同时维护两套路由守卫逻辑，减少“当前真实守卫在哪里”的认知漂移

### 3.6 删除候选边界落盘

已新增：

- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\route-audit-matrix.md`

结果：

- 已按当前仓库快照把登录后路由分成：
  - 主架构保留页
  - 兼容治理页
  - 删除候选页
- 已明确：
  - `recruit/*`
  - `membership/*`
  的依赖边界，并据此推进候删域核销
- 但这些页面仍保留 direct route，不在本轮贸然物理删除

### 3.7 membership 域已退场

已修改 / 删除：

- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\admin-information-architecture.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\permission-registry.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\status.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\api\membership.ts`（删除）
- `D:\XM\kaipai-team\kaipai-admin\src\types\membership.ts`（删除）
- `D:\XM\kaipai-team\kaipai-admin\src\views\membership\ProductsView.vue`（删除）
- `D:\XM\kaipai-team\kaipai-admin\src\views\membership\AccountsView.vue`（删除）
- `D:\XM\kaipai-team\kaipai-admin\README.md`

结果：

- `membership/*` 已从当前后台运行时路由中移除
- `adminMenus` 中的会员中心菜单库存已删除
- membership 专属页面、API、类型与仅其使用的状态常量已删除
- 权限注册表仍保留 legacy membership 标签，用于已存在旧权限码的只读展示，不再继续作为可见业务域存在

### 3.8 无权限回退兜底修正

已修改：

- `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\auth\LoginView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\common\ForbiddenView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`

结果：

- `landingPath` 在无可用页面时不再伪造 `/dashboard/index`
- 登录成功后若没有可用页面，会进入 `/403`
- 已新增 `/403` 路由，避免删除候删域后出现登录或无权限死循环
- 403 页会优先返回当前账号可用页面；若无任何可用页面，则退出并回到登录页

### 3.9 companion/tooling 页候删分层推进

已修改：

- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\route-audit-matrix.md`

结果：

- 以下三页已从 `tooling` 调整为 `retire-candidate`：
  - `/verify/history`
  - `/payment/transactions`
  - `/refund/logs`
- 提升到候删层级的依据是：
  - `verify/history` 只是 `VerificationBoard` 的 `history` 包装页
  - `payment/transactions` 的核心流水回看已能在订单详情完成
  - `refund/logs` 的核心日志回看已能在退款详情完成
- 其中 `verify/history`、`payment/transactions`、`refund/logs` 现都已完成物理退场

### 3.10 `verify/history` 已退场

已修改 / 删除：

- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\verify\HistoryView.vue`（删除）
- `D:\XM\kaipai-team\kaipai-admin\src\views\verify\VerifyListView.vue`（删除）
- `D:\XM\kaipai-team\kaipai-admin\src\views\verify\VerificationBoard.vue`

结果：

- `/verify/history` 已从当前后台前端运行时移除
- 认证治理只保留 `/verify/pending` 作为正式 tooling 入口
- `VerificationBoard.vue` 已补动态语义：
  - 默认 `status = 1` 时表达“待审核队列”
  - 当用户切换状态或清空状态时，在同一页表达“审核记录回看”
- 因此历史回看能力没有丢，只是从独立路由回收到同一治理页

### 3.11 `payment/transactions` 与 `refund/logs` 已退场

已修改 / 删除：

- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\api\payment.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\api\refund.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\types\payment.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\types\refund.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\payment\TransactionsView.vue`（删除）
- `D:\XM\kaipai-team\kaipai-admin\src\views\refund\LogsView.vue`（删除）
- `D:\XM\kaipai-team\kaipai-admin\README.md`

结果：

- `/payment/transactions` 与 `/refund/logs` 已从当前后台前端运行时移除
- 支付治理当前只保留 `/payment/orders`
- 退款治理当前只保留 `/refund/orders`
- 支付订单详情仍可回看关联流水
- 退款详情仍可回看操作日志
- 这两页的独立筛查能力已退出当前后台运行时

### 3.12 `content/templates` 与 `content/default-general-card` 保留边界已收口

已修改：

- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\requirements.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\route-audit-matrix.md`
- `D:\XM\kaipai-team\.sce\specs\README.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`

结果：

- `content/templates` 已明确收口为长期 tooling retain，而不是“待下一轮确认”
- `content/default-general-card` 已明确收口为长期 tooling retain，而不是默认候删页
- 当前保留依据已落盘：
  - `AdminContentController.java` 仍暴露模板治理、默认普通卡策略摘要、单用户状态与补偿接口
  - `CardSceneTemplateServiceImpl.java` 仍把 `requiredInviteCount`、`baseThemeJson`、`artifactPresetJson` 合并进当前分享卡 runtime
  - `UserShareCardServiceImpl.java` 创建分享卡时仍受模板邀请门槛 gating
  - `TemplatesView.vue` 与 `DefaultGeneralCardView.vue` 仍直接承接这些治理动作
- 因此这两页继续保留 direct route + permission guard，但不进入主导航
- `00-72` 的验收项与任务状态已同步回填，避免 spec 继续停留在“仍待下一轮确认”的过时状态

### 3.13 `system/*` 与 `recruit/*` 的 tooling 边界已收口

已修改：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\admin-information-architecture.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\route-audit-matrix.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\execution.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`

结果：

- `system/admin-users`
- `system/roles`
- `system/operation-logs`
- `system/ai-resume-governance`

已明确收口为 **长期 tooling retain**，不再被笼统写成“兼容保留页”。

- `recruit/projects`
- `recruit/roles`
- `recruit/applies`

已明确收口为 **兼容过渡 tooling**，原因不是“页面还在”，而是：

- 前端页面仍在直接执行项目 / 角色状态校准或投递链路回看
- 后端 `AdminRecruitController.java` / `AdminRecruitGovernanceServiceImpl.java` 仍提供真实列表与处置接口
- `system/RolesView.vue` / `AdminRoleServiceImpl.java` 仍显式追踪招募授权矩阵和 `page.system.admin-users` fallback 退场条件

同时，为避免顶部继续把长期治理工具误写成“兼容治理页”：

- tooling 顶部眉标已从 `TOOLING / 兼容治理` 收口为 `TOOLING / 治理工具`
- `system/*`、`recruit/*`、`content/templates`、`content/default-general-card` 的路由标题与顶部说明已改成更明确的治理语义

### 3.14 `recruit/*` 的 fallback 可见化已补齐

已修改：

- `D:\XM\kaipai-team\kaipai-admin\src\utils\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\ProjectsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\RolesView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\AppliesView.vue`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\route-audit-matrix.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`

结果：

- 权限层已新增 `getPermissionAccessMode()` / `permissionStore.getAccessMode()`，可以区分：
  - `direct`
  - `fallback`
  - `denied`
- `recruit/projects`
- `recruit/roles`
- `recruit/applies`

现在会在页面内显式提示当前是否仍通过 `page.system.admin-users` fallback 兼容访问。

其中：

- `ProjectsView.vue` 会额外区分“页面 fallback”与“状态处置动作 fallback”
- `RolesView.vue` 会额外区分“页面 fallback”与“状态处置动作 fallback”
- `AppliesView.vue` 会提示页面级 fallback 访问

这一步不改变现有授权结果，只把“当前仍在兼容过渡”从隐式状态改为显式提示，便于后续继续推进 fallback 退场。

### 3.15 招募矩阵的 `menu.recruit` 口径已按 runtime 修正

已修改：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\system\service\impl\AdminRoleServiceImpl.java`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\route-audit-matrix.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`

结果：

- 已核实 `adminMenus` 的 `recruit` 顶级分组当前没有 `menuPermission`，因此 `menu.recruit` 并不参与现有 runtime 菜单 gating
- 后端 `AdminRoleServiceImpl.java` 的招募矩阵现在改为：
  - `recruitReady` 只按 `page.recruit.*` + `action.recruit.*` 判断
  - `missingPermissions` 不再把 `menu.recruit` 列为 runtime 缺口
  - `partial_recruit / compat_transition` 也只按真实页面 / 动作权限计算
- 前端 `RolesView.vue` 同步改为：
  - 招募权限包不再强制附带 `menu.recruit`
  - 招募矩阵把 `menu.recruit` 降级为“历史登记”标签
  - 招募矩阵 summary / alert 改为显式区分“页面 fallback”与“动作 fallback”
  - 角色编辑提示改成按 `page.recruit.*` / `action.recruit.*` 表达 ready 口径

这一步修掉的是“矩阵口径和当前运行时不一致”的事实漂移，而不是单纯的文案优化。

### 3.16 招募矩阵已升级为后端直接产出 page/action fallback 事实源

已修改：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\model\system\dto\AdminRoleRecruitGovernanceMatrixItemDTO.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\model\system\dto\AdminRoleRecruitGovernanceMatrixRespDTO.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\system\service\impl\AdminRoleServiceImpl.java`
- `D:\XM\kaipai-team\kaipai-admin\src\types\system.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\route-audit-matrix.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`

结果：

- 后端招募矩阵 item 已新增：
  - `pageReady`
  - `actionReady`
  - `pageReliesOnFallback`
  - `actionReliesOnFallback`
- 后端招募矩阵 summary 已新增：
  - `pageReadyRoleCount`
  - `actionReadyRoleCount`
  - `pageFallbackRoleCount`
  - `actionFallbackRoleCount`
- 前端 `RolesView.vue` 已优先消费这组后端字段，不再把前端按行推导作为唯一事实源
- 招募矩阵 summary 现可直接展示：
  - 页面 ready 数
  - 动作 ready 数
  - 页面 fallback 数
  - 动作 fallback 数

这一步的意义不是新增功能，而是把“下一步该先退页面 fallback 还是先退动作 fallback”的判断基础，收口到后端事实源。

### 3.17 招募矩阵已补双 gating 信号

已修改：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\model\system\dto\AdminRoleRecruitGovernanceMatrixRespDTO.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\system\service\impl\AdminRoleServiceImpl.java`
- `D:\XM\kaipai-team\kaipai-admin\src\types\system.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\route-audit-matrix.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`

结果：

- 后端招募矩阵 summary 已新增：
  - `canRetirePageFallback`
  - `canRetireActionFallback`
- `RolesView.vue` 现在会直接基于这两个后端布尔量展示：
  - `页面/动作均可退`
  - `可先退页面 Fallback`
  - `可先退动作 Fallback`
  - `仍需兼容过渡`
- 招募矩阵 alert 也已改为优先说明：
  - 是否已经可以先退页面 fallback
  - 是否已经可以先退动作 fallback

这一步的意义是：在已有 page/action fallback 计数之上，再补一层明确的退场判断信号，减少前端继续解释计数的空间。

### 3.18 招募动作 fallback 已进入第一层真实退场

已修改：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\common\auth\RecruitGovernanceFallbackGate.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\recruit\AdminRecruitController.java`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\ProjectsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\RolesView.vue`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\route-audit-matrix.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`

结果：

- 后端已新增 `RecruitGovernanceFallbackGate.java`
- `AdminRecruitController.java` 的两个状态处置接口已改为：
  - 总是允许独立 `action.recruit.*`
  - 只有在 `allowLegacyActionFallback()` 返回 true 时，才继续接受 `page.system.admin-users` 动作兜底
- 前端 `ProjectsView.vue` / `RolesView.vue` 已同步拉取招募矩阵 summary：
  - 当 `canRetireActionFallback = true` 时，不再给状态按钮附带 fallback permissions
  - 当 `canRetireActionFallback = false` 时，继续保留动作 fallback
- 页面 fallback 仍保留，没有在本轮一并退场

这一步不是“只改提示”，而是招募 fallback 收缩的第一层真实落地：**动作 fallback 已开始按矩阵信号动态关闭**。

### 3.19 招募 gating 信号已下沉到后台会话

已修改：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\model\adminauth\dto\AdminSessionInfoDTO.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\adminauth\service\impl\AdminAuthServiceImpl.java`
- `D:\XM\kaipai-team\kaipai-admin\src\types\admin.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\ProjectsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\RolesView.vue`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\route-audit-matrix.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`

结果：

- `/admin/auth/login` 与 `/admin/auth/me` 返回的后台会话已新增：
  - `allowLegacyRecruitPageFallback`
  - `allowLegacyRecruitActionFallback`
- `AuthServiceImpl.java` 现在会在生成会话时同步下发这两个全局 gating 信号
- `permissionStore` 已新增动态 fallback 解析：
  - 当 `allowLegacyRecruitPageFallback = false` 时，`page.recruit.*` 的 fallback 在菜单 / 路由守卫 / landing path 中会自动失效
  - 当 `allowLegacyRecruitActionFallback = false` 时，`action.recruit.*` 的 fallback 在前端按钮权限判断中会自动失效
- `ProjectsView.vue` / `RolesView.vue` 已不再依赖 `recruit-governance-matrix` 接口来决定按钮 fallback，而是直接读取会话级 gating 信号

这一步解决的是一个关键边界：`recruit-governance-matrix` 本身受 `page.system.roles` 保护，不能作为所有 admin 的统一前端 gating 事实源；因此真正的前端动态收口，必须落到会话信息。

### 3.20 招募页面 fallback 已进入第一层真实退场

已修改：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\common\auth\RecruitGovernanceFallbackGate.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\recruit\AdminRecruitController.java`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-72-current-phase-admin-information-architecture-alignment\route-audit-matrix.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`

结果：

- `RecruitGovernanceFallbackGate.java` 已补 `allowLegacyPageFallback()`
- `AdminRecruitController.java` 的三个列表接口已改为：
  - 总是允许独立 `page.recruit.*`
  - 只有在 `allowLegacyPageFallback()` 返回 true 时，才继续接受 `page.system.admin-users` 页面兜底
- 因此当前 page fallback 已和 session gating / 前端菜单过滤 / 路由守卫 / landing path 对齐，不再只有前端单边预演

这一步不是删除招募页面，而是 **页面 fallback 的第一层真实退场**：后端 GET 接口也开始按同一 gating 信号动态关闭 `page.system.admin-users` 页面兜底。

## 4. 本轮未做的事

- 还没有物理删除 `verify / referral / recruit / payment / refund / system` 等旧页面
- 还没有给所有候删页面补齐更细粒度的“页面级删除前置条件”说明
- 还没有继续把 `recruit/*` 从 fallback 兼容过渡推进到可删除结论，因此相关旧域仍未进入物理删除阶段

因此本轮结论应限定为：

- **主导航与主界面语义已收口**
- **旧业务域已从“正式主入口”降级为兼容治理语境**
- **但旧页面仍保留在路由库存中，尚未进入大规模删除阶段**

## 5. 验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`
- `cd D:\XM\kaipai-team\kaipaile-server && mvn -DskipTests compile`

结果：

- `type-check`：通过
- `build`：通过
- `mvn -DskipTests compile`：通过

补充说明：

- 构建仍有既有 Vite chunk 体积 warning
- 构建仍有 Sass legacy JS API deprecation warning
- 这两项都不是本轮后台信息架构收口引入的新错误

## 6. 当前不确定边界

### 6.1 用户中心能力边界

当前把 `用户中心` 收口到：

- `content/share-cards`
- `content/contact-requests`

**依据**：这是仓库里当前最接近“用户与分享相关真实治理能力”的已存在页面。
**置信度**：中高。
**不确定边界**：如果后续出现真实的“平台用户列表 / 用户详情”页面能力，用户中心还需要再扩展，不应把当前定义当成永久终态。

### 6.2 旧业务域删除顺序

**依据**：当前已完成首轮路由分层与已知候删页核销，但并没有把剩余 tooling 域全部推进到“可删除”结论。
**置信度**：高。
**不确定边界**：后续若要继续缩减后台库存，重点将落在 `recruit/*` 的 fallback 退场，而不是已经核实应长期保留的 `system/*`、`content/templates` / `content/default-general-card`。

### 6.3 删除候选域的最终去留

`membership/*` 已在当前轮完成物理退场。

**依据**：当前仓库快照里，没有发现 `membership/*` 继续被主导航、dashboard 快捷入口、recentItems 或治理导航引用；同时其代码依赖已核销完成。
**置信度**：高。
**不确定边界**：后端接口与旧权限码仍可能在历史数据中存在，因此当前仅退掉前端运行时入口，不等同于后端域已彻底清零。

### 6.4 `recruit/*` 的边界修正

本轮继续核查后，`recruit/*` 不再维持“删除候选”判断，而是回退为 **兼容过渡 tooling**。

**依据**：

- `system/RolesView.vue` 当前仍显式维护“招募治理授权矩阵”
- 招募治理权限包仍直接引用：
  - `page.recruit.projects`
  - `page.recruit.roles`
  - `page.recruit.applies`
  - `action.recruit.project.status`
  - `action.recruit.role.status`
- `fetchAdminRoleRecruitGovernanceMatrix()` 仍从后端读取招募治理矩阵

**置信度**：高。
**不确定边界**：只有在角色治理矩阵与对应权限包不再依赖招募页面时，`recruit/*` 才适合再进入删除候选池。

### 6.5 companion/tooling 页的最终去留

当前已进入删除候选池且完成物理退场的 companion 页：

- `verify/history`
- `payment/transactions`
- `refund/logs`

**依据**：

- 它们都不再是主导航或 dashboard 正式入口
- 且主链详情页已具备对应的核心回看能力
- 当前运行时保留这些独立入口只会放大旧多业务域噪音

**置信度**：高。
**不确定边界**：如果后续运营明确要求恢复独立筛查入口，需要重新立项，不再默认保留旧页。

### 6.6 `content/templates` 与 `content/default-general-card` 的保留边界

当前已明确：

- `content/templates`：长期 tooling retain
- `content/default-general-card`：长期 tooling retain

**依据**：

- `AdminContentController.java` 当前仍暴露模板治理、默认普通卡策略摘要、用户检查与补偿接口
- `CardSceneTemplateServiceImpl.java` 当前仍把 `requiredInviteCount`、`baseThemeJson`、`artifactPresetJson` 合并进分享卡模板 runtime
- `UserShareCardServiceImpl.java` 当前仍按模板邀请门槛控制分享卡创建
- 前端 `TemplatesView.vue` 与 `DefaultGeneralCardView.vue` 仍直接承接这些治理动作

**置信度**：高。
**不确定边界**：只有在模板 runtime 不再依赖后台手工治理，且默认普通卡初始化/补偿不再需要单独治理页时，这两页才适合重新进入删除候选。

### 6.7 `system/*` 的保留边界

当前已明确：

- `system/admin-users`：长期 tooling retain
- `system/roles`：长期 tooling retain
- `system/operation-logs`：长期 tooling retain
- `system/ai-resume-governance`：长期 tooling retain

**依据**：

- `AdminUsersView.vue` + `AdminSystemController.java` 仍承接后台账号 CRUD、启停用、密码重置与角色绑定
- `RolesView.vue` + `AdminRoleServiceImpl.java` 仍承接角色 CRUD、权限树、AI / 招募授权矩阵与 fallback 退场判断
- `OperationLogsView.vue` 仍承接操作留痕回看，且 `AiResumeGovernanceView.vue` 还直接消费日志接口作为治理动作日志源
- `AiResumeGovernanceView.vue` + `AdminAiResumeController.java` 仍承接 AI 失败样本、敏感命中、协同与处置动作

**置信度**：高。
**不确定边界**：除非未来后台账号、角色、操作日志或 AI 治理被整体迁到新的独立治理入口，否则这几页不适合进入默认候删队列。

### 6.8 `recruit/*` 的保留边界

当前已明确：

- `recruit/*`：兼容过渡 tooling

**依据**：

- `ProjectsView.vue` 与 `RolesView.vue` 仍直接执行状态校准动作
- `AppliesView.vue` 仍承担 `apply -> role -> project -> company` 链路回看
- `AdminRecruitController.java` / `AdminRecruitGovernanceServiceImpl.java` 仍提供真实列表与状态处置接口
- 但其页面权限与动作仍保留 `page.system.admin-users` fallback，且 `RolesView.vue` / `AdminRoleServiceImpl.java` 仍显式跟踪 fallback 退场条件

**置信度**：高。
**不确定边界**：只有在招募治理矩阵不再依赖 `system/admin-users` fallback，且真实后台运营确认无需保留这些治理页时，`recruit/*` 才适合重新进入删除候选。

## 7. 后续建议顺序

1. `00-72` 当前主目标已收口；若继续压缩后台库存，下一轮优先推进 `recruit/*` 的 fallback 退场审计，而不是再重复盘点 `system/*`
2. 继续保持 `system/*`、`content/templates` 与 `content/default-general-card` 为 tooling，不再把它们放入默认候删队列
3. 若未来出现真实的平台用户列表 / 用户详情主链，再另起 Spec 扩展“用户中心”，而不是把现有治理页挪成主导航
