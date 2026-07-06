# 00-190 当前阶段小程序登录返回与个人中心复核补充 - 执行记录

## 执行摘要

已完成登录页返回按钮补充、个人中心复核记录补充和独立验收脚本。
用户截图补充后，已进一步将登录页返回按钮从胶囊下方调整为与微信胶囊按钮同一行。
用户继续指出点击底部“我的”不应直接跳登录后，已补充个人中心游客态整改。

- 登录页：`pages/login/index`
- 个人中心：`pages/mine/index`
- 上游证据：`00-189` run `20260703-091427`
- 新增验收脚本：`scripts/verify-miniapp-login-back-and-mine-supplement.mjs`

## 红灯记录

实现前执行：

```powershell
node '.sce\specs\00-190-current-phase-miniapp-login-back-and-mine-review-supplement\scripts\verify-miniapp-login-back-and-mine-supplement.mjs'
```

结果：失败，符合预期。

失败项：

- `login source renders local back button`
- `login source implements back fallback to home`
- `dist/build/mp-weixin` 登录页返回按钮与 fallback 缺失
- `dist/dev/mp-weixin` 登录页返回按钮与 fallback 缺失

通过项：

- 登录页未引入平台品牌化文案。
- `00-189` latest run marker 存在。
- `00-189` flow matrix 包含 `mine` 流程。
- `00-189` 存在 `11-pages-mine-index-default.png` 截图。

## 实现记录

修改文件：

- `kaipai-frontend/src/pages/login/index.vue`

实现内容：

- 在 `KpCapsuleSpacer` 下方新增 `login-page__nav`。
- 新增本地返回按钮 `login-page__back`，包含左箭头和“返回”文本。
- 新增 `handleBack()`：
  - 页面栈长度大于 1 时调用 `uni.navigateBack()`。
  - `navigateBack` 失败或无历史栈时调用 `uni.reLaunch({ url: '/pages/home/index' })`。
- 新增本地样式：
  - `login-page__nav`
  - `login-page__back`
  - `login-page__back-icon`
  - `login-page__back-text`
- 将 `login-page__stage` 顶部 padding 从 `6vh` 收到 `2vh`，抵消新增返回按钮导致的整体下沉。

用户截图补充后的同排对齐调整：

- 将原 `KpCapsuleSpacer` 后方另起一行的 `login-page__nav` 改为顶部 `login-page__topbar`。
- `login-page__topbar` 内同时包含 `KpCapsuleSpacer` 和本地 `login-page__back`。
- 返回按钮使用 `getFloatingBackNavStyles()` 产出的 `backButtonStyle`，复用微信胶囊按钮的 `top / height`。
- `.login-page__back` 改为 `position: absolute; left: 32rpx; top: 0;`，实际 top / height 由内联样式覆盖，从而与右侧胶囊按钮保持同一横向导航层。
- 00-190 验收脚本已新增 `login source aligns back button with capsule row` 和 dist WXML topbar 顺序检查，防止回退为胶囊下方按钮。

构建产物检查：

- `kaipai-frontend/dist/dev/mp-weixin/pages/login/index.wxml` 包含 `login-page__back`、`login-page__back-text` 和“返回”。
- `kaipai-frontend/dist/dev/mp-weixin/pages/login/index.wxml` 中 `login-page__back` 位于 `login-page__topbar` 内，并在 `login-page__stage` 之前。
- `kaipai-frontend/dist/dev/mp-weixin/pages/login/index.wxss` 包含 `login-page__topbar`、`login-page__back` 和 `padding:2vh 0 0`。

## 个人中心复核记录

个人中心沿用 `00-189` 全量 E2E 证据：

- Flow matrix：`D:\XM\kaipai-team\output\miniapp-e2e\00-189\20260703-091427\flow-matrix.md`
- 截图：`D:\XM\kaipai-team\output\miniapp-e2e\00-189\20260703-091427\screenshots\11-pages-mine-index-default.png`
- 流程行：`mine | 我的页与账号设置 | pages/mine/index`

本轮明确复核区域：

- 个人资料区：头像 / 昵称 / ID / 编辑入口。
- 我的数据区：分享数、打开数、趋势条、卡片 / 海报 / 再进入摘要。
- 快捷入口：创建分享、我的二维码。
- 设置项：我的作品集、联系申请、收藏的分享、消息通知、偏好设置。
- 账号操作：退出登录入口。

## 个人中心游客态补充记录

根因定位：

- 底部“我的”Tab 配置本身指向 `pages/mine/index`。
- 直接跳登录不是 TabBar 点击层触发，而是 `pages/mine/index` 的 `onShow -> hydrateMinePage -> ensureUserSessionReady()`。
- `ensureUserSessionReady()` 在未登录时会调用 `goLogin()`，导致用户刚进入个人中心就被 `reLaunch('/pages/login/index')`。

红灯补充：

```powershell
node '.sce\specs\00-190-current-phase-miniapp-login-back-and-mine-review-supplement\scripts\verify-miniapp-login-back-and-mine-supplement.mjs'
```

