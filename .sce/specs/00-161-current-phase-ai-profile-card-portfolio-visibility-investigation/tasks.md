# AI Profile Card Portfolio Visibility Investigation Tasks

## Phase 1: Runtime API Verification

- [x] Confirm deployed backend includes `GET /api/ai/profile-card/tasks`.
- [x] With a fresh authenticated session, call `GET /api/ai/profile-card/tasks` and record only non-sensitive fields: `taskId`, `status`, `shareCardId`, `generatedImageUrl` presence, `failureReason` presence.
- [ ] Call `GET /api/card/my-cards` and record the visible card count and `cardId` values.
- [x] For each visible `cardId`, call `GET /api/card/config?shareCardId=...` and record whether `highlightedPhotos[0]` is a generated image or an original actor photo.
- [ ] Confirm whether the linked `shareCardId` from the AI task appears in `my-cards`.

## Phase 2: Database Verification

- [ ] Query `actor_ai_profile_card_task` for the affected user.
- [ ] Verify the latest task status and generated image URL.
- [ ] Verify `share_card_id` is set after success.
- [ ] Query `actor_card_config` for the linked `share_card_id`.
- [ ] Verify `highlighted_photo_urls` contains the generated image URL as the first item.
- [ ] Query `user_share_card` and confirm whether the same template card is being reused.

## Phase 3: Frontend Runtime Verification

- [x] Confirm the mini-program build includes the route `pkg-card/ai-profile-card-detail/index`.
- [x] Confirm portfolio source includes `isAiGeneratedShare`.
- [ ] Confirm DevTools is running a build after frontend commit `a6a2683`.
- [ ] In DevTools network panel, inspect whether `GET /api/ai/profile-card/tasks` is called when opening `pkg-card/portfolio/index`.
- [ ] Confirm whether the response is empty, failed, or missing generated image fields.

## Phase 4: Product Decision

- [x] Decide whether AI generated images should increase the `已创建分享` count.
- [x] If yes, define AI generated images as separate artifacts instead of normal template cards.
- [ ] If no, define how the existing scene card should visually show that it has an AI generated detail page.
- [ ] Decide whether the portfolio should show a separate section named `AI生成分享图`.

## Phase 5: Fix Plan After Investigation

- [x] If backend task is missing or failed, fix provider/task execution first.
- [ ] If task succeeds but config persistence is missing, fix `saveGeneratedShareCard`.
- [x] If backend data is correct but frontend classification fails, replace heuristic detection with a first-class artifact API.
- [x] Add frontend fallback that renders successful AI generation tasks as independent portfolio AI artifacts when the artifact endpoint is empty or stale.
- [x] Persist provider-returned generated image URLs into backend COS storage before exposing them to the mini program.
- [x] Reject mock provider resolution and hide historical mock/source-image artifacts from portfolio/detail reads.
- [x] If runtime is stale, redeploy backend and rebuild/reload mini program before further code changes.
- [x] Add regression checks for AI task list, portfolio classification, AI detail routing, and share path routing.

## Current Working Hypothesis

The most likely card point is a product/data-model mismatch:

- Existing share cards are keyed by scene template and are reused.
- AI generated images are generation artifacts but are currently stored inside normal card config.
- Therefore the portfolio still shows 3 scene cards, and the AI result is not discoverable as its own portfolio item unless task/config data is correctly surfaced and labeled.

## Progress 2026-05-09

- Online unauthenticated `GET https://api.kplyyk.com/api/ai/profile-card/tasks` returns `401`, not `404`, confirming the deployed route exists and requires login.
- Code inspection confirmed `UserShareCardServiceImpl.createCard(...)` reuses the active share card for the same scene template, so `GET /api/card/my-cards` is not expected to increase beyond the three scene cards.
- Source fix added a first-class AI artifact read model backed by `actor_ai_profile_card_task`:
  - Authenticated list: `GET /api/ai/profile-card/artifacts`
  - Public detail: `GET /api/ai/profile-card/artifacts/{artifactId}`
- Frontend portfolio now renders successful AI artifacts as independent entries inside `已创建分享`, so the count becomes manual scene card count plus generated AI artifacts.
- AI detail page share paths now preserve `taskId`, and shared visitors can load the generated image through the public artifact endpoint.

## Progress 2026-05-09 Follow-up

