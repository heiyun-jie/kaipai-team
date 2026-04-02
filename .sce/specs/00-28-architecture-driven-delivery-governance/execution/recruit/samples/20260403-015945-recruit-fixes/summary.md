# Recruit Authenticated Sample 20260403-015945-recruit-fixes

- Generated At: `2026-04-03T01:59:45`
- Base URL: `http://101.43.57.62/api`
- Sample Label: `recruit-fixes`

## Entity IDs

- Actor User ID: `10000`
- Project ID: `1775152786145572`
- Role ID: `10001`
- Apply ID: `10001`

## Checks

- `PASS` actor-login: userId=10000
- `FAIL` save-company: message=操作失败
- `PASS` roles-by-project: total=1
- `PASS` search-total-aligned: total=1, list=1
- `PASS` search-project-id-aligned: expected=1775152786145572, actual=1775152786145572
- `PASS` detail-project-id-aligned: detailProjectId=1775152786145572
- `PASS` my-applies-total-aligned: total=2, list=2
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
