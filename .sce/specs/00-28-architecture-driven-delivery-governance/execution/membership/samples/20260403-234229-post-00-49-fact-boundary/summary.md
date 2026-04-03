# Preview Overlay Static Audit 20260403-234229-post-00-49-fact-boundary

- Generated At: `2026-04-03T23:42:29`
- Frontend Root: `D:\XM\kaipai-team\kaipai-frontend\src`
- Passed: `True`
- Total Findings: `0`

## Rules

- Query key literals `['previewAccent', 'previewBackground', 'previewLayout', 'previewPrimary']` must not appear anywhere in frontend runtime code
- Session storage literal `kp:personalization-preview-overlay-session` only allowed in `utils/personalization.ts`
- Preview overlay helpers must stay within the approved file set

## Touchpoints

- `pages/actor-profile/detail.vue` -> helpers=`readPersonalizationPreviewOverlaySession, applyPersonalizationPreviewOverlay`
- `pkg-card/actor-card/index.vue` -> helpers=`PersonalizationPreviewOverlay, readPersonalizationPreviewOverlaySession, writePersonalizationPreviewOverlaySession, diffPersonalizationPreviewOverlay, applyPersonalizationPreviewOverlay`
- `types/personalization.ts` -> helpers=`PersonalizationPreviewOverlay`
- `utils/personalization.ts` -> helpers=`PersonalizationPreviewOverlay, readPersonalizationPreviewOverlaySession, writePersonalizationPreviewOverlaySession, diffPersonalizationPreviewOverlay, applyPersonalizationPreviewOverlay`

## Findings

- No findings

## Artifacts

- `captures/preview-overlay-static-audit.json`
- `summary.md`

