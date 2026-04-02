# Recruit Authenticated Sample 20260403-020306-recruit-fixes-post-company-fix

- Generated At: `2026-04-03T02:03:06`
- Base URL: `http://101.43.57.62/api`
- Sample Label: `recruit-fixes-post-company-fix`

## Entity IDs

- Actor User ID: `10000`
- Project ID: `1775152987105853`
- Role ID: `10002`
- Apply ID: `10002`

## Checks

- `PASS` actor-login: userId=10000
- `PASS` save-company: message=操作成功
- `PASS` roles-by-project: total=1
- `PASS` search-total-aligned: total=1, list=1
- `PASS` search-project-id-aligned: expected=1775152987105853, actual=1775152987105853
- `PASS` detail-project-id-aligned: detailProjectId=1775152987105853
- `PASS` my-applies-total-aligned: total=3, list=3
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
