# Production Tencent Hunyuan Provider Config Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the verified `tencent-hunyuan` AI image provider configuration from `kaipai_dev` into the active production database `kaipai_prod` and prove that production can generate an image through Tencent Hunyuan.

**Architecture:** A dedicated SCE script generates guarded SQL and runs it through the existing backend release helper. The SQL copies only the `tencent-hunyuan` row, creates target-side backup tables before mutation, activates Tencent as the single active provider, and writes a sanitized migration audit row. Verification reads only non-secret fields and is followed by the existing authenticated provider test endpoint.

**Tech Stack:** Python 3 standard library, `unittest`, MySQL 8, OpenSSH/SCP, `kaipai-backend-release-helper.sh`, Spring Boot admin provider API.

---

### Task 1: Establish SCE Governance

**Files:**
- Create: `.sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/requirements.md`
- Create: `.sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/design.md`
- Create: `.sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/tasks.md`
- Create: `.sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/execution.md`
- Modify: `.sce/specs/README.md`
- Modify: `.sce/specs/spec-code-mapping.md`

- [ ] Record the source and target database facts, the exact provider contract, secret-handling rules, backup requirements, rollback boundary, and production smoke criteria.
- [ ] Add `00-197` to the Spec index and code mapping without changing unrelated entries.

### Task 2: Write Failing Migration Script Tests

**Files:**
- Create: `.sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/scripts/test-run-production-tencent-provider-migration.py`
- Test: `.sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/scripts/test-run-production-tencent-provider-migration.py`

- [ ] Add tests asserting that precheck SQL reads `kaipai_dev` and `kaipai_prod`, requires one active/enabled source row with ciphertext, and never selects ciphertext in output.
- [ ] Add tests asserting that apply SQL guards before backup, creates `zz197_` backup tables, copies only `tencent-hunyuan`, deactivates any target active row, and writes `migration_restore` audit metadata.
- [ ] Add tests asserting that verify SQL exposes only provider code, endpoint, model, enabled/active flags, secret presence, and test status.
- [ ] Run:

```powershell
python .sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/scripts/test-run-production-tencent-provider-migration.py
```

Expected: `ModuleNotFoundError` or missing-script failure because the implementation file does not exist yet.

### Task 3: Implement the Guarded Migration Runner

**Files:**
- Create: `.sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/scripts/run-production-tencent-provider-migration.py`
- Test: `.sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/scripts/test-run-production-tencent-provider-migration.py`

- [ ] Implement `Context`, SQL identifier validation, helper output parsing, marker parsing, SSH/SCP execution, and remote temporary SQL cleanup.
- [ ] Implement modes `precheck`, `apply`, and `verify` with defaults `source=kaipai_dev`, `target=kaipai_prod`, `container=kaipai-mysql`.
- [ ] Build apply SQL with these guarded operations:

```sql
UPDATE `kaipai_prod`.`ai_image_provider_config`
SET `active` = 0
WHERE `active` = 1;

INSERT INTO `kaipai_prod`.`ai_image_provider_config` (...)
SELECT ...
FROM `kaipai_dev`.`ai_image_provider_config`
WHERE `provider_code` = 'tencent-hunyuan' AND `deleted` = 0;
```

- [ ] Keep `secret_config_ciphertext` inside the database-to-database `INSERT ... SELECT`; do not print or persist it locally.
- [ ] Reset stale test-result fields during migration and insert a sanitized `migration_restore` audit row.
- [ ] Run the unit test command again and expect all tests to pass.

### Task 4: Run Production Precheck and Backup-Gated Apply

**Files:**
- Modify: `.sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/execution.md`

- [ ] Run:

```powershell
python .sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/scripts/run-production-tencent-provider-migration.py --mode precheck --operator codex
```

Expected markers: one source row, `enabled=1`, `active=1`, endpoint `https://aiart.tencentcloudapi.com`, model `hunyuan-image-3.0`, secret present, and zero target provider rows.

- [ ] Run:

```powershell
python .sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/scripts/run-production-tencent-provider-migration.py --mode apply --operator codex
```

Expected markers: backup table names beginning `zz197_`, one target Tencent row, one active provider, secret present, and `MIGRATION_APPLIED=1`.

### Task 5: Verify Runtime Selection and Real Provider Call

**Files:**
- Modify: `.sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/execution.md`

- [ ] Run `--mode verify` and require `ACTIVE_PROVIDER=tencent-hunyuan`, `MODEL=hunyuan-image-3.0`, and `HAS_SECRET=1`.
- [ ] Open `https://kplyyk.com/system/ai-image-providers` with the existing authorized production administrator session.
- [ ] Invoke the existing Tencent provider test once with the default prompt. Require API result `status=success`, a persisted test image URL, and an updated production `last_test_status=success`.
- [ ] Re-run `--mode verify` and record only the sanitized result and elapsed time; do not record credentials or generated image bytes.

### Task 6: Close Documentation and Rollback Readiness

**Files:**
- Modify: `.sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/tasks.md`
- Modify: `.sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/execution.md`

- [ ] Record source/target databases, backup table names, active provider, endpoint/model, secret-presence flag, provider test result, and whether rollback was required.
- [ ] Confirm temporary local and remote SQL files are removed.
- [ ] Run `git status --short` and verify only intended `00-197`, index, and plan files were added or changed alongside pre-existing user work.
