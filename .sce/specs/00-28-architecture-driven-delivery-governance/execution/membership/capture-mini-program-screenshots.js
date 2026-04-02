const fs = require('fs')
const path = require('path')
const Module = require('module')

const DEFAULT_WS_ENDPOINT = 'ws://127.0.0.1:9421'
const DEFAULT_BASE_URL = 'http://101.43.57.62/api'
const DEFAULT_PHONE = '13800138000'
const DEFAULT_SMS_CODE = ''
const DEFAULT_ACTOR_ID = '10000'
const DEFAULT_SCENE_KEY = 'general'
const DEFAULT_CAPTURE_LABEL = ''
const DEFAULT_CAPTURE_MANIFEST_NAME = 'mini-program-screenshot-capture.json'
const WORKSPACE_ROOT = path.resolve(__dirname, '..', '..', '..', '..', '..')

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

async function requestJson(url, options = {}) {
  const response = await fetch(url, options)
  const payload = await response.json()

  if (!response.ok || payload.code !== 200) {
    throw new Error(payload.message || `request failed: ${url}`)
  }

  return payload.data
}

async function createSession(baseUrl, phone, smsCode) {
  const freshCode = await requestJson(`${baseUrl}/auth/sendCode`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone }),
  })

  const effectiveCode = freshCode || smsCode
  const loginData = await requestJson(`${baseUrl}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, code: effectiveCode }),
  })

  const userMe = await requestJson(`${baseUrl}/user/me`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${loginData.token}`,
    },
  })

  return {
    smsCode: effectiveCode,
    token: loginData.token,
    user: {
      id: userMe.userId,
      phone: userMe.phone || phone,
      role: userMe.userType,
      status: userMe.status ?? 1,
      registeredAt: userMe.registeredAt,
      nickname: userMe.nickName,
      avatar: userMe.avatarUrl,
      realAuthStatus: userMe.realAuthStatus ?? 0,
      isCertified: userMe.isCertified ?? (userMe.realAuthStatus ?? 0) === 2,
      realName: userMe.realName,
      idCardMasked: userMe.idCardMasked,
      verifyRejectReason: userMe.verifyRejectReason,
      profileCompletion: userMe.profileCompletion,
      inviteCode: userMe.inviteCode,
      invitedByUserId: userMe.invitedByUserId,
      validInviteCount: userMe.validInviteCount,
      totalInviteCount: userMe.totalInviteCount,
      pendingInviteCount: userMe.pendingInviteCount,
      flaggedInviteCount: userMe.flaggedInviteCount,
      membershipTier: userMe.membershipTier,
    },
  }
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
      await userStore.syncActorRuntimeState()

      return {
        token: wx.getStorageSync('kp_token'),
        user: JSON.parse(wx.getStorageSync('kp_user')),
      }
    }
  `)()
  return await miniProgram.evaluate(injectSessionFunction)
}

async function ensureSession(miniProgram, baseUrl, phone, smsCode) {
  const session = await createSession(baseUrl, phone, smsCode)
  await injectSession(miniProgram, session)
  await sleep(1000)

  return {
    session,
    currentPage: await miniProgram.currentPage(),
  }
}

async function capturePage(miniProgram, item, screenshotDir) {
  const page = await miniProgram.reLaunch(item.path)
  await page.waitFor(item.waitForMs || 5000)

  const currentPage = await miniProgram.currentPage()
  const screenshotPath = path.join(screenshotDir, item.fileName)
  await miniProgram.screenshot({ path: screenshotPath })

  return {
    ...item,
    actualPath: currentPage.path,
    actualQuery: currentPage.query,
    screenshotPath,
  }
}

function toFilePrefix(label) {
  return String(label || '')
    .trim()
    .replace(/[^a-zA-Z0-9-_]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function buildTargetPaths(actorId, sceneKey, personalization, captureLabel) {
  const artifactMap = Object.fromEntries((personalization.artifacts || []).map(item => [item.type, item]))
  const filePrefix = toFilePrefix(captureLabel)
  const withPrefix = fileName => (filePrefix ? `${filePrefix}-${fileName}` : fileName)

  return [
    {
      name: 'membership',
      fileName: withPrefix('membership-index.png'),
      path: '/pkg-card/membership/index',
      waitForMs: 4000,
    },
    {
      name: 'actor-card',
      fileName: withPrefix('actor-card-mini-program-card.png'),
      path: artifactMap.miniProgramCard?.path || `/pkg-card/actor-card/index?actorId=${actorId}&scene=${sceneKey}&shared=1&artifact=miniProgramCard`,
      waitForMs: 5000,
    },
    {
      name: 'actor-profile-detail',
      fileName: withPrefix('actor-profile-detail.png'),
      path: artifactMap.publicCardPage?.path || `/pages/actor-profile/detail?actorId=${actorId}&scene=${sceneKey}&shared=1`,
      waitForMs: 5000,
    },
    {
      name: 'invite-card',
      fileName: withPrefix('invite-card.png'),
      path: artifactMap.inviteCard?.path || `/pkg-card/invite/index?actorId=${actorId}&scene=${sceneKey}&artifact=inviteCard&shared=1`,
      waitForMs: 5000,
    },
    {
      name: 'fortune',
      fileName: withPrefix('fortune-general.png'),
      path: `/pkg-card/fortune/index?scene=${encodeURIComponent(sceneKey)}`,
      waitForMs: 5000,
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
  const smsCode = process.argv[6] || DEFAULT_SMS_CODE
  const actorId = process.argv[7] || DEFAULT_ACTOR_ID
  const sceneKey = process.argv[8] || DEFAULT_SCENE_KEY
  const captureLabel = process.argv[9] || DEFAULT_CAPTURE_LABEL
  const captureManifestName = process.argv[10] || DEFAULT_CAPTURE_MANIFEST_NAME

  const screenshotDir = path.join(sampleRoot, 'screenshots')
  const captureDir = path.join(sampleRoot, 'captures')

  fs.mkdirSync(screenshotDir, { recursive: true })
  fs.mkdirSync(captureDir, { recursive: true })

  const miniProgram = await automator.connect({ wsEndpoint })

  try {
    const beforeLoginPage = await miniProgram.currentPage()
    const { session, currentPage } = await ensureSession(miniProgram, baseUrl, phone, smsCode)
    const personalization = await requestJson(
      `${baseUrl}/card/personalization?actorId=${encodeURIComponent(actorId)}&scene=${encodeURIComponent(sceneKey)}&loadFortune=true`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${session.token}`,
        },
      },
    )
    const targets = buildTargetPaths(actorId, sceneKey, personalization, captureLabel)

    const captures = []
    for (const target of targets) {
      captures.push(await capturePage(miniProgram, target, screenshotDir))
    }

    const result = {
      generatedAt: new Date().toISOString(),
      wsEndpoint,
      baseUrl,
      phone,
      actorId,
      sceneKey,
      captureLabel: captureLabel || null,
      captureManifestName,
      automatorResolvedFrom: resolvedAutomator.resolvedFrom,
      beforeLoginPage: {
        path: beforeLoginPage.path,
        query: beforeLoginPage.query,
      },
      sessionPage: {
        path: currentPage.path,
        query: currentPage.query,
      },
      personalization: {
        themeId: personalization.theme?.themeId,
        themePrimary: personalization.theme?.primary,
        canApplyFortuneTheme: personalization.capability?.canApplyFortuneTheme,
        reasonCodes: personalization.capability?.reasonCodes || [],
        sharePreferences: personalization.profile?.sharePreferences || null,
        artifactPaths: Object.fromEntries(
          (personalization.artifacts || []).map(item => [item.type, item.path]),
        ),
      },
      captures,
    }

    fs.writeFileSync(
      path.join(captureDir, captureManifestName),
      JSON.stringify(result, null, 2),
      'utf8',
    )

    console.log(JSON.stringify(result, null, 2))
  } finally {
    miniProgram.disconnect()
  }
}

main().catch(error => {
  console.error(error)
  process.exit(1)
})
