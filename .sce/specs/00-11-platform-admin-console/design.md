# 平台后台管理端 - 技术设计

_Requirements: 00-11 全部_

## 1. 设计目标

00-11 负责定义平台后台管理端本身，而不是重复定义后端数据库蓝图。

本 Spec 主要回答三个问题：

1. 后台 Web 应该有哪些页面和菜单
2. 每个后台页面负责什么，不负责什么
3. 后台前端如何与 `/api/admin/**` 接口和权限模型对接

## 2. 总体形态

```text
平台后台 Web
  -> 登录页
  -> 主框架 Layout
  -> 左侧菜单 + 顶部用户区 + 内容区
  -> /api/admin/**
```

### 2.1 技术形态建议

- 单独工程，例如 `kaipai-admin`
- 建议技术栈：Vue 3 + TypeScript + Vite
- 建议 UI 组件：Element Plus 或 Naive UI
- 路由按后台业务模块拆分
- 登录态与菜单权限在后台前端统一维护

### 2.2 不采用的形态

- 不放进 `kaipai-frontend`
- 不使用 uni-app 承担后台 Web
- 不在小程序里做运营后台入口

## 3. 路由与菜单信息架构

### 3.1 一级菜单

| 菜单 | 路由前缀 | 目标 |
|------|----------|------|
| 工作台 | `/dashboard` | 运营总览 |
| 用户中心 | `/users` | 用户查询与状态概览 |
| 实名认证 | `/verify` | 认证审核 |
| 邀请裂变 | `/referral` | 邀请记录、异常、资格、规则 |
| 会员中心 | `/membership` | 产品、权益、会员状态 |
| 订单中心 | `/payment` | 会员支付订单与流水 |
| 退款中心 | `/refund` | 退款审核与执行状态 |
| 页面配置 | `/content` | 模板、主题、分享产物配置 |
| 系统管理 | `/system` | 账号、角色、日志 |

### 3.2 二级页面建议

#### 工作台

- `/dashboard/index`

模块：

- 待审核实名认证卡片
- 待处理异常邀请卡片
- 待审核退款卡片
- 今日订单概览

#### 用户中心

- `/users/index`
- `/users/:id`

详情页展示：

- 基础信息
- 实名状态
- 邀请状态
- 会员状态
- 权益状态
- 最近操作摘要

#### 实名认证

- `/verify/pending`
- `/verify/history`
- `/verify/:id`

详情页动作：

- 审核通过
- 审核拒绝

#### 邀请裂变

- `/referral/records`
- `/referral/risk`
- `/referral/policies`
- `/referral/eligibility`

职责拆分：

- 记录页只看关系与统计
- 风控页只处理异常邀请
- 规则页只处理配置
- 资格页只处理人工发放与撤销

#### 会员中心

- `/membership/products`
- `/membership/benefits`
- `/membership/accounts`
- `/membership/logs`

职责拆分：

- 产品页维护商品与价格
- 权益页维护说明与能力项
- 账户页查看和调整用户会员态
- 日志页追踪会员变更

#### 订单中心

- `/payment/orders`
- `/payment/transactions`

职责：

- 订单页看业务订单
- 流水页看渠道事实

#### 退款中心

- `/refund/orders`
- `/refund/logs`

职责：

- 退款单列表
- 退款详情
- 审核与执行记录

#### 页面配置

- `/content/templates`
- `/content/theme-tokens`
- `/content/share-artifacts`
- `/content/publish-logs`

职责：

- 模板定义
- 主题 token
- 分享卡片 / 海报预设
- 发布记录

#### 系统管理

- `/system/admin-users`
- `/system/roles`
- `/system/operation-logs`

## 4. 页面模式设计

### 4.1 列表页模式

统一结构：

1. 筛选区
2. 表格区
3. 批量操作区（按需）
4. 分页区

适用页面：

- 实名认证列表
- 邀请记录
- 异常邀请
- 会员账户列表
- 支付订单
- 退款单
- 模板列表
- 操作日志

### 4.2 详情页模式

统一结构：

1. 业务摘要卡
2. 关键字段区
3. 状态流转区
4. 操作区
5. 日志区

适用页面：

- 认证详情
- 用户详情
- 退款详情
- 订单详情

### 4.3 配置页模式

统一结构：

1. 当前配置基础信息
2. 配置表单
3. 预览区
4. 草稿 / 发布区

适用页面：

- 会员产品配置
- 邀请规则配置
- 模板配置
- 主题 token 配置

## 5. 权限模型设计

### 5.1 角色基线

| 角色 | 主要权限 |
|------|----------|
| `super_admin` | 全部页面与全部操作 |
| `verify_operator` | 认证审核相关页面与操作 |
| `referral_operator` | 邀请记录、异常审核、资格发放 |
| `membership_operator` | 会员产品、会员状态、权益配置 |
| `finance_operator` | 支付订单、退款审核与执行 |
| `content_operator` | 模板、主题、分享产物配置与发布 |

### 5.2 权限拆分

建议拆成三层：

- `menu:*` 菜单可见
- `page:*` 页面访问
- `action:*` 明确操作权限

示例：

- `menu.verify`
- `page.verify.pending`
- `action.verify.approve`
- `action.verify.reject`

### 5.3 高风险操作

以下操作必须单独授权并记录日志：

- 实名认证通过 / 拒绝
- 邀请资格发放 / 撤销
- 手工开通会员 / 延期 / 关闭
- 退款审核通过 / 拒绝
- 模板发布 / 回滚

## 6. 状态标签体系

后台应统一状态标签映射，避免各页各自定义：

- 实名认证：未提交 / 待审核 / 已通过 / 已拒绝
- 邀请记录：待生效 / 已生效 / 无效 / 复核中
- 会员状态：未开通 / 生效中 / 已过期 / 已关闭
- 支付订单：待支付 / 已支付 / 已关闭 / 已退款 / 部分退款
- 退款单：待审核 / 审核通过 / 审核拒绝 / 退款中 / 退款成功 / 退款失败
- 模板状态：草稿 / 已发布 / 已停用

## 7. 接口消费原则

### 7.1 查询接口

后台查询优先使用聚合接口，例如：

- `/api/admin/dashboard/overview`
- `/api/admin/users`
- `/api/admin/verify/list`
- `/api/admin/referral/risk/list`
- `/api/admin/membership/accounts`
- `/api/admin/payment/orders`
- `/api/admin/refund/orders`
- `/api/admin/content/templates`

### 7.2 写操作接口

后台写接口必须按动作分开：

- 审核通过
- 审核拒绝
- 发放资格
- 撤销资格
- 发布模板
- 回滚模板

不建议使用“一个大更新接口兼容所有操作”的模式。

## 8. 与 00-10 的关系

- 00-10 负责后端架构与数据库蓝图
- 00-11 负责后台管理端产品结构与页面设计
- 后台前端开发必须服从 00-10 的业务域划分与数据边界

## 9. 实施优先级

```text
P0
  -> 登录与主框架
  -> 实名认证审核
  -> 邀请异常审核
  -> 会员产品与会员账户
  -> 模板配置

P1
  -> 支付订单
  -> 退款审核
  -> 邀请资格发放
  -> 系统权限与操作日志

P2
  -> 工作台统计深化
  -> 发布记录回滚
  -> 更细颗粒度权限
```

## 10. 页面字段矩阵

### 10.1 工作台

`/dashboard/index`

- 筛选字段：时间范围、业务线
- 概览字段：待审核实名认证数、待处理异常邀请数、待审核退款数、今日支付订单数
- 详情摘要：各指标快捷入口、最近处理记录摘要
- 主要动作：进入待办模块、刷新概览

### 10.2 用户中心

`/users/index`

- 筛选字段：用户 ID、手机号、昵称、角色、实名状态、会员状态、邀请状态、资格状态、注册时间
- 列表字段：用户 ID、昵称、手机号、角色、实名状态、会员状态、有效邀请数、资格状态、注册时间、最后活跃时间
- 主要动作：查看详情、导出

`/users/:id`

