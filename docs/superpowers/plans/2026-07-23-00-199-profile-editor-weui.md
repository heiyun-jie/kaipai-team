# 00-199 Profile Editor WeUI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current warm card-style `pages/actor-profile/edit` UI with the confirmed WeUI-inspired grouped editor while preserving the versioned profile draft, asset-based avatar selection, reviewed AI import, and single-save contract.

**Architecture:** Keep the existing route, API types, draft object, validation, asset-selection store, and import-review route. Recompose only the page shell and interaction presentation around `KpFloatingBackButton`, independent inline career/intro expansion, one bottom multi-select sheet for all tag fields, explicit page states, and a fixed flex footer; do not add a new edit route or restore legacy media/work fields.

**Tech Stack:** uni-app 3, Vue 3.4 Composition API, TypeScript, SCSS, WeChat Mini Program APIs, existing Node static governance script.

---

## Preconditions And File Map

The written design baseline is outer-repository commit `7e43eee`. Work remains on branch `codex/00-199-miniapp-profile-library-import` in both the outer repository and `kaipai-frontend`; do not create a worktree. Preserve unrelated frontend changes in `src/api/auth.ts`, `src/pages/login/index.vue`, `src/utils/runtime.ts`, and `pnpm-lock.yaml`.

This plan implements R21-R31h and the profile-editor portions of R124, R129, R133-R136, and R148-R150.

- Modify: `.sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs`
- Modify: `kaipai-frontend/src/pages/actor-profile/edit.vue`
- Verify generated: `kaipai-frontend/dist/build/mp-weixin/pages/actor-profile/edit.wxml`
- Verify generated: `kaipai-frontend/dist/build/mp-weixin/pages/actor-profile/edit.wxss`
- Verify generated: `kaipai-frontend/dist/dev/mp-weixin/pages/actor-profile/edit.wxml`
- Verify generated: `kaipai-frontend/dist/dev/mp-weixin/pages/actor-profile/edit.wxss`

The page must continue calling only:

```ts
getMyCareerProfile({ showLoading: false, showError: false })
updateMyActorProfile(draft)
assetSelectionStore.consumeAvatar()
importStore.setContext('full_profile', draft.expectedProfileVersion, workLibraryVersion.value)
```

It must not call the legacy `updateActorProfile` aggregate writer or add photo, video, PDF, work, or completeness data back into the page.

## Task 1: Add The Confirmed Profile-Editor Red Gate

**Files:**
- Modify: `.sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs`
- Test: the same static verification script

- [ ] **Step 1: Remove the editor from the old warm-style loop**

Keep the warm neutral and display-font assertions for history, favorites, assets, import review, works, work edit, and settings. Remove only `kaipai-frontend/src/pages/actor-profile/edit.vue` from that loop because R135 now makes it an explicit WeUI-neutral exception.

- [ ] **Step 2: Add source assertions for R31b-R31h**

Add these assertions next to the existing `const edit = ...` block:

```js
assertMatch(edit, /<KpFloatingBackButton\s+@click="requestLeave"/, 'Shared floating back button')
assertNoMatch(edit, /KpCapsuleSpacer|profile-edit__back|<text>‹<\/text>/, 'No private profile back control')
assertMatch(edit, /从复制内容智能填写[\s\S]*核心资料/, 'Import entry precedes core profile')
assertMatch(edit, /profile-edit__cell-group/, 'WeUI cell groups')
assertMatch(edit, /careerExpanded[\s\S]*introExpanded/, 'Independent inline editor expansion')
assertMatch(edit, /activeTagField[\s\S]*profile-edit__tag-sheet/, 'Bottom multi-select tag sheet')
assertMatch(edit, /workLibraryVersion\.value[\s\S]*setContext\(scene, draft\.expectedProfileVersion, workLibraryVersion\.value\)/, 'Real import context version')
assertMatch(edit, /getMyCareerProfile\(\{\s*showLoading:\s*false,\s*showError:\s*false\s*\}\)/, 'Page-owned load error feedback')
assertMatch(edit, /保存资料并返回[\s\S]*放弃修改[\s\S]*继续编辑/, 'Dirty leave action sheet')
assertMatch(edit, /background:\s*#f5f5f5/i, 'Neutral profile page background')
assertMatch(edit, /background:\s*#242424/i, 'Neutral profile primary action')
assertMatch(edit, /profile-edit__tag-sheet[\s\S]*border-radius:\s*28rpx\s+28rpx\s+0\s+0/, 'Tag sheet top radius')
assertNoMatch(
  edit,
  /linear-gradient|\$kp-font-family-display|\$kp-shadow-card|\$kp-radius-card/,
  'No warm card visual language in profile editor',
)
assertNoMatch(edit, /多个内容用逗号分隔/, 'No comma-entry tag editor')
```

