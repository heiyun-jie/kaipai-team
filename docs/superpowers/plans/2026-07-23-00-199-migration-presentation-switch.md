# 00-199 Migration And Presentation Switch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate historical profile media and share selections into typed relations, then switch every public/share/AI/completeness reader to a relation-backed presentation resolver without deleting legacy fields.

**Architecture:** Preserve legacy columns as short-lived read-only compatibility inputs during migration. Copy historical objects into private storage, create explicit profile/work/share relationships, expose only resolver DTOs with scenario-scoped signed URLs, and stop new writes to legacy JSON before a separate physical-retirement audit.

**Tech Stack:** Spring Boot 3.2, Java 17, MyBatis-Plus, MySQL 8, Tencent COS private objects and temporary signatures, JUnit 5/Mockito, uni-app/Vue 3/TypeScript, Node static verification.

---

## Preconditions And Migration Order

Plan 1 has delivered profile/work/asset/relation/favorite tables and APIs. Plan 2 has delivered DeepSeek apply that writes only new domains. Plan 3 has moved profile editing, work library, asset library, and favorite UI to new APIs.

Use this migration order; do not change an already applied SQL file:

```text
# Already applied prerequisites
V20260723_001__career_profile_domain_foundation.sql
V20260723_002__actor_media_asset_relations.sql
V20260723_003__share_card_favorite.sql
V20260723_004__ai_profile_import_governance.sql
V20260723_005__ai_profile_import_permission_alignment.sql

# Required runtime order
standalone read-only baseline inspect (legacy schema only; no V006 dependency)
deploy:
V20260723_006__profile_library_presentation_and_ai_asset_refs.sql
dry-run -> apply -> verify
isolated rollback rehearsal -> rollback verify
Wang Huohuo restore-fixture -> restore verify
only after real verify plus rollback/restore evidence: author -> test -> deploy
V20260723_007__actor_experience_active_dedupe_gate.sql
resolver/read switch
```

`V005` already belongs to DeepSeek permission alignment. Before `V006` is deployed, capture the baseline through a standalone read-only inspector that reads only legacy schema and neither needs nor writes migration batch/mapping/exception tables. `V006` then creates those tables plus `actor_ai_profile_card_task.source_asset_id` and `generated_asset_id`; it does not drop legacy URL fields or add a legacy URL fallback to public resolution. `V007` is a separate post-backfill gate: do not author its SQL or test resource, commit it, package it, deploy it, or execute it until real target-database `verify` proves active blank normalized/dedupe keys and duplicate `(user_id, dedupe_key)` groups are both zero. A failed precheck blocks the migration and never auto-deletes or auto-merges historical works.

Resolver and `V006` implementation code may be developed and tested before the controlled migration, but the only production order is `standalone read-only baseline inspect -> deploy V006 -> hash-bound dry-run/apply/verify -> isolated rollback rehearsal/verify -> Wang Huohuo restore-fixture/verify -> V007 RED/GREEN/commit/deploy -> resolver/read switch`. Never substitute a post-`V006` inspect for the baseline or include any `V007` resource before all pre-V007 evidence passes.

## File Map

- Create: `kaipaile-server/src/main/resources/db/migration/V20260723_006__profile_library_presentation_and_ai_asset_refs.sql`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/migration/ProfileLibraryMigrationMode.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/migration/ProfileLibraryMigrationReport.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/migration/ProfileLibraryMigrationService.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/migration/ProfileLibraryMigrationCommand.java`
- Create: `kaipaile-server/src/test/java/com/kaipai/ProfileLibraryMigrationRunner.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/actor/dto/ActorProfilePresentationRespDTO.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/card/dto/ShareCardPresentationRespDTO.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/presentation/ProfilePresentationResolver.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/presentation/ProfilePresentationResolverImpl.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/presentation/ProfileCompletenessSnapshot.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/card/dto/ShareCardContentSaveDTO.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/card/dto/ShareCardContentRespDTO.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/card/ShareCardContentSelectionService.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/card/impl/ShareCardContentSelectionServiceImpl.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/ai/profilecard/AiGeneratedImageStorage.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/card/impl/ActorCardConfigServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/card/impl/UserShareCardServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/card/impl/ActorPersonalizationServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/card/impl/ShareCardViewHistoryServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/card/impl/ShareCardFavoriteServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/actor/support/ActorProfileCompletionCalculator.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/capability/impl/CapabilityAccountServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/verify/impl/IdentityVerificationServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/recruit/impl/RecruitApplyServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/ai/impl/AiProfileCardServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/ai/profilecard/AiProfileCardPromptAgent.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/controller/api/actor/ActorController.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/controller/api/actor/ActorProfileController.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/controller/api/card/CardController.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/controller/api/ai/AiProfileCardController.java`
- Create: `kaipai-frontend/src/types/profile-presentation.ts`
- Create: `kaipai-frontend/src/api/profile-presentation.ts`
- Create: `kaipai-frontend/src/api/share-card-content.ts`
- Modify: `kaipai-frontend/src/types/personalization.ts`
- Modify: `kaipai-frontend/src/types/level.ts`
- Modify: `kaipai-frontend/src/types/ai-profile-card.ts`
- Modify: `kaipai-frontend/src/api/level.ts`
- Modify: `kaipai-frontend/src/api/ai-profile-card.ts`
- Modify: `kaipai-frontend/src/utils/share-card-latest.ts`
- Modify: `kaipai-frontend/src/utils/actor-card.ts`
- Modify: `kaipai-frontend/src/pkg-card/card-list/index.vue`
- Modify: `kaipai-frontend/src/pkg-card/portfolio/index.vue`
- Modify: `kaipai-frontend/src/pkg-card/actor-card/index.vue`
- Modify: `kaipai-frontend/src/pages/actor-profile/detail.vue`
- Modify: `kaipai-frontend/src/pkg-card/ai-profile-card/index.vue`
- Modify: `kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue`
- Modify: `kaipai-frontend/src/pages/apply-confirm/index.vue`
- Modify: `.sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs`

`V007` and `ActiveWorkDedupeGateMigrationTest` are deliberately absent from this initial File Map. Task 6 first creates them inside its post-verify-only step; they must not exist in the worktree, a commit, or a package before the authorized real-database verify succeeds.

## Shared Presentation Contract

```java
public interface ProfilePresentationResolver {
    ActorProfilePresentationRespDTO resolvePublicProfile(Long profileUserId, Long viewerUserId);
    ShareCardPresentationRespDTO resolveShareCard(Long shareCardId, Long viewerUserId);
    ProfileCompletenessSnapshot resolveOwnedCompleteness(Long ownerUserId);
}

