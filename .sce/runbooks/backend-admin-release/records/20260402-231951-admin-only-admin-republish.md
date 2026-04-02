# 后端与管理端发布记录

## 1. 基本信息

- 发布批次号：`20260402-231951-admin-only-admin-republish`
- 发布时间：`2026-04-02 23:21:42 +08:00`
- 发布范围：`admin-only`
- 操作人：`codex`
- 关联 Spec / 需求：
  - `00-29 backend-admin-release-governance`
  - 按更新后的标准 runbook 再次执行一次后台管理端发布，并核对发布时间与发布结果

## 2. 发布前检查

- 目标环境：
  - 远端主机：`101.43.57.62`
  - nginx 静态目录：`/opt/kaipai/nginx/html`
  - nginx `/api` 反代目标：`http://kaipai-backend:8080`
- 后端运行时集合核对：
  - 本轮不发布后端，仅要求 `/api/v3/api-docs` 正常
- 管理端运行时集合核对：
  - 本地构建目录：`D:\XM\kaipai-team\kaipai-admin\dist`
  - 本地归档格式：`tar.gz`
  - 线上首页发布前状态：`HTTP/1.1 200 OK`
- 是否需要联合发布：`否`
- 中止门禁检查结果：`通过，进入 admin-only 重发`

## 3. 产物信息

### 3.1 后端

- 本地 jar 路径：`N/A`
- 本地 jar SHA256：`N/A`
- 远端备份路径：`N/A`
- 远端落地路径：`N/A`
- 容器内 `/app/app.jar` SHA256：`N/A`

### 3.2 管理端

- 本地 dist 路径：`D:\XM\kaipai-team\kaipai-admin\dist`
- 本地产物压缩包：`D:\XM\kaipai-team\tmp\admin-dist-20260402-231951-admin-only-admin-republish.tar.gz`
- 本地产物 SHA256：`E6CB8130FB9E55BEEA98FFB1C0FB0578C91715603BA709A78E82FB9F98468DFD`
- 远端静态备份路径：`/opt/kaipai/backups/releases/20260402-231951-admin-only-admin-republish/admin-html/`
- 远端静态落地路径：`/opt/kaipai/nginx/html`
- 远端构建落地路径：`/opt/kaipai/builds/20260402-231951-admin-only-admin-republish/admin-dist.tar.gz`
- `index.html` 回读结果：
  - `<title>开拍了后台</title>`
  - `src="/assets/index-q5qZpz_X.js"`
  - `href="/assets/index-CXJTLMJc.css"`

## 4. 执行摘要

- 后端执行命令摘要：`无`
- 管理端执行命令摘要：
  - 本地：`npm run build`
  - 本地：`tar.exe -C D:\XM\kaipai-team\kaipai-admin\dist -czf D:\XM\kaipai-team\tmp\admin-dist-20260402-231951-admin-only-admin-republish.tar.gz .`
  - 远端：备份 `/opt/kaipai/nginx/html` 与 `/opt/kaipai/nginx/conf/default.conf`
  - 远端：上传到 `/opt/kaipai/builds/20260402-231951-admin-only-admin-republish/admin-dist.tar.gz`
  - 远端：解压到 `/opt/kaipai/builds/20260402-231951-admin-only-admin-republish/admin-dist/` 后同步到 `/opt/kaipai/nginx/html`
- 是否执行回滚：`否`

## 5. smoke 结果

- 后端容器状态：
  - `kaipai-backend   kaipai-kaipai:latest   Up About an hour   0.0.0.0:8080->8080/tcp`
- `/api/v3/api-docs`：
  - 远端内网：`curl -I http://127.0.0.1/api/v3/api-docs -> HTTP/1.1 200`
- 业务接口 smoke：
  - 公网：`POST http://101.43.57.62/api/admin/auth/login` 使用 `admin/admin123` -> `200`
- 管理端首页：
  - 远端内网发布时间回读：`2026-04-02 23:21:42 +0800`
  - 公网：`http://101.43.57.62/ -> HTTP/1.1 200 OK`
  - 公网首页 `Last-Modified`：`Thu, 02 Apr 2026 15:20:56 GMT`
  - 公网静态资源：`http://101.43.57.62/assets/index-q5qZpz_X.js -> HTTP/1.1 200 OK`
- 后台页面人工验证：
  - 通过公网首页 HTML 回读确认已加载当前静态入口
  - 通过后台登录接口确认页面依赖接口可用
- 联合 smoke：`N/A`

## 6. 结论

- 最终结论：`完成`
- 问题与备注：
  - 本次为按更新后 runbook 执行的重复发布，流程与文档一致
  - 本轮未发布后端，仅复核后端容器和 `/api` 基础入口仍正常
- 后续动作：
  - 后续若继续发布后台管理端，沿用同一 `tar.gz` 流程
