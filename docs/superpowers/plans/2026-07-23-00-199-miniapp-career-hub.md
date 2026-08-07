# 00-199 Mini-Program Career Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the mini-program Career Hub, simplified profile editor, profile subpackage, record/favorites experience, and verified user-driven import review flow on top of the new backend contracts.

**Architecture:** Keep `pages/mine/index` and `pages/actor-profile/edit` in the main package; route list-heavy profile operations into `pkg-profile`; retain import source text only in non-persisted Pinia state; use API contracts from Plans 1 and 2 without falling back to legacy aggregate profile writes.

**Tech Stack:** uni-app 3, Vue 3.4 Composition API, TypeScript strict mode, Pinia, SCSS `$kp-*` tokens, WeChat Mini Program APIs.

---

## Preconditions And File Map

Execute this plan after Plan 1 exposes the profile/work/asset/favorite APIs and Plan 2 exposes capability/extract/apply. Before changing rendered UI, read and use `mp-ui-change-verification`; do not place `pkg-profile` imports in a main-package module.

- Modify: `kaipai-frontend/src/pages.json`
- Modify: `kaipai-frontend/src/utils/request.ts`
- Modify: `kaipai-frontend/src/api/actor.ts`
- Modify: `kaipai-frontend/src/types/actor.ts`
- Modify: `kaipai-frontend/src/api/history.ts`
- Modify: `kaipai-frontend/src/types/history.ts`
- Modify: `kaipai-frontend/src/pages/mine/index.vue`
- Modify: `kaipai-frontend/src/pages/history/index.vue`
- Modify: `kaipai-frontend/src/pages/actor-profile/edit.vue`
- Modify: `kaipai-frontend/src/pages/actor-profile/components/BasicInfoSection.vue`
- Modify: `kaipai-frontend/src/pages/actor-profile/components/SkillTagSection.vue`
- Modify: `kaipai-frontend/src/pages/actor-profile/components/AppearanceTagSection.vue`
- Modify: `kaipai-frontend/src/pkg-card/favorites/index.vue`
- Modify: `kaipai-frontend/src/pages/actor-profile/detail.vue`
- Modify: `kaipai-frontend/src/pkg-card/actor-card/index.vue`
- Modify: `kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue`
- Create: `kaipai-frontend/src/pkg-tools/settings/index.vue`
- Create: `kaipai-frontend/src/pkg-profile/import-review/index.vue`
- Create: `kaipai-frontend/src/pkg-profile/works/index.vue`
- Create: `kaipai-frontend/src/pkg-profile/work-edit/index.vue`
- Create: `kaipai-frontend/src/pkg-profile/assets/index.vue`
- Create: `kaipai-frontend/src/types/profile.ts`
- Create: `kaipai-frontend/src/types/actor-work.ts`
- Create: `kaipai-frontend/src/types/actor-asset.ts`
- Create: `kaipai-frontend/src/types/profile-import.ts`
- Create: `kaipai-frontend/src/types/share-card-favorite.ts`
- Create: `kaipai-frontend/src/api/profile-import.ts`
- Create: `kaipai-frontend/src/api/actor-work.ts`
- Create: `kaipai-frontend/src/api/actor-asset.ts`
- Create: `kaipai-frontend/src/api/share-card-favorite.ts`
- Create: `kaipai-frontend/src/stores/profile-import.ts`
- Create: `kaipai-frontend/src/stores/record-navigation.ts`
- Create: `.sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs`

## Contracts Used By This Plan

```ts
export interface ApiErrorShape extends Error {
  code?: number
  errorCode?: string
}

export interface ProfileImportContextVersion {
  profileVersion: number
  workLibraryVersion: number
}

export interface ProfileImportCapability {
  enabled: boolean
  available: boolean
  providerCode: 'deepseek'
  modelName: string | null
  maxInputLength: number | null
  unavailableReason: string | null
}
```

The import page maps numeric codes `46001-46017` in one local function and never compares the response message. `rawText` exists only in `useProfileImportStore`; the store has no persisted-state plugin and must call `clear()` on a completed apply or page unload.

## Task 1: Add Static UI Gate And Stable Request Error

**Files:**
- Modify: `kaipai-frontend/src/utils/request.ts`
- Create: `.sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs`

- [ ] **Step 1: Write the static gate before UI changes**

