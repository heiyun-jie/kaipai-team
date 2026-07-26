# 00-200 Admin UI And Phase A Rollout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the Prompt governance UI to the existing DeepSeek settings page, prove permission/privacy behavior in development and sanitized production builds, and normally test and release both bootstrap v1 drafts while production recognition remains on `legacy-code-v1`.

**Architecture:** A single `ProfileImportPromptTemplatePanel` owns summary/versions/detail loading and draft actions without mixing model-config and Prompt audits. Shared request handling preserves stable backend `errorCode`, `AuditConfirmDialog` gains an optional fixed-choice mode, and the existing CDP E2E becomes the authority for permission isolation, body non-exposure, conflict retention, and real `dist` loading. Phase A rollout uses the standard schema/backend/admin release scripts, then performs real fixed-fixture tests and normal publish transactions for both scenes.

**Tech Stack:** Vue 3 Composition API, TypeScript 5.4, Element Plus 2.9, Axios, Vite 5.2, native Chrome DevTools Protocol E2E, Node.js 22, existing backend/admin release scripts.

---

## Preconditions And Execution Boundary

Execute only after every gate in `2026-07-26-00-200-prompt-governance-backend.md` passes. Work remains on `codex/00-199-miniapp-profile-library-import`. The `kaipai-admin` repository is clean at baseline commit `fdd7c5f`; all admin commit commands run from `D:\XM\kaipai-team\kaipai-admin`.

Do not change `src/router/index.ts`, `src/constants/menus.ts`, `vite.config.ts`, or `package.json`. The existing `/system/ai-profile-import` route and seven-page navigation are authoritative. Do not place Prompt governance in the sharing-style template page, create another route, or touch the mini-program.

Use this one immutable production tuple for every Phase A preflight, schema migration, remote SQL validation, backend release, admin release, and public smoke. Set it once at the start of Task 7 and do not redeclare or substitute any member later:

```powershell
$phaseADatabase = 'kaipai_prod'
$phaseAApiBaseUrl = 'https://api.kplyyk.com'
$phaseAAdminBaseUrl = 'https://kplyyk.com'
$phaseATuple = "$phaseADatabase|$phaseAApiBaseUrl|$phaseAAdminBaseUrl"
if ($phaseATuple -ne 'kaipai_prod|https://api.kplyyk.com|https://kplyyk.com') {
  throw "PHASE_A_TARGET_TUPLE_MISMATCH: $phaseATuple"
}
```

Phase A ends only when:

- V001 and V002 are recorded against production schema `kaipai_prod`, matching `https://api.kplyyk.com` and `https://kplyyk.com`; a development database may never be paired with these production domains.
- Governance backend and admin UI are deployed with release records.
- Target data initially proves two `draft/untested` bootstrap v1 rows and null active pointers.
- Each scene is tested through the real configured DeepSeek model.
- Each scene is released through the normal publish API with a valid fixed reason code.
- Target data proves two released active v1 rows and immutable publish-binding audits.
- A code/runtime check still proves ordinary user recognition uses `legacy-code-v1`.

No Phase B code is deployed in this plan.

## File Map

Modify admin production files:

- `src/types/common.ts`
- `src/utils/request.ts`
- `src/types/ai.ts`
- `src/api/ai.ts`
- `src/constants/permission.ts`
- `src/constants/permission-registry.ts`
- `src/components/dialogs/AuditConfirmDialog.vue`
- `src/views/system/AiProfileImportConfigView.vue`
- `src/views/system/SettingsView.vue`

Create admin production file:

- `src/components/business/ProfileImportPromptTemplatePanel.vue`

Modify admin E2E:

- `scripts/e2e-ai-profile-import-config.mjs`

Create outer-repository rollout verification SQL:

- `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/verify-phase-a-prompt-state.sql`

## Task 1: Stable Business Errors, Prompt Types, APIs, And Permission Registry

**Files:**

- Modify: `src/types/common.ts`
- Modify: `src/utils/request.ts`
- Modify: `src/types/ai.ts`
- Modify: `src/api/ai.ts`
- Modify: `src/constants/permission.ts`
- Modify: `src/constants/permission-registry.ts`
- Modify: `scripts/e2e-ai-profile-import-config.mjs`

- [ ] **Step 1: Extend E2E mocks for stable errors and five new permissions, then verify RED**

Extend `actionPermissions` without renaming the existing model-config actions:

```js
const actionPermissions = {
  update: 'action.system.ai-profile-import.update',
  secret: 'action.system.ai-profile-import.secret',
  test: 'action.system.ai-profile-import.test',
  audit: 'action.system.ai-profile-import.audit',
  templateRead: 'action.system.ai-profile-import.template-read',
  templateUpdate: 'action.system.ai-profile-import.template-update',
  templateTest: 'action.system.ai-profile-import.template-test',
  templatePublish: 'action.system.ai-profile-import.template-publish',
  templateRestore: 'action.system.ai-profile-import.template-restore',
}
```

Add `apiError` support for stable strings:

```js
function apiError(message, code = 400, errorCode = null) {
  return { code, message, errorCode, data: null }
}
```

Add a mock conflict endpoint returning HTTP 200 and:

```js
apiError(
  'Prompt 版本已变化，请重新加载后人工合并',
  46018,
  'PROFILE_IMPORT_PROMPT_VERSION_CONFLICT',
)
```

Add an assertion that a rejected request is an actual `ApiBusinessError` with `name='ApiBusinessError'`, numeric `code=46018`, string `errorCode='PROFILE_IMPORT_PROMPT_VERSION_CONFLICT'`, and the backend `message`; a plain `Error` or any missing field fails. Run:

```powershell
cd D:\XM\kaipai-team\kaipai-admin
npm run e2e:ai-profile-import-config
```

Expected: FAIL because the current response interceptor discards `code/errorCode` and the Prompt panel/API does not exist.

- [ ] **Step 2: Preserve the backend business envelope in a typed error**

Change the common types to:

```ts
export interface ApiResponse<T> {
  code: number
  message: string
  errorCode?: string | null
  data: T
}

export interface ApiBusinessErrorShape {
  code: number
  errorCode?: string | null
  message: string
}
```

In `request.ts`, export a typed error and guard:

```ts
export class ApiBusinessError extends Error {
  readonly code: number
  readonly errorCode: string | null

  constructor(payload: ApiBusinessErrorShape) {
    super(payload.message || '请求失败')
    this.name = 'ApiBusinessError'
    this.code = payload.code
    this.errorCode = payload.errorCode || null
  }
}

export function isApiBusinessError(error: unknown): error is ApiBusinessError {
  return error instanceof ApiBusinessError
}
```

Replace only the business-failure rejection with:

```ts
ElMessage.error(payload.message || '请求失败')
return Promise.reject(new ApiBusinessError(payload))
```

Keep existing auth-expiry cleanup, network failures, query sanitization, and existing toast behavior. Do not parse or match localized message text anywhere.

- [ ] **Step 3: Add complete list/detail/write TypeScript contracts**

Append these unions and interfaces to `src/types/ai.ts`:

```ts
export type ProfileImportPromptScene = 'full_profile' | 'works_only'
export type ProfileImportPromptLifecycle = 'draft' | 'released' | 'abandoned'
export type ProfileImportPromptTestStatus = 'untested' | 'success' | 'failed' | 'stale'
export type ProfileImportPromptReasonCode =
  | 'INITIAL_RELEASE'
  | 'QUALITY_ADJUSTMENT'
  | 'CONFIG_ALIGNMENT'
  | 'QUALITY_REGRESSION'
  | 'INCIDENT_ROLLBACK'
  | 'DRAFT_SUPERSEDED'
  | 'DRAFT_INVALID'

export interface ProfileImportPromptTemplateSummary {
  templateId: number
  templateCode: string
  scene: ProfileImportPromptScene
  displayName: string
  activeVersionId?: number | null
  activeVersionNo?: number | null
  activeVersionLabel?: string | null
  activeContentSha256?: string | null
  draftVersionId?: number | null
  draftVersionNo?: number | null
  draftVersionLabel?: string | null
  draftTestStatus?: ProfileImportPromptTestStatus | null
  version: number
}

export interface ProfileImportPromptVersionSummary {
  promptVersionId: number
  versionNo: number
  versionLabel: string
  lifecycleStatus: ProfileImportPromptLifecycle
  contentSha256: string
  testStatus: ProfileImportPromptTestStatus
  testedModelName?: string | null
  testErrorCode?: string | null
  testCandidateCount: number
  testWorkCount: number
  testElapsedMs?: number | null
  testedBy?: number | null
  testedAt?: string | null
  releasedBy?: number | null
  releasedAt?: string | null
  updateUserName?: string | null
  lastUpdate?: string | null
  version: number
}

export interface ProfileImportPromptVersionDetail extends ProfileImportPromptVersionSummary {
  systemPromptBody: string
  repairPromptBody: string
  schemaVersion: string
  contractVersion: string
  changeSummary?: string | null
}

export interface ProfileImportPromptTestResult {
  promptVersionId: number
  contentSha256: string
  runtimeSha256: string
  fixtureCode: string
  fixtureVersion: string
  fixtureSha256: string
  modelName: string
  configVersion: number
  status: 'success' | 'failed'
  candidateCount: number
  workCount: number
  elapsedMs: number
  errorCode?: string | null
  testedBy: number
  testedAt: string
}

export interface ProfileImportPromptAudit {
  promptAuditId: number
  templateId: number
  promptVersionId?: number | null
  actionCode: string
  fromVersionId?: number | null
  toVersionId?: number | null
  contentSha256?: string | null
  runtimeSha256?: string | null
  schemaVersion?: string | null
  contractVersion?: string | null
  fixtureCode?: string | null
  fixtureVersion?: string | null
  fixtureSha256?: string | null
  modelName?: string | null
  configVersion?: number | null
  testOperatorId?: number | null
  testedAt?: string | null
  operatorId: number
  operatorName?: string | null
  reasonCode: string
  resultStatus: string
  errorCode?: string | null
  message?: string | null
  createTime?: string | null
}
```

