# AI Profile Card Agent Contract Documentation Requirements

## Context

The AI profile card flow has reached a product-design decision point. Recent real E2E evidence shows that letting one fixed frontend coordinate map cover every generated style is fragile, but letting the image model freely render final user data is also unsafe.

This spec creates the documentation and contract needed before the next implementation pass. The document must make the agent boundary explicit:

- The agent reads actor profile data and selected style.
- The agent produces structured display content, layout choice, and background-generation brief.
- The image model generates a visual background/template only.
- The mini-program or deterministic image renderer renders final text, photos, video entry, share cover, and contact actions.

The goal is not to immediately rewrite the implementation. The goal is to create a durable agent contract document that future backend, frontend, and QA work can follow.

## Requirements

### R1. Agent Responsibility Contract

The documentation MUST state that the agent owns:

- actor profile understanding;
- content prioritization;
- concise poster copy generation;
- style-aware wording;
- layout preset selection;
- image-background prompt generation;
- quality checklist generation;
- provider-independent prompt JSON.

The documentation MUST state that the agent does not own:

- final readable text rendering inside generated images;
- phone/contact rendering;
- QR code rendering;
- video player rendering;
- share button rendering;
- mini-program route behavior;
- direct user-visible mock success artifacts.

### R2. Deterministic Rendering Contract

The documentation MUST require final business content to be rendered by deterministic code, either:

- mini-program native components for interactive detail pages; or
- backend/frontend canvas composition for static share previews.

The image model MUST NOT be trusted to render final actor facts, Chinese text, work titles, numbers, phone, QR code, or contact data.

### R3. Structured Poster Content

The documentation MUST define a `posterContent` schema for agent output. At minimum it MUST include:

- identity;
- facts;
- skills;
- work summary;
- intro;
- photo slots;
- video resume reference;
- missing-data fallbacks;
- display limits;
- source fields used.

The schema MUST be concise enough to fit fixed visual slots and MUST reject half-sentence clipping.

### R4. Layout Preset Contract

The documentation MUST require per-style `layoutPreset` definitions instead of one global coordinate map.

Every layout preset MUST define:

- canvas size and ratio;
- subject/portrait box;
- identity slot;
- facts slot;
- skills slot;
- works slot;
- photo strip slot;
- intro/about slot;
- video slot;
- safe footer/action area;
- text theme;
- maximum lines and item counts;
- screenshot/share requirements.

The documentation MUST include at least these presets as target contracts:

- `costume_profile_v1`;
- `classic_profile_v1`;
- `urban_profile_v1`;
- `commercial_profile_v1`;
- `artistic_profile_v1`.

### R5. Image Background Prompt Contract

The documentation MUST define the prompt contract for background generation:

- target size `2160x3840`;
- no readable final text;
- no phone numbers;
- no QR codes;
- no logos or watermarks;
- visible empty frame/panel regions for the selected layout;
- actor identity preservation from the source image;
- provider-independent prompt JSON;
- negative prompt requirements.

The documentation MUST clarify that the model may create decorative frames, ornaments, paper texture, lighting, background atmosphere, and blank photo/video placeholders, but must not fill them with final business data.

### R6. Quality Gate and Regeneration Policy

The documentation MUST define how a generated background is accepted or rejected:

- all required layout regions are visible or otherwise safely renderable;
- text contrast can be satisfied by the selected text theme;
- portrait does not cover reserved business slots;
- no model-generated readable text appears;
- image is not a source-image echo;
- provider is not mock;
- generated asset is stored and linked to the task/share card.

The documentation SHOULD define a future regeneration policy for failed layout compliance.

### R7. Privacy and Data-Minimization

The documentation MUST state that contact phone, private notes, tokens, and raw authorization data must never be sent to the image provider.

Profile signals sent to the model MUST be minimized and used only to guide visual style, not to render final text.

### R8. Style Coverage

The documentation MUST include a style verification matrix for:

- costume;
- urban;
- classic;
- commercial;
- artistic.

For each style, it MUST specify expected evidence:

- generated task ID;
- provider/model;
- background image tail;
- screenshot of detail page;
- share payload;
- slot position assertions;
- visual review notes.

If a style is unavailable for the current account, the documentation MUST record the blocker instead of silently marking it covered.

### R9. No Mock or Free-Form Final Image Regression

The documentation MUST explicitly prohibit:

- frontend mock generation;
- source image fallback as successful AI artifact;
- hardcoded generated image URLs in the mini-program;
- a provider-generated full poster with final Chinese actor text as the default mode.

### R10. Delivery Artifacts

This spec is complete when it creates an implementation-ready documentation plan covering:

- requirements;
- design;
- tasks;
- acceptance evidence;
- open decisions.

The later implementation pass SHOULD create or update the durable agent contract document in a stable docs location, such as `docs/ai-profile-card-agent-contract.md` or an equivalent project-approved path.

## Non-Goals

- Do not implement the new agent schema in this spec.
- Do not change backend database schema in this spec.
- Do not rework mini-program detail rendering in this spec.
- Do not trigger new provider generation in this spec.
- Do not remove current working AI detail behavior while the contract is being documented.
