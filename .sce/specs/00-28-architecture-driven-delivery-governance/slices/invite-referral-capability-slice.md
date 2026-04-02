# 邀请裂变与邀请资格闭环切片卡

## 1. 切片名称

邀请裂变与邀请资格闭环

## 2. 切片目标

建立“已认证用户生成邀请码 -> 新用户注册绑定 -> 邀请记录与风险识别 -> 邀请资格 / 权益发放 -> 小程序邀请入口与分享产物联动”的完整闭环。

本切片的价值不只是补一个邀请页，而是为等级成长、资格发放、会员能力和统一分享产物体系提供可治理的数据来源。

## 3. 上位 Spec

- `00-10 platform-admin-backend-architecture`
- `00-11 platform-admin-console`
- `00-28 architecture-driven-delivery-governance`
- `05-09 identity-verification`
- `05-10 invite-referral`
- `05-11 fortune-driven-share-personalization`

## 4. 业务范围

### 4.1 本轮范围

- 已认证用户生成邀请码
- invite 二维码能力分两层理解：
  - 第一层：邀请码链接二维码
  - 第二层：微信官方 `wxacode`
- 注册流程处理 `inviteCode` 绑定
- 建立裂变邀请记录、有效邀请计数和风险标记
- 后台查看邀请记录、异常邀请、邀请规则和资格发放
- 根据规则或后台动作发放 / 撤销 / 延长邀请资格
- 邀请页、等级中心、名片页消费邀请统计和资格状态
- 邀请海报 / 邀请卡片纳入统一分享产物体系

### 4.2 不在本轮范围

- 现金返佣或积分奖励
- 多级裂变分账
- 团队邀请或渠道代理体系
- 独立营销活动平台

## 5. 数据与状态模型

### 5.1 关键实体 / 表

- `invite_code`
- `referral_record`
- `referral_policy`
- `user_entitlement_grant`
- `entitlement_rule`
- `user`（`invited_by_user_id`、`valid_invite_count` 等冗余字段）
- `admin_operation_log`

### 5.2 关键状态

#### 邀请记录状态

- 未生效
- 已生效
- 风险待复核
- 已作废

#### 资格状态

- 待生效
- 生效中
- 已撤销
- 已过期

### 5.3 状态流转

```text
邀请人已认证
  -> 生成 invite_code / qrcode
  -> 新用户带 inviteCode 注册
  -> 创建 referral_record（初始未生效）
  -> 满足资料完成度 / 风控规则
  -> referral_record 生效
  -> inviter.valid_invite_count 增长
  -> 触发等级重算或资格发放

若命中风险规则
  -> referral_record 标记为风险待复核
  -> 后台 risk 审核
  -> 通过 / 作废 / 复核完成

若有权益或资格发放
  -> 写入 user_entitlement_grant
  -> 小程序消费资格和能力 gating
```

## 6. 后端交付

### 6.1 核心接口

#### 小程序端

- `GET /api/invite/code`
- `GET /api/invite/qrcode`
- `GET /api/invite/records`
- `GET /api/invite/stats`
- `POST /api/auth/register`（新增 `inviteCode` 处理）

#### 后台端

- `GET /api/admin/referral/records`
- `GET /api/admin/referral/records/{id}`
- `GET /api/admin/referral/risk/list`
- `GET /api/admin/referral/risk/{id}`
- `POST /api/admin/referral/risk/{id}/approve`
- `POST /api/admin/referral/risk/{id}/invalidate`
- `POST /api/admin/referral/risk/{id}/resolve`
- `GET /api/admin/referral/policies`
- `POST /api/admin/referral/policies`
- `PUT /api/admin/referral/policies/{id}`
- `POST /api/admin/referral/policies/{id}/enable`
- `POST /api/admin/referral/policies/{id}/disable`
- `GET /api/admin/referral/eligibility`
- `GET /api/admin/referral/eligibility/{grantId}`
- `POST /api/admin/referral/eligibility/grant`
- `POST /api/admin/referral/eligibility/revoke`
- `POST /api/admin/referral/eligibility/extend`

### 6.2 核心服务规则

- 只有已实名认证用户才能生成邀请码
- 每个新用户只能绑定一次邀请关系
- 有效邀请需要满足注册完成和资料门槛，不等于仅扫码
- 同设备、多次高频注册等规则要写入风控判断，而不是只在前端提示
- 等级增长和资格发放必须消费同一份邀请事实数据
- 邀请资格、会员状态、等级状态不得混成同一个布尔字段

