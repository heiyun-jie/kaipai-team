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
assertNoMatch(importStore, /uni\.setStorage|localStorage|persist/, 'No persisted profile import source')

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

const mpSync = await readText('kaipai-frontend/scripts/sync-mp-weixin.ps1')
assertMatch(mpSync, /Apply-LocalDevProjectConfig/, 'Local MiniProgram project config sync')
assertMatch(mpSync, /\.env\.local[\s\S]*VITE_API_BASE_URL/, 'Local API override detection')
assertMatch(mpSync, /urlCheck\s*=\s*\$false/, 'Local URL validation override')

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
assertMatch(importPage, /beginClipboardRead[\s\S]*uni\.getClipboardData/, 'Explicit clipboard read')
assertNoMatch(importPage, /onLoad\([^)]*=>[\s\S]{0,300}getClipboardData/, 'No automatic clipboard read')
assertMatch(importPage, /async function submitExtraction\(\)[\s\S]*extractProfileImport/, 'Explicit extraction action')
assertMatch(importPage, /requiresExplicitConfirmation[\s\S]*confirmed/, 'Explicit inferred candidate confirmation')
assertMatch(importPage, /个人资料[\s\S]*作品[\s\S]*需要确认[\s\S]*疑似重复[\s\S]*未映射内容/, 'Import review groups')
assertMatch(importPage, /onUnload\(\(\) =>[\s\S]*clear\(\)/, 'Import source cleanup')
assertMatch(importPage, /mapProfileImportError/, 'Profile import error mapping')
assertNoMatch(importPage, /:\s*any\b|as any\b/, 'Typed profile import review')

const worksPage = await readText('kaipai-frontend/src/pkg-profile/works/index.vue')
assertMatch(worksPage, /const PAGE_SIZE\s*=\s*10/, 'Ten-item work pages')
assertMatch(worksPage, /loadNextPage/, 'Paged work loading')
assertMatch(worksPage, /keyword[\s\S]*publishStatus[\s\S]*workTypeCode/, 'Work filters')
assertMatch(worksPage, /getRepresentativeWorks[\s\S]*setRepresentativeWorks/, 'Representative work editing')
assertMatch(worksPage, /deleteActorWork[\s\S]*PROFILE_WORK_IN_USE/, 'Protected work deletion')
assertNoMatch(worksPage, /MAX_WORK_EXPERIENCES|最多 10 条|:\s*any\b|as any\b/, 'Unlimited typed work library')

const workEditPage = await readText('kaipai-frontend/src/pkg-profile/work-edit/index.vue')
assertMatch(workEditPage, /getActorWork[\s\S]*updateActorWork[\s\S]*createActorWork/, 'Work create and edit')
assertMatch(workEditPage, /项目名称[\s\S]*角色名称[\s\S]*播出状态[\s\S]*作品类型[\s\S]*拍摄时间[\s\S]*平台/, 'Complete work form')
assertNoMatch(workEditPage, /:\s*any\b|as any\b/, 'Typed work editor')

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
