# Recruit Authenticated Sample 20260403-065131-continue-recheck

- Generated At: `2026-04-03T06:51:31`
- Base URL: `http://101.43.57.62/api`
- Sample Label: `continue-recheck`

## Entity IDs

- Actor User ID: `10000`
- Project ID: `1775170290915996`
- Role ID: `10003`
- Apply ID: `10003`

## Checks

- `PASS` actor-login: userId=10000
- `PASS` save-company: message=操作成功
- `PASS` roles-by-project: total=1
- `PASS` search-total-aligned: total=1, list=1
- `PASS` search-project-id-aligned: expected=1775170290915996, actual=1775170290915996
- `PASS` detail-project-id-aligned: detailProjectId=1775170290915996
- `PASS` my-applies-total-aligned: total=4, list=4
- `PASS` admin-projects-visible: total=1
- `PASS` admin-roles-visible: total=1
- `PASS` admin-applies-visible: total=1
- `PASS` pause-hides-role: list=0
- `PASS` resume-restores-role: list=1
- `PASS` project-end-hides-role: list=0
- `PASS` project-end-blocks-role-resume: message=关联项目已结束，不能恢复招募
- `PASS` project-resume-does-not-auto-resume-role: list=0
- `PASS` final-role-resume-restores-visibility: list=1
- `PASS` role-applies-query-clean: total=1

## Artifacts

- `results.json`
