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

const request = await readText('kaipai-frontend/src/utils/request.ts')
assertMatch(request, /class ApiError extends Error/, 'Structured API error class')
assertMatch(
  request,
  /new ApiError\(response\.message \|\| '请求失败', response\.code, response\.errorCode\)/,
  'Structured API error construction',
)

const mine = await readText('kaipai-frontend/src/pages/mine/index.vue')
assertNoMatch(mine, /analytics|trendHeights|openMyQrCode|我的二维码/, 'Mine career hub')

const edit = await readText('kaipai-frontend/src/pages/actor-profile/edit.vue')
assertNoMatch(
  edit,
  /updateActorProfile\(|PhotoCategorySection|WorkExperienceSection|PdfResumeSection|VideoResumeSection/,
  'Simplified actor profile editor',
)

const importPage = await readText('kaipai-frontend/src/pkg-profile/import-review/index.vue')
assertMatch(importPage, /beginClipboardRead[\s\S]*uni\.getClipboardData/, 'Explicit clipboard read')
assertNoMatch(importPage, /onLoad[\s\S]*getClipboardData/, 'No automatic clipboard read')

console.log('Mini-program career profile hub static gate passed.')