`ProfileImportPromptVersionSummary` intentionally omits `templateId`. Ownership is bound by the `/{templateCode}/versions` request and the selected template in component state; the admin must not require an extra field and the backend DTO remains unchanged. Detail and action requests use only `promptVersionId`, while the backend rechecks template ownership under lock.

Write payloads are exact and contain no operator, state, hashes, test result, or free `reason`:

```ts
export interface ProfileImportPromptCreateDraftPayload {
  sourceVersionId?: number | null
  expectedTemplateVersion: number
}

export interface ProfileImportPromptUpdateDraftPayload {
  versionLabel: string
  systemPromptBody: string
  repairPromptBody: string
  changeSummary?: string | null
  expectedVersion: number
}

export interface ProfileImportPromptVersionActionPayload {
  reasonCode: ProfileImportPromptReasonCode
  expectedTemplateVersion: number
  expectedVersion: number
}

export interface ProfileImportPromptRestorePayload {
  reasonCode: ProfileImportPromptReasonCode
  expectedTemplateVersion: number
}
```

- [ ] **Step 4: Add API functions with exact paths and test timeout**

Add imports and these functions to `src/api/ai.ts`:

```ts
export function fetchProfileImportPromptTemplates() {
  return request.get('/admin/ai/profile-import/prompt-templates').then((data) => data as unknown as ProfileImportPromptTemplateSummary[])
}

export function fetchProfileImportPromptVersions(templateCode: string) {
  return request.get(`/admin/ai/profile-import/prompt-templates/${templateCode}/versions`).then((data) => data as unknown as ProfileImportPromptVersionSummary[])
}

export function fetchProfileImportPromptVersion(versionId: number) {
  return request.get(`/admin/ai/profile-import/prompt-templates/versions/${versionId}`).then((data) => data as unknown as ProfileImportPromptVersionDetail)
}

export function createProfileImportPromptDraft(templateCode: string, payload: ProfileImportPromptCreateDraftPayload) {
  return request.post(`/admin/ai/profile-import/prompt-templates/${templateCode}/drafts`, payload).then((data) => data as unknown as ProfileImportPromptTemplateSummary)
}

export function updateProfileImportPromptDraft(versionId: number, payload: ProfileImportPromptUpdateDraftPayload) {
  return request.put(`/admin/ai/profile-import/prompt-templates/versions/${versionId}`, payload).then((data) => data as unknown as ProfileImportPromptVersionDetail)
}

export function abandonProfileImportPromptDraft(versionId: number, payload: ProfileImportPromptVersionActionPayload) {
  return request.post(`/admin/ai/profile-import/prompt-templates/versions/${versionId}/abandon`, payload).then((data) => data as unknown as ProfileImportPromptTemplateSummary)
}

export function testProfileImportPromptVersion(versionId: number) {
  return request.post(`/admin/ai/profile-import/prompt-templates/versions/${versionId}/test`, undefined, { timeout: 180000 }).then((data) => data as unknown as ProfileImportPromptTestResult)
}

export function publishProfileImportPromptVersion(versionId: number, payload: ProfileImportPromptVersionActionPayload) {
  return request.post(`/admin/ai/profile-import/prompt-templates/versions/${versionId}/publish`, payload).then((data) => data as unknown as ProfileImportPromptTemplateSummary)
}

export function restoreProfileImportPromptTemplate(templateCode: string, versionId: number, payload: ProfileImportPromptRestorePayload) {
  return request.post(`/admin/ai/profile-import/prompt-templates/${templateCode}/versions/${versionId}/restore`, payload).then((data) => data as unknown as ProfileImportPromptTemplateSummary)
}

export function fetchProfileImportPromptAudits() {
  return request.get('/admin/ai/profile-import/prompt-templates/audits').then((data) => data as unknown as ProfileImportPromptAudit[])
}
```

- [ ] **Step 5: Register five independent actions without fallback**

Add exact constants:

```ts
systemAiProfileImportTemplateRead: 'action.system.ai-profile-import.template-read',
systemAiProfileImportTemplateUpdate: 'action.system.ai-profile-import.template-update',
systemAiProfileImportTemplateTest: 'action.system.ai-profile-import.template-test',
systemAiProfileImportTemplatePublish: 'action.system.ai-profile-import.template-publish',
systemAiProfileImportTemplateRestore: 'action.system.ai-profile-import.template-restore',
```

Add matching registry rows under module `system`, with labels `Prompt 正文读取`, `Prompt 草稿编辑`, `Prompt 固定样例试运行`, `Prompt 版本发布`, and `Prompt 历史恢复`. Reuse the existing audit action. Do not infer any Prompt permission from model config update/test or page permission.

- [ ] **Step 6: Run the partial type-check without committing a red vertical slice**

```powershell
npm run type-check
```

Expected: type-check PASS. The default E2E intentionally remains RED because the dialog, panel, and page integration are not complete. Do not stage or commit any Task 1-4 admin production file until Task 4 turns that same default E2E GREEN.

## Task 2: Fixed-Reason Confirmation Dialog With Backward Compatibility

**Files:**

- Modify: `src/components/dialogs/AuditConfirmDialog.vue`
- Modify: `scripts/e2e-ai-profile-import-config.mjs`

- [ ] **Step 1: Add E2E assertions for select mode and verify RED**

Cover both modes in an explicit development Vite harness; no repository test runner, completed Prompt panel, or alternate route is assumed.

Implement `runAuditDialogHarnesses(client)` in `scripts/e2e-ai-profile-import-config.mjs`. When `distMode=false`, evaluate an async browser function on the already-loaded app origin that dynamically imports `/node_modules/.vite/deps/vue.js`, `/node_modules/.vite/deps/element-plus.js`, and `/src/components/dialogs/AuditConfirmDialog.vue`; append a dedicated host, register `ElementPlus.default`, and mount the real component. First loop over these literal label/value sets: publish `首次发布=INITIAL_RELEASE`, `质量调整=QUALITY_ADJUSTMENT`, `模型配置对齐=CONFIG_ALIGNMENT`; restore `质量回退=QUALITY_REGRESSION`, `故障恢复=INCIDENT_ROLLBACK`; abandon `已有替代草稿=DRAFT_SUPERSEDED`, `草稿内容无效=DRAFT_INVALID`. Render with `modelValue=true`, `requireReason=true`, and that `reasonOptions`; require exactly one enabled `.dialog-reason-select`, zero textarea, and option labels/values equal only that set. Unmount and remove the teleported dialog after each case. Then mount once with `title='E2E 旧调用方'`, no `reasonOptions`, require exactly one textarea and zero `.dialog-reason-select`, set its value to `  旧调用备注  ` through the native input event, click the primary confirm button, and require the captured `submit` value to equal `旧调用备注`. In `finally`, call `app.unmount()`, remove the host, and remove every harness-owned teleported dialog node. Run this function before every assertion that depends on the not-yet-mounted Prompt panel, so the Task 2 RED is specifically the missing select mode. When `distMode=true`, do not import `/src`; the full Prompt publish/restore/abandon lifecycle remains the production-build select-mode gate.

Run:

```powershell
npm run e2e:ai-profile-import-config
```

Expected: FAIL in the first fixed-option harness because `AuditConfirmDialog` renders a textarea and no select. This is an isolated Task 2 RED even though the shared Task 1-4 default E2E also remains RED for the missing panel.

- [ ] **Step 2: Add optional reason options without changing existing callers**

Extend props:

```ts
reasonOptions?: Array<{ label: string; value: string }>
```

Default to an empty array. Keep the existing `submit` and `confirm` events as strings. Render exactly one control:

```vue
<el-select
  v-if="reasonOptions.length"
  v-model="state.reason"
  :placeholder="placeholder"
  class="dialog-reason-select"
>
  <el-option
    v-for="option in reasonOptions"
    :key="option.value"
    :label="option.label"
    :value="option.value"
  />
</el-select>
<el-input
  v-else
  v-model="state.reason"
  type="textarea"
  :rows="4"
  :placeholder="placeholder"
/>
```

Required validation applies to either mode. Reset state whenever the dialog closes. Do not add a free-text supplement beside the select.

- [ ] **Step 3: Type-check the dialog slice without claiming the still-red E2E is GREEN**

```powershell
npm run type-check
```

Expected: type-check PASS. The complete default E2E remains RED for the missing panel/page integration, so there is no intermediate commit.

## Task 3: Prompt Governance Panel, Lazy Detail Loading, And Conflict Retention

**Files:**

- Create: `src/components/business/ProfileImportPromptTemplatePanel.vue`
- Modify: `scripts/e2e-ai-profile-import-config.mjs`

- [ ] **Step 1: Build complete Prompt mock state and lifecycle assertions, then verify RED**

Add state that contains no bodies in summaries and keeps bodies only in detail fixtures:

```js
const sensitivePromptMarker = `PROMPT_BODY_DETAIL_ONLY_${randomUUID()}`

function createPromptState() {
  return {
    templates: [
      {
        templateId: 11,
        templateCode: 'full_profile',
        scene: 'full_profile',
        displayName: '完整资料识别',
        activeVersionId: null,
        activeVersionNo: null,
        activeVersionLabel: null,
        activeContentSha256: null,
        draftVersionId: 101,
        draftVersionNo: 1,
        draftVersionLabel: 'bootstrap-v1',
        draftTestStatus: 'untested',
        version: 0,
      },
      {
        templateId: 12,
        templateCode: 'works_only',
        scene: 'works_only',
        displayName: '仅作品识别',
        activeVersionId: null,
        activeVersionNo: null,
        activeVersionLabel: null,
        activeContentSha256: null,
        draftVersionId: 201,
        draftVersionNo: 1,
        draftVersionLabel: 'bootstrap-v1',
        draftTestStatus: 'untested',
        version: 0,
      },
    ],
    versions: {
      full_profile: [versionSummary(101, 1, 'draft', 'untested')],
      works_only: [versionSummary(201, 1, 'draft', 'untested')],
    },
    details: {
      101: versionDetail(101, 1, 'draft', sensitivePromptMarker),
      201: versionDetail(201, 1, 'draft', `${sensitivePromptMarker}_WORKS`),
    },
    audits: [],
    conflictNextSave: false,
    testAttemptByVersion: new Map(),
  }
}
```