- Runtime symptom reported: frontend still cannot see the AI generated image.
- Additional root-cause risk found in source: provider URL results were stored directly when the image API returned `imageUrl`; WeChat mini program may not render arbitrary external image domains, and this did not satisfy the product requirement that generated images are saved to the backend.
- Backend fix added COS persistence for provider-returned image URLs:
  - New generations download provider image URLs and upload them to the configured COS bucket before `generatedImageUrl` is saved.
  - Existing successful tasks with external `generatedImageUrl` are lazily mirrored to COS when task/artifact data is read, then the task row and linked card config are updated to the COS URL.
  - KPLYYK provider parsing now accepts common `image_url` / `output` response shapes and resolves relative image paths against the configured endpoint before persistence.
- Frontend fix added task-list fallback:
  - `pkg-card/portfolio/index` now creates independent AI artifact rows from successful `GET /api/ai/profile-card/tasks` results when `GET /api/ai/profile-card/artifacts` is empty/stale.
  - If an older task has no `shareCardId`, the portfolio maps it to the matching scene card so the AI detail page can still open.
- Verification:
  - Backend `mvn -q -DskipTests compile` passed.
  - Frontend `npm run type-check` passed.
  - Frontend `npm run build:mp-weixin` passed and synced to `dist/dev/mp-weixin`.
- Deployment:
  - Backend commit `48540b9` was deployed to the runtime jar at `/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar`.
  - Public smoke passed for `/api/card/scene-templates`.
  - Public artifact detail route `/api/ai/profile-card/artifacts/{artifactId}` is reachable without auth; a non-existent artifact now returns business code `400` instead of security `401`.
  - Release evidence was recorded at `.sce/runbooks/backend-admin-release/records/20260509-204642-backend-only-ai-profile-card-image-url-persist.md`.

## Progress 2026-05-09 No-Mock Verification

- Backend runtime was updated to reject the mock provider and default to `kplyyk`.
- Backend commit `982f5e4` was deployed by release batch `20260509-223416-backend-only-ai-profile-card-no-mock-provider`.
- Backend regression tests added in commit `75dbdc4`:
  - provider registry rejects `provider-code=mock`;
  - `AiProfileCardPromptAgent` builds fixed-layout prompt and calls the resolved provider;
  - provider results equal to the source image are rejected.
- Frontend audit script added in commit `46bf5ba`:
  - generation page must call backend `/api/ai/profile-card/generate`;
  - portfolio/detail must read backend task/artifact APIs;
  - generated image must pass provider/source-image validation;
  - mini-program build output must not call `/manage/image-generation`, `/v0/management/image-generation`, or embed a bearer token.
- Local verification passed:
  - backend `mvn -q test`;
  - frontend `npm run type-check`;
  - frontend `npm run build:mp-weixin`;
  - frontend `scripts/audit-ai-profile-card.ps1`;
  - frontend `scripts/audit-mp-package.ps1`;
  - frontend `scripts/audit-api-runtime.ps1`.
- Online protected-flow verification used a newly created test actor session, not a real user token:
  - `POST /api/auth/sendCode` returned business `200`;
  - `POST /api/auth/register` returned business `200`;
  - `PUT /api/actor/profile` returned business `200`;
  - `POST /api/ai/profile-card/generate` returned business `200` and created task `aipf_2dbcda20db654596b0e5e794eda9bd7b`;
  - task readback showed `providerCode=kplyyk`, `modelCode=gpt-image-2`, `generatedImageUrl` absent, and status `failed` because KPLYYK management API key is not configured in backend runtime.
- Earlier production blocker: `AI_PROFILE_CARD_KPLYYK_AUTH_TOKEN` was not present in the backend container or detected Nacos config. With the no-mock contract, that correctly blocked fake generation until the key was supplied through secure runtime config and the backend runtime was redeployed.

## Progress 2026-05-09 Real Provider Runtime Verification

- Runtime config was synced through the backend release runbook and backend-only redeploy `20260509-225212-backend-only-ai-profile-card-kplyyk-auth-runtime`.
- The protected E2E used a newly created test actor session and a synthetic portrait image; no user-provided token was used in evidence.
- Real generation completed without mock fallback:
  - `taskId=aipf_7ece25e97162480fba110639e73a962b`;
  - `status=success`;
  - `providerCode=kplyyk`;
  - `modelCode=gpt-image-2`;
  - `shareCardId=19`;
  - `generatedImageUrl` is present and persisted to `kaipai-1412601014.cos.ap-shanghai.myqcloud.com`;
  - generated image URL is different from the uploaded source image URL.
