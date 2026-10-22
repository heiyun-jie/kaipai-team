#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, isAbsolute, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(process.env.KAIPAI_REPO_ROOT || join(scriptDir, '..', '..'));
const frontendRoot = join(repoRoot, 'kaipai-frontend');
const devProject = join(frontendRoot, 'dist', 'dev', 'mp-weixin');
const cliPath = process.env.WECHAT_DEVTOOLS_CLI || 'D:\\AP\\微信web开发者工具\\cli.bat';
const skillCliPath = process.env.WECHATIDE_CLI || join(dirname(cliPath), 'wechatide.cmd');
const skillClientName = process.env.WECHATIDE_CLIENT_NAME || 'Codex';
const evidenceRoot = join(repoRoot, '.sce', 'evidence', 'wechat-devtools');
const outputLimit = 24000;
const defaultTimeoutMs = 120000;
const visibleWindowApprovalDescription = 'Must be true only after the user explicitly confirms that opening or revealing a visible WeChat DevTools window will not interfere with their desktop use.';

const tools = [
  {
    name: 'wechat_devtools_status',
    description: 'Read-only status for the registered WeChat DevTools CLI, fixed project directories, and recognizable DevTools processes.',
    annotations: { readOnlyHint: true, destructiveHint: false },
    inputSchema: { type: 'object', properties: {}, additionalProperties: false },
  },
  {
    name: 'wechat_devtools_build',
    description: 'Build the mini program with the repository script npm run build:mp-weixin and return a bounded command summary.',
    annotations: { readOnlyHint: false, destructiveHint: false },
    inputSchema: { type: 'object', properties: { timeoutMs: { type: 'integer', minimum: 10000, maximum: 300000 } }, additionalProperties: false },
  },
  {
    name: 'wechat_devtools_artifact_check',
    description: 'Read-only check of the fixed runtime WXML, WXSS, and JS files plus SHA-256 and data-v scoped hashes for one route.',
    annotations: { readOnlyHint: true, destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: { route: { type: 'string', description: 'For example pages/home/index or pkg-actor-card/create/index.' } },
      required: ['route'],
      additionalProperties: false,
    },
  },
  {
    name: 'wechat_devtools_open',
    description: 'Open only the fixed project in the WeChat DevTools internal simulator (liteMode). This may create or reveal a visible DevTools window, so it requires allowVisibleWindow=true after explicit user confirmation.',
    annotations: { readOnlyHint: false, destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        target: { type: 'string', enum: ['dev'], default: 'dev' },
        port: { type: 'integer', minimum: 1024, maximum: 65535 },
        allowVisibleWindow: { type: 'boolean', description: visibleWindowApprovalDescription },
      },
      required: ['allowVisibleWindow'],
      additionalProperties: false,
    },
  },
  {
    name: 'wechat_devtools_quit',
    description: 'Quit the fixed WeChat DevTools project through its project-level CLI command; does not kill arbitrary processes.',
    annotations: { readOnlyHint: false, destructiveHint: true },
    inputSchema: {
      type: 'object',
      properties: { target: { type: 'string', enum: ['dev'], default: 'dev' } },
      additionalProperties: false,
    },
  },
  {
    name: 'wechat_devtools_enable_automation',
    description: 'Open the fixed project in the WeChat DevTools internal simulator so its registered page automation tools can be used. This may create or reveal a visible DevTools window, so it requires allowVisibleWindow=true after explicit user confirmation.',
    annotations: { readOnlyHint: false, destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        target: { type: 'string', enum: ['dev'], default: 'dev' },
        trustProject: { type: 'boolean', default: true },
        allowVisibleWindow: { type: 'boolean', description: visibleWindowApprovalDescription },
      },
      required: ['allowVisibleWindow'],
      additionalProperties: false,
    },
  },
  {
    name: 'wechat_devtools_open_project_window',
    description: 'Open the fixed project using the WeChat DevTools internal liteMode simulator window. This may create or reveal a visible DevTools window, so it requires allowVisibleWindow=true after explicit user confirmation.',
    annotations: { readOnlyHint: false, destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        target: { type: 'string', enum: ['dev'], default: 'dev' },
        allowVisibleWindow: { type: 'boolean', description: visibleWindowApprovalDescription },
      },
      required: ['allowVisibleWindow'],
      additionalProperties: false,
    },
  },
  {
    name: 'wechat_devtools_close_project_window',
    description: 'Close only the fixed WeChat DevTools project window through its internal initializer API.',
    annotations: { readOnlyHint: false, destructiveHint: true },
    inputSchema: {
      type: 'object',
      properties: { target: { type: 'string', enum: ['dev'], default: 'dev' } },
      additionalProperties: false,
    },
  },
  {
    name: 'wechat_devtools_open_page',
    description: 'Compile and open one registered mini-program route inside the WeChat DevTools simulator.',
    annotations: { readOnlyHint: false, destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        target: { type: 'string', enum: ['dev'], default: 'dev' },
        route: { type: 'string', description: 'One registered route, for example pages/home/index.' },
        query: { type: 'string' },
        scene: { type: 'integer', minimum: 0, maximum: 9999 },
      },
      required: ['route'],
      additionalProperties: false,
    },
  },
  {
    name: 'wechat_devtools_refresh',
    description: 'Refresh the current page inside the fixed WeChat DevTools simulator.',
    annotations: { readOnlyHint: false, destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: { target: { type: 'string', enum: ['dev'], default: 'dev' } },
      additionalProperties: false,
    },
  },
  {
    name: 'wechat_devtools_screenshot',
    description: 'Capture only the WeChat DevTools simulator surface, never the Windows desktop. Optional output paths must stay under .sce/evidence/wechat-devtools.',
    annotations: { readOnlyHint: false, destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        target: { type: 'string', enum: ['dev'], default: 'dev' },
        path: { type: 'string', description: 'Optional absolute path under .sce/evidence/wechat-devtools.' },
        wait: { type: 'number', minimum: 0, maximum: 10 },
        waitForSelector: { type: 'string', maxLength: 300 },
        optimize: { type: 'boolean', default: false },
        quality: { type: 'integer', minimum: 1, maximum: 100 },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'wechat_devtools_runtime_info',
    description: 'Read the current mini-program page stack, current page, or system info from the internal simulator.',
    annotations: { readOnlyHint: true, destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        target: { type: 'string', enum: ['dev'], default: 'dev' },
        action: { type: 'string', enum: ['pageStack', 'currentPage', 'systemInfo'], default: 'currentPage' },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'wechat_devtools_element_action',
    description: 'Read or operate an element inside the mini-program simulator through the registered WeChat automation API.',
    annotations: { readOnlyHint: false, destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        target: { type: 'string', enum: ['dev'], default: 'dev' },
        action: { type: 'string', enum: ['tap', 'longpress', 'trigger', 'input', 'size', 'offset', 'text', 'attribute', 'value', 'property', 'wxml', 'outerWxml', 'style', 'scrollWidth', 'scrollHeight', 'scrollTo', 'touchstart', 'touchmove', 'touchend'] },
        selector: { type: 'string', minLength: 1, maxLength: 300 },
        type: { type: 'string', maxLength: 100 },
        detail: { type: 'object' },
        value: { type: 'string', maxLength: 2000 },
        name: { type: 'string', maxLength: 200 },
        x: { type: 'number' },
        y: { type: 'number' },
        wait: { type: 'number', minimum: 0, maximum: 10 },
        waitForSelector: { type: 'string', maxLength: 300 },
      },
      required: ['action', 'selector'],
      additionalProperties: false,
    },
  },
  {
    name: 'wechat_devtools_page_action',
    description: 'Read or call a page-level operation inside the mini-program simulator through the registered WeChat automation API.',
    annotations: { readOnlyHint: false, destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        target: { type: 'string', enum: ['dev'], default: 'dev' },
        action: { type: 'string', enum: ['getData', 'setData', 'querySelector', 'querySelectorAll', 'size', 'callMethod', 'scrollTop'] },
        dataPath: { type: 'string', maxLength: 300 },
        patch: { type: 'object' },
        selector: { type: 'string', maxLength: 300 },
        method: { type: 'string', maxLength: 200 },
        args: { type: 'array' },
        wait: { type: 'number', minimum: 0, maximum: 10 },
        waitForSelector: { type: 'string', maxLength: 300 },
      },
      required: ['action'],
      additionalProperties: false,
    },
  },
  {
    name: 'wechat_devtools_console',
    description: 'Read simulator console lines using a restricted grep expression; no shell command is accepted.',
    annotations: { readOnlyHint: true, destructiveHint: false },
    inputSchema: {
      type: 'object',
      properties: { target: { type: 'string', enum: ['dev'], default: 'dev' }, command: { type: 'string', maxLength: 120, default: 'grep -n .' } },
      additionalProperties: false,
    },
  },
];

