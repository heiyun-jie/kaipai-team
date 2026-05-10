# AI Profile Card Deterministic Layout Requirements

## Context

The AI profile card detail page currently renders a generated 2160x3840 image as the poster background and overlays mini-program components with fixed percentage coordinates.

The latest visual review found a visible mismatch in the lower poster area:

- works text is not aligned with the generated works frame;
- photo strip and lower modules do not match the generated background frames;
- intro and video content are placed over AI-generated panel art instead of a deterministic layout;
- text clarity depends on the generated image underneath;
- every style can drift because the image model is not a layout engine.

This spec turns the previous agent contract into an implementation target. The system must stop depending on AI-generated business frames as the source of truth. The AI model should generate a background layer, while deterministic code owns all factual text, cards, frames, photo/video slots, and share composition.

## Requirements

### R1. Background-Only Image Contract

AI-generated images MUST be treated as visual backgrounds, not final profile cards.

The provider prompt MUST request:

- target size `2160x3840`;
- actor identity preservation from the selected source photo;
- style-specific atmosphere, paper texture, light, subject pose, and decorative background;
- reserved visual quiet zones compatible with the selected layout preset;
- no final readable Chinese text, English text, numbers, phone numbers, QR codes, logos, watermarks, or fake UI labels.

The provider prompt MUST NOT require the image model to draw final business cards, text-bearing frames, work rows, skill chips, photo thumbnails, video player UI, contact buttons, or exact module borders that frontend content must align to.

### R2. Deterministic Layout Ownership

The mini-program detail page and static share cover MUST derive visible business layout from a shared deterministic contract:

- `layoutPreset`;
- `posterContent`;
- `textTheme`;
- canvas size `2160x3840`;
- slot coordinates measured in the canvas coordinate system.

The following visual elements MUST be rendered by deterministic code:

- identity text;
- actor facts;
- skill chips;
- works text;
- photo slots and photos;
- intro/about text;
- video resume thumbnail and duration;
- section titles;
- information panel borders/background surfaces;
- contact/share actions.

The frontend MUST NOT rely on hardcoded global percentages such as one shared `top: 60.1%` for all styles once v2 artifacts are available.

### R3. Layout Preset Schema

Every v2 AI profile card artifact MUST carry a `layoutPreset` code and renderable layout metadata.

Each preset MUST define:

- `canvas.width = 2160`;
- `canvas.height = 3840`;
- `safeArea` for mini-program status/menu overlays;
- `posterArea` for the actual share card area;
- `hero` subject-safe and identity-safe regions;
- slots for `identity`, `facts`, `skills`, `works`, `photos`, `intro`, and `video`;
- footer/action exclusion area;
- text theme;
- panel theme;
- item and line limits per slot.

Coordinates MUST be stored in canvas pixels or normalized fractions. If normalized fractions are used, they MUST be derived from the same 2160x3840 canvas.

### R4. Poster Content Schema

The backend agent MUST output or persist structured `posterContent` for v2 artifacts.

At minimum it MUST include:

- actor name and meta line;
- style label;
- one selling point;
- up to four facts;
- up to four skills;
- one to two work summaries;
- one short intro;
- selected photo URLs;
- video resume URL/poster/duration when available;
- source field references or reasoned missing-data fallbacks.

The agent MUST limit text before rendering:

- no half-sentence clipping;
- no raw ellipsis as the final intended copy;
- works must prefer one complete high-value work over several clipped records;
- intro must be placed in the intro slot, not the works or video slot.

### R5. API and Persistence Contract

The backend MUST persist enough metadata to reconstruct the same detail page and share image:

- `backgroundImageUrl`;
- `finalShareImageUrl` when server-side composition is available;
- `posterContentJson`;
- `layoutPreset`;
- `layoutPresetJson` or preset version reference;
- `textTheme`;
- `renderMode`;
- `qualityGateStatus`;
- `qualityGateReason`.

Existing `generatedImageUrl` MAY remain for backward compatibility, but v2 response semantics MUST distinguish:

- raw AI background image;
- deterministic final share image;
- old v1 generated profile-card image.

The frontend MUST keep a v1 fallback for existing artifacts without v2 metadata.

### R6. Detail Page Rendering

For v2 artifacts, `pkg-card/ai-profile-card-detail/index` MUST:

- render a fixed-ratio 9:16 poster container;
- render the AI image as a background layer;
- use deterministic panels and slots above the background;
- convert slot coordinates from the 2160x3840 canvas to the displayed poster dimensions;
- prevent bottom action bar and safe area from changing poster coordinate mapping;
- render video resume in the video slot without native `controls` overlay unless explicitly opened;
- render intro in the configured intro slot;
- render works in the configured works slot;
- keep text readable with style-aware contrast surfaces.

The page MUST NOT depend on the AI background containing frames for the red-box content area.

### R7. Share Image Rendering

The shared image MUST be composed from the same v2 data:

```text
backgroundImageUrl + layoutPreset + posterContent + deterministic renderer = final share cover
```

The preferred implementation is backend composition because it is device-independent and reproducible.

If frontend canvas composition is used in the first pass, it MUST:

- use the same 2160x3840 coordinate contract;
- produce a temp image that includes deterministic panels, text, photos, and video thumbnail;
- not use the raw AI background as the share image when visible text is rendered natively.

### R8. Quality Gate

The system MUST reject or mark as failed any v2 generation where:

- provider returns a mock or source-image echo;
- background contains readable final profile text;
- portrait covers reserved text/panel regions;
- text contrast cannot be satisfied by the selected theme;
- required quiet zones are missing;
- returned image is not compatible with the expected 9:16 ratio;
- image cannot be stored in the backend artifact pipeline.

If a provider cannot satisfy background-only constraints after retry, the task MUST fail with a visible reason instead of saving a misleading artifact.

### R9. Tests and E2E

The implementation MUST include automated checks for:

- no v2 detail page uses v1 hardcoded global slot CSS;
- every style has a layout preset;
- every required slot exists;
- text limits are enforced before render;
- v2 share image is composed, not raw background;
- v1 artifacts still open through fallback;
- AI artifacts appear in portfolio and open AI detail pages.

Before marking this spec complete,真人 E2E simulation MUST verify:

- generate or open real AI artifacts;
- portfolio card enters AI detail page;
- detail page shows AI background plus deterministic content;
- red-box area content aligns with deterministic panels;
- intro, works, photos, and video appear in correct slots;
- share payload path enters AI detail route;
- share image is the composed final image;
- at least all currently available styles are tested;
- unavailable styles are explicitly recorded as blockers, not as passed.

## Non-Goals

- This spec does not change the normal actor card detail page.
- This spec does not remove existing v1 AI artifacts.
- This spec does not permit frontend mock data for success states.
- This spec does not require AI to render final Chinese text.
- This spec does not require all styles to share one layout.

## Acceptance Criteria

- New v2 artifacts no longer rely on AI-generated lower frames for content alignment.
- The red-box lower content area is rendered by deterministic panels and slots.
- Frontend and share image use the same 2160x3840 layout contract.
- The backend persists v2 metadata or returns it from a stable preset registry.
- Existing v1 artifacts remain viewable.
- Automated audit, type-check/build, backend tests, and真人 E2E pass.
