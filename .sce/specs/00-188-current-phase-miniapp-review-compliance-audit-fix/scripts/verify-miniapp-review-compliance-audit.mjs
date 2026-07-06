import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.cwd());

function absolute(relativePath) {
  return path.join(root, relativePath);
}

function exists(relativePath) {
  return fs.existsSync(absolute(relativePath));
}

function read(relativePath) {
  return fs.readFileSync(absolute(relativePath), 'utf8');
}

function readJson(relativePath) {
  return JSON.parse(stripJsonComments(read(relativePath)));
}

function stripJsonComments(content) {
  let output = '';
  let inString = false;
  let escaped = false;
  let inLineComment = false;
  let inBlockComment = false;

  for (let index = 0; index < content.length; index += 1) {
    const char = content[index];
    const next = content[index + 1];

    if (inLineComment) {
      if (char === '\n' || char === '\r') {
        inLineComment = false;
        output += char;
      }
      continue;
    }

    if (inBlockComment) {
      if (char === '*' && next === '/') {
        inBlockComment = false;
        index += 1;
      }
      continue;
    }

    if (inString) {
      output += char;
      if (escaped) {
        escaped = false;
      } else if (char === '\\') {
        escaped = true;
      } else if (char === '"') {
        inString = false;
      }
      continue;
    }

    if (char === '"') {
      inString = true;
      output += char;
      continue;
    }

    if (char === '/' && next === '/') {
      inLineComment = true;
      index += 1;
      continue;
    }

    if (char === '/' && next === '*') {
      inBlockComment = true;
      index += 1;
      continue;
    }

    output += char;
  }

  return output;
}

function listFiles(relativePath, extensions, results = []) {
  const dir = absolute(relativePath);
  if (!fs.existsSync(dir)) return results;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const childRelative = path.join(relativePath, entry.name);
    if (entry.isDirectory()) {
      listFiles(childRelative, extensions, results);
      continue;
    }
    if (extensions.includes(path.extname(entry.name))) {
      results.push(childRelative);
    }
  }
  return results;
}

const checks = [];

function check(name, pass, detail) {
  checks.push({ name, pass, detail });
}

function checkNoPattern(name, files, pattern, detail) {
  const matches = [];
  for (const file of files) {
    if (!exists(file)) continue;
    const content = read(file);
    if (pattern.test(content)) {
      matches.push(file);
    }
  }
  check(name, matches.length === 0, matches.length ? `${detail}\n  Matched: ${matches.join(', ')}` : detail);
}

const sourcePages = readJson('kaipai-frontend/src/pages.json');
check(
  'source default launch page is home',
  sourcePages.pages?.[0]?.path === 'pages/home/index',
  'kaipai-frontend/src/pages.json must list pages/home/index before pages/login/index.',
);

const sourceManifest = readJson('kaipai-frontend/src/manifest.json');
check(
  'source mp-weixin urlCheck is enabled',
  sourceManifest['mp-weixin']?.setting?.urlCheck === true,
  'kaipai-frontend/src/manifest.json mp-weixin.setting.urlCheck must be true for review builds.',
);

check(
  'source official-looking WeChat login icon is removed',
  !exists('kaipai-frontend/src/static/icons/wechat-login.png'),
  'Delete the unused official-looking static/icons/wechat-login.png asset.',
);

const sourceTextFiles = listFiles('kaipai-frontend/src', ['.vue', '.ts', '.json']);
checkNoPattern(
  'source has no media autoplay',
  sourceTextFiles,
  /\bautoplay\b/i,
  'Remove autoplay from mini-program media components.',
);
checkNoPattern(
  'source has no wechat-login asset references',
  sourceTextFiles,
  /wechat-login\.png/i,
  'Remove all references to the retired official-looking login icon.',
);

const visibleBrandFiles = [
  'kaipai-frontend/src/pkg-card/actor-card/index.vue',
  'kaipai-frontend/src/pkg-card/card-list/index.vue',
  'kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue',
  'kaipai-frontend/src/utils/share-artifact.ts',
  'kaipai-frontend/src/utils/actor-card.ts',
];
checkNoPattern(
  'source visible sharing copy avoids platform-brand packaging',
  visibleBrandFiles,
  /WECHAT|微信对话|微信分享面板|调起微信|朋友圈|转发朋友圈/i,
  'Use neutral copy such as 会话卡片、小程序卡片、系统分享面板、保存后发送.',
);

