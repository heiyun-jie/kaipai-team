# AI Profile Card Agent Reference Quality Tasks

## Phase 1: Preserve Current Work

- [x] Preserve the current in-progress backend agent changes; do not revert them.
- [x] Create this spec as the source of truth for the next implementation pass.
- [x] Review current backend diff before further edits.
- [x] Fix the current Java compile blocker caused by `Map.of(...)` having more than ten key/value pairs.

## Phase 2: Prompt Agent Structure

- [x] Refactor `AiProfileCardPromptAgent` so the fixed-layout map can safely contain all required regions.
- [x] Keep `promptJson` deterministic and readable by using ordered structures.
- [x] Add or keep `referenceQuality` in the prompt JSON.
- [x] Add or keep `moduleAesthetics` in the prompt JSON.
- [x] Ensure `styleCode` is present in both provider request and prompt content.
- [x] Keep `templateSceneCode` behavior compatible with existing frontend and backend APIs.

## Phase 3: Reference-Quality Costume Style

- [x] Strengthen `costume_actor_profile_full_card` style direction around the provided reference image:
  - warm ivory parchment/rice paper;
  - ink-wash Jiangnan mountains, bridge, pavilion, bamboo;
  - right-side realistic period actor portrait;
  - antique-gold double-line border and corner ornaments;
  - abstract cinnabar seal accents without readable characters;
  - empty profile/skills/works/about/stats modules;
  - six portrait-thumbnail slots.
- [x] Avoid fantasy over-styling, anime faces, modern gradients, and dense decoration.
- [x] Preserve actor identity and source-image face consistency.

## Phase 4: Native Text Safety

- [x] Ensure prompt text clearly says every final text-bearing area is blank for native mini-program rendering.
- [x] Expand the negative prompt to reject readable Chinese, random calligraphy, filled profile text, numbers, phone, QR, logos, fake UI labels, and watermarks.
- [x] Allow only abstract seal/ornament shapes that cannot be read as text.
- [x] Confirm no final contact information is sent as a renderable image-text instruction.

## Phase 5: Tests

- [x] Update `AiProfileCardPromptAgentTest` to assert:
  - target size `2160x3840`;
  - selected `styleCode`;
  - `referenceQuality`;
  - `profilePanelRegion`, `skillsRegion`, `worksRegion`, `photoStripRegion`, `aboutRegion`, `statsRegion`, and `footerRegion`;
  - high-quality Chinese period actor profile sheet language;
  - antique-gold border language;
  - portrait thumbnail strip language;
  - negative prompt entries for random readable calligraphy and filled profile text.
- [x] Run targeted test:

```powershell
mvn -q -Dtest=AiProfileCardPromptAgentTest test
```

- [x] Run backend regression:

```powershell
mvn -q test
```

## Phase 6: Real Provider Verification

- [x] After KPLYYK provider authentication is valid, trigger a fresh protected generation with:
  - `templateSceneCode=costume`;
  - `styleCode=costume_actor_profile_full_card`;
  - a real actor source image.
- [x] Confirm backend task reaches real provider, not mock.
- [x] Confirm successful artifact:
  - provider code is `kplyyk`;
  - model code is `gpt-image-2` or configured provider model;
  - generated image is different from source image;
  - generated image is stored in backend COS;
  - share card/artifact IDs are persisted.
- [x] If provider returns `401 token_invalidated`, record that as an external credential blocker and keep fail-closed behavior.

## Phase 7: Mini-Program Detail Verification

- [x] Rebuild the mini-program:

```powershell
npm run build:mp-weixin
```

- [x] Clear WeChat DevTools compile cache before judging screenshots.
- [x] Open AI detail path with `shareCardId` and `taskId` for an existing successful artifact.
- [x] Verify:
  - AI visual asset renders;
  - actor name/facts/skills/works/photos/intro/stats/video resume render natively;
  - no URL or model-generated readable text appears in native text slots;
  - share path points to `pkg-card/ai-profile-card-detail/index`;
  - share image uses the generated AI artifact.

