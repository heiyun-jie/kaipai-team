import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { readFile, rm } from 'node:fs/promises';
import { setTimeout as delay } from 'node:timers/promises';

const repoRoot = new URL('../../..', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const frontendRoot = `${repoRoot}/kaipai-frontend`;
const mockPort = Number(process.env.MOCK_API_PORT || 58072);
const h5Port = Number(process.env.H5_PORT || 58073);
const chromePath = process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const shareCardId = 17201;

const oneByOnePng = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=',
  'base64',
);

function jsonResponse(res, data, statusCode = 200) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
  });
  res.end(JSON.stringify({ code: statusCode === 200 ? 200 : statusCode, message: statusCode === 200 ? 'success' : 'error', data }));
}

function buildTheme() {
  return {
    tokenKey: 'classic-pro-e2e',
    primary: '#8c6f4f',
    accent: '#d4b896',
    background: '#f5f3ee',
    surface: '#fbfaf6',
    surfaceStrong: '#eadfce',
    textPrimary: '#231b15',
    textSecondary: '#6c7483',
    heroText: '#fffdf8',
    buttonStyle: 'outline',
    mood: 'classic',
    posterPreset: 'classic',
    cardPreset: 'classic',
  };
}

function buildLevelInfo() {
  return {
    level: 5,
    inviteCount: 8,
    nextLevelRequirement: null,
    isCertified: true,
    profileCompletion: 96,
    capabilityTier: 'pro',
  };
}

function buildTemplate() {
  return {
    templateSceneCode: 'classic',
    name: '经典',
    description: '自动化测试模板',
    coverImage: '',
    heroEyebrow: 'CLASSIC',
    themeColors: {
      primary: '#8c6f4f',
      accent: '#d4b896',
      background: '#f5f3ee',
      text: '#231b15',
      heroText: '#fffdf8',
    },
    layoutVariant: 'compact',
    contentFocus: ['PDF 简历', 'AI 分享图'],
    tier: 'free',
    requiredLevel: 1,
    requiredInviteCount: 0,
  };
}

function buildActorSnapshot(baseUrl) {
  return {
    userId: 90001,
    name: '自动化演员',
    gender: 'female',
    age: 26,
    height: 168,
    weight: 48,
    city: '上海',
    avatar: `${baseUrl}/assets/avatar.png`,
    intro: '用于验证 AI 分享图详情页承接 PDF 简历展示范围。',
    photos: [`${baseUrl}/assets/photo-1.png`, `${baseUrl}/assets/photo-2.png`],
    photoCategories: {
      portrait: [`${baseUrl}/assets/photo-1.png`],
      lifestyle: [`${baseUrl}/assets/photo-2.png`],
      production: [],
    },
    videoUrl: `${baseUrl}/assets/video.mp4`,
    skillTypes: ['舞蹈', '表演'],
    languages: ['普通话', '英语'],
    workExperiences: [
      {
        id: 1,
        projectName: '自动化短片',
        roleName: '女主角',
        shootDate: '2026',
        photos: [`${baseUrl}/assets/work-1.png`],
        description: '用于页面内容流验证。',
      },
    ],
    bodyType: '清爽自然',
    hairStyle: '黑色长发',
    resumePdfUrl: `${baseUrl}/assets/resume.pdf`,
    resumePdfName: '自动化演员PDF简历.pdf',
    resumePdfPageCount: 2,
    resumePdfPageImageUrls: [`${baseUrl}/assets/pdf-page-1.png`, `${baseUrl}/assets/pdf-page-2.png`],
    contactPhone: '',
    hasContactPhone: false,
    isCertified: true,
    capabilitySummary: buildLevelInfo(),
  };
}

function buildPersonalization(baseUrl) {
  const theme = buildTheme();
  const template = buildTemplate();
  const levelInfo = buildLevelInfo();
  const profile = {
    profileUserId: 90001,
    shareCardId,
    levelInfo,
    capabilityTier: 'pro',
    templateSceneCode: 'classic',
    template,
    templateId: 'e2e-classic',
    customConfig: {
      profileUserId: 90001,
      shareCardId,
      templateSceneCode: 'classic',
      layoutVariant: 'compact',
      primaryColor: '#8c6f4f',
      accentColor: '#d4b896',
      backgroundColor: '#f5f3ee',
      highlightedExperiences: [1],
      highlightedPhotos: [],
      tagOrder: [],
    },
    sharePreferences: {
      preferredArtifact: 'miniProgramCard',
    },
  };
  const capability = {
    canUseBasicCard: true,
    canUsePersonalizedTheme: true,
    canUseCustomMiniProgramCard: true,
    canUseCustomPoster: true,
    canUseCustomInviteCard: true,
    reasonCodes: [],
  };
  return {
    templates: [template],
    profile,
    theme,
    capability,
    actorSnapshot: buildActorSnapshot(baseUrl),
    artifacts: [
      {
        type: 'miniProgramCard',
        label: '小程序名片',
        title: '经典小程序名片',
        subtitle: '自动化测试',
        coverImage: '',
        path: `/pkg-card/ai-profile-card-detail/index?shareCardId=${shareCardId}&shared=1`,
        shareImageUrl: '',
        locked: false,
        theme,
        capability,
      },
    ],
  };
}

