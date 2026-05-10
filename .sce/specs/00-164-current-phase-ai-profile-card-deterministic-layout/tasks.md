# AI Profile Card Deterministic Layout Tasks

## Phase 1: Spec Creation

- [x] Create this spec for the AI profile card positioning mismatch.
- [x] Record the root cause: AI-generated frames and frontend fixed overlays use different layout sources of truth.
- [x] Lock the implementation direction: AI background-only image plus deterministic layout rendering.
- [x] Define requirements for `layoutPreset`, `posterContent`, persistence, frontend rendering, share composition, and E2E.

## Phase 2: Current Code Evidence Review

- [x] Confirm frontend detail page currently uses generated image as background:
  - `kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue`;
  - `image.ai-share-detail-page__poster-bg`;
  - `mode="scaleToFill"`.
- [x] Confirm frontend detail page currently overlays sections with v1 hardcoded slots:
  - identity;
  - facts;
  - skills;
  - works;
  - photo strip;
  - intro;
  - video.
- [x] Confirm current frontend audit still checks v1 fixed percentages:
  - `kaipai-frontend/scripts/audit-ai-profile-card.ps1`;
  - intro `top: 80.7%`;
  - works `top: 60.1%`.
- [x] Confirm backend prompt currently asks the provider for visible fixed layout regions:
  - `kaipaile-server/src/main/java/com/kaipai/module/server/ai/profilecard/AiProfileCardPromptAgent.java`.
- [x] Confirm current database table lacks v2 deterministic metadata:
  - `kaipaile-server/src/main/resources/db/migration/V20260509_033__ai_profile_card_generation.sql`;
  - no `poster_content_json`;
  - no `layout_preset_json`;
  - no `background_image_url`;
  - no `final_share_image_url`.

## Phase 3: Backend V2 Metadata and Agent

- [ ] Add database migration for v2 metadata fields.
- [ ] Extend `ActorAiProfileCardTask` with v2 fields.
- [ ] Extend backend task/artifact DTOs with v2 fields.
- [ ] Add backend layout preset model/registry.
- [ ] Add `posterContent` builder from `ActorProfileDTO`.
- [ ] Add text limit enforcement for facts, skills, works, intro, photos, and video.
- [ ] Change `AiProfileCardPromptAgent` to emit background-only prompt for v2 artifacts.
- [ ] Stop asking provider to draw exact lower business frames for v2.
- [ ] Persist `backgroundImageUrl` separately from legacy `generatedImageUrl`.
- [ ] Persist `posterContentJson`, `layoutPreset`, `layoutPresetJson`, `textTheme`, `renderMode`, and quality gate fields.
- [ ] Keep v1 compatibility for old tasks/artifacts.
- [ ] Add backend unit tests for prompt contract, poster content limits, style/preset compatibility, and no private data leakage.

## Phase 4: Frontend V2 Detail Rendering

- [ ] Extend frontend AI profile card types with v2 metadata.
- [ ] Add frontend layout preset registry and coordinate conversion helpers.
- [ ] Add deterministic v2 render mode in `pkg-card/ai-profile-card-detail/index`.
- [ ] Render AI image as background only for v2.
- [ ] Render panels, section titles, facts, skills, works, photos, intro, and video from `posterContent`.
- [ ] Ensure intro always uses intro slot and works always uses works slot.
- [ ] Ensure bottom action bar does not affect poster coordinate mapping.
- [ ] Remove dependency on AI-generated lower frames for v2 red-box content.
- [ ] Keep v1 fallback for old artifacts without v2 metadata.
- [ ] Update frontend audit to reject v2 implementation that relies only on global fixed CSS percentages.

## Phase 5: Share Image Composition

- [ ] Update share preparation to use v2 deterministic renderer when v2 metadata exists.
- [ ] Compose share image from `backgroundImageUrl + layoutPreset + posterContent`.
- [ ] Prefer `finalShareImageUrl` when backend provides it.
- [ ] Ensure share image is not raw AI background when deterministic text is rendered on detail page.
- [ ] Keep legacy share behavior for v1 artifacts.

## Phase 6: Portfolio and Navigation Regression

- [ ] Verify portfolio still lists backend AI artifacts only.
- [ ] Verify portfolio AI artifact click enters `pkg-card/ai-profile-card-detail/index`.
- [ ] Verify non-AI portfolio items still use their existing routes.
- [ ] Verify generated v2 artifact can be shared and reopened by another viewer.

## Phase 7: Automated Verification

- [ ] Backend tests pass for AI profile card service/agent/provider registry.
- [ ] Frontend `npm run type-check` passes.
- [ ] Frontend `npm run build:mp-weixin` passes.
- [ ] `scripts/audit-ai-profile-card.ps1` is updated and passes.
- [ ] Add or update an audit that checks all v2 styles have required slots.
- [ ] Add or update an audit that checks v2 share image is composed from deterministic content.

## Phase 8: 真人 E2E Simulation

- [ ] Run WeChat DevTools with the current protected-account authorization context.
- [ ] Generate or open a real v2 AI artifact.
- [ ] Verify portfolio shows the AI artifact.
- [ ] Verify clicking portfolio AI artifact opens AI detail page.
- [ ] Verify visible background is the AI-generated background.
- [ ] Verify red-box lower area content aligns with deterministic panels:
  - works;
  - photos;
  - intro;
  - video.
- [ ] Verify share page path remains the AI detail route.
- [ ] Verify share image is composed final image, not raw AI background.
- [ ] Repeat for all available styles.
- [ ] Record unavailable styles as blockers instead of passed.

## Phase 9: Acceptance Criteria

- [ ] New v2 AI profile card artifacts render without depending on AI-generated business frames.
- [ ] New v2 detail page uses `layoutPreset` as the source of truth for section positions.
- [ ] New v2 share image uses the same layout contract as the detail page.
- [ ] The screenshot red-box class of mismatch is resolved in真人 E2E evidence.
- [ ] Existing v1 AI artifacts remain viewable.
- [ ] No mock success path is introduced.
- [ ] All touched code is committed and pushed.
- [ ] Specs are updated only after each item is actually completed.

## Current Status

- Spec created to lock the implementation target.
- Current code evidence review completed from source files.
- No backend or frontend business implementation has been changed by this spec creation step.
- Existing dirty/untracked files outside this spec are unrelated and must not be reverted.
- Implementation, audit updates, and真人 E2E are not complete yet.
