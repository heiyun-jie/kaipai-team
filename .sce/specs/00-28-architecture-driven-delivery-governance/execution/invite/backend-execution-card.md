# 邀请裂变与邀请资格闭环后端执行卡

## 1. 执行卡名称

邀请裂变与邀请资格闭环 - 后端执行卡

## 2. 归属切片

- `../../slices/invite-referral-capability-slice.md`

## 3. 负责范围

- `invite_code`、`referral_record`、`referral_policy`、`user_entitlement_grant` 的模型边界和状态流转
- 注册接口处理 `inviteCode`，建立邀请关系与风险标记
- 演员端邀请码、统计、记录、小程序码接口
- 后台邀请记录、风险复核、规则配置、资格发放接口稳定化
- 操作日志、权限边界与聚合字段回写

## 4. 不负责范围

- 小程序页面交互、海报绘制、分享文案
- 后台前端页面布局、表格交互和运营提示
- 现金返佣、积分发放、多级分销
- 任何复用旧 `invite_record` 剧组邀约语义的实现

## 5. 关键输入

- 上位 Spec：
  - `00-10 platform-admin-backend-architecture`
  - `05-10 invite-referral`
  - `05-11 fortune-driven-share-personalization`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/referral/ReferralController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/referral/AdminReferralController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/ReferralRecordService.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/impl/ReferralRecordServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/impl/ReferralPolicyServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/impl/UserEntitlementGrantServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/impl/InviteCodeServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/user/service/impl/UserServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/referral/entity/InviteCode.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/referral/entity/ReferralRecord.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/invite/entity/InviteRecord.java`
  - `kaipaile-server/src/main/resources/db/migration/V20260331_001__platform_admin_baseline.sql`

## 6. 目标交付物

- `ReferralController` 不再是空壳，演员端邀请码 / 记录 / 统计 / 小程序码接口可用
- `/api/auth/register` 真实处理 `inviteCode`，形成唯一邀请关系并回写 `user.invitedByUserId`
- 邀请记录的待生效 / 已生效 / 风险待复核 / 已作废状态机清楚且可追溯
- 规则变更、风险复核、资格发放进入 `admin_operation_log`
- 裂变邀请统一落在 `referral_*` 模型，不复用旧 `invite_record`

## 7. 关键任务

1. 锁定领域边界
   - 明确 `InviteRecord` 继续代表剧组邀约，不进入裂变邀请链路
   - 明确 `ReferralRecord`、`InviteCode`、`UserEntitlementGrant` 的职责和关联关系
2. 打通演员端接口
   - 当前 `ReferralController` 已挂在 `/referral` 下但没有实际方法
   - 补齐邀请码、邀请记录、邀请统计、小程序码接口
   - 明确是否兼容前端现有 `/api/invite/*` 命名，至少不能继续让前端与服务端长期双口径
3. 打通注册绑定链路
   - `/api/auth/register` 处理 `inviteCode`
   - 一个新用户只能绑定一次邀请关系
   - 记录 `inviteCodeSnapshot`、设备指纹、初始状态、风险原因
4. 固化生效与风险规则
   - 已认证前置、资料完成度门槛、同设备限制、同小时频次限制进入后端
   - 邀请记录生效后再增长 `user.validInviteCount`
   - 风险记录进入后台复核，而不是由前端自行“看起来像异常”
5. 收口资格发放与聚合摘要
   - 规则配置、手工发放、撤销、延期的接口 DTO 稳定
   - 用户聚合摘要中的邀请码、邀请数、资格状态与邀请事实保持一致
   - 资格、等级、邀请统计消费同一份后端事实数据

## 8. 依赖项

- 前端要尽早锁定演员端接口命名和字段口径，避免 `/invite` 与 `/referral` 双命名长期并存
- 后台权限码、路由和页面入口要与 `@PreAuthorize` 一致
- 实名前置、资料完成度和等级重算如果依赖其他域服务，需要明确唯一权威来源

## 9. 验证方式

- `POST /api/auth/register` 携带 `inviteCode` 后，用户成功绑定邀请关系并创建 `referral_record`
- `GET /api/referral/code`、`/records`、`/stats`、`/qrcode` 或等效兼容接口返回稳定结果
- 邀请记录进入风险待复核后，可被后台通过 / 作废 / 复核完成，并记录操作日志
- 资格发放、撤销、延期接口可真实改变 `user_entitlement_grant`
- `invite_record` 旧模型不参与裂变邀请链路，避免两套业务共表

## 10. 完成定义

- 演员端与后台端邀请接口都可用
- 注册绑定、邀请生效、风险复核、资格发放链路闭环
- 用户聚合摘要和后台详情使用同一份邀请事实
- 日志、权限、状态机和幂等规则清楚
- 后端可以支撑小程序和后台的真实联调，而不是仅有管理端半成品

## 11. 风险与备注

- 当前 `ReferralController` 已具备演员端 `code / stats / records / qrcode` 接口，最大的剩余后端阻塞已从“接口不存在”收敛为“二维码虽已真实生成，但仍不是微信官方小程序码”
- `kaipai-frontend` 与后端当前通过 `/api/invite/*` 兼容层对齐；若后续移除兼容层，必须先同步前端与联调脚本，不能再次制造双口径
- 当前仓内没有微信小程序 `appid / secret` 或现成 `wxacode.getUnlimited` 调用基础，因此不能把“邀请码链接二维码”误写成“官方小程序码已接通”
- 若为了图快把裂变邀请塞回 `invite_record`，会直接破坏 `00-10` 已锁定的领域边界
