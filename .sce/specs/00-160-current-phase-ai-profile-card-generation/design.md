# AI Profile Card Generation Design

## Existing Flow To Preserve

The current mini-program flow is:

Home page -> `pkg-card/card-list/index` -> style select -> photo select -> save share card -> `pkg-card/actor-card/index` preview.

Portfolio uses `getMyShareCards()` and lists `已创建分享`. Each card opens the existing preview path with `shareCardId` and artifact type.

The AI generation feature must reuse this storage and display path instead of introducing a second portfolio surface.

## Frontend Design

New entry:

- File: `kaipai-frontend/src/pages/home/index.vue`
- Add a compact action inside the existing hero stats strip action area: `AI生成分享图`.
- Tap navigates to `pkg-card/ai-profile-card/index`.

New page:

- File: `kaipai-frontend/src/pkg-card/ai-profile-card/index.vue`
- Loads existing share templates through `getMyShareCards()`.
- Follows the existing `pkg-card/card-list/index` UI structure: compact title, step indicator, white selection panel, concise review row, and bottom action bar.
- Presents style choices using the same `KpShareSceneCard` visual language with concise captions that do not overflow the card grid.
- Bottom button: `一键生成`.
- On submit, calls `POST /api/ai/profile-card/generate`.
- On success, shows modal with the required 10-minute portfolio message.

The page must not let users enter free-form prompts in this phase. Style choice is the only generation control.

## Backend Design

New API:

- `POST /api/ai/profile-card/generate`
- `GET /api/ai/profile-card/tasks/{taskId}`

New persistence:

- Table: `actor_ai_profile_card_task`
- Stores owner, actor profile, style, source image, prompt brief, provider prompt, provider/model, status, generated image URL, linked share card, and failure reason.

Task execution:

1. Controller resolves authenticated user id from Spring Security authentication.
2. Service loads `ActorProfileDTO` through `ActorProfileService.mine(userId)`.
3. Service picks a source image from avatar, portrait photos, lifestyle photos, production photos, or experience photos.
4. Service creates a pending task and returns immediately.
5. Background worker builds prompt through `AiProfileCardPromptAgent`.
6. Provider registry dispatches to:
   - `mock`: returns source image URL for local/dev smoke flow.
   - `openai`: image edit style HTTP adapter.
   - `http`: generic adapter for Doubao/Seedream or bridge services.
7. If the provider returns bytes, backend uploads the image to COS through the AI generated image storage component.
8. On success, service creates or reuses a normal `user_share_card`, saves generated image as the first `actor_card_config.highlightedPhotoUrls`, and sets preferred artifact to `poster`.

## Prompt Agent Contract

The Prompt Agent returns:

- `promptJson`: model-independent structured brief.
- `promptText`: provider-ready natural language prompt.
- `negativePrompt`: prohibited content and quality failures.

Fixed layout rules are mandatory:

- 9:16 vertical canvas, target size `2160x3840`.
- Actor identity reference is source image #1.
- Actor occupies right-side box `x=1180-1980, y=400-3380`.
- Face center near `x=1530,y=1080`.
- Left safe area `x=160-1020, y=430-3200`.
- No generated text, QR code, phone, logo, watermark, or contact info.

This keeps final share text deterministic in the app and makes provider swaps safer.

## Provider Swap Strategy

The mini-program always calls the same backend endpoint. Provider changes happen through backend configuration:

- `kaipai.ai.profile-card.provider-code=mock|openai|http|kplyyk`
- OpenAI settings under `kaipai.ai.profile-card.openai.*`
- Generic HTTP provider settings under `kaipai.ai.profile-card.http.*`
- KPLYYK management image-generation settings under `kaipai.ai.profile-card.kplyyk.*`

The generic HTTP provider expects a JSON response containing either `imageUrl`/`url` or `b64Json`/`b64_json`.

The KPLYYK provider adapts the management workbench mounted at `http://kplyyk.com/manage/image-generation`. The page itself is not the API; it calls:

- `POST /v0/management/image-generation/test`
- `GET /v0/management/image-generation/test/{task_id}`

For actor share images, the provider uses image-to-image multipart upload with field `image`, model `gpt-image-2`, quality `high`, count `1`, and fixed output size `2160x3840`. The management key is supplied through environment configuration and must not be committed into source code.

## Compatibility Notes

The current share-card service reuses one active card per template. Therefore repeated AI generation for the same style updates the same style card configuration. This keeps the MVP non-invasive. Supporting many generated images per style requires a separate multi-instance share-card change.
