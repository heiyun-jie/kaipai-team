# 00-200 Runtime Phase B Cutover Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cut ordinary `full_profile` and `works_only` recognition over to released database Prompt versions, remove production Java Prompt fallback, persist sanitized call lineage, and complete deployment, smoke, rollback, and SCE evidence.

**Architecture:** `ProfileImportServiceImpl` resolves a fresh released Prompt runtime after model configuration and before quota consumption, passes it into the extractor for both initial and repair calls, validates the scene contract, and writes the same lineage to success/failure audits. Missing or damaged Prompt state fails closed as `PROFILE_IMPORT_UNAVAILABLE`; there is no cache or fallback. A target-state preflight blocks deployment unless both v1 releases and immutable bindings exist, while post-deploy smoke and MySQL evidence prove each scene uses active lineage.

**Tech Stack:** Java 17, Spring Boot 3.2.3, MyBatis-Plus, MySQL 8.0.36, Testcontainers, JUnit 5, Mockito, Maven, PowerShell API smoke, standard backend release and diagnostics scripts.

---

## Preconditions And Irreversible Boundary

Do not execute this plan until Plan 2 has recorded all of these target facts:

```text
TEMPLATE_COUNT=2
OPEN_DRAFT_COUNT=0
ACTIVE_RELEASED_COUNT=2
ACTIVE_V1_COUNT=2
CROSS_POINTER_COUNT=0
RELEASE_BINDING_INCOMPLETE_COUNT=0
ACTIVE_PUBLISH_BINDING_MISMATCH_COUNT=0
ACTIVE_INITIAL_RELEASE_AUDIT_COUNT=2
PROMPT_PUBLISH_OPERATION_LOG_COUNT=2
PROMPT_OPERATION_LOG_PAYLOAD_VIOLATION_COUNT=0
```

The count block is necessary but not sufficient. Before Task 1 starts, all of these evidence gates must also exist:

- `requirements.md`, `design.md`, and `tasks.md` record the user's written-Spec confirmation and the three-plan execution order.
- Every required Plan 1/Plan 2 backend unit, MySQL 8.0.36, Maven package, admin type-check/build, development E2E, and sanitized-dist E2E gate has a fresh exit-0 record.
- V001/V002 are present in `kaipai_prod.schema_release_history`; Phase A backend/admin release records identify artifact SHAs and prove the production domains use `kaipai_prod`.
- Both scenes have real `test` and normal `publish` audit IDs, operator IDs, `testedAt`, and complete binding hashes recorded without bodies or secrets.
- Immediately before the Phase B SQL preflight, an authorized administrator reruns `固定样例试运行` on both active released v1 rows through the deployed Phase A UI/API. Both tests must succeed against the current ready DeepSeek config; this fresh retest proves the current code contract and fixture still render and execute. A stale earlier test is not accepted.

The production target is fixed for every Phase B command: public API `https://api.kplyyk.com`, database `kaipai_prod`, host `101.43.57.62`, and MySQL container `kaipai-mysql`. `kaipai_test` is read only by the dual-environment isolation preflight. No Phase B production helper, schema-history check, release, or smoke command may use a development database or a test domain.

Both v1 rows must have been tested through the real current DeepSeek config and released through normal publish transactions. SQL pointer edits, fabricated test fields, one-scene release, or a v1-to-v1 restore no-op do not satisfy this prerequisite. The immutable publish audit remains the historical release snapshot; the fresh released-version retest updates only version `tested_*` state and supplies separate current-renderability evidence.

Work stays on `codex/00-199-miniapp-profile-library-import`. Backend commits run from `D:\XM\kaipai-team\kaipaile-server`; documentation commits run from `D:\XM\kaipai-team`. Preserve the same unrelated backend and outer-repository changes listed in Plans 1 and 2.

Phase B changes the production runtime contract. After its backend artifact is deployed:

- Template or active-version defects block intelligent recognition.
- Manual profile/work editing remains available.
- Application code cannot fall back to `legacy-code-v1`, another history row, an empty/default string, or rule-based rewriting.
- Operational rollback to the prior Phase A backend artifact remains possible because schema changes are additive; do not clear active pointers or run a destructive down migration.

## File Map

Modify backend production files:

- `src/main/java/com/kaipai/integration/ai/profileimport/DeepSeekProfileTextExtractor.java`
- `src/main/java/com/kaipai/service/ai/impl/ProfileImportServiceImpl.java`
- `src/main/java/com/kaipai/service/ai/profileimport/ProfileImportSchemaValidator.java`

Modify backend tests:

- `src/test/java/com/kaipai/service/ai/profileimport/DeepSeekProfileTextExtractorTest.java`
- `src/test/java/com/kaipai/service/ai/impl/ProfileImportServiceImplTest.java`
- `src/test/java/com/kaipai/service/ai/profileimport/ProfileImportSchemaValidatorTest.java`
- `src/test/java/com/kaipai/migration/ProfileImportPromptGovernanceMySqlIntegrationTest.java`
- `src/test/java/com/kaipai/migration/ProfileImportApplyMySqlIntegrationTest.java` for resolver constructor wiring and the fresh 29-work/apply regression gate

Create outer-repository operational evidence files:

- `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/verify-phase-b-prompt-runtime.sql`
- `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/summarize-phase-b-runtime-logs.py`
- `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/test_summarize_phase_b_runtime_logs.py`
- `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/execution.md`
- `.sce/runbooks/backend-admin-release/profile-import-prompt-governance-runbook.md`

Modify outer-repository governance files:

- `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/tasks.md`
- `.sce/specs/spec-code-mapping.md`
- `.sce/specs/README.md`
- `.sce/steering/CURRENT_CONTEXT.md`
- `docs/dev-playbook.md`

## Task 1: Phase B Preflight And Runtime RED Tests

**Files:**

- Create: `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/verify-phase-b-prompt-runtime.sql`
- Modify: `src/test/java/com/kaipai/service/ai/profileimport/DeepSeekProfileTextExtractorTest.java`
- Modify: `src/test/java/com/kaipai/service/ai/impl/ProfileImportServiceImplTest.java`
- Modify: `src/test/java/com/kaipai/service/ai/profileimport/ProfileImportSchemaValidatorTest.java`

- [ ] **Step 1: Create the exact-binding target-data cutover preflight query**

The read-only SQL emits only IDs, versions, hashes, counts, and stable markers; it never selects Prompt/fixture/user/model-response bodies or secrets.

