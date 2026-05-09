# AI Profile Card Generation Tasks

## Phase 1: Backend Task Foundation

- [x] Add `actor_ai_profile_card_task` migration.
- [x] Add task entity, mapper, request/response DTOs.
- [x] Add `AiProfileCardService`.
- [x] Add `POST /api/ai/profile-card/generate`.
- [x] Add `GET /api/ai/profile-card/tasks/{taskId}`.
- [x] Add async executor for generation tasks.

## Phase 2: Prompt Agent And Provider Boundary

- [x] Add `AiProfileCardPromptAgent`.
- [x] Encode fixed subject/safe-area layout rules.
- [x] Add provider interface and registry.
- [x] Retire mock provider from the runtime generation path.
- [x] Add OpenAI provider adapter.
- [x] Add generic HTTP provider adapter for Doubao/bridge usage.
- [x] Add generated image byte storage without changing existing upload flow.

## Phase 3: Existing Share Flow Integration

- [x] On task success, create or reuse a normal user share card.
- [x] Save generated image into `actor_card_config.highlightedPhotoUrls`.
- [x] Keep existing portfolio and preview routes unchanged.
- [x] Confirm manual `创建分享` flow is unaffected.

## Phase 4: Mini Program UI

- [x] Add home page entry `AI生成分享图`.
- [x] Add `pkg-card/ai-profile-card/index.vue`.
- [x] Register page in `pages.json`.
- [x] Add frontend API wrapper.
- [x] Use existing style-card components and style template data.
- [x] Show required generation modal after submit.

## Phase 5: Verification

- [x] Run backend compile/test check.
- [x] Run frontend type check.
- [x] Inspect git status and stage only this feature's files.
- [x] Commit and push backend repo changes.
- [x] Commit and push frontend repo changes.
- [x] Commit and push top-level spec changes.

## Evidence

- Backend compile: `mvn -q -DskipTests compile`
- Frontend type check: `npm run type-check`
- Backend commits pushed: `4ed5ef6`, `64c7f62`, `16acf7a`
- Frontend commits pushed: `f9ad43b`, `3c5ac2d`, `4b80336`
- Spec commits pushed: `4e7a394`, `3589ef1`, `074e143`, `29c9bdf`
- Backend schema release: `20260509-170934-backend-schema-ai-profile-card-generation`
- Backend code release: `20260509-171050-backend-only-ai-profile-card-generation`
- Public route verification: `POST https://api.kplyyk.com/api/ai/profile-card/generate` now returns `401` without login instead of the previous `404`, confirming the online route exists.
- KPLYYK provider follow-up: added provider for `http://kplyyk.com/v0/management/image-generation/test`, image-to-image multipart upload, polling by `task_id`, and fixed 9:16 size `2160x3840`.
- Mini-program UI follow-up: moved the home entry into the existing stats strip action area and aligned `pkg-card/ai-profile-card/index` with the existing card-list page structure.
- No-mock follow-up: runtime default provider is `kplyyk`, `provider-code=mock` is rejected by backend provider resolution, the mock provider class is removed, and portfolio/detail responses hide historical mock/source-image artifacts.
