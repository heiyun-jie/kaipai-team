# AI Profile Card Portfolio Visibility Investigation Requirements

## Background

As of 2026-05-09, the mini program can submit an `AI生成分享图` task and the frontend has an AI detail page route. The observed product issue is still:

- `我的作品集` -> `已创建分享` shows only 3 existing scene cards.
- The user cannot find a distinct AI-generated detail page from the portfolio list.
- The visible cards show normal scene entries (`都市`, `古风`, `经典`) rather than an obvious AI-generated share-image entry.

This spec is an investigation spec. Its purpose is to identify the exact blocking point before more implementation changes are made.

## Product Expectation To Validate

1. After a successful AI image generation task, the generated image must be visible from `我的作品集`.
2. The portfolio entry must route to an AI-generated share detail page, not the normal card preview.
3. Sharing that detail page must let external viewers enter the AI-generated detail page.
4. The AI-generated image should be treated as a backend-saved artifact, not as a temporary frontend-only preview.
5. The implementation must not break the current three manual share scene cards.

## Current Evidence From Code

1. Backend generation currently calls `UserShareCardService.createCard(...)` from `AiProfileCardServiceImpl.saveGeneratedShareCard(...)`.
2. `UserShareCardServiceImpl.createCard(...)` reuses an existing active card for the same template:
   - It checks `findActiveOwnedCardByTemplateId(...)`.
   - If found, it returns the existing card instead of inserting a new one.
3. Therefore, if the actor already has the three scene cards, AI generation is expected to remain inside one of those existing three cards rather than increase the `已创建分享` count.
4. Backend stores the generated image by saving it into `actor_card_config.highlightedPhotoUrls`.
5. Frontend portfolio currently tries to detect AI cards through:
   - `GET /api/ai/profile-card/tasks`
   - generated image fallback from `highlightedPhotos`
6. If the user still sees normal portrait covers and no AI detail entry, one of the backend task, persistence, deployment, or frontend runtime paths is not producing a recognizable generated artifact.

## Investigation Questions

1. Did the online backend actually receive and complete an AI generation task for this actor?
2. Does `actor_ai_profile_card_task` have a `success` task with `generated_image_url` and `share_card_id` for this user?
3. Does `GET /api/ai/profile-card/tasks` exist on the deployed backend and return the successful task to the mini program?
4. Does `GET /api/card/config?shareCardId=...` return `highlightedPhotos[0]` equal to the generated image URL?
5. Is the mini program running the latest frontend build that contains the AI detail route and portfolio AI detection?
6. Should AI generated images be modeled as separate portfolio artifacts instead of being written into normal scene card config?

## Non-Goals

1. Do not change the generation provider or prompt agent in this investigation.
2. Do not store, commit, or paste user bearer tokens in any spec, script, or log.
3. Do not remove the existing manual share cards.
4. Do not add another visual workaround before confirming the backend task and artifact state.

## Acceptance Criteria

This investigation is complete when the team can state which of the following is true:

1. **Generation did not complete:** the task is missing, failed, or has no generated image URL.
2. **Generation completed but was not persisted:** task has an image URL, but card config does not expose it.
3. **Persistence works but frontend cannot discover it:** API returns data, but portfolio does not classify the card as AI-generated.
4. **Everything works in code but runtime is stale:** deployed backend or mini-program build is not the latest pushed code.
5. **Current data model is insufficient:** generated AI images need a separate artifact/list/detail API because reusing `user_share_card` by scene template hides the AI result inside the existing three scene cards.

