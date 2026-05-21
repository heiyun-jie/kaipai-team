# 00-72 设计说明

## 1. 设计目标

`00-72` 不再解决“后台长什么样”，而是解决“后台当前阶段到底应该呈现什么信息架构”：

1. 延续 `00-71` 已完成的 `_-_1.html` 控制台视觉基线
2. 把 `00-69` 定义的后台当前架构落实到菜单、路由、页面归类
3. 在不盲删旧页面的前提下，把主架构、tooling 页、删除候选页彻底分开

## 2. 与已有 Spec 的关系

### 2.1 `00-71` 负责什么

- 后台公共壳层
- 顶部栏与窄侧栏语言
- 工作台看板式结构
- 登录页与全站视觉系统收口

### 2.2 `00-72` 负责什么

- 当前阶段后台主架构定义
- 主导航事实源收口
- 页面分层：主架构 / 隐藏治理 / 删除候选
- 后续旧业务域退场顺序

### 2.3 `00-69` 与 `00-72` 的关系

- `00-69` 是全项目上位架构 Spec，定义“后台只保留控制台 / 用户中心”
- `00-72` 是 `kaipai-admin` 的具体落地 Spec，负责把这一上位结论落到后台代码结构

## 3. 当前差距事实

| 事实 | 当前状态 | 说明 |
|------|----------|------|
| 登录页 | 已完成 | `LoginView.vue` 已按 `00-71` 收口，不再作为本轮主变量 |
| 视觉壳层 | 已完成首轮 | `AdminLayout / AdminSidebar / AdminTopbar / OverviewView` 已按 `_-_1.html` 收口 |
| 主导航投影 | 已完成 | `adminSidebarMenus` 已只保留两类导航，且已被 `AdminSidebar` 真正消费 |
| 原始菜单库存 | 已分层保留 | `adminMenus` 继续作为能力库存保留，`adminSidebarMenus` 作为主导航投影 |
| 路由库存 | 已完成首轮收口 | `router/index.ts` 已标记 `mainline / tooling / retire-candidate`，并清理已核销候删页 |
| 页面语义分层 | 已固化首轮 | `route-audit-matrix.md` 已明确主架构保留、tooling 保留与已退场域 |

## 4. 目标信息架构

### 4.1 登录前

- `/login`
- 仅做入口与鉴权承接
- 已由 `00-71` 完成，`00-72` 只做回归一致性约束

### 4.2 登录后主架构

#### A. 控制台 / 渠道分析

- 主承接页：`/dashboard/index`
- 角色：当前阶段唯一可见的分析中枢
- 边界：
  - 内部可以展示分享渠道、来源、回访、转化、风格点击等分析区块
  - 但不新增独立 `analytics` 路由

#### B. 用户中心

- 当前主承接页：
  - `/content/share-cards`
  - `/content/contact-requests`
- 表达方式：
  - 分享卡治理
  - 联系方式申请
- 当前阶段不新增独立“平台用户列表 / 用户详情”新路由；若未来补齐真实能力，另起 Spec 进入主架构

## 5. 页面分类矩阵

### 5.1 主架构保留项

| 路由 | 页面 | 分类原因 | 导航暴露 |
|------|------|----------|----------|
| `/dashboard/index` | `OverviewView.vue` | 当前阶段控制台 / 渠道分析主入口 | 主导航 |
| `/content/share-cards` | `ShareCardsView.vue` | 当前阶段最接近“用户已创建分享卡片”的真实能力 | 主导航 |
| `/content/contact-requests` | `ContactRequestsView.vue` | 当前阶段最接近“用户相关联系治理”的真实能力 | 主导航 |

### 5.2 tooling 保留项

| 域 | 当前页面 | 保留原因 | 导航暴露 |
|----|----------|----------|----------|
| `verify` | `Pending` | 历史回看已回收到同页状态筛选，待审治理页仍需保留 | 不进入主导航 |
| `referral` | `Records / Risk / Policies / Eligibility` | 历史治理页与迁移期工具 | 不进入主导航 |
| `recruit` | `Projects / Roles / Applies` | 当前仍是招募治理工具，但授权仍保留 `system/admin-users` fallback，属于兼容过渡 tooling | 不进入主导航 |
| `payment` | `Orders` | 订单治理仍被 dashboard `recentItems` 引用，流水回看已收回订单详情 | 不进入主导航 |
| `refund` | `Orders` | 退款治理仍被 dashboard `recentItems` 引用，日志回看已收回退款详情 | 不进入主导航 |
| `content/templates` | `TemplatesView.vue` | 当前分享卡模板的 `sceneKey / 门槛 / theme / artifact` runtime 配置仍由该页治理 | 不进入主导航 |
| `content/default-general-card` | `DefaultGeneralCardView.vue` | 默认普通卡策略摘要、单用户检查与补偿仍由该页治理 | 不进入主导航 |
| `system/*` | `AI 简历治理 / 后台账号 / 角色 / 日志` | 属于长期后台治理工具：分别承接 AI 失败治理、后台账号、角色权限矩阵与操作审计 | 不进入主导航 |

### 5.3 删除候选项

当前登录后 direct route 里，已无仍保留的删除候选页。

已完成物理退场的历史候删项包括：

