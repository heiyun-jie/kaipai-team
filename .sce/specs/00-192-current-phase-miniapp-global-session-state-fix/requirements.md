# 00-192 当前阶段小程序全局登录态恢复修复

## 1. 概述

用户在微信开发者工具中已登录，`Storage` 已存在 `kp_token` 与 `kp_user`，但 `pages/mine/index` 仍显示「未登录用户」。这说明登录态判断没有统一放在全局：页面首次渲染时读取的是 Pinia store 的内存默认值，而不是持久化 session。

本轮修复目标是把登录态恢复和判断收口到 `stores/user.ts`，页面只消费全局状态，不再各自基于本地默认值推断登录态。

## 2. 用户故事

作为已登录用户，我重新打开小程序或切回「我的」页时，只要本地 `Storage` 中仍有有效 `kp_token / kp_user`，页面就应显示我的账号信息，而不是「未登录用户」。

作为开发者，我需要一个统一的全局登录态入口，避免首页、历史页、个人中心、详情页各自判断时出现不一致。

## 3. 功能需求

### 3.1 全局 session 初始化

**描述**：`useUserStore()` 创建后必须能从 `Storage` 恢复登录态。`isLoggedIn` 应基于“已全局初始化后的 token”判断，不能依赖页面主动调用 `bootstrapSession()` 后才变为 true。

**验收标准**：

- WHEN `Storage` 中存在 `kp_token` THEN `userStore.isLoggedIn` 在页面读取前能够基于全局恢复后的 token 返回 true。
- WHEN `Storage` 中存在 `kp_user` THEN `userStore.userInfo` 能恢复为该用户对象。
- WHEN `Storage` 中缺少 token THEN 全局登录态为游客态。
- WHEN `Storage` 中 `kp_user` 解析失败 THEN 不影响 token 的登录态判断，但用户详情可后续通过 `/api/user/me` 补齐。

### 3.2 个人中心消费全局状态

**描述**：`pages/mine/index` 不再维护一套独立“未登录用户”判断。进入页面时先执行全局 session 恢复，再根据全局 store 的 `currentUser` / `hasStoredSession` 渲染账号头部。

**验收标准**：

- WHEN 已登录且 `kp_user` 有 `id=5, phone=137...` THEN 个人中心头部不能显示「未登录用户」。
- WHEN 已登录用户没有昵称 THEN 个人中心头部显示脱敏手机号。
- WHEN 是游客 THEN 个人中心仍展示游客态完整页面，并且点击账号相关操作才进入登录页。
- WHEN 附属运行态同步失败 THEN 不得重置账号头部为游客态。

### 3.3 登录门禁复用全局判断

**描述**：账号相关跳转、强登录页面的判断应优先使用 `userStore.bootstrapSession()`，避免绕过全局 store 直接读 storage 形成第二套口径。

**验收标准**：

- WHEN action 需要登录 THEN 使用全局 store 恢复后的 session 判断是否登录。
- WHEN token 存在但 user role 未恢复 THEN 允许通过 `bootstrapSession()` 拉取 `/api/user/me` 补齐用户。
- WHEN session 无效或接口返回 401 THEN 清理本地 session 并进入登录页。

### 3.4 回归验证

**描述**：新增专项脚本防止本问题回退。

**验收标准**：

- WHEN `isLoggedIn` 仍只是 `computed(() => !!token.value)` 且没有全局 hydrate THEN 脚本失败。
- WHEN `mine` 页仍只用本地 `displayName='未登录用户'` 而没有全局 session 头部派生 THEN 脚本失败。
- WHEN `ensureUserSession` 仍绕过 store 直接读 storage THEN 脚本失败。
- WHEN 构建产物未同步到 `dist/dev/mp-weixin` THEN 产物层检查失败。

## 4. 非功能需求

- 不恢复首页强制登录；审核整改要求的游客可浏览继续保留。
- 不新增 mock 登录态。
- 不改变 token 存储键名 `kp_token` 和用户存储键名 `kp_user`。
- 不把后端 401 静默吞掉；无效 session 仍应清理并引导登录。

## 5. 约束条件

- 以 `stores/user.ts` 作为唯一登录态事实源。
- 页面只消费 store 暴露的登录态 / 用户信息，不再自行创造并行判断。
- 保持 `00-187 / 00-188 / 00-190 / 00-191` 审核整改验收继续通过。
