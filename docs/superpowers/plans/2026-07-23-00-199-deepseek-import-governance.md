# 00-199 DeepSeek Import Governance Implementation Plan

> **Status:** Plan 2 is complete and its verification gate has passed. Plan 3 / T6 already has implementation history on this branch, but remains incomplete and is not marked complete by this plan; 00-199 as a whole is not complete.
>
> **Historical execution method:** This plan was executed task-by-task with subagent review and verification. Checked steps record the completed Plan 2 scope.

**Goal:** Provide separately governed DeepSeek configuration, capability, structured extraction, audited rate limiting, and atomic import application without retaining raw clipboard text, full model output, source evidence, or API keys.

**Architecture:** The AI domain owns configuration, encryption, provider calls, rate-limit counters, and sanitized audits. The profile domain from Plan 1 owns profile/work/asset persistence. Extract returns signed candidate proofs; apply locks a sanitized request audit, validates proofs and versions, and delegates one transaction to the profile import writer.

**Tech Stack:** Spring Boot 3.2.3, Java 17 HTTP client, MyBatis-Plus, Redis counter only, AES-GCM secret service, Vue 3, TypeScript, Element Plus.

---

## Preconditions And File Map

Plan 1 was completed and passed its verification gate before this plan. Its shared ProfileDomainErrorCode remains the only stable 00-199 error map. Plan 2 completed the numeric and string mapping 46001 through 46017; it did not create a second error-code enum.

- Create: kaipaile-server/src/main/resources/db/migration/V20260723_004__ai_profile_import_governance.sql
- Create: kaipaile-server/src/main/java/com/kaipai/model/ai/entity/AiProfileImportConfig.java
- Create: kaipaile-server/src/main/java/com/kaipai/model/ai/entity/AiProfileImportConfigAudit.java
- Create: kaipaile-server/src/main/java/com/kaipai/model/ai/entity/AiProfileImportRequestAudit.java
- Create: kaipaile-server/src/main/java/com/kaipai/mapper/ai/AiProfileImportConfigMapper.java
- Create: kaipaile-server/src/main/java/com/kaipai/mapper/ai/AiProfileImportConfigAuditMapper.java
- Create: kaipaile-server/src/main/java/com/kaipai/mapper/ai/AiProfileImportRequestAuditMapper.java
- Create: kaipaile-server/src/main/java/com/kaipai/model/ai/dto/ProfileImportCapabilityRespDTO.java
- Create: kaipaile-server/src/main/java/com/kaipai/model/ai/dto/ProfileImportExtractReqDTO.java
- Create: kaipaile-server/src/main/java/com/kaipai/model/ai/dto/ProfileImportExtractionRespDTO.java
- Create: kaipaile-server/src/main/java/com/kaipai/model/ai/dto/ProfileImportApplyReqDTO.java
- Create: kaipaile-server/src/main/java/com/kaipai/model/ai/dto/ProfileImportApplyRespDTO.java
- Create: kaipaile-server/src/main/java/com/kaipai/service/ai/ProfileTextExtractor.java
- Create: kaipaile-server/src/main/java/com/kaipai/service/ai/ProfileImportConfigService.java
- Create: kaipaile-server/src/main/java/com/kaipai/service/ai/ProfileImportService.java
- Create: kaipaile-server/src/main/java/com/kaipai/service/ai/ProfileImportApplyService.java
- Create: kaipaile-server/src/main/java/com/kaipai/service/ai/impl/ProfileImportConfigServiceImpl.java
- Create: kaipaile-server/src/main/java/com/kaipai/service/ai/impl/ProfileImportServiceImpl.java
- Create: kaipaile-server/src/main/java/com/kaipai/service/ai/impl/ProfileImportApplyServiceImpl.java
- Create: kaipaile-server/src/main/java/com/kaipai/service/ai/profileimport/ProfileImportSchemaValidator.java
- Create: kaipaile-server/src/main/java/com/kaipai/service/ai/profileimport/ProfileImportCandidateProofService.java
- Create: kaipaile-server/src/main/java/com/kaipai/service/ai/profileimport/ProfileImportPayloadHasher.java
- Create: kaipaile-server/src/main/java/com/kaipai/integration/ai/profileimport/DeepSeekProfileTextExtractor.java
- Create: kaipaile-server/src/main/java/com/kaipai/controller/api/ai/AiProfileImportController.java
- Create: kaipaile-server/src/main/java/com/kaipai/controller/admin/ai/AdminAiProfileImportController.java
- Modify: kaipaile-server/src/main/java/com/kaipai/common/result/R.java
- Modify: kaipaile-server/src/main/java/com/kaipai/common/exception/GlobalExceptionHandler.java
- Modify: kaipai-admin/src/api/ai.ts
- Modify: kaipai-admin/src/types/ai.ts
- Modify: kaipai-admin/src/types/common.ts
- Modify: kaipai-admin/src/utils/request.ts
- Modify: kaipai-admin/src/views/system/SettingsView.vue
- Modify: kaipai-admin/src/router/index.ts
- Modify: kaipai-admin/src/constants/permission.ts
- Modify: kaipai-admin/src/constants/permission-registry.ts
- Modify: kaipai-admin/src/constants/menus.ts
- Create: kaipai-admin/src/views/system/AiProfileImportConfigView.vue
- Create: kaipai-admin/scripts/e2e-ai-profile-import-config.mjs

