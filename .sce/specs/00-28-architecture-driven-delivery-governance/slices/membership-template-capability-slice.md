# 会员能力与模板配置闭环切片卡

## 1. 切片名称

会员能力与模板配置闭环

## 2. 切片目标

建立“会员产品 / 账户 / 权益配置 -> 模板 / 主题 / 分享产物配置 -> 前台能力 gating 与展示恢复”的完整闭环。

本切片的价值不只是补一个会员页或模板页，而是把会员能力从页面入口级控制升级为分享产物级控制，并让后台配置真正成为前台名片、公开详情、海报和分享卡片的权威来源。

## 3. 上位 Spec

- `00-10 platform-admin-backend-architecture`
- `00-11 platform-admin-console`
- `00-28 architecture-driven-delivery-governance`
- `05-05 card-share-membership`
- `05-11 fortune-driven-share-personalization`

## 4. 业务范围

### 4.1 本轮范围

- 会员产品、会员账户、会员权益说明的后台配置与操作
- 场景模板、主题 token、分享产物预设的后台配置与发布
- 后端输出会员能力、模板能力、分享产物门槛
- 小程序等级中心、名片页、公开详情页消费统一能力口径
- 会员能力与模板配置联动到分享产物 gating

### 4.2 不在本轮范围

- 真实支付渠道接入和扣费流程细节
- 完整 CMS 拖拽装修平台
- 多租户模板市场
- 复杂营销订阅体系

## 5. 数据与状态模型

### 5.1 关键实体 / 表

- `membership_product`
- `membership_account`
- `membership_change_log`
- `payment_order`
- `payment_transaction`
- `refund_order`
- `card_scene_template`
- `template_publish_log`
- `actor_card_config`
- `actor_share_preference`
- `admin_operation_log`

### 5.2 关键状态

#### 会员状态

- 未开通
- 生效中
- 已过期
- 已关闭

#### 模板状态

- 草稿
- 已启用
- 已停用
- 已发布

#### 产物能力状态

- 基础可用
- 等级解锁
- 会员解锁
- 命理增强可用

### 5.3 状态流转

```text
后台配置会员产品 / 权益
  -> 开通或变更 membership_account
  -> 写入 membership_change_log

后台配置 card_scene_template / theme / share artifact
  -> 草稿保存
  -> 启停用
  -> 发布 / 回滚
  -> 写入 template_publish_log

前台进入名片 / 会员 / 公开详情
  -> 消费会员状态 + 等级状态 + 模板配置 + 产物配置
  -> 统一 resolver 输出 capability gate 和主题结果
```

## 6. 后端交付

### 6.1 核心接口

#### 后台端

- `GET /api/admin/membership/products`
- `GET /api/admin/membership/products/{id}`
- `POST /api/admin/membership/products`
- `PUT /api/admin/membership/products/{id}`
- `POST /api/admin/membership/products/{id}/enable`
- `POST /api/admin/membership/products/{id}/disable`
- `GET /api/admin/membership/accounts`
- `GET /api/admin/membership/accounts/{userId}`
- `POST /api/admin/membership/accounts/{userId}/open`
- `POST /api/admin/membership/accounts/{userId}/extend`
- `POST /api/admin/membership/accounts/{userId}/close`
- `GET /api/admin/membership/benefits`
- `POST /api/admin/membership/benefits`
- `PUT /api/admin/membership/benefits/{id}`
- `GET /api/admin/content/templates`
- `GET /api/admin/content/templates/{id}`
- `POST /api/admin/content/templates`
- `PUT /api/admin/content/templates/{id}`
- `POST /api/admin/content/templates/{id}/publish`
- `POST /api/admin/content/templates/{id}/rollback`
- `GET /api/admin/content/theme-tokens`
- `PUT /api/admin/content/theme-tokens/{templateId}`
- `GET /api/admin/content/share-artifacts`
- `PUT /api/admin/content/share-artifacts/{templateId}`

#### 小程序端

- 等级 / 能力查询接口
- 模板 / 场景 / 主题配置查询接口
- 分享产物配置查询接口
- 会员状态查询接口

### 6.2 核心服务规则

- 会员状态、邀请等级、资格权益必须分别建模，不能互相替代
- 模板配置、主题 token、分享产物预设优先由后台和后端下发，不在前端硬编码完整规则库
- 会员 gating 必须精确到分享产物维度，而不只是“能否进入某页面”
- 模板发布和回滚必须带版本和操作日志
- 订单、支付、退款模型和会员账户变更必须边界清晰，不能混用

