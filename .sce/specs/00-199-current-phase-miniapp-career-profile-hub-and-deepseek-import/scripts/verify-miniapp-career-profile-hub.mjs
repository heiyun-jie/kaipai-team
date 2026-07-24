import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const repositoryRoot = resolve(import.meta.dirname, '..', '..', '..', '..')

async function readText(path) {
  try {
    return await readFile(resolve(repositoryRoot, path), 'utf8')
  } catch (error) {
    throw new Error(`Cannot read ${path}: ${error.message}`)
  }
}

function assertMatch(source, pattern, label) {
  if (!pattern.test(source)) {
    throw new Error(`${label}: expected ${pattern} to match`)
  }
}

function assertNoMatch(source, pattern, label) {
  if (pattern.test(source)) {
    throw new Error(`${label}: forbidden pattern ${pattern} matched`)
  }
}

function assertEqual(actual, expected, label) {
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(`${label}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`)
  }
}

function extractSfcSections(source, label) {
  const templateStart = source.indexOf('<template')
  const scriptStart = source.indexOf('<script')
  if (templateStart < 0) throw new Error(`${label}: missing outer <template> block`)
  if (scriptStart < 0 || scriptStart <= templateStart) throw new Error(`${label}: missing <script> block after template`)

  const templateOpenEnd = source.indexOf('>', templateStart)
  const templateClose = source.lastIndexOf('</template>', scriptStart)
  if (templateOpenEnd < 0 || templateOpenEnd >= scriptStart || templateClose <= templateOpenEnd) {
    throw new Error(`${label}: invalid outer <template> boundaries`)
  }

  const scriptOpenEnd = source.indexOf('>', scriptStart)
  const scriptClose = source.indexOf('</script>', scriptOpenEnd + 1)
  if (scriptOpenEnd < 0 || scriptClose <= scriptOpenEnd) {
    throw new Error(`${label}: invalid <script> boundaries`)
  }

  const styleStart = source.indexOf('<style', scriptClose + '</script>'.length)
  if (styleStart < 0) throw new Error(`${label}: missing <style> block after script`)
  const styleOpenEnd = source.indexOf('>', styleStart)
  const styleClose = source.indexOf('</style>', styleOpenEnd + 1)
  if (styleOpenEnd < 0 || styleClose <= styleOpenEnd) {
    throw new Error(`${label}: invalid <style> boundaries`)
  }

  return {
    template: source.slice(templateOpenEnd + 1, templateClose),
    script: source.slice(scriptOpenEnd + 1, scriptClose),
    style: source.slice(styleOpenEnd + 1, styleClose),
  }
}

function extractFunctionBlock(source, signaturePattern, label) {
  const signatureMatch = signaturePattern.exec(source)
  if (!signatureMatch) {
    throw new Error(`${label}: expected function signature ${signaturePattern} to match`)
  }

  const openingBrace = source.indexOf('{', signatureMatch.index + signatureMatch[0].length)
  if (openingBrace < 0) throw new Error(`${label}: function has no body`)

  let depth = 1
  for (let index = openingBrace + 1; index < source.length; index += 1) {
    if (source[index] === '{') depth += 1
    if (source[index] === '}') depth -= 1
    if (depth === 0) return source.slice(openingBrace + 1, index)
  }

  throw new Error(`${label}: function body is unterminated`)
}

function assertStyleBlock(source, selectorPattern, propertyPattern, label) {
  const selectorMatch = selectorPattern.exec(source)
  if (!selectorMatch) {
    throw new Error(`${label}: expected selector ${selectorPattern} to match`)
  }

  const openingBrace = source.indexOf('{', selectorMatch.index + selectorMatch[0].length)
  if (openingBrace < 0) {
    throw new Error(`${label}: selector ${selectorPattern} has no declaration block`)
  }

  let depth = 1
  let declarations = ''
  for (let index = openingBrace + 1; index < source.length && depth > 0; index += 1) {
    const character = source[index]
    if (character === '{') {
      depth += 1
    } else if (character === '}') {
      depth -= 1
    } else if (depth === 1) {
      declarations += character
    }
  }

  if (depth !== 0) {
    throw new Error(`${label}: selector ${selectorPattern} has an unterminated declaration block`)
  }
  if (!propertyPattern.test(declarations)) {
    throw new Error(`${label}: expected ${propertyPattern} in selector ${selectorPattern}`)
  }
}

const pages = JSON.parse(await readText('kaipai-frontend/src/pages.json'))
const profilePackage = pages.subPackages?.find((item) => item.root === 'pkg-profile')
assertEqual(
  profilePackage?.pages?.map((item) => item.path),
  ['import-review/index', 'works/index', 'work-edit/index', 'assets/index'],
  'Profile subpackage routes',
)
const toolsPackage = pages.subPackages?.find((item) => item.root === 'pkg-tools')
assertMatch(JSON.stringify(toolsPackage), /settings\/index/, 'Settings route')

const importStore = await readText('kaipai-frontend/src/stores/profile-import.ts')
assertMatch(importStore, /setRawText[\s\S]*rawText\.value/, 'In-memory profile import source')
assertMatch(importStore, /function clear\(\)[\s\S]*rawText\.value = ''/, 'Profile import cleanup')
assertMatch(importStore, /markApplied[\s\S]*consumeApplied/, 'One-shot profile import applied signal')
const clearExtractionDraftBody = extractFunctionBlock(
  importStore,
  /function\s+clearExtractionDraft\s*\(\s*\)\s*:\s*void/,
  'clearExtractionDraft',
)
assertMatch(clearExtractionDraftBody, /extraction\.value\s*=\s*null/, 'Extraction-only draft cleanup')
assertNoMatch(
  clearExtractionDraftBody,
  /rawText|scene|profileVersion|workLibraryVersion/,
  'Extraction cleanup preserves source scene and versions',
)
assertMatch(
  importStore,
  /function setExtraction[\s\S]*profileVersion\.value\s*=\s*value\.profileVersion[\s\S]*workLibraryVersion\.value\s*=\s*value\.workLibraryVersion/,
  'Extraction server context snapshot',
)
assertNoMatch(importStore, /uni\.setStorage|localStorage|persist/, 'No persisted profile import source')

const importTypes = await readText('kaipai-frontend/src/types/profile-import.ts')
const importCapabilityBody = extractFunctionBlock(
  importTypes,
  /export\s+interface\s+ProfileImportCapability/,
  'ProfileImportCapability',
)
for (const field of [
  'enabled',
  'available',
  'providerCode',
  'modelName',
  'maxInputLength',
  'unavailableReason',
]) {
  assertMatch(importCapabilityBody, new RegExp(`\\b${field}:`), `Required capability field ${field}`)
}
assertNoMatch(importCapabilityBody, /\breason\??:/, 'No legacy capability reason field')
for (const field of [
  'profileVersion',
  'workLibraryVersion',
  'confidence',
  'sourceText',
  'warning',
  'reviewStatus',
  'conflict',
  'matchStatus',
  'selectedAction',
  'matchedExperienceId',
  'allowedActions',
  'conflictFields',
  'fields',
  'conflicts',
  'confirmedConflictFields',
  'candidateValue',
]) {
  assertMatch(importTypes, new RegExp(`\\b${field}\\??:`), `Profile import contract field ${field}`)
}

