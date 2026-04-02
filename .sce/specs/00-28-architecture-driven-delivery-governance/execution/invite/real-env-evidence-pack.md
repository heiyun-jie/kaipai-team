# 邀请裂变真实环境证据包

## 1. 用途

本文件用于把 invite 闭环联调从“口头确认”收口成“同一样本链证据确认”。

固定验证链：

`invite_code -> user.invitedByUserId -> referral_record -> user_entitlement_grant -> 前台 invite / level 状态`

## 2. 当前必须说明的前提

### 2.1 `/invite` 是兼容层，不是另一套新领域

- 服务端演员端控制器挂载在：
  - `@RequestMapping({"/referral", "/invite"})`
- 前端当前仍请求：
  - `/api/invite/code`
  - `/api/invite/stats`
  - `/api/invite/records`
  - `/api/invite/qrcode`
- 联调结论必须明确写成“当前通过兼容层跑通”，不能误写成“命名已完全统一”。

### 2.2 二维码已脱离占位图，但仍不是微信官方小程序码

- `/invite/code` 当前返回的 `qrCodeUrl` 已改成后端实时生成的邀请码链接二维码内容
- `/invite/qrcode` 当前也返回同一份二维码图片内容，不再直接返回 `/static/logo.png`
- 这只能证明“前端已开始消费真实二维码字段”，仍不能据此宣告“微信官方小程序码已闭环”。
- `2026-04-03` 的真实自动样本 `invite-20260403-030705-remote-invite-auto` 已确认这两个接口在公网都返回 `200`，因此当前阻塞已从“二维码接口业务 500”收敛为“资格链与微信官方码未闭环”

## 3. 前台证据点

### 3.1 小程序邀请页

- 页面：
  - `kaipai-frontend/src/pkg-card/invite/index.vue`
- 必截字段：
  - 邀请码
  - 有效邀请数
  - 总邀请数
  - 待生效数
  - 风险标记数
  - 邀请记录列表
- 对应接口：
  - `GET /api/invite/code`
  - `GET /api/invite/stats`
  - `GET /api/invite/records`
  - `GET /api/invite/qrcode`

### 3.2 登录注册页

- 页面：
  - `kaipai-frontend/src/pages/login/index.vue`
- 必截字段：
  - `inviteCode` 或 `scene` 被正确解析
  - 注册成功后的用户身份
- 对应请求关键点：
  - 注册请求带 `inviteCode`
  - 注册请求带 `deviceFingerprint`

### 3.3 等级 / 能力摘要

- 前端消费：
  - `GET /api/level/info`
- 关键字段：
  - `inviteCount`
  - `level`
  - `profileCompletion`
  - `membershipTier`
  - `shareCapability`
- 说明：
  - 前端 `userStore.syncLevelInfo()` 会把 `inviteCount` 回写到本地 `validInviteCount`
  - 所以 invite 页与 level 页口径必须一起比对，不能只看一个页面

## 4. 后台证据点

### 4.1 邀请记录

- 页面：
  - `/referral/records`
- 必截字段：
  - `referralId`
  - `inviteCode`
  - `inviterUserId`
  - `inviteeUserId`
  - `status`
  - `riskFlag`
  - `registeredAt`
  - `validatedAt`

### 4.2 异常邀请

- 页面：
  - `/referral/risk`
- 必截字段：
  - `riskReason`
  - `registerDeviceFingerprint`
  - `sameHourHitSummary`
  - 审核动作结果

### 4.3 邀请规则

- 页面：
  - `/referral/policies`
- 必截字段：
  - `policyId`
  - `policyName`
  - `enabled`
  - `requireRealAuth`
  - `requireProfileCompletion`
  - `profileCompletionThreshold`
  - `sameDeviceLimit`
  - `hourlyInviteLimit`
  - `autoGrantEnabled`
  - `grantRuleJson`

### 4.4 邀请资格

- 页面：
  - `/referral/eligibility`
- 必截字段：
  - `grantId`
  - `userId`
  - `grantType`
  - `grantCode`
  - `status`
  - `sourceType`
  - `sourceRefId`
  - `effectiveTime`
  - `expireTime`

## 5. 数据库证据点

## 5.1 表与关键字段

### `invite_code`

- `invite_code_id`
- `user_id`
- `code`
- `status`

### `user`

- `user_id`
- `invited_by_user_id`
- `valid_invite_count`
- `register_device_fingerprint`
- `real_auth_status`
- `create_time`

### `referral_record`

- `referral_id`
- `inviter_user_id`
- `invitee_user_id`
- `invite_code_id`
- `invite_code_snapshot`
- `register_device_fingerprint`
- `status`
- `risk_flag`
- `risk_reason`
- `registered_at`
- `validated_at`

### `user_entitlement_grant`

- `grant_id`
- `user_id`
- `grant_type`
- `grant_code`
- `status`
- `effective_time`
- `expire_time`
- `source_type`
- `source_ref_id`
- `remark`

### `admin_operation_log`

- `operation_log_id`
- `module_code`
- `operation_code`
- `target_type`
- `target_id`
- `operation_result`
- `before_snapshot_json`
- `after_snapshot_json`
- `extra_context_json`
- `create_time`

