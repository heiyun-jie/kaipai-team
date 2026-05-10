# Backend Release Record

## Basic Information

- Release id: `20260510-102739-backend-only-ai-profile-card-reference-quality-agent`
- Released at: `2026-05-10 10:28:31 +0800`
- Scope: `backend-only`
- Operator: `codex`
- Related work:
  - AI profile card reference-quality prompt-agent upgrade
  - `.sce/specs/00-162-current-phase-ai-profile-card-agent-reference-quality/`

## Artifact

- Backend project: `D:\XM\kaipai-team\kaipaile-server`
- Built jar: `target\kaipai-backend-1.0.0-SNAPSHOT.jar`
- Local jar SHA256: `3D1E6255A962CF9D16CFF101F02F1C7DFD51EA764EF80854D57E982EFEC93D51`
- Remote jar SHA256: `3D1E6255A962CF9D16CFF101F02F1C7DFD51EA764EF80854D57E982EFEC93D51`
- Container `/app/app.jar` SHA256: `3D1E6255A962CF9D16CFF101F02F1C7DFD51EA764EF80854D57E982EFEC93D51`

## Execution Summary

- Ran the standard backend-only release process.
- Rebuilt and recreated the backend container.
- Public smoke against `https://api.kplyyk.com` passed for API documentation availability.
- Backend container started successfully after deployment.
- No rollback was executed.

## Runtime Notes

- Runtime provider configuration was present for AI profile card generation.
- Sensitive runtime values, including database passwords, Redis passwords, provider tokens, and admin access tokens, are intentionally omitted from this record.

## Post-Release Verification

- Backend prompt-agent tests had passed before release:
  - `mvn -q -Dtest=AiProfileCardPromptAgentTest test`
  - `mvn -q test`
- Fresh protected AI profile card generation reached the real provider path after release:
  - `taskId=aipf_00ee0c0ec3b84fd1b48e7fc064bb79f7`
  - `templateSceneCode=costume`
  - `styleCode=costume_actor_profile_full_card`
  - `providerCode=kplyyk`
  - `modelCode=gpt-image-2`
- The fresh generation failed before image output because the KPLYYK provider returned `401 token_invalidated`.
- No mock fallback artifact was exposed.

## E2E Display Guard

- Existing successful artifact detail/share E2E was rerun to guard the mini-program display path:
  - `shareCardId=18`
  - `taskId=aipf_53cd81ac506841799fc98fb496b5b46d`
  - route `/pkg-card/ai-profile-card-detail/index?shareCardId=18&shared=1&taskId=aipf_53cd81ac506841799fc98fb496b5b46d`
  - generated image tail `f9f56e0596aa498e9202a9910f2bcbd3.png`
  - native actor name rendered as `林夏`
  - native sections rendered for skills, works, photos, intro, and video resume
  - share path retained the AI detail route and task id
- Screenshot evidence:
  - `output/ai-profile-card-e2e/post-agent-release-existing-artifact.png`

## Current Conclusion

- The prompt-agent quality contract is upgraded, tested, pushed, and deployed.
- The mini-program AI detail/share display path works for a persisted AI artifact.
- A new real generated image cannot be quality-certified against the reference image until the KPLYYK provider credential is refreshed, because the provider rejects the request before producing output.
