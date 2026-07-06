# 00-189 当前阶段小程序全量 E2E 截图与文档整理审计 - 执行记录

## 执行摘要

已完成当前小程序运行态启动、全页面截图、业务流程矩阵与旧文档整理矩阵。

- 最终验收 run：`20260703-091427`
- 小程序工程目录：`D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- Automator endpoint：`ws://127.0.0.1:19425`
- 运行态页面：27 个（主包 15，`pkg-card` 10，`pkg-tools` 2）
- 截图目标：34 个页面 / 参数变体
- 页面截图结果：34/34 passed，0 failed，0 redirected
- 登录交互检查：passed（2 个 input，验证码按钮存在，手机号快捷登录按钮存在）
- 业务流程矩阵：20 条流程
- 旧文档矩阵：498 条文档记录

说明：当前正式短信接口不回传验证码，DevTools storage 也没有可复用 token。因此登录态页面采用 `mock-api-assisted` 方式渲染，只用于页面结构、文案、路由、审核风险和截图覆盖复核；不声明真实手机号验证码登录或真实提交动作已闭环。

## 输出目录

- `D:\XM\kaipai-team\output\miniapp-e2e\00-189\20260703-091427`
- 截图目录：`D:\XM\kaipai-team\output\miniapp-e2e\00-189\20260703-091427\screenshots`
- 捕获目录：`D:\XM\kaipai-team\output\miniapp-e2e\00-189\20260703-091427\captures`
- `LATEST_RUN.txt` 已指向 `20260703-091427`。

## 启动记录

启动命令：

```powershell
& 'C:\Users\33340\.codex\skills\launch-wechat-miniprogram\scripts\launch-wechat-miniprogram.ps1' `
  -ProjectPath 'D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin'
```

启动结果：

- 记录文件：`D:\XM\kaipai-team\output\miniapp-e2e\00-189\20260703-091427\launch-result.json`
- `ProjectPath`：`D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `DevToolsRoot`：`D:\AP\微信web开发者工具`
- `Cli`：`D:\AP\微信web开发者工具\cli.bat`
- `ProjectSeenInLog=true`
- `SimulatorReadyInLog=true`

登录态检查：

```powershell
& 'D:\AP\微信web开发者工具\cli.bat' islogin
```

- 记录文件：`D:\XM\kaipai-team\output\miniapp-e2e\00-189\20260703-091427\islogin.txt`
- 输出包含 `{"login":true}`。
- PowerShell 会把 CLI 的 `- initialize` stderr 视作 native error record；实际命令输出仍显示 `√ islogin`。

## 页面截图记录

截图脚本：

```powershell
$env:RUN_ID = '20260703-091427'
node '.sce\specs\00-189-current-phase-miniapp-full-e2e-screenshot-and-docs-audit\scripts\capture-miniapp-full-e2e.mjs'
```

核心产物：

- Manifest：`D:\XM\kaipai-team\output\miniapp-e2e\00-189\20260703-091427\captures\full-page-screenshot-manifest.json`
- Progress log：`D:\XM\kaipai-team\output\miniapp-e2e\00-189\20260703-091427\captures\miniapp-e2e-progress.log`
- Page data：`D:\XM\kaipai-team\output\miniapp-e2e\00-189\20260703-091427\captures\page-data-*.json`

Manifest 摘要：

```json
{
  "runtimePageCount": 27,
  "targetCount": 34,
  "captureCount": 34,
  "passedCount": 34,
  "redirectedCount": 0,
  "failedCount": 0,
  "screenshotCount": 34,
  "uniqueScreenshotHashCount": 33,
  "failedTargets": []
}
```

截图文件检查：

- `screenshots/*.png` 共 35 张：34 张页面 / 变体截图 + 1 张登录交互截图。
- 像素采样检查：`BLANKISH=0`，`MIN_SAMPLE_COLORS=10`。
- Manifest 与输出目录扫描未发现 `[Circular]`。

首页截图说明：

