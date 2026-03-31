# 平台后台与服务端架构 - 技术设计

_Requirements: 00-10 全部_

## 1. 设计目标

本 Spec 解决的不是某一个页面，而是平台下一阶段的整体系统骨架：

1. 给小程序主线补齐运营后台承载面
2. 给后端补齐按业务域划分的模块边界
3. 给数据库补齐会员、支付、退款、邀请资格、模板配置的主模型
4. 为 05-09 / 05-10 / 05-11 以及后续真实会员支付接入提供统一服务基线

## 2. 总体架构

```text
演员小程序
  -> /api/**

平台后台 Web
  -> /api/admin/**

统一 Spring Boot 服务
  -> auth / actor / verify / referral / membership / payment / refund / card / fortune / personalization
  -> MySQL
  -> Redis
```

### 2.1 架构选择

- 采用模块化单体，不采用微服务
- 后台 Web 单独建工程，不混入 uni-app 小程序工程
- 小程序与后台共用同一服务端和数据库

### 2.2 原因

- 当前团队阶段更需要快速闭环，而不是服务拆分复杂度
- 认证、邀请、会员、个性化分享之间事务和读模型耦合较强
- 当前后台诉求以审核、配置、订单、退款为主，不需要独立服务网格

## 3. 服务端模块分层

### 3.1 推荐模块

| 模块 | 职责 |
|------|------|
| `auth` | 登录、鉴权、后台账号登录 |
| `actor` | 演员档案与资料完成度 |
| `verify` | 实名认证申请与审核 |
| `referral` | 邀请码、邀请记录、异常复核、邀请规则 |
| `membership` | 会员产品、会员状态、会员变更 |
| `payment` | 支付订单、支付流水、支付回调 |
| `refund` | 退款申请、退款审核、退款执行 |
| `card` | 场景模板、主题配置、名片配置、分享偏好 |
| `fortune` | 命理报告、月度缓存、命理来源 |
| `personalization` | 聚合等级、会员、命理、模板、配置，输出统一读模型 |

### 3.2 分层职责

| 层级 | 职责 |
|------|------|
| Controller | 区分 `/api/**` 与 `/api/admin/**` 出口 |
| Application Service | 编排事务、流程、权限校验 |
| Domain Service | 封装业务规则、状态流转、资格判断 |
| Mapper / Repository | 访问单表或简单聚合 |
| Facade | 聚合跨域读模型，如 `PersonalizationFacadeService` |

### 3.3 推荐目录结构

```text
com.kaipai.module
├── controller
│   ├── auth
│   ├── actor
│   ├── verify
│   ├── referral
│   ├── membership
│   ├── payment
│   ├── refund
│   ├── card
│   ├── fortune
│   ├── personalization
│   └── admin
│       ├── verify
│       ├── referral
│       ├── membership
│       ├── payment
│       ├── refund
│       ├── content
│       └── system
├── model
│   ├── auth
│   ├── actor
│   ├── verify
│   ├── referral
│   ├── membership
│   ├── payment
│   ├── refund
│   ├── card
│   ├── fortune
│   └── system
└── server
    ├── auth
    ├── actor
    ├── verify
    ├── referral
    ├── membership
    ├── payment
    ├── refund
    ├── card
    ├── fortune
    ├── personalization
    └── system
```

说明：

- 现有三层骨架 `controller / model / server` 继续保留
- 后台接口不另起独立工程包，统一收敛到 `controller/admin/**`
- `personalization` 主要承担聚合服务，实体数量应最少

### 3.4 现有模块复用与新增边界

| 现有能力 | 处理方式 |
|------|------|
| `auth` | 继续复用，补充后台账号登录出口 |
| `actor` | 继续复用，承接档案与资料完成度 |
| `order` / `cooperation_order` | 保留合作订单语义，不承担会员支付 |
| `invite` / `invite_record` | 保留剧组邀约语义，不复用于裂变邀请 |
| `company` / `recruit` | 当前不作为后台主线改造重点 |
| `verify` / `referral` / `membership` / `payment` / `refund` / `card` / `fortune` / `personalization` | 按本 Spec 新增或扩展 |

明确约束：

- 当前已有 `/invite` 路由默认对应剧组邀约，不再向该模块叠加裂变逻辑
- 裂变邀请统一进入 `referral` 模块，避免“invite”一词同时表示两套业务
- 会员支付与合作订单彻底分开，不在同一个 `order` 控制器下混写

