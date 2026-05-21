# 00-61 设计说明

## 1. 设计原则

- 已完成真实环境闭环的 auth 主链只保留单事实源，不再维持前端演示态双轨
- 收口范围只限 auth 主链，不顺手扩散到上传、invite、微信真实配置或正式短信
- 运行时门禁、页面提示和实际 API 实现必须一起对齐，不能只删调用点
- 若环境不可用，优先显式报错，不再继续伪造“看起来能登录”的假联通

## 2. 当前阶段收口边界

| 模块 | 当前阶段策略 | 本轮不做 |
|------|--------------|----------|
| `src/api/auth.ts` | `sendCode / login / register / wechat-login / user.me / user.role` 全部只走真实接口 | 不再保留 auth mock service 分流 |
| `src/stores/user.ts` | `bootstrapSession()` 只认 token + `/api/user/me` | 不再保留 mock 会话恢复 |
| `src/utils/runtime.ts` | `VITE_USE_MOCK=true` 但缺少 baseUrl 时，明确阻塞 auth 域 | 不删除其他能力域的 `useMock()` 用途 |
| `src/pages/login/index.vue` | 微信入口与开发验证码展示都按真实 auth 语义处理 | 不推进微信真实配置与正式短信 |
| `src/mock/service.ts` / `src/mock/database.ts` | 删除整体文件 | 不重建新的 auth 演示态假数据 |

## 3. 实现方案

### 3.1 API 层

- `auth.ts` 删除 `@/mock/service` import 与所有 `useMock()` 分支
- `sendSmsCode()` 统一调用 `POST /api/auth/sendCode`
- `loginByPhone()` 统一调用 `POST /api/auth/login`
- `registerByPhone()` 统一调用 `POST /api/auth/register`
- `loginByWechat()` 统一调用 `POST /api/auth/wechat-login`
- `getUserInfo()` 统一调用 `GET /api/user/me`
- `updateUserRole()` 统一调用 `PUT /api/user/role`

### 3.2 Store 与页面

- `stores/user.ts`
  - 删除 `bootstrapSession()` 中基于 `useMock()` 的早退分支
  - 删除已失效的 `syncMockSession()`
- `pages/login/index.vue`
  - 删除对 `useMock()` 的 auth 展示依赖
  - `sendSmsCode()` 只要真实返回验证码，就直接展示开发态验证码弹窗
  - 微信入口显隐完全跟随 `canUseWechatAuth()` 与 `getWechatAuthBlocker()`

### 3.3 Runtime 门禁

- `runtime.ts` 保留 `useMock()` 给非 auth 场景使用
- `getRuntimeConfigBlocker()` 新增一条显式分支：
  - 当 `VITE_USE_MOCK=true` 且缺少 `VITE_API_BASE_URL` 时，明确提示“auth 显式 mock 已退场，登录/会话不可验证”
- `canUseWechatAuth()` 不再因为 `useMock()` 直接返回 `true`
- `getWechatAuthBlocker()` 只认真实运行时 blocker 与 `VITE_ENABLE_WECHAT_AUTH`

### 3.4 Mock 文件清理

- 删除 `src/mock/service.ts`
- 删除 `src/mock/database.ts`
- 以全文搜索确认前端源码已无 `@/mock/service`、`@/mock/database` 引用

## 4. 风险与约束

### 4.1 本轮完成后，auth 域不再支持“纯前端演示”

- 若本地未配置 `VITE_API_BASE_URL`，登录页与请求层都会直接报运行时阻塞
- 这是预期行为，目的就是阻止继续把假登录当成真实联调

### 4.2 显式 mock 总闸仍然存在

- `useMock()` 仍被上传和少量非 auth helper 使用
- 这不代表 auth 主链还能继续走 mock；后续若继续清理其他域，应另起 spec

## 5. 影响文件

- `.sce/specs/00-61-current-phase-auth-explicit-mock-retirement/requirements.md`
- `.sce/specs/00-61-current-phase-auth-explicit-mock-retirement/design.md`
- `.sce/specs/00-61-current-phase-auth-explicit-mock-retirement/tasks.md`
- `.sce/specs/00-61-current-phase-auth-explicit-mock-retirement/execution.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/execution/login-auth/README.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/login-auth-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `kaipai-frontend/src/api/auth.ts`
- `kaipai-frontend/src/stores/user.ts`
- `kaipai-frontend/src/utils/runtime.ts`
- `kaipai-frontend/src/pages/login/index.vue`
- `kaipai-frontend/src/mock/service.ts`
- `kaipai-frontend/src/mock/database.ts`
