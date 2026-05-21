# 00-110 Formal Page Backend Binding Matrix

> 目的：固化正式 8 页与真实后端事实源的绑定关系，区分“已接真实后端”“聚合复用”“已接但事实源异常”。

| 正式页 | 路径 | 前端容器 | 前端 API 装配 | 真实后端接口 | 后端 controller 证据 | 当前状态 | 边界说明 |
|--------|------|----------|---------------|--------------|----------------------|----------|----------|
| 仪表盘 | `/dashboard/index` | `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue` | `D:\XM\kaipai-team\kaipai-admin\src\api\dashboard.ts` -> `fetchDashboardOverview` | `GET /admin/dashboard/overview` | `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\dashboard\AdminDashboardController.java` | **已接真实后端** | 当前主仪表盘聚合页，不是占位页 |
| 数据分析 | `/dashboard/analytics` | `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardAnalyticsView.vue` | `D:\XM\kaipai-team\kaipai-admin\src\api\dashboard.ts` -> `fetchDashboardOverview` | `GET /admin/dashboard/overview` | `AdminDashboardController.java` | **聚合复用** | 当前渠道 / 留存 / 漏斗 / 分群主要复用 dashboard overview 聚合字段，不是独立 BI 服务 |
| 用户管理 | `/users/index` | `D:\XM\kaipai-team\kaipai-admin\src\views\user\UserCenterView.vue` | `D:\XM\kaipai-team\kaipai-admin\src\api\user-center.ts` -> `fetchUserCenterUsers` / `fetchUserCenterUserDetail` | `GET /admin/users`、`GET /admin/users/{id}` | `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\user\AdminUserController.java` | **已接真实后端** | 当前明确是业务用户中心，不再用后台账号治理页顶替 |
| 分享内容 | `/content/share-cards` | `D:\XM\kaipai-team\kaipai-admin\src\views\content\ShareCardsView.vue` | `D:\XM\kaipai-team\kaipai-admin\src\api\content.ts` -> `fetchContentShareCards` / `fetchContentShareCardDetail` / `fetchContentShareCardLegacySummary` / `repairContentShareCardLegacy` | `GET /admin/content/share-cards`、`GET /admin/content/share-cards/{shareCardId}`、`GET /admin/content/share-cards/legacy-summary`、`POST /admin/content/share-cards/repair-legacy` | `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\content\AdminContentController.java` | **已接真实后端** | 已接真实内容治理接口，同时保留 legacy 修复事实源 |
| 风格模板 | `/content/templates` | `D:\XM\kaipai-team\kaipai-admin\src\views\content\TemplatesView.vue` | `D:\XM\kaipai-team\kaipai-admin\src\api\content.ts` -> `fetchTemplates` / `fetchTemplateDetail` / `createTemplate` / `updateTemplate` / `publishTemplate` / `rollbackTemplate` | `GET /admin/content/templates`、`GET /admin/content/templates/{id}`、`POST /admin/content/templates`、`POST /admin/content/templates/{id}/publish`、`POST /admin/content/templates/{id}/rollback` 等 | `AdminContentController.java` | **已接真实后端** | 已接配置、发布、回滚治理链 |
| 运营动作 | `/operate/actions` | `D:\XM\kaipai-team\kaipai-admin\src\views\operate\ActionsView.vue` | `D:\XM\kaipai-team\kaipai-admin\src\api\dashboard.ts` + `D:\XM\kaipai-team\kaipai-admin\src\api\content.ts` | `GET /admin/dashboard/overview`、`GET /admin/content/share-cards/legacy-summary` | `AdminDashboardController.java` + `AdminContentController.java` | **聚合复用** | 当前页重组现有概览与 legacy 治理摘要，不是独立运营动作服务 |
| 系统设置 | `/system/settings` | `D:\XM\kaipai-team\kaipai-admin\src\views\system\SettingsView.vue` | `D:\XM\kaipai-team\kaipai-admin\src\api\dashboard.ts` + `content.ts` + `system.ts` | `GET /admin/dashboard/overview`、`GET /admin/content/templates`、`GET /admin/content/share-cards`、`GET /admin/system/users`、`GET /admin/system/roles`、`GET /admin/system/operation-logs`、`GET /admin/system/roles/ai-governance-matrix` | `AdminDashboardController.java` + `AdminContentController.java` + `AdminSystemController.java` | **已接真实后端聚合** | 当前页能聚合多个真实后台接口，`operation-logs` 事实源已恢复，前端降级承接仅保留为兜底 |

## 补充判断

### 1. 当前正式 8 页不是纯 UI

依据：

- 上述 8 页都能在前端容器中定位到 API 装配
- 对应后端 controller 都存在明确 `@RequestMapping / @GetMapping / @PostMapping`

### 2. “已连后端”不等于“每页都有独立新服务”

当前需区分：

- **已接真实后端**：用户管理、分享内容、模板库、仪表盘、系统设置
- **聚合复用**：数据分析、运营动作

### 3. 当前最需要谨慎的例外

- `share-card legacy-summary / repair-legacy`：
  - 当前仍存在
  - 但它属于实例化迁移后的治理兜底，不再代表正式页缺真实后端
