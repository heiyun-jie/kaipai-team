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

const userStoreSource = read('kaipai-frontend/src/stores/user.ts');
const mineSource = read('kaipai-frontend/src/pages/mine/index.vue');
const navigationSource = read('kaipai-frontend/src/utils/navigation.ts');

check(
  'user store has global storage hydration helper',
  /function ensureStorageHydrated\(\): void/.test(userStoreSource) &&
    /let storageHydrated = false;/.test(userStoreSource) &&
    /storageHydrated = true;/.test(userStoreSource),
  'stores/user.ts must expose one global storage hydration path instead of requiring every page to call initFromStorage first.',
);

check(
  'user store logged-in computed hydrates before reading token',
  /const isLoggedIn = computed\(\(\) => \{\s*ensureStorageHydrated\(\);\s*return !!token\.value;\s*\}\);/s.test(userStoreSource),
  'isLoggedIn must hydrate from kp_token before returning false.',
);

check(
  'user store exposes hydrated current session state',
  /const currentUser = computed\(\(\) => \{\s*ensureStorageHydrated\(\);\s*return userInfo\.value;\s*\}\);/s.test(userStoreSource) &&
    /const hasStoredSession = computed\(\(\) => \{\s*ensureStorageHydrated\(\);\s*return !!token\.value;\s*\}\);/s.test(userStoreSource),
  'Store should expose currentUser and hasStoredSession as the canonical page-facing session state.',
);

check(
  'bootstrap session reuses global storage hydration',
  /async function bootstrapSession\(\): Promise<UserInfo \| null> \{\s*ensureStorageHydrated\(\);/s.test(userStoreSource) &&
    !/async function bootstrapSession\(\): Promise<UserInfo \| null> \{\s*initFromStorage\(\);/s.test(userStoreSource),
  'bootstrapSession() must use the global hydration helper, not a page-triggered local init path.',
);

check(
  'mine page consumes global session state',
  /const isVisitor = computed\(\(\) => !userStore\.hasStoredSession\);/.test(mineSource) &&
    /const currentUser = computed\(\(\) => userStore\.currentUser\);/.test(mineSource) &&
    /userStore\.currentUser/.test(mineSource),
  'pages/mine/index.vue should consume userStore.hasStoredSession/currentUser instead of only reading unhydrated isLoggedIn/userInfo.',
);

check(
  'mine page account header falls back to stored phone before visitor copy',
  /const displayName = computed\(\(\) => \{\s*if \(isVisitor\.value\) return '未登录';\s*return currentUser\.value\?\.nickname \|\| formatPhone\(currentUser\.value\?\.phone \|\| ''\) \|\| '演员用户';\s*\}\);/s.test(mineSource),
  'Logged-in mine header must render nickname, masked phone, or user id from global user state before showing visitor copy.',
);

check(
  'mine page gates actions with global session state',
  /function openAccountCapability\(url: string\): void \{\s*if \(isVisitor\.value\) \{\s*goLogin\(\);/s.test(mineSource),
  'Mine actions should use global session state for login gating.',
);

check(
  'navigation session guard uses user store',
  !/import \{ getToken, getUserInfo \} from '@\/utils\/auth';/.test(navigationSource) &&
    /const userStore = useUserStore\(\);/.test(navigationSource) &&
    /userStore\.ensureStorageHydrated\(\);/.test(navigationSource) &&
    /userStore\.currentUser/.test(navigationSource),
  'utils/navigation.ts should not keep a second storage-only login gate beside the global store.',
);

for (const distRoot of ['kaipai-frontend/dist/build/mp-weixin', 'kaipai-frontend/dist/dev/mp-weixin']) {
  const mineJsPath = `${distRoot}/pages/mine/index.js`;
  if (!exists(mineJsPath)) {
    check(`${distRoot} generated mine bundle exists`, false, 'Run npm run build:mp-weixin before final verification.');
    continue;
  }
  const mineJs = read(mineJsPath);
  check(
    `${distRoot} mine bundle uses global session state`,
    mineJs.includes('.currentUser') && mineJs.includes('.hasStoredSession') && mineJs.includes('演员用户'),
    'Generated mine JS should include the global session-state based header fallback.',
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
  console.error(`\n${failed.length} global session state check(s) failed.`);
  process.exit(1);
}

console.log('\nAll miniapp global session state checks passed.');
