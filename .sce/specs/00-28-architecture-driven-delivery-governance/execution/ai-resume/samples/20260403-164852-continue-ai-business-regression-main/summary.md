# AI Resume Validation Sample 20260403-164852-continue-ai-business-regression-main

- Generated At: `2026-04-03T16:48:52`
- Base URL: `http://101.43.57.62/api`
- Sample Label: `continue-ai-business-regression-main`

## Key IDs

- Actor User ID: `10000`
- Success Request ID: `airp_req_10dc0c05b517405386483af460e19a66`
- Draft ID: `airp_draft_9bd7f9b10ed44bbe9828271bcc480290`
- History ID: `airp_hist_ccdd1616ea424d5780da35c99cca8c1a`
- Failure Request ID: `airp_req_9b3a2981112147d9a0783020a77e06fb`
- Failure ID: `airp_fail_a188719854194c70912aabb807502496`

## Checks

- `PASS` actor-login: userId=10000
- `PASS` actor-certified: isCertified=True
- `PASS` quota-remaining-before: remaining=3, total=5, used=2
- `PASS` polish-success: patchCount=1
- `PASS` patch-apply-local: applied=1, total=1
- `PASS` profile-reflects-applied-patches: requestId=airp_req_10dc0c05b517405386483af460e19a66
- `PASS` history-recorded: historyId=airp_hist_ccdd1616ea424d5780da35c99cca8c1a
- `PASS` admin-history-visible: list=1
- `PASS` rollback-restores-fields: historyId=airp_hist_ccdd1616ea424d5780da35c99cca8c1a
- `PASS` quota-incremented-once: before=2, after=3
- `PASS` blocked-content-fails: code=7105, message=命中敏感内容，未生成 patch
- `PASS` ai-governance-matrix-visible: totalRoles=1, aiReady=1, fallback=0
- `PASS` admin-failure-visible: failureId=airp_fail_a188719854194c70912aabb807502496, handlingStatus=pending
- `PASS` admin-sensitive-hit-visible: count=1
- `PASS` admin-review-action: status=reviewed
- `PASS` admin-close-action: status=closed
- `PASS` operation-log-visible: list=1

## Artifacts

- `results.json`
