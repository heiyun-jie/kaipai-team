# 实名认证闭环后端执行卡

## 1. 执行卡名称

实名认证闭环 - 后端执行卡

## 2. 归属切片

- `../../slices/verify-capability-slice.md`

## 3. 负责范围

- `identity_verification` 数据模型与状态流转
- 演员端提交与状态查询接口
- 后台列表、详情、审核通过、审核拒绝接口
- 审核结果回写 `user` 与 `actor_profile`
- 操作日志和权限边界配合

## 4. 不负责范围

- 小程序页面交互和展示细节
- 后台前端页面布局和交互文案
- 第三方公安核验、人脸识别
- 前端页面上的引导和兜底文案

## 5. 关键输入

- 上位 Spec：
  - `00-10 platform-admin-backend-architecture`
  - `05-09 identity-verification`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/verify/VerifyController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/verify/AdminVerifyController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/IdentityVerificationService.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/impl/IdentityVerificationServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/verify/mapper/IdentityVerificationMapper.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/verify/entity/IdentityVerification.java`
  - `kaipaile-server/src/main/resources/db/migration/V20260331_001__platform_admin_baseline.sql`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/user/entity/User.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/actor/entity/ActorProfile.java`

## 6. 目标交付物

- 实名认证提交、状态查询、后台审核接口口径稳定
- `identity_verification` 状态流转和唯一约束清楚
- 审核结果稳定回写 `user.realAuthStatus`、`actor_profile.isCertified`、`actor_profile.realName`
- 审核动作进入操作日志
- 敏感字段加密存储、对外脱敏展示

## 7. 关键任务

1. 固化数据模型
   - 校验 `identity_verification` 字段、索引、唯一约束
   - 明确一人同一时间只能存在一条待审核记录
2. 固化状态机
   - 未认证
   - 审核中
   - 已认证
   - 认证失败
3. 打通演员端接口
   - 提交实名
   - 查询当前状态
   - 控制重复提交与失败重提
4. 打通后台端接口
   - 列表
   - 详情
   - 审核通过
   - 审核拒绝
5. 审核回写与审计
   - 同步更新 `user` 与 `actor_profile`
   - 记录 `admin_operation_log`
   - 输出前端可消费的拒绝原因和审核时间

## 8. 依赖项

- 需要后台权限码和审核动作口径与 `00-11` 对齐
- 需要前端消费字段尽早锁定，避免 DTO 反复改名
- 档案完成度门槛如果作为提交前置，需要明确由哪个服务负责输出

## 9. 验证方式

- `POST /api/verify/submit` 提交后，新纪录进入待审核
- `GET /api/verify/status` 返回统一状态口径
- 后台通过后，`user.realAuthStatus` 与 `actor_profile.isCertified` 被正确回写
- 后台拒绝后，拒绝原因可被前端读取
- 重复审核和重复待审提交被正确阻断
- 操作日志写入 `verify` 模块，目标为 `identity_verification`

## 10. 完成定义

- 演员端接口和后台接口均可用
- 状态回写稳定且幂等
- 数据约束、状态机和拒绝重提逻辑清楚
- 敏感字段安全要求满足
- 日志和权限所需字段已准备齐全

## 11. 风险与备注

- 若 `identity_verification` 与 `user.realAuthStatus` 不同步，前台一定会出现状态分裂
- 若 DTO 返回口径不稳定，前端和后台会被迫各做兼容
- 若操作日志缺失，后台审核链路无法满足平台治理要求
