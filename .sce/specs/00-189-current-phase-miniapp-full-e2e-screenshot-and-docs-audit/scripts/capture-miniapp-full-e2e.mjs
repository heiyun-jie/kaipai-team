import crypto from 'node:crypto';
import fs from 'node:fs';
import Module from 'node:module';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import zlib from 'node:zlib';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const specRoot = path.resolve(scriptDir, '..');
const workspaceRoot = path.resolve(scriptDir, '..', '..', '..', '..');
const frontendRoot = path.join(workspaceRoot, 'kaipai-frontend');
const projectPath = process.env.MP_PROJECT_PATH || path.join(frontendRoot, 'dist', 'dev', 'mp-weixin');
const cliPath = process.env.WECHAT_DEVTOOLS_CLI || 'D:\\AP\\微信web开发者工具\\cli.bat';
const autoPort = Number(process.env.MP_AUTO_PORT || 19425);
const runId = process.env.RUN_ID || readLatestRunId() || makeRunId();
const outputRoot = process.env.OUTPUT_ROOT || path.join(workspaceRoot, 'output', 'miniapp-e2e', '00-189');
const runRoot = process.env.RUN_ROOT || path.join(outputRoot, runId);
const screenshotDir = path.join(runRoot, 'screenshots');
const captureDir = path.join(runRoot, 'captures');
const progressPath = path.join(captureDir, 'miniapp-e2e-progress.log');
const manifestPath = path.join(captureDir, 'full-page-screenshot-manifest.json');
const flowMatrixPath = path.join(runRoot, 'flow-matrix.md');
const docAuditMatrixPath = path.join(runRoot, 'doc-audit-matrix.md');
const launchDiagnosticsPath = path.join(runRoot, 'automator-launch-diagnostics.json');
const appJsonPath = path.join(projectPath, 'app.json');
const windowCaptureScript = path.join(
  workspaceRoot,
  '.sce',
  'specs',
  '00-28-architecture-driven-delivery-governance',
  'execution',
  'recruit',
  'capture-wechatdevtools-window.ps1',
);
const stepTimeoutMs = Number(process.env.MP_STEP_TIMEOUT_MS || 30000);
const screenshotTimeoutMs = Number(process.env.MP_SCREENSHOT_TIMEOUT_MS || 15000);
const automatorEnableTimeoutMs = Number(process.env.MP_AUTOMATOR_ENABLE_TIMEOUT_MS || 180000);

const resolvedAutomator = resolveModuleFromNodeModules('miniprogram-automator');
const automator = resolvedAutomator.module.default?.connect ? resolvedAutomator.module.default : resolvedAutomator.module;

fs.mkdirSync(screenshotDir, { recursive: true });
fs.mkdirSync(captureDir, { recursive: true });
fs.mkdirSync(outputRoot, { recursive: true });
fs.writeFileSync(path.join(outputRoot, 'LATEST_RUN.txt'), `${runId}\n`, 'utf8');

const mockState = buildMockState();
const appManifest = JSON.parse(fs.readFileSync(appJsonPath, 'utf8'));
const runtimePages = collectRuntimePages(appManifest);
const targets = buildTargets(runtimePages);
const consoleRecords = [];

function readLatestRunId() {
  try {
    return fs.readFileSync(path.join(outputRoot, 'LATEST_RUN.txt'), 'utf8').trim();
  } catch {
    return '';
  }
}

function makeRunId() {
  const now = new Date();
  const pad = (value) => String(value).padStart(2, '0');
  return [
    now.getFullYear(),
    pad(now.getMonth() + 1),
    pad(now.getDate()),
    '-',
    pad(now.getHours()),
    pad(now.getMinutes()),
    pad(now.getSeconds()),
  ].join('');
}

function resolveModuleFromNodeModules(moduleName) {
  const nodeModulesDirs = [
    path.join(workspaceRoot, '.sce', 'tools', 'mp-automator', 'node_modules'),
    path.join(frontendRoot, 'node_modules'),
    path.join(workspaceRoot, 'tmp', 'automator-probe', 'node_modules'),
  ];

  for (const nodeModulesDir of nodeModulesDirs) {
    const packageJsonPath = path.join(nodeModulesDir, moduleName, 'package.json');
    if (!fs.existsSync(packageJsonPath)) {
      continue;
    }
    const candidateRequire = Module.createRequire(packageJsonPath);
    return {
      resolvedFrom: packageJsonPath,
      module: candidateRequire(moduleName),
    };
  }

  throw new Error(`Cannot resolve ${moduleName} from ${nodeModulesDirs.join(', ')}`);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function withTimeout(label, promise, timeoutMs = stepTimeoutMs) {
  let timer = null;
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error(`${label} timeout after ${timeoutMs}ms`)), timeoutMs);
      }),
    ]);
  } finally {
    if (timer) {
      clearTimeout(timer);
    }
  }
}

function appendProgress(event, data = {}) {
  const entry = {
    at: new Date().toISOString(),
    event,
    ...data,
  };
  fs.appendFileSync(progressPath, `${JSON.stringify(entry)}\n`, 'utf8');
  console.log(JSON.stringify(entry));
}

