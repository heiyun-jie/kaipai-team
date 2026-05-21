#!/usr/bin/env node

const fs = require('fs');

const baseUrl = (process.argv[2] || process.env.API_BASE_URL || 'http://127.0.0.1:8080/api').replace(/\/$/, '');
const reportPath = process.env.REPORT_PATH || '';
const adminSmokePassword = process.env.KAIPAI_ADMIN_SMOKE_PASSWORD || '';
const methods = ['get', 'post', 'put', 'delete', 'patch'];
const state = {
  adminToken: '',
  actorToken: '',
  crewToken: '',
  actorUserId: 1,
  crewUserId: 1,
  projectId: 1,
  runId: String(Date.now()).slice(-8),
};

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function request(method, path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), options.timeoutMs || 20000);
  const headers = { ...(options.headers || {}) };
  let body;
  if (options.body !== undefined) {
    headers['content-type'] = headers['content-type'] || 'application/json';
    body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
  }
  if (options.formData !== undefined) {
    delete headers['content-type'];
    body = options.formData;
  }
  try {
    const started = Date.now();
    const response = await fetch(baseUrl + path, {
      method: method.toUpperCase(),
      headers,
      body,
      signal: controller.signal,
    });
    const text = await response.text();
    let json = null;
    try {
      json = text ? JSON.parse(text) : null;
    } catch {
      json = null;
    }
    return {
      ok: true,
      method: method.toUpperCase(),
      path,
      httpStatus: response.status,
      ms: Date.now() - started,
      json,
      text: text.slice(0, 600),
    };
  } catch (error) {
    return {
      ok: false,
      method: method.toUpperCase(),
      path,
      httpStatus: 0,
      ms: 0,
      error: error && error.message ? error.message : String(error),
    };
  } finally {
    clearTimeout(timer);
  }
}

function bearer(token) {
  return token ? { authorization: `Bearer ${token}` } : {};
}

async function postJson(path, body, token = '') {
  return request('post', path, { body, headers: bearer(token) });
}

async function bootstrapPhoneUser(userType) {
  const phone = `139${String(Date.now() % 100000000).padStart(8, '0')}`;
  await sleep(5);
  const codeResp = await postJson('/auth/sendCode', { phone });
  const code = codeResp.json && codeResp.json.data;
  if (!code) {
    throw new Error(`sendCode failed for ${phone}: ${JSON.stringify(codeResp)}`);
  }
  const registerResp = await postJson('/auth/register', {
    phone,
    code,
    userType,
    nickName: `audit_${userType}_${state.runId}`,
    deviceFingerprint: `online-openapi-audit-${state.runId}`,
  });
  if (!registerResp.json || registerResp.json.code !== 200) {
    throw new Error(`register failed for ${phone}: ${JSON.stringify(registerResp)}`);
  }
  return {
    phone,
    token: registerResp.json.data.token,
    userId: registerResp.json.data.userId,
  };
}

async function bootstrap() {
  if (!adminSmokePassword) {
    throw new Error('KAIPAI_ADMIN_SMOKE_PASSWORD is required for admin login smoke');
  }
  const admin = await postJson('/admin/auth/login', { account: 'admin', password: adminSmokePassword });
  if (!admin.json || admin.json.code !== 200 || !admin.json.data || !admin.json.data.accessToken) {
    throw new Error(`admin login failed: ${JSON.stringify(admin)}`);
  }
  state.adminToken = admin.json.data.accessToken;

  const actor = await bootstrapPhoneUser(1);
  state.actorToken = actor.token;
  state.actorUserId = actor.userId;

  const crew = await bootstrapPhoneUser(2);
  state.crewToken = crew.token;
  state.crewUserId = crew.userId;

  const project = await postJson('/project', {
    title: `audit_project_${state.runId}`,
    description: 'online api audit',
    location: 'Shanghai',
    status: 1,
    type: 'web_short_drama',
    shootingDate: '2026-04-26',
    coverImage: 'https://kplyyk.com/audit.png',
  }, state.crewToken);
  if (project.json && project.json.code === 200 && project.json.data && project.json.data.id) {
    state.projectId = project.json.data.id;
  }
}

