# Membership Validation Report

- Generated At: 2026-04-02T21:09:14
- Environment: dev

## Local Runtime Scan

- Frontend baseURL: http://101.43.57.62
- Frontend mock flag: false
- Admin baseURL: /api
- Server exposes /api context path: True

## Blockers

- [x] No blocker detected from local file scan
- [x] Historical DevTools authorization blocker has been captured in `captures/devtools-auth-blocker.txt`
- [x] `2026-04-02 20:53` official `cli auto --project ... --auto-port 9421` has recovered and can be connected by automator
- [x] `2026-04-02 21:09` automator captured the five target mini-program pages into the sample `screenshots/` directory

## Manual Evidence To Add

- [ ] Membership accounts admin screenshot
- [ ] Templates admin screenshot
- [x] level.info / card.personalization capture
- [x] membership / actor-card / detail / invite / fortune screenshots
- [x] DB query result for membership_account / membership_change_log / card_scene_template / template_publish_log / admin_operation_log
- [x] DevTools auth blocker capture: `captures/devtools-auth-blocker.txt`
- [x] Mini-program screenshot capture: `captures/mini-program-screenshot-capture.json`

## Output Files

- captures/admin-membership-template-chain-results.json
- captures/admin-membership-template-chain-db.txt
- captures/mini-program-screenshot-capture.json
- runtime-summary.md
- sample-ledger.md
- validation-report.md
