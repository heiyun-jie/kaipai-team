# 会员与模板真实环境运行时清单

## 1. 目的

本清单用于在开始 membership 真实环境联调前，先确认“后台、后端、小程序”是否命中同一套模板与会员事实环境。

如果这一页没有先确认，后续看到的“后台已发布模板 / 小程序已显示会员权益 / 公开页主题已变化”很容易来自不同环境，结论无效。

## 2. 服务端运行时

### 2.1 必查文件

- `kaipaile-server/src/main/resources/bootstrap.yml`
- `kaipaile-server/src/main/resources/application.yml`
- `kaipaile-server/src/main/resources/application-dev.yml`

### 2.2 当前仓内已知事实

- 默认 profile 更接近 `dev`
- `application.yml` 定义 `server.servlet.context-path=/api`
- `application-dev.yml` 覆盖 `server.port=8010`
- membership 联调主链依赖：
  - `/api/level/info`
  - `/api/card/scene-templates`
  - `/api/card/config`
  - `/api/card/personalization`
  - `/api/fortune/report`
  - `/api/ai/quota`
  - `/api/actor/profile/*`

### 2.3 联调前必须确认

- 当前服务真实 profile
- `NACOS_ENABLED` 是否开启
- 后端真实访问入口
- 数据库是否为目标模板 / 会员验证环境
- 是否已执行与 membership / template 相关的 migration

## 3. 小程序前端运行时

### 3.1 必查文件

- `kaipai-frontend/.env`
- `kaipai-frontend/.env.example`
- `kaipai-frontend/src/utils/runtime.ts`
- `kaipai-frontend/src/utils/personalization.ts`

### 3.2 当前仓内已知事实

- `.env` 当前显式写明：
  - `VITE_API_BASE_URL=http://101.43.57.62`
  - `VITE_USE_MOCK=false`
  - `VITE_ENABLE_WECHAT_AUTH=false`
- `project.config.json` 当前 `appid=wxd38339082a9cfa4e`
- `runtime.ts` 当前规则：
  - `VITE_USE_MOCK='false'` 时强制关闭 mock
  - `VITE_USE_MOCK='true'` 时强制开启 mock
  - 未显式配置且缺少 `VITE_API_BASE_URL` 时，会自动回退 mock
- membership 主链当前依赖真接口能力：
  - `verify`
  - `invite`
  - `level`
  - `card`
  - `ai`
  - `fortune`
  - `actor`

### 3.3 联调前必须确认

- 当前小程序 `VITE_API_BASE_URL`
- 当前小程序 `VITE_USE_MOCK`
- 当前微信开发者工具登录账号是否具备 `wxd38339082a9cfa4e` 开发者权限
- 当前是否出现运行时阻塞提示
- 当前 actor-card / detail / invite 是否都命中同一套 personalization 结果

## 4. 后台运行时

### 4.1 必查文件

- `kaipai-admin/.env.development`
- `kaipai-admin/.env.test`
- `kaipai-admin/.env.production`
- `kaipai-admin/src/utils/request.ts`

### 4.2 当前仓内已知事实

- 开发环境默认走 `/api` 代理
- `.env.test` 当前指向 `http://localhost:8080/api`
- membership / template 治理主链依赖：
  - `/membership/products`
  - `/membership/accounts`
  - `/content/templates`

### 4.3 联调前必须确认

- 后台当前 `VITE_API_BASE_URL`
- 后台是否与后端命中同一环境
- 后台账号是否具备会员产品、会员账户、模板发布 / 回滚相关权限

## 5. membership 样本链必须写清的 11 个值

1. 当前环境名
2. Spring profile
3. `NACOS_ENABLED`
4. 后端真实入口
5. 后台 `VITE_API_BASE_URL`
6. 小程序 `VITE_API_BASE_URL`
7. 小程序 `VITE_USE_MOCK`
8. 样本 actorUserId
9. 样本 membershipAccountId
10. 样本 templateId / publishLogId
11. 当前样本是否覆盖发布 / 回滚链路

## 6. 最小确认结论模板

```md
- 环境：
- Spring profile：
- NACOS_ENABLED：
- 后端实际入口：
- 后台 baseURL：
- 小程序 baseURL：
- 小程序 mock 开关：
- actorUserId：
- membershipAccountId：
- templateId：
- publishLogId：
- membership 联调结论：
  - 后台与后端同环境：是 / 否
  - 小程序与后端同环境：是 / 否
  - 当前是否覆盖模板发布 / 回滚链路：是 / 否
  - 当前是否存在运行时阻塞提示：是 / 否
```
