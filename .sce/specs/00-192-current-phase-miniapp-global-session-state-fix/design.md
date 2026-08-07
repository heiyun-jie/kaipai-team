# 00-192 当前阶段小程序全局登录态恢复修复 - 技术设计

## 1. 设计结论

本轮采用全局 store 收口方案：

```text
utils/auth
  -> 负责 storage get/set/remove、AuthSessionSnapshot 与统一 clearSession

utils/request
  -> 请求发出时捕获 auth token + revision
  -> 只允许当前请求会话的 401 清 Storage / Pinia 并跳登录

stores/user
  -> 新增 ensureStorageHydrated()
  -> store 初始化时恢复 token/user
  -> isLoggedIn / currentUser / hasStoredSession 都基于已恢复的全局状态
  -> bootstrapSession() 复用同一入口，不再让页面各自 init

pages/mine/index
  -> isVisitor / currentUser computed 直接消费全局状态
  -> hydrateMinePage 只加载职业资料摘要
  -> 仅游客态显示「未登录用户」

utils/navigation
  -> ensureUserSession / ensureUserSessionReady 统一通过 userStore.bootstrapSession()
```

_Requirements: 3.1, 3.2, 3.3_

## 2. 全局 Store 设计

在 `stores/user.ts` 中新增状态：

```ts
let storageHydrated = false;
```

新增方法：

```ts
function ensureStorageHydrated(): void
```

职责：

- 只执行一次 storage 读取。
- 读取 `kp_token` 到 `token.value`。
- 读取 `kp_user` 到 `userInfo.value`。
- 不访问网络。
- 解析失败的 `kp_user` 保持 `null`，后续由 `bootstrapSession()` 通过 `/api/user/me` 补齐。

`isLoggedIn` 改为依赖已恢复状态：

```ts
const isLoggedIn = computed(() => {
  ensureStorageHydrated();
  return !!token.value;
});
```

同时暴露：

```ts
const currentUser = computed(() => {
  ensureStorageHydrated();
  return userInfo.value;
});

const hasStoredSession = computed(() => {
  ensureStorageHydrated();
  return !!token.value;
});
```

_Requirements: 3.1_

### 2.1 请求层 401 会话所有权

`utils/auth.ts` 使用独立单调 `auth revision` 形成 `AuthSessionSnapshot(token + revision)`。`setToken()` 和 `removeToken()` 都推进 revision；`clearSession(expectedSession)` 仅在快照仍为当前会话时删除 `kp_token / kp_user`，并通过已注册 handler 同步清空 Pinia 内存。

`utils/request.ts` 在发请求时捕获 auth snapshot，并把它带到 401 处理。账号 A 的请求挂起、账号 B 登录、A 的 401 晚到时，revision 已变化，旧 401 不执行清理或登录跳转；B 自己的 401 则先完成 Storage + Pinia 清理，再跳登录。

该 auth revision 只治理请求层副作用；`stores/user.ts` 的 session revision 继续治理 bootstrap 和业务 GET / POST 的异步写回，两者不合并为循环依赖。

_Requirements: 3.3_

## 3. 个人中心设计

`pages/mine/index` 继续允许游客浏览，但登录态显示只跟随全局 store。00-199 重构后的当前结构为：

- `isVisitor = computed(() => !userStore.hasStoredSession)`。
- `currentUser = computed(() => userStore.currentUser)`。
- `displayName / avatar / accountMeta` 都由 `isVisitor / currentUser` 派生，不维护页面可变账号副本。
- `openAccountCapability()` 通过 `isVisitor` 判断，必要时调用 `goLogin()`。
- `hydrateMinePage()` 的职业资料摘要失败只写入 `hubError`，不清空 Store session。

已登录页面的 `displayName` 必须按昵称、脱敏手机号、账号兜底文案依次派生，不得因为摘要接口失败退回游客文案。

_Requirements: 3.2_

## 4. 导航门禁设计

`utils/navigation.ts` 的 `ensureUserSession()` 原来直接读取 storage，形成与 store 并行的登录态判断。本轮改为：

```ts
export function ensureUserSession(expectedRole?: UserRole): UserInfo | null {
  const userStore = useUserStore();
  userStore.ensureStorageHydrated();
  const user = userStore.currentUser;
  ...
}
```

异步版本继续使用 `bootstrapSession()`。

_Requirements: 3.3_

## 5. 验证设计

新增脚本：

```text
.sce/specs/00-192-current-phase-miniapp-global-session-state-fix/scripts/verify-miniapp-global-session-state.mjs
```

检查：

- `stores/user.ts` 存在 `ensureStorageHydrated()`。
- `isLoggedIn / currentUser / hasStoredSession` 都调用全局 hydration。
- `bootstrapSession()` 使用 `ensureStorageHydrated()`。
- `pages/mine/index.vue` 使用 `userStore.hasStoredSession` / `userStore.currentUser`。
- `pages/mine/index.vue` 使用当前 `isVisitor / currentUser` computed 派生头部，不要求已退场的 `profileUser / applyMineUserHeader()`。
- `utils/navigation.ts` 不再直接 `getToken/getUserInfo` 绕过 store。
- `utils/auth.ts / utils/request.ts` 对 401 使用请求发起 auth snapshot 条件失效；00-191 行为门禁覆盖旧账号 401 与当前账号 401 两个方向。
- `dist/build/mp-weixin` 与 `dist/dev/mp-weixin` 均包含更新后的 mine bundle。

必须执行：

1. `node .sce/specs/00-192-current-phase-miniapp-global-session-state-fix/scripts/verify-miniapp-global-session-state.mjs`
2. `cd kaipai-frontend && npm run type-check`
3. `cd kaipai-frontend && npm run build:mp-weixin`
4. `cd kaipai-frontend && npm run audit:mp-package`
5. `node .sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/scripts/verify-miniapp-review-login-gate.mjs`
6. `node .sce/specs/00-188-current-phase-miniapp-review-compliance-audit-fix/scripts/verify-miniapp-review-compliance-audit.mjs`
7. `node .sce/specs/00-190-current-phase-miniapp-login-back-and-mine-review-supplement/scripts/verify-miniapp-login-back-and-mine-supplement.mjs`
8. `node .sce/specs/00-191-current-phase-miniapp-verify-status-500-fix/scripts/verify-miniapp-verify-status-500-fix.mjs`

_Requirements: 3.4_
