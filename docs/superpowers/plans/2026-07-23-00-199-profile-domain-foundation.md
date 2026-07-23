# 00-199 Profile Domain Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the durable profile, work-library, private-media, and real-favorite backend foundation while preventing old aggregate profile saves from deleting works or media.

**Architecture:** Retain `actor_profile` as the core profile and extend `actor_experience` in place as the unique work table. New write paths use typed DTOs, explicit relationship tables, optimistic versions, and private object references; legacy `PUT /api/actor/profile` remains a guarded scalar-only compatibility path.

**Tech Stack:** Spring Boot 3.2.3, Java 17, MyBatis-Plus, MySQL 8, JUnit 5, Mockito, Spring MVC tests, Testcontainers MySQL for generated-column and index integration proof.

---

## Preconditions And File Map

This is Plan 1. It implements R10, R21-R59, R100-R109, R124-R137, and backend portions of R146-R148. Do not call DeepSeek, backfill production records, or switch public readers in this plan.

- Create: `kaipaile-server/src/main/resources/db/migration/V20260723_001__career_profile_domain_foundation.sql`
- Create: `kaipaile-server/src/main/resources/db/migration/V20260723_002__actor_media_asset_relations.sql`
- Create: `kaipaile-server/src/main/resources/db/migration/V20260723_003__share_card_favorite.sql`
- Modify: `kaipaile-server/pom.xml`
- Modify: `kaipaile-server/src/main/java/com/kaipai/model/actor/entity/ActorProfile.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/model/actor/entity/ActorExperience.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/model/actor/dto/ActorProfileSaveDTO.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/controller/api/actor/ActorProfileController.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/actor/ActorProfileService.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/actor/impl/ActorProfileServiceImpl.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/integration/storage/CosUtil.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/common/service/PdfUploadService.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/controller/api/card/CardController.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/actor/entity/ActorProfileRepresentativeWork.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/actor/entity/ActorMediaAsset.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/actor/entity/ActorMediaAssetPage.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/actor/entity/ActorProfileAsset.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/actor/entity/ActorWorkAsset.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/card/entity/ShareCardWork.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/card/entity/ShareCardAsset.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/card/entity/ShareCardFavorite.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/model/actor/dto/ProfileDomainErrorCode.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/ActorProfileWriteService.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/ActorWorkService.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/ActorMediaAssetService.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/card/ShareCardFavoriteService.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/controller/api/actor/ActorWorkController.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/controller/api/actor/ActorMediaAssetController.java`
- Create: `kaipaile-server/src/test/java/com/kaipai/migration/CareerProfileSchemaMigrationTest.java`
- Create: `kaipaile-server/src/test/java/com/kaipai/service/actor/impl/ActorProfileServiceImplTest.java`
- Create: `kaipaile-server/src/test/java/com/kaipai/service/actor/impl/ActorProfileWriteServiceImplTest.java`
- Create: `kaipaile-server/src/test/java/com/kaipai/service/actor/impl/ActorWorkServiceImplTest.java`
- Create: `kaipaile-server/src/test/java/com/kaipai/service/actor/impl/ActorMediaAssetServiceImplTest.java`
- Create: `kaipaile-server/src/test/java/com/kaipai/service/card/impl/ShareCardFavoriteServiceImplTest.java`

The single shared `ProfileDomainErrorCode` owns every 00-199 code from `46001` to `46017`. This plan implements the domain cases it needs; Plan 2 completes its import-specific map. Do not create a second error-code enum.

## Task 1: Additive DDL With Executable Schema Proof

**Files:**
- Modify: `kaipaile-server/pom.xml`
- Create: the three Plan 1 migration files
- Test: `kaipaile-server/src/test/java/com/kaipai/migration/CareerProfileSchemaMigrationTest.java`

- [ ] **Step 1: Write the failing schema test**

