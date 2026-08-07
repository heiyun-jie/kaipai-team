# AI Profile Card Tencent OCR ImageNoText Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Treat Tencent OCR `FailedOperation.ImageNoText` as a successful no-text quality result so AI profile-card tasks continue to share-card persistence without another image generation.

**Architecture:** Keep HTTP transport and the existing quality inspection contract, but move Tencent business-response interpretation into one focused method. The method maps only the exact no-text code to `accept()`, preserves all other errors, and reuses existing blocked-text extraction for successful OCR responses.

**Tech Stack:** Java 17, Spring Boot 3.2.3, Jackson, JUnit 5, Spring `ReflectionTestUtils`, Maven, standard backend-only release helper.

---

### Task 1: Record The SCE Contract

**Files:**
- Create: `.sce/specs/00-198-current-phase-ai-profile-card-tencent-ocr-no-text-quality-gate-fix/requirements.md`
- Create: `.sce/specs/00-198-current-phase-ai-profile-card-tencent-ocr-no-text-quality-gate-fix/design.md`
- Create: `.sce/specs/00-198-current-phase-ai-profile-card-tencent-ocr-no-text-quality-gate-fix/tasks.md`
- Create: `.sce/specs/00-198-current-phase-ai-profile-card-tencent-ocr-no-text-quality-gate-fix/execution.md`
- Modify: `.sce/specs/README.md`
- Modify: `.sce/specs/spec-code-mapping.md`

- [x] **Step 1: Add the exact error-code contract**

Document `FailedOperation.ImageNoText -> accepted=true, retryable=false`, with other errors fail-closed.

- [x] **Step 2: Record production evidence and non-goals**

Record task `aipf_a11b4df10cf349f7a9104d245344e4de`, no historical mutation, no OCR disable, and no orphan COS cleanup.

- [x] **Step 3: Update indexes**

Add 00-198 to the quick index, full table, and code mapping without overwriting current dirty-worktree changes.

### Task 2: Write And Verify The Failing Inspector Test

**Files:**
- Test: `kaipaile-server/src/test/java/com/kaipai/module/server/ai/profilecard/TencentOcrAiProfileCardImageQualityInspectorTest.java`

- [x] **Step 1: Add the failing no-text response test**

```java
@Test
void imageNoTextResponseShouldBeAccepted() throws Exception {
    TencentOcrAiProfileCardImageQualityInspector inspector = new TencentOcrAiProfileCardImageQualityInspector(
            mock(AiImageProviderConfigService.class),
            new ObjectMapper());
    JsonNode root = new ObjectMapper().readTree("""
            {"Response":{"Error":{"Code":"FailedOperation.ImageNoText","Message":"照片中未检测到文本"}}}
            """);

    AiProfileCardImageQualityInspection inspection = ReflectionTestUtils.invokeMethod(
            inspector,
            "inspectTencentResponse",
            root);

    assertTrue(inspection.accepted());
    assertFalse(inspection.retryable());
}
```

- [x] **Step 2: Add an adjacent-error protection test**

```java
@Test
void otherTencentApiErrorShouldRemainFailure() throws Exception {
    TencentOcrAiProfileCardImageQualityInspector inspector = new TencentOcrAiProfileCardImageQualityInspector(
            mock(AiImageProviderConfigService.class),
            new ObjectMapper());
    JsonNode root = new ObjectMapper().readTree("""
            {"Response":{"Error":{"Code":"FailedOperation.ImageDecodeFailed","Message":"图片解码失败"}}}
            """);

    BizException error = assertThrows(BizException.class, () -> ReflectionTestUtils.invokeMethod(
            inspector,
            "inspectTencentResponse",
            root));

    assertTrue(error.getMessage().contains("ImageDecodeFailed"));
}
```

- [x] **Step 3: Run the red test**

Run:

```powershell
cd D:\XM\kaipai-team\kaipaile-server
mvn -q -Dtest=TencentOcrAiProfileCardImageQualityInspectorTest test
```

Expected: FAIL because `inspectTencentResponse(JsonNode)` does not exist.

### Task 3: Implement The Exact Semantic Mapping

**Files:**
- Modify: `kaipaile-server/src/main/java/com/kaipai/service/ai/profilecard/TencentOcrAiProfileCardImageQualityInspector.java`

- [x] **Step 1: Route parsed JSON through a response interpreter**

Replace the inline snippet extraction in `inspectCover(...)` with:

```java
JsonNode root = callTencent(client, secretId, secretKey, runtime, imageUrl.trim());
return inspectTencentResponse(root);
```

- [x] **Step 2: Move business-error handling into the interpreter**

