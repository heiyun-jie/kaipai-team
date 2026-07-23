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
V20260723_001__career_profile_domain_foundation.sql
V20260723_002__actor_media_asset_relations.sql
V20260723_003__share_card_favorite.sql
V20260723_004__ai_profile_import_governance.sql
V20260723_005__profile_library_presentation_and_ai_asset_refs.sql
```

The final migration creates batch, mapping, and exception audit tables plus `actor_ai_profile_card_task.source_asset_id` and `generated_asset_id`. It does not drop legacy URL fields or add a legacy URL fallback to public resolution.

## File Map

- Create: `kaipaile-server/src/main/resources/db/migration/V20260723_005__profile_library_presentation_and_ai_asset_refs.sql`
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
- Create: `kaipaile-server/src/main/resources/db/migration/V20260723_005__profile_library_presentation_and_ai_asset_refs.sql`
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
```

- [ ] **Step 2: Run the red tests**

Run:

```powershell
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -Dtest=ProfileLibraryMigrationServiceTest test
```

Expected: FAIL because migration batching, legacy mapping, exception reporting, and rollback compensation do not exist.

- [ ] **Step 3: Implement fixed migration rules**

For each user, strictly parse `extended_field`; malformed JSON writes a hashed exception and leaves the user unmodified. For valid data, copy objects to private storage, then run one database transaction that creates assets, pages, explicit relations, mapping rows, `avatar_asset_id`, and `current_resume_asset_id`. If the database transaction fails, delete objects copied in that attempt and record a hashed cleanup error if deletion fails.

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

The runner accepts only `inspect`, `dry-run`, `apply`, `verify`, and `rollback`. It reads database/COS credentials only from environment variables, and it outputs counts, identifiers, hashes, and stable errors but never raw URLs, source text, credentials, or tokens.

- [ ] **Step 4: Run green tests**

Run:

```powershell
mvn -q -Dtest=ProfileLibraryMigrationServiceTest test
```

Expected: PASS for strict parsing, idempotent mapping, per-user transaction, and compensation boundaries.

- [ ] **Step 5: Commit**

```powershell
git add kaipaile-server/src/main/resources/db/migration/V20260723_005__profile_library_presentation_and_ai_asset_refs.sql kaipaile-server/src/main/java/com/kaipai/service/actor/migration kaipaile-server/src/test/java/com/kaipai/ProfileLibraryMigrationRunner.java kaipaile-server/src/test/java/com/kaipai/module/server/actor/migration/ProfileLibraryMigrationServiceTest.java
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

- [ ] **Step 3: Run controlled inspect, dry-run, apply, verify, and restore**

Only after explicit environment migration authorization, run:

```powershell
$batch = "00-199-" + (Get-Date -Format "yyyyMMddHHmmss")
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.ProfileLibraryMigrationRunner -Dexec.args="inspect --batch=$batch" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.ProfileLibraryMigrationRunner -Dexec.args="dry-run --batch=$batch" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.ProfileLibraryMigrationRunner -Dexec.args="apply --batch=$batch" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
mvn -q -Dexec.classpathScope=test -Dexec.mainClass=com.kaipai.ProfileLibraryMigrationRunner -Dexec.args="verify --batch=$batch" org.codehaus.mojo:exec-maven-plugin:3.6.1:java
```

`verify` must compare counts, owners, relation references, active public behavior, duplicate-run totals, rollback results, and the restorable Wang Huohuo snapshot. It must never print raw source text, credentials, permanent URLs, or signed URLs.

- [ ] **Step 4: Run the final engineering gate**

Run:

```powershell
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -Dtest=ProfileLibraryMigrationServiceTest,ProfilePresentationResolverTest,ShareCardContentSelectionServiceImplTest,ActorProfileCompletionCalculatorTest,AiProfileCardServiceImplTest,AiProfileCardPromptAgentTest test
mvn -q clean package
cd ..\kaipai-frontend
npm run type-check
npm run build:mp-weixin
npm run audit:steering
npm run audit:mp-package
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

- [ ] **Step 5: Record and commit evidence**

`execution.md` records migration file names, batch ID, inspect/dry-run/apply/verify status, exception count, rollback rehearsal, Wang Huohuo restoration, build results, and screenshot paths. It must not contain database credentials, raw import text, or access URLs.

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
