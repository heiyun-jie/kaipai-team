# AI Profile Card Agent Reference Quality Design

## Design Summary

The AI profile card agent should turn actor profile data, selected style, and a source portrait into a structured image-generation brief. For the provided reference style, the output should feel like a premium Chinese period actor dossier: parchment paper, ink-wash scene, ornate but restrained borders, right-side actor portrait, and blank native-rendering regions.

The key design decision is to separate visual generation from factual rendering:

- **Image model owns** portrait transformation, background, paper texture, decorative frames, empty photo slots, and atmosphere.
- **Mini-program owns** actor name, profile facts, skills, works, intro, contact request, video resume, sharing, and screenshots.

This keeps quality high while preventing Chinese text drift, numeric mistakes, fake QR codes, and non-interactive long images.

## Reference Image Decomposition

The reference image has the following reusable qualities:

| Area | Quality to Preserve | What Must Stay Native |
| --- | --- | --- |
| Top title area | large negative space, calligraphy mood, pale ink landscape, antique corner border | final title, actor name, selling points |
| Actor hero | right-side portrait, period costume, hair ornament, fan/prop, soft daylight | identity from actual source image |
| Background | Jiangnan bridge, distant mountains, pavilion, bamboo, rice-paper texture | any readable signage |
| Basic profile card | left lower blank bordered module, icon rhythm, light parchment | height, weight, city, skills text |
| Skills card | right lower blank bordered module, list rhythm | skill labels/descriptions |
| Works list | wide long card, 3 row structure | work names, roles, years, tags |
| Photo strip | 4-6 portrait thumbnail frames | actual profile/work photos rendered by frontend |
| Intro/stat cards | two bottom cards with blank text and four statistic columns | bio and numeric stats |
| Footer | calm lower area for contact/action UI | phone, WeChat, QR, share/contact buttons |

## Prompt Contract

`AiProfileCardPromptAgent` should emit both `promptJson` and `promptText`.

### Prompt JSON

Recommended shape:

```json
{
  "task": "image_to_image_actor_profile_card_background",
  "modelCode": "gpt-image-2",
  "templateSceneCode": "costume",
  "styleCode": "costume_actor_profile_full_card",
  "canvas": {
    "ratio": "9:16 vertical",
    "targetSize": "2160x3840",
    "renderIntent": "visual background asset for mini program native actor detail rendering"
  },
  "referenceQuality": {
    "benchmark": "premium Chinese period actor profile sheet ...",
    "qualityBar": "commercial casting-book finish ...",
    "importantConstraint": "leave every text-bearing area blank ..."
  },
  "fixedLayout": {
    "subjectBox": "hero right side ...",
    "heroTextSafeArea": "hero left side ...",
    "profilePanelRegion": "...",
    "skillsRegion": "...",
    "worksRegion": "...",
    "photoStripRegion": "...",
    "aboutRegion": "...",
    "statsRegion": "...",
    "footerRegion": "..."
  },
  "moduleAesthetics": [
    "thin antique-gold double-line page border ...",
    "warm ivory rice-paper/parchment texture ...",
    "misty Jiangnan ink-wash landscape ...",
    "abstract cinnabar seal shapes only ..."
  ],
  "profileSignals": {
    "gender": "female",
    "age": 24,
    "height": 168,
    "city": "上海",
    "skills": ["影视表演", "古装"]
  },
  "qualityChecklist": [
    "portrait identity is consistent with source image",
    "no readable words, phone numbers, QR codes, logos or watermarks",
    "all fixed layout regions remain open for deterministic mini-program component rendering"
  ]
}
```

Use `LinkedHashMap` or `Map.ofEntries` for maps with more than ten keys. Java `Map.of(...)` cannot hold more than ten pairs and will not compile.

### Prompt Text

The text prompt should be readable by model providers and model-agnostic. It should explicitly state:

- 2160x3840 vertical canvas.
- Reference image is actor identity source.
- Actor is placed on the right hero area.
- Left hero and lower modules remain blank for native text.
- The lower page uses premium empty dossier modules, not text-filled poster cards.
- Antique-gold borders, rice-paper texture, ink-wash landscape, bamboo, bridge, pavilion, and abstract seals define the style.
- No Chinese characters, letters, numbers, QR codes, logos, watermarks, contact info, or UI labels inside the generated image.

### Negative Prompt

The negative prompt should include:

```text
readable text, Chinese characters, English letters, random readable calligraphy,
filled profile text, phone number, QR code, watermark, brand logo, fake UI labels,
extra face, distorted face, deformed hands, cropped head, busy profile-card text regions,
dense decorations covering component regions, cheap fantasy costume, overly modern gradient poster
```

## Style Code Behavior

### `costume_actor_profile_full_card`

This style should be the direct reference-quality implementation. It should ask for:

- premium Chinese period actor dossier;
- right-side realistic portrait;
- Han/Tang costume cues without fantasy exaggeration;
- warm ivory parchment;
- ink-wash Jiangnan scene;
- antique-gold modular frames;
- blank profile/skills/works/about/stats cards;
- six portrait-thumbnail slots.

### Other Scene Codes

Other `templateSceneCode` values can keep their existing behavior, but should still obey:

- native text safety;
- fixed layout regions;
- no mock/source-image success exposure.

## Frontend Relationship

The current page `pkg-card/ai-profile-card-detail/index` remains the native detail page. The visual asset is a hero/cover layer and should not be treated as the only information surface.

Expected frontend responsibilities:

- use generated image as AI visual asset;
- render actor name and facts natively;
- render works/photos/intro/stats/video resume natively;
- share the AI detail page path and generated image as share cover;
- keep screenshot/share behavior page-based rather than static long-image based.

## Current Starting State

There is an in-progress backend prompt-agent change in `kaipaile-server` that should be preserved. It currently strengthens reference-quality language and tests, but the first test run exposed a Java compile blocker: a `Map.of(...)` call exceeded Java's ten-pair limit. Implementation should fix that with `LinkedHashMap` or `Map.ofEntries` before running the backend test suite.

## Acceptance Evidence

Implementation is complete only when evidence includes:

- prompt-agent unit test output;
- backend regression output;
- provider request payload shape sample without secrets;
- existing successful artifact detail E2E screenshot;
- fresh generation attempt result, or explicit provider-auth blocker if KPLYYK still returns `401 token_invalidated`.