function resolveSchema(doc, schema, depth = 0) {
  if (!schema || depth > 8) return schema || {};
  if (schema.$ref) {
    const name = schema.$ref.split('/').pop();
    return resolveSchema(doc, doc.components && doc.components.schemas ? doc.components.schemas[name] : {}, depth + 1);
  }
  if (schema.allOf && schema.allOf.length) {
    return Object.assign({}, ...schema.allOf.map((item) => resolveSchema(doc, item, depth + 1)));
  }
  return schema;
}

function sampleString(name) {
  const key = name.toLowerCase();
  if (key.includes('phone')) return '13900000001';
  if (key.includes('password')) return `AuditPassword_${state.runId}`;
  if (key.includes('account')) return `audit_${state.runId}`;
  if (key.includes('email')) return `audit_${state.runId}@kplyyk.com`;
  if (key.includes('idcard')) return '110101199001011234';
  if (key.includes('realname')) return 'Audit User';
  if (key.includes('name')) return `audit_${state.runId}`;
  if (key.includes('title')) return `audit title ${state.runId}`;
  if (key.includes('code')) return `AUDIT_${state.runId}`;
  if (key.includes('scene')) return 'actor_profile';
  if (key.includes('type')) return 'resume_polish';
  if (key.includes('status')) return 'active';
  if (key.includes('date')) return '2026-04-26';
  if (key.includes('time')) return '2026-04-26T16:00:00';
  if (key.includes('url')) return 'https://kplyyk.com/audit.png';
  if (key.includes('reason')) return 'online api audit';
  if (key.includes('remark')) return 'online api audit';
  if (key.includes('file')) return 'audit-file-content';
  return `audit_${state.runId}`;
}

function sampleNumber(name, unsafe) {
  const key = name.toLowerCase();
  if (key.includes('pageno') || key === 'page') return 1;
  if (key.includes('pagesize') || key === 'size') return 1;
  if (key === 'userid' || key.endsWith('userid')) return state.actorUserId;
  if (key.includes('roleid')) return unsafe ? 999999999 : 1;
  if (key.includes('projectid')) return unsafe ? 999999999 : state.projectId;
  if (key.includes('templateid')) return unsafe ? 999999999 : 1;
  if (key.includes('sharecardid')) return unsafe ? 999999999 : 1;
  if (key.includes('requestid')) return unsafe ? 999999999 : 1;
  if (key.includes('historyid')) return unsafe ? 999999999 : 1;
  if (key.includes('failureid')) return unsafe ? 999999999 : 1;
  if (key.includes('grantid')) return unsafe ? 999999999 : 1;
  if (key.includes('applyid')) return unsafe ? 999999999 : 1;
  if (key === 'id' || key.endsWith('id')) return unsafe ? 999999999 : 1;
  if (key.includes('status')) return 1;
  if (key.includes('gender')) return 1;
  if (key.includes('sort')) return 1;
  if (key.includes('count')) return 1;
  return 1;
}

function sampleValue(doc, name, schema, unsafe = false, depth = 0) {
  const resolved = resolveSchema(doc, schema, depth);
  if (resolved.enum && resolved.enum.length) return resolved.enum[0];
  if (resolved.type === 'array') return [sampleValue(doc, name, resolved.items || {}, unsafe, depth + 1)];
  if (resolved.type === 'integer' || resolved.type === 'number') return sampleNumber(name, unsafe);
  if (resolved.type === 'boolean') return false;
  if (resolved.type === 'string' || resolved.format === 'binary') return sampleString(name);
  if (resolved.type === 'object' || resolved.properties) {
    const output = {};
    const properties = resolved.properties || {};
    for (const [propertyName, propertySchema] of Object.entries(properties)) {
      output[propertyName] = sampleValue(doc, propertyName, propertySchema, unsafe, depth + 1);
    }
    return output;
  }
  return sampleString(name);
}