API surface:

```text
GET  /api/ai/profile-import/capability
POST /api/ai/profile-import/extract
POST /api/actor/profile-import/apply
GET  /api/admin/ai/profile-import/config
PUT  /api/admin/ai/profile-import/config
PUT  /api/admin/ai/profile-import/secret
PUT  /api/admin/ai/profile-import/enabled
POST /api/admin/ai/profile-import/test
GET  /api/admin/ai/profile-import/audits
```

## Task 1: Stable Error Envelope and Sanitized Audit Schema

**Files:**
- Modify: ProfileDomainErrorCode, R.java, GlobalExceptionHandler
- Create: V20260723_004 migration, config/audit/request entities and mappers
- Test: ProfileImportErrorContractTest and AiProfileImportPersistenceShapeTest

- [x] **Step 1: Write red error and persistence tests**

```java
@Test
void importErrorMapIsStable() {
    assertEquals(46001, ProfileDomainErrorCode.PROFILE_IMPORT_DISABLED.code());
    assertEquals("PROFILE_IMPORT_DISABLED", ProfileDomainErrorCode.PROFILE_IMPORT_DISABLED.errorCode());
    assertEquals(46017, ProfileDomainErrorCode.PROFILE_LEGACY_COLLECTION_WRITE_RETIRED.code());
}

@Test
void requestAuditCannotPersistSourceTextOrSecrets() {
    assertNoDeclaredField(AiProfileImportRequestAudit.class, "rawText");
    assertNoDeclaredField(AiProfileImportRequestAudit.class, "response");
    assertNoDeclaredField(AiProfileImportRequestAudit.class, "sourceText");
    assertNoDeclaredField(AiProfileImportConfig.class, "apiKey");
}
```

- [x] **Step 2: Run red tests**

```powershell
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -Dtest=ProfileImportErrorContractTest,AiProfileImportPersistenceShapeTest test
```

Expected: FAIL because the schema, error envelope, and entities do not exist.

- [x] **Step 3: Implement error envelope and DDL**

Extend R with optional errorCode while preserving existing code/message/data clients. Create config, config-audit, and request-audit tables. Request audit stores IDs, model, input length, counts, elapsed time, status, stable error code, extraction versions, and apply hash/status/summary/time. It has unique user_id plus request_id and has no raw source/model response/evidence/API-key column.

- [x] **Step 4: Run green tests and commit**

```powershell
mvn -q -Dtest=ProfileImportErrorContractTest,AiProfileImportPersistenceShapeTest test
git add kaipaile-server/src/main/resources/db/migration/V20260723_004__ai_profile_import_governance.sql kaipaile-server/src/main/java/com/kaipai/model/actor/dto/ProfileDomainErrorCode.java kaipaile-server/src/main/java/com/kaipai/model/ai kaipaile-server/src/main/java/com/kaipai/mapper/ai kaipaile-server/src/main/java/com/kaipai/common/result/R.java kaipaile-server/src/main/java/com/kaipai/common/exception/GlobalExceptionHandler.java kaipaile-server/src/test/java/com/kaipai
git commit -m "feat(ai): add profile import error and audit schema"
```

Expected: tests PASS.