- 详情字段：基础信息、演员档案摘要、实名状态、邀请状态、会员状态、资格状态、最近订单摘要、最近退款摘要、最近操作日志摘要
- 主要动作：跳转会员账户页、跳转资格管理、跳转实名认证记录、查看操作轨迹

### 10.3 实名认证

`/verify/pending`

- 筛选字段：申请单号、用户 ID、手机号、真实姓名、提交时间范围、状态
- 列表字段：申请单号、用户 ID、昵称/手机号、真实姓名脱敏、提交时间、资料完成度快照、当前状态
- 详情字段：真实姓名、身份证脱敏值、申请时间、资料完成度快照、历史拒绝记录、审核备注区
- 主要动作：查看详情、审核通过、审核拒绝

`/verify/history`

- 筛选字段：申请单号、用户 ID、手机号、状态、审核人、审核时间范围
- 列表字段：申请单号、用户 ID、手机号、状态、审核人、审核时间、拒绝原因摘要
- 主要动作：查看详情

`/verify/:id`

- 详情字段：申请信息、用户信息、实名信息脱敏展示、审核状态流转、审核人、审核时间、拒绝原因、关联日志
- 主要动作：审核通过、审核拒绝、返回列表

### 10.4 邀请裂变

`/referral/records`

- 筛选字段：邀请人用户 ID、邀请码、被邀请人用户 ID、状态、风险标记、注册时间范围、生效时间范围
- 列表字段：记录 ID、邀请人、邀请码、被邀请人、状态、风险标记、注册时间、生效时间
- 详情字段：邀请人信息、被邀请人信息、设备指纹摘要、状态流转、风险原因、资格联动情况
- 主要动作：查看详情、导出

`/referral/risk`

- 筛选字段：邀请码、邀请人 ID、被邀请人 ID、风险原因、状态、注册时间范围
- 列表字段：记录 ID、邀请码、邀请人、被邀请人、风险原因、当前状态、注册时间
- 详情字段：设备指纹、同设备命中情况、同小时邀请码命中次数、历史处理记录
- 主要动作：通过、作废、标记复核完成

`/referral/policies`

- 筛选字段：规则名称、启用状态
- 列表字段：规则名称、是否启用、实名前置、资料完成度门槛、同设备限制、小时频率限制、自动下发开关、更新时间
- 详情字段：规则全量配置、版本备注、修改人、修改时间
- 主要动作：新建、编辑、启用、停用

`/referral/eligibility`

- 筛选字段：用户 ID、手机号、资格类型、资格编码、状态、生效时间范围、过期时间范围、来源类型
- 列表字段：资格记录 ID、用户 ID、资格类型、资格编码、状态、生效时间、过期时间、来源、备注
- 详情字段：资格全量信息、来源单据、关联活动/订单、操作日志
- 主要动作：手工发放、撤销资格、延期资格

### 10.5 会员中心

`/membership/products`

- 筛选字段：产品编码、产品名称、会员层级、状态
- 列表字段：产品 ID、产品编码、产品名称、会员层级、时长、原价、售价、状态、排序、更新时间
- 详情字段：产品基础信息、权益配置表单、适用范围、发布状态
- 主要动作：新建、编辑、启用、停用、排序调整

`/membership/benefits`

- 筛选字段：会员层级、状态
- 列表字段：权益项编码、权益项名称、会员层级、能力说明、状态、更新时间
- 详情字段：权益说明、能力矩阵、影响页面/产物、关联产品
- 主要动作：新建、编辑、启用、停用

`/membership/accounts`

- 筛选字段：用户 ID、手机号、会员层级、会员状态、生效时间范围、过期时间范围、来源类型
- 列表字段：用户 ID、昵称/手机号、当前层级、状态、生效时间、过期时间、来源、最近变更时间
- 详情字段：当前会员账户、会员来源、关联支付单、关联资格、变更记录摘要
- 主要动作：手工开通、延期、关闭、查看日志

`/membership/logs`

- 筛选字段：用户 ID、变更原因、来源类型、时间范围
- 列表字段：日志 ID、用户 ID、变更前层级、变更后层级、变更原因、来源类型、操作时间
- 详情字段：变更备注、来源单据、操作者
- 主要动作：查看详情

### 10.6 订单与退款

`/payment/orders`

- 筛选字段：订单号、用户 ID、手机号、产品 ID、支付状态、支付渠道、下单时间范围、支付时间范围
- 列表字段：支付订单 ID、订单号、用户、产品、金额、支付状态、支付渠道、下单时间、支付时间
- 详情字段：订单基础信息、商品信息、支付信息、退款信息摘要、回调摘要
- 主要动作：查看详情、导出

`/payment/transactions`

- 筛选字段：支付订单号、渠道流水号、渠道、状态、回调时间范围
- 列表字段：流水 ID、支付订单号、渠道流水号、渠道、交易类型、金额、状态、回调时间
- 详情字段：原始回调摘要、订单关联信息、异常说明
- 主要动作：查看详情

`/refund/orders`

- 筛选字段：退款单号、支付订单号、用户 ID、审核状态、退款状态、申请时间范围、审核时间范围
- 列表字段：退款单 ID、退款单号、支付订单号、用户、退款金额、审核状态、退款状态、申请时间、审核时间
- 详情字段：退款原因、审核备注、渠道退款单号、退款执行状态、操作日志
- 主要动作：审核通过、审核拒绝、查看详情

`/refund/logs`

- 筛选字段：退款单号、操作人、动作类型、时间范围
- 列表字段：日志 ID、退款单号、操作人、动作类型、备注、操作时间
- 详情字段：动作前后状态、异常回执摘要
- 主要动作：查看详情

### 10.7 页面配置

`/content/templates`

- 筛选字段：模板编码、模板名称、场景、状态、层级要求、会员要求
- 列表字段：模板 ID、模板编码、模板名称、场景、布局、层级要求、会员要求、状态、排序、更新时间
- 详情字段：基础信息、主题配置、分享产物预设、草稿/发布状态、发布记录摘要
- 主要动作：新建、编辑、启用、停用、发布、回滚、排序

`/content/theme-tokens`

- 筛选字段：主题编码、场景、状态
- 列表字段：主题编码、所属模板、场景、主色、强调色、背景色、状态、更新时间
- 详情字段：颜色、字体层级、按钮样式、背景纹理、装饰元素、适用产物
- 主要动作：编辑、预览、发布

`/content/share-artifacts`

- 筛选字段：产物类型、模板、状态
- 列表字段：配置 ID、产物类型、模板、标题规则、摘要规则、封面规则、状态、更新时间
- 详情字段：产物类型、文案模板、图片预设、会员门槛、等级门槛、预览配置
- 主要动作：编辑、预览、发布

`/content/publish-logs`

- 筛选字段：模板 ID、发布版本、动作类型、发布人、时间范围
- 列表字段：发布记录 ID、模板 ID、版本号、动作类型、发布人、发布时间、备注
- 详情字段：配置快照、回滚来源、发布说明
- 主要动作：查看详情、触发回滚

### 10.8 系统管理

`/system/admin-users`

- 筛选字段：账号、姓名、手机号、状态、角色
- 列表字段：账号 ID、账号、姓名、手机号、状态、角色摘要、最后登录时间
- 详情字段：账号信息、角色绑定、最近登录信息、最近操作摘要
- 主要动作：新建、编辑、启用、禁用、重置密码、分配角色

`/system/roles`

- 筛选字段：角色编码、角色名称、状态
- 列表字段：角色 ID、角色编码、角色名称、状态、备注、更新时间
- 详情字段：菜单权限、页面权限、操作权限、高风险权限项
- 主要动作：新建、编辑、启用、停用、复制角色

`/system/operation-logs`

- 筛选字段：操作人、模块、动作、目标类型、请求 ID、结果、时间范围
- 列表字段：日志 ID、操作人、模块、动作、目标类型、目标 ID、结果、操作时间
- 详情字段：请求 ID、IP、操作明细 JSON、前后状态摘要
- 主要动作：查看详情、导出

## 11. 权限矩阵与权限码规范

### 11.1 角色矩阵