```java
@Test
void schemaContainsProfileWorkAssetAndFavoriteFoundation() throws Exception {
    try (Connection connection = MigrationTestDatabase.apply(
            "V20260723_001__career_profile_domain_foundation.sql",
            "V20260723_002__actor_media_asset_relations.sql",
            "V20260723_003__share_card_favorite.sql")) {
        assertColumn(connection, "actor_profile", "avatar_asset_id");
        assertColumn(connection, "actor_profile", "work_library_version");
        assertColumn(connection, "actor_experience", "dedupe_key");
        assertTable(connection, "actor_media_asset");
        assertTable(connection, "actor_profile_representative_work");
        assertTable(connection, "share_card_favorite");
        assertIndex(connection, "share_card_favorite", "uk_share_card_favorite_user_active_card");
    }
}
```

- [ ] **Step 2: Run the red test**

Run:

```powershell
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -Dtest=CareerProfileSchemaMigrationTest test
```

Expected: FAIL because the migration files and isolated migration test database do not exist.

- [ ] **Step 3: Add the three incremental migrations**

`V20260723_001` adds profile career columns, partial birthday fields, work-library version, work metadata, and `actor_profile_representative_work`. `V20260723_002` creates the asset/page and typed profile/work/share relation tables. `V20260723_003` creates `share_card_favorite` with generated `active_share_card_id` and unique `(user_id, active_share_card_id)`.

Do not add the active work dedupe unique index until the migration inspection confirms existing active rows have normalized keys with no duplicates. The later gated migration adds the generated active key and its unique index.

- [ ] **Step 4: Run the green test**

Run:

```powershell
mvn -q -Dtest=CareerProfileSchemaMigrationTest test
```

Expected: PASS after all three SQL files apply in order.

- [ ] **Step 5: Commit**

```powershell
git add kaipaile-server/pom.xml kaipaile-server/src/main/resources/db/migration/V20260723_001__career_profile_domain_foundation.sql kaipaile-server/src/main/resources/db/migration/V20260723_002__actor_media_asset_relations.sql kaipaile-server/src/main/resources/db/migration/V20260723_003__share_card_favorite.sql kaipaile-server/src/test/java/com/kaipai/migration/CareerProfileSchemaMigrationTest.java
git commit -m "feat(profile): add career profile domain schema"
```

## Task 2: Guard Legacy Aggregate Profile PUT

**Files:**
- Modify: `kaipaile-server/src/main/java/com/kaipai/model/actor/dto/ActorProfileSaveDTO.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/actor/ActorProfileService.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/actor/impl/ActorProfileServiceImpl.java`
- Create: `kaipaile-server/src/main/java/com/kaipai/service/actor/support/LegacyProfileWriteGuard.java`
- Test: `kaipaile-server/src/test/java/com/kaipai/service/actor/impl/ActorProfileServiceImplTest.java`

- [ ] **Step 1: Write legacy PUT red tests**

```java
@Test
void emptyLegacyCollectionsDoNotDeleteExistingWorks() {
    ActorProfileSaveDTO request = legacyScalarRequest();
    request.setWorkExperiences(List.of());

    service.saveProfile(USER_ID, request);

    verify(actorExperienceMapper, never()).delete(any());
    verify(actorExperienceMapper, never()).deleteBatchIds(anyCollection());
}

@Test
void nonEmptyLegacyCollectionsAreRejectedBeforeAnyWrite() {
    ActorProfileSaveDTO request = legacyScalarRequest();
    request.setWorkExperiences(List.of(new ActorProfileSaveDTO.WorkExperienceDTO()));

    BizException error = assertThrows(BizException.class, () -> service.saveProfile(USER_ID, request));

    assertEquals(46017, error.getCode());
    verify(actorExperienceMapper, never()).insert(any());
    verify(actorExperienceMapper, never()).updateById(any());
}
```

- [ ] **Step 2: Run the red test**

Run:

```powershell
mvn -q -Dtest=ActorProfileServiceImplTest test
```

Expected: FAIL because `saveProfile` still invokes `syncExperiences` and writes legacy media fields.

