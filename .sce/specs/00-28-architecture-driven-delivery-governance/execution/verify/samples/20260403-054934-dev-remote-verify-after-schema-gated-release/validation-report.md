# Verify Validation Report

## Sample

- SampleName: remote-verify-after-schema-gated-release
- Environment: dev
- ApiBaseUrl: http://101.43.57.62
- UserId: 10021
- FirstVerificationId: 12
- RetryVerificationId: 13

## Extracted Facts

### Final Actor Snapshot

- status: approved
- realName: æµè¯4934
- rejectReason: --
- submittedAt: 2026-04-02T21:49:35
- reviewedAt: 2026-04-02T21:49:36

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
- retryReviewedAt: 2026-04-02T21:49:36

## Cross Checks

- First record rejected: 是
- Retry record approved: 是
- Two verification IDs differ: 是
- Final actor status is approved: 是
- Final level/info isCertified: 是

## Capture Summary

- OK endpoints: 6
- Error endpoints: 0
- Capture directory: D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\verify\samples\20260403-054934-dev-remote-verify-after-schema-gated-release
