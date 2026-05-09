# AI Profile Card Generation Requirements

## Background

The mini program needs a new share-image creation flow. The user enters from the home page, selects a visual style, taps one action button, and later checks the generated result in `我的作品集` -> `已创建分享`.

This work must be based on the current repository snapshot and must not replace the existing manual share-card flow.

## Scope

1. Add a home-page entry named `AI生成分享图`.
2. Add a new mini-program page for AI share-image generation.
3. Let the user select an existing share style scene, then submit one generation task.
4. Show a modal after submission: `图片生成中，请在10分钟后到「我的作品集」的「已创建分享」中查看。`
5. Backend reads the authenticated actor profile and profile photos. It must not trust a user id supplied by the client.
6. Backend builds a model-independent prompt brief through a Prompt Agent, then sends provider-specific image-generation input.
7. Generation must be image-to-image when a real provider is configured.
8. The Prompt Agent must fix major layout positions:
   - Source portrait/reference image is the identity source.
   - Actor is placed on the right side of a 9:16 vertical image.
   - Left side is kept as a clean text-safe area for deterministic app overlay.
   - Generated image must not contain text, phone numbers, QR codes, logos, or watermarks.
9. On success, backend saves or links the generated image to the existing share-card data so it appears through the current `已创建分享` list and preview path.
10. Provider selection must be configurable so OpenAI, Doubao, or another HTTP image provider can be swapped without changing the mini-program page.

## Non-Goals

1. Do not remove or rewrite the current `创建分享` flow.
2. Do not expose an open-ended chat Agent to the client.
3. Do not write final profile text into the generated bitmap. Text remains app-rendered for quality and auditability.
4. Do not hardcode bearer tokens or provider API keys in source code.
5. Do not add a paid/free entitlement gate in this phase unless a separate product rule is supplied.

## Acceptance Criteria

1. Existing homepage style cards and `创建分享` path still work.
2. `AI生成分享图` is an additional entry only.
3. Submitting generation creates a backend task and returns immediately.
4. The backend task records prompt, provider, status, source image, generated image, and linked share card.
5. The generation flow must not use a mock provider in any runtime path. If no real provider credential is configured, the backend must fail the task explicitly instead of returning the source image.
6. Frontend only calls the backend API. Backend calls the Prompt Agent. The Prompt Agent calls the configured image-generation model/provider and returns the result to backend persistence.
7. With a real provider configured, the same Prompt Agent contract is used across KPLYYK, OpenAI, Doubao/HTTP bridge, or future providers.
8. The portfolio page can see the generated share through backend-saved task/artifact data after task success.