- [ ] **Step 3: Run the red gate and confirm the failure reason**

Run:

```powershell
cd D:\XM\kaipai-team
node .sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: FAIL first at `Shared floating back button`; the current source still imports `KpCapsuleSpacer`, renders a private `‹`, uses a gradient/card tokens, and lacks a tag sheet.

- [ ] **Step 4: Commit only the red gate**

```powershell
git add .sce/specs/00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import/scripts/verify-miniapp-career-profile-hub.mjs
git commit -m "test(miniapp): gate weui profile editor"
```

## Task 2: Recompose Navigation, First Viewport, And Page States

**Files:**
- Modify: `kaipai-frontend/src/pages/actor-profile/edit.vue`
- Test: outer static verification script

- [ ] **Step 1: Replace the private header with the shared navigation component**

Use this shell and keep `requestLeave` as the click handler:

```vue
<view class="profile-edit">
  <view class="profile-edit__nav">
    <KpFloatingBackButton @click="requestLeave" />
    <text class="profile-edit__nav-title">个人档案</text>
  </view>

  <scroll-view scroll-y class="profile-edit__scroll">
    <!-- loading, error, and editor content -->
  </scroll-view>

  <view class="profile-edit__footer">
    <button class="profile-edit__save" :disabled="saving || loading || !!loadError" @click="saveProfile">
      {{ saving ? '保存中...' : '保存资料' }}
    </button>
  </view>
</view>
```

Replace `KpCapsuleSpacer` with:

```ts
import KpFloatingBackButton from '@/components/KpFloatingBackButton.vue';
```

The root is a `100vh` column flex container. The shared navigation owns its runtime capsule height, the scroll view uses `flex: 1; min-height: 0`, and the footer remains outside the scroll view so safe-area content is never covered.

- [ ] **Step 2: Put the smart-import cell before core data**

The first editable content must be:

```vue
<view class="profile-edit__cell-group">
  <view class="profile-edit__cell profile-edit__cell--action" @click="openImportReview">
    <view class="profile-edit__cell-main">
      <text class="profile-edit__cell-title">从复制内容智能填写</text>
      <text class="profile-edit__cell-desc">识别后由你确认再填入</text>
    </view>
    <text class="profile-edit__chevron">›</text>
  </view>
</view>
```

Follow it with a `核心资料` group containing avatar, public name, gender, age, height, and current city. Inputs are right-aligned row values, the gender control is a compact two-item segmented control, and the avatar row still calls `chooseAvatarFromAssets`.

- [ ] **Step 3: Add independent summary entries for career and intro**

Add script state and summaries:

```ts
const careerExpanded = ref(false);
const introExpanded = ref(false);
const workLibraryVersion = ref(0);

const careerSummary = computed(() => {
  const values = [
    draft.career.weight,
    draft.career.originPlace,
    draft.career.schoolName,
    draft.career.majorName,
    ...draft.career.languageTags,
    ...draft.career.specialtyTags,
    ...draft.career.roleTypeTags,
    ...draft.career.professionalAbilityTags,
  ];
  const count = values.filter((value) => value !== null && String(value).trim()).length;
  return count ? `已填写 ${count} 项` : '待完善';
});

