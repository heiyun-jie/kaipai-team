# 邀请裂变真实环境运行时清单

## 1. 目的

本清单用于在开始 invite 真实环境联调前，先确认“三端到底请求哪一套环境”。

如果这一页没有先确认，后续看到的 `inviteCode / referral_record / grant` 很容易来自不同环境，结论无效。

## 2. 服务端运行时

### 2.1 应用基础配置

- 文件：
  - `kaipaile-server/src/main/resources/bootstrap.yml`
  - `kaipaile-server/src/main/resources/application.yml`
  - `kaipaile-server/src/main/resources/application-dev.yml`
- 当前仓库默认值：
  - `spring.profiles.active=dev`
  - `application.yml` 定义 `server.servlet.context-path=/api`
  - `application-dev.yml` 覆盖 `server.port=8010`

### 2.1.1 当前默认本地生效链

- 在未额外覆盖、且 `NACOS_ENABLED=false` 的情况下
- 当前仓库默认更接近：
  - `bootstrap.yml` 先激活 `dev`
  - 再加载 `application.yml`
  - 再叠加 `application-dev.yml`
- 所以源码默认本地入口应按：
  - `http://host:8010/api`
  - 而不是单看 `application.yml` 的 `8080`

### 2.1.2 当前源码内已看到的运行时资源

- `application-dev.yml` 中已定义：
  - MySQL datasource
  - Redis
  - COS
  - `server.port=8010`
- 这些值属于真实运行时配置
- 联调文档只记录“要核对哪些项”，不要把账号密钥再抄到验收文档里

### 2.2 Nacos 开关

- `bootstrap.yml` 中：
  - `spring.cloud.nacos.config.enabled=${NACOS_ENABLED:false}`
- 结论：
  - 默认不启用 Nacos
  - 但一旦外部环境把 `NACOS_ENABLED=true`，DB / Redis / 其他 profile 配置就可能被远端覆盖
- 远端配置入口：
  - `101.43.57.62:8848`

### 2.3 联调前必须确认

- 当前服务是否真的以 `dev` profile 启动
- 当前服务是否启用了 `NACOS_ENABLED=true`
- 当前真实生效的数据源是不是本地 `application.yml` 之外的远端配置
- 当前真实生效端口是不是 `application-dev.yml` 的 `8010`
- 当前服务外部访问地址是不是直接 `8010/api`，还是又被反向代理成了其他端口

## 3. 后台管理端运行时

### 3.1 本地 dev 行为

- 文件：
  - `kaipai-admin/vite.config.ts`
  - `kaipai-admin/src/utils/request.ts`
- 当前本地 dev：
  - Vite 端口：`5174`
  - 默认代理前缀：`/api`
  - 代理目标：`http://127.0.0.1:8010`
- 所以本地浏览器访问：
  - `http://localhost:5174`
- 实际后台请求：
  - `http://127.0.0.1:8010/api/...`

### 3.2 `VITE_API_BASE_URL` 覆盖规则

- `src/utils/request.ts` 中：
  - `baseURL: import.meta.env.VITE_API_BASE_URL || '/api'`
- 结论：
  - 如果没配 `VITE_API_BASE_URL`，后台走本地 `/api` 再经 Vite 代理转发
  - 如果显式配置了 `VITE_API_BASE_URL`，则直接请求该地址，Vite 代理不再是唯一入口

### 3.3 联调前必须确认

- 当前后台页面到底是走 `http://127.0.0.1:8010/api`，还是走外部 `VITE_API_BASE_URL`
- 当前登录和邀请治理页是否与后端同一环境

## 4. 小程序前端运行时

### 4.1 真接口 / mock 总开关

- 文件：
  - `kaipai-frontend/src/utils/runtime.ts`
- 判定规则：
  - `VITE_USE_MOCK='false'` 时，强制关闭 mock
  - `VITE_USE_MOCK='true'` 时，强制开启 mock
  - 未显式配置时，如果 `VITE_API_BASE_URL` 为空，则默认走 mock
- `2026-04-02` 起，`App` 启动时会对以下两类情况给出显式阻塞提示：
  - 未显式配置 `VITE_USE_MOCK` 且缺少 `VITE_API_BASE_URL`
  - `VITE_USE_MOCK='false'` 但缺少 `VITE_API_BASE_URL`

### 4.2 小程序没有本地代理

- 文件：
  - `kaipai-frontend/vite.config.ts`
- 结论：
  - 当前没有像后台那样的 `/api -> 本地服务` Vite 代理
  - 小程序端请求地址直接由 `VITE_API_BASE_URL` 决定

### 4.3 `baseURL` 归一化规则

- 文件：
  - `kaipai-frontend/src/utils/runtime.ts`
  - `kaipai-frontend/src/utils/request.ts`
- 关键逻辑：
  - `normalizeApiBaseUrl()` 只会去掉结尾斜杠
- 联调前必须确认：
  - 当前真实 base URL 是否已经带 `/api`
  - 当前真实 base URL 是否与后端暴露地址完全一致

### 4.4 invite 联调相关远端能力

- `REMOTE_CAPABILITIES` 当前包含：
  - `auth`
  - `verify`
  - `invite`
  - `level`
  - `card`
  - `ai`
  - `fortune`
  - `actor`
- 这意味着：
  - invite 闭环所需的 `auth / verify / invite / level / actor` 可以走真接口
  - 但 `company / project / role / apply` 仍可能继续走 mock
- 所以 invite 联调时不要顺带拿 `project / role` 页面是否是真接口来判断整站环境

### 4.5 一条高风险误配

- 如果：
  - `VITE_USE_MOCK='false'`
  - 且 `VITE_API_BASE_URL` 为空
- 那么：
  - 小程序不会走 mock
  - 但请求会落到相对路径 `/api/...`
- 这类配置经常会表现成“看起来像真接口已开，实际上请求地址不对”

## 5. 当前已知本地入口

### 5.1 后台本地入口

- `http://localhost:5174`
- 通过代理访问：
  - `http://127.0.0.1:8010/api`

### 5.2 后端本地服务入口

- 按当前默认 `dev` 口径，仓库本地入口更接近：
  - `http://127.0.0.1:8010/api`
- `application.yml` 中仍保留：
  - `context-path=/api`
- `application-dev.yml` 中已覆盖：
  - `server.port=8010`
- 历史治理文档也已记录运行态检查地址为：
  - `http://127.0.0.1:8010/api`
- 结论：
  - 当前源码更支持“`8010` 是 `dev` 真实服务端口”这个判断
  - 但真实环境仍要继续确认是否还有反向代理层或外部启动参数覆盖

## 6. 联调前必须写实的 8 个值

每次开始真实环境 invite 联调前，先写清楚：

1. 当前环境名
2. Spring profile
3. `NACOS_ENABLED` 是否开启
4. 后端实际访问地址
5. 后台 `VITE_API_BASE_URL`
6. 小程序 `VITE_API_BASE_URL`
7. 小程序 `VITE_USE_MOCK`
8. 当前 invite 链路是否直接命中 `8010/api`，还是还有额外代理层

## 7. 最小确认结论模板

```md
- 环境：dev / test / prod-like
- Spring profile：
- NACOS_ENABLED：
- 后端实际入口：
- 后台 baseURL：
- 小程序 baseURL：
- 小程序 mock 开关：
- invite 联调结论：
  - 后台与后端同环境：是 / 否
  - 小程序与后端同环境：是 / 否
  - 是否存在代理层：是 / 否
  - 小程序启动时是否出现运行时阻塞提示：是 / 否
```