### 3.5 推荐类粒度

每个业务域至少按以下粒度拆分：

- Entity：单表实体
- Mapper：单表或轻聚合访问
- Service：单域服务
- AdminService：后台写操作或后台聚合读操作
- FacadeService：跨域聚合，如 `PersonalizationFacadeService`
- Controller：前台接口
- AdminController：后台接口

示例：

- `VerifyController` / `AdminVerifyController`
- `ReferralController` / `AdminReferralController`
- `MembershipController` / `AdminMembershipController`
- `PaymentController` / `AdminPaymentController`
- `RefundController` / `AdminRefundController`
- `CardController` / `AdminContentController`

## 4. 后台 Web 模块设计

### 4.1 一级菜单

- 工作台
- 用户中心
- 实名认证
- 邀请裂变
- 会员中心
- 订单中心
- 退款中心
- 页面配置
- 系统管理

### 4.2 二级菜单建议

| 一级菜单 | 二级菜单 |
|----------|----------|
| 实名认证 | 待审核列表、审核历史 |
| 邀请裂变 | 邀请记录、异常邀请审核、邀请规则配置、邀请资格下发 |
| 会员中心 | 会员产品、会员权益配置、用户会员状态、会员变更记录 |
| 订单中心 | 支付订单、支付流水 |
| 退款中心 | 退款申请、退款审核、退款日志 |
| 页面配置 | 场景模板、分享卡片配置、海报配置、模板发布记录 |
| 系统管理 | 后台账号、角色权限、操作日志 |

### 4.3 后台配置定位

后台的“页面装修配置”在当前阶段定义为：

- 结构化模板配置后台
- 结构化主题 token 配置后台
- 结构化分享产物配置后台

明确不做：

- 自由拖拽式低代码搭建器
- 任意页面可视化拼装器

## 5. 数据库设计基线

## 5.1 设计原则

1. 主数据表承载当前真实状态
2. 过程表承载申请、审核、支付、退款等流程痕迹
3. 配置表承载模板、规则、权益说明
4. 日志表承载操作追溯与发布追溯
5. 新表默认沿用现有 `BaseEntity` 公共字段，不平行发明审计字段

## 5.2 保留并扩展的现有表

### `user`

建议补充：

- `invited_by_user_id`
- `valid_invite_count`
- `register_device_fingerprint`

说明：

- `realAuthStatus` 继续作为用户实名结果态
- `valid_invite_count` 作为高频读取冗余字段允许保留

### `actor_profile`

建议补充：

- `birth_hour`

说明：

- `realName`、`isCertified` 继续作为演员档案侧结果态

### `cooperation_order`

说明：

- 继续仅表示演员与剧组的合作业务订单
- 不复用为会员支付订单

## 5.3 新增数据表蓝图

### A. 实名认证域

`identity_verification`

职责：

- 记录实名认证申请、审核结果、拒绝原因、审核人

关键字段：

- `verification_id`
- `user_id`
- `real_name`
- `id_card_no_cipher`
- `id_card_hash`
- `status`
- `reject_reason`
- `reviewer_id`
- `reviewed_at`

规则：

- 同一用户同一时刻只能存在一条待审核申请
- 审核通过后回写 `user.realAuthStatus` 与 `actor_profile.isCertified`

### B. 裂变邀请域

`invite_code`

职责：

- 保存用户邀请码主记录

关键字段：

- `invite_code_id`
- `user_id`
- `code`
- `status`

`referral_record`

职责：

- 保存裂变邀请关系与有效性状态

关键字段：

- `referral_id`
- `inviter_user_id`
- `invitee_user_id`
- `invite_code_id`
- `invite_code_snapshot`
- `register_device_fingerprint`
- `status`
- `risk_flag`
- `risk_reason`
- `registered_at`
- `validated_at`

推荐状态：

- `0` 待生效
- `1` 已生效
- `2` 无效
- `3` 人工复核中

`referral_policy`

职责：

- 保存邀请规则配置

关键字段：

- `policy_id`
- `policy_name`
- `enabled`
- `require_real_auth`
- `require_profile_completion`
- `profile_completion_threshold`
- `same_device_limit`
- `hourly_invite_limit`
- `auto_grant_enabled`
- `grant_rule_json`

