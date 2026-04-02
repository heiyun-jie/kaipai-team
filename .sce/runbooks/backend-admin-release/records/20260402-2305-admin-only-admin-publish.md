# 后端与管理端发布记录

## 1. 基本信息

- 发布批次号：`20260402-2305-admin-only-admin-publish`
- 发布时间：`2026-04-02 23:10:33 +08:00`
- 发布范围：`admin-only`
- 操作人：`codex`
- 关联 Spec / 需求：
  - `00-29 backend-admin-release-governance`
  - 管理端静态资源补发布，消除线上 `http://101.43.57.62/` 的 `403`

## 2. 发布前检查

- 目标环境：
  - 远端主机：`101.43.57.62`
  - nginx 静态目录：`/opt/kaipai/nginx/html`
  - nginx `/api` 反代目标：`http://kaipai-backend:8080`
- 后端运行时集合核对：
  - 本轮不发布后端，仅要求 `/api/v3/api-docs` 可用
- 管理端运行时集合核对：
  - 本地开发代理 `5174 -> 8010` 已恢复
  - 线上根路径发布前实测返回 `403 Forbidden`
- 是否需要联合发布：`否`
- 中止门禁检查结果：`通过，进入 admin-only 发布`

## 3. 产物信息

### 3.1 后端

- 本地 jar 路径：`N/A`
- 本地 jar SHA256：`N/A`
- 远端备份路径：`N/A`
- 远端落地路径：`N/A`
- 容器内 `/app/app.jar` SHA256：`N/A`

### 3.2 管理端

- 本地 dist 路径：`D:\XM\kaipai-team\kaipai-admin\dist`
- 本地产物压缩包：`D:\XM\kaipai-team\tmp\admin-dist-20260402-2305.tar.gz`
- 本地产物 SHA256：`E2E529D92C62430D4CEEB3C49042263898039D4A7EDDB0489B757C5574C861EC`
- 远端静态备份路径：`/opt/kaipai/backups/releases/20260402-2305-admin-only-admin-publish/admin-html/`
- 远端静态落地路径：`/opt/kaipai/nginx/html`
- 远端构建落地路径：`/opt/kaipai/builds/20260402-2305-admin-only-admin-publish/admin-dist.tar.gz`
- `index.html` 回读结果：
  - `<title>开拍了后台</title>`
  - `src="/assets/index-q5qZpz_X.js"`
  - `href="/assets/index-CXJTLMJc.css"`

## 4. 执行摘要

- 后端执行命令摘要：`无`
- 管理端执行命令摘要：
  - 本地：`npm run build`
  - 本地：`tar.exe -C D:\XM\kaipai-team\kaipai-admin\dist -czf D:\XM\kaipai-team\tmp\admin-dist-20260402-2305.tar.gz .`
  - 远端备份：备份 `/opt/kaipai/nginx/html` 与 `/opt/kaipai/nginx/conf/default.conf`
  - 远端替换：上传到 `/opt/kaipai/builds/20260402-2305-admin-only-admin-publish/admin-dist.tar.gz`，解压到 `admin-dist/`，再同步到 `/opt/kaipai/nginx/html`
  - 本地联调修复：重启 `8010` 为当前源码实例，恢复 `5174 -> 8010` 管理端代理链
- 是否执行回滚：`否`

## 5. smoke 结果

- 后端容器状态：
  - `kaipai-backend   kaipai-kaipai:latest   Up About an hour   0.0.0.0:8080->8080/tcp`
- `/api/v3/api-docs`：
  - 远端内网：`curl -I http://127.0.0.1/api/v3/api-docs -> HTTP/1.1 200`
  - 公网：`http://101.43.57.62/api/v3/api-docs` 可正常登录后调用后台接口
- 业务接口 smoke：
  - 本地 `8010`：`GET /api/admin/recruit/roles?pageNo=1&pageSize=20&keyword=` -> `200`，`{"total":0,"list":[]}`
  - 本地 `5174` 代理：同接口 -> `200`，`{"total":0,"list":[]}`
  - 公网：`POST /api/admin/auth/login` 使用 `admin/admin123` -> `200`
- 管理端首页：
  - 发布前：`http://101.43.57.62/` -> `403 Forbidden`
  - 发布后：`http://101.43.57.62/` -> `200 OK`
  - 公网静态资源：`http://101.43.57.62/assets/index-q5qZpz_X.js` -> `200 OK`
- 后台页面人工验证：
  - 通过 HTML 回读确认首页已切到正式管理端入口
  - 通过后台登录接口确认登录链路可用
- 联合 smoke：
  - `http://101.43.57.62/` 返回管理端首页
  - `http://101.43.57.62/api/admin/auth/login` 返回 `200`

## 6. 结论

- 最终结论：`完成`
- 问题与备注：
  - 发布前线上管理端首页不可访问，根路径返回 `403`
  - 本批次首次使用 Windows zip 上传时，远端出现反斜杠文件名，已在同一批次内改为 `tar.gz` 重新落地，最终线上目录为标准 `assets/` 结构
  - 该差异已回写 `00-29` 与 `backend-admin-standard-release.md`，后续管理端发布统一按 `tar.gz` 链路执行
  - 小程序演员首页筛选 400 已在 `kaipai-frontend/src/utils/request.ts` 增加 `undefined` 参数剔除
- 后续动作：
  - 后续每次后台发布继续沿用本手册与同目录记录模板
  - 如需补充后台人工页面级验收，可直接访问 `http://101.43.57.62/`
