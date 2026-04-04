# Login Auth Phone Session Sample

- Generated At: `2026-04-04T02:31:18`
- Environment: `dev`
- Base URL: `http://101.43.57.62`
- Sample Label: `continue-phone-session-mainline`

## Runtime

- Frontend `.env` base URL: `http://101.43.57.62`
- Frontend `.env` mock flag: `false`
- Frontend `.env` WeChat flag: `false`

## Sample Context

- Phone: `13800138000`
- User ID: `10000`
- Token Preview: `eyJhbGciOiJI...4tz8BQIJ`
- Membership Tier: `member`
- Level: `5`
- Invite Count: `9`
- Verify Status: `2`

## Primary Chain

- sendCode message: `验证码发送成功`
- login userId: `10000`
- user.me userId: `10000`
- level.info inviteCount: `9`
- personalization reasonCodes: `[]`

## Restored Session

- restored user.me userId: `10000`
- restored level.info level: `5`
- restored invite.stats validInviteCount: `9`

## Confirmed

- 手机号 `13800138000` 可通过 `sendCode -> login` 获取真实 token，并命中 `userId=10000`。
- `/api/user/me`、`/api/verify/status`、`/api/invite/stats`、`/api/level/info`、`/api/card/personalization` 当前同一 token 下全部返回 `200/code=200`。
- fresh session 复用同一 Bearer token 后，`user.me / verify.status / invite.stats / level.info` 仍保持同一用户与同一等级摘要，说明当前会话恢复口径稳定。
- `/api/card/personalization` 当前 `reasonCodes=[]`。

## Blockers

- `sendCode` still directly returns a development verification code; this proves interface connectivity, not commercial SMS closure.

## Artifacts

- `sample-metadata.json`
- `closure-context.json`
- `captures/send-code.json`
- `captures/login.json`
- `captures/user-me.json`
- `captures/verify-status.json`
- `captures/invite-stats.json`
- `captures/level-info.json`
- `captures/card-personalization.json`
- `captures/restored-user-me.json`
- `captures/restored-verify-status.json`
- `captures/restored-invite-stats.json`
- `captures/restored-level-info.json`
- `summary.md`
