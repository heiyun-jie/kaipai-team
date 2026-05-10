# AI Profile Card Deterministic Layout Design

## Design Summary

The current failure is caused by two independent layout systems:

```text
AI model draws visual frames in one approximate position.
Frontend overlays business content in another fixed percentage position.
```

The v2 design removes that dependency:

```text
AI background: portrait, mood, texture, quiet zones.
Deterministic renderer: panels, titles, facts, works, photos, intro, video, share cover.
```

The AI background may look like a premium paper/poster surface, but it must not be the source of truth for content frames. All frame geometry that business content aligns to must come from `layoutPreset`.

## Rendering Layers

### Layer 1: AI Background

Input:

- selected source portrait;
- selected style;
- profile signals for mood only;
- layout quiet-zone instructions.

Output:

- `backgroundImageUrl`;
- 2160x3840 image;
- no final readable text;
- no final panel borders that must align with content;
- no QR/contact/video UI.

The background can include:

- paper texture;
- ink wash;
- studio light;
- portrait;
- soft blank areas;
- abstract ornaments.

The background should not include:

- section titles;
- data rows;
- hard information cards;
- thumbnail frames that frontend must match exactly;
- readable Chinese or English text.

### Layer 2: Deterministic Poster Layout

Input:

- `layoutPreset`;
- `posterContent`;
- `backgroundImageUrl`.

Output on detail page:

- native mini-program components positioned over a fixed 9:16 poster.

Output for share:

- composed image with the same visual placement.

## Data Contract

### Artifact Response

The backend v2 task/artifact response should extend current DTOs with:

```json
{
  "artifactVersion": 2,
  "renderMode": "deterministic_overlay",
  "backgroundImageUrl": "https://cdn.example.com/ai-profile-card/bg.png",
  "generatedImageUrl": "https://cdn.example.com/ai-profile-card/bg.png",
  "finalShareImageUrl": "https://cdn.example.com/ai-profile-card/share.png",
  "layoutPreset": "classic_profile_v2",
  "layoutPresetVersion": "2026-05-10",
  "layoutPresetJson": {},
  "textTheme": "classic_light_paper",
  "posterContent": {},
  "qualityGateStatus": "passed",
  "qualityGateReason": ""
}
```

`generatedImageUrl` remains as a compatibility alias only. New code should prefer `backgroundImageUrl` for detail background and `finalShareImageUrl` for sharing.

### Poster Content

```json
{
  "identity": {
    "name": "林夏",
    "meta": "女演员 · 24岁 · 168cm · 上海",
    "styleLabel": "经典",
    "sellingPoint": "常驻上海，可配合项目沟通"
  },
  "facts": [
    { "label": "身高", "value": "168cm" },
    { "label": "体重", "value": "待完善" },
    { "label": "常驻地", "value": "上海" },
    { "label": "发型", "value": "长发" }
  ],
  "skills": ["影视表演", "短剧", "情绪戏", "现代戏"],
  "works": ["《向光而行》 · 饰 实习记者 · 2025"],
  "intro": "热爱镜头表达，具备稳定的表演专注度和现场配合意识。",
  "photos": [],
  "videoResume": {
    "url": "",
    "posterUrl": "",
    "durationText": "00:08"
  }
}
```

### Layout Preset

Use a 2160x3840 coordinate system. Store pixel coordinates to avoid ambiguous percentage rounding.

```json
{
  "code": "classic_profile_v2",
  "canvas": {
    "width": 2160,
    "height": 3840
  },
  "safeArea": {
    "top": 160,
    "right": 120,
    "bottom": 360,
    "left": 120
  },
  "backgroundPolicy": {
    "mode": "background_only",
    "requireQuietZones": true,
    "allowDecorativeTexture": true,
    "allowHardFrames": false
  },
  "theme": {
    "text": "dark",
    "panelFill": "rgba(255, 248, 232, 0.72)",
    "panelStroke": "rgba(190, 150, 86, 0.62)",
    "chipFill": "#a94438",
    "chipText": "#ffffff"
  },
  "slots": {
    "identity": { "x": 180, "y": 520, "w": 840, "h": 520, "maxLines": 5 },
    "facts": { "x": 180, "y": 1540, "w": 850, "h": 560, "maxItems": 4 },
    "skills": { "x": 1080, "y": 1540, "w": 850, "h": 560, "maxItems": 4 },
    "works": { "x": 180, "y": 2200, "w": 1770, "h": 360, "maxLines": 2 },
    "photos": { "x": 180, "y": 2630, "w": 1770, "h": 330, "maxItems": 6 },
    "intro": { "x": 180, "y": 3040, "w": 850, "h": 420, "maxLines": 3 },
    "video": { "x": 1080, "y": 3040, "w": 850, "h": 420, "maxItems": 1 }
  }
}
```

The exact numbers above are starter geometry. The implementation must tune them against actual device screenshots and share output, then commit the final values.

## Frontend Architecture

### Preset Registry

Create a local frontend preset registry for the first pass:

```text
kaipai-frontend/src/pkg-card/ai-profile-card-detail/layout-presets.ts
```

Responsibilities:

