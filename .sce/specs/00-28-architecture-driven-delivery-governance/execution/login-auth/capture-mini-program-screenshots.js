const fs = require('fs')
const path = require('path')
const Module = require('module')
const crypto = require('crypto')
const { spawnSync } = require('child_process')

const DEFAULT_WS_ENDPOINT = 'ws://127.0.0.1:9421'
const DEFAULT_BASE_URL = 'http://101.43.57.62/api'
const DEFAULT_PHONE = '13800138000'
const DEFAULT_CAPTURE_MANIFEST_NAME = 'mini-program-screenshot-capture.json'
const AUTOMATOR_SCREENSHOT_TIMEOUT_MS = 15000
const STEP_TIMEOUT_MS = 30000
const WORKSPACE_ROOT = path.resolve(__dirname, '..', '..', '..', '..', '..')
const WINDOW_CAPTURE_SCRIPT = path.resolve(__dirname, '..', 'recruit', 'capture-wechatdevtools-window.ps1')

function resolveModuleFromNodeModules(moduleName) {
  const nodeModulesDirs = [
    path.join(__dirname, 'node_modules'),
    path.join(WORKSPACE_ROOT, 'kaipai-frontend', 'node_modules'),
    path.join(WORKSPACE_ROOT, 'tmp', 'automator-probe', 'node_modules'),
  ]

  for (const nodeModulesDir of nodeModulesDirs) {
    const packageJsonPath = path.join(nodeModulesDir, moduleName, 'package.json')
    if (!fs.existsSync(packageJsonPath)) {
      continue
    }
    const candidateRequire = Module.createRequire(packageJsonPath)
    return {
      resolvedFrom: packageJsonPath,
      module: candidateRequire(moduleName),
    }
  }

  throw new Error(`Cannot resolve module ${moduleName} from ${nodeModulesDirs.join(', ')}`)
}

const resolvedAutomator = resolveModuleFromNodeModules('miniprogram-automator')
const automator = resolvedAutomator.module

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function withTimeout(label, promise, timeoutMs = STEP_TIMEOUT_MS) {
  let timer = null
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error(`${label} timeout after ${timeoutMs}ms`)), timeoutMs)
      }),
    ])
  } finally {
    if (timer) {
      clearTimeout(timer)
    }
  }
}

function appendProgress(captureDir, event, data = {}) {
  const entry = {
    at: new Date().toISOString(),
    event,
    ...data,
  }
  const progressPath = path.join(captureDir, 'mini-program-capture-progress.log')
  fs.appendFileSync(progressPath, `${JSON.stringify(entry)}\n`, 'utf8')
  console.log(JSON.stringify(entry))
}

function hashFile(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex')
}

function writePageDataSnapshot(captureDir, itemName, pageData) {
  const fileName = `page-data-${itemName}.json`
  const pageDataPath = path.join(captureDir, fileName)
  fs.writeFileSync(pageDataPath, JSON.stringify(pageData, null, 2), 'utf8')
  return pageDataPath
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options)
  const payload = await response.json()
  if (!response.ok || payload.code !== 200) {
    throw new Error(payload.message || `request failed: ${options.method || 'GET'} ${url}`)
  }
  return payload.data
}

function normalizeUserInfo(payload, fallbackPhone = '') {
  const normalizedRealAuthStatus = payload.realAuthStatus ?? 0
  return {
    id: payload.userId,
    phone: payload.phone || fallbackPhone,
    role: payload.userType,
    status: payload.status ?? 1,
    registeredAt: payload.registeredAt,
    nickname: payload.nickName,
    avatar: payload.avatarUrl,
    realAuthStatus: normalizedRealAuthStatus,
    isCertified: payload.isCertified ?? normalizedRealAuthStatus === 2,
    realName: payload.realName,
    idCardMasked: payload.idCardMasked,
    verifyRejectReason: payload.verifyRejectReason,
    profileCompletion: payload.profileCompletion,
    inviteCode: payload.inviteCode,
    invitedByUserId: payload.invitedByUserId,
    validInviteCount: payload.validInviteCount,
    totalInviteCount: payload.totalInviteCount,
    pendingInviteCount: payload.pendingInviteCount,
    flaggedInviteCount: payload.flaggedInviteCount,
    membershipTier: payload.membershipTier,
  }
}

async function createSession(baseUrl, phone) {
  const smsCode = await requestJson(`${baseUrl}/auth/sendCode`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone }),
  })

  const loginData = await requestJson(`${baseUrl}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, code: String(smsCode) }),
  })

  const userMe = await requestJson(`${baseUrl}/user/me`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${loginData.token}`,
    },
  })

  return {
    token: loginData.token,
    user: normalizeUserInfo(userMe, phone),
  }
}