- [ ] **Step 3: Implement the guard**

```java
public void assertCompatible(ActorProfileSaveDTO request) {
    if (hasNonEmptyWorks(request) || hasLegacyMedia(request)) {
        throw ProfileDomainErrorCode.PROFILE_LEGACY_COLLECTION_WRITE_RETIRED.toException();
    }
}
```

Call it before mutation. Compatible legacy scalar requests may update only explicitly retained scalar fields; do not write photo JSON, video URL, PDF JSON, or execute `syncExperiences`.

- [ ] **Step 4: Run the green test and commit**

Run:

```powershell
mvn -q -Dtest=ActorProfileServiceImplTest test
```

Expected: PASS and no aggregate request can erase or replace works/media.

```powershell
git add kaipaile-server/src/main/java/com/kaipai/model/actor/dto/ActorProfileSaveDTO.java kaipaile-server/src/main/java/com/kaipai/model/actor/dto/ProfileDomainErrorCode.java kaipaile-server/src/main/java/com/kaipai/service/actor/ActorProfileService.java kaipaile-server/src/main/java/com/kaipai/service/actor/impl/ActorProfileServiceImpl.java kaipaile-server/src/main/java/com/kaipai/service/actor/support/LegacyProfileWriteGuard.java kaipaile-server/src/test/java/com/kaipai/service/actor/impl/ActorProfileServiceImplTest.java
git commit -m "fix(profile): stop legacy collection replacement"
```

## Task 3: Add Versioned Mine Profile API

**Files:**
- Create: `ActorProfileMineUpdateDTO`, `ActorProfileCoreUpdateDTO`, `ActorProfileCareerUpdateDTO`, `ActorProfileRespDTO`
- Create: `ActorProfileWriteService.java`, `ActorProfileWriteServiceImpl.java`
- Modify: `ActorProfile.java`, `ActorProfileController.java`
- Test: `ActorProfileWriteServiceImplTest.java`

- [ ] **Step 1: Write mine-save red tests**

```java
@Test
void mineSaveRejectsStaleProfileVersion() {
    BizException error = assertThrows(BizException.class,
        () -> service.saveMine(USER_ID, requestWithVersion(2)));
    assertEquals(ProfileDomainErrorCode.PROFILE_VERSION_CONFLICT.code(), error.getCode());
}

@Test
void mineSaveWritesCoreCareerIntroAndAvatarOnly() {
    ActorProfileRespDTO result = service.saveMine(USER_ID, validRequest());
    assertEquals("王火火", result.getPublicName());
    verify(actorExperienceMapper, never()).delete(any());
}
```

- [ ] **Step 2: Run the red test**

Run:

```powershell
mvn -q -Dtest=ActorProfileWriteServiceImplTest test
```

Expected: FAIL because the dedicated DTOs and service do not exist.

- [ ] **Step 3: Implement the mine contract**

```http
GET /api/actor/profile/mine
PUT /api/actor/profile/mine
```

`ActorProfileMineUpdateDTO` contains `expectedProfileVersion`, `avatarAssetId`, `core`, `career`, and `intro`. Validate avatar ownership, photo type, and ready status; update only new core/career/intro fields in one transaction and return `profileVersion` plus `workLibraryVersion`.

- [ ] **Step 4: Run green test and commit**

Run:

```powershell
mvn -q -Dtest=ActorProfileWriteServiceImplTest test
```

Expected: PASS with no work/media mutation.

```powershell
git add kaipaile-server/src/main/java/com/kaipai/model/actor kaipaile-server/src/main/java/com/kaipai/controller/api/actor/ActorProfileController.java kaipaile-server/src/main/java/com/kaipai/service/actor/ActorProfileWriteService.java kaipaile-server/src/main/java/com/kaipai/service/actor/impl/ActorProfileWriteServiceImpl.java kaipaile-server/src/test/java/com/kaipai/service/actor/impl/ActorProfileWriteServiceImplTest.java
git commit -m "feat(profile): add versioned mine profile API"
```