- define fallback presets for existing styles;
- normalize backend preset JSON when present;
- expose helpers to convert canvas pixels to poster percentages;
- expose required slot names for audit.

If backend returns `layoutPresetJson`, frontend uses it. Otherwise frontend resolves by `layoutPreset` or `styleCode`.

### Detail Page

For v2:

- poster container keeps `aspect-ratio: 9 / 16`;
- background image uses `scaleToFill` inside the fixed-ratio poster only;
- overlay root is absolute `inset: 0`;
- panels are rendered from preset slots;
- all panel styles come from deterministic theme tokens;
- photo and video slots are clipped by deterministic containers.

For v1:

- keep current fallback classes so old artifacts can still be opened.

The detail page should decide mode with:

```ts
const isDeterministicArtifact = computed(() =>
  artifactVersion >= 2 || renderMode === 'deterministic_overlay' || !!posterContent || !!layoutPresetJson,
);
```

### Share Composition

Preferred later state:

- backend produces `finalShareImageUrl`.

First acceptable frontend state:

- `prepareShareImage` composes from `backgroundImageUrl`, `layoutPreset`, and `posterContent`;
- canvas dimensions are derived from 2160x3840, not ad hoc 560x896 coordinates;
- the share image contains the same deterministic panels and content as the detail page.

## Backend Architecture

### Agent

`AiProfileCardPromptAgent` should evolve from prompt-only to content-and-layout director:

```text
ActorProfileDTO + style + source image
  -> posterContent
  -> layoutPreset selection
  -> background-only prompt
  -> provider call
  -> quality gate metadata
```

The prompt should stop asking the provider to draw exact hard frames in fixed coordinates. It should ask for quiet zones compatible with the selected preset.

### Persistence

Add a migration after `V20260509_033__ai_profile_card_generation.sql` for v2 metadata:

```sql
ALTER TABLE actor_ai_profile_card_task
  ADD COLUMN artifact_version INT NOT NULL DEFAULT 1,
  ADD COLUMN render_mode VARCHAR(64) DEFAULT NULL,
  ADD COLUMN background_image_url VARCHAR(1024) DEFAULT NULL,
  ADD COLUMN final_share_image_url VARCHAR(1024) DEFAULT NULL,
  ADD COLUMN poster_content_json LONGTEXT DEFAULT NULL,
  ADD COLUMN layout_preset VARCHAR(128) DEFAULT NULL,
  ADD COLUMN layout_preset_json LONGTEXT DEFAULT NULL,
  ADD COLUMN text_theme VARCHAR(128) DEFAULT NULL,
  ADD COLUMN quality_gate_status VARCHAR(32) DEFAULT NULL,
  ADD COLUMN quality_gate_reason VARCHAR(1024) DEFAULT NULL;
```

If database compatibility requires smaller steps, add nullable fields first and backfill only new artifacts.

### DTOs

Extend:

- `AiProfileCardTaskRespDTO`;
- `AiProfileCardArtifactRespDTO`;
- frontend `AiProfileCardTask`;
- frontend `AiProfileCardArtifact`.

Keep old fields in responses to avoid breaking existing consumers.

## Quality Gate

Initial gate can be deterministic metadata plus provider checks:

- provider code is not mock;
- generated image URL differs from source image URL;
- stored image exists;
- style and preset are compatible;
- prompt JSON includes `renderMode=background_only`;
- negative prompt includes no text, QR, watermark, contact details;
- v2 artifact has `posterContentJson` and `layoutPreset`.

Future visual gate can use image OCR/object detection to reject readable text or covered quiet zones.

## E2E Plan

Run after implementation:

1. Generate one artifact from the real backend using the protected account token.
2. Wait for completion or open a known successful v2 task.
3. Open portfolio and verify the AI artifact appears.
4. Tap the artifact and verify route is `pkg-card/ai-profile-card-detail/index`.
5. Verify background image is visible.
6. Verify deterministic panel coordinates are used, not v1 hardcoded CSS.
7. Verify the red-box lower content area aligns: works, photos, intro, video.
8. Trigger share and verify share image is composed final image, not raw background.
9. Repeat for all currently available styles.
10. Record unavailable styles with precise blocker.

## Compatibility

Existing v1 artifacts stay supported:

- if no v2 metadata exists, use current v1 fallback rendering;
- show legacy generated image as before;
- do not mutate historical tasks unless a migration/backfill is explicitly requested.

New v2 artifacts should be visibly marked through metadata, not inferred only from URL shape.

## Risks

- Backend image composition may need font availability and CDN upload support.
- Frontend canvas composition may behave differently across devices if kept long-term.
- Some image providers may keep drawing fake text or hard frames despite prompt constraints.
- Commercial and artistic styles may remain unavailable to the current account and must not be counted as passed.

## Rollout

Phase 1:

- add v2 metadata fields and DTOs;
- generate `posterContent` and `layoutPreset`;
- render v2 detail page deterministically;
- keep frontend canvas share composition if backend composition is not ready.

Phase 2:

- add backend share-cover composition;
- expose `finalShareImageUrl`;
- make frontend share use backend final image first.

Phase 3:

- add visual quality gate and regeneration policy;
- expand style coverage after commercial/artistic unlock.
