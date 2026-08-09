/**
 * 00-207 专项门禁：v2 Tab 页壳层胶囊对齐、mine 游客态收口、小程序压缩兼容与启动脚本去重。
 *
 * 门禁分四组：
 *   [protect]  保护 00-206 已建立的 home-v2 / card-list-page / mine-v2 壳层与动作，防止本轮对齐改动误删既有能力
 *   [align]    本轮新增的三页标题行胶囊对齐合同
 *   [visitor]  本轮新增的 mine 游客态收口合同
 *   [compat]   minify 兼容、首页风格卡比例与本地启动脚本合同
 *   [dist]     src / dist/build / dist/dev 三层一致性
 *
 * 用法：node .sce/specs/00-207-.../scripts/verify-miniapp-v2-tab-shell-and-mp-minify.mjs
 * 退出码：全部通过 0，存在失败 1。
 */

import { readFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(scriptDirectory, '..', '..', '..', '..');
const frontendRoot = resolve(repositoryRoot, 'kaipai-frontend');

const checks = [];

function check(group, name, pass, detail) {
  checks.push({ group, name, pass: Boolean(pass), detail });
}

function readOrEmpty(relativePath) {
  const absolute = resolve(frontendRoot, relativePath);
  if (!existsSync(absolute)) return '';
  return readFileSync(absolute, 'utf8');
}

/** 抽取 <style ...> ... </style> 内容，避免把模板/脚本文本误判为样式合同。 */
function extractStyleBlock(source) {
  const match = /<style\b[^>]*>([\s\S]*?)<\/style>/.exec(source);
  return match?.[1] || '';
}

/** 抽取 <script setup ...> ... </script> 内容。 */
function extractSetupBlock(source) {
  const match = /<script\b[^>]*\bsetup\b[^>]*>([\s\S]*?)<\/script>/.exec(source);
  return match?.[1] || '';
}

/** 抽取 <template> ... </template> 内容。 */
function extractTemplateBlock(source) {
  const match = /<template\b[^>]*>([\s\S]*)<\/template>/.exec(source);
  return match?.[1] || '';
}

/**
 * 抽取 SCSS 嵌套块 `&__name { ... }` 的花括号平衡内容。
 * 用于对单个 BEM 元素做属性级断言，而不是整文件快照。
 */
function extractScssElementBlock(styleSource, elementName) {
  const anchor = `&__${elementName}`;
  let searchFrom = 0;
  for (;;) {
    const anchorIndex = styleSource.indexOf(anchor, searchFrom);
    if (anchorIndex < 0) return '';

    // 排除 `&__style-img-wrap` 命中 `&__style-img` 这类前缀误匹配
    const nextChar = styleSource[anchorIndex + anchor.length];
    if (nextChar && /[A-Za-z0-9-]/.test(nextChar)) {
      searchFrom = anchorIndex + anchor.length;
      continue;
    }

    const openingBrace = styleSource.indexOf('{', anchorIndex + anchor.length);
    if (openingBrace < 0) return '';

    let depth = 1;
    for (let index = openingBrace + 1; index < styleSource.length; index += 1) {
      if (styleSource[index] === '{') depth += 1;
      if (styleSource[index] === '}') depth -= 1;
      if (depth === 0) return styleSource.slice(openingBrace + 1, index);
    }
    return '';
  }
}

const CAPSULE_BIND = /:style\s*=\s*"\{\s*top:\s*backButtonStyle\.top\s*,\s*height:\s*backButtonStyle\.height\s*\}"/;
const FLOATING_IMPORT = /import\s*\{\s*getFloatingBackNavStyles\s*\}\s*from\s*'@\/utils\/floating-back-nav'/;
const FLOATING_CALL = /const\s*\{\s*backButtonStyle\s*\}\s*=\s*getFloatingBackNavStyles\(\)/;

// ---------------------------------------------------------------------------
// 通用：三页共享的胶囊对齐合同
// ---------------------------------------------------------------------------

const alignTargets = [
  {
    label: 'home',
    path: 'src/pages/home/index.vue',
    titleRowClass: 'home-v2__title-row',
    headerElement: 'header',
    titleElement: 'title-row',
  },
  {
    label: 'card-list',
    path: 'src/pages/card-list/index.vue',
    titleRowClass: 'card-list-page__title-row',
    headerElement: 'header',
    titleElement: 'title-row',
  },
  {
    label: 'mine',
    path: 'src/pages/mine/index.vue',
    titleRowClass: 'mine-v2__header-row',
    headerElement: 'header',
    titleElement: 'header-row',
  },
];

for (const target of alignTargets) {
  const source = readOrEmpty(target.path);
  const template = extractTemplateBlock(source);
  const setup = extractSetupBlock(source);
  const style = extractStyleBlock(source);

  check('align', `${target.label}: 存在源文件`, source.length > 0, target.path);

  check(
    'align',
    `${target.label}: 引入 getFloatingBackNavStyles`,
    FLOATING_IMPORT.test(setup) && FLOATING_CALL.test(setup),
    '需从 @/utils/floating-back-nav 引入并解构 backButtonStyle',
  );

  // 标题行所在标签必须同时携带目标 class 与胶囊绑定
  const titleRowTagPattern = new RegExp(
    `<view\\b[^>]*\\bclass\\s*=\\s*"[^"]*\\b${target.titleRowClass}\\b[^"]*"[^>]*>`,
  );
  const titleRowTag = titleRowTagPattern.exec(template)?.[0] || '';
  check(
    'align',
    `${target.label}: 标题行绑定胶囊 top/height`,
    titleRowTag.length > 0 && CAPSULE_BIND.test(titleRowTag),
    `${target.titleRowClass} 需绑定 backButtonStyle.top 与 backButtonStyle.height`,
  );

  check(
    'align',
    `${target.label}: 保留 KpCapsuleSpacer`,
    /<KpCapsuleSpacer\b/.test(template),
    '状态栏占位组件不得在本轮被移除',
  );

  const headerBlock = extractScssElementBlock(style, target.headerElement);
  check(
    'align',
    `${target.label}: header 为定位父级`,
    /position\s*:\s*relative/.test(headerBlock),
    '标题行脱离文档流后 header 必须是 relative',
  );

  const titleBlock = extractScssElementBlock(style, target.titleElement);
  check(
    'align',
    `${target.label}: 标题行 absolute + 右侧避让 200rpx`,
    /position\s*:\s*absolute/.test(titleBlock) &&
      /left\s*:\s*32rpx/.test(titleBlock) &&
      /right\s*:\s*200rpx/.test(titleBlock) &&
      /align-items\s*:\s*center/.test(titleBlock),
    '需 absolute + left 32rpx + right 200rpx + 垂直居中',
  );
}

// ---------------------------------------------------------------------------
// 各页塌陷补偿 + 00-206 既有能力保护
// ---------------------------------------------------------------------------

const homeSource = readOrEmpty('src/pages/home/index.vue');
const homeStyle = extractStyleBlock(homeSource);
const homeSetup = extractSetupBlock(homeSource);
const homeTemplate = extractTemplateBlock(homeSource);

check(
  'align',
  'home: greeting 补 margin-top 补偿塌陷',
  /margin-top\s*:\s*12rpx/.test(extractScssElementBlock(homeStyle, 'greeting')),
  '标题行 absolute 后 greeting 需补上边距',
);

check(
  'compat',
  'home: 风格卡比例为 3/2',
  /aspect-ratio\s*:\s*3\s*\/\s*2/.test(extractScssElementBlock(homeStyle, 'style-img-wrap')),
  '&__style-img-wrap 需为 aspect-ratio: 3/2',
);

check(
  'protect',
  'home: 保留 00-206 创建入口与草稿恢复',
  /function\s+goCreate\b|const\s+goCreate\b/.test(homeSetup) &&
    /goCreateWithStyle/.test(homeSetup) &&
    /resumeDraft/.test(homeSetup) &&
    /listActorCards/.test(homeSetup),
  'goCreate / goCreateWithStyle / resumeDraft / listActorCards 不得丢失',
);

check(
  'protect',
  'home: 保留 AI 横幅与模板创建区',
  /AI\s*创建演员卡/.test(homeTemplate) &&
    /模板创建/.test(homeTemplate) &&
    /home-v2__style-grid/.test(homeTemplate),
  '00-206 首页三区结构不得在本轮被改写',
);

const cardListSource = readOrEmpty('src/pages/card-list/index.vue');
const cardListStyle = extractStyleBlock(cardListSource);
const cardListTemplate = extractTemplateBlock(cardListSource);

check(
  'align',
  'card-list: tabs 补 margin-top 补偿塌陷',
  /margin-top\s*:\s*16rpx/.test(extractScssElementBlock(cardListStyle, 'tabs')),
  '标题行 absolute 后 tabs 需补上边距',
);

check(
  'protect',
  'card-list: 保留名片夹标题与双 Tab 结构',
  /名片夹/.test(cardListTemplate) && /card-list-page__tabs/.test(cardListTemplate),
  '00-206 名片夹壳层不得在本轮被改写',
);

// ---------------------------------------------------------------------------
// mine 游客态收口
// ---------------------------------------------------------------------------

const mineSource = readOrEmpty('src/pages/mine/index.vue');
const mineSetup = extractSetupBlock(mineSource);
const mineStyle = extractStyleBlock(mineSource);

check(
  'align',
  'mine: header 补 padding-bottom 补偿塌陷',
  /padding-bottom\s*:\s*20rpx/.test(extractScssElementBlock(mineStyle, 'header')),
  '标题行 absolute 后 header 需补下内距',
);

check(
  'visitor',
  'mine: isVisitor 由 hasStoredSession 判定',
  /const\s+isVisitor\s*=\s*computed\(\s*\(\)\s*=>\s*!userStore\.hasStoredSession\s*\)/.test(mineSetup) &&
    /const\s+isLoggedIn\s*=\s*computed\(\s*\(\)\s*=>\s*!isVisitor\.value\s*\)/.test(mineSetup),
  '需与 00-192 全局会话语义对齐，不再直接用 userStore.isLoggedIn',
);

check(
  'visitor',
  'mine: 存在登录门禁与统一入口包装',
  /function\s+requireLoginForMineAction\s*\(\s*\)\s*:\s*boolean/.test(mineSetup) &&
    /function\s+openAccountCapability\s*\(\s*url\s*:\s*string\s*\)\s*:\s*void/.test(mineSetup),
  'requireLoginForMineAction / openAccountCapability 必须存在',
);

const gatedAccountRoutes = [
  "'/pages/actor-profile/edit'",
  "'/pages/actor-profile/edit?tab=experience'",
  "'/pages/actor-profile/edit?tab=intro'",
  "'/pkg-card/verify/index'",
];
for (const route of gatedAccountRoutes) {
  const gatedPattern = new RegExp(`openAccountCapability\\(\\s*${route.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*\\)`);
  const rawNavPattern = new RegExp(
    `uni\\.navigateTo\\(\\s*\\{\\s*url\\s*:\\s*${route.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*\\}`,
  );
  check(
    'visitor',
    `mine: 账号入口经门禁 ${route}`,
    gatedPattern.test(mineSetup) && !rawNavPattern.test(mineSetup),
    '账号类入口必须走 openAccountCapability，不得保留裸 navigateTo',
  );
}

check(
  'visitor',
  'mine: displayName 回退到脱敏手机号',
  /import\s*\{\s*formatPhone\s*\}\s*from\s*'@\/utils\/format'/.test(mineSetup) &&
    /formatPhone\(\s*currentUser\.value\?\.phone\s*\|\|\s*''\s*\)/.test(mineSetup),
  '已登录无昵称时需回退 formatPhone(phone)',
);

check(
  'visitor',
  'mine: 游客态不请求完整度',
  /onShow\(\s*async\s*\(\)\s*=>\s*\{[\s\S]*?if\s*\(\s*isVisitor\.value\s*\)\s*return\s*;/.test(mineSetup),
  'onShow 必须在游客分支前置返回，避免个人数据请求',
);

check(
  'protect',
  'mine: 保留退出登录确认链路',
  /KpConfirmDialog/.test(mineSource) && /showLogoutDialog/.test(mineSetup) && /logout/.test(mineSetup),
  '00-206 退出登录能力不得在本轮被移除',
);

// ---------------------------------------------------------------------------
// 压缩兼容 + 启动脚本
// ---------------------------------------------------------------------------

const viteConfig = readOrEmpty('vite.config.ts');

check(
  'compat',
  'vite: 关闭 mp 压缩',
  /build\s*:\s*\{[\s\S]*?minify\s*:\s*false/.test(viteConfig),
  'build.minify 必须为 false',
);

check(
  'compat',
  'vite: 关闭压缩附带原因注释',
  /微信小程序/.test(viteConfig) && /minify/.test(viteConfig) && /(navigateTo|白屏|解析)/.test(viteConfig),
  '必须保留关闭压缩的原因说明，避免后续被误当冗余配置删除',
);

const launcher = readOrEmpty('scripts/start-miniapp.py');

check(
  'compat',
  'launcher: dev watch 去重',
  /def\s+has_existing_dev_watch\s*\(\s*\)\s*->\s*bool\s*:/.test(launcher) && /Win32_Process/.test(launcher),
  '需通过只读进程查询避免重复启动同一个 uni watch',
);

check(
  'compat',
  'launcher: 等待本次真实构建',
  /def\s+file_signature\s*\(/.test(launcher) &&
    /def\s+wait_for_dev_build\s*\(\s*[\s\S]*?proc\s*:\s*subprocess\.Popen/.test(launcher) &&
    /previous_signature/.test(launcher),
  'wait_for_dev_build 需比对 app.json 签名而不是只判断文件存在',
);

check(
  'compat',
  'launcher: dev watch 早退即失败',
  /returncode\s*=\s*proc\.poll\(\)/.test(launcher) && /raise\s+SystemExit/.test(launcher),
  'dev watch 在首次构建前退出必须失败退出，不得假成功',
);

// ---------------------------------------------------------------------------
// 三层产物一致性
// ---------------------------------------------------------------------------

const distLayers = [
  { label: 'dist/build', root: 'dist/build/mp-weixin' },
  { label: 'dist/dev', root: 'dist/dev/mp-weixin' },
];

for (const layer of distLayers) {
  const wxss = readOrEmpty(`${layer.root}/pages/home/index.wxss`);
  const pageJs = readOrEmpty(`${layer.root}/pages/home/index.js`);

  check(
    'dist',
    `${layer.label}: 首页样式已产出 3/2 比例`,
    /aspect-ratio\s*:\s*3\s*\/\s*2/.test(wxss),
    `${layer.root}/pages/home/index.wxss 需包含 aspect-ratio: 3/2`,
  );

  check(
    'dist',
    `${layer.label}: 首页逻辑已产出胶囊对齐`,
    /backButtonStyle/.test(pageJs),
    `${layer.root}/pages/home/index.js 需包含 backButtonStyle`,
  );
}

// ---------------------------------------------------------------------------
// 汇总
// ---------------------------------------------------------------------------

const groupOrder = ['protect', 'align', 'visitor', 'compat', 'dist'];
const groupLabels = {
  protect: '00-206 既有能力保护',
  align: '标题行胶囊对齐',
  visitor: 'mine 游客态收口',
  compat: '压缩兼容与启动脚本',
  dist: '三层产物一致性',
};

let failed = 0;
for (const group of groupOrder) {
  const groupChecks = checks.filter((item) => item.group === group);
  if (!groupChecks.length) continue;
  const groupPassed = groupChecks.filter((item) => item.pass).length;
  console.log(`\n[${group}] ${groupLabels[group]} — ${groupPassed} / ${groupChecks.length} PASS`);
  for (const item of groupChecks) {
    if (item.pass) {
      console.log(`  PASS  ${item.name}`);
    } else {
      failed += 1;
      console.log(`  FAIL  ${item.name}`);
      console.log(`        ${item.detail}`);
    }
  }
}

const total = checks.length;
const passed = total - failed;
console.log(`\n00-207 门禁汇总：${passed} / ${total} PASS`);

if (failed > 0) {
  console.log(`存在 ${failed} 项失败。`);
  process.exit(1);
}
console.log('全部通过。');
