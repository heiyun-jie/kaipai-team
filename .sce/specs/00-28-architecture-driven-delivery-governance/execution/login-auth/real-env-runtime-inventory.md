# 登录鉴权真实环境运行时清单

## 1. 目的

本清单用于在开始 login-auth 真实环境联调前，先确认“小程序、后台、后端、微信配置”是否指向同一套环境。

如果这一页没有先确认，后续看到的“微信按钮可见 / 短信可发 / `user.me` 可用”很容易来自不同环境，结论无效。

## 2. 服务端运行时

### 2.1 必查文件

- `kaipaile-server/src/main/resources/bootstrap.yml`
- `kaipaile-server/src/main/resources/application.yml`
- `kaipaile-server/src/main/resources/application-dev.yml`

### 2.2 当前仓内已知事实

- 默认 profile 更接近 `dev`
- `application.yml` 定义 `server.servlet.context-path=/api`
- `application-dev.yml` 覆盖 `server.port=8010`
- `application.yml` 已暴露：
  - `wechat.miniapp.app-id=${WECHAT_MINIAPP_APP_ID:}`
  - `wechat.miniapp.app-secret=${WECHAT_MINIAPP_APP_SECRET:}`

### 2.3 联调前必须确认

- 当前服务真实 profile
- `NACOS_ENABLED` 是否开启
- 后端真实访问入口
- `WECHAT_MINIAPP_APP_ID` 是否已配置
- `WECHAT_MINIAPP_APP_SECRET` 是否已配置

## 3. 小程序前端运行时

### 3.1 必查文件

- `kaipai-frontend/.env`
- `kaipai-frontend/.env.example`
- `kaipai-frontend/src/utils/runtime.ts`
- `kaipai-frontend/src/pages/login/index.vue`

### 3.2 当前仓内已知事实

- `.env` 当前显式写明：
  - `VITE_API_BASE_URL=http://101.43.57.62`
  - `VITE_USE_MOCK=false`
  - `VITE_ENABLE_WECHAT_AUTH=false`
- `runtime.ts` 当前规则：
  - `VITE_USE_MOCK='false'` 时强制关闭 mock
  - `VITE_USE_MOCK='true'` 时强制开启 mock
  - 未显式配置且缺少 `VITE_API_BASE_URL` 时，会自动回退 mock
- `App` 启动时会对以下场景直接弹阻塞提示：
  - 缺少 `VITE_API_BASE_URL` 且未显式配置 mock
  - `VITE_USE_MOCK=false` 但缺少 `VITE_API_BASE_URL`

### 3.3 联调前必须确认

- 当前小程序 `VITE_API_BASE_URL`
- 当前小程序 `VITE_USE_MOCK`
- 当前小程序 `VITE_ENABLE_WECHAT_AUTH`
- 微信按钮是否应显示
- 当前运行时是否已出现阻塞提示

## 4. 后台运行时

### 4.1 必查文件

- `kaipai-admin/.env.development`
- `kaipai-admin/.env.test`
- `kaipai-admin/.env.production`
- `kaipai-admin/src/utils/request.ts`

### 4.2 当前仓内已知事实

- 开发环境默认走 `/api` 代理
- `.env.test` 当前指向 `http://localhost:8080/api`
- 后台本轮不新增独立登录治理页，但它承担运行时台账和联调准入记录

### 4.3 联调前必须确认

- 后台当前 `VITE_API_BASE_URL`
- 后台是否与后端命中同一环境
- 后台账号是否具备登录相关治理与日志查看能力

## 5. 登录样本链必须写清的 10 个值

1. 当前环境名
2. Spring profile
3. `NACOS_ENABLED`
4. 后端真实入口
5. 后端微信配置是否齐全
6. 小程序 `VITE_API_BASE_URL`
7. 小程序 `VITE_USE_MOCK`
8. 小程序 `VITE_ENABLE_WECHAT_AUTH`
9. 后台 `VITE_API_BASE_URL`
10. 当前样本是否允许验证微信真实登录

## 6. 最小确认结论模板

```md
- 环境：
- Spring profile：
- NACOS_ENABLED：
- 后端实际入口：
- 后端微信配置：
  - WECHAT_MINIAPP_APP_ID：
  - WECHAT_MINIAPP_APP_SECRET：
- 小程序 baseURL：
- 小程序 mock 开关：
- 小程序微信开关：
- 后台 baseURL：
- login-auth 联调结论：
  - 小程序与后端同环境：是 / 否
  - 后台与后端同环境：是 / 否
  - 当前是否允许验证微信真实登录：是 / 否
  - 当前是否存在运行时阻塞提示：是 / 否
```
