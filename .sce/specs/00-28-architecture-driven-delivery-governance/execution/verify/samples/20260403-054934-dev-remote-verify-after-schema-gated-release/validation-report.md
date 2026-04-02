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
- realName: 测试4934
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

### Database Snapshot

- schemaMigrationPresent: 是
- schemaReleaseId: 20260403-054130-backend-schema-verify-resubmit-history-fix
- identityVerificationIndex: idx_identity_verification_id_card_hash(non_unique=1, column=id_card_hash)
- user.real_auth_status: 2
- actor_profile.real_name: 测试4934
- actor_profile.is_certified: True
- firstDbRecordStatus: 3
- firstDbRejectReason: spec verify reject first pass
- retryDbRecordStatus: 2
- retryDbReviewedAt: 2026-04-02 21:49:36
- owner.user_id: 10021
- owner.id_card_hash: b3d1bb9f35f920eeae0cfff51e2da464f520d950c78183952298927274334751
- rejectLog: operation_log_id=37, target_id=12, operation_result=1, create_time=2026-04-02 21:49:35
- approveLog: operation_log_id=38, target_id=13, operation_result=1, create_time=2026-04-02 21:49:36

## Cross Checks

- First record rejected: 是
- Retry record approved: 是
- Two verification IDs differ: 是
- Final actor status is approved: 是
- Final level/info isCertified: 是
- Actor status equals user.real_auth_status: 是
- Actor approval equals actor_profile.is_certified: 是
- Admin detail matches DB records: 是

## Capture Summary

- OK endpoints: 6
- Error endpoints: 0
- Validation result file: 是
- Capture directory: D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\verify\samples\20260403-054934-dev-remote-verify-after-schema-gated-release\captures

## Conclusion

- Verdict: 闭环完成
- Summary: 同一样本 userId=10021（尾号 4934）已完成拒绝后重提再通过闭环；DB 已回读 release_id=20260403-054130-backend-schema-verify-resubmit-history-fix、owner.user_id=10021、verification_id=12/13，首单拒绝=是，重提通过=是。