## Task 4: Add Paged Work Library And Representatives

**Files:**
- Modify: `kaipaile-server/src/main/java/com/kaipai/model/actor/entity/ActorExperience.java`
- Create: `ActorWorkQueryDTO`, `ActorWorkSaveDTO`, `ActorWorkRespDTO`, `ActorRepresentativeWorksUpdateDTO`
- Create: `ActorWorkService.java`, `ActorWorkServiceImpl.java`, `ActorWorkDeduplicationSupport.java`, `ActorWorkController.java`
- Test: `kaipaile-server/src/test/java/com/kaipai/service/actor/impl/ActorWorkServiceImplTest.java`

- [ ] **Step 1: Write work-library red tests**

```java
@Test
void listDefaultsToTenButRetainsAllTwentyNineWorks() {
    seedWorks(USER_ID, 29);
    PageResult<ActorWorkRespDTO> page = service.listWorks(USER_ID, new ActorWorkQueryDTO());
    assertEquals(10, page.getList().size());
    assertEquals(29L, page.getTotal());
}

@Test
void representativeListRejectsMoreThanSixWorks() {
    ActorRepresentativeWorksUpdateDTO request = ids(1L, 2L, 3L, 4L, 5L, 6L, 7L);
    BizException error = assertThrows(BizException.class, () -> service.replaceRepresentativeWorks(USER_ID, request));
    assertEquals(ProfileDomainErrorCode.PROFILE_REPRESENTATIVE_WORK_LIMIT.code(), error.getCode());
}

@Test
void duplicateProjectAndRoleForSameUserIsRejected() {
    service.createWork(USER_ID, work("绝不回头，白爷宠她成瘾", "程雪"));
    BizException error = assertThrows(BizException.class,
        () -> service.createWork(USER_ID, work("绝不回头，白爷宠她成瘾", "程雪")));
    assertEquals(46015, error.getCode());
}
```

- [ ] **Step 2: Run the red tests**

Run:

```powershell
mvn -q -Dtest=ActorWorkServiceImplTest test
```

Expected: FAIL because the work library service and DTOs do not exist.

- [ ] **Step 3: Implement work APIs**

```http
GET    /api/actor/works?page=1&size=10&keyword=&publishStatus=&workTypeCode=
POST   /api/actor/works
GET    /api/actor/works/{experienceId}
PUT    /api/actor/works/{experienceId}
DELETE /api/actor/works/{experienceId}
PUT    /api/actor/works/representatives
PUT    /api/actor/works/{experienceId}/assets
```

Normalize project/role values before deriving a SHA-256 dedupe key. Increment `work_library_version` atomically for each work create/update/delete, representative reorder, and asset binding. Preserve `experience_id`; do not clone the work table.

- [ ] **Step 4: Run green tests and commit**

Run:

```powershell
mvn -q -Dtest=ActorWorkServiceImplTest test
```

Expected: PASS for pagination, ownership, dedupe, representative limit, and version increments.

```powershell
git add kaipaile-server/src/main/java/com/kaipai/model/actor/entity/ActorExperience.java kaipaile-server/src/main/java/com/kaipai/model/actor/dto kaipaile-server/src/main/java/com/kaipai/service/actor/ActorWorkService.java kaipaile-server/src/main/java/com/kaipai/service/actor/impl/ActorWorkServiceImpl.java kaipaile-server/src/main/java/com/kaipai/service/actor/support/ActorWorkDeduplicationSupport.java kaipaile-server/src/main/java/com/kaipai/controller/api/actor/ActorWorkController.java kaipaile-server/src/test/java/com/kaipai/service/actor/impl/ActorWorkServiceImplTest.java
git commit -m "feat(profile): add actor work library"
```

## Task 5: Add Private Media Asset Domain