- `membership/*`
- `verify/history`
- `payment/transactions`
- `refund/logs`

若后续出现新的候删对象，仍按“先做依赖审计、再做物理删除”的口径逐项核销。

## 6. 菜单与路由策略

### 6.1 菜单源分层

建议把后台菜单事实源拆成两层：

1. **能力库存层**
   - 当前对应 `adminMenus`
   - 记录真实存在的页面能力和权限
2. **主导航投影层**
   - 当前对应 `adminSidebarMenus`
   - 只负责当前阶段用户可见主架构

约束：

- 主导航不再直接读取原始全量菜单库存
- 原始库存只作为能力登记和隐藏治理路由来源
- 当前 `adminMenus` 里的 `recruit` 顶级分组未设置 `menuPermission`，因此 `menu.recruit` 不参与现有 runtime 菜单 gating；招募 readiness 应以真实页面 / 动作权限为准

### 6.2 路由分层

路由暂不一次性删除，但需要在实现阶段补齐显式分类：

- `mainline`
- `tooling`
- `retire-candidate`

这层分类至少要能服务于：

- 左侧主导航投影
- dashboard 快捷入口过滤
- 后续删除审计

### 6.3 Dashboard 入口策略

`OverviewView` 中的功能快捷入口、最近事项和说明文案必须遵循：

- 只把主架构页面作为默认正式入口
- 对兼容保留治理页，若仍需保留跳转，则必须显式标为治理工具或迁移工具

### 6.4 tooling 语义策略

- `tooling` 不是单指“兼容残留页”
- 当前后台 tooling 同时包含两类对象：
  - 长期治理工具：
    - `system/*`
    - `content/templates`
    - `content/default-general-card`
  - 兼容过渡工具：
    - `verify/*`
    - `referral/*`
    - `payment/orders`
    - `refund/orders`
    - `recruit/*`
- 因此顶部语义、路由标题与说明文案应统一使用更宽泛的“治理工具”表达，避免把长期保留页误写成纯兼容页
- 对仍保留 fallback 的过渡工具页，页面内还应补显式提示，避免操作者误以为当前角色已完成独立权限切换
- 对 `recruit/*`，还需要额外避免把历史 `menu.recruit` 误当成 runtime 必需项；矩阵、权限包和提示文案都应以 `page.recruit.*` / `action.recruit.*` 为准
- 招募矩阵若继续承担 fallback 退场判定，页面 fallback / 动作 fallback 的统计应优先由后端 DTO 直接产出，而不是仅由前端按行数据二次推导
- 在 page/action fallback 计数之上，还应补 `canRetirePageFallback / canRetireActionFallback` 这类后端双 gating 信号，让前端直接判断“可先退哪一层”，而不是继续自行解释计数
- 当 `canRetireActionFallback = true` 时，应优先先退动作 fallback：
  - 后端状态处置接口不再接受 `page.system.admin-users` 作为动作兜底
  - 前端状态处置按钮也不再携带 `page.system.admin-users` fallback
- 页面 fallback 是否退场仍单独由 `canRetirePageFallback` 决定，不应在动作 fallback 退场时被一并移除
- 由于招募矩阵 summary 接口本身受 `page.system.roles` 保护，不能作为所有 admin 的前端统一 gating 事实源
- 因此 page/action fallback 的全局开关应继续下沉到 `/admin/auth/me` 会话信息里，让：
  - 菜单过滤
  - 路由守卫
  - landing path
  - 招募页按钮与提示
  共享同一份会话级 gating 信号
- 当 `allowLegacyRecruitPageFallback = false` 时，应继续把页面 fallback 推进到真实退场：
  - 前端菜单 / 路由守卫 / landing path 不再承认 `page.system.admin-users` 对 `page.recruit.*` 的兜底
  - 后端 `GET /admin/recruit/*` 也不再接受 `page.system.admin-users` 作为页面兜底

## 7. 实施顺序

### Phase 1 — 盘点与标注

- 盘点当前登录后全部路由
- 为每个路由标记主架构 / 隐藏治理 / 删除候选
- 产出页面分类矩阵

### Phase 2 — 主导航与语义收口

- 固化 `adminSidebarMenus` 的主导航职责
- 清理 dashboard / topbar / breadcrumb 中仍残留的旧多业务域语义
- 确保当前可见后台始终表达为“控制台 / 渠道分析 + 用户中心”

### Phase 3 — 兼容页降级与删除准备

- 让旧业务域退出主导航
- 保留 direct route + permission guard
- 对无依赖页面进入删除审计队列

## 8. 验证方式

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`
- 路由扫描：确认登录后主导航只暴露两类顶层语义
- 页面抽检：确认 dashboard / share-cards / contact-requests 的标题、面包屑和快捷入口不再混入旧多业务域表达
- 兼容验证：隐藏治理页 direct route 仍受既有权限守卫控制

## 9. 风险控制

- 不允许把“当前只剩两类主导航”误解成“现在就删除全部旧页面”
- 不允许把 `system/admin-users` 等后台账号治理页误判为用户中心
- 不允许因为参考稿里出现 `analytics / users / templates / settings` 等词，就新增对应正式业务域
- 不允许在没有依赖审计前大面积物理删除旧路由与页面
