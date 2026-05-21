# 00-74 设计说明

## 1. 设计目标

`00-74` 不是回到 `00-71` 再做一轮局部美化，也不是继续延长 `00-72` 的两入口收口；它要解决的是：

1. **reference fidelity**：把登录后正式后台重新拉回 `D:\XM\kaipai-team\_-_1.html` 对应的 8 页信息架构
2. **capability remapping**：把当前已经存在的后台能力重新映射到 reference 页面职责上
3. **tooling separation**：把仍需保留的治理工具页从正式导航中退回，但不在事实未核实前直接删掉

## 2. 已核实的参考事实

### 2.1 总览参考文件

- `D:\XM\kaipai-team\_-_1.html`

### 2.2 当前线程已补充的逐页后台参考图

截至 `2026-04-21`，用户在当前线程已补充：

- 仪表盘
- 数据分析
- 用户管理
- 分享内容
- 风格模板
- 运营动作
- 系统设置

已确认：

- `机构管理` 当前只有 reference 导航存在证据，没有独立单页截图
- 因此 `机构管理` 的视觉合同不能靠截图硬猜；当前实现只能基于真实事实源落一张“招募链路机构目录”正式页，不能伪装成完整组织主数据中心

## 3. 当前运行态与代码事实

### 3.1 当前正式导航事实

当前运行态侧栏正式入口已经恢复为：

- `/dashboard/index`
- `/dashboard/analytics`
- `/users/index`
- `/users/orgs`
- `/content/share-cards`
- `/content/templates`
- `/operate/actions`
- `/system/settings`

对应代码事实：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminSidebar.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\admin-information-architecture.ts`

当前已确认：

- 正式侧栏已经不再停留在 `00-72` 的两入口 shrink-phase
- 但 `dashboard/index` 仍然保留阶段说明语义，尚未回到 reference 的完整 dashboard 合同

### 3.2 已存在但未接入正式架构的 capability

#### 业务用户管理

后端已存在：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\user\AdminUserController.java`

前端已存在：

- `D:\XM\kaipai-team\kaipai-admin\src\api\user-center.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\types\user-center.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\user\UserCenterView.vue`

当前已核实：

- `/admin/users?pageNo=1&pageSize=5` 可以返回真实业务用户列表
- `/admin/users/{id}` 可以返回真实业务用户详情
- `UserCenterView.vue` 已完成回接，当前已进入正式运行态

#### 分享内容

当前 `content/share-cards` 已有真实列表、详情和 legacy 修复动作，但页面第一语义仍是“治理表格”。

#### 风格模板

当前 `content/templates` 已有真实模板列表、详情、编辑、发布、回滚与启停用动作，但页面第一语义仍是“模板配置治理台账”。

### 3.3 当前缺口事实

#### 机构管理

当前没有独立的后台机构主数据接口，也没有单页 reference 截图，但已经核实出一条可复用的首轮正式页事实链：

- `GET /admin/recruit/projects`
  - 提供 `crewUserId / companyProfileId / companyName / contactName / contactPhone / location / sourceUpdatedAt`
- `GET /admin/recruit/roles`
  - 提供角色侧项目归属、招募状态和投递量
- `GET /admin/recruit/applies`
  - 提供投递链路侧活跃度
- `GET /company/{userId}`
  - 提供公司 / 剧组档案详情

因此 `机构管理` 当前可以落一张真实正式页，但边界必须写明：

- 只覆盖**已经进入招募链路**的机构 / 剧组目录
- 不等于完整组织主数据中心
- 后续若要扩成 reference 级完整机构域，仍需要补独立列表接口或独立主数据模型

#### 运营动作 / 系统设置

当前没有直接一一对应的正式页面，但存在可重组的能力来源：

- 工作台概览接口与最近事项
- `content/templates`
- `content/share-cards`
- `content/contact-requests`
- `system/admin-users`
- `system/roles`
- `system/operation-logs`
- `system/ai-resume-governance`

这意味着：

- 可以新增前端正式容器页
- 但只能作为 orchestration / entry hub
- 不能伪造新的业务能力和新的后端事实源

## 4. 目标 reference 页面与 route ownership