public record PresentedAsset(
        Long assetId,
        String mediaType,
        String categoryCode,
        String originalName,
        String accessUrl,
        Instant accessUrlExpiresAt,
        Integer sortNo) {}

public record PresentedWork(
        Long experienceId,
        String projectName,
        String roleName,
        String publishStatus,
        String workTypeCode,
        String roleLevelCode,
        String syncSoundStatus,
        List<String> collaborators,
        String achievementText,
        String description,
        List<PresentedAsset> stills,
        List<PresentedAsset> clips) {}
```

Public DTOs must not contain storage object keys, buckets, legacy URLs, `extended_field`, raw photo arrays, unselected private assets, or private contact information.

## Task 1: Create a Repeatable Per-User Migration

**Files:**
- Create: `kaipaile-server/src/main/resources/db/migration/V20260723_006__profile_library_presentation_and_ai_asset_refs.sql`
- Create: all `service/actor/migration` paths listed above
- Create: `kaipaile-server/src/test/java/com/kaipai/ProfileLibraryMigrationRunner.java`
- Test: `kaipaile-server/src/test/java/com/kaipai/module/server/actor/migration/ProfileLibraryMigrationServiceTest.java`

- [ ] **Step 1: Write red migration tests**

```java
@Test
void secondApplyReusesLegacyMapAndDoesNotCreateAnotherAsset() {
    migrationService.applyProfile(BATCH_ID, profileWithOneLegacyPhoto());
    migrationService.applyProfile(BATCH_ID, profileWithOneLegacyPhoto());

    verify(assetMapper, times(1)).insert(any(ActorMediaAsset.class));
    verify(profileAssetMapper, times(1)).insert(any(ActorProfileAsset.class));
}

@Test
void malformedExtendedFieldRecordsExceptionAndDoesNotPartiallyMigrateUser() {
    var result = migrationService.applyProfile(BATCH_ID, profileWithMalformedExtendedField());

    assertEquals(MigrationStatus.FAILED, result.status());
    verify(exceptionMapper).insert(argThat(item -> "parse_extended_field".equals(item.getStageCode())));
    verifyNoInteractions(assetMapper, profileAssetMapper, workAssetMapper);
}

@Test
void standaloneBaselineInspectWorksAgainstLegacySchemaWithoutV006Tables() {
    try (Connection legacyOnly = MigrationTestDatabase.applyLegacySchemaOnly()) {
        ProfileLibraryMigrationReport report = baselineInspector.inspect(legacyOnly);

        assertNotNull(report.baselineHash());
        assertTableMissing(legacyOnly, "profile_library_migration_batch");
        assertTableMissing(legacyOnly, "profile_library_legacy_asset_map");
        assertTableMissing(legacyOnly, "profile_library_migration_exception");
    }
}

