# 00-188 当前阶段小程序复审合规专项整改 - 执行记录

## 执行摘要

已完成。

本轮对照微信官方《常见拒绝情形》继续复查 `2026-07-01` 小程序「开拍了演员卡」拒审反馈之外的复审风险，重点覆盖：

- 3.2.1 页面内容诱导分享风险。
- 3.2.12 页面内容暗示腾讯官方背书 / 合作风险。
- 3.3 可用性和完整性。
- 3.4.1 / 3.4.5 授权、用户数据和头像昵称展示风险。
- 3.5.2 多媒体自动播放。
- 3.5.5 账号体系退出入口。
- 3.6 UI 规范。

实施结果：

- 新增 `verify-miniapp-review-compliance-audit.mjs`，同时扫描 `src`、`dist/build/mp-weixin`、`dist/dev/mp-weixin`。
- `pages.json` 默认启动页改为 `pages/home/index`，登录页保留为用户主动进入账号功能后的页面。
- `manifest.json` 的 `mp-weixin.setting.urlCheck` 改为 `true`，构建产物 `project.config.json` 已同步。
- `pkg-tools/video-player/index.vue` 移除 `autoplay`，可见标签从自动播放改为手动 / 点击播放语义。
- `pkg-tools/webview/index.vue` 删除任意 `url` 外链 `web-view` 模式，只保留本地协议、隐私、关于、通知和偏好设置内容。
- 删除未使用的 `src/static/icons/wechat-login.png`，构建产物中已无该资产。
- 分享卡 / 海报 / 创建页中的 `WECHAT`、`微信对话`、`微信分享面板`、`朋友圈` 等包装文案已改为中性分享表达。
- 风格、AI 分享图、等级进度中的「再邀请 X 人解锁 / 升级」文案已改为中性能力状态。
- 后端邀请、等级、分享卡和登录 API 合同未改动。

复审残余风险评估：

- 前台仍保留 `邀请码`、`邀请记录`、`有效邀请`、`邀请海报` 等业务事实表达，用于既有邀请记录页和成长记录展示；本轮已移除「再邀请 X 人解锁 / 升级」这一类诱导式表达。
- `kaipai-frontend/src/pages/mine/index.vue` 与 `pkg-tools/webview/index.vue` 仍有明确 `退出登录` 入口，符合账号体系退出要求。
- 登录页和首页继续沿用 `00-187` 结果：不恢复首屏强制登录，不恢复微信官方 logo / 微信登录文案。

## 验证记录

### 红灯验证

命令：

```bash
node .sce/specs/00-188-current-phase-miniapp-review-compliance-audit-fix/scripts/verify-miniapp-review-compliance-audit.mjs
```

初始结果：失败 21 项，覆盖源码与旧构建产物中的以下风险：

- 默认启动页仍为 `pages/login/index`。
- `urlCheck=false`。
- `src/static/icons/wechat-login.png` 存在。
- 视频播放器存在 `autoplay`。
- 可见分享文案包含 `WECHAT`、`微信对话`、`微信分享面板`、`朋友圈`。
- 邀请文案包含「再邀请 X 人解锁 / 升到」。
- `pkg-tools/webview` 存在任意 `url` 外链 `web-view` 模式。

### 源码层绿灯

命令：

```bash
node .sce/specs/00-188-current-phase-miniapp-review-compliance-audit-fix/scripts/verify-miniapp-review-compliance-audit.mjs
```

源码层结果：全部通过；旧 `dist/build`、`dist/dev` 因尚未重新构建仍失败 14 项。

### 构建与完整验证

命令：

```bash
cd kaipai-frontend
npm run type-check
npm run build:mp-weixin
npm run audit:mp-package
cd ..
node .sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/scripts/verify-miniapp-review-login-gate.mjs
node .sce/specs/00-188-current-phase-miniapp-review-compliance-audit-fix/scripts/verify-miniapp-review-compliance-audit.mjs
```

结果：

- `npm run type-check`：通过。
- `npm run build:mp-weixin`：通过，postbuild 已同步 `dist/dev/mp-weixin`。
- `npm run audit:mp-package`：通过；总构建大小 `760.37 KB`，主包 `521.13 KB / 2 MB`，`pkg-card 211.01 KB / 2 MB`，`pkg-tools 28.23 KB / 2 MB`。
- `00-187` 登录门禁脚本：全部通过。
- `00-188` 复审合规脚本：源码、`dist/build/mp-weixin`、`dist/dev/mp-weixin` 全部通过。

### 产物定点核对

- `dist/build/mp-weixin/app.json.pages[0]` = `pages/home/index`。
- `dist/dev/mp-weixin/app.json.pages[0]` = `pages/home/index`。
- `dist/build/mp-weixin/project.config.json.setting.urlCheck` = `true`。
- `dist/dev/mp-weixin/project.config.json.setting.urlCheck` = `true`。
- `dist/build/mp-weixin/static/icons/wechat-login.png` 不存在。
- `dist/dev/mp-weixin/static/icons/wechat-login.png` 不存在。
- `dist/build/mp-weixin/pkg-tools/video-player/index.wxml` 与 `dist/dev/mp-weixin/pkg-tools/video-player/index.wxml` 均无 `autoplay`，并含 `MANUAL PLAY` / `点击播放`。
- `dist/build/mp-weixin/pkg-tools/webview/index.wxml` 与 `dist/dev/mp-weixin/pkg-tools/webview/index.wxml` 均无 `<web-view>`。
- `dist/build/mp-weixin/pkg-card/actor-card/index.wxml` 与 `dist/dev/mp-weixin/pkg-card/actor-card/index.wxml` 均含 `SESSION CARD PREVIEW` / `MINI PROGRAM CARD`，无 `WECHAT` / `朋友圈`。
