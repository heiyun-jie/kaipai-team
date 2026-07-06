# 00-187 当前阶段小程序提审登录门禁整改 - 执行记录

## 1. 触发原因

`2026-07-01` 微信小程序「开拍了演员卡」审核未通过。审核反馈指向登录页官方元素混淆、首页首屏强制手机号授权、登录功能点击无响应三类问题。

## 2. 执行记录

### 2.0 远端基线合并说明

提交前同步 `origin/main` 时发现远端已有提交 `0679e09 fix: remove quick phone auth login entry`，该提交删除登录页手机号快速验证入口、删除 `loginByWechat()` 前端调用和 `canUseWechatAuth()` 前端开关，并移除 `wechat-login.png`。

本地 rebase 后采用远端更保守的复审方向：登录页不再暴露 `getPhoneNumber` 手机号快速验证入口，只保留短信验证码登录；同时保留本轮登录返回按钮、首页游客态、个人中心游客态和登录后运行态同步不抢占导航的整改。

### 2.1 红灯验证

新增 `scripts/verify-miniapp-review-login-gate.mjs` 后，先在未整改代码上运行：

```text
node .sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/scripts/verify-miniapp-review-login-gate.mjs
```

结果：失败 `8` 项，覆盖登录页官方 logo、登录页微信品牌文案、首页 `ensureUserSessionReady()` 强制登录、`dist/build` / `dist/dev` 旧产物仍携带风险。

### 2.2 登录页整改

- `kaipai-frontend/src/pages/login/index.vue`
  - 删除手机号快速验证按钮，不再在登录页渲染 `getPhoneNumber` 授权入口。
  - 移除 `/static/icons/wechat-login.png` image 节点及相关 `login-page__wechat*` 样式。
  - 登录页仅保留短信验证码登录路径，避免再次触发「未浏览体验功能服务即要求手机号授权」审核风险。
- `kaipai-frontend/src/utils/runtime.ts`
  - 删除前端手机号快速验证开关 helper。
- `kaipai-frontend/src/api/auth.ts`
  - 删除前端 `loginByWechat()` 调用入口；后端接口不在本轮强制删除。

### 2.3 首页游客态整改

- `kaipai-frontend/src/pages/home/index.vue`
  - 移除 `ensureUserSessionReady()` 导入和首页首屏强制登录。
  - `hydratePage()` 改为直接调用 `userStore.bootstrapSession()`；未登录时保留首页游客态，不跳登录。
  - 游客态复用 fallback 模板生成基础风格卡，并展示「可浏览 / 已解锁 / 登录后记录」统计。
  - 「我的数据」「AI生成分享图」「登录后创建分享页」「风格卡」「完善档案」等账号相关入口点击后再进入登录页。
  - 操作指南视频仍允许游客浏览。

### 2.4 验证结果

| 验证项 | 命令 | 结果 |
|---|---|---|
| 前端类型检查 | `cd kaipai-frontend && npm run type-check` | 通过 |
| 小程序构建 | `cd kaipai-frontend && npm run build:mp-weixin` | 通过，`postbuild:mp-weixin` 已同步到 `dist/dev/mp-weixin` |
| 包体审计 | `cd kaipai-frontend && npm run audit:mp-package` | 通过，main `537.98 KB`，`pkg-card 211.23 KB`，`pkg-tools 28.31 KB`，均低于 `2 MB` |
| 拒审专项验收 | `node .sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/scripts/verify-miniapp-review-login-gate.mjs` | 通过，`src`、`dist/build`、`dist/dev` 全部通过 |

### 2.5 当前结论

- 登录页不再渲染微信官方 logo 或用户可见「微信登录」文案。
- 首页未登录首屏不再自动跳转登录页，用户可以先浏览风格和操作指南。
- 登录页不再暴露手机号快速验证入口；短信登录在未勾协议、信息不完整或登录失败时都有明确反馈。
- 本轮未删除短信验证码登录，也未修改后端登录接口合同。

### 2.6 登录成功仍停留登录页补充

用户反馈登录成功后仍停留在 `pages/login/index`。根因定位为登录页成功路径中存在阻断顺序：