## Task 2: Govern Config, Secret, Test, and Permissions

**Files:**
- Create: ProfileImportConfigService, ProfileImportConfigServiceImpl, admin DTOs and controller
- Modify: admin permission seed and registry files
- Test: ProfileImportConfigServiceImplTest and AdminAiProfileImportControllerTest

- [x] **Step 1: Write red configuration tests**

```java
@Test
void secretIsEncryptedAndReadBackOnlyAsMask() {
    var result = configService.saveSecret(adminId, newSecret("sk-test"));
    assertEquals("****test", result.getSecretMask());
    assertFalse(result.toString().contains("sk-test"));
}

@Test
void capabilityStaysUnavailableUntilEnabledAndSuccessfulTest() {
    configService.savePublicConfig(adminId, validConfig());
    assertFalse(configService.capability().isAvailable());
    configService.saveSecret(adminId, newSecret("sk-test"));
    configService.testConnection(adminId);
    configService.setEnabled(adminId, true);
    assertTrue(configService.capability().isAvailable());
}
```

- [x] **Step 2: Run red tests**

```powershell
mvn -q -Dtest=ProfileImportConfigServiceImplTest,AdminAiProfileImportControllerTest test
```

Expected: FAIL because configuration lifecycle and admin endpoints do not exist.

- [x] **Step 3: Implement config rules**

Reuse only AES-GCM encrypt/decrypt from AiProviderSecretCryptoService; do not use image-provider configuration or secret-reveal endpoints. Public/secret changes reset test status. Test connection sends a fixed no-user-data JSON probe. Endpoint validation requires HTTPS, rejects loopback/private IP resolution, and accepts only the controlled DeepSeek host set.

Use actual permissions:

```text
page.system.ai-profile-import
action.system.ai-profile-import.update
action.system.ai-profile-import.secret
action.system.ai-profile-import.test
action.system.ai-profile-import.audit
```

- [x] **Step 4: Run green tests and commit**

```powershell
mvn -q -Dtest=ProfileImportConfigServiceImplTest,AdminAiProfileImportControllerTest test
git add kaipaile-server/src/main/java/com/kaipai/service/ai kaipaile-server/src/main/java/com/kaipai/controller/admin/ai/AdminAiProfileImportController.java kaipaile-server/src/test/java/com/kaipai
git commit -m "feat(ai): add governed deepseek configuration"
```

Expected: tests PASS and audit snapshots contain masks/stable codes only.

## Task 3: Constrained Extraction and Candidate Proof

**Files:**
- Create: extractor, validator, proof/hash services, extraction DTOs
- Test: DeepSeekProfileTextExtractorTest, ProfileImportSchemaValidatorTest, ProfileImportCandidateProofServiceTest

- [x] **Step 1: Write red extraction tests**

```java
@Test
void invalidResponseGetsOneRepairThenReturns46007() {
    server.enqueue("not json");
    server.enqueue("still not json");
    BizException error = assertThrows(BizException.class, () -> extractor.extract(request()));
    assertEquals(46007, error.getCode());
    assertEquals(2, server.requestCount());
}

@Test
void roleEvidenceCreatesUnselectedFemaleCandidate() {
    var gender = validator.validate(goldenWangHuohuoResponse()).profileCandidate("gender");
    assertEquals("female", gender.value());
    assertFalse(gender.selected());
    assertFalse(gender.confirmed());
    assertTrue(gender.requiresExplicitConfirmation());
}
```

- [x] **Step 2: Run red tests**

```powershell
mvn -q -Dtest=DeepSeekProfileTextExtractorTest,ProfileImportSchemaValidatorTest,ProfileImportCandidateProofServiceTest test
```

Expected: FAIL because no extractor or validation path exists.

- [x] **Step 3: Implement fixed extraction path**

The extractor uses the configured key only in the request stack, logs no body, makes exactly one repair request for invalid JSON, maps timeout to 46006 and provider failure to 46002. The validator rejects unknown fields, preserves partial birthday precision, preserves origin/current-city separation and numerical achievements, ignores image/video placeholders, and creates no asset candidates.

Return HMAC candidateProof bound to request ID, candidate ID, original value, source type, and confirmation requirement. The response carries the proof; no audit table stores it.

- [x] **Step 4: Run green tests and commit**

