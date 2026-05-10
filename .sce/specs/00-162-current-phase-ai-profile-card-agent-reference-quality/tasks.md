# AI Profile Card Agent Reference Quality Tasks

## Phase 1: Preserve Current Work

- [x] Preserve the current in-progress backend agent changes; do not revert them.
- [x] Create this spec as the source of truth for the next implementation pass.
- [ ] Review current backend diff before further edits.
- [ ] Fix the current Java compile blocker caused by `Map.of(...)` having more than ten key/value pairs.

## Phase 2: Prompt Agent Structure

- [ ] Refactor `AiProfileCardPromptAgent` so the fixed-layout map can safely contain all required regions.
- [ ] Keep `promptJson` deterministic and readable by using ordered structures.
- [ ] Add or keep `referenceQuality` in the prompt JSON.
- [ ] Add or keep `moduleAesthetics` in the prompt JSON.
- [ ] Ensure `styleCode` is present in both provider request and prompt content.
- [ ] Keep `templateSceneCode` behavior compatible with existing frontend and backend APIs.

## Phase 3: Reference-Quality Costume Style

- [ ] Strengthen `costume_actor_profile_full_card` style direction around the provided reference image:
  - warm ivory parchment/rice paper;
  - ink-wash Jiangnan mountains, bridge, pavilion, bamboo;
  - right-side realistic period actor portrait;
  - antique-gold double-line border and corner ornaments;
  - abstract cinnabar seal accents without readable characters;
  - empty profile/skills/works/about/stats modules;
  - six portrait-thumbnail slots.
- [ ] Avoid fantasy over-styling, anime faces, modern gradients, and dense decoration.
- [ ] Preserve actor identity and source-image face consistency.

## Phase 4: Native Text Safety

- [ ] Ensure prompt text clearly says every final text-bearing area is blank for native mini-program rendering.
- [ ] Expand the negative prompt to reject readable Chinese, random calligraphy, filled profile text, numbers, phone, QR, logos, fake UI labels, and watermarks.
- [ ] Allow only abstract seal/ornament shapes that cannot be read as text.
- [ ] Confirm no final contact information is sent as a renderable image-text instruction.

## Phase 5: Tests

- [ ] Update `AiProfileCardPromptAgentTest` to assert:
  - target size `2160x3840`;
  - selected `styleCode`;
  - `referenceQuality`;
  - `profilePanelRegion`, `skillsRegion`, `worksRegion`, `photoStripRegion`, `aboutRegion`, `statsRegion`, and `footerRegion`;
  - high-quality Chinese period actor profile sheet language;
  - antique-gold border language;
  - portrait thumbnail strip language;
  - negative prompt entries for random readable calligraphy and filled profile text.
- [ ] Run targeted test:

```powershell
mvn -q -Dtest=AiProfileCardPromptAgentTest test
```

- [ ] Run backend regression:

```powershell
mvn -q test
```

## Phase 6: Real Provider Verification

- [ ] After KPLYYK provider authentication is valid, trigger a fresh protected generation with:
  - `templateSceneCode=costume`;
  - `styleCode=costume_actor_profile_full_card`;
  - a real actor source image.
- [ ] Confirm backend task reaches real provider, not mock.
- [ ] Confirm successful artifact:
  - provider code is `kplyyk`;
  - model code is `gpt-image-2` or configured provider model;
  - generated image is different from source image;
  - generated image is stored in backend COS;
  - share card/artifact IDs are persisted.
- [ ] If provider returns `401 token_invalidated`, record that as an external credential blocker and keep fail-closed behavior.

## Phase 7: Mini-Program Detail Verification

- [ ] Rebuild the mini-program:

```powershell
npm run build:mp-weixin
```

- [ ] Clear WeChat DevTools compile cache before judging screenshots.
- [ ] Open AI detail path with `shareCardId` and `taskId`.
- [ ] Verify:
  - AI visual asset renders;
  - actor name/facts/skills/works/photos/intro/stats/video resume render natively;
  - no URL or model-generated readable text appears in native text slots;
  - share path points to `pkg-card/ai-profile-card-detail/index`;
  - share image uses the generated AI artifact.

## Phase 8: Documentation and Release

- [ ] Record prompt-agent change summary in this spec.
- [ ] Commit backend code only after tests pass.
- [ ] Push backend branch after successful commit.
- [ ] If backend deployment is required, run the existing backend-only release process and record the release ID.

## Known Starting Issue

The preserved in-progress backend change currently does not compile because Java `Map.of(...)` was expanded past the method overload limit. Do not treat this as a reason to revert; fix it in the next implementation pass by using `LinkedHashMap` or `Map.ofEntries`.