## Phase 8: Documentation and Release

- [x] Record prompt-agent change summary in this spec.
- [x] Commit backend code only after tests pass.
- [x] Push backend branch after successful commit.
- [x] If backend deployment is required, run the existing backend-only release process and record the release ID.

## Known Starting Issue

The preserved in-progress backend change currently does not compile because Java `Map.of(...)` was expanded past the method overload limit. Do not treat this as a reason to revert; fix it in the next implementation pass by using `LinkedHashMap` or `Map.ofEntries`.

## Progress 2026-05-10 Reference Quality Agent Pass

- Backend prompt-agent implementation was completed from the preserved in-progress version:
  - fixed the Java compile blocker by replacing the oversized `Map.of(...)` layout declaration with an ordered `LinkedHashMap`;
  - kept `referenceQuality`, `moduleAesthetics`, fixed safe regions, and strengthened negative prompt clauses;
  - locked regression assertions for reference-quality wording, `profilePanelRegion`, `statsRegion`, photo strip slots, random readable calligraphy, and filled profile text.
- Verification passed locally in `kaipaile-server`:
  - `mvn -q -Dtest=AiProfileCardPromptAgentTest test`;
  - `mvn -q test`.
- Backend commit pushed:
  - `57a91ba feat: refine AI profile card reference prompt`.
- Backend-only release completed:
  - release id `20260510-102739-backend-only-ai-profile-card-reference-quality-agent`;
  - record `.sce/runbooks/backend-admin-release/records/20260510-102739-backend-only-ai-profile-card-reference-quality-agent.md`;
  - public smoke passed against `https://api.kplyyk.com`.
- Fresh protected real-user generation was attempted after release:
  - `taskId=aipf_00ee0c0ec3b84fd1b48e7fc064bb79f7`;
  - request reached backend/provider with `templateSceneCode=costume`, `styleCode=costume_actor_profile_full_card`, `providerCode=kplyyk`, and `modelCode=gpt-image-2`;
  - task ended `status=failed`;
  - KPLYYK returned `401 token_invalidated`;
  - no generated image was produced, and no mock/source-image artifact was exposed.
- Existing successful artifact detail E2E was rerun to guard the display/share path:
  - path `/pkg-card/ai-profile-card-detail/index?shareCardId=18&shared=1&taskId=aipf_53cd81ac506841799fc98fb496b5b46d`;
  - page opened `pkg-card/ai-profile-card-detail/index`;
  - generated image tail `f9f56e0596aa498e9202a9910f2bcbd3.png` rendered;
  - native name rendered `林夏`;
  - sections included skills, works, photos, intro, and video resume;
  - share path and timeline query retained the AI task id;
  - screenshot evidence `output/ai-profile-card-e2e/post-agent-release-existing-artifact.png`.
- Current quality conclusion:
  - prompt-agent quality has been upgraded and regression-tested against the reference-image structure;
  - real end-to-end generation quality cannot be certified until KPLYYK provider authentication is refreshed, because the provider rejects the request before image output;
  - after provider auth is fixed, the next required step is a fresh generation and manual/automated image-quality review against the reference.

## Progress 2026-05-10 Real Provider Success and Background Detail Pass

- After the provider credential was refreshed, a fresh protected real-user generation succeeded:
  - `taskId=aipf_fd44377b5b084d9a904a7fdc7784fb32`;
  - `status=success`;
  - `providerCode=kplyyk`;
  - `modelCode=gpt-image-2`;
  - `styleCode=costume_actor_profile_full_card`;
  - `shareCardId=17`;
  - generated image tail `c76411969de24f9984927cd2fe84e387.png`;
  - source image tail `e5d9a10d87954527bb554337ac2f286b.png`.
