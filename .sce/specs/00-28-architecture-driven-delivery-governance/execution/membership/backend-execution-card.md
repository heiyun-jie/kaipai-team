# 会员能力与模板配置闭环后端执行卡

## 1. 执行卡名称

会员能力与模板配置闭环 - 后端执行卡

## 2. 归属切片

- `../../slices/membership-template-capability-slice.md`

## 3. 负责范围

- 会员产品、会员账户、会员权益说明的后台接口与规则
- 场景模板、主题 token、分享产物配置、发布 / 回滚的后台接口与日志
- 小程序侧会员状态、模板配置、能力 gating、分享产物配置接口
- 会员、模板、邀请等级、资格权益的边界收口
- 审计日志、权限边界与聚合摘要输出

## 4. 不负责范围

- 小程序页面视觉、交互、海报绘制和分享文案
- 后台页面表格、弹窗和运营文案细节
- 真正的支付渠道接入、扣费与退款资金流
- 任何把会员、等级、资格混成一个布尔开关的临时实现

## 5. 关键输入

- 上位 Spec：
  - `00-10 platform-admin-backend-architecture`
  - `05-05 card-share-membership`
  - `05-11 fortune-driven-share-personalization`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/membership/MembershipController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/membership/AdminMembershipController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/membership/service/impl/MembershipProductServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/membership/service/impl/MembershipAccountServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/CardSceneTemplateServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/TemplatePublishLogServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorSharePreferenceServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/membership/entity/MembershipProduct.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/membership/entity/MembershipAccount.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/card/entity/CardSceneTemplate.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/card/entity/TemplatePublishLog.java`

## 6. 目标交付物

- `AdminMembershipController` 与 `AdminContentController` 对应的后台能力稳定可用
- `MembershipController` 与 `CardController` 不再是空壳，小程序侧可查询会员状态、模板配置、分享产物配置与能力结果
- 会员状态、等级状态、邀请资格、模板状态、分享产物门槛口径清楚
- 模板发布、回滚、主题调整、产物调整、会员开关都进入操作日志
- 前端可消费统一的能力与主题结果，而不是继续依赖本地完整规则库

## 7. 关键任务

1. 锁定领域边界
   - 区分 `membership_*`、`payment_*`、`refund_*`、`card_scene_template`、`user_entitlement_grant`
   - 明确会员状态、等级能力、邀请资格、模板能力各自职责
2. 打通小程序侧会员与模板接口
   - 当前 `MembershipController`、`CardController` 只有服务注入，没有实际接口
   - 补齐会员状态、能力查询、模板查询、主题配置、分享产物配置、公开详情恢复所需接口
3. 收口统一能力输出
   - 后端输出会员状态、模板状态、能力矩阵、产物锁定、命理增强可用性
   - 前端只做轻量聚合，不再自己定义完整能力真相
4. 稳定后台治理接口
   - 会员产品、会员账户、会员权益、模板、主题 token、分享产物、发布日志接口口径稳定
   - 详情、启停用、排序、发布、回滚、手工开通 / 延期 / 关闭均可追溯
5. 对齐日志与权限
   - 会员开通、关闭、延期
   - 模板创建、编辑、启停用、排序、发布、回滚
   - 主题 token 与分享产物编辑

## 8. 依赖项

- 前端要尽早冻结小程序侧能力 DTO，避免继续把 resolver 规则写回页面
- 后台路由和权限码要跟 `@PreAuthorize` 保持一致
- 若会员能力与模板恢复依赖演员卡片配置、分享偏好、命理结果，需要明确每类数据的唯一权威来源

## 9. 验证方式

- 后台产品、账户、模板、主题、产物配置变更后，对应接口返回稳定结果
- 小程序侧能拿到会员状态、模板状态、主题配置、产物能力和公开详情恢复所需字段
- 模板发布 / 回滚会写入 `template_publish_log` 与 `admin_operation_log`
- 会员开通 / 延期 / 关闭会写入 `membership_change_log` 与 `admin_operation_log`
- 不存在把会员状态、邀请资格或模板状态混为同一字段的情况

## 10. 完成定义

- 后台端与小程序端接口都具备
- 会员、模板、产物、命理增强的后端事实口径统一
- 演员端控制器不再是空壳，能够真实支撑前端恢复
- 模板和会员治理动作可追溯
- 后端可以支撑“后台配置驱动前台恢复”的闭环联调

## 11. 风险与备注

- 当前 `AdminMembershipController` 与 `AdminContentController` 比演员端成熟得多，但 `MembershipController`、`CardController` 仍是空壳，这意味着后台并不等于闭环
- 若后端不尽快输出小程序侧能力摘要，前端本地 resolver 会继续膨胀，后续每加一个产物都要改多处页面
- 若会员、等级、资格、模板边界不清，任何一个新需求都会把 gating 逻辑再次搅乱
