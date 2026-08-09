import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.cwd());
const checks = [];

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function exists(relativePath) {
  return fs.existsSync(path.join(root, relativePath));
}

function check(name, pass, detail) {
  checks.push({ name, pass, detail });
}

function latestMiniappRunId() {
  const marker = 'output/miniapp-e2e/00-189/LATEST_RUN.txt';
  if (!exists(marker)) {
    return '';
  }
  return read(marker).trim();
}

const loginSourcePath = 'kaipai-frontend/src/pages/login/index.vue';
const loginSource = read(loginSourcePath);
const mineSourcePath = 'kaipai-frontend/src/pages/mine/index.vue';
const mineSource = read(mineSourcePath);

check(
  'login source renders local back button',
  /class="login-page__back"/.test(loginSource) && /login-page__back-text/.test(loginSource) && />返回</.test(loginSource),
  'Add a visible local 返回 button to pages/login/index.vue.',
);

check(
  'login source aligns back button with capsule row',
  /class="login-page__topbar"/.test(loginSource) &&
    /<view class="login-page__topbar">[\s\S]*<KpCapsuleSpacer[\s\S]*class="login-page__back"[\s\S]*<\/view>/m.test(loginSource) &&
    /:style="backButtonStyle"/.test(loginSource) &&
    /getFloatingBackNavStyles/.test(loginSource) &&
    /position:\s*absolute;[\s\S]*top:\s*0;[\s\S]*left:\s*32rpx;/.test(loginSource),
  'Back button must share the topbar/capsule row instead of rendering below KpCapsuleSpacer.',
);

check(
  'login source implements back fallback to home',
  /function handleBack\(\): void/.test(loginSource) &&
    loginSource.includes('getCurrentPages()') &&
    loginSource.includes('uni.navigateBack') &&
    loginSource.includes("uni.reLaunch({ url: '/pages/home/index' })"),
  'handleBack() must navigateBack first and reLaunch /pages/home/index as fallback.',
);

check(
  'login source visible copy still avoids platform-brand packaging',
  !/微信登录|微信一键登录|微信授权|WECHAT|朋友圈|微信分享面板/.test(loginSource),
  'Login page must not reintroduce platform-brand login or share packaging copy.',
);