function shouldIncludeOptional(name) {
  const key = name.toLowerCase();
  return [
    'page',
    'pageno',
    'pagesize',
    'size',
    'keyword',
    'query',
    'status',
    'type',
    'scene',
    'templateid',
    'templatescenecode',
    'reason',
    'remark',
  ].some((part) => key.includes(part));
}

function operationToken(path) {
  if (path.startsWith('/admin/')) return state.adminToken;
  if (path.startsWith('/project') || path.startsWith('/role') || path.startsWith('/company')) return state.crewToken;
  return state.actorToken;
}

function isUnsafe(method, path) {
  if (method === 'delete') return true;
  if (method === 'put') return true;
  if (method === 'post' && /\{[^}]+}/.test(path)) return true;
  return false;
}

function buildPath(doc, method, path, operation) {
  const unsafe = isUnsafe(method, path);
  return path.replace(/\{([^}]+)}/g, (_, name) => encodeURIComponent(String(sampleNumber(name, unsafe))));
}

function appendQuery(doc, path, parameters, unsafe) {
  const query = new URLSearchParams();
  for (const parameter of parameters || []) {
    if (parameter.in !== 'query') continue;
    const schema = resolveSchema(doc, parameter.schema || {});
    if (schema.type === 'object' || schema.properties) {
      for (const [name, propSchema] of Object.entries(schema.properties || {})) {
        if (parameter.required || shouldIncludeOptional(name)) {
          query.set(name, String(sampleValue(doc, name, propSchema, unsafe)));
        }
      }
    } else if (parameter.required || shouldIncludeOptional(parameter.name)) {
      query.set(parameter.name, String(sampleValue(doc, parameter.name, schema, unsafe)));
    }
  }
  const qs = query.toString();
  return qs ? `${path}${path.includes('?') ? '&' : '?'}${qs}` : path;
}

function requestBody(doc, method, path, operation) {
  if (!operation.requestBody || !operation.requestBody.content) return undefined;
  const jsonContent = operation.requestBody.content['application/json'] || Object.values(operation.requestBody.content)[0];
  if (!jsonContent || !jsonContent.schema) return {};
  const body = sampleValue(doc, 'body', jsonContent.schema, isUnsafe(method, path));
  if (path === '/admin/auth/login') return { account: 'admin', password: adminSmokePassword };
  if (path === '/user/role') return { userType: 1 };
  if (path === '/auth/wechat-login') return { code: `audit_${state.runId}`, inviteCode: '' };
  if (path.includes('/reset-password')) return { newPassword: `AuditReset_${state.runId}` };
  if (path.includes('/bind-roles')) return { roleCodes: ['ADMIN'] };
  if (path === '/admin/referral/policies') {
    return {
      policyName: `audit_policy_${state.runId}`,
      enabled: 1,
      requireRealAuth: 0,
      requireProfileCompletion: 0,
      profileCompletionThreshold: 0,
      sameDeviceLimit: 0,
      hourlyInviteLimit: 0,
      autoGrantEnabled: 0,
      grantRuleJson: '{}',
    };
  }
  if (path === '/admin/referral/eligibility/grant') {
    return {
      userId: state.actorUserId,
      grantType: 'audit',
      grantCode: `AUDIT_${state.runId}`,
      effectiveTime: '2026-04-26T16:00:00',
      expireTime: '2026-05-26T16:00:00',
      sourceType: 'manual',
      sourceRefId: 0,
      remark: 'online api audit',
    };
  }
  return body;
}

function fileForm(path) {
  if (!path.startsWith('/file/upload/')) return null;
  const form = new FormData();
  const isVideo = path.includes('/video');
  const blob = new Blob([isVideo ? 'audit-video' : 'audit-image'], {
    type: isVideo ? 'video/mp4' : 'image/png',
  });
  form.set('file', blob, isVideo ? 'audit.mp4' : 'audit.png');
  return form;
}