**Files:**
- Modify: `kaipaile-server/src/main/java/com/kaipai/integration/storage/CosUtil.java`
- Modify: `kaipaile-server/src/main/java/com/kaipai/common/service/PdfUploadService.java`
- Create: asset/page/relation entities, mappers, DTOs, `ActorMediaAssetService`, `PrivateActorMediaStorage`, `ActorMediaAssetReferenceInspector`, and `ActorMediaAssetController`
- Test: `kaipaile-server/src/test/java/com/kaipai/service/actor/impl/ActorMediaAssetServiceImplTest.java`

- [ ] **Step 1: Write asset red tests**

```java
@Test
void assetStoresObjectIdentityButNotPermanentUrl() {
    ActorAssetRespDTO result = service.createFromUploadedObject(USER_ID, uploadedPhoto());
    assertEquals("ready", result.getProcessStatus());
    assertNotNull(result.getObjectKey());
    assertNull(result.getAccessUrl());
}

@Test
void failedPdfCannotBecomeCurrentResume() {
    BizException error = assertThrows(BizException.class, () -> service.setCurrentResume(USER_ID, FAILED_PDF_ID));
    assertEquals(46013, error.getCode());
}

@Test
void referencedAssetCannotBeDeleted() {
    stubAssetUsage(READY_PHOTO_ID, List.of("avatar"));
    BizException error = assertThrows(BizException.class, () -> service.delete(USER_ID, READY_PHOTO_ID));
    assertEquals(46014, error.getCode());
}
```

- [ ] **Step 2: Run the red tests**

Run:

```powershell
mvn -q -Dtest=ActorMediaAssetServiceImplTest test
```

Expected: FAIL because private asset service and relation inspection do not exist.

- [ ] **Step 3: Implement assets and owner access**

```http
GET    /api/actor/assets
POST   /api/actor/assets
GET    /api/actor/assets/{assetId}
PUT    /api/actor/assets/{assetId}
DELETE /api/actor/assets/{assetId}
PUT    /api/actor/assets/current-resume
POST   /api/actor/assets/{assetId}/access-url
```

`PrivateActorMediaStorage` persists provider, bucket code, object key, and thumbnail key. It never persists a signed or public URL. PDF conversion records ordered page rows, keeps a failed state on error, and only permits ready PDF assets as current resume.

- [ ] **Step 4: Run green tests and commit**

Run:

```powershell
mvn -q -Dtest=ActorMediaAssetServiceImplTest test
```

Expected: PASS for ready gating, owner-only short URL, PDF state, and reference deletion protection.

```powershell
git add kaipaile-server/src/main/java/com/kaipai/integration/storage/CosUtil.java kaipaile-server/src/main/java/com/kaipai/common/service/PdfUploadService.java kaipaile-server/src/main/java/com/kaipai/model/actor kaipaile-server/src/main/java/com/kaipai/service/actor/ActorMediaAssetService.java kaipaile-server/src/main/java/com/kaipai/service/actor/impl/ActorMediaAssetServiceImpl.java kaipaile-server/src/main/java/com/kaipai/service/actor/support/PrivateActorMediaStorage.java kaipaile-server/src/main/java/com/kaipai/service/actor/support/ActorMediaAssetReferenceInspector.java kaipaile-server/src/main/java/com/kaipai/controller/api/actor/ActorMediaAssetController.java kaipaile-server/src/test/java/com/kaipai/service/actor/impl/ActorMediaAssetServiceImplTest.java
git commit -m "feat(profile): add private actor media assets"
```

## Task 6: Implement Real Share-Card Favorites

**Files:**
- Modify: `kaipaile-server/src/main/java/com/kaipai/controller/api/card/CardController.java`
- Create: `ShareCardFavorite.java`, mapper, DTOs, service, implementation
- Test: `kaipaile-server/src/test/java/com/kaipai/service/card/impl/ShareCardFavoriteServiceImplTest.java`

- [ ] **Step 1: Write favorite red tests**

