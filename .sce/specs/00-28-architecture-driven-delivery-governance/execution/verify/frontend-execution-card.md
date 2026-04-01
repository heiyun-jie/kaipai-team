# 实名认证闭环前端执行卡

## 1. 执行卡名称

实名认证闭环 - 小程序前端执行卡

## 2. 归属切片

- `../../slices/verify-capability-slice.md`

## 3. 负责范围

- 小程序实名认证提交页
- 小程序实名认证状态展示
- 小程序实名状态回接到共享用户态
- 名片页、等级中心、“我的”页对实名状态的统一消费
- 提交中、失败、拒绝原因、重提入口等前端体验

## 4. 不负责范围

- `identity_verification` 表结构设计
- 后端加密、审核、回写和日志落库
- 后台审核页权限与操作日志实现
- 第三方实名核验

## 5. 关键输入

- 上位 Spec：
  - `00-27 mini-program-frontend-architecture`
  - `05-09 identity-verification`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipai-frontend/src/pkg-card/verify/index.vue`
  - `kaipai-frontend/src/pages/mine/index.vue`
  - `kaipai-frontend/src/pkg-card/membership/index.vue`
  - `kaipai-frontend/src/pkg-card/actor-card/index.vue`
  - `kaipai-frontend/src/stores/user.ts`
  - `kaipai-frontend/src/api/verify.ts`
  - `kaipai-frontend/src/types/verify.ts`
  - `kaipai-frontend/src/utils/verify.ts`

## 6. 目标交付物

- 实名认证页完成真实提交、状态查询、失败提示和重提入口
- `stores/user.ts` 统一承接认证状态
- “我的”、等级中心、名片页统一消费同一份实名状态
- 拒绝原因、审核中、已认证三种关键状态在前端展示清楚
- 前端不再散写一套本地实名判断逻辑

## 7. 关键任务

1. 盘点并统一前端实名状态来源
   - 确认 `stores/user.ts` 中的实名状态字段
   - 清理页面内散落的本地推断
2. 回接实名认证页
   - 提交表单调用真实 `verify` API
   - 审核中禁止重复提交
   - 认证失败展示拒绝原因
   - 允许重提
3. 回接实名状态消费页
   - `pages/mine/index.vue`
   - `pkg-card/membership/index.vue`
   - `pkg-card/actor-card/index.vue`
4. 统一前端 gating
   - 未认证引导去认证
   - 已认证放行
   - 审核中提示等待
   - 认证失败允许重新提交
5. 补齐前端验证说明
   - 状态流转
   - 页面表现
   - 依赖的后端字段

## 8. 依赖项

- 后端先稳定以下能力：
  - 提交接口
  - 状态查询接口
  - 审核结果回写 `user.realAuthStatus`
  - 拒绝原因返回口径
- 后台审核链路要能真实改变状态，否则前端无法完成联调

## 9. 验证方式

- 提交实名申请后，实名认证页进入“审核中”
- 后台审核通过后，重新进入小程序或刷新用户态，状态变为“已认证”
- 后台审核拒绝后，小程序可见拒绝原因
- `mine / membership / actor-card` 三处实名状态口径一致
- 未认证用户进入需要实名前置的能力时，提示一致，不出现页面 A 可进、页面 B 不可进的分裂

## 10. 完成定义

- 实名认证页可完成真实提交与状态展示
- 用户共享状态统一承接实名结果
- 三个关键消费页统一使用同一份实名状态
- 拒绝原因和重提入口可用
- 不再存在页面私下维护的第二套实名判断

## 11. 风险与备注

- 若后端拒绝原因字段或状态枚举未定，前端容易写出临时兼容分支
- 若 `stores/user.ts` 不作为唯一状态入口，后续邀请和会员 gating 仍会分裂
- 前端这张执行卡默认以后端契约为准，不通过前端兼容逻辑掩盖后端状态问题
