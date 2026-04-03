# Preview Overlay Static Audit 20260403-122158-preview-overlay-static-audit-single-query-entry

- Generated At: `2026-04-03T12:21:58`
- Frontend Root: `D:\XM\kaipai-team\kaipai-frontend\src`
- Passed: `True`
- Total Findings: `0`

## Rules

- Query key literals `['previewAccent', 'previewBackground', 'previewLayout', 'previewPrimary']` only allowed in `utils/personalization.ts`
- Session storage literal `kp:personalization-preview-overlay-session` only allowed in `utils/personalization.ts`
- Preview overlay helpers must stay within the approved file set

## Touchpoints

- `pages/actor-profile/detail.vue` -> helpers=`PersonalizationPreviewOverlay, readPersonalizationPreviewOverlaySession, applyPersonalizationPreviewOverlay`
- `pkg-card/actor-card/index.vue` -> helpers=`PersonalizationPreviewOverlay, readPersonalizationPreviewOverlay, readPersonalizationPreviewOverlaySession, writePersonalizationPreviewOverlaySession, diffPersonalizationPreviewOverlay, applyPersonalizationPreviewOverlay`
- `pkg-card/invite/index.vue` -> helpers=`readPersonalizationPreviewOverlaySession, applyPersonalizationPreviewOverlay`
- `types/personalization.ts` -> helpers=`PersonalizationPreviewOverlay`
- `utils/personalization.ts` -> helpers=`PersonalizationPreviewOverlay, readPersonalizationPreviewOverlay, readPersonalizationPreviewOverlaySession, writePersonalizationPreviewOverlaySession, diffPersonalizationPreviewOverlay, applyPersonalizationPreviewOverlay`

## Findings

- No findings

## Artifacts

- `captures/preview-overlay-static-audit.json`
- `summary.md`