| 角色 | 工作台 | 用户中心 | 实名认证 | 邀请裂变 | 会员中心 | 订单中心 | 退款中心 | 页面配置 | 系统管理 |
|------|------|------|------|------|------|------|------|------|------|
| `super_admin` | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| `verify_operator` | R | R | Y |  |  |  |  |  |  |
| `referral_operator` | R | R |  | Y |  |  |  |  |  |
| `membership_operator` | R | R |  |  | Y | R |  |  |  |
| `finance_operator` | R | R |  |  | R | Y | Y |  |  |
| `content_operator` | R |  |  |  |  |  |  | Y |  |

说明：

- `Y` 表示默认具备页面访问与所属动作权限
- `R` 表示默认只读
- 高风险动作仍需单独 `action:*` 权限
- `page.system.ai-resume-governance` 与 `action.system.ai-resume.review`、`action.system.ai-resume.resolve` 归属“系统管理”域，默认不并入 `verify_operator`、`referral_operator`、`membership_operator`、`finance_operator`、`content_operator`
- 若需要日常 AI 治理账号，应通过角色管理页显式分配 AI 独立页面 / 动作权限，不应长期依赖 `page.system.operation-logs` 兼容兜底

### 11.2 高风险动作

- `action.verify.approve`
- `action.verify.reject`
- `action.referral.risk.approve`
- `action.referral.risk.invalidate`
- `action.referral.risk.resolve`
- `action.referral.policy.enable`
- `action.referral.policy.disable`
- `action.referral.eligibility.grant`
- `action.referral.eligibility.revoke`
- `action.referral.eligibility.extend`
- `action.membership.account.open`
- `action.membership.account.extend`
- `action.membership.account.close`
- `action.membership.product.enable`
- `action.membership.product.disable`
- `action.refund.approve`
- `action.refund.reject`
- `action.content.template.enable`
- `action.content.template.disable`
- `action.content.template.publish`
- `action.content.template.rollback`
- `action.content.theme.publish`
- `action.content.artifact.publish`
- `action.system.admin-user.enable`
- `action.system.admin-user.disable`
- `action.system.admin-user.reset-password`
- `action.system.admin-user.bind-roles`
- `action.system.ai-resume.review`
- `action.system.ai-resume.resolve`
- `action.system.role.edit`
- `action.system.role.enable`
- `action.system.role.disable`

### 11.3 权限码规则

建议严格拆为三层：

- 菜单权限：`menu.{module}`
- 页面权限：`page.{module}.{page}`
- 操作权限：`action.{module}.{resource}.{verb}`

命名约束：

1. `module` 统一使用后台一级业务域
2. `page` 使用页面业务语义，不直接拼技术路由
3. `resource` 使用实体或业务对象名称
4. `verb` 使用明确动作，不使用含糊词如 `do`、`update`
5. 高风险动作不得复用普通编辑权限

示例：

- `menu.verify`
- `menu.referral`
- `page.verify.pending`
- `page.membership.products`
- `page.content.templates`
- `action.verify.approve`
- `action.referral.eligibility.grant`
- `action.membership.account.extend`
- `action.refund.reject`
- `action.content.template.publish`

## 12. 后台查询 / 写操作接口清单最终版

说明：

- 后台接口统一走 `/api/admin/**`
- 查询接口优先返回页面所需聚合结构，不让后台前端拼多个单表接口
- 写接口按动作拆分，不使用“大而全 update 接口”

### 12.1 工作台

`/dashboard/index`

- 查询接口：`GET /api/admin/dashboard/overview`
- 写接口：无
- 请求参数摘要：`dateFrom`、`dateTo`、`bizLine?`
- 返回结构摘要：
  - `verifyPendingCount`
  - `referralRiskPendingCount`
  - `refundPendingCount`
  - `todayPaymentOrderCount`
  - `recentItems[]`
- 聚合要求：必须聚合认证、邀请、退款、支付四个域

### 12.2 用户中心

`/users/index`

- 查询接口：`GET /api/admin/users`
- 写接口：无
- 请求参数摘要：
  - `userId?`
  - `phone?`
  - `nickname?`
  - `role?`
  - `realAuthStatus?`
  - `membershipStatus?`
  - `referralStatus?`
  - `entitlementStatus?`
  - `pageNo`
  - `pageSize`
- 返回结构摘要：
  - `list[]`
    - `userId`
    - `nickname`
    - `phone`
    - `role`
    - `realAuthStatus`
    - `membershipTier`
    - `validInviteCount`
    - `entitlementSummary`
    - `registeredAt`
    - `lastActiveAt`
  - `total`

`/users/:id`

- 查询接口：`GET /api/admin/users/{id}`
- 写接口：无
- 请求参数摘要：路径参数 `id`
- 返回结构摘要：
  - `userInfo`
  - `actorProfileSummary`
  - `verifySummary`
  - `referralSummary`
  - `membershipSummary`
  - `entitlementSummary`
  - `paymentSummary`
  - `refundSummary`
  - `recentOperationLogs[]`
- 聚合要求：必须为聚合接口

### 12.3 实名认证

`/verify/pending`

- 查询接口：`GET /api/admin/verify/list`
- 写接口：
  - `POST /api/admin/verify/{id}/approve`
  - `POST /api/admin/verify/{id}/reject`
- 请求参数摘要：
  - 查询：`verificationId?`、`userId?`、`phone?`、`realName?`、`status=pending`、`submitDateFrom?`、`submitDateTo?`、`pageNo`、`pageSize`
  - 通过：路径参数 `id`，Body 可含 `remark?`
  - 拒绝：路径参数 `id`，Body `rejectReason`
- 返回结构摘要：
  - 查询：`list[]` 含申请摘要字段 + `total`
  - 详情：`verificationInfo`、`userInfo`、`historyRejects[]`
  - 写操作：`success`、`updatedStatus`

`/verify/history`

- 查询接口：`GET /api/admin/verify/list`
- 写接口：无
- 请求参数摘要：`verificationId?`、`userId?`、`phone?`、`status?`、`reviewerId?`、`reviewDateFrom?`、`reviewDateTo?`、`pageNo`、`pageSize`
- 返回结构摘要：`list[]`、`total`

`/verify/:id`

- 查询接口：`GET /api/admin/verify/{id}`
- 写接口：
  - `POST /api/admin/verify/{id}/approve`
  - `POST /api/admin/verify/{id}/reject`
- 请求参数摘要：路径参数 `id`
- 返回结构摘要：
  - `verificationInfo`
  - `userInfo`
  - `maskedIdentityInfo`
  - `reviewFlow`
  - `operationLogs[]`

### 12.4 邀请裂变

`/referral/records`

- 查询接口：
  - `GET /api/admin/referral/records`
  - `GET /api/admin/referral/records/{id}`
- 写接口：无
- 请求参数摘要：
  - `inviterUserId?`
  - `inviteCode?`
  - `inviteeUserId?`
  - `status?`
  - `riskFlag?`
  - `registeredAtFrom?`
  - `registeredAtTo?`
  - `validatedAtFrom?`
  - `validatedAtTo?`
  - `pageNo`
  - `pageSize`
- 返回结构摘要：
  - 列表：`list[]`、`total`
  - 详情：`recordInfo`、`inviterInfo`、`inviteeInfo`、`riskInfo`

`/referral/risk`

- 查询接口：
  - `GET /api/admin/referral/risk/list`
  - `GET /api/admin/referral/risk/{id}`
- 写接口：
  - `POST /api/admin/referral/risk/{id}/approve`
  - `POST /api/admin/referral/risk/{id}/invalidate`
  - `POST /api/admin/referral/risk/{id}/resolve`
- 请求参数摘要：
  - 查询：`inviteCode?`、`inviterUserId?`、`inviteeUserId?`、`riskReason?`、`status?`、`registeredAtFrom?`、`registeredAtTo?`、`pageNo`、`pageSize`
  - 写：路径参数 `id`，Body `remark?`
- 返回结构摘要：
  - 列表：风险记录摘要
  - 详情：`recordInfo`、`deviceHitSummary`、`sameHourHitSummary`、`historyLogs[]`

`/referral/policies`

