# 邀请裂变与邀请资格闭环前端执行卡

## 1. 执行卡名称

邀请裂变与邀请资格闭环 - 小程序前端执行卡

## 2. 归属切片

- `../../slices/invite-referral-capability-slice.md`

## 3. 负责范围

- 登录 / 注册页接收 `inviteCode` 并参与注册提交
- 邀请页展示邀请码、统计、邀请记录、分享入口和海报保存
- 名片页、等级中心消费邀请统计、实名 gating 和邀请能力摘要
- `stores/user.ts` 统一承接邀请码、邀请统计、实名状态、等级能力
- 邀请卡片 / 邀请海报纳入统一分享产物模型

## 4. 不负责范围

- `referral_record`、`invite_code`、`user_entitlement_grant` 表结构与状态机设计
- 风险审核、资格发放、规则配置等后端治理动作
- 后台管理页的权限码、菜单和运营交互
- 现金返佣、积分奖励、多级分销

## 5. 关键输入

- 上位 Spec：
  - `00-27 mini-program-frontend-architecture`
  - `05-10 invite-referral`
  - `05-11 fortune-driven-share-personalization`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipai-frontend/src/pages/login/index.vue`
  - `kaipai-frontend/src/pkg-card/invite/index.vue`
  - `kaipai-frontend/src/pkg-card/membership/index.vue`
  - `kaipai-frontend/src/pkg-card/actor-card/index.vue`
  - `kaipai-frontend/src/stores/user.ts`
  - `kaipai-frontend/src/api/invite.ts`
  - `kaipai-frontend/src/types/invite.ts`
  - `kaipai-frontend/src/utils/invite.ts`
  - `kaipai-frontend/src/utils/personalization.ts`
  - `kaipai-frontend/src/utils/share-artifact.ts`

## 6. 目标交付物

- 登录页可稳定接收分享链路中的 `inviteCode`，并在首次注册时提交给真实接口
- 邀请页消费真实邀请码、统计、记录和小程序码，不再长期依赖 mock
- `membership / actor-card / invite` 三处消费同一份邀请事实与资格摘要
- 邀请卡片、邀请海报、公开页分享产物保持同一主题体系
- 前端不再额外推断“是否可领奖 / 是否可升级”，只消费后端事实字段

## 7. 关键任务

1. 收口前端邀请数据源
   - 以 `stores/user.ts` 为共享入口承接 `inviteCode`、`validInviteCount`、实名状态和等级能力
   - 明确 `api/invite.ts` 与服务端 `referral` 契约的最终口径，避免长期一边叫 `invite` 一边叫 `referral`
2. 回接登录注册链路
   - `pages/login/index.vue` 接收分享参数并展示邀请提示
   - `registerByPhone` 首次注册时稳定透传 `inviteCode`
   - 登录模式下明确告知邀请码仅首次注册生效
3. 回接邀请页
   - `pkg-card/invite/index.vue` 消费真实邀请码、邀请记录和小程序码
   - 邀请按钮、复制链接、海报生成与实名 gating 对齐
   - 邀请记录状态只展示后端下发的 `valid / pending / review` 事实
4. 回接等级中心与名片页
   - `pkg-card/membership/index.vue` 展示邀请统计和能力矩阵
   - `pkg-card/actor-card/index.vue` 展示邀请入口、邀请码复制和统一分享产物
   - 邀请能力与会员主题共享同一套 personalization / share-artifact 口径
5. 补齐前端验证说明
   - 邀请链接进入登录页
   - 注册绑定成功后的页面表现
   - 邀请生效 / 风险待复核 / 资格生效时的前端展示矩阵

## 8. 依赖项

- 后端先稳定以下能力：
  - 注册接口真实处理 `inviteCode`
  - 小程序侧邀请码、统计、记录、小程序码接口
  - 邀请记录状态、资格摘要、实名前置字段的统一 DTO
- 后台风险审核和资格发放要能真实改变记录状态，否则前端无法完成闭环联调
- 统一分享产物模型要保留邀请卡片能力，不能被页面局部实现绕开

## 9. 验证方式

- 携带 `inviteCode` 进入登录页时，可见邀请提示，切到注册模式后完成注册
- 注册成功后，邀请记录在邀请页和后台都可追踪
- `invite / membership / actor-card` 三处的邀请码、邀请数、实名 gating 口径一致
- 已认证用户可发起分享，未认证用户被一致引导去认证
- 邀请卡片与邀请海报复用同一主题，不出现邀请链路单独一套视觉或参数口径

## 10. 完成定义

- 登录注册、邀请页、等级中心、名片页都接回真实邀请链路
- 前端共享状态统一承接邀请事实和资格摘要
- 邀请展示与分享产物统一进入同一主题体系
- 不再存在页面各自维护第二套邀请码、邀请统计或资格判断
- 前端可以明确给出“邀请闭环已打通”或“仍缺后端契约”的判断

## 11. 风险与备注

- 当前 `kaipai-frontend/src/api/invite.ts` 使用 `/api/invite/*`，而服务端演员端控制器实际是 `ReferralController` 且尚未实现，接口命名与落地存在硬断层
- `utils/invite.ts` 会根据统计推导 `pendingInviteCount`，该推导只能用于展示文案，不能外溢成资格判断
- 若 `membership / actor-card / invite` 不统一消费 `stores/user.ts` 和后端字段，邀请、会员、实名三条 gating 很快会再次分裂
