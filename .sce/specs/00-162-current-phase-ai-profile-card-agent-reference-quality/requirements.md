# AI Profile Card Agent Reference Quality Requirements

## Context

This spec hardens the AI profile card agent against the reference document `wechat-miniapp-actor-detail-agent-spec.md` and the provided high-quality Chinese period actor profile image.

The reference image is a quality and structure benchmark, not a request to make the model render final business text. The active product contract remains:

- Backend reads the actor profile and selected style.
- Backend prompt agent prepares a model-independent visual brief.
- Backend provider calls the real image model.
- Backend stores the generated asset and exposes it as an AI artifact.
- Mini-program detail page renders accurate text, contacts, video resume, and share interaction with native components.

## Requirements

### R1. Output Mode

- The default output mode MUST remain `miniapp-components`.
- The model MUST generate a visual asset/background layer only.
- The model MUST NOT be responsible for final readable Chinese text, phone numbers, QR codes, contact buttons, or share UI.
- Single long-image generation MAY exist only as an explicit future mode and MUST NOT replace the current default detail page path.

### R2. Reference Quality Target

For `styleCode=costume_actor_profile_full_card`, the agent MUST describe the provided reference quality in model-independent terms:

- warm ivory rice-paper or parchment texture;
- pale ink-wash landscape with bridge, distant mountains, pavilion/garden architecture, and bamboo details;
- right-side Chinese period actor portrait with refined costume/hair ornament details;
- antique-gold double-line border and small corner ornaments;
- cinnabar seal-like accents as abstract shapes only;
- modular dossier-card structure for basic profile, skills, works, photos, intro, and stats;
- commercial casting-book polish, realistic facial detail, restrained decoration, and readable negative space.

### R3. Fixed Layout Contract

The agent MUST emit fixed 2160x3840 layout regions that the frontend can rely on:

- hero actor region on the right;
- hero text-safe region on the left;
- basic profile card region;
- skills card region;
- works list region;
- more photos strip region;
- about card region;
- stats card region;
- footer/contact-safe region.

Every text-bearing region MUST be described as blank, low-contrast, and safe for native mini-program text.

### R4. Native Text Safety

The prompt and negative prompt MUST explicitly reject:

- readable Chinese characters;
- random calligraphy intended as text;
- English letters;
- numbers;
- filled profile text;
- phone numbers;
- QR codes;
- logos and watermarks;
- fake UI labels;
- decorations that cover component regions.

Abstract seals, divider strokes, icon-like ornaments, and pale text guide lines MAY be allowed only if they are not readable and do not compete with native components.

### R5. Actor Identity and Photo Consistency

The agent MUST use the input/source actor image as identity reference and instruct the model to preserve:

- recognizable face;
- age impression;
- natural skin texture;
- hairstyle direction;
- realistic proportions;
- clean hands, eyes, hairline, and costume edges.

The agent SHOULD use profile signals such as gender, age, city, body type, hair style, skills, and works only to guide visual mood and costume suitability. These values MUST NOT be rendered as text in the image.

### R6. Provider Independence

The prompt contract MUST be portable across image models such as gpt-image-2, Doubao-style image models, or future providers:

- core brief is stored as structured JSON;
- prompt text summarizes the same constraints in plain language;
- provider payload includes `styleCode`, `templateSceneCode`, `sourceImageUrl`, `promptText`, `negativePrompt`, and `promptJson`;
- no model-specific hidden assumptions are required for quality.

### R7. Regression Coverage

Backend tests MUST verify that `AiProfileCardPromptAgent` includes:

- `targetSize=2160x3840`;
- the selected `styleCode`;
- `referenceQuality`;
- fixed regions for profile, skills, works, photos, about, stats, and footer;
- reference-image identity preservation;
- native component rendering statement;
- negative prompt clauses for readable text, random readable calligraphy, filled profile text, QR code, and watermark.

### R8. No Mock Exposure

No implementation step may reintroduce mock image artifacts as successful user-visible AI outputs. If the provider fails, the task MUST fail closed and the frontend MUST not present the source image as an AI-generated success.

### R9. Verification

Before completion, the implementation MUST pass:

- targeted backend unit tests for the prompt agent;
- backend test suite or the project-approved backend regression subset;
- API smoke for prompt/provider request shape where feasible;
- real detail-page E2E using an existing successful artifact;
- fresh generation E2E only after valid provider authentication is available.

## Non-Goals

- Do not redesign the entire mini-program detail page in this spec.
- Do not make the image model render final actor profile text.
- Do not change portfolio routing unless needed to preserve AI artifact visibility.
- Do not add large new dependencies.

