# 00-188 当前阶段小程序复审合规专项整改

## 1. 概述

`00-187` 已完成 `2026-07-01` 微信小程序「开拍了演员卡」拒审反馈中的登录门禁整改。本轮在继续对照微信官方《常见拒绝情形》后，发现当前小程序源码与 `mp-weixin` 构建产物仍存在若干复审风险：

1. `pkg-tools/video-player` 使用视频自动播放，触发官方 3.5.2。
2. 小程序默认启动页仍为登录页，可能削弱“先浏览服务后登录”的整改结果。
3. 未使用的微信官方风格图标仍进入构建包。
4. 部分分享产物页面继续展示「微信 / WECHAT / 朋友圈 / 微信分享面板」等平台品牌化文案。
5. 风格、AI 分享图、等级进度仍展示「再邀请 X 人解锁 / 升级」类诱导文案。
6. `pkg-tools/webview` 接受任意 `url` 参数直接打开 `web-view`。
7. `mp-weixin` 构建配置仍保留 `urlCheck=false`。

本 Spec 负责把以上风险从源码和 `dist/build`、`dist/dev` 构建产物中同步收口，并新增静态合规脚本作为复审前门禁。

## 2. 用户故事

作为审核人员，我打开小程序时默认进入可浏览的首页，而不是直接进入登录授权页。

作为审核人员，我点击首页操作指南视频时，视频不会自动播放，必须由用户主动点击播放。

作为审核人员，我浏览分享卡、海报、创建页和 AI 分享图入口时，不会看到可能暗示腾讯官方背书的「微信 / WECHAT」包装文案，也不会看到以邀请人数诱导解锁核心能力的提示。

作为开发者，我可以运行一个专项脚本，在提审前确认源码和构建产物中不再包含本轮复审高风险项。

## 3. 功能需求

### 3.1 禁止多媒体自动播放

**描述**：所有小程序视频播放器不得使用 `autoplay`，也不得显示“自动播放”能力标签。

**验收标准**：

- WHEN 用户进入 `pkg-tools/video-player/index` THEN 视频组件不带 `autoplay`。
- WHEN 用户进入操作指南视频页 THEN 页面文案表达为手动播放或点击播放。
- WHEN 构建 `mp-weixin` 产物 THEN `dist/build/mp-weixin` 与 `dist/dev/mp-weixin` 内不包含 `<video ... autoplay>`。

### 3.2 首页作为默认启动页

**描述**：小程序冷启动默认页面必须是 `pages/home/index`，让审核人员和新用户先浏览风格分馆与操作指南；登录页只能作为用户主动进入账号功能后的页面。

**验收标准**：

- WHEN 读取 `kaipai-frontend/src/pages.json` THEN `pages[0].path` 为 `pages/home/index`。
- WHEN 构建 `mp-weixin` 产物 THEN `app.json.pages[0]` 为 `pages/home/index`。
- WHEN 用户点击需要账号的功能 THEN 继续进入 `pages/login/index`。

### 3.3 官方品牌混淆元素退场

**描述**：本轮继续收口登录页之外的官方品牌混淆风险。未使用的微信官方风格图标必须删除，分享卡 / 海报 / 创建页中的平台包装文案必须改为中性小程序分享表达。

**验收标准**：

- WHEN 检查源码 THEN 不存在 `src/static/icons/wechat-login.png`。
- WHEN 构建 `mp-weixin` 产物 THEN `dist/build` 与 `dist/dev` 不存在 `static/icons/wechat-login.png`。
- WHEN 用户浏览分享卡、海报、创建页 THEN 不出现 `WECHAT`、`微信对话`、`微信分享面板` 等可见文案。
- WHEN 页面描述分享动作 THEN 使用「会话卡片」「小程序卡片」「系统分享面板」「保存后发送」等中性表达。

### 3.4 邀请解锁诱导文案降风险

**描述**：保留当前后端邀请 / 等级事实模型，但复审包的前台文案不得以「再邀请 X 人解锁 / 升级」的方式引导用户传播。锁定能力只展示中性能力状态。

**验收标准**：

- WHEN 风格未开放 THEN 文案为「当前能力未开放」「完成成长条件后开放」等中性表达。
- WHEN AI 分享图风格未开放 THEN toast 不出现「再邀请 X 人解锁」。
- WHEN 等级进度未满足 THEN 不出现「再邀请 X 人升到下一等级」。
- WHEN 构建 `mp-weixin` 产物 THEN `dist/build` 与 `dist/dev` 不包含 `再邀请.*解锁` 或 `再邀请.*升到`。

### 3.5 禁用任意 web-view 外链

**描述**：`pkg-tools/webview/index` 当前仅承担协议、隐私、关于、通知和偏好设置的本地内容展示，不再接受任意 `url` 参数进入外部 `web-view` 模式。

**验收标准**：

- WHEN 用户打开 `pkg-tools/webview/index?url=...` THEN 页面忽略 `url` 参数并展示本地默认说明。
- WHEN 检查源码和构建产物 THEN 不存在 `<web-view :src="externalUrl">` 或 `options.url` 直连 `web-view` 的逻辑。
- WHEN 用户打开协议 / 隐私 / 通知 / 偏好页 THEN 原本本地内容继续可访问。

### 3.6 复审构建配置收口

**描述**：复审构建配置不得继续显式关闭 URL 合法域名校验。

**验收标准**：

- WHEN 检查 `src/manifest.json` THEN `mp-weixin.setting.urlCheck` 为 `true`。
- WHEN 检查 `dist/build/mp-weixin/project.config.json` 和 `dist/dev/mp-weixin/project.config.json` THEN `setting.urlCheck` 为 `true`。

### 3.7 合规脚本固化

**描述**：新增 `verify-miniapp-review-compliance-audit.mjs`，静态检查源码、`dist/build` 和 `dist/dev` 是否仍包含本轮高风险项。

**验收标准**：

- WHEN 当前代码仍包含视频 `autoplay` THEN 脚本失败。
- WHEN 默认启动页不是首页 THEN 脚本失败。
- WHEN 官方图标资产仍存在 THEN 脚本失败。
- WHEN 任意 web-view 外链逻辑仍存在 THEN 脚本失败。
- WHEN 平台品牌混淆文案或邀请解锁诱导文案仍存在 THEN 脚本失败。
- WHEN 重新构建并完成整改 THEN 脚本通过。

## 4. 非功能需求

- 不删除后端邀请、等级、分享卡、微信手机号登录接口；本轮只调整复审包可见层和静态门禁。
- 不新增 mock 数据。
- 不改动登录页 `getPhoneNumber` 的用户主动触发语义。
- 不新增外部依赖。
- 不扩大到后端内容安全能力实现；后端内容安全作为提审材料与后续治理项单独处理。

## 5. 约束条件

- 遵循 `00-187` 的登录整改结果，不能恢复首屏强制登录。
- 小程序 UI / 文案修改后必须执行 `npm run build:mp-weixin` 并核对 `dist/build/mp-weixin` 与 `dist/dev/mp-weixin`。
- 删除官方图标资产后必须确认构建产物中没有旧文件残留。
- `urlCheck=true` 需要配合微信公众平台后台合法域名配置；本轮只收口本地构建配置。
