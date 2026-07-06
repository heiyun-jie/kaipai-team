# 00-192 当前阶段小程序全局登录态恢复修复 - 执行记录

## 执行摘要

用户反馈微信开发者工具 Storage 已存在 `kp_token` 和 `kp_user`，但 `pages/mine/index` 顶部仍显示「未登录用户」。本轮已把登录态判断从页面局部收口到全局 `stores/user.ts`：

- `userStore.isLoggedIn / currentUser / hasStoredSession` 在读取前都会先从 Storage 恢复 session。
- `bootstrapSession()` 复用同一个全局 hydration 入口。
- `pages/mine/index` 先用 `userStore.currentUser` 渲染账号头部，已登录无昵称时显示脱敏手机号，只有游客态才显示「未登录用户」。
- `utils/navigation.ts` 不再绕过 store 直接读取 `kp_token / kp_user`，登录门禁统一走全局 store。

## 根因记录

截图事实：

```text
Storage:
  kp_token = eyJ...
  kp_user = {"id":5,"phone":"13782296737","role":1,...}

页面:
  pages/mine/index
  顶部显示「未登录用户」
```

代码根因：

```text
stores/user.ts
  token = ref(null)
  userInfo = ref(null)
  isLoggedIn = computed(() => !!token.value)

pages/mine/index
  isVisitor = computed(() => !userStore.isLoggedIn)
  displayName = ref('未登录用户')
```

`kp_token / kp_user` 已在 Storage 中，但 Pinia store 初始化时没有全局读取 Storage。只有页面主动调用 `initFromStorage()` 或 `bootstrapSession()` 后，内存 token 才会恢复。因此页面首次计算 `isVisitor` 时可能拿到 `false` 登录态，并停留在本地默认「未登录用户」。

## 红灯记录

实现前执行：

```powershell
node .sce\specs\00-192-current-phase-miniapp-global-session-state-fix\scripts\verify-miniapp-global-session-state.mjs
```

结果：失败，符合预期。

失败项：

- `user store has global storage hydration helper`
- `user store logged-in computed hydrates before reading token`
- `user store exposes hydrated current session state`
- `bootstrap session reuses global storage hydration`
- `mine page consumes global session state`
- `mine page account header falls back to stored phone before visitor copy`
- `mine page gates actions with global session state`
- `navigation session guard uses user store`
- `dist/build` 与 `dist/dev` 产物层检查

## 实现记录

`kaipai-frontend/src/stores/user.ts`：

- 新增 `storageHydrated` 标记。
- 新增 `ensureStorageHydrated()`，统一读取 `kp_token / kp_user`。
- `isLoggedIn / currentUser / hasStoredSession` 读取前都会调用 `ensureStorageHydrated()`。
- `bootstrapSession()` 改为复用 `ensureStorageHydrated()`。
- `syncVerificationStatus / syncInviteStats / syncLevelInfo / syncActorRuntimeState / ensureInviteInfo` 进入前也先确保全局 session 已恢复。

`kaipai-frontend/src/pages/mine/index.vue`：

- 新增 `profileUser = computed(() => userStore.currentUser)`。
- `isVisitor` 改为 `!userStore.hasStoredSession`。
- 头部在 `bootstrapSession()` 前先用 `profileUser` 渲染。
- `applyMineUserHeader()` 的最终 fallback 从「未登录用户」改为 `用户 ${user.id}`，已登录无昵称时优先显示脱敏手机号。
- `requireLoginForMineAction()` 使用 `userStore.hasStoredSession && userStore.currentUser`。

`kaipai-frontend/src/utils/navigation.ts`：

- 移除直接 `getToken / getUserInfo` 的并行门禁。
- `ensureUserSession()` 和 `ensureUserSessionReady()` 统一通过 `userStore.ensureStorageHydrated()` / `bootstrapSession()` 判断。

脚本更新：

- 新增 `00-192` 专项脚本：`verify-miniapp-global-session-state.mjs`。
- 更新 `00-190` 脚本中个人中心游客态检查，从旧 `userStore.isLoggedIn` 口径改为 `userStore.hasStoredSession` 口径。

## 验证记录

已执行：

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check
```

结果：通过。

已执行：

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run build:mp-weixin
```

结果：通过，postbuild 已同步到 `dist/dev/mp-weixin`。输出仍包含既有 uni-app 新版本提示、Sass legacy JS API warning 与 empty chunk `types/project` warning。

已执行：

```powershell
node .sce\specs\00-192-current-phase-miniapp-global-session-state-fix\scripts\verify-miniapp-global-session-state.mjs
```

结果：通过。源码层和 `dist/build / dist/dev` 产物层均确认个人中心使用全局 session state。

已执行：

```powershell
node .sce\specs\00-190-current-phase-miniapp-login-back-and-mine-review-supplement\scripts\verify-miniapp-login-back-and-mine-supplement.mjs
```

结果：通过。确认个人中心仍允许游客浏览，不会在 tab entry 直接跳登录。

已执行：

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run audit:mp-package
```

结果：通过。

```text
Total build size: 763.94 KB
main      524.70 KB / 2 MB
pkg-card  211.01 KB / 2 MB
pkg-tools 28.23 KB / 2 MB
```

已执行：

```powershell
node .sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs
node .sce\specs\00-188-current-phase-miniapp-review-compliance-audit-fix\scripts\verify-miniapp-review-compliance-audit.mjs
node .sce\specs\00-191-current-phase-miniapp-verify-status-500-fix\scripts\verify-miniapp-verify-status-500-fix.mjs
```

结果：全部通过。

已执行：

```powershell
git diff --check
git -C kaipai-frontend diff --check
```

结果：通过；仅保留 Windows 工作区 LF/CRLF 提示。
