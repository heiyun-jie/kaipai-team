# AI Profile Card 750 Design Coordinate Contract Requirements

## Scope

This spec locks the AI profile card generation and detail rendering to the mini-program logical design canvas while keeping provider output high resolution.

The change must not reintroduce mock generation, local fake URLs, or frontend direct calls to image-generation management APIs.

## Requirements

1. The mini-program AI profile card detail page must use a `750 x 1334` logical design canvas as the authoritative layout coordinate system.
2. The backend prompt agent must explicitly tell the image provider that `750 x 1334` is the mini-program design coordinate system and `2160 x 3840` is only the high-resolution provider output target.
3. Slot regions for identity, facts, skills, works, photos, intro, and video must be defined in the `750 x 1334` design coordinate system and converted from that source into percentages, share canvas pixels, and provider pixel descriptions.
4. The provider prompt must require the generated image to be a background layer only. The model must not render final profile text, app panels, section titles, rows, chips, thumbnails, video controls, phone numbers, QR codes, watermarks, or fake UI labels.
5. The frontend must continue rendering all user-visible profile information with native components over the generated background image.
6. The share preview canvas must use the same design slots as the detail page and scale them to the share output size.
7. The frontend audit must fail if the implementation no longer exposes `750 x 1334` design canvas metadata or if it regresses to only `2160 x 3840` slot coordinates.
8. The backend tests must fail if the agent prompt no longer includes the mini-program design canvas, provider output canvas, and design-coordinate layout regions.
9. 真人 E2E can only mark a style as passed when the real mini-program page loads a backend AI artifact, opens the AI detail page, and shows complete foreground content without visible clipping or layout deformation.
10. Styles unavailable to the protected test account must be recorded as blocked/unavailable and must not be counted as passed.
11. The generated background for every available style must be full-bleed and frame-free. `classic` and `costume` must not generate visible borders, paper sheet edges, card outlines, document pages, scroll edges, corner ornaments, boxed backgrounds, or any visual shell behind the frontend-rendered content.
12. After changing the prompt contract, old backend artifacts are not valid proof. The affected styles must be regenerated through the real backend API and then rechecked in the mini-program AI detail page before the task can be marked complete.

## Non-Goals

- Do not reduce the provider output to `750px` wide unless a later product decision explicitly accepts lower share-image quality.
- Do not make the model responsible for rendering readable business text.
- Do not modify unrelated portfolio, contact, membership, or card-list flows.
