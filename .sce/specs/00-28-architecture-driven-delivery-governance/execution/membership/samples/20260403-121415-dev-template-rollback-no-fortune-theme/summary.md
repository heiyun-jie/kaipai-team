# Admin Template Rollback Mini Program No Fortune Theme 20260403-121415-dev-template-rollback-no-fortune-theme

- Generated At: `2026-04-03T12:16:35`
- Source Sample: `20260402-212713-dev-fortune-theme-lv5-unlock`
- Chain Script: `run-admin-template-rollback-mini-program-chain.py`
- Mode: `force-disable-fortune-theme + restore-original-fortune-theme`

## Artifacts

- `captures/no-fortune-theme-chain.stdout.log`
- `captures/no-fortune-theme-chain.stderr.log`
- `captures/admin-template-rollback-mini-program-results.json`
- `captures/admin-template-rollback-mini-program-db.txt`
- `captures/mini-program-screenshot-capture-before-rollback.json`
- `captures/mini-program-screenshot-capture-after-rollback.json`
- `captures/mini-program-screenshot-capture-after-restore.json`
- `admin-template-rollback-mini-program-summary.md`

## Chain Output

```json
{
  "sampleRoot": "D:\\XM\\kaipai-team\\.sce\\specs\\00-28-architecture-driven-delivery-governance\\execution\\membership\\samples\\20260403-121415-dev-template-rollback-no-fortune-theme",
  "before": {
    "membershipTier": "member",
    "level": 5,
    "reasonCodes": [],
    "templateStatus": 1,
    "templateName": "Smoke Template",
    "templateRequiredLevel": 1,
    "templateThemePrimary": "#7A3E2B",
    "personalizationThemeId": "general-member-base",
    "personalizationThemePrimary": "#FF6B35",
    "artifactCount": 4,
    "publishVersion": "SMOKE_RESTORE_MP_20260403_120307",
    "publishLogId": 21
  },
  "afterRollback": {
    "membershipTier": "member",
    "level": 5,
    "reasonCodes": [],
    "templateStatus": 2,
    "templateName": "通用",
    "templateRequiredLevel": 1,
    "templateThemePrimary": "#ff7a45",
    "personalizationThemeId": "general-member-base",
    "personalizationThemePrimary": "#FF6B35",
    "artifactCount": 4,
    "publishVersion": "SMOKE_RESTORE_MP_20260403_120307",
    "publishLogId": 22
  },
  "afterRestore": {
    "membershipTier": "member",
    "level": 5,
    "reasonCodes": [],
    "templateStatus": 1,
    "templateName": "Smoke Template",
    "templateRequiredLevel": 1,
    "templateThemePrimary": "#7A3E2B",
    "personalizationThemeId": "general-member-base",
    "personalizationThemePrimary": "#FF6B35",
    "artifactCount": 4,
    "publishVersion": "SMOKE_RESTORE_MP_20260403_121416",
    "publishLogId": 23
  },
  "miniProgramBefore": {
    "captureLabel": "before-rollback",
    "themeId": "general-member-base",
    "themePrimary": "#FF6B35",
    "reasonCodes": [],
    "actorCardPath": "/pkg-card/actor-card/index?actorId=10000&scene=general&shared=1&artifact=miniProgramCard&themeId=general-member-base&tone=warm",
    "actorCardQuery": {
      "actorId": "10000",
      "scene": "general",
      "shared": "1",
      "artifact": "miniProgramCard",
      "themeId": "general-member-base",
      "tone": "warm"
    },
    "detailPath": "/pages/actor-profile/detail?actorId=10000&scene=general&themeId=general-member-base&shared=1",
    "detailQuery": {
      "actorId": "10000",
      "scene": "general",
      "themeId": "general-member-base",
      "shared": "1"
    },
    "invitePath": "/pkg-card/invite/index?actorId=10000&scene=general&artifact=inviteCard&themeId=general-member-base&shared=1&tone=warm",
    "inviteQuery": {
      "actorId": "10000",
      "scene": "general",
      "artifact": "inviteCard",
      "themeId": "general-member-base",
      "shared": "1",
      "tone": "warm"
    },
    "manifestName": "mini-program-screenshot-capture-before-rollback.json"
  },
  "miniProgramAfterRollback": {
    "captureLabel": "after-rollback",
    "themeId": "general-member-base",
    "themePrimary": "#FF6B35",
    "reasonCodes": [],
    "actorCardPath": "/pkg-card/actor-card/index?actorId=10000&scene=general&shared=1&artifact=miniProgramCard&themeId=general-member-base&tone=warm",
    "actorCardQuery": {
      "actorId": "10000",
      "scene": "general",
      "shared": "1",
      "artifact": "miniProgramCard",
      "themeId": "general-member-base",
      "tone": "warm"
    },
    "detailPath": "/pages/actor-profile/detail?actorId=10000&scene=general&themeId=general-member-base&shared=1",
    "detailQuery": {
      "actorId": "10000",
      "scene": "general",
      "themeId": "general-member-base",
      "shared": "1"
    },
    "invitePath": "/pkg-card/invite/index?actorId=10000&scene=general&artifact=inviteCard&themeId=general-member-base&shared=1&tone=warm",
    "inviteQuery": {
      "actorId": "10000",
      "scene": "general",
      "artifact": "inviteCard",
      "themeId": "general-member-base",
      "shared": "1",
      "tone": "warm"
    },
    "manifestName": "mini-program-screenshot-capture-after-rollback.json"
  },
  "miniProgramAfterRestore": {
    "captureLabel": "after-restore",
    "themeId": "general-member-base",
    "themePrimary": "#FF6B35",
    "reasonCodes": [],
    "actorCardPath": "/pkg-card/actor-card/index?actorId=10000&scene=general&shared=1&artifact=miniProgramCard&themeId=general-member-base&tone=warm",
    "actorCardQuery": {
      "actorId": "10000",
      "scene": "general",
      "shared": "1",
      "artifact": "miniProgramCard",
      "themeId": "general-member-base",
      "tone": "warm"
    },
    "detailPath": "/pages/actor-profile/detail?actorId=10000&scene=general&themeId=general-member-base&shared=1",
    "detailQuery": {
      "actorId": "10000",
      "scene": "general",
      "themeId": "general-member-base",
      "shared": "1"
    },
    "invitePath": "/pkg-card/invite/index?actorId=10000&scene=general&artifact=inviteCard&themeId=general-member-base&shared=1&tone=warm",
    "inviteQuery": {
      "actorId": "10000",
      "scene": "general",
      "artifact": "inviteCard",
      "themeId": "general-member-base",
      "shared": "1",
      "tone": "warm"
    },
    "manifestName": "mini-program-screenshot-capture-after-restore.json"
  }
}
```