const registeredRoutes = new Set([
  'pages/home/index', 'pages/login/index', 'pages/actor-profile/edit/index', 'pages/mine/index', 'pages/card-list/index', 'pages/assets/index',
  'pkg-actor-card/create/index', 'pkg-actor-card/step-visual/index', 'pkg-actor-card/step-profile/index', 'pkg-actor-card/step-works/index',
  'pkg-actor-card/step-photos/index', 'pkg-actor-card/step-video/index', 'pkg-actor-card/step-attachment/index', 'pkg-actor-card/step-settings/index',
  'pkg-actor-card/generate/index', 'pkg-actor-card/view/index', 'pkg-profile/import-review/index', 'pkg-profile/assets/index',
  'pkg-tools/webview/index', 'pkg-tools/video-player/index', 'pkg-card/verify/index',
]);

function truncate(value) {
  const text = String(value || '');
  if (text.length <= outputLimit) return text;
  return `${text.slice(0, outputLimit)}\n...[truncated ${text.length - outputLimit} chars]`;
}

function shellQuote(value) {
  const text = String(value);
  if (/^[A-Za-z0-9_./:\\-]+$/.test(text)) return text;
  // Backslashes are ordinary characters for cmd.exe; escaping them here would
  // turn a PowerShell path wildcard into a different pattern.
  return `"${text.replace(/"/g, '\\"')}"`;
}

