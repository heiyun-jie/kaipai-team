# 00-110 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`README.md`、`spec-code-mapping.md` 与 `00-109`
- 已确认当前用户问题已从“单页 UI 精修”切到“旧代码是否删完 / 新页面是否连后端”的架构审计问题
- 已把本轮范围收窄为 spec-only 审计建档，不直接删除任何代码

## 2. 已核实证据

### 2.1 正式导航与隐藏能力库存分离

文件：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`

已确认：

- `adminMenus` 仍是 full capability inventory
- `adminSidebarMenus` 才是 reference-driven 的正式 8 页投影

### 2.2 仍保留的隐藏治理路由

文件：

- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`

当前已确认仍保留的隐藏治理 / 兼容路由包括：

- `/verify/pending`
- `/referral/records`
- `/referral/risk`
- `/referral/policies`
- `/referral/eligibility`
- `/recruit/projects`
- `/recruit/roles`
- `/recruit/applies`
- `/payment/orders`
- `/refund/orders`
- `/content/contact-requests`
- `/content/default-general-card`
- `/system/ai-resume-governance`
- `/system/admin-users`
- `/system/roles`
- `/system/operation-logs`

### 2.3 已发现的候删文件样本

文件：

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\referral\ReferralRiskView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\shared\PlaceholderView.vue`

当前 `rg` 核查未命中对以下名称的引用：

- `DashboardView`
- `ReferralRiskView`
- `PlaceholderView`

当前判断：

- 这批文件是候删样本
- 但还没有完成动态引用 / 文档依赖 / 删除前门禁核销，当前不能直接删

### 2.4 fallback 兼容仍在运行态

文件：

- `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\utils\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\ProjectsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\RolesView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\AppliesView.vue`

已确认：

- 当前仍存在权限 fallback / 兼容授权口径
- 删除旧页面或旧逻辑不能先于 fallback 依赖核销

### 2.5 正式 8 页后端连通性已有初步事实

已核实的正式页与事实源包括：

- `OverviewView.vue` / `DashboardAnalyticsView.vue` -> `/admin/dashboard/overview`
- `UserCenterView.vue` -> `/admin/users`
- `OrganizationsView.vue` -> `/admin/recruit/projects|roles|applies` + `/company/{userId}`
- `ShareCardsView.vue` -> `/admin/content/share-cards`
- `TemplatesView.vue` -> `/admin/content/templates`
- `ActionsView.vue` -> `/admin/dashboard/overview` + `/admin/content/share-cards/legacy-summary`
- `SettingsView.vue` -> 聚合多个真实后台接口

## 3. 设计判断

当前最合理的下一手是：

- 先建 `00-110` 审计 spec
- 后续再基于审计矩阵决定是否进入真实删除切片

原因：

- 现阶段“旧代码未删完”是事实，但原因分散在隐藏路由、fallback、候删文件、历史壳层与治理页保留
- 如果不先做分类矩阵，直接删代码风险高
- 用户当前更需要的是一份能支撑后续删除的依据，而不是仓促删除

## 4. 本轮实施

本轮为 spec-only 建档阶段：

- 新建 `00-110`
- 回填 README / mapping / CURRENT_CONTEXT
- 不改运行时代码

第二轮已继续补齐两张矩阵：

- `D:\XM\kaipai-team\.sce\specs\00-110-current-phase-admin-legacy-route-and-fallback-retirement-audit\legacy-inventory-matrix.md`
- `D:\XM\kaipai-team\.sce\specs\00-110-current-phase-admin-legacy-route-and-fallback-retirement-audit\formal-page-backend-binding-matrix.md`

### 4.1 Legacy inventory matrix 已补齐

当前已把对象分成 4 类：

- Formal active
- Hidden tooling
- Compat fallback
- Retire candidate

其中已明确：

- 正式 8 页全部归为 `Formal active`
- verify / referral / recruit / payment / refund / default-general-card / system/* 治理入口归为 `Hidden tooling`
- recruit 页面的页面 / 动作兼容与 `RolesView.vue` 中的 AI / 招募 fallback 矩阵归为 `Compat fallback`
- `DashboardView.vue`、`ReferralRiskView.vue`、`PlaceholderView.vue` 当前只列为 `Retire candidate / Verify-before-delete`

### 4.2 Formal page backend binding matrix 已补齐

当前已对正式 8 页逐页补齐：

- 页面路径
- 前端容器
- 前端 API 装配文件
- 真实后端接口
- 后端 controller 证据
- 当前状态：
  - 已接真实后端
  - 聚合复用
  - 已接但事实源异常

## 5. 下一步口径

当前矩阵已经补齐，下一步不应直接跨到大范围删除，而应进入**实现型删除前验证切片**，口径如下：

1. **Retain**
   - 正式 8 页
   - hidden tooling 路由
   - 所有仍承担治理职责的页面
2. **Verify-before-delete**
   - 当前 `Retire candidate` 文件
   - 所有仍与 fallback 兼容链有关的页面 / 权限
3. **Retire candidate**
   - 仅在完成动态 import / 文档依赖 / 运行态路径核销后，才可进入真实删除切片

当前删除前门禁已明确：

- 不在 `adminSidebarMenus`
- 不在 `adminMenus`
- 不在 `router/index.ts`
- 无 fallback 依赖
- 无源码 import / 动态 import / 文档引用
- 不承担当前治理或降级承接职责

## 6. 结论

`00-110` 已完成本轮目标：

- 已把“旧代码是否删完 / 新页面是否连后端”从聊天判断提升为独立 audit spec
- 已补齐：
  - legacy inventory matrix
  - formal page backend binding matrix
- 已形成 retain / retire-candidate / verify-before-delete 的删除前执行口径

当前更合理的下一手，不是直接顺手删代码，而是另起一个实现型切片，只处理经过 `00-110` 核销后的真正候删对象。
