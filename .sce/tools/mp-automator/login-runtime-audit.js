const automator = require('miniprogram-automator');
const childProcess = require('child_process');

const projectPath = 'D:\\XM\\kaipai-team\\kaipai-frontend\\dist\\dev\\mp-weixin';
const cliPath = 'D:\\AP\\微信web开发者工具\\cli.bat';
const autoPort = Number(process.env.MP_AUTO_PORT || 19425);
let activeMiniProgram = null;

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function withTimeout(promise, label, ms = 15000) {
  return Promise.race([
    promise,
    new Promise((_, reject) => setTimeout(() => reject(new Error(`${label} timed out after ${ms}ms`)), ms)),
  ]);
}

async function connectWithRetry(wsEndpoint) {
  let lastError = null;
  for (let attempt = 1; attempt <= 12; attempt += 1) {
    try {
      return await automator.connect({ wsEndpoint });
    } catch (error) {
      lastError = error;
      await wait(1000);
    }
  }
  throw lastError;
}

async function main() {
  const records = [];
  let miniProgram = null;
  console.log('[audit] enabling wechat automator');
  const cliOutput = childProcess.execFileSync('cmd.exe', [
    '/c',
    cliPath,
    'auto',
    '--project',
    projectPath,
    '--auto-port',
    String(autoPort),
    '--trust-project',
    '--lang',
    'zh',
  ], { encoding: 'utf8' });
  process.stdout.write(cliOutput);

  const portMatch = cliOutput.match(/127\.0\.0\.1:(\d+)/);
  const resolvedPort = portMatch ? Number(portMatch[1]) : autoPort;

  await wait(3000);
  console.log(`[audit] connecting ws://127.0.0.1:${resolvedPort}`);
  miniProgram = await withTimeout(connectWithRetry(`ws://127.0.0.1:${resolvedPort}`), 'connectWithRetry', 30000);
  activeMiniProgram = miniProgram;
  console.log('[audit] connected');

  miniProgram.on('console', (record) => {
    records.push({ type: 'console', record });
  });
  miniProgram.on('exception', (record) => {
    records.push({ type: 'exception', record });
  });

  console.log('[audit] relaunch login page');
  const page = await withTimeout(miniProgram.reLaunch('/pages/login/index'), 'reLaunch login', 30000);
  await withTimeout(page.waitFor(1200), 'wait login', 5000);

  console.log('[audit] query inputs');
  const inputs = await withTimeout(page.$$('input'), 'query inputs', 10000);
  if (inputs.length < 2) {
    throw new Error(`登录页输入框数量异常：${inputs.length}`);
  }

  console.log('[audit] input phone and sms');
  await withTimeout(inputs[0].input('13782296737'), 'input phone', 10000);

  console.log('[audit] tap send sms');
  const sendSms = await withTimeout(page.$('.login-page__field-action'), 'query send sms', 10000);
  if (!sendSms) {
    throw new Error('验证码发送按钮未找到');
  }
  await withTimeout(sendSms.tap(), 'tap send sms', 10000);
  await withTimeout(page.waitFor(2500), 'wait send sms request', 8000);
  const sendSmsAfterTap = await withTimeout(sendSms.wxml(), 'read send sms wxml after tap', 10000);
  const pageDataAfterSendSms = await withTimeout(page.data(), 'read page data after send sms', 10000);
  const pageDataAfterSendSmsText = JSON.stringify(pageDataAfterSendSms);
  const countdownTextAfterSendSms = pageDataAfterSendSmsText.match(/"((?:[1-5]?\d|60)s)"/)?.[1] || '';

  await withTimeout(inputs[1].input('十大12三4567'), 'input sms', 10000);
  await withTimeout(page.waitFor(300), 'wait input', 5000);
  const phoneValue = await withTimeout(inputs[0].value(), 'read phone value', 10000);
  const smsValue = await withTimeout(inputs[1].value(), 'read sms value', 10000);

  console.log('[audit] query agreement');
  const agreement = await withTimeout(page.$('.login-page__agreement'), 'query agreement', 10000);
  if (!agreement) {
    throw new Error('协议点击区域未找到');
  }
  console.log('[audit] tap agreement');
  await withTimeout(agreement.tap(), 'tap agreement', 10000);
  await withTimeout(page.waitFor(300), 'wait agreement tap', 5000);
  const agreementAfterTap = await withTimeout(agreement.wxml(), 'read agreement wxml after tap', 10000);

  console.log('[audit] untap agreement');
  await withTimeout(agreement.tap(), 'untap agreement', 10000);
  await withTimeout(page.waitFor(300), 'wait agreement untap', 5000);

  console.log('[audit] query submit');
  const submit = await withTimeout(page.$('.login-page__submit'), 'query submit', 10000);
  if (!submit) {
    throw new Error('登录按钮未找到');
  }
  console.log('[audit] tap submit');
  await withTimeout(submit.tap(), 'tap submit', 10000);
  await withTimeout(page.waitFor(800), 'wait modal', 5000);
  const agreementAfterModal = await withTimeout(agreement.wxml(), 'read agreement wxml after modal', 10000);

  const currentPage = await withTimeout(miniProgram.currentPage(), 'current page', 10000);
  const result = {
    pagePath: currentPage && currentPage.path,
    inputCount: inputs.length,
    phoneValue,
    smsValue,
    sendSmsAfterTap,
    countdownTextAfterSendSms,
    agreementAfterTap,
    agreementAfterModal,
    records,
  };

  console.log(JSON.stringify(result, null, 2));

  if (!countdownTextAfterSendSms) {
    throw new Error(`验证码发送后未进入倒计时，pageDataAfterSendSms=${JSON.stringify(pageDataAfterSendSms)}`);
  }
  const badRecords = records.filter((item) => JSON.stringify(item).includes('ERR_CONNECTION_CLOSED'));
  if (badRecords.length > 0) {
    throw new Error(`微信运行态仍存在 ERR_CONNECTION_CLOSED：${JSON.stringify(badRecords)}`);
  }

  await withTimeout(miniProgram.close(), 'close miniProgram', 15000);
  miniProgram = null;
  activeMiniProgram = null;
}

main().catch(async (error) => {
  if (activeMiniProgram) {
    try {
      await withTimeout(activeMiniProgram.close(), 'close miniProgram after failure', 15000);
    } catch (closeError) {
      console.error(closeError && closeError.stack ? closeError.stack : closeError);
    }
  }
  console.error(error && error.stack ? error.stack : error);
  process.exit(1);
});