```java
@Test
void favoriteAddAndRemoveAreIdempotentAndOwnCardIsRejected() {
    assertTrue(service.addFavorite(VIEWER_ID, CARD_ID).isFavorited());
    assertTrue(service.addFavorite(VIEWER_ID, CARD_ID).isFavorited());
    assertFalse(service.removeFavorite(VIEWER_ID, CARD_ID).isFavorited());
    assertFalse(service.removeFavorite(VIEWER_ID, CARD_ID).isFavorited());
    assertThrows(BizException.class, () -> service.addFavorite(OWNER_ID, CARD_ID));
}
```

- [ ] **Step 2: Run the red test**

Run:

```powershell
mvn -q -Dtest=ShareCardFavoriteServiceImplTest test
```

Expected: FAIL because no favorite service exists.

- [ ] **Step 3: Implement favorite API**

```http
GET    /api/card/favorites?page=1&size=10
PUT    /api/card/{shareCardId}/favorite
DELETE /api/card/{shareCardId}/favorite
```

List only active cards with real favorite rows. Add rejects own cards; remove returns `favorited=false` when no active relation exists.

- [ ] **Step 4: Run green test and commit**

Run:

```powershell
mvn -q -Dtest=ShareCardFavoriteServiceImplTest test
```

Expected: PASS for idempotency, ownership, and inactive-card filtering.

```powershell
git add kaipaile-server/src/main/java/com/kaipai/controller/api/card/CardController.java kaipaile-server/src/main/java/com/kaipai/model/card kaipaile-server/src/main/java/com/kaipai/mapper/card kaipaile-server/src/main/java/com/kaipai/service/card/ShareCardFavoriteService.java kaipaile-server/src/main/java/com/kaipai/service/card/impl/ShareCardFavoriteServiceImpl.java kaipaile-server/src/test/java/com/kaipai/service/card/impl/ShareCardFavoriteServiceImplTest.java
git commit -m "feat(card): persist share card favorites"
```

## Task 7: Add Inspect and Fixture Gates

**Files:**
- Create: `kaipaile-server/src/test/java/com/kaipai/CareerProfileMigrationRunner.java`
- Create: `kaipaile-server/src/test/java/com/kaipai/migration/CareerProfileMigrationRunnerTest.java`
- Create: `kaipaile-server/src/test/resources/profile-migration/wang-huohuo-baseline.json`

- [ ] **Step 1: Write runner red tests**

```java
@Test
void inspectReportsMalformedExtendedFieldRows() {
    seedProfileWithMalformedExtendedField(USER_ID);
    assertTrue(runner.inspect().getMalformedExtendedFieldProfileIds().contains(USER_ID));
}

@Test
void dryRunDoesNotCreateAssetsOrRelations() {
    long before = count("actor_media_asset");
    runner.dryRun(USER_ID);
    assertEquals(before, count("actor_media_asset"));
}
```

- [ ] **Step 2: Run red tests, implement modes, and run green tests**

Run:

```powershell
mvn -q -Dtest=CareerProfileMigrationRunnerTest test
```

Expected before implementation: FAIL. Implement `inspect`, `dry-run`, `verify`, and `restore-fixture` modes; do not print raw URLs or clipboard source. Rerun the same command and expect PASS.

- [ ] **Step 3: Commit and run Plan 1 gate**

```powershell
git add kaipaile-server/src/test/java/com/kaipai/CareerProfileMigrationRunner.java kaipaile-server/src/test/java/com/kaipai/migration/CareerProfileMigrationRunnerTest.java kaipaile-server/src/test/resources/profile-migration/wang-huohuo-baseline.json
git commit -m "test(profile): add migration inspection fixture"
mvn -q -Dtest=CareerProfileSchemaMigrationTest,ActorProfileServiceImplTest,ActorProfileWriteServiceImplTest,ActorWorkServiceImplTest,ActorMediaAssetServiceImplTest,ShareCardFavoriteServiceImplTest,CareerProfileMigrationRunnerTest test
mvn -q clean package
```

Expected: all targeted tests and `clean package` pass. Plan 2 may now consume profile/work versions, asset ownership checks, and the shared error code enum.
