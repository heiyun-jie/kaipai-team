# 00-192 当前阶段小程序全局登录态恢复修复 - 技术设计

## 1. 设计结论

本轮采用全局 store 收口方案：

```text
utils/auth
  -> 继续只负责 storage get/set/remove

stores/user
  -> 新增 ensureStorageHydrated()
  -> store 初始化时恢复 token/user
  -> isLoggedIn / currentUser / hasStoredSession 都基于已恢复的全局状态
  -> bootstrapSession() 复用同一入口，不再让页面各自 init

pages/mine/index
  -> onShow 先 bootstrapSession()
  -> 头部由 userStore.currentUser 派生
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

## 3. 个人中心设计

`pages/mine/index` 继续允许游客浏览，但登录态显示只跟随全局 store：

- `isVisitor = computed(() => !userStore.hasStoredSession)`。
- `profileUser = computed(() => userStore.currentUser)`。
- `applyMineUserHeader(user)` 仅接收全局 user。
- `resetVisitorMinePage()` 只在全局确认无 session 时调用。
- `requireLoginForMineAction()` 通过 `userStore.hasStoredSession && userStore.currentUser` 判断，必要时调用 `goLogin()`。

默认 `displayName` 仍可以初始化为「未登录用户」，但进入已登录页面时必须由 `bootstrapSession()` 或 storage user 覆盖为昵称 / 脱敏手机号，不再停留在默认值。

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
- `pages/mine/index.vue` 的 `applyMineUserHeader()` 在 runtime sync 前执行。
- `utils/navigation.ts` 不再直接 `getToken/getUserInfo` 绕过 store。
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
