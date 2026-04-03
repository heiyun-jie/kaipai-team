# Recruit Admin Page Evidence 20260403-110916-recruit-admin-page-evidence

- Generated At: `2026-04-03T11:09:28`
- Base URL: `http://101.43.57.62/api`
- Proxy URL: `http://127.0.0.1:8011`
- Local Admin URL: `http://127.0.0.1:5176`
- Source Recruit Sample: `20260403-065131-continue-recheck`

## Entity IDs

- Actor User ID: `10000`
- Project ID: `1775170290915996`
- Role ID: `10003`
- Apply ID: `10003`
- Sample Label: `continue-recheck`

## Captures

- `admin-recruit-projects` -> route=`/recruit/projects` filters=`{"pageNo": 1, "pageSize": 20, "projectId": "1775170290915996", "keyword": "continue-recheck"}` list=`admin-recruit-projects.png` detail=`admin-recruit-projects-detail.png` pageData=`page-data-admin-recruit-projects.json` rows=`1`
- `admin-recruit-roles` -> route=`/recruit/roles` filters=`{"pageNo": 1, "pageSize": 20, "roleId": "10003", "projectId": "1775170290915996", "keyword": "continue-recheck"}` list=`admin-recruit-roles.png` detail=`admin-recruit-roles-detail.png` pageData=`page-data-admin-recruit-roles.json` rows=`1`
- `admin-recruit-applies` -> route=`/recruit/applies` filters=`{"pageNo": 1, "pageSize": 20, "applyId": "10003", "roleId": "10003", "actorUserId": "10000", "keyword": "continue-recheck"}` list=`admin-recruit-applies.png` detail=`admin-recruit-applies-detail.png` pageData=`page-data-admin-recruit-applies.json` rows=`1`

## Artifacts

- `captures/admin-recruit-screenshot-capture.json`
- `captures/admin-recruit-screenshot-capture.stdout.log`
- `captures/admin-recruit-screenshot-capture.stderr.log`
- `captures/admin-local-vite.log`
- `captures/page-data-admin-recruit-projects.json`
- `captures/page-data-admin-recruit-roles.json`
- `captures/page-data-admin-recruit-applies.json`
- `screenshots/admin-recruit-projects.png`
- `screenshots/admin-recruit-projects-detail.png`
- `screenshots/admin-recruit-roles.png`
- `screenshots/admin-recruit-roles-detail.png`
- `screenshots/admin-recruit-applies.png`
- `screenshots/admin-recruit-applies-detail.png`