const importPayloadBuilder = await readText('kaipai-frontend/src/utils/profile-import-payload.ts')
assertMatch(importPayloadBuilder, /buildProfileImportApplyRequest/, 'Pure profile import apply builder')
assertMatch(
  importPayloadBuilder,
  /candidateValue:\s*candidate\.candidateValue[\s\S]*value:\s*profileFinalValues\[candidate\.candidateId\]/,
  'Signed profile candidate value and independent final value',
)
for (const field of [
  'matchStatus',
  'selectedAction',
  'matchedExperienceId',
  'allowedActions',
  'conflictFields',
  'confirmedConflictFields',
  'projectName',
  'roleName',
  'publishStatus',
  'workTypeCode',
  'roleLevelCode',
  'shootYear',
  'shootMonth',
  'platform',
  'syncSoundStatus',
  'collaborators',
  'achievementText',
  'description',
]) {
  assertMatch(importPayloadBuilder, new RegExp(`\\b${field}:`), `Profile import apply work field ${field}`)
}
assertMatch(
  importPayloadBuilder,
  /selectedAction\s*===\s*'merge'[\s\S]*finalFields/,
  'Merge-only final work fields',
)
assertMatch(
  importPayloadBuilder,
  /scene\s*===\s*'works_only'\s*\?\s*\[\]/,
  'Works-only apply strips profile candidates',
)

const navigationStore = await readText('kaipai-frontend/src/stores/record-navigation.ts')
assertMatch(navigationStore, /openFavorites[\s\S]*'favorites'/, 'Favorites navigation intent')
assertMatch(navigationStore, /consumeSegment[\s\S]*\.value = null/, 'One-shot navigation intent')

const request = await readText('kaipai-frontend/src/utils/request.ts')
assertMatch(request, /class ApiError extends Error/, 'Structured API error class')
assertMatch(
  request,
  /new ApiError\(response\.message \|\| '请求失败', response\.code, response\.errorCode\)/,
  'Structured API error construction',
)

const profileImportApi = await readText('kaipai-frontend/src/api/profile-import.ts')
for (const [signature, requestPattern, label] of [
  [
    /export\s+function\s+getProfileImportCapability\s*\(\s*\)\s*:\s*Promise<ProfileImportCapability>/,
    /get\(\s*'\/api\/ai\/profile-import\/capability'\s*,\s*undefined\s*,\s*\{\s*showError:\s*false\s*\}\s*\)/,
    'Capability request',
  ],
  [
    /export\s+function\s+extractProfileImport\s*\([^)]*\)\s*:\s*Promise<ProfileImportExtraction>/,
    /post\(\s*'\/api\/ai\/profile-import\/extract'\s*,[\s\S]*?\{\s*showError:\s*false\s*\}\s*,?\s*\)/,
    'Extract request',
  ],
  [
    /export\s+function\s+applyProfileImport\s*\([^)]*\)\s*:\s*Promise<ProfileImportApplyResult>/,
    /post\(\s*'\/api\/actor\/profile-import\/apply'\s*,[\s\S]*?\{\s*showError:\s*false\s*\}\s*,?\s*\)/,
    'Apply request',
  ],
]) {
  const body = extractFunctionBlock(profileImportApi, signature, label)
  assertMatch(
    body,
    requestPattern,
    `${label} delegates error feedback to the page`,
  )
}

const mpSync = await readText('kaipai-frontend/scripts/sync-mp-weixin.ps1')
assertMatch(mpSync, /Apply-LocalDevProjectConfig/, 'Local MiniProgram project config sync')
assertMatch(mpSync, /\.env\.local[\s\S]*VITE_API_BASE_URL/, 'Local API override detection')
assertMatch(mpSync, /urlCheck\s*=\s*\$false/, 'Local URL validation override')