function hashFile(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

function inspectPngVisual(filePath) {
  const buffer = fs.readFileSync(filePath);
  const signature = buffer.subarray(0, 8).toString('hex');
  if (signature !== '89504e470d0a1a0a') {
    return { width: 0, height: 0, sampleColorCount: 0, unsupported: 'not-png' };
  }

  let offset = 8;
  let width = 0;
  let height = 0;
  let bitDepth = 0;
  let colorType = 0;
  const idatChunks = [];
  while (offset + 8 <= buffer.length) {
    const length = buffer.readUInt32BE(offset);
    const type = buffer.subarray(offset + 4, offset + 8).toString('ascii');
    const data = buffer.subarray(offset + 8, offset + 8 + length);
    offset += 12 + length;
    if (type === 'IHDR') {
      width = data.readUInt32BE(0);
      height = data.readUInt32BE(4);
      bitDepth = data[8];
      colorType = data[9];
    } else if (type === 'IDAT') {
      idatChunks.push(data);
    } else if (type === 'IEND') {
      break;
    }
  }

  const channelsByColorType = new Map([
    [0, 1],
    [2, 3],
    [4, 2],
    [6, 4],
  ]);
  const channels = channelsByColorType.get(colorType);
  if (!width || !height || bitDepth !== 8 || !channels || !idatChunks.length) {
    return { width, height, sampleColorCount: 0, unsupported: `bitDepth=${bitDepth};colorType=${colorType}` };
  }

  const inflated = zlib.inflateSync(Buffer.concat(idatChunks));
  const rowLength = width * channels;
  const rows = [];
  let inputOffset = 0;
  for (let y = 0; y < height; y += 1) {
    const filter = inflated[inputOffset];
    inputOffset += 1;
    const row = Buffer.from(inflated.subarray(inputOffset, inputOffset + rowLength));
    inputOffset += rowLength;
    const previous = rows[y - 1] || Buffer.alloc(rowLength);
    for (let x = 0; x < rowLength; x += 1) {
      const left = x >= channels ? row[x - channels] : 0;
      const up = previous[x] || 0;
      const upLeft = x >= channels ? previous[x - channels] || 0 : 0;
      let predictor = 0;
      if (filter === 1) predictor = left;
      else if (filter === 2) predictor = up;
      else if (filter === 3) predictor = Math.floor((left + up) / 2);
      else if (filter === 4) predictor = paethPredictor(left, up, upLeft);
      row[x] = (row[x] + predictor) & 0xff;
    }
    rows.push(row);
  }

  const colors = new Set();
  const stepX = Math.max(1, Math.floor(width / 16));
  const stepY = Math.max(1, Math.floor(height / 16));
  for (let y = 0; y < height; y += stepY) {
    const row = rows[y];
    for (let x = 0; x < width; x += stepX) {
      const i = x * channels;
      colors.add(Array.from(row.subarray(i, i + channels)).join(','));
      if (colors.size > 8) {
        return { width, height, sampleColorCount: colors.size, unsupported: '' };
      }
    }
  }
  return { width, height, sampleColorCount: colors.size, unsupported: '' };
}

function paethPredictor(left, up, upLeft) {
  const p = left + up - upLeft;
  const pa = Math.abs(p - left);
  const pb = Math.abs(p - up);
  const pc = Math.abs(p - upLeft);
  if (pa <= pb && pa <= pc) return left;
  if (pb <= pc) return up;
  return upLeft;
}

function isLikelyBlankScreenshot(filePath) {
  try {
    const visual = inspectPngVisual(filePath);
    return {
      ...visual,
      blank: !visual.unsupported && visual.sampleColorCount <= 3,
    };
  } catch (error) {
    return {
      width: 0,
      height: 0,
      sampleColorCount: 0,
      blank: false,
      unsupported: error.message,
    };
  }
}

function safeFileSegment(value) {
  return String(value || '')
    .replace(/^\//, '')
    .replace(/[?&=]+/g, '-')
    .replace(/[^A-Za-z0-9._-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

function safeStringify(value) {
  const seen = new WeakSet();
  return JSON.stringify(value, (key, item) => {
    if (typeof item === 'function') {
      return `[Function ${item.name || 'anonymous'}]`;
    }
    if (item && typeof item === 'object') {
      if (seen.has(item)) {
        return '[Circular]';
      }
      seen.add(item);
    }
    return item;
  }, 2);
}

function writeJson(filePath, value) {
  fs.writeFileSync(filePath, `${safeStringify(value)}\n`, 'utf8');
}

function cloneForManifest(value) {
  return JSON.parse(JSON.stringify(value));
}

function collectRuntimePages(manifest) {
  const pages = [];
  for (const pagePath of manifest.pages || []) {
    pages.push({
      packageName: 'main',
      pagePath,
      isTab: (manifest.tabBar?.list || []).some((item) => item.pagePath === pagePath),
    });
  }
  for (const subPackage of manifest.subPackages || []) {
    for (const pagePath of subPackage.pages || []) {
      pages.push({
        packageName: subPackage.root,
        pagePath: `${subPackage.root}/${pagePath}`,
        isTab: false,
      });
    }
  }
  return pages;
}

function routeFor(pagePath, query = '') {
  return `/${pagePath}${query ? `?${query}` : ''}`;
}

function buildTargets(pages) {
  const byPage = new Map(pages.map((item) => [item.pagePath, item]));
  const targetSpecs = [
    ['pages/home/index', '', 'guest', '游客首页，不应入场即强制授权', ['guest-home']],
    ['pages/login/index', '', 'guest', '登录页和手机号快捷登录入口', ['login']],
    ['pages/actor-profile/edit', '', 'actor', '演员档案编辑页', ['actor-profile']],
    ['pages/actor-profile/detail', 'shared=1&shareCardId=17201', 'guest', '公开演员详情页', ['public-detail']],
    ['pages/apply-confirm/index', 'roleId=8801', 'actor', '演员投递确认页', ['apply']],
    ['pages/apply-detail/index', 'id=7001', 'actor', '投递详情页', ['apply']],
    ['pages/apply-manage/index', 'roleId=8801', 'crew', '旧剧组投递管理保留页', ['legacy-crew']],
    ['pages/crew-profile/edit', '', 'crew', '旧剧组资料编辑保留页', ['legacy-crew']],
    ['pages/contacts/index', '', 'actor', '联系方式申请列表页', ['contacts']],
    ['pages/history/index', '', 'actor', '浏览历史页', ['history']],
    ['pages/mine/index', '', 'actor', '我的页与账号入口', ['mine']],
    ['pages/my-applies/index', '', 'actor', '我的投递列表页', ['apply']],
    ['pages/project/create', '', 'crew', '旧剧组项目创建保留页', ['legacy-crew']],
    ['pages/project/role-create', 'projectId=9901', 'crew', '旧剧组角色创建保留页', ['legacy-crew']],
    ['pages/role-detail/index', 'id=8801', 'actor', '角色详情页', ['apply']],
    ['pkg-card/actor-card/index', 'mode=preview&shareCardId=17201&artifact=miniProgramCard', 'actor', '分享卡预览页', ['share-card']],
    ['pkg-card/verify/index', '', 'actor', '实名认证页', ['verify']],
    ['pkg-card/card-list/index', 'scene=urban&step=1', 'actor', '创建分享页第一步', ['create-share']],
    ['pkg-card/ai-profile-card/index', '', 'actor', 'AI 分享图生成页', ['ai-share']],
    ['pkg-card/ai-profile-card-detail/index', 'shareCardId=17201&taskId=task-e2e-001', 'guest', 'AI 分享图公开详情页', ['ai-share']],
    ['pkg-card/portfolio/index', '', 'actor', '作品集和已创建分享页', ['portfolio']],
    ['pkg-card/style-detail/index', 'scene=urban', 'actor', '风格详情页', ['style-detail']],
    ['pkg-card/favorites/index', '', 'actor', '收藏页保留运行态', ['favorites']],
    ['pkg-card/invite/index', '', 'actor', '邀请记录页', ['invite']],
    ['pkg-card/capability/index', '', 'actor', '能力中心页', ['capability']],
    ['pkg-tools/webview/index', 'type=privacy', 'guest', '隐私政策本地内容页', ['agreements']],
    ['pkg-tools/video-player/index', 'type=guide', 'guest', '操作指南视频页，手动播放', ['video-guide']],
  ];

  const targets = targetSpecs.map(([pagePath, query, sessionName, purpose, flowIds], index) => {
    const pageMeta = byPage.get(pagePath);
    if (!pageMeta) {
      throw new Error(`Target page is not present in app.json: ${pagePath}`);
    }
    return buildTarget({
      index: index + 1,
      pageMeta,
      query,
      sessionName,
      purpose,
      flowIds,
      variant: 'default',
    });
  });

  const extraTargets = [
    {
      pagePath: 'pkg-card/actor-card/index',
      query: 'mode=preview&shareCardId=17201&artifact=poster',
      sessionName: 'actor',
      purpose: '分享海报预览变体',
      flowIds: ['share-card'],
      variant: 'poster',
    },
    {
      pagePath: 'pkg-card/card-list/index',
      query: 'scene=urban&step=2',
      sessionName: 'actor',
      purpose: '创建分享页第二步作品选择',
      flowIds: ['create-share'],
      variant: 'step-2',
    },
    {
      pagePath: 'pkg-card/card-list/index',
      query: 'scene=urban&step=3&mode=edit',
      sessionName: 'actor',
      purpose: '创建分享页第三步预览保存',
      flowIds: ['create-share'],
      variant: 'step-3',
    },
    ...['user', 'about', 'notice', 'preferences'].map((type) => ({
      pagePath: 'pkg-tools/webview/index',
      query: `type=${type}`,
      sessionName: type === 'notice' || type === 'preferences' ? 'actor' : 'guest',
      purpose: `工具页 ${type} 本地内容变体`,
      flowIds: ['agreements'],
      variant: type,
    })),
  ];

  extraTargets.forEach((item) => {
    const pageMeta = byPage.get(item.pagePath);
    if (!pageMeta) {
      throw new Error(`Extra target page is not present in app.json: ${item.pagePath}`);
    }
    targets.push(buildTarget({
      index: targets.length + 1,
      pageMeta,
      ...item,
    }));
  });

  return targets;
}

function buildTarget({ index, pageMeta, query, sessionName, purpose, flowIds, variant }) {
  const id = `${String(index).padStart(2, '0')}-${safeFileSegment(pageMeta.pagePath)}-${variant || sessionName}`;
  return {
    id,
    pagePath: pageMeta.pagePath,
    packageName: pageMeta.packageName,
    isTab: pageMeta.isTab,
    route: routeFor(pageMeta.pagePath, query),
    query: query || '',
    sessionName,
    mockApi: true,
    purpose,
    flowIds,
    variant: variant || 'default',
    screenshotFileName: `${id}.png`,
    pageDataFileName: `page-data-${id}.json`,
    waitForMs: waitForPageMs(pageMeta.pagePath),
  };
}

function waitForPageMs(pagePath) {
  if (pagePath === 'pages/home/index') return 12000;
  if (pagePath === 'pkg-card/ai-profile-card-detail/index') return 8000;
  return 5200;
}

function buildMockState() {
  const levelInfo = {
    level: 5,
    inviteCount: 8,
    nextLevelRequirement: null,
    isCertified: true,
    profileCompletion: 96,
    capabilityTier: 'pro',
    levelCapability: {
      maxScenes: 5,
      canCustomColor: true,
      canCustomLayout: true,
      aiQuotaPerMonth: 20,
      paidSkinFreePreview: true,
    },
    shareCapability: {
      canUseBasicCard: true,
      canUsePersonalizedTheme: true,
      canUseCustomMiniProgramCard: true,
      canUseCustomPoster: true,
      canUseCustomInviteCard: true,
      reasonCodes: [],
    },
  };
  const actorUser = {
    id: 90001,
    userId: 90001,
    phone: '13800138000',
    userType: 1,
    role: 1,
    status: 1,
    nickName: '复审演员',
    nickname: '复审演员',
    avatarUrl: '/static/logo.png',
    avatar: '/static/logo.png',
    realAuthStatus: 2,
    isCertified: true,
    realName: '复审演员',
    idCardMasked: '310***********0021',
    profileCompletion: 96,
    inviteCode: 'KP2026',
    validInviteCount: 8,
    totalInviteCount: 8,
    pendingInviteCount: 1,
    flaggedInviteCount: 0,
    capabilityTier: 'pro',
  };
  const crewUser = {
    id: 91001,
    userId: 91001,
    phone: '13900139000',
    userType: 2,
    role: 2,
    status: 1,
    nickName: '复审剧组',
    nickname: '复审剧组',
    avatarUrl: '/static/logo.png',
    avatar: '/static/logo.png',
  };
  const actor = {
    userId: 90001,
    name: '林夏',
    gender: 'female',
    age: 26,
    height: 168,
    weight: 48,
    city: '上海',
    avatar: '/static/logo.png',
    intro: '复审样本演员，具备都市短剧、品牌广告和古装试镜素材。',
    photos: ['/static/logo.png'],
    photoCategories: {
      portrait: ['/static/logo.png'],
      lifestyle: ['/static/logo.png'],
      production: ['/static/logo.png'],
    },
    videoUrl: '/static/videos/operation-guide.mp4',
    skillTypes: ['表演', '舞蹈', '台词'],
    languages: ['普通话', '英语'],
    workExperiences: [
      {
        id: 501,
        projectName: '都市短剧《夏夜回响》',
        roleName: '女主角',
        shootDate: '2026',
        photos: ['/static/logo.png'],
        description: '负责都市情感线主角表演，适合复审截图素材。',
      },
      {
        id: 502,
        projectName: '品牌广告《午后光影》',
        roleName: '模特演员',
        shootDate: '2025',
        photos: ['/static/logo.png'],
        description: '品牌广告平面与短视频拍摄经验。',
      },
    ],
    bodyType: '清爽自然',
    hairStyle: '黑色长发',
    resumePdfUrl: '/static/logo.png',
    resumePdfName: '林夏演员简历.pdf',
    resumePdfPageCount: 2,
    resumePdfPageImageUrls: ['/static/logo.png', '/static/logo.png'],
    contactPhone: '',
    hasContactPhone: false,
    realName: '林夏',
    isCertified: true,
    capabilitySummary: levelInfo,
  };
  const templates = [
    buildTemplate('classic', '经典', '适合常规演员资料分享', 'CLASSIC', 0),
    buildTemplate('urban', '都市', '适合现代短剧、广告和生活化角色', 'URBAN', 0),
    buildTemplate('costume', '古装', '适合古装、年代和传统气质角色', 'COSTUME', 1),
    buildTemplate('commercial', '商业', '适合品牌广告和平面展示', 'COMMERCIAL', 3),
    buildTemplate('artistic', '艺术', '适合质感影像和作者表达', 'ARTISTIC', 5),
  ];
  const cards = [
    buildCard(17200, 'classic', true),
    buildCard(17201, 'urban', false),
    buildCard(17202, 'costume', false),
  ];
  const theme = {
    tokenKey: 'urban-pro-base',
    primary: '#8c6f4f',
    accent: '#d4b896',
    background: '#f5f3ee',
    surface: '#fbfaf6',
    surfaceStrong: '#eadfce',
    textPrimary: '#231b15',
    textSecondary: '#6c7483',
    heroText: '#fffdf8',
    buttonStyle: 'glass',
    mood: 'modern',
    posterPreset: 'urban',
    cardPreset: 'urban',
  };
  const cardConfig = {
    profileUserId: 90001,
    shareCardId: 17201,
    templateSceneCode: 'urban',
    layoutVariant: 'compact',
    primaryColor: '#8c6f4f',
    accentColor: '#d4b896',
    backgroundColor: '#f5f3ee',
    highlightedExperiences: [501, 502],
    highlightedPhotos: ['/static/logo.png'],
    tagOrder: ['表演', '舞蹈', '普通话'],
  };
  const personalization = {
    templates,
    profile: {
      profileUserId: 90001,
      shareCardId: 17201,
      levelInfo,
      capabilityTier: 'pro',
      templateSceneCode: 'urban',
      template: templates[1],
      templateId: 'tpl-urban',
      customConfig: cardConfig,
      sharePreferences: {
        preferredArtifact: 'miniProgramCard',
      },
    },
    theme,
    capability: {
      canUseBasicCard: true,
      canUsePersonalizedTheme: true,
      canUseCustomMiniProgramCard: true,
      canUseCustomPoster: true,
      canUseCustomInviteCard: true,
      reasonCodes: [],
    },
    actorSnapshot: actor,
    artifacts: [
      {
        type: 'miniProgramCard',
        label: '小程序名片',
        title: '都市小程序名片',
        subtitle: '复审样本',
        coverImage: '/static/logo.png',
        path: '/pages/actor-profile/detail?shared=1&shareCardId=17201',
        shareImageUrl: '',
        locked: false,
        theme,
        capability: {
          canUseBasicCard: true,
          canUsePersonalizedTheme: true,
          canUseCustomMiniProgramCard: true,
          canUseCustomPoster: true,
          canUseCustomInviteCard: true,
          reasonCodes: [],
        },
      },
      {
        type: 'poster',
        label: '海报',
        title: '都市分享海报',
        subtitle: '复审样本',
        coverImage: '/static/logo.png',
        path: '/pages/actor-profile/detail?shared=1&shareCardId=17201',
        shareImageUrl: '',
        locked: false,
        theme,
        capability: {
          canUseBasicCard: true,
          canUsePersonalizedTheme: true,
          canUseCustomMiniProgramCard: true,
          canUseCustomPoster: true,
          canUseCustomInviteCard: true,
          reasonCodes: [],
        },
      },
    ],
  };
  const project = {
    id: 9901,
    crewId: 91001,
    title: '都市短剧《夏夜回响》',
    description: '复审样本项目，用于验证演员投递和旧剧组页面运行态。',
    location: '上海',
    status: 1,
    type: '都市短剧',
    shootingDate: '2026-08-18',
    roleCount: 1,
    coverImage: '/static/logo.png',
  };
  const crew = {
    userId: 91001,
    avatar: '/static/logo.png',
    crewName: '开拍了复审剧组',
    contactName: '制片老师',
    contactPhone: '13900139000',
    remark: '用于复审自动化截图的剧组样本。',
    location: '上海',
    crewType: '短剧剧组',
    teamScale: '20-50人',
    focusDirection: '都市短剧、品牌广告',
    representativeWorks: '夏夜回响',
    cooperationNeed: '寻找表演稳定的青年演员',
    officeAddress: '上海市徐汇区',
  };
  const role = {
    id: 8801,
    projectId: 9901,
    roleName: '青年女主角',
    gender: '女',
    minAge: 22,
    maxAge: 30,
    requirement: '自然生活化表演，台词清晰，有短剧拍摄经验优先。',
    fee: '800/天',
    deadline: '2026-08-01',
    status: 'recruiting',
    tags: ['都市', '短剧', '女主'],
    publishTime: '2026-07-01 10:00:00',
    coverImage: '/static/logo.png',
    project,
    crew,
  };
  const apply = {
    id: 7001,
    roleId: 8801,
    profileUserId: 90001,
    shareCardId: 17201,
    status: 1,
    remark: '复审样本投递备注。',
    applyTime: '2026-07-02 18:20:00',
    actorName: actor.name,
    actorAvatar: actor.avatar,
    actorPhone: actorUser.phone,
    roleName: role.roleName,
    projectName: project.title,
    actorProfile: actor,
    role,
  };
  const aiArtifact = {
    artifactId: 'artifact-e2e-001',
    taskId: 'task-e2e-001',
    status: 'success',
    templateSceneCode: 'urban',
    styleCode: 'urban_profile_full_card',
    providerCode: 'tencent-hunyuan',
    modelCode: 'e2e-review',
    shareCardId: 17201,
    sourceImageUrl: '/static/logo.png',
    generatedImageUrl: '/static/logo.png',
    theme: {
      backgroundColor: '#f5f3ee',
      surfaceColor: '#fbfaf6',
      surfaceStrongColor: '#eadfce',
      accentColor: '#8c6f4f',
      textColor: '#231b15',
      mutedTextColor: '#6c7483',
      borderColor: 'rgba(35, 27, 21, 0.12)',
    },
    createTime: '2026-07-02 18:00:00',
    lastUpdate: '2026-07-02 18:05:00',
  };
  return {
    actorUser,
    crewUser,
    actor,
    crew,
    levelInfo,
    templates,
    shareCards: {
      cards,
      templates,
    },
    cardConfig,
    personalization,
    project,
    role,
    apply,
    pageResult: {
      total: 1,
      list: [role],
    },
    applyPageResult: {
      total: 1,
      list: [apply],
    },
    inviteInfo: {
      inviteCode: 'KP2026',
      inviteLink: '/pages/login/index?inviteCode=KP2026',
      validInviteCount: 8,
      totalInviteCount: 8,
      pendingInviteCount: 1,
      flaggedInviteCount: 0,
    },
    inviteRecords: [
      {
        id: 1,
        inviteePhone: '137****8000',
        status: 'valid',
        registeredAt: '2026-07-01 12:00:00',
      },
    ],
    historyItems: [
      {
        profileUserId: 90001,
        shareCardId: 17201,
        templateSceneCode: 'urban',
        actorName: actor.name,
        actorAvatar: actor.avatar,
        templateName: '都市',
        intro: actor.intro,
        contactLabel: '联系需先申请授权',
        viewedAt: '2026-07-02T10:00:00',
      },
    ],
    contacts: [
      {
        requestId: 8101,
        shareCardId: 17201,
        templateSceneCode: 'urban',
        templateName: '都市',
        status: 'pending',
        holderUserId: 90001,
        ownerName: actor.name,
        ownerPhone: actorUser.phone,
        viewerUserId: 91001,
        viewerName: crew.crewName,
        viewerPhone: crew.contactPhone,
        requestedAt: '2026-07-02 16:00:00',
      },
    ],
    contactStatus: {
      shareCardId: 17201,
      status: 'none',
      templateSceneCode: 'urban',
      templateName: '都市',
      contactPhone: '',
    },
    aiTask: {
      taskId: 'task-e2e-001',
      status: 'success',
      templateSceneCode: 'urban',
      styleCode: 'urban_profile_full_card',
      providerCode: 'tencent-hunyuan',
      modelCode: 'e2e-review',
      shareCardId: 17201,
      sourceImageUrl: '/static/logo.png',
      generatedImageUrl: '/static/logo.png',
      createTime: '2026-07-02 18:00:00',
      lastUpdate: '2026-07-02 18:05:00',
    },
    aiArtifact,
    aiQuota: {
      userId: 90001,
      quotaType: 'resume_polish',
      totalQuota: 20,
      usedCount: 2,
      periodType: 'monthly',
      periodStart: '2026-07-01',
    },
  };
}

function buildTemplate(templateSceneCode, name, description, heroEyebrow, requiredInviteCount) {
  return {
    templateSceneCode,
    name,
    description,
    coverImage: '/static/logo.png',
    heroEyebrow,
    themeColors: {
      primary: '#8c6f4f',
      accent: '#d4b896',
      background: '#f5f3ee',
      text: '#231b15',
      heroText: '#fffdf8',
    },
    layoutVariant: 'compact',
    contentFocus: ['分享卡', 'AI 分享图'],
    tier: 'free',
    requiredLevel: 0,
    requiredInviteCount,
  };
}

function buildCard(cardId, templateSceneCode, defaultCard) {
  return {
    cardId,
    configId: cardId + 1000,
    profileUserId: 90001,
    templateId: cardId + 2000,
    templateSceneCode,
    layoutVariant: 'compact',
    primaryColor: '#8c6f4f',
    accentColor: '#d4b896',
    backgroundColor: '#f5f3ee',
    defaultCard,
    createTime: '2026-07-02 10:00:00',
    updateTime: '2026-07-02 11:00:00',
  };
}

function enableAutomator() {
  appendProgress('automator-enable-start', { cliPath, projectPath, autoPort });
  const completed = spawnSync('cmd.exe', [
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
  ], {
    cwd: workspaceRoot,
    encoding: 'utf8',
    timeout: automatorEnableTimeoutMs,
  });
  const output = `${completed.stdout || ''}${completed.stderr || ''}`;
  const autoPortMatch = output.match(/auto(?:mator)?[^\r\n]*127\.0\.0\.1:(\d+)/i);
  const resolvedPort = autoPortMatch ? Number(autoPortMatch[1]) : autoPort;
  const diagnostics = {
    cliPath,
    projectPath,
    requestedAutoPort: autoPort,
    resolvedPort,
    status: completed.status,
    signal: completed.signal,
    error: completed.error ? completed.error.message : null,
    output,
    acceptedAsReady: completed.status === 0 || /auto/i.test(output),
  };
  writeJson(launchDiagnosticsPath, diagnostics);
  appendProgress('automator-enable-result', {
    status: completed.status,
    resolvedPort,
    acceptedAsReady: diagnostics.acceptedAsReady,
  });
  if (!diagnostics.acceptedAsReady) {
    throw new Error(`wechat devtools auto failed: ${output}`);
  }
  return `ws://127.0.0.1:${resolvedPort}`;
}

async function connectWithRetry(wsEndpoint) {
  let lastError = null;
  for (let attempt = 1; attempt <= 15; attempt += 1) {
    try {
      appendProgress('automator-connect-attempt', { wsEndpoint, attempt });
      return await automator.connect({ wsEndpoint });
    } catch (error) {
      lastError = error;
      await sleep(1000);
    }
  }
  throw lastError;
}

async function installMockApi(miniProgram) {
  await withTimeout('install-mock-state', miniProgram.evaluate((state) => {
    globalThis.__KP_E2E_API_STATE = state;
    return {
      installed: true,
      keys: Object.keys(state),
    };
  }, mockState));

  await withTimeout('mock-wx-request', miniProgram.mockWxMethod('request', function mockRequest(options) {
    const state = globalThis.__KP_E2E_API_STATE || {};

    function normalizePath(url) {
      const fullUrl = String(url || '');
      const withoutHost = fullUrl.replace(/^https?:\/\/[^/]+/i, '');
      return withoutHost || fullUrl;
    }

    function parseQuery(url) {
      const queryString = String(url || '').split('?')[1] || '';
      const result = {};
      queryString.split('&').forEach((pair) => {
        if (!pair) return;
        const parts = pair.split('=');
        const key = decodeURIComponent(parts[0] || '');
        const value = decodeURIComponent(parts.slice(1).join('=') || '');
        if (key) result[key] = value;
      });
      return result;
    }

    function pageResult(list) {
      return {
        total: list.length,
        list,
      };
    }

    function pickCurrentUser(header) {
      const auth = String((header && (header.Authorization || header.authorization)) || '');
      return auth.includes('crew') ? state.crewUser : state.actorUser;
    }

    function resolveData(pathname, query, method, header) {
      if (pathname === '/api/auth/sendCode') return '123456';
      if (pathname === '/api/auth/login' || pathname === '/api/auth/register' || pathname === '/api/auth/wechat-login') {
        return { ...state.actorUser, token: 'mock-actor-token' };
      }
      if (pathname === '/api/user/me') return pickCurrentUser(header);
      if (pathname === '/api/verify/status') {
        return {
          status: 2,
          realName: '林夏',
          idCardNo: '310***********0021',
          rejectReason: '',
          submitTime: '2026-07-02 10:00:00',
          auditTime: '2026-07-02 11:00:00',
        };
      }
      if (pathname === '/api/referral/stats') return state.inviteInfo;
      if (pathname === '/api/referral/code') return state.inviteInfo;
      if (pathname === '/api/referral/records') return state.inviteRecords;
      if (pathname === '/api/level/info') return state.levelInfo;
      if (pathname === '/api/card/scene-templates') return state.templates;
      if (pathname === '/api/card/my-cards') return state.shareCards;
      if (pathname === '/api/card/config') return state.cardConfig;
      if (pathname === '/api/card/personalization') return state.personalization;
      if (pathname === '/api/actor/profile/mine') return state.actor;
      if (pathname.indexOf('/api/actor/') === 0) return state.actor;
      if (pathname === '/api/crew/mine') return state.crew;
      if (pathname.indexOf('/api/crew/') === 0) return state.crew;
      if (pathname === '/api/project/mine' || pathname === '/api/project/list') return pageResult([state.project]);
      if (pathname.indexOf('/api/project/') === 0) return state.project;
      if (pathname === '/api/role/search') return pageResult([state.role]);
      if (pathname.indexOf('/api/role/project/') === 0) return pageResult([state.role]);
      if (pathname.indexOf('/api/role/') === 0) return state.role;
      if (pathname === '/api/apply/mine') return state.applyPageResult;
      if (pathname.indexOf('/api/apply/role/') === 0) return state.applyPageResult;
      if (pathname.indexOf('/api/apply/') === 0) return state.apply;
      if (pathname === '/api/card/view-histories') {
        return method === 'POST' ? null : state.historyItems;
      }
      if (pathname === '/api/card/view-histories/clear') return null;
      if (pathname === '/api/card/contact-requests/status') return state.contactStatus;
      if (pathname === '/api/card/contact-requests/approved') return state.contacts;
      if (pathname === '/api/card/contact-requests/owned') return state.contacts;
      if (pathname === '/api/card/contact-requests') return {
        ...state.contactStatus,
        status: 'pending',
      };
      if (pathname.indexOf('/api/card/contact-requests/') === 0) return {
        ...state.contactStatus,
        status: pathname.endsWith('/approve') ? 'approved' : 'rejected',
      };
      if (pathname === '/api/ai/quota') return state.aiQuota;
      if (pathname === '/api/ai/profile-card/tasks') return [state.aiTask];
      if (pathname.indexOf('/api/ai/profile-card/tasks/') === 0) return state.aiTask;
      if (pathname === '/api/ai/profile-card/artifacts') return [state.aiArtifact];
      if (pathname.indexOf('/api/ai/profile-card/artifacts/') === 0) return state.aiArtifact;
      if (pathname.indexOf('/api/ai/profile-card/share-cards/') === 0 && pathname.endsWith('/artifact')) {
        return state.aiArtifact;
      }
      if (pathname === '/api/ai/resume-polish/history') return {
        total: 0,
        list: [],
      };
      if (pathname === '/api/ai/polish-resume') return {
        requestId: 'mock-ai-resume',
        patches: [],
      };
      return null;
    }

    const requestPath = normalizePath(options && options.url);
    const pathname = requestPath.split('?')[0];
    const query = parseQuery(requestPath);
    const method = String((options && options.method) || 'GET').toUpperCase();
    const data = resolveData(pathname, query, method, options && options.header);
    const response = {
      statusCode: 200,
      header: {},
      data: {
        code: 200,
        message: 'success',
        data,
      },
    };
    if (options && typeof options.success === 'function') options.success(response);
    if (options && typeof options.complete === 'function') options.complete(response);
    return {
      errMsg: 'request:ok',
    };
  }));
  appendProgress('mock-api-installed', { stateKeys: Object.keys(mockState).length });
}

async function injectSession(miniProgram, sessionName) {
  if (sessionName === 'guest') {
    await withTimeout('clear-session', miniProgram.evaluate(() => {
      wx.removeStorageSync('kp_token');
      wx.removeStorageSync('kp_user');
      const app = typeof getApp === 'function' ? getApp() : null;
      const store = app && app.$vm && app.$vm.$pinia && app.$vm.$pinia._s
        ? app.$vm.$pinia._s.get('user')
        : null;
      if (store && typeof store.logout === 'function') {
        store.logout();
      }
      return {
        token: wx.getStorageSync('kp_token') || '',
        user: wx.getStorageSync('kp_user') || '',
      };
    }));
    return {
      sessionName,
      tokenPresent: false,
      userRole: null,
    };
  }

  const user = sessionName === 'crew' ? mockState.crewUser : mockState.actorUser;
  const token = sessionName === 'crew' ? 'mock-crew-token' : 'mock-actor-token';
  return await withTimeout(`inject-session-${sessionName}`, miniProgram.evaluate((nextSession) => {
    wx.setStorageSync('kp_token', nextSession.token);
    wx.setStorageSync('kp_user', JSON.stringify(nextSession.user));
    const app = typeof getApp === 'function' ? getApp() : null;
    const store = app && app.$vm && app.$vm.$pinia && app.$vm.$pinia._s
      ? app.$vm.$pinia._s.get('user')
      : null;
    if (store && typeof store.setUserData === 'function') {
      store.setUserData(nextSession.user, nextSession.token);
    }
    return {
      tokenPresent: !!wx.getStorageSync('kp_token'),
      user: JSON.parse(wx.getStorageSync('kp_user')),
    };
  }, { token, user }));
}

async function routeToTarget(miniProgram, target) {
  if (target.isTab) {
    return await withTimeout(`switchTab-${target.id}`, miniProgram.switchTab(target.route));
  }
  return await withTimeout(`reLaunch-${target.id}`, miniProgram.reLaunch(target.route));
}

async function capturePage(miniProgram, target) {
  appendProgress('target-start', {
    id: target.id,
    route: target.route,
    sessionName: target.sessionName,
  });
  const recordStartIndex = consoleRecords.length;
  let capture = {
    ...target,
    status: 'failed',
    startedAt: new Date().toISOString(),
    finishedAt: '',
    actualPath: '',
    actualQuery: {},
    pageDataPath: '',
    pageDataKeyCount: 0,
    pageDataKeysSample: [],
    screenshotPath: '',
    screenshotSha256: '',
    screenshotMethod: '',
    screenshotDiagnostic: null,
    needsReconnect: false,
    consoleRecords: [],
    error: null,
  };

  try {
    const sessionResult = await injectSession(miniProgram, target.sessionName);
    appendProgress('target-session-ready', {
      id: target.id,
      sessionName: target.sessionName,
      tokenPresent: !!sessionResult.tokenPresent,
      userRole: sessionResult.user?.role || sessionResult.userRole || null,
    });

    await routeToTarget(miniProgram, target);
    appendProgress('target-route-ok', { id: target.id, route: target.route });
    await withTimeout(`waitFor-${target.id}`, sleep(target.waitForMs), target.waitForMs + 2000);

    const currentPage = await withTimeout(`currentPage-${target.id}`, miniProgram.currentPage());
    const pageData = await withTimeout(`pageData-${target.id}`, currentPage.data());
    const pageDataSnapshot = {
      target,
      actualPath: currentPage.path,
      actualQuery: currentPage.query,
      pageData,
    };
    const pageDataPath = path.join(captureDir, target.pageDataFileName);
    writeJson(pageDataPath, pageDataSnapshot);
    appendProgress('target-page-data-ok', {
      id: target.id,
      actualPath: currentPage.path,
      keys: Object.keys(pageData).slice(0, 16),
    });

    const screenshotPath = path.join(screenshotDir, target.screenshotFileName);
    let screenshotMethod = 'automator';
    let screenshotDiagnostic = null;
    try {
      await withTimeout(
        `screenshot-${target.id}`,
        miniProgram.screenshot({ path: screenshotPath }),
        screenshotTimeoutMs,
      );
      appendProgress('target-screenshot-ok', { id: target.id, screenshotPath });
    } catch (error) {
      capture = {
        ...capture,
        screenshotPath,
        screenshotMethod: 'automator-timeout',
        screenshotDiagnostic: {
          automatorError: error.message,
        },
        needsReconnect: true,
      };
      appendProgress('target-screenshot-timeout', {
        id: target.id,
        screenshotPath,
        automatorError: error.message,
      });
      throw error;
    }
    const visual = isLikelyBlankScreenshot(screenshotPath);
    if (visual.blank) {
      appendProgress('target-screenshot-blank-detected', {
        id: target.id,
        screenshotPath,
        visual,
      });
      capture = {
        ...capture,
        screenshotPath,
        screenshotMethod,
        screenshotDiagnostic: {
          ...screenshotDiagnostic,
          blankDetection: visual,
        },
        needsReconnect: true,
      };
      throw new Error(`blank screenshot detected for ${target.id}: ${safeStringify(visual)}`);
    }

    capture = {
      ...capture,
      status: currentPage.path === target.pagePath ? 'passed' : 'redirected',
      actualPath: currentPage.path,
      actualQuery: currentPage.query,
      pageDataPath,
      pageDataKeyCount: Object.keys(pageData).length,
      pageDataKeysSample: Object.keys(pageData).slice(0, 20),
      screenshotPath,
      screenshotSha256: hashFile(screenshotPath),
      screenshotMethod,
      screenshotDiagnostic,
    };
  } catch (error) {
    capture.error = {
      message: error.message,
      stack: error.stack,
    };
    appendProgress('target-failed', {
      id: target.id,
      message: error.message,
    });
  } finally {
    capture.finishedAt = new Date().toISOString();
    capture.consoleRecords = consoleRecords.slice(recordStartIndex);
  }

  return capture;
}

function captureWechatDevtoolsWindow(screenshotPath) {
  if (!fs.existsSync(windowCaptureScript)) {
    throw new Error(`window capture script missing: ${windowCaptureScript}`);
  }
  const completed = spawnSync('powershell', [
    '-ExecutionPolicy',
    'Bypass',
    '-File',
    windowCaptureScript,
    '-OutputPath',
    screenshotPath,
  ], {
    cwd: workspaceRoot,
    encoding: 'utf8',
    timeout: stepTimeoutMs,
  });
  if (completed.error) {
    throw completed.error;
  }
  if (completed.status !== 0) {
    throw new Error(`wechatdevtools window capture failed: ${completed.stderr || completed.stdout}`);
  }
  return JSON.parse((completed.stdout || '').trim());
}

async function runLoginInteractionCheck(miniProgram) {
  const result = {
    id: 'flow-login-button-response',
    status: 'failed',
    route: '/pages/login/index',
    screenshotPath: '',
    screenshotSha256: '',
    inputCount: 0,
    sendSmsFound: false,
    phoneQuickFound: false,
    pageDataKeys: [],
    error: null,
  };
  try {
    await injectSession(miniProgram, 'guest');
    const page = await withTimeout('login-flow-relaunch', miniProgram.reLaunch('/pages/login/index'));
    await withTimeout('login-flow-wait', sleep(1200), 4000);
    const inputs = await withTimeout('login-flow-inputs', page.$$('input'), 10000);
    result.inputCount = inputs.length;
    if (inputs[0]) {
      await withTimeout('login-flow-input-phone', inputs[0].input('13800138000'), 10000);
    }
    const sendSms = await withTimeout('login-flow-send-query', page.$('.login-page__field-action'), 10000);
    result.sendSmsFound = !!sendSms;
    if (sendSms) {
      await withTimeout('login-flow-send-tap', sendSms.tap(), 10000);
      await withTimeout('login-flow-send-wait', sleep(1200), 5000);
    }
    const phoneQuick = await withTimeout('login-flow-quick-query', page.$('.login-page__phone-quick'), 10000);
    result.phoneQuickFound = !!phoneQuick;
    const currentPage = await withTimeout('login-flow-current', miniProgram.currentPage());
    const pageData = await withTimeout('login-flow-data', currentPage.data());
    result.pageDataKeys = Object.keys(pageData).slice(0, 20);
    const screenshotPath = path.join(screenshotDir, 'flow-login-button-response.png');
    await withTimeout('login-flow-screenshot', miniProgram.screenshot({ path: screenshotPath }), screenshotTimeoutMs);
    result.screenshotPath = screenshotPath;
    result.screenshotSha256 = hashFile(screenshotPath);
    result.status = result.inputCount >= 2 && result.sendSmsFound ? 'passed' : 'failed';
  } catch (error) {
    result.error = {
      message: error.message,
      stack: error.stack,
    };
  }
  writeJson(path.join(captureDir, 'interaction-login-button-response.json'), result);
  appendProgress('interaction-login-button-response', {
    status: result.status,
    inputCount: result.inputCount,
    sendSmsFound: result.sendSmsFound,
  });
  return result;
}

function coverageFromCaptures(captures) {
  return runtimePages.map((page) => {
    const related = captures.filter((capture) => capture.pagePath === page.pagePath);
    return {
      ...page,
      targetCount: related.length,
      passedCount: related.filter((capture) => capture.status === 'passed').length,
      redirectedCount: related.filter((capture) => capture.status === 'redirected').length,
      failedCount: related.filter((capture) => capture.status === 'failed').length,
      screenshotCount: related.filter((capture) => !!capture.screenshotPath && fs.existsSync(capture.screenshotPath)).length,
      statuses: related.map((capture) => ({
        id: capture.id,
        status: capture.status,
        actualPath: capture.actualPath,
        screenshotPath: capture.screenshotPath,
        error: capture.error?.message || null,
      })),
    };
  });
}

function summarizeVisualCoverage(captures) {
  return {
    runtimePageCount: runtimePages.length,
    targetCount: targets.length,
    captureCount: captures.length,
    passedCount: captures.filter((item) => item.status === 'passed').length,
    redirectedCount: captures.filter((item) => item.status === 'redirected').length,
    failedCount: captures.filter((item) => item.status === 'failed').length,
    screenshotCount: captures.filter((item) => item.screenshotPath && fs.existsSync(item.screenshotPath)).length,
    uniqueScreenshotHashCount: new Set(captures.filter((item) => item.screenshotSha256).map((item) => item.screenshotSha256)).size,
    failedTargets: captures
      .filter((item) => item.status === 'failed')
      .map((item) => ({ id: item.id, route: item.route, error: item.error?.message || '' })),
  };
}

function buildFlowRows(captures, interactions) {
  const byFlow = new Map();
  for (const capture of captures) {
    for (const flowId of capture.flowIds || []) {
      if (!byFlow.has(flowId)) {
        byFlow.set(flowId, []);
      }
      byFlow.get(flowId).push(capture);
    }
  }

  const flowSpecs = [
    ['guest-home', '游客打开首页并浏览', 'pages/home/index', '游客态', '启动首页，确认不被立即要求手机号、头像、昵称授权', '停留首页，可浏览分享入口和指南入口'],
    ['login', '用户主动进入登录页', 'pages/login/index', '游客主动进入', '打开登录页，点击验证码发送入口', '登录页按钮有响应，手机号快捷登录文案不混淆官方'],
    ['actor-profile', '演员档案维护', 'pages/actor-profile/edit', '演员登录态', '进入档案编辑，读取头像、照片、经历、PDF、视频模块', '页面可渲染完整档案编辑结构'],
    ['verify', '实名认证', 'pkg-card/verify/index', '演员登录态', '进入实名页查看认证状态与提交表单', '展示实名状态，不泄露身份证原文'],
    ['create-share', '创建分享页三步', 'pkg-card/card-list/index', '演员登录态', '风格选择、作品选择、保存预览三个状态', '三步均可渲染，保存动作不在本轮自动提交'],
    ['style-detail', '风格详情', 'pkg-card/style-detail/index', '演员登录态', '查看风格状态、分享入口和说明', '风格详情可渲染且不出现诱导分享文案'],
    ['share-card', '分享卡和海报预览', 'pkg-card/actor-card/index', '演员登录态', '打开小程序卡片和海报两个预览变体', '公开分享路径可生成截图证据'],
    ['ai-share', 'AI 分享图生成与详情', 'pkg-card/ai-profile-card/index', '演员登录态 / 游客公开态', '进入 AI 生成页和 AI 公开详情页', '生成入口、详情页、PDF 简历区可渲染'],
    ['portfolio', '作品集/已创建分享', 'pkg-card/portfolio/index', '演员登录态', '查看作品集、已创建分享、AI 图记录', '作品集列表可渲染'],
    ['public-detail', '公开演员详情', 'pages/actor-profile/detail', '游客态', '通过 shareCardId 访问公开详情', '公开详情可浏览，联系申请有登录/授权边界'],
    ['history', '浏览历史', 'pages/history/index', '演员登录态', '查看浏览历史列表', '历史页可渲染并可回到分享详情'],
    ['contacts', '联系方式申请', 'pages/contacts/index', '演员登录态', '查看联系方式申请列表', '申请列表可渲染'],
    ['mine', '我的页与账号设置', 'pages/mine/index', '演员登录态', '查看我的页入口和退出/设置入口', '我的页可渲染'],
    ['agreements', '协议、隐私、关于、通知、偏好', 'pkg-tools/webview/index', '游客/演员态', '打开 webview 工具页多种本地 type', '本地内容页可渲染，未开放任意 URL'],
    ['video-guide', '操作指南视频', 'pkg-tools/video-player/index', '游客态', '打开指南视频页', '视频页为手动播放状态'],
    ['apply', '角色详情与投递链路', 'pages/role-detail/index', '演员登录态', '角色详情、投递确认、我的投递、投递详情', '投递相关页面可渲染，提交动作不在本轮自动提交'],
    ['legacy-crew', '旧剧组/投递保留页面', 'pages/project/create', '剧组登录态', '剧组资料、项目创建、角色创建、投递管理', '旧页面保留运行态截图，但不作为当前小程序主线扩展'],
    ['capability', '能力中心', 'pkg-card/capability/index', '演员登录态', '查看等级能力和产物状态', '能力状态使用中性文案'],
    ['invite', '邀请记录', 'pkg-card/invite/index', '演员登录态', '查看邀请记录与统计', '不出现“再邀请 X 人解锁”等诱导表述'],
    ['favorites', '收藏页', 'pkg-card/favorites/index', '演员登录态', '打开收藏页保留运行态', '页面可渲染或明确空状态'],
  ];

  return flowSpecs.map(([flowId, name, entry, precondition, steps, expected]) => {
    const related = byFlow.get(flowId) || [];
    const failed = related.filter((item) => item.status === 'failed');
    const redirected = related.filter((item) => item.status === 'redirected');
    const screenshots = related
      .filter((item) => item.screenshotPath)
      .map((item) => path.relative(runRoot, item.screenshotPath).replace(/\\/g, '/'));
    const interaction = flowId === 'login' ? interactions.find((item) => item.id === 'flow-login-button-response') : null;
    let status = related.length ? 'passed' : 'static-only';
    if (failed.length) status = 'failed';
    if (!failed.length && redirected.length) status = 'blocked';
    if (interaction && interaction.status !== 'passed') status = 'blocked';
    const issueParts = [];
    if (failed.length) issueParts.push(`${failed.length} 个截图目标失败`);
    if (redirected.length) issueParts.push(`${redirected.length} 个目标发生路由重定向`);
    if (interaction && interaction.status !== 'passed') issueParts.push('登录按钮响应未完全通过自动化断言');
    const mockAssisted = related.some((item) => item.mockApi);
    return {
      flowId,
      name,
      entry,
      precondition,
      steps,
      expected,
      evidence: screenshots.join('<br>') || '-',
      status,
      issue: issueParts.join('；') || (mockAssisted ? 'mock-api-assisted：线上短信不回传验证码，本轮使用 mock API 渲染登录态页面' : '-'),
    };
  });
}

function writeFlowMatrix(captures, interactions, summary) {
  const rows = buildFlowRows(captures, interactions);
  const lines = [
    '# 00-189 小程序业务流程 E2E 复核矩阵',
    '',
    `- 生成时间：${new Date().toISOString()}`,
    `- 运行目录：\`${runRoot}\``,
    `- 截图目标：${summary.targetCount}，运行态页面：${summary.runtimePageCount}，成功截图：${summary.screenshotCount}`,
    '- 说明：登录态页面使用 `mock-api-assisted` 方式渲染，原因是当前正式短信接口不回传验证码，DevTools storage 也没有可复用 token；真实提交动作未在本轮自动执行。',
    '',
    '| flowId | 流程 | 入口 | 前置条件 | 关键步骤 | 预期结果 | 状态 | 证据 | 问题/说明 |',
    '| --- | --- | --- | --- | --- | --- | --- | --- | --- |',
    ...rows.map((row) => [
      row.flowId,
      row.name,
      `\`${row.entry}\``,
      row.precondition,
      row.steps,
      row.expected,
      row.status,
      row.evidence,
      row.issue,
    ].map(escapeMarkdownCell).join(' | ')).map((line) => `| ${line} |`),
    '',
    '## 阻断与降级口径',
    '',
    '- 真实手机号快捷登录和短信验证码登录未做线上闭环提交：正式短信接口返回 `data: null`，无法自动拿验证码创建真实 token。',
    '- 所有登录态页面截图均保留 `mock-api-assisted` 标记，只用于页面结构、文案、路由和审核风险复核，不替代真实后端联调验收。',
    '- 旧剧组/投递页面仍按“代码保留运行态”截图；当前小程序复审主线仍以演员首页、登录、分享、作品集、协议设置为主。',
    '',
  ];
  fs.writeFileSync(flowMatrixPath, `${lines.join('\n')}\n`, 'utf8');
  return rows;
}

function escapeMarkdownCell(value) {
  return String(value ?? '')
    .replace(/\|/g, '\\|')
    .replace(/\r?\n/g, '<br>');
}

function writeDocAuditMatrix() {
  const docs = scanDocTargets();
  const lines = [
    '# 00-189 旧文档整理矩阵',
    '',
    `- 生成时间：${new Date().toISOString()}`,
    '- 整理原则：不大范围重写历史执行记录；历史 Spec 保留为证据，当前引用口径由 `00-189`、`00-188`、`00-187`、`00-27` 与产品主线文档承接。',
    '- 重点风险：旧剧组端、小程序旧首页强登录、旧 fortune/命理、旧 membership、任意 web-view、微信/朋友圈分享文案、自动播放视频。',
    '',
    '| docPath | topic | currentStatus | finding | action | ownerSpec |',
    '| --- | --- | --- | --- | --- | --- |',
    ...docs.map((row) => [
      `\`${row.docPath}\``,
      row.topic,
      row.currentStatus,
      row.finding,
      row.action,
      row.ownerSpec,
    ].map(escapeMarkdownCell).join(' | ')).map((line) => `| ${line} |`),
    '',
    '## 当前引用口径',
    '',
    '- 小程序复审主线：游客首页可浏览；登录页只在用户主动进入账号/登录能力时出现；手机号授权文案统一为“手机号快捷登录”。',
    '- 当前分享主线：创建分享页、分享卡/海报预览、AI 分享图、公开详情、作品集、历史、我的页。',
    '- 旧剧组端与投递管理：保留运行态截图和历史说明，不作为本轮复审主线扩展承诺。',
    '- 旧 fortune/命理、旧 membership、朋友圈/微信分享面板等历史描述：只可作为历史记录，不得作为当前运行态依据。',
    '',
  ];
  fs.writeFileSync(docAuditMatrixPath, `${lines.join('\n')}\n`, 'utf8');
  return docs;
}

function scanDocTargets() {
  const candidates = [
    path.join(workspaceRoot, 'docs'),
    path.join(frontendRoot, 'docs'),
    path.join(workspaceRoot, '.sce', 'specs', '00-27-mini-program-frontend-architecture'),
    path.join(workspaceRoot, '.sce', 'specs', '00-28-architecture-driven-delivery-governance'),
    path.join(workspaceRoot, '.sce', 'specs', '00-05-mini-program-package-governance'),
    ...fs.readdirSync(path.join(workspaceRoot, '.sce', 'specs'), { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .filter((entry) => /^05-/.test(entry.name) || /^00-1(4|7|8)\d/.test(entry.name) || /^00-18[789]/.test(entry.name))
      .map((entry) => path.join(workspaceRoot, '.sce', 'specs', entry.name)),
  ];
  const files = [];
  for (const candidate of candidates) {
    if (!fs.existsSync(candidate)) continue;
    const stat = fs.statSync(candidate);
    if (stat.isFile() && candidate.endsWith('.md')) {
      files.push(candidate);
    } else if (stat.isDirectory()) {
      walkMarkdown(candidate, files);
    }
  }

  const uniqueFiles = [...new Set(files)].sort((left, right) => left.localeCompare(right));
  return uniqueFiles.map((filePath) => classifyDoc(filePath));
}

function walkMarkdown(dir, files) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const filePath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (['node_modules', 'dist', 'build', 'output'].includes(entry.name)) continue;
      walkMarkdown(filePath, files);
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      files.push(filePath);
    }
  }
}

function classifyDoc(filePath) {
  const relative = path.relative(workspaceRoot, filePath).replace(/\\/g, '/');
  const content = fs.readFileSync(filePath, 'utf8');
  const staleKeywords = [
    'fortune',
    '命理',
    '朋友圈',
    '微信分享面板',
    'membership',
    '会员',
    'company-profile',
    'pages/company-profile',
    '剧组端',
    '自动播放',
    'autoplay',
  ];
  const currentKeywords = [
    '00-187',
    '00-188',
    '00-189',
    '演员卡',
    '分享卡',
    'AI 分享图',
    '作品集',
    '手机号快捷登录',
  ];
  const staleHits = staleKeywords.filter((keyword) => content.includes(keyword));
  const currentHits = currentKeywords.filter((keyword) => content.includes(keyword));
  let currentStatus = 'unknown';
  let action = 'verify-later';
  let ownerSpec = '00-189';
  let finding = '未发现明显小程序复审关键词，后续按需核对。';
  let topic = inferTopic(relative);

  if (relative.includes('/archive/') || /05-0(3|8|11)/.test(relative)) {
    currentStatus = 'historical';
    action = 'archive';
    ownerSpec = relative.includes('05-08') ? '00-149' : '00-189';
    finding = '历史方案或已退场能力，仅保留为历史证据。';
  } else if (relative.includes('00-187') || relative.includes('00-188') || relative.includes('00-189')) {
    currentStatus = 'current';
    action = 'keep';
    ownerSpec = relative.match(/00-\d+[^/]+/)?.[0] || '00-189';
    finding = '当前复审专项链路文档，可作为本轮执行依据。';
  } else if (relative.includes('00-27') || relative.includes('00-28') || relative.endsWith('docs/product-design.md')) {
    currentStatus = staleHits.length ? 'current-with-stale-fragments' : 'current';
    action = staleHits.length ? 'update' : 'keep';
    ownerSpec = relative.includes('00-27') ? '00-27' : relative.includes('00-28') ? '00-28' : '00-189';
    finding = staleHits.length
      ? `仍含旧口径关键词：${staleHits.slice(0, 6).join('、')}。需要以 00-189 矩阵校准当前引用。`
      : '当前总纲/产品文档可保留。';
  } else if (staleHits.length) {
    currentStatus = 'stale-review';
    action = 'update';
    ownerSpec = '00-189';
    finding = `命中旧口径关键词：${staleHits.slice(0, 6).join('、')}。不得直接作为当前复审依据。`;
  } else if (currentHits.length) {
    currentStatus = 'current-reference';
    action = 'keep';
    ownerSpec = '00-189';
    finding = `命中当前主线关键词：${currentHits.slice(0, 6).join('、')}。`;
  }

  return {
    docPath: relative,
    topic,
    currentStatus,
    finding,
    action,
    ownerSpec,
  };
}

function inferTopic(relative) {
  if (relative.includes('product-design')) return '产品设计';
  if (relative.includes('dev-playbook')) return '开发手册';
  if (relative.includes('00-27')) return '小程序前端架构';
  if (relative.includes('00-28')) return '小程序治理执行';
  if (relative.includes('05-')) return '小程序历史功能 Spec';
  if (relative.includes('kaipai-frontend/docs')) return '前端旧导览文档';
  return '项目文档';
}

async function connectPreparedMiniProgram(wsEndpoint, label) {
  appendProgress('automator-connect-prepared-start', { label, wsEndpoint });
  const miniProgram = await withTimeout(`connectWithRetry-${label}`, connectWithRetry(wsEndpoint), 45000);
  miniProgram.on('console', (record) => {
    consoleRecords.push({ type: 'console', record, at: new Date().toISOString(), connection: label });
  });
  miniProgram.on('exception', (record) => {
    consoleRecords.push({ type: 'exception', record, at: new Date().toISOString(), connection: label });
  });
  await installMockApi(miniProgram);
  appendProgress('automator-connect-prepared-ok', { label });
  return miniProgram;
}

async function disposeMiniProgram(miniProgram, label) {
  if (!miniProgram) return;
  try {
    await miniProgram.restoreWxMethod('request');
  } catch {
    // The DevTools session may already be disposed.
  }
  try {
    miniProgram.disconnect();
  } catch {
    // Disconnect is best-effort during timeout recovery.
  }
  appendProgress('automator-disconnected', { label });
}

async function main() {
  appendProgress('run-start', {
    runId,
    runRoot,
    projectPath,
    runtimePageCount: runtimePages.length,
    targetCount: targets.length,
    automatorResolvedFrom: resolvedAutomator.resolvedFrom,
  });

  const wsEndpoint = enableAutomator();
  await sleep(2500);
  let miniProgram = await connectPreparedMiniProgram(wsEndpoint, 'initial');
  try {
    const captures = [];
    for (const target of targets) {
      let capture = await capturePage(miniProgram, target);
      if (capture.needsReconnect) {
        appendProgress('target-retry-after-reconnect-start', {
          id: target.id,
          firstError: capture.error?.message || '',
        });
        await disposeMiniProgram(miniProgram, `before-retry-${target.id}`);
        await sleep(1500);
        miniProgram = await connectPreparedMiniProgram(wsEndpoint, `retry-${target.id}`);
        capture = await capturePage(miniProgram, { ...target, retryAttempt: 1 });
        capture.retryOf = target.id;
        if (capture.needsReconnect) {
          appendProgress('target-retry-still-needs-reconnect', {
            id: target.id,
            retryError: capture.error?.message || '',
          });
          await disposeMiniProgram(miniProgram, `after-failed-retry-${target.id}`);
          await sleep(1500);
          miniProgram = await connectPreparedMiniProgram(wsEndpoint, `after-failed-retry-${target.id}`);
        }
      }
      captures.push(capture);
    }
    const interactions = [await runLoginInteractionCheck(miniProgram)];
    const summary = summarizeVisualCoverage(captures);
    const pageCoverage = coverageFromCaptures(captures);
    const flowRows = writeFlowMatrix(captures, interactions, summary);
    const docRows = writeDocAuditMatrix();
    const result = {
      generatedAt: new Date().toISOString(),
      runId,
      runRoot,
      projectPath,
      appJsonPath,
      cliPath,
      wsEndpoint,
      autoPort,
      automatorResolvedFrom: resolvedAutomator.resolvedFrom,
      screenshotStrategy: 'automator-first-with-wechatdevtools-window-fallback',
      apiStrategy: 'mock-api-assisted-because-real-sms-code-is-not-returned-and-current-devtools-storage-has-no-token',
      runtimePages: cloneForManifest(runtimePages),
      targets: cloneForManifest(targets),
      summary,
      pageCoverage: cloneForManifest(pageCoverage),
      interactions: cloneForManifest(interactions),
      flowMatrixPath,
      docAuditMatrixPath,
      docAuditRowCount: docRows.length,
      flowRowCount: flowRows.length,
      consoleRecordCount: consoleRecords.length,
      consoleRecords: cloneForManifest(consoleRecords),
      captures: cloneForManifest(captures),
    };
    writeJson(manifestPath, result);
    appendProgress('manifest-written', {
      manifestPath,
      screenshotCount: summary.screenshotCount,
      failedCount: summary.failedCount,
      flowMatrixPath,
      docAuditMatrixPath,
      docAuditRowCount: docRows.length,
    });
    console.log(safeStringify(result));
  } finally {
    await disposeMiniProgram(miniProgram, 'final');
    appendProgress('run-finished', { runId });
  }
}

main().catch((error) => {
  appendProgress('run-failed', {
    message: error.message,
    stack: error.stack,
  });
  console.error(error && error.stack ? error.stack : error);
  process.exit(1);
});