function startMockApi() {
  const baseUrl = `http://127.0.0.1:${mockPort}`;
  const server = createServer((req, res) => {
    if (req.method === 'OPTIONS') {
      jsonResponse(res, {});
      return;
    }
    const url = new URL(req.url || '/', baseUrl);
    if (url.pathname.startsWith('/assets/')) {
      if (url.pathname.endsWith('.mp4')) {
        res.writeHead(200, {
          'Content-Type': 'video/mp4',
          'Access-Control-Allow-Origin': '*',
        });
        res.end(Buffer.from(''));
        return;
      }
      res.writeHead(200, {
        'Content-Type': url.pathname.endsWith('.pdf') ? 'application/pdf' : 'image/png',
        'Access-Control-Allow-Origin': '*',
      });
      res.end(url.pathname.endsWith('.pdf') ? Buffer.from('%PDF-1.4\n% e2e\n') : oneByOnePng);
      return;
    }
    if (url.pathname === '/api/card/personalization') {
      jsonResponse(res, buildPersonalization(baseUrl));
      return;
    }
    if (url.pathname === `/api/ai/profile-card/share-cards/${shareCardId}/artifact`) {
      jsonResponse(res, {
        artifactId: 'artifact-e2e',
        taskId: 'task-e2e',
        status: 'success',
        templateSceneCode: 'classic',
        styleCode: 'classic_profile_full_card',
        providerCode: 'tencent-hunyuan',
        modelCode: 'e2e',
        shareCardId,
        sourceImageUrl: `${baseUrl}/assets/source.png`,
        generatedImageUrl: 'https://kaipai-e2e.cos.ap-shanghai.myqcloud.com/ai-profile-card/e2e-cover.jpg',
        theme: {
          backgroundColor: '#f5f3ee',
          surfaceColor: '#fbfaf6',
          surfaceStrongColor: '#eadfce',
          accentColor: '#8c6f4f',
          textColor: '#231b15',
          mutedTextColor: '#6c7483',
          borderColor: 'rgba(35, 27, 21, 0.12)',
        },
      });
      return;
    }
    if (url.pathname === '/api/card/contact-requests/status') {
      jsonResponse(res, {
        shareCardId,
        status: 'none',
        templateSceneCode: 'classic',
        templateName: '经典',
        contactPhone: '',
      });
      return;
    }
    if (url.pathname === '/api/card/view-histories') {
      jsonResponse(res, null);
      return;
    }
    jsonResponse(res, null, 404);
  });
  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(mockPort, '127.0.0.1', () => resolve({ server, baseUrl }));
  });
}

function spawnProcess(command, args, options = {}) {
  const isWindows = process.platform === 'win32';
  const child = spawn(isWindows ? (process.env.ComSpec || 'cmd.exe') : command, isWindows ? ['/d', '/s', '/c', command, ...args] : args, {
    cwd: options.cwd,
    env: { ...process.env, ...options.env },
    shell: false,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  child.stdout.on('data', (chunk) => process.stdout.write(`[${options.name || command}] ${chunk}`));
  child.stderr.on('data', (chunk) => process.stderr.write(`[${options.name || command}:err] ${chunk}`));
  return child;
}

async function waitForExit(child, timeoutMs, label) {
  let timeout;
  const exitPromise = once(child, 'exit').then(([code]) => code);
  const timeoutPromise = new Promise((_, reject) => {
    timeout = setTimeout(() => reject(new Error(`${label} timed out after ${timeoutMs}ms`)), timeoutMs);
  });
  try {
    return await Promise.race([exitPromise, timeoutPromise]);
  } finally {
    clearTimeout(timeout);
  }
}

function killProcessTree(pid) {
  if (!pid) {
    return;
  }
  if (process.platform === 'win32') {
    spawn(process.env.ComSpec || 'cmd.exe', ['/d', '/s', '/c', 'taskkill', '/PID', String(pid), '/T', '/F'], {
      stdio: 'ignore',
      shell: false,
    });
    return;
  }
  try {
    process.kill(pid, 'SIGTERM');
  } catch {
    // Process already exited.
  }
}

async function waitForHttp(url, timeoutMs = 45000) {
  const deadline = Date.now() + timeoutMs;
  let lastError;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok || response.status < 500) {
        return;
      }
      lastError = new Error(`HTTP ${response.status}`);
    } catch (error) {
      lastError = error;
    }
    await delay(600);
  }
  throw new Error(`Timed out waiting for ${url}: ${lastError?.message || 'no response'}`);
}