### C. 会员域

`membership_product`

职责：

- 定义会员可售商品与权益包

关键字段：

- `product_id`
- `product_code`
- `product_name`
- `membership_tier`
- `duration_days`
- `list_price`
- `sale_price`
- `status`
- `benefit_config_json`

`membership_account`

职责：

- 保存用户当前会员主状态

关键字段：

- `membership_id`
- `user_id`
- `tier`
- `status`
- `effective_time`
- `expire_time`
- `source_type`
- `source_ref_id`

`membership_change_log`

职责：

- 保存会员变更流水

关键字段：

- `change_log_id`
- `user_id`
- `before_tier`
- `after_tier`
- `change_reason`
- `source_type`
- `source_ref_id`
- `effective_time`
- `expire_time`

### D. 支付与退款域

`payment_order`

职责：

- 保存会员购买 / 续费的支付订单

关键字段：

- `payment_order_id`
- `order_no`
- `user_id`
- `biz_type`
- `biz_ref_id`
- `product_id`
- `amount`
- `pay_status`
- `pay_channel`
- `paid_at`

推荐状态：

- `0` 待支付
- `1` 已支付
- `2` 已关闭
- `3` 已退款
- `4` 部分退款

`payment_transaction`

职责：

- 保存第三方渠道支付流水与回调事实

关键字段：

- `transaction_id`
- `payment_order_id`
- `channel_trade_no`
- `channel`
- `trade_type`
- `amount`
- `status`
- `callback_payload`

`refund_order`

职责：

- 保存退款申请、审核与退款执行状态

关键字段：

- `refund_order_id`
- `refund_no`
- `payment_order_id`
- `user_id`
- `refund_amount`
- `refund_reason`
- `audit_status`
- `refund_status`
- `auditor_id`
- `audited_at`
- `channel_refund_no`
- `refunded_at`

说明：

- `audit_status` 与 `refund_status` 必须拆开

`refund_operate_log`

职责：

- 保存退款操作日志

关键字段：

- `log_id`
- `refund_order_id`
- `operator_id`
- `action_type`
- `remark`

### E. 名片模板与分享配置域

`card_scene_template`

职责：

- 定义场景模板、主题 token、等级门槛、会员门槛

关键字段：

- `template_id`
- `template_code`
- `scene_key`
- `template_name`
- `description`
- `layout_variant`
- `tier`
- `required_level`
- `base_theme_json`
- `artifact_preset_json`
- `status`
- `sort_no`

`actor_card_config`

职责：

- 保存用户按场景的名片定制配置

关键字段：

- `config_id`
- `user_id`
- `actor_profile_id`
- `scene_key`
- `template_id`
- `layout_variant`
- `primary_color`
- `accent_color`
- `background_color`
- `highlighted_experience_ids`
- `highlighted_photo_urls`
- `tag_order_json`

`actor_share_preference`

职责：

- 保存用户按场景的分享偏好

关键字段：

- `preference_id`
- `user_id`
- `scene_key`
- `preferred_artifact`
- `preferred_tone`
- `enable_fortune_theme`

### F. 命理域

`fortune_report`

职责：

- 按月缓存命理报告

关键字段：

- `fortune_report_id`
- `user_id`
- `report_month`
- `zodiac_animal`
- `zodiac_fortune`
- `constellation`
- `constellation_fortune`
- `ziwei_star`
- `ziwei_profile`
- `lucky_color`
- `lucky_color_name`
- `lucky_color_interpretation`
- `lucky_number`
- `lucky_number_interpretation`
- `birth_hour`
- `source_type`
- `raw_payload`

说明：

- `report_month` 推荐使用 `DATE`，存每月第一天，不用 `VARCHAR(7)`

### G. 资格与权益域

`user_entitlement_grant`

职责：

- 保存用户被授予的资格或权益

关键字段：

- `grant_id`
- `user_id`
- `grant_type`
- `grant_code`
- `status`
- `effective_time`
- `expire_time`
- `source_type`
- `source_ref_id`
- `remark`

示例：

- 邀请资格
- 会员试用资格
- 定制模板试用资格
- 海报生成加赠次数

`entitlement_rule`

职责：

- 保存自动资格下发规则

关键字段：