async function fetchInviteCode(baseUrl, token) {
  const inviteInfo = await requestJson(`${baseUrl}/invite/code`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
  return String(inviteInfo.inviteCode || '').trim()
}

async function injectSession(miniProgram, session) {
  const sessionLiteral = JSON.stringify(session)
  const injectSessionFunction = new Function(`
    return async () => {
      const nextSession = ${sessionLiteral}
      const app = getApp()
      const userStore = app.$vm.$pinia._s.get('user')

      wx.setStorageSync('kp_token', nextSession.token)
      wx.setStorageSync('kp_user', JSON.stringify(nextSession.user))

      userStore.setUserData(nextSession.user, nextSession.token)
      if (nextSession.user.role === 1) {
        await userStore.syncActorRuntimeState()
      }

      return {
        token: wx.getStorageSync('kp_token'),
        user: JSON.parse(wx.getStorageSync('kp_user')),
      }
    }
  `)()

  return await miniProgram.evaluate(injectSessionFunction)
}

async function clearSession(miniProgram) {
  const clearSessionFunction = new Function(`
    return async () => {
      wx.removeStorageSync('kp_token')
      wx.removeStorageSync('kp_user')
      const app = getApp()
      const userStore = app.$vm.$pinia._s.get('user')
      userStore.logout()
      return {
        token: wx.getStorageSync('kp_token') || '',
        user: wx.getStorageSync('kp_user') || '',
      }
    }
  `)()

  return await miniProgram.evaluate(clearSessionFunction)
}

function captureWechatDevtoolsWindow(screenshotPath) {
  const completed = spawnSync(
    'powershell',
    [
      '-ExecutionPolicy',
      'Bypass',
      '-File',
      WINDOW_CAPTURE_SCRIPT,
      '-OutputPath',
      screenshotPath,
    ],
    {
      cwd: __dirname,
      encoding: 'utf8',
      timeout: STEP_TIMEOUT_MS,
    },
  )

  if (completed.error) {
    throw completed.error
  }
  if (completed.status !== 0) {
    throw new Error(`wechatdevtools window capture failed: ${completed.stderr || completed.stdout}`)
  }

  return JSON.parse((completed.stdout || '').trim())
}

async function capturePage(miniProgram, item, screenshotDir, captureDir) {
  appendProgress(captureDir, 'target-start', { name: item.name, path: item.path, requireSession: item.requireSession })

  const page = await withTimeout(`reLaunch-${item.name}`, miniProgram.reLaunch(item.path))
  appendProgress(captureDir, 'target-relaunch-ok', { name: item.name })

  await withTimeout(`waitFor-${item.name}`, page.waitFor(item.waitForMs || 5000))
  appendProgress(captureDir, 'target-wait-ok', { name: item.name })

  const currentPage = await withTimeout(`currentPage-${item.name}`, miniProgram.currentPage())
  const pageData = await withTimeout(`pageData-${item.name}`, currentPage.data())
  const pageDataPath = writePageDataSnapshot(captureDir, item.name, pageData)
  appendProgress(captureDir, 'target-page-data-ok', {
    name: item.name,
    pageDataPath,
    pageDataKeys: Object.keys(pageData).slice(0, 16),
  })

  const screenshotPath = path.join(screenshotDir, item.fileName)
  let screenshotMethod = 'automator'
  let screenshotDiagnostic = null

  try {
    await withTimeout(
      `automator-screenshot-${item.name}`,
      miniProgram.screenshot({ path: screenshotPath }),
      AUTOMATOR_SCREENSHOT_TIMEOUT_MS,
    )
    appendProgress(captureDir, 'target-screenshot-automator-ok', { name: item.name, screenshotPath })
  } catch (error) {
    screenshotMethod = 'wechatdevtools-window-fallback'
    screenshotDiagnostic = {
      automatorError: error.message,
      windowCapture: captureWechatDevtoolsWindow(screenshotPath),
    }
    appendProgress(captureDir, 'target-screenshot-fallback-ok', {
      name: item.name,
      screenshotPath,
      automatorError: error.message,
      windowCapture: screenshotDiagnostic.windowCapture,
    })
  }

  return {
    ...item,
    actualPath: currentPage.path,
    actualQuery: currentPage.query,
    pageDataPath,
    pageDataKeyCount: Object.keys(pageData).length,
    pageDataKeysSample: Object.keys(pageData).slice(0, 20),
    screenshotPath,
    screenshotSha256: hashFile(screenshotPath),
    screenshotMethod,
    screenshotDiagnostic,
  }
}

async function connectMiniProgram(wsEndpoint, captureDir, targetName) {
  appendProgress(captureDir, 'connect-start', { wsEndpoint, targetName: targetName || null })
  const miniProgram = await withTimeout('automator-connect', automator.connect({ wsEndpoint }))
  appendProgress(captureDir, 'connect-ok', {
    wsEndpoint,
    targetName: targetName || null,
    automatorResolvedFrom: resolvedAutomator.resolvedFrom,
  })
  return miniProgram
}

function disconnectMiniProgram(miniProgram, captureDir, targetName) {
  appendProgress(captureDir, 'disconnect', { targetName: targetName || null })
  miniProgram.disconnect()
}

async function captureTargetWithFreshConnection({
  wsEndpoint,
  captureDir,
  session,
  target,
  screenshotDir,
}) {
  const miniProgram = await connectMiniProgram(wsEndpoint, captureDir, target.name)
  try {
    if (target.requireSession) {
      await withTimeout(`injectSession-${target.name}`, injectSession(miniProgram, session))
      appendProgress(captureDir, 'target-session-injected', {
        name: target.name,
        userId: session.user.id,
        userRole: session.user.role,
      })
      await sleep(1000)
    } else {
      await withTimeout(`clearSession-${target.name}`, clearSession(miniProgram))
      appendProgress(captureDir, 'target-session-cleared', { name: target.name })
      await sleep(1000)
    }
    return await capturePage(miniProgram, target, screenshotDir, captureDir)
  } finally {
    disconnectMiniProgram(miniProgram, captureDir, target.name)
  }
}

function buildTargets(inviteCode) {
  const loginPath = inviteCode
    ? `/pages/login/index?inviteCode=${encodeURIComponent(inviteCode)}`
    : '/pages/login/index'

  return [
    {
      requireSession: false,
      name: 'login-page-invite',
      fileName: 'login-page-invite.png',
      path: loginPath,
      waitForMs: 5000,
    },
    {
      requireSession: true,
      name: 'mine-page-actor',
      fileName: 'mine-page-actor.png',
      path: '/pages/mine/index',
      waitForMs: 6000,
    },
    {
      requireSession: true,
      name: 'membership-page',
      fileName: 'membership-page.png',
      path: '/pkg-card/membership/index',
      waitForMs: 6000,
    },
    {
      requireSession: true,
      name: 'invite-page',
      fileName: 'invite-page.png',
      path: '/pkg-card/invite/index',
      waitForMs: 6000,
    },
  ]
}

async function main() {
  const sampleRoot = process.argv[2]
  if (!sampleRoot) {
    throw new Error('sampleRoot is required')
  }

  const wsEndpoint = process.argv[3] || DEFAULT_WS_ENDPOINT
  const baseUrl = process.argv[4] || DEFAULT_BASE_URL
  const phone = process.argv[5] || DEFAULT_PHONE
  const actorUserId = String(process.argv[6] || '')
  const sourceSampleId = String(process.argv[7] || '')
  const captureManifestName = process.argv[8] || DEFAULT_CAPTURE_MANIFEST_NAME

  if (!actorUserId) {
    throw new Error('actorUserId is required')
  }

  const screenshotDir = path.join(sampleRoot, 'screenshots')
  const captureDir = path.join(sampleRoot, 'captures')
  fs.mkdirSync(screenshotDir, { recursive: true })
  fs.mkdirSync(captureDir, { recursive: true })

  const session = await createSession(baseUrl, phone)
  const inviteCode = await fetchInviteCode(baseUrl, session.token)
  const targets = buildTargets(inviteCode)
  const captures = []

  for (const target of targets) {
    captures.push(await captureTargetWithFreshConnection({
      wsEndpoint,
      captureDir,
      session,
      target,
      screenshotDir,
    }))
  }

  const result = {
    generatedAt: new Date().toISOString(),
    wsEndpoint,
    baseUrl,
    phone,
    actorUserId,
    inviteCode,
    sourceSampleId: sourceSampleId || null,
    captureManifestName,
    automatorResolvedFrom: resolvedAutomator.resolvedFrom,
    screenshotStrategy: 'automator-first-with-wechatdevtools-window-fallback-per-target-connection',
    targets: targets.map(item => ({
      name: item.name,
      requireSession: item.requireSession,
      path: item.path,
    })),
    visualReview: {
      uniqueScreenshotHashCount: new Set(captures.map(item => item.screenshotSha256)).size,
      uniqueActualPathCount: new Set(captures.map(item => item.actualPath)).size,
    },
    captures,
  }

  result.visualReview.visualDidNotRefresh = (
    result.visualReview.uniqueScreenshotHashCount === 1 &&
    result.visualReview.uniqueActualPathCount > 1
  )

  fs.writeFileSync(
    path.join(captureDir, captureManifestName),
    JSON.stringify(result, null, 2),
    'utf8',
  )
  appendProgress(captureDir, 'manifest-written', {
    manifestPath: path.join(captureDir, captureManifestName),
    captureCount: captures.length,
    fallbackCount: captures.filter(item => item.screenshotMethod !== 'automator').length,
    visualDidNotRefresh: result.visualReview.visualDidNotRefresh,
  })

  console.log(JSON.stringify(result, null, 2))
}

main().catch(error => {
  console.error(error)
  process.exit(1)
})