```ts
userStore.setUserData(user, token);
await userStore.syncActorRuntimeState();
navigateAfterLogin(user);
```

`syncActorRuntimeState()` 会继续请求实名、邀请、等级等运行态接口。只要这些后续同步中任意接口失败，就会进入登录页外层 `catch`，从而在 token/user 已保存的情况下仍停留登录页。

红灯补充：

```powershell
node '.sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs'
```

结果：失败，符合预期。

失败项：

- `login success navigation is not blocked by runtime sync`

实现补充：

- `kaipai-frontend/src/pages/login/index.vue` 新增 `syncActorRuntimeStateAfterNavigation()`。
- 短信登录 / 自动注册成功后改为：
  - `userStore.setUserData(user, token)`
  - `navigateAfterLogin(user)`
  - `syncActorRuntimeStateAfterNavigation()`
- 本地已有 session 恢复成功后同样先 `navigateAfterLogin(user)`，再非阻断同步。
- `syncActorRuntimeStateAfterNavigation()` 使用 `void userStore.syncActorRuntimeState().catch(...)`，同步失败只 toast，不阻断首页跳转。

### 2.7 登录成功后又回到登录页补充

用户继续反馈登录成功后页面仍回到 `pages/login/index`。二次定位发现 2.6 已解决“等待同步再跳转”的阻断问题，但登录后的附属运行态同步仍会调用实名、邀请、等级接口；这些接口一旦返回 401，`kaipai-frontend/src/utils/request.ts` 的全局未授权处理会执行：

```ts
uni.reLaunch({ url: '/pages/login/index' });
```

因此运行态表现为：登录接口已成功、token/user 已保存、首页跳转已发起，但后续同步接口 401 又把页面重启回登录页。

红灯补充：

```powershell
node '.sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs'
```

结果：失败，符合预期。

失败项：

- `login follow-up runtime sync cannot redirect back to login page`

实现补充：

- `kaipai-frontend/src/api/verify.ts`、`src/api/invite.ts`、`src/api/level.ts` 为运行态查询透传 `Partial<RequestOptions>`。
- `kaipai-frontend/src/stores/user.ts` 新增 `ActorRuntimeSyncOptions`，并让 `syncVerificationStatus()`、`syncInviteStats()`、`syncLevelInfo()`、`syncActorRuntimeState()` 透传 `redirectOnUnauthorized`。
- `kaipai-frontend/src/pages/login/index.vue` 的 `syncActorRuntimeStateAfterNavigation()` 改为：

```ts
void userStore.syncActorRuntimeState({ redirectOnUnauthorized: false }).catch(...)
```

这样登录后的附属同步失败只进入本地 catch/toast，不再通过全局 401 逻辑抢占首页导航。其他业务页未传该选项，仍保留需要登录时自动回登录页的默认门禁行为。

验证结果：

| 验证项 | 命令 | 结果 |
|---|---|---|
| 登录门禁回归 | `node .sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs` | 通过，新增 401 不回登录页检查通过 |
| 前端类型检查 | `cd kaipai-frontend && npm run type-check` | 通过 |
| 小程序构建 | `cd kaipai-frontend && npm run build:mp-weixin` | 通过，`postbuild:mp-weixin` 已同步到 `dist/dev/mp-weixin` |
| 包体审计 | `cd kaipai-frontend && npm run audit:mp-package` | 通过，main `524.34 KB`，`pkg-card 211.01 KB`，`pkg-tools 28.23 KB`，均低于 `2 MB` |
| 复审合规脚本 | `node .sce\specs\00-188-current-phase-miniapp-review-compliance-audit-fix\scripts\verify-miniapp-review-compliance-audit.mjs` | 通过 |
| 登录返回与个人中心补充 | `node .sce\specs\00-190-current-phase-miniapp-login-back-and-mine-review-supplement\scripts\verify-miniapp-login-back-and-mine-supplement.mjs` | 通过 |
| 空白检查 | `git diff --check` / `git -C kaipai-frontend diff --check` | 仅 LF/CRLF 提示，无空白错误 |