Handle every Spec route and enforce its exact action permission. Route handlers reject bodies containing `reason`, operator fields, lifecycle/pointer fields, Schema/contract fields, hashes, or test metadata. The test route asserts `request.postData` is absent; `{}` is rejected because the endpoint has no request body. Test calls return `failed` on the first configured attempt and `success` on the next; publish rejects untested/failed/stale; update increments row version and makes prior success stale; first publish creates the active pointer; a later draft can be abandoned; a second normally released version allows a real `v2 -> v1` restore fixture.

Make the no-body assertion literal in the Prompt test route; do not pass `postData` through `parseBody`:

```js
if (postData !== undefined) {
  throw new Error('Prompt test request must not contain postData')
}
```

Add resettable mock controls `templateListFailuresRemaining`, `emptyVersionTemplateCode`, and `blockedMutation`. `blockedMutation` exposes a Promise gate so the browser can issue a mutation while the mock deliberately withholds its response. Exercise these four scenarios in fresh state/session instances:

1. Set `templateListFailuresRemaining=1`, navigate, require the first root `GET /admin/ai/profile-import/prompt-templates` to render `模板加载失败` and one enabled `重试` command, click it, then require exactly two root-list calls and the two scene tabs to render. No page reload is allowed.
2. Set `emptyVersionTemplateCode='works_only'`, select `仅作品`, require the version table's empty state and zero version-detail or mutation calls for that scene; the summary must remain usable and the other scene must still load.
3. Hold `POST /admin/ai/profile-import/prompt-templates/versions/101/publish` in `blockedMutation`, dispatch two rapid clicks on the same confirm button before resolving the gate, require the confirm button to be disabled and `.is-loading`, and require exactly one matching POST. Resolve the gate and require one success transition. A second request, two audits, or two summary refresh chains fails the test.
4. Use `Emulation.setDeviceMetricsOverride` with `{ width: 390, height: 844, deviceScaleFactor: 1, mobile: false }`, render the panel and open the editor and action dialogs. Require `document.documentElement.scrollWidth <= document.documentElement.clientWidth`; require each visible dialog, footer, toolbar, and row-action group to stay within the 390px viewport; and pairwise-intersect the visible controls inside each group, failing on any positive-area overlap. Internal table scrolling is allowed only inside its `.el-scrollbar__wrap`.

Add browser scenarios with these exact outcomes:

```text
two scene tabs and body-free summaries render
opening a draft makes exactly one detail request
editing and saving preserves active pointer
version conflict keeps all three local fields and shows the server snapshot separately
failed test keeps draft and disables publish
successful test enables publish
publish uses select reason and moves active/draft summary
released version can seed a new draft
open draft can be abandoned only after active exists
restore uses select reason and keeps an open draft
template audit refreshes independently from model-config audit
initial template-list failure retries successfully without a page reload
an empty version list renders an explicit empty state and makes no detail/mutation call
rapid double submit produces one mutation while the command remains loading-locked
390px viewport has no document overflow, clipped dialog/actions, or overlapping controls
no unhandled mock, console, page, HTTP, or network errors
```

Run:

```powershell
npm run e2e:ai-profile-import-config
```

Expected: FAIL because `ProfileImportPromptTemplatePanel.vue` does not exist.

- [ ] **Step 2: Implement independent permissions and conditional loading**

Inside the new component, compute permissions directly from the store:

```ts
const canRead = computed(() => permissionStore.hasAction(PERMISSIONS.action.systemAiProfileImportTemplateRead))
const canUpdate = computed(() => permissionStore.hasAction(PERMISSIONS.action.systemAiProfileImportTemplateUpdate))
const canTest = computed(() => permissionStore.hasAction(PERMISSIONS.action.systemAiProfileImportTemplateTest))
const canPublish = computed(() => permissionStore.hasAction(PERMISSIONS.action.systemAiProfileImportTemplatePublish))
const canRestore = computed(() => permissionStore.hasAction(PERMISSIONS.action.systemAiProfileImportTemplateRestore))
const canAudit = computed(() => permissionStore.hasAction(PERMISSIONS.action.systemAiProfileImportAudit))

onMounted(async () => {
  const work: Promise<unknown>[] = []
  if (canRead.value) work.push(loadTemplates())
  if (canAudit.value) work.push(loadAudits())
  await Promise.all(work)
})
```

If `canRead=false`, never call template list, versions, or detail APIs and never allocate a body form. If only audit is granted, render the sanitized template audit table. If neither read nor audit is granted, render nothing. Action buttons use `PermissionButton mode="hide"` and the matching action code; do not disable a forbidden button into view.

- [ ] **Step 3: Implement state, lazy detail, and stable error branches**

Use explicit state rather than storing responses in browser storage:

```ts
const templates = ref<ProfileImportPromptTemplateSummary[]>([])
const versions = ref<ProfileImportPromptVersionSummary[]>([])
const audits = ref<ProfileImportPromptAudit[]>([])
const selectedTemplateCode = ref<ProfileImportPromptScene>('full_profile')
const editorOpen = ref(false)
const editorLoading = ref(false)
const conflictSnapshot = ref<ProfileImportPromptVersionDetail | null>(null)
const editor = reactive<ProfileImportPromptUpdateDraftPayload>({
  versionLabel: '',
  systemPromptBody: '',
  repairPromptBody: '',
  changeSummary: '',
  expectedVersion: 0,
})
```

`openEditor(versionId)` calls detail once, copies it into memory, and opens the dialog. Nothing prefetches bodies. The stable error branch is exact:

```ts
const promptErrorCopy: Record<string, string> = {
  PROFILE_IMPORT_PROMPT_VERSION_CONFLICT: '版本已变化，请对照服务端版本人工合并',
  PROFILE_IMPORT_PROMPT_INVALID: '模板内容或操作参数无效',
  PROFILE_IMPORT_PROMPT_TEST_REQUIRED: '请先完成固定样例试运行',
  PROFILE_IMPORT_PROMPT_TEST_STALE: '试运行绑定已失效，请重新测试',
  PROFILE_IMPORT_PROMPT_STATE_CONFLICT: '当前模板状态不允许该操作',
}

function promptErrorMessage(error: unknown, fallback: string) {
  if (isApiBusinessError(error) && error.errorCode) {
    return promptErrorCopy[error.errorCode] || fallback
  }
  return fallback
}
```

On `PROFILE_IMPORT_PROMPT_VERSION_CONFLICT`, keep `editorOpen=true` and leave `editor` byte-for-byte unchanged. Fetch the latest detail into `conflictSnapshot`; display its row version, label, and read-only System/Repair bodies in a separate comparison area. Provide an explicit `采用服务端版本号` command that changes only `editor.expectedVersion`; it never overwrites local body/label/change summary. Other errors also keep the editor open.

- [ ] **Step 4: Implement actions and action-specific reason choices**

Fixed UI option arrays are:

```ts
const publishReasons = [
  { label: '首次发布', value: 'INITIAL_RELEASE' },
  { label: '质量调整', value: 'QUALITY_ADJUSTMENT' },
  { label: '模型配置对齐', value: 'CONFIG_ALIGNMENT' },
]
const restoreReasons = [
  { label: '质量回退', value: 'QUALITY_REGRESSION' },
  { label: '故障恢复', value: 'INCIDENT_ROLLBACK' },
]
const abandonReasons = [
  { label: '已有替代草稿', value: 'DRAFT_SUPERSEDED' },
  { label: '草稿内容无效', value: 'DRAFT_INVALID' },
]
```

Use one action state containing kind, template, version, and selected fixed code. `AuditConfirmDialog` receives only the matching options. Payloads contain `reasonCode`, expected template version, and expected row version. The bootstrap abandon action is absent while `activeVersionId` is null. Restore is absent on the current active version and present only on nonactive released history. Test is available for draft/released versions with test permission. Publish is present only for an open draft; backend errors remain authoritative even when UI status looks eligible.

All create/save/test/publish/restore/abandon handlers share one synchronous entry guard and loading lock. The first line after argument validation is `if (mutationLoading.value) return`; set `mutationLoading.value=true` before the API Promise is created and reset it in `finally`. Bind the initiating and confirmation commands to that same loading/disabled state so the blocked-response E2E can prove there is only one request.

After every successful mutation, reload summaries and the selected version list; refresh audit only when `canAudit`. Do not close the editor on failed save. Do not load detail as part of a list refresh.

- [ ] **Step 5: Implement a restrained, responsive panel layout**

Render one outer `el-card` with 8px radius and no nested cards. Use:

- Header: `识别模板` plus icon refresh command.
- `el-tabs` for `完整资料` and `仅作品`.
- An unframed summary grid with current version, open draft, test state, and hash prefix.
- One `el-table` with version, lifecycle, 12-character hash prefix, tested model/result, operator/time, and action column.
- `StatusTag` for lifecycle/test status and `TableActions` for row commands.
- A second tab/section for template audit only when audit permission exists.
- A wide editor dialog with `width="min(1040px, calc(100vw - 32px))"`, two labeled textareas, version label, change summary, immutable Schema/contract values, and the optional conflict comparison.

Use Element Plus icons from the installed library (`Edit`, `VideoPlay`, `Promotion`, `RefreshLeft`, `Close`, `Plus`, `Refresh`) in command buttons. Keep compact panel headings, 0 letter spacing, stable table/action widths, horizontal overflow on narrow screens, and no global style changes. Do not add a hero, marketing explanation, cards inside cards, gradients, or decorative imagery.

At widths below 640px, keep page width fixed to the viewport, wrap the toolbar and summary grid, constrain dialogs to `calc(100vw - 32px)`, and put wide version content in its own horizontal scroller. Dialog footers and action groups wrap with an 8px gap; no control may be clipped or overlap another control. The 390px CDP scenario above is the acceptance gate.

- [ ] **Step 6: Type-check the unmounted panel without committing**

```powershell
npm run type-check
```

Expected: type-check PASS. The panel is not mounted until Task 4, so the default E2E is still the same expected RED and no files are staged or committed.