```sql
WITH expected(template_code, fixture_code, fixture_version) AS (
    SELECT 'full_profile', 'full-profile-v1', '1'
    UNION ALL
    SELECT 'works_only', 'works-only-v1', '1'
)
SELECT CONCAT('PHASE_B_TEMPLATE_COUNT=', COUNT(*)) AS marker
FROM expected e
JOIN ai_profile_import_prompt_template t
  ON t.template_code=e.template_code AND t.scene=e.template_code AND t.deleted=0;

WITH expected(template_code) AS (
    SELECT 'full_profile' UNION ALL SELECT 'works_only'
)
SELECT CONCAT('PHASE_B_READY_ACTIVE_COUNT=', COUNT(*)) AS marker
FROM expected e
JOIN ai_profile_import_prompt_template t
  ON t.template_code=e.template_code AND t.scene=e.template_code AND t.deleted=0
JOIN ai_profile_import_prompt_version v
  ON v.prompt_version_id=t.active_version_id AND v.template_id=t.template_id
WHERE v.deleted=0
  AND v.lifecycle_status='released'
  AND v.schema_version='profile-import-json-v1'
  AND v.contract_version='profile-import-contract-v1';

WITH expected(template_code) AS (
    SELECT 'full_profile' UNION ALL SELECT 'works_only'
)
SELECT CONCAT('PHASE_B_POINTER_OR_STATE_ERROR_COUNT=', COUNT(*)) AS marker
FROM expected e
LEFT JOIN ai_profile_import_prompt_template t
  ON t.template_code=e.template_code AND t.scene=e.template_code AND t.deleted=0
LEFT JOIN ai_profile_import_prompt_version v
  ON v.prompt_version_id=t.active_version_id AND v.template_id=t.template_id
WHERE t.template_id IS NULL
   OR t.active_version_id IS NULL
   OR v.prompt_version_id IS NULL
   OR v.deleted<>0
   OR v.lifecycle_status<>'released'
   OR v.schema_version<>'profile-import-json-v1'
   OR v.contract_version<>'profile-import-contract-v1';

WITH expected(template_code, fixture_code, fixture_version) AS (
    SELECT 'full_profile', 'full-profile-v1', '1'
    UNION ALL
    SELECT 'works_only', 'works-only-v1', '1'
)
SELECT CONCAT('PHASE_B_EXACT_BINDING_MISMATCH_COUNT=', COUNT(*)) AS marker
FROM expected e
LEFT JOIN ai_profile_import_prompt_template t
  ON t.template_code=e.template_code AND t.scene=e.template_code AND t.deleted=0
LEFT JOIN ai_profile_import_prompt_version v
  ON v.prompt_version_id=t.active_version_id AND v.template_id=t.template_id AND v.deleted=0
LEFT JOIN ai_profile_import_config c
  ON c.provider_code='deepseek' AND c.deleted=0
WHERE t.template_id IS NULL
   OR v.prompt_version_id IS NULL
   OR v.lifecycle_status<>'released'
   OR v.test_status<>'success'
   OR NOT (v.tested_content_sha256 <=> v.content_sha256)
   OR v.tested_runtime_sha256 IS NULL
   OR NOT (v.test_fixture_code <=> e.fixture_code)
   OR NOT (v.test_fixture_version <=> e.fixture_version)
   OR v.test_fixture_sha256 IS NULL
   OR c.config_id IS NULL
   OR COALESCE(c.enabled, 0)<>1
   OR c.last_test_status<>'success'
   OR NOT (v.tested_model_name <=> c.model_name)
   OR NOT (v.tested_config_version <=> c.version)
   OR v.tested_by IS NULL
   OR v.tested_at IS NULL;

WITH expected(template_code, fixture_code, fixture_version) AS (
    SELECT 'full_profile', 'full-profile-v1', '1'
    UNION ALL
    SELECT 'works_only', 'works-only-v1', '1'
)
SELECT CONCAT('PHASE_B_RENDERABLE_SCENE_COUNT=', COUNT(*)) AS marker
FROM expected e
JOIN ai_profile_import_prompt_template t
  ON t.template_code=e.template_code AND t.scene=e.template_code AND t.deleted=0
JOIN ai_profile_import_prompt_version v
  ON v.prompt_version_id=t.active_version_id AND v.template_id=t.template_id AND v.deleted=0
JOIN ai_profile_import_config c
  ON c.provider_code='deepseek' AND c.deleted=0
WHERE v.lifecycle_status='released'
  AND v.schema_version='profile-import-json-v1'
  AND v.contract_version='profile-import-contract-v1'
  AND v.test_status='success'
  AND v.tested_content_sha256=v.content_sha256
  AND v.tested_runtime_sha256 IS NOT NULL
  AND v.test_fixture_code=e.fixture_code
  AND v.test_fixture_version=e.fixture_version
  AND v.test_fixture_sha256 IS NOT NULL
  AND c.enabled=1
  AND c.last_test_status='success'
  AND v.tested_model_name=c.model_name
  AND v.tested_config_version=c.version
  AND v.tested_at >= CURRENT_TIMESTAMP - INTERVAL 30 MINUTE;

WITH expected(template_code) AS (
    SELECT 'full_profile' UNION ALL SELECT 'works_only'
)
SELECT CONCAT('PHASE_B_IMMUTABLE_PUBLISH_SNAPSHOT_COUNT=', COUNT(*)) AS marker
FROM (
    SELECT e.template_code
    FROM expected e
    JOIN ai_profile_import_prompt_template t
      ON t.template_code=e.template_code AND t.scene=e.template_code AND t.deleted=0
    JOIN ai_profile_import_prompt_version v
      ON v.prompt_version_id=t.active_version_id AND v.template_id=t.template_id AND v.deleted=0
    LEFT JOIN ai_profile_import_prompt_audit a
      ON a.template_id=t.template_id
     AND a.prompt_version_id=v.prompt_version_id
     AND a.action_code='publish'
     AND a.reason_code='INITIAL_RELEASE'
     AND a.result_status='success'
     AND a.deleted=0
    GROUP BY e.template_code, t.template_id, v.prompt_version_id, v.content_sha256,
             v.schema_version, v.contract_version
    HAVING COUNT(a.audit_id)=1
       AND SUM(CASE WHEN a.content_sha256=v.content_sha256
                     AND a.schema_version=v.schema_version
                     AND a.contract_version=v.contract_version
                     AND a.runtime_sha256 IS NOT NULL
                     AND a.fixture_code IS NOT NULL
                     AND a.fixture_version IS NOT NULL
                     AND a.fixture_sha256 IS NOT NULL
                     AND a.model_name IS NOT NULL
                     AND a.config_version IS NOT NULL
                     AND a.test_operator_id IS NOT NULL
                     AND a.tested_at IS NOT NULL
                    THEN 1 ELSE 0 END)=1
) complete_snapshot_per_scene;

SELECT t.template_code, v.prompt_version_id, v.version_no, v.content_sha256,
       v.tested_runtime_sha256, v.schema_version, v.contract_version,
       v.test_fixture_code, v.test_fixture_version, v.test_fixture_sha256,
       v.tested_model_name, v.tested_config_version, v.tested_by, v.tested_at,
       c.config_id, c.version AS current_config_version
FROM ai_profile_import_prompt_template t
JOIN ai_profile_import_prompt_version v
  ON v.prompt_version_id=t.active_version_id AND v.template_id=t.template_id
JOIN ai_profile_import_config c
  ON c.provider_code='deepseek' AND c.deleted=0
WHERE t.deleted=0 AND t.template_code IN ('full_profile','works_only')
ORDER BY t.template_code;
```

`PHASE_B_EXACT_BINDING_MISMATCH_COUNT` validates current version `tested_*` state against the current enabled, connection-tested model configuration. `PHASE_B_RENDERABLE_SCENE_COUNT` is accepted only immediately after both released versions complete a fresh fixed-fixture retest through the deployed Phase A renderer/tester. `PHASE_B_IMMUTABLE_PUBLISH_SNAPSHOT_COUNT` counts a scene only when its active template/version has exactly one successful `INITIAL_RELEASE` publish audit and that one row contains the complete immutable binding snapshot. It does not compare the historical runtime/fixture/model/config values to later refreshed `tested_*` values; a valid fresh retest must not mutate that audit row.

Expected before any code edit:

```text
PHASE_B_TEMPLATE_COUNT=2
PHASE_B_READY_ACTIVE_COUNT=2
PHASE_B_POINTER_OR_STATE_ERROR_COUNT=0
PHASE_B_EXACT_BINDING_MISMATCH_COUNT=0
PHASE_B_RENDERABLE_SCENE_COUNT=2
PHASE_B_IMMUTABLE_PUBLISH_SNAPSHOT_COUNT=2
```

- [ ] **Step 2: Run the production dual-environment gate, fresh retest, and exact helper preflight**

Run the existing sanitized dual-environment gate with explicit production/test targets:

```powershell
cd D:\XM\kaipai-team
python .sce/runbooks/backend-admin-release/scripts/check-dual-env-preflight.py --host 101.43.57.62 --user kaipaile --identity-file C:\Users\33340\.ssh\kaipai_release_ed25519 --expected-ip 101.43.57.62 --test-api-host test-api.kplyyk.com --test-admin-host test.kplyyk.com --test-data-id kaipai-backend-test.yml --prod-data-id kaipai-backend-prod.yml --test-database kaipai_test --prod-database kaipai_prod --mysql-container kaipai-mysql
if ($LASTEXITCODE -ne 0) { throw 'dual-environment preflight failed' }
```

Expected: JSON has `"passed": true`; both Nacos targets and both databases are distinct and ready. Do not use `--allow-fail`.

Require an authorized admin token only in process memory, discover the two active version IDs from the production API, and retest both released rows. Print only IDs, stable status, hashes, counts, model/config version, and `testedAt`:

```powershell
if (-not $env:KAIPAI_ADMIN_ACCESS_TOKEN) { throw 'KAIPAI_ADMIN_ACCESS_TOKEN is required' }
$phaseBBaseUrl = 'https://api.kplyyk.com'
$adminHeaders = @{ Authorization = "Bearer $env:KAIPAI_ADMIN_ACCESS_TOKEN" }
$templatesResponse = Invoke-RestMethod -Method Get -Uri "$phaseBBaseUrl/api/admin/ai/profile-import/prompt-templates" -Headers $adminHeaders
if ($templatesResponse.code -ne 200) { throw "template list failed with code $($templatesResponse.code)" }
$retestEvidence = @()
foreach ($templateCode in @('full_profile', 'works_only')) {
    $template = @($templatesResponse.data) | Where-Object { $_.templateCode -eq $templateCode }
    if (@($template).Count -ne 1 -or -not $template.activeVersionId) { throw "missing unique active version for $templateCode" }
    $testResponse = Invoke-RestMethod -Method Post -Uri "$phaseBBaseUrl/api/admin/ai/profile-import/prompt-templates/versions/$($template.activeVersionId)/test" -Headers $adminHeaders -TimeoutSec 180
    if ($testResponse.code -ne 200 -or $testResponse.data.status -ne 'success') { throw "fresh retest failed for $templateCode" }
    $retestEvidence += [pscustomobject]@{
        templateCode = $templateCode
        promptVersionId = $testResponse.data.promptVersionId
        status = $testResponse.data.status
        contentSha256 = $testResponse.data.contentSha256
        runtimeSha256 = $testResponse.data.runtimeSha256
        fixtureCode = $testResponse.data.fixtureCode
        fixtureVersion = $testResponse.data.fixtureVersion
        fixtureSha256 = $testResponse.data.fixtureSha256
        modelName = $testResponse.data.modelName
        configVersion = $testResponse.data.configVersion
        candidateCount = $testResponse.data.candidateCount
        workCount = $testResponse.data.workCount
        testedAt = $testResponse.data.testedAt
    }
}
$retestEvidence
$adminHeaders = $null
$templatesResponse = $null
```

Within 30 minutes of those two successful retests, upload and run the exact working-tree SQL against production through the full helper command; Task 6 commits the already exercised script before deployment:

```powershell
$phaseBSql = '.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/verify-phase-b-prompt-runtime.sql'
scp -i C:\Users\33340\.ssh\kaipai_release_ed25519 $phaseBSql kaipaile@101.43.57.62:/tmp/00-200-verify-phase-b.sql
if ($LASTEXITCODE -ne 0) { throw 'failed to upload Phase B preflight SQL' }
ssh -i C:\Users\33340\.ssh\kaipai_release_ed25519 kaipaile@101.43.57.62 "sudo -n /usr/local/bin/kaipai-backend-release-helper.sh --mysql-validation --mysql-script-path /tmp/00-200-verify-phase-b.sql --mysql-database kaipai_prod --mysql-container kaipai-mysql"
if ($LASTEXITCODE -ne 0) { throw 'production Phase B preflight failed' }
```