@Test
void canonicalBaselineHashIsStableAndDryRunRejectsLegacyDrift() {
    BaselineArtifact first = baselineInspector.inspect(legacyConnection());
    BaselineArtifact second = baselineInspector.inspect(legacyConnection());
    assertEquals(first.baselineHash(), second.baselineHash());

    migrationBatchMapper.insert(batch(BATCH_ID, first.baselineHash()));
    mutateLegacyProfileAfterInspect();

    BaselineDriftException error = assertThrows(BaselineDriftException.class,
        () -> migrationService.dryRun(BATCH_ID, first.baselineHash()));
    assertEquals("BASELINE_DRIFT", error.code());
    verifyNoInteractions(assetMapper, profileAssetMapper, workAssetMapper);
}
```

- [ ] **Step 2: Run the red tests**

Run:

```powershell
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -Dtest=ProfileLibraryMigrationServiceTest test
```

Expected: FAIL because migration batching, legacy mapping, exception reporting, and rollback compensation do not exist.

- [ ] **Step 3: Implement fixed migration rules**

For each user, strictly parse `extended_field`; malformed JSON writes a hashed exception and leaves the user unmodified. For valid data, copy objects to private storage, then run one database transaction that creates assets, pages, explicit relations, mapping rows, `avatar_asset_id`, and `current_resume_asset_id`. If the database transaction fails, delete objects copied in that attempt and record a hashed cleanup error if deletion fails. `V006` gives migration batch/audit rows a required `baseline_hash` column.

| Legacy source | New relation |
|---|---|
| `actor_profile.avatar_url` | photo asset + `avatar_asset_id` |
| profile photo arrays/categories | photo asset + `actor_profile_asset(public_photo)` |
| `video_url` | video asset + `actor_profile_asset(public_video)` |
| legacy PDF and page URLs | PDF asset/pages + `current_resume_asset_id` + `public_resume` relation |
| work image JSON | `actor_work_asset(still)` |
| `highlighted_experience_ids` | ordered `share_card_work` |
| `highlighted_photo_urls` | `share_card_asset`, first `cover`, remainder `gallery` |
| successful AI image URLs | `source_asset_id`/`generated_asset_id` and active share-card cover relation |

The runner accepts `inspect`, `validate-baseline-artifact`, `dry-run`, `apply`, `verify`, and `rollback`. Its `inspect` mode delegates to a standalone read-only baseline inspector that queries only legacy tables and works before `V006`; it does not create a batch or call any `V006` mapper. It writes a sanitized canonical artifact and stable SHA-256 hash. `validate-baseline-artifact` is database-free: it requires the approved artifact path, reparses the file, verifies the artifact `batchId`, canonical payload, and SHA-256 `baselineHash`, and rejects a path/batch mismatch or modified content before a caller exports process-local batch/hash values. Every database mode requires both `--baseline-artifact` and `--expected-baseline-hash`, rereads legacy inputs through the same canonicalizer before doing work, compares the recomputed hash with the artifact, argument, and batch/audit binding, and fails closed with `BASELINE_DRIFT` before object copies or database mutation. It reads database/COS credentials only from environment variables, and it outputs counts, identifiers, hashes, and stable errors but never raw URLs, source text, credentials, or tokens.

Historical `actor_experience` rows receive normalized names, nonblank dedupe keys, and server-owned `source_type=migration`; this provenance is distinct from import-candidate evidence source types. The runner consumes `wang-huohuo-works-golden.json` as a 29-row normalized expectation (`aired=14 / upcoming=6 / stage=3 / horizontal=6`) but never stores or prints the clipboard body.

- [ ] **Step 4: Run green tests**

Run:

```powershell
mvn -q -Dtest=ProfileLibraryMigrationServiceTest test
```

Expected: PASS for strict parsing, idempotent mapping, per-user transaction, and compensation boundaries.

- [ ] **Step 5: Commit**

```powershell
git add kaipaile-server/src/main/resources/db/migration/V20260723_006__profile_library_presentation_and_ai_asset_refs.sql kaipaile-server/src/main/java/com/kaipai/service/actor/migration kaipaile-server/src/test/java/com/kaipai/ProfileLibraryMigrationRunner.java kaipaile-server/src/test/java/com/kaipai/module/server/actor/migration/ProfileLibraryMigrationServiceTest.java
git commit -m "feat(profile-library): add repeatable legacy media migration"
```

## Task 2: Add Relation-Backed Presentation Resolver

**Files:**
- Create: `kaipaile-server/src/main/java/com/kaipai/model/actor/dto/ActorProfilePresentationRespDTO.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/card/dto/ShareCardPresentationRespDTO.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/presentation/ProfilePresentationResolver.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/presentation/ProfilePresentationResolverImpl.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/presentation/ProfileCompletenessSnapshot.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/controller/api/actor/ActorController.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/controller/api/actor/ActorProfileController.java`
- Test: `kaipaile-server/src/test/java/com/kaipai/module/server/actor/presentation/ProfilePresentationResolverTest.java`

- [ ] **Step 1: Write resolver red tests**

```java
@Test
void shareCardPresentationUsesOnlySelectedRelationsAndNeverLegacyUrls() {
    when(shareCardWorkMapper.selectList(any())).thenReturn(List.of(selectedWork(41L, 1)));
    when(shareCardAssetMapper.selectList(any())).thenReturn(List.of(selectedAsset(81L, "cover", 1)));
    when(actorCardConfigMapper.selectById(any())).thenReturn(configWithLegacyPhotoUrl());

    ShareCardPresentationRespDTO result = resolver.resolveShareCard(12L, null);

    assertEquals(List.of(41L), result.getWorks().stream().map(PresentedWork::experienceId).toList());
    assertEquals(List.of(81L), result.getAssets().stream().map(PresentedAsset::assetId).toList());
    assertFalse(result.toString().contains("legacy-photo.example"));
}