- 查询接口：
  - `GET /api/admin/referral/policies`
  - `GET /api/admin/referral/policies/{id}`
- 写接口：
  - `POST /api/admin/referral/policies`
  - `PUT /api/admin/referral/policies/{id}`
  - `POST /api/admin/referral/policies/{id}/enable`
  - `POST /api/admin/referral/policies/{id}/disable`
- 请求参数摘要：
  - 查询：`policyName?`、`enabled?`
  - 写：`policyName`、`enabled`、`requireRealAuth`、`requireProfileCompletion`、`profileCompletionThreshold`、`sameDeviceLimit`、`hourlyInviteLimit`、`autoGrantEnabled`、`grantRuleJson`
- 返回结构摘要：
  - `policyInfo`
  - `versionInfo`

`/referral/eligibility`

- 查询接口：
  - `GET /api/admin/referral/eligibility`
  - `GET /api/admin/referral/eligibility/{grantId}`
- 写接口：
  - `POST /api/admin/referral/eligibility/grant`
  - `POST /api/admin/referral/eligibility/revoke`
  - `POST /api/admin/referral/eligibility/extend`
- 请求参数摘要：
  - 查询：`userId?`、`phone?`、`grantType?`、`grantCode?`、`status?`、`sourceType?`、`effectiveFrom?`、`effectiveTo?`、`expireFrom?`、`expireTo?`、`pageNo`、`pageSize`
  - 发放：`userId`、`grantType`、`grantCode`、`effectiveTime?`、`expireTime?`、`remark?`
  - 撤销：`grantId`、`remark`
  - 延期：`grantId`、`expireTime`、`remark?`
- 返回结构摘要：
  - `grantInfo`
  - `operatorLogSummary`

### 12.5 会员中心

`/membership/products`

- 查询接口：
  - `GET /api/admin/membership/products`
  - `GET /api/admin/membership/products/{id}`
- 写接口：
  - `POST /api/admin/membership/products`
  - `PUT /api/admin/membership/products/{id}`
  - `POST /api/admin/membership/products/{id}/enable`
  - `POST /api/admin/membership/products/{id}/disable`
  - `POST /api/admin/membership/products/{id}/sort`
- 请求参数摘要：
  - 查询：`productCode?`、`productName?`、`membershipTier?`、`status?`
  - 写：`productCode`、`productName`、`membershipTier`、`durationDays`、`listPrice`、`salePrice`、`benefitConfigJson`、`status`、`sortNo`
- 返回结构摘要：
  - 列表：产品摘要
  - 详情：产品基础信息 + 权益配置

`/membership/benefits`

- 查询接口：`GET /api/admin/membership/benefits`
- 写接口：
  - `POST /api/admin/membership/benefits`
  - `PUT /api/admin/membership/benefits/{id}`
- 请求参数摘要：`membershipTier?`、`status?`
- 返回结构摘要：
  - `benefitItems[]`
  - `capabilityMatrix`
- 聚合要求：可依附产品与能力配置聚合返回

`/membership/accounts`

- 查询接口：
  - `GET /api/admin/membership/accounts`
  - `GET /api/admin/membership/accounts/{userId}`
- 写接口：
  - `POST /api/admin/membership/accounts/{userId}/open`
  - `POST /api/admin/membership/accounts/{userId}/extend`
  - `POST /api/admin/membership/accounts/{userId}/close`
- 请求参数摘要：
  - 查询：`userId?`、`phone?`、`tier?`、`status?`、`effectiveFrom?`、`effectiveTo?`、`expireFrom?`、`expireTo?`、`sourceType?`、`pageNo`、`pageSize`
  - 开通：`tier`、`effectiveTime`、`expireTime`、`sourceType`、`remark?`
  - 延期：`expireTime`、`remark?`
  - 关闭：`remark`
- 返回结构摘要：
  - 列表：账户摘要
  - 详情：`accountInfo`、`changeLogs[]`、`relatedPaymentOrders[]`、`relatedEntitlements[]`
- 聚合要求：详情必须聚合

`/membership/logs`

- 查询接口：`GET /api/admin/membership/logs`
- 写接口：无
- 请求参数摘要：`userId?`、`changeReason?`、`sourceType?`、`dateFrom?`、`dateTo?`、`pageNo`、`pageSize`
- 返回结构摘要：`list[]`、`total`

### 12.6 订单中心

`/payment/orders`

- 查询接口：
  - `GET /api/admin/payment/orders`
  - `GET /api/admin/payment/orders/{id}`
- 写接口：无
- 请求参数摘要：`orderNo?`、`userId?`、`phone?`、`productId?`、`payStatus?`、`payChannel?`、`createdAtFrom?`、`createdAtTo?`、`paidAtFrom?`、`paidAtTo?`、`pageNo`、`pageSize`
- 返回结构摘要：
  - 列表：订单摘要
  - 详情：`orderInfo`、`productInfo`、`paymentInfo`、`refundSummary`

`/payment/transactions`

- 查询接口：
  - `GET /api/admin/payment/transactions`
  - `GET /api/admin/payment/transactions/{id}`
- 写接口：无
- 请求参数摘要：`paymentOrderNo?`、`channelTradeNo?`、`channel?`、`status?`、`callbackFrom?`、`callbackTo?`、`pageNo`、`pageSize`
- 返回结构摘要：
  - 列表：交易摘要
  - 详情：`transactionInfo`、`callbackPayloadSummary`

### 12.7 退款中心

`/refund/orders`

- 查询接口：
  - `GET /api/admin/refund/orders`
  - `GET /api/admin/refund/orders/{id}`
- 写接口：
  - `POST /api/admin/refund/{id}/approve`
  - `POST /api/admin/refund/{id}/reject`
- 请求参数摘要：
  - 查询：`refundNo?`、`paymentOrderNo?`、`userId?`、`auditStatus?`、`refundStatus?`、`createdAtFrom?`、`createdAtTo?`、`auditedAtFrom?`、`auditedAtTo?`、`pageNo`、`pageSize`
  - 审核通过：路径参数 `id`，Body `auditRemark?`
  - 审核拒绝：路径参数 `id`，Body `auditRemark`
- 返回结构摘要：
  - 列表：退款单摘要
  - 详情：`refundInfo`、`paymentOrderInfo`、`operateLogs[]`
- 聚合要求：详情必须聚合退款单、支付单、日志

`/refund/logs`

- 查询接口：`GET /api/admin/refund/logs`
- 写接口：无
- 请求参数摘要：`refundNo?`、`operatorId?`、`actionType?`、`dateFrom?`、`dateTo?`、`pageNo`、`pageSize`
- 返回结构摘要：`list[]`、`total`

### 12.8 页面配置

`/content/templates`

- 查询接口：
  - `GET /api/admin/content/templates`
  - `GET /api/admin/content/templates/{id}`
- 写接口：
  - `POST /api/admin/content/templates`
  - `PUT /api/admin/content/templates/{id}`
  - `POST /api/admin/content/templates/{id}/enable`
  - `POST /api/admin/content/templates/{id}/disable`
  - `POST /api/admin/content/templates/{id}/publish`
  - `POST /api/admin/content/templates/{id}/rollback`
  - `POST /api/admin/content/templates/{id}/sort`
- 请求参数摘要：
  - 查询：`templateCode?`、`templateName?`、`sceneKey?`、`status?`、`requiredLevel?`、`membershipRequired?`
  - 写：`templateCode`、`templateName`、`sceneKey`、`layoutVariant`、`requiredLevel`、`membershipRequired`、`baseThemeJson`、`artifactPresetJson`、`status`、`sortNo`
- 返回结构摘要：
  - 列表：模板摘要
  - 详情：`templateInfo`、`draftInfo`、`publishInfo`、`publishLogs[]`
- 聚合要求：详情必须聚合模板与发布记录

`/content/theme-tokens`

- 查询接口：`GET /api/admin/content/theme-tokens`
- 写接口：`PUT /api/admin/content/theme-tokens/{templateId}`
- 请求参数摘要：`themeCode?`、`sceneKey?`、`status?`
- 返回结构摘要：
  - `list[]`
  - `themeTokenDetail`
