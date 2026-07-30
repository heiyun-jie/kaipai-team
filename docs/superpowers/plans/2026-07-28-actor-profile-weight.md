# Actor Profile Weight Visibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the existing actor weight field directly editable in the personal-profile core section while preserving every unrelated page element and locking the database/API contract.

**Architecture:** Reuse the existing `draft.career.weight -> ActorProfileCareerUpdateDTO.weight -> actor_profile.weight -> ActorProfileRespDTO.weight` path. Move the existing input into the always-visible measurement row, add the existing column to the local schema gate, and add focused contract tests. Do not introduce a second field, a no-op migration, or unrelated profile refactoring.

**Tech Stack:** uni-app 3, Vue 3, TypeScript, Spring Boot, MyBatis-Plus, MySQL 8, JUnit 5, MockMvc.

---

### Task 1: Lock The Narrow Contract

**Files:**
- Create: `.sce/specs/00-204-current-phase-miniapp-actor-profile-weight-visibility/requirements.md`
- Create: `.sce/specs/00-204-current-phase-miniapp-actor-profile-weight-visibility/design.md`
- Create: `.sce/specs/00-204-current-phase-miniapp-actor-profile-weight-visibility/tasks.md`
- Modify: `.sce/specs/README.md`
- Modify: `.sce/specs/spec-code-mapping.md`

- [x] **Step 1: Record the single-field rule**

Specify that UI, request, entity, database, and response all reuse `weight`; prohibit `weight_kg`, `body_weight`, or another column.

- [x] **Step 2: Record the no-other-content rule**

Specify that the existing career editor, all copy, colors, spacing, routes, and unrelated behavior remain unchanged.

### Task 2: Lock The Existing Database Field

**Files:**
- Modify: `.sce/tools/start-kaipai-local-backend.ps1`
- Modify: `.sce/tools/tests/test_start_kaipai_local_backend_schema_gate.py`

- [x] **Step 1: Verify the current schema read-only**

Query `INFORMATION_SCHEMA.COLUMNS` and confirm `actor_profile.weight` is nullable `INT`. Do not print credentials or row data.

- [x] **Step 2: Extend the local schema gate**

Add only `actor_profile.weight` to the required-column list and its focused Python assertion.

- [x] **Step 3: Run the gate tests**

Run:

```powershell
python -m unittest .sce/tools/tests/test_start_kaipai_local_backend_schema_gate.py
```

Expected: all schema-gate tests pass.

### Task 3: Lock The Existing API Contract

**Files:**
- Modify: `kaipaile-server/src/test/java/com/kaipai/controller/api/actor/ActorProfileControllerContractTest.java`
- Modify: `kaipaile-server/src/test/java/com/kaipai/service/actor/impl/ActorProfileWriteServiceImplTest.java`

- [x] **Step 1: Assert request and response fields**

Add `career.weight: 45` to the PUT request, capture the deserialized DTO, and assert the response contains `data.weight: 45`.

- [x] **Step 2: Assert persistence mapping**

In the existing create-profile test, assert the captured `ActorProfile` has `weight == 45`.

- [x] **Step 3: Run focused backend tests**

Run:

```powershell
mvn -q -Dtest=ActorProfileControllerContractTest,ActorProfileWriteServiceImplTest test
```

Expected: all focused tests pass.

### Task 4: Add The Visible Weight Input

**Files:**
- Modify: `kaipai-frontend/src/pages/actor-profile/edit.vue`

- [x] **Step 1: Move the existing weight editor**

Remove only the old expanded-career weight node, add a `profile-edit__measurement` after height, bind it to `draft.career.weight`, and render the `kg` unit. Do not change the style block or any unrelated node.

- [x] **Step 2: Type-check and build**

Run:

```powershell
npm run type-check
npm run build:mp-weixin
```

Expected: both commands exit 0 and postbuild sync completes.

- [x] **Step 3: Verify generated layers**

Confirm the source, `dist/build/mp-weixin/pages/actor-profile/edit.*`, and `dist/dev/mp-weixin/pages/actor-profile/edit.*` each contain the new core measurement binding and `kg` unit.

### Task 5: Complete Repository Verification

**Files:**
- Modify: `.sce/specs/00-204-current-phase-miniapp-actor-profile-weight-visibility/tasks.md`

- [x] **Step 1: Run steering audit**

Run `npm run audit:steering` from `kaipai-frontend`; expect exit 0.

- [x] **Step 2: Run package audit**

Run `npm run audit:mp-package`; record any pre-existing environment URL failure without changing unrelated API configuration.

- [x] **Step 3: Review the exact diff**

Verify no unrelated visible content, styles, DTOs, entities, routes, or database objects changed.
