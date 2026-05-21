# 00-110 设计说明

## 1. 设计目标

`00-110` 不是删除实现 spec，而是删除前的独立审计 spec，目标分成两块：

1. **legacy inventory audit**
   - 正式 8 页之外还保留了哪些运行态能力
   - 哪些是隐藏治理页
   - 哪些是候删文件
   - 哪些仍依赖 fallback
2. **formal page runtime binding audit**
   - 正式 8 页各自连接了哪些真实后端事实源
   - 哪些页只是复用已有聚合接口
   - 哪些页已接接口但事实源异常

## 2. 已核实事实

### 2.1 正式侧栏与 full capability inventory 已分离

从：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`

已确认：

- `adminMenus` 仍是 full capability inventory
- `adminSidebarMenus` 才是 reference-driven 的正式 8 页导航投影

这说明“旧功能没有出现在正式导航”不等于“旧能力已经删除”。

### 2.2 router 仍保留大量隐藏 tooling 路由

从：

- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`

已确认仍保留：

- verify
- referral
- recruit
- payment
- refund
- content/default-general-card
- system/admin-users
- system/roles
- system/ai-resume-governance
- system/operation-logs

这些当前属于隐藏治理页或迁移期兼容入口。

### 2.3 仓内仍存在疑似未引用文件

从当前 `rg` 核查已确认未命中引用的候选包括：

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\referral\ReferralRiskView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\shared\PlaceholderView.vue`

但它们还不能直接删除，因为还缺“运行路由 / 动态引用 / 文档依赖”最终核销。

### 2.4 fallback 仍是当前运行态的一部分

从：

- `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\utils\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\ProjectsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\RolesView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\AppliesView.vue`

已确认：

- 当前仍存在权限 fallback / 兼容授权模式
- 因此删除旧代码不能先于 fallback 依赖核销

## 3. 审计策略

### 3.1 四象限分类

本 spec 将所有对象分为：

1. **Formal active**
   - 正式 8 页
2. **Hidden tooling**
   - 不在正式侧栏，但仍是运行态治理入口
3. **Compat fallback**
   - 仍被权限兼容或迁移逻辑使用
4. **Retire candidate**
   - 当前未发现运行引用、仅剩历史壳层价值的候删对象

### 3.2 后端绑定矩阵

本 spec 将为正式 8 页补一张矩阵，字段至少包含：

- 页面路径
- 前端容器文件
- 前端 API 装配文件
- 真实后端接口
- 后端 controller 证据
- 当前状态：
  - 已接真实后端
  - 已接但事实源异常
  - 聚合复用

### 3.3 删除前门禁

后续任何真实删除动作都必须先满足：

- 不在正式侧栏
- 不在 router 运行路径
- 不在 adminMenus 的隐藏治理入口
- 无 fallback 依赖
- 无 import / 动态 import / 文档依赖

否则只能保留或继续隐藏，不能直接删。

## 4. 风险与边界

### 4.1 已确认

- 当前阶段最合理的是先做审计 spec，而不是直接删代码
- 旧代码未删除并不自动表示方向错误，很多是迁移期治理资产

### 4.2 待验证

- 哪些候删文件确实完全没有动态引用
- 哪些 fallback 仍有运行态价值
- 哪些隐藏治理页未来应该保留，哪些应彻底退场

因此本轮只做建档与分类，不做删除实现。