- Generated image verification:
  - downloaded to `output/ai-profile-card-e2e/real-provider-reference-agent-generated-17.png`;
  - size is `2160x3840`;
  - output is not the source-image echo;
  - visual review confirms warm parchment/rice-paper texture, Jiangnan ink-wash bridge/pavilion/bamboo, antique-gold border, right-side period actor portrait, blank native-text regions, and six portrait-thumbnail slots.
- API readback passed:
  - `GET /api/ai/profile-card/tasks/aipf_fd44377b5b084d9a904a7fdc7784fb32` returned success with provider/model/style/share card fields;
  - `GET /api/ai/profile-card/artifacts` included the task artifact;
  - `GET /api/card/my-cards` included `shareCardId=17`;
  - `GET /api/card/config?shareCardId=17` used the generated image as the first highlighted photo;
  - `GET /api/card/personalization?shareCardId=17` returned the actor snapshot, photos, and one video resume.
- Frontend detail rendering was adjusted to match the desired behavior:
  - generated image is now rendered as a full-page fixed background layer in `pkg-card/ai-profile-card-detail/index`;
  - the previous duplicate generated image inside the visual card was removed;
  - native profile/contact/share/video content remains over the generated background;
  - clicking the visual profile region still previews the generated image.
- Frontend verification passed in `kaipai-frontend`:
  - `npm run type-check`;
  - `npm run build:mp-weixin`;
  - `scripts/audit-ai-profile-card.ps1`;
  - WeChat DevTools automator route/share readback for `shareCardId=17` confirmed:
    - actual route `pkg-card/ai-profile-card-detail/index`;
    - query retained `shareCardId=17`, `shared=1`, and the task id;
    - page data contained generated image tail and actor name;
    - `onShareAppMessage().path` returned the AI detail page path with the task id;
    - `onShareAppMessage().imageUrl` used generated image tail `c76411969de24f9984927cd2fe84e387.png`;
    - timeline query retained the same share card id and task id.
- Frontend commit pushed:
  - `2c8ebf3 feat: use AI profile image as detail background`.

## Progress 2026-05-10 Mini-Program Slot-Fill Detail Pass

- User clarified the mini-program must fill information inside the template's red-box/blank regions, not render separate content cards below the generated image.
- Frontend detail rendering was updated in `kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue`:
  - the AI-generated `2160x3840` image now renders as a full-width `750rpx x 1334rpx` page template with `scaleToFill`;
  - native mini-program components are absolutely positioned into the fixed template slots for identity, basic facts, skills, intro, six photos, representative work, and video resume;
  - the return button is an overlay so the generated template starts at the top of the page;
  - long identity/intro/work copy is trimmed to avoid half-line clipping inside fixed template boxes;
  - the fixed bottom action bar keeps page share and contact application controls outside the template artwork.
- Frontend verification passed:
  - `npm run type-check`;
  - `npm run build:mp-weixin`;
  - `scripts/audit-ai-profile-card.ps1`.
- WeChat DevTools real artifact E2E was run after restarting the automation project to clear stale compiled code:
  - path `/pkg-card/ai-profile-card-detail/index?shareCardId=17&shared=1&taskId=aipf_fd44377b5b084d9a904a7fdc7784fb32`;
  - route resolved to `pkg-card/ai-profile-card-detail/index`;
  - generated background image tail matched `c76411969de24f9984927cd2fe84e387.png`;
  - native slot text rendered actor `林夏`, basic facts, skills, intro, representative work, and video resume;
  - six photo slot container rendered;
  - `onShareAppMessage().path` retained the AI detail page with `shareCardId=17` and task id;
  - `onShareAppMessage().imageUrl` used generated image tail `c76411969de24f9984927cd2fe84e387.png`;
  - screenshot evidence `output/ai-profile-card-e2e/real-provider-reference-agent-detail-slot-17-final-v3.png`;
  - machine-readable evidence `output/ai-profile-card-e2e/real-provider-reference-agent-detail-slot-17-final-v3.json`.
- Frontend commit pushed:
  - `2a88413 feat: align AI detail content to generated template slots`.

