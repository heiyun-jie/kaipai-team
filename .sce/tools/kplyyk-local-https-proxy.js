const fs = require('fs');
const http = require('http');
const https = require('https');
const path = require('path');

const runtimeDir = process.env.KPLYYK_LOCAL_PROXY_RUNTIME_DIR || path.resolve(__dirname, '..', 'runtime', 'kplyyk-local-proxy');
const proxyDomain = process.env.KPLYYK_LOCAL_PROXY_DOMAIN || 'localhost';
const certName = proxyDomain.replace(/[^a-zA-Z0-9.-]/g, '_');
const keyPath = path.join(runtimeDir, `${certName}.local.key`);
const certPath = path.join(runtimeDir, `${certName}.local.crt`);
const pidPath = path.join(runtimeDir, 'proxy.pid');
const listenHost = process.env.KPLYYK_LOCAL_PROXY_HOST || '127.0.0.1';
const listenPort = Number(process.env.KPLYYK_LOCAL_PROXY_PORT || '18443');
const targetHost = process.env.KPLYYK_LOCAL_PROXY_TARGET_HOST || '127.0.0.1';
const targetPort = Number(process.env.KPLYYK_LOCAL_PROXY_TARGET_PORT || '18080');

function sendJson(res, statusCode, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(body),
  });
  res.end(body);
}

function proxyRequest(req, res) {
  const chunks = [];
  req.on('data', (chunk) => chunks.push(chunk));
  req.on('end', () => {
    const body = Buffer.concat(chunks);
    const headers = { ...req.headers };
    headers.host = proxyDomain;
    headers['x-forwarded-proto'] = 'https';
    headers['x-forwarded-host'] = proxyDomain;
    headers['x-real-ip'] = req.socket.remoteAddress || '127.0.0.1';
    headers['content-length'] = body.length;

    const upstream = http.request(
      {
        host: targetHost,
        port: targetPort,
        method: req.method,
        path: req.url,
        headers,
        timeout: 15000,
      },
      (upstreamRes) => {
        res.writeHead(upstreamRes.statusCode || 502, upstreamRes.headers);
        upstreamRes.pipe(res);
      },
    );

    upstream.on('timeout', () => {
      upstream.destroy(new Error('upstream timeout'));
    });
    upstream.on('error', (error) => {
      sendJson(res, 502, {
        code: 502,
        message: `local proxy upstream error: ${error.message}`,
        data: null,
      });
    });
    upstream.end(body);
  });
}

fs.mkdirSync(runtimeDir, { recursive: true });
fs.writeFileSync(pidPath, `${process.pid}\n`, 'utf8');

const server = https.createServer(
  {
    key: fs.readFileSync(keyPath),
    cert: fs.readFileSync(certPath),
  },
  (req, res) => {
    if (req.url === '/' || req.url === '/__proxy_health') {
      sendJson(res, 200, {
        code: 200,
        message: 'kplyyk local https proxy ok',
        data: { target: `http://${targetHost}:${targetPort}` },
      });
      return;
    }
    proxyRequest(req, res);
  },
);

server.on('error', (error) => {
  console.error(`[kplyyk-local-proxy] listen failed: ${error.message}`);
  process.exit(1);
});

server.listen(listenPort, listenHost, () => {
  console.log(`[kplyyk-local-proxy] listening https://${listenHost}:${listenPort} -> http://${targetHost}:${targetPort}`);
});
