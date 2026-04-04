# Login Auth Mini Program Page Evidence 20260404-024359-continue-login-auth-mini-program-page-evidence

- Generated At: `2026-04-03T18:44:43.669Z`
- Base URL: `http://101.43.57.62/api`
- WS Endpoint: `ws://127.0.0.1:9421`
- Source Login Sample: `20260404-023118-dev-continue-phone-session-mainline`

## Source Context

- Phone: `13800138000`
- Actor User ID: `10000`
- Level: `5`
- Invite Count: `9`
- Membership Tier: `member`

## Captures

- `login-page-invite` -> path=`pages/home/index` query=`{}` screenshot=`login-page-invite.png` method=`automator` pageData=`page-data-login-page-invite.json`
- `mine-page-actor` -> path=`pages/mine/index` query=`{}` screenshot=`mine-page-actor.png` method=`automator` pageData=`page-data-mine-page-actor.json`
- `membership-page` -> path=`pkg-card/membership/index` query=`{}` screenshot=`membership-page.png` method=`automator` pageData=`page-data-membership-page.json`
- `invite-page` -> path=`pkg-card/invite/index` query=`{}` screenshot=`invite-page.png` method=`automator` pageData=`page-data-invite-page.json`

## Current Scope Note

- 当前真实页面证据先固定 `login(带inviteCode) -> mine -> membership -> invite`。
- `role-select` 当前不纳入真实样本，因为现网手机号登录样本已是明确身份用户，不会落到未知身份页。

## Visual Review

- Unique Screenshot Hash Count: `4`
- Unique Actual Path Count: `4`
- Visual Did Not Refresh: `False`

## Artifacts

- `captures/mini-program-screenshot-capture.json`
- `captures/mini-program-capture-progress.log`
- `captures/mini-program-screenshot-capture.stdout.log`
- `captures/mini-program-screenshot-capture.stderr.log`
- `captures/page-data-*.json`
- `screenshots/login-page-invite.png`
- `screenshots/mine-page-actor.png`
- `screenshots/membership-page.png`
- `screenshots/invite-page.png`

