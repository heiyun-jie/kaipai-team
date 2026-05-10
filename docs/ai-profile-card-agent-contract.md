# AI Profile Card Agent Contract

## Status

This document locks the target contract for the AI profile card generation flow. It is a product and engineering contract, not a claim that the full implementation is already complete.

The current default mode is:

```text
Agent structures profile content and chooses a layout.
Image provider generates a no-final-text visual background.
Mini-program or deterministic canvas renderer renders factual user content.
```

The default mode is not:

```text
Image provider freely paints final Chinese profile text into the generated image.
```

## Product Decision

The agent should act as the director and editor:

- read the actor profile and selected style;
- select the highest-value facts, skills, works, photos, and intro;
- produce concise display copy that fits the selected layout;
- select a per-style `layoutPreset`;
- produce a provider-independent prompt for a visual background/template;
- produce quality checks that can be audited.

The image model should act as the visual background generator:

- preserve actor identity from the source image;
- generate the style, portrait, paper/studio/cinematic atmosphere, empty modules, blank frames, and decorative elements;
- leave all final business text regions empty and safe for deterministic rendering.

The deterministic renderer should act as the final typesetter:

- render actor name, facts, skills, works, intro, photos, video resume, share cover content, and contact actions;
- keep interactive detail pages clickable and shareable;
- keep static share covers reproducible and testable.

This contract is required because the current E2E evidence shows two risks:

- one global frontend coordinate map cannot reliably fit every generated style;
- letting a model freely render final Chinese text would create wrong, blurry, non-interactive, and hard-to-audit profile data.

## Responsibilities

### Agent Owns

- Profile understanding.
- Content prioritization.
- Style-aware wording.
- Missing-data fallback selection.
- `posterContent` generation.
- `layoutPreset` selection.
- Background prompt generation.
- Provider-independent `promptJson`.
- Negative prompt construction.
- Quality gate input and reasons.

### Agent Does Not Own

- Final readable Chinese text rendering in the generated image.
- Phone/contact rendering.
- QR code rendering.
- Video player rendering.
- Share/contact button rendering.
- Mini-program route behavior.
- Mock/source-image fallback as a successful AI artifact.
- Free-form final poster generation as the default mode.

## Data Boundaries

The agent may receive profile signals needed for content and visual decisions:

```json
{
  "actorProfile": {
    "name": "林夏",
    "gender": "female",
    "age": 24,
    "height": 168,
    "weight": null,
    "city": "上海",
    "hairStyle": "长发",
    "bodyType": "",
    "skills": ["影视表演", "短剧", "情绪戏", "现代戏"],
    "works": [
      {
        "projectName": "向光而行",
        "roleName": "实习记者/林夏",
        "shootDate": "2025-06"
      }
    ],
    "intro": "热爱镜头表达，具备稳定的表演专注度和现场配合意识。",
    "photos": ["https://example.invalid/photo.png"],
    "videoResume": "https://example.invalid/video.mp4"
  },
  "templateSceneCode": "classic",
  "styleCode": "classic"
}
```

The image provider must not receive:

- bearer tokens;
- raw authorization headers;
- private phone numbers;
- contact application records;
- private notes;
- internal-only audit fields;
- any data only needed by mini-program interaction.

Profile signals sent to the provider must be minimized and used to guide visual mood only. They must not instruct the model to render final readable business text.

## `posterContent` Schema

`posterContent` is the agent output used by deterministic renderers. It must be compact, factual, and slot-safe.

```json
{
  "layoutPreset": "classic_profile_v1",
  "textTheme": "dark",
  "posterContent": {
    "identity": {
      "name": "林夏",
      "meta": "女演员 · 24岁 · 168cm · 上海",
      "tag": "经典",
      "sellingPoint": "常驻上海，可配合项目沟通"
    },
    "facts": [
      { "label": "身高", "value": "168cm", "source": "height" },
      { "label": "体重", "value": "待完善", "source": "weight" },
      { "label": "常驻地", "value": "上海", "source": "city" },
      { "label": "发型", "value": "长发", "source": "hairStyle" }
    ],
    "skills": [
      { "label": "影视表演", "source": "skillTypes" },
      { "label": "短剧", "source": "skillTypes" },
      { "label": "情绪戏", "source": "skillTypes" },
      { "label": "现代戏", "source": "skillTypes" }
    ],
    "workSummary": {
      "text": "《向光而行》 · 饰 实习记者 · 2025",
      "source": "workExperiences[0]"
    },
    "intro": {
      "text": "热爱镜头表达，具备稳定的表演专注度和现场配合意识。",
      "source": "intro"
    },
    "photoSlots": {
      "items": ["..."],
      "limit": 6
    },
    "videoResume": {
      "enabled": true,
      "source": "primaryVideoResume"
    }
  },
  "displayLimits": {
    "facts": 4,
    "skills": 4,
    "photos": 6,
    "introMaxChars": 32,
    "workMaxChars": 48
  }
}
```