function commandLine(command, args) {
  return [command, ...args].map(shellQuote).join(' ');
}

function runProcess(command, args, { cwd = repoRoot, timeoutMs = defaultTimeoutMs } = {}) {
  return new Promise((resolveResult) => {
    const child = spawn(commandLine(command, args), {
      cwd,
      shell: true,
      windowsHide: true,
      env: process.env,
    });
    let stdout = '';
    let stderr = '';
    let timedOut = false;
    const timer = setTimeout(() => {
      timedOut = true;
      child.kill();
    }, timeoutMs);

    child.stdout?.setEncoding('utf8');
    child.stderr?.setEncoding('utf8');
    child.stdout?.on('data', (chunk) => { stdout += chunk; });
    child.stderr?.on('data', (chunk) => { stderr += chunk; });
    child.on('error', (error) => {
      clearTimeout(timer);
      resolveResult({ code: null, signal: null, timedOut, stdout: truncate(stdout), stderr: truncate(`${stderr}${error.message}`) });
    });
    child.on('close', (code, signal) => {
      clearTimeout(timer);
      resolveResult({ code, signal, timedOut, stdout: truncate(stdout), stderr: truncate(stderr) });
    });
  });
}

function assertDirectory(path, label) {
  if (!existsSync(path) || !statSync(path).isDirectory()) throw new Error(`${label} does not exist: ${path}`);
}

function projectForTarget(target = 'dev') {
  if (target !== 'dev') throw new Error('only the fixed dev runtime project is supported');
  assertDirectory(devProject, 'dev runtime project');
  return devProject;
}

function assertRoute(route) {
  if (typeof route !== 'string' || !/^(?:pages|pkg-[A-Za-z0-9_-]+)(?:\/[A-Za-z0-9_-]+)+\/index$/.test(route)) {
    throw new Error('route must be a page route ending in /index, such as pages/home/index');
  }
  return route;
}

