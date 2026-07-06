# 00-192 当前阶段小程序全局登录态恢复修复 - 任务拆解

## T1 根因定位与 Spec

- [x] 确认截图中 `kp_token / kp_user` 已存在但 `pages/mine/index` 显示「未登录用户」。
- [x] 定位 `stores/user.ts` 的 `isLoggedIn` 只读内存 `token.value`，而 store 创建时未全局恢复 storage。
- [x] 新增 `00-192` requirements / design / tasks。

## T2 红灯验收

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [x] 新增 `verify-miniapp-global-session-state.mjs`。
- [x] 实现前执行脚本并确认失败。

## T3 全局 Store 修复

**Validates: Requirements 3.1**

- [x] 在 `stores/user.ts` 增加 `ensureStorageHydrated()`。
- [x] 让 `isLoggedIn / currentUser / hasStoredSession` 基于全局 hydration。
- [x] 让 `bootstrapSession()` 复用全局 hydration，不再形成页面级初始化依赖。

## T4 个人中心消费全局登录态

**Validates: Requirements 3.2**

- [x] 修改 `pages/mine/index.vue` 的 `isVisitor / userIdText / roleBadgeText / profileSubtitle / requireLoginForMineAction`。
- [x] 已登录无昵称时显示脱敏手机号。
- [x] 附属 runtime sync 失败不重置账号头部。

## T5 导航门禁收口

**Validates: Requirements 3.3**

- [x] 修改 `utils/navigation.ts`，同步和异步 session 判断都经由 `userStore`。
- [x] 保持无效 session 清理和登录跳转行为。

## T6 验证与产物同步

**Validates: Requirements 3.4**

- [x] 执行 `verify-miniapp-global-session-state.mjs`。
- [x] 执行 `npm run type-check`。
- [x] 执行 `npm run build:mp-weixin` 并确认同步到 `dist/dev/mp-weixin`。
- [x] 执行 `npm run audit:mp-package`。
- [x] 执行 00-187 / 00-188 / 00-190 / 00-191 专项脚本。
- [x] 更新 `.sce/specs/README.md` 与 `.sce/specs/spec-code-mapping.md`。
