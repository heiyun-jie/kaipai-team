# AI 通知 HTTP Bridge 代理路由同步记录

## 1. 基本信息

- 批次号：`20260404-090551-ai-notification-http-bridge-proxy-continue-http-provider-bridge-proxy`
- 执行时间：`2026-04-04 09:05:59 +0800`
- 操作人：`codex`
- 目标主机：`101.43.57.62`
- 路由：`/bridge/ai-notification/`
- 反代目标：`http://172.17.0.1:19081/`

## 2. 远端结果

- 备份目录：`/opt/kaipai/backups/releases/20260404-090551-ai-notification-http-bridge-proxy-continue-http-provider-bridge-proxy/ai-http-bridge-proxy`
- nginx 配置：`/opt/kaipai/nginx/conf/default.conf`

## 3. Nginx 检查

- `nginx -t`：`nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful`
- `nginx reload`：`2026/04/04 01:06:00 [notice] 68#68: signal process started`

## 4. 代理探活

```text
HTTP/1.1 405 Not Allowed
Server: nginx/1.29.6
Date: Sat, 04 Apr 2026 01:06:00 GMT
Content-Type: text/html
Content-Length: 157
Connection: keep-alive

<html>
<head><title>405 Not Allowed</title></head>
<body>
<center><h1>405 Not Allowed</h1></center>
<hr><center>nginx/1.29.6</center>
</body>
</html>
```