```powershell
mvn -q -Dtest=DeepSeekProfileTextExtractorTest,ProfileImportSchemaValidatorTest,ProfileImportCandidateProofServiceTest test
git add kaipaile-server/src/main/java/com/kaipai/integration/ai/profileimport kaipaile-server/src/main/java/com/kaipai/service/ai/ProfileTextExtractor.java kaipaile-server/src/main/java/com/kaipai/service/ai/profileimport kaipaile-server/src/main/java/com/kaipai/model/ai/dto kaipaile-server/src/test/java/com/kaipai
git commit -m "feat(ai): add constrained deepseek extraction"
```

Expected: tests PASS.

## Task 4: Capability, Extract, Rate Limit, and Sanitized Request Audit

**Files:**
- Create: ProfileImportService, ProfileImportServiceImpl, rate-limit service/key, AiProfileImportController
- Modify: request-audit mapper and DTOs
- Test: ProfileImportServiceImplTest and AiProfileImportControllerTest

- [x] **Step 1: Write red service tests**

```java
@Test
void disabledCapabilityRejectsBeforeModelCall() {
    disableProvider();
    BizException error = assertThrows(BizException.class, () -> service.extract(USER_ID, request()));
    assertEquals(46001, error.getCode());
    verifyNoInteractions(extractor);
}

@Test
void extractWritesOnlySanitizedAudit() {
    service.extract(USER_ID, request("演员王火火 170/45kg"));
    var audit = auditMapper.selectByUserAndRequest(USER_ID, requestId());
    assertEquals(16, audit.getInputLength());
    assertNull(audit.getRawText());
    assertNull(audit.getRawResponse());
}

@Test
void dailyLimitRejectsBeforeModelCall() {
    rateLimit.exhaust(USER_ID);
    BizException error = assertThrows(BizException.class, () -> service.extract(USER_ID, request()));
    assertEquals(46005, error.getCode());
    verifyNoInteractions(extractor);
}
```

- [x] **Step 2: Run red tests**

```powershell
mvn -q -Dtest=ProfileImportServiceImplTest,AiProfileImportControllerTest test
```

Expected: FAIL because capability/extract/rate-limit endpoints do not exist.

- [x] **Step 3: Implement execution order**

```text
login -> capability -> empty/length guard -> Redis daily counter
-> profile/work context reader -> extractor -> schema/proof validation
-> sanitized request audit -> response
```

Redis key format is ai:profile-import:daily:{yyyy-MM-dd}:{userId}; it contains a count and expiry only. The extract endpoint requires login but does not require real-name verification and does not call the profile writer.

- [x] **Step 4: Run green tests and commit**

```powershell
mvn -q -Dtest=ProfileImportServiceImplTest,AiProfileImportControllerTest test
git add kaipaile-server/src/main/java/com/kaipai/service/ai kaipaile-server/src/main/java/com/kaipai/controller/api/ai/AiProfileImportController.java kaipaile-server/src/test/java/com/kaipai
git commit -m "feat(ai): expose profile import extraction"
```

Expected: tests PASS with no business write during extract.

## Task 5: Atomic Apply, Version Check, and Idempotency

**Files:**
- Create: ProfileImportApplyService and ProfileImportApplyServiceImpl
- Create: import apply DTOs
- Modify: request-audit entity/mapper with selectForUpdate
- Use: `kaipaile-server/src/test/resources/profile-migration/wang-huohuo-works-golden.json`
- Test: ProfileImportApplyServiceImplTest and ProfileImportApplyMySqlIntegrationTest

- [x] **Step 1: Write red apply tests**

