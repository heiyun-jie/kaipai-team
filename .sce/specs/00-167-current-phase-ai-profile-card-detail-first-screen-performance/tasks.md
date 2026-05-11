# AI Profile Card Detail First-Screen Performance Tasks

## Phase 1: Investigation And Spec

- [x] Measure current public detail API latency.
- [x] Measure current generated background image size and derivative size.
- [x] Identify duplicate hydrate and non-critical request coupling in `pkg-card/ai-profile-card-detail/index`.
- [x] Create requirements, design, and task tracking for first-screen performance.

## Phase 2: Frontend Fix

- [x] Add display-sized COS derivative URL handling for AI generated backgrounds.
- [x] Keep original generated image URL for preview and artifact checks.
- [x] Split critical poster hydration from contact/history side effects.
- [x] Remove initial `onLoad`/`onShow` duplicate hydrate for the same route.
- [x] Avoid owner-only task fallback on shared public routes.

## Phase 3: Verification

- [x] Run frontend type-check.
- [x] Run WeChat mini-program build.
- [x] Run real mini-program E2E timing check for AI detail page.
- [x] Record evidence path and measured first-screen timings.

## Current Status

- Direct public API checks were fast for personalization and artifact lookup.
- Current AI artifact background was measured at about 8.7 MB as the original PNG.
- COS image-processing derivatives were measured as much smaller than the original image and are now used for display rendering.
- Frontend type-check passed.
- WeChat mini-program build passed and synced to `dist/dev/mp-weixin`.
- Real mini-program E2E passed:
  - evidence JSON: `output/ai-profile-card-e2e/detail-first-screen-performance.json`;
  - screenshot: `output/ai-profile-card-e2e/detail-first-screen-performance.png`;
  - route: `/pkg-card/ai-profile-card-detail/index?shareCardId=18&shared=1&taskId=aipf_e52d00139d1045ad94760a311431b65b`;
  - navigation: `4567ms`;
  - identity visible after navigation: `5ms`;
  - display background derivative visible after navigation: `8ms`;
  - background URL includes `imageMogr2/thumbnail/1080x1920!/format/jpg/quality/85`;
  - preview still uses the original backend artifact URL;
  - share payload omits custom `imageUrl` and keeps the AI detail path.