Expected: helper output identifies `MYSQL_DATABASE=kaipai_prod`, all six markers match the expected block above, and the two sanitized version rows match `$retestEvidence`. Stop if the 30-minute renderability window expires; rerun both fixed-fixture tests instead of weakening the query.

- [ ] **Step 3: Rewrite extractor expectations for a supplied runtime and verify RED**

Replace assertions against hardcoded content with:

```java
@Test
void initialAndRepairCallsUseTheSameSuppliedRuntimeVersion() throws Exception {
    ProfileImportHttpTransport transport = mock(ProfileImportHttpTransport.class);
    when(transport.post(any(), any(), any(), anyInt(), anyInt()))
            .thenReturn("not json", "{\"profileCandidates\":[],\"workCandidates\":[]}");
    ProfileImportPromptRuntime runtime = runtime(
            101L, 1, "SYSTEM_FROM_RELEASED_V1", "REPAIR_FROM_RELEASED_V1");

    new DeepSeekProfileTextExtractor(transport)
            .extract(config(), "sk-memory", runtime, "用户独立原文", "request-id-must-not-enter-prompt");

    ArgumentCaptor<String> payloads = ArgumentCaptor.forClass(String.class);
    verify(transport, times(2)).post(any(), eq("sk-memory"), payloads.capture(), anyInt(), anyInt());
    JsonNode first = mapper.readTree(payloads.getAllValues().get(0));
    JsonNode repair = mapper.readTree(payloads.getAllValues().get(1));
    assertEquals("SYSTEM_FROM_RELEASED_V1", first.at("/messages/0/content").asText());
    assertEquals("SYSTEM_FROM_RELEASED_V1", repair.at("/messages/0/content").asText());
    assertEquals("用户独立原文", first.at("/messages/1/content").asText());
    assertTrue(repair.at("/messages/1/content").asText().startsWith("REPAIR_FROM_RELEASED_V1\n"));
    assertFalse(payloads.getAllValues().toString().contains("request-id-must-not-enter-prompt"));
}

@Test
void extractorExposesNoLegacyProductionEntryPointOrPromptField() {
    assertThrows(NoSuchMethodException.class, () -> DeepSeekProfileTextExtractor.class.getMethod(
            "extract", AiProfileImportConfig.class, String.class, String.class, String.class));
    assertTrue(Arrays.stream(DeepSeekProfileTextExtractor.class.getDeclaredFields())
            .noneMatch(field -> field.getName().contains("SYSTEM_PROMPT")
                    || field.getName().contains("LEGACY")));
}
```

- [ ] **Step 4: Add service order, lineage, and no-fallback tests**

Add a strict resolver mock and inject it into the manual service constructor. Required cases:

```java
@Test
void resolvesPromptBeforeQuotaAndModelCall() {
    when(config.runtimeConfig()).thenReturn(runtimeConfig());
    when(promptResolver.resolve("full_profile")).thenReturn(promptRuntime());
    when(limiter.allow(7L, 10)).thenReturn(true);
    stubValidExtraction();
    service.extract(7L, request("资料"));
    InOrder order = inOrder(config, promptResolver, limiter, extractor);
    order.verify(config).runtimeConfig();
    order.verify(promptResolver).resolve("full_profile");
    order.verify(limiter).allow(7L, 10);
    order.verify(extractor).extract(any(), eq("sk-memory"), eq(promptRuntime()), eq("资料"), eq("req-1"));
}

@Test
void resolverFailureConsumesNoQuotaCallsNoModelAndAuditsNullLineage() {
    when(config.runtimeConfig()).thenReturn(runtimeConfig());
    when(promptResolver.resolve("full_profile"))
            .thenThrow(ProfileDomainErrorCode.PROFILE_IMPORT_UNAVAILABLE.toException());
    BizException error = assertThrows(BizException.class, () -> service.extract(7L, request("资料")));
    assertEquals(46002, error.getCode());
    verifyNoInteractions(limiter, extractor);
    verify(audit).insert(argThat(row ->
            "PROFILE_IMPORT_UNAVAILABLE".equals(row.getErrorCode())
                    && row.getPromptTemplateCode() == null
                    && row.getPromptVersionId() == null
                    && row.getPromptRuntimeSha256() == null));
}

@Test
void successRateLimitAndModelFailureAuditsCarryTheResolvedLineage() {
    assertLineage(successAudit(), promptRuntime());
    assertLineage(rateLimitedAudit(), promptRuntime());
    assertLineage(modelFailureAudit(), promptRuntime());
}

@Test
void worksOnlyModelOutputWithProfileCandidateIsRejectedRatherThanDiscarded() {
    stubResolvedScene("works_only");
    stubExtractionWithOneProfileCandidate();
    ProfileImportExtractReqDTO request = request("作品资料");
    request.setScene("works_only");
    BizException error = assertThrows(BizException.class, () -> service.extract(7L, request));
    assertEquals(46007, error.getCode());
    verify(audit).insert(argThat(row ->
            "PROFILE_IMPORT_RESPONSE_INVALID".equals(row.getErrorCode())
                    && "works_only".equals(row.getScene())));
}
```

Also prove invalid/missing active state never calls a legacy overload, never searches history, and does not consume quota. Verify success/failure/rate-limit audits store template code, version ID/no, Schema version, contract version, and runtime hash, but not full Prompt.

- [ ] **Step 5: Run the RED selector**

```powershell
cd D:\XM\kaipai-team\kaipaile-server
mvn -q "-Dtest=DeepSeekProfileTextExtractorTest,ProfileImportServiceImplTest,ProfileImportSchemaValidatorTest" test
```

Expected: FAIL because the legacy four-argument method/constants still exist and production service has no resolver dependency/lineage wiring.

## Task 2: Remove Legacy Production Prompt And Require Supplied Runtime

**Files:**

- Modify: `src/main/java/com/kaipai/integration/ai/profileimport/DeepSeekProfileTextExtractor.java`
- Modify: `src/test/java/com/kaipai/service/ai/profileimport/DeepSeekProfileTextExtractorTest.java`

- [ ] **Step 1: Delete the legacy method and constants**

The only public extraction method becomes:

```java
public JsonNode extract(
        AiProfileImportConfig config,
        String apiKey,
        ProfileImportPromptRuntime promptRuntime,
        String rawText,
        String requestId) {
    Objects.requireNonNull(promptRuntime, "promptRuntime");
    String response;
    try {
        response = post(config, apiKey, payload(
                promptRuntime.systemPrompt(), rawText, config));
        requireBoundedResponse(response, config);
    } catch (BizException error) {
        throw error;
    } catch (ProfileImportHttpTransport.Timeout error) {
        throw ProfileDomainErrorCode.PROFILE_IMPORT_MODEL_TIMEOUT.toException();
    } catch (Exception error) {
        throw ProfileDomainErrorCode.PROFILE_IMPORT_UNAVAILABLE.toException();
    }
    try {
        return parse(response);
    } catch (Exception firstError) {
        return repair(config, apiKey, promptRuntime, response);
    }
}
```

`repair` sends the same `promptRuntime.systemPrompt()` as system and `promptRuntime.repairPrompt() + "\n" + response` as user. Delete `SYSTEM_PROMPT`, `LEGACY_SYSTEM_PROMPT`, `LEGACY_REPAIR_PROMPT`, and the four-argument public method. Keep one repair maximum, response bounds, timeout/provider/error mapping, `json_object`, token limit, and temperature zero.

The connection probe remains in `ProfileImportConnectionTesterImpl`; do not move or delete it because it is not a production recognition Prompt.

- [ ] **Step 2: Run extractor tests and commit**

```powershell
mvn -q "-Dtest=DeepSeekProfileTextExtractorTest,ProfileImportPromptTesterImplTest" test
git add src/main/java/com/kaipai/integration/ai/profileimport/DeepSeekProfileTextExtractor.java src/test/java/com/kaipai/service/ai/profileimport/DeepSeekProfileTextExtractorTest.java
git commit -m "refactor(ai): require released prompt runtime"
```

Expected: PASS; fixed-fixture tester uses the same sole runtime-aware method.

## Task 3: Resolve Before Quota, Enforce Scene, And Persist Call Lineage

**Files:**

- Modify: `src/main/java/com/kaipai/service/ai/impl/ProfileImportServiceImpl.java`
- Modify: `src/main/java/com/kaipai/service/ai/profileimport/ProfileImportSchemaValidator.java`
- Modify: `src/test/java/com/kaipai/service/ai/impl/ProfileImportServiceImplTest.java`
- Modify: `src/test/java/com/kaipai/service/ai/profileimport/ProfileImportSchemaValidatorTest.java`
- Modify constructor wiring: `src/test/java/com/kaipai/migration/ProfileImportApplyMySqlIntegrationTest.java`

- [ ] **Step 1: Inject resolver and implement the exact order**

Add one constructor dependency:

```java
private final ProfileImportPromptRuntimeResolver promptRuntimeResolver;
```

After request/capability/raw-empty checks, use this order:

```java
ProfileImportRuntimeConfig runtime = requireRuntimeConfig();
long startedAt = System.nanoTime();
ProfileImportPromptRuntime promptRuntime;
try {
    promptRuntime = promptRuntimeResolver.resolve(scene);
} catch (RuntimeException error) {
    saveFailureAuditBestEffort(
            userId, requestId, scene, request.getRawText().length(), runtime, null,
            new ProfileContext(0L, 0L, null), elapsedMillis(startedAt),
            ProfileDomainErrorCode.PROFILE_IMPORT_UNAVAILABLE.errorCode());
    throw ProfileDomainErrorCode.PROFILE_IMPORT_UNAVAILABLE.toException();
}
if (request.getRawText().length() > runtime.maxInputChars()) {
    throw ProfileDomainErrorCode.PROFILE_IMPORT_INPUT_TOO_LONG.toException();
}
if (!rateLimiter.allow(userId, runtime.dailyLimit())) {
    saveFailureAuditBestEffort(
            userId, requestId, scene, request.getRawText().length(), runtime, promptRuntime,
            new ProfileContext(0L, 0L, null), elapsedMillis(startedAt),
            ProfileDomainErrorCode.PROFILE_IMPORT_RATE_LIMITED.errorCode());
    throw ProfileDomainErrorCode.PROFILE_IMPORT_RATE_LIMITED.toException();
}
```

Do not call the resolver before a valid current model config, after quota, or inside the extractor. Resolver failure is normalized to 46002 and does not expose internal state.

- [ ] **Step 2: Pass the runtime through model and scene validation**

Change the model call to:

```java
JsonNode root = extractor.extract(
        config, runtime.apiKey(), promptRuntime, request.getRawText(), requestId);
```

Change validation to:

```java
extraction = validator.validate(root.toString(), request.getRawText(), scene);
```

Keep the old validator overloads for existing tests/callers. `works_only` with nonempty profile candidates is invalid before response mapping; do not silently omit them in `response()` as the primary enforcement.

- [ ] **Step 3: Centralize nullable lineage population**

Add `ProfileImportPromptRuntime promptRuntime` to success/failure/base audit helpers. The only lineage writer is:

```java
private void applyPromptLineage(
        AiProfileImportRequestAudit audit,
        ProfileImportPromptRuntime promptRuntime) {
    if (promptRuntime == null) {
        return;
    }
    audit.setPromptTemplateCode(promptRuntime.templateCode());
    audit.setPromptVersionId(promptRuntime.promptVersionId());
    audit.setPromptVersionNo(promptRuntime.versionNo());
    audit.setPromptSchemaVersion(promptRuntime.schemaVersion());
    audit.setPromptContractVersion(promptRuntime.contractVersion());
    audit.setPromptRuntimeSha256(promptRuntime.runtimeSha256());
}
```

Call it for success, rate-limit, model/schema/context failures after resolution. Resolver failures use null. Continue to store only input length/counts/status/error and IDs/hashes; do not add raw input, source evidence, response, API key, or Prompt body.

- [ ] **Step 4: Run GREEN unit tests and commit**

```powershell
mvn -q "-Dtest=DeepSeekProfileTextExtractorTest,ProfileImportServiceImplTest,ProfileImportSchemaValidatorTest,ProfileImportPromptRuntimeResolverImplTest,ProfileImportPromptTesterImplTest" test
git add src/main/java/com/kaipai/service/ai/impl/ProfileImportServiceImpl.java src/main/java/com/kaipai/service/ai/profileimport/ProfileImportSchemaValidator.java src/test/java/com/kaipai/service/ai/impl/ProfileImportServiceImplTest.java src/test/java/com/kaipai/service/ai/profileimport/ProfileImportSchemaValidatorTest.java src/test/java/com/kaipai/migration/ProfileImportApplyMySqlIntegrationTest.java
git commit -m "feat(ai): cut profile import over to released prompts"
```

Expected: PASS; the old works-only silent-discard test is replaced by a stable rejection test.

## Task 4: Real MySQL Call-Lineage, Restore Immutability, And Existing Import Regression

**Files:**

- Modify: `src/test/java/com/kaipai/migration/ProfileImportPromptGovernanceMySqlIntegrationTest.java`
- Modify for constructor/runtime wiring: `src/test/java/com/kaipai/migration/ProfileImportApplyMySqlIntegrationTest.java`
- Re-open a Phase B production file from Tasks 2-3 only after a named failing assertion identifies the runtime behavior that violates the plan; record that assertion and file before editing

- [ ] **Step 1: Add Spring-proxied runtime lineage tests and verify RED**

Extend the existing Prompt MySQL fixture with a Spring-proxied `ProfileImportService`. Mock only `ProfileImportHttpTransport` and `ProfileImportRateLimiter`. Use the real `DeepSeekProfileTextExtractor`, runtime resolver, renderer, service, mappers, request-audit insert, and MySQL active pointers. Capture both transport payloads and prove the initial and repair requests use the exact runtime resolved from MySQL.

```java
@Test
void fullAndWorksCallsPersistTheExactActiveLineage() throws Exception {
    ProfileImportExtractionRespDTO full = profileImportService.extract(
            FULL_USER_ID, request("mysql-lineage-full", "full_profile", fullText()));
    ProfileImportExtractionRespDTO works = profileImportService.extract(
            WORKS_USER_ID, request("mysql-lineage-works", "works_only", worksText()));
    assertNotNull(full);
    assertNotNull(works);
    assertEquals(0, works.getProfileCandidateCount());
    assertAuditMatchesActive("mysql-lineage-full", "full_profile");
    assertAuditMatchesActive("mysql-lineage-works", "works_only");
}

@Test
void failedSchemaAfterResolutionKeepsLineageAndNoBody() {
    stubInvalidSchemaResponse();
    assertThrows(BizException.class, () -> profileImportService.extract(
            FULL_USER_ID, request("mysql-lineage-invalid", "full_profile", sensitiveText())));
    Map<String, Object> audit = audit("mysql-lineage-invalid");
    assertEquals("failed", audit.get("status"));
    assertEquals("PROFILE_IMPORT_RESPONSE_INVALID", audit.get("error_code"));
    assertNotNull(audit.get("prompt_version_id"));
    assertFalse(audit.toString().contains(sensitiveText()));
}

@Test
void restoreChangesNewRequestLineageWithoutRewritingOldAudit() {
    normallyPublishV2AndMakeActive();
    profileImportService.extract(FULL_USER_ID,
            request("mysql-before-restore", "full_profile", fullText()));
    managementService.restore(ADMIN_ID, "full_profile", releasedV1Id(),
            restoreRequest("INCIDENT_ROLLBACK"));
    profileImportService.extract(FULL_USER_ID,
            request("mysql-after-restore", "full_profile", fullText()));
    assertEquals(releasedV2Id(), auditPromptVersion("mysql-before-restore"));
    assertEquals(releasedV1Id(), auditPromptVersion("mysql-after-restore"));
}
```

Add information-schema/data assertions proving request audit contains no raw text, source evidence, full response, complete Prompt, API key, or candidate proof. The transport captor must parse both the initial and repair JSON payloads, compare their System/Repair content to the real renderer output for the active MySQL version, and prove both calls carry the same resolved version/runtime hash. Do not mock or spy `DeepSeekProfileTextExtractor`.

Run:

```powershell
mvn -q "-Dtest=ProfileImportPromptGovernanceMySqlIntegrationTest" test
```

Expected: FAIL until actual runtime service wiring and audit lineage are correct under Spring/MySQL.

- [ ] **Step 2: Fix only runtime behavior exposed by real-MySQL RED cases**

Production files remain unchanged in this task unless a named failing assertion identifies a runtime defect. When that happens, stop Task 4, return to the owning Task 2 or Task 3 step, add the narrow failing unit case and production fix there, rerun its gates, commit the exact files there, and then restart Task 4. Preserve resolver fresh reads, stable error mapping, quota order, transaction semantics, and privacy shape. Do not add a cache or fallback to make the test pass. Request audit insert remains best effort on failures and required on successes, matching existing behavior.

- [ ] **Step 3: Run schema/proof/apply and 29-work golden regression**

```powershell
mvn -q "-Dtest=DeepSeekProfileTextExtractorTest,ProfileImportServiceImplTest,ProfileImportSchemaValidatorTest,ProfileImportCandidateProofServiceTest,ProfileImportApplyServiceImplTest" test
mvn -q "-Dtest=ProfileImportPromptGovernanceMySqlIntegrationTest,ProfileImportApplyMySqlIntegrationTest" test
```

Expected: PASS. `ProfileImportApplyMySqlIntegrationTest` still proves the explicit Wang Huohuo fixture contains and persists exactly 29 distinct active works, repeats as skips without duplicates, and preserves apply idempotency/concurrency behavior.

- [ ] **Step 4: Commit runtime MySQL evidence**

```powershell
git add src/test/java/com/kaipai/migration/ProfileImportPromptGovernanceMySqlIntegrationTest.java src/test/java/com/kaipai/migration/ProfileImportApplyMySqlIntegrationTest.java
git diff --cached --check
git commit -m "test(ai): prove released prompt call lineage"
```

Expected: no unrelated backend files or generated `target/` output are staged.

## Task 5: Final Backend, Admin, And Artifact No-Fallback Gate

**Files:**

- Verify only; production changes are complete before this task

- [ ] **Step 1: Run the complete related test matrix**

