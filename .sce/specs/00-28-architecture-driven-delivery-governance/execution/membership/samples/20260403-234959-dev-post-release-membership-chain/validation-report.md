# Membership Validation Report

- Generated At: 2026-04-03T23:49:59
- Environment: dev

## Local Runtime Scan

- Frontend baseURL: http://101.43.57.62
- Frontend mock flag: false
- Admin baseURL: /api
- Server exposes /api context path: True

## Blockers

- [x] No blocker detected from local file scan

## Manual Evidence To Add

- [ ] Membership accounts admin screenshot
- [ ] Templates admin screenshot
- [x] level.info / card.personalization capture
- [x] membership / actor-card / detail / invite / fortune screenshots
- [x] DB query result for membership_account / card_scene_template / template_publish_log

## Current Evidence Summary

- 本轮正式样本目录：`20260403-234959-dev-post-release-membership-chain`
- 已确认发布后 membership 主链继续稳定：
  - `membershipTier: member -> none -> member`
  - `after-close.reasonCodes: member_required`
  - `publishLogId=26`
  - `publishVersion=SMOKE_V2_ADMIN_20260403_235012`
- 已补齐五页小程序页面证据：
  - `membership`
  - `actor-card`
  - `actor-profile-detail`
  - `invite-card`
  - `fortune`
- 已补齐页面证据清单：
  - `captures/mini-program-screenshot-capture.json`
  - `captures/post-release-page-data-membership.json`
  - `captures/post-release-page-data-actor-card.json`
  - `captures/post-release-page-data-actor-profile-detail.json`
  - `captures/post-release-page-data-invite-card.json`
  - `captures/post-release-page-data-fortune.json`
  - `screenshots/post-release-membership-index.png`
  - `screenshots/post-release-actor-card-mini-program-card.png`
  - `screenshots/post-release-actor-profile-detail.png`
  - `screenshots/post-release-invite-card.png`
  - `screenshots/post-release-fortune-general.png`

## Output Files

- captures/capture-results.json
- captures/admin-membership-template-chain-results.json
- captures/admin-membership-template-chain-db.txt
- captures/mini-program-screenshot-capture.json
- captures/post-release-page-data-membership.json
- captures/post-release-page-data-actor-card.json
- captures/post-release-page-data-actor-profile-detail.json
- captures/post-release-page-data-invite-card.json
- captures/post-release-page-data-fortune.json
- runtime-summary.md
- admin-membership-template-chain-summary.md
- sample-ledger.md
- validation-report.md
