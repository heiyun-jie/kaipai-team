# 00-196 当前阶段小程序手机号快捷登录入口恢复

## 1. 概述

`00-195` 已确认：`pages/login/index` 中上一版存在的「手机号快捷登录」入口被 `kaipai-frontend` 提交 `0679e09 fix: remove quick phone auth login entry` 物理删除。该删除把 `2026-07-01` 微信审核反馈中的“去除微信官方 logo / 微信品牌化文案，并把授权登录提示改为手机号快捷登录”误扩大为“删除 `getPhoneNumber` 手机号快捷登录入口”。

本 Spec 负责执行修复：恢复登录页合规版「手机号快捷登录」入口，继续禁止官方风格 logo 和「微信登录 / 微信一键登录 / 微信授权」用户可见文案，并同步修正 `00-187` 的错误验收脚本。

## 2. 用户故事

作为小程序用户，我在登录页可以选择短信验证码登录，也可以选择「手机号快捷登录」。

作为审核人员，我看到的是小程序自有能力文案「手机号快捷登录」，不会看到微信官方 logo 或“微信登录”类品牌化提示。

作为开发者，我需要静态验收脚本防止后续再次把「去品牌化」误实现成「删除快捷登录入口」。

## 3. 功能需求

### 3.1 恢复登录页合规快捷登录入口

**描述**：`pages/login/index` 必须恢复一个自有文案按钮「手机号快捷登录」，通过微信小程序原生 `getPhoneNumber` 能力获取手机号授权 code 并调用后端登录接口。

**验收标准**：

- WHEN 用户打开 `pages/login/index` THEN 页面展示「手机号快捷登录」按钮。
- WHEN 用户未勾选协议点击「手机号快捷登录」 THEN 只弹出协议确认，确认后勾选协议，不直接触发授权。
- WHEN 用户已勾选协议点击「手机号快捷登录」 THEN 按钮挂载 `open-type="getPhoneNumber"`。
- WHEN `getPhoneNumber` 返回 `ok` 且 code 存在 THEN 前端调用 `/api/auth/wechat-login` 完成登录或自动注册。
- WHEN 登录成功 THEN 先保存 token/user 并导航，再执行非阻断演员运行态同步。

### 3.2 去除官方混淆元素

**描述**：恢复入口时不得恢复 `/static/icons/wechat-login.png`，不得使用微信官方 logo、微信品牌化文案或暗示腾讯官方背书的可见元素。

**验收标准**：

- WHEN 查看登录页源码 THEN 不存在 `wechat-login.png`。
- WHEN 查看登录页源码和构建产物 THEN 不存在 `login-page__wechat-icon`。
- WHEN 查看登录页和运行时可见文案 THEN 不出现「微信登录」「微信一键登录」「微信授权」。
- WHEN 授权失败、缺 code、配置不可用或后端失败 THEN toast 使用「手机号快捷登录 / 手机号授权」相关自有能力文案。

### 3.3 修正验收门禁

**描述**：`00-187` 验收脚本必须从“禁止快捷入口”改为“要求合规快捷入口”，并继续保留首页游客态、登录后非阻断同步、官方 logo 删除等检查。

**验收标准**：

- WHEN 当前源码缺少「手机号快捷登录」入口 THEN `verify-miniapp-review-login-gate.mjs` 失败。
- WHEN 当前源码恢复合规入口但恢复官方图标 THEN `verify-miniapp-review-login-gate.mjs` 失败。
- WHEN 当前源码出现「微信登录 / 微信一键登录 / 微信授权」可见文案 THEN `verify-miniapp-review-login-gate.mjs` 失败。
- WHEN 当前源码和构建产物均恢复合规入口 THEN `verify-miniapp-review-login-gate.mjs` 通过。

### 3.4 构建产物同步

**描述**：小程序 UI 修改后必须重新构建，并确认 `dist/build/mp-weixin` 与 `dist/dev/mp-weixin` 都包含合规快捷登录入口。

**验收标准**：

- WHEN 执行 `npm run build:mp-weixin` THEN 构建通过并同步 `dist/dev/mp-weixin`。
- WHEN 查看 `dist/build/mp-weixin/pages/login/index.wxml` THEN 存在「手机号快捷登录」对应文本和 `getPhoneNumber` 绑定。
- WHEN 查看 `dist/dev/mp-weixin/pages/login/index.wxml` THEN 存在「手机号快捷登录」对应文本和 `getPhoneNumber` 绑定。
- WHEN 查看构建产物 THEN 不存在 `static/icons/wechat-login.png`。

## 4. 非功能需求

- 不恢复旧 `wechat-login.png` 文件。
- 不新增头像、昵称授权入口。
- 不改变首页未登录可浏览策略。
- 不改变短信验证码登录路径。
- 不改变后端 `/api/auth/wechat-login` 合同。

## 5. 约束条件

- 本轮优先修改 `kaipai-frontend/src/pages/login/index.vue`、`src/api/auth.ts`、`src/utils/runtime.ts` 与 `00-187` 验收脚本。
- 内部后端接口路径 `/api/auth/wechat-login` 可保留；它不是用户可见文案。
- 登录成功后的运行态同步必须继续使用 `redirectOnUnauthorized: false`。
- 当前根仓库已有 `00-194 / 00-195` 文档变更，本轮不得回滚或覆盖这些用户上下文。