结果：失败，符合预期。

新增失败项：

- `mine source allows unauthenticated tab viewing`
- `mine source renders visitor account state`
- `dist/build/mp-weixin mine WXML renders visitor account card`
- `dist/build/mp-weixin mine bundle does not redirect on tab entry`
- `dist/dev/mp-weixin mine WXML renders visitor account card`
- `dist/dev/mp-weixin mine bundle does not redirect on tab entry`

实现补充：

- `kaipai-frontend/src/pages/mine/index.vue` 移除页面展示阶段的 `ensureUserSessionReady()` 强登录守卫。
- `hydrateMinePage()` 改为调用 `userStore.bootstrapSession()`：有 token 时恢复会话；无 token / 无用户时调用 `resetVisitorMinePage()` 并停留当前页。
- 新增 `isVisitor`，未登录时显示：
  - `未登录用户`
  - `登录后查看账号数据与作品集`
  - `mine-page__login-card`
  - “登录后查看账号数据”
  - “登录 / 注册”
- 新增 `requireLoginForMineAction()`，编辑、创建分享、我的二维码、作品集、联系申请、收藏、通知和偏好设置等账号动作点击后再跳登录。
- 退出登录入口只在已登录时展示。

该补充直接对应复审规则第 2 条：用户进入首页 / Tab 页面后应先能浏览功能服务，不应一进入个人中心就被要求授权登录。

补充验证：

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check
```

结果：通过。

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run build:mp-weixin
```

结果：通过，postbuild 已同步到 `dist/dev/mp-weixin`。输出包含 uni-app 新版本提示、既有 Sass legacy JS API warning 与 empty chunk `types/project` warning。

构建产物核验：

- `kaipai-frontend/dist/build/mp-weixin/pages/mine/index.wxml` 包含 `mine-page__login-card`、“登录后查看账号数据”和“登录 / 注册”。
- `kaipai-frontend/dist/dev/mp-weixin/pages/mine/index.wxml` 包含 `mine-page__login-card`、“登录后查看账号数据”和“登录 / 注册”。
- `kaipai-frontend/dist/build/mp-weixin/pages/mine/index.js` 不再包含 `ensureUserSessionReady`，保留 `bootstrapSession` 与账号动作跳登录路径。
- `kaipai-frontend/dist/dev/mp-weixin/pages/mine/index.js` 不再包含 `ensureUserSessionReady`，保留 `bootstrapSession` 与账号动作跳登录路径。

```powershell
node '.sce\specs\00-190-current-phase-miniapp-login-back-and-mine-review-supplement\scripts\verify-miniapp-login-back-and-mine-supplement.mjs'
```

结果：通过。新增的个人中心游客态检查项通过：

- `mine source allows unauthenticated tab viewing`
- `mine source renders visitor account state`
- `dist/build/mp-weixin mine WXML renders visitor account card`
- `dist/build/mp-weixin mine bundle does not redirect on tab entry`
- `dist/dev/mp-weixin mine WXML renders visitor account card`
- `dist/dev/mp-weixin mine bundle does not redirect on tab entry`

同时重新执行并通过：

```powershell
node '.sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs'
node '.sce\specs\00-188-current-phase-miniapp-review-compliance-audit-fix\scripts\verify-miniapp-review-compliance-audit.mjs'
cd D:\XM\kaipai-team\kaipai-frontend
npm run audit:mp-package
```

最新包体审计结果：

```text
main      524.20 KB / 2.00 MB
pkg-card  211.01 KB / 2.00 MB
pkg-tools 28.23 KB  / 2.00 MB
```

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

结果：通过，postbuild 已同步到 `dist/dev/mp-weixin`。输出仍包含既有 Sass legacy JS API warning 与 empty chunk `types/project` warning。

已执行：

```powershell
node '.sce\specs\00-190-current-phase-miniapp-login-back-and-mine-review-supplement\scripts\verify-miniapp-login-back-and-mine-supplement.mjs'
```

结果：通过。源码、`dist/build`、`dist/dev` 三层均包含登录返回按钮和首页 fallback，个人中心证据存在。

已执行：

```powershell
node '.sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs'
```

结果：通过。

已执行：

```powershell
node '.sce\specs\00-188-current-phase-miniapp-review-compliance-audit-fix\scripts\verify-miniapp-review-compliance-audit.mjs'
```

结果：通过。

已执行：

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run audit:mp-package
```

结果：通过。

```text
main      522.34 KB / 2.00 MB
pkg-card  211.01 KB / 2.00 MB
pkg-tools 28.23 KB  / 2.00 MB
```

## 用户截图补充验证

用户指出 `pages/login/index` 返回按钮仍位于胶囊按钮下方。本轮补充后重新执行：

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check
```

结果：通过。

