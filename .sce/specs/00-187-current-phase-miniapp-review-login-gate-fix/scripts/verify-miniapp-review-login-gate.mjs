import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.cwd());

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function exists(relativePath) {
  return fs.existsSync(path.join(root, relativePath));
}

const checks = [];

function check(name, pass, detail) {
  checks.push({ name, pass, detail });
}

const loginSource = read('kaipai-frontend/src/pages/login/index.vue');
const authSource = read('kaipai-frontend/src/api/auth.ts');
const homeSource = read('kaipai-frontend/src/pages/home/index.vue');
const runtimeSource = read('kaipai-frontend/src/utils/runtime.ts');
const userStoreSource = read('kaipai-frontend/src/stores/user.ts');

check(
  'login page does not render official WeChat logo asset',
  !loginSource.includes('/static/icons/wechat-login.png') && !loginSource.includes('wechat-login.png'),
  'Remove the official-looking login icon from pages/login/index.vue.',
);

check(
  'login page visible copy avoids WeChat-login branding',
  !/微信登录|微信一键登录|微信授权/.test(loginSource + runtimeSource + authSource),
  'Use self-owned copy such as 手机号快捷登录 instead of 微信登录 wording.',
);

check(
  'login page exposes compliant quick phone authorization entry',
  /手机号快捷登录/.test(loginSource) &&
    /:?open-type="[^"]*getPhoneNumber/.test(loginSource) &&
    /@getphonenumber="handlePhoneQuickLogin"/.test(loginSource) &&
    /loginByPhoneQuickAuth/.test(loginSource) &&
    /loginByPhoneQuickAuth/.test(authSource) &&
    /\/api\/auth\/wechat-login/.test(authSource),
  'Login page must keep a self-owned 手机号快捷登录 button backed by getPhoneNumber and /api/auth/wechat-login.',
);

check(
  'quick phone authorization entry has no official-looking image node',
  !/login-page__wechat-icon|login-page__quick-login-icon|<image[^>]+wechat-login/i.test(loginSource),
  'The quick phone button must be text-only or self-owned UI, without official-looking logo assets.',
);

check(
  'quick phone auth code error copy is self-owned',
  /手机号授权结果缺少 code/.test(authSource + loginSource) && !/微信未返回手机号授权 code|微信授权结果缺少 code/.test(authSource + loginSource),
  'Missing-code messages should use 手机号授权 wording instead of 微信授权 wording.',
);

check(
  'login success navigation is not blocked by runtime sync',
  /function syncActorRuntimeStateAfterNavigation\(\): void/.test(loginSource) &&
    !/await userStore\.syncActorRuntimeState\(\);\s*navigateAfterLogin\(user\);/.test(loginSource) &&
    /navigateAfterLogin\(user\);\s*syncActorRuntimeStateAfterNavigation\(\);/.test(loginSource),
  'After token/user are saved, login page must navigate first and run actor runtime sync as a non-blocking follow-up.',
);

check(
  'login follow-up runtime sync cannot redirect back to login page',
  /syncActorRuntimeState\(\{ redirectOnUnauthorized: false \}\)/.test(loginSource) &&
    /syncActorRuntimeState\(options\?: ActorRuntimeSyncOptions\)/.test(userStoreSource) &&
    /syncVerificationStatus\(options\), syncInviteStats\(options\), syncLevelInfo\(options\)/.test(userStoreSource),
  'Post-login actor runtime sync may show a toast on failure, but ancillary 401 responses must not reLaunch pages/login/index after a successful login navigation.',
);

check(
  'home page does not import the auto-redirect session helper',
  !homeSource.includes('ensureUserSessionReady'),
  'Home must not force unauthenticated users to the login page on first view.',
);

check(
  'home page has an explicit login action for gated features',
  /goLogin|\/pages\/login\/index/.test(homeSource),
  'Visitor homepage should login only after an explicit gated action.',
);

for (const distRoot of ['kaipai-frontend/dist/build/mp-weixin', 'kaipai-frontend/dist/dev/mp-weixin']) {
  const loginWxml = `${distRoot}/pages/login/index.wxml`;
  const loginJs = `${distRoot}/pages/login/index.js`;
  const homeJs = `${distRoot}/pages/home/index.js`;

  if (!exists(loginWxml) || !exists(loginJs) || !exists(homeJs)) {
    check(`${distRoot} exists`, false, 'Run npm run build:mp-weixin before this verification.');
    continue;
  }

  const loginWxmlContent = read(loginWxml);
  const loginJsContent = read(loginJs);
  const homeJsContent = read(homeJs);

  check(
    `${distRoot} login WXML has no quick-login image node`,
    !/login-page__wechat-icon|wechat-login|<image[^>]+login-page__quick-login-icon/.test(loginWxmlContent),
    'Generated login WXML must not render the official-looking login image.',
  );

  check(
    `${distRoot} login WXML exposes compliant quick phone authorization entry`,
    /login-page__phone-quick/.test(loginWxmlContent) &&
      /bindgetphonenumber/.test(loginWxmlContent) &&
      /手机号快捷登录/.test(loginJsContent) &&
      /getPhoneNumber/.test(loginJsContent),
    'Generated login page must contain the phone quick button, bindgetphonenumber, 手机号快捷登录, and getPhoneNumber.',
  );

  check(
    `${distRoot} home bundle does not force login during hydrate`,
    !homeJsContent.includes('ensureUserSessionReady'),
    'Generated home bundle should not force login on first view.',
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
  console.error(`\n${failed.length} review gate check(s) failed.`);
  process.exit(1);
}

console.log('\nAll miniapp review login gate checks passed.');