```java
private AiProfileCardImageQualityInspection inspectTencentResponse(JsonNode root) {
    JsonNode error = root == null ? null : root.at("/Response/Error");
    if (error != null && !error.isMissingNode()) {
        String code = error.path("Code").asText("").trim();
        if ("FailedOperation.ImageNoText".equals(code)) {
            return AiProfileCardImageQualityInspection.accept();
        }
        throw new BizException("腾讯 OCR API 错误：" + truncate(error.toString()));
    }
    List<String> snippets = extractBlockedSnippets(root);
    if (!snippets.isEmpty()) {
        return AiProfileCardImageQualityInspection.rejected("封面成图检测到文字：" + String.join(" | ", snippets));
    }
    return AiProfileCardImageQualityInspection.accept();
}
```

- [x] **Step 3: Keep `callTencent(...)` transport-only**

Remove its existing `/Response/Error` throw after JSON parsing and return the parsed root unchanged.

- [x] **Step 4: Run the green test**

```powershell
mvn -q -Dtest=TencentOcrAiProfileCardImageQualityInspectorTest test
```

Expected: PASS with all inspector tests green.

### Task 4: Run Related Verification

**Files:**
- Verify: `kaipaile-server/src/test/java/com/kaipai/module/server/ai/service/impl/AiProfileCardServiceImplTest.java`

- [x] **Step 1: Run inspector and service tests**

```powershell
mvn -q -Dtest=TencentOcrAiProfileCardImageQualityInspectorTest,AiProfileCardServiceImplTest test
```

Expected: PASS, zero failures and errors.

- [x] **Step 2: Build the release JAR**

```powershell
mvn -q -DskipTests clean package
```

Expected: exit code 0 and `target/kaipai-backend-1.0.0-SNAPSHOT.jar` exists.

- [x] **Step 3: Review the diff**

Confirm only the inspector, inspector tests, 00-198 docs, indexes, plan, and execution records changed for this fix. Confirm no credential values or broad `FailedOperation` matching were added.

### Task 5: Publish Backend-Only

**Files:**
- Release: `.sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py`
- Record: `.sce/runbooks/backend-admin-release/records/<generated-release-id>.md`

- [x] **Step 1: Verify release prerequisites before deployment**

Confirm SSH key/helper health, `KAIPAI_ADMIN_SMOKE_PASSWORD` is set, and the command explicitly uses `--mysql-database kaipai_prod`.

Approved one-time deviation for this batch: when the password environment variable is unavailable, reuse the standard script's precheck/build/upload/helper functions, replace only the password login probe with an authenticated Chrome UI smoke, and write a manual deviation record. Never inspect browser credentials or claim that `POST /api/admin/auth/login` ran.

- [x] **Step 2: Run the approved browser-smoke deviation release**

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py --label tencent-ocr-image-no-text-fix --operator codex --host 101.43.57.62 --public-base-url https://api.kplyyk.com --mysql-database kaipai_prod --overlay-path src/main/java/com/kaipai/service/ai/profilecard/TencentOcrAiProfileCardImageQualityInspector.java --overlay-path src/test/java/com/kaipai/module/server/ai/profilecard/TencentOcrAiProfileCardImageQualityInspectorTest.java
```

Expected: release helper, internal smoke, public smoke, and release record all pass.

- [x] **Step 3: Capture post-release diagnostics**

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-backend-runtime-logs.py --label tencent-ocr-image-no-text-post-release --host 101.43.57.62 --container kaipai-backend --since 15m --tail 800
```

Expected: container running with the new JAR and no startup error.

### Task 6: Verify A New User Task

**Files:**
- Modify: `.sce/specs/00-198-current-phase-ai-profile-card-tencent-ocr-no-text-quality-gate-fix/tasks.md`
- Modify: `.sce/specs/00-198-current-phase-ai-profile-card-tencent-ocr-no-text-quality-gate-fix/execution.md`
- Modify: `.sce/specs/spec-code-mapping.md`

- [x] **Step 1: Have `userId=4` create a new AI share-image task**

Do not retry or rewrite the historical failed task.

- [x] **Step 2: Query the new task and associations**

Verify `status=success`, `provider_code=tencent-hunyuan`, `model_code=hunyuan-image-3.0`, and non-empty `generated_image_url/share_card_id`; verify the associated share-card and actor-card configuration rows exist.

- [x] **Step 3: Verify the image URL**

Run a read-only HTTP HEAD/GET and require a successful image response.

- [x] **Step 4: Complete SCE records**

Record release ID, JAR SHA, test counts, task ID, share-card ID, image availability, and any remaining orphan-image cleanup debt without storing secrets.