- 说明：当前收口在 `card_scene_template.base_theme_json`

`/content/share-artifacts`

- 查询接口：`GET /api/admin/content/share-artifacts`
- 写接口：`PUT /api/admin/content/share-artifacts/{templateId}`
- 请求参数摘要：`artifactType?`、`templateId?`、`status?`
- 返回结构摘要：
  - `list[]`
  - `artifactConfigDetail`
- 说明：当前收口在 `card_scene_template.artifact_preset_json`

`/content/publish-logs`

- 查询接口：`GET /api/admin/content/publish-logs`
- 写接口：`POST /api/admin/content/templates/{id}/rollback`
- 请求参数摘要：`templateId?`、`publishVersion?`、`actionType?`、`publishedBy?`、`publishedAtFrom?`、`publishedAtTo?`、`pageNo`、`pageSize`
- 返回结构摘要：`list[]`、`total`

### 12.9 系统管理

`/system/admin-users`

- 查询接口：
  - `GET /api/admin/system/admin-users`
  - `GET /api/admin/system/admin-users/{id}`
- 写接口：
  - `POST /api/admin/system/admin-users`
  - `PUT /api/admin/system/admin-users/{id}`
  - `POST /api/admin/system/admin-users/{id}/enable`
  - `POST /api/admin/system/admin-users/{id}/disable`
  - `POST /api/admin/system/admin-users/{id}/reset-password`
  - `POST /api/admin/system/admin-users/{id}/bind-roles`
- 请求参数摘要：`account?`、`userName?`、`phone?`、`status?`、`roleCode?`、`pageNo`、`pageSize`
- 返回结构摘要：
  - 列表：账号摘要
  - 详情：`adminUserInfo`、`roleBindings[]`、`recentOperationLogs[]`

`/system/roles`

- 查询接口：
  - `GET /api/admin/system/roles`
  - `GET /api/admin/system/roles/{id}`
  - `GET /api/admin/system/roles/ai-governance-matrix`
- 写接口：
  - `POST /api/admin/system/roles`
  - `PUT /api/admin/system/roles/{id}`
  - `POST /api/admin/system/roles/{id}/enable`
  - `POST /api/admin/system/roles/{id}/disable`
- 请求参数摘要：`roleCode?`、`roleName?`、`status?`
- 返回结构摘要：
  - 列表：角色摘要
  - 详情：`roleInfo`、`menuPermissions[]`、`pagePermissions[]`、`actionPermissions[]`
  - AI 授权矩阵：`enabledRoleCount`、`fallbackRoleCount`、`fallbackBoundUserCount`、`canRetireFallback`、`roles[]`

`/system/ai-resume-governance`

- 查询接口：
  - `GET /api/admin/ai/resume/overview`
  - `GET /api/admin/ai/resume/histories`
  - `GET /api/admin/ai/resume/histories/{historyId}`
  - `GET /api/admin/ai/resume/failures`
  - `GET /api/admin/ai/resume/sensitive-hits`
- 写接口：
  - `POST /api/admin/ai/resume/failures/{failureId}/review`
  - `POST /api/admin/ai/resume/failures/{failureId}/suggest-retry`
- 请求参数摘要：
  - 列表：`userId?`、`realAuthStatus?`、`status?`、`keyword?`、`requestId?`、`pageNo`、`pageSize`
  - 写动作：`reason`
- 返回结构摘要：
  - 概览：`quotaOverview`、`topUsers[]`
  - 历史：`histories[]`、`historyDetail`
  - 样本：`failures[]`、`sensitiveHits[]`
  - 审计：可按 `ai_resume_review`、`ai_resume_suggest_retry` 回看最近治理动作
- 权限摘要：
  - 页面：`page.system.ai-resume-governance`
  - 动作：`action.system.ai-resume.review`、`action.system.ai-resume.resolve`
  - 兼容：当前允许 `page.system.operation-logs` 作为过渡兜底，但只用于存量角色迁移，不应继续作为新角色授权主口径

`/system/operation-logs`

- 查询接口：`GET /api/admin/system/operation-logs`
- 写接口：无
- 请求参数摘要：`adminUserId?`、`moduleCode?`、`operationCode?`、`targetType?`、`requestId?`、`operationResult?`、`dateFrom?`、`dateTo?`、`pageNo`、`pageSize`
- 返回结构摘要：`list[]`、`total`

### 12.10 必须优先合并成聚合接口的页面

以下页面必须优先使用聚合接口，而不是后台前端自己拼装：

1. 工作台 `GET /api/admin/dashboard/overview`
2. 用户详情 `GET /api/admin/users/{id}`
3. 会员账户详情 `GET /api/admin/membership/accounts/{userId}`
4. 退款详情 `GET /api/admin/refund/orders/{id}`
5. 模板详情 `GET /api/admin/content/templates/{id}`

原因：

- 页面天然跨多张表
- 状态口径必须统一
- 权限判断与操作日志挂载点也必须统一

## 13. 后台前端工程初始化方案

### 13.1 工程形态与目录建议

建议单独创建 `kaipai-admin` 工程，至少包含以下目录：

```text
kaipai-admin
├── src
│   ├── api
│   │   ├── dashboard.ts
│   │   ├── verify.ts
│   │   ├── referral.ts
│   │   ├── membership.ts
│   │   ├── payment.ts
│   │   ├── refund.ts
│   │   ├── content.ts
│   │   └── system.ts
│   ├── router
│   │   ├── static-routes.ts
│   │   ├── async-routes.ts
│   │   └── guard.ts
│   ├── layouts
│   │   └── AdminLayout.vue
│   ├── views
│   │   ├── dashboard
│   │   ├── users
│   │   ├── verify
│   │   ├── referral
│   │   ├── membership
│   │   ├── payment
│   │   ├── refund
│   │   ├── content
│   │   └── system
│   ├── stores
│   │   ├── auth.ts
│   │   ├── permission.ts
│   │   └── app.ts
│   ├── components
│   │   ├── business
│   │   ├── tables
│   │   ├── forms
│   │   └── dialogs
│   ├── constants
│   ├── utils
│   ├── styles
│   │   ├── tokens.css
│   │   └── index.scss
│   ├── types
│   └── main.ts
├── .env.development
├── .env.test
├── .env.production
├── package.json
├── tsconfig.json
└── vite.config.ts
```

目录约束：

- `api/*` 按后台一级业务域拆分，不允许多个页面重复手写相同请求
- `views/*` 按路由模块拆分，页面内部只消费本模块的查询与写接口
- `components/business/*` 承载跨页面复用的业务组件，不承载页面私有逻辑
- `stores/*` 只维护登录态、权限、全局 UI 状态，不把页面筛选条件塞进全局

### 13.2 初始化基线

推荐初始化清单：

1. `Vue 3 + TypeScript + Vite`
2. `Vue Router` 负责静态路由与权限路由装配
3. `Pinia` 负责登录态、权限、菜单与全局配置
4. `Axios` 或统一请求层负责鉴权头、错误码、重试与下载
5. `ESLint + Prettier` 统一工程格式
6. `Stylelint` 约束后台样式 token 与页面壳层命名

工程初始化时必须同步建立：

- `.env.*` 区分开发、测试、生产 API 地址
- `src/constants/permission.ts` 统一维护权限码常量
- `src/constants/status.ts` 统一维护后台状态标签映射
- `src/router/guard.ts` 统一维护登录校验、403 跳转、标题装配

### 13.3 工程约束

- 后台前端只允许消费 `/api/admin/**`，不得直接混用小程序前台接口
- 页面筛选 DTO、表格返回 DTO、写接口 DTO 应分开建类型，避免一个类型兼容全部场景
- 所有导出、批量操作、高风险写操作都必须经过统一请求封装与权限指令
- 状态展示、按钮显隐、字段脱敏必须走公共工具，不允许页面内各自写一套判断

## 14. 主框架 Layout、路由骨架与菜单装配方案

### 14.1 静态路由与动态路由

静态路由最小集合：

- `/login`
- `/403`
- `/404`
- `/redirect`

动态路由按后台一级模块拆分：

