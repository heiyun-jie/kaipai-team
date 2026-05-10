# AI Profile Card Style Stability And E2E Quality Gate Design

## Problem Statement

The current implementation has three independent sources of truth:

1. Backend prompt describes safe regions and background aesthetics.
2. Frontend CSS places deterministic panels with one shared percentage map.
3. E2E checks only route/basic geometry, not visual compatibility or all-style quality.

This lets a task pass even when the result is visually wrong. The urban screenshot is the clearest example: the generated image is a dark editorial portrait, while the foreground still reads as light parchment dossier panels. Text contrast and visual hierarchy fail even though the route and coordinates exist.

## Root Causes

### RC1. Prompt Style Drift

`AiProfileCardPromptAgent` has a global `fixedLayout` and `referenceQuality` that describe parchment, ink-wash, and Chinese period profile sheet quality for every style. Even when `templateSceneCode=urban`, the prompt still includes古风 paper/surface wording in the model-independent brief.

Impact:

- non-costume styles can receive incompatible background instructions;
- provider output can fight the selected frontend panel theme;
- model has no per-style safe-zone contract tied to actual frontend styles.

### RC2. One Global Slot Map

`layout-presets.ts` creates all presets from `BASE_SLOTS`. Codes differ, but coordinates do not. CSS in `index.vue` then hardcodes the same slot percentages directly.

Impact:

- per-style validation cannot tune coordinates;
- the frontend cannot adapt if provider composition differs by style;
- tests can pass because every style shares the same coordinates, not because every style fits.

### RC3. Foreground Theme Too Shallow

The frontend only special-cases urban/artistic with dark translucent panels and light text. Other visual properties, chip colors, panel density, background conflict, and share-canvas rendering remain partly global.

Impact:

- style compatibility is accidental;
- share image can differ from detail page;
- readable text depends on the generated background.

### RC4. Content Fit Is Post-Render, Not Agent-Owned

The frontend trims intro/work strings with fixed character counts, while the backend agent does not persist a `posterContent` contract. Long or unusual profile data can be hidden by `overflow: hidden` instead of being summarized before rendering.

Impact:

- content can be incomplete;
- clipping is hard to audit;
- share canvas and detail page can diverge.

### RC5. E2E Gate Is Underpowered

The previous audit checks static source patterns and basic screenshots, but it does not fail on:

- style mismatch;
- low contrast;
- horizontal clipping;
- missing all-style evidence;
- raw background share images;
- manual visual rejection.

Impact:

- visible product failures can be reported as "passed".

## Target Architecture

```text
Style Preset Registry
  -> Backend prompt safe regions
  -> Backend posterContent limits
  -> Frontend detail slots/themes
  -> Frontend share canvas composition
  -> E2E assertions
```

The style preset registry is the shared contract. It can be duplicated in backend/frontend for this phase, but the data shape must match and every style must be present.

## Backend Design

### Style Preset

Add a backend model/registry that resolves:

- `layoutPreset`;
- `textTheme`;
- `panelTheme`;
- `canvas`;
- slot boxes in pixels;
- content limits;
- image prompt safe-zone descriptions;
- style visual direction.

The registry should have dedicated entries for:

- `classic_profile_v3`;
- `costume_profile_v3`;
- `urban_profile_v3`;
- `commercial_profile_v3`;
- `artistic_profile_v3`.

### Prompt Agent

Update `AiProfileCardPromptAgent` so prompt JSON is composed from the resolved style preset:

- use style-specific `backgroundDirection`;
- use style-specific `safeZoneTone`;
- never inject古风 parchment wording globally;
- include `layoutPreset`, `textTheme`, `panelTheme`, and slot coordinates;
- include concise `profileSignals`;
- keep privacy exclusion and no-readable-text rules.

For this phase, persistence of v2 metadata may remain a follow-up if the database migration is too broad, but the provider request must already be generated from the same preset contract used by the frontend.

### Poster Content

The ideal backend output is structured `posterContent`. If full persistence is not completed in this phase, frontend fallback must remain deterministic and bounded, and the spec task must remain open.

## Frontend Design

### Per-Style Presets

Replace `BASE_SLOTS` cloning with per-style definitions. Presets must include:

- `code`;
- `scene`;
- `canvas`;
- `textTheme`;
- `panelTheme`;
- `slots`;
- `limits`;
- `colors`.

Slot values should still be based on the validated `top: 15.2%` identity offset, but the lower slots may differ by style after visual review.

### Rendering

`pkg-card/ai-profile-card-detail/index.vue` should:

- bind inline slot styles from `activeLayoutPreset`, not hardcoded CSS percentages;
- bind style variables from preset colors;
- use style-specific panel classes for detail page;
- use the same preset colors in `generateAiProfileSharePreviewImage`;
- keep all poster children inside `width: 100%; aspect-ratio: 2160 / 3840`.

### Content Fit

The frontend should add deterministic fit helpers:

- `limitTextByChars`;
- complete-sentence intro fallback;
- per-style/per-slot skill limit;
- fact value normalization;
- work summary normalization.

It must avoid silently rendering long content and hiding the overflow as the only fit strategy.

## E2E Design

Add or extend scripts so each run produces a JSON evidence bundle:

```json
{
  "generatedAt": "2026-05-10T00:00:00+08:00",
  "styles": [
    {
      "scene": "urban",
      "status": "passed|failed|unavailable",
      "route": "/pkg-card/ai-profile-card-detail/index?...",
      "providerCode": "kplyyk",
      "screenshot": "output/...",
      "checks": {
        "routeIsAiDetail": true,
        "posterWithinViewport": true,
        "noHorizontalClip": true,
        "allRequiredTextVisible": true,
        "themeMatchesStyle": true,
        "shareImageComposed": true
      },
      "manualVerdict": "passed|failed",
      "notes": ""
    }
  ],
  "overallPassed": false
}
```

Overall pass requires:

- every available style `passed`;
- no style `failed`;
- unavailable styles listed with evidence;
- manual visual verdict present for every available style.

## Implementation Phases

1. Create this spec and mark only spec creation/review tasks complete after actual creation.
2. Refactor frontend presets and CSS to make style contracts real.
3. Refactor backend prompt agent to use per-style prompt contracts.
4. Strengthen audit scripts so obvious incomplete implementation fails.
5. Run unit/build/audit checks.
6. Run真人 E2E for all styles and record evidence.
7. Only then mark acceptance tasks complete and commit/push.

## Risks

- Real provider generation may take time or fail transiently. This is not a pass; it is a blocker/evidence item.
- Some styles may be locked for the test account. Locked/unavailable styles must be recorded and cannot be counted as pass.
- Without backend `posterContentJson` persistence, detail/share rendering still relies on current actor snapshot. That is acceptable only as a bounded fallback, not the final target.