@Test
void publicProfileOmitsPrivateUnrelatedAsset() {
    when(profileAssetMapper.selectList(any())).thenReturn(List.of(privateAssetRelation(91L)));

    ActorProfilePresentationRespDTO result = resolver.resolvePublicProfile(PROFILE_USER_ID, null);

    assertTrue(result.getAssets().isEmpty());
}
```

- [ ] **Step 2: Run the red tests**

Run:

```powershell
mvn -q -Dtest=ProfilePresentationResolverTest test
```

Expected: FAIL because current readers still hydrate old `ActorProfileDTO.photos`, `workExperiences`, and highlighted JSON arrays.

- [ ] **Step 3: Implement resolver and presentation endpoints**

`resolvePublicProfile` reads only avatar asset, representative work relations, `public_photo/public_video/public_resume` relations, and work still/clip relations. `resolveShareCard` reads only active share-card work and asset relations in sort order. Both validate `ready`, relation existence, and access scene before asking the asset service for a short-lived URL.

Expose:

```http
GET /api/actor/{userId}/presentation
GET /api/actor/profile/mine/presentation
```

Existing legacy read endpoints can temporarily return projections built from the resolver, but they may not source URLs from old media fields.

- [ ] **Step 4: Run the green tests**

Run:

```powershell
mvn -q -Dtest=ProfilePresentationResolverTest test
```

Expected: PASS for relation-only public reads, short URL issuance, and no legacy URL leakage.

- [ ] **Step 5: Commit**

```powershell
git add kaipaile-server/src/main/java/com/kaipai/model/actor/dto/ActorProfilePresentationRespDTO.java kaipaile-server/src/main/java/com/kaipai/model/card/dto/ShareCardPresentationRespDTO.java kaipaile-server/src/main/java/com/kaipai/service/actor/presentation kaipaile-server/src/main/java/com/kaipai/controller/api/actor/ActorController.java kaipaile-server/src/main/java/com/kaipai/controller/api/actor/ActorProfileController.java kaipaile-server/src/test/java/com/kaipai/module/server/actor/presentation/ProfilePresentationResolverTest.java
git commit -m "feat(profile-library): add relation backed presentation resolver"
```

## Task 3: Store Share-Card Content As Explicit References

**Files:**
- Create: `kaipaile-server/src/main/java/com/kaipai/model/card/dto/ShareCardContentSaveDTO.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/card/dto/ShareCardContentRespDTO.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/card/ShareCardContentSelectionService.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/card/impl/ShareCardContentSelectionServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/controller/api/card/CardController.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/card/impl/ActorCardConfigServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/card/impl/UserShareCardServiceImpl.java`
- Test: `kaipaile-server/src/test/java/com/kaipai/module/server/card/ShareCardContentSelectionServiceImplTest.java`

- [ ] **Step 1: Write content selection red tests**

```java
@Test
void savingContentReplacesRelationsWithoutWritingLegacyHighlightJson() {
    contentService.save(OWNER_ID, CARD_ID, request(List.of(41L), List.of(asset(81L, "cover", 1))));

    verify(shareCardWorkMapper).delete(any());
    verify(shareCardWorkMapper).insert(argThat(item -> item.getExperienceId().equals(41L)));
    verify(shareCardAssetMapper).insert(argThat(item -> item.getAssetId().equals(81L)));
    verify(actorCardConfigMapper, never()).update(argThat(item ->
        item.getHighlightedPhotoUrls() != null || item.getHighlightedExperienceIds() != null), any());
}
```

- [ ] **Step 2: Run the red test**

Run:

```powershell
mvn -q -Dtest=ShareCardContentSelectionServiceImplTest test
```

Expected: FAIL because Card configuration writes content into legacy JSON fields.

- [ ] **Step 3: Implement content API and create-card defaults**

Expose:

```http
GET /api/card/{shareCardId}/content
PUT /api/card/{shareCardId}/content
```

The save transaction verifies active-card ownership, work ownership, ready assets, accepted usage codes `cover/gallery/video/resume`, and then replaces sorted relation rows. On card creation, create the first relation set from representative works and public assets. Keep layout/theme settings in `actor_card_config`, but never use its highlight arrays as a new content writer.

- [ ] **Step 4: Run the green test and commit**

Run:

```powershell
mvn -q -Dtest=ShareCardContentSelectionServiceImplTest test
```

Expected: PASS and no content writer invokes legacy highlight JSON.

```powershell
git add kaipaile-server/src/main/java/com/kaipai/model/card/dto/ShareCardContentSaveDTO.java kaipaile-server/src/main/java/com/kaipai/model/card/dto/ShareCardContentRespDTO.java kaipaile-server/src/main/java/com/kaipai/service/card/ShareCardContentSelectionService.java kaipaile-server/src/main/java/com/kaipai/service/card/impl/ShareCardContentSelectionServiceImpl.java kaipaile-server/src/main/java/com/kaipai/controller/api/card/CardController.java kaipaile-server/src/main/java/com/kaipai/service/card/impl/ActorCardConfigServiceImpl.java kaipaile-server/src/main/java/com/kaipai/service/card/impl/UserShareCardServiceImpl.java kaipaile-server/src/test/java/com/kaipai/module/server/card/ShareCardContentSelectionServiceImplTest.java
git commit -m "feat(share-card): store selected content by reference"
```

## Task 4: Switch Backend Completion, History, Favorite, And AI Consumers

**Files:**
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/card/impl/ActorPersonalizationServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/card/impl/ShareCardViewHistoryServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/card/impl/ShareCardFavoriteServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/actor/support/ActorProfileCompletionCalculator.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/capability/impl/CapabilityAccountServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/verify/impl/IdentityVerificationServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/recruit/impl/RecruitApplyServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/model/ai/entity/ActorAiProfileCardTask.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/model/ai/dto/AiProfileCardGenerateReqDTO.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/ai/impl/AiProfileCardServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/ai/profilecard/AiProfileCardPromptAgent.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/controller/api/ai/AiProfileCardController.java`
- Test: `kaipaile-server/src/test/java/com/kaipai/module/server/actor/ActorProfileCompletionCalculatorTest.java`
- Test: `kaipaile-server/src/test/java/com/kaipai/module/server/ai/service/impl/AiProfileCardServiceImplTest.java`
- Test: `kaipaile-server/src/test/java/com/kaipai/module/server/ai/profilecard/AiProfileCardPromptAgentTest.java`

- [ ] **Step 1: Write red consumer tests**

```java
@Test
void completenessUsesReadyReferencedAssetsNotLegacyPhotoColumns() {
    ProfileCompletenessSnapshot snapshot = new ProfileCompletenessSnapshot(true, true, 3, 1, 2, true, true, true);

    assertEquals(70, ActorProfileCompletionCalculator.calculate(snapshot));
}

@Test
void generateUsesOwnedReadySourceAssetNotClientUrl() {
    AiProfileCardGenerateReqDTO request = new AiProfileCardGenerateReqDTO();
    request.setSourceAssetId(601L);

    service.generate(OWNER_ID, request);

    verify(actorMediaAssetService).requireOwnedReadyPhoto(OWNER_ID, 601L);
    verifyNoInteractions(legacyUrlResolver);
}
```

- [ ] **Step 2: Run the red tests**

Run:

```powershell
mvn -q -Dtest=ActorProfileCompletionCalculatorTest,AiProfileCardServiceImplTest,AiProfileCardPromptAgentTest test
```

Expected: FAIL because the current implementations read profile photo/video/works arrays and client image URLs.

- [ ] **Step 3: Implement resolver consumption**

Make personalization, browsing history, favorites, completion, capability, verification, and recruit apply read `ProfilePresentationResolver` or its owned completeness snapshot. Old profile columns with values but without ready relations must not make a profile appear completed.

Change AI generation to accept `sourceAssetId`, validate ownership/ready state, issue a provider-scoped signed URL server-side, store generated results as private assets, and create the selected share-card cover relation. `AiProfileCardPromptAgent` reads presentation data, never `ActorProfileDTO.workExperiences` or photo arrays.

- [ ] **Step 4: Run the green tests and commit**

Run:

```powershell
mvn -q -Dtest=ActorProfileCompletionCalculatorTest,AiProfileCardServiceImplTest,AiProfileCardPromptAgentTest test
```

Expected: PASS for resolver-only consumers and source-asset AI generation.

