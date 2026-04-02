# 实名认证真实环境运行时清单

## 1. 目的

本清单用于在开始 verify 真实环境联调前，先确认 actor、小程序后台和审核后台是否命中同一套运行时。

如果这一步没有先确认，后续“提交成功”“后台可见”“前台放行”很容易来自不同环境，结论无效。

## 2. 服务端运行时

### 2.1 应用基础配置

- 关键文件：
  - `kaipaile-server/src/main/resources/bootstrap.yml`
  - `kaipaile-server/src/main/resources/application.yml`
  - `kaipaile-server/src/main/resources/application-dev.yml`
- 当前仓库默认事实：
  - `server.servlet.context-path=/api`
  - `application-dev.yml` 覆盖 `server.port=8010`
  - 外部真实环境当前长期按 `NACOS_ENABLED=true + SPRING_PROFILES_ACTIVE=dev` 运行

### 2.2 verify 相关真实接口

- actor 侧：
  - `GET /api/verify/status`
  - `POST /api/verify/submit`
  - `GET /api/level/info`
- admin 侧：
  - `GET /api/admin/verify/list`
  - `GET /api/admin/verify/{id}`
  - `POST /api/admin/verify/{id}/approve`
  - `POST /api/admin/verify/{id}/reject`

### 2.3 联调前必须确认

1. 当前 profile 是否仍为 `dev`
2. 当前运行时是否仍开启 `NACOS_ENABLED=true`
3. 当前 verify 链命中的数据库是否仍为 `kaipai_dev`
4. 当前 `/api/v3/api-docs` 中是否已能看到 `/verify/*` 与 `/admin/verify/*`

## 3. 后台管理端运行时

### 3.1 本地 dev 行为

- `kaipai-admin/vite.config.ts`
  - 本地端口：`5174`
  - 代理目标：`http://127.0.0.1:8010`
- `kaipai-admin/src/utils/request.ts`
  - 若未显式配置 `VITE_API_BASE_URL`，默认走 `/api`

### 3.2 verify 后台治理前置

- 当前登录态必须具备：
  - `page.verify.pending`
  - `page.verify.history`
  - `page.verify.detail`
  - `action.verify.approve`
  - `action.verify.reject`

## 4. 小程序前端运行时

### 4.1 真接口 / mock 总闸

- `kaipai-frontend/src/utils/runtime.ts`
  - `VITE_USE_MOCK='false'` 时，关闭全局 mock
  - 缺少 `VITE_API_BASE_URL` 时，小程序会退回 mock 或错误相对路径

### 4.2 verify 联调相关远端能力

- `REMOTE_CAPABILITIES` 已包含：
  - `auth`
  - `verify`
  - `level`
  - `actor`

### 4.3 联调前必须确认

1. `kaipai-frontend/.env` 中 `VITE_USE_MOCK=false`
2. `kaipai-frontend/.env` 中 `VITE_API_BASE_URL` 指向真实后端根地址
3. 当前 actor 档案具备 `profileCompletion >= 70`

## 5. 本轮 verify 样本特殊约束

1. 必须固定同一个 `userId`
2. 必须固定两条 `verificationId`
  - 第一条：被拒绝
  - 第二条：重提后通过
3. 必须同时保留：
  - actor 侧最终 `verify/status`
  - admin 侧两条审核详情
  - `identity_verification` 表两条记录
  - `identity_verification_owner` 归属记录
  - `schema_release_history` 中本轮 migration 记录
  - `admin_operation_log` 中 `reject / approve` 两条动作

## 6. 联调前必须写实的 8 个值

1. 当前环境名
2. Spring profile
3. `NACOS_ENABLED` 是否开启
4. 后端实际访问地址
5. 后台 `VITE_API_BASE_URL`
6. 小程序 `VITE_API_BASE_URL`
7. 小程序 `VITE_USE_MOCK`
8. 当前 verify 样本 `userId`
