# Login Auth Validation Report

- Generated At: 2026-04-02T18:39:46
- Environment: dev

## Local Runtime Scan

- Frontend baseURL: http://101.43.57.62
- Frontend mock flag: false
- Frontend WeChat flag: false
- Admin baseURL: /api
- Server exposes WeChat placeholders: appId=True, appSecret=True

## Blockers

- [ ] Frontend VITE_ENABLE_WECHAT_AUTH is not true; real WeChat path cannot be validated

## Manual Evidence To Add

- [ ] Login page screenshot
- [ ] Auth API capture
- [ ] user.me / verify / invite / level capture
- [ ] DB query result for user / referral_record
- [ ] WeChat error or success evidence when enabled

## Output Files

- captures/capture-results.json
- runtime-summary.md
- sample-ledger.md
- validation-report.md
