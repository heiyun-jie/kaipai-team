# AI Profile Card 750 Design Coordinate Contract Design

## Problem

The detail page displays the poster at `750rpx x 1334rpx`, but the frontend preset slots and backend agent prompt were using `2160 x 3840` as the primary coordinate contract. This makes it easy for the model, frontend page, and share canvas to drift in how they understand fixed regions.

## Design Decision

Use two explicit canvases:

- `designCanvas`: `750 x 1334`
- `providerCanvas`: `2160 x 3840`

The `designCanvas` is authoritative for all product layout decisions. The `providerCanvas` is only the high-resolution bitmap output target.

## Frontend Contract

The frontend stores all AI profile card slots in `750 x 1334` design coordinates:

- `identity`
- `facts`
- `skills`
- `works`
- `photos`
- `intro`
- `video`

The detail page converts those slots to percentages against `750 x 1334`, so the displayed `750rpx x 1334rpx` poster remains aligned with the design contract.

The share canvas converts the same design slots to the share output canvas with independent X/Y scaling:

```text
shareX = designX * shareWidth / 750
shareY = designY * shareHeight / 1334
```

## Backend Agent Contract

The backend prompt JSON includes:

- `canvas.designCanvas.width = 750`
- `canvas.designCanvas.height = 1334`
- `canvas.providerCanvas.width = 2160`
- `canvas.providerCanvas.height = 3840`
- `canvas.targetSize = 2160x3840`
- fixed layout regions expressed in design coordinates and provider coordinates

The prompt text instructs the model to:

- treat `750 x 1334` as the mini-program design coordinate system;
- scale safe zones proportionally to `2160 x 3840`;
- generate only the background layer;
- keep all business foreground regions calm and low-detail;
- avoid any final text or app UI.

## Quality Gate

Passing this spec means:

- frontend audit, type-check, and WeChat build pass;
- backend prompt-agent tests pass;
- available real styles in WeChat DevTools open the AI detail page and show complete deterministic foreground content;
- unavailable styles remain explicitly blocked and are not marked complete.
