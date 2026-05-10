# AI Profile Card Agent Contract Documentation Tasks

## Phase 1: Spec Creation

- [x] Create this spec to document the next agent-contract pass.
- [x] Capture the product decision that agent output should be structured content and background prompt, not final free-form text painted into the image.
- [x] Define requirements for `posterContent`, `layoutPreset`, prompt contract, privacy, and quality gates.
- [x] Define design guidance for a durable agent contract document.

## Phase 2: Current Evidence Review

- [ ] Review current generated evidence:
  - `output/ai-profile-card-e2e/ai-profile-detail-intro-about-slot.png`;
  - `output/ai-profile-card-e2e/ai-profile-detail-style-urban-light-text.png`;
  - `output/ai-profile-card-e2e/ai-profile-detail-style-classic.png`.
- [ ] Record the observed limits:
  - classic/costume can work with framed document-style backgrounds;
  - urban currently relies on a dark full-bleed portrait background and needs a dedicated preset or stricter prompt gate;
  - commercial/artistic were not available to the current protected account in the previous pass.
- [ ] Confirm current frontend commit baseline:
  - `9ea1ddb fix: verify AI profile styles and intro slot`.
- [ ] Confirm current spec baseline:
  - `8c4108c docs: record AI profile multi-style verification`.

## Phase 3: Durable Agent Contract Document

- [ ] Create or update the durable documentation file, expected path:

```text
docs/ai-profile-card-agent-contract.md
```

- [ ] Add a product decision summary:
  - agent is director/editor;
  - image model generates no-final-text background;
  - deterministic renderer owns factual user content.
- [ ] Add agent responsibilities and explicit non-responsibilities.
- [ ] Add `posterContent` schema with examples.
- [ ] Add `layoutPreset` schema with examples.
- [ ] Add style preset matrix for:
  - `costume_profile_v1`;
  - `classic_profile_v1`;
  - `urban_profile_v1`;
  - `commercial_profile_v1`;
  - `artistic_profile_v1`.
- [ ] Add provider prompt JSON and negative prompt contract.
- [ ] Add privacy/data-minimization rules.
- [ ] Add quality gate and regeneration policy placeholder.
- [ ] Add E2E acceptance checklist.
- [ ] Add migration plan from current implementation.
- [ ] Add open decisions for persistence, backend canvas composition, and unavailable styles.

## Phase 4: Backend Follow-Up Planning

- [ ] Plan backend agent changes for a later implementation pass:
  - generate structured `posterContent`;
  - select `layoutPreset`;
  - emit prompt JSON based on the preset;
  - keep final readable text out of provider image prompt;
  - persist enough metadata to reconstruct the detail/share rendering.
- [ ] Identify model DTO/API additions needed for:
  - `posterContentJson`;
  - `layoutPreset`;
  - `textTheme`;
  - `qualityGateStatus`;
  - `qualityGateReason`.
- [ ] Define tests for the prompt/content agent:
  - content fits display limits;
  - intro/work are complete short sentences;
  - contact/private data is excluded;
  - generated styleCode and layoutPreset are compatible.

## Phase 5: Frontend Follow-Up Planning

- [ ] Plan frontend detail rendering changes for a later implementation pass:
  - read `layoutPreset` instead of hardcoded global slot CSS;
  - render slots from `posterContent` when available;
  - keep fallback for current artifacts without `posterContent`;
  - keep style-aware text theme;
  - keep composed share image behavior.
- [ ] Define frontend tests/audits:
  - every style has a layout preset;
  - every preset has all required slots;
  - text limits are enforced;
  - share image is composed when native text is shown.

## Phase 6: Multi-Style QA Plan

- [ ] Define real-provider generation matrix for:
  - costume;
  - urban;
  - classic;
  - commercial;
  - artistic.
- [ ] For every available style, capture:
  - task ID;
  - provider code;
  - model code;
  - generated image tail;
  - share card ID;
  - detail screenshot;
  - share payload;
  - slot assertions.
- [ ] For unavailable styles, record the blocker:
  - missing template;
  - locked template;
  - provider failure;
  - account capability issue.

## Phase 7: Acceptance Criteria

- [ ] Durable agent contract document exists and is committed.
- [ ] Document states that final factual text is deterministic, not image-model-rendered.
- [ ] Document includes `posterContent` and `layoutPreset` schemas.
- [ ] Document includes style matrix and quality gate.
- [ ] Document includes privacy exclusions.
- [ ] Document references current known evidence and limitations.
- [ ] No business code is changed in this documentation-only pass unless separately requested.

## Current Status

- This spec has been created as the source of truth for the next agent documentation pass.
- No implementation code has been changed by this spec creation.
- Existing dirty/untracked files outside this spec are unrelated and must not be reverted as part of this work.
