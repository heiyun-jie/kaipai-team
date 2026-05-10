# AI Profile Card Style Stability And E2E Quality Gate Tasks

## Phase 1: Deep Investigation And Spec

- [x] Inspect current frontend AI detail page, layout presets, portfolio route, and audit script.
- [x] Inspect current backend prompt agent, provider call path, task persistence, and DTOs.
- [x] Inspect existing E2E screenshots and identify why old checks passed visually bad output.
- [x] Create this spec with requirements, design, and task tracking.
- [ ] Commit and push the new spec after review.

## Phase 2: Root-Cause Fix Plan

- [x] Define per-style frontend preset schema with slots, limits, text theme, panel theme, and colors.
- [x] Define matching backend prompt style contract for every style.
- [x] Decide which current acceptance gaps remain explicit follow-ups instead of being marked complete.

## Phase 3: Frontend Style Stability

- [x] Replace cloned global slot presets with dedicated style presets.
- [x] Render poster blocks and photo strip from preset slot styles instead of hardcoded CSS percentages.
- [x] Apply preset-driven style variables for panel, text, chip, and video colors.
- [x] Ensure urban/artistic do not use parchment-looking panels unless their generated background is light-zone compatible.
- [x] Ensure poster uses stable 9:16 responsive dimensions without horizontal clipping.
- [x] Ensure share canvas uses the same preset theme values as detail rendering.
- [ ] Keep legacy artifact fallback working.

## Phase 4: Backend Agent Stability

- [x] Add backend style preset/prompt contract.
- [x] Refactor `AiProfileCardPromptAgent` to generate prompts from the resolved style contract.
- [x] Remove global古风/parchment wording from non-costume/non-classic styles.
- [x] Include layout preset, text theme, panel theme, and safe-zone coordinates in provider prompt JSON.
- [x] Add unit tests covering all five styles and privacy/no-final-text constraints.

## Phase 5: Audit And Test Gate

- [x] Strengthen frontend audit to fail when styles share only a cloned base preset.
- [x] Strengthen frontend audit to require preset-driven slot binding in the detail page.
- [x] Strengthen frontend audit to require all five style presets.
- [ ] Add or update E2E evidence validation so old mechanical screenshots cannot produce overall pass without manual/style verdicts.
- [x] Run frontend audit.
- [x] Run frontend type-check.
- [x] Run frontend WeChat mini-program build.
- [x] Run backend prompt-agent tests.

## Phase 6: 真人 E2E Simulation

- [x] Start or connect WeChat DevTools.
- [x] Use real authorization/session context, no frontend mock.
- [x] Verify portfolio lists backend AI artifacts.
- [x] Verify portfolio AI artifact click opens `pkg-card/ai-profile-card-detail/index`.
- [x] Verify share path points to AI detail page.
- [x] Verify share image is composed with deterministic foreground.
- [x] Capture and review `classic`.
- [x] Capture and review `costume`.
- [x] Capture and review `urban`.
- [ ] Capture and review `commercial`.
- [ ] Capture and review `artistic`.
- [x] Record unavailable/locked styles with evidence and do not count them as passed.
- [x] Confirm no content is incomplete or clipped in each available style.
- [x] Confirm no generated image/front-end style conflict in each available style.
- [x] Confirm no front-end deformation in each available style.

## Phase 7: Acceptance And Delivery

- [ ] Update this task list only for items actually completed.
- [ ] Commit and push frontend changes.
- [ ] Commit and push backend changes.
- [ ] Commit and push final spec status update.
- [ ] Provide final report with commits, evidence paths, styles passed, unavailable blockers, and any remaining open risks.

## Current Status

- Investigation confirms the instability is multi-source: backend prompt style drift, cloned frontend slot map, shallow foreground theming, and weak E2E gates.
- New spec has been created.
- First implementation pass is complete for frontend per-style presets/themes, backend per-style prompt contracts, and automated source/build checks.
- 真人 E2E passed for the three styles currently exposed to the protected account:
  - `classic`;
  - `costume`;
  - `urban`.
- `commercial` and `artistic` are not exposed by `/api/card/my-cards` for this account, so they are recorded as unavailable and not counted as passed.
- Evidence:
  - `output/ai-profile-card-e2e/style-stability-e2e-summary.json`;
  - `output/ai-profile-card-e2e/style-stability-e2e-portfolio.png`;
  - `output/ai-profile-card-e2e/style-stability-e2e-classic.png`;
  - `output/ai-profile-card-e2e/style-stability-e2e-costume.png`;
  - `output/ai-profile-card-e2e/style-stability-e2e-urban.png`.
- Overall completion remains incomplete because `commercial` and `artistic` could not be tested in this account and the new backend prompt contract still needs deployed real-provider generation verification.