重新执行：

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run build:mp-weixin
```

结果：通过，postbuild 已同步到 `dist/dev/mp-weixin`。输出仍包含既有 Sass legacy JS API warning 与 empty chunk `types/project` warning。

构建产物核验：

- `kaipai-frontend/dist/build/mp-weixin/pages/login/index.wxml` 中 `login-page__topbar` 包住 `kp-capsule-spacer` 与 `login-page__back`。
- `kaipai-frontend/dist/dev/mp-weixin/pages/login/index.wxml` 中 `login-page__topbar` 包住 `kp-capsule-spacer` 与 `login-page__back`。
- 两层产物中 `login-page__back` 都位于 `login-page__stage` 之前。
- `kaipai-frontend/dist/dev/mp-weixin/pages/login/index.wxss` 中 `.login-page__back` 包含 `position:absolute; top:0; left:32rpx`，实际 `top / height` 由 `backButtonStyle` 内联样式覆盖。

重新执行：

```powershell
node '.sce\specs\00-190-current-phase-miniapp-login-back-and-mine-review-supplement\scripts\verify-miniapp-login-back-and-mine-supplement.mjs'
```

结果：通过。新增的胶囊同排检查项通过：

- `login source aligns back button with capsule row`
- `dist/build/mp-weixin login WXML keeps back button in capsule row`
- `dist/dev/mp-weixin login WXML keeps back button in capsule row`

同时重新执行并通过：

```powershell
node '.sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs'
node '.sce\specs\00-188-current-phase-miniapp-review-compliance-audit-fix\scripts\verify-miniapp-review-compliance-audit.mjs'
cd D:\XM\kaipai-team\kaipai-frontend
npm run audit:mp-package
```

最新包体审计结果：

```text
main      522.45 KB / 2.00 MB
pkg-card  211.01 KB / 2.00 MB
pkg-tools 28.23 KB  / 2.00 MB
```

`git diff --check` 通过；仅保留既有 Windows 行尾提示。

## 个人中心完整游客内容补充

用户进一步指出 `pages/mine/index` 游客态不应只显示“登录后查看账号数据”卡片，卡片下方不能是空白；个人中心页面内容都需要展示，点击具体入口时再跳转登录。

红灯补充：

```powershell
node '.sce\specs\00-190-current-phase-miniapp-login-back-and-mine-review-supplement\scripts\verify-miniapp-login-back-and-mine-supplement.mjs'
```

结果：失败，符合预期。

新增失败项：

- `mine source shows full page content for visitors`

实现补充：

- `kaipai-frontend/src/pages/mine/index.vue` 新增 `showMineContent = computed(() => isVisitor.value || userStore.isActor)`。
- 游客态继续展示顶部 `mine-page__login-card`。
- 登录卡之后继续展示：
  - `mine-page__analytics`
  - `mine-page__quick-grid`
  - `mine-page__settings`
- 原 `v-else-if="userStore.isActor"` 改为 `v-if="showMineContent"`，避免游客态只显示登录卡。
- 编辑、登录卡、创建分享、我的二维码、作品集、联系申请、收藏、通知、偏好设置继续通过 `requireLoginForMineAction()` 跳登录。

该补充后的视觉合同：

- 未登录进入 `pages/mine/index` 时，页面主体不是空白。
- 用户能看到个人中心的数据区、快捷入口和设置项。
- 真正需要账号态的数据和操作不会自动请求 token 接口；点击账号动作再进入登录页。

补充验证：

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run build:mp-weixin
```

结果：通过，postbuild 已同步到 `dist/dev/mp-weixin`。输出包含 uni-app 新版本提示、既有 Sass legacy JS API warning 与 empty chunk `types/project` warning。

构建产物核验：

- `kaipai-frontend/dist/build/mp-weixin/pages/mine/index.wxml` 中 `mine-page__login-card` 后继续出现 `mine-page__analytics`、`mine-page__quick-grid` 和 `mine-page__settings`。
- `kaipai-frontend/dist/dev/mp-weixin/pages/mine/index.wxml` 中 `mine-page__login-card` 后继续出现 `mine-page__analytics`、`mine-page__quick-grid` 和 `mine-page__settings`。
- `kaipai-frontend/dist/dev/mp-weixin/pages/mine/index.js` 不包含 `ensureUserSessionReady`，保留 `bootstrapSession` 和账号动作登录路径。

重新执行并通过：

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run type-check
npm run audit:mp-package
cd D:\XM\kaipai-team
node '.sce\specs\00-190-current-phase-miniapp-login-back-and-mine-review-supplement\scripts\verify-miniapp-login-back-and-mine-supplement.mjs'
node '.sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs'
node '.sce\specs\00-188-current-phase-miniapp-review-compliance-audit-fix\scripts\verify-miniapp-review-compliance-audit.mjs'
```

00-190 新增检查项通过：

- `mine source shows full page content for visitors`
- `dist/build/mp-weixin mine WXML keeps full visitor content available`
- `dist/dev/mp-weixin mine WXML keeps full visitor content available`

最新包体审计结果：

```text
main      524.22 KB / 2.00 MB
pkg-card  211.01 KB / 2.00 MB
pkg-tools 28.23 KB  / 2.00 MB
```
