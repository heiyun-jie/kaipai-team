# AI Profile Card Style Stability And E2E Quality Gate Requirements

## Context

The AI profile card flow is now able to generate images, store artifacts, and open a dedicated mini-program detail page. The latest真人 review still fails product acceptance:

- generated backgrounds and deterministic foreground panels conflict in several styles;
- text can become low contrast, visually blurred, or clipped after screenshot/share rendering;
- some content starts too high or appears over unintended background material;
- one shared slot map and a small dark/light theme switch cannot fit all style outputs;
- the existing E2E script passed despite visible style mismatch and content risk.

This spec replaces the previous "mechanical pass" with a strict quality contract. The task is not complete until every available style has been tested against the same visual and route expectations. Unavailable styles are blockers or explicitly unavailable, never counted as passed.

## Requirements

### R1. No Mock Or Frontend Shortcut

The production flow MUST remain:

```text
frontend -> backend generate API -> backend agent -> real image provider -> backend storage/database -> frontend portfolio/detail/share
```

The frontend MUST NOT create successful mock artifacts, fake generated URLs, or infer success from local state.

The backend MUST NOT expose provider `mock` outputs or source-image echoes as successful AI artifacts.

### R2. Agent Output Contract

The backend agent MUST produce a model-independent generation contract for each task:

- `templateSceneCode`;
- `styleCode`;
- `layoutPreset`;
- `textTheme`;
- `panelTheme`;
- `posterContent`;
- prompt JSON for the image provider;
- negative prompt;
- quality gate intent.

The agent MUST use actor profile information and selected style as input to decide:

- which facts, skills, works, intro, photos, and video data are shown;
- which copy is short enough to fit each slot;
- which style preset and panel theme should be used;
- what background-safe zones the image model must preserve.

The image provider MUST be asked to generate a visual background layer, not final factual Chinese text.

### R3. Per-Style Layout And Theme Contract

Every supported style MUST have a dedicated preset. A preset MUST include:

- canvas `2160x3840`;
- safe top offset compatible with `top: 15.2%` for identity start unless that style explicitly documents a different validated value;
- slots for `identity`, `facts`, `skills`, `works`, `photos`, `intro`, and `video`;
- text limits per slot;
- panel background, border, title, primary text, secondary text, chip, and video colors;
- image prompt layout regions generated from the same slot map.

The frontend MUST NOT rely on one global CSS map as the source of truth for all styles.

### R4. Content Fit Contract

The rendered detail page and share image MUST NOT show incomplete business content:

- actor name must fit without horizontal clipping;
- identity meta must fit in its slot;
- facts must show complete values or approved short fallback text;
- skill chips must wrap or clamp without escaping their slot;
- works must prefer one complete high-value work summary over multiple clipped records;
- intro must be placed in the intro slot and remain readable;
- photo strip must stay within its slot;
- video resume must stay in the video slot and must not use a native playback overlay in the composed share image.

If data exceeds a slot, the agent/frontend must reduce, summarize, or clamp by rule before rendering. It must not rely on random CSS overflow hiding to make bad content disappear.

### R5. Style Compatibility Contract

Generated image and frontend foreground MUST be visually compatible:

- `classic` and `costume` may use light paper/dossier panels;
- `urban` must use dark/cinema-compatible panels and light text unless a validated light-zone background is returned;
- `commercial` must use clean studio panels with neutral high contrast;
- `artistic` must use a controlled gallery/cinema panel style and explicit contrast guard.

The frontend MUST apply style-specific foreground themes, not only background text color.

The backend prompt MUST not describe all styles as古风宣纸. Each style must receive a matching visual direction and safe-zone wording.

### R6. No Page Deformation

The AI detail page MUST keep a stable `9:16` poster:

- no horizontal clipping at supported mobile widths;
- no content outside the poster bounds;
- no poster width greater than viewport width;
- no bottom action bar changing poster coordinate mapping;
- no unexpected blank black region inside the captured poster area;
- external screenshots and share captures must use the same layout contract.

### R7. Portfolio And Share Route Contract

AI artifacts MUST appear in `pkg-card/portfolio/index` under "已创建分享" after successful backend storage.

Clicking an AI artifact MUST open:

```text
/pkg-card/ai-profile-card-detail/index?shareCardId=...&taskId=...
```

Sharing from that detail page MUST share the AI detail page route, and the share image MUST be a composed image that includes deterministic foreground content, not the raw background alone.

### R8. Quality Gate And Fail-Closed Behavior

A generated task MUST NOT be considered product-pass if any of these occur:

- provider is mock;
- generated image equals the source image;
- background is incompatible with the selected foreground theme;
- business text or modules are missing, clipped, or unreadable;
- foreground panels conflict with the generated style;
- page deforms or clips horizontally;
- share path does not open AI detail;
- share image is raw background only;
- a style is unavailable but counted as passed.

If a quality gate cannot be automated yet, it MUST be represented as a required真人 review step with screenshot evidence and a recorded result.

### R9. E2E Matrix

真人 E2E MUST cover every style exposed to the account/runtime:

- `classic`;
- `costume`;
- `urban`;
- `commercial`;
- `artistic`.

For each style, E2E MUST record:

- task ID or artifact ID;
- provider code;
- model code;
- generated image URL tail;
- share card ID;
- route after portfolio click;
- detail screenshot;
- share payload path;
- share image evidence;
- DOM geometry assertions;
- style/theme assertion;
- manual visual verdict.

The overall spec MUST remain incomplete until all exposed styles pass or are explicitly unavailable with evidence.

## Non-Goals

- This spec does not replace the normal non-AI actor card flow.
- This spec does not ask the image model to render final Chinese body text.
- This spec does not introduce frontend mock data.
- This spec does not mark older mechanically passing screenshots as sufficient acceptance evidence.

## Acceptance Criteria

- A new style-stability spec exists and tracks root cause, design, and tasks.
- Backend prompt agent uses per-style layout/theme contracts and does not apply古风宣纸 background wording to every style.
- Frontend detail rendering uses per-style preset/theme data for panels, text, and share composition.
- Automated audit fails on one global slot map, missing style presets, raw background sharing, or missing all-style E2E evidence.
- 真人 E2E verifies portfolio -> AI detail -> share route/share image for all available styles.
- No style is marked passed without screenshot and route evidence.
- All touched code/spec changes are committed and pushed only after verification relevant to that repo.
