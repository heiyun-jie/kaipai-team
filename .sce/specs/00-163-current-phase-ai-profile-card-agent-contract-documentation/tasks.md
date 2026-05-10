# AI Profile Card Agent Contract Documentation Tasks

## Phase 1: Spec Creation

- [x] Create this spec to document the next agent-contract pass.
- [x] Capture the product decision that agent output should be structured content and background prompt, not final free-form text painted into the image.
- [x] Define requirements for `posterContent`, `layoutPreset`, prompt contract, privacy, and quality gates.
- [x] Define design guidance for a durable agent contract document.

## Phase 2: Current Evidence Review

- [x] Review current generated evidence:
  - `output/ai-profile-card-e2e/ai-profile-detail-intro-about-slot.png`;
  - `output/ai-profile-card-e2e/ai-profile-detail-style-urban-light-text.png`;
  - `output/ai-profile-card-e2e/ai-profile-detail-style-classic.png`.
- [x] Record the observed limits:
  - classic/costume can work with framed document-style backgrounds;
  - urban currently relies on a dark full-bleed portrait background and needs a dedicated preset or stricter prompt gate;
  - commercial/artistic were not available to the current protected account in the previous pass.
- [x] Confirm current frontend commit baseline:
  - `9ea1ddb fix: verify AI profile styles and intro slot`.
- [x] Confirm current spec baseline:
  - `8c4108c docs: record AI profile multi-style verification`.

## Phase 3: Durable Agent Contract Document

- [x] Create or update the durable documentation file, expected path:

```text
docs/ai-profile-card-agent-contract.md
```

- [x] Add a product decision summary:
  - agent is director/editor;
  - image model generates no-final-text background;
  - deterministic renderer owns factual user content.
- [x] Add agent responsibilities and explicit non-responsibilities.
- [x] Add `posterContent` schema with examples.
- [x] Add `layoutPreset` schema with examples.
- [x] Add style preset matrix for:
  - `costume_profile_v1`;
  - `classic_profile_v1`;
  - `urban_profile_v1`;
  - `commercial_profile_v1`;
  - `artistic_profile_v1`.
- [x] Add provider prompt JSON and negative prompt contract.
- [x] Add privacy/data-minimization rules.
- [x] Add quality gate and regeneration policy placeholder.
- [x] Add E2E acceptance checklist.
- [x] Add migration plan from current implementation.
- [x] Add open decisions for persistence, backend canvas composition, and unavailable styles.

## Phase 4: Backend Follow-Up Planning

- [x] Plan backend agent changes for a later implementation pass:
  - generate structured `posterContent`;
  - select `layoutPreset`;
  - emit prompt JSON based on the preset;
  - keep final readable text out of provider image prompt;
  - persist enough metadata to reconstruct the detail/share rendering.
- [x] Identify model DTO/API additions needed for:
  - `posterContentJson`;
  - `layoutPreset`;
  - `textTheme`;
  - `qualityGateStatus`;
  - `qualityGateReason`.
- [x] Define tests for the prompt/content agent:
  - content fits display limits;
  - intro/work are complete short sentences;
  - contact/private data is excluded;
  - generated styleCode and layoutPreset are compatible.

## Phase 5: Frontend Follow-Up Planning

- [x] Plan frontend detail rendering changes for a later implementation pass:
  - read `layoutPreset` instead of hardcoded global slot CSS;
  - render slots from `posterContent` when available;
  - keep fallback for current artifacts without `posterContent`;
  - keep style-aware text theme;
  - keep composed share image behavior.
- [x] Define frontend tests/audits:
  - every style has a layout preset;
  - every preset has all required slots;
  - text limits are enforced;
  - share image is composed when native text is shown.

## Phase 6: Multi-Style QA Plan

- [x] Define real-provider generation matrix for:
  - costume;
  - urban;
  - classic;
  - commercial;
  - artistic.
- [x] For every available style, capture:
  - task ID;
  - provider code;
  - model code;
  - generated image tail;
  - share card ID;
  - detail screenshot;
  - share payload;
  - slot assertions.
- [x] For unavailable styles, record the blocker:
  - missing template;
  - locked template;
  - provider failure;
  - account capability issue.

## Phase 7: Acceptance Criteria

- [ ] Durable agent contract document exists and is committed.
- [x] Document states that final factual text is deterministic, not image-model-rendered.
- [x] Document includes `posterContent` and `layoutPreset` schemas.
- [x] Document includes style matrix and quality gate.
- [x] Document includes privacy exclusions.
- [x] Document references current known evidence and limitations.
- [x] No business code is changed in this documentation-only pass unless separately requested.

## Current Status

- This spec has been created as the source of truth for the next agent documentation pass.
- Durable document created at `docs/ai-profile-card-agent-contract.md`.
- No implementation code has been changed by this documentation pass.
- Existing dirty/untracked files outside this spec are unrelated and must not be reverted as part of this work.
- Audit completed for this documentation pass:
  - `kaipai-frontend/scripts/audit-ai-profile-card.ps1` passed.
  - `npm run type-check` passed.
  - `npm run build:mp-weixin` passed and synced `dist/dev/mp-weixin`.
- WeChat DevTools real E2E simulation completed for available protected-account styles:
  - `costume`: `shareCardId=17`, `taskId=aipf_fd44377b5b084d9a904a7fdc7784fb32`, screenshot `output/ai-profile-card-e2e/agent-contract-doc-e2e-costume.png`.
  - `urban`: `shareCardId=18`, `taskId=aipf_53cd81ac506841799fc98fb496b5b46d`, screenshot `output/ai-profile-card-e2e/agent-contract-doc-e2e-urban.png`.
  - `classic`: `shareCardId=14`, `taskId=aipf_ec58dd65c32d4f9ca4d2bbd3f3d3c43a`, screenshot `output/ai-profile-card-e2e/agent-contract-doc-e2e-classic.png`.
  - Summary evidence: `output/ai-profile-card-e2e/agent-contract-doc-e2e-summary.json`.
  - All checked available styles passed route, task, background, slot, and composed-share-image assertions.
- `commercial` and `artistic` were not tested in the E2E run because they were unavailable to the current protected account; this is a recorded limitation, not a completed verification.
- The `Durable agent contract document exists and is committed` acceptance item remains unchecked until the document commit exists.