async function customAuthOperation(method, path) {
  if (method !== 'post') return null;
  if (path === '/auth/sendCode') {
    return postJson('/auth/sendCode', { phone: `139${String(Date.now() % 100000000).padStart(8, '0')}` });
  }
  if (path === '/auth/register') {
    const phone = `139${String((Date.now() + 11) % 100000000).padStart(8, '0')}`;
    const codeResp = await postJson('/auth/sendCode', { phone });
    return postJson('/auth/register', {
      phone,
      code: codeResp.json && codeResp.json.data,
      userType: 1,
      nickName: `audit_register_${state.runId}`,
      deviceFingerprint: `online-openapi-audit-${state.runId}`,
    });
  }
  if (path === '/auth/login') {
    const phone = `139${String((Date.now() + 22) % 100000000).padStart(8, '0')}`;
    const codeResp = await postJson('/auth/sendCode', { phone });
    await postJson('/auth/register', {
      phone,
      code: codeResp.json && codeResp.json.data,
      userType: 1,
      nickName: `audit_login_${state.runId}`,
      deviceFingerprint: `online-openapi-audit-${state.runId}`,
    });
    const codeResp2 = await postJson('/auth/sendCode', { phone });
    return postJson('/auth/login', { phone, code: codeResp2.json && codeResp2.json.data });
  }
  return null;
}

function classify(result) {
  const code = result.json && typeof result.json.code === 'number' ? result.json.code : null;
  const serverFailure = !result.ok || result.httpStatus >= 500 || code === 500;
  const businessCodeGte500 = code !== null && code >= 500;
  return {
    serverFailure,
    businessCodeGte500,
    code,
  };
}

async function main() {
  const docsResp = await request('get', '/v3/api-docs');
  if (!docsResp.ok || docsResp.httpStatus !== 200 || !docsResp.json) {
    throw new Error(`OpenAPI docs unavailable: ${JSON.stringify(docsResp)}`);
  }
  const doc = docsResp.json;
  await bootstrap();

  const operations = [];
  for (const [path, item] of Object.entries(doc.paths || {})) {
    for (const method of methods) {
      if (item[method]) {
        operations.push({ method, path, operation: item[method], pathParameters: item.parameters || [] });
      }
    }
  }

  const results = [];
  for (const entry of operations) {
    const custom = await customAuthOperation(entry.method, entry.path);
    let result = custom;
    if (!result) {
      const operationParameters = [...(entry.pathParameters || []), ...(entry.operation.parameters || [])];
      const unsafe = isUnsafe(entry.method, entry.path);
      const pathWithIds = buildPath(doc, entry.method, entry.path, entry.operation);
      const finalPath = appendQuery(doc, pathWithIds, operationParameters, unsafe);
      const body = requestBody(doc, entry.method, entry.path, entry.operation);
      const formData = fileForm(entry.path);
      result = await request(entry.method, finalPath, {
        body: formData ? undefined : body,
        formData,
        headers: bearer(operationToken(entry.path)),
      });
    }
    const status = classify(result);
    results.push({
      operationId: entry.operation.operationId,
      summary: entry.operation.summary,
      method: entry.method.toUpperCase(),
      path: entry.path,
      requestedPath: result.path,
      httpStatus: result.httpStatus,
      ms: result.ms,
      bodyCode: status.code,
      message: result.json && result.json.message ? result.json.message : result.error || '',
      serverFailure: status.serverFailure,
      businessCodeGte500: status.businessCodeGte500,
      responsePreview: result.text || '',
    });
  }

  const failures = results.filter((item) => item.serverFailure);
  const businessWarnings = results.filter((item) => item.businessCodeGte500 && !item.serverFailure);
  const report = {
    auditedAt: new Date().toISOString(),
    baseUrl,
    totalOperations: operations.length,
    serverFailureCount: failures.length,
    businessCodeGte500WarningCount: businessWarnings.length,
    failures,
    businessWarnings,
    results,
  };
  if (reportPath) {
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  }
  console.log(JSON.stringify({
    auditedAt: report.auditedAt,
    baseUrl,
    totalOperations: report.totalOperations,
    serverFailureCount: report.serverFailureCount,
    businessCodeGte500WarningCount: report.businessCodeGte500WarningCount,
    failures: failures.slice(0, 20),
  }, null, 2));
  process.exit(failures.length || businessWarnings.length ? 1 : 0);
}

main().catch((error) => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(2);
});
