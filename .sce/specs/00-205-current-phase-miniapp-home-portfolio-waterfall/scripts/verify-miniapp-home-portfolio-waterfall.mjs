import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(scriptDirectory, '..', '..', '..', '..');
const homePath = resolve(repositoryRoot, 'kaipai-frontend/src/pages/home/index.vue');
const homeSource = readFileSync(homePath, 'utf8');
const checks = [];

function check(name, pass, detail) {
  checks.push({ name, pass: Boolean(pass), detail });
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function extractTagContent(source, tagPattern) {
  const match = tagPattern.exec(source);
  return match?.[1] || '';
}

function extractFunctionBody(source, signaturePattern) {
  const match = signaturePattern.exec(source);
  if (!match) return '';

  const openingBrace = source.indexOf('{', match.index + match[0].length);
  if (openingBrace < 0) return '';

  let depth = 1;
  for (let index = openingBrace + 1; index < source.length; index += 1) {
    if (source[index] === '{') depth += 1;
    if (source[index] === '}') depth -= 1;
    if (depth === 0) return source.slice(openingBrace + 1, index);
  }
  return '';
}

function extractBalancedBlock(source, anchor) {
  const anchorIndex = source.indexOf(anchor);
  if (anchorIndex < 0) return '';

  const openingBrace = source.indexOf('{', anchorIndex + anchor.length);
  if (openingBrace < 0) return '';

  let depth = 1;
  for (let index = openingBrace + 1; index < source.length; index += 1) {
    if (source[index] === '{') depth += 1;
    if (source[index] === '}') depth -= 1;
    if (depth === 0) return source.slice(openingBrace + 1, index);
  }
  return '';
}

function extractViewByClass(source, className) {
  const classPattern = new RegExp(
    `<view\\b[^>]*\\bclass\\s*=\\s*["'][^"']*\\b${escapeRegExp(className)}\\b[^"']*["'][^>]*>`,
    'g',
  );
  const opening = classPattern.exec(source);
  if (!opening) return '';

  const viewPattern = /<\/?view\b[^>]*>/g;
  viewPattern.lastIndex = opening.index;
  let depth = 0;
  let match = viewPattern.exec(source);
  while (match) {
    const isClosing = match[0].startsWith('</');
    const isSelfClosing = /\/\s*>$/.test(match[0]);
    if (isClosing) {
      depth -= 1;
    } else if (!isSelfClosing) {
      depth += 1;
    }

    if (depth === 0) return source.slice(opening.index, viewPattern.lastIndex);
    match = viewPattern.exec(source);
  }
  return '';
}

function hasOrderedFragments(source, fragments) {
  let cursor = -1;
  for (const fragment of fragments) {
    cursor = source.indexOf(fragment, cursor + 1);
    if (cursor < 0) return false;
  }
  return true;
}

const templateSource = extractTagContent(homeSource, /<template>([\s\S]*?)<\/template>/);
const scriptSource = extractTagContent(homeSource, /<script\s+setup[^>]*>([\s\S]*?)<\/script>/);
const styleSource = extractTagContent(homeSource, /<style[^>]*>([\s\S]*?)<\/style>/);
const hydratePageBody = extractFunctionBody(scriptSource, /async\s+function\s+hydratePage\s*\(\s*\)\s*:\s*Promise<void>/);
const loadHomePortfolioItemsBody = extractFunctionBody(scriptSource, /async\s+function\s+loadHomePortfolioItems\s*\(\s*\)\s*:\s*Promise<HomePortfolioItem\[\]>/);
const buildHomeAiPortfolioItemsBody = extractFunctionBody(scriptSource, /function\s+buildHomeAiPortfolioItems\s*\(/);
const buildHomeAiItemBody = extractFunctionBody(scriptSource, /function\s+buildHomeAiItem\s*\(/);
const buildHomeManualPortfolioItemsBody = extractFunctionBody(scriptSource, /async\s+function\s+buildHomeManualPortfolioItems\s*\(/);
const isUsableAiTaskBody = extractFunctionBody(scriptSource, /function\s+isUsableAiTask\s*\(/);
const isUsableAiArtifactBody = extractFunctionBody(scriptSource, /function\s+isUsableAiArtifact\s*\(/);
const openHomePortfolioItemBody = extractFunctionBody(scriptSource, /function\s+openHomePortfolioItem\s*\(/);
const waterfallTemplate = extractViewByClass(templateSource, 'home-page__portfolio-waterfall');
const waterfallStyle = extractBalancedBlock(styleSource, '&__portfolio-waterfall');
const columnStyle = extractBalancedBlock(styleSource, '&__portfolio-column');

// 00-201 protections: these must stay green before and after the new work exists.
check(
  '00-201 Hero title remains intact',
  /为每一次相遇[\s\S]{0,80}留下光影/.test(templateSource),
  'Keep the existing Home Hero title; the waterfall belongs after the creation stage.',
);
check(
  '00-201 Hero subtitle remains intact',
  /用 AI 快速生成你的分享图/.test(templateSource),
  'Keep the existing Home Hero subtitle.',
);
check(
  '00-201 yin-yang background URL remains local and unchanged',
  /background-image:\s*url\(['"]\/static\/home\/yin-yang-creation\.png['"]\)/.test(scriptSource),
  'Keep creationStageStyle pointed at /static/home/yin-yang-creation.png.',
);
check(
  '00-201 creation stage remains 480rpx',
  /height:\s*480rpx\s*;/.test(extractBalancedBlock(styleSource, '&__creation-stage')),
  'Keep home-page__creation-stage at height: 480rpx.',
);

const goAiProfileCardBody = extractFunctionBody(scriptSource, /function\s+goAiProfileCard\s*\(\s*\)\s*:\s*void/);
const goCardListBody = extractFunctionBody(scriptSource, /function\s+goCardList\s*\(\s*\)\s*:\s*void/);
check(
  '00-201 AI creation handler and route remain intact',
  /@click="goAiProfileCard"/.test(templateSource) && /\/pkg-card\/ai-profile-card\/index/.test(goAiProfileCardBody),
  'Keep the existing AI entry bound to goAiProfileCard() and /pkg-card/ai-profile-card/index.',
);
check(
  '00-201 manual creation handler and route remain intact',
  /@click="goCardList"/.test(templateSource) && /\/pkg-card\/card-list\/index/.test(goCardListBody),
  'Keep the existing manual entry bound to goCardList() and /pkg-card/card-list/index.',
);

// 00-205 placement and quiet visual contract.
check(
  'waterfall is rendered only after the existing yin-yang stage',
  hasOrderedFragments(templateSource, ['home-page__creation-stage', 'home-page__portfolio-waterfall']),
  'Add the waterfall immediately after home-page__creation-stage, never inside the Hero or stage.',
);
check(
  'waterfall is conditional on real items only',
  /<view\b[^>]*\bv-if\s*=\s*["']portfolioItems\.length["'][^>]*\bclass\s*=\s*["'][^"']*home-page__portfolio-waterfall/.test(templateSource),
  'Render home-page__portfolio-waterfall only when portfolioItems.length is non-zero.',
);
check(
  'waterfall has no heading, empty state, loading state, or controls',
  Boolean(waterfallTemplate) &&
    !/<text\b|<button\b|KpEmpty\b|portfolio-(?:heading|empty|loading|error)/.test(waterfallTemplate),
  'The Home waterfall is image-only: no heading, status copy, empty state, retry, or new action.',
);
check(
  'waterfall uses two explicit vertical columns with widthFix images',
  /v-for="\(column,\s*columnIndex\)\s+in\s+portfolioColumns"/.test(waterfallTemplate) &&
    /v-for="item\s+in\s+column"/.test(waterfallTemplate) &&
    /<image\b[^>]*\bmode\s*=\s*["']widthFix["']/.test(waterfallTemplate) &&
    /display:\s*flex\s*;/.test(waterfallStyle) &&
    /flex-direction:\s*column\s*;/.test(columnStyle) &&
    /flex:\s*1\s*;/.test(columnStyle),
  'Use portfolioColumns with two equal flex columns and natural-height widthFix image tiles.',
);
check(
  'portfolio item state starts empty and is split deterministically into two columns',
  /const\s+portfolioItems\s*=\s*ref(?:<[^>]+>)?\(\s*\[\s*\]\s*\)/.test(scriptSource) &&
    /const\s+portfolioColumns\s*=\s*computed/.test(scriptSource) &&
    /portfolioItems\.value[\s\S]{0,700}index\s*%\s*2/.test(scriptSource),
  'Keep a local empty portfolioItems ref and derive exactly two columns from its item index.',
);
check(
  'waterfall contains no static fake or external placeholder artwork',
  Boolean(waterfallTemplate) &&
    !/https?:\/\/(?:images\.unsplash\.com|picsum\.photos|placehold\.co|dummyimage\.com)/i.test(waterfallTemplate),
  'Portfolio tiles must receive only API-derived URLs or the existing KpShareSceneCover fallback.',
);

// Actor-only request boundary, stale clearing, and quiet failure behavior.
const hydrateClearsBeforeGuard = hasOrderedFragments(hydratePageBody, [
  'portfolioItems.value = [];',
  'bootstrapSession()',
  'if (requestVersion !== portfolioRequestVersion || !user || user.role === 2)',
]);
const adapterAfterGuard = hydratePageBody.indexOf('loadHomePortfolioItems()') > hydratePageBody.indexOf('user.role === 2');
check(
  'visitor and crew clear stale items before the personal-data request boundary',
  /let\s+portfolioRequestVersion\s*=\s*0\s*;/.test(scriptSource) && hydrateClearsBeforeGuard && adapterAfterGuard,
  'Clear portfolioItems at every hydrate start, then return for no user or role === 2 before loadHomePortfolioItems().',
);
check(
  'only the actor-side adapter reads existing personal-work APIs',
  Boolean(loadHomePortfolioItemsBody) &&
    /getMyShareCards\(\)/.test(loadHomePortfolioItemsBody) &&
    /listAiProfileCardArtifacts\(\)/.test(loadHomePortfolioItemsBody) &&
    /listAiProfileCardTasks\(\)/.test(loadHomePortfolioItemsBody) &&
    /getActorCardConfig\(/.test(scriptSource),
  'Read /api/card/my-cards, /api/card/config, AI artifacts, and AI tasks only through the Home-local actor adapter.',
);
check(
  'portfolio reads fail quietly to an empty result',
  Boolean(loadHomePortfolioItemsBody) && /catch[\s\S]{0,240}return\s*\[\s*\]/.test(loadHomePortfolioItemsBody) && !/showToast|showLoading|showModal/.test(loadHomePortfolioItemsBody),
  'loadHomePortfolioItems() must catch its own read failures and return [] without a visible loading or error state.',
);

// Real AI/manual item construction.
check(
  'AI artifacts use the existing image display helper and real-artifact filter',
  /buildAiProfileCardDisplayImageUrl/.test(scriptSource) &&
    /isUsableAiArtifact/.test(scriptSource) &&
    /!!artifact\.generatedImageUrl/.test(isUsableAiArtifactBody) &&
    /!!artifact\.shareCardId/.test(isUsableAiArtifactBody) &&
    /!isMockProvider\(artifact\.providerCode\)/.test(isUsableAiArtifactBody) &&
    /!isSameMediaUrl\(artifact\.generatedImageUrl,\s*artifact\.sourceImageUrl\)/.test(isUsableAiArtifactBody),
  'Official AI items require a genuine generated image, valid share card, non-mock provider, and non-source image.',
);
check(
  'successful AI task fallback is deduplicated by task ID after official artifacts',
  Boolean(buildHomeAiPortfolioItemsBody) &&
    /representedTaskIds\s*=\s*new Set/.test(buildHomeAiPortfolioItemsBody) &&
    /representedTaskIds\s*=\s*new Set\([\s\S]{0,260}(?:artifact|item)\.taskId/.test(buildHomeAiPortfolioItemsBody) &&
    /representedTaskIds\.has\(task\.taskId\)/.test(buildHomeAiPortfolioItemsBody) &&
    /representedTaskIds\.add\(task\.taskId\)/.test(buildHomeAiPortfolioItemsBody) &&
    /task\.shareCardId[\s\S]{0,180}shareCardIdByScene\[task\.templateSceneCode\]/.test(buildHomeAiPortfolioItemsBody) &&
    /task\.status\s*===\s*['"]success['"]/.test(isUsableAiTaskBody) &&
    /!!task\.generatedImageUrl/.test(isUsableAiTaskBody) &&
    /!isMockProvider\(task\.providerCode\)/.test(isUsableAiTaskBody) &&
    /!isSameMediaUrl\(task\.generatedImageUrl,\s*task\.sourceImageUrl\)/.test(isUsableAiTaskBody),
  'Add usable task results only when their taskId is not already represented by an official artifact.',
);
check(
  'every manual card remains and uses first non-empty highlighted photo with cover fallback',
  Boolean(buildHomeManualPortfolioItemsBody) &&
    /cards\.map\(/.test(buildHomeManualPortfolioItemsBody) &&
    !/\.filter\(/.test(buildHomeManualPortfolioItemsBody) &&
    /highlightedPhotos[\s\S]{0,260}\.find\([\s\S]{0,120}trim\(\)/.test(buildHomeManualPortfolioItemsBody) &&
    /<KpShareSceneCover\b[^>]*\bv-else\b/.test(waterfallTemplate),
  'Map every manual card; use the first trimmed highlightedPhotos URL, otherwise render KpShareSceneCover.',
);

// Existing detail routes remain the only portfolio click targets.
check(
  'AI and manual tiles reuse their existing detail routes',
  /\/pkg-card\/ai-profile-card-detail\/index\?/.test(scriptSource) &&
    /detailTaskId:\s*artifact\.artifactId\s*\|\|\s*artifact\.taskId/.test(buildHomeAiItemBody) &&
    /item\.kind\s*===\s*['"]ai['"]/.test(openHomePortfolioItemBody) &&
    /item\.detailTaskId/.test(openHomePortfolioItemBody) &&
    /buildShareCardDetailPath\(\{\s*shareCardId:\s*item\.shareCardId\s*\}\)/.test(openHomePortfolioItemBody),
  'AI tiles must prefer artifactId for the existing AI detail loader; manual tiles must call buildShareCardDetailPath({ shareCardId }).',
);

const failed = checks.filter((item) => !item.pass);
for (const item of checks) {
  console.log(`${item.pass ? 'PASS' : 'FAIL'} ${item.name}`);
  if (!item.pass) console.log(`  ${item.detail}`);
}

if (failed.length) {
  console.error(`\n${failed.length} miniapp Home portfolio waterfall check(s) failed.`);
  process.exit(1);
}

console.log('\nAll miniapp Home portfolio waterfall checks passed.');
