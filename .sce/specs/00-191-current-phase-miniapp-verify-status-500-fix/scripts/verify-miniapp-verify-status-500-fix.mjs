import fs from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';

const root = path.resolve(process.cwd());

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function readTree(relativePath, predicate = () => true) {
  const dir = path.join(root, relativePath);
  const parts = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const absolute = path.join(dir, entry.name);
    const childRelative = path.join(relativePath, entry.name).replaceAll('\\', '/');
    if (entry.isDirectory()) {
      parts.push(readTree(childRelative, predicate));
      continue;
    }
    if (predicate(childRelative)) {
      parts.push(fs.readFileSync(absolute, 'utf8'));
    }
  }
  return parts.join('\n');
}

async function verifyStaleUnauthorizedSessionOwnership(authModuleSource) {
  const requireFromFrontend = createRequire(path.join(root, 'kaipai-frontend/package.json'));
  const typescript = requireFromFrontend('typescript');
  const compiled = typescript.transpileModule(authModuleSource, {
    compilerOptions: {
      module: typescript.ModuleKind.CommonJS,
      target: typescript.ScriptTarget.ES2020,
    },
  }).outputText;
  const storage = new Map();
  const uni = {
    getStorageSync: (key) => storage.get(key),
    setStorageSync: (key, value) => storage.set(key, value),
    removeStorageSync: (key) => storage.delete(key),
  };
  const module = { exports: {} };
  const evaluate = new Function('exports', 'module', 'require', 'uni', compiled);
  evaluate(module.exports, module, requireFromFrontend, uni);
  const auth = module.exports;
  let memoryClearCount = 0;
  let redirectCount = 0;
  auth.registerSessionClearHandler(() => {
    memoryClearCount += 1;
  });
  auth.setToken('token-account-a');
  auth.setUserInfo({ id: 10001, role: 1 });
  const accountARequestSession = auth.captureAuthSession();

  let resolveOldUnauthorized;
  const oldUnauthorized = new Promise((resolve) => {
    resolveOldUnauthorized = resolve;
  }).then(() => {
    if (auth.clearSession(accountARequestSession)) {
      redirectCount += 1;
    }
  });

  auth.setToken('token-account-b');
  auth.setUserInfo({ id: 20002, role: 1 });
  resolveOldUnauthorized();
  await oldUnauthorized;

  const staleUnauthorizedPreservedNewSession =
    auth.getToken() === 'token-account-b' &&
    auth.getUserInfo()?.id === 20002 &&
    memoryClearCount === 0 &&
    redirectCount === 0;
  const accountBRequestSession = auth.captureAuthSession();
  if (auth.clearSession(accountBRequestSession)) {
    redirectCount += 1;
  }

  return (
    staleUnauthorizedPreservedNewSession &&
    auth.getToken() === null &&
    auth.getUserInfo() === null &&
    memoryClearCount === 1 &&
    redirectCount === 1
  );
}

const checks = [];

function check(name, pass, detail) {
  checks.push({ name, pass, detail });
}

const verifyServiceSource = read('kaipaile-server/src/main/java/com/kaipai/service/verify/impl/IdentityVerificationServiceImpl.java');
const globalExceptionHandlerSource = read('kaipaile-server/src/main/java/com/kaipai/common/exception/GlobalExceptionHandler.java');
const verifyEntitySource = read('kaipaile-server/src/main/java/com/kaipai/model/verify/entity/IdentityVerification.java');
const verifyDetailDtoSource = read('kaipaile-server/src/main/java/com/kaipai/model/verify/dto/IdentityVerificationDetailRespDTO.java');
const verifyJavaSources = readTree('kaipaile-server/src/main/java/com/kaipai', (file) => file.endsWith('.java'));
const mineSource = read('kaipai-frontend/src/pages/mine/index.vue');
const userStoreSource = read('kaipai-frontend/src/stores/user.ts');
const verifyPageSource = read('kaipai-frontend/src/pkg-card/verify/index.vue');
const requestSource = read('kaipai-frontend/src/utils/request.ts');
const authSource = read('kaipai-frontend/src/utils/auth.ts');
const adminVerifyTypesSource = read('kaipai-admin/src/types/verify.ts');
const adminVerifyBoardSource = read('kaipai-admin/src/views/verify/VerificationBoard.vue');
const staleUnauthorizedSessionOwnershipPass = await verifyStaleUnauthorizedSessionOwnership(authSource);