- `/dashboard/**`
- `/users/**`
- `/verify/**`
- `/referral/**`
- `/membership/**`
- `/payment/**`
- `/refund/**`
- `/content/**`
- `/system/**`

约束：

- 路由 `meta` 至少包含 `title`、`menuCode`、`pageCode`、`keepAlive?`
- 动态路由装配以权限码过滤为准，不以页面名称字符串判断
- 无页面权限时，前端应直接剔除对应菜单与路由，不展示“点击后才 403”的死入口

### 14.2 Layout 壳层

主框架建议固定为：

1. 左侧菜单区
2. 顶部栏
3. 面包屑区
4. 内容区
5. 全局抽屉 / 对话框挂载区

布局要求：

- 左侧菜单承载一级菜单与必要二级入口
- 顶部栏展示当前账号、角色摘要、登出入口
- 内容区统一使用页面容器组件，避免每页各自处理留白、滚动与高度
- 全局抽屉 / 对话框统一挂到 Layout 根部，便于高风险确认框、详情抽屉、JSON 预览复用

### 14.3 登录态与鉴权

后台登录态至少包含：

- `accessToken`
- `refreshToken` 或可续签凭证
- `adminUserInfo`
- `menuPermissions`
- `pagePermissions`
- `actionPermissions`

登录流转建议：

1. 登录成功后一次性拉取账号信息与权限集合
2. 首屏进入 Layout 前完成路由装配
3. 页面刷新时优先恢复本地 token，再补拉当前账号权限
4. 任一接口返回未登录或权限失效时，清空登录态并跳回 `/login`

明确约束：

- 按钮是否可点必须以 `actionPermissions` 判断，不能只看菜单可见
- 敏感字段是否可见必须额外判断权限，不随页面访问权限自动放开

### 14.4 菜单装配

推荐使用“前端维护路由壳，后端返回权限码”的装配方式：

- 前端维护完整路由骨架、页面标题、图标、默认排序
- 后端返回当前账号的 `menu.*`、`page.*`、`action.*` 权限集合
- 前端按权限集合过滤菜单树、路由表与操作按钮

菜单节点最少字段：

- `name`
- `path`
- `icon`
- `menuCode`
- `pageCode`
- `children`
- `hidden`

### 14.5 页面级基础能力

所有后台页面默认接入以下壳层能力：

- 页面标题与面包屑自动装配
- 筛选条件持久化到当前页面，不跨页面污染
- 列表页统一空状态、异常态、加载态
- 高风险写操作统一走确认弹窗
- 详情抽屉 / 详情页统一支持操作日志区块

## 15. 后台 UI 设计规范与组件复用约束

### 15.1 设计方向

后台界面应强调信息密度、稳定性、可审计性，不追求营销型视觉风格。

统一原则：

- 页面骨架统一，减少学习成本
- 状态色、危险色、成功色使用固定 token，不按页面自定义
- 列表、详情、配置三种页面模式必须复用相同的间距、标题层级与操作栏结构

### 15.2 页面模板

建议抽成以下公共容器：

- `PageContainer`：统一标题、说明、内容间距
- `FilterPanel`：统一筛选区布局、收起展开、查询与重置按钮
- `ListTableCard`：统一表格容器、批量区、分页区
- `DetailDrawer`：统一详情抽屉与日志区布局
- `ConfigEditorLayout`：统一配置表单、预览区、发布区三栏结构

### 15.3 业务组件最小集合

建议优先沉淀以下复用组件：

| 组件 | 职责 | 强制要求 |
|------|------|----------|
| `StatusTag` | 统一状态标签文案与颜色 | 状态码映射来自公共常量 |
| `PermissionButton` | 按 `action.*` 控制按钮显隐与禁用 | 不允许页面手写重复权限判断 |
| `AuditConfirmDialog` | 高风险操作二次确认 | 支持备注、拒绝原因、影响提示 |
| `SearchTableLayout` | 列表页筛选 + 表格 + 分页 | 统一 loading、empty、error 展示 |
| `JsonPreviewDialog` | 日志、回调、模板快照查看 | 统一脱敏与复制能力 |
| `PublishDiffPanel` | 模板发布、回滚差异展示 | 必须能展示草稿与线上差异 |

### 15.4 列表、表单、详情约束

- 列表页默认最多展示 8 到 10 个核心字段，超长信息进入详情抽屉
- 操作列固定在右侧，危险操作按钮必须有明显分组
- 拒绝、撤销、关闭、回滚类动作必须要求填写原因或备注
- 身份证、手机号、渠道单号等敏感字段默认脱敏展示，仅在具备权限时展示完整值
- 配置页必须同时提供表单视图与预览视图，不允许纯 JSON 文本编辑作为默认主交互

### 15.5 状态、文案与显示口径

- 实名、邀请、会员、支付、退款、模板状态全部复用统一状态字典
- 资格状态、支付方式、模板发布状态等展示文案必须来自单一常量或公共工具
- 同一业务对象的状态标签、操作按钮可用性、空状态文案不得在多个页面各写一套逻辑

## 16. 查询 / 写入权限与高风险操作日志要求

### 16.1 权限分层要求

每个后台页面必须同时定义：

1. 页面查询权限：`page.*`
2. 写操作权限：`action.*`
3. 高风险动作是否强制审计：`required`

约束：

- 只读角色可以进入页面，但没有对应 `action.*` 时不得触发写操作
- 菜单可见不代表页面可访问，页面可访问也不代表按钮可点击
- 所有高风险写操作都必须写入 `admin_operation_log`

### 16.2 审计日志字段要求

`admin_operation_log` 除复用 `BaseEntity` 公共字段外，业务字段至少包含：

- `admin_user_id`
- `admin_user_name`
- `module_code`
- `operation_code`
- `target_type`
- `target_id`
- `request_id`
- `client_ip`
- `user_agent`
- `before_snapshot_json`
- `after_snapshot_json`
- `operation_result`
- `fail_reason`
- `extra_context_json`
- `confirm_token`
- `confirmed_at`

补充要求：

- 财务操作必须把金额、订单号、退款单号写入 `extra_context_json`
- 资格发放必须把 `grant_type`、`grant_code`、生效区间写入 `extra_context_json`
- 模板发布 / 回滚必须把版本号、发布说明、回滚来源写入 `extra_context_json`

### 16.3 高风险确认弹窗要求

以下动作必须先弹出统一确认框，再允许提交：

- 审核通过 / 审核拒绝
- 邀请异常通过 / 作废 / 标记复核完成
- 邀请规则启用 / 停用
- 邀请资格发放 / 撤销 / 延期
- 会员产品启用 / 停用
- 会员开通 / 延期 / 关闭
- 退款审核通过 / 拒绝
- 模板启用 / 停用
- 模板发布 / 回滚
- 主题 token 发布
- 分享产物发布
- 后台账号启用 / 禁用 / 重置密码
- 后台账号分配角色
- 角色权限编辑 / 启用 / 停用

确认框最少展示：

1. 当前对象摘要
2. 当前状态与目标状态
3. 影响范围
4. 操作权限码
5. 备注输入区

表单约束：

- 拒绝、撤销、关闭、回滚类动作必须填写原因
- 财务动作建议增加二次确认文案
- 提交成功后前端需要保存本次确认流水标识，便于与日志对齐

### 16.4 页面级查询 / 写入权限与日志要求