- Public AI artifact detail verification passed:
  - `GET /api/ai/profile-card/artifacts/aipf_7ece25e97162480fba110639e73a962b` returned business `200`;
  - response includes `status=success`, `providerCode=kplyyk`, `modelCode=gpt-image-2`, `shareCardId=19`, and a non-empty generated image URL.
- Share card config verification passed:
  - `GET /api/card/config?shareCardId=19` returned business `200`;
  - `highlightedPhotos[0]` is the generated COS image;
  - the uploaded source image remains only as a secondary photo.
- Final local verification was rerun after the runtime fix:
  - backend `mvn -q test` passed;
  - frontend `npm run type-check` passed;
  - frontend `npm run build:mp-weixin` passed and synced `dist/dev/mp-weixin`;
  - frontend `scripts/audit-ai-profile-card.ps1` passed;
  - frontend `scripts/audit-mp-package.ps1 -BuildDir dist/build/mp-weixin` passed;
  - frontend `scripts/audit-api-runtime.ps1` passed;
  - built mini-program output has no management image-generation API references or embedded bearer authorization headers.
- Final conclusion: the original card point is resolved by treating AI generated results as first-class AI artifacts. The frontend portfolio/detail reads backend task/artifact APIs, backend generation flows through the prompt agent and real KPLYYK provider, and successful output is persisted before exposure.

## Progress 2026-05-09 Real Person Share Verification

- A public real-person portrait image was used as the source image for a fresh protected E2E run; the user-provided temporary images were not available on disk.
- The protected E2E used a newly created actor test account and did not reuse any user-provided bearer token.
- Real generation completed:
  - `taskId=aipf_965d5818dd2e4caa8ef5523f1783ba6e`;
  - `status=success`;
  - `providerCode=kplyyk`;
  - `modelCode=gpt-image-2`;
  - `shareCardId=20`;
  - uploaded source image is `900x1350`;
  - generated image is `2160x3840`;
  - generated image SHA-256 differs from the uploaded source SHA-256;
  - generated image URL is a backend-managed COS URL.
- Backend visibility verification passed:
  - public artifact detail returned business `200` and the same generated image URL;
  - authenticated artifact list contains the task;
  - `GET /api/card/config?shareCardId=20` returned business `200`;
  - `highlightedPhotos[0]` equals the generated image URL;
  - `highlightedPhotos[1]` equals the uploaded source image URL.
- WeChat DevTools automator verification passed against `dist/dev/mp-weixin`:
  - direct share path `/pkg-card/ai-profile-card-detail/index?shareCardId=20&shared=1&taskId=aipf_965d5818dd2e4caa8ef5523f1783ba6e` opened `pkg-card/ai-profile-card-detail/index`;
  - current page query retained `shareCardId=20`, `shared=1`, and the same `taskId`;
  - page runtime data contained the generated COS image URL and no `AI 分享图加载失败` state;
  - `onShareAppMessage()` returned the AI detail path with the same `taskId`;
  - `onShareAppMessage().imageUrl` equaled the generated COS image URL.

## Progress 2026-05-09 Provided User Session Verification

- A protected E2E was run with the user-provided bearer session. The raw token was not written to specs, temp scripts, or git-tracked files.
- Read-only precheck found the provided account had profile photos and a video resume, but `GET /api/ai/profile-card/artifacts` returned an empty list before the new run. The latest historical AI task for this account was a mock-provider task and was correctly not surfaced as a usable artifact.
- Real generation was triggered through the backend endpoint `POST /api/ai/profile-card/generate` with the account's own profile photo as source:
  - `taskId=aipf_53cd81ac506841799fc98fb496b5b46d`;
  - `status=success` after 116 seconds of polling;
  - `providerCode=kplyyk`;
  - `modelCode=gpt-image-2`;
  - `shareCardId=18`;
  - generated image is persisted to the backend COS bucket, tail `f9f56e0596aa498e9202a9910f2bcbd3.png`;
  - source image tail was `992e5f8600b94dfdb776c36a80be538c.png`;
  - generated image URL differs from the source image URL.
