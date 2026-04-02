# 登录鉴权真实环境证据包

## 1. 用途

本文件用于把 login-auth 联调从“口头确认”收口成“同一样本链证据确认”。

固定验证链：

`auth.sendCode -> auth.login / auth.register / auth.wechat-login -> token -> user.me -> verify / invite / level`

## 2. 前台证据点

### 2.1 登录页

- 页面：
  - `kaipai-frontend/src/pages/login/index.vue`
- 必截字段：
  - 手机号
  - `inviteCode` 或 `scene`
  - 当前是否显示微信按钮
  - 当前是否显示“稍后接入”降级提示
  - 当前是否出现运行时阻塞提示

### 2.2 会话恢复

- 入口：
  - `kaipai-frontend/src/stores/user.ts`
- 必截字段：
  - `bootstrapSession`
  - `syncActorRuntimeState`
- 对应接口：
  - `GET /api/user/me`
  - `GET /api/verify/status`
  - `GET /api/invite/stats`
  - `GET /api/level/info`

## 3. 接口证据点

### 3.1 认证接口

- `POST /api/auth/sendCode`
- `POST /api/auth/login`
- `POST /api/auth/register`
- `POST /api/auth/wechat-login`
- 若尚未具备人工微信授权条件，至少补一组 `run-login-auth-validation.ps1 -EnableLiveProbe` 自动生成的：
  - `captures/live-probe-sendCode.json`
  - `captures/live-probe-wechat-login.json`

### 3.2 用户与摘要接口

- `GET /api/user/me`
- `PUT /api/user/role`
- `GET /api/verify/status`
- `GET /api/invite/stats`
- `GET /api/level/info`

### 3.3 必核字段

- 登录返回：
  - `token`
  - `userId`
  - `userType`
  - `realAuthStatus`
  - `invitedByUserId`
  - `validInviteCount`
- `user.me`：
  - `id`
  - `role`
  - `inviteCode`
  - `validInviteCount`
  - `membershipTier`

## 4. 数据库证据点

### 4.1 `user`

- `user_id`
- `phone`
- `user_type`
- `invited_by_user_id`
- `valid_invite_count`
- `register_source`
- `register_device_fingerprint`
- `last_login_time`
- `create_time`

### 4.2 `referral_record`

- `referral_id`
- `inviter_user_id`
- `invitee_user_id`
- `invite_code_snapshot`
- `register_device_fingerprint`
- `status`
- `risk_flag`

### 4.3 Redis

- `sms:code:{phone}`
- `wechat:miniapp:access-token`

## 5. 同一样本链的最小比对矩阵

| 证据面 | 必须一致的字段 | 样本值 |
|-------|---------------|--------|
| 登录页 | `inviteCode`、微信按钮显隐 | |
| 登录 / 注册响应 | `userId`、`invitedByUserId`、`validInviteCount` | |
| `user.me` | `id`、`inviteCode`、`validInviteCount` | |
| `verify/status` | `status` | |
| `invite/stats` | `validInviteCount` | |
| `level/info` | `inviteCount`、`membershipTier` | |
| `user` | `user_id`、`invited_by_user_id`、`register_source` | |
| `referral_record` | `invitee_user_id`、`invite_code_snapshot`、`status` | |

## 6. 当前不能误判为完成的点

满足以下任一条，都不能写“login-auth 闭环完成”：

- 只测了手机号登录，没有测注册、邀请码和会话恢复
- 微信按钮能显示，但没有真实微信样本
- `sendCode` 可用就误写成短信能力已正式完成
- `login / register / wechat-login` 与 `user.me` 字段口径不一致
- 登录后 `verify / invite / level` 没有回到同一用户事实源

## 7. 建议执行顺序

1. 固定样本 `phone / inviteCode / userId`
2. 先跑 `run-login-auth-validation.ps1 -EnableLiveProbe`，确认当前环境不是 mock 回退，而是真接口 / 真阻塞
3. 再抓登录页与接口响应
4. 再核对 `user.me / verify / invite / level`
5. 再查 `user / referral_record / Redis`
6. 最后回填 `status/login-auth-status.md`