const actorApi = await readText('kaipai-frontend/src/api/actor.ts')
const profileTypes = await readText('kaipai-frontend/src/types/profile.ts')
const actorProfileRespBody = extractFunctionBlock(
  profileTypes,
  /export\s+interface\s+ActorProfileResp/,
  'ActorProfileResp',
)
for (const [field, type] of [
  ['actorProfileId', 'number'],
  ['publicName', 'string'],
  ['gender', 'ActorGender'],
  ['age', 'number'],
  ['height', 'number'],
  ['currentCity', 'string'],
  ['originPlace', 'string'],
  ['schoolName', 'string'],
  ['majorName', 'string'],
  ['intro', 'string'],
]) {
  assertMatch(
    actorProfileRespBody,
    new RegExp(`\\b${field}: ${type} \\| null;`),
    `ActorProfileResp ${field} empty-draft nullability`,
  )
}
for (const [field, typePattern] of [
  ['userId', 'number'],
  ['profileVersion', 'number'],
  ['workLibraryVersion', 'number'],
  ['languageTags', 'string\\[\\]'],
  ['specialtyTags', 'string\\[\\]'],
  ['roleTypeTags', 'string\\[\\]'],
  ['professionalAbilityTags', 'string\\[\\]'],
]) {
  assertMatch(
    actorProfileRespBody,
    new RegExp(`\\b${field}: ${typePattern};`),
    `ActorProfileResp ${field} remains required`,
  )
}
const getMyActorProfileBody = extractFunctionBlock(
  actorApi,
  /export\s+function\s+getMyActorProfile\s*\([^)]*\)\s*:\s*Promise<ActorProfile>/,
  'getMyActorProfile',
)
const getMyCareerProfileBody = extractFunctionBlock(
  actorApi,
  /export\s+function\s+getMyCareerProfile\s*\([^)]*\)\s*:\s*Promise<ActorProfileResp>/,
  'getMyCareerProfile',
)
assertMatch(
  getMyActorProfileBody,
  /get<ActorProfile>\('\/api\/actor\/profile\/mine\/legacy'/,
  'Legacy aggregate profile API route',
)
assertMatch(
  getMyCareerProfileBody,
  /get<ActorProfileResp>\('\/api\/actor\/profile\/mine'/,
  'Versioned career profile API route',
)
assertNoMatch(getMyCareerProfileBody, /\/mine\/career/, 'Deprecated career profile alias is not consumed')

const mine = await readText('kaipai-frontend/src/pages/mine/index.vue')
assertMatch(mine, /个人档案[\s\S]*作品库[\s\S]*素材库/, 'Mine profile hierarchy')
assertMatch(mine, /创建分享[\s\S]*联系申请[\s\S]*设置/, 'Mine common actions')
assertMatch(mine, /<KpMineIcon\s+:name="item\.icon"/, 'Mine entry icon component')
assertNoMatch(mine, /<text>\{\{\s*item\.icon\s*\}\}<\/text>/, 'No Mine text icon placeholders')
assertNoMatch(mine, /analytics|trendHeights|openMyQrCode|我的二维码/, 'Mine career hub')
assertNoMatch(mine, /我的数据|近 30 天|getMyShareCards\(|getShareCardHistory\(/, 'No pseudo Mine analytics')
assertMatch(
  mine,
  /linear-gradient\(180deg,\s*#f5f3ee 0%,\s*#f1ede6 100%\)/,
  'Mine warm neutral page background',
)
assertMatch(mine, /\$kp-font-family-display/, 'Mine display typography')
assertMatch(mine, /#8c6f4f|#a58c67/, 'Mine brand brown palette')
assertNoMatch(mine, /#202724|#245f4b|#e6f1ec|#eef0f8/, 'No foreign green Mine palette')
assertMatch(
  mine,
  /async function hydrateMinePage\(\)[\s\S]*if \(isVisitor\.value\)[\s\S]*getCareerHubSummary\(\)/,
  'Visitor-safe career hub hydration',
)

const mineIcon = await readText('kaipai-frontend/src/components/KpMineIcon.vue')
for (const name of ['profile', 'works', 'assets', 'share', 'contacts', 'settings']) {
  assertMatch(mineIcon, new RegExp(`'${name}'`), `Mine ${name} icon type`)
  const iconAsset = await readText(`kaipai-frontend/src/static/mine-icons/${name}.svg`)
  assertMatch(iconAsset, /<svg[\s\S]*stroke="#8c6f4f"/, `Mine ${name} icon asset`)
}

for (const path of [
  'kaipai-frontend/src/pages/history/index.vue',
  'kaipai-frontend/src/pkg-card/favorites/index.vue',
  'kaipai-frontend/src/pkg-profile/assets/index.vue',
  'kaipai-frontend/src/pkg-profile/import-review/index.vue',
  'kaipai-frontend/src/pkg-profile/work-edit/index.vue',
  'kaipai-frontend/src/pkg-profile/works/index.vue',
  'kaipai-frontend/src/pkg-tools/settings/index.vue',
]) {
  const page = await readText(path)
  assertMatch(page, /\$kp-color-bg|#f5f3ee/, `${path} warm page background`)
  assertMatch(page, /\$kp-color-primary|#8c6f4f/, `${path} brand brown accent`)
  assertMatch(page, /\$kp-font-family-display/, `${path} display typography`)
  assertNoMatch(
    page,
    /#f3f5f4|#202421|#245f4b|#dfe4e1|#edf0ee|#eef0f8|#44547d/,
    `${path} foreign green-gray palette`,
  )
}

const history = await readText('kaipai-frontend/src/pages/history/index.vue')
assertMatch(history, /'history'[\s\S]*'favorites'/, 'Record segments')
assertMatch(history, /getShareCardHistory[\s\S]*listShareCardFavorites/, 'Independent record sources')
const historySections = extractSfcSections(history, 'Record page SFC')
const hydrateActiveSegmentBody = extractFunctionBlock(
  historySections.script,
  /async\s+function\s+hydrateActiveSegment\s*\(\s*\)\s*:\s*Promise<void>/,
  'hydrateActiveSegment',
)
assertMatch(historySections.script, /let\s+recordRequestRevision\s*=\s*0/, 'Record request revision')
assertMatch(
  historySections.script,
  /function\s+isCurrentRecordRequest\s*\(\s*revision:\s*number,\s*segment:\s*RecordSegment\s*\)\s*:\s*boolean[\s\S]*revision\s*===\s*recordRequestRevision[\s\S]*activeSegment\.value\s*===\s*segment/,
  'Record request currentness helper',
)
assertMatch(
  hydrateActiveSegmentBody,
  /const\s+requestedSegment\s*=\s*activeSegment\.value[\s\S]*const\s+requestRevision\s*=\s*\+\+recordRequestRevision/,
  'Record request captures segment and revision',
)
assertMatch(
  hydrateActiveSegmentBody,
  /if\s*\(\s*!userStore\.hasStoredSession\s*\)\s*\{[\s\S]*loading\.value\s*=\s*false[\s\S]*return/,
  'Visitor hydration settles superseded loading state',
)
assertMatch(
  hydrateActiveSegmentBody,
  /await\s+userStore\.bootstrapSession\(\)[\s\S]*if\s*\(\s*!isCurrentRecordRequest\(requestRevision,\s*requestedSegment\)\s*\)\s*return[\s\S]*if\s*\(\s*requestedSegment\s*===\s*'history'\s*\)/,
  'Record endpoint selection uses the captured segment',
)
assertMatch(
  hydrateActiveSegmentBody,
  /const\s+nextHistoryItems\s*=\s*await\s+getShareCardHistory\(\)[\s\S]*if\s*\(\s*!isCurrentRecordRequest\(requestRevision,\s*requestedSegment\)\s*\)\s*return[\s\S]*historyItems\.value\s*=\s*nextHistoryItems/,
  'Stale history response cannot replace current data',
)
assertMatch(
  hydrateActiveSegmentBody,
  /const\s+nextFavoritePage\s*=\s*await\s+listShareCardFavorites\(1,\s*50\)[\s\S]*if\s*\(\s*!isCurrentRecordRequest\(requestRevision,\s*requestedSegment\)\s*\)\s*return[\s\S]*favoriteItems\.value\s*=\s*nextFavoritePage\.list/,
  'Stale favorite response cannot replace current data',
)
assertMatch(
  hydrateActiveSegmentBody,
  /catch\s*\(error\)\s*\{\s*if\s*\(\s*isCurrentRecordRequest\(requestRevision,\s*requestedSegment\)\s*\)\s*\{[\s\S]*loadError\.value\s*=/,
  'Stale record request cannot replace current error',
)
assertMatch(
  hydrateActiveSegmentBody,
  /finally\s*\{\s*if\s*\(\s*isCurrentRecordRequest\(requestRevision,\s*requestedSegment\)\s*\)\s*\{[\s\S]*loading\.value\s*=\s*false/,
  'Stale record request cannot clear current loading state',
)

const favorites = await readText('kaipai-frontend/src/pkg-card/favorites/index.vue')
assertMatch(favorites, /useRecordNavigationStore[\s\S]*switchTab\(\{ url: '\/pages\/history\/index' \}\)/, 'Favorite route compatibility')
assertNoMatch(favorites, /ref\(\[\]\)/, 'No fake favorite list')

const settings = await readText('kaipai-frontend/src/pkg-tools/settings/index.vue')
assertMatch(settings, /消息通知[\s\S]*偏好设置[\s\S]*用户协议[\s\S]*隐私政策[\s\S]*关于/, 'Settings hierarchy')

const edit = await readText('kaipai-frontend/src/pages/actor-profile/edit.vue')
const { template: editTemplate, script: editScript, style: editStyle } = extractSfcSections(edit, 'Profile editor SFC')
const hydrateDraftBody = extractFunctionBlock(
  editScript,
  /function\s+hydrateDraft\s*\(\s*profile:\s*ActorProfileResp\s*\)\s*:\s*void/,
  'hydrateDraft',
)
const loadProfileBody = extractFunctionBlock(
  editScript,
  /async\s+function\s+loadProfile\s*\(\s*\)\s*:\s*Promise<void>/,
  'loadProfile',
)
const openImportReviewBody = extractFunctionBlock(
  editScript,
  /function\s+openImportReview\s*\(\s*\)\s*:\s*void/,
  'openImportReview',
)
const activeTagOptionsBody = extractFunctionBlock(
  editScript,
  /const\s+activeTagOptions\s*=\s*computed(?:\s*<[^>]+>)?\s*\(\s*\(\)\s*=>/,
  'activeTagOptions',
)
const openTagSheetBody = extractFunctionBlock(
  editScript,
  /function\s+openTagSheet\s*\(\s*key:\s*TagKey\s*\)\s*:\s*void/,
  'openTagSheet',
)
const onShowBody = extractFunctionBlock(
  editScript,
  /onShow\(\s*\(\)\s*=>/,
  'profile editor onShow',
)

assertMatch(
  editTemplate,
  /<KpFloatingBackButton\b(?=[^>]*@click="requestLeave")[^>]*>/,
  'Shared floating back button',
)
assertNoMatch(edit, /KpCapsuleSpacer|profile-edit__back|<text>‹<\/text>/, 'No private profile back control')
assertMatch(editTemplate, /从复制内容智能填写[\s\S]*核心资料/, 'Import entry precedes core profile')
assertMatch(
  editTemplate,
  /<view\b(?=[^>]*class="profile-edit__cell profile-edit__cell--action")(?=[^>]*@click="openImportReview")[^>]*>/,
  'Import cell action',
)
assertMatch(editTemplate, /class="profile-edit__cell-group"/, 'WeUI cell groups')
assertMatch(editTemplate, /v-if="careerExpanded"/, 'Inline career editor')
assertMatch(editTemplate, /v-if="introExpanded"/, 'Inline intro editor')
assertMatch(editScript, /const\s+careerExpanded\s*=\s*ref\(false\)/, 'Independent career expansion state')
assertMatch(editScript, /const\s+introExpanded\s*=\s*ref\(false\)/, 'Independent intro expansion state')
assertMatch(
  editTemplate,
  /<button\b(?=[^>]*class="profile-edit__save")(?=[^>]*:disabled="saving \|\| loading \|\| !!loadError")[^>]*>/,
  'Profile save disabled after load failure',
)
assertStyleBlock(
  editStyle,
  /&__nav\s*(?=\{)/,
  /border-bottom:\s*1rpx\s+solid\s+#ededed\s*;/i,
  'Profile nav divider',
)
assertStyleBlock(editStyle, /&__nav-title\s*(?=\{)/, /height:\s*64rpx\s*;/, 'Profile nav capsule alignment')
assertMatch(editTemplate, /v-if="activeTagField"/, 'Tag sheet visibility state')
assertMatch(editTemplate, /class="profile-edit__tag-sheet"/, 'Bottom multi-select tag sheet')
assertMatch(editScript, /const\s+activeTagField\s*=\s*ref<TagKey\s*\|\s*null>\(null\)/, 'Shared tag field state')
assertMatch(
  editTemplate,
  /<view\b(?=[^>]*class="profile-edit__tag-row")(?=[^>]*aria-role="button")(?=[^>]*:aria-label="(?=[^"]*field\.label)(?=[^"]*tagSummary\s*\(\s*field\.key\s*\))[^"]*")[^>]*>/,
  'Accessible tag field action',
)
assertMatch(
  editTemplate,
  /<view\b(?=[^>]*class="profile-edit__tag-sheet-close")(?=[^>]*aria-role="button")(?=[^>]*aria-label="关闭标签选择")[^>]*>/,
  'Accessible tag sheet close',
)
assertMatch(
  editTemplate,
  /<view\b(?=[^>]*class="profile-edit__tag-option")(?=[^>]*aria-role="checkbox")(?=[^>]*:aria-label="option")(?=[^>]*:aria-checked="isTagSelected\(option\)")[^>]*>/,
  'Accessible tag option state',
)
assertStyleBlock(
  editStyle,
  /&__tag-sheet-close\s*(?=\{)/,
  /(?:^|[;\s])width:\s*88rpx\s*;/,
  'Tag sheet close width',
)
assertStyleBlock(
  editStyle,
  /&__tag-sheet-close\s*(?=\{)/,
  /(?:^|[;\s])height:\s*88rpx\s*;/,
  'Tag sheet close height',
)
assertMatch(
  editScript,
  /const\s+tagOptionMemory\s*=\s*reactive\s*<\s*Record\s*<\s*TagKey\s*,\s*string\[\]\s*>\s*>\s*\(/,
  'Tag option memory',
)
assertMatch(activeTagOptionsBody, /return\s+tagOptionMemory\s*\[\s*key\s*\]/, 'Tag options use session memory')
assertEqual(
  [hydrateDraftBody, openTagSheetBody].some(
    (body) =>
      /tagOptionMemory\s*\[[^\]]+\]\s*=/.test(body) &&
      /new Set\s*\(/.test(body) &&
      /tagOptionCatalog\s*\[[^\]]+\]/.test(body) &&
      /(?:profile(?:\.[A-Za-z]+|\s*\[[^\]]+\])|draft\.career(?:\.[A-Za-z]+|\s*\[[^\]]+\]))/.test(body),
  ),
  true,
  'Tag option memory union',
)
assertNoMatch(
  activeTagOptionsBody,
  /\[\s*\.\.\.tagOptionCatalog\s*\[\s*key\s*\]\s*,\s*\.\.\.draft\.career\s*\[\s*key\s*\]\s*\]/,
  'No draft-only tag option source',
)
assertMatch(
  editScript,
  /onBackPress\(\s*\(\)\s*=>\s*\{\s*if\s*\(\s*activeTagField\.value\s*\)\s*\{\s*closeTagSheet\(\)\s*;?\s*return\s+true\s*;?\s*\}\s*if\s*\(\s*!isDirty\.value\s*\)/,
  'Back closes tag sheet first',
)
assertStyleBlock(
  editStyle,
  /&__tag-option\s*(?=\{)/,
  /(?:^|[;\s])height:\s*96rpx\s*;/,
  'Fixed tag option height',
)
assertStyleBlock(editStyle, /&__tag-option-label\s*(?=\{)/, /flex:\s*1\s*;/, 'Flexible tag option label')
assertStyleBlock(editStyle, /&__tag-option-label\s*(?=\{)/, /min-width:\s*0\s*;/, 'Tag option label min width')
assertStyleBlock(editStyle, /&__tag-option-label\s*(?=\{)/, /overflow:\s*hidden\s*;/, 'Tag option label clipping')
assertStyleBlock(
  editStyle,
  /&__tag-option-label\s*(?=\{)/,
  /text-overflow:\s*ellipsis\s*;/,
  'Tag option label ellipsis',
)
assertStyleBlock(editStyle, /&__tag-option-label\s*(?=\{)/, /white-space:\s*nowrap\s*;/, 'Tag option label single line')
assertMatch(hydrateDraftBody, /workLibraryVersion\.value\s*=\s*profile\.workLibraryVersion/, 'Hydrated work library version')
assertMatch(
  openImportReviewBody,
  /setContext\(\s*scene\s*,\s*draft\.expectedProfileVersion\s*,\s*workLibraryVersion\.value\s*\)/,
  'Real import context version',
)
assertMatch(
  onShowBody,
  /consumeApplied\(\)[\s\S]*loadProfile\(\)/,
  'Profile editor reloads after applied import',
)
assertMatch(
  loadProfileBody,
  /getMyCareerProfile\(\{\s*showLoading:\s*false,\s*showError:\s*false\s*\}\)/,
  'Page-owned load error feedback',
)
assertMatch(loadProfileBody, /\btry\s*\{/, 'Profile load try block')
assertMatch(
  loadProfileBody,
  /catch\s*\([^)]*\)\s*\{[\s\S]*?loadError\.value\s*=/,
  'Captured profile load error',
)
assertMatch(loadProfileBody, /hydrateDraft\s*\(/, 'Profile hydration after load')
assertMatch(editTemplate, /v-else-if="loadError"[\s\S]*档案读取失败/, 'Explicit profile load error state')
assertMatch(
  editTemplate,
  /<button\b(?=[^>]*@click="loadProfile")[^>]*>[\s\S]*?重新加载[\s\S]*?<\/button>/,
  'Profile load retry action',
)
assertEqual((editTemplate.match(/@click="saveProfile"/g) || []).length, 1, 'Single profile save action')
assertEqual((editScript.match(/updateMyActorProfile\(/g) || []).length, 1, 'Single profile save request')
assertMatch(
  editScript,
  /itemList:\s*\[\s*'保存资料并返回'\s*,\s*'放弃修改'\s*,\s*'继续编辑'\s*\]/,
  'Dirty leave action sheet',
)
assertStyleBlock(editStyle, /\.profile-edit\s*(?=\{)/, /background:\s*#f5f5f5\s*;/i, 'Neutral profile page background')
assertStyleBlock(editStyle, /&__save\s*(?=\{)/, /background:\s*#242424\s*;/i, 'Neutral profile primary action')
assertStyleBlock(
  editStyle,
  /&__tag-sheet\s*(?=\{)/,
  /border-radius:\s*28rpx\s+28rpx\s+0\s+0\s*;/,
  'Tag sheet top radius',
)
assertNoMatch(
  editStyle,
  /linear-gradient|\$kp-font-family-display|\$kp-shadow-card|\$kp-radius-card/,
  'No warm card visual language in profile editor',
)
assertNoMatch(editTemplate, /多个内容用逗号分隔/, 'No comma-entry tag editor')
assertMatch(editScript, /chooseAvatarFromAssets/, 'Avatar asset selection')
assertNoMatch(editTemplate, /完成度|提升建议|AI 全量润色/, 'No profile operation cards')
assertNoMatch(
  edit,
  /updateActorProfile\(|buildPayload\(|workExperiences|photoCategories|videoUrl|resumePdf|PhotoCategorySection|WorkExperienceSection|PdfResumeSection|VideoResumeSection/,
  'Simplified actor profile editor',
)

const importPage = await readText('kaipai-frontend/src/pkg-profile/import-review/index.vue')
const importPageSections = extractSfcSections(importPage, 'Profile import review')
const invalidateExtractionDraftBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+invalidateExtractionDraft\s*\(\s*\)\s*:\s*void/,
  'invalidateExtractionDraft',
)
assertMatch(
  invalidateExtractionDraftBody,
  /importStore\.clearExtractionDraft\(\)/,
  'Page invalidation clears store extraction',
)
assertMatch(
  invalidateExtractionDraftBody,
  /extractionDraftRevision\.value\s*\+=\s*1/,
  'Page invalidation advances extraction revision',
)
for (const state of [
  'profileFinalValues',
  'profileConflictChoices',
  'workFinalFields',
  'workConflictChoices',
]) {
  assertMatch(
    invalidateExtractionDraftBody,
    new RegExp(`${state}\\.value\\s*=\\s*\\{\\}`),
    `Page invalidation clears ${state}`,
  )
}
const submitExtractionBody = extractFunctionBlock(
  importPageSections.script,
  /async\s+function\s+submitExtraction\s*\(\s*\)\s*:\s*Promise<void>/,
  'submitExtraction',
)
const beginClipboardReadBody = extractFunctionBlock(
  importPageSections.script,
  /async\s+function\s+beginClipboardRead\s*\(\s*\)\s*:\s*Promise<void>/,
  'beginClipboardRead',
)
const applyReviewBody = extractFunctionBlock(
  importPageSections.script,
  /async\s+function\s+applyReview\s*\(\s*\)\s*:\s*Promise<void>/,
  'applyReview',
)
const goBackBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+goBack\s*\(\s*\)\s*:\s*void/,
  'goBack',
)
assertMatch(
  importPageSections.script,
  /set:\s*\(value:\s*string\)\s*=>\s*\{[\s\S]*?invalidateExtractionDraft\(\)[\s\S]*?importStore\.setRawText\(value\)/,
  'Editing source invalidates prior extraction',
)
assertMatch(
  beginClipboardReadBody,
  /rawText\.value\s*=\s*String\(result\.data\s*\|\|\s*''\)\.trim\(\)/,
  'Clipboard replacement uses invalidating source setter',
)
assertMatch(
  beginClipboardReadBody,
  /invalidateExtractionDraft\(\)[\s\S]*const\s+requestRevision\s*=\s*extractionDraftRevision\.value[\s\S]*await\s+uni\.getClipboardData\(\)/,
  'Clipboard read invalidates prior review immediately',
)
assertMatch(
  beginClipboardReadBody,
  /await\s+uni\.getClipboardData\(\)[\s\S]*if\s*\([^)]*!pageActive\.value[^)]*requestRevision\s*!==\s*extractionDraftRevision\.value[^)]*\)\s*return[\s\S]*rawText\.value\s*=/,
  'Clipboard result cannot repopulate source after unload or source revision change',
)
assertMatch(
  beginClipboardReadBody,
  /finally\s*\{\s*if\s*\(\s*pageActive\.value\s*\)\s*readingClipboard\.value\s*=\s*false/,
  'Clipboard finally cannot mutate a destroyed page',
)
assertMatch(
  submitExtractionBody,
  /invalidateExtractionDraft\(\)[\s\S]*await\s+extractProfileImport\(/,
  'New extraction invalidates prior review before request',
)
assertMatch(
  submitExtractionBody,
  /const\s+requestRevision\s*=\s*extractionDraftRevision\.value[\s\S]*await\s+extractProfileImport\([\s\S]*if\s*\(requestRevision\s*!==\s*extractionDraftRevision\.value\)\s*return[\s\S]*importStore\.setExtraction\(result\)/,
  'Edited source cannot accept stale in-flight extraction',
)
assertMatch(importPageSections.script, /const\s+pageActive\s*=\s*ref\(true\)/, 'Explicit page-active state')
assertMatch(importPageSections.script, /const\s+applyRevision\s*=\s*ref\(0\)/, 'Apply request revision')
const isCurrentApplyBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+isCurrentApply\s*\(\s*requestRevision:\s*number\s*\)\s*:\s*boolean/,
  'isCurrentApply',
)
assertMatch(isCurrentApplyBody, /pageActive\.value/, 'Current apply requires an active page')
assertMatch(
  isCurrentApplyBody,
  /requestRevision\s*===\s*applyRevision\.value/,
  'Current apply requires the latest request revision',
)
assertMatch(
  applyReviewBody,
  /const\s+requestRevision\s*=\s*\+\+applyRevision\.value[\s\S]*await\s+applyProfileImport\(payload\)[\s\S]*importStore\.markApplied\(\)[\s\S]*if\s*\(\s*!isCurrentApply\(requestRevision\)\s*\)\s*return[\s\S]*importStore\.clear\(\)/,
  'Late apply success preserves the parent refresh signal without clearing a future page',
)
assertNoMatch(
  applyReviewBody.slice(
    applyReviewBody.indexOf('if (!isCurrentApply(requestRevision)) return'),
    applyReviewBody.indexOf('importStore.clear()'),
  ),
  /uni\.showToast|uni\.navigateBack/,
  'Apply page UI remains behind the active-page gate',
)
const applyReviewCatchBody = extractFunctionBlock(
  applyReviewBody,
  /catch\s*\([^)]*\)/,
  'applyReview catch',
)
assertMatch(
  applyReviewCatchBody,
  /if\s*\(\s*!isCurrentApply\(requestRevision\)\s*\)\s*return/,
  'Inactive apply failure is ignored',
)
assertMatch(
  applyReviewCatchBody,
  /extractionError\.value\s*=\s*mapProfileImportError\([^)]*\)/,
  'Active apply failure uses one code-mapped feedback message',
)
assertEqual(
  (applyReviewCatchBody.match(/uni\.showToast\(/g) || []).length,
  0,
  'Apply failure has no duplicate Toast',
)
assertNoMatch(
  applyReviewCatchBody,
  /importStore\.clear|invalidateExtractionDraft|clearExtractionDraft/,
  'Apply failure preserves candidates',
)
assertMatch(
  applyReviewBody,
  /setTimeout\s*\(\s*\(\)\s*=>\s*\{[\s\S]*?if\s*\(\s*!isCurrentApply\(requestRevision\)\s*\)\s*return[\s\S]*?uni\.navigateBack\(\)/,
  'Delayed apply navigation is page/revision guarded',
)
for (const [signature, label] of [
  [/async\s+function\s+beginClipboardRead\s*\(\s*\)\s*:\s*Promise<void>/, 'Clipboard read'],
  [/async\s+function\s+submitExtraction\s*\(\s*\)\s*:\s*Promise<void>/, 'Extraction'],
  [/function\s+toggleProfileCandidate\s*\([^)]*\)\s*:\s*void/, 'Profile selection'],
  [/function\s+confirmInferredCandidate\s*\([^)]*\)\s*:\s*void/, 'Inferred confirmation'],
  [/function\s+selectProfileConflictValue\s*\([^)]*\)\s*:\s*void/, 'Profile conflict selection'],
  [/function\s+toggleWorkCandidate\s*\([^)]*\)\s*:\s*void/, 'Work selection'],
  [/function\s+selectWorkConflictValue\s*\([^)]*\)\s*:\s*void/, 'Work conflict selection'],
]) {
  const body = extractFunctionBlock(importPageSections.script, signature, label)
  assertMatch(body, /if\s*\([^)]*applying\.value[^)]*\)\s*return/, `${label} is locked during apply`)
}
assertMatch(goBackBody, /if\s*\(\s*applying\.value\s*\)\s*return/, 'Back action is locked during apply')
assertMatch(
  importPageSections.script,
  /onBackPress\(\s*\(\)\s*=>\s*\{\s*if\s*\(\s*!applying\.value\s*\)\s*return\s+false\s*;?\s*return\s+true/,
  'System back is locked during apply',
)
assertMatch(
  importPageSections.script,
  /set:\s*\(value:\s*string\)\s*=>\s*\{\s*if\s*\(\s*applying\.value\s*\)\s*return/,
  'Source editing is locked during apply',
)
assertMatch(
  importPageSections.template,
  /<textarea\b(?=[^>]*:disabled="applying")[^>]*>/,
  'Source textarea exposes apply lock state',
)
assertMatch(importPage, /beginClipboardRead[\s\S]*uni\.getClipboardData/, 'Explicit clipboard read')
assertNoMatch(importPage, /onLoad\([^)]*=>[\s\S]{0,300}getClipboardData/, 'No automatic clipboard read')
assertMatch(importPage, /async function submitExtraction\(\)[\s\S]*extractProfileImport/, 'Explicit extraction action')
assertMatch(importPage, /requiresExplicitConfirmation[\s\S]*confirmed/, 'Explicit inferred candidate confirmation')
assertMatch(importPage, /个人资料[\s\S]*作品[\s\S]*需要确认[\s\S]*疑似重复[\s\S]*未映射内容/, 'Import review groups')
const profileGroupStart = importPageSections.template.indexOf('>个人资料</text>')
const workGroupStart = importPageSections.template.indexOf('>作品</text>', profileGroupStart + 1)
const confirmationGroupStart = importPageSections.template.indexOf('>需要确认</text>', workGroupStart + 1)
const duplicateGroupStart = importPageSections.template.indexOf('>疑似重复</text>', confirmationGroupStart + 1)
const unmappedGroupStart = importPageSections.template.indexOf('>未映射内容</text>', duplicateGroupStart + 1)
assertEqual(
  [profileGroupStart, workGroupStart, confirmationGroupStart, duplicateGroupStart, unmappedGroupStart]
    .every((value, index, values) => value >= 0 && (index === 0 || value > values[index - 1])),
  true,
  'Ordered import review section boundaries',
)
const profileGroupTemplate = importPageSections.template.slice(profileGroupStart, workGroupStart)
const workGroupTemplate = importPageSections.template.slice(workGroupStart, confirmationGroupStart)
const confirmationGroupTemplate = importPageSections.template.slice(confirmationGroupStart, duplicateGroupStart)
const duplicateGroupTemplate = importPageSections.template.slice(duplicateGroupStart, unmappedGroupStart)
const unmappedGroupTemplate = importPageSections.template.slice(unmappedGroupStart)
assertMatch(
  importPageSections.script,
  /REVIEW_PROFILE_STATUSES[\s\S]*'conflict'[\s\S]*'low_confidence'[\s\S]*'derived'[\s\S]*'unreadable'/,
  'Review-required profile statuses',
)
assertMatch(
  importPageSections.script,
  /requiresProfileReview[\s\S]*candidate\.conflict/,
  'Profile conflicts always enter the confirmation group',
)
assertMatch(importPageSections.script, /regularProfileCandidates[\s\S]*!requiresProfileReview/, 'Regular profile grouping')
assertMatch(importPageSections.script, /reviewProfileCandidates[\s\S]*requiresProfileReview/, 'Review profile grouping')
assertMatch(importPageSections.script, /newWorkCandidates[\s\S]*matchStatus\s*===\s*'new'/, 'New work grouping')
assertMatch(importPageSections.script, /duplicateWorkCandidates[\s\S]*matchStatus\s*!==\s*'new'/, 'Duplicate work grouping')
assertMatch(profileGroupTemplate, /v-for="candidate in regularProfileCandidates"/, 'Personal profile group data source')
assertMatch(workGroupTemplate, /v-for="work in newWorkCandidates"/, 'New work group data source')
assertMatch(
  confirmationGroupTemplate,
  /v-for="candidate in reviewProfileCandidates"/,
  'Needs-confirmation group data source',
)
assertMatch(profileGroupTemplate, /reviewStatus\s*===\s*'unchanged'[\s\S]*无需修改/, 'Unchanged profile status')
assertMatch(
  profileGroupTemplate,
  /:disabled="applying\s*\|\|\s*isUnchangedCandidate\(candidate\)"/,
  'Unchanged profile candidate cannot be selected',
)
const toggleProfileCandidateBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+toggleProfileCandidate\s*\([^)]*\)\s*:\s*void/,
  'toggleProfileCandidate',
)
assertMatch(toggleProfileCandidateBody, /isUnchangedCandidate\(candidate\)/, 'Unchanged profile selection guard')
assertMatch(duplicateGroupTemplate, /v-for="work in duplicateWorkCandidates"/, 'Duplicate group data source')
assertNoMatch(
  importPageSections.template,
  /v-for="work in extraction\.workCandidates"/,
  'No ungrouped work candidates',
)
assertMatch(
  unmappedGroupTemplate,
  /v-for="(?:segment|\(segment,\s*index\)) in extraction\.unmappedSegments"/,
  'Unmapped segments are rendered individually',
)
assertMatch(unmappedGroupTemplate, /ignoredMediaPlaceholderCount/, 'Media placeholders remain separately visible')
for (const field of [
  'projectName',
  'roleName',
  'publishStatus',
  'workTypeCode',
  'roleLevelCode',
  'shootYear',
  'shootMonth',
  'platform',
  'syncSoundStatus',
  'collaborators',
  'achievementText',
  'description',
]) {
  assertMatch(importPageSections.script, new RegExp(`key:\\s*'${field}'`), `Visible work field ${field}`)
}
assertMatch(importPageSections.template, /visibleWorkFields\(work\)/, 'All populated work fields are rendered')
assertMatch(
  importPageSections.template,
  /formatProfileImportValue\(candidate\.fieldKey,/,
  'Profile enum values use display-only labels',
)
assertMatch(
  importPageSections.template,
  /formatWorkImportValue\(field\.key,\s*field\.value\)/,
  'Work enum values use display-only labels',
)
const profileEnumLabelsBody = extractFunctionBlock(
  importPageSections.script,
  /const\s+PROFILE_ENUM_VALUE_LABELS[^=]*=/,
  'PROFILE_ENUM_VALUE_LABELS',
)
const workEnumLabelsBody = extractFunctionBlock(
  importPageSections.script,
  /const\s+WORK_ENUM_VALUE_LABELS[^=]*=/,
  'WORK_ENUM_VALUE_LABELS',
)
for (const [field, values, source] of [
  ['gender', ['male', 'female'], profileEnumLabelsBody],
  ['birth_precision', ['year', 'month', 'day'], profileEnumLabelsBody],
  ['publishStatus', ['aired', 'upcoming', 'stage', 'horizontal', 'other'], workEnumLabelsBody],
  [
    'workTypeCode',
    [
      'short_drama', 'horizontal_short_drama', 'stage_play', 'musical', 'tv_column_drama',
      'film_tv', 'micro_film', 'horizontal', 'stage', 'other',
    ],
    workEnumLabelsBody,
  ],
  [
    'roleLevelCode',
    [
      'lead', 'supporting', 'antagonist', 'female_lead', 'female_supporting_1',
      'female_supporting_2', 'female_antagonist_1', 'male_lead', 'male_supporting_1',
      'male_supporting_2', 'male_antagonist_1', 'other',
    ],
    workEnumLabelsBody,
  ],
  ['syncSoundStatus', ['sync', 'dubbed', 'unknown'], workEnumLabelsBody],
]) {
  const fieldLabelsBody = extractFunctionBlock(source, new RegExp(`\\b${field}\\s*:`), `${field} labels`)
  for (const value of values) {
    assertMatch(fieldLabelsBody, new RegExp(`\\b${value}:`), `${field} display label ${value}`)
  }
}
const formatProfileImportValueBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+formatProfileImportValue\s*\([^)]*\)\s*:\s*string/,
  'formatProfileImportValue',
)
const formatWorkImportValueBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+formatWorkImportValue\s*\([^)]*\)\s*:\s*string/,
  'formatWorkImportValue',
)
assertNoMatch(
  `${formatProfileImportValueBody}\n${formatWorkImportValueBody}`,
  /profileFinalValues|workFinalFields|candidateValue\s*=/,
  'Display labels cannot mutate raw apply values',
)
assertMatch(
  importPageSections.script,
  /result\.profileCandidates\.map\(\(candidate\)\s*=>\s*\[candidate\.candidateId,\s*candidate\.candidateValue\]\)/,
  'Profile apply draft retains raw candidate values',
)
assertMatch(
  importPageSections.script,
  /result\.workCandidates\.map\(\(work\)\s*=>\s*\[work\.candidateId,\s*copyProfileImportWorkFields\(work\)\]\)/,
  'Work apply draft retains raw candidate values',
)
assertMatch(importPageSections.template, /field\.sourceText/, 'Per-field work evidence')
assertMatch(importPageSections.template, /field\.warning/, 'Per-field work warning')
assertMatch(importPageSections.template, /workMatchStatusLabel\(work\.matchStatus\)/, 'Visible work match status')
assertNoMatch(importPageSections.script, /function\s+workSourceText/, 'No single aggregated work evidence fallback')
assertMatch(
  importPageSections.script,
  /onUnload\(\(\)\s*=>\s*\{[\s\S]*pageActive\.value\s*=\s*false[\s\S]*applyRevision\.value\s*\+=\s*1[\s\S]*invalidateExtractionDraft\(\)[\s\S]*importStore\.clear\(\)/,
  'Import unload invalidates in-flight extraction and fully clears source',
)
const mapProfileImportErrorBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+mapProfileImportError\s*\(\s*error:\s*unknown\s*\)\s*:\s*string/,
  'mapProfileImportError',
)
for (let code = 46001; code <= 46017; code += 1) {
  assertMatch(importPageSections.script, new RegExp(`\\b${code}:`), `Profile import numeric error ${code}`)
}
assertMatch(mapProfileImportErrorBody, /PROFILE_IMPORT_ERROR_MESSAGES\[error\.code\]/, 'Numeric profile import error lookup')
assertNoMatch(mapProfileImportErrorBody, /error\.(?:errorCode|message)/, 'Known errors do not depend on response text')
assertNoMatch(importPageSections.script, /capability\.reason/, 'No legacy capability reason fallback')
assertMatch(importPage, /applyProfileImport[\s\S]*markApplied\(\)/, 'Applied import refresh signal')
assertMatch(importPage, /buildProfileImportApplyRequest/, 'Profile import apply builder usage')
assertMatch(importPageSections.template, /sourceText/, 'Human-readable source evidence')
assertNoMatch(importPageSections.template, /candidateProof/, 'Candidate proof is not rendered as evidence')
assertNoMatch(
  importPageSections.template,
  /v-model="(?:candidate\.candidateValue|work\.(?:projectName|roleName))"/,
  'Signed extraction values remain read-only',
)
assertNoMatch(importPage, /:\s*any\b|as any\b/, 'Typed profile import review')

const worksPage = await readText('kaipai-frontend/src/pkg-profile/works/index.vue')
assertMatch(worksPage, /const PAGE_SIZE\s*=\s*10/, 'Ten-item work pages')
assertMatch(worksPage, /loadNextPage/, 'Paged work loading')
assertMatch(worksPage, /keyword[\s\S]*publishStatus[\s\S]*workTypeCode/, 'Work filters')
assertMatch(worksPage, /getRepresentativeWorks[\s\S]*setRepresentativeWorks/, 'Representative work editing')
assertMatch(worksPage, /deleteActorWork[\s\S]*PROFILE_WORK_IN_USE/, 'Protected work deletion')
assertNoMatch(worksPage, /MAX_WORK_EXPERIENCES|最多 10 条|:\s*any\b|as any\b/, 'Unlimited typed work library')

const actorWorkTypes = await readText('kaipai-frontend/src/types/actor-work.ts')
const actorWorkSaveBody = extractFunctionBlock(
  actorWorkTypes,
  /export\s+interface\s+ActorWorkSave/,
  'ActorWorkSave',
)
assertNoMatch(actorWorkSaveBody, /\bsourceType\??\s*:/, 'Work save DTO excludes server provenance')
assertMatch(
  actorWorkTypes,
  /export\s+type\s+ActorWorkSourceType\s*=\s*'manual'\s*\|\s*'import'\s*\|\s*'migration'/,
  'Work provenance values',
)
assertNoMatch(
  actorWorkTypes,
  /ActorWorkSourceType[^\n]*(?:explicit|inferred_from_roles|direct)/,
  'Work provenance excludes import evidence values',
)
const actorWorkBody = extractFunctionBlock(
  actorWorkTypes,
  /export\s+interface\s+ActorWork\b(?:\s+extends[^\{]+)?/,
  'ActorWork',
)
assertMatch(actorWorkBody, /\bsourceType:\s*ActorWorkSourceType\s*;/, 'Work response includes provenance')
assertMatch(
  actorWorkTypes,
  /export\s+type\s+PositiveSortNo\s*=\s*number\s*&\s*\{\s*readonly\s+__positiveSortNo:\s*unique symbol;?\s*\}/,
  'Work asset sort number has a positive-value brand',
)
const actorAssetBindingBody = extractFunctionBlock(
  actorWorkTypes,
  /export\s+interface\s+ActorAssetBinding/,
  'ActorAssetBinding',
)
assertMatch(actorAssetBindingBody, /\bassetId:\s*number\s*;/, 'Work asset binding ID')
assertMatch(actorAssetBindingBody, /\busageCode:\s*'still'\s*\|\s*'clip'\s*;/, 'Work asset binding usage')
assertMatch(actorAssetBindingBody, /\bsortNo:\s*PositiveSortNo\s*;/, 'Work asset binding positive sort')

const actorWorkApi = await readText('kaipai-frontend/src/api/actor-work.ts')
const replaceActorWorkAssetsBody = extractFunctionBlock(
  actorWorkApi,
  /export\s+function\s+replaceActorWorkAssets\s*\(\s*id:\s*number,\s*bindings:\s*ActorAssetBinding\[\]\s*\)\s*:\s*Promise<void>/,
  'replaceActorWorkAssets',
)
assertMatch(
  replaceActorWorkAssetsBody,
  /return\s+put<void>\(\s*`\/api\/actor\/works\/\$\{id\}\/assets`,\s*\{\s*bindings\s*\}\s*\)/,
  'Work asset complete-set replacement API',
)

const workEditPage = await readText('kaipai-frontend/src/pkg-profile/work-edit/index.vue')
const workEditSections = extractSfcSections(workEditPage, 'Work editor SFC')
assertMatch(workEditPage, /getActorWork[\s\S]*updateActorWork[\s\S]*createActorWork/, 'Work create and edit')
assertMatch(workEditPage, /项目名称[\s\S]*角色名称[\s\S]*播出状态[\s\S]*作品类型[\s\S]*拍摄时间[\s\S]*平台/, 'Complete work form')
assertNoMatch(workEditPage, /:\s*any\b|as any\b/, 'Typed work editor')
assertMatch(
  workEditSections.template,
  /work-edit__source-row[\s\S]*作品来源[\s\S]*\{\{\s*sourceTypeLabel\s*\}\}/,
  'Existing work provenance is a compact read-only row',
)
assertMatch(
  workEditSections.script,
  /manual:\s*'手动创建'[\s\S]*import:\s*'智能导入'[\s\S]*migration:\s*'历史迁移'/,
  'Work provenance display labels',
)
assertNoMatch(
  workEditSections.script,
  /reactive<ActorWorkSave>\s*\(\s*\{[^}]*\bsourceType\s*:/,
  'Work draft excludes provenance',
)
const hydrateWorkBody = extractFunctionBlock(
  workEditSections.script,
  /async\s+function\s+hydrateWork\s*\([^)]*\)/,
  'hydrateWork',
)
assertMatch(hydrateWorkBody, /workSourceType\.value\s*=\s*work\.sourceType/, 'Hydrated provenance stays read-only')
assertNoMatch(hydrateWorkBody, /Object\.assign\(draft,\s*work\)|sourceType\s*:/, 'Hydration excludes provenance from draft')
const buildWorkSavePayloadBody = extractFunctionBlock(
  workEditSections.script,
  /function\s+buildWorkSavePayload\s*\(\s*\)\s*:\s*ActorWorkSave/,
  'buildWorkSavePayload',
)
assertNoMatch(buildWorkSavePayloadBody, /sourceType/, 'Work save payload excludes provenance')
const saveWorkBody = extractFunctionBlock(
  workEditSections.script,
  /async\s+function\s+saveWork\s*\(\s*\)/,
  'saveWork',
)
assertMatch(saveWorkBody, /const\s+payload\s*=\s*buildWorkSavePayload\(\)/, 'Work save uses an explicit payload')
assertMatch(saveWorkBody, /updateActorWork\(workId\.value,\s*payload\)[\s\S]*createActorWork\(payload\)/, 'Work save submits only editable fields')

const favoriteComposable = await readText('kaipai-frontend/src/composables/use-share-card-favorite.ts')
assertMatch(favoriteComposable, /getShareCardFavoriteStatus/, 'Favorite status API')
assertMatch(favoriteComposable, /addShareCardFavorite/, 'Favorite add API')
assertMatch(favoriteComposable, /removeShareCardFavorite/, 'Favorite remove API')
assertMatch(favoriteComposable, /requireLoginForFavorite[\s\S]*goLogin\(\)/, 'Favorite login gate')
for (const path of [
  'kaipai-frontend/src/pages/actor-profile/detail.vue',
  'kaipai-frontend/src/pkg-card/actor-card/index.vue',
  'kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue',
]) {
  const publicPage = await readText(path)
  assertMatch(publicPage, /useShareCardFavorite/, `${path} favorite state`)
  assertMatch(publicPage, /toggleFavorite/, `${path} favorite action`)
}

console.log('Mini-program career profile hub static gate passed.')
