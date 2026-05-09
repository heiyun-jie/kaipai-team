# AI Profile Card Portfolio Visibility Investigation Design

## Diagnostic Model

The current flow has four persistence/discovery layers:

1. **Task layer**
   - Table: `actor_ai_profile_card_task`
   - API: `POST /api/ai/profile-card/generate`
   - API: `GET /api/ai/profile-card/tasks`
   - Expected state: task status is `success`, `generatedImageUrl` is present, and `shareCardId` is present.

2. **Share-card layer**
   - Table: `user_share_card`
   - API: `GET /api/card/my-cards`
   - Current behavior: one active card per scene template is reused.
   - Consequence: AI generation does not necessarily create a fourth portfolio card.

3. **Card-config layer**
   - Table: `actor_card_config`
   - API: `GET /api/card/config?shareCardId=...`
   - Expected state: `highlightedPhotos[0]` points to the generated AI image for the linked share card.

4. **Portfolio UI layer**
   - Page: `pkg-card/portfolio/index`
   - Expected behavior: if a share card is linked to a successful AI task, card click routes to `pkg-card/ai-profile-card-detail/index`.
   - Fallback behavior: if the cover image is not one of the actor's source photos, treat it as generated.

## Highest-Probability Blocking Points

### Blocker A: The data model hides AI results inside the existing 3 cards

`UserShareCardServiceImpl.createCard(...)` returns an existing active share card for the same template. This explains why the portfolio count remains `3`.

This may be acceptable only if the product wants AI generation to replace a scene card cover. It is not acceptable if the product expects a discoverable AI-generated artifact in addition to normal scene cards.

### Blocker B: Online backend may not include the task-list endpoint

The frontend depends on `GET /api/ai/profile-card/tasks` for reliable AI classification. If the online backend has not been deployed with the latest backend commit, the request can fail silently and portfolio falls back to image heuristics.

### Blocker C: Generated image may not be written to card config

If the task succeeds but `actor_card_config.highlightedPhotoUrls` is unchanged or still contains the source portrait, the portfolio will keep showing the original portrait image.

### Blocker D: Frontend build/runtime may be stale

If WeChat DevTools or the test device is running an older `dist/dev/mp-weixin` package, the AI detail route and classification logic will not be active even though the source branch is pushed.

## Recommended Product Contract

The current `user_share_card` list is scene-template based. AI-generated share images are generation artifacts. They should have a first-class read model.

Recommended backend response model:

```json
{
  "artifactId": "aipf_xxx",
  "taskId": "aipf_xxx",
  "shareCardId": 123,
  "templateSceneCode": "urban",
  "styleCode": "urban",
  "generatedImageUrl": "https://...",
  "sourceImageUrl": "https://...",
  "status": "success",
  "createdAt": "2026-05-09T20:00:00"
}
```

Recommended API:

- `GET /api/ai/profile-card/artifacts`
- `GET /api/ai/profile-card/artifacts/{artifactId}`

The portfolio can then render a separate `AI生成分享图` section or add an explicit artifact row under `已创建分享` without guessing from card config photos.

## Verification Strategy

1. Use authenticated API calls only in local terminal or secure runtime. Do not persist bearer tokens.
2. Compare three API surfaces for the same user:
   - `/api/ai/profile-card/tasks`
   - `/api/card/my-cards`
   - `/api/card/config?shareCardId=...`
3. Confirm whether the generated image URL is stable and reachable.
4. Confirm whether the mini-program source and WeChat runtime include the latest frontend commits.
5. Decide whether the final implementation should keep the current heuristic or replace it with first-class artifact APIs.