Rules:

- Use complete short sentences.
- Do not output half-sentences or dangling ellipses as final display copy.
- Prefer one high-signal work over several clipped work items.
- Prefer true actor-specific details over generic phrases.
- Use `待完善` only for product-approved missing values.
- Do not include contact phone, QR, token, or authorization data.

## `layoutPreset` Schema

Each style must have a dedicated layout preset. A preset is shared by backend prompt construction, mini-program rendering, canvas share composition, and QA.

```json
{
  "layoutPreset": "classic_profile_v1",
  "canvas": {
    "width": 2160,
    "height": 3840,
    "ratio": "9:16"
  },
  "textTheme": "dark",
  "slots": {
    "identity": { "x": 0.108, "y": 0.152, "w": 0.31, "h": 0.218 },
    "facts": { "x": 0.11, "y": 0.434, "w": 0.38, "h": 0.138 },
    "skills": { "x": 0.56, "y": 0.434, "w": 0.34, "h": 0.138 },
    "works": { "x": 0.112, "y": 0.601, "w": 0.776, "h": 0.084 },
    "photos": { "x": 0.106, "y": 0.696, "w": 0.788, "h": 0.087 },
    "intro": { "x": 0.108, "y": 0.807, "w": 0.374, "h": 0.119 },
    "video": { "x": 0.554, "y": 0.807, "w": 0.35, "h": 0.119 }
  },
  "limits": {
    "identityLines": 5,
    "facts": 4,
    "skills": 4,
    "photos": 6,
    "introLines": 2,
    "workLines": 2
  },
  "share": {
    "requiresComposedImage": true,
    "detailRoute": "/pkg-card/ai-profile-card-detail/index"
  }
}
```

Preset requirements:

- Every preset must define all required slots.
- Slot coordinates must be per style, not inherited from one global map unless verified.
- `textTheme` must be compatible with the generated background.
- The subject/portrait box must not cover business slots.
- The safe footer/action area must remain clear of required mini-program controls.

## Style Preset Matrix

| Style | Preset | Text Theme | Required Direction |
| --- | --- | --- | --- |
| `costume` | `costume_profile_v1` | `dark` | parchment or period dossier, visible empty frames |
| `classic` | `classic_profile_v1` | `dark` | warm studio/dossier layout, visible empty frames |
| `urban` | `urban_profile_v1` | `light` | dark cinematic layout with explicit readable-safe zones |
| `commercial` | `commercial_profile_v1` | `dark` or `light` | clean studio layout with clear card regions |
| `artistic` | `artistic_profile_v1` | `light` or `dark` | expressive layout with guarded readable-safe regions |

Current evidence:

| Style | Evidence | Status |
| --- | --- | --- |
| `costume` | `output/ai-profile-card-e2e/ai-profile-detail-intro-about-slot.png` | Existing artifact verified after intro slot correction |
| `urban` | `output/ai-profile-card-e2e/ai-profile-detail-style-urban-light-text.png` | Existing artifact verified with light text, but background lacks ideal module frames |
| `classic` | `output/ai-profile-card-e2e/ai-profile-detail-style-classic.png` | Fresh provider generation verified |
| `commercial` | none in current account | Blocked by template/account availability in last pass |
| `artistic` | none in current account | Blocked by template/account availability in last pass |

## Background Prompt Contract

The provider-facing prompt should be generated from `layoutPreset`, `posterContent`, source image, and style. It should describe the visual background, not final rendered text.

Prompt JSON concept:

```json
{
  "task": "ai_profile_card_background",
  "targetSize": "2160x3840",
  "renderMode": "background_only",
  "layoutPreset": "classic_profile_v1",
  "templateSceneCode": "classic",
  "styleCode": "classic",
  "sourceImageUrl": "https://example.invalid/source.png",
  "profileSignals": {
    "gender": "female",
    "age": 24,
    "city": "上海",
    "hairStyle": "长发",
    "skills": ["影视表演", "短剧", "情绪戏", "现代戏"]
  },
  "layoutRegions": {
    "identity": "blank safe text region",
    "facts": "blank bordered information module",
    "skills": "blank bordered skill module",
    "works": "blank wide works module",
    "photos": "six blank photo frames",
    "intro": "blank about module",
    "video": "blank video module"
  },
  "finalTextPolicy": "do_not_render_final_business_text"
}
```

Negative prompt minimum:

```text
readable text, Chinese characters, English letters, numbers, phone number,
QR code, watermark, brand logo, fake UI labels, filled profile text,
random readable calligraphy, source image echo, full-bleed portrait covering modules,
missing module frames, subject covering reserved slots, mock output
```

Allowed visual elements:

- portrait transformation;
- paper/studio/cinematic background;
- decorative borders;
- blank cards or frames;
- abstract seals or ornaments without readable characters;
- blank photo/video placeholders.

Disallowed visual elements:

- final actor facts painted into the image;
- fake Chinese/English labels;
- fake QR codes;
- fake contact UI;
- phone numbers;
- logos or watermarks;
- source image copied back as success.

