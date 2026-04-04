# Login Auth Register Invite Sample

- Generated At: `2026-04-04T02:37:37`
- Environment: `dev`
- Base URL: `http://101.43.57.62`
- Sample Label: `continue-register-invite-mainline`

## Sample Context

- Inviter Phone: `13800138000`
- Inviter User ID: `10000`
- Invite Code: `SMK100`
- Registered Phone: `13941457242`
- Registered User ID: `10022`
- Registered Nickname: `登录样本7242`
- Device Fingerprint: `login-auth-register-13941457242`

## Register Chain

- inviter invite total before: `11`
- inviter invite total after: `12`
- register invitedByUserId: `10000`
- user.me invitedByUserId: `10000`
- referralRecordId: `12`
- referral status: `0`
- restore userId: `10022`

## Confirmed

- 手机号 `13941457242` 已通过 `sendCode -> register(inviteCode=SMK100)` 创建真实新用户，并返回 `userId=10022` token。
- 注册回包与 `/api/user/me` 都已固定 `invitedByUserId=10000`，说明当前 login-auth 注册链已承接邀请码。
- 后台 `/admin/referral/records` 已回读到 `referralId=12`，证明注册链已落 `referral_record`。
- 注册后 fresh session 复用同一 Bearer token 仍可恢复到 `userId=10022`。
- 邀请人 `/api/invite/stats.totalInviteCount` 已从 `11` 变化到 `12`。

## Blockers

- `sendCode` still directly returns a development verification code; this proves interface connectivity, not commercial SMS closure.

## Artifacts

- `sample-metadata.json`
- `closure-context.json`
- `captures/inviter-send-code.json`
- `captures/inviter-login.json`
- `captures/inviter-invite-code.json`
- `captures/inviter-invite-stats-before.json`
- `captures/register-send-code.json`
- `captures/register.json`
- `captures/registered-user-me.json`
- `captures/registered-verify-status.json`
- `captures/registered-level-info.json`
- `captures/registered-invite-stats.json`
- `captures/restored-registered-user-me.json`
- `captures/admin-login.json`
- `captures/admin-referral-records.json`
- `captures/inviter-invite-stats-after.json`
- `summary.md`
