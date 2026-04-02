# Verify Validation Report

## Sample

- SampleName: remote-verify-reject-retry-approve-after-history-fix
- Environment: dev
- ApiBaseUrl: http://101.43.57.62
- UserId: 10020
- FirstVerificationId: 10
- RetryVerificationId: 11

## Extracted Facts

### Final Actor Snapshot

- status: approved
- realName: æµè¯4221
- rejectReason: --
- submittedAt: 2026-04-02T21:42:22
- reviewedAt: 2026-04-02T21:42:22

### Final Level Snapshot

- isCertified: True
- level: 1
- profileCompletion: 95
- membershipTier: none

### Admin Record Snapshot

- verifyRecordCount: 2
- firstRecordStatus: rejected
- firstRejectReason: spec verify reject first pass
- retryRecordStatus: approved
- retryReviewedAt: 2026-04-02T21:42:22

## Cross Checks

- First record rejected: 是
- Retry record approved: 是
- Two verification IDs differ: 是
- Final actor status is approved: 是
- Final level/info isCertified: 是

## Capture Summary

- OK endpoints: 6
- Error endpoints: 0
- Capture directory: D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\verify\samples\20260403-054221-dev-remote-verify-reject-retry-approve-after-history-fix