```js
const source = await readText('kaipai-frontend/src/pages/mine/index.vue')
assertNoMatch(source, /analytics|trendHeights|openMyQrCode|我的二维码/)

const edit = await readText('kaipai-frontend/src/pages/actor-profile/edit.vue')
assertNoMatch(edit, /updateActorProfile\(|PhotoCategorySection|WorkExperienceSection|PdfResumeSection|VideoResumeSection/)

const importPage = await readText('kaipai-frontend/src/pkg-profile/import-review/index.vue')
assertMatch(importPage, /beginClipboardRead[\s\S]*uni\.getClipboardData/)
assertNoMatch(importPage, /onLoad[\s\S]*getClipboardData/)
```

- [ ] **Step 2: Run the red static gate**

Run:

```powershell
node .sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: FAIL because the current Mine page still contains analytics and the new import page does not exist.

- [ ] **Step 3: Preserve API errors without parsing messages**

```ts
export class ApiError extends Error {
  constructor(
    message: string,
    readonly code?: number,
    readonly errorCode?: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

throw new ApiError(response.message || '请求失败', response.code, response.errorCode)
```

Do not change success response handling. Update the static gate so it verifies that `request.ts` constructs `ApiError` with `response.code`.

- [ ] **Step 4: Run the static gate again**

Run:

```powershell
node .sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: it continues to fail only for the not-yet-replaced pages and confirms the request layer test section passes.

- [ ] **Step 5: Commit the test scaffold and error contract**

```powershell
git add kaipai-frontend/src/utils/request.ts .sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs
git commit -m "test(miniapp): add career hub static gate"
```

## Task 2: Add API Types, Non-Persisted Stores, And Routes

**Files:**
- Modify: `kaipai-frontend/src/pages.json`
- Modify: `kaipai-frontend/src/api/actor.ts`
- Modify: `kaipai-frontend/src/types/actor.ts`
- Create: all `src/types/*.ts`, `src/api/*.ts`, and `src/stores/*.ts` paths listed above

- [ ] **Step 1: Write type-level red checks**

```ts
const draft = useProfileImportStore()
draft.setRawText('演员王火火 170/45kg')
expect(draft.rawText).toBe('演员王火火 170/45kg')
draft.clear()
expect(draft.rawText).toBe('')

const intent = useRecordNavigationStore()
intent.openFavorites()
expect(intent.consumeSegment()).toBe('favorites')
expect(intent.consumeSegment()).toBeNull()
```

Place these assertions in the static verification script when the repository has no unit-test runner for Pinia. The script must also parse `pages.json` and assert the `pkg-profile` subpackage contains exactly `import-review/index`, `works/index`, `work-edit/index`, and `assets/index`.

Define work provenance as a read-only response field, separate from import-candidate evidence:

```ts
export type ActorWorkSourceType = 'manual' | 'import' | 'migration'

export interface ActorWorkSave {
  projectName: string
  // editable work fields only; no sourceType
}

export interface ActorWork extends ActorWorkSave {
  experienceId: number
  sourceType: ActorWorkSourceType
}
```

The verification script must fail when `ActorWorkSave` contains `sourceType`, when `ActorWork` omits it, or when work provenance accepts candidate evidence values such as `explicit` or `inferred_from_roles`.

- [ ] **Step 2: Run type-check and the red route gate**

Run:

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: FAIL because new API modules, stores, and `pkg-profile` routes do not exist.

- [ ] **Step 3: Implement typed API adapters and routes**

Implement only these calls in the new API modules:

```ts
getMyActorProfile(): Promise<ActorProfileResp>
updateMyActorProfile(payload: ActorProfileMineUpdate): Promise<ActorProfileResp>
getActorWorks(query: ActorWorkQuery): Promise<PageResult<ActorWork>>
getActorWork(id: number): Promise<ActorWork>
createActorWork(payload: ActorWorkSave): Promise<ActorWork>
updateActorWork(id: number, payload: ActorWorkSave): Promise<ActorWork>
deleteActorWork(id: number): Promise<void>
replaceActorWorkAssets(id: number, bindings: ActorAssetBinding[]): Promise<void>
getActorAssets(query: ActorAssetQuery): Promise<PageResult<ActorAsset>>
getProfileImportCapability(): Promise<ProfileImportCapability>
extractProfileImport(payload: ProfileImportExtractRequest): Promise<ProfileImportExtraction>
applyProfileImport(payload: ProfileImportApplyRequest): Promise<ProfileImportApplyResult>
listShareCardFavorites(page: number, size: number): Promise<PageResult<ShareCardFavoriteItem>>
addShareCardFavorite(shareCardId: number): Promise<ShareCardFavoriteStatus>
removeShareCardFavorite(shareCardId: number): Promise<ShareCardFavoriteStatus>
```

Add `pkg-profile` as a subpackage and `pkg-tools/settings/index` under the existing tools package. Keep `pages/mine/index` and `pages/actor-profile/edit` in the main package.

- [ ] **Step 4: Run the green checks**

Run:

```powershell
npm run type-check
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: type-check passes and the route/store portion of the static gate passes.

- [ ] **Step 5: Commit**

```powershell
git add kaipai-frontend/src/pages.json kaipai-frontend/src/api kaipai-frontend/src/types kaipai-frontend/src/stores .sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs
git commit -m "feat(miniapp): add career profile API contracts and routes"
```

## Task 3: Replace Mine, Record, Settings, And Favorites Shells

**Files:**
- Modify: `kaipai-frontend/src/pages/mine/index.vue`
- Modify: `kaipai-frontend/src/pages/history/index.vue`
- Modify: `kaipai-frontend/src/pkg-card/favorites/index.vue`
- Create: `kaipai-frontend/src/pkg-tools/settings/index.vue`
- Modify: `.sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs`

- [ ] **Step 1: Extend the static gate with visitor and hierarchy assertions**

```js
assertMatch(mine, /个人档案[\s\S]*作品库[\s\S]*素材库/)
assertMatch(mine, /创建分享[\s\S]*联系申请[\s\S]*设置/)
assertNoMatch(mine, /我的数据|近 30 天|我的二维码|编辑资料/)
assertNoMatch(mine, /getMyShareCards\(|getShareCardHistory\(/)
assertMatch(favorites, /useRecordNavigationStore[\s\S]*switchTab\(['"]\/pages\/history\/index['"]\)/)
assertNoMatch(favorites, /ref\(\[\]\)/)
```

The script must inspect `hydrateMinePage` and assert it guards `getCareerHubSummary()` behind `userStore.hasStoredSession`.

- [ ] **Step 2: Run the red static gate**

Run:

```powershell
node .sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: FAIL because the current Mine page still fetches pseudo statistics and the old favorites page is an empty array.

- [ ] **Step 3: Implement the Career Hub shell**

`pages/mine/index.vue` must follow this boundary:

```ts
const isVisitor = computed(() => !userStore.hasStoredSession)

async function hydrateMinePage(): Promise<void> {
  if (isVisitor.value) return
  try {
    hub.value = await getCareerHubSummary()
  } catch (error) {
    hubError.value = toMessage(error)
  }
}

function openAccountCapability(url: string): void {
  if (isVisitor.value) {
    goLogin()
    return
  }
  uni.navigateTo({ url })
}
```

Keep account identity sourced from `userStore.currentUser` even when the summary request fails. Omit current city when empty. Do not render placeholder numbers for visitors.

`pages/history/index.vue` has two stable segment values, `history` and `favorites`; query browser history only for the first and call `listShareCardFavorites` only for the second. The old favorite route sets one-shot `record-navigation` intent and calls `uni.switchTab({ url: '/pages/history/index' })`.

The settings page exposes notification, preferences, agreement, privacy, about, and sign-out. Agreement/privacy/about are direct navigation for visitors; account actions call the same login gate.

- [ ] **Step 4: Run green static and type checks**

Run:

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: PASS for Mine, history, settings, and favorite compatibility assertions.

- [ ] **Step 5: Commit**

```powershell
git add kaipai-frontend/src/pages/mine/index.vue kaipai-frontend/src/pages/history/index.vue kaipai-frontend/src/pkg-card/favorites/index.vue kaipai-frontend/src/pkg-tools/settings/index.vue kaipai-frontend/src/stores/record-navigation.ts .sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs
git commit -m "feat(miniapp): simplify mine into career hub"
```

## Task 4: Simplify The Profile Editor To One Mine-Save Draft

**Files:**
- Modify: `kaipai-frontend/src/pages/actor-profile/edit.vue`
- Modify: `kaipai-frontend/src/pages/actor-profile/components/BasicInfoSection.vue`
- Modify: `kaipai-frontend/src/pages/actor-profile/components/SkillTagSection.vue`
- Modify: `kaipai-frontend/src/pages/actor-profile/components/AppearanceTagSection.vue`
- Delete after no imports remain: `kaipai-frontend/src/pages/actor-profile/components/WorkExperienceSection.vue`
- Delete after no imports remain: `kaipai-frontend/src/pages/actor-profile/components/PhotoCategorySection.vue`
- Delete after no imports remain: `kaipai-frontend/src/pages/actor-profile/components/PdfResumeSection.vue`
- Delete after no imports remain: `kaipai-frontend/src/pages/actor-profile/components/VideoResumeSection.vue`
- Delete after no imports remain: `kaipai-frontend/src/pages/actor-profile/components/ProfileCompletionBar.vue`

- [ ] **Step 1: Write editor static gate assertions**

```js
assertMatch(edit, /updateMyActorProfile\(/)
assertNoMatch(edit, /updateActorProfile\(|buildPayload\(|workExperiences|photoCategories|videoUrl|resumePdf/)
assertMatch(edit, /chooseAvatarFromAssets/)
assertMatch(edit, /保存资料/)
assertNoMatch(edit, /完成度|提升建议|AI 全量润色/)
```

- [ ] **Step 2: Run the red gate**

Run:

```powershell
node .sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: FAIL because the old editor imports legacy upload and aggregate-save sections.

- [ ] **Step 3: Implement a single profile draft**

```ts
const draft = reactive<ActorProfileMineUpdate>({
  expectedProfileVersion: 0,
  avatarAssetId: null,
  core: { publicName: '', gender: '', age: null, height: null, currentCity: '' },
  career: { weight: null, originPlace: '', schoolName: '', majorName: '', languageTags: [], specialtyTags: [], roleTypeTags: [], professionalAbilityTags: [] },
  intro: '',
})

async function saveProfile(): Promise<void> {
  validateCoreProfile(draft)
  saving.value = true
  try {
    const saved = await updateMyActorProfile(draft)
    hydrateDraft(saved)
    isDirty.value = false
  } finally {
    saving.value = false
  }
}
```

The avatar cell navigates to `pkg-profile/assets/index?mode=avatar-select`; assets emits the selected ID through the shared selection state and the editor refreshes it on return. Keep career fields collapsed by default. The only fixed bottom action is `保存资料`.

On navigation away with a dirty draft, show `保存资料`, `放弃修改`, and `继续编辑`; choosing save awaits `saveProfile` and only then leaves.

- [ ] **Step 4: Run green checks**

Run:

```powershell
npm run type-check
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: PASS and no new source path invokes the old aggregate profile PUT.

- [ ] **Step 5: Commit**

```powershell
git add kaipai-frontend/src/pages/actor-profile/edit.vue kaipai-frontend/src/pages/actor-profile/components/BasicInfoSection.vue kaipai-frontend/src/pages/actor-profile/components/SkillTagSection.vue kaipai-frontend/src/pages/actor-profile/components/AppearanceTagSection.vue .sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs
git rm kaipai-frontend/src/pages/actor-profile/components/WorkExperienceSection.vue kaipai-frontend/src/pages/actor-profile/components/PhotoCategorySection.vue kaipai-frontend/src/pages/actor-profile/components/PdfResumeSection.vue kaipai-frontend/src/pages/actor-profile/components/VideoResumeSection.vue kaipai-frontend/src/pages/actor-profile/components/ProfileCompletionBar.vue
git commit -m "feat(miniapp): simplify actor profile editor"
```

## Task 5: Build User-Driven Import Review

**Files:**
- Create: `kaipai-frontend/src/pkg-profile/import-review/index.vue`
- Create: `kaipai-frontend/src/stores/profile-import.ts`
- Modify: `kaipai-frontend/src/pages/actor-profile/edit.vue`
- Modify: `kaipai-frontend/src/pkg-profile/works/index.vue`
- Modify: `.sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs`

- [ ] **Step 1: Write import interaction static assertions**

```js
assertMatch(importPage, /async function beginClipboardRead\(\)[\s\S]*uni\.getClipboardData/)
assertMatch(importPage, /async function submitExtraction\(\)[\s\S]*extractProfileImport/)
assertMatch(importPage, /requiresExplicitConfirmation[\s\S]*confirmed/)
assertMatch(importPage, /onUnload\(\(\) =>[\s\S]*clear\(\)/)
assertNoMatch(importStore, /uni\.setStorage|persist|localStorage/)
assertNoMatch(importPage, /getClipboardData\([\s\S]*onLoad/)
```

- [ ] **Step 2: Run the red gate**

Run:

```powershell
node .sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: FAIL because no review page or in-memory draft store exists.

- [ ] **Step 3: Implement the in-memory review state and explicit read**

```ts
async function beginClipboardRead(): Promise<void> {
  readingClipboard.value = true
  try {
    const result = await uni.getClipboardData()
    importStore.setRawText(result.data.trim())
  } finally {
    readingClipboard.value = false
  }
}

async function submitExtraction(): Promise<void> {
  const rawText = importStore.rawText.trim()
  if (!rawText) return
  extracting.value = true
  try {
    const extraction = await extractProfileImport({
      rawText,
      scene: importStore.scene,
      contextVersion: importStore.contextVersion,
    })
    importStore.setExtraction(extraction)
  } catch (error) {
    extractionError.value = mapProfileImportError(error)
  } finally {
    extracting.value = false
  }
}
```

Show editable source text first, then a second explicit action to extract. Render candidates under five business groups: `个人资料`, `作品`, `需要确认`, `疑似重复`, and `未映射内容`. When a candidate has `sourceType === 'inferred_from_roles'`, its checkbox remains disabled until a separate confirmation action updates `confirmed=true` and `selected=true`.

`applyReview()` sends only user-selected final values, proofs, actions, request ID, scene, and versions. It retains the editable draft after a `46010` version conflict or field validation error, clears only after a successful apply, and does not call `updateActorProfile`.

- [ ] **Step 4: Run the green static and type checks**

Run:

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: PASS for explicit clipboard read, non-persistence, confirmation, retry, and cleanup rules.

- [ ] **Step 5: Commit**

```powershell
git add kaipai-frontend/src/pkg-profile/import-review/index.vue kaipai-frontend/src/stores/profile-import.ts kaipai-frontend/src/pages/actor-profile/edit.vue kaipai-frontend/src/pkg-profile/works/index.vue .sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs
git commit -m "feat(miniapp): add reviewed profile import"
```

## Task 6: Build Paged Works And Unified Asset Library

**Files:**
- Create: `kaipai-frontend/src/pkg-profile/works/index.vue`
- Create: `kaipai-frontend/src/pkg-profile/work-edit/index.vue`
- Create: `kaipai-frontend/src/pkg-profile/assets/index.vue`
- Modify: `kaipai-frontend/src/pages/actor-profile/edit.vue`
- Modify: `.sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs`

- [ ] **Step 1: Write paged-work and asset-protection gate assertions**

```js
assertMatch(worksPage, /const PAGE_SIZE = 10/)
assertMatch(worksPage, /loadNextPage/)
assertNoMatch(worksPage, /MAX_WORK_EXPERIENCES|最多 10 条/)
assertMatch(worksPage, /setRepresentativeWorks/)
assertMatch(workEditPage, /updateActorWork|createActorWork/)
assertMatch(workEditPage, /sourceTypeLabel/)
assertMatch(workEditPage, /replaceActorWorkAssets/)
assertNoMatch(actorWorkTypes, /interface ActorWorkSave\s*\{[^}]*sourceType/)
assertMatch(actorWorkTypes, /type ActorWorkSourceType\s*=\s*'manual'\s*\|\s*'import'\s*\|\s*'migration'/)
assertMatch(actorWorkTypes, /interface ActorWork(?:\s+extends[^\{]+)?\s*\{[^}]*sourceType:\s*ActorWorkSourceType/)
assertNoMatch(actorWorkTypes, /ActorWorkSourceType[^\n]*(explicit|direct|inferred_from_roles)/)
assertMatch(assetsPage, /mediaType.*photo[\s\S]*video[\s\S]*pdf/)
assertMatch(assetsPage, /requestAssetAccessUrl/)
assertMatch(assetsPage, /deleteAsset[\s\S]*PROFILE_ASSET_IN_USE/)
```

- [ ] **Step 2: Run the red gate**

Run:

```powershell
node .sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: FAIL because the profile subpackage pages do not exist.

- [ ] **Step 3: Implement works list and editor**

`works/index.vue` requests at most 10 records per page, appends the next page, and renders exact total count. It supplies keyword/status/type filters, navigation to manual edit, an import route with `scene=works_only`, representative selection limited by backend response, and impact confirmation before delete.

`work-edit/index.vue` keeps one work draft. It requires project name, sends all other omitted values as `null` or absent according to the API type, and never sends `sourceType`. For existing works it renders the server value as a read-only `手动创建 / 智能导入 / 历史迁移` label; candidate evidence `sourceType` is never displayed as work provenance. Description polish remains a local field action.

The editor keeps one complete desired binding list and submits it once through `replaceActorWorkAssets(id, bindings)`. An empty list intentionally clears the work assets. Do not call an append-only binding endpoint per selected item. While the PUT is pending, lock asset edits; on failure keep the local selection and show a retry state, because the backend guarantees the previous relation set and version remain unchanged. An identical list is a backend no-op.

- [ ] **Step 4: Implement the asset library**

`assets/index.vue` uses a fixed type segment `photo | video | pdf`; each list row contains readiness state, category, name, and an icon action for preview/rename/delete. The upload path creates an asset metadata record after upload, then polls or refreshes processing status until `ready` or `failed`. It never saves `accessUrl` into a profile/works/share payload.

In `mode=avatar-select`, only ready photo assets can be selected. When no ready photo exists, display upload first and return selection through the shared route state after it becomes ready. Current PDF uses `setCurrentResume(assetId)`; setting it does not make it public.

- [ ] **Step 5: Run green checks**

Run:

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: PASS for pagination, no ten-work cap, read-only server work provenance, complete-set asset replacement, asset state handling, and protected deletion feedback.

- [ ] **Step 6: Commit**

```powershell
git add kaipai-frontend/src/pkg-profile/works/index.vue kaipai-frontend/src/pkg-profile/work-edit/index.vue kaipai-frontend/src/pkg-profile/assets/index.vue kaipai-frontend/src/pages/actor-profile/edit.vue .sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs
git commit -m "feat(miniapp): add work and asset libraries"
```

## Task 7: Add Public Favorite Actions And Verify Built Mini-Program

**Files:**
- Modify: `kaipai-frontend/src/pages/actor-profile/detail.vue`
- Modify: `kaipai-frontend/src/pkg-card/actor-card/index.vue`
- Modify: `kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue`
- Modify: `.sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs`

- [ ] **Step 1: Write favorite action gate assertions**

```js
for (const page of [actorDetail, actorCard, aiCardDetail]) {
  assertMatch(page, /addShareCardFavorite|removeShareCardFavorite/)
  assertMatch(page, /requireLoginFor.*Favorite|goLogin/)
}
```

- [ ] **Step 2: Run the red gate**

Run:

```powershell
node .sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: FAIL because public pages do not yet use the favorite API.

- [ ] **Step 3: Implement favorite state with explicit login gate**

On a public page, fetch favorite status only after a valid session is available. A visitor tapping the icon navigates to login; it does not issue a favorite request. A signed-in user sees a loading icon while the PUT/DELETE runs and receives the updated `favorited` state from the server.

- [ ] **Step 4: Build and audit package output**

Run:

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check
npm run build:mp-weixin
npm run audit:steering
npm run audit:mp-package
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: all commands exit 0. The static script must inspect `src`, `dist/build/mp-weixin/app.json`, and `dist/dev/mp-weixin/app.json`, assert that `pkg-profile` is registered, and report each package below 2 MB.

- [ ] **Step 5: Perform WeChat DevTools evidence review**

Open `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin` in WeChat DevTools and capture the following states:

1. Visitor Mine and visitor Settings agreement/privacy/about access.
2. Signed-in Career Hub summary and no pseudo analytics/QR.
3. Simplified profile save and dirty-leave modal.
4. Import review with user-triggered clipboard read and unconfirmed inferred gender.
5. Twenty-nine-work fixture across paged results and work filters.
6. Asset upload, asset-in-use delete message, and avatar selection.
7. Public favorite add/remove and Record favorites segment.

- [ ] **Step 6: Commit**

```powershell
git add kaipai-frontend/src/pages/actor-profile/detail.vue kaipai-frontend/src/pkg-card/actor-card/index.vue kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue .sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs
git commit -m "feat(miniapp): add favorite actions and verify career hub"
```

## Verification Gate For Plan 3

Run the Task 7 command set again from a clean working tree. Do not proceed to the presentation read switch until the static script validates no Mine pseudo analytics, no legacy editor collection writer, no persisted clipboard source text, and no empty-array favorite implementation.
