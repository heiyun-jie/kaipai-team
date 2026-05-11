# AI Profile Card Detail First-Screen Performance Requirements

## Context

The AI profile card detail page can take minutes to become usable on a real phone. Direct runtime checks show the API calls for the current route are fast, while the generated AI background image is a high-resolution `2160 x 3840` PNG of about 8.7 MB. The current page also starts duplicate hydration from `onLoad` and `onShow`, and waits for work that is not required for the first visible poster.

## Requirements

1. Opening `pkg-card/ai-profile-card-detail/index` must render the deterministic poster foreground from backend profile data without waiting for contact status, view-history recording, level refresh, or owner-only task fallback.
2. The detail page must not run duplicate hydrate cycles for the same `shareCardId + taskId + shared` route during initial page open.
3. The first-screen background image must use a display-sized derivative of the real backend-generated COS image, not the original multi-megabyte provider output.
4. The original generated image URL must remain available for explicit image preview and artifact identity checks.
5. Public/shared detail routes must not require a logged-in user session before the poster can render.
6. The implementation must not introduce mock data, fake generated URLs, or frontend provider shortcuts.
7. If the AI artifact API is available, the page should use it as the public generated-image fact source before any owner-only task endpoint.
8. Non-critical side effects such as contact status and view-history recording must run after first render and must not blank the page if they fail.
9. The page must preserve the existing 750 x 1334 logical poster layout and style preset behavior.
10. Verification must include type-check, WeChat mini-program build, and a real mini-program E2E timing check that records navigation, poster visibility, background URL, and share route.

## Non-Goals

- Do not change the AI provider output size or prompt contract in this spec.
- Do not regenerate AI images only to solve display latency.
- Do not change unrelated portfolio, contact, membership, or normal actor-card flows unless needed to avoid loading oversized AI image covers.
