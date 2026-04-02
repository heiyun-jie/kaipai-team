# 邀请裂变联调样本登记模板

## 1. 用途

每次 invite 真实环境联调，都必须固定至少一组样本链，不允许这次看邀请码、下次看另一条 `referral_record`。

本模板用于登记同一样本在前台、后台、DB、日志四侧的证据。

## 2. 样本信息

### 基础信息

- 验证日期：
- 环境：
- 操作人：
- 目标结论：
  - 正常链路
  - 风险链路
  - 资格链路

### 样本主键

- inviterUserId：
- inviteCode：
- inviteCodeId：
- inviteeUserId：
- referralId：
- grantId：
- policyId：

## 3. 小程序证据

### 登录注册

- 登录页是否收到 `inviteCode / scene`：
- 注册请求是否带 `inviteCode`：
- 注册请求是否带 `deviceFingerprint`：
- 注册响应中的 `invitedByUserId`：
- 注册响应中的 `validInviteCount`：

### invite 页

- `inviteCode`：
- `validInviteCount`：
- `totalInviteCount`：
- `pendingInviteCount`：
- `flaggedInviteCount`：
- 邀请记录数量：
- 二维码返回值：

### level/info

- `inviteCount`：
- `level`：
- `profileCompletion`：
- `membershipTier`：

## 4. 后台证据

### 邀请记录页

- 页面是否查到样本：
- `referralId`：
- `inviteCode`：
- `status`：
- `riskFlag`：
- `registeredAt`：
- `validatedAt`：

### 异常邀请页

- 页面是否查到样本：
- `riskReason`：
- 风控动作：
- 动作后状态：

### 邀请规则页

- 当前生效 `policyId`：
- `policyName`：
- `enabled`：
- `sameDeviceLimit`：
- `hourlyInviteLimit`：
- `autoGrantEnabled`：

### 邀请资格页

- 页面是否查到样本：
- `grantId`：
- `status`：
- `sourceType`：
- `sourceRefId`：
- `effectiveTime`：
- `expireTime`：

## 5. 数据库证据

### `invite_code`

- `invite_code_id`：
- `user_id`：
- `code`：
- `status`：

### `user`

- `user_id`：
- `invited_by_user_id`：
- `valid_invite_count`：
- `register_device_fingerprint`：

### `referral_record`

- `referral_id`：
- `inviter_user_id`：
- `invitee_user_id`：
- `invite_code_snapshot`：
- `status`：
- `risk_flag`：
- `risk_reason`：
- `registered_at`：
- `validated_at`：

### `user_entitlement_grant`

- `grant_id`：
- `user_id`：
- `grant_type`：
- `grant_code`：
- `status`：
- `source_type`：
- `source_ref_id`：

## 6. 一致性检查

- 小程序 `inviteCode` = `invite_code.code`：是 / 否
- 注册响应 `invitedByUserId` = `user.invited_by_user_id`：是 / 否
- `user.invited_by_user_id` = `referral_record.inviter_user_id`：是 / 否
- `referral_record.invitee_user_id` = 当前样本用户：是 / 否
- 小程序 `validInviteCount` = `/api/level/info inviteCount`：是 / 否
- `/api/level/info inviteCount` = `referral_record status=1` 数量：是 / 否
- `grant.source_ref_id` 是否指向当前样本链：是 / 否
- 后台页面与 DB 是否一致：是 / 否

## 7. 缺陷归因

### 前端

- 

### 后端

- 

### 后台

- 

### 环境 / 配置

- 

## 8. 本轮结论

- 当前判定：
  - 未开始
  - 局部完成
  - 可继续联调
  - 闭环完成
- 一句话结论：

## 9. 附件清单

- 小程序截图：
- 后台截图：
- API 响应：
- SQL 结果：
- 操作日志：
