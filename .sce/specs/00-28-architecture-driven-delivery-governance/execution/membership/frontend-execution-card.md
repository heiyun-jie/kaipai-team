# 会员能力与模板配置闭环前端执行卡

## 1. 执行卡名称

会员能力与模板配置闭环 - 小程序前端执行卡

## 2. 归属切片

- `../../slices/membership-template-capability-slice.md`

## 3. 负责范围

- 等级中心承接会员状态、等级能力、模板能力与分享产物说明
- 名片页、公开详情页、命理页、邀请页消费统一主题与能力结果
- `personalization / theme-resolver / share-artifact` 的前端聚合逻辑收口
- 模板、主题、分享产物在前端的恢复与展示
- AI 配额、会员能力、命理增强、邀请卡片能力的统一展示

## 4. 不负责范围

- `membership_*`、`payment_*`、`refund_*`、`card_scene_template` 表结构和落库规则
- 后台会员产品、会员账户、模板发布、主题 token 配置页面的实现
- 会员订单计费、支付、退款结算
- 脱离统一能力口径的单页视觉扩展

## 5. 关键输入

- 上位 Spec：
  - `00-27 mini-program-frontend-architecture`
  - `05-05 card-share-membership`
  - `05-11 fortune-driven-share-personalization`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipai-frontend/src/pkg-card/membership/index.vue`
  - `kaipai-frontend/src/pkg-card/actor-card/index.vue`
  - `kaipai-frontend/src/pages/actor-profile/detail.vue`
  - `kaipai-frontend/src/pkg-card/fortune/index.vue`
  - `kaipai-frontend/src/pkg-card/invite/index.vue`
  - `kaipai-frontend/src/utils/personalization.ts`
  - `kaipai-frontend/src/utils/theme-resolver.ts`
  - `kaipai-frontend/src/utils/share-artifact.ts`
  - `kaipai-frontend/src/api/personalization.ts`
  - `kaipai-frontend/src/stores/user.ts`

## 6. 目标交付物

- 等级中心不再只是静态说明页，而是展示真实会员状态、能力矩阵、模板与产物门槛
- 名片页、公开详情页、命理页、邀请页统一消费同一份 personalization 结果
- 模板、主题 token、分享产物配置从后台 / 后端权威来源恢复，而不是长期靠前端本地规则库
- 会员能力 gating 精确到分享产物维度，而不只是“能否进入页面”
- 前端不再私下维护另一套模板、主题、会员能力判断

## 7. 关键任务

1. 收口前端能力与主题数据源
   - 当前 `api/personalization.ts` 仍以 `getSceneTemplates`、`getActorCardConfig`、`getFortuneReport` 拼装结果
   - 当前 `theme-resolver.ts`、`share-artifact.ts` 仍承担大量本地规则推导
   - 需要明确哪些字段由后端直接下发，哪些仍可保留在前端做轻量聚合
2. 回接等级中心
   - `pkg-card/membership/index.vue` 展示真实会员状态、模板能力、分享产物数、AI 配额
   - 区分等级能力、会员能力、命理增强，不得混成单一“已开通 / 未开通”
3. 回接名片页与公开详情页
   - `pkg-card/actor-card/index.vue` 和 `pages/actor-profile/detail.vue` 统一消费模板、主题、产物配置
   - 模板变更、主题变更、回滚后前端能恢复对应结果
4. 回接命理页与邀请页
   - `pkg-card/fortune/index.vue` 与 `pkg-card/invite/index.vue` 共享同一能力口径
   - 命理增强和邀请卡片能力不再各自写锁定逻辑
5. 补齐前端验证说明
   - 非会员基础产物
   - 会员定制产物
   - 命理增强主题
   - 模板发布 / 回滚后的页面恢复结果

## 8. 依赖项

- 后端要先稳定小程序侧会员状态、模板配置、分享产物配置、能力摘要接口
- 后台模板 / 主题 / 产物配置必须是真实权威来源，否则前端无法完成“后台配置驱动前台恢复”
- `stores/user.ts` 中会员状态、实名状态、等级能力字段要保持唯一共享入口

## 9. 验证方式

- 后台开通 / 延期 / 关闭会员后，小程序等级中心、名片页、命理页能力同步变化
- 后台发布模板 / 更新主题 / 更新产物配置后，名片页和公开详情页恢复对应结果
- 非会员只能使用基础分享产物，会员产物锁定与解锁口径一致
- 邀请页、命理页、名片页使用同一套主题和能力结果，不出现 A 页有能力、B 页没有能力的分裂
- 模板回滚后，前端能够恢复到指定版本的展示效果

## 10. 完成定义

- 等级中心、名片页、公开详情页、命理页、邀请页都接回统一能力口径
- 前端不再维护完整模板库和产物规则库的第二套真相
- 会员能力、模板状态、产物 gating、命理增强的展示保持一致
- 能明确证明“后台配置变化会驱动前台恢复”
- 前端可以对闭环完成度给出明确判断，而不是只看到局部页面可用

## 11. 风险与备注

- 当前前端仍强依赖 `personalization.ts`、`theme-resolver.ts`、`share-artifact.ts` 本地 resolver，后端若不尽快输出权威字段，前端会越补越重
- `pages/actor-profile/detail.vue` 目前直接用本地模板与主题推导公开详情表现，模板发布 / 回滚若不回接真实配置，公开页会最先失真
- 若 `membership / actor-card / fortune / invite` 各自维护能力锁定逻辑，会员、等级、命理三条主线会继续分裂