| 页面 | 查询权限 | 写权限 | 是否强制审计 | 额外日志要求 |
|------|----------|--------|--------------|--------------|
| `/dashboard/index` | `page.dashboard.index` | 无 | 否 | 聚合查询不落操作日志 |
| `/users/index`、`/users/:id` | `page.users.index`、`page.users.detail` | 无 | 否 | 用户详情查询仅做访问留痕可选 |
| `/verify/pending`、`/verify/:id` | `page.verify.pending`、`page.verify.detail` | `action.verify.approve`、`action.verify.reject` | 是 | 记录 `verification_id`、拒绝原因、用户实名状态回写结果 |
| `/verify/history` | `page.verify.history` | 无 | 否 | 仅查询 |
| `/referral/records` | `page.referral.records` | 无 | 否 | 仅查询 |
| `/referral/risk` | `page.referral.risk` | `action.referral.risk.approve`、`action.referral.risk.invalidate`、`action.referral.risk.resolve` | 是 | 记录风险原因、设备命中摘要、最终处理结论 |
| `/referral/policies` | `page.referral.policies` | `action.referral.policy.create`、`action.referral.policy.edit`、`action.referral.policy.enable`、`action.referral.policy.disable` | 是 | 记录规则快照、开关状态、阈值变更前后值 |
| `/referral/eligibility` | `page.referral.eligibility` | `action.referral.eligibility.grant`、`action.referral.eligibility.revoke`、`action.referral.eligibility.extend` | 是 | 记录 `grant_type`、`grant_code`、来源单据、生效区间 |
| `/membership/products` | `page.membership.products` | `action.membership.product.create`、`action.membership.product.edit`、`action.membership.product.enable`、`action.membership.product.disable`、`action.membership.product.sort` | 是 | 记录价格、层级、权益配置差异、排序变化 |
| `/membership/benefits` | `page.membership.benefits` | `action.membership.benefit.create`、`action.membership.benefit.edit`、`action.membership.benefit.enable`、`action.membership.benefit.disable` | 是 | 记录能力项编码、影响页面、变更说明 |
| `/membership/accounts` | `page.membership.accounts` | `action.membership.account.open`、`action.membership.account.extend`、`action.membership.account.close` | 是 | 记录层级、来源类型、关联支付单、到期时间变化 |
| `/membership/logs` | `page.membership.logs` | 无 | 否 | 仅查询 |
| `/payment/orders`、`/payment/transactions` | `page.payment.orders`、`page.payment.transactions` | 无 | 否 | 导出动作如后续开放需单独授权 |
| `/refund/orders` | `page.refund.orders` | `action.refund.approve`、`action.refund.reject` | 是 | 记录退款金额、审核备注、渠道退款状态 |
| `/refund/logs` | `page.refund.logs` | 无 | 否 | 仅查询 |
| `/content/templates` | `page.content.templates` | `action.content.template.create`、`action.content.template.edit`、`action.content.template.enable`、`action.content.template.disable`、`action.content.template.publish`、`action.content.template.rollback`、`action.content.template.sort` | 是 | 记录模板版本、差异快照、发布说明、回滚来源、排序变化 |
| `/content/theme-tokens` | `page.content.theme-tokens` | `action.content.theme.edit`、`action.content.theme.publish` | 是 | 记录主题 token 前后差异、发布版本 |
| `/content/share-artifacts` | `page.content.share-artifacts` | `action.content.artifact.edit`、`action.content.artifact.publish` | 是 | 记录分享文案、图片预设、门槛配置变化、发布版本 |
| `/content/publish-logs` | `page.content.publish-logs` | `action.content.template.rollback` | 是 | 记录回滚来源版本、回滚说明、目标版本 |
| `/system/admin-users` | `page.system.admin-users` | `action.system.admin-user.create`、`action.system.admin-user.edit`、`action.system.admin-user.enable`、`action.system.admin-user.disable`、`action.system.admin-user.reset-password`、`action.system.admin-user.bind-roles` | 是 | 记录角色绑定差异、账号状态变化、密码重置结果 |
| `/system/roles` | `page.system.roles` | `action.system.role.create`、`action.system.role.edit`、`action.system.role.enable`、`action.system.role.disable`、`action.system.role.copy` | 是 | 记录菜单、页面、操作权限变更前后差异 |
| `/system/ai-resume-governance` | `page.system.ai-resume-governance` | `action.system.ai-resume.review`、`action.system.ai-resume.resolve` | 是 | 记录失败样本处理前后状态、请求 ID、错误码、失败类型与人工备注；当前允许 `page.system.operation-logs` 作为迁移期兜底 |
| `/system/operation-logs` | `page.system.operation-logs` | 无 | 否 | 仅查询 |

### 16.5 高风险操作清单与动作必填日志字段

说明：

- 以下所有动作除必须记录 `16.2` 的通用字段外，还必须补齐本节的动作必填字段
- `reason` 表示拒绝原因、撤销原因、关闭原因、回滚原因等统一原因字段
- 只要动作进入统一确认弹窗，日志中必须带 `confirm_token`、`confirmed_at`

| 业务域 | 高风险操作 | 权限码 | 动作必填日志字段 |
|------|----------|--------|------------------|
| 实名认证 | 审核通过 | `action.verify.approve` | `verification_id`、`apply_user_id`、`verify_status_before`、`verify_status_after`、`audit_remark` |
| 实名认证 | 审核拒绝 | `action.verify.reject` | `verification_id`、`apply_user_id`、`verify_status_before`、`verify_status_after`、`reason`、`audit_remark` |
| 邀请裂变 | 异常邀请通过 | `action.referral.risk.approve` | `referral_record_id`、`inviter_user_id`、`invitee_user_id`、`risk_code`、`risk_status_before`、`risk_status_after`、`decision` |
| 邀请裂变 | 异常邀请作废 | `action.referral.risk.invalidate` | `referral_record_id`、`inviter_user_id`、`invitee_user_id`、`risk_code`、`risk_status_before`、`risk_status_after`、`reason` |
| 邀请裂变 | 标记复核完成 | `action.referral.risk.resolve` | `referral_record_id`、`risk_code`、`risk_status_before`、`risk_status_after`、`review_conclusion`、`reviewed_at` |
| 邀请裂变 | 邀请规则启用 / 停用 | `action.referral.policy.enable`、`action.referral.policy.disable` | `policy_id`、`policy_code`、`policy_status_before`、`policy_status_after`、`rule_snapshot_before_json`、`rule_snapshot_after_json`、`reason?` |
| 邀请裂变 | 资格发放 | `action.referral.eligibility.grant` | `grant_id`、`user_id`、`grant_type`、`grant_code`、`effective_time`、`expire_time`、`source_type`、`source_id`、`remark` |
| 邀请裂变 | 资格撤销 | `action.referral.eligibility.revoke` | `grant_id`、`user_id`、`grant_type`、`grant_code`、`grant_status_before`、`grant_status_after`、`reason` |
| 邀请裂变 | 资格延期 | `action.referral.eligibility.extend` | `grant_id`、`user_id`、`grant_type`、`grant_code`、`expire_time_before`、`expire_time_after`、`remark` |
| 会员中心 | 会员产品启用 / 停用 | `action.membership.product.enable`、`action.membership.product.disable` | `product_id`、`product_code`、`product_status_before`、`product_status_after`、`membership_tier`、`price_snapshot_json`、`reason?` |
| 会员中心 | 手工开通会员 | `action.membership.account.open` | `membership_account_id`、`user_id`、`membership_tier_before`、`membership_tier_after`、`effective_time`、`expire_time`、`source_type`、`source_id`、`remark` |
| 会员中心 | 会员延期 | `action.membership.account.extend` | `membership_account_id`、`user_id`、`membership_tier`、`expire_time_before`、`expire_time_after`、`source_type`、`source_id`、`remark` |
| 会员中心 | 会员关闭 | `action.membership.account.close` | `membership_account_id`、`user_id`、`membership_status_before`、`membership_status_after`、`closed_at`、`reason` |
| 退款中心 | 退款审核通过 | `action.refund.approve` | `refund_order_id`、`refund_no`、`payment_order_id`、`payment_order_no`、`refund_amount`、`audit_status_before`、`audit_status_after`、`channel_status`、`audit_remark` |
| 退款中心 | 退款审核拒绝 | `action.refund.reject` | `refund_order_id`、`refund_no`、`payment_order_id`、`payment_order_no`、`refund_amount`、`audit_status_before`、`audit_status_after`、`reason`、`audit_remark` |
| 页面配置 | 模板启用 / 停用 | `action.content.template.enable`、`action.content.template.disable` | `template_id`、`template_code`、`template_status_before`、`template_status_after`、`scene_code`、`reason?` |
| 页面配置 | 模板发布 | `action.content.template.publish` | `template_id`、`template_code`、`publish_version`、`draft_version`、`publish_note`、`diff_summary_json` |
| 页面配置 | 模板回滚 | `action.content.template.rollback` | `template_id`、`template_code`、`rollback_from_version`、`rollback_to_version`、`reason`、`diff_summary_json` |
| 页面配置 | 主题 token 发布 | `action.content.theme.publish` | `theme_token_id`、`theme_code`、`template_id`、`publish_version`、`diff_summary_json`、`publish_note` |
| 页面配置 | 分享产物发布 | `action.content.artifact.publish` | `artifact_config_id`、`artifact_type`、`template_id`、`publish_version`、`threshold_snapshot_json`、`publish_note` |
| 系统管理 | 后台账号启用 / 禁用 | `action.system.admin-user.enable`、`action.system.admin-user.disable` | `target_admin_user_id`、`target_admin_account`、`account_status_before`、`account_status_after`、`reason?` |
| 系统管理 | 重置后台账号密码 | `action.system.admin-user.reset-password` | `target_admin_user_id`、`target_admin_account`、`reset_result`、`credential_delivery_mode`、`reason?` |
| 系统管理 | 后台账号分配角色 | `action.system.admin-user.bind-roles` | `target_admin_user_id`、`target_admin_account`、`role_codes_before`、`role_codes_after`、`high_risk_action_codes_after`、`reason?` |
| 系统管理 | 角色权限编辑 | `action.system.role.edit` | `role_id`、`role_code`、`menu_permissions_before`、`menu_permissions_after`、`page_permissions_before`、`page_permissions_after`、`action_permissions_before`、`action_permissions_after`、`reason?` |
| 系统管理 | 角色启用 / 停用 | `action.system.role.enable`、`action.system.role.disable` | `role_id`、`role_code`、`role_status_before`、`role_status_after`、`bound_admin_user_count`、`reason?` |
| 系统管理 | AI 失败样本人工复核 | `action.system.ai-resume.review` | `failure_id`、`request_id`、`handling_status`、`reason`、`error_code`、`failure_type` |
| 系统管理 | AI 失败样本建议重试 | `action.system.ai-resume.resolve` | `failure_id`、`request_id`、`handling_status`、`reason`、`error_code`、`failure_type` |

