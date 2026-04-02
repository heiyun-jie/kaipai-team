# AI Resume Validation Sample 20260403-071241-continue-rerun

- Generated At: `2026-04-03T07:12:41`
- Base URL: `http://101.43.57.62/api`
- Sample Label: `continue-rerun`

## Key IDs

- Actor User ID: `10000`
- Success Request ID: `airp_req_68af135e0f674a2694decabf2124ab43`
- Draft ID: `airp_draft_f7b1ae4f44b04625bc078cf886766301`
- History ID: `airp_hist_912dfa4393404253a0354217019178f2`
- Failure Request ID: `airp_req_495724ad93c64312b29d4bd94efb42fb`
- Failure ID: `airp_fail_e65454af8350411b93bad6ef82abaca0`

## Checks

- `PASS` actor-login: userId=10000
- `PASS` actor-certified: isCertified=True
- `PASS` quota-remaining-before: remaining=4, total=5, used=1
- `PASS` polish-success: patchCount=1
- `PASS` patch-apply-local: applied=1, total=1
- `PASS` profile-reflects-applied-patches: requestId=airp_req_68af135e0f674a2694decabf2124ab43
- `PASS` history-recorded: historyId=airp_hist_912dfa4393404253a0354217019178f2
- `PASS` admin-history-visible: list=1
- `PASS` rollback-restores-fields: historyId=airp_hist_912dfa4393404253a0354217019178f2
- `PASS` quota-incremented-once: before=1, after=2
- `PASS` blocked-content-fails: code=7105, message=命中敏感内容，未生成 patch
- `PASS` ai-governance-matrix-visible: totalRoles=1, aiReady=0, fallback=1
- `PASS` admin-failure-visible: failureId=airp_fail_e65454af8350411b93bad6ef82abaca0, handlingStatus=pending
- `PASS` admin-sensitive-hit-visible: count=1
- `PASS` admin-review-action: status=reviewed
- `PASS` admin-close-action: status=closed
- `PASS` operation-log-visible: list=1

## Artifacts

- `results.json`