check(
  'verify status service has default response helper',
  /private IdentityVerificationStatusRespDTO buildDefaultStatusResp\(User user\)/.test(verifyServiceSource) &&
    /dto\.setStatus\(user == null \|\| user\.getRealAuthStatus\(\) == null \? 0 : user\.getRealAuthStatus\(\)\)/.test(verifyServiceSource),
  'GET /verify/status should be able to return user.realAuthStatus/default 0 without relying on identity_verification rows.',
);

check(
  'verify status service catches and records latest record query fallback',
  /IdentityVerificationStatusRespDTO defaultResp = buildDefaultStatusResp\(user\);/.test(verifyServiceSource) &&
    /try\s*\{\s*latestRecord = selectLatestByUserId\(userId\);/s.test(verifyServiceSource) &&
    /catch \(RuntimeException error\)\s*\{\s*log\.warn\([^;]+userId=.*fallbackStatus=.*error\);\s*return defaultResp;\s*\}/s.test(verifyServiceSource),
  'currentStatus() must retain its narrow fallback and leave a safe WARN record when the ancillary lookup fails.',
);

check(
  'global exception handler returns a non-sensitive correlation code',
  /"INTERNAL_ERROR_" \+ UUID\.randomUUID\(\)\.toString\(\)/.test(globalExceptionHandlerSource) &&
    /log\.error\("系统异常: errorCode=\{\}, method=\{\}, uri=\{\}"/.test(globalExceptionHandlerSource) &&
    /return R\.fail\(ResultCode\.FAILED\.getCode\(\), errorCode, ResultCode\.FAILED\.getMessage\(\)\);/.test(globalExceptionHandlerSource),
  'Unexpected exceptions must expose only a generated correlation code while logging the same code with method and URI.',
);

check(
  'mine page keeps identity based on current global session state',
  /const isVisitor = computed\(\(\) => !userStore\.hasStoredSession\);/.test(mineSource) &&
    /const currentUser = computed\(\(\) => userStore\.currentUser\);/.test(mineSource) &&
    /if \(isVisitor\.value\) return '未登录';/.test(mineSource) &&
    /catch \(error\)\s*\{\s*hubError\.value = \(error as Error\)\.message \|\| '资料摘要加载失败';\s*\}/s.test(mineSource) &&
    !/syncActorRuntimeState\(/.test(mineSource),
  'Mine must render its account header from hasStoredSession/currentUser and keep auxiliary failures local, not reintroduce the retired runtime-sync prerequisite.',
);

check(
  'verify page reads status once through the user store',
  !/import \{[^}]*getVerifyStatus[^}]*\} from '@\/api\/verify';/.test(verifyPageSource) &&
    !/getVerifyStatus\(/.test(verifyPageSource) &&
    (verifyPageSource.match(/userStore\.syncVerificationStatus\(/g) || []).length === 1 &&
    /userStore\.syncVerificationStatus\(\{ showLoading: false, showError: false \}\)/.test(verifyPageSource),
  'The verify page must not issue a duplicate direct GET after Store synchronization.',
);

check(
  'verify page owns loading error retry and correlation-code presentation',
  /const loading = ref\(false\);/.test(verifyPageSource) &&
    /const loadError = ref\(''\);/.test(verifyPageSource) &&
    /catch \(error\)\s*\{[\s\S]*loadError\.value = resolveErrorMessage\(error, '认证状态加载失败，请稍后重试'\);/s.test(verifyPageSource) &&
    /@click="hydratePage"/.test(verifyPageSource) &&
    /error instanceof ApiError && error\.errorCode \? `\$\{message\}（关联码 \$\{error\.errorCode\}）` : message/.test(verifyPageSource),
  'The onShow hydration must close errors locally and show a retryable, non-sensitive correlation code.',
);

check(
  'verify page preserves the preflight summary while status data is loading or failed',
  /<view class="verify-page__summary">/.test(verifyPageSource) &&
    !/<view v-if="!loading && !loadError" class="verify-page__summary">/.test(verifyPageSource),
  'Only the status/form region may change to loading or error; the preflight summary must remain visible.',
);

check(
  'verify submit directly applies the returned status without a second GET',
  /const submittedStatus = await submitVerify\(/.test(verifyPageSource) &&
    /\{ showError: false \},\s*\);/s.test(verifyPageSource) &&
    /const requestSession = userStore\.captureActorSession\(\);/.test(verifyPageSource) &&
    /if \(!ownsViewGeneration\(generation\) \|\| requestGeneration !== submitGeneration\) \{\s*return;\s*\}/s.test(verifyPageSource) &&
    /if \(!userStore\.applyVerificationStatus\(submittedStatus, requestSession\)\)\s*\{\s*invalidateStaleSessionView\(generation\);\s*return;\s*\}\s*status\.value = submittedStatus;/s.test(verifyPageSource) &&
    /catch \(error\) \{[\s\S]*if \(!userStore\.isActorSessionCurrent\(requestSession\)\) \{\s*invalidateStaleSessionView\(generation\);\s*return;\s*\}/s.test(verifyPageSource),
  'Submit must conditionally apply its response to the initiating actor session before updating page state, without re-fetching status.',
);

check(
  'user store returns and applies a single verification read',
  /function captureActorSession\(\): ActorSessionSnapshot \| null/.test(userStoreSource) &&
    /function isActorSessionCurrent\(session: ActorSessionSnapshot\): boolean/.test(userStoreSource) &&
    /function applyVerificationStatus\(\s*status: IdentityVerification,\s*expectedSession: ActorSessionSnapshot,\s*\): boolean/s.test(userStoreSource) &&
    /async function syncVerificationStatus\(options\?: ActorRuntimeSyncOptions\): Promise<IdentityVerification \| null>/.test(userStoreSource) &&
    /const requestSession = captureActorSession\(\);\s*if \(!requestSession\) \{\s*return null;\s*\}/s.test(userStoreSource) &&
    /if \(!applyVerificationStatus\(status, requestSession\)\) \{\s*return null;\s*\}\s*return status;/s.test(userStoreSource) &&
    (userStoreSource.match(/catch \(error\) \{\s*if \(!isActorSessionCurrent\(requestSession\)\) \{\s*return null;\s*\}\s*throw error;\s*\}/gs) || []).length >= 2 &&
    /return null;/.test(userStoreSource),
  'Store callers must reuse one status response, reject stale cross-session writes, and distinguish a skipped actor sync from a successful response.',
);

check(
  'verify page separates profile completion failures from verification status',
  /ensureUserSessionReady\(UserRole\.Actor\)/.test(verifyPageSource) &&
    /status\.value = nextStatus;[\s\S]*statusReady\.value = true;[\s\S]*shouldLoadProfileCompletion = true;/.test(verifyPageSource) &&
    /async function hydrateProfileCompletion\([\s\S]*\): Promise<void> \{[\s\S]*const levelInfo = await userStore\.syncLevelInfo\(\{ showLoading: false, showError: false \}\);[\s\S]*if \(!levelInfo \|\| !userStore\.isActorSessionCurrent\(requestSession\)\) \{\s*invalidateStaleSessionView\(generation\);\s*return;\s*\}[\s\S]*profileCompletion\.value = levelInfo\.profileCompletion;[\s\S]*completionError\.value = resolveErrorMessage/s.test(verifyPageSource) &&
    /@click="retryProfileCompletion"/.test(verifyPageSource),
  'A level-info failure must keep the valid verification response visible and retry only profile completion.',
);

check(
  'level sync rejects stale cross-session responses',
  /async function syncLevelInfo\(options\?: ActorRuntimeSyncOptions\): Promise<UserLevelInfo \| null>/.test(userStoreSource) &&
    /const requestSession = captureActorSession\(\);\s*if \(!requestSession\) \{\s*return null;\s*\}[\s\S]*const levelInfo = await getLevelInfo\(options\);\s*if \(!isActorSessionCurrent\(requestSession\)\) \{\s*return null;\s*\}\s*serverLevelInfo\.value = levelInfo;/s.test(userStoreSource) &&
    /return levelInfo;/.test(userStoreSource),
  'Level/profile completion responses must not overwrite a different current account and must expose skipped or stale results as null.',
);

check(
  'session invalidation clears storage and Pinia memory',
  staleUnauthorizedSessionOwnershipPass &&
    /export interface AuthSessionSnapshot \{\s*token: string \| null;\s*revision: number;\s*\}/s.test(authSource) &&
    /export function captureAuthSession\(\): AuthSessionSnapshot/.test(authSource) &&
    /export function clearSession\(expectedSession\?: AuthSessionSnapshot\): boolean \{\s*if \(expectedSession && !isAuthSessionCurrent\(expectedSession\)\) \{\s*return false;\s*\}/s.test(authSource) &&
    /import \{ captureAuthSession, clearSession, type AuthSessionSnapshot \} from '\.\/auth';/.test(requestSource) &&
    /function onUnauthorized\(requestSession: AuthSessionSnapshot\): void \{\s*if \(!clearSession\(requestSession\)\) \{\s*return;\s*\}\s*uni\.reLaunch/s.test(requestSource) &&
    /const requestSession = captureAuthSession\(\);\s*const token = requestSession\.token;/s.test(requestSource) &&
    /response\.code === 401[\s\S]*onUnauthorized\(requestSession\);/s.test(requestSource) &&
    /registerSessionClearHandler\(clearMemorySession\);/.test(userStoreSource) &&
    /session\.revision === sessionRevision/.test(userStoreSource) &&
    /getToken\(\) === session\.token/.test(userStoreSource),
  'A 401 may invalidate Storage and Pinia only when it still belongs to the current request session; an old account response must not clear or redirect a newer account.',
);

check(
  'bootstrap response remains owned by its initiating session',
  /const requestToken = token\.value;\s*const requestRevision = sessionRevision;/s.test(userStoreSource) &&
    /bootstrapRequestToken === requestToken &&\s*bootstrapRequestRevision === requestRevision/s.test(userStoreSource) &&
    /if \(!isSessionRequestCurrent\(requestToken, requestRevision\)\) \{\s*return null;\s*\}\s*setUserData\(currentUser, requestToken\);/s.test(userStoreSource) &&
    /catch \(error\) \{\s*if \(!isSessionRequestCurrent\(requestToken, requestRevision\)\) \{\s*return null;\s*\}\s*logout\(\);/s.test(userStoreSource),
  'bootstrapSession must never combine a stale /api/user/me response with a newer token or log out a newer session.',
);

check(
  'verify page async callbacks are generation owned',
  /let viewGeneration = 0;\s*let completionGeneration = 0;\s*let submitGeneration = 0;/s.test(verifyPageSource) &&
    /function ownsViewGeneration\(generation: number\): boolean/.test(verifyPageSource) &&
    /const generation = \+\+viewGeneration;/.test(verifyPageSource) &&
    /const requestGeneration = \+\+completionGeneration;/.test(verifyPageSource) &&
    /const requestGeneration = \+\+submitGeneration;/.test(verifyPageSource) &&
    (verifyPageSource.match(/if \(!ownsViewGeneration\(generation\)\)/g) || []).length >= 3 &&
    /invalidateStaleSessionView\(generation\)/.test(verifyPageSource),
  'Old hydration, completion, and submit callbacks must silently exit instead of mutating a newer page generation.',
);

check(
  'verify status never exposes encrypted identity material',
  /dto\.setIdCardNo\(resolveMaskedIdCardNo\(record\.getIdCardNoMasked\(\)\)\);/.test(verifyServiceSource) &&
    /dto\.setIdCardNoMasked\(resolveMaskedIdCardNo\(record\.getIdCardNoMasked\(\)\)\);/.test(verifyServiceSource) &&
    /private String resolveMaskedIdCardNo\(String maskedIdCardNo\)/.test(verifyServiceSource) &&
    !/getIdCardNoMasked\(\) == null \? record\.getIdCardNoCipher\(\)/.test(verifyServiceSource) &&
    !/private String idCardNoCipher;/.test(verifyDetailDtoSource) &&
    !/idCardNoCipher/.test(adminVerifyTypesSource) &&
    !/maskText\(detail\.idCardNoCipher\)/.test(adminVerifyBoardSource),
  'Miniapp and admin DTOs must return only a validated masked ID value and never expose cipher or hash storage.',
);

check(
  'verify submit uses the canonical realname provider only',
  !/TencentIdCardVerificationClient|TencentIdCardVerificationResult|applyProviderVerification\(/.test(verifyServiceSource),
  'IdentityVerificationServiceImpl should not call the retired TencentIdCardVerificationClient after RealNameVerificationProvider has taken over the submit state machine.',
);

check(
  'verify backend has no retired provider column mapping',
  !/TencentIdCardVerificationClient|TencentIdCardVerificationProperties|TencentIdCardVerificationResult|private String verifyProvider;|private String providerDescription;|setVerifyProvider\(|setProviderDescription\(|getVerifyProvider\(|getProviderDescription\(/.test(verifyJavaSources) &&
    !/private String verifyProvider;|private String providerDescription;/.test(verifyEntitySource),
  'Verify backend should not keep retired TencentIdCardVerification classes or verify_provider/provider_description mappings after provider_code/provider_result_message became canonical.',
);

const failed = checks.filter((item) => !item.pass);

for (const item of checks) {
  const prefix = item.pass ? 'PASS' : 'FAIL';
  console.log(`${prefix} ${item.name}`);
  if (!item.pass) {
    console.log(`  ${item.detail}`);
  }
}

if (failed.length > 0) {
  console.error(`\n${failed.length} verify status 500 fix check(s) failed.`);
  process.exit(1);
}

console.log('\nAll miniapp verify status 500 fix checks passed.');