check(
  'mine source allows unauthenticated tab viewing',
  !mineSource.includes('ensureUserSessionReady') &&
    /const isVisitor = computed\(\(\) => !userStore\.hasStoredSession/.test(mineSource) &&
    /const currentUser = computed\(\(\) => userStore\.currentUser\)/.test(mineSource) &&
    /onShow\(async \(\) => \{\s*if \(isVisitor\.value\) return;/s.test(mineSource),
  'pages/mine/index must not redirect to login on tab entry; render visitor state and gate account actions only.',
);

check(
  'mine source renders current visitor account state',
  /class="mine-v2__profile-card"\s+@click="goEditProfile"/.test(mineSource) &&
    /if \(isVisitor\.value\) return '未登录用户';/.test(mineSource) &&
    /formatPhone\(currentUser\.value\?\.phone \|\| ''\)/.test(mineSource),
  'Current mine-v2 profile card must derive visitor, nickname, and masked-phone states from the global session.',
);

check(
  'mine source shows full mine-v2 content for visitors',
  /mine-v2__completeness-card/.test(mineSource) &&
    /mine-v2__stats-row/.test(mineSource) &&
    /mine-v2__section-group/.test(mineSource) &&
    /演员资料/.test(mineSource) &&
    /账户与服务/.test(mineSource),
  'Visitor mine page must keep completeness, stats, actor-profile, and account-service sections visible.',
);

check(
  'mine source gates all protected account entries before navigation',
  /function requireLoginForMineAction\(\): boolean \{\s*if \(isVisitor\.value\) \{\s*uni\.navigateTo\(\{ url: '\/pages\/login\/index' \}\);\s*return false;\s*\}\s*return true;\s*\}/s.test(mineSource) &&
    /function openAccountCapability\(url: string\): void \{\s*if \(!requireLoginForMineAction\(\)\) return;\s*uni\.navigateTo\(\{ url \}\);\s*\}/s.test(mineSource) &&
    /function goEditProfile\(\): void \{\s*openAccountCapability\('\/pages\/actor-profile\/edit'\);\s*\}/s.test(mineSource) &&
    mineSource.includes("openAccountCapability('/pages/actor-profile/edit?tab=experience')") &&
    mineSource.includes("openAccountCapability('/pages/actor-profile/edit?tab=intro')") &&
    mineSource.includes("openAccountCapability('/pkg-card/verify/index')"),
  'Profile card, completion CTA, profile rows, and verification must gate visitors before creating a protected page.',
);

check(
  'mine source uses one direct login navigation without protected-page races',
  !/uni\.navigateTo\(\{\s*url:\s*['"]\/(?:pages\/actor-profile\/edit|pkg-card\/verify\/index)/.test(mineSource) &&
    !/return\s+uni\.navigateTo\(/.test(mineSource) &&
    !/goLogin\(|reLaunch\(\{\s*url:\s*['"]\/pages\/login\/index/.test(mineSource),
  'Mine must navigate through openAccountCapability and use only navigateTo(/pages/login/index) for visitors.',
);

for (const distRoot of ['kaipai-frontend/dist/build/mp-weixin', 'kaipai-frontend/dist/dev/mp-weixin']) {
  const loginWxmlPath = `${distRoot}/pages/login/index.wxml`;
  const loginJsPath = `${distRoot}/pages/login/index.js`;
  if (!exists(loginWxmlPath) || !exists(loginJsPath)) {
    check(`${distRoot} generated login files exist`, false, 'Run npm run build:mp-weixin before final verification.');
    continue;
  }
  const loginWxml = read(loginWxmlPath);
  const loginJs = read(loginJsPath);
  check(
    `${distRoot} login WXML renders back button`,
    loginWxml.includes('login-page__back') && loginWxml.includes('login-page__back-text') && loginWxml.includes('返回'),
    'Generated login WXML must include the 返回 button.',
  );
  check(
    `${distRoot} login WXML keeps back button in capsule row`,
    loginWxml.includes('login-page__topbar') &&
      loginWxml.indexOf('login-page__topbar') < loginWxml.indexOf('login-page__back') &&
      loginWxml.indexOf('login-page__back') < loginWxml.indexOf('login-page__stage'),
    'Generated login WXML must render the 返回 button in the topbar before the stage content.',
  );
  check(
    `${distRoot} login bundle includes home fallback`,
    loginJs.includes('/pages/home/index') && loginJs.includes('navigateBack'),
    'Generated login JS must include navigateBack and /pages/home/index fallback.',
  );

  const mineWxmlPath = `${distRoot}/pages/mine/index.wxml`;
  const mineJsPath = `${distRoot}/pages/mine/index.js`;
  if (!exists(mineWxmlPath) || !exists(mineJsPath)) {
    check(`${distRoot} generated mine files exist`, false, 'Run npm run build:mp-weixin before final verification.');
    continue;
  }
  const mineWxml = read(mineWxmlPath);
  const mineJs = read(mineJsPath);
  check(
    `${distRoot} mine WXML renders current mine-v2 profile card`,
    mineWxml.includes('mine-v2__profile-card') &&
      mineWxml.includes('mine-v2__completeness-card') &&
      mineWxml.includes('mine-v2__stats-row'),
    'Generated mine WXML must include the current profile, completeness, and stats blocks.',
  );
  check(
    `${distRoot} mine WXML keeps full current visitor content available`,
    mineWxml.includes('演员资料') &&
      mineWxml.includes('账户与服务') &&
      mineWxml.includes('mine-v2__group-card') &&
      mineWxml.includes('mine-v2__row'),
    'Generated mine WXML must keep actor-profile and account-service groups available to visitors.',
  );
  check(
    `${distRoot} mine bundle uses direct entry-level login gate`,
    !mineJs.includes('ensureUserSessionReady') &&
      mineJs.includes('hasStoredSession') &&
      mineJs.includes('currentUser') &&
      mineJs.includes('/pages/login/index') &&
      mineJs.includes('/pages/actor-profile/edit') &&
      mineJs.includes('/pkg-card/verify/index'),
    'Generated mine JS must consume global session state and gate account targets before protected-page navigation.',
  );
}

const runId = latestMiniappRunId();
check(
  '00-189 latest run marker exists',
  !!runId,
  'Run 00-189 E2E first or restore output/miniapp-e2e/00-189/LATEST_RUN.txt.',
);

if (runId) {
  const runRoot = `output/miniapp-e2e/00-189/${runId}`;
  const flowMatrixPath = `${runRoot}/flow-matrix.md`;
  const mineScreenshotPath = `${runRoot}/screenshots/11-pages-mine-index-default.png`;
  check(
    '00-189 flow matrix contains mine flow',
    exists(flowMatrixPath) && /\| mine \| 我的页与账号设置 \| `pages\/mine\/index`/.test(read(flowMatrixPath)),
    '00-189 flow-matrix.md must include the mine / pages/mine/index flow row.',
  );
  check(
    '00-189 mine screenshot exists',
    exists(mineScreenshotPath) && fs.statSync(path.join(root, mineScreenshotPath)).size > 0,
    '00-189 screenshots must include 11-pages-mine-index-default.png.',
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
  console.error(`\n${failed.length} login back / mine review supplement check(s) failed.`);
  process.exit(1);
}

console.log('\nAll login back / mine review supplement checks passed.');