- Backend visibility verification passed:
  - `GET /api/ai/profile-card/artifacts/aipf_53cd81ac506841799fc98fb496b5b46d` returned business `200`;
  - authenticated `GET /api/ai/profile-card/artifacts` returned one artifact and included this task;
  - `GET /api/card/config?shareCardId=18` returned business `200`;
  - `highlightedPhotos[0]` is the generated COS image;
  - `highlightedPhotos[1]` is the source profile photo.
- WeChat DevTools automator verification passed against `dist/dev/mp-weixin`:
  - direct shared path `/pkg-card/ai-profile-card-detail/index?shareCardId=18&shared=1&taskId=aipf_53cd81ac506841799fc98fb496b5b46d` opened `pkg-card/ai-profile-card-detail/index`;
  - current page query retained `shareCardId=18`, `shared=1`, and the same `taskId`;
  - the detail page rendered the generated image tail `f9f56e0596aa498e9202a9910f2bcbd3.png`, not the source image tail;
  - `onShareAppMessage().path` returned the AI detail path with the same `taskId`;
  - `onShareAppMessage().imageUrl` used the generated image tail `f9f56e0596aa498e9202a9910f2bcbd3.png`;
  - timeline share query retained `shareCardId=18` and `taskId=aipf_53cd81ac506841799fc98fb496b5b46d`.
- Portfolio entry verification passed with the same provided user session injected into mini-program storage:
  - `pkg-card/portfolio/index` loaded without the portfolio error state;
  - the first rendered portfolio image was the generated image tail `f9f56e0596aa498e9202a9910f2bcbd3.png`;
  - the generated image appeared before the original source photo in the rendered image list;
  - tapping the portfolio AI share item navigated to `pkg-card/ai-profile-card-detail/index`;
  - the tapped detail page retained `taskId=aipf_53cd81ac506841799fc98fb496b5b46d`, rendered the generated image, and returned the generated image in the share payload.

## Phase 6: Full Profile Share Image Rendering

- [x] Update the prompt agent so `styleCode` is part of the actual model prompt and layout brief.
- [x] Change the prompt contract from portrait-only safe-area generation to a 2160x3840 profile-card background layer with fixed regions.
- [x] Add a backend deterministic renderer that composes final profile facts, sections, thumbnails, contact footer, and QR code onto the AI background.
- [x] Store the composed final PNG as the task `generatedImageUrl`, not the raw AI background.
- [x] Keep raw model output out of portfolio/detail APIs unless a separate debug field is introduced later.
- [x] Add regression tests proving the prompt includes full-card layout coordinates and style code.
- [x] Add regression tests proving the final renderer emits a 2160x3840 image with profile facts.
- [x] Re-run backend tests and frontend audits after implementation.

## Progress 2026-05-10 Full Profile Share Image Rendering

- Backend prompt contract now treats the model output as a background layer for a deterministic full profile card, not as the final share image.
- `styleCode` is now forwarded into `AiProfileCardPromptAgent`, `AiProfileImageGenerationRequest`, and the generic HTTP provider payload.
- Prompt JSON/text now includes fixed 2160x3840 regions for hero, facts, skills, works, more photos, about, stats, and footer.
- Added `AiProfileCardFinalImageRenderer`:
  - downloads the AI background layer;
  - renders real actor profile facts and controlled fallbacks at fixed coordinates;
  - renders skills, works, more photos, intro, stats, contact-entry copy, video-resume status, and QR code;
  - uploads the final composed PNG to COS folder `ai-profile-card-final`.
- `AiProfileCardServiceImpl.runGeneration(...)` now saves the composed final PNG as task `generatedImageUrl`; raw AI background URL is not exposed by artifact/detail APIs.
- Verification passed:
  - backend `mvn -q test`;
  - frontend `npm run type-check`;
  - frontend `scripts/audit-ai-profile-card.ps1`.
- Backend commit `da2bc22` was deployed by backend-only release `20260510-084453-backend-only-ai-profile-card-final-rendering`; public smoke passed against `https://api.kplyyk.com`.
- Post-release protected generation reached the new online backend path and stored `styleCode=costume_actor_profile_full_card`, but the provider call failed before image output:
  - `taskId=aipf_ca848b11853c4e95929144dc2b303347`;
  - `status=failed`;
  - `providerCode=kplyyk`;
  - `modelCode=gpt-image-2`;
  - failure reason from KPLYYK: `401 token_invalidated`.
- Conclusion: final rendering code is deployed, but a fresh KPLYYK provider authentication token is required before a real online image can complete through the new final-card renderer.