- `rule_id`
- `rule_code`
- `rule_name`
- `grant_type`
- `trigger_type`
- `rule_config_json`
- `enabled`

### H. 后台治理域

`admin_user`

职责：

- 后台登录账号

`admin_role`

职责：

- 角色定义

`admin_user_role`

职责：

- 账号与角色映射

`admin_operation_log`

职责：

- 记录审核、退款、配置发布、资格发放等操作

`template_publish_log`

职责：

- 记录模板、主题 token、分享产物配置的发布、回滚、版本说明

## 6. 聚合模型设计

### 6.1 `PersonalizationProfile`

定位：

- 后端读模型聚合结果
- 不作为事实表直接落库

输入来源：

- 等级信息
- 会员状态
- 命理报告
- 模板定义
- 用户名片配置
- 分享偏好
- 资格 / 权益

输出对象：

- 当前主线所需的个性化主题、分享产物、能力 gating 结果

### 6.2 聚合服务

建议新增：

- `PersonalizationFacadeService`

职责：

1. 查询等级与邀请状态
2. 查询会员主状态
3. 查询命理报告
4. 查询模板与用户配置
5. 查询资格与额外权益
6. 输出统一 DTO 给前端

### 6.3 接口分组基线

前台接口建议：

| 模块 | 建议接口前缀 |
|------|--------------|
| `auth` | `/api/auth` |
| `actor` | `/api/actor/profile` |
| `verify` | `/api/verify` |
| `referral` | `/api/referral` |
| `membership` | `/api/membership` |
| `payment` | `/api/payment` |
| `refund` | `/api/refund` |
| `card` | `/api/card` |
| `fortune` | `/api/fortune` |
| `personalization` | `/api/personalization` |

后台接口建议：

| 模块 | 建议接口前缀 |
|------|--------------|
| 工作台 | `/api/admin/dashboard` |
| 用户中心 | `/api/admin/users` |
| 认证审核 | `/api/admin/verify` |
| 邀请裂变 | `/api/admin/referral` |
| 会员中心 | `/api/admin/membership` |
| 支付订单 | `/api/admin/payment` |
| 退款中心 | `/api/admin/refund` |
| 页面配置 | `/api/admin/content` |
| 系统管理 | `/api/admin/system` |

### 6.4 核心接口清单建议

前台接口最小集合：

- `GET /api/verify/status`
- `POST /api/verify/submit`
- `GET /api/referral/code`
- `GET /api/referral/records`
- `GET /api/referral/stats`
- `GET /api/membership/account`
- `GET /api/membership/products`
- `POST /api/payment/orders`
- `POST /api/refund/orders`
- `GET /api/card/templates`
- `GET /api/card/config`
- `POST /api/card/config`
- `GET /api/fortune/report`
- `GET /api/personalization/profile`

后台接口最小集合：

- `GET /api/admin/dashboard/overview`
- `GET /api/admin/users`
- `GET /api/admin/users/{id}`
- `GET /api/admin/verify/list`
- `POST /api/admin/verify/{id}/approve`
- `POST /api/admin/verify/{id}/reject`
- `GET /api/admin/referral/records`
- `GET /api/admin/referral/risk/list`
- `POST /api/admin/referral/risk/{id}/approve`
- `POST /api/admin/referral/risk/{id}/invalidate`
- `GET /api/admin/referral/policies`
- `PUT /api/admin/referral/policies/{id}`
- `POST /api/admin/referral/eligibility/grant`
- `POST /api/admin/referral/eligibility/revoke`
- `GET /api/admin/membership/products`
- `POST /api/admin/membership/products`
- `GET /api/admin/membership/accounts`
- `POST /api/admin/membership/accounts/{userId}/open`
- `POST /api/admin/membership/accounts/{userId}/extend`
- `POST /api/admin/membership/accounts/{userId}/close`
- `GET /api/admin/payment/orders`
- `GET /api/admin/payment/transactions`
- `GET /api/admin/refund/orders`
- `POST /api/admin/refund/{id}/approve`
- `POST /api/admin/refund/{id}/reject`
- `GET /api/admin/content/templates`
- `POST /api/admin/content/templates`
- `POST /api/admin/content/templates/{id}/publish`
- `POST /api/admin/content/templates/{id}/rollback`
- `GET /api/admin/system/admin-users`
- `GET /api/admin/system/roles`
- `GET /api/admin/system/operation-logs`

