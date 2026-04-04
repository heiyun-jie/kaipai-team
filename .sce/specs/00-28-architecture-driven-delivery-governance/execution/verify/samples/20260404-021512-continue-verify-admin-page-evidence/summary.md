# Verify Admin Page Evidence 20260404-021512-continue-verify-admin-page-evidence

- Generated At: `2026-04-04T02:15:21`
- Base URL: `http://101.43.57.62/api`
- Proxy URL: `http://127.0.0.1:8012`
- Local Admin URL: `http://127.0.0.1:5177`
- Source Verify Sample: `20260403-054934-dev-remote-verify-after-schema-gated-release`

## Entity IDs

- Actor User ID: `10021`
- First Verification ID: `12`
- Retry Verification ID: `13`
- Real Name: `测试4934`

## Captures

- `admin-verify-pending-empty` -> route=`/verify/pending` screenshot=`admin-verify-pending-empty.png` pageData=`page-data-admin-verify-pending-empty.json` rows=`0`
- `admin-verify-history` -> route=`/verify/history` list=`admin-verify-history.png` detail=`admin-verify-history-detail.png` pageData=`page-data-admin-verify-history.json` rows=`2`

## Artifacts

- `captures/admin-verify-screenshot-capture.json`
- `captures/admin-verify-screenshot-capture.stdout.log`
- `captures/admin-verify-screenshot-capture.stderr.log`
- `captures/admin-local-vite.log`
- `captures/page-data-admin-verify-pending-empty.json`
- `captures/page-data-admin-verify-history.json`
- `screenshots/admin-verify-pending-empty.png`
- `screenshots/admin-verify-history.png`
- `screenshots/admin-verify-history-detail.png`

