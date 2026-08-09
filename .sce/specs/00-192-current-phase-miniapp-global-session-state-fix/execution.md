# 00-192 当前阶段小程序全局登录态恢复修复 - 执行记录

> **分期说明**：主体章节记录 00-199 重构前的首次修复与当时验证，`profileUser / applyMineUserHeader / requireLoginForMineAction` 是历史实现，不是当前合同。00-199 后的等价语义与 2026-07-27 最新门禁结果见文末。

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

## 2026-07-27 T7：00-199 后 Mine 等价语义

当前 `pages/mine/index.vue` 不再维护页面级账号头部副本：

- `isVisitor = !userStore.hasStoredSession`、`currentUser = userStore.currentUser` 直接消费全局 Store。
- `displayName / avatar / accountMeta` 由 computed 派生；游客当前可见文案为“未登录”，已登录无昵称时回落到脱敏手机号或“演员用户”。
- `openAccountCapability()` 在用户触发具体账号能力时执行登录 / 角色门禁。
- `hydrateMinePage()` 只加载职业资料摘要，失败只写 `hubError`；不会清空 session，也不会把头部切为游客态。
- Mine 当前不读取实名、邀请或等级运行态。

`verify-miniapp-global-session-state.mjs` 已从退场 helper 名称改为上述等价行为断言。最新构建后的源码、`dist/build` 与 `dist/dev` 共 `10/10 PASS`。

## 2026-07-27 最新组合门禁

- `npm run type-check`、`npm run build:mp-weixin`：通过。
- `00-192`：`10/10 PASS`；`00-191`：`17/17 PASS`；`00-187`：`15/15 PASS`。
- `00-190`：9 项失败，均绑定 00-199 已退场的旧 Mine helper / class 结构；这是旧 Spec 门禁与当前主线漂移，不能通过恢复旧页面结构消除。
- `00-188`：1 项失败，原因是 postbuild 主动将固定 `dist/dev` 的 `urlCheck` 设为 `false`；源码与 `dist/build` 为 `true`。
- `npm run audit:mp-package`：首个已知阻断为 `actor-asset.js` 中构建注入的 `http://127.0.0.1:8010`。
- `npm run audit:steering`：通过。

当前会话所有权补充：

- Store 使用 `ActorSessionSnapshot(token + userId + revision)` 拒绝 bootstrap、实名、等级和邀请统计的跨账号旧响应。
- 请求层使用独立 `AuthSessionSnapshot(token + auth revision)`；只有仍属于当前会话的 401 可以统一清理 Storage + Pinia 并跳登录。
- 延迟 Promise 回归已覆盖“A 请求挂起 -> B 登录 -> A 晚到 401”不影响 B，以及 B 当前 401 正常清理并跳转一次。

以上结果取代主体章节中“全部通过”作为当前工作树结论；主体结果仅代表其执行日期的历史状态。

## 2026-08-07 `mine-v2` 入口门禁等价语义恢复

- Mine 改版回归已修复：当前页面重新使用 `isVisitor = !userStore.hasStoredSession`、`currentUser = userStore.currentUser`。
- 已登录无昵称时恢复 `formatPhone(currentUser.phone)` fallback，只有游客显示“未登录用户”。
- 资料卡等六个账号入口通过 `requireLoginForMineAction / openAccountCapability` 消费同一全局 Session 状态。
- 游客入口使用单次 `navigateTo('/pages/login/index')`，不再先创建受保护页并触发其 `reLaunch` 守卫。
- `verify-miniapp-global-session-state.mjs` 已按当前 `mine-v2` 等价语义更新，源码、`dist/build`、`dist/dev` 共 `10/10 PASS`。
- 00-190 旧结构漂移已同时修复，当前专项门禁全部通过；00-188 与包体审计仍保留 2026-07-27 已记录的本地环境阻断。