```java
@Test
void applyRejectsUnconfirmedInferredGender() {
    var request = applyRequestWithInferredGender(false);
    BizException error = assertThrows(BizException.class, () -> applyService.apply(USER_ID, request));
    assertEquals(46011, error.getCode());
}

@Test
void sameRequestAndPayloadReturnsStoredResultWithoutSecondWriterCall() {
    var first = applyService.apply(USER_ID, validApplyRequest());
    var second = applyService.apply(USER_ID, validApplyRequest());
    assertEquals(first, second);
    verify(profileImportWriter, times(1)).applyImport(eq(USER_ID), any());
}

@Test
void sameRequestWithDifferentPayloadReturns46009() {
    applyService.apply(USER_ID, validApplyRequest());
    BizException error = assertThrows(BizException.class,
        () -> applyService.apply(USER_ID, changedApplyRequest()));
    assertEquals(46009, error.getCode());
}

@Test
void freshRequestWithSameWangHuohuoContentMatchesExistingWorksAndStaysAtTwentyNine() {
    ProfileContextVersion initialContext = currentContextVersions(USER_ID);
    ProfileImportApplyReqDTO first = extractReviewAndPersistAuditFromGolden(
        USER_ID, "req-wang-1", initialContext, "wang-huohuo-works-golden.json");
    assertEquals(29, first.getWorks().size());

    applyService.apply(USER_ID, first);

    assertEquals(29L, countActiveWorks(USER_ID));
    assertEquals(29L, countDistinctExperienceIds(USER_ID));
    assertEquals(29L, countDistinctNonblankDedupeKeys(USER_ID));
    assertEquals(Map.of("aired", 14L, "upcoming", 6L, "stage", 3L, "horizontal", 6L),
        queryCategoryCounts(USER_ID));

    ProfileContextVersion refreshedContext = currentContextVersions(USER_ID);
    ProfileImportApplyReqDTO second = extractReviewAndPersistAuditFromGolden(
        USER_ID, "req-wang-2", refreshedContext, "wang-huohuo-works-golden.json");

    assertNotEquals(first.getRequestId(), second.getRequestId());
    assertNotEquals(requestAuditId(USER_ID, first.getRequestId()),
        requestAuditId(USER_ID, second.getRequestId()));
    assertEquals("success", requestAuditStatus(USER_ID, second.getRequestId()));
    assertEquals(canonicalWorkContent(first), canonicalWorkContent(second));
    assertNotEquals(first.getWorks().get(0).getProof(), second.getWorks().get(0).getProof());
    assertEquals(refreshedContext.profileVersion(), second.getProfileVersion());
    assertEquals(refreshedContext.workLibraryVersion(), second.getWorkLibraryVersion());
    assertTrue(second.getWorks().stream().allMatch(work -> "skip".equals(work.getSelectedAction())));

    applyService.apply(USER_ID, second);
    assertEquals(29L, countActiveWorks(USER_ID));
}
```

`extractReviewAndPersistAuditFromGolden` represents a fresh successful extraction lifecycle: it creates a new request-audit row, binds newly issued candidate proofs to that request ID, uses the current profile/work context versions, matches the same normalized work content against existing rows, and builds reviewed `skip` actions. It must not clone the first apply request or reuse its audit row/proofs. The separate `sameRequestAndPayloadReturnsStoredResultWithoutSecondWriterCall` test remains the only same-request idempotency proof.

- [x] **Step 2: Run red tests**

```powershell
mvn -q -Dtest=ProfileImportApplyServiceImplTest,ProfileImportApplyMySqlIntegrationTest test
```

Expected: FAIL because apply service and audit-row locking do not exist, and the MySQL integration case has no fresh-request Wang Huohuo golden lifecycle yet: the second request must have a distinct audit row, newly request-bound proofs, refreshed context versions, matched `skip` actions, and a final database count of 29.

- [x] **Step 3: Implement one transaction**

Within a rollback-for-exception transaction: select the audit row FOR UPDATE; verify owner/status/proofs; hash canonical payload; compare extracted and current profile/work versions; revalidate enum/numeric/asset/work ownership; enforce explicit confirmation for inferred gender; call the Plan 1 writer; save only the apply hash/status/summary/time.

The internal work writer always persists `actor_experience.source_type=import` for created import works and preserves the stored provenance for merges. It must not copy candidate evidence values such as `explicit`, `direct`, or `inferred_from_roles` into work provenance. Public `ActorWorkSaveDTO` remains source-free.

For full_profile enforce avatar, public name, gender, age, height, and current city. For works_only allow a minimal non-public profile shell and skip those core requirements.

- [x] **Step 4: Run unit and MySQL integration proof**

```powershell
mvn -q -Dtest=ProfileImportApplyServiceImplTest test
mvn -q -Dtest=ProfileImportApplyMySqlIntegrationTest test
```

