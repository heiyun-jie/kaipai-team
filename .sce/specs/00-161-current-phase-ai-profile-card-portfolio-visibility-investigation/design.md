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

## Mini Program Component Detail Page Design

The reference document `wechat-miniapp-actor-detail-agent-spec.md` establishes the default output mode as `miniapp-components`.

The AI profile card pipeline is split into two layers:

1. **AI visual layer**
   - Produced by the prompt agent and image provider.
   - Contains actor portrait, wardrobe, atmosphere, scenic background, paper texture, and clean visual areas.
   - Must not contain final readable Chinese text, English letters, phone numbers, QR codes, logos, or UI labels.
   - Uses fixed 2160x3840 layout instructions so the actor is placed in the hero area and component-rendered text regions stay readable.

2. **Mini-program native detail page**
   - Produced by `pkg-card/ai-profile-card-detail/index`.
   - Uses the AI visual layer as a hero/cover image.
   - Renders all profile facts, skills, works, photo thumbnails, intro, video resume, contact request and share actions as native components.
   - Keeps text accurate and interactive; contact and QR-like navigation must not be model-generated.

### Visual Asset Guidance Regions

The prompt agent gives the image provider these 2160x3840 regions:

- Hero visual: `x=0,y=0,w=2160,h=1380`
- Hero title and fact block: `x=120,y=150,w=1020,h=1110`
- Actor subject guidance for model: `x=1120,y=120,w=980,h=1320`
- Skills section: `x=120,y=1450,w=850,h=760`
- Works section: `x=1080,y=1450,w=930,h=760`
- More photos: `x=120,y=2340,w=1920,h=360`
- About section: `x=120,y=2860,w=1920,h=360`
- Stats strip: `x=120,y=3220,w=1920,h=220`
- Contact footer: `x=0,y=3540,w=2160,h=300`

These regions are intentionally owned by prompt/page contract so model/provider changes cannot cover areas where the mini program renders facts.

### Data Mapping

- Backend prompt/profile signals:
  - `gender`, `age`, `height`, `weight`, `city`, `bodyType`, `hairStyle`, `skillTypes`, work summaries and photo group counts guide visual mood only.
- Mini-program page facts:
  - `ActorProfile.name` -> hero name.
  - `height`, `weight`, `city`, `bodyType`, `hairStyle` -> facts card.
  - `skillTypes` -> skills section.
  - `workExperiences` -> works section, using project name, role, shoot date/year, description, and first work photo when present.
  - `photos`, photo categories, avatar, and work photos -> more photos.
  - `intro` -> about section.
  - `videoUrl` -> video resume section.
  - contact request state -> bottom action bar.

### Failure Behavior

- If AI generation succeeds, the visual asset is stored as the task `generatedImageUrl` and the page renders facts from the share-card actor snapshot.
- If optional profile images are missing, the mini-program hides or skips those thumbnails.
- If optional profile text is missing, the mini-program writes controlled fallback labels or hides the module.
- If the provider token is invalid, the task fails and no mock/source-image artifact is shown.