```powershell
mvn -q "-Dtest=AiProfileImportPersistenceShapeTest,ProfileImportConfigServiceImplTest,AdminOperationLoggerTest,ProfileImportErrorContractTest,ProfileImportPromptPolicyTest,ProfileImportPromptRendererTest,ProfileImportPromptRuntimeResolverImplTest,ProfileImportPromptManagementServiceImplTest,ProfileImportPromptTesterImplTest,AdminAiProfileImportPromptControllerTest,DeepSeekProfileTextExtractorTest,ProfileImportServiceImplTest,ProfileImportSchemaValidatorTest,ProfileImportCandidateProofServiceTest,ProfileImportApplyServiceImplTest,ProfileImportPromptGovernanceMySqlIntegrationTest,ProfileImportApplyMySqlIntegrationTest" test
```

Expected: BUILD SUCCESS; MySQL container cases execute.

- [ ] **Step 2: Run the full package gate**

```powershell
mvn -q clean package
```

Expected: exit 0 and fresh `target/kaipai-backend-1.0.0-SNAPSHOT.jar`.

- [ ] **Step 3: Rerun all admin compilation and browser gates**

```powershell
cd D:\XM\kaipai-team\kaipai-admin
npm run type-check
npm run build
npm run e2e:ai-profile-import-config
npm run e2e:ai-profile-import-config -- --dist
```

Expected: all four commands exit 0. `npm run build` executes `scripts/sanitize-dist.mjs`; the development and sanitized-dist E2E runs both remain authoritative even though Phase B changes no admin source.

- [ ] **Step 4: Prove source and compiled extractor have no production legacy entry**

```powershell
cd D:\XM\kaipai-team\kaipaile-server
$phaseBMatches = & rg -n "LEGACY_SYSTEM_PROMPT|LEGACY_REPAIR_PROMPT|legacy-code-v1|private static final String SYSTEM_PROMPT" src/main/java/com/kaipai/integration/ai/profileimport/DeepSeekProfileTextExtractor.java src/main/java/com/kaipai/service/ai/impl/ProfileImportServiceImpl.java src/main/java/com/kaipai/service/ai/impl/ProfileImportPromptRuntimeResolverImpl.java src/main/java/com/kaipai/service/ai/profileimport/ProfileImportPromptRenderer.java
$phaseBRgExit = $LASTEXITCODE
if ($phaseBRgExit -eq 0) { throw 'legacy production Prompt dependency remains in the extractor/service/resolver/renderer scan' }
if ($phaseBRgExit -ne 1) { throw "rg failed during the no-fallback scan with exit code $phaseBRgExit" }
$extractorSignature = javap -classpath target/classes -private com.kaipai.integration.ai.profileimport.DeepSeekProfileTextExtractor
if ($LASTEXITCODE -ne 0) { throw 'javap failed for DeepSeekProfileTextExtractor' }
if ($extractorSignature -match 'LEGACY|SYSTEM_PROMPT|extract\(com\.kaipai\.model\.ai\.entity\.AiProfileImportConfig, java\.lang\.String, java\.lang\.String, java\.lang\.String\)') { throw "compiled extractor retains legacy Prompt surface" }
$extractorSignature
```

Expected: `rg` exits exactly 1 across the extractor, service, resolver, and renderer; any other exit is a hard failure. `javap` shows only the runtime-aware public method, and the PowerShell block exits 0. Contract text in `ProfileImportPromptContract` and bootstrap history in V001 are legitimate and are outside this scoped check.

- [ ] **Step 5: Inspect commits and working tree**

```powershell
git status --short
git log --oneline -10
```

Expected: Phase B production/tests are committed; unrelated pre-existing edits remain unstaged and unchanged.

## Task 6: Phase B Backend Deployment, Two-Scene Smoke, And Runtime Audit Proof

**Files:**

- Commit before deployment: `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/verify-phase-b-prompt-runtime.sql`
- Create: `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/summarize-phase-b-runtime-logs.py`
- Create: `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/test_summarize_phase_b_runtime_logs.py`
- Generate locally through the standard release script: ignored `.sce/runbooks/backend-admin-release/records/*.md` release records
- Generate locally: ignored `output/00-200/` sanitized smoke SQL and runtime-summary artifacts

- [ ] **Step 1: Write the streaming runtime-log sanitizer tests and verify RED**

The unit test supplies sectioned helper stdout containing `DOCKER_INSPECT_ENV` with a fake `.Config.Env` secret and `DOCKER_LOGS_TAIL` with allowlisted stable codes, a fake API key, a fixed Prompt-contract sentinel, a fake smoke-user sentinel, and a fixture sentinel loaded from a temporary fixture file. Assert all of these contracts:

- The summary contains only fixed status/count keys, leak-category count keys, and observed names from the stable-code allowlist.
- No raw helper line, matched fragment, fake key, Prompt/user/fixture sentinel, or `.Config.Env` value appears in stdout or the saved JSON.
- A clean log returns exit 0; any Prompt, user, fixture, or API-key match returns nonzero after writing category counts only.
- Missing/unterminated `DOCKER_LOGS_TAIL`, a failed SSH/helper process, or invalid arguments return nonzero without echoing input.

```powershell
cd D:\XM\kaipai-team
python .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/test_summarize_phase_b_runtime_logs.py
```

Expected: FAIL because the sanitizer does not exist.

- [ ] **Step 2: Implement the streaming counts-only sanitizer and verify GREEN**

`summarize-phase-b-runtime-logs.py` launches native SSH with batch/key-only options and the full remote helper command `sudo -n /usr/local/bin/kaipai-backend-release-helper.sh --runtime-diagnostics --container kaipai-backend --since 20m --tail 800`. It reads helper stdout one line at a time. Outside `__DOCKER_LOGS_TAIL_BEGIN__` / `__DOCKER_LOGS_TAIL_END__`, it recognizes section delimiters and immediately discards every payload line; in particular, it never inspects, buffers, serializes, or writes `DOCKER_INSPECT_ENV`. Inside the log section it updates counters and immediately discards each raw line. It must never create raw log, filtered-log, environment, compose, or helper-output files.

The fixed stable-code allowlist is `PROFILE_IMPORT_UNAVAILABLE`, `PROFILE_IMPORT_RESPONSE_INVALID`, `PROFILE_IMPORT_MODEL_TIMEOUT`, `PROFILE_IMPORT_RATE_LIMITED`, `PROFILE_IMPORT_PROMPT_INVALID`, `PROFILE_IMPORT_PROMPT_STATE_CONFLICT`, `PROFILE_IMPORT_PROMPT_TEST_REQUIRED`, `PROFILE_IMPORT_PROMPT_TEST_STALE`, and `PROFILE_IMPORT_PROMPT_VERSION_CONFLICT`. The leak matchers comprise an API-key pattern, three fixed code-held Prompt-contract sentinels (`顶层必须且只能包含 profileCandidates`, `用户原文只存在于独立 user message`, and `不得新增、删除、猜测或改写事实`), both nonempty smoke raw texts read by environment-variable name, and normalized nonempty lines loaded directly from both fixture files. Match results increment only `apiKey`, `promptContract`, `smokeUserText`, or `fixtureText`; neither matched content nor its line number is retained.

The only JSON fields are `status`, `logLineCount`, `errorLineCount`, `stackTraceLineCount`, `resolverFailureCount`, `stableCodeCounts`, and `leakCategoryCounts`; code-map keys must come from the allowlist and all other values are fixed strings or integers. The script writes UTF-8 JSON to an explicit path under ignored `output/` and emits that same sanitized JSON, with no progress log. A leak count, malformed log section, SSH/helper failure, missing forbidden-value environment variable, or missing fixture returns nonzero.

```powershell
python .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/test_summarize_phase_b_runtime_logs.py
```

Expected: PASS, including the non-echo and nonzero leak cases.

- [ ] **Step 3: Commit the static preflight and sanitizer**

```powershell
git add .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/verify-phase-b-prompt-runtime.sql .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/summarize-phase-b-runtime-logs.py .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/test_summarize_phase_b_runtime_logs.py
git diff --cached --check
git commit -m "test(sce): add prompt phase b runtime gates"
```

Expected: the committed SQL contains only the six static preflight markers from Task 1. Smoke-specific SQL remains per-run and ignored.

- [ ] **Step 4: Rerun dual-environment isolation, both fresh retests, and the exact production preflight immediately before deployment**

