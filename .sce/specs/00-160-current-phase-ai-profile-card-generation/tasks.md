# AI Profile Card Generation Tasks

## Phase 1: Backend Task Foundation

- [ ] Add `actor_ai_profile_card_task` migration.
- [ ] Add task entity, mapper, request/response DTOs.
- [ ] Add `AiProfileCardService`.
- [ ] Add `POST /api/ai/profile-card/generate`.
- [ ] Add `GET /api/ai/profile-card/tasks/{taskId}`.
- [ ] Add async executor for generation tasks.

## Phase 2: Prompt Agent And Provider Boundary

- [ ] Add `AiProfileCardPromptAgent`.
- [ ] Encode fixed subject/safe-area layout rules.
- [ ] Add provider interface and registry.
- [ ] Add mock provider.
- [ ] Add OpenAI provider adapter.
- [ ] Add generic HTTP provider adapter for Doubao/bridge usage.
- [ ] Add generated image byte storage without changing existing upload flow.

## Phase 3: Existing Share Flow Integration

- [ ] On task success, create or reuse a normal user share card.
- [ ] Save generated image into `actor_card_config.highlightedPhotoUrls`.
- [ ] Keep existing portfolio and preview routes unchanged.
- [ ] Confirm manual `创建分享` flow is unaffected.

## Phase 4: Mini Program UI

- [ ] Add home page entry `AI生成分享图`.
- [ ] Add `pkg-card/ai-profile-card/index.vue`.
- [ ] Register page in `pages.json`.
- [ ] Add frontend API wrapper.
- [ ] Use existing style-card components and style template data.
- [ ] Show required generation modal after submit.

## Phase 5: Verification

- [ ] Run backend compile/test check.
- [ ] Run frontend type check.
- [ ] Inspect git status and stage only this feature's files.
- [ ] Commit and push backend repo changes.
- [ ] Commit and push frontend repo changes.
- [ ] Commit and push top-level spec changes.