| Reference page | 目标路由 | 当前 capability carrier | 当前状态 | 设计结论 |
|------|------|------|------|------|
| 仪表盘 | `/dashboard/index` | `OverviewView.vue` + `/admin/dashboard/overview` | 已存在，但语义漂移 | 保留路由，重写为 reference dashboard |
| 数据分析 | `/dashboard/analytics` | `/admin/dashboard/overview` | 路由缺失 | 新增前端正式页，复用 overview 数据 |
| 用户管理 | `/users/index` | `/admin/users` + `user-center.ts` + `UserCenterView.vue` | API 已存在，视图未接入 | 复活为正式页 |
| 机构管理 | `/users/orgs` | `admin/recruit/projects + roles + applies + company/{userId}` | 已完成 source audit，但无独立机构主数据接口 | 先落“进入招募链路的机构目录”正式页，并显式写清边界 |
| 分享内容 | `/content/share-cards` | `ShareCardsView.vue` | 已存在，但治理语义过强 | 保留路由，回收为 reference content page |
| 风格模板 | `/content/templates` | `TemplatesView.vue` | 已存在，但配置台账语义过强 | 保留路由，回收为 reference template library |
| 运营动作 | `/operate/actions` | dashboard + content + system 的既有能力 | 路由缺失 | 新增前端 orchestration 页 |
| 系统设置 | `/system/settings` | system/* + content/* 的既有能力 | 路由缺失 | 新增前端 aggregation 页 |

## 5. 正式导航与隐藏治理工具分层

### 5.1 正式导航

后续正式侧栏必须恢复为：

- `OVERVIEW`
  - 仪表盘
  - 数据分析
- `GROWTH`
  - 用户管理
  - 机构管理
  - 分享内容
- `OPERATE`
  - 风格模板
  - 运营动作
  - 系统设置

### 5.2 隐藏治理工具

以下页面继续保留，但不属于正式 reference 导航：

- `verify/*`
- `referral/*`
- `recruit/*`
- `payment/orders`
- `refund/orders`
- `content/contact-requests`
- `content/default-general-card`
- `system/admin-users`
- `system/roles`
- `system/operation-logs`
- `system/ai-resume-governance`

设计原则：

- 正式 reference 页面负责“产品级入口”
- 隐藏治理工具负责“运维、审计、修复、兼容治理”

## 6. 权限与路由策略

### 6.1 全量能力库存

继续以：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`

作为全量能力库存。

### 6.2 正式导航投影

后续正式侧栏不再使用当前 shrink-phase 的 `adminSidebarMenus` 作为最终目标；应改为新的 reference projection：

- 第一阶段可以直接替换 `adminSidebarMenus`
- 也可以抽出新的 projection 常量

但无论采用哪种实现，必须满足：

- 正式导航只呈现 reference 8 页
- 隐藏治理工具不从正式侧栏暴露
- 仍由当前权限集合过滤

### 6.3 权限复用原则

第一阶段新正式页优先复用既有 page permission：

| 目标正式页 | 第一阶段建议权限来源 |
|------|------|
| 仪表盘 | `page.dashboard.index` |
| 数据分析 | `page.dashboard.index` |
| 用户管理 | `page.users.index` |
| 机构管理 | `page.users.index` |
| 分享内容 | `page.content.share-cards` |
| 风格模板 | `page.content.templates` |
| 运营动作 | `page.dashboard.index` 或容器页复用策略 |
| 系统设置 | `page.system.roles` / `page.system.admin-users` 的聚合承接策略 |

约束：

- 第一阶段不得因为新建正式容器页就同步引入一整套新后端权限码
- 但也不能绕开现有权限直接把页面暴露给无关角色

## 7. 页面级设计策略

### 7.1 仪表盘

继续使用当前 `/admin/dashboard/overview`，但页面结构需回到 reference：

- 顶部搜索 / 日期 / 通知 / 导出语义
- 4 张 KPI
- 漏斗 + 趋势
- 留存 / 风格 / 渠道三块组合

### 7.2 数据分析

作为独立正式页，从 dashboard 能力中拆出：

- 分渠道表现
- 渠道 mix
- 洞察说明

不新增后端接口，只做前端结构重组。

### 7.3 用户管理

以真实 `/admin/users` 为主事实源，落地 reference 的：

- 顶部统计卡
- 用户类型 tabs
- 主表格
- 详情抽屉或详情页

`system/admin-users` 只保留后台账号治理，不再承接业务用户管理。

### 7.4 机构管理

当前已完成 source audit，第一阶段改为：

- 正式导航位置保留
- 页面主合同升级为真实机构目录页
- 目录骨架由 `admin/recruit/projects` 聚合承接
- 角色与投递计数由 `admin/recruit/roles`、`admin/recruit/applies` 汇总补齐
- 详情抽屉由 `company/{userId}` 补齐机构档案字段

页面必须显式说明：

- 当前只覆盖已进入招募链路的机构
- 当前不是完整组织主数据中心
- 若数据量继续上升，需要补专门机构列表接口，而不是继续无限制前端拼接

### 7.5 分享内容

以 `content/share-cards` 为主 carrier，页面可增加：

- 画廊模式 / 列表模式切换
- 公开 / 审核中 / 下架等内容态标签
- 分享数 / 进入数等内容导向指标

但：

- legacy 修复与治理字段不得继续占据页面主视觉
- 它们应沉到详情、二级操作或治理模式中

### 7.6 风格模板

以 `content/templates` 为主 carrier，改为：

- 模板卡片网格
- 使用次数、状态和编辑动作
- 新建模板主按钮

现有发布、回滚、启停用动作保留，但改变其视觉承载方式。

### 7.7 运营动作

新增前端 orchestration 页，允许聚合：

- dashboard 的关键统计
- share-cards / templates / contact-requests 的可执行动作
- 当前仍存在的治理工具入口

页面只负责“推荐、配置、跳转”，不负责新业务能力落地。

### 7.8 系统设置

新增前端 aggregation 页，允许聚合：

- 平台基础信息
- 内容审核入口
- 角色与后台账号入口
- 审计入口

约束：

- 第一阶段可以是 entry-list 结构
- 不能伪装成已有完整配置写入能力

## 8. 分阶段实施顺序

### 8.1 阶段 1：spec 与导航回收

- 新增 `00-74`
- 更新 README / mapping / CURRENT_CONTEXT
- 调整正式侧栏 projection
- 明确 hidden tooling

### 8.2 阶段 2：已有 capability 的正式页回收

- 仪表盘
- 数据分析
- 用户管理
- 分享内容
- 风格模板

### 8.3 阶段 3：容器页补齐

- 运营动作
- 系统设置

### 8.4 阶段 4：机构管理 source audit

- 已完成首轮 audit
- 当前结论：可以落一张“招募链路机构目录”正式页
- 后续若要继续向 reference 完整机构域推进，需要额外补机构主数据事实源

## 9. 影响文件

### 9.1 正式导航与壳层

- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminSidebar.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminTopbar.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\admin-information-architecture.ts`

### 9.2 页面级改造

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\user\UserCenterView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\content\ShareCardsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\content\TemplatesView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\AdminUsersView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\OperationLogsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\content\ContactRequestsView.vue`

### 9.3 现有 API / 类型事实源

- `D:\XM\kaipai-team\kaipai-admin\src\api\user-center.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\types\user-center.ts`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\user\AdminUserController.java`

## 10. 风险与边界

### 10.1 已确认

- 当前正式后台与 reference 的偏差已经是架构级，而不是只差样式
- `/admin/users` 是真实事实源，可支撑业务用户管理页
- `UserCenterView.vue` 已完成回接，当前业务用户管理事实源稳定
- `机构管理` 已完成首轮事实源审计，并可落地为“已进入招募链路的机构目录”正式页

### 10.2 实施待核实

- `数据分析` 拆页后是否只靠现有 `/admin/dashboard/overview` 就足够支撑 reference 的渠道分析块
- `运营动作 / 系统设置` 是否需要少量只读配置常量才能完整表达 reference 顶层信息
- `机构管理` 后续是否需要独立机构主数据接口，以摆脱前端对 recruit / company 多源拼接的依赖

因此：

- 当前已足够继续按 spec 推进后台 reference 重构方向
- 但 `机构管理` 当前只能被定义为“招募链路机构目录”，不能误报成完整组织主数据中心
