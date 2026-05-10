# AI Profile Card 750 Design Coordinate Contract Tasks

## Phase 1: Spec

- [x] Create requirements, design, and task tracking for the 750 design coordinate contract.

## Phase 2: Frontend Contract

- [x] Add explicit `750 x 1334` design canvas metadata.
- [x] Keep explicit `2160 x 3840` provider canvas metadata.
- [x] Convert AI profile card slots to design coordinates.
- [x] Scale share canvas drawing from design coordinates instead of provider pixels.
- [x] Strengthen frontend audit for the design/provider canvas split.

## Phase 3: Backend Agent Contract

- [x] Add design canvas and provider canvas to the prompt JSON.
- [x] Express fixed layout regions in design coordinates and provider coordinates.
- [x] Update prompt text to make `750 x 1334` the authoritative mini-program coordinate system.
- [x] Update backend prompt-agent tests.

## Phase 4: Verification

- [x] Run frontend AI profile audit.
- [x] Run frontend type-check.
- [x] Run frontend WeChat mini-program build.
- [x] Run backend prompt-agent tests.
- [x] Run 真人 E2E for available styles with real backend artifacts.
- [x] Record unavailable styles without marking them passed.

## Phase 5: Frame-Free Background Regression

- [x] Confirm existing `classic` and `costume` artifacts were reused and were not regenerated after the 750-coordinate prompt tightening.
- [x] Tighten backend agent prompt JSON and prompt text so every available style is full-bleed and frame-free.
- [x] Add backend prompt-agent tests for no-frame/no-document-page constraints.
- [x] Rebuild and test the backend prompt agent locally.
- [ ] Commit and push the prompt-contract change.
- [ ] Deploy the backend prompt-contract change before real regeneration.
- [ ] Regenerate affected styles through the real backend API.
- [ ] Run 真人 E2E against fresh artifacts and visually confirm no visible background frame, no foreground clipping, and no page deformation.

## Current Status

- The 750-coordinate contract completed a local verification pass for previously available styles.
- Overall completion is not complete because `commercial` and `artistic` remain unavailable in the protected test account, and `classic` / `costume` require fresh regenerated artifacts after the no-frame prompt contract is deployed.
