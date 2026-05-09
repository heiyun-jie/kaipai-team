# Backend Only Release Record: AI Profile Card Image URL Persist

- Release id: `20260509-204642-backend-only-ai-profile-card-image-url-persist`
- Scope: `backend-only`
- Operator: `codex`
- Public smoke base: `https://api.kplyyk.com`
- Related spec: `.sce/specs/00-161-current-phase-ai-profile-card-portfolio-visibility-investigation`
- Backend commit: `48540b9 fix: persist AI profile card image urls`

## Purpose

Fix the runtime issue where the mini program could not reliably display AI generated share images.

The backend now:

- Downloads provider-returned generated image URLs and uploads them to configured COS before saving `generatedImageUrl`.
- Lazily mirrors existing successful external `generatedImageUrl` values to COS when task/artifact data is read.
- Updates the linked card config from the external generated image URL to the persisted COS URL.
- Accepts common KPLYYK response shapes such as `image_url` and `output`, including relative image paths.

## Execution

Command started:

```powershell
python .sce\runbooks\backend-admin-release\scripts\run-backend-only-release.py --label ai-profile-card-image-url-persist --operator codex --public-base-url https://api.kplyyk.com
```

The local wrapper timed out after 15 minutes while waiting on the SSH helper process. Follow-up checks showed the remote helper was no longer running, the new jar had been installed, and the backend process had restarted.

The local hanging SSH/Python process was then terminated after confirming no remote `kaipai-backend-release-helper` process remained.

## Remote Artifact

- Remote jar: `/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar`
- Remote jar modified time: `2026-05-09 20:47:45 +0800`
- Remote jar SHA256: `282211154850cdd6f8466945dc869d957b080cf4b49853739df053783de79ce0`
- Backend process check: `java -jar app.jar` running, elapsed `16m+` at post-check time.

## Post-Release Smoke

- `GET https://api.kplyyk.com/api/card/scene-templates`
  - HTTP status: `200`
  - business code: `200`
  - result: pass
- `GET https://api.kplyyk.com/api/ai/profile-card/artifacts`
  - HTTP status without auth: `401`
  - result: pass, authenticated list still requires login
- `GET https://api.kplyyk.com/api/ai/profile-card/artifacts/not-exists-probe`
  - HTTP status: `200`
  - business code: `400`
  - message: AI share image artifact does not exist
  - result: pass, public artifact detail route is reachable without auth and no longer blocked by security

## Review Conclusion

Deployment action completed and public smoke passed for the routes affected by this backend fix.

Known caveat: because the standard release wrapper timed out waiting for SSH closure, this record was completed manually from post-release evidence rather than emitted automatically by the script. The remote process and public API checks confirm the new backend jar is active.