const inviteRiskFiles = [
  'kaipai-frontend/src/utils/share-card-mvp.ts',
  'kaipai-frontend/src/utils/level.ts',
  'kaipai-frontend/src/components/KpInviteSummaryCard.vue',
  'kaipai-frontend/src/pkg-card/card-list/index.vue',
  'kaipai-frontend/src/pkg-card/ai-profile-card/index.vue',
  'kaipai-frontend/src/pkg-card/style-detail/index.vue',
  'kaipai-frontend/src/utils/verify.ts',
  'kaipai-frontend/src/utils/personalization-copy.ts',
];
checkNoPattern(
  'source has no invite-to-unlock inducement copy',
  inviteRiskFiles,
  /再邀请\s*\$\{?[^，。]*?(?:解锁|升到|后可)|邀请[^，。]*?(?:解锁|升级|裂变)/,
  'Replace invite-to-unlock/upgrade copy with neutral capability status copy.',
);

const webviewSource = 'kaipai-frontend/src/pkg-tools/webview/index.vue';
checkNoPattern(
  'source webview page does not expose arbitrary external url mode',
  [webviewSource],
  /<web-view\b|options\.url|externalUrl|web-view 模式/,
  'pkg-tools/webview/index.vue should only render local agreement/settings content.',
);

for (const distRoot of ['kaipai-frontend/dist/build/mp-weixin', 'kaipai-frontend/dist/dev/mp-weixin']) {
  const appJsonPath = `${distRoot}/app.json`;
  const projectConfigPath = `${distRoot}/project.config.json`;

  if (!exists(appJsonPath) || !exists(projectConfigPath)) {
    check(`${distRoot} exists`, false, 'Run npm run build:mp-weixin before final verification.');
    continue;
  }

  const appJson = readJson(appJsonPath);
  check(
    `${distRoot} default launch page is home`,
    appJson.pages?.[0] === 'pages/home/index',
    `${appJsonPath} must list pages/home/index first.`,
  );

  const projectConfig = readJson(projectConfigPath);
  check(
    `${distRoot} urlCheck is enabled`,
    projectConfig.setting?.urlCheck === true,
    `${projectConfigPath} setting.urlCheck must be true.`,
  );

  check(
    `${distRoot} retired WeChat icon asset is absent`,
    !exists(`${distRoot}/static/icons/wechat-login.png`),
    'Generated package must not contain static/icons/wechat-login.png.',
  );

  const distTextFiles = listFiles(distRoot, ['.wxml', '.js', '.json']);
  checkNoPattern(
    `${distRoot} has no media autoplay`,
    distTextFiles,
    /\bautoplay\b/i,
    'Generated package must not contain autoplay.',
  );
  checkNoPattern(
    `${distRoot} has no wechat-login references`,
    distTextFiles,
    /wechat-login\.png/i,
    'Generated package must not reference the retired icon.',
  );
  checkNoPattern(
    `${distRoot} has no arbitrary web-view mode`,
    distTextFiles.filter((file) => file.includes(`${path.sep}pkg-tools${path.sep}webview${path.sep}`)),
    /<web-view\b|web-view 模式|options\.url|externalUrl/,
    'Generated webview page must not expose arbitrary external URL rendering.',
  );
  checkNoPattern(
    `${distRoot} visible sharing copy avoids platform-brand packaging`,
    distTextFiles.filter((file) => (
      file.includes(`${path.sep}pkg-card${path.sep}actor-card${path.sep}`)
      || file.includes(`${path.sep}pkg-card${path.sep}card-list${path.sep}`)
      || file.includes(`${path.sep}pkg-card${path.sep}ai-profile-card-detail${path.sep}`)
      || file.includes(`${path.sep}utils${path.sep}share-artifact.js`)
      || file.includes(`${path.sep}utils${path.sep}actor-card.js`)
    )),
    /WECHAT|微信对话|微信分享面板|调起微信|朋友圈|转发朋友圈/i,
    'Generated visible copy should use neutral sharing terminology.',
  );
  checkNoPattern(
    `${distRoot} has no invite-to-unlock inducement copy`,
    distTextFiles,
    /再邀请\s*\$\{?[^，。]*?(?:解锁|升到|后可)|邀请[^，。]*?(?:解锁|升级|裂变)/,
    'Generated package should not contain invite-to-unlock/upgrade inducement copy.',
  );
}

const failed = checks.filter((item) => !item.pass);

for (const item of checks) {
  const prefix = item.pass ? 'PASS' : 'FAIL';
  console.log(`${prefix} ${item.name}`);
  if (!item.pass) {
    console.log(`  ${item.detail}`);
  }
}

if (failed.length > 0) {
  console.error(`\n${failed.length} miniapp review compliance check(s) failed.`);
  process.exit(1);
}

console.log('\nAll miniapp review compliance checks passed.');
