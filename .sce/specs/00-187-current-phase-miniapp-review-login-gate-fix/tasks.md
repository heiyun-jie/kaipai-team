# 00-187 当前阶段小程序提审登录门禁整改 - 任务拆解

> 执行原则：一次一个任务，执行后更新状态并保留验证证据。

## T1 建立拒审整改 Spec 与验收脚本

- [x] 新增 `00-187` requirements / design / tasks。
- [x] 新增 `verify-miniapp-review-login-gate.mjs` 静态验收脚本。
- [x] 在当前未整改代码上运行脚本，确认红灯失败。

## T2 登录页官方混淆元素退场

- [x] 移除登录页手机号快捷登录按钮中的 `/static/icons/wechat-login.png`。
- [x] 登录页用户可见文案统一为「手机号快捷登录」。
- [x] 授权失败、缺 code、配置不可用、后端失败文案去「微信登录」品牌化。
- [x] 点击不可用状态时给出明确 toast 或协议弹窗。

## T3 首页游客态浏览

- [x] `pages/home/index` 未登录时不再调用 `ensureUserSessionReady()` 强制跳登录。
- [x] 未登录首页展示游客态统计、基础风格分馆和操作指南。
- [x] 账号相关入口点击时再跳登录。
- [x] 已登录演员 / 剧组用户原有行为保持。

## T4 验证与产物核对

- [x] `kaipai-frontend npm run type-check` 通过。
- [x] `kaipai-frontend npm run build:mp-weixin` 通过。
- [x] `kaipai-frontend npm run audit:mp-package` 通过。
- [x] `verify-miniapp-review-login-gate.mjs` 通过。
- [x] 核对 `dist/build/mp-weixin` 与 `dist/dev/mp-weixin` 登录页 / 首页产物。