function assertRegisteredRoute(route) {
  const normalized = assertRoute(route);
  if (!registeredRoutes.has(normalized)) throw new Error(`route is not registered for this project: ${normalized}`);
  return normalized;
}

function assertSafeSelector(value, label = 'selector') {
  if (typeof value !== 'string' || value.trim() === '' || value.length > 300 || /[\r\n]/.test(value)) {
    throw new Error(`${label} must be a non-empty selector no longer than 300 characters`);
  }
  return value;
}

function assertEvidencePath(pathInput) {
  if (pathInput === undefined) return undefined;
  if (typeof pathInput !== 'string' || !isAbsolute(pathInput)) throw new Error('screenshot path must be an absolute path under the evidence directory');
  const path = resolve(pathInput);
  const root = resolve(evidenceRoot);
  if (path !== root && !path.startsWith(`${root}${sep}`)) throw new Error(`screenshot path must stay under ${relative(repoRoot, root)}`);
  mkdirSync(dirname(path), { recursive: true });
  return path;
}

function assertVisibleWindowAllowed(args, toolName) {
  if (args.allowVisibleWindow !== true) {
    throw new Error(`${toolName} may create or reveal a visible WeChat DevTools window. It is disabled during normal desktop use unless allowVisibleWindow=true is passed after explicit user confirmation. Use artifact_check, non-window internal reads, or user-provided screenshots instead.`);
  }
}

function sha256File(filePath) {
  return createHash('sha256').update(readFileSync(filePath)).digest('hex').toUpperCase();
}

function scopedHashes(filePath) {
  const source = readFileSync(filePath, 'utf8');
  return [...new Set(source.match(/data-v-[A-Za-z0-9]+/g) || [])].sort();
}

async function artifactCheck(routeInput) {
  const route = assertRoute(routeInput);
  const files = {};
  for (const ext of ['js', 'wxml', 'wxss']) {
    const filePath = join(devProject, `${route}.${ext}`);
    const exists = existsSync(filePath) && statSync(filePath).isFile();
    files[ext] = exists ? { path: relative(repoRoot, filePath), sha256: sha256File(filePath), scopedHashes: scopedHashes(filePath), exists: true } : { path: relative(repoRoot, filePath), exists: false };
  }
  const complete = ['js', 'wxml', 'wxss'].every((ext) => files[ext].exists);
  const scopedHashSet = ['js', 'wxml', 'wxss'].map((ext) => JSON.stringify(files[ext].scopedHashes || []));
  const scopedHashConsistent = complete && scopedHashSet.every((hashes) => hashes === scopedHashSet[0]);
  return { route, runtimeProject: relative(repoRoot, devProject), runtime: files, complete, scopedHashConsistent };
}