## Task 4: Existing Settings Page Integration And Audit Separation

**Files:**

- Modify: `src/views/system/AiProfileImportConfigView.vue`
- Modify: `src/views/system/SettingsView.vue`
- Modify: `scripts/e2e-ai-profile-import-config.mjs`

- [ ] **Step 1: Add integration assertions and verify RED**

Assert that `/system/settings` still shows one DeepSeek entry, the sidebar has no DeepSeek item, and the entry copy is `模型、密钥与 Prompt 版本治理`. On the config page assert model-config audit and Prompt audit have separate headings/data arrays and refreshing one cannot replace the other.

Run:

```powershell
npm run e2e:ai-profile-import-config
```

Expected: FAIL because the existing entry copy and page composition are unchanged.

- [ ] **Step 2: Mount the panel without coupling its state to model configuration**

Import and render:

```vue
<ProfileImportPromptTemplatePanel />
```

Place it after the model configuration/secret/test bands and before the existing configuration-audit card. Keep `load()` responsible only for model config and model-config audits. Rename the visible existing heading to `模型配置审计`; the panel owns `Prompt 模板审计`. Do not pass API keys, model form state, or audit arrays to the panel.

- [ ] **Step 3: Update only the Settings summary text**

Change:

```vue
<span>结构化识别、密钥与调用门禁</span>
```

to:

```vue
<span>模型、密钥与 Prompt 版本治理</span>
```

Do not add a route/sidebar/menu entry.

- [ ] **Step 4: Run GREEN checks and commit**

```powershell
npm run type-check
npm run e2e:ai-profile-import-config
git add src/types/common.ts src/utils/request.ts src/types/ai.ts src/api/ai.ts src/constants/permission.ts src/constants/permission-registry.ts src/components/dialogs/AuditConfirmDialog.vue src/components/business/ProfileImportPromptTemplatePanel.vue src/views/system/AiProfileImportConfigView.vue src/views/system/SettingsView.vue scripts/e2e-ai-profile-import-config.mjs
git commit -m "feat(admin): add profile import prompt governance"
```

Expected: type-check and the same default E2E command both PASS with the full lifecycle, distinct audit sections, and unchanged navigation count. This is the first Task 1-4 production commit; no commit in the slice contains known-red default E2E.

## Task 5: Permission And Prompt-Body Non-Exposure E2E Gate

**Files:**

- Modify: `scripts/e2e-ai-profile-import-config.mjs`
- Modify only if a test exposes a defect: Task 1-4 admin files

- [ ] **Step 1: Add each independent permission scenario**

Run a fresh session and request log for each action. Assert:

```text
template-read: summaries/version rows visible; no edit/test/publish/restore commands
template-update: draft/create/edit/eligible-abandon commands visible only when template-read is also present
template-test: test command visible only when template-read is also present
template-publish: publish command visible only when template-read is also present
template-restore: restore command visible only when template-read is also present
audit: Prompt audit visible and audit API called even without template-read; no template/version/detail API called
```

Action-only sessions without template-read have no actionable version surface because no version data is fetched. This proves action permission does not imply body read.

- [ ] **Step 2: Add the no-read body leakage proof**

Create a session with page permission and every action except `template-read`, including the existing audit action. Add `sentResponsePayloads: []` to mock state and reset it with the request log. In the `Fetch.requestPaused` responder, serialize once and record the exact value that is then sent to Chrome:

```js
const responseJson = JSON.stringify(response)
state.sentResponsePayloads.push(JSON.parse(responseJson))
await client.send('Fetch.fulfillRequest', {
  requestId: event.requestId,
  responseCode: 200,
  responsePhrase: 'OK',
  responseHeaders: [
    { name: 'Content-Type', value: 'application/json; charset=utf-8' },
    { name: 'Cache-Control', value: 'no-store' },
  ],
  body: Buffer.from(responseJson).toString('base64'),
})
```

After resetting both arrays, navigate and wait for network idle. Among the Prompt route family, the audit GET must be the only request; root list, either version list, and every version detail must independently be zero:

```js
const promptRoot = '/admin/ai/profile-import/prompt-templates'
const promptCalls = state.requests.filter(({ pathname }) => pathname.startsWith(promptRoot))
const rootListCalls = promptCalls.filter(({ method, pathname }) =>
  method === 'GET' && pathname === promptRoot)
const versionListCalls = promptCalls.filter(({ method, pathname }) =>
  method === 'GET' && /^\/admin\/ai\/profile-import\/prompt-templates\/(full_profile|works_only)\/versions$/.test(pathname))
const versionDetailCalls = promptCalls.filter(({ method, pathname }) =>
  method === 'GET' && /^\/admin\/ai\/profile-import\/prompt-templates\/versions\/\d+$/.test(pathname))

assertEqual(rootListCalls.length, 0, 'template root-list requests without template-read')
assertEqual(versionListCalls.length, 0, 'version-list requests without template-read')
assertEqual(versionDetailCalls.length, 0, 'version-detail requests without template-read')
assertEqual(
  JSON.stringify(promptCalls.map(({ method, pathname }) => [method, pathname])),
  JSON.stringify([['GET', `${promptRoot}/audits`]]),
  'only Prompt audit may be requested without template-read',
)

function rejectPromptBodyRecursively(value, location = '$') {
  if (typeof value === 'string') {
    if (value.includes(sensitivePromptMarker)) {
      throw new Error(`sensitive Prompt marker in browser response at ${location}`)
    }
    return
  }
  if (Array.isArray(value)) {
    value.forEach((item, index) => rejectPromptBodyRecursively(item, `${location}[${index}]`))
    return
  }
  if (!value || typeof value !== 'object') return
  for (const [key, item] of Object.entries(value)) {
    if (key === 'systemPromptBody' || key === 'repairPromptBody') {
      throw new Error(`Prompt body field in browser response at ${location}.${key}`)
    }
    rejectPromptBodyRecursively(item, `${location}.${key}`)
  }
}

state.sentResponsePayloads.forEach((payload, index) =>
  rejectPromptBodyRecursively(payload, `$responses[${index}]`))

const exposure = await evaluate(client, `(() => {
  const marker = ${jsString(sensitivePromptMarker)};
  const values = Array.from(document.querySelectorAll('input, textarea'))
    .map((node) => String(node.value));
  const storage = JSON.stringify({
    local: Object.fromEntries(Object.keys(localStorage).map((key) => [key, localStorage.getItem(key)])),
    session: Object.fromEntries(Object.keys(sessionStorage).map((key) => [key, sessionStorage.getItem(key)])),
  });
  return {
    dom: document.documentElement.innerHTML.includes(marker) || document.body.innerText.includes(marker),
    form: values.some((value) => value.includes(marker)),
    storage: storage.includes(marker),
  };
})()`)
assertEqual(exposure.dom, false, 'Prompt body in DOM without read permission')
assertEqual(exposure.form, false, 'Prompt body in form values without read permission')
assertEqual(exposure.storage, false, 'Prompt body in browser storage without read permission')
```

The recursive assertion runs against serialized response payloads, not server-side fixtures, so it covers the exact auth/config/audit responses received by the browser. In separate read-enabled list scenarios, run the same recursive assertion over root-list, version-list, and audit responses before any detail request; only the explicit detail response may contain the two body keys or the marker.

- [ ] **Step 3: Prove version-conflict retention and stable branching**

Enter unique local label/System/Repair/change-summary markers, trigger the one-shot 46018 response, and assert all markers remain in live form values. Assert the server snapshot marker appears only in the read-only comparison region. Assert the dialog stays open and the component branched on `errorCode`; change the Chinese message in the mock while keeping `errorCode` and prove behavior remains identical.

Then run this table-driven stable-error matrix. Each mock response uses a randomized Chinese `message` that is deliberately different from production copy; the fixed UI copy must still come from `errorCode`:

```js
const promptErrorCases = [
  ['PROFILE_IMPORT_PROMPT_INVALID', 46019, '模板内容或操作参数无效', 'save', 'editor'],
  ['PROFILE_IMPORT_PROMPT_TEST_REQUIRED', 46020, '请先完成固定样例试运行', 'publish', 'action-dialog'],
  ['PROFILE_IMPORT_PROMPT_TEST_STALE', 46021, '试运行绑定已失效，请重新测试', 'publish', 'action-dialog'],
  ['PROFILE_IMPORT_PROMPT_STATE_CONFLICT', 46022, '当前模板状态不允许该操作', 'abandon', 'action-dialog'],
  ['PROFILE_IMPORT_PROMPT_VERSION_CONFLICT', 46018, '版本已变化，请对照服务端版本人工合并', 'save', 'editor'],
]
```

For every row assert the captured rejection has exact `name`, `code`, `errorCode`, and randomized backend `message`; the rendered copy equals the table's fixed copy and does not contain that randomized message. Save failures keep all local editor fields. Publish/abandon failures keep the draft summary and confirmation state; no success refresh or dialog close occurs. This proves all five R56 branches and prevents localized-message matching.

- [ ] **Step 4: Run the full development E2E and commit**

```powershell
npm run type-check
npm run e2e:ai-profile-import-config
git add scripts/e2e-ai-profile-import-config.mjs src/types/common.ts src/utils/request.ts src/types/ai.ts src/api/ai.ts src/constants/permission.ts src/constants/permission-registry.ts src/components/dialogs/AuditConfirmDialog.vue src/components/business/ProfileImportPromptTemplatePanel.vue src/views/system/AiProfileImportConfigView.vue src/views/system/SettingsView.vue
git commit -m "test(admin): verify prompt governance permissions"
```

Expected terminal summary includes zero console errors, zero warnings, zero page/network/HTTP errors, zero unhandled mocks, plaintext secret scan PASS, and Prompt body no-read scan PASS.

## Task 6: Sanitized Production Build E2E

**Files:**

- Modify: `scripts/e2e-ai-profile-import-config.mjs`

- [ ] **Step 1: Add `--dist` assertions and verify RED before building**

At process startup add:

```js
const distMode = process.argv.includes('--dist')
const distDir = path.resolve(process.env.E2E_DIST_DIR || path.join(projectRoot, 'dist'))

if (distMode && !fsSync.existsSync(path.join(distDir, 'index.html'))) {
  console.error('DIST_INDEX_MISSING')
  process.exit(2)
}
```

Rename `startDevServer()` to `startFrontendServer()` and branch its Vite arguments:

```js
const args = distMode
  ? [viteCli, 'preview', '--outDir', distDir, '--host', '127.0.0.1', '--port', String(port), '--strictPort']
  : [viteCli, '--host', '127.0.0.1', '--port', String(port), '--strictPort']
```

Record `Network.responseReceived` script/stylesheet URLs and, in dist mode, assert at least one `/assets/` URL and zero `/src/` URLs. Log `mode=development` or `mode=dist distDir=<absolute path>` in `e2e.log`.

Prove RED against a newly created empty temporary directory, independent of any stale ignored project `dist`:

```powershell
$emptyDist = Join-Path ([IO.Path]::GetTempPath()) "kaipai-admin-empty-dist-$([guid]::NewGuid().ToString('N'))"
New-Item -ItemType Directory -Path $emptyDist -ErrorAction Stop | Out-Null
try {
  $env:E2E_DIST_DIR = $emptyDist
  $redOutput = @(& npm.cmd run e2e:ai-profile-import-config -- --dist 2>&1 | ForEach-Object { "$_" })
  $redExit = $LASTEXITCODE
  if ($redExit -eq 0) { throw 'dist RED unexpectedly passed' }
  if (-not ($redOutput -contains 'DIST_INDEX_MISSING')) {
    throw "expected exact DIST_INDEX_MISSING, got:`n$($redOutput -join "`n")"
  }
} finally {
  Remove-Item Env:E2E_DIST_DIR -ErrorAction SilentlyContinue
  if (Test-Path -LiteralPath $emptyDist) {
    Remove-Item -LiteralPath $emptyDist -Recurse -Force
  }
}
```

Expected: native exit code is nonzero and one captured output line is exactly `DIST_INDEX_MISSING`. The project `dist` is neither read nor removed by this RED gate.

- [ ] **Step 2: Build, sanitize, and run the real dist E2E**

```powershell
npm run type-check
npm run build
npm run e2e:ai-profile-import-config
$realDist = (Resolve-Path -LiteralPath .\dist).Path
if (-not (Test-Path -LiteralPath (Join-Path $realDist 'index.html') -PathType Leaf)) {
  throw 'real build did not create dist/index.html'
}
try {
  $env:E2E_DIST_DIR = $realDist
  npm run e2e:ai-profile-import-config -- --dist
  if ($LASTEXITCODE -ne 0) { throw 'real dist E2E failed' }
} finally {
  Remove-Item Env:E2E_DIST_DIR -ErrorAction SilentlyContinue
}
```

Expected: all commands exit 0. `npm run build` runs `vue-tsc`, Vite build, and `scripts/sanitize-dist.mjs`; the resolved `E2E_DIST_DIR` is the real project `dist`, and dist E2E proves the settings entry, route guard, Prompt panel, retry/empty/loading/responsive states, lazy detail, permissions, conflict retention, and asset origin from `/assets/`.

- [ ] **Step 3: Commit dist-mode coverage**

```powershell
git add scripts/e2e-ai-profile-import-config.mjs
git commit -m "test(admin): run prompt governance against dist"
```

Do not stage `dist/` unless the admin repository already tracks it and `git status` explicitly shows expected tracked output; current baseline treats it as build output.

## Task 7: Phase A Schema, Governance Deployment, Real Tests, And Normal v1 Releases

**Files:**

- Create: `.sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/verify-phase-a-prompt-state.sql`
- Generate through standard scripts: `.sce/runbooks/backend-admin-release/records/*.md`

Run all Task 7 steps in one PowerShell session. Before Step 1, execute the production tuple block from Preconditions once; retain `$phaseADatabase`, `$phaseAApiBaseUrl`, `$phaseAAdminBaseUrl`, and the provenance variables captured below through Step 9.

- [ ] **Step 1: Create and commit a read-only target-state query**

From the outer repository, create the SQL file with these exact marker queries. The global operation-log contract is fixed by the reviewed 00-200 Spec: `module_code='ai-profile-import'`, `operation_code='prompt-publish'|'prompt-restore'`, `target_type='ai_profile_import_prompt_template'`, and the ten-key value object below. Do not substitute the generic `system` module or infer operation names at rollout time.

```sql
SELECT CONCAT('TEMPLATE_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_template WHERE deleted=0;
SELECT CONCAT('EXPECTED_TEMPLATE_SCENE_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_template WHERE deleted=0 AND ((template_code='full_profile' AND scene='full_profile') OR (template_code='works_only' AND scene='works_only'));
SELECT CONCAT('OPEN_DRAFT_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_version WHERE lifecycle_status='draft' AND deleted=0;
SELECT CONCAT('BOOTSTRAP_UNTESTED_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_version WHERE version_no=1 AND lifecycle_status='draft' AND test_status='untested' AND deleted=0;
SELECT CONCAT('VALID_DRAFT_POINTER_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_template t JOIN ai_profile_import_prompt_version v ON v.prompt_version_id=t.draft_version_id AND v.template_id=t.template_id WHERE t.deleted=0 AND v.deleted=0 AND v.lifecycle_status='draft';
SELECT CONCAT('UNREFERENCED_LIVE_DRAFT_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_version v LEFT JOIN ai_profile_import_prompt_template t ON t.template_id=v.template_id AND t.draft_version_id=v.prompt_version_id AND t.deleted=0 WHERE v.deleted=0 AND v.lifecycle_status='draft' AND t.template_id IS NULL;
SELECT CONCAT('ACTIVE_RELEASED_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_template t JOIN ai_profile_import_prompt_version v ON v.prompt_version_id=t.active_version_id AND v.template_id=t.template_id WHERE t.deleted=0 AND v.deleted=0 AND v.lifecycle_status='released';
SELECT CONCAT('ACTIVE_V1_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_template t JOIN ai_profile_import_prompt_version v ON v.prompt_version_id=t.active_version_id AND v.template_id=t.template_id WHERE t.deleted=0 AND v.deleted=0 AND v.lifecycle_status='released' AND v.version_no=1;
SELECT CONCAT('CROSS_POINTER_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_template t LEFT JOIN ai_profile_import_prompt_version av ON av.prompt_version_id=t.active_version_id LEFT JOIN ai_profile_import_prompt_version dv ON dv.prompt_version_id=t.draft_version_id WHERE t.deleted=0 AND ((t.active_version_id IS NOT NULL AND (av.prompt_version_id IS NULL OR av.template_id<>t.template_id)) OR (t.draft_version_id IS NOT NULL AND (dv.prompt_version_id IS NULL OR dv.template_id<>t.template_id)));
SELECT CONCAT('RELEASE_BINDING_INCOMPLETE_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_template t JOIN ai_profile_import_prompt_version v ON v.prompt_version_id=t.active_version_id AND v.template_id=t.template_id WHERE t.deleted=0 AND (v.deleted<>0 OR v.lifecycle_status<>'released' OR v.test_status<>'success' OR COALESCE(v.content_sha256,'') NOT REGEXP '^[0-9a-f]{64}$' OR NOT (v.tested_content_sha256<=>v.content_sha256) OR COALESCE(v.tested_runtime_sha256,'') NOT REGEXP '^[0-9a-f]{64}$' OR NULLIF(TRIM(v.schema_version),'') IS NULL OR NULLIF(TRIM(v.contract_version),'') IS NULL OR NULLIF(TRIM(v.test_fixture_code),'') IS NULL OR NULLIF(TRIM(v.test_fixture_version),'') IS NULL OR COALESCE(v.test_fixture_sha256,'') NOT REGEXP '^[0-9a-f]{64}$' OR NULLIF(TRIM(v.tested_model_name),'') IS NULL OR v.tested_config_version IS NULL OR v.tested_config_version<=0 OR v.tested_by IS NULL OR v.tested_by<=0 OR v.tested_at IS NULL OR v.released_by IS NULL OR v.released_by<=0 OR v.released_at IS NULL);
SELECT CONCAT('ACTIVE_PUBLISH_AUDIT_CARDINALITY_VIOLATION_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_template t JOIN ai_profile_import_prompt_version v ON v.prompt_version_id=t.active_version_id AND v.template_id=t.template_id WHERE t.deleted=0 AND v.deleted=0 AND (SELECT COUNT(*) FROM ai_profile_import_prompt_audit a WHERE a.template_id=t.template_id AND a.prompt_version_id=v.prompt_version_id AND a.action_code='publish' AND a.result_status='success' AND a.reason_code='INITIAL_RELEASE' AND a.deleted=0)<>1;
SELECT CONCAT('ACTIVE_PUBLISH_BINDING_MISMATCH_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_template t JOIN ai_profile_import_prompt_version v ON v.prompt_version_id=t.active_version_id AND v.template_id=t.template_id WHERE t.deleted=0 AND v.deleted=0 AND NOT EXISTS (SELECT 1 FROM ai_profile_import_prompt_audit a WHERE a.template_id=t.template_id AND a.prompt_version_id=v.prompt_version_id AND a.action_code='publish' AND a.result_status='success' AND a.reason_code='INITIAL_RELEASE' AND a.deleted=0 AND a.content_sha256<=>v.content_sha256 AND a.runtime_sha256<=>v.tested_runtime_sha256 AND a.schema_version<=>v.schema_version AND a.contract_version<=>v.contract_version AND a.fixture_code<=>v.test_fixture_code AND a.fixture_version<=>v.test_fixture_version AND a.fixture_sha256<=>v.test_fixture_sha256 AND a.model_name<=>v.tested_model_name AND a.config_version<=>v.tested_config_version AND a.test_operator_id<=>v.tested_by AND a.tested_at<=>v.tested_at);
SELECT CONCAT('ACTIVE_INITIAL_RELEASE_AUDIT_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_template t JOIN ai_profile_import_prompt_version v ON v.prompt_version_id=t.active_version_id AND v.template_id=t.template_id JOIN ai_profile_import_prompt_audit a ON a.template_id=t.template_id AND a.prompt_version_id=v.prompt_version_id WHERE t.deleted=0 AND v.deleted=0 AND v.lifecycle_status='released' AND v.version_no=1 AND a.deleted=0 AND a.action_code='publish' AND a.reason_code='INITIAL_RELEASE' AND a.result_status='success' AND a.content_sha256=v.content_sha256 AND a.runtime_sha256=v.tested_runtime_sha256 AND a.schema_version=v.schema_version AND a.contract_version=v.contract_version AND a.fixture_code=v.test_fixture_code AND a.fixture_version=v.test_fixture_version AND a.fixture_sha256=v.test_fixture_sha256 AND a.model_name=v.tested_model_name AND a.config_version=v.tested_config_version AND a.test_operator_id=v.tested_by AND a.tested_at=v.tested_at;
SELECT CONCAT('PROMPT_PUBLISH_OPERATION_LOG_COUNT=', COUNT(*)) AS marker FROM admin_operation_log WHERE deleted=0 AND module_code='ai-profile-import' AND operation_code='prompt-publish' AND target_type='ai_profile_import_prompt_template' AND operation_result=1;
SELECT CONCAT('ACTIVE_PUBLISH_OPERATION_LOG_CARDINALITY_VIOLATION_COUNT=', COUNT(*)) AS marker FROM ai_profile_import_prompt_template t JOIN ai_profile_import_prompt_version v ON v.prompt_version_id=t.active_version_id AND v.template_id=t.template_id WHERE t.deleted=0 AND v.deleted=0 AND (SELECT COUNT(*) FROM admin_operation_log l WHERE l.deleted=0 AND l.module_code='ai-profile-import' AND l.operation_code='prompt-publish' AND l.target_type='ai_profile_import_prompt_template' AND l.target_id=t.template_id AND l.operation_result=1 AND JSON_UNQUOTE(JSON_EXTRACT(l.extra_context_json,'$.templateId'))=CAST(t.template_id AS CHAR) AND JSON_UNQUOTE(JSON_EXTRACT(l.extra_context_json,'$.promptVersionId'))=CAST(v.prompt_version_id AS CHAR) AND JSON_UNQUOTE(JSON_EXTRACT(l.extra_context_json,'$.versionNo'))=CAST(v.version_no AS CHAR) AND JSON_UNQUOTE(JSON_EXTRACT(l.extra_context_json,'$.scene'))=t.scene AND JSON_UNQUOTE(JSON_EXTRACT(l.extra_context_json,'$.contentSha256'))=v.content_sha256 AND JSON_UNQUOTE(JSON_EXTRACT(l.extra_context_json,'$.runtimeSha256'))=v.tested_runtime_sha256 AND JSON_UNQUOTE(JSON_EXTRACT(l.extra_context_json,'$.reasonCode'))='INITIAL_RELEASE')<>1;
WITH prompt_operation_logs AS (SELECT l.*, CASE WHEN l.extra_context_json IS NOT NULL AND JSON_VALID(l.extra_context_json)=1 THEN l.extra_context_json ELSE JSON_OBJECT() END AS safe_payload, CASE WHEN l.extra_context_json IS NOT NULL AND JSON_VALID(l.extra_context_json)=1 THEN 1 ELSE 0 END AS payload_valid FROM admin_operation_log l WHERE l.deleted=0 AND l.module_code='ai-profile-import' AND l.operation_code IN ('prompt-publish','prompt-restore')) SELECT CONCAT('PROMPT_OPERATION_LOG_PAYLOAD_VIOLATION_COUNT=', COUNT(*)) AS marker FROM prompt_operation_logs l WHERE l.target_type<>'ai_profile_import_prompt_template' OR l.target_id IS NULL OR l.target_id<=0 OR l.operation_result<>1 OR l.before_snapshot_json IS NOT NULL OR l.after_snapshot_json IS NOT NULL OR l.fail_reason IS NOT NULL OR l.confirm_token IS NOT NULL OR l.confirmed_at IS NOT NULL OR l.payload_valid=0 OR JSON_TYPE(l.safe_payload)<>'OBJECT' OR JSON_LENGTH(JSON_KEYS(l.safe_payload))<>10 OR NOT JSON_CONTAINS_PATH(l.safe_payload,'all','$.templateId','$.promptVersionId','$.versionNo','$.scene','$.contentSha256','$.runtimeSha256','$.lifecycleStatus','$.reasonCode','$.candidateCount','$.workCount') OR JSON_TYPE(JSON_EXTRACT(l.safe_payload,'$.templateId')) NOT IN ('INTEGER','UNSIGNED INTEGER') OR CAST(JSON_UNQUOTE(JSON_EXTRACT(l.safe_payload,'$.templateId')) AS UNSIGNED)<>l.target_id OR JSON_TYPE(JSON_EXTRACT(l.safe_payload,'$.promptVersionId')) NOT IN ('INTEGER','UNSIGNED INTEGER') OR CAST(JSON_UNQUOTE(JSON_EXTRACT(l.safe_payload,'$.promptVersionId')) AS UNSIGNED)<=0 OR JSON_TYPE(JSON_EXTRACT(l.safe_payload,'$.versionNo')) NOT IN ('INTEGER','UNSIGNED INTEGER') OR CAST(JSON_UNQUOTE(JSON_EXTRACT(l.safe_payload,'$.versionNo')) AS UNSIGNED)<=0 OR JSON_UNQUOTE(JSON_EXTRACT(l.safe_payload,'$.scene')) NOT IN ('full_profile','works_only') OR JSON_UNQUOTE(JSON_EXTRACT(l.safe_payload,'$.contentSha256')) NOT REGEXP '^[0-9a-f]{64}$' OR JSON_UNQUOTE(JSON_EXTRACT(l.safe_payload,'$.runtimeSha256')) NOT REGEXP '^[0-9a-f]{64}$' OR JSON_UNQUOTE(JSON_EXTRACT(l.safe_payload,'$.lifecycleStatus'))<>'released' OR JSON_UNQUOTE(JSON_EXTRACT(l.safe_payload,'$.reasonCode')) NOT IN ('INITIAL_RELEASE','QUALITY_ADJUSTMENT','CONFIG_ALIGNMENT','QUALITY_REGRESSION','INCIDENT_ROLLBACK') OR JSON_TYPE(JSON_EXTRACT(l.safe_payload,'$.candidateCount')) NOT IN ('INTEGER','UNSIGNED INTEGER') OR CAST(JSON_UNQUOTE(JSON_EXTRACT(l.safe_payload,'$.candidateCount')) AS SIGNED)<0 OR JSON_TYPE(JSON_EXTRACT(l.safe_payload,'$.workCount')) NOT IN ('INTEGER','UNSIGNED INTEGER') OR CAST(JSON_UNQUOTE(JSON_EXTRACT(l.safe_payload,'$.workCount')) AS SIGNED)<0;
SELECT CONCAT('ELIGIBLE_ROLE_MISSING_PROMPT_PERMISSION_COUNT=', COUNT(*)) AS marker FROM admin_role WHERE status=1 AND deleted=0 AND (LOWER(role_code) IN ('admin','super_admin') OR JSON_CONTAINS(COALESCE(menu_permissions_json,JSON_ARRAY()),JSON_QUOTE('menu.system'))) AND NOT (JSON_CONTAINS(COALESCE(page_permissions_json,JSON_ARRAY()),JSON_QUOTE('page.system.ai-profile-import')) AND JSON_CONTAINS(COALESCE(action_permissions_json,JSON_ARRAY()),JSON_QUOTE('action.system.ai-profile-import.audit')) AND JSON_CONTAINS(COALESCE(action_permissions_json,JSON_ARRAY()),JSON_QUOTE('action.system.ai-profile-import.template-read')) AND JSON_CONTAINS(COALESCE(action_permissions_json,JSON_ARRAY()),JSON_QUOTE('action.system.ai-profile-import.template-update')) AND JSON_CONTAINS(COALESCE(action_permissions_json,JSON_ARRAY()),JSON_QUOTE('action.system.ai-profile-import.template-test')) AND JSON_CONTAINS(COALESCE(action_permissions_json,JSON_ARRAY()),JSON_QUOTE('action.system.ai-profile-import.template-publish')) AND JSON_CONTAINS(COALESCE(action_permissions_json,JSON_ARRAY()),JSON_QUOTE('action.system.ai-profile-import.template-restore')));
SELECT CONCAT('FORBIDDEN_AUDIT_SCHEMA_COLUMN_COUNT=', COUNT(*)) AS marker FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name IN ('ai_profile_import_prompt_audit','ai_profile_import_request_audit','admin_operation_log') AND column_name IN ('system_prompt_body','repair_prompt_body','raw_text','raw_response','source_text','fixture_body','api_key','secret','change_summary','free_reason');
```

Commit only this new SQL from `D:\XM\kaipai-team`:

```powershell
git add .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/verify-phase-a-prompt-state.sql
git commit -m "test(sce): add prompt phase a state gate"
```

Expected: existing 00-199 edits and `.tmp-kaipaile-server-pdf-retry/` remain unstaged.

- [ ] **Step 2: Rerun fresh local backend and admin gates immediately before release**

```powershell
$workspaceRoot = 'D:\XM\kaipai-team'
$backendRoot = Join-Path $workspaceRoot 'kaipaile-server'
$backendPlan = Join-Path $workspaceRoot 'docs\superpowers\plans\2026-07-26-00-200-prompt-governance-backend.md'
$backendPlanLines = Get-Content -LiteralPath $backendPlan
$fileMapStart = [Array]::IndexOf($backendPlanLines, '## File Map')
$task1Start = [Array]::IndexOf($backendPlanLines, '## Task 1: Persistence Shape, Bootstrap Drafts, And Locking Mappers')
if ($fileMapStart -lt 0 -or $task1Start -le $fileMapStart) { throw '00-200 backend File Map boundary missing' }
$phaseABackendPaths = @($backendPlanLines[($fileMapStart + 1)..($task1Start - 1)] | ForEach-Object {
  if ($_ -match '^- `(?<path>src/(?:main|test)/[^`]+)`$') { $Matches.path }
} | Sort-Object -Unique)
if ($phaseABackendPaths.Count -ne 56) { throw "expected 56 reviewed 00-200 backend paths, got $($phaseABackendPaths.Count)" }

Push-Location $backendRoot
try {
  $phaseAHead = (git rev-parse HEAD).Trim()
  if ($LASTEXITCODE -ne 0 -or $phaseAHead -notmatch '^[0-9a-f]{40}$') { throw 'cannot capture phaseAHead' }
  foreach ($relativePath in $phaseABackendPaths) {
    git cat-file -e "$($phaseAHead):$relativePath"
    if ($LASTEXITCODE -ne 0) { throw "00-200 path absent from phaseAHead: $relativePath" }
  }
  git diff --exit-code $phaseAHead -- @phaseABackendPaths
  if ($LASTEXITCODE -ne 0) { throw '00-200 backend path differs from phaseAHead' }
  $phaseAPathStatus = @(git status --porcelain --untracked-files=all -- @phaseABackendPaths)
  if ($phaseAPathStatus.Count -ne 0) { throw "00-200 backend path status is not clean:`n$($phaseAPathStatus -join "`n")" }

  $phaseAControllerPath = 'src/main/java/com/kaipai/controller/admin/ai/AdminAiProfileImportPromptController.java'
  $phaseAOverlayBlob = (git rev-parse "$($phaseAHead):$phaseAControllerPath").Trim()
  $phaseAWorkingControllerBlob = (git hash-object -- $phaseAControllerPath).Trim()
  if ($phaseAOverlayBlob -ne $phaseAWorkingControllerBlob) { throw 'controller overlay blob differs from phaseAHead' }

  $phaseAWorktree = Join-Path ([IO.Path]::GetTempPath()) "kaipai-phase-a-$([guid]::NewGuid().ToString('N'))"
  try {
    git worktree add --detach $phaseAWorktree $phaseAHead
    if ($LASTEXITCODE -ne 0) { throw 'detached Phase A worktree creation failed' }
    Push-Location $phaseAWorktree
    try {
      mvn -q "-Dtest=AiProfileImportPersistenceShapeTest,ProfileImportConfigServiceImplTest,AdminOperationLoggerTest,ProfileImportErrorContractTest,ProfileImportPromptPolicyTest,ProfileImportPromptRendererTest,ProfileImportPromptRuntimeResolverImplTest,ProfileImportPromptManagementServiceImplTest,ProfileImportPromptTesterImplTest,AdminAiProfileImportPromptControllerTest,DeepSeekProfileTextExtractorTest,ProfileImportServiceImplTest,ProfileImportSchemaValidatorTest,ProfileImportCandidateProofServiceTest,ProfileImportApplyServiceImplTest,ProfileImportPromptGovernanceMySqlIntegrationTest,ProfileImportApplyMySqlIntegrationTest" test
      if ($LASTEXITCODE -ne 0) { throw 'detached Phase A Maven selector failed' }
      mvn -q clean package
      if ($LASTEXITCODE -ne 0) { throw 'detached Phase A Maven package failed' }
    } finally {
      Pop-Location
    }
  } finally {
    if (Test-Path -LiteralPath $phaseAWorktree) {
      git worktree remove --force $phaseAWorktree
      if ($LASTEXITCODE -ne 0) { throw 'detached Phase A worktree cleanup failed' }
    }
  }
} finally {
  Pop-Location
}

Set-Location D:\XM\kaipai-team\kaipai-admin
npm run type-check
if ($LASTEXITCODE -ne 0) { throw 'admin type-check failed' }
npm run build
if ($LASTEXITCODE -ne 0) { throw 'admin build failed' }
npm run e2e:ai-profile-import-config
if ($LASTEXITCODE -ne 0) { throw 'admin development E2E failed' }
npm run e2e:ai-profile-import-config -- --dist
if ($LASTEXITCODE -ne 0) { throw 'admin real-dist E2E failed' }
```

Expected: all 56 reviewed 00-200 paths exist in `$phaseAHead`, have no tracked or untracked difference from that HEAD, and the controller overlay blob equals the HEAD blob. Both Maven gates run from a detached clean worktree at exactly `$phaseAHead`; every command exits 0 and Docker-backed MySQL tests execute. The ordinary dirty backend worktree is never used for test/package evidence.

- [ ] **Step 3: Apply V001 and V002 through the standard schema release script**

Return to `D:\XM\kaipai-team` and run both the sanitized dual-environment check and the live production-container profile readback before any schema write. Keep raw runtime output only in memory; do not print or persist environment values.

```powershell
Set-Location D:\XM\kaipai-team
if ($phaseADatabase -eq 'kaipai_dev' -and ($phaseAApiBaseUrl -eq 'https://api.kplyyk.com' -or $phaseAAdminBaseUrl -eq 'https://kplyyk.com')) {
  throw 'production domains cannot be paired with kaipai_dev'
}
if ($phaseATuple -ne 'kaipai_prod|https://api.kplyyk.com|https://kplyyk.com') { throw 'Phase A tuple changed after capture' }

$preflightText = (& python .sce/runbooks/backend-admin-release/scripts/check-dual-env-preflight.py --prod-database $phaseADatabase 2>&1 | Out-String)
$preflightExit = $LASTEXITCODE
if ($preflightExit -ne 0) { throw 'production dual-environment preflight failed' }
$preflight = $preflightText | ConvertFrom-Json
$prodNacos = $preflight.gates.nacos.prod
$prodDatabaseGate = $preflight.gates.database.databases.PSObject.Properties[$phaseADatabase].Value
if (-not $preflight.passed -or -not $prodNacos.readable -or -not $prodNacos.containsExpectedDatabase -or $prodNacos.expectedDatabase -ne $phaseADatabase -or -not $prodDatabaseGate.passed) {
  throw 'production runtime datasource readback does not resolve exclusively to the Phase A database gate'
}

$runtimeReadback = (& ssh -i C:\Users\33340\.ssh\kaipai_release_ed25519 kaipaile@101.43.57.62 "sudo -n /usr/local/bin/kaipai-backend-release-helper.sh --runtime-diagnostics --container kaipai-backend --since 1m --tail 1" 2>&1 | Out-String)
$runtimeExit = $LASTEXITCODE
if ($runtimeExit -ne 0 -or $runtimeReadback -notmatch '(?m)^SPRING_PROFILES_ACTIVE=prod\r?$' -or $runtimeReadback -notmatch '(?m)^NACOS_ENABLED=true\r?$') {
  $runtimeReadback = $null
  throw 'production profile/env readback is absent or mismatched'
}
$runtimeReadback = $null

python .sce/runbooks/backend-admin-release/scripts/run-backend-schema-migration.py --label 00-200-prompt-phase-a --operator codex --mysql-database $phaseADatabase --migration-file kaipaile-server/src/main/resources/db/migration/V20260726_001__ai_profile_import_prompt_template_governance.sql --migration-file kaipaile-server/src/main/resources/db/migration/V20260726_002__ai_profile_import_prompt_permission_alignment.sql
if ($LASTEXITCODE -ne 0) { throw 'Phase A schema migration failed' }
```

Expected: the immutable tuple, sanitized prod Nacos datasource result, reachable database gate, and live container `prod`/Nacos readback all agree before the migration command runs. Missing readback, `kaipai_dev`, or either nonproduction domain is a hard stop. Schema release exits 0, creates a `backend-schema` release record, records both filenames in `kaipai_prod.schema_release_history`, and performs no application deployment. If target history is not initialized, stop and follow the runbook's `--mode baseline-existing`; do not bypass the history gate.

- [ ] **Step 4: Prove the honest bootstrap target state before backend deployment**

Upload and execute the read-only verification through the installed helper:

```powershell
scp -i C:\Users\33340\.ssh\kaipai_release_ed25519 .sce/specs/00-200-current-phase-deepseek-profile-import-prompt-template-governance/scripts/verify-phase-a-prompt-state.sql kaipaile@101.43.57.62:/tmp/00-200-verify-phase-a.sql
if ($LASTEXITCODE -ne 0) { throw 'Phase A verification SQL upload failed' }
ssh -i C:\Users\33340\.ssh\kaipai_release_ed25519 kaipaile@101.43.57.62 "sudo -n /usr/local/bin/kaipai-backend-release-helper.sh --mysql-validation --mysql-script-path /tmp/00-200-verify-phase-a.sql --mysql-database $phaseADatabase --mysql-container kaipai-mysql"
if ($LASTEXITCODE -ne 0) { throw 'initial Phase A marker validation failed' }
```

Expected initial markers:

```text
TEMPLATE_COUNT=2
EXPECTED_TEMPLATE_SCENE_COUNT=2
OPEN_DRAFT_COUNT=2
BOOTSTRAP_UNTESTED_COUNT=2
VALID_DRAFT_POINTER_COUNT=2
UNREFERENCED_LIVE_DRAFT_COUNT=0
ACTIVE_RELEASED_COUNT=0
ACTIVE_V1_COUNT=0
CROSS_POINTER_COUNT=0
RELEASE_BINDING_INCOMPLETE_COUNT=0
ACTIVE_PUBLISH_AUDIT_CARDINALITY_VIOLATION_COUNT=0
ACTIVE_PUBLISH_BINDING_MISMATCH_COUNT=0
ACTIVE_INITIAL_RELEASE_AUDIT_COUNT=0
PROMPT_PUBLISH_OPERATION_LOG_COUNT=0
ACTIVE_PUBLISH_OPERATION_LOG_CARDINALITY_VIOLATION_COUNT=0
PROMPT_OPERATION_LOG_PAYLOAD_VIOLATION_COUNT=0
ELIGIBLE_ROLE_MISSING_PROMPT_PERMISSION_COUNT=0
FORBIDDEN_AUDIT_SCHEMA_COLUMN_COUNT=0
```

The binding/audit/operation-log active-row markers are vacuous before any active release; `ACTIVE_RELEASED_COUNT=0` and `ACTIVE_V1_COUNT=0` make that explicit. The two draft counts, `VALID_DRAFT_POINTER_COUNT=2`, and `UNREFERENCED_LIVE_DRAFT_COUNT=0` jointly prove that both live bootstrap drafts are referenced by their owning templates.

- [ ] **Step 5: Deploy the Phase A backend and admin through standard scripts**

The backend repository may still contain unrelated dirty files. Recheck the captured HEAD and all reviewed 00-200 paths, then use the standard clean-HEAD snapshot mode with one overlay whose blob was already proved identical to HEAD. Require a completely clean admin worktree before its release; ignored `dist/` is allowed because `git status --porcelain --untracked-files=all` does not report it.

```powershell
Set-Location D:\XM\kaipai-team\kaipaile-server
if ((git rev-parse HEAD).Trim() -ne $phaseAHead) { throw 'backend HEAD changed after Phase A verification' }
git diff --exit-code $phaseAHead -- @phaseABackendPaths
if ($LASTEXITCODE -ne 0) { throw '00-200 backend path changed after Phase A verification' }
if ((git hash-object -- $phaseAControllerPath).Trim() -ne $phaseAOverlayBlob) { throw 'controller overlay blob changed after Phase A verification' }

Set-Location D:\XM\kaipai-team
python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py --label 00-200-prompt-phase-a --operator codex --public-base-url $phaseAApiBaseUrl --mysql-database $phaseADatabase --overlay-path $phaseAControllerPath
if ($LASTEXITCODE -ne 0) { throw 'Phase A backend release failed' }

Set-Location D:\XM\kaipai-team\kaipai-admin
$adminReleaseStatus = @(git status --porcelain --untracked-files=all)
if ($adminReleaseStatus.Count -ne 0) { throw "admin worktree must be clean before release:`n$($adminReleaseStatus -join "`n")" }
$phaseAAdminHead = (git rev-parse HEAD).Trim()
$phaseAAdminSourceTree = (git rev-parse "$($phaseAAdminHead)^{tree}").Trim()
if ($phaseAAdminHead -notmatch '^[0-9a-f]{40}$' -or $phaseAAdminSourceTree -notmatch '^[0-9a-f]{40}$') { throw 'admin source provenance capture failed' }

Set-Location D:\XM\kaipai-team
python .sce/runbooks/backend-admin-release/scripts/run-admin-only-release.py --label 00-200-prompt-phase-a --operator codex --public-base-url $phaseAAdminBaseUrl
if ($LASTEXITCODE -ne 0) { throw 'Phase A admin release failed' }
```

Expected: both scripts exit 0 and write release records containing artifact SHA, backups, inner/public smoke, and post-release review. The backend record must read back `SPRING_PROFILES_ACTIVE=prod`, `NACOS_ENABLED=true`, and schema-history target `kaipai_prod`; any different database/profile combination is a hard stop. If the backend helper reports any unrecorded migration, stop instead of bypassing the schema history check. The backend-only record intentionally reports local release commit as `N/A`; provenance is `$phaseAHead` plus the identical `$phaseAOverlayBlob` and the record's local/remote JAR SHA, not a claimed deployed commit. The admin record must expose its generated snapshot commit and remote dist SHA; relate them to `$phaseAAdminHead` and `$phaseAAdminSourceTree` in execution evidence.

- [ ] **Step 6: Confirm Phase A runtime still uses legacy production recognition**

Inspect the exact backend source HEAD captured and tested before release. Do not use working-tree files, and do not read a nonexistent backend deployed commit from the backend-only release record:

```powershell
Set-Location D:\XM\kaipai-team\kaipaile-server
$extractorAtPhaseAHead = @(git show "$($phaseAHead):src/main/java/com/kaipai/integration/ai/profileimport/DeepSeekProfileTextExtractor.java")
if ($LASTEXITCODE -ne 0) { throw 'cannot read extractor from phaseAHead' }
$serviceAtPhaseAHead = @(git show "$($phaseAHead):src/main/java/com/kaipai/service/ai/impl/ProfileImportServiceImpl.java")
if ($LASTEXITCODE -ne 0) { throw 'cannot read service from phaseAHead' }

$extractorAtPhaseAHead | rg -n "LEGACY_SYSTEM_PROMPT|legacy-code-v1"
if ($LASTEXITCODE -ne 0) { throw 'legacy extractor marker absent from phaseAHead' }
$serviceAtPhaseAHead | rg -n "extract\(config, runtime\.apiKey\(\), request\.getRawText\(\), requestId\)"
if ($LASTEXITCODE -ne 0) { throw 'legacy four-argument production call absent from phaseAHead' }
$serviceAtPhaseAHead | rg -n "ProfileImportPromptRuntimeResolver"
if ($LASTEXITCODE -eq 0) { throw 'Phase A service already depends on Prompt runtime resolver' }
if ($LASTEXITCODE -ne 1) { throw 'resolver-absence search failed' }
```

Expected: both positive searches exit 0 and the resolver-absence search exits exactly 1. Record the matching lines with `$phaseAHead`; no working-tree or UI inference is accepted.

- [ ] **Step 7: Real-test and normally publish both bootstrap v1 drafts**

Open [the deployed settings page](https://kplyyk.com/system/ai-profile-import) with an administrator holding the five new actions and existing audit permission. For `完整资料` and then `仅作品`:

1. Confirm the current version is empty, the open draft is v1, and status is `未测试`.
2. Run `固定样例试运行` and wait for completion; the request timeout is 180 seconds.
3. Require status `success`, nonempty content/runtime/fixture hashes, the current model name/config version, and scene-appropriate counts. `仅作品` must report zero profile candidates.
4. Open publish confirmation, choose `首次发布`, and submit.
5. Confirm v1 becomes released/current, draft pointer clears, and a publish audit appears.

If either test fails or becomes stale, stop. Do not update SQL pointers, fake test metadata, or publish only one scene and continue to Phase B.

- [ ] **Step 8: Prove the released target state and immutable binding**

Rerun the same helper validation command from Step 4. Expected final markers:

```text
TEMPLATE_COUNT=2
EXPECTED_TEMPLATE_SCENE_COUNT=2
OPEN_DRAFT_COUNT=0
BOOTSTRAP_UNTESTED_COUNT=0
VALID_DRAFT_POINTER_COUNT=0
UNREFERENCED_LIVE_DRAFT_COUNT=0
ACTIVE_RELEASED_COUNT=2
ACTIVE_V1_COUNT=2
CROSS_POINTER_COUNT=0
RELEASE_BINDING_INCOMPLETE_COUNT=0
ACTIVE_PUBLISH_AUDIT_CARDINALITY_VIOLATION_COUNT=0
ACTIVE_PUBLISH_BINDING_MISMATCH_COUNT=0
ACTIVE_INITIAL_RELEASE_AUDIT_COUNT=2
PROMPT_PUBLISH_OPERATION_LOG_COUNT=2
ACTIVE_PUBLISH_OPERATION_LOG_CARDINALITY_VIOLATION_COUNT=0
PROMPT_OPERATION_LOG_PAYLOAD_VIOLATION_COUNT=0
ELIGIBLE_ROLE_MISSING_PROMPT_PERMISSION_COUNT=0
FORBIDDEN_AUDIT_SCHEMA_COLUMN_COUNT=0
```

Also refresh `Prompt 模板审计` and require one successful `test` plus one successful `publish` action per scene. The model-config audit remains separate. Capture the helper output and browser screenshots under the Phase A release record/evidence directory without Prompt bodies, fixtures, user text, API keys, or full model responses.

- [ ] **Step 9: Record the hard Phase B prerequisite**

Record these exact facts in the active 00-200 execution notes before `2026-07-26-00-200-runtime-phase-b-cutover.md` creates `execution.md`:

```text
Phase A schema release record path and release ID
phaseAHead and the 56-path zero-diff gate result
controller overlay blob SHA and proof that it equals the phaseAHead blob
backend release record path plus local JAR, remote JAR, and container JAR SHA256
phaseAAdminHead and phaseAAdminSourceTree
admin release record path, generated snapshot commit, and remote dist archive SHA256
initial and final marker outputs
full_profile v1 content/runtime/fixture/model/config binding IDs and hashes
works_only v1 content/runtime/fixture/model/config binding IDs and hashes
publish audit IDs
legacy-code-v1 git-show proof tied to phaseAHead
```

Record hashes and IDs only. Do not copy Prompt/fixture/user/model-response bodies or secrets.

## Requirements Coverage Self-Check

| Requirements | Admin/rollout evidence in this plan |
|---|---|
| R1-R2 | Existing settings route and seven-page navigation retained; no style-template reuse |
| R3-R17 | Two scene tabs, draft lifecycle, first-release abandon guard, history/restore UI |
| R18-R26 | Read-only contract metadata; body editor cannot modify Schema/contract; separate body/detail requests |
| R27-R37 | Fixed-fixture test action, stable status/binding display, fixed publish/restore reasons |
| R38-R45 | Phase A deployment proves legacy production path; audits/DOM/storage exclude sensitive bodies |
| R46-R57 | Lazy detail, independent action permissions, stable `errorCode`, conflict draft retention |
| R58-R63 | Standard additive schema rollout, honest bootstrap state, two normal v1 releases before cutover |
| R64-R68 | Backend gates from `2026-07-26-00-200-prompt-governance-backend.md` rerun in a detached clean `$phaseAHead` worktree; 56 reviewed paths and overlay blob are HEAD-identical |
| R69-R70 | Development CDP E2E, deterministic empty-dist RED, real project-dist GREEN, retry/empty/loading/390px gates, exact no-read route counts, and recursive sent-payload body scan |
| R71 | Fresh backend selector/package results from the detached `$phaseAHead` worktree immediately before Phase A release |
| R72 | Backend HEAD/overlay/artifact and admin HEAD/tree/snapshot/dist provenance captured for `2026-07-26-00-200-runtime-phase-b-cutover.md` execution evidence |

Do not begin `2026-07-26-00-200-runtime-phase-b-cutover.md` unless every final marker and both normal publish audits exist.