### 16.6 权限码缺项检查

结论：

- 当前 `00-11` 已有权限体系方向；本次对照页面动作与路由清单后，原有缺项已经在 `16.4` 收口补齐
- 最终落地到权限常量、角色矩阵和按钮显隐时，以下权限码不得遗漏；导出类动作如本轮保留，也必须单独授权

本次收口新增并要求纳入最终清单的页面权限码：

- `page.verify.history`
- `page.membership.logs`
- `page.content.publish-logs`

本次收口新增并要求纳入最终清单的操作权限码：

- `action.referral.risk.resolve`
- `action.referral.eligibility.extend`
- `action.membership.product.sort`
- `action.membership.benefit.enable`
- `action.membership.benefit.disable`
- `action.content.template.sort`
- `action.content.theme.publish`
- `action.content.artifact.publish`
- `action.system.role.copy`

如本轮保留导出能力，还需补齐以下独立操作权限码，不应复用页面查询权限：

- `action.users.export`
- `action.referral.record.export`
- `action.payment.order.export`
- `action.system.operation-log.export`

## 17. 最终交付清单

### 17.1 页面与路由交付

| 一级模块 | 路由前缀 | 必交付页面 | 必要聚合接口 |
|----------|----------|------------|--------------|
| 工作台 | `/dashboard` | `/dashboard/index` | `GET /api/admin/dashboard/overview` |
| 用户中心 | `/users` | `/users/index`、`/users/:id` | `GET /api/admin/users`、`GET /api/admin/users/{id}` |
| 实名认证 | `/verify` | `/verify/pending`、`/verify/history`、`/verify/:id` | `GET /api/admin/verify/list`、`GET /api/admin/verify/{id}` |
| 邀请裂变 | `/referral` | `/referral/records`、`/referral/risk`、`/referral/policies`、`/referral/eligibility` | `GET /api/admin/referral/records`、`GET /api/admin/referral/risk/list`、`GET /api/admin/referral/policies`、`GET /api/admin/referral/eligibility` |
| 会员中心 | `/membership` | `/membership/products`、`/membership/benefits`、`/membership/accounts`、`/membership/logs` | `GET /api/admin/membership/products`、`GET /api/admin/membership/benefits`、`GET /api/admin/membership/accounts`、`GET /api/admin/membership/logs` |
| 订单中心 | `/payment` | `/payment/orders`、`/payment/transactions` | `GET /api/admin/payment/orders`、`GET /api/admin/payment/transactions` |
| 退款中心 | `/refund` | `/refund/orders`、`/refund/logs` | `GET /api/admin/refund/orders`、`GET /api/admin/refund/logs` |
| 页面配置 | `/content` | `/content/templates`、`/content/theme-tokens`、`/content/share-artifacts`、`/content/publish-logs` | `GET /api/admin/content/templates`、`GET /api/admin/content/theme-tokens`、`GET /api/admin/content/share-artifacts`、`GET /api/admin/content/publish-logs` |
| 系统管理 | `/system` | `/system/admin-users`、`/system/roles`、`/system/ai-resume-governance`、`/system/operation-logs` | `GET /api/admin/system/admin-users`、`GET /api/admin/system/roles`、`GET /api/admin/system/roles/ai-governance-matrix`、`GET /api/admin/ai/resume/overview`、`GET /api/admin/system/operation-logs` |

### 17.2 权限与菜单交付

最终交付前必须核对：

1. 每个一级模块均已配置 `menu.*`
2. 每个页面路由均已配置 `page.*`
3. 每个写操作均已配置独立 `action.*`
4. 高风险动作均已接入统一确认弹窗与操作日志
5. 角色矩阵已覆盖 `super_admin`、`verify_operator`、`referral_operator`、`membership_operator`、`finance_operator`、`content_operator`
6. AI 治理页已完成一次真实角色授权收口，不再把 `page.system.operation-logs` 当成新增角色的主授权口径

### 17.3 接口与 00-10 表结构对齐

| 页面域 | 对齐的数据主表 | 关键写接口 |
|--------|----------------|------------|
| 实名认证 | `identity_verification`、`user`、`actor_profile` | `POST /api/admin/verify/{id}/approve`、`POST /api/admin/verify/{id}/reject` |
| 邀请裂变 | `invite_code`、`referral_record`、`referral_policy`、`user_entitlement_grant` | `POST /api/admin/referral/risk/{id}/approve`、`POST /api/admin/referral/eligibility/grant` |
| 会员中心 | `membership_product`、`membership_account`、`membership_change_log` | `POST /api/admin/membership/products`、`POST /api/admin/membership/accounts/{userId}/open` |
| 订单与退款 | `payment_order`、`payment_transaction`、`refund_order`、`refund_operate_log` | `POST /api/admin/refund/{id}/approve`、`POST /api/admin/refund/{id}/reject` |
| 页面配置 | `card_scene_template`、`template_publish_log` | `POST /api/admin/content/templates/{id}/publish`、`POST /api/admin/content/templates/{id}/rollback` |
| 系统管理 | `admin_user`、`admin_role`、`admin_user_role`、`admin_operation_log` | `POST /api/admin/system/admin-users`、`POST /api/admin/system/roles` |

### 17.4 分阶段验收

| 阶段 | 必须交付 | 验收口径 |
|------|----------|----------|
| P0 | 登录、主框架、实名认证审核、邀请异常审核、会员产品、会员账户、模板配置 | 页面可访问、路由可装配、聚合接口已对接、关键高风险日志可追溯 |
| P1 | 支付订单、退款审核、邀请资格发放、系统权限与日志查询 | 财务与资格写操作具备独立权限码、确认弹窗、日志字段完整 |
| P2 | 工作台统计深化、模板发布回滚、细粒度权限扩展 | 聚合指标口径统一、发布回滚闭环、角色矩阵可扩展 |

最终验收必须同时检查“页面 + 路由 + 权限 + 接口 + 日志”五个维度，不允许只完成页面而缺权限或审计闭环。