### 6.5 后台页面到接口与主表映射

| 后台页面 | 查询接口 | 写接口 | 主要数据表 | 说明 |
|------|------|------|------|------|
| 工作台 | `GET /api/admin/dashboard/overview` | — | `identity_verification`, `referral_record`, `refund_order`, `payment_order` | 必须是聚合接口，不做单表直查拼装 |
| 用户列表 | `GET /api/admin/users` | — | `user`, `actor_profile`, `membership_account`, `user_entitlement_grant` | 允许后台聚合查询 |
| 用户详情 | `GET /api/admin/users/{id}` | — | `user`, `actor_profile`, `membership_account`, `payment_order`, `refund_order` | 用户详情必须聚合，不建议前端拼多个接口 |
| 实名认证待审核 / 历史 / 详情 | `GET /api/admin/verify/list`, `GET /api/admin/verify/{id}` | `POST /api/admin/verify/{id}/approve`, `POST /api/admin/verify/{id}/reject` | `identity_verification`, `user`, `actor_profile` | 审核动作需要事务回写用户与演员结果态 |
| 邀请记录 | `GET /api/admin/referral/records`, `GET /api/admin/referral/{id}` | — | `referral_record`, `invite_code`, `user` | 记录页偏查询，不承担规则修改 |
| 异常邀请审核 | `GET /api/admin/referral/risk/list`, `GET /api/admin/referral/risk/{id}` | `POST /api/admin/referral/risk/{id}/approve`, `POST /api/admin/referral/risk/{id}/invalidate`, `POST /api/admin/referral/risk/{id}/resolve` | `referral_record`, `invite_code`, `user` | 风控页与记录页分开，避免职责混淆 |
| 邀请规则配置 | `GET /api/admin/referral/policies` | `POST /api/admin/referral/policies`, `PUT /api/admin/referral/policies/{id}` | `referral_policy` | 单域配置页 |
| 邀请资格管理 | `GET /api/admin/referral/eligibility` | `POST /api/admin/referral/eligibility/grant`, `POST /api/admin/referral/eligibility/revoke`, `POST /api/admin/referral/eligibility/extend` | `user_entitlement_grant`, `entitlement_rule`, `user` | 发放与撤销必须记录操作日志 |
| 会员产品 | `GET /api/admin/membership/products` | `POST /api/admin/membership/products`, `PUT /api/admin/membership/products/{id}`, `POST /api/admin/membership/products/{id}/enable`, `POST /api/admin/membership/products/{id}/disable` | `membership_product` | 单表配置页 |
| 会员权益配置 | `GET /api/admin/membership/benefits` | `POST /api/admin/membership/benefits`, `PUT /api/admin/membership/benefits/{id}` | `membership_product` | 现阶段可依附产品配置，不单独起表 |
| 会员账户 | `GET /api/admin/membership/accounts`, `GET /api/admin/membership/accounts/{userId}` | `POST /api/admin/membership/accounts/{userId}/open`, `POST /api/admin/membership/accounts/{userId}/extend`, `POST /api/admin/membership/accounts/{userId}/close` | `membership_account`, `membership_change_log`, `payment_order` | 查询需聚合账户与变更记录 |
| 会员变更记录 | `GET /api/admin/membership/logs` | — | `membership_change_log` | 单表查询页 |
| 支付订单 | `GET /api/admin/payment/orders`, `GET /api/admin/payment/orders/{id}` | — | `payment_order`, `membership_product` | 支付页只看会员支付订单，不看合作订单 |
| 支付流水 | `GET /api/admin/payment/transactions`, `GET /api/admin/payment/transactions/{id}` | — | `payment_transaction`, `payment_order` | 详情页展示渠道回调摘要 |
| 退款单 | `GET /api/admin/refund/orders`, `GET /api/admin/refund/orders/{id}` | `POST /api/admin/refund/{id}/approve`, `POST /api/admin/refund/{id}/reject` | `refund_order`, `payment_order`, `refund_operate_log` | 审核状态与退款执行状态必须同时展示 |
| 退款日志 | `GET /api/admin/refund/logs` | — | `refund_operate_log` | 单表查询页 |
| 场景模板 | `GET /api/admin/content/templates`, `GET /api/admin/content/templates/{id}` | `POST /api/admin/content/templates`, `PUT /api/admin/content/templates/{id}`, `POST /api/admin/content/templates/{id}/publish`, `POST /api/admin/content/templates/{id}/rollback` | `card_scene_template`, `template_publish_log` | 配置页需要草稿与发布态 |
| 主题 Token | `GET /api/admin/content/theme-tokens` | `PUT /api/admin/content/theme-tokens/{templateId}` | `card_scene_template` | 主题 token 当前收口在模板表 JSON 中 |
| 分享产物配置 | `GET /api/admin/content/share-artifacts` | `PUT /api/admin/content/share-artifacts/{templateId}` | `card_scene_template` | 产物预设当前收口在模板表 JSON 中 |
| 模板发布记录 | `GET /api/admin/content/publish-logs` | `POST /api/admin/content/templates/{id}/rollback` | `template_publish_log` | 发布记录与模板详情联动 |
| 后台账号 | `GET /api/admin/system/admin-users` | `POST /api/admin/system/admin-users`, `PUT /api/admin/system/admin-users/{id}`, `POST /api/admin/system/admin-users/{id}/enable`, `POST /api/admin/system/admin-users/{id}/disable`, `POST /api/admin/system/admin-users/{id}/reset-password` | `admin_user`, `admin_user_role` | 高风险操作需记录日志 |
| 角色权限 | `GET /api/admin/system/roles` | `POST /api/admin/system/roles`, `PUT /api/admin/system/roles/{id}` | `admin_role`, `admin_user_role` | 后续如权限项增多可新增权限点表 |
| 操作日志 | `GET /api/admin/system/operation-logs` | — | `admin_operation_log` | 单表查询页 |