```powershell
cd D:\XM\kaipai-team
python .sce/runbooks/backend-admin-release/scripts/check-dual-env-preflight.py --host 101.43.57.62 --user kaipaile --identity-file C:\Users\33340\.ssh\kaipai_release_ed25519 --expected-ip 101.43.57.62 --test-api-host test-api.kplyyk.com --test-admin-host test.kplyyk.com --test-data-id kaipai-backend-test.yml --prod-data-id kaipai-backend-prod.yml --test-database kaipai_test --prod-database kaipai_prod --mysql-container kaipai-mysql
if ($LASTEXITCODE -ne 0) { throw 'dual-environment preflight failed immediately before Phase B deployment' }

if (-not $env:KAIPAI_ADMIN_ACCESS_TOKEN) { throw 'KAIPAI_ADMIN_ACCESS_TOKEN is required' }
$phaseBBaseUrl = 'https://api.kplyyk.com'
$adminHeaders = @{ Authorization = "Bearer $env:KAIPAI_ADMIN_ACCESS_TOKEN" }
$templatesResponse = Invoke-RestMethod -Method Get -Uri "$phaseBBaseUrl/api/admin/ai/profile-import/prompt-templates" -Headers $adminHeaders
if ($templatesResponse.code -ne 200) { throw "template list failed with code $($templatesResponse.code)" }
$retestEvidence = @()
foreach ($templateCode in @('full_profile', 'works_only')) {
    $template = @($templatesResponse.data) | Where-Object { $_.templateCode -eq $templateCode }
    if (@($template).Count -ne 1 -or -not $template.activeVersionId) { throw "missing unique active version for $templateCode" }
    $testResponse = Invoke-RestMethod -Method Post -Uri "$phaseBBaseUrl/api/admin/ai/profile-import/prompt-templates/versions/$($template.activeVersionId)/test" -Headers $adminHeaders -TimeoutSec 180
    if ($testResponse.code -ne 200 -or $testResponse.data.status -ne 'success') { throw "fresh retest failed for $templateCode" }
    $retestEvidence += [pscustomobject]@{
        templateCode = $templateCode
        promptVersionId = $testResponse.data.promptVersionId
        status = $testResponse.data.status
        contentSha256 = $testResponse.data.contentSha256
        runtimeSha256 = $testResponse.data.runtimeSha256
        fixtureCode = $testResponse.data.fixtureCode
        fixtureVersion = $testResponse.data.fixtureVersion
        fixtureSha256 = $testResponse.data.fixtureSha256
        modelName = $testResponse.data.modelName
        configVersion = $testResponse.data.configVersion
        candidateCount = $testResponse.data.candidateCount
        workCount = $testResponse.data.workCount
        testedAt = $testResponse.data.testedAt
    }
}
$retestEvidence
$adminHeaders = $null
$templatesResponse = $null

$phaseBSql = '.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/verify-phase-b-prompt-runtime.sql'
scp -i C:\Users\33340\.ssh\kaipai_release_ed25519 $phaseBSql kaipaile@101.43.57.62:/tmp/00-200-verify-phase-b.sql
if ($LASTEXITCODE -ne 0) { throw 'failed to upload Phase B preflight SQL' }
ssh -i C:\Users\33340\.ssh\kaipai_release_ed25519 kaipaile@101.43.57.62 "sudo -n /usr/local/bin/kaipai-backend-release-helper.sh --mysql-validation --mysql-script-path /tmp/00-200-verify-phase-b.sql --mysql-database kaipai_prod --mysql-container kaipai-mysql"
if ($LASTEXITCODE -ne 0) { throw 'production Phase B preflight failed' }
```

Expected: the dual-environment JSON has `"passed": true`; helper output identifies `MYSQL_DATABASE=kaipai_prod`; both sanitized version rows match `$retestEvidence`; and every static marker is exact:

```text
PHASE_B_TEMPLATE_COUNT=2
PHASE_B_READY_ACTIVE_COUNT=2
PHASE_B_POINTER_OR_STATE_ERROR_COUNT=0
PHASE_B_EXACT_BINDING_MISMATCH_COUNT=0
PHASE_B_RENDERABLE_SCENE_COUNT=2
PHASE_B_IMMUTABLE_PUBLISH_SNAPSHOT_COUNT=2
```

Stop on any mismatch or expired 30-minute test window. Rerun both released-version tests and the static helper preflight after any delay or config change.