- 首次全量 run 中 `pages/home/index` 的 automator 截图超时，窗口兜底图为空白。
- 已使用同一 automator endpoint 单独 `reLaunch('/pages/home/index')`，等待 12 秒后重采首页截图。
- 已用有效首页截图覆盖 `screenshots/01-pages-home-index-default.png`，并同步 manifest 中 `screenshotMethod=automator-recapture-after-render-stabilized` 与 SHA256。
- 首页最终截图 SHA256：`48fe6689ad65330cdac925d49845640c60a1c173d4d1e848b58f00e2c2d67c86`。

## 业务流程矩阵

- 矩阵文件：`D:\XM\kaipai-team\output\miniapp-e2e\00-189\20260703-091427\flow-matrix.md`
- 流程数量：20
- 状态：20 条均为 `passed`。

覆盖流程：

- `guest-home`：游客打开首页并浏览。
- `login`：用户主动进入登录页，登录页按钮响应。
- `actor-profile`：演员档案维护。
- `verify`：实名认证。
- `create-share`：创建分享页三步。
- `style-detail`：风格详情。
- `share-card`：分享卡和海报预览。
- `ai-share`：AI 分享图生成页与公开详情。
- `portfolio`：作品集 / 已创建分享。
- `public-detail`：公开演员详情。
- `history`：浏览历史。
- `contacts`：联系方式申请。
- `mine`：我的页与账号设置。
- `agreements`：协议、隐私、关于、通知、偏好。
- `video-guide`：操作指南视频。
- `apply`：角色详情与投递链路。
- `legacy-crew`：旧剧组 / 投递保留页面。
- `capability`：能力中心。
- `invite`：邀请记录。
- `favorites`：收藏页。

## 旧文档整理矩阵

- 矩阵文件：`D:\XM\kaipai-team\output\miniapp-e2e\00-189\20260703-091427\doc-audit-matrix.md`
- 扫描记录：498 条。
- 整理口径：不大范围重写历史执行记录；历史 Spec 保留为证据，当前引用口径由 `00-189`、`00-188`、`00-187`、`00-27` 与产品主线文档承接。

当前引用口径：

- 小程序复审主线：游客首页可浏览；登录页只在用户主动进入账号 / 登录能力时出现；手机号授权文案统一为“手机号快捷登录”。
- 当前分享主线：创建分享页、分享卡 / 海报预览、AI 分享图、公开详情、作品集、历史、我的页。
- 旧剧组端与投递管理：保留运行态截图和历史说明，不作为本轮复审主线扩展承诺。
- 旧 fortune / 命理、旧 membership、朋友圈 / 微信分享面板等历史描述：只可作为历史记录，不得作为当前运行态依据。

## 验证记录

已执行：

```powershell
cd D:\XM\kaipai-team\kaipai-frontend
npm run build:mp-weixin
```

结果：通过。构建输出包含 `DONE Build complete` 与 postbuild `synced mp-weixin build to dev`；仅有 Dart Sass legacy JS API warning 与 empty chunk `types/project` warning。

已执行：

```powershell
node --check '.sce\specs\00-189-current-phase-miniapp-full-e2e-screenshot-and-docs-audit\scripts\capture-miniapp-full-e2e.mjs'
```

结果：通过。

已执行：

```powershell
rg "\[Circular\]" "output\miniapp-e2e\00-189\20260703-091427"
```

结果：未命中。

已执行截图像素采样检查：

```text
RUN_ID=20260703-091427 COUNT=35 BLANKISH=0 MIN_SAMPLE_COLORS=10
```

收尾验证已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`：通过。
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`：通过，postbuild 已同步 `dist/build/mp-weixin` 到 `dist/dev/mp-weixin`；保留 Sass legacy JS API warning 与 empty chunk `types/project` warning。
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run audit:mp-package`：通过，`main=521.13 KB`、`pkg-card=211.01 KB`、`pkg-tools=28.23 KB`，均低于 `2 MB`。
- `node .sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs`：通过。
- `node .sce\specs\00-188-current-phase-miniapp-review-compliance-audit-fix\scripts\verify-miniapp-review-compliance-audit.mjs`：通过。