Expected: unit and isolated MySQL tests PASS. The integration cases must prove a failing second work write rolls back profile/work/audit updates, concurrent retry produces one work set, and the normalized Wang Huohuo golden fixture creates exactly 29 active works with 29 distinct IDs and nonblank dedupe keys plus category counts `14/6/3/6`. A second extraction of identical work content must use a fresh request ID, fresh successful audit, newly request-bound proofs, current context versions, and matched `skip` actions, after which the database remains at 29. Do not substitute the separate same-request idempotency path, a mocked total, fixture self-comparison, or a loop that seeds the expected count. The fixture contains no original clipboard body; a configured real DeepSeek smoke does not replace this deterministic DB proof.

- [x] **Step 5: Commit**

```powershell
git add kaipaile-server/src/main/java/com/kaipai/service/ai/ProfileImportApplyService.java kaipaile-server/src/main/java/com/kaipai/service/ai/impl/ProfileImportApplyServiceImpl.java kaipaile-server/src/main/java/com/kaipai/model/ai/dto kaipaile-server/src/main/java/com/kaipai/mapper/ai kaipaile-server/src/test/java/com/kaipai
git commit -m "feat(ai): apply profile import atomically"
```

## Task 6: Build the Admin System-Settings Tool

**Files:**
- Create: kaipai-admin/src/views/system/AiProfileImportConfigView.vue
- Create: kaipai-admin/scripts/e2e-ai-profile-import-config.mjs
- Modify: listed admin API/types/request/router/permissions/settings/menu files

- [x] **Step 1: Add the mock E2E scenario**

The E2E must prove all of the following:

1. A user with page permission sees System Settings, AI Service, DeepSeek Profile Import.
2. A user without the page permission cannot see or navigate to the page.
3. Secret save renders only a mask; page DOM, browser storage, and audit fixture contain no input secret.
4. Update, secret, test, enable, and audit actions obey their separate permissions.
5. A config update resets test status; only successful test plus complete config permits enable.
6. The route does not appear in the formal seven-page sidebar.

- [x] **Step 2: Run the red type/E2E commands**

```powershell
cd D:\XM\kaipai-team\kaipai-admin
npm run type-check
npm run e2e:ai-profile-import-config
```

Expected: FAIL because API module, route, view, and script are absent.

- [x] **Step 3: Implement the hidden System Settings page**

Route path is /system/ai-profile-import with architectureLayer tooling. SettingsView shows it only with page.system.ai-profile-import. The page supplies endpoint/model/timeout/input/output/daily-limit fields, a one-way password input for key updates, save/test/enable controls, recent stable result, and audits. It must never expose provider response text or reveal the API key.

Admin request errors retain numeric code and errorCode in a typed ApiRequestError; page states use errorCode rather than Chinese message matching.

- [x] **Step 4: Run green checks and commit**

```powershell
npm run type-check
npm run build
npm run e2e:ai-profile-import-config
git add kaipai-admin/src/api/ai.ts kaipai-admin/src/types kaipai-admin/src/utils/request.ts kaipai-admin/src/views/system/AiProfileImportConfigView.vue kaipai-admin/src/views/system/SettingsView.vue kaipai-admin/src/router/index.ts kaipai-admin/src/constants kaipai-admin/scripts/e2e-ai-profile-import-config.mjs kaipai-admin/package.json
git commit -m "feat(admin): add deepseek profile import settings"
```

Expected: type-check/build/E2E PASS with no real DeepSeek call or key in source/output.

## Verification Gate For Plan 2 (PASS)

```powershell
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -Dtest=ProfileImportErrorContractTest,AiProfileImportPersistenceShapeTest,ProfileImportConfigServiceImplTest,AdminAiProfileImportControllerTest,DeepSeekProfileTextExtractorTest,ProfileImportSchemaValidatorTest,ProfileImportCandidateProofServiceTest,ProfileImportServiceImplTest,AiProfileImportControllerTest,ProfileImportApplyServiceImplTest,ProfileImportApplyMySqlIntegrationTest test
mvn -q clean package
cd ..\kaipai-admin
npm run type-check
npm run build
npm run e2e:ai-profile-import-config
```

**Result:** PASS. The listed server tests, server package build, admin type-check/build, and admin E2E gate passed. A real DeepSeek smoke remains an administrator-controlled runtime action and was not part of the local gate. This result completes Plan 2 only, not 00-199 as a whole.