### 6.3 安全 / 权限 / 审计

- 风险审核、规则变更、资格发放都必须具备独立操作权限
- 高风险操作进入 `admin_operation_log`
- 邀请页只展示脱敏昵称和受控统计，不暴露敏感信息
- 邀请资格判断以前后端统一口径为准，不在页面本地推断

## 7. 后台交付

### 7.1 管理页 / 治理动作

- `kaipai-admin/src/views/referral/RiskView.vue`
- 邀请记录页
- 异常邀请复核页
- 邀请规则配置页
- 邀请资格发放页

### 7.2 运营侧关键动作

- 查看邀请记录、邀请码、邀请人与被邀请人关系
- 复核异常邀请，决定通过 / 作废 / 标记复核完成
- 配置实名前置、资料完整度、同设备限制、频次限制等规则
- 向用户发放、撤销、延期邀请资格或关联权益

## 8. 小程序 / 前台交付

### 8.1 页面落点

- `pkg-card/invite/index`
- `pkg-card/membership/index`
- `pkg-card/actor-card/index`
- `pages/login/index`

### 8.2 前端 gating / 展示 / 回写

- 登录页从分享链接接收 `inviteCode` 并参与注册
- 邀请页展示邀请码、统计、邀请记录和分享入口
- 名片页、等级中心展示邀请引导和资格摘要
- 邀请海报 / 邀请卡片必须使用统一主题与分享产物模型
- 页面只展示后端下发的统计与资格状态，不本地推断是否“可领奖”或“可升级”

## 9. 联调点

- 邀请链接注册后，后台邀请记录可见
- 被邀请人满足门槛后，邀请记录生效且邀请人数更新
- 风险记录在后台可复核，复核结果影响邀请有效性
- 资格发放后，小程序会员 / 名片 / 邀请页消费同一口径
- 邀请卡片、海报和小程序邀请入口主题保持一致

## 10. 当前阻塞项

- 邀请事实、资格事实、等级事实三套模型仍需持续收口，避免页面各写一套判断
- 注册链路的 `inviteCode` 参数与小程序分享入口需要做统一追踪
- 风险审核和资格发放虽有后台能力，但前台消费口径仍需继续统一到 resolver / 后端字段
- invite 当前已跑通的是“邀请码链接二维码 + API/DB 闭环”，尚未跑通“微信官方 `wxacode` + 真实扫码落地”
- 微信官方小程序码必须按独立子问题继续推进，执行入口固定为 `../execution/invite/wxacode-execution-card.md`

## 11. 建议推进顺序

1. 数据与状态
2. 后端规则与接口
3. 后台治理入口
4. 小程序前台回接
5. 联调与验收

### 11.1 第一步：数据与状态

- 锁定 `invite_code`、`referral_record`、`referral_policy`、`user_entitlement_grant` 的边界
- 锁定邀请生效、风险待复核、资格生效的状态口径
- 锁定 `valid_invite_count` 的冗余更新规则

### 11.2 第二步：后端规则与接口

- 打通注册绑定、邀请统计、邀请记录、风险审核、资格发放接口
- 把实名前置、资料门槛、设备限制、频率限制统一放后端
- 确保等级与资格消费同一份事实数据

### 11.3 第三步：后台治理入口

- 先让运营能看记录、看风险、配规则、发资格
- 不要只做前台邀请页而缺少后台治理闭环

### 11.4 第四步：小程序前台回接

- 登录页处理 `inviteCode`
- 邀请页和等级中心消费后端统计
- 名片页和邀请页接入统一邀请卡片 / 海报产物

### 11.5 第五步：联调与验收

- 跑通“邀请 -> 注册 -> 生效 -> 升级 / 发资格 -> 前台可见”的完整链路
- 校验风险记录、审核结果、资格动作和日志可追溯性

## 12. 完成定义

### 12.1 局部完成

以下只能算局部完成：

- 只有邀请页，没有注册绑定
- 只有统计，没有风险审核和资格发放
- 只有后台复核，没有小程序前台消费
- 只有海报入口，没有统一分享产物模型

### 12.2 闭环完成

以下同时满足，才能算闭环完成：

- 已认证用户可生成邀请码和微信官方小程序码
- 新用户注册可绑定邀请关系并形成记录
- 邀请有效性、风险状态和资格状态可在后台治理
- 等级、资格、邀请统计消费同一份后端事实数据
- 邀请页、等级中心、名片页和邀请卡片统一进入分享产物体系
- 规则变更、复核动作、资格发放均可追溯