### 6.6 需要优先使用聚合接口的页面

以下页面默认应由后端提供聚合查询接口，而不是让后台前端同时调多个单域接口：

1. 工作台
2. 用户详情
3. 会员账户详情
4. 退款详情
5. 场景模板详情

原因：

- 这些页面天然跨越多张表
- 如果改成前端拼装，会把领域边界重新打散到后台 Web
- 容易导致状态口径和操作权限判断不一致

### 6.7 最容易产生耦合冲突的边界

1. `invite` 与 `referral`
   - `invite_record` 继续保留剧组邀约语义
   - 裂变邀请统一进入 `referral`

2. `order` 与 `payment`
   - `cooperation_order` 继续只表示合作业务订单
   - 会员购买统一进入 `payment_order`

3. `membership` 与 `user_entitlement_grant`
   - 会员状态与资格发放不是同一个模型
   - 页面展示时可聚合，但后端落库必须分域

4. `card_scene_template` 与 `actor_card_config`
   - 模板定义与用户个性化配置必须分开
   - 后台模板配置页不得直接编辑用户配置表

## 7. 状态机约束

### 7.1 实名认证

```text
未提交 -> 待审核 -> 通过
               -> 拒绝 -> 重新提交
```

### 7.2 裂变邀请

```text
注册绑定 -> 待生效 -> 已生效
                  -> 无效
                  -> 人工复核中
```

### 7.3 会员状态

```text
未开通 -> 生效中 -> 已过期
              -> 手工关闭
```

### 7.4 支付订单

```text
待支付 -> 已支付 -> 已退款 / 部分退款
      -> 已关闭
```

### 7.5 退款单

```text
待审核 -> 审核通过 -> 退款中 -> 退款成功
      -> 审核拒绝
                  -> 退款失败
```

## 8. 实施优先级

```text
P0
  -> 实名认证审核后台
  -> 邀请异常审核后台
  -> 会员产品与会员状态后台
  -> 模板配置后台

P1
  -> 会员支付订单
  -> 退款申请与退款审核
  -> 邀请资格与权益下发

P2
  -> 自动权益规则引擎
  -> 模板版本发布与回滚
  -> 更细的风控与运营报表
```

### 8.1 推荐执行顺序

第一步，并行启动：

- `00-11 / T3-T4` 后台工程初始化与主框架
- `00-11 / T7` 页面字段清单
- `00-10 / T10` 后台信息架构与权限矩阵对齐

第二步，并行推进：

- `00-11 / T8-T10` 页面接口与权限码
- `00-10 / T11` 页面能力与表结构/接口模型对齐