- [ ] **Step 5: Deploy the Phase B backend through the standard production release script**

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py --label 00-200-prompt-phase-b --operator codex --public-base-url https://api.kplyyk.com --mysql-database kaipai_prod --overlay-path src/main/java/com/kaipai/service/ai/impl/ProfileImportServiceImpl.java
```

Expected: exit 0 and a locally generated ignored backend release record with artifact SHA, backup jar path, container runtime readback, internal/public smoke, and post-release review. No schema migration or admin deployment is needed in Phase B.

- [ ] **Step 6: Run one authorized smoke for each scene without persisting response bodies**

Require the designated test-user token plus two fixed fictional smoke texts in process environment only. Set their values outside the recorded command transcript; never print them. Keep the exact request IDs for the audit query and sanitizer:

```powershell
if (-not $env:KAIPAI_PROFILE_IMPORT_SMOKE_TOKEN) { throw 'KAIPAI_PROFILE_IMPORT_SMOKE_TOKEN is required' }
if (-not $env:PHASE_B_FULL_SMOKE_RAW_TEXT) { throw 'PHASE_B_FULL_SMOKE_RAW_TEXT is required' }
if (-not $env:PHASE_B_WORKS_SMOKE_RAW_TEXT) { throw 'PHASE_B_WORKS_SMOKE_RAW_TEXT is required' }
$smokeStamp = Get-Date -Format 'yyyyMMddHHmmss'
$fullRequestId = "00-200-phase-b-full-$smokeStamp"
$worksRequestId = "00-200-phase-b-works-$smokeStamp"
$smokeHeaders = @{ Authorization = "Bearer $env:KAIPAI_PROFILE_IMPORT_SMOKE_TOKEN"; 'Content-Type' = 'application/json' }
$fullPayload = @{ requestId = $fullRequestId; scene = 'full_profile'; rawText = $env:PHASE_B_FULL_SMOKE_RAW_TEXT } | ConvertTo-Json -Compress
$worksPayload = @{ requestId = $worksRequestId; scene = 'works_only'; rawText = $env:PHASE_B_WORKS_SMOKE_RAW_TEXT } | ConvertTo-Json -Compress
$fullResult = Invoke-RestMethod -Method Post -Uri 'https://api.kplyyk.com/api/ai/profile-import/extract' -Headers $smokeHeaders -Body $fullPayload
$worksResult = Invoke-RestMethod -Method Post -Uri 'https://api.kplyyk.com/api/ai/profile-import/extract' -Headers $smokeHeaders -Body $worksPayload
if ($fullResult.code -ne 200) { throw "full_profile smoke failed with code $($fullResult.code)" }
if ($worksResult.code -ne 200) { throw "works_only smoke failed with code $($worksResult.code)" }
if (@($worksResult.data.profileCandidates).Count -ne 0) { throw 'works_only returned profile candidates' }
@{ fullRequestId = $fullRequestId; worksRequestId = $worksRequestId; fullProfileCandidates = @($fullResult.data.profileCandidates).Count; fullWorks = @($fullResult.data.workCandidates).Count; worksOnlyWorks = @($worksResult.data.workCandidates).Count }
$fullResult = $null
$worksResult = $null
$fullPayload = $null
$worksPayload = $null
$smokeHeaders = $null
```

Expected: both business codes are 200, works-only profile count is zero, and only request IDs/counts are printed. Do not redirect response objects or environment values to disk and do not copy source evidence into `execution.md`.

- [ ] **Step 7: Prove the two exact request audits use current active lineage**

Validate the fixed-format IDs before SQL interpolation. Generate UTF-8 without BOM under ignored `output/`, upload it, execute it against `kaipai_prod`, assert all five markers, and delete both temporary SQL files in `finally`:

```powershell
if ($fullRequestId -notmatch '\A00-200-phase-b-full-\d{14}\z') { throw 'invalid fullRequestId format' }
if ($worksRequestId -notmatch '\A00-200-phase-b-works-\d{14}\z') { throw 'invalid worksRequestId format' }
if ($smokeStamp -notmatch '\A\d{14}\z') { throw 'invalid smokeStamp format' }
$smokeOutputDir = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) 'output/00-200'))
[System.IO.Directory]::CreateDirectory($smokeOutputDir) | Out-Null
$smokeSqlPath = Join-Path $smokeOutputDir "$smokeStamp-phase-b-smoke-audit.sql"
$smokeRemoteSql = "/tmp/00-200-phase-b-smoke-$smokeStamp.sql"
$smokeSql = @"
SELECT CONCAT('PHASE_B_SMOKE_EXACT_REQUEST_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_request_audit WHERE request_id IN ('$fullRequestId','$worksRequestId');
SELECT CONCAT('PHASE_B_SMOKE_SUCCESS_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_request_audit WHERE request_id IN ('$fullRequestId','$worksRequestId') AND status='success';
SELECT CONCAT('PHASE_B_SMOKE_SCENE_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_request_audit WHERE (request_id='$fullRequestId' AND scene='full_profile') OR (request_id='$worksRequestId' AND scene='works_only');
SELECT CONCAT('PHASE_B_SMOKE_MISSING_LINEAGE_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_request_audit WHERE request_id IN ('$fullRequestId','$worksRequestId') AND (prompt_template_code IS NULL OR prompt_version_id IS NULL OR prompt_version_no IS NULL OR prompt_schema_version IS NULL OR prompt_contract_version IS NULL OR prompt_runtime_sha256 IS NULL);
SELECT CONCAT('PHASE_B_SMOKE_NONACTIVE_LINEAGE_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_request_audit s LEFT JOIN ai_profile_import_prompt_template t ON t.template_code=s.prompt_template_code AND t.scene=s.scene AND t.active_version_id=s.prompt_version_id AND t.deleted=0 LEFT JOIN ai_profile_import_prompt_version v ON v.prompt_version_id=s.prompt_version_id AND v.template_id=t.template_id AND v.deleted=0 WHERE s.request_id IN ('$fullRequestId','$worksRequestId') AND (t.template_id IS NULL OR v.prompt_version_id IS NULL OR v.lifecycle_status<>'released' OR NOT (s.prompt_version_no <=> v.version_no) OR NOT (s.prompt_schema_version <=> v.schema_version) OR NOT (s.prompt_contract_version <=> v.contract_version) OR NOT (s.prompt_runtime_sha256 <=> v.tested_runtime_sha256));
SELECT request_id, scene, status, error_code, prompt_template_code, prompt_version_id, prompt_version_no, prompt_schema_version, prompt_contract_version, prompt_runtime_sha256, candidate_count, work_count, elapsed_ms FROM ai_profile_import_request_audit WHERE request_id IN ('$fullRequestId','$worksRequestId') ORDER BY FIELD(request_id, '$fullRequestId', '$worksRequestId');
"@
[System.IO.File]::WriteAllText($smokeSqlPath, $smokeSql, [System.Text.UTF8Encoding]::new($false))
$smokeRemoteUploaded = $false
$smokeRemoteCleanupExit = 0
try {
    scp -i C:\Users\33340\.ssh\kaipai_release_ed25519 $smokeSqlPath "kaipaile@101.43.57.62:$smokeRemoteSql"
    if ($LASTEXITCODE -ne 0) { throw 'failed to upload exact smoke audit SQL' }
    $smokeRemoteUploaded = $true
    $smokeAuditOutput = & ssh -i C:\Users\33340\.ssh\kaipai_release_ed25519 kaipaile@101.43.57.62 "sudo -n /usr/local/bin/kaipai-backend-release-helper.sh --mysql-validation --mysql-script-path $smokeRemoteSql --mysql-database kaipai_prod --mysql-container kaipai-mysql"
    if ($LASTEXITCODE -ne 0) { throw 'exact production smoke audit failed' }
    $smokeAuditText = $smokeAuditOutput -join "`n"
    foreach ($expectedMarker in @('PHASE_B_SMOKE_EXACT_REQUEST_COUNT=2','PHASE_B_SMOKE_SUCCESS_COUNT=2','PHASE_B_SMOKE_SCENE_COUNT=2','PHASE_B_SMOKE_MISSING_LINEAGE_COUNT=0','PHASE_B_SMOKE_NONACTIVE_LINEAGE_COUNT=0')) {
        if ($smokeAuditText -notmatch "(?m)^$([regex]::Escape($expectedMarker))`r?$") { throw "missing exact smoke marker: $expectedMarker" }
    }
    $smokeAuditOutput
} finally {
    if ($smokeRemoteUploaded) {
        ssh -i C:\Users\33340\.ssh\kaipai_release_ed25519 kaipaile@101.43.57.62 "rm -f -- '$smokeRemoteSql'"
        $smokeRemoteCleanupExit = $LASTEXITCODE
    }
    if (Test-Path -LiteralPath $smokeSqlPath) { Remove-Item -LiteralPath $smokeSqlPath -Force }
    if ($smokeRemoteCleanupExit -ne 0) { throw 'failed to delete remote smoke audit SQL' }
}
```

Expected exact markers:

```text
PHASE_B_SMOKE_EXACT_REQUEST_COUNT=2
PHASE_B_SMOKE_SUCCESS_COUNT=2
PHASE_B_SMOKE_SCENE_COUNT=2
PHASE_B_SMOKE_MISSING_LINEAGE_COUNT=0
PHASE_B_SMOKE_NONACTIVE_LINEAGE_COUNT=0
```

The two sanitized rows must be the `$fullRequestId` and `$worksRequestId` values created in Step 6 and must show their matching scenes, active version IDs, `profile-import-json-v1`, `profile-import-contract-v1`, 64-character runtime hashes, counts, and elapsed time. Body columns are forbidden.

- [ ] **Step 8: Run the sanitized streaming diagnostic and apply the rollback rule**

```powershell
$runtimeSummaryPath = Join-Path $smokeOutputDir "$smokeStamp-phase-b-runtime-summary.json"
python .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/summarize-phase-b-runtime-logs.py --host 101.43.57.62 --user kaipaile --identity-file C:\Users\33340\.ssh\kaipai_release_ed25519 --container kaipai-backend --since 20m --tail 800 --forbidden-env PHASE_B_FULL_SMOKE_RAW_TEXT --forbidden-env PHASE_B_WORKS_SMOKE_RAW_TEXT --fixture-file kaipaile-server/src/main/resources/ai/profile-import/prompt-fixtures/full-profile-v1.txt --fixture-file kaipaile-server/src/main/resources/ai/profile-import/prompt-fixtures/works-only-v1.txt --output $runtimeSummaryPath
$runtimeSummaryExit = $LASTEXITCODE
if (Test-Path -LiteralPath $runtimeSummaryPath) { Get-Content -LiteralPath $runtimeSummaryPath -Raw }
Remove-Item Env:PHASE_B_FULL_SMOKE_RAW_TEXT -ErrorAction SilentlyContinue
Remove-Item Env:PHASE_B_WORKS_SMOKE_RAW_TEXT -ErrorAction SilentlyContinue
if ($runtimeSummaryExit -ne 0) { throw 'sanitized runtime diagnostic found leakage, malformed helper output, or a helper failure; inspect counts-only JSON' }
```

Expected: exit 0 and a counts-only JSON artifact with zero leak-category, stack-trace, and repeated-resolver-failure counts and no unexplained stable-code spike. No raw log or `.Config.Env` artifact exists. If the deployment, either smoke, either exact audit, or the sanitizer fails, restore the Phase A jar from the backup path in the ignored Phase B release record and follow section 6.1 of `backend-admin-standard-release.md`; rerun the standard backend smoke. Do not change active pointers or database rows during application rollback.

## Task 7: Runbook, Execution Evidence, SCE Mapping, And Final Acceptance

**Files:**

- Create: `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/execution.md`
- Create: `.sce/runbooks/backend-admin-release/profile-import-prompt-governance-runbook.md`
- Modify: `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/tasks.md`
- Modify: `.sce/specs/spec-code-mapping.md`
- Modify: `.sce/specs/README.md`
- Modify: `.sce/steering/CURRENT_CONTEXT.md`
- Modify: `docs/dev-playbook.md`

- [ ] **Step 1: Write the operating runbook with exact safety boundaries**

The runbook contains these sections and concrete procedures:

```text
scope: full_profile/works_only and Repair only
permissions: read/update/test/publish/restore/audit separation
draft: one open draft, expectedVersion conflict, bootstrap abandon prohibition
test: fixed fictional fixture, current ready model, no user quota/business write
publish: successful exact binding, fixed reasons, template-version-config lock order
restore: released owned target, pointer switch only, fixed restore reasons, open draft preserved
Phase A: migrations -> governance deploy -> real test -> normal release of both v1
Phase B: target preflight -> no-legacy artifact -> backend deploy -> two-scene smoke -> lineage proof
observation: stable errors, Schema-invalid ratio, elapsed time, sanitized audits
privacy: forbidden body/response/key/reason/change-summary destinations
rollback: Prompt quality uses history restore; application failure restores Phase A jar; no pointer clearing/down migration
```

Include exact commands from Plans 1-3 and link the standard release manual. Do not include credentials, tokens, JDBC URLs, Prompt bodies, fixtures, user source text, or model responses.

- [ ] **Step 2: Create `execution.md` with fresh evidence**

Record:

- Backend commit SHAs for Phase A and Phase B slices.
- Admin commit SHAs.
- Exact Maven/npm commands and exit codes.
- MySQL 8.0.36 container execution, not skipped.
- Development and dist E2E evidence paths and zero-error summaries.
- Ignored schema/backend/admin release records, referenced by sanitized path, timestamp, label, and artifact SHA; record explicitly that these generated files are not staged or committed.
- Initial bootstrap and final Phase A marker blocks.
- Two v1 IDs/version numbers/content/runtime/fixture/model/config hashes and publish audit IDs.
- Phase B preflight markers, no-legacy `rg/javap` result, smoke request IDs/counts, lineage markers, and ignored counts-only runtime-summary path/timestamp.
- Isolated v2-to-v1 MySQL test evidence showing old audit remains v2 and new audit uses v1.
- Explicit statement that 00-199 T6/T9, work active-uniqueness migration, and asset migration are not closed by 00-200.

Use IDs/hashes/counts only. Redact tokens and never paste body-bearing data.

- [ ] **Step 3: Update SCE status without falsely closing 00-199**

Mark 00-200 T1-T10 checkboxes complete only when their linked evidence exists. Update Spec README/current context from `书面 Spec/待实施` to the actual Phase A + Phase B complete state. Defer the mixed-worktree `spec-code-mapping.md` edit to the exact index-and-worktree patch in Step 4. Preserve the current statement that 00-199 Plan 3/T6 and overall gates remain incomplete.

Update `docs/dev-playbook.md` with the durable rule:

```text
Profile-import Prompt changes are draft -> fixed-fixture test -> normal publish.
Production reads only released active versions and has no Prompt cache/fallback.
Publish/restore/abandon accept fixed reasonCode only.
Prompt quality rollback uses history restore; application rollback uses the prior jar and leaves pointers intact.
```

- [ ] **Step 4: Stage outer-repository files without capturing existing 00-199 edits**

Stage clean/new files explicitly:

```powershell
git add .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/tasks.md .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/execution.md .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/verify-phase-a-prompt-state.sql .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/verify-phase-b-prompt-runtime.sql .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/summarize-phase-b-runtime-logs.py .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/test_summarize_phase_b_runtime_logs.py .sce/specs/README.md .sce/steering/CURRENT_CONTEXT.md .sce/runbooks/backend-admin-release/profile-import-prompt-governance-runbook.md docs/dev-playbook.md
```

`.sce/specs/spec-code-mapping.md` already contains unrelated unstaged 00-199 edits. Do not edit or stage it before this point and do not run plain `git add` on it. Apply this literal patch to the index first and then to the working tree; its context is confined to the committed 00-200 block, so the adjacent 00-199 working-tree changes remain untouched:

```powershell
$mappingAlreadyStaged = @(git diff --cached --name-only -- .sce/specs/spec-code-mapping.md)
if ($LASTEXITCODE -ne 0) { throw 'failed to inspect staged mapping state' }
if ($mappingAlreadyStaged.Count -ne 0) { throw 'spec-code-mapping.md already has staged content; stop before applying the 00-200 patch' }
$mappingPatch = @'
diff --git a/.sce/specs/spec-code-mapping.md b/.sce/specs/spec-code-mapping.md
--- a/.sce/specs/spec-code-mapping.md
+++ b/.sce/specs/spec-code-mapping.md
@@ -1527,6 +1527,9 @@
-| 00-200 deepseek-profile-import-prompt-template-governance | `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/requirements.md` | — | 📝 已编制待最终审阅：仅治理 full_profile / works_only 与 Repair Prompt 的草稿、试运行、发布、恢复、权限和谱系 |
-| | `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/design.md` | — | 📝 已编制待最终审阅：独立模板定义 / 版本 / 审计表，代码安全合同，现有配置页内治理，无运行时缓存 |
-| | `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/tasks.md` | — | ⏳ 待用户书面 Spec 审阅后编写详细实施计划并按 TDD 执行 |
-| | `kaipai-admin/src/components/business/ProfileImportPromptTemplatePanel.vue` | — | ⏳ 计划新增：双场景版本台账、草稿编辑、试运行、发布和恢复 |
-| | `kaipaile-server/src/main/java/com/kaipai/service/ai/profileimport/ProfileImportPromptContract.java` | — | ⏳ 计划新增：后台不可修改的字段、枚举、证据和防幻觉合同 |
-| | `kaipaile-server/src/main/java/com/kaipai/service/ai/impl/ProfileImportPromptManagementServiceImpl.java` | — | ⏳ 计划新增：草稿、试运行、发布、恢复和审计事务 |
+| 00-200 deepseek-profile-import-prompt-template-governance | `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/requirements.md` | `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/execution.md` | ✅ 已完成：full_profile / works_only 与 Repair Prompt 的草稿、固定样例试运行、正常发布、恢复、权限、运行时接管和谱系审计 |
+| | `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/design.md` | `.sce/runbooks/backend-admin-release/profile-import-prompt-governance-runbook.md` | ✅ 已落地：独立模板 / 版本 / 审计表、代码安全合同、现有配置页治理、无缓存且 fail closed |
+| | `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/tasks.md` | `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/execution.md` | ✅ T1-T10 已按证据核销；Phase A 两个 v1 正常发布后完成 Phase B 接管 |
+| | `kaipaile-server/src/main/resources/db/migration/V20260726_001__ai_profile_import_prompt_template_governance.sql` | `kaipaile-server/src/test/java/com/kaipai/migration/ProfileImportPromptGovernanceMySqlIntegrationTest.java` | ✅ 已验证：诚实 bootstrap、复合指针、单开放草稿、绑定审计、并发事务与恢复语义 |
+| | `kaipai-admin/src/components/business/ProfileImportPromptTemplatePanel.vue` | `kaipai-admin/scripts/e2e-ai-profile-import-config.mjs` | ✅ 已验证：双场景版本治理、权限隔离、按需正文、冲突保留及开发态 / sanitized dist E2E |
+| | `kaipaile-server/src/main/java/com/kaipai/service/ai/profileimport/ProfileImportPromptContract.java` | `kaipaile-server/src/test/java/com/kaipai/service/ai/profileimport/ProfileImportPromptRendererTest.java` | ✅ 已验证：后端固定字段 / 枚举 / 证据合同与四字节长度前缀哈希 |
+| | `kaipaile-server/src/main/java/com/kaipai/service/ai/impl/ProfileImportPromptManagementServiceImpl.java` | `kaipaile-server/src/test/java/com/kaipai/service/ai/impl/ProfileImportPromptManagementServiceImplTest.java` | ✅ 已验证：草稿、测试、原子发布、不可变绑定快照、恢复和固定 reasonCode 审计 |
+| | `kaipaile-server/src/main/java/com/kaipai/service/ai/impl/ProfileImportPromptRuntimeResolverImpl.java` | `kaipaile-server/src/test/java/com/kaipai/service/ai/impl/ProfileImportServiceImplTest.java` | ✅ 已验证：fresh read、无缓存 / fallback、配额前解析和全路径调用谱系 |
+| | `kaipaile-server/src/main/java/com/kaipai/integration/ai/profileimport/DeepSeekProfileTextExtractor.java` | `kaipaile-server/src/test/java/com/kaipai/service/ai/profileimport/DeepSeekProfileTextExtractorTest.java` | ✅ 已验证：生产 Java Prompt 已删除，首次提取与 Repair 使用同一 released runtime |
'@
$mappingPatch | git apply --unidiff-zero --cached --check -
if ($LASTEXITCODE -ne 0) { throw '00-200 mapping patch does not apply cleanly to the index' }
$mappingPatch | git apply --unidiff-zero --cached -
if ($LASTEXITCODE -ne 0) { throw 'failed to stage the 00-200 mapping patch' }
$cachedMappingDiff = @(git diff --cached --unified=0 -- .sce/specs/spec-code-mapping.md)
if ($LASTEXITCODE -ne 0) { throw 'failed to inspect the cached 00-200 mapping patch' }
$expectedMappingAdds = @($mappingPatch -split "`r?`n" | Where-Object { $_ -match '^\+\|' })
$expectedMappingRemoves = @($mappingPatch -split "`r?`n" | Where-Object { $_ -match '^-\|' })
$actualMappingAdds = @($cachedMappingDiff | Where-Object { $_ -match '^\+\|' })
$actualMappingRemoves = @($cachedMappingDiff | Where-Object { $_ -match '^-\|' })
$mappingAddDifference = @(Compare-Object -ReferenceObject $expectedMappingAdds -DifferenceObject $actualMappingAdds)
$mappingRemoveDifference = @(Compare-Object -ReferenceObject $expectedMappingRemoves -DifferenceObject $actualMappingRemoves)
$mappingHunks = @($cachedMappingDiff | Where-Object { $_ -match '^@@ ' })
$mappingNumstat = git diff --cached --numstat -- .sce/specs/spec-code-mapping.md
if ($expectedMappingAdds.Count -ne 9 -or $actualMappingAdds.Count -ne 9 -or $mappingAddDifference.Count -ne 0) { throw 'cached mapping additions are not the exact nine 00-200 rows' }
if ($expectedMappingRemoves.Count -ne 6 -or $actualMappingRemoves.Count -ne 6 -or $mappingRemoveDifference.Count -ne 0) { throw 'cached mapping removals are not the exact six committed 00-200 rows' }
if ($mappingHunks.Count -ne 1 -or $mappingNumstat -ne "9`t6`t.sce/specs/spec-code-mapping.md") { throw 'cached mapping diff contains content outside the exact 00-200 hunk' }
$mappingPatch | git apply --unidiff-zero --check -
if ($LASTEXITCODE -ne 0) { throw '00-200 mapping patch does not apply cleanly to the working tree' }
$mappingPatch | git apply --unidiff-zero -
if ($LASTEXITCODE -ne 0) { throw 'failed to update the working-tree 00-200 mapping block' }
git diff --cached --check
git diff --cached --name-only
git diff --cached -- .sce/specs/spec-code-mapping.md
git diff -- .sce/specs/spec-code-mapping.md
```

Expected: the cached mapping diff contains only the nine 00-200 rows shown above. The uncached mapping diff still contains the pre-existing 00-199 edits and contains no inverse/reversion of the staged 00-200 block. No temporary patch file is created or committed.

- [ ] **Step 5: Commit final governance evidence**

```powershell
git commit -m "docs(sce): close prompt governance rollout"
```

Expected: commit succeeds without `.tmp-kaipaile-server-pdf-retry/` or any 00-199 source/spec edit.

- [ ] **Step 6: Perform final R1-R72 acceptance review**

Read `requirements.md` from top to bottom and attach each requirement to fresh evidence. Minimum mapping:

| Requirements | Final evidence |
|---|---|
| R1-R6 | Existing settings IA, two scenes, shared envelope, works-only model/validator enforcement |
| R7-R17 | DB pointers/unique gate, optimistic draft tests, immutable release, real v2-to-v1 restore |
| R18-R26 | Code-held contract, framed hashes, separate user message, same-runtime repair, no variables |
| R27-R37 | Versioned fictional fixtures, real current-model tests, exact binding, lock order, rollback |
| R38-R45 | Fresh resolver reads, no cache/fallback, no-legacy artifact, sanitized call lineage |
| R46-R57 | Lazy details, strict DTOs, independent permissions, stable errors, conflict retention |
| R58-R63 | Additive migrations, honest bootstrap, Phase A releases before Phase B, fail closed |
| R64-R68 | RED/GREEN commits, unit/MySQL concurrency, extractor/Schema/proof/apply/29-work gates |
| R69-R70 | Development and sanitized-dist CDP E2E, no-read body leakage proof |
| R71 | Full related selectors and `mvn clean package` exit 0 |
| R72 | Mapping/context/playbook/runbook/execution committed; ignored release and diagnostic records generated locally and referenced from `execution.md` by sanitized path, timestamp, label, and artifact SHA |

Any missing evidence leaves the corresponding task unchecked and 00-200 incomplete. Completion is not inferred from code presence alone.