const introSummary = computed(() => {
  const value = draft.intro.trim();
  return value ? (value.length > 24 ? `${value.slice(0, 24)}...` : value) : '待完善';
});
```

Set `workLibraryVersion.value = profile.workLibraryVersion` inside `hydrateDraft`. Career and intro rows toggle their own booleans. Do not close one when opening the other. Career renders its scalar rows inline; intro renders its textarea inline. `openImportReview` must pass `workLibraryVersion.value`, never a fixed `0`.

- [ ] **Step 4: Implement loading and service-error states**

Use `v-if="loading"`, `v-else-if="loadError"`, and `v-else` so a real load failure does not look like an empty valid profile. Loading renders fixed skeleton rows plus “正在读取档案”; an error renders “档案读取失败” and a `重新加载` button bound to `loadProfile`. Call `getMyCareerProfile({ showLoading: false, showError: false })` so the request layer does not also emit a Toast. The existing `profileVersion=0` backend response continues through `hydrateDraft` and therefore displays the normal empty form without an error toast.

- [ ] **Step 5: Apply the confirmed neutral tokens**

Use exact page-local values:

```scss
.profile-edit {
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  color: #191919;

  &__nav { position: relative; flex: 0 0 auto; background: #ffffff; border-bottom: 1rpx solid #ededed; }
  &__nav-title { position: absolute; right: 160rpx; bottom: 0; left: 160rpx; height: 64rpx; font-size: 34rpx; line-height: 64rpx; text-align: center; }
  &__scroll { flex: 1; min-height: 0; }
  &__content { padding: 24rpx 0 32rpx; }
  &__cell-group { margin-bottom: 24rpx; background: #ffffff; }
  &__cell { min-height: 104rpx; padding: 0 32rpx; border-bottom: 1rpx solid #ededed; }
  &__save { border-radius: 14rpx; background: #242424; color: #ffffff; }
}
```

Do not use page-section radius, page-section shadow, gradient, serif/display font, or warm orange/brown action colors.

- [ ] **Step 6: Run the partial green checks**

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: type-check PASS; the static gate may now fail only at the bottom tag-sheet assertion until Task 3.

## Task 3: Add One Bottom Multi-Select Sheet For All Tag Fields

**Files:**
- Modify: `kaipai-frontend/src/pages/actor-profile/edit.vue`
- Test: outer static verification script

- [ ] **Step 1: Replace comma text inputs with tag rows**

Define one catalog and include existing imported/custom values in the active option list:

```ts
type TagKey = 'languageTags' | 'specialtyTags' | 'roleTypeTags' | 'professionalAbilityTags';

const tagFields: Array<{ key: TagKey; label: string }> = [
  { key: 'languageTags', label: '语言 / 方言' },
  { key: 'specialtyTags', label: '职业特长' },
  { key: 'roleTypeTags', label: '人物类型 / 戏路' },
  { key: 'professionalAbilityTags', label: '职业能力' },
];

const tagOptionCatalog: Record<TagKey, string[]> = {
  languageTags: ['普通话', '粤语', '英语', '东北话', '四川话', '其他方言'],
  specialtyTags: ['表演', '主持', '唱歌', '跳舞', '架子鼓', '球类', '跑步', '游泳'],
  roleTypeTags: ['悲情女主', '复仇大女主', '小白花', '绿茶', '正派', '反派'],
  professionalAbilityTags: ['同期声', '台词', '眼神戏', '情感戏', '爆发力', '动作戏', '威亚'],
};

const activeTagField = ref<TagKey | null>(null);
const activeTagOptions = computed(() => {
  const key = activeTagField.value;
  if (!key) return [];
  return [...new Set([...tagOptionCatalog[key], ...draft.career[key]])];
});

const activeTagTitle = computed(() => {
  const key = activeTagField.value;
  return tagFields.find((field) => field.key === key)?.label || '选择标签';
});

function tagSummary(key: TagKey): string {
  return draft.career[key].length ? draft.career[key].join('、') : '请选择';
}
```

Each tag cell opens the same sheet and displays selected values or “请选择”. Preserve values received from AI/import even when they are not part of the default catalog.

- [ ] **Step 2: Implement selection without a separate save request**

```ts
function openTagSheet(key: TagKey): void {
  activeTagField.value = key;
}

function toggleTag(value: string): void {
  const key = activeTagField.value;
  if (!key) return;
  const selected = draft.career[key];
  draft.career[key] = selected.includes(value)
    ? selected.filter((item) => item !== value)
    : [...selected, value];
}

function isTagSelected(value: string): boolean {
  const key = activeTagField.value;
  return key ? draft.career[key].includes(value) : false;
}

function closeTagSheet(): void {
  activeTagField.value = null;
}
```

The sheet never invokes an API. Its selections mutate only the shared page draft, so dirty-state tracking and the final `updateMyActorProfile(draft)` remain the single save path.

- [ ] **Step 3: Render the sheet as a proper bottom layer**

```vue
<view v-if="activeTagField" class="profile-edit__sheet-layer">
  <view class="profile-edit__sheet-mask" @click="closeTagSheet" />
  <view class="profile-edit__tag-sheet">
    <view class="profile-edit__sheet-head">
      <text class="profile-edit__sheet-title">{{ activeTagTitle }}</text>
      <view class="profile-edit__sheet-close" @click="closeTagSheet"><text>×</text></view>
    </view>
    <scroll-view scroll-y class="profile-edit__sheet-options">
      <view
        v-for="option in activeTagOptions"
        :key="option"
        class="profile-edit__sheet-option"
        :class="{ 'profile-edit__sheet-option--selected': isTagSelected(option) }"
        @click="toggleTag(option)"
      >
        <text>{{ option }}</text>
        <text v-if="isTagSelected(option)">✓</text>
      </view>
    </scroll-view>
    <view class="profile-edit__sheet-footer">
      <button class="profile-edit__sheet-done" @click="closeTagSheet">完成</button>
    </view>
  </view>
</view>
```

Use `border-radius: 28rpx 28rpx 0 0` and one light upward shadow only on `__tag-sheet`. Give the close command a stable square hit area, and keep option row dimensions fixed so selection does not shift layout.

- [ ] **Step 4: Correct dirty-leave copy and feedback**

Set the native action list to exactly:

```ts
itemList: ['保存资料并返回', '放弃修改', '继续编辑']
```

The first action awaits `saveProfile()` before navigating; the second clears dirty state and navigates; the third leaves the page and draft unchanged. Keep success Toast `资料已保存`, do not navigate after a normal footer save, and keep save-failure feedback as a Toast.

- [ ] **Step 5: Run the complete source gate**

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: both commands PASS. The editor contains one save API call, independent career/intro expansion, one tag sheet, and no legacy media/work writer.

- [ ] **Step 6: Commit the frontend implementation without unrelated files**

```powershell
git add src/pages/actor-profile/edit.vue
git commit -m "feat(miniapp): apply weui profile editor"
```

Before committing, `git diff --cached --name-only` must list only `src/pages/actor-profile/edit.vue`.

## Task 4: Build, Inspect Generated Output, And Verify Runtime UI

**Files:**
- Verify: source and generated paths listed above
- Update only if a real generated/runtime mismatch is found: `kaipai-frontend/src/pages/actor-profile/edit.vue`

- [ ] **Step 1: Run the mini-program engineering gate**

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check
npm run build:mp-weixin
npm run audit:steering
npm run audit:mp-package
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: every command exits `0`; postbuild sync updates `dist/dev/mp-weixin` from `dist/build/mp-weixin` while preserving the local API override.

- [ ] **Step 2: Prove the generated visual anchors exist in both outputs**

```powershell
rg -n "kp-floating-back-button|profile-edit__cell-group|profile-edit__tag-sheet|从复制内容智能填写" dist/build/mp-weixin/pages/actor-profile/edit.wxml dist/dev/mp-weixin/pages/actor-profile/edit.wxml
rg -n "#f5f5f5|#242424|border-radius: 28rpx 28rpx 0 0" dist/build/mp-weixin/pages/actor-profile/edit.wxss dist/dev/mp-weixin/pages/actor-profile/edit.wxss
```

Expected: all four visual anchors appear in both `dist/build` and `dist/dev`; neither generated WXSS contains the old profile-editor gradient.

- [ ] **Step 3: Verify the exact runtime states in WeChat DevTools**

Open only `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`. Capture and inspect:

1. Loaded first viewport: shared `‹ 返回` capsule, centered title, import cell first, core group, save footer.
2. Career and intro both expanded at the same time.
3. A tag bottom sheet with multi-selection, top-only radius, no text clipping, and no footer overlap.
4. `profileVersion=0` empty form without an “演员档案不存在” popup.
5. Save loading/success and dirty back action sheet.
6. A simulated real load failure with in-page “重新加载”.

Use iPhone SE and iPhone 15 Pro Max viewport presets. Confirm every row remains `48-56px` high, content does not pass under the footer, and the longest tag/label wraps or truncates without overlap.

- [ ] **Step 4: Commit any evidence-driven correction separately**

If runtime verification requires a correction, first extend the static gate so it fails for that mismatch, then edit only the direct visual anchor, rebuild, and commit:

```powershell
git add src/pages/actor-profile/edit.vue
git commit -m "fix(miniapp): align profile editor runtime"
```

If no correction is needed, do not create an empty commit.

## Final Verification Gate

```powershell
cd D:\XM\kaipai-team
git status --short
cd kaipai-frontend
git status --short
npm run type-check
npm run build:mp-weixin
npm run audit:steering
npm run audit:mp-package
node ..\.sce\specs\00-199-current-phase-miniapp-career-profile-hub-and-deepseek-import\scripts\verify-miniapp-career-profile-hub.mjs
```

Expected: the outer repository is clean after its plan/test commits. The frontend may still show only the user's pre-existing unrelated changes in `src/api/auth.ts`, `src/pages/login/index.vue`, `src/utils/runtime.ts`, and `pnpm-lock.yaml`; the profile editor implementation itself is committed and all verification commands pass.