```powershell
git add kaipaile-server/src/main/java/com/kaipai/service/card/impl kaipaile-server/src/main/java/com/kaipai/service/actor/support/ActorProfileCompletionCalculator.java kaipaile-server/src/main/java/com/kaipai/service/capability/impl/CapabilityAccountServiceImpl.java kaipaile-server/src/main/java/com/kaipai/service/verify/impl/IdentityVerificationServiceImpl.java kaipaile-server/src/main/java/com/kaipai/service/recruit/impl/RecruitApplyServiceImpl.java kaipaile-server/src/main/java/com/kaipai/model/ai kaipaile-server/src/main/java/com/kaipai/service/ai kaipaile-server/src/main/java/com/kaipai/controller/api/ai/AiProfileCardController.java kaipaile-server/src/test/java/com/kaipai/module/server
git commit -m "refactor(profile-library): switch consumers to presentation facts"
```

## Task 5: Switch Mini-Program Presentation Consumers And Stop Legacy Writes

**Files:**
- Create: `kaipai-frontend/src/types/profile-presentation.ts`
- Create: `kaipai-frontend/src/api/profile-presentation.ts`
- Create: `kaipai-frontend/src/api/share-card-content.ts`
- Modify: `kaipai-frontend/src/types/personalization.ts`
- Modify: `kaipai-frontend/src/types/level.ts`
- Modify: `kaipai-frontend/src/types/ai-profile-card.ts`
- Modify: `kaipai-frontend/src/api/level.ts`
- Modify: `kaipai-frontend/src/api/ai-profile-card.ts`
- Modify: `kaipai-frontend/src/utils/share-card-latest.ts`
- Modify: `kaipai-frontend/src/utils/actor-card.ts`
- Modify: `kaipai-frontend/src/pkg-card/card-list/index.vue`
- Modify: `kaipai-frontend/src/pkg-card/portfolio/index.vue`
- Modify: `kaipai-frontend/src/pkg-card/actor-card/index.vue`
- Modify: `kaipai-frontend/src/pages/actor-profile/detail.vue`
- Modify: `kaipai-frontend/src/pkg-card/ai-profile-card/index.vue`
- Modify: `kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue`
- Modify: `kaipai-frontend/src/pages/apply-confirm/index.vue`
- Modify: `.sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs`

- [ ] **Step 1: Add failing static assertions for old consumers**

```js
const consumers = [
  'kaipai-frontend/src/pages/actor-profile/detail.vue',
  'kaipai-frontend/src/pkg-card/actor-card/index.vue',
  'kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue',
  'kaipai-frontend/src/pkg-card/portfolio/index.vue',
  'kaipai-frontend/src/pkg-card/card-list/index.vue',
]
for (const file of consumers) {
  const source = await readText(file)
  assertNoMatch(source, /highlightedPhotos|highlightedExperiences|resumePdfPageImageUrls|videoUrl/)
}
assertNoMatch(await readText('kaipai-frontend/src/pkg-card/card-list/index.vue'), /updateActorProfile|buildPhotoProfilePayload/)
assertNoMatch(await readText('kaipai-frontend/src/pkg-card/ai-profile-card/index.vue'), /updateActorProfile|sourceImageUrl/)
```

- [ ] **Step 2: Run the red gate**

Run:

```powershell
node .sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: FAIL because share/list/detail pages still use old arrays and URL writers.

- [ ] **Step 3: Implement relation-backed frontend types and readers**

`profile-presentation.ts` models `assetId`, `accessUrl`, `accessUrlExpiresAt`, ordered works, and PDF pages. `share-card-latest.ts` returns a `presentation` object. `actor-card.ts` only formats presentation data; it no longer chooses representative content from local `highlighted*` arrays.

`card-list/index.vue` selects asset IDs and calls `/api/card/{shareCardId}/content`. `portfolio/index.vue` retains share management but reads works/assets through the new APIs. Public detail and AI detail render only the resolver response. AI profile-card input uses `sourceAssetId`. Apply-confirm uses owned presentation readiness instead of `videoUrl`.

- [ ] **Step 4: Run green frontend checks**

Run:

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
npm run type-check
npm run build:mp-weixin
npm run audit:steering
npm run audit:mp-package
```

Expected: all commands pass; source and both generated `app.json` files contain the expected subpackage and no old consumer writer.

- [ ] **Step 5: Commit**

```powershell
git add kaipai-frontend/src/types/profile-presentation.ts kaipai-frontend/src/api/profile-presentation.ts kaipai-frontend/src/api/share-card-content.ts kaipai-frontend/src/types/personalization.ts kaipai-frontend/src/types/level.ts kaipai-frontend/src/types/ai-profile-card.ts kaipai-frontend/src/api/level.ts kaipai-frontend/src/api/ai-profile-card.ts kaipai-frontend/src/utils/share-card-latest.ts kaipai-frontend/src/utils/actor-card.ts kaipai-frontend/src/pkg-card/card-list/index.vue kaipai-frontend/src/pkg-card/portfolio/index.vue kaipai-frontend/src/pkg-card/actor-card/index.vue kaipai-frontend/src/pages/actor-profile/detail.vue kaipai-frontend/src/pkg-card/ai-profile-card/index.vue kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue kaipai-frontend/src/pages/apply-confirm/index.vue .sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs
git commit -m "refactor(miniapp): consume profile presentation facts"
```

## Task 6: Stop Legacy Writes And Record Evidence

