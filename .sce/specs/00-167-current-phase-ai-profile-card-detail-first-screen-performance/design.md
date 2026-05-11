# AI Profile Card Detail First-Screen Performance Design

## Root Cause

The slow phone render has three contributing factors:

- The detail page displays the provider output PNG directly. Current real artifacts can be about 8.7 MB, which is too heavy for first-screen mobile rendering.
- `onLoad` starts `hydratePage`, then `onShow` can immediately start the same hydrate again after `shareCardId` is assigned.
- The hydrate flow mixes first-screen data with non-critical work: session bootstrap, level refresh, contact status, and view-history recording.

## Design

The detail page keeps two image URLs:

- `generatedImageUrl`: the original backend artifact URL, used for preview and artifact identity.
- `displayGeneratedImageUrl`: a COS image-processing derivative used only by the `<image>` background.

For COS PNG/JPG URLs without an existing query string, the display derivative appends:

```text
?imageMogr2/thumbnail/1080x1920!/format/jpg/quality/85
```

This keeps the visible 9:16 background aligned with the 750 x 1334 mini-program poster while reducing first-screen bytes from multi-megabyte PNGs to a display-sized derivative. Non-COS or already-query-bearing URLs fall back to the original URL.

Hydration is split into:

- critical path: route validation, storage-only session initialization, personalization snapshot, actor/config/theme assignment, share path setup, public AI artifact lookup;
- non-critical path: contact status and view-history recording after the poster is visible;
- optional owner fallback: owner-only task lookup only when the public artifact endpoint cannot resolve and the page is not a shared public route.

A route key prevents the initial `onLoad`/`onShow` duplicate hydrate for the same route. A sequence id prevents stale async work from overwriting newer route state.

## Quality Gate

Passing this spec requires:

- source audit confirms no duplicate initial hydrate and no direct oversized image binding;
- type-check passes;
- WeChat mini-program build passes;
- E2E records that the poster appears quickly, the background `<image>` uses the COS derivative URL, the original preview URL remains the backend artifact URL, and the share path still points to AI detail.