## 5.2 推荐 SQL 模板

### 按邀请码找邀请码主记录

```sql
SELECT
  invite_code_id,
  user_id,
  code,
  status,
  create_time,
  last_update
FROM invite_code
WHERE code = UPPER(:inviteCode);
```

### 按被邀请人确认用户绑定关系

```sql
SELECT
  user_id,
  user_name,
  phone,
  invited_by_user_id,
  valid_invite_count,
  register_device_fingerprint,
  real_auth_status,
  create_time
FROM user
WHERE user_id = :inviteeUserId;
```

### 按被邀请人或邀请码查邀请记录

```sql
SELECT
  referral_id,
  inviter_user_id,
  invitee_user_id,
  invite_code_id,
  invite_code_snapshot,
  register_device_fingerprint,
  status,
  risk_flag,
  risk_reason,
  registered_at,
  validated_at,
  create_time,
  last_update
FROM referral_record
WHERE invitee_user_id = :inviteeUserId
   OR invite_code_snapshot = UPPER(:inviteCode)
ORDER BY referral_id DESC;
```

### 按邀请人统计同一邀请码的记录状态

```sql
SELECT
  inviter_user_id,
  invite_code_snapshot,
  COUNT(*) AS total_count,
  SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) AS pending_count,
  SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) AS valid_count,
  SUM(CASE WHEN status = 2 THEN 1 ELSE 0 END) AS invalid_count,
  SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END) AS review_count,
  SUM(CASE WHEN risk_flag = 1 THEN 1 ELSE 0 END) AS flagged_count
FROM referral_record
WHERE inviter_user_id = :inviterUserId
GROUP BY inviter_user_id, invite_code_snapshot;
```

### 按 referralId 查资格记录是否来自同一事实链

```sql
SELECT
  grant_id,
  user_id,
  grant_type,
  grant_code,
  status,
  source_type,
  source_ref_id,
  effective_time,
  expire_time,
  remark,
  create_time,
  last_update
FROM user_entitlement_grant
WHERE user_id = :inviteeUserId
   OR source_ref_id = :referralId
ORDER BY grant_id DESC;
```

### 按资格记录查后台操作日志

```sql
SELECT
  operation_log_id,
  module_code,
  operation_code,
  target_type,
  target_id,
  operation_result,
  before_snapshot_json,
  after_snapshot_json,
  extra_context_json,
  create_time
FROM admin_operation_log
WHERE module_code = 'referral'
  AND (
    (target_type = 'referral_record' AND target_id = :referralId)
    OR (target_type = 'user_entitlement_grant' AND target_id = :grantId)
    OR (target_type = 'referral_policy' AND target_id = :policyId)
  )
ORDER BY operation_log_id DESC;
```

## 6. 状态机口径

### 6.1 `referral_record.status`

- `0`: 待生效
- `1`: 有效
- `2`: 已作废
- `3`: 复核中

### 6.2 `referral_record.risk_flag`

- `0`: 无风险
- `1`: 命中风险

### 6.3 `user_entitlement_grant.status`

- `1`: 生效中
- `2`: 已过期
- `3`: 已撤销

## 7. 同一样本链的最小比对矩阵

| 证据面 | 必须一致的字段 | 样本值 |
|-------|---------------|--------|
| 小程序 invite 页 | `inviteCode`、`validInviteCount`、邀请记录条数 | |
| 小程序 level/info | `inviteCount` | |
| 登录注册响应 | `invitedByUserId`、`validInviteCount` | |
| `invite_code` | `code`、`user_id` | |
| `user` | `invited_by_user_id`、`valid_invite_count` | |
| `referral_record` | `referral_id`、`inviter_user_id`、`invitee_user_id`、`invite_code_snapshot`、`status` | |
| `user_entitlement_grant` | `grant_id`、`user_id`、`source_type`、`source_ref_id`、`status` | |
| 后台邀请记录页 | `referralId`、`inviteCode`、`status`、`riskFlag` | |
| 后台资格页 | `grantId`、`sourceType`、`sourceRefId`、`status` | |

## 8. 当前不能误判为完成的点

满足以下任一条，都不能写“invite 闭环完成”：

- 二维码虽然不再是 `/static/logo.png` 占位，但仍未验证微信官方小程序码能力与真实扫码打开路径
- 只验证了 `/invite/*` 兼容接口能返回数据，但没有验证注册绑定
- `user.valid_invite_count` 与 `referral_record status=1` 数量不一致
- 有资格记录，但 `source_ref_id` 与当前样本链无关
- `2026-04-03` 的真实样本里，`inviteeUserId=10014` 对应的后台资格列表为空，因此当前还不能宣告 `referral_record -> user_entitlement_grant` 已形成同一事实链
- 后台动作后，小程序 invite 页或 `/api/level/info` 没同步变化

## 9. 建议执行顺序

1. 固定样本 `inviterUserId / inviteCode / inviteeUserId`
2. 先抓前台请求与返回
3. 再查 `user` / `referral_record` / `user_entitlement_grant`
4. 再看后台记录 / 风险 / 资格页面
5. 最后回填 `status/invite-status.md`