### 6.3 安全 / 权限 / 审计

- 会员开通、延期、关闭必须具备独立操作权限
- 模板编辑、发布、回滚、主题调整、产物调整必须具备独立操作权限
- 高风险动作全部进入 `admin_operation_log`
- 前台展示能力状态以后端返回和统一 resolver 为准

## 7. 后台交付

### 7.1 管理页 / 治理动作

- `kaipai-admin/src/views/membership/ProductsView.vue`
- `kaipai-admin/src/views/membership/AccountsView.vue`
- 会员权益说明页
- `kaipai-admin/src/views/content/TemplatesView.vue`
- 主题 token 配置页
- 分享产物配置页
- 发布日志页

### 7.2 运营侧关键动作

- 创建 / 编辑 / 启停用会员产品
- 为用户开通、延期、关闭会员
- 配置不同模板对应的等级和会员门槛
- 调整主题 token 和分享产物预设
- 执行模板发布、回滚和版本回看

## 8. 小程序 / 前台交付

### 8.1 页面落点

- `pkg-card/membership/index`
- `pkg-card/actor-card/index`
- `pages/actor-profile/detail`
- `pkg-card/fortune/index`
- `pkg-card/invite/index`

### 8.2 前端 gating / 展示 / 回写

- 等级中心作为能力说明中心，区分等级能力与会员能力
- 名片页按模板 / 等级 / 会员 / 命理结果恢复场景和主题
- 公开详情页消费统一主题与分享产物参数
- 命理页和邀请页消费同一套能力结果，不再各自写一套“可用能力”判断
- 前台不得硬编码完整模板库，只消费后端下发与 resolver 聚合结果

## 9. 联调点

- 后台修改会员账户后，小程序能力状态同步变化
- 后台发布模板 / 主题 / 分享产物后，名片页和公开详情页可恢复最新配置
- 非会员只能使用基础产物，会员产物 gating 生效
- 模板回滚后，前台恢复到指定版本表现
- 模板配置、会员状态、邀请等级共同影响最终分享结果，但展示口径保持一致

## 10. 当前阻塞项

- 真实会员支付和退款链路仍是平台侧能力，前台消费需避免假装“已完全商业化”
- 模板 / 主题 / 产物配置虽已有后台与服务端骨架，但前台仍需继续减少本地散写规则
- 会员能力、等级能力和个性化结果之间的 resolver 口径需要继续收口

## 11. 建议推进顺序

1. 数据与状态
2. 后端规则与接口
3. 后台治理入口
4. 小程序前台回接
5. 联调与验收

### 11.1 第一步：数据与状态

- 锁定 `membership_*`、`payment_*`、`refund_*`、`card_scene_template`、`template_publish_log` 的边界
- 锁定模板状态、会员状态、产物能力状态口径
- 锁定等级 / 会员 / 模板 / 资格四者的消费关系

### 11.2 第二步：后端规则与接口

- 先打通会员产品、会员账户、模板、主题 token、分享产物的后台接口
- 再统一输出前台消费的能力和主题结果
- 把模板发布、回滚、能力 gating 收口到后端和 resolver

### 11.3 第三步：后台治理入口

- 优先保证运营能配产品、配模板、发会员、看版本
- 不要只做前台名片页而缺少后台权威配置来源

### 11.4 第四步：小程序前台回接

- 等级中心承接能力解释
- 名片页、公开详情页、邀请页、命理页统一消费配置结果
- 验证基础产物、会员产物、个性化产物的差异化表现

### 11.5 第五步：联调与验收

- 跑通“后台配置 -> 后端下发 -> 前台恢复”的完整链路
- 验证模板版本、会员状态、产物 gating 和日志追溯

## 12. 完成定义

### 12.1 局部完成

以下只能算局部完成：

- 只有会员页说明，没有后台会员产品和账户治理
- 只有模板配置页，没有前台恢复链路
- 只有前台 gating，没有后端统一能力口径
- 只有模板草稿，没有发布 / 回滚和日志

### 12.2 闭环完成

以下同时满足，才能算闭环完成：

- 后台可维护会员产品、会员账户和权益说明
- 后台可维护模板、主题 token、分享产物并执行发布 / 回滚
- 后端可统一输出会员状态、模板状态和分享产物 gating
- 小程序名片页、等级中心、公开详情页、邀请页、命理页消费同一口径
- 模板变更、会员变更、发布回滚动作可追溯
- 前台不再依赖散落页面的本地规则来判断模板和能力
