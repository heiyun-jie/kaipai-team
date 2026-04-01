# 实名认证闭环切片卡

## 1. 切片名称

实名认证闭环

## 2. 切片目标

让演员在小程序完成实名认证提交，平台在后台完成审核，审核结果稳定回写到用户实名状态、演员认证状态和前台能力 gating，并形成可追溯的后台操作记录。

## 3. 上位 Spec

- `00-10 platform-admin-backend-architecture`
- `00-11 platform-admin-console`
- `00-28 architecture-driven-delivery-governance`
- `05-09 identity-verification`
- `05-05 card-share-membership`
- `05-10 invite-referral`

## 4. 业务范围

### 4.1 本轮范围

- 演员端实名认证提交与状态查询
- 后台待审核 / 历史记录 / 详情 / 通过 / 拒绝
- 审核结果回写 `user` 与 `actor_profile`
- 名片页、等级中心、邀请资格等前置条件联动
- 敏感信息脱敏展示、后台审计和操作日志

### 4.2 不在本轮范围

- 第三方公安实名核验
- 人脸识别或活体检测
- 企业 / 剧组认证
- 申诉、人工客服复核流程

## 5. 数据与状态模型

### 5.1 关键实体 / 表

- `identity_verification`
- `user.realAuthStatus`
- `actor_profile.isCertified`
- `actor_profile.realName`
- `admin_operation_log`

### 5.2 关键状态

- 前台用户态：
  - `0` 未认证
  - `1` 认证中
  - `2` 已认证
  - `3` 认证失败
- 审核态：
  - 待审核
  - 审核通过
  - 审核拒绝

### 5.3 状态流转

```text
未认证
  -> 提交实名
  -> 认证中 / 待审核
     -> 后台通过
        -> user.realAuthStatus = 2
        -> actor_profile.isCertified = true
        -> actor_profile.realName 回写
     -> 后台拒绝
        -> user.realAuthStatus = 3
        -> 记录 rejectReason
        -> 前台允许重新提交
```

## 6. 后端交付

### 6.1 核心接口

- 演员端：
  - `GET /api/verify/status`
  - `POST /api/verify/submit`
- 后台端：
  - `GET /api/admin/verify/list`
  - `GET /api/admin/verify/{id}`
  - `POST /api/admin/verify/{id}/approve`
  - `POST /api/admin/verify/{id}/reject`

### 6.2 核心服务规则

- 同一用户同一时间只能存在一条待审核申请
- 身份证号后端加密存储，前端和低权限页面只展示脱敏值
- 审核通过时同步更新 `user.realAuthStatus`、`actor_profile.isCertified`、`actor_profile.realName`
- 审核拒绝必须填写原因，前台需要可见
- 认证失败后允许重新提交，但必须保留审核历史

### 6.3 安全 / 权限 / 审计

- 敏感字段查看必须受后台权限控制
- 审核通过 / 拒绝必须记录 `admin_operation_log`
- 后台接口走 `/api/admin/**`，不能复用前台接口拼装审核流程

## 7. 后台交付

### 7.1 管理页 / 治理动作

- 页面：
  - `kaipai-admin/src/views/verify/VerificationBoard.vue`
  - `kaipai-admin/src/views/verify/PendingView.vue`
  - `kaipai-admin/src/views/verify/HistoryView.vue`
- 接口：
  - `kaipai-admin/src/api/verify.ts`
- 能力：
  - 待审核列表
  - 历史记录
  - 详情抽屉
  - 审核通过
  - 审核拒绝

### 7.2 运营侧关键动作

- 按用户、状态、时间筛选待审核记录
- 查看实名申请详情与脱敏证件信息
- 填写备注后通过或拒绝
- 在审核后回看历史处理结果

## 8. 小程序 / 前台交付

### 8.1 页面落点

- `pkg-card/verify/index`
- `pages/mine/index`
- `pkg-card/membership/index`
- `pkg-card/actor-card/index`

### 8.2 前端 gating / 展示 / 回写

- 未认证用户在“我的”和等级中心看到“去认证”入口
- 认证中展示“审核中”，禁止重复提交
- 认证失败展示拒绝原因和“重新提交”
- 名片生成、邀请裂变、等级能力需消费认证状态
- 前台登录态 / 用户态刷新后，认证状态要同步进入 `stores/user.ts`

## 9. 联调点

- 后台审核通过后，小程序侧状态必须同步变更
- 后台拒绝后，小程序侧必须可见拒绝原因
- 名片页、等级中心、邀请页对认证前置条件的判断必须统一
- 后台审核动作必须可在操作日志中追踪

## 10. 当前阻塞项

- `05-09` 的产品和前端基线已建，但第三方实名校验未接
- 需要确认演员端提交接口与当前 `VerifyController` 的最终契约
- 需要确认 `档案完成度 >= 70%` 的前置判断由谁作为权威输出
- 需要确认后台敏感字段查看权限与脱敏策略的最终口径

## 11. 建议推进顺序

1. 数据与状态
   - 固化 `identity_verification` 表字段、唯一约束、索引和审核状态
   - 明确 `user.realAuthStatus` 与 `actor_profile.isCertified` 的回写口径
2. 后端规则与接口
   - 打通提交 / 状态查询 / 后台列表 / 详情 / 审核接口
   - 接入加密、重复申请限制和拒绝原因
3. 后台治理入口
   - 完成待审核、历史记录、详情抽屉、通过 / 拒绝动作
   - 对齐权限与操作日志
4. 小程序前台回接
   - 打通认证提交页
   - 在 mine / membership / actor-card 统一使用认证状态
5. 联调与验收
   - 校验审核结果回写
   - 校验前台 gating 一致
   - 校验日志可追溯

## 12. 完成定义

### 12.1 局部完成

- 只有认证提交页，没有后台审核入口
- 只有后台审核页，没有状态回写
- 有状态回写，但名片 / 邀请 / 等级页仍各自判断认证状态

### 12.2 闭环完成

- 演员可提交实名申请并查询状态
- 后台可列表查看、详情查看、通过 / 拒绝并记录原因
- 审核结果稳定回写 `user` 与 `actor_profile`
- 名片、等级、邀请等前台能力统一消费认证状态
- 敏感信息脱敏、权限控制和操作日志全部到位