## Deterministic Rendering Modes

### Interactive Detail Page

The mini-program detail page owns:

- actor name;
- identity meta;
- facts;
- skill chips;
- work summary;
- intro;
- photos;
- video resume;
- page share;
- contact application.

This page remains the canonical shared destination.

### Static Share Cover

The share cover must be composed when native text should appear in the share card:

```text
generated background + posterContent + layoutPreset renderer = static share cover
```

The current implementation uses mini-program canvas temp images. A future backend image service may replace or supplement it, but the output must remain deterministic and auditable.

## Quality Gate

Generated artifacts should not become user-visible success unless they pass the quality gate.

| Gate | Accept | Reject |
| --- | --- | --- |
| Provider | real provider such as `kplyyk` | `mock` |
| Source relation | generated image differs from source | source image echo |
| Text safety | no generated readable business text | Chinese/English/fake labels inside background |
| Slot compliance | required slots visible or safely renderable | subject/background covers required slots |
| Contrast | selected text theme is readable | text disappears into background |
| Storage | image stored and linked to task/share card | transient or missing artifact |
| Detail route | AI detail page opens with task/share id | legacy or non-AI page |
| Share | composed image includes rendered content | raw background when text is needed |

Future regeneration policy:

- If provider output fails text safety, source relation, or slot compliance, mark quality gate failed.
- If provider supports retry, regenerate with stricter prompt and same `layoutPreset`.
- If retry still fails, keep the task failed or manual-review blocked.
- Do not expose a failed background as a successful AI artifact.

## Backend Follow-Up Plan

Future backend work should add or derive:

- `posterContentJson`;
- `layoutPreset`;
- `textTheme`;
- `qualityGateStatus`;
- `qualityGateReason`;
- provider prompt JSON generated from the selected preset;
- prompt-agent tests for content limits, privacy exclusions, and layout compatibility.

Backend tests should verify:

- contact/private data is not sent to the image provider;
- `posterContent` fits display limits;
- intro/work copy uses complete short sentences;
- generated `layoutPreset` is compatible with `templateSceneCode` and `styleCode`;
- provider request still includes `targetSize=2160x3840`;
- failure remains fail-closed and does not create mock success artifacts.

## Frontend Follow-Up Plan

Future mini-program work should:

- read `layoutPreset` when available;
- render slots from `posterContent` when available;
- keep fallback rendering for old artifacts without `posterContent`;
- keep style-aware text themes;
- keep composed share image behavior;
- audit every style for slot completeness and text fit.

Frontend audits should assert:

- every style has a preset;
- every preset has all required slots;
- text limits are enforced before render;
- share image is composed when native text is shown;
- unavailable styles are shown as locked/unavailable instead of silently omitted.

## E2E Acceptance Checklist

For each available style, capture:

- generated task ID;
- provider code;
- model code;
- `templateSceneCode`;
- `styleCode`;
- `layoutPreset`;
- generated image tail;
- share card ID;
- detail route;
- detail screenshot;
- share payload;
- slot position assertions;
- visual review notes.

Minimum pass criteria:

- opens `pkg-card/ai-profile-card-detail/index`;
- background is a real generated artifact;
- text/photos/video are deterministic rendered content;
- intro and works occupy their preset slots;
- share image is composed, not a raw background-only image;
- contact action remains outside the generated visual template;
- unavailable styles have explicit blocker notes.

## Current Evidence Baseline

Frontend baseline:

```text
9ea1ddb fix: verify AI profile styles and intro slot
```

Spec baseline:

```text
8c4108c docs: record AI profile multi-style verification
```

Observed style state:

- `costume`: existing artifact works with framed document-style background.
- `classic`: fresh provider generation works with framed document-style background.
- `urban`: current artifact works only after light text adaptation; it needs a dedicated `urban_profile_v1` prompt/preset or stricter regeneration gate.
- `commercial`: not available to the protected account in the last pass.
- `artistic`: not available to the protected account in the last pass.

## Migration Plan

1. Add `posterContent` generation behind the current backend agent without removing current response fields.
2. Add `layoutPreset` and `textTheme` metadata to task/artifact responses.
3. Add frontend preset registry and render from metadata when present.
4. Keep fallback for current artifacts.
5. Add quality gate status before artifact exposure.
6. Move share cover composition toward a deterministic shared renderer if frontend canvas becomes unreliable.
7. Run real-provider E2E for every available style before marking implementation complete.

## Open Decisions

- Should static share covers be composed by frontend canvas, backend image service, or both?
- Where should `posterContentJson` and `layoutPreset` be persisted?
- Should failed quality gates trigger automatic regeneration?
- How many regeneration attempts are allowed per user action?
- Should unavailable styles be hidden, locked, or shown with a reason?
- Should every style have a dedicated styleCode instead of reusing scene codes?
- Should admin tooling expose quality-gate review for failed backgrounds?
