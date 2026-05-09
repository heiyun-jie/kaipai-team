# AI Profile Card Portfolio Visibility Investigation Tasks

## Phase 1: Runtime API Verification

- [ ] Confirm deployed backend includes `GET /api/ai/profile-card/tasks`.
- [ ] With a fresh authenticated session, call `GET /api/ai/profile-card/tasks` and record only non-sensitive fields: `taskId`, `status`, `shareCardId`, `generatedImageUrl` presence, `failureReason` presence.
- [ ] Call `GET /api/card/my-cards` and record the visible card count and `cardId` values.
- [ ] For each visible `cardId`, call `GET /api/card/config?shareCardId=...` and record whether `highlightedPhotos[0]` is a generated image or an original actor photo.
- [ ] Confirm whether the linked `shareCardId` from the AI task appears in `my-cards`.

## Phase 2: Database Verification

- [ ] Query `actor_ai_profile_card_task` for the affected user.
- [ ] Verify the latest task status and generated image URL.
- [ ] Verify `share_card_id` is set after success.
- [ ] Query `actor_card_config` for the linked `share_card_id`.
- [ ] Verify `highlighted_photo_urls` contains the generated image URL as the first item.
- [ ] Query `user_share_card` and confirm whether the same template card is being reused.

## Phase 3: Frontend Runtime Verification

- [ ] Confirm the mini-program build includes the route `pkg-card/ai-profile-card-detail/index`.
- [ ] Confirm portfolio source includes `isAiGeneratedShare`.
- [ ] Confirm DevTools is running a build after frontend commit `a6a2683`.
- [ ] In DevTools network panel, inspect whether `GET /api/ai/profile-card/tasks` is called when opening `pkg-card/portfolio/index`.
- [ ] Confirm whether the response is empty, failed, or missing generated image fields.

## Phase 4: Product Decision

- [ ] Decide whether AI generated images should increase the `已创建分享` count.
- [ ] If yes, define AI generated images as separate artifacts instead of normal template cards.
- [ ] If no, define how the existing scene card should visually show that it has an AI generated detail page.
- [ ] Decide whether the portfolio should show a separate section named `AI生成分享图`.

## Phase 5: Fix Plan After Investigation

- [ ] If backend task is missing or failed, fix provider/task execution first.
- [ ] If task succeeds but config persistence is missing, fix `saveGeneratedShareCard`.
- [ ] If backend data is correct but frontend classification fails, replace heuristic detection with a first-class artifact API.
- [ ] If runtime is stale, redeploy backend and rebuild/reload mini program before further code changes.
- [ ] Add regression checks for AI task list, portfolio classification, AI detail routing, and share path routing.

## Current Working Hypothesis

The most likely card point is a product/data-model mismatch:

- Existing share cards are keyed by scene template and are reused.
- AI generated images are generation artifacts but are currently stored inside normal card config.
- Therefore the portfolio still shows 3 scene cards, and the AI result is not discoverable as its own portfolio item unless task/config data is correctly surfaced and labeled.

