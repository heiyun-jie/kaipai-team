# 00-74 执行记录

## 1. 当前状态

- 已重新读取 `User Global Memory`
- 已核对 `00-71 / 00-72` 的当前后台边界
- 已对当前运行态后台与用户补充的 reference 截图做逐页对比
- 已确认需要新增 `00-74`，作为后台 reference UI / 架构二次收口的独立 Spec

## 2. 已核实的 reference 事实

### 2.1 参考文件

- `D:\XM\kaipai-team\_-_1.html`

### 2.2 用户在当前线程补充的逐页后台截图

已覆盖：

- 仪表盘
- 数据分析
- 用户管理
- 分享内容
- 风格模板
- 运营动作
- 系统设置

已确认：

- reference 左侧导航中存在 `机构管理`
- 但当前线程尚未补充 `机构管理` 的独立页面截图

## 3. 已核实的当前运行态事实

### 3.1 当前正式导航

通过真实浏览器登录 `http://127.0.0.1:5100` 后，当前正式入口只有：

- `/dashboard/index`
- `/content/share-cards`
- `/content/contact-requests`

实际页面文案可见：

- `CURRENT PHASE`
- `主导航已收口`
- `当前后台主入口只围绕分享访问、风格偏好、成卡转化与联系闭环组织`

对应代码事实：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\admin-information-architecture.ts`

这证明当前后台仍停留在 `00-72` 的 shrink-phase。

### 3.2 逐页对比结论

#### 仪表盘

- 当前存在真实页面：`/dashboard/index`
- 但页面语义已经改成阶段收口说明，不再是 reference 的完整 dashboard

#### 数据分析

- 当前没有独立正式页
- 但可复用 `/admin/dashboard/overview` 作为数据来源

#### 用户管理

- 当前没有正式业务用户管理页
- 但存在真实 API 与前端类型 / API 装配层

#### 分享内容

- 当前 `content/share-cards` 为真实运行页
- 但第一语义是治理表格，不是 reference 的内容卡片墙

#### 风格模板

- 当前 `content/templates` 为真实运行页
- 但第一语义是模板配置治理台账，不是 reference 的模板库

#### 运营动作

- 当前没有独立正式页
- 但存在可重组的统计与治理动作来源

#### 系统设置

- 当前没有 reference 级聚合页
- 但存在可汇聚的 `system/*` 工具页

#### 机构管理

- 当前缺少独立正式页
- 当前缺少明确 runtime source
- 当前缺少单页 reference 截图

因此它必须被定义为“事实源待补齐页”。

## 4. 已核实的 capability 事实源

### 4.1 `/admin/users` 可返回真实业务用户数据

已通过现有后台登录态实际调用：

- `GET /api/admin/users?pageNo=1&pageSize=5`
- `GET /api/admin/users/10000`

结果已确认：

- 列表可返回真实业务用户
- 详情可返回用户、演员档案、认证、邀请、会员、支付、退款与最近操作留痕

这证明：

- `用户管理` 并非只能由 `system/admin-users` 伪代
- 当前真正的业务用户中心事实源已经存在

### 4.2 前端业务用户中心当前仍是占位

已核对：

- `D:\XM\kaipai-team\kaipai-admin\src\views\user\UserCenterView.vue`

当前文件长度仅 23 字节，占位内容尚未接入运行态。

已核对对应前端事实源：

- `D:\XM\kaipai-team\kaipai-admin\src\api\user-center.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\types\user-center.ts`

这证明：

- 当前不是没有用户中心能力
- 而是“接口与类型已接通、页面壳未接入”

## 5. 本轮已完成动作

- 已新增：
  - `D:\XM\kaipai-team\.sce\specs\00-74-current-phase-admin-reference-ui-architecture-rebuild\requirements.md`
  - `D:\XM\kaipai-team\.sce\specs\00-74-current-phase-admin-reference-ui-architecture-rebuild\design.md`
  - `D:\XM\kaipai-team\.sce\specs\00-74-current-phase-admin-reference-ui-architecture-rebuild\tasks.md`
  - `D:\XM\kaipai-team\.sce\specs\00-74-current-phase-admin-reference-ui-architecture-rebuild\execution.md`
- 已回填：
  - `D:\XM\kaipai-team\.sce\specs\README.md`
  - `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`
  - `D:\XM\kaipai-team\.sce\steering\CURRENT_CONTEXT.md`

### 5.1 已完成 `T4`：正式导航 projection 与路由骨架回收

已改：

- `D:\XM\kaipai-team\kaipai-admin\src\types\admin.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\permission-registry.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminSidebar.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\admin-information-architecture.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`

当前结果：

- 正式侧栏已从 `CURRENT PHASE` 两入口恢复为：
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
- `menu.users`、`page.users.index`、`page.users.detail` 已进入前端权限登记口径
- 已补正式路由骨架：
  - `/dashboard/analytics`
  - `/users/index`
  - `/users/orgs`
  - `/operate/actions`
  - `/system/settings`
- 其中当前仍缺事实源的页面先通过 placeholder route 承接，不伪装成已完成

### 5.2 已完成 `T5`：真实业务用户管理页回接

已改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\user\UserCenterView.vue`

当前结果：

- `UserCenterView.vue` 已从占位页回接为真实业务用户管理页
- 页面已接入：
  - `/admin/users`
  - `/admin/users/{id}`
- 当前页已具备：
  - 顶部 4 张概览卡
  - reference 风格的 segment 视图切换
  - 业务用户筛选区
  - 真实业务用户列表
  - 用户详情抽屉
- 页面显式说明：
  - 已回接真实 `/admin/users` 事实源
  - 后台账号治理继续留在隐藏工具域，不再顶替业务用户管理

### 5.3 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过
- 已新增构建产物：
  - `dist/assets/UserCenterView-*.js`
  - `dist/assets/UserCenterView-*.css`

### 5.4 运行态核对

已通过真实浏览器会话打开：

- `http://127.0.0.1:5100/users/index`

已确认：

- 左侧正式导航已显示 `OVERVIEW / GROWTH / OPERATE`
- `用户管理` 页面可正常进入
- 顶部 eyebrow 已切到 `GROWTH / 用户增长`
- 页面已展示真实业务用户列表与分页，而不是占位页

### 5.5 已完成 `T6`：分享内容 / 风格模板正式页面表达首轮回收

已改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\content\ShareCardsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\content\TemplatesView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\api\content.ts`

当前结果：

- `分享内容`
  - 已从“治理表格页”改成默认卡片视图
  - 已补：
    - 顶部 tabs
    - 卡片 / 列表视图切换
    - 内容卡片墙
    - 互动摘要
  - `legacy 修复` 仍保留，但已下沉为辅助治理区，不再占据页面主视觉
  - 详情抽屉与真实治理字段仍继续保留，避免为了贴 reference 把 runtime 排查能力做丢

- `风格模板`
  - 已从“模板配置治理台账”改成默认模板库卡片网格
  - 已补：
    - 状态 tabs
    - 模板库 / 列表视图切换
    - 模板卡片网格
    - 卡片内启用 / 停用 / 发布 / 回滚 / 编辑动作
  - 保留真实模板运行时链路：
    - 新建
    - 编辑
    - 启停用
    - 发布
    - 回滚

### 5.6 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过
- 已新增 / 更新构建产物：
  - `dist/assets/ShareCardsView-*.js`
  - `dist/assets/ShareCardsView-*.css`
  - `dist/assets/TemplatesView-*.js`
  - `dist/assets/TemplatesView-*.css`

### 5.7 本轮运行态抽查

已通过真实浏览器会话打开：

- `http://127.0.0.1:5100/content/share-cards`
- `http://127.0.0.1:5100/content/templates`

已确认：

- `分享内容`
  - 顶部 eyebrow 已切到 `GROWTH / 分享内容`
  - 页面默认进入卡片化内容墙，不再默认停留在治理表格
  - 页面仍能继续进入详情抽屉与 legacy 修复动作

- `风格模板`
  - 顶部 eyebrow 已切到 `OPERATE / 运营管理`
  - 页面默认进入模板卡片库，不再默认停留在台账表格
  - 卡片内真实编辑 / 启停用 / 发布 / 回滚动作仍可见

### 5.8 已完成 `T7.1`：数据分析正式页首轮落地

已改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardAnalyticsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`

当前结果：

- `/dashboard/analytics` 已从 placeholder route 回接为真实正式页
- 页面已具备：
  - 页内 tabs：渠道分析 / 留存分析 / 转化漏斗 / 用户分群
  - 时间窗口筛选
  - 独立分析面板与 donut 结构
- 当前数据来源继续只认现有 `/admin/dashboard/overview`
- 页面已显式写明：
  - 当前后端没有微信好友 / 朋友圈 / 企业微信等真实渠道字段
  - 当前“渠道块”仅由 `scene` 分布近似承接
  - 不伪造真实渠道口径

### 5.9 本轮补充验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过
- 已新增 / 更新构建产物：
  - `dist/assets/DashboardAnalyticsView-*.js`
  - `dist/assets/DashboardAnalyticsView-*.css`

### 5.10 本轮运行态抽查补充

已通过真实浏览器会话打开：

- `http://127.0.0.1:5100/dashboard/analytics`

已确认：

- 页面标题已变为 `数据分析`
- `OVERVIEW / 数据分析` eyebrow 正常显示
- 页面内 tabs 已可见
- 页面中已明确出现“当前后端未返回真实渠道字段，本页先用 scene 分布承接 reference 结构，不伪造渠道口径”的说明文案

### 5.11 已完成 `T7.2`：运营动作 / 系统设置正式容器页落地

已改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\operate\ActionsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\SettingsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`

当前结果：

- `/operate/actions`
  - 已从 placeholder route 回接为真实正式页
  - 页面只重组现有 overview、legacy summary 与治理入口
  - 不新增伪运营能力或伪 Campaign 模型
- `/system/settings`
  - 已从 placeholder route 回接为真实聚合页
  - 平台信息、内容治理、权限治理都只认现有真实 carrier
  - 对没有稳定事实源的平台域名 / 客服联系明确显示“未纳入后台正式事实源”
  - `operation-logs` 接口异常时，已通过分源降级保持页面可用

### 5.12 已完成 `T8`：机构管理事实源审计与首轮正式页落地

#### 5.12.1 已核实的机构事实源

已通过真实后台登录态调用：

- `POST /api/admin/auth/login`
- `GET /api/admin/recruit/projects?pageNo=1&pageSize=5`
- `GET /api/admin/recruit/roles?pageNo=1&pageSize=5`
- `GET /api/admin/recruit/applies?pageNo=1&pageSize=5`
- `GET /api/company/10000`

已确认：

- `admin/recruit/projects` 可返回：
  - `crewUserId`
  - `companyProfileId`
  - `companyName`
  - `contactName`
  - `contactPhone`
  - `location`
  - `sourceUpdatedAt`
- `admin/recruit/roles` 可返回：
  - 机构侧角色、项目归属与投递量
- `admin/recruit/applies` 可返回：
  - 机构侧投递活跃度
- `company/{userId}` 可返回：
  - `companyType`
  - `teamScale`
  - `focusDirection`
  - `representativeWorks`
  - `cooperationNeed`
  - `officeAddress`

这证明：

- 当前虽然没有独立的后台机构列表接口
- 但已经存在一条足以承接首轮正式机构管理页的真实事实链

#### 5.12.2 已改与已落地页面

已改：

- `D:\XM\kaipai-team\kaipai-admin\src\types\company.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\api\company.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\user\OrganizationsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\admin-information-architecture.ts`

当前结果：

- `/users/orgs` 已从 placeholder route 回接为真实正式页
- 页面主表达已改为“机构目录”
- 目录只承接：
  - 已进入招募链路的机构 / 剧组
- 页面显式写明：
  - 当前事实源来自 `projects + roles + applies + company`
  - 当前不是完整组织主数据中心
- 页面已具备：
  - 顶部 4 张概览卡
  - segment 视图
  - 快速筛选 + 高级筛选
  - 机构卡片目录
  - 机构详情抽屉
  - 项目 / 角色 / 投递 drill-down 跳转

#### 5.12.3 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过
- 已新增构建产物：
  - `dist/assets/OrganizationsView-*.js`
  - `dist/assets/OrganizationsView-*.css`

#### 5.12.4 浏览器运行态核对

已通过真实浏览器会话打开：

- `http://127.0.0.1:5100/users/orgs`

已确认：

- 左侧正式导航中的 `机构管理` 可正常进入
- 顶部 eyebrow 已切到 `GROWTH / 机构管理`
- 页面已显示真实机构目录卡片，而非占位页
- 详情抽屉已成功拉起，并显示：
  - 公司档案
  - 招募链路摘要
  - 最近项目 / 角色 / 投递
- 当前运行态只有 1 个机构目录样本，来自现有招募链路数据

### 5.13 已完成 `OverviewView.vue`：仪表盘正式 dashboard 合同回收

已改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue`

当前结果：

- `OverviewView.vue` 已从 shrink-phase 说明页回收为 reference 仪表盘正式页
- 页面已具备：
  - 顶部轻量控制条
  - 4 张 KPI 大卡
  - 转化漏斗
  - 主链热度曲线
  - 留存承接卡
  - 风格偏好 donut
  - 渠道分布近似承接卡
  - 正式页面矩阵
  - 治理动态区
- 当前仪表盘继续只认：
  - `/admin/dashboard/overview`
- 页面已显式写明：
  - 当前没有真实留存字段
  - 当前没有真实渠道归因字段
  - 留存与渠道区域仅做事实边界内的正式卡位承接，不伪造数据
- 原本只指向 shrink-phase 3 个入口的模块区，已回收为 reference 的 8 页正式矩阵

#### 5.13.1 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过
- 已新增 / 更新构建产物：
  - `dist/assets/OverviewView-*.js`
  - `dist/assets/OverviewView-*.css`

#### 5.13.2 浏览器运行态核对

已通过真实浏览器会话打开：

- `http://127.0.0.1:5100/dashboard/index`

已确认：

- 顶部 eyebrow 已显示 `OVERVIEW / 仪表盘`
- 页面第一屏已不再出现 `CURRENT PHASE / 主导航已收口` 的 shrink-phase 说明文案
- 页面已实际显示：
  - 顶部控制条
  - 4 张 KPI 卡
  - 转化漏斗
  - 主链热度曲线
  - 留存 / 风格 / 渠道三块
- 8 页正式矩阵
- 治理动态区
- 当前运行态 `recentItems` 为空，因此治理动态区正确显示空态，而不是伪造最近事项

### 5.14 已完成 `T9`：8 页正式页面运行态证据回填

#### 5.14.1 已采集的运行态截图

已通过真实浏览器登录态，批量采集以下正式页面全页截图：

- `D:\XM\kaipai-team\output\playwright\00-74\dashboard-index.png`
- `D:\XM\kaipai-team\output\playwright\00-74\dashboard-analytics.png`
- `D:\XM\kaipai-team\output\playwright\00-74\users-index.png`
- `D:\XM\kaipai-team\output\playwright\00-74\users-orgs.png`
- `D:\XM\kaipai-team\output\playwright\00-74\content-share-cards.png`
- `D:\XM\kaipai-team\output\playwright\00-74\content-templates.png`
- `D:\XM\kaipai-team\output\playwright\00-74\operate-actions.png`
- `D:\XM\kaipai-team\output\playwright\00-74\system-settings.png`

#### 5.14.2 当前证据结论

已确认上述 8 页都已进入真实运行态，而不是 placeholder route 或 shrink-phase 残留页：

- `dashboard/index`
  - 已回到 reference 仪表盘合同
- `dashboard/analytics`
  - 已为真实数据分析页
- `users/index`
  - 已为真实业务用户管理页
- `users/orgs`
  - 已为真实机构目录页
- `content/share-cards`
  - 已为正式内容卡片墙表达
- `content/templates`
  - 已为正式模板库表达
- `operate/actions`
  - 已为真实运营动作聚合页
- `system/settings`
  - 已为真实系统设置聚合页

#### 5.14.3 T9 收口结论

当前 `00-74` 已完成：

- `src` 层：正式 8 页都已有实际 carrier
- `build` 层：最近一轮 `type-check / build` 均通过
- `runtime(browser)` 层：8 页正式页面都已完成真实浏览器截图取证

这意味着：

- `T9` 已满足当前阶段的最小验收条件
- `00-74` 的核心任务链已经全部闭环

### 5.15 已完成 `AdminTopbar.vue`：reference 顶控语义精修

已改：

- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminTopbar.vue`

当前结果：

- 顶部控制条已补回 reference 的四类核心语义：
  - 搜索框
  - 窗口切换入口
  - 通知入口
  - 导出按钮
- mainline 页顶部左侧已收为 `eyebrow + title`
  - 不再显示长说明文案
- mainline 页顶部右侧已隐藏日期 / 服务状态 / 角色三类冗余芯片
  - 保留轻量账号入口
- 但当前没有伪造能力：
  - 全局搜索未接通真实事实源时，显式提示继续使用页内筛选
  - 导出按钮保留 reference 语义，但继续禁用，避免误导
  - 通知入口只使用真实 `/admin/dashboard/overview` 的待办聚合
- 当前顶部控制条已比之前更接近 reference，但仍保持真实能力边界

#### 5.15.1 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

#### 5.15.2 浏览器抽查

已通过真实浏览器会话打开：

- `http://127.0.0.1:5100/dashboard/index`

已确认顶部控制条已出现：

- 搜索输入
- 窗口按钮
- 通知按钮
- 导出报表按钮
- 轻量账号入口

同时已确认：

- mainline 顶部不再继续堆叠日期 / 服务状态 / 角色芯片
- mainline 顶部不再显示拉高首屏的长说明文案

这说明 `AdminTopbar.vue` 已不再停留在早期简化版状态。

### 5.16 已完成：dashboard 时间窗口从页内工具条上移到顶控

已改：

- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminTopbar.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardAnalyticsView.vue`

当前结果：

- `AdminTopbar.vue`
  - 顶部窗口按钮已从占位提示升级为真实 dashboard 窗口控制
  - 支持：
    - 近 7 天
    - 近 30 天
    - 近 90 天
    - 自定义时间范围
    - 清除窗口
  - 窗口状态通过 route query 写入：
    - `dateFrom`
    - `dateTo`
- `OverviewView.vue`
  - 已移除页内重复的顶部工具条卡片
  - 已改为读取 route query 中的 `dateFrom / dateTo`
  - 时间窗口变更后自动重新加载 `/admin/dashboard/overview`
- `DashboardAnalyticsView.vue`
  - 页内工具条已只保留分析 tabs
  - 日期窗口控制上移到顶部控制条
  - 同样读取 route query 中的 `dateFrom / dateTo`

#### 5.16.1 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

#### 5.16.2 浏览器抽查

已通过真实浏览器会话打开：

- `http://127.0.0.1:5100/dashboard/index`
- `http://127.0.0.1:5100/dashboard/analytics?dateFrom=2026-03-24T00:00:00&dateTo=2026-04-22T23:59:59`

已确认：

- 仪表盘页面首屏不再出现页内重复顶部工具条卡片
- 顶控窗口按钮可打开窗口面板
- 点击 `近 30 天` 后，URL 已写入：
  - `dateFrom=2026-03-24T00:00:00`
  - `dateTo=2026-04-22T23:59:59`
- 数据分析页面顶部工具条已只保留 tabs，不再重复显示页内日期选择器 / 重置 / 刷新
- 顶控窗口按钮在数据分析页显示为 `近 30 天`

### 5.17 已完成：数据分析 tabs 壳层轻量化

已改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardAnalyticsView.vue`

当前结果：

- 数据分析页顶部 tabs 壳层已从“占满整行的大卡”收成更轻的参考稿风格
- 当页内日期控制上移后，tabs 区不再保留右侧空白动作位
- 当前页面首屏结构更接近：
  - 标题
  - 顶控
  - 轻量 tabs 壳层
  - 内容区

#### 5.17.1 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

#### 5.17.2 浏览器抽查

已通过真实浏览器会话打开：

- `http://127.0.0.1:5100/dashboard/analytics?dateFrom=2026-03-24T00:00:00&dateTo=2026-04-22T23:59:59`

已确认：

- 页内 tabs 卡已不再占满整行
- tabs 区当前只承担分析维度切换，不再承担重复窗口控制

### 5.18 已完成：侧栏 footer 壳层收紧

已改：

- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminSidebar.vue`

当前结果：

- 侧栏 footer 已从“头像 + admin + collapse 按钮”收成更接近 reference 的：
  - 身份徽记
  - 双行角色文案
  - 轻量尾按钮
- 当前保留真实运行态信息：
  - `平台运营 · admin`
  - `ADMIN`
- 同时没有丢失侧栏收起能力；尾按钮继续承接 collapse 动作

#### 5.18.1 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

#### 5.18.2 浏览器抽查

已通过真实浏览器会话打开：

- `http://127.0.0.1:5100/dashboard/index`

已确认：

- 侧栏 footer 当前已显示：
  - `管`
  - `平台运营 · admin`
  - `ADMIN`
- 视觉结构已更贴近 reference 页底身份区

### 5.19 已核实：仪表盘 `TOP CONTENT` 当前仍缺真实排序事实源

已通过真实后台登录态调用：

- `GET /api/admin/content/share-cards?pageNo=1&pageSize=5`

已确认当前分享卡治理列表可返回：

- `shareCardId`
- `ownerUserId`
- `ownerName`
- `sceneKey`
- `templateName`
- `shareStatus`
- `historyCount`
- `totalContactRequestCount`
- `approvedContactRequestCount`

但当前缺少 reference `TOP CONTENT` 真正需要的关键排序事实：

- 分享总次数
- 带来进入数
- 进入率
- 可稳定排序的高价值内容热度字段

当前样本里也可见：

- `historyCount` 多数为 `0`
- `totalContactRequestCount` 多数为 `0`

因此，当前 `OverviewView.vue` 底部继续保留为：

- 正式页面矩阵

而不是伪造 reference 的“高价值内容 TOP 榜”。

### 5.20 已完成：最新壳层尺寸收紧后的浏览器复核

#### 5.20.1 复核范围

本轮复核针对上一轮已经完成但尚未取证的壳层尺寸与留白调整：

- `D:\XM\kaipai-team\kaipai-admin\src\layouts\AdminLayout.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminSidebar.vue`

当前源码事实：

- `AdminLayout.vue`
  - 主区 padding 已收为 `12px 16px 16px 0`
  - 内容区左侧 padding 已收为 `16px`
  - content shell padding 已收为 `18px 20px 24px`
  - content shell radius 已收为 `28px`
  - content shell 阴影已减弱
- `AdminSidebar.vue`
  - 侧栏宽度已收为 `232px`
  - 折叠宽度已收为 `86px`
  - brand、section gap、menu item、footer 与 collapse 按钮尺寸均已收紧

#### 5.20.2 浏览器运行态证据

已复用真实 Playwright 会话：

- session：`layout-shell`
- URL：`http://127.0.0.1:5100/dashboard/index`

已采集最新全页截图：

- `D:\XM\kaipai-team\output\playwright\00-74\dashboard-index-shell-verify.png`

已确认：

- 页面仍停留在真实登录后后台运行态，不是静态截图或构建产物预览
- 左侧正式导航仍为 `OVERVIEW / GROWTH / OPERATE`
- 当前活跃页仍为 `仪表盘`
- 顶控仍显示：
  - 搜索输入
  - dashboard 窗口按钮
  - 通知按钮
  - 禁用态导出按钮
  - 轻量账号入口
- 侧栏收窄后未出现主导航文字拥挤、footer 破版或身份区挤压
- 主内容 shell 与 reference 的左右贴合感比 `dashboard-layout-before.png` 更接近
- 浏览器 console 当前唯一错误为 `favicon.ico` 404，与本轮壳层调整无关

#### 5.20.3 本轮判断

本轮最新壳层尺寸调整可以保留。

依据：

- `src` 层：`AdminLayout.vue / AdminSidebar.vue` 的尺寸、padding、radius、shadow 已明确收紧
- `runtime(browser)` 层：`dashboard-index-shell-verify.png` 已证明最新壳层运行态可正常展示
- 视觉对比层：当前剩余差异主要来自仪表盘页内数据事实源与 reference 示例内容不同，而不是壳层宽度或导航结构问题

因此本轮不继续盲调壳层，不新增页面或新能力，只回填运行态证据。

## 6. 当前结论（历史阶段）

当前后台与 reference 的偏差已经不是“样式细节未对齐”，而是：

- 正式信息架构被 `00-72` 历史阶段收口到了 3 个入口
- reference 需要的是 8 个正式页面状态
- 其中 `用户管理` 已有真实事实源，可进入后续实现
- `机构管理` 在当时仍没有足够事实源，必须保持显式待审计状态

因此，本轮最合理的推进方式不是回滚 `00-72` 历史文档，而是：

- 新增 `00-74`
- 让 `00-74` 成为后台当前主线
- 后续按“正式 reference 页面恢复 -> 隐藏治理工具退回 -> 机构事实源审计”的顺序推进

## 7. 最新结论（2026-04-22）

当前 `00-74` 主线已经完成：

- 正式导航恢复
- 仪表盘回收
- 用户管理回接
- 分享内容回收
- 风格模板回收
- 数据分析落地
- 运营动作落地
- 系统设置落地
- 机构管理完成事实源审计并落首轮正式页
- `T9` 运行态证据回填完成
- `AdminTopbar` 顶控语义精修完成
- `AdminSidebar` footer 壳层精修完成
- `AdminLayout / AdminSidebar` 最新壳层尺寸收紧已完成浏览器运行态复核
- 已新增最新壳层复核截图：`D:\XM\kaipai-team\output\playwright\00-74\dashboard-index-shell-verify.png`

因此，后台 reference-driven 二次收口当前已经从“导航骨架恢复阶段”进入到：

- “核心任务与主要壳层精修都已完成、且关键事实边界已核实的可验收阶段”