## Progress 2026-05-10 Readability and Share Preview Repair

- User reported three production-quality issues from real screenshots:
  - native detail text was clipped or visually blurry in fixed template slots;
  - some generated backgrounds lacked clear blank module frames, especially non-parchment/dark styles;
  - WeChat share cards used the raw AI background image, so native page text did not appear in the share preview.
- Frontend detail page was repaired:
  - native translucent slot panels are now drawn over the AI background, so information remains readable even when the generated image omits module frames;
  - text shadows were removed from slot text to reduce blur;
  - intro and work copy now use compact complete sentences instead of long clipped paragraphs;
  - identity slot was moved below the floating back button and enlarged so the selling point is not cut off;
  - page share now pre-composes a `1000x800` canvas cover and uses the resulting temp JPG as `onShareAppMessage().imageUrl`, preventing raw-AI-image share previews.
- Backend prompt-agent was strengthened:
  - added `layoutCompliance` requiring visible blank frames in every style;
  - changed fixed layout regions from soft `should` wording to mandatory visible empty bordered cards;
  - added negative prompt guards for unframed information regions, plain full-bleed portrait backgrounds, and full-bleed photos covering modules.
- Verification passed:
  - frontend `npm run type-check`;
  - frontend `npm run build:mp-weixin`;
  - frontend `scripts/audit-ai-profile-card.ps1`;
  - backend `mvn -q -Dtest=AiProfileCardPromptAgentTest test`;
  - backend `mvn -q test`;
  - WeChat DevTools E2E for `shareCardId=17` confirmed:
    - AI background tail `c76411969de24f9984927cd2fe84e387.png`;
    - detail slots render complete native identity/intro/work sentences;
    - share path stays on `pkg-card/ai-profile-card-detail/index`;
    - share image is a generated temp JPG, not the raw AI background URL.
- Evidence:
  - screenshot `output/ai-profile-card-e2e/ai-profile-detail-readable-panels-final.png`;
  - JSON `output/ai-profile-card-e2e/ai-profile-detail-readable-panels-final.json`.

## Progress 2026-05-10 No-Overlay Template Fill Correction

- User clarified the visible slot backgrounds added in the previous readability pass were not desired for the framed parchment template:
  - the AI-generated image must remain the visible background/template;
  - mini-program native content should be filled into the template's existing blank frames;
  - no extra translucent/native panel backgrounds should appear over those frames;
  - slot content should sit closer to the top of each generated frame.
- Frontend detail slot styling was corrected in `kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue`:
  - removed native padding, border, border radius, and translucent backgrounds from all AI detail poster text blocks;
  - removed native background/border from the six photo slots;
  - realigned identity, facts, skills, intro, photo strip, works, and video regions to the framed areas in the generated image;
  - preserved the canvas-composited share preview behavior, so WeChat share cards still include native rendered information instead of using the raw AI background alone.
- Verification passed in `kaipai-frontend`:
  - `npm run type-check`;
  - `npm run build:mp-weixin`;
  - `scripts/audit-ai-profile-card.ps1`;
  - WeChat DevTools E2E for `/pkg-card/ai-profile-card-detail/index?shareCardId=17&shared=1&taskId=aipf_fd44377b5b084d9a904a7fdc7784fb32`.
- E2E assertions confirmed:
  - generated background tail `c76411969de24f9984927cd2fe84e387.png`;
  - poster information blocks have transparent background, zero border, and zero top padding;
  - photo slot background is transparent;
  - `onShareAppMessage().imageUrl` is a composed temp JPG, not the raw AI image URL.
- Evidence:
  - screenshot `output/ai-profile-card-e2e/ai-profile-detail-no-overlay-final-v2.png`;
  - JSON `output/ai-profile-card-e2e/ai-profile-detail-no-overlay-final-v2.json`.
- Frontend commit pushed:
  - `72e822c fix: align AI detail slots without overlay panels`.