async function runChromeDump(url) {
  const runId = `${Date.now()}-${process.pid}`;
  const chromeProfileDir = `${frontendRoot}/.tmp-00-172-chrome-profile-${runId}`;
  const stdoutPath = `${frontendRoot}/.tmp-00-172-chrome-stdout-${runId}.txt`;
  const stderrPath = `${frontendRoot}/.tmp-00-172-chrome-stderr-${runId}.txt`;
  const args = [
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--disable-extensions',
    '--disable-background-networking',
    '--virtual-time-budget=12000',
    '--window-size=390,1200',
    `--user-data-dir=${chromeProfileDir}`,
    '--dump-dom',
    url,
  ];
  const chrome = process.platform === 'win32'
    ? spawn('powershell.exe', [
      '-NoProfile',
      '-ExecutionPolicy',
      'Bypass',
      '-EncodedCommand',
      Buffer.from([
        "$ProgressPreference = 'SilentlyContinue'",
        `$p = Start-Process -FilePath '${chromePath.replace(/'/g, "''")}' -ArgumentList @(${args.map((arg) => `'${arg.replace(/'/g, "''")}'`).join(',')}) -NoNewWindow -Wait -PassThru -RedirectStandardOutput '${stdoutPath.replace(/'/g, "''")}' -RedirectStandardError '${stderrPath.replace(/'/g, "''")}'`,
        'exit $p.ExitCode',
      ].join('\n'), 'utf16le').toString('base64'),
    ], { cwd: frontendRoot, shell: false, stdio: ['ignore', 'pipe', 'pipe'] })
    : spawn(chromePath, args, { cwd: frontendRoot, shell: false, stdio: ['ignore', 'pipe', 'pipe'] });
  let stdout = '';
  let stderr = '';
  chrome.stdout.on('data', (chunk) => { stdout += chunk.toString(); });
  chrome.stderr.on('data', (chunk) => { stderr += chunk.toString(); });
  try {
    const code = await waitForExit(chrome, 45000, 'Chrome DOM dump');
    if (code !== 0) {
      throw new Error(`Chrome exited with ${code}\n${stderr}`);
    }
    const redirectedStdout = process.platform === 'win32' ? await readFile(stdoutPath, 'utf8').catch(() => '') : stdout;
    const redirectedStderr = process.platform === 'win32' ? await readFile(stderrPath, 'utf8').catch(() => '') : stderr;
    return { stdout: redirectedStdout, stderr: redirectedStderr || stderr };
  } catch (error) {
    killProcessTree(chrome.pid);
    throw error;
  } finally {
    await Promise.all([
      rm(stdoutPath, { force: true }),
      rm(stderrPath, { force: true }),
      rm(chromeProfileDir, { recursive: true, force: true }),
    ]);
  }
}

async function main() {
  const mock = await startMockApi();
  const h5 = spawnProcess('npm.cmd', ['run', 'dev:h5', '--', '--host', '127.0.0.1', '--port', String(h5Port)], {
    cwd: frontendRoot,
    name: 'h5',
    env: {
      VITE_API_BASE_URL: mock.baseUrl,
      VITE_ENABLE_WECHAT_AUTH: 'false',
    },
  });
  try {
    await waitForHttp(`http://127.0.0.1:${h5Port}/`);
    const pageUrl = `http://127.0.0.1:${h5Port}/#/pkg-card/ai-profile-card-detail/index?shareCardId=${shareCardId}&shared=1`;
    const { stdout: dom, stderr } = await runChromeDump(pageUrl);
    const required = [
      'PDF 简历',
      '自动化演员PDF简历.pdf',
      '2 页',
      'ai-share-detail-page__pdf-page',
      `${mock.baseUrl}/assets/pdf-page-1.png`,
      `${mock.baseUrl}/assets/pdf-page-2.png`,
    ];
    const missing = required.filter((item) => !dom.includes(item));
    if (missing.length) {
      throw new Error(`AI detail PDF flow assertion failed. Missing: ${missing.join(', ')}\nChrome stderr:\n${stderr}\nDOM excerpt:\n${dom.slice(0, 4000)}`);
    }
    if (dom.includes('分享图加载失败') || dom.includes('暂无 AI 封面')) {
      throw new Error('AI detail page entered error/unavailable state unexpectedly.');
    }
    const videoIndex = dom.lastIndexOf('视频简历');
    const pdfIndex = dom.indexOf('PDF 简历');
    if (videoIndex < 0 || pdfIndex < 0 || pdfIndex < videoIndex) {
      throw new Error(`AI detail PDF section order assertion failed. videoIndex=${videoIndex}, pdfIndex=${pdfIndex}`);
    }
    console.log(JSON.stringify({
      status: 'passed',
      pageUrl,
      assertions: [...required, 'PDF section is rendered after video section'],
    }, null, 2));
  } finally {
    killProcessTree(h5.pid);
    mock.server.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