第三步，统一收口：

- `00-11 / T11-T13`
- `00-10 / T12-T13`

### 8.2 关键前置关系

1. `00-10` 已完成的 DDL、模块目录与接口分组，是 `00-11` 页面设计的前提。
2. `00-11 / T7` 页面字段清单必须先于 `T8` 接口精细化，否则接口会反复改动。
3. `00-11 / T10` 权限码矩阵必须先于 `T11` 高风险操作日志要求。
4. `00-10 / T11` 页面能力与表结构/接口模型对齐，必须先于最终映射文档。
5. 支付订单与退款页面落地前，必须先固定“合作订单不复用为支付订单”的边界。

## 9. 对现有 Spec 和代码的约束关系

- 05-09 的实名认证前端实现后续必须接入本 Spec 规定的审核后台与认证表
- 05-10 的邀请裂变必须使用独立裂变模型，不得复用现有剧组邀约表
- 05-11 的个性化主模型后续应由本 Spec 的后台配置、会员、资格和模板表提供真实数据
- 现有 `cooperation_order` 保持合作业务语义，不承担会员支付职责

## 10. 跨工作流最终收口

### 10.1 DDL 交付清单

| 表 / 视图 | 责任工作流 | 说明 |
|------------|------------|------|
| `identity_verification`、`referral_*`、`membership_*`、`payment_order`、`payment_transaction`、`refund_*`、`card_scene_template`、`actor_*`、`fortune_report`、`user_entitlement_grant`、`entitlement_rule`、`admin_user`、`admin_role`、`admin_user_role`、`admin_operation_log`、`template_publish_log` | Workstream A + C | 覆盖实名、裂变、会员、支付、退款、模板、资格与后台治理的主模型，DDL 提交时需附带审计字段统一说明。 |
| `ALTER TABLE user` / `actor_profile` | Workstream A | 精准加字段扩展，避免并行部署时出现不同步。 |

每张表在上线前必须有对应的 00-11 页面或接口声明，否则属于未对齐产出。

### 10.2 接口与页面映射

| 后台页面 | 聚合查询 | 写接口 | 主表落脚 | 说明 |
|----------|------------|--------|-----------|------|
| Dashboard、用户详情、退款详情、会员账户详情、模板详情 | 详见 6.5 / 12.x | 按页面动作拆分 | 多表聚合 | 聚合接口由 Workstream C 验证一致性，后端按 Workstream B 接口方案实现。 |
| 认证、邀请、会员、支付、退款、模板配置、系统 | `/api/admin/**` 数百条接口 | 每一个高风险动作必须提供独立 `action:*` 权限 | 对应主表 | 前端与后端接口清单在 00-11 T8/T10 中完成，每个接口都应挂到具体表。 |

### 10.3 后台页面与权限映射

- 所有后台页面必须列出对应的菜单（`menu.*`）、页面（`page.*`）与操作（`action.*`）权限，且在 00-11 / T10 的权限矩阵中有记录。
- 工作台：`menu.dashboard` / `page.dashboard.index` / 无写操作。
- 用户中心：`menu.users` / `page.users.index`、`page.users.detail` / `action.user.entitlement.view` 等。
- 实名认证、邀请风控、会员产品与账户、订单、退款、内容模板、系统运营必须按 00-11 的高风险动作定义提供审批、发布、回滚的 `action.*` 权限，相关操作要同时写入 `admin_operation_log`、`refund_operate_log` 等日志表。

### 10.4 上线里程碑与阶段

1. **阶段 1（基础后台）**：完成后台框架、登录、工作台、认证与邀请审核、会员产品与账户、模板编辑；对应 DDL、接口与 00-11 页面逐项验收，确保 Workstream C / B 与 A 交互顺畅。
2. **阶段 2（支付与退款、资格）**：补齐支付订单、流水、退款单、资格下发、会员变更等表与接口，后台写接口必须经权限与日志校验。
3. **阶段 3（发布与数据保障）**：上线模板发布回滚、自动资格规则、个性化聚合读模型与后台运营报表，验证 `PersonalizationProfile` 聚合服务与权限审计闭环。

每个阶段必须列出版本说明、里程碑负责人、数据回滚窗口与回滚流程，Workstream C 负责跟后台确认页面与接口是否按表展开。