**Files:**
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/actor/impl/ActorProfileServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/ai/impl/AiResumeServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/ai/impl/AiResumeApplyRecorderImpl.java`
- Modify: `.sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/execution.md`
- Modify: `.sce/specs/spec-code-mapping.md`
- Modify: `docs/product-design.md`

`V007` SQL and its dedicated test are intentionally not Task 6 start files. They first appear as outputs inside Step 6, after the authorized real `verify`, isolated rollback, and fixture restore reports have passed.

- [ ] **Step 1: Add the legacy-write regression test**

```java
@Test
void legacyAggregatePayloadCannotMutateWorkOrAssetCollections() {
    ActorProfileSaveDTO request = legacyPayloadWithTenWorksAndPhotoUrls();

    assertThrows(BizException.class, () -> profileService.saveProfile(USER_ID, request));

    verifyNoInteractions(actorExperienceMapper, actorMediaAssetMapper, profileAssetMapper);
}
```

- [ ] **Step 2: Enforce write stop**

Allow compatible legacy scalar updates only. Any non-empty old work/photo/video/PDF collection returns `PROFILE_LEGACY_COLLECTION_WRITE_RETIRED`; empty or missing collections are no-op. AI resume polish and its apply recorder must not route through the legacy aggregate DTO.

- [ ] **Step 3: Capture the standalone read-only baseline before deploying V006**

Before the target database has `V006`, and only after explicit environment inspection authorization, run:

```powershell
$env:PROFILE_MIGRATION_BATCH_ID = "00-199-" + (Get-Date -Format "yyyyMMddHHmmss")
$baselineArtifact = "D:\XM\kaipai-team\output\migrations\00-199\$env:PROFILE_MIGRATION_BATCH_ID\baseline.json"
$baselineRepeatArtifact = "D:\XM\kaipai-team\output\migrations\00-199\$env:PROFILE_MIGRATION_BATCH_ID\baseline-repeat.json"
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.ProfileLibraryMigrationRunner -Dexec.args="inspect --batch=$env:PROFILE_MIGRATION_BATCH_ID --baseline-artifact=$baselineArtifact" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.ProfileLibraryMigrationRunner -Dexec.args="inspect --batch=$env:PROFILE_MIGRATION_BATCH_ID --baseline-artifact=$baselineRepeatArtifact" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
$baseline = Get-Content -Raw -LiteralPath $baselineArtifact | ConvertFrom-Json
$baselineRepeat = Get-Content -Raw -LiteralPath $baselineRepeatArtifact | ConvertFrom-Json
$artifactBatchId = [string]$baseline.batchId
$repeatBatchId = [string]$baselineRepeat.batchId
if (-not $artifactBatchId -or $artifactBatchId -ne $env:PROFILE_MIGRATION_BATCH_ID) { throw 'baseline artifact batchId missing or inconsistent' }
if ($repeatBatchId -ne $artifactBatchId) { throw 'repeat baseline artifact batchId is inconsistent' }
$env:PROFILE_MIGRATION_BASELINE_HASH = [string]$baseline.baselineHash
if ($env:PROFILE_MIGRATION_BASELINE_HASH -notmatch '^sha256:[0-9a-f]{64}$') { throw 'baseline hash missing or invalid' }
if ($env:PROFILE_MIGRATION_BASELINE_HASH -ne [string]$baselineRepeat.baselineHash) { throw 'baseline hash is not reproducible' }
```

Expected: PASS against legacy schema without any `V006` migration table. The artifact contains its nonblank `batchId`, only sanitized canonical counts/hashes, and a stable SHA-256 `baselineHash`; repeating inspect against unchanged inputs reproduces the same batch/hash. Record the artifact path, batch ID, and hash outside database migration tables, then stop. After approval, the operator must retain or copy the exact approved artifact to a protected, immutable path that preserves the final `{batchId}\baseline.json` segments. In each later PowerShell session the operator explicitly sets required `PROFILE_MIGRATION_BASELINE_ARTIFACT` to that approved path; Step 3 process environment variables are ephemeral and must never be treated as continuation evidence. Do not deploy `V006` until this evidence is reviewed and confirmed restorable.

- [ ] **Step 4: Deploy V006, then run hash-bound dry-run, apply, and verify**

After the Step 3 baseline is approved, deploy the already tested `V20260723_006__profile_library_presentation_and_ai_asset_refs.sql` through the repository's standard backend migration release and confirm its Flyway history row succeeded. In a new controlled PowerShell session, the operator sets `PROFILE_MIGRATION_BASELINE_ARTIFACT` to the protected approved artifact; the block derives batch/hash from that file and does not depend on Step 3 environment state:

```powershell
if (-not $env:PROFILE_MIGRATION_BASELINE_ARTIFACT) { throw 'approved baseline artifact path missing' }
$baselineArtifactPath = (Resolve-Path -LiteralPath $env:PROFILE_MIGRATION_BASELINE_ARTIFACT -ErrorAction Stop).Path
$baselineArtifact = Get-Content -Raw -LiteralPath $baselineArtifactPath | ConvertFrom-Json
$artifactBatchId = [string]$baselineArtifact.batchId
$artifactBaselineHash = [string]$baselineArtifact.baselineHash
if (-not $artifactBatchId) { throw 'baseline artifact batchId missing' }
if ($artifactBaselineHash -notmatch '^sha256:[0-9a-f]{64}$') { throw 'baseline artifact hash missing or invalid' }
if ($null -eq $baselineArtifact.canonicalPayload) { throw 'baseline artifact canonical payload missing' }
if ((Split-Path -Leaf $baselineArtifactPath) -ne 'baseline.json') { throw 'approved artifact filename must remain baseline.json' }
if ((Split-Path -Leaf (Split-Path -Parent $baselineArtifactPath)) -ne $artifactBatchId) { throw 'baseline artifact path and batchId are inconsistent' }
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.ProfileLibraryMigrationRunner -Dexec.args="validate-baseline-artifact --baseline-artifact=$baselineArtifactPath --batch=$artifactBatchId --expected-baseline-hash=$artifactBaselineHash" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
if ($LASTEXITCODE -ne 0) { throw 'approved baseline artifact content validation failed' }
$env:PROFILE_MIGRATION_BATCH_ID = $artifactBatchId
$env:PROFILE_MIGRATION_BASELINE_HASH = $artifactBaselineHash
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.ProfileLibraryMigrationRunner -Dexec.args="dry-run --baseline-artifact=$baselineArtifactPath --batch=$env:PROFILE_MIGRATION_BATCH_ID --expected-baseline-hash=$env:PROFILE_MIGRATION_BASELINE_HASH" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.ProfileLibraryMigrationRunner -Dexec.args="apply --baseline-artifact=$baselineArtifactPath --batch=$env:PROFILE_MIGRATION_BATCH_ID --expected-baseline-hash=$env:PROFILE_MIGRATION_BASELINE_HASH" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.ProfileLibraryMigrationRunner -Dexec.args="verify --baseline-artifact=$baselineArtifactPath --batch=$env:PROFILE_MIGRATION_BATCH_ID --expected-baseline-hash=$env:PROFILE_MIGRATION_BASELINE_HASH" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
```

Before each mode does any work it rereads legacy inputs, rebuilds the canonical baseline, compares it with `--expected-baseline-hash`, and checks the migration batch/audit binding. Drift returns `BASELINE_DRIFT` with no object copy, business write, or batch advancement. `verify` must compare counts, owners, relation references, active public behavior, migration duplicate-run totals, rollback results, and the restorable Wang Huohuo snapshot. For the fixed golden import sample it must query the database and prove 29 active rows, 29 distinct `experience_id` values, 29 distinct nonblank `dedupe_key` values, category counts `14/6/3/6`, and 29 distinct results after paging. Its second import uses a fresh request ID, fresh successful audit/proofs, current context versions, and matched `skip` actions for the same content; the database must remain at 29. The same-request idempotent return is a separate test and is not this proof. A mock total, fixture self-comparison, or loop that seeds the expected count is not evidence. It must never print raw source text, credentials, permanent URLs, or signed URLs.

- [ ] **Step 5: Rehearse rollback in isolation and restore the Wang Huohuo fixture**

Prepare an explicitly authorized isolated clone at the same schema/data checkpoint as the verified target. Start from a new PowerShell session and set the approved artifact path, clone JDBC URL, primary JDBC URL used only for inequality checking, fixed Wang Huohuo test user ID, and the clone's allowlisted rehearsal environment ID. `restore-fixture` and `verify-restore` are rehearsal-clone-only commands; they are not production recovery procedures.

```powershell
if (-not $env:PROFILE_MIGRATION_BASELINE_ARTIFACT) { throw 'approved baseline artifact path missing' }
$baselineArtifactPath = (Resolve-Path -LiteralPath $env:PROFILE_MIGRATION_BASELINE_ARTIFACT -ErrorAction Stop).Path
$baselineArtifact = Get-Content -Raw -LiteralPath $baselineArtifactPath | ConvertFrom-Json
$artifactBatchId = [string]$baselineArtifact.batchId
$artifactBaselineHash = [string]$baselineArtifact.baselineHash
if (-not $artifactBatchId) { throw 'baseline artifact batchId missing' }
if ($artifactBaselineHash -notmatch '^sha256:[0-9a-f]{64}$') { throw 'baseline artifact hash missing or invalid' }
if ($null -eq $baselineArtifact.canonicalPayload) { throw 'baseline artifact canonical payload missing' }
if ((Split-Path -Leaf $baselineArtifactPath) -ne 'baseline.json') { throw 'approved artifact filename must remain baseline.json' }
if ((Split-Path -Leaf (Split-Path -Parent $baselineArtifactPath)) -ne $artifactBatchId) { throw 'baseline artifact path and batchId are inconsistent' }
if (-not $env:PROFILE_MIGRATION_REHEARSAL_JDBC_URL) { throw 'isolated rehearsal JDBC URL missing' }
if (-not $env:PROFILE_MIGRATION_PRIMARY_JDBC_URL) { throw 'primary JDBC URL is required for rehearsal inequality check' }
if ($env:PROFILE_MIGRATION_REHEARSAL_JDBC_URL -eq $env:PROFILE_MIGRATION_PRIMARY_JDBC_URL) { throw 'rollback rehearsal must not use the primary database' }
if (-not $env:WANG_HUOHUO_TEST_USER_ID) { throw 'fixed Wang Huohuo test user ID missing' }
if (-not $env:PROFILE_MIGRATION_REHEARSAL_ENVIRONMENT_ID) { throw 'authorized rehearsal environment ID missing' }
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.ProfileLibraryMigrationRunner -Dexec.args="validate-baseline-artifact --baseline-artifact=$baselineArtifactPath --batch=$artifactBatchId --expected-baseline-hash=$artifactBaselineHash" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
if ($LASTEXITCODE -ne 0) { throw 'approved baseline artifact content validation failed' }
$env:PROFILE_MIGRATION_BATCH_ID = $artifactBatchId
$env:PROFILE_MIGRATION_BASELINE_HASH = $artifactBaselineHash
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.ProfileLibraryMigrationRunner -Dexec.args="rollback --baseline-artifact=$baselineArtifactPath --batch=$env:PROFILE_MIGRATION_BATCH_ID --expected-baseline-hash=$env:PROFILE_MIGRATION_BASELINE_HASH --jdbc-url-env=PROFILE_MIGRATION_REHEARSAL_JDBC_URL" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.ProfileLibraryMigrationRunner -Dexec.args="verify --baseline-artifact=$baselineArtifactPath --batch=$env:PROFILE_MIGRATION_BATCH_ID --expected-baseline-hash=$env:PROFILE_MIGRATION_BASELINE_HASH --expect-restored-baseline=true --jdbc-url-env=PROFILE_MIGRATION_REHEARSAL_JDBC_URL" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.CareerProfileMigrationRunner -Dexec.args="restore-fixture --baseline-artifact=$baselineArtifactPath --batch=$env:PROFILE_MIGRATION_BATCH_ID --fixture=wang-huohuo-baseline.json --expected-baseline-hash=$env:PROFILE_MIGRATION_BASELINE_HASH --jdbc-url-env=PROFILE_MIGRATION_REHEARSAL_JDBC_URL --user-id=$env:WANG_HUOHUO_TEST_USER_ID --environment-id=$env:PROFILE_MIGRATION_REHEARSAL_ENVIRONMENT_ID" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.CareerProfileMigrationRunner -Dexec.args="verify-restore --baseline-artifact=$baselineArtifactPath --batch=$env:PROFILE_MIGRATION_BATCH_ID --fixture=wang-huohuo-baseline.json --expected-baseline-hash=$env:PROFILE_MIGRATION_BASELINE_HASH --jdbc-url-env=PROFILE_MIGRATION_REHEARSAL_JDBC_URL --user-id=$env:WANG_HUOHUO_TEST_USER_ID --environment-id=$env:PROFILE_MIGRATION_REHEARSAL_ENVIRONMENT_ID" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
```

Expected: isolated rollback verify matches the canonical baseline, and Wang Huohuo restore verify matches the pre-test snapshot counts/hash. The fixture stores the fixed test `userId` and authorized rehearsal environment ID; both runners compare them with the explicit arguments, resolve the named JDBC environment, and reject a primary JDBC target, a primary environment marker, an unknown environment marker, or any fixture/user/environment mismatch before writes. Record both reports without JDBC URLs or raw fixture data. A successful production apply is not rolled back for rehearsal. Any production restore requires separate incident authorization, a dedicated recovery procedure, and explicit production safeguards; these rehearsal commands must never perform it.

- [ ] **Step 6: Author the V007 test, observe RED, then create SQL and observe GREEN**

Proceed only when the Step 4 real-database report records both `activeBlankNormalizedOrDedupeKeyCount=0` and `duplicateActiveUserDedupeGroupCount=0`, and Step 5 rollback/restore reports pass. Otherwise stop; do not create any `V007` SQL/test resource, commit/package/deploy it, auto-delete works, or enable resolver consumers.

First create only:

- `kaipaile-server/src/test/java/com/kaipai/module/server/actor/migration/ActiveWorkDedupeGateMigrationTest.java`

The Testcontainers test expects `V20260723_007__actor_experience_active_dedupe_gate.sql`, proves dirty/duplicate fixtures are rejected, and proves verified data receives the generated column/unique index and allows recreation after logical deletion. Run it before creating SQL:

Run:

```powershell
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -Dtest=ActiveWorkDedupeGateMigrationTest test
```

Expected RED: FAIL because `V20260723_007__actor_experience_active_dedupe_gate.sql` is missing.

Only after observing that RED, create `kaipaile-server/src/main/resources/db/migration/V20260723_007__actor_experience_active_dedupe_gate.sql`. It repeats the prechecks and fails closed, then adds stored generated `active_dedupe_key=CASE WHEN deleted=0 THEN dedupe_key ELSE NULL END` and unique index `uk_actor_experience_user_active_dedupe(user_id, active_dedupe_key)`. Rerun:

```powershell
mvn -q -Dtest=ActiveWorkDedupeGateMigrationTest test
```

Expected GREEN: PASS. Now create the first commit containing `V007` resources:

```powershell
git add kaipaile-server/src/main/resources/db/migration/V20260723_007__actor_experience_active_dedupe_gate.sql kaipaile-server/src/test/java/com/kaipai/module/server/actor/migration/ActiveWorkDedupeGateMigrationTest.java
git commit -m "feat(profile-library): gate active work dedupe after backfill"
```

Deploy that commit through the post-backfill migration release and confirm the target Flyway history row succeeds before enabling the production resolver/read switch.

- [ ] **Step 7: Run the final engineering gate**

Run:

```powershell
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -Dtest=ProfileLibraryMigrationServiceTest,ActiveWorkDedupeGateMigrationTest,ProfilePresentationResolverTest,ShareCardContentSelectionServiceImplTest,ActorProfileCompletionCalculatorTest,AiProfileCardServiceImplTest,AiProfileCardPromptAgentTest test
mvn -q clean package
cd ..\kaipai-frontend
npm run type-check
npm run build:mp-weixin
npm run audit:steering
npm run audit:mp-package
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

