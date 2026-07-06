import fs from 'node:fs';
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

const checks = [];

function check(name, pass, detail) {
  checks.push({ name, pass, detail });
}

const verifyServiceSource = read('kaipaile-server/src/main/java/com/kaipai/service/verify/impl/IdentityVerificationServiceImpl.java');
const verifyEntitySource = read('kaipaile-server/src/main/java/com/kaipai/model/verify/entity/IdentityVerification.java');
const verifyJavaSources = readTree('kaipaile-server/src/main/java/com/kaipai', (file) => file.endsWith('.java'));
const mineSource = read('kaipai-frontend/src/pages/mine/index.vue');

check(
  'verify status service has default response helper',
  /private IdentityVerificationStatusRespDTO buildDefaultStatusResp\(User user\)/.test(verifyServiceSource) &&
    /dto\.setStatus\(user == null \|\| user\.getRealAuthStatus\(\) == null \? 0 : user\.getRealAuthStatus\(\)\)/.test(verifyServiceSource),
  'GET /verify/status should be able to return user.realAuthStatus/default 0 without relying on identity_verification rows.',
);

check(
  'verify status service catches latest record query failure',
  /IdentityVerificationStatusRespDTO defaultResp = buildDefaultStatusResp\(user\);/.test(verifyServiceSource) &&
    /try\s*\{\s*latestRecord = selectLatestByUserId\(userId\);/s.test(verifyServiceSource) &&
    /catch \(RuntimeException error\)\s*\{\s*return defaultResp;\s*\}/s.test(verifyServiceSource),
  'currentStatus() must not return code=500 when the ancillary latest identity_verification lookup fails.',
);

check(
  'mine page applies account header before actor runtime sync',
  /function applyMineUserHeader\(user: UserInfo\): void/.test(mineSource) &&
    mineSource.indexOf('applyMineUserHeader(user);') !== -1 &&
    mineSource.indexOf('await userStore.syncActorRuntimeState();') !== -1 &&
    mineSource.indexOf('applyMineUserHeader(user);') < mineSource.indexOf('await userStore.syncActorRuntimeState();'),
  'Mine page should render the logged-in account header before syncing verify/invite/level runtime data.',
);

check(
  'mine page catches actor runtime sync failure locally',
  /try\s*\{\s*await userStore\.syncActorRuntimeState\(\);\s*\}\s*catch \(error\)\s*\{/s.test(mineSource) &&
    /analyticsError\.value = \(error as Error\)\.message \|\| '账号状态同步失败';/.test(mineSource),
  'Mine page should keep the account page visible and show a data-area error when actor runtime sync fails.',
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
