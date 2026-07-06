# 00-187 当前阶段小程序提审登录门禁整改 - 技术设计

## 1. 设计结论

本轮做三处最小整改：

```text
pages/login/index
  -> 去除手机号快捷登录按钮中的微信官方 logo image
  -> 可见文案统一为“手机号快捷登录”
  -> 授权失败 / 缺 code / 配置不可用文案去“微信”品牌化
  -> 点击不可用状态时仍明确 toast 或协议弹窗
  -> 登录成功后先保存 token/user 并跳首页，演员运行态同步改为非阻断后续任务

pages/home/index
  -> 首页 hydrate 不再调用 ensureUserSessionReady()
  -> 未登录时不跳登录，展示基础模板 + 游客态统计 / 引导
  -> 只有点击账号相关入口时进入登录页

scripts/verify-miniapp-review-login-gate.mjs
  -> 静态检查 src + dist/build + dist/dev
```

_Requirements: 3.1, 3.2, 3.3, 3.4_

## 2. 路由配置

- 不新增页面。
- `pages/home/index` 继续作为首页与 Tab 页。
- `pages/login/index` 继续作为登录页。

_Requirements: 3.2_

## 3. 依赖清单

### 登录页

继续复用：

- `@/api/auth`
  - `loginByPhone`
  - `loginByWechat`
  - `registerByPhone`
  - `sendSmsCode`
- `@/utils/runtime`
  - `canUseWechatAuth`
  - `getWechatAuthBlocker`
- `@/stores/user`
- `@/utils/navigation`

移除模板依赖：

- `/static/icons/wechat-login.png` 在登录页不再使用。

### 首页

继续复用：

- `@/api/level`
  - `getMyShareCards`
- `@/stores/user`
- `@/utils/share-card-mvp`
- `@/utils/navigation`
  - 新增或复用显式登录跳转，不再在 `hydratePage()` 中使用 `ensureUserSessionReady()`。

_Requirements: 3.1, 3.2_

## 4. 页面状态定义

### 登录页

保留现有状态：

- `phone`
- `smsCode`
- `authMode`
- `registerRole`
- `agreed`
- `smsLoading`
- `loginLoading`
- `countdown`

新增或调整计算：

- `phoneQuickLoginTip`：配置不可用时返回「手机号快捷登录暂不可用，请使用验证码登录」。
- `phoneQuickActionText`：按钮文案固定为「手机号快捷登录」或登录中态。

### 首页

新增计算：

- `isVisitor`：`!userStore.isLoggedIn`。
- `homeStats`：未登录时展示「可浏览 / 待登录」类静态值；已登录时展示真实个人数据。
- `visibleTemplateItems`：未登录时基于模板数据与空等级生成可浏览风格卡；已登录时沿用真实等级。

首页 `hydratePage()` 行为：

```text
bootstrapSession()
  -> null: 保持游客态，加载基础模板，不跳登录
  -> actor: syncActorRuntimeState + getMyShareCards
  -> crew: 清空演员卡片数据，展示账号不适用引导
```

如果游客态无法获取真实模板，页面展示可浏览空态与登录 CTA，不把请求失败转成登录跳转。

_Requirements: 3.2, 3.3_

## 5. 交互逻辑

### 登录页手机号快捷登录

```text
click 手机号快捷登录
  -> loginLoading: return
  -> capability 不可用: toast「手机号快捷登录暂不可用，请使用验证码登录」
  -> 未勾协议: showModal 协议确认，确认后只勾选协议，不直接授权
  -> 已勾协议且 capability 可用: open-type=getPhoneNumber
```

授权回调：

```text
getPhoneNumber
  -> errMsg != ok: toast「需要授权手机号才能登录」
  -> code 为空: toast「手机号授权结果缺少 code」
  -> 调后端 /api/auth/wechat-login
  -> 失败: toast「手机号快捷登录失败」
```

### 登录成功导航

短信登录、自动注册和手机号快捷登录都遵循同一顺序：

```text
login/register success
  -> userStore.setUserData(user, token)
  -> navigateAfterLogin(user)
  -> syncActorRuntimeStateAfterNavigation()
```

`syncActorRuntimeStateAfterNavigation()` 内部使用 `void userStore.syncActorRuntimeState().catch(...)`，只做登录后的实名、邀请、等级等运行态补充同步。同步失败只 toast，不再进入登录页主 try/catch，也不阻断首页跳转。

登录后的运行态同步必须传入 `redirectOnUnauthorized: false`。原因是该同步属于登录完成后的附属刷新，不是页面访问门禁；如果实名 / 邀请 / 等级接口临时返回 401，不能让 `utils/request.ts` 的全局未授权处理再次 `reLaunch('/pages/login/index')`，否则用户会看到登录成功后又回到登录页。

该顺序避免后端登录已经成功、token/user 已保存，但运行态同步接口异常时用户仍停留在登录页。

### 首页游客态

游客态允许：

- 浏览首页 hero。
- 浏览风格分馆基础展示。
- 浏览操作指南。

游客态点击以下入口进入登录页：

- 我的数据
- AI 生成分享图
- 开始创建分享页
- 具体风格卡
- 完善档案类空态动作

_Requirements: 3.2, 3.3_

## 6. 生命周期

### 登录页

- `onLoad` 保持读取邀请码。
- 有本地 token / userInfo 时继续尝试恢复 session。
- 恢复失败仍由登录页承接，不影响游客首页浏览。

### 首页

- `onShow` 调用 `hydratePage()`。
- `hydratePage()` 不再把缺 token 视作错误。
- 下拉刷新游客态时仍停留首页。

_Requirements: 3.2_

## 7. 验证设计

必须执行：

1. `cd kaipai-frontend && npm run type-check`
2. `cd kaipai-frontend && npm run build:mp-weixin`
3. `cd kaipai-frontend && npm run audit:mp-package`
4. `node .sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/scripts/verify-miniapp-review-login-gate.mjs`

构建产物核验：

- `kaipai-frontend/dist/build/mp-weixin/pages/login/index.wxml`
- `kaipai-frontend/dist/dev/mp-weixin/pages/login/index.wxml`
- `kaipai-frontend/dist/build/mp-weixin/pages/home/index.js`
- `kaipai-frontend/dist/dev/mp-weixin/pages/home/index.js`

核验点：

- 登录页 WXML 不包含官方 logo image。
- 登录页源码不再引用 `/static/icons/wechat-login.png`。
- 登录页用户可见文案不含「微信登录」。
- 登录页登录成功路径不再出现 `await userStore.syncActorRuntimeState(); navigateAfterLogin(user);` 的阻断顺序。
- 登录页登录后调用 `userStore.syncActorRuntimeState({ redirectOnUnauthorized: false })`，避免附属同步 401 抢占已完成导航。
- 首页源码不再在 `hydratePage()` 里调用 `ensureUserSessionReady()`。
- 首页未登录状态不调用 `goLogin()`。

_Requirements: 3.1, 3.2, 3.3, 3.4_