async function status() {
  const cliDirectory = dirname(cliPath).replace(/'/g, "''");
  const processQuery = `Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -like '${cliDirectory}\\*' } | Select-Object ProcessId,Name,ExecutablePath | ConvertTo-Json -Compress`;
  const processResult = await runProcess('powershell.exe', ['-NoProfile', '-Command', processQuery], { timeoutMs: 10000 });
  let processes = [];
  if (processResult.code === 0 && processResult.stdout.trim()) {
    try { processes = Array.isArray(JSON.parse(processResult.stdout)) ? JSON.parse(processResult.stdout) : [JSON.parse(processResult.stdout)]; } catch { processes = [{ raw: processResult.stdout.trim() }]; }
  }
  return {
    repoRoot,
    frontendRoot,
    cli: { path: cliPath, exists: existsSync(cliPath) },
    runtimeProject: { path: devProject, exists: existsSync(devProject) },
    processes,
    node: process.version,
  };
}

function ensureCli() {
  if (!/\.(?:bat|cmd)$/i.test(cliPath) || !existsSync(cliPath) || !statSync(cliPath).isFile()) {
    throw new Error(`WeChat DevTools CLI must be an existing .bat or .cmd file: ${cliPath}`);
  }
}

async function cli(args, options = {}) {
  ensureCli();
  return runProcess(cliPath, args, options);
}

function ensureSkillCli() {
  if (!/\.(?:bat|cmd)$/i.test(skillCliPath) || !existsSync(skillCliPath) || !statSync(skillCliPath).isFile()) {
    throw new Error(`WeChat internal skill CLI must be an existing .bat or .cmd file: ${skillCliPath}`);
  }
}

function pushOption(args, name, value) {
  if (value === undefined || value === null) return;
  if (typeof value === 'boolean') args.push(`--${name}=${value}`);
  else args.push(`--${name}`, String(value));
}

async function skillCall(toolName, options = {}, { timeoutMs = 30000 } = {}) {
  ensureSkillCli();
  const args = ['-c', skillClientName, toolName];
  for (const [name, value] of Object.entries(options)) pushOption(args, name, value);
  return { clientName: skillClientName, tool: toolName, project: options.project, ...(await runProcess(skillCliPath, args, { timeoutMs })) };
}

function validateConsoleCommand(command = 'grep -n .') {
  if (typeof command !== 'string' || command.length > 120 || !/^grep(?:\s+-[A-Za-z]+)?(?:\s+[-A-Za-z0-9_.* ]+)?$/.test(command.trim())) {
    throw new Error('command must be a restricted grep expression such as grep -i error or grep -n .');
  }
  return command.trim();
}

function resultText(value) {
  return JSON.stringify(value, null, 2);
}

async function callTool(name, args = {}) {
  switch (name) {
    case 'wechat_devtools_status':
      return status();
    case 'wechat_devtools_build':
      return { command: 'npm run build:mp-weixin', cwd: relative(repoRoot, frontendRoot), ...(await runProcess('npm.cmd', ['run', 'build:mp-weixin'], { cwd: frontendRoot, timeoutMs: args.timeoutMs || 180000 })) };
    case 'wechat_devtools_artifact_check':
      return artifactCheck(args.route);
    case 'wechat_devtools_open': {
      const project = projectForTarget(args.target || 'dev');
      if (args.port !== undefined) throw new Error('port is not supported by the internal liteMode opener');
      assertVisibleWindowAllowed(args, name);
      return skillCall('open_project_window', { project, windowMode: 'liteMode' });
    }
    case 'wechat_devtools_quit': {
      const project = projectForTarget(args.target || 'dev');
      return { project, ...(await cli(['quit', '--project', project], { timeoutMs: 30000 })) };
    }
    case 'wechat_devtools_enable_automation': {
      const project = projectForTarget(args.target || 'dev');
      assertVisibleWindowAllowed(args, name);
      return skillCall('open_project_window', { project, windowMode: 'liteMode' });
    }
    case 'wechat_devtools_open_project_window': {
      const project = projectForTarget(args.target || 'dev');
      assertVisibleWindowAllowed(args, name);
      return skillCall('open_project_window', { project, windowMode: 'liteMode' });
    }
    case 'wechat_devtools_close_project_window': {
      const project = projectForTarget(args.target || 'dev');
      return skillCall('close_project_window', { project });
    }
    case 'wechat_devtools_open_page': {
      const project = projectForTarget(args.target || 'dev');
      const route = assertRegisteredRoute(args.route);
      if (args.query !== undefined && (typeof args.query !== 'string' || args.query.length > 1000 || /[\r\n]/.test(args.query))) throw new Error('query must be a single-line string no longer than 1000 characters');
      return skillCall('simulator_open_page', { project, page: route, query: args.query, scene: args.scene }, { timeoutMs: 120000 });
    }
    case 'wechat_devtools_refresh': {
      const project = projectForTarget(args.target || 'dev');
      return skillCall('simulator_refresh', { project }, { timeoutMs: 120000 });
    }
    case 'wechat_devtools_screenshot': {
      const project = projectForTarget(args.target || 'dev');
      const path = assertEvidencePath(args.path);
      if (args.waitForSelector !== undefined) assertSafeSelector(args.waitForSelector, 'waitForSelector');
      return skillCall('simulator_screenshot', {
        project,
        path,
        wait: args.wait,
        waitForSelector: args.waitForSelector,
        optimize: args.optimize === undefined ? false : args.optimize,
        quality: args.quality,
      }, { timeoutMs: 60000 });
    }
    case 'wechat_devtools_runtime_info': {
      const project = projectForTarget(args.target || 'dev');
      const action = args.action || 'currentPage';
      return skillCall('automation_runtime_info', { project, action });
    }
    case 'wechat_devtools_element_action': {
      const project = projectForTarget(args.target || 'dev');
      assertSafeSelector(args.selector);
      if (args.waitForSelector !== undefined) assertSafeSelector(args.waitForSelector, 'waitForSelector');
      return skillCall('automation_element_action', {
        project,
        action: args.action,
        selector: args.selector,
        type: args.type,
        detail: args.detail === undefined ? undefined : JSON.stringify(args.detail),
        value: args.value,
        name: args.name,
        x: args.x,
        y: args.y,
        wait: args.wait,
        waitForSelector: args.waitForSelector,
      });
    }
    case 'wechat_devtools_page_action': {
      const project = projectForTarget(args.target || 'dev');
      if (args.selector !== undefined) assertSafeSelector(args.selector);
      if (args.waitForSelector !== undefined) assertSafeSelector(args.waitForSelector, 'waitForSelector');
      return skillCall('automation_page_action', {
        project,
        action: args.action,
        dataPath: args.dataPath,
        patch: args.patch === undefined ? undefined : JSON.stringify(args.patch),
        selector: args.selector,
        method: args.method,
        args: args.args === undefined ? undefined : JSON.stringify(args.args),
        wait: args.wait,
        waitForSelector: args.waitForSelector,
      });
    }
    case 'wechat_devtools_console': {
      const project = projectForTarget(args.target || 'dev');
      return skillCall('get_simulator_console', { project, command: validateConsoleCommand(args.command) });
    }
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

function send(message) {
  process.stdout.write(`${JSON.stringify(message)}\n`);
}

function handleRequest(request) {
  if (!request || typeof request !== 'object') return;
  const id = request.id;
  if (request.method === 'notifications/initialized' || request.method === 'notifications/cancelled') return;
  if (request.method === 'ping') return id === undefined ? undefined : send({ jsonrpc: '2.0', id, result: {} });
  if (request.method === 'initialize') {
    return send({ jsonrpc: '2.0', id, result: {
      protocolVersion: '2025-06-18',
      capabilities: { tools: { listChanged: false } },
      serverInfo: { name: 'kaipai-wechat-devtools', version: '0.1.0' },
      instructions: 'Only use this server for the fixed kaipai-team WeChat mini-program projects. It does not execute arbitrary shell commands, kill arbitrary processes, use desktop screenshots/coordinates, or force windows topmost/foreground. Tools that may open or reveal a visible DevTools window require allowVisibleWindow=true after explicit user confirmation.',
    } });
  }
  if (request.method === 'tools/list') return send({ jsonrpc: '2.0', id, result: { tools } });
  if (request.method === 'tools/call') {
    const name = request.params?.name;
    const args = request.params?.arguments || {};
    return callTool(name, args).then((value) => send({ jsonrpc: '2.0', id, result: { content: [{ type: 'text', text: resultText(value) }] } })).catch((error) => send({ jsonrpc: '2.0', id, result: { isError: true, content: [{ type: 'text', text: error instanceof Error ? error.message : String(error) }] } }));
  }
  if (id !== undefined) send({ jsonrpc: '2.0', id, error: { code: -32601, message: `Method not found: ${request.method}` } });
}

let inputBuffer = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => {
  inputBuffer += chunk;
  let newline;
  while ((newline = inputBuffer.indexOf('\n')) >= 0) {
    const line = inputBuffer.slice(0, newline).trim();
    inputBuffer = inputBuffer.slice(newline + 1);
    if (!line) continue;
    try { handleRequest(JSON.parse(line)); } catch (error) { send({ jsonrpc: '2.0', id: null, error: { code: -32700, message: error instanceof Error ? error.message : String(error) } }); }
  }
});

process.on('uncaughtException', (error) => process.stderr.write(`[kaipai-wechat-devtools] ${error.stack || error.message}\n`));
process.on('unhandledRejection', (error) => process.stderr.write(`[kaipai-wechat-devtools] ${String(error)}\n`));