- [ ] **Step 8: Record and commit evidence**

`execution.md` records the ordered evidence `standalone pre-V006 baseline artifact/hash -> V006 deployment -> hash-bound dry-run/apply/verify -> isolated rollback/verify -> Wang Huohuo restore-fixture/verify -> V007 RED/GREEN/commit/deploy -> resolver switch`, batch ID, artifact path/hash, batch/audit hash binding, drift check, both dedupe precheck counts, exact Wang Huohuo 29-row/category DB proof, exception count, build results, and screenshot paths. It must not contain database credentials, raw import text, JDBC URLs, or access URLs.

```powershell
git add kaipaile-server/src/main/java/com/kaipai/service/actor/impl/ActorProfileServiceImpl.java kaipaile-server/src/main/java/com/kaipai/service/ai/impl/AiResumeServiceImpl.java kaipaile-server/src/main/java/com/kaipai/service/ai/impl/AiResumeApplyRecorderImpl.java .sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/execution.md .sce/specs/spec-code-mapping.md docs/product-design.md
git commit -m "chore(profile-library): verify migration and stop legacy writes"
```

## Verification Coverage

- R110-R117: Task 1 snapshot, strict parsing, mapping, private copy, per-user transaction, exception isolation, and compensation.
- R118-R120: Tasks 2-5 resolver and consumer switches, with legacy fields retained only as read-only compatibility inputs.
- R121: Task 6 records physical deletion as a separate future retirement audit.
- R122-R123: Task 1 and Task 6 inspect, dry-run, repeatability, verify, rollback, and Wang Huohuo restore.
- R146-R147: asset privacy, ownership, reference protection, counts, duplicate runs, and rollback tests.
- R148-R151: backend tests/package, mini-program type-check/build/audits, four-layer source/build/devtools evidence, and staged release gates.

Do not delete old columns, old DTOs, old components, or old routes in this plan. The next retirement Spec begins only after every resolver consumer is proven to use the new facts.
