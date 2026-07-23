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
  'kaipai-frontend/src/pages/actor-profile/edit.vue',
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
assertMatch(edit, /updateMyActorProfile\(/, 'Versioned Mine profile save')
assertMatch(edit, /chooseAvatarFromAssets/, 'Avatar asset selection')
assertMatch(edit, /保存资料/, 'Single profile save action')
assertMatch(edit, /保存资料[\s\S]*放弃修改[\s\S]*继续编辑/, 'Dirty leave choices')
assertNoMatch(edit, /完成度|提升建议|AI 全量润色/, 'No profile operation cards')
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
