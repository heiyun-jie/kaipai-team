# AI Profile Card Agent Contract Documentation Design

## Design Summary

The documentation should turn the current product decision into an enforceable contract:

> Use the agent as the director and editor. Use the image model as the visual background generator. Use deterministic rendering for factual user content.

This resolves the two failure modes observed in current testing:

- A single global coordinate map cannot reliably fit every AI-generated style.
- Letting the image model freely paint final Chinese profile text would be inaccurate, non-interactive, and hard to verify.

The documentation must therefore describe a hybrid system:

1. Agent reads user profile and selected style.
2. Agent generates `posterContent`, `layoutPreset`, and model prompt.
3. Provider generates a no-final-text visual background.
4. Deterministic renderer fills text/photos/video/share content into layout slots.
5. QA validates every style with screenshots and share payloads.

## Contract Layers

### Layer 1: Profile Input

The agent may receive profile signals needed for visual and content decisions:

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
    "photos": ["..."],
    "videoResume": "..."
  },
  "styleCode": "classic",
  "templateSceneCode": "classic"
}
```

Sensitive data must be excluded:

- bearer tokens;
- private phone/contact fields;
- internal IDs not needed by the provider;
- private notes;
- raw authorization headers.

### Layer 2: Agent Poster Content Output

The agent should produce structured, deterministic display content:

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
    "skills": ["影视表演", "短剧", "情绪戏", "现代戏"],
    "workSummary": "《向光而行》 · 饰 实习记者 · 2025",
    "intro": "热爱镜头表达，具备稳定的表演专注度和现场配合意识。",
    "photoSlots": ["最多6张"],
    "videoResume": {
      "enabled": true,
      "display": "主视频"
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
- Do not produce dangling ellipses as final copy.
- Prefer one high-signal work over many clipped works.
- Prefer the actor's actual strengths over generic phrases.
- Keep missing values explicit as `待完善` only where product-approved.

### Layer 3: Layout Preset Output

Each style needs its own layout preset. A preset should be expressible in JSON and reusable by frontend, backend canvas composition, and QA.

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
    "skills": 4,
    "photos": 6,
    "introLines": 2,
    "workLines": 2
  }
}
```

The documentation should warn that current `urban` evidence proves coordinates alone are not enough. Some styles require a different background prompt or dedicated visual frame policy.

## Background Generation Prompt

The prompt document should define the provider-facing payload conceptually:

```json
{
  "task": "ai_profile_card_background",
  "targetSize": "2160x3840",
  "renderMode": "background_only",
  "layoutPreset": "classic_profile_v1",
  "styleCode": "classic",
  "sourceImageUrl": "...",
  "profileSignals": {
    "gender": "female",
    "age": 24,
    "city": "上海",
    "hairStyle": "长发",
    "skills": ["影视表演", "短剧", "情绪戏", "现代戏"]
  },
  "layoutRegions": {
    "identity": "blank safe text region",
    "facts": "blank bordered module",
    "skills": "blank bordered module",
    "works": "blank wide module",
    "photos": "six blank photo frames",
    "intro": "blank about module",
    "video": "blank video module"
  }
}
```

Negative prompt:

```text
readable text, Chinese characters, English letters, numbers, phone number,
QR code, watermark, brand logo, fake UI labels, filled profile text,
random readable calligraphy, source image echo, full-bleed portrait covering modules,
missing module frames, subject covering reserved slots
```

## Rendering Modes

### Interactive Detail Page

The mini-program renders:

- profile text;
- facts;
- skill chips;
- work summary;
- intro;
- photo slots;
- video resume;
- share button;
- contact application button.

This page remains the canonical shared destination.

### Static Share Cover

The static share image is a composed image:

```text
AI background + posterContent + layoutPreset renderer
```

It may be generated by:

- frontend canvas for current mini-program flow; or
- backend canvas/image service in a future pass.

It must not be the raw AI background when native text is needed in the share card.

## Quality Gate

The documentation should define an accept/reject gate:

| Gate | Accept | Reject |
| --- | --- | --- |
| Provider | real provider such as `kplyyk` | `mock` |
| Image relation | generated image differs from source | source-image echo |
| Text safety | no readable generated business text | Chinese/English text or fake labels in background |
| Slot compliance | all required slots visible or safely renderable | subject/background covers slots |
| Contrast | text theme gives readable output | text disappears into background |
| Share | composed temp/static image includes rendered content | raw background share image |
| Detail route | opens AI detail page | opens legacy/non-AI card |

## Style Matrix

The documentation should track style readiness:

| Style | Layout Preset | Text Theme | Current Evidence Need |
| --- | --- | --- | --- |
| costume | `costume_profile_v1` | dark | existing artifact plus future regenerated background |
| urban | `urban_profile_v1` | light | dedicated framed dark layout or regeneration gate |
| classic | `classic_profile_v1` | dark | fresh successful generation and visual QA |
| commercial | `commercial_profile_v1` | dark/light by output | account/template availability needed |
| artistic | `artistic_profile_v1` | light/dark by output | account/template availability needed |

## Proposed Durable Document

The future implementation pass should create a stable document such as:

```text
docs/ai-profile-card-agent-contract.md
```

Recommended sections:

1. Product decision summary.
2. Agent responsibilities.
3. Non-responsibilities.
4. `posterContent` schema.
5. `layoutPreset` schema.
6. Style preset matrix.
7. Prompt and negative prompt contract.
8. Privacy and data minimization.
9. Quality gate.
10. E2E evidence checklist.
11. Migration plan from current implementation.
12. Open decisions.

## Open Decisions

- Should final static share images be composed by frontend canvas or backend image service?
- Should failed layout compliance trigger automatic regeneration?
- Where should `posterContentJson` and `layoutPreset` be persisted?
- Should unavailable styles be hidden from the generation page or shown with locked state?
- Should each style have a separate provider prompt styleCode instead of using scene codes directly?
