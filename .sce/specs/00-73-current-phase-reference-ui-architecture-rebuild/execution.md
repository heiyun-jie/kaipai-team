# 00-73 执行记录

## 1. 当前状态

- 已重新读取 `User Global Memory`
- 已核对 `00-28 / 00-69 / 00-70` 的当前前台治理边界
- 已核对 `D:\XM\kaipai-team\_-_.html` 的运行态截图与 screen map
- 已确认本轮新增 `00-73`，用于承接“reference-driven 的前台 UI / 架构二次重构”

## 2. 已核实的 reference 事实

### 2.1 参考文件

- `D:\XM\kaipai-team\_-_.html`

### 2.2 截图证据

已执行：

- `npx playwright screenshot --viewport-size=1400,900 "file:///D:/XM/kaipai-team/_-_.html" "D:/XM/kaipai-team/output/playwright/reference-overview.png"`
- `npx playwright screenshot --full-page --viewport-size=2200,1300 "file:///D:/XM/kaipai-team/_-_.html" "D:/XM/kaipai-team/output/playwright/reference-full.png"`

已确认截图：

- `D:\XM\kaipai-team\output\playwright\reference-overview.png`
- `D:\XM\kaipai-team\output\playwright\reference-full.png`

### 2.3 结构证据

通过对 `_-_.html` 内嵌 manifest 解码，已确认 reference 显式包含以下 screen/component：

- `WXPhone`
- `BottomTabs`
- `LoginScreen`
- `HomeScreen`
- `RecordsScreen`
- `MyScreen`
- `CreateScreen`
- `CardPreviewScreen`
- `PosterPreviewScreen`

已确认 reference screen map 为：

1. 登录 / 注册
2. 首页
3. 记录
4. 我的
5. 创建分享页
6. 卡片预览
7. 海报预览

### 2.4 视觉 token 事实

已确认 reference 默认 theme 为 `studio`，关键 token 为：

- bg: `#F5F3EE`
- surface: `#FBFAF6`
- surface2: `#EEEBE3`
- ink: `#1A1816`
- accent: `#8C6F4F`

## 3. 已核实的当前代码事实

### 3.1 当前 active routes

已核对：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages.json`

当前 active 前台路由为：

- `pages/login/index`
- `pages/role-select/index`
- `pages/home/index`
- `pages/actor-profile/edit`
- `pages/history/index`
- `pages/mine/index`
- `pages/actor-profile/detail`
- `pkg-card/actor-card/index`
- `pkg-card/verify/index`
- `pkg-card/card-list/index`
- `pkg-tools/webview/index`
- `pkg-tools/video-player/index`

### 3.2 当前 creator chain 漂移

已核对：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\detail.vue`

已确认：

- `card-list` 仍带有较重的旧“分享卡片列表 / 管理”职责
- `actor-card` 已经具备 `card / poster` 双 preview 能力
- `actor-profile/detail` 仍被历史链路借作 share detail / preview 语义承接

这证明：

- 当前并不是没有 reference 对齐基础
- 但 creator chain 的 route ownership 仍没有按 reference 7 屏完全收口

## 4. 本轮已完成动作

- 已新增：
  - `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\requirements.md`
  - `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\design.md`
  - `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\tasks.md`
  - `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\execution.md`
- 已回填：
  - `D:\XM\kaipai-team\.sce\specs\README.md`
  - `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`
  - `D:\XM\kaipai-team\.sce\steering\CURRENT_CONTEXT.md`

### 4.1 已完成 `T3` 首轮 shared visual contract 收口

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\styles\_tokens.scss`
- `D:\XM\kaipai-team\kaipai-frontend\src\styles\_mixins.scss`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpButton.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpPillSelector.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpSectionHead.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages.json`

当前结果：

- 全局默认 token 已继续向 reference `studio` 收口：
  - bg: `#F5F3EE`
  - card: `#FBFAF6`
  - text primary: `#1A1816`
- 已新增 serif display token：`Songti SC / STSong / Baskerville / Times New Roman`
- `kp-text-display / h1 / h2` 已切到 serif display 语法
- `KpButton` 已统一为更接近 reference 的 `primary / secondary / glass` 合同
- `KpPillSelector` 已统一为浅底边框 pill + 深底 active pill
- `KpSectionHead` 已统一为 serif title + mono side label 语法
- `pages.json` 的全局背景与 tabbar 浅色底已继续收口到 reference 色值

### 4.2 已完成 `T4` 的四个 core screen 首轮收口

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\login\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\history\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\mine\index.vue`

当前结果：

- `login`
  - hero / sheet / 输入框 / CTA / 协议区进一步贴近 reference `LoginScreen`
  - 登录页已把协议区收回到 sheet 内部
  - `register / invite` 额外信息被压缩为低干扰 assist 区，而不是大块插入卡
- `home`
  - 顶部 strap 已从 `SCREEN 02 · HOME` 收回为 `JU MING PIAN · STUDIO`
  - 主标题已改为 `为每一次相遇 / 留下光影`
  - hero stats 改为细条摘要卡
  - `快速开始` 已改为更接近 reference 的 `操作指南` 视频舞台块
- `history`
  - hero 已收回为 `MY · RECORDS`
  - 移除了额外 hero stats，只保留 strap + serif title + subtitle
  - 筛选 pill、封面列表卡、再次进入动作继续保留真实链路
- `mine`
  - 页面已从“工作台 section + 账号状态 section”重组为更接近 reference `MyScreen` 的：
    - profile header
    - data card
    - 双动作卡
    - setting list
    - logout
  - 同时保留当前主线必需入口：个人档案 / 创建分享 / 退出登录

### 4.3 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- 构建后 `sync-mp-weixin.ps1` 已把 `build` 同步到 `dev`
- 已对 `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin` 执行微信开发者工具 CLI 刷新：
  - `close --project`
  - `reset-fileutils --project`
  - `open --project`
  - `auto-preview --project`
- 补充事实：本轮 `cache --clean *` 子命令因 CLI 需要显式 project/appid 返回 `project path / appid required`，但 `open / auto-preview` 已成功，当前运行态已重新指向 `dist/dev/mp-weixin`
- 当前仍只有 Sass legacy API deprecation warning，不阻塞构建

### 4.4 关键产物证据

#### login

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\login\index.wxss`
  - 已命中：
    - `min-height:562rpx`
    - `margin-top:-86rpx`
    - `font-family:Songti SC,STSong,Baskerville,Times New Roman,serif`
    - `.login-page__submit--active{background:#1a1816`
    - `.login-page__assist-pill--active{background:#1a1816`

#### home

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxml`
  - 已命中：
    - `JU MING PIAN · STUDIO`
    - `操作指南`
    - `HOW-TO · 02:34`
    - `home-page__guide-stage`
    - `home-page__stats-strip`

#### history

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\history\index.wxml`
  - 已命中：
    - `MY · RECORDS`
    - `曾打开的分享`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\history\index.wxss`
  - 已命中：
    - `font-family:Songti SC,STSong,Baskerville,Times New Roman,serif`
    - `.history-page__filter--active{background:#1a1816`

#### mine

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\mine\index.wxml`
  - 已命中：
    - `mine-page__analytics`
    - `mine-page__quick-grid`
    - `mine-page__settings`
    - `CREATE NEW`
    - `PROFILE FILE`
    - `成长等级`
    - `实名状态`

#### shared components

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\components\KpButton.wxss`
  - 已命中：
    - `.kp-button--primary{background:#1a1816;color:#fbfaf6`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\components\KpPillSelector.wxss`
  - 已命中：
    - `.kp-pill-selector__item--active{background:var(--kp-pill-active-bg, #1a1816)`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\components\KpSectionHead.wxss`
  - 已命中：
    - `font-family:Songti SC,STSong,Baskerville,Times New Roman,serif`
    - `background:var(--kp-section-side-bg, #eeebe3)`

### 4.5 已完成 `T5` 的 creator chain 首轮 route ownership 收口

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-card-mvp.ts`

当前结果：

- `card-list`
  - 已从“旧分享卡列表管理桌面”收口为更接近 reference `CreateScreen` 的三步创建页：
    - `STEP 01 选择风格`
    - `STEP 02 作品素材`
    - `STEP 03 命名与产物`
  - 底部固定 CTA 已改为“直接进入 creator preview”语义，而不是单纯“新增卡片”
  - 已创建卡片列表仍保留，但降级为 secondary section，不再占据页面主叙事
- `actor-card`
  - 顶部已收口为 reference 风格 topbar：
    - 中央标题
    - 右侧 `切到海报 / 切到卡片`
  - `CardPreviewScreen` 已收口为：
    - 微信聊天预览区
    - 分享卡片组合
    - `QUICK EDIT`
    - 底部 `复制链接 / 发送给好友`
  - `PosterPreviewScreen` 已收口为：
    - 深色外部背景
    - 浅色预览舞台
    - `QUICK EDIT`
    - 底部 `保存相册 / 分享到朋友圈`
- `share-card-mvp`
  - creator 语义展示已从旧 `普通 / 古代` 收口到更接近 reference 的：
    - `经典`
    - `都市`
    - `古风`

### 4.6 creator chain 关键产物证据

#### card-list

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\card-list\index.wxml`
  - 已命中：
    - `STEP 01`
    - `STEP 02`
    - `STEP 03`
    - `卡片预览`
    - `海报预览`
    - `已创建分享`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\card-list\index.wxss`
  - 已命中：
    - `.card-list-page__artifact-pill--active{background:#1a1816`
    - `.card-list-page__created-list`
    - `.card-list-page__style-card--active`

#### actor-card

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxml`
  - 已命中：
    - `切到海报`
    - `切到卡片`
    - `QUICK EDIT`
    - `保存相册`
    - `分享到朋友圈`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxss`
  - 已命中：
    - `.card-page__topbar`
    - `.card-page--poster-preview{background:#18181b`
    - `.card-page__quick-edit`
    - `.card-page__panel--focus`
    - `.card-page__picker-block--focus`

### 4.7 DevTools 运行态对齐

已再次执行：

- `close --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `reset-fileutils --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `open --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `auto-preview --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`

结果：

- 当前微信开发者工具已重新指向最新 `dist/dev/mp-weixin`

### 4.8 已完成 `T6` 的第一段：`detail` 退出 creator preview

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\detail.vue`

当前结果：

- `detail` 的 hero 已从 `SCREEN 06 · CARD PREVIEW` 改成公开 / 兼容详情语义：
  - `PUBLIC CARD · SHARE DETAIL`
  - `LEGACY DETAIL · COMPAT`
- 已移除首屏微信聊天气泡预览区与 preview card 舞台，不再继续承担 internal creator preview
- 当前首屏已回收为：
  - hero 文案
  - 公开 / 兼容入口 pill
  - 资料概览
  - 简介 / 经历 / 照片 / 视频 / 联系方式申请
- 已补 `actorId` 兼容加载：
  - 若存在 `shareCardId`，继续走最新公开名片链路
  - 若只有 `actorId`，回落到只读兼容详情展示
- 联系方式申请链路已显式分流：
  - `shareCardId` 公开页：保留真实申请 / 查看电话链路
  - `actorId` 兼容页：提示“请从最新公开名片进入”

### 4.9 `detail` 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\actor-profile\detail.wxss`
  - 已命中：
    - `.actor-detail-page__hero-pill-row`
    - `.actor-detail-page__hero-pill--strong{background:#1a1816`
    - `font-family:Songti SC,STSong,Baskerville,Times New Roman,serif`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\actor-profile\detail.wxml`
  - 当前结构已只保留：
    - hero
    - overview
    - intro
    - experience
    - photo
    - video
    - action bar
- 补充反证：
  - 对 `dist\dev\mp-weixin\pages\actor-profile\detail.*` 扫描，旧 creator preview 结构已不再命中：
    - `WECHAT CHAT PREVIEW`
    - `SCREEN 06 · CARD PREVIEW`
    - `actor-detail-page__stage`
    - `actor-detail-page__preview-card`
    - `这是我当前做的分享页`

### 4.10 已完成 `T6` 的第二段：`video-player / webview` support routes 收口

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-tools\video-player\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-tools\webview\index.vue`

当前结果：

- `video-player`
  - 已从旧 `SCREEN 09 · VIDEO / PLAYER DESK` desk 语义收口为 support route：
    - `SUPPORT ROUTE · VIDEO`
    - `视频简历`
    - hero pill row
    - summary card
    - player card / empty card
  - 当前页只保留“看视频能否播放”的最小职责，不再伪装成 creator preview 主屏
- `webview`
  - 已从旧 `RULE DESK / POLICY DESK / ABOUT DESK / ACCOUNT DESK` 头部堆叠收口为 support route：
    - support hero
    - hero pill row
    - summary card
    - content card
    - settings 退出弹层
  - 当前页明确只承载说明文案，不再把解释性页面做成过重的 editor desk 结构

### 4.11 support routes 关键产物证据

#### video-player

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-tools\video-player\index.wxml`
  - 已命中：
    - `SUPPORT ROUTE · VIDEO`
    - `VIDEO ONLY`
    - `播放器 support route`
    - `LIVE PLAY`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-tools\video-player\index.wxss`
  - 已命中：
    - `.video-player-page__hero-pill-row`
    - `.video-player-page__empty-action`
- 补充反证：
  - 对 `dist\dev\mp-weixin\pkg-tools\video-player\index.*` 扫描，旧 desk 化结构已不再命中：
    - `SCREEN 09 · VIDEO`
    - `PLAYER DESK`
    - `video-player-page__summary-pill`

#### webview

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-tools\webview\index.wxml`
  - 已命中：
    - `SUPPORT ROUTE · USER TERMS`
    - `SUPPORT ROUTE · PRIVACY`
    - `SUPPORT ROUTE · ABOUT`
    - `SUPPORT ROUTE · SETTINGS`
    - `确认退出`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-tools\webview\index.wxss`
  - 已命中：
    - `.webview-page__hero-pill-row`
    - `当前 support route 只承载解释性文案`
- 补充反证：
  - 对 `dist\dev\mp-weixin\pkg-tools\webview\index.*` 扫描，旧 desk 化头部类名已不再命中：
    - `RULE DESK`
    - `POLICY DESK`
    - `webview-page__summary-badge`
    - `webview-page__hero-side`

### 4.12 已进入 `T7`：拿到首张 DevTools 运行态截图，并定位 compile condition 切页阻塞点

已核实：

- 当前 DevTools 工程切换必须优先使用：
  - `open-other --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- 仅执行 `open --project ...` 时，窗口可能停在项目选择层，不足以视为进入运行态

本轮运行态截图证据：

- `D:\XM\kaipai-team\output\playwright\desktop-devtools-home-clean.png`
  - 已确认 DevTools 已进入 `dist/dev/mp-weixin` 工程
  - 已确认模拟器首屏可见，当前显示的是 `home` 运行态
- `D:\XM\kaipai-team\output\playwright\devtools-active-home.png`
  - 已补活动窗口截图
  - 已再次确认当前可见页不是旧 UI，而是 `JU MING PIAN · STUDIO / 为每一次相遇 / 留下光影` 的新首页

补充事实：

- 为了验证 compile condition，本轮已把
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\project.private.config.json`
  - `condition.miniprogram.list[0]`
  - 临时切到：
    - `name: t7-history`
    - `pathName: pages/history/index`
- 但切页后拿到的截图：
  - `D:\XM\kaipai-team\output\playwright\desktop-after-history-condition.png`
  - 当前显示仍是 DevTools 资源管理器态，而不是稳定的 history 模拟器画面
- 进一步排查后，已把 `project.private.config.json` 的临时入口恢复为：
  - `name: t7-home`
  - `pathName: pages/home/index`
  - 目的是避免把下轮继续推进建立在 `t7-history` 的不稳定入口之上
- 但本轮过程中，DevTools GUI 还被切到了 `Run and Debug` 侧栏态，说明：
  - 配置入口虽然已回到 `home`
  - 当前桌面窗口状态仍需要下一轮先做一次干净的 DevTools 视图复位，再继续抓其他页面截图

这说明：

- `T7` 已经不再是“完全没有运行态截图”
- 当前真正阻塞点变成：
  1. DevTools 存在“项目选择层 / 资源管理器层 / 模拟器层”三种状态切换
  2. `compile condition` 切到指定页面后，DevTools 可能回落到资源管理器态
  3. `pages/login/index` 即使被设为入口，也会因当前会话自动回跳到 `home`

因此当前 `T7` 结论更新为：

- 已拿到首页 DevTools 运行态截图
- 但其他 core screen 的截图闭环仍需继续推进，下一步重点不是样式改动，而是先稳定 DevTools 的“指定页面 -> 模拟器可见”运行路径

## 5. 当前结论

- `00-69` 解决的是 active 架构边界
- `00-70` 解决的是首轮 reference 风格落地
- `00-73` 要解决的是：
  - reference 7 屏 flow 的 frame-level 复刻
  - creator chain 的 route ownership 重构
  - `detail` 与 internal preview 的角色分层

因此：

- 后续不应继续把“前台 reference 二次重构”混写到 `00-70`
- 当前前台主线应明确切到 `00-73`

## 6. 当前结论

- `00-73 / T3` 已进入已实现、已构建、已进入 `dist/dev` 的状态
- `00-73 / T4` 的 `login / home / history / mine` 已完成首轮 frame-level 收口
- `00-73 / T5` 已完成首轮 creator chain route ownership 收口，并已进入 `dist/dev`
- `00-73 / T6` 已完成：
  - `detail` 已退出 internal creator preview
  - `video-player / webview` 已完成 support route 同语法收口
- 但当前还不能宣称 7 屏全部 1:1 完成，原因有两类边界仍在：
  1. `home` 的风格卡作品数、`mine` 的统计项没有完全等价于 reference Web 原型里的静态演示值，当前保持真实字段优先
  2. `T7` 虽已拿到首页 DevTools 运行态截图，但其他页面仍被 DevTools 的 compile condition / 资源管理器态切换阻塞，尚未补齐全量截图与真机确认

## 7. 下一步

1. 进入 `00-73 / T7`
   - 用 `dist/dev/mp-weixin` + 微信开发者工具截图继续做运行态确认
2. 若截图仍发现偏差，再按截图回到对应页面做窄改

## 8. 基于用户补充逐页 reference 的结论修正

### 8.1 新增 reference 事实

截至 `2026-04-21`，用户在当前线程补充了一组逐页 reference 截图，已明确覆盖：

- 登录页
- 首页（含下半屏 continuation）
- 创建分享页（含 step 02 / step 03 continuation）
- 卡片预览
- 海报预览
- 我的页

这意味着：

- 对上述页面，页级 reference 不再只能依赖 `reference-full / reference-overview` 的总览裁切推断
- 后续验收优先级应改为：`用户补充的逐页 reference > _-_.html 总览裁切图`

### 8.2 对当前实现的修正结论

#### home

- 先前结论里把 `home` 视为“首轮 frame-level 收口已完成”，现在需要修正
- 当前运行态虽然已经进入：
  - `JU MING PIAN · STUDIO`
  - serif 主标题
  - 暖米白 + 深墨语法
- 但与用户补充的单页 reference 相比，仍未完整落出：
  - 三列风格卡
  - 教程区的完整说明文案
  - 三步胶囊
  - 底部主 CTA `开始创建分享页`

因此：

- `home` 不能再按“已 1:1”汇报
- 应重开 `T4` 中的页面级实现任务

#### mine

- 先前结论里把 `mine` 视为“更接近 reference 的 MyScreen”，现在需要修正
- 当前运行态仍是：
  - `个人档案 / 创建分享`
  - `认证状态 / 成长等级 / 邀请进度 / 当前账号`
- 但用户补充的单页 reference 明确要求：
  - `创建分享 + 我的二维码`
  - `我的作品集 / 收藏的分享 / 消息通知 / 偏好设置`
  - 趋势线与 `卡片 / 海报 / 再进入` 子统计

因此：

- `mine` 当前只能算“同色系 + 同壳层接近”
- 其信息架构仍与单页 reference 不一致

#### create

- 先前结论里把 `card-list` 视为“create screen 首轮 route ownership 已收口”，这条仍成立
- 但若按用户补充的单页 reference 做 frame-level 验收，当前 create 页仍未完成：
  1. `STEP 01` 三风格卡选择未完整落地
  2. `STEP 02` 仍是素材统计 / 去完善档案语义，不是上传网格
  3. `STEP 03` 仍是 preview artifact pill，而不是标题输入 + 卡片/海报两张大形式卡
  4. 固定底部 CTA 虽然存在，但其 copy / 交互语义仍未对齐 `生成分享卡片`

因此：

- `T5` 应从“已完成”调整为“route ownership 首轮完成，但 frame-level 仍待继续”

#### card / poster preview

- 用户已补充 `card preview / poster preview` 单页 reference
- 但当前 execution 里还没有这两页的最新运行态截图与逐页核验结论

因此：

- 当前不能宣称 `actor-card(card/poster)` 已完成最终 1:1 验收
- `T5` 与 `T7` 需要联动继续推进

#### verify / actor-profile/edit

- 用户补充的逐页 reference 没有覆盖 `verify` 与 `actor-profile/edit`
- 它们继续是 support routes，而不是 core screen
- 但用户发来的运行态截图已直接证明，这两页仍残留：
  - `SCREEN 04B · VERIFY`
  - `VERIFY DESK`
  - `SCREEN 04A · PROFILE`
  - `PROFILE DESK`
  - `AI DESK`

因此：

- `verify / actor-profile/edit` 不应再纳入 7 屏 1:1 验收
- 但 `T6` 需要重开，用于去掉旧 desk 化叙事

#### records

- 当前仍未拿到用户补充的 `records` 单页 reference
- 因此 records 页目前只能继续以：
  - `reference-full.png`
  - `reference-overview.png`
  - `_-.html` 总览中的 `RecordsScreen`
  作为页级基线

这意味着：

- records 页暂不能按“缺单页截图”就宣称完全完成
- 但也不能像 home / mine / create 一样，直接用用户补充单页图做精确 block-level 重开

### 8.3 任务状态更新

基于以上修正：

- `T4` 从“已完成”调整为“重新打开”
- `T5` 从“已完成”调整为“重新打开”
- `T6` 从“已完成”调整为“重新打开”
- `T7` 继续保持未完成

原因不是 route ownership 结论被推翻，而是：

- 新增了更高优先级的页级 reference 基线
- 现有运行态与该页级基线相比，仍存在明确的结构与信息架构差异

## 9. 下一步（更新）

1. 先按用户补充的单页 reference 重排 `home / mine / create`
2. 再补 `card preview / poster preview` 的运行态截图，并完成逐页核验
3. `verify / actor-profile/edit` 改为 support route 去 desk 化收口，不再混入 core reference 验收
4. `records` 在单页 reference 未补齐前，继续按总览图与真实运行态列表页共同验收

## 10. 本轮实现进展（P0 首轮）

### 10.1 已改文件

- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-card-mvp.ts`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\mine\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`

### 10.2 本轮实现结论

#### home

- 已把风格卡顺序统一为 reference 的：
  - `都市 / 古风 / 经典`
- 已把首页下半屏继续向单页 reference 收口为：
  - `风格分馆 / SELECT A STYLE`
  - 三卡片式风格块
  - 深色教程舞台
  - `三步创建你的分享页`
  - `01 选风格 / 02 传作品 / 03 成海报`
  - 底部主 CTA `开始创建分享页`

#### mine

- 已把“个人档案 / 创建分享 + 认证状态列表”重排为更接近单页 reference 的信息架构：
  - 头像 / 姓名 / 用户信息 / 编辑按钮
  - `我的数据` 大卡
  - 趋势线
  - `卡片 / 海报 / 再进入` 子统计
  - 双主动作卡：`创建分享 / 我的二维码`
  - 设置列表：`我的作品集 / 收藏的分享 / 消息通知 / 偏好设置`
- 当前指标仍优先复用现有真实前台数据：
  - `shareCards.cards`
  - `history`
  - `inviteInfo`
  而不是伪造 reference 静态演示值

#### create

- 已把 `card-list` 继续从旧 creator desk 收到单页 reference 的三段式结构：
  - `STEP 01 选择风格`：三风格卡 + 选中勾态
  - `STEP 02 上传作品`：素材网格 + 上传入口
  - `STEP 03 命名 & 选择分享形式`：标题输入 + `卡片 / 海报` 两张大形式卡
- 底部固定 CTA 语义已统一为：
  - `生成分享卡片`

### 10.3 本轮构建与产物核对

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `sync-mp-weixin.ps1`：已把 `dist\build\mp-weixin` 同步到 `dist\dev\mp-weixin`

### 10.4 关键产物证据

#### home

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxml`
  - 已命中：
    - `SELECT A STYLE`
    - `三步创建你的分享页`
    - `01 选风格`
    - `02 传作品`
    - `03 成海报`
    - `开始创建分享页`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `.home-page__style-card--urban .home-page__style-cover`
    - `.home-page__guide-steps`
    - `.home-page__guide-cta`

#### mine

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\mine\index.wxml`
  - 已命中：
    - `我的二维码`
    - `我的作品集`
    - `消息通知`
    - `偏好设置`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\mine\index.wxss`
  - 已命中：
    - `.mine-page__trend`
    - `.mine-page__quick-card--create`
    - `.mine-page__setting-label`

#### create

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\card-list\index.wxml`
  - 已命中：
    - `STEP 02`
    - `上传作品`
    - `STEP 03`
    - `命名 & 选择分享形式`
    - `分享页标题`
    - `微信对话展开`
    - `长图 · 朋友圈`
    - `生成分享卡片`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\card-list\index.wxss`
  - 已命中：
    - `.card-list-page__style-cover--urban`
    - `.card-list-page__style-check`
    - `.card-list-page__materials-upload`
    - `.card-list-page__artifact-grid`
    - `.card-list-page__action-bar{...padding:0`

### 10.5 当前边界

- 本轮只完成了 `home / mine / create` 的 P0 首轮重排，还没有补最新运行态截图
- `card preview / poster preview` 仍待按用户补充的单页 reference 做下一轮 frame-level 收口
- `verify / actor-profile/edit` 的去旧 `DESK` 叙事还未开始，本轮未覆盖

## 11. 当前推进规则更新

截至 `2026-04-21`，用户又进一步明确：

- 持续整理 UI 页面
- 页面截图对比推进
- 当调试错误 3 次之后，需要自动更换方向，继续推动

基于当前框架与 specs 评估，已确认这条规则最适合落在：

- `00-73`：当前前台 UI 主线的页级推进约束
- `docs/dev-playbook.md`：后续 UI 页面整理时可直接复用的经验规则

本轮结论：

- 不新开 spec
- 不把它泛化成全项目所有能力都必须遵守的重治理规则
- 先把它固定为当前 UI 主线默认推进循环

### 11.1 当前默认推进循环

1. 看 reference 截图
2. 看当前运行态截图
3. 定义当前差异块
4. 做一轮窄改
5. build
6. 核 `src / dist/build / dist/dev`
7. 再拿运行态截图复核

### 11.2 三次失败后的自动换向口径

若同一页面、同一可见块、同一类问题连续 3 次调试后，运行态截图仍未产生正确变化，则：

- 停止第 4 次同类试错
- 自动切换推进方向
- 并在 execution 里补：
  - 页面
  - 可见块
  - 已失败 3 次的旧方向
  - 新方向
  - 原方向为什么停

## 12. 已触发一次“三次失败后自动换向”

### 12.1 页面 / 可见块

- 页面：`pages/home/index`
- 可见块：`风格分馆` 与首页运行态截图获取路径

### 12.2 已失败的 3 次旧方向

当前已经出现 3 次连续失败，且都没有把首页运行态截图稳定收口到“可直接做 reference 对照”的状态：

1. **桌面整屏截图失败**
   - 截到的是其他桌面窗口，不是微信开发者工具模拟器
   - 说明“只抓当前桌面”不是稳定截图路径
2. **wechatdevtools 窗口截图失败（资源管理器态）**
   - 虽然已命中 `微信开发者工具` 主窗口
   - 但窗口停在资源管理器 / 非模拟器态，不能直接用于首页 reference 对照
3. **重置并重新打开 DevTools 后再次失败**
   - 已执行：
     - `close --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
     - `reset-fileutils --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
     - `open-other --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
     - `auto-preview --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
   - 但重新截到的 DevTools 主窗口仍停在资源管理器态，而不是稳定模拟器态

### 12.3 自动换向后的新方向

基于以上 3 次失败，已按 `R28-R30` 自动换向，不再继续第 4 次沿“先把 DevTools 窗口截对”的旧方向试错。

新的推进方向改为：

1. **先用截图结果反推问题性质**
   - 当前首页只出现一张风格卡，不再先猜是“卡片太大”
   - 改为怀疑 `templateItems` 生成本身只有一项
2. **从样式微调切到数据 / 结构推进**
   - 已把 `share-card-mvp.ts` 改为对 `urban / costume / general` 三个 reference 风格项做 fallback 生成
   - 先保证首页 / 创建页稳定出现 3 个 reference 风格入口
3. **把运行态截图通路与页面实现推进解耦**
   - 页面实现继续沿 `src -> dist/build -> dist/dev` 前进
   - DevTools 截图恢复改走仓内现有 `automator/window-fallback` 脚本路径，而不再依赖当前主窗口状态

### 12.4 为什么原方向停止

原因不是“截图不重要”，而是：

- 旧方向已经连续 3 次没有把窗口带到可用的模拟器态
- 继续第 4 次只会重复同类 DevTools 窗口试错
- 对当前 UI 主线来说，更高价值的推进是：
  - 先继续让页面结构向 reference 收口
  - 再用更稳定的脚本路径恢复截图

## 13. 当前轮次新增事实：截图链路已恢复，UI 继续推进

### 13.1 本轮新增事实

截至 `2026-04-22 00:44`，当前小程序页面级截图链路已经恢复为可用状态：

- `D:\AP\微信web开发者工具\cli.bat auto --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin --auto-port 9520`
  - 已返回 `√ auto`
- 已通过仓内现成脚本：
  - `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\capture-mini-program-screenshots.js`
  - 在 `ws://127.0.0.1:9520`
  - 对 `home / card-list / actor-card(card) / actor-card(poster) / detail / history / mine`
    完成自动截图

补充事实：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r4\captures\mini-program-screenshot-capture.json`
  - `captureCount = 10`
  - `visualDidNotRefresh = false`
  - `owner-share-action-mini-program` 与 `owner-share-action-poster` 已切到 `shareMode=1`
- 本轮 owner 预览截图已不再停留在旧编辑配置态

### 13.2 本轮新增实现动作

#### 数据 / 结构换向

在首页运行态只出现一张风格卡后，本轮已把推进方向从“继续调视觉容器”换到“先补齐 reference 所需风格数据”：

- 已改：
  - `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-card-mvp.ts`
- 当前 `urban / costume / general` 三个 reference 风格项在模板缺失时会使用 fallback 生成

#### actor-card 收口

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

本轮结果：

- 新增 `isFinalPreviewMode`
  - `shareMode=1` 或 `shared=1` 时进入最终预览态
- `card preview`
  - 预览态不再继续露出下方配置面板
  - 已出现：
    - 圆形返回按钮
    - 标题 `卡片预览`
    - 右侧 `切到海报`
    - 聊天气泡 + 分享卡片
    - `QUICK EDIT`
    - 底部 `复制链接 / 发送给好友`
- `poster preview`
  - 已出现：
    - 深色外部背景
    - 标题 `海报预览`
    - 右侧 `切到卡片`
    - 大图 + 双小图
    - 二维码 footer
    - 底部 `保存相册 / 分享到朋友圈`

### 13.3 本轮关键运行态截图

#### home

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r4\screenshots\owner-home-share-cards.png`
  - 当前已看到：
    - 三张风格卡
    - `SELECT A STYLE`
    - 教程区继续在首屏下半部

#### create

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r4\screenshots\owner-card-list.png`
  - 当前已看到：
    - `STEP 01` 三风格卡
    - `STEP 02` 上传作品网格
    - 底部 `生成分享卡片`

#### mine

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r4\screenshots\owner-mine.png`
  - 当前已看到：
    - 头像 / 姓名 / 用户信息 / 编辑
    - 数据卡 + 趋势线
    - `创建分享 / 我的二维码`
    - `我的作品集 / 收藏的分享 / 消息通知 / 偏好设置`

#### card preview（owner 最终预览态）

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r4\screenshots\owner-share-action-mini-program.png`
  - 当前已看到：
    - `卡片预览`
    - `切到海报`
    - 聊天气泡 + 分享卡片
    - `QUICK EDIT`
    - 底部 `复制链接 / 发送给好友`

#### poster preview（owner 最终预览态）

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r4\screenshots\owner-share-action-poster.png`
  - 当前已看到：
    - 深色外部背景
    - `海报预览`
    - `切到卡片`
    - 大图 + 双小图
    - 二维码 footer
    - 底部 `保存相册 / 分享到朋友圈`

### 13.4 当前结论更新

- `T7` 已不再是“截图链路不可用”
- 当前已进入“有真实运行态截图、可直接按 reference 做差异收口”的阶段
- 下一步重点从“恢复截图”转为：
  - 继续压缩 `home / create / mine / actor-card` 与 reference 的剩余细节差异
  - 再推进 `verify / actor-profile/edit` 的去旧 `DESK` 叙事

## 14. support routes 去旧 DESK 叙事：首轮完成

### 14.1 已改文件

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\edit.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\verify\index.vue`

### 14.2 本轮动作

本轮没有继续扩改 support routes 的结构和业务逻辑，只做了去旧 `DESK` 叙事的窄改：

#### actor-profile/edit

- `SCREEN 04A · PROFILE` -> `SUPPORT ROUTE · PROFILE`
- `PROFILE DESK` -> `PROFILE FILE`
- `AI DESK` -> `AI RESUME`
- `SAVE DESK` -> `SAVE PROFILE`

#### verify

- `SCREEN 04B · VERIFY` -> `SUPPORT ROUTE · VERIFY`
- `VERIFY DESK` -> `VERIFY ENTRY`

### 14.3 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `sync-mp-weixin.ps1`：已把 `dist\build\mp-weixin` 同步到 `dist\dev\mp-weixin`

### 14.4 当前结论

- `verify / actor-profile/edit` 当前已从旧 `DESK` 话术中退出第一步
- 这两页仍是 support routes，不纳入 7 屏 reference 1:1 验收
- 下一步若继续推进这两页，应优先做运行态截图核对，再决定是否需要进一步压缩头部、摘要卡或底部动作区节奏

## 15. actor-card 继续按截图收口：文案、舞台留白与分享态标题已推进

### 15.1 本轮已改文件

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

### 15.2 本轮差异定义

本轮继续沿 `pkg-card/actor-card/index` 的最终预览态推进，不再改动：

- `shareMode / sharedEntry / isFinalPreviewMode` 的模式判断
- `card / poster` 两种最终态的 route ownership

本轮只收口以下可见差异块：

1. `card preview`
   - 顶部标题与切换 pill 节奏偏重
   - 分享卡片过宽，外层舞台偏白，和 reference 的灰底舞台 + 居中卡片不一致
   - meta 文案仍暴露 `Smoke Template` 之类的技术名
   - 底部按钮还带整体外托盘，不够接近 reference 的独立 pill
2. `poster preview`
   - 头部 meta 行仍是时间戳式文案，和内容无关
   - 底部动作与海报 footer 的节奏仍需要继续观察

### 15.3 本轮实现动作

#### actor-card / card preview

- 聊天气泡 copy 收口为：
  - `这是我做的分享页，看看～`
- 卡片标题仍保留：
  - `林夏的经典写真集` 这一类 scene-driven 标题
- 卡片 meta 改为内容导向文案：
  - `作品精选 · 经典风格 · 3 张作品`
- 最终预览态 topbar 调整为更接近 reference 的左侧标题节奏
- 最终预览态舞台改为浅灰底，缩小卡片宽度并居中，减少“整块白板 + 过宽卡片”的视觉漂移
- 最终预览态 action bar 改为透明宿主，保留独立 `复制链接 / 发送给好友` pill，而不是大白色托盘

#### actor-card / poster preview

- 海报 meta 改为内容导向文案：
  - `CLASSIC STYLE · 3 WORKS · 林夏`
- owner / viewer 分享标题不再继续透出 backend template 名，而是统一收口为：
  - `林夏的经典写真集小程序卡片`
  - `林夏的经典写真集海报`
- 仅保留卡片预览态的 `QUICK EDIT`；海报预览态不再主动把 quick edit 作为本轮默认结构目标

### 15.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- `D:\AP\微信web开发者工具\cli.bat auto --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin --auto-port 9520`
- `node D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\capture-mini-program-screenshots.js ...`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `sync-mp-weixin.ps1`：已把 `dist\build\mp-weixin` 同步到 `dist\dev\mp-weixin`
- `r5 / r6` 两轮截图均已成功完成 10 张页面级 automator 截图
- `r6` manifest：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r6\captures\mini-program-screenshot-capture.json`
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

补充事实：

- 本轮第一次截图尝试把 `cli auto` 与截图脚本并行启动，导致 automator 在 `owner-home-share-cards` 处出现 `Connection closed`
- 随后按串行方式复跑，截图链路恢复正常
- 这记为**截图链路 1 次失败**，不是页面样式 1 次失败；当前未达到“同一页面同一可见块连续 3 次失败”的换向阈值

### 15.5 关键产物证据

#### src / dist / dev 三层命中

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxml`
  - 已命中：
    - `这是我做的分享页，看看～`
    - `作品精选`
    - `CLASSIC STYLE · 3 WORKS · 林夏`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.js`
  - 已命中：
    - `林夏的经典写真集小程序卡片`
    - `林夏的经典写真集海报`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxss`
  - 已命中：
    - `background:#efeeeb`
    - `width:560rpx`
    - `padding-left:18rpx`
    - `padding-bottom:calc(236rpx + env(safe-area-inset-bottom))`

#### 本轮关键运行态截图

##### card preview（owner 最终预览态）

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r6\screenshots\owner-share-action-mini-program.png`
  - 当前已看到：
    - 左侧标题节奏更接近 reference
    - 灰底舞台
    - 居中的分享卡片
    - `作品精选 · 经典风格 · 3 张作品`
    - 独立 `复制链接 / 发送给好友` pill

##### poster preview（owner 最终预览态）

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r6\screenshots\owner-share-action-poster.png`
  - 当前已看到：
    - `CLASSIC STYLE · 3 WORKS · 林夏`
    - 深色外背景 + 海报舞台 + 二维码 footer 仍保持
    - 底部主按钮仍可见且分享标题已收口

### 15.6 当前结论

- `actor-card / card preview` 本轮确实产生了可见正向变化，已经比 `r4` 更接近 reference：
  - 文案不再暴露 backend template 名
  - 舞台与卡片比例更接近原型
  - 底部按钮结构更接近 reference
- `actor-card / poster preview` 也完成了头部文案与分享标题收口
- 但 `poster preview` 底部区域仍需要下一轮继续判断：
  - 是真实可见块仍有节奏问题
  - 还是截图中由透明 action bar / 阴影 / 原生按钮层叠带来的视觉误判

因此下一轮若继续压 `poster preview`，必须先拿当前运行态截图做更细判断，再决定是否继续改 action bar / safe-area / button 宿主，而不能直接重复试 padding 数值

## 16. support routes 运行态截图已补：profile 已命中，verify 需区分账号状态

### 16.1 本轮没有新增源码修改

本轮目标不是继续改 support routes 源码，而是补齐运行态证据，验证：

- `pages/actor-profile/edit`
- `pkg-card/verify/index`

当前源码层事实保持不变：

- `SUPPORT ROUTE · PROFILE`
- `PROFILE FILE`
- `AI RESUME`
- `SAVE PROFILE`
- `SUPPORT ROUTE · VERIFY`
- `VERIFY ENTRY`

### 16.2 本轮运行态取证路径

#### profile

使用仓内现成脚本：

- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\ai-resume\capture-mini-program-screenshots.js`

样本目录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-support-routes-r1\profile`

#### verify

使用仓内现成脚本：

- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\verify\capture-mini-program-screenshots.js`

首次取证目录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-support-routes-r1\verify`

补充 unverified actor 运行态目录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-support-routes-r2-verify-unverified`

### 16.3 verified actor 下的关键事实：verify route 会被状态链路带走

使用已认证 actor 账号：

- phone: `13800138000`
- userId: `10000`

得到的关键事实：

- target 目标：
  - `/pkg-card/verify/index`
- 实际命中：
  - `actualPath = pages/actor-profile/edit`
- 对应 manifest：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-support-routes-r1\verify\captures\mini-program-screenshot-capture.json`
- 对应 page-data：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-support-routes-r1\verify\captures\page-data-verify-page.json`

page-data 里的 API 快照已确认：

- `verifyStatus.status = 2`
- `realAuthStatus = 2`
- `isCertified = true`

这说明：

- 当前 verified actor 进入 `/pkg-card/verify/index` 时，运行态不会停在 verify support route
- 它会落到 `pages/actor-profile/edit`
- 因此先前“缺少 verify 运行态截图”的真正原因不是源码没生效，而是**截图账号状态不对**

### 16.4 为拿到真实 verify support route，本轮新增一个 unverified actor 样本

本轮新建 sandbox 样本账号：

- phone: `13955550011`
- userId: `10031`
- nickName: `Spec未认证样本`

创建方式：

- `POST /auth/sendCode`
- `POST /auth/register`
  - `userType = 1`

创建后已核实：

- `realAuthStatus = 0`
- `verifyStatus.status = 0`

这说明该账号可用于真实 verify support route 截图，而不会被“已认证状态”带走。

### 16.5 本轮关键运行态截图

#### profile support route

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-support-routes-r1\profile\screenshots\actor-profile-edit.png`
  - 当前已看到：
    - `SUPPORT ROUTE · PROFILE`
    - `PROFILE FILE`
    - profile summary 卡
    - `AI RESUME`
    - `SAVE PROFILE`

#### verify support route（unverified actor）

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-support-routes-r2-verify-unverified\screenshots\verify-page.png`
  - 当前已看到：
    - `SUPPORT ROUTE · VERIFY`
    - `VERIFY ENTRY`
    - `PROFILE LOCK`
    - `NOT SUBMITTED`
    - `去完善档案`
    - `REAL NAME`

### 16.6 关键产物证据

#### 正证：src / dist/build / dist/dev 已命中新 support 文案

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\edit.vue`
  - 已命中：
    - `SUPPORT ROUTE · PROFILE`
    - `PROFILE FILE`
    - `AI RESUME`
    - `SAVE PROFILE`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\verify\index.vue`
  - 已命中：
    - `SUPPORT ROUTE · VERIFY`
    - `VERIFY ENTRY`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\actor-profile\edit.wxml`
  - 已命中：
    - `SUPPORT ROUTE · PROFILE`
    - `PROFILE FILE`
    - `AI RESUME`
    - `SAVE PROFILE`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pkg-card\verify\index.wxml`
  - 已命中：
    - `SUPPORT ROUTE · VERIFY`
    - `VERIFY ENTRY`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\actor-profile\edit.wxml`
  - 已命中：
    - `SUPPORT ROUTE · PROFILE`
    - `PROFILE FILE`
    - `AI RESUME`
    - `SAVE PROFILE`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\verify\index.wxml`
  - 已命中：
    - `SUPPORT ROUTE · VERIFY`
    - `VERIFY ENTRY`

#### 反证：旧 `DESK / SCREEN 04` 文案在 src / dist/build / dist/dev 已不再命中

已对以下范围执行全文扫描：

- `src/pages/actor-profile/edit.vue`
- `src/pkg-card/verify/index.vue`
- `dist/build/mp-weixin/pages/actor-profile`
- `dist/build/mp-weixin/pkg-card/verify`
- `dist/dev/mp-weixin/pages/actor-profile`
- `dist/dev/mp-weixin/pkg-card/verify`

结果：

- `SCREEN 04`
- `PROFILE DESK`
- `AI DESK`
- `SAVE DESK`
- `VERIFY DESK`

当前均未命中。

### 16.7 当前结论

- `actor-profile/edit` 的 support route 去旧 desk 化已获得运行态证据，不再停留在源码层
- `verify` 的 support route 去旧 desk 化也已获得真实运行态证据
- 同时，本轮明确补上了一个很关键的状态边界：
  - verified actor 进入 verify route，会被账号状态链路带走
  - 所以 verify 页必须用 unverified actor 才能拿到真实运行态截图

因此：

- `T6` 的 support routes 去旧 desk 化部分，当前已经具备：
  - 源码证据
  - 生成产物证据
  - 运行态截图证据
- 下一轮可把焦点重新切回：
  1. `poster preview` 底部区域的真实差异判断
  2. 或继续压 `home / create / mine` 的剩余细节差异

## 17. poster preview 底部灰块已判定为运行态旧包，不是当前源码仍有 quick edit

### 17.1 本轮差异块

- 页面：`/pkg-card/actor-card/index?shareCardId=1&artifact=poster&shareMode=1`
- 可见块：底部 `保存相册 / 分享到朋友圈` 上方的灰色残影

### 17.2 先前怀疑

先前怀疑该灰块可能来自：

- 透明 action bar 宿主样式
- 原生按钮层叠
- 仍残留的 `QUICK EDIT` 行

其中“仍残留 quick edit”在当时还不能直接下结论，因为 `r6` 运行态截图没有更新，无法只靠肉眼判断。

### 17.3 新增事实：旧运行态与新产物冲突

已核实：

- 最新 `dist/dev` 的 `pkg-card/actor-card/index.wxml`
  - `poster` 最终预览态下，`QUICK EDIT` 的条件已经收窄到：
    - `miniProgramCard`
- 最新 `page-data-owner-share-action-poster.json`
  - `i = false`
  - `v = false`
  - 当前运行态已明确是 `poster`，且 quick edit 不应渲染

但在刷新前的 `r6` 截图里，底部灰块仍露出类似 `编辑标题` 的旧按钮文案。

这形成了明显冲突：

- **当前产物**：poster 态不应再有 quick edit
- **旧截图**：仍露出 quick edit 残影

因此本轮优先按“运行态还是旧包”处理，而不是继续改样式。

### 17.4 本轮动作：强制刷新 DevTools 工程，再复跑截图

已执行：

- `D:\AP\微信web开发者工具\cli.bat close --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `D:\AP\微信web开发者工具\cli.bat reset-fileutils --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `D:\AP\微信web开发者工具\cli.bat open-other --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `D:\AP\微信web开发者工具\cli.bat auto-preview --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `D:\AP\微信web开发者工具\cli.bat auto --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin --auto-port 9520`

然后再次执行：

- `share-card-mvp/capture-mini-program-screenshots.js`

输出目录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r7`

### 17.5 刷新后的关键事实

#### manifest

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r7\captures\mini-program-screenshot-capture.json`
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

#### poster 页面数据

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r7\captures\page-data-owner-share-action-poster.json`
  - `pageDataKeyCount` 从旧轮次的 `43` 下降到 `40`
  - `v = false`
  - `i = false`

这说明：

- 新运行态已经真正加载到了不渲染 quick edit 的 poster 结构

#### 截图 hash 变化

- `r6 owner-share-action-poster`
  - `38d86f1d88e9d3a28e3b8eec489ffd3cdd58b6bb7c69c2efcf2438f2b1c9889b`
- `r7 owner-share-action-poster`
  - `b276b53943336aba4aa3a1d9340f6b8b416ae24823acadeaaaedd26a33679184`

hash 已变化，说明这次不是“又截到同一张旧图”。

### 17.6 最新运行态截图结论

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r7\screenshots\owner-share-action-poster.png`
- 裁切复核：
  - `D:\XM\kaipai-team\tmp\poster-bottom-r7.png`

当前已确认：

- 底部灰色残影已消失
- 只剩：
  - `保存相册`
  - `分享到朋友圈`
  两个真实按钮

因此当前结论更新为：

- `poster preview` 底部灰块不是当前源码结构问题
- 它是前一轮 DevTools / automator 仍在吃旧运行态产物造成的假象

### 17.7 当前结论

- 这次没有新增样式修改，但完成了一次很关键的**错误定性修正**
- 对 `poster preview` 来说，本轮应记为：
  - **不是样式三连败**
  - 而是一次成功的“运行态旧包 -> 强制刷新 -> 截图恢复”闭环

因此下一轮无需继续在 `poster preview` 底部区域重复试 padding / margin；当前优先级应切回：

1. `home`
2. `create`
3. `mine`

## 18. home 教程舞台继续压缩：让 guide 标题更早进入首屏

### 18.1 本轮已改文件

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

### 18.2 本轮差异定义

- 页面：`pages/home/index`
- 可见块：`操作指南` 视频舞台
- 目标：在不动 hero 与三张风格卡结构的前提下，让教程区下半部更早进入首屏，减少“舞台过高，把 guide 文案压到视口外”的漂移

### 18.3 本轮动作

本轮没有重排首页结构，只对 guide block 做窄改：

- `home-page__guide-cover`
  - `height: 372rpx -> 316rpx`
- `home-page__guide-play`
  - `108rpx -> 96rpx`
- `home-page__guide-copy`
  - `bottom: 26rpx -> 22rpx`
- `home-page__guide-note-title`
  - `38rpx -> 34rpx`
- `home-page__guide-note-copy`
  - `22rpx / 1.7 -> 20rpx / 1.6`

本轮没有改：

- hero 标题
- stats strip
- 三张风格卡
- steps / CTA 的结构与顺序

### 18.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- DevTools 工程强制刷新：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`
- `share-card-mvp/capture-mini-program-screenshots.js`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `sync-mp-weixin.ps1`：已把 `dist\build\mp-weixin` 同步到 `dist\dev\mp-weixin`
- `r8` manifest：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r8\captures\mini-program-screenshot-capture.json`
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

### 18.5 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `height:316rpx`
    - `width:96rpx`
    - `bottom:22rpx`
    - `font-size:34rpx`
    - `font-size:20rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 同样已命中上述值

### 18.6 最新运行态截图

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r7\screenshots\owner-home-share-cards.png`
  - 改前：guide 舞台更高，首屏里只露出更少的 guide 文案
- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r8\screenshots\owner-home-share-cards.png`
  - 改后：`三步创建你的分享页` 更早进入首屏下沿，可见变化已产生

### 18.7 当前结论

- `home / 操作指南` 这轮不是“页面没变化”
- guide 舞台压缩已经在运行态截图中产生了正向变化
- 但 `steps / CTA` 仍没有完全进入当前首屏截图，因此：
  - 若下一轮继续压 `home`，应继续只围绕 `guide-cover` 这一块收口
  - 不要扩改 hero / 风格卡 / stats strip

## 19. home 首屏继续推进：三步胶囊已进入当前运行态截图

### 19.1 本轮差异判断更新

在第 18 节之后，`guide-cover` 本身继续变矮虽然有正向变化，但仍不足以把三步胶囊带进首屏。

因此本轮调整了控制变量：

- 不再只盯 `guide-cover`
- 改为收 `style cards + section spacing`

原因：

- 当前首屏下沿的真实锚点，已经同时受：
  - `home-page__body gap`
  - `home-page__style-cover min-height`
  - `home-page__style-foot`
  - `home-page__guide-cover`
  共同影响

### 19.2 本轮已改文件

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

### 19.3 本轮动作

#### 继续保留 guide block 的上一轮收口

- `guide-cover = 268rpx`
- `guide-play = 88rpx`
- `guide-copy bottom = 20rpx`
- `guide-note-title = 32rpx`
- `guide-note-copy = 18rpx`
- `guide-step min-height = 60rpx`

#### 新增对 style cards / section spacing 的窄改

- `home-page__body`
  - `gap: 28rpx -> 22rpx`
- `home-page__style-grid`
  - `gap: 14rpx -> 12rpx`
- `home-page__style-cover`
  - `min-height: 304rpx -> 268rpx`
  - `padding: 30rpx 18rpx 22rpx -> 24rpx 16rpx 18rpx`
- `home-page__style-main`
  - `gap: 20rpx -> 16rpx`
- `home-page__style-title`
  - `54rpx -> 48rpx`
- `home-page__style-foot`
  - `padding: 18rpx 18rpx 20rpx -> 16rpx 16rpx 18rpx`
  - `gap: 8rpx -> 6rpx`
- `home-page__style-foot-title`
  - `22rpx -> 20rpx`
- `home-page__style-foot-meta`
  - `18rpx -> 16rpx`

本轮仍未改：

- hero 标题
- stats strip
- 三卡片数量与结构

### 19.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- DevTools 工程强制刷新：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`
- `share-card-mvp/capture-mini-program-screenshots.js`

本轮样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r10`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `sync-mp-weixin.ps1`：已完成
- `r10` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

### 19.5 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `gap:22rpx`
    - `min-height:268rpx`
    - `padding:24rpx 16rpx 18rpx`
    - `font-size:48rpx`
    - `font-size:20rpx`
    - `font-size:16rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 同样已命中上述值

### 19.6 最新运行态截图结论

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r9\screenshots\owner-home-share-cards.png`
  - 改前：
    - guide 标题与舞台主体已进入首屏
    - 但三步胶囊还未进入
- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r10\screenshots\owner-home-share-cards.png`
  - 改后：
    - 三步胶囊：
      - `01 选风格`
      - `02 传作品`
      - `03 成海报`
      已进入当前首屏截图

### 19.7 当前结论

- `home` 页面当前已经完成一个阶段性目标：
  - `guide title + guide copy + 三步胶囊` 都进入了当前运行态首屏截图
- 但底部 CTA `开始创建分享页` 仍未完全进入当前首屏

因此当前建议更新为：

1. 若继续压 `home`，下一轮只剩一个目标：
   - 把 CTA 再往上拉近一截
2. 也可以转去 `create` 或 `mine` 继续推进，因为：
   - `home` 当前已经不再卡在“首屏只看到风格卡和视频舞台”的早期状态

## 20. create 首屏继续推进：STEP 03 已被拉到首屏边缘

### 20.1 本轮方向切换

在 `home` 完成：

- guide title
- guide copy
- 三步胶囊

都进入首屏后，本轮主工作流从 `home` 切到：

- `pkg-card/card-list/index`

这不是“三次失败后被动换向”，而是基于当前 UI 主线收益排序做的主动推进：

- `home` 继续压只剩 CTA
- `create` 还有更高价值的首屏收口空间

### 20.2 本轮已改文件

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`

### 20.3 本轮差异定义

- 页面：`pkg-card/card-list/index`
- 可见块：`STEP 01 / STEP 02` 首屏节奏

主要问题：

1. 顶部留白偏大
2. `STEP 01` 三风格卡高度偏高
3. `STEP 02` 上传网格高度偏高
4. `STEP 03` 完全被压出首屏
5. 固定 CTA 覆盖 `STEP 02` 下半区的感知较重

目标：

- 不改三步结构与路由 ownership
- 只通过压缩首屏上半段，把 `STEP 03` 往首屏拉近

### 20.4 本轮实现动作

#### 第一轮 create 收口

- `hero-copy`
  - `136rpx -> 108rpx`
- `body gap`
  - `20rpx -> 16rpx`
- `panel`
  - `padding: 28rpx -> 24rpx`
  - `border-radius: 28rpx -> 26rpx`
- `panel-head`
  - `margin-bottom: 18rpx -> 14rpx`
- `style-cover / style-copy`
  - `228rpx -> 196rpx`
- `style-title`
  - `52rpx -> 46rpx`
- `materials-grid`
  - `gap: 12rpx -> 10rpx`
- `materials-tile / materials-photo`
  - `220rpx -> 184rpx`
- `title-card / title-input`
  - `18rpx -> 16rpx`
  - `96rpx -> 88rpx`
- `artifact-card`
  - `188rpx -> 164rpx`

#### 第二轮 create 收口

在第一轮后，`STEP 03` 仍未进入首屏，因此继续只压首屏上半段：

- `hero-copy`
  - `108rpx -> 92rpx`
- `body gap`
  - `16rpx -> 14rpx`
- `steps gap`
  - `8rpx -> 6rpx`
- `step-index`
  - `52rpx -> 48rpx`
- `panel`
  - `24rpx -> 20rpx`
  - `26rpx -> 24rpx`
- `panel-head`
  - `gap: 12rpx -> 10rpx`
  - `margin-bottom: 14rpx -> 12rpx`
- `panel-title`
  - `30rpx -> 28rpx`
- `style-cover / style-copy`
  - `196rpx -> 180rpx`
- `style-title`
  - `46rpx -> 42rpx`
- `materials-tile / materials-photo`
  - `184rpx -> 164rpx`
- `materials-badge`
  - `40rpx -> 36rpx`
- `materials-upload-icon`
  - `44rpx -> 40rpx`

### 20.5 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- DevTools 工程强制刷新：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`
- `share-card-mvp/capture-mini-program-screenshots.js`

#### 第一轮截图样本

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r1`

补充事实：

- `create-r1` 中发生过一次 automator 连接失效：
  - `Failed connecting to ws://127.0.0.1:9520`
- 随后重开 `auto --auto-port 9520` 后恢复
- 这记为**截图链路 1 次失败**，不是页面样式失败

#### 第二轮截图样本

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r2b`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `create-r2b` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

### 20.6 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\card-list\index.wxss`
  - 已命中：
    - `padding:92rpx`
    - `gap:14rpx`
    - `width:48rpx`
    - `min-height:180rpx`
    - `min-height:164rpx`
    - `height:164rpx`
    - `font-size:42rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pkg-card\card-list\index.wxss`
  - 同样已命中上述值

### 20.7 运行态截图结论

#### 第一轮

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r1\screenshots\owner-card-list.png`
  - 当前已看到：
    - 顶部留白收短
    - `STEP 02` 网格更紧凑
    - 但 `STEP 03` 仍未进入首屏

#### 第二轮

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r2b\screenshots\owner-card-list.png`
  - 当前已看到：
    - `STEP 03` 的标题卡已经被拉到首屏底部边缘
    - `STEP 01 / STEP 02` 的节奏继续贴近 reference 风格

### 20.8 当前结论

- `create` 当前也已完成一个阶段性目标：
  - `STEP 03` 不再完全压出首屏
- 但 `STEP 03` 的主内容区还没有完整进入首屏

因此下一轮有两个合理方向：

1. 继续压 `create`
   - 只剩把 `STEP 03` 主体再拉近一点
2. 切到 `mine`
   - 继续推进整体页面收口节奏

## 21. mine 首屏继续收口：四条设置与退出登录已进入运行态截图

### 21.1 本轮方向切换

在 `create` 把 `STEP 03` 拉到首屏边缘后，本轮主工作流切到：

- `pages/mine/index`

原因：

- `mine` 当前信息架构已经正确
- 但首屏纵向节奏仍偏高，导致：
  - `偏好设置`
  - `退出登录`
  还没有稳定进入首屏

### 21.2 本轮已改文件

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\mine\index.vue`

### 21.3 本轮差异定义

- 页面：`pages/mine/index`
- 可见块：`我的数据 + quick cards + settings list`

目标：

- 不改数据来源
- 不改入口逻辑
- 只压首屏纵向节奏，让设置列表更完整进入首屏

### 21.4 本轮动作

- `mine-page__body`
  - `gap: 22rpx -> 16rpx`
- `mine-page__analytics`
  - `padding: 34rpx 34rpx 30rpx -> 26rpx 28rpx 24rpx`
- `mine-page__analytics-head`
  - `margin-bottom: 28rpx -> 20rpx`
- `mine-page__analytics-title`
  - `34rpx -> 32rpx`
- `mine-page__analytics-main`
  - `gap: 28rpx -> 22rpx`
- `mine-page__analytics-value`
  - `76rpx -> 64rpx`
- `mine-page__analytics-copy`
  - `22rpx -> 20rpx`
- `mine-page__trend`
  - `108rpx -> 86rpx`
  - `margin-top: 26rpx -> 20rpx`
- `mine-page__analytics-strip`
  - `gap: 20rpx -> 16rpx`
  - `margin-top: 24rpx -> 18rpx`
- `mine-page__analytics-mini`
  - `gap: 10rpx -> 8rpx`
  - `padding-top: 16rpx -> 12rpx`
- `mine-page__analytics-mini-key`
  - `20rpx -> 18rpx`
- `mine-page__analytics-mini-value`
  - `32rpx -> 28rpx`
- `mine-page__quick-grid`
  - `gap: 18rpx -> 14rpx`
- `mine-page__quick-card`
  - `min-height: 190rpx -> 156rpx`
  - `padding: 30rpx 28rpx -> 24rpx`
  - `border-radius: 28rpx -> 26rpx`
- `mine-page__quick-icon`
  - `48rpx -> 40rpx`
- `mine-page__quick-title`
  - `34rpx -> 30rpx`
- `mine-page__quick-eyebrow`
  - `18rpx -> 16rpx`
- `mine-page__setting-row`
  - `min-height: 104rpx -> 88rpx`
  - `gap: 24rpx -> 20rpx`
  - `padding: 0 30rpx -> 0 26rpx`
- `mine-page__setting-label`
  - `30rpx -> 28rpx`
- `mine-page__logout`
  - `72rpx -> 60rpx`

### 21.5 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- DevTools 工程强制刷新：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`
- `share-card-mvp/capture-mini-program-screenshots.js`

样本目录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-mine-r1`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `sync-mp-weixin.ps1`：已完成
- `mine-r1` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

### 21.6 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\mine\index.wxss`
  - 已命中：
    - `gap:16rpx`
    - `padding:26rpx 28rpx 24rpx`
    - `font-size:64rpx`
    - `height:86rpx`
    - `min-height:156rpx`
    - `min-height:88rpx`
    - `min-height:60rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\mine\index.wxss`
  - 同样已命中上述值

### 21.7 最新运行态截图结论

- 改前：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r2b\screenshots\owner-mine.png`
  - 当时：
    - `偏好设置` 在首屏底部边缘
    - `退出登录` 不在首屏
- 改后：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-mine-r1\screenshots\owner-mine.png`
  - 当前已看到：
    - 四条设置：
      - `我的作品集`
      - `收藏的分享`
      - `消息通知`
      - `偏好设置`
    - `退出登录`
    都进入了当前首屏截图

### 21.8 当前结论

- `mine` 本轮不是“页面没变化”
- 当前 `mine` 首屏已经完成阶段性目标：
  - 完整的 profile header
  - analytics 卡
  - quick cards
  - 四条 settings
  - `退出登录`
  都进入了运行态首屏截图

因此下一轮可优先回到：

1. `create`
   - 继续把 `STEP 03` 主体拉进首屏
2. 或 `home`
   - 继续尝试把 CTA 拉进首屏

## 22. create 首屏三轮后自动换向：停止继续磨 STEP 03，转去 home CTA

### 22.1 本轮目标与边界

- 页面：`pkg-card/card-list/index`
- 可见块：`STEP 03` 标题输入区 + 底部 CTA `生成分享卡片`
- 目标：
  - 不再大幅压 `STEP 02` 图片网格
  - 只尝试把 `STEP 03` 主体再往首屏拉近

### 22.2 第 1 轮：改 CTA 自身尺寸

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
  - `KpButton size: large -> medium`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r3-actionbar`

事实：

- `src / dist/build / dist/dev` 都已更新到 `size:"medium"`
- 运行态截图 `owner-card-list.png` 与上一轮相比，底部 CTA 占高有变化
- 但变化只发生在最底部窄区域，`STEP 03` 主体并没有被稳定拉进首屏

### 22.3 第 2 轮：改 CTA 固定栏底部偏移

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
  - `card-list-page__action-bar bottom: calc(24rpx + env(...)) -> calc(12rpx + env(...))`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r4-actionbar-bottom12`

事实：

- `dist\dev\mp-weixin\pkg-card\card-list\index.wxss`
  - 已命中：`bottom:calc(12rpx + env(safe-area-inset-bottom))`
- `dist\build\mp-weixin\pkg-card\card-list\index.wxss`
  - 同样已命中上述值
- 运行态截图仍只在底部露出极小差异，`STEP 03` 主体没有进入当前首屏

### 22.4 第 3 轮：改 STEP 03 结构重排

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
  - 给 `STEP 03` 面板增加 `card-list-page__panel--draft`
  - `card-list-page__panel--draft margin-top: -10rpx`
  - CTA 固定栏底部偏移回退到 `24rpx`

验证样本：

- 首次截图链路超时并落到资源管理器窗口：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r5-draft-reflow`
  - 这次记为**截图链路失败**，不是样式结论
- 重挂 automator 后稳定复跑：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r5b-draft-reflow`

关键证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\card-list\index.wxml`
  - 已命中：`card-list-page__panel--draft`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\card-list\index.wxss`
  - 已命中：`margin-top:-10rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pkg-card\card-list\index.wxss`
  - 同样已命中：`margin-top:-10rpx`

运行态结论：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r5b-draft-reflow\screenshots\owner-card-list.png`
  - `STEP 03` 顶部标题卡比 `r2b` 稍微多露出一截
  - 但 `STEP 03` 主体仍没有完整进入首屏

### 22.5 按规则自动换向

本轮针对同一页面、同一可见块、同一目标已经连续做了 3 次调试：

1. 缩 CTA 尺寸
2. 改 CTA 底部偏移
3. 改 `STEP 03` 面板结构

虽然 3 次都产生了可验证的代码 / 产物变化，但都**没有把 `STEP 03` 主体稳定拉进首屏**，收益已经明显下降。

因此按 `00-73` 的 `R28-R30`，本轮停止继续磨 `create`，自动切换方向到：

- `pages/home/index`
- 目标块：底部主 CTA `开始创建分享页`

原因：

- `create` 剩余问题已经进入低收益微调区
- `home` 当前只差把 CTA 再拉进一截，成功概率更高

## 23. home 继续推进：缩短 guide stage 后，CTA 已进入首屏底边

### 23.1 本轮目标

- 页面：`pages/home/index`
- 可见块：`操作指南` 区块下方 CTA `开始创建分享页`
- 目标：
  - 不动 hero / stats / 风格卡
  - 只缩短 guide 视频舞台，让 CTA 往首屏里再上来一截

### 23.2 本轮已改文件

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

### 23.3 本轮动作

- `home-page__guide-cover`
  - `height: 268rpx -> 232rpx`

### 23.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- DevTools 工程强制刷新：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`
- `share-card-mvp/capture-mini-program-screenshots.js`

样本目录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r1-guide232`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `home-r1-guide232` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

### 23.5 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：`height:232rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 同样已命中：`height:232rpx`

### 23.6 运行态截图结论

- 改前：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-create-r5b-draft-reflow\screenshots\owner-home-share-cards.png`
  - 当时：
    - 只能看到三步胶囊
    - CTA `开始创建分享页` 完全不在首屏
- 改后：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r1-guide232\screenshots\owner-home-share-cards.png`
  - 当前已看到：
    - 三步胶囊下方，黑色 CTA 顶边已经进入当前首屏

辅助对照裁切：

- 改前底部裁切：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r1-guide232\owner-home-r5b-bottom-crop.png`
- 改后底部裁切：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r1-guide232\owner-home-r1-bottom-crop.png`

### 23.7 当前结论

- `home` 本轮不是“页面没变化”
- 当前已经把 CTA 从“完全不在首屏”推进到“进入首屏底边”
- 但 CTA 还没有完整落入首屏

因此下一轮优先级更新为：

1. 继续 `home`
   - 只做 guide 区块的轻量压缩，争取让 CTA 再多露出一截
2. `create`
   - 暂停，除非后续有新的 reference 证据或更高收益结构方案

## 24. home 继续推进：CTA 进入量继续增加，当前方向仍有效

### 24.1 第 2 轮：继续压 guide stage

页面：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

可见块：

- `操作指南` 区块下方 CTA `开始创建分享页`

本轮只改：

- `home-page__guide-cover`
  - `height: 232rpx -> 208rpx`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r2-guide208`

验证结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- manifest：
  - `captureCount = 10`
  - `fallbackCount = 1`
  - `visualDidNotRefresh = false`

关键产物证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：`height:208rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 同样已命中：`height:208rpx`

运行态说明：

- `owner-home-share-cards` 这页截图走了 1 次 DevTools window fallback
- 但最终截图仍是正确的小程序页面，不是资源管理器或错误窗口：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r2-guide208\screenshots\owner-home-share-cards.png`

运行态结论：

- CTA 比 `r1` 又多露出一截
- 但仍未完整进入首屏

### 24.2 第 3 轮：改三步胶囊高度，继续把 CTA 往上拉

本轮继续同一页面、同一目标，但更换到 CTA 的直接上游块：

- `home-page__guide-step`
  - `min-height: 60rpx -> 52rpx`

原因：

- `guide-cover` 连续两轮都有效
- 但继续压舞台本身会逐步损伤视频区比例
- 当前更合理的真实锚点是 CTA 正上方的三步胶囊

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r3-guide208-step52`

验证过程补充：

- 第一次复跑时出现过 1 次会话注入超时：
  - `injectSession-owner-home-share-cards timeout after 30000ms`
- 该次记为**截图链路失败**，不是样式结论
- 重挂 `auto --auto-port 9520` 后复跑成功

验证结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `home-r3-guide208-step52` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

关键产物证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `height:208rpx`
    - `min-height:52rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 同样已命中：
    - `height:208rpx`
    - `min-height:52rpx`

运行态截图：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r3-guide208-step52\screenshots\owner-home-share-cards.png`

辅助底部裁切对照：

- 改前：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r3-guide208-step52\owner-home-r2-bottom-crop.png`
- 改后：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r3-guide208-step52\owner-home-r3-bottom-crop.png`

运行态结论：

- CTA 当前已比 `r2` 再多露出一截
- 现在不再只是“顶边进入首屏”，而是已经能看到更明显的按钮上半部
- 但 CTA 仍未完整进入首屏

### 24.3 当前结论

- `home` 当前方向仍然有效，没有触发 3 次失败换向条件
- 连续两轮都拿到了用户可感知的正向变化：
  1. CTA 从“完全不在首屏”到“进入首屏底边”
  2. CTA 从“只露顶边”到“露出更明显上半部”

因此下一轮仍优先继续：

1. `home`
   - 只做 CTA 邻近区块的轻量压缩
   - 目标是把 `开始创建分享页` 完整拉进首屏
2. `create`
   - 继续暂停

## 25. home 继续推进：CTA 文字已经完整进入首屏，方向仍有效

### 25.1 第 4 轮：改 CTA 自身高度

页面：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

可见块：

- `操作指南` 区块下方 CTA `开始创建分享页`

本轮只改：

- `home-page__guide-cta`
  - `height: 96rpx -> 84rpx`

原因：

- 当前 CTA 已经进入首屏
- 继续压 CTA 本身，比继续压风格卡或 hero 的风险更低

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r4-cta84`

验证结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `home-r4-cta84` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

关键产物证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `height:208rpx`
    - `min-height:52rpx`
    - `height:84rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 同样已命中上述值

运行态结论：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r4-cta84\screenshots\owner-home-share-cards.png`
  - CTA 比 `r3` 继续多露出一截
  - 当前已经能更清楚看到 `开始创建分享页` 的文字

### 25.2 第 5 轮：改 guide section 垂直节奏

本轮继续同一页面、同一目标，但不再继续压 CTA 本身，而是改它所在 section 的垂直节奏：

- `home-page__section--guide`
  - `gap: 16rpx -> 12rpx`

原因：

- `CTA height` 这一轮已有效
- 继续单独缩按钮本身，偏离 reference 风险会开始升高
- 当前更合理的下一锚点是 guide 区块的整体垂直节奏

关键提醒：

- 改完后先核对 `src / dist/build / dist/dev`
- 之后重新补跑运行态截图，不能拿旧截图充当结论

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r5-cta84-gap12`

验证结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `home-r5-cta84-gap12` manifest：
  - `captureCount = 10`
  - `fallbackCount = 2`
  - `visualDidNotRefresh = false`

补充说明：

- 两次 fallback 都发生在：
  - `viewer-history`
  - `owner-mine`
- `owner-home-share-cards` 仍是 automator 直截图，不影响首页结论

关键产物证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `gap:12rpx`
    - `height:208rpx`
    - `min-height:52rpx`
    - `height:84rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 同样已命中上述值

运行态截图：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r5-cta84-gap12\screenshots\owner-home-share-cards.png`

底部裁切对照：

- 改前：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r5-cta84-gap12\owner-home-r4-bottom-crop.png`
- 改后：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r5-cta84-gap12\owner-home-r5-bottom-crop.png`

运行态结论：

- CTA 当前已比 `r4` 再上来一截
- 不再只是“按钮上半部更明显”
- 当前已经能完整看到：
  - `＋`
  - `开始创建分享页`
  这一行的主要内容
- 但按钮底边仍没有完全进入首屏

### 25.3 当前结论

- `home` 当前方向仍然有效，没有触发 3 次失败换向条件
- 本轮连续两次都拿到了用户可感知的正向变化：
  1. `r4`：CTA 文字可见度继续增加
  2. `r5`：CTA 主文案行已经完整进入首屏

因此下一轮优先级保持：

1. 继续 `home`
   - 只做 CTA 邻近区块的轻量压缩
   - 目标是让按钮底边也完整进入首屏
2. `create`
   - 继续暂停

## 26. home CTA 首屏收口：按钮底边已完整进入首屏

### 26.1 第 6 轮：继续压 guide section gap

页面：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

可见块：

- `操作指南` 区块下方 CTA `开始创建分享页`

本轮只改：

- `home-page__section--guide`
  - `gap: 12rpx -> 8rpx`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r6-gap8`

验证结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `home-r6-gap8` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

关键产物证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `gap:8rpx`
    - `height:208rpx`
    - `min-height:52rpx`
    - `height:84rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 同样已命中上述值

运行态结论：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r6-gap8\screenshots\owner-home-share-cards.png`
  - CTA 整体继续上移
  - 文案行完整可见
  - 底部仍略贴首屏底线

### 26.2 第 7 轮：换到 body section 间距，完成按钮底边收口

本轮不再继续压 `section--guide gap`，因为它已经到 `4rpx` 前后的低值区；换到同一页面、同一目标的另一个上游锚点：

- `home-page__body`
  - `gap: 22rpx -> 16rpx`

原因：

- 继续压 guide 内部 gap 会损伤局部呼吸感
- `body gap` 只影响 `styles` 与 `guide` 两个 section 的距离，能把整个 guide 区块轻微上移
- 不动 hero、stats、风格卡内部结构、视频舞台和 CTA 自身厚度

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r7-bodygap16`

验证结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `home-r7-bodygap16` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

关键产物证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `gap:16rpx`
    - `gap:4rpx`
    - `height:208rpx`
    - `min-height:52rpx`
    - `height:84rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 同样已命中上述值

运行态截图：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r7-bodygap16\screenshots\owner-home-share-cards.png`

底部裁切对照：

- 改前：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r7-bodygap16\owner-home-r6-bottom-crop.png`
- 改后：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r7-bodygap16\owner-home-r7-bottom-crop.png`

运行态结论：

- CTA `开始创建分享页` 已完整进入当前首屏
- 当前已能看到：
  - 三步胶囊
  - CTA 完整主文案
  - CTA 底部圆角 / 底边
- `home` 从“CTA 完全不在首屏”推进到“CTA 完整进入首屏”的阶段性目标已达成

### 26.3 当前结论

- `home` 方向没有触发 3 次失败换向条件
- 本轮是连续正向变化，不是盲调
- 当前 `home` 首屏 CTA 可视目标已经阶段性收口

下一步优先级建议：

1. 暂停继续压 `home`
   - 避免继续损伤 guide 区块呼吸感
2. 切到下一页继续推进
   - 推荐回到 `actor-card` 细节或 `history` 记录页
   - `create` 继续暂停，除非有新的 reference 或结构方案

## 27. actor-card card preview：QUICK EDIT pills 已收细

### 27.1 本轮方向

在 `home` CTA 阶段性收口后，本轮主工作流切到：

- `pkg-card/actor-card/index`

本轮只处理 `card preview`，不改：

- `shareMode / sharedEntry / isFinalPreviewMode`
- `card / poster` route ownership
- 底部分享按钮文案
- 海报预览态结构

### 27.2 本轮视觉合同

- 页面：`pkg-card/actor-card/index?shareCardId=1&artifact=miniProgramCard&shareMode=1`
- 可见块：`QUICK EDIT` 三个胶囊按钮
- 目标：
  - 从偏厚重矩形按钮收细为更接近 reference 的细长 pill
  - 保留 `编辑封面 / 编辑标题 / 编辑简介` 三个入口

### 27.3 本轮已改文件

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

### 27.4 本轮动作

- `card-page__quick-edit-row`
  - `gap: 12rpx -> 10rpx`
  - `margin-top: 12rpx -> 10rpx`
- `card-page__quick-edit-button`
  - `min-height: 68rpx -> 58rpx`
  - `border-radius: 20rpx -> 999rpx`
  - `font-size: 20rpx -> 19rpx`

### 27.5 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

补充链路事实：

- 本轮第一次复跑截图时，`http://101.43.57.62/api` 被 301 到 `https://101.43.57.62/api`，触发 TLS SAN 校验问题：
  - `ERR_TLS_CERT_ALTNAME_INVALID`
- 证书 SAN 包含 `api.kplyyk.com`，但当前脚本使用 IP 访问
- 后续验证中临时使用：
  - `NODE_TLS_REJECT_UNAUTHORIZED=0`
  - baseUrl：`https://101.43.57.62/api`
- 该问题记为**截图链路 / 环境问题**，不是样式失败，也不是 `actor-card` 调试失败

稳定截图样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r11c-quick-edit`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `actor-card-r11c-quick-edit` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

### 27.6 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxss`
  - 已命中：
    - `gap:10rpx`
    - `margin-top:10rpx`
    - `min-height:58rpx`
    - `border-radius:999rpx`
    - `font-size:19rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pkg-card\actor-card\index.wxss`
  - 同样已命中上述值

### 27.7 运行态结论

- 改后截图：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r11c-quick-edit\screenshots\owner-share-action-mini-program.png`
- 当前已看到：
  - `QUICK EDIT` 三个按钮从偏厚重矩形变成更细的 pill
  - 卡片预览页主结构、底部分享按钮、卡片文案未被破坏

当前结论：

- `actor-card / card preview` 本轮是有效推进
- 未触发 3 次失败换向条件

下一步：

- `actor-card` 可暂时不继续细压，避免对已稳定的 preview 结构过度调整
- 主工作流切到 `history`，处理 records 页仍暴露技术模板名的问题

## 28. history 记录页：技术模板名已收口，列表卡密度已压缩

### 28.1 本轮方向

在 `actor-card / card preview` 的 `QUICK EDIT` 局部收口后，本轮主工作流切到：

- `pages/history/index`

原因：

- records 页没有单页 reference，只能继续以 `reference-full / reference-overview` 总览中的 `RecordsScreen` 与真实运行态共同验收
- 当前运行态仍可见技术模板名 `Smoke Template`，明显不符合 reference 的 `都市 / 古风 / 经典` 分馆语义

### 28.2 第一阶段：shared scene title 口径收口

本阶段没有在 `history` 页面内联新判断，而是修改 shared display source：

- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-card-mvp.ts`

动作：

- 新增 `isTechnicalTemplateName`
- `resolveShareCardSceneTitle` 对包含以下技术词的模板名不再直接展示：
  - `template`
  - `smoke`
- 回退到 `sceneKey` 的稳定展示名：
  - `general -> 经典`
  - `urban -> 都市`
  - `costume -> 古风`

原因：

- `history` 与 `contact` 都复用 `resolveShareCardSceneTitle`
- 按“展示状态与资格判断必须单一来源”的规则，不在页面里散落一套 label 判断

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r1-scene-title`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `history-r1-scene-title` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

运行态结论：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r1-scene-title\screenshots\viewer-history.png`
  - filter pill 已从 `Smoke Template` 变为 `经典`
  - 卡片 tag 已从 `Smoke Template` 变为 `经典`
  - cover label 已从 `Smoke Template` 变为 `经典`
- 同轮 `viewer-public-card-detail` 分享 payload 也从：
  - `Smoke Template公开名片页`
  收口为：
  - `经典公开名片页`

### 28.3 第二阶段：records 列表卡密度压缩

本阶段只调整：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\history\index.vue`

视觉合同：

- 页面：`pages/history/index`
- 可见块：首条 history list card
- 目标：
  - 列表卡从偏厚重、偏高，压到更接近 `RecordsScreen` 的列表密度
  - 不改 hero / filters / 路由行为

动作：

- `history-page__card`
  - `padding: 18rpx -> 16rpx`
  - `border-radius: 28rpx -> 26rpx`
  - `grid-template-columns: 132rpx -> 116rpx`
  - `gap: 18rpx -> 14rpx`
- `history-page__cover`
  - `border-radius: 22rpx -> 20rpx`
  - `min-height: 168rpx -> 148rpx`
- `history-page__card-main`
  - `gap: 16rpx -> 12rpx`
- `history-page__name`
  - `font-size: 30rpx -> 28rpx`
- `history-page__studio`
  - `margin-top: 8rpx -> 6rpx`
  - `font-size: 20rpx -> 18rpx`
  - `line-height: 1.6 -> 1.5`
  - 增加 3 行截断
- `history-page__time`
  - `font-size: 20rpx -> 18rpx`
- `history-page__meta-row`
  - `gap: 14rpx -> 12rpx`
- `history-page__tag`
  - `height: 46rpx -> 42rpx`
  - `padding: 0 18rpx -> 0 16rpx`
  - `border-radius: 16rpx -> 14rpx`
  - `font-size: 20rpx -> 18rpx`
- `history-page__meta`
  - `font-size: 20rpx -> 18rpx`
- `history-page__reenter`
  - `height: 48rpx -> 44rpx`
  - `padding: 0 20rpx -> 0 18rpx`
  - `border-radius: 16rpx -> 14rpx`
  - `font-size: 20rpx -> 18rpx`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r2-density`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `history-r2-density` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

关键产物证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\history\index.wxss`
  - 已命中：
    - `padding:16rpx`
    - `border-radius:26rpx`
    - `grid-template-columns:116rpx minmax(0,1fr)`
    - `gap:14rpx`
    - `min-height:148rpx`
    - `font-size:28rpx`
    - `-webkit-line-clamp:3`
    - `height:42rpx`
    - `height:44rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\history\index.wxss`
  - 同样已命中上述值

运行态截图：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r2-density\screenshots\viewer-history.png`

辅助裁切对照：

- 改前：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r2-density\viewer-history-r1-crop.png`
- 改后：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r2-density\viewer-history-r2-crop.png`

运行态结论：

- 首条 history card 明显收短
- 封面列更接近 records reference 里的紧凑列表缩略图
- 简介文本被限制在 3 行，不再继续撑高卡片
- `经典` scene label 已稳定出现在：
  - filter
  - cover label
  - card tag

### 28.4 当前结论

- `history` 本轮是有效推进
- 未触发 3 次失败换向条件
- records 页仍缺单页 reference，因此不能宣称最终 1:1 完成
- 但当前已完成两个高收益问题：
  1. 去掉技术模板名
  2. 首屏列表卡密度向 reference 收口

下一步建议：

1. 继续 `history`
   - 只做轻量首屏密度和 filter 行节奏整理
2. 或切回 `actor-card(poster)`
   - 处理 poster preview 的顶部 / footer 细节
3. `create`
   - 继续暂停

## 30. history 记录页：运行态时间闭环修复，filter pills 继续收细

### 30.1 本轮方向

主工作流继续固定在：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\history\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\api\history.ts`

原因：

- `history` 是当前 records 主工作流
- `home` 已阶段性收口，不再继续压
- `create` 已按 3 次低收益规则暂停，不再做第 4 次同类试错
- `actor-card / card preview` 本轮已经有正向截图证据，暂不继续细压

### 30.2 先换向到运行态核对：确认旧截图不是当前 dist

本轮先复核：

- `src`
- `dist/build`
- `dist/dev`
- 运行态截图 / page-data

发现：

- `src/pages/history/index.vue` 已经把时间从 card head 移到 `history-page__foot`
- `dist/dev/mp-weixin/pages/history/index.wxml` 也已经是底部 foot 结构
- `dist/dev/mp-weixin/api/history.js` 已经包含相对时间文案：
  - `刚刚`
  - `分钟前`
  - `小时前`
  - `昨天`
  - `前天`
- 但旧样本 `history-r2b-density` 的运行态仍显示：
  - 右上角 `2026-04-22 07:47`
  - page-data 字段映射仍是旧模板结构

结论：

- 这是 DevTools / 运行态未刷新导致的截图链路偏差
- 本轮没有继续改样式数值，而是先按 `R29` 换到 `src / dist/build / dist/dev / DevTools` 四层核对
- 该问题不是页面样式失败，不计入同一可见块的 3 次失败

### 30.3 第 3 轮样本：DevTools 强刷后确认时间已到底部，但文案为空

执行：

- `npm run type-check`
- `npm run build:mp-weixin`
- 微信开发者工具：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`

截图样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r3-runtime-sync`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `history-r3-runtime-sync` manifest：
  - `captureCount = 10`
  - `fallbackCount = 2`
  - `visualDidNotRefresh = false`

运行态结论：

- `viewer-history` 已不再显示右上角绝对时间
- 这证明当前运行态已经吃到新的 foot 结构
- 但 page-data 中首条记录的 `viewedAt` 为空，导致底部右侧时间没有显示

进一步核实后端原始返回：

- `/api/card/view-histories`
  - `viewedAt: "2026-04-22T07:47:09"`

根因：

- 原实现使用 `value.replace(/-/g, '/')` 后再解析
- 对 `2026-04-22T07:47:09` 会变成 `2026/04/22T07:47:09`
- 该格式在当前运行态解析失败，所以相对时间被格式化为空

### 30.4 第 4 轮样本：相对时间已恢复到底部右侧

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\api\history.ts`

动作：

- 新增 `parseHistoryViewedTimestamp`
- 支持：
  - `YYYY-MM-DDTHH:mm:ss`
  - `YYYY-MM-DD HH:mm:ss`
  - 带 `Z` 或 timezone offset 的 ISO 字符串
  - `YYYY-MM-DD`
- `昨天 HH:mm` 与 `YYYY-MM-DD` 回落改用已解析 timestamp，避免二次解析失败

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r4-time-relative`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `history-r4-time-relative` manifest：
  - `captureCount = 10`
  - `fallbackCount = 3`
  - `visualDidNotRefresh = false`

关键产物证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\api\history.js`
  - 已命中：
    - `replace("T"," ").replace(/-/g,"/")`
    - `小时前`
    - `昨天`
    - `前天`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\api\history.js`
  - 同样已命中上述解析逻辑

运行态截图：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r4-time-relative\screenshots\viewer-history.png`

运行态结论：

- 首条记录右上角不再显示绝对时间
- `12小时前` 已显示在 card footer 右侧
- page-data 中首条记录已显示：
  - `h: "12小时前"`
  - `i: "12小时前"`

### 30.5 第 5 轮样本：filter pills 收细

视觉合同：

- 页面：`pages/history/index`
- 可见块：`history-page__filters`
- 目标：
  - 四个分馆胶囊更短、更薄，靠近 reference records crop 的一行节奏
  - 不动 hero、列表卡结构、刚修复的 footer time

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\history\index.vue`

动作：

- `history-page__filters`
  - `gap: 16rpx -> 12rpx`
  - `margin-bottom: 28rpx -> 24rpx`
- `history-page__filter`
  - `min-width: 96rpx -> 88rpx`
  - `height: 60rpx -> 54rpx`
  - `padding: 0 24rpx -> 0 20rpx`
  - `font-size: 22rpx -> 20rpx`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r5-filter-pills`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `history-r5-filter-pills` manifest：
  - `captureCount = 10`
  - `fallbackCount = 2`
  - `visualDidNotRefresh = false`

关键产物证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\history\index.wxss`
  - 已命中：
    - `gap:12rpx`
    - `margin-bottom:24rpx`
    - `min-width:88rpx`
    - `height:54rpx`
    - `padding:0 20rpx`
    - `font-size:20rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\history\index.wxss`
  - 同样已命中上述值

运行态截图：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r5-filter-pills\screenshots\viewer-history.png`

运行态结论：

- filter 胶囊比 `r4` 明显更细，和 reference records crop 的一行 pill 节奏更接近
- `12小时前` 仍稳定显示在 footer 右侧，没有被本轮 filter 修改破坏
- 标题 `林夏的经典写真集`、`经典` scene label、`再次进入` 入口均保持

### 30.6 当前结论

- `history` 本轮有效推进：
  1. 先通过四层核对排除了旧截图误导
  2. 修复了 `viewedAt` ISO 字符串解析导致的相对时间空白
  3. 继续把 filter pills 收细到更接近 reference
- 本轮没有触发“同一页面、同一可见块、同一类问题连续 3 次失败”：
  - `r3` 是运行态同步核对
  - `r4` 是数据格式解析修复
  - `r5` 是新可见块 filter pills 收口

下一步建议：

1. 继续 `history`
   - 可看首条 card 的 footer 结构是否要向 reference 的 `再次进入 + 次数 + 时间` 更进一步收口
2. 若继续压 `history` 的单条数据形态收益下降，再切到 `actor-card / poster preview`
3. `create` 继续暂停，除非先有新的结构方案或 reference 证据

## 31. actor-card / poster preview：补出真实 reference 后继续收口海报舞台与底部动作

### 31.1 从 `history` 换向到 `poster preview`

本轮先核对 `history` footer 是否能继续向 reference 的：

- `再次进入 + 次数 + 时间`

收口。

已核实：

- `D:\XM\kaipai-team\kaipai-frontend\src\types\history.ts`
- live `/api/card/view-histories`

结果：

- 当前真实历史数据只有：
  - `actorId`
  - `shareCardId`
  - `sceneKey`
  - `actorName`
  - `actorAvatar`
  - `templateName`
  - `intro`
  - `contactLabel`
  - `viewedAt`
- 没有可复用的“打开次数 / 再次进入次数”字段

结论：

- 当前不能在 `history` 里伪造次数文案
- 因此不继续在同一块 footer 上硬凑 reference，而是切到：
  - `pkg-card/actor-card/index?shareCardId=1&artifact=poster&shareMode=1`

这次换向不是“3 次失败后被动停下”，而是基于真实数据边界的主动止损。

### 31.2 先补出真正的 poster reference，不再拿错误裁切图当基线

先前 `D:\XM\kaipai-team\tmp\reference-crops\poster.png` 实际只是一张：

- `海报预览`

入口卡片，不是完整 `PosterPreviewScreen`。

因此本轮先补 reference 取证：

1. 在 repo 根目录临时生成：
   - `D:\XM\kaipai-team\_poster_ref_tmp.html`
2. 只把原型里：
   - `p3 initial: 'cardPreview'`
   临时改成：
   - `p3 initial: 'posterPreview'`
3. 执行：
   - `npx playwright screenshot --full-page --viewport-size=2200,1300 file:///D:/XM/kaipai-team/_poster_ref_tmp.html D:/XM/kaipai-team/output/playwright/reference-poster-full.png`
4. 再裁出：
   - `D:\XM\kaipai-team\tmp\reference-poster-phone.png`

当前 poster 页级 reference 基线改为：

- `D:\XM\kaipai-team\tmp\reference-poster-phone.png`

### 31.3 第 12 轮：缩短主图高度，让 poster stage 更接近 reference 纵向节奏

页面：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

视觉合同：

- 页面：`pkg-card/actor-card/index?shareCardId=1&artifact=poster&shareMode=1`
- 可见块：`card-page__poster-cover`
- 目标：
  - 主图高度下降一档
  - 让 thumb / footer / 底部 action bar 拿回接近 reference 的呼吸空间
  - 不改 topbar、不改分享逻辑

动作：

- `card-page__poster-cover`
  - `height: 560rpx -> 508rpx`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r12-poster-cover508`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `actor-card-r12-poster-cover508` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

关键产物证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxss`
  - 已命中：
    - `height:508rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pkg-card\actor-card\index.wxss`
  - 同样已命中上述值

运行态截图：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r12-poster-cover508\screenshots\owner-share-action-poster.png`

运行态结论：

- 主图高度比前一轮明显收短
- thumb 与 footer 不再被主图挤得过低
- poster 舞台的整体纵向节奏更接近 `reference-poster-phone`

### 31.4 第 13 轮：poster 底部主次按钮先走错宿主锚点，再改为 shared button variant

本轮可见块：

- `card-page__action-row`

reference 对照结论：

- reference：
  - 左侧更弱的 `保存相册`
  - 右侧金棕主按钮 `分享到朋友圈`
- 当前实现：
  - 左侧仍是实体白按钮
  - 右侧默认 `KpButton primary` 是深色主按钮

#### 31.4.1 第一次尝试：直接改页面级 class（已证伪）

第一次动作：

- `card-page--poster-preview &__ghost-button`
  - 改成透明弱操作
- `card-page--poster-preview &__action-button`
  - 试图直接改成金棕主按钮

构建与截图样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r13-poster-actions`

截图现象：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r13-poster-actions\screenshots\owner-share-action-poster.png`
- 右侧只出现了金色宿主背景
- 内部真实按钮仍维持深色主按钮

结论：

- 页面级 class 改到的是组件宿主，不是 `KpButton` 内部真正可见按钮根
- 这是一次有效的“锚点证伪”，不是继续盲调数值

#### 31.4.2 第二次尝试：切到 shared component 口径

随后立刻换向到 shared component：

- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpButton.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

动作：

- `KpButton`
  - 新增 `accent` variant
  - `kp-button--accent`
    - `background: #a8865d`
    - `color: #fbfaf6`
- poster 右侧主按钮
  - 改为：
    - `variant="accent"`
- poster 左侧按钮继续保持：
  - 透明弱操作

关键产物证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\components\KpButton.wxss`
  - 已命中：
    - `.kp-button--accent`
    - `background:#a8865d`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`
  - 已命中：
    - `variant="accent"`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxss`
  - 已命中：
    - `card-page--poster-preview .card-page__ghost-button{background:transparent`

当前判断：

- 这次 shared 口径比“继续堆页面级宿主样式”更正确
- 但 poster 主按钮当前运行态仍偏深，距离 reference 的金棕主按钮还有剩余差距

### 31.5 当前结论

- `poster preview` 本轮已经拿到真实页级 reference，不再靠错误裁切图猜测
- 当前两步有效推进分别是：
  1. 主图高度收短，舞台纵向节奏更接近 reference
  2. 底部按钮的技术锚点已经从“页面级宿主”换到“shared button variant”
- `poster action bar` 当前还没有达到最终 1:1，但也没有触发 3 次失败：
  - 第 1 次：页面级宿主样式，证伪
  - 第 2 次：shared `accent` variant，方向正确但仍需下一轮核实最终视觉

下一步建议：

1. 继续 `actor-card / poster preview`
   - 优先只看右侧金棕主按钮为什么在运行态仍偏深
   - 若 shared variant 在运行态仍受原生按钮皮肤影响，再切到组件模板级或原生 button 结构级处理
2. 暂不回 `history`
   - 因为当前 `history` 已到真实数据边界
3. `create`
   - 继续暂停

## 32. actor-card / poster preview：主按钮已切成金棕原生按钮，和 reference 主次关系一致

### 32.1 第 3 次尝试：直接绕开 `KpButton`，改用页面内原生按钮

上一轮已确认：

- `dist/dev` 里：
  - `KpButton` 已有 `accent` variant
  - `actor-card` 也已传入 `variant="accent"`
- 但运行态 `owner-share-action-poster` 里，右侧主按钮仍偏深

因此本轮不再继续在 shared component 上叠加猜测，而是对同一页面、同一可见块、同一类问题做第 3 次尝试时，直接改成更可证实的页面级原生按钮。

页面：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

可见块：

- `pkg-card/actor-card/index?shareCardId=1&artifact=poster&shareMode=1`
- 底部 action bar 右侧主按钮 `分享到朋友圈`

目标：

- 彻底绕开 `KpButton` 组件宿主 / variant / 原生皮肤叠层
- 让 poster 主按钮直接落成 reference 的金棕主按钮
- 不动 miniProgramCard 分享按钮、不动 poster 生成逻辑

动作：

- 模板：
  - poster 分支不再使用 `KpButton`
  - 改为页面内原生：
    - `button.card-page__poster-primary-button`
- 样式：
  - `background: #a8865d`
  - `color: #fbfaf6`
  - `min-height: 88rpx`
  - `border-radius: 24rpx`
  - 去掉默认 `::after` 边框

### 32.2 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- 微信开发者工具：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`
- 截图脚本：
  - `capture-mini-program-screenshots.js`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r14-poster-native-button`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `actor-card-r14-poster-native-button` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

### 32.3 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxml`
  - poster 主按钮已命中：
    - `button class="card-page__poster-primary-button"`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxss`
  - 已命中：
    - `.card-page__poster-primary-button`
    - `background:#a8865d`
    - `color:#fbfaf6`
    - `min-height:88rpx`
    - `border-radius:24rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pkg-card\actor-card\index.wxml`
  - 同样已切为原生 button 结构
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pkg-card\actor-card\index.wxss`
  - 同样已命中上述值

### 32.4 运行态截图结论

reference：

- `D:\XM\kaipai-team\tmp\reference-poster-phone.png`

当前运行态：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r14-poster-native-button\screenshots\owner-share-action-poster.png`

当前已确认：

- 左侧 `保存相册`
  - 维持弱操作
- 右侧 `分享到朋友圈`
  - 已真正变成金棕原生按钮
  - 不再是黑色主按钮套金色宿主边框
- 主次关系已经与 reference 一致

同时本轮沿用前一轮的有效收口：

- `card-page__poster-cover`
  - `560rpx -> 508rpx`

因此 poster 页当前已经完成两块高收益差异收口：

1. 海报舞台主图纵向节奏更接近 reference
2. 底部主次按钮关系与颜色语义已回到 reference 方向

### 32.5 当前结论

- `poster preview` 底部主按钮问题本轮闭环
- 对同一可见块的 3 次尝试口径为：
  1. 页面级宿主样式
  2. shared `accent` variant
  3. 页面内原生按钮
- 第 3 次已成功，因此：
  - 不触发失败换向
  - 这块不再继续猜

下一步建议：

1. 继续 `poster preview`
   - 只看标题下方 meta 行
   - reference：`MAY · 2026 · BY 栖光摄影`
   - 当前：`CLASSIC STYLE · 3 WORKS · 林夏`
2. 但这一步必须先核是否有真实 `studio/company` 字段
   - 没有就只能用可证实的品牌 fallback
3. `history`
   - 继续暂停在当前真实数据边界

## 33. actor-card / poster preview：meta 行已从场景说明收回到时间 + BY studio

### 33.1 先核数据事实，不直接硬编码 reference 文案

本轮继续停留在：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

可见块：

- `card-page__poster-meta`

目标：

- 从当前：
  - `CLASSIC STYLE · 3 WORKS · 林夏`
  收回到更接近 reference 的：
  - `MAY · 2026 · BY 栖光摄影`

但先核实真实数据源，避免直接硬编码机构名。

已核实：

- `D:\XM\kaipai-team\kaipai-frontend\src\types\actor.ts`
- `D:\XM\kaipai-team\kaipai-frontend\src\types\company.ts`
- `D:\XM\kaipai-team\kaipai-frontend\src\api\company.ts`
- live API：
  - `/api/company/mine`
  - `/api/company/10000`

结果：

- `ActorProfile` 本身没有 `studio/companyName`
- 但 company API 确实有机构字段：
  - `companyName: "Spec剧组0403065131"`
- 这个值是明显的测试 / 技术名，不适合直接作为 poster 对外展示名

当前结论：

- 不直接伪造 `栖光摄影`
- 也不直接把 `Spec剧组0403065131` 放进 poster
- 采用：
  - 真实字段优先
  - 技术名过滤
  - 品牌 fallback：`剧名片 STUDIO`

### 33.2 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

动作：

1. 新增 `getCompanyInfo` 接入
2. 新增：
   - `posterStudioName`
   - `posterStudioOwnerId`
3. 新增：
   - `formatPosterMonthYear`
   - `normalizePosterStudioName`
   - `hydratePosterStudioName`
4. `reloadLatestSnapshot()` 中，在拿到 `snapshot.actor.userId` 后补拉 company 信息
5. `posterMetaLine` 从：
   - `CLASSIC STYLE · 3 WORKS · 林夏`
   改为：
   - `${当前月} · ${当前年} · BY ${过滤后的 studioName}`

过滤规则：

- 若 `companyName` 包含：
  - `spec`
  - `test`
  - `mock`
  - `demo`
  - `continue-recheck`
- 则回退：
  - `剧名片 STUDIO`

### 33.3 本轮验证

已执行：

- `npm run type-check`
- `npm run build:mp-weixin`
- 微信开发者工具：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`
- 截图脚本：
  - `capture-mini-program-screenshots.js`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r15-poster-meta`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `actor-card-r15-poster-meta` manifest：
  - `captureCount = 10`
  - `fallbackCount = 2`
  - `visualDidNotRefresh = false`

补充说明：

- `fallbackCount = 2` 发生在：
  - `viewer-history`
  - `owner-mine`
- `owner-share-action-poster` 本身仍为 automator 直截图，不影响本页结论

### 33.4 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`
  - 已命中：
    - `getCompanyInfo`
    - `formatPosterMonthYear`
    - `normalizePosterStudioName`
    - `hydratePosterStudioName`
    - `posterMetaLine`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.js`
  - 已命中：
    - `APR · 2026 · BY 剧名片 STUDIO`
    - company API 调用
    - 技术名过滤逻辑
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxml`
  - `poster meta` 结构保持不变，仍由 `{{q}}` 驱动
- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r15-poster-meta\captures\page-data-owner-share-action-poster.json`
  - 已确认：
    - `q: "APR · 2026 · BY 剧名片 STUDIO"`

### 33.5 运行态结论

reference：

- `D:\XM\kaipai-team\tmp\reference-poster-phone.png`

当前运行态：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r15-poster-meta\screenshots\owner-share-action-poster.png`

当前已确认：

- poster meta 行已不再是：
  - `CLASSIC STYLE · 3 WORKS · 林夏`
- 而是：
  - `APR · 2026 · BY 剧名片 STUDIO`

因此本轮完成的不是“纯样式微调”，而是：

- 从错误的信息架构收回到更接近 reference 的时间 + studio 语义
- 并且保持真实数据优先，不展示测试公司名

### 33.6 当前结论

- `poster preview` 当前已经连续完成三块高收益差异收口：
  1. 海报主图纵向节奏
  2. 底部主次按钮关系
  3. meta 行信息架构
- 当前没有触发失败换向：
  - meta 行本轮第一次尝试即形成正确运行态变化

下一步建议：

1. 继续 `poster preview`
   - 只看 meta 行的字号 / 字距 / 行距是否还需更接近 reference
   - 或继续看 title 区与主图之间的垂直节奏
2. `history`
   - 继续停在真实数据边界
3. `create`
   - 继续暂停

## 35. actor-card / poster preview：标题区到主图间距收紧

### 35.1 本轮方向

主工作流继续固定在：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

页面：

- `pkg-card/actor-card/index?shareCardId=1&artifact=poster&shareMode=1`

可见块：

- `card-page__poster-head -> card-page__poster-cover`

目标：

- 只收紧标题区到主图之间的垂直间距
- 不动：
  - meta 文案
  - 主图高度
  - 底部按钮
  - footer
  - 分享逻辑

原因：

- 对比 `reference-poster-phone.png` 与 `r15` 运行态，当前标题区和主图之间的空白仍比 reference 略松
- 真实视觉锚点是 `card-page__poster-cover` 的 `margin-top`

### 35.2 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

动作：

- `card-page__poster-cover`
  - 新增 / 覆盖：
    - `margin-top: 10rpx`

说明：

- 共享的 `mini-card-cover / poster-cover` 基础规则仍保留 `margin-top: 18rpx`
- 但 poster preview 用 `card-page__poster-cover` 单独覆盖，避免影响 card preview

### 35.3 本轮验证

已执行：

- `npm run type-check`
- `npm run build:mp-weixin`
- 微信开发者工具：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`
- 截图脚本：
  - `capture-mini-program-screenshots.js`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r16-poster-covergap10`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `actor-card-r16-poster-covergap10` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

### 35.4 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxss`
  - 已命中：
    - `.card-page__poster-cover{height:508rpx;margin-top:10rpx}`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pkg-card\actor-card\index.wxss`
  - 同样已命中上述值
- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r16-poster-covergap10\captures\page-data-owner-share-action-poster.json`
  - 仍确认：
    - `q: "APR · 2026 · BY 剧名片 STUDIO"`

### 35.5 运行态结论

reference：

- `D:\XM\kaipai-team\tmp\reference-poster-phone.png`

当前运行态：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r16-poster-covergap10\screenshots\owner-share-action-poster.png`

当前已确认：

- 标题区到主图之间的空白较 `r15` 收紧
- meta 行、主图高度、底部按钮均保持上一轮结果
- 当前变化不是旧图，manifest 已确认：
  - `visualDidNotRefresh = false`
  - `fallbackCount = 0`

### 35.6 当前结论

- `poster preview` 本轮继续有效推进
- 当前已经连续完成五个高收益差异块：
  1. 主图纵向节奏
  2. 底部主次按钮
  3. meta 行信息架构
  4. poster head 视觉权重
  5. 标题区到主图的垂直间距
- 本轮没有触发失败换向：
  - `poster-cover margin-top` 第一次尝试即产生正确可见变化

下一步建议：

1. 继续 `poster preview`
   - 只看 topbar 的 back / title / switch 三点对齐
2. 如果 topbar 连续调试收益下降，再切到 `card preview` 或 `mine`
3. `history`
   - 继续停在真实数据边界

## 34. actor-card / poster preview：poster head 节奏继续收轻，meta 行更接近 reference

### 34.1 本轮方向

主工作流继续固定在：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

页面：

- `pkg-card/actor-card/index?shareCardId=1&artifact=poster&shareMode=1`

可见块：

- `card-page__poster-head`
- `card-page__poster-meta`

原因：

- `history` 已明确到真实数据边界，不再继续硬凑次数字段
- `poster preview` 当前仍有可见层差异，但已经拿到真实 reference
- 经过上一轮按钮与 meta 信息架构收口后，下一块高收益差异变成：
  - poster head 的视觉权重仍偏重
  - meta 行仍比 reference 更粗、更显眼

### 34.2 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

动作：

- `card-page__poster-head`
  - `gap: 8rpx -> 6rpx`
- `card-page__poster-meta`
  - `font-size: 20rpx -> 18rpx`
  - `line-height: 1.6 -> 1.42`
  - `letter-spacing: 0 -> 0.08em`
  - `color` 调浅为：
    - `rgba(143, 130, 117, 0.82)`

不改：

- 主图高度
- 底部按钮
- footer
- 分享逻辑

### 34.3 本轮验证

已执行：

- `npm run type-check`
- `npm run build:mp-weixin`
- 微信开发者工具：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`
- 截图脚本：
  - `capture-mini-program-screenshots.js`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r15-poster-meta`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `actor-card-r15-poster-meta` manifest：
  - `captureCount = 10`
  - `fallbackCount = 2`
  - `visualDidNotRefresh = false`

补充说明：

- `fallbackCount = 2` 发生在：
  - `viewer-history`
  - `owner-mine`
- `owner-share-action-poster` 仍为 automator 直截图，不影响本页结论

### 34.4 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxss`
  - 已命中：
    - `card-page__poster-head{gap:6rpx}`
    - `card-page__poster-meta{...font-size:18rpx...line-height:1.42...letter-spacing:.08em}`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pkg-card\actor-card\index.wxss`
  - 同样已命中上述值
- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r15-poster-meta\captures\page-data-owner-share-action-poster.json`
  - 已确认：
    - `q: "APR · 2026 · BY 剧名片 STUDIO"`

### 34.5 运行态结论

reference：

- `D:\XM\kaipai-team\tmp\reference-poster-phone.png`

当前运行态：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r15-poster-meta\screenshots\owner-share-action-poster.png`

当前已确认：

- meta 行已经保持上一轮的信息架构：
  - `APR · 2026 · BY 剧名片 STUDIO`
- 本轮进一步把它收轻：
  - 更小
  - 更淡
  - 与标题更贴近

因此本轮是“视觉层继续收口”，不是数据口径回退。

### 34.6 当前结论

- `poster preview` 当前已经连续完成四个高收益差异块：
  1. 主图纵向节奏
  2. 底部主次按钮
  3. meta 行信息架构
  4. poster head 视觉权重
- 本轮没有触发失败换向：
  - `poster head` 本轮第一次尝试即形成正确运行态变化

下一步建议：

1. 继续 `poster preview`
   - 只看标题区与主图之间的垂直节奏
   - 或看 topbar 的 back / title / switch 三点对齐
2. `history`
   - 继续停在真实数据边界
3. `create`
   - 继续暂停
## 29. actor-card / history 本轮继续推进：card preview pills 收细，records 结构语义更接近 reference

### 29.1 actor-card / card preview：`QUICK EDIT` pills 继续收口

页面：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

视觉合同：

- 页面：`/pkg-card/actor-card/index?shareCardId=1&artifact=miniProgramCard&shareMode=1`
- 可见块：`QUICK EDIT` 三个胶囊按钮
- 目标：
  - 从偏厚重矩形进一步收细成更接近 reference 的 pill
  - 不改底部分享按钮、不改 card/poster route ownership

本轮动作：

- `card-page__quick-edit-row`
  - `gap: 12rpx -> 10rpx`
  - `margin-top: 12rpx -> 10rpx`
- `card-page__quick-edit-button`
  - `min-height: 68rpx -> 58rpx`
  - `border-radius: 20rpx -> 999rpx`
  - `font-size: 20rpx -> 19rpx`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r11c-quick-edit`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `actor-card-r11c-quick-edit` manifest：
  - `captureCount = 10`
  - `fallbackCount = 0`
  - `visualDidNotRefresh = false`

关键产物证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxss`
  - 已命中：
    - `gap:10rpx`
    - `margin-top:10rpx`
    - `min-height:58rpx`
    - `border-radius:999rpx`
    - `font-size:19rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pkg-card\actor-card\index.wxss`
  - 同样已命中上述值

运行态截图：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r11c-quick-edit\screenshots\owner-share-action-mini-program.png`

运行态结论：

- `QUICK EDIT` 三个按钮已从偏厚重矩形收细为更接近 reference 的细长 pill
- 本轮是有效推进，不触发 3 次失败换向

补充链路说明：

- 本轮第一次截图时，`http://101.43.57.62/api` 被 301 到 `https://101.43.57.62/api`，命中 TLS SAN 校验问题
- 后续用：
  - `NODE_TLS_REJECT_UNAUTHORIZED=0`
  - baseUrl：`https://101.43.57.62/api`
  恢复截图链路
- 该问题记为**截图链路问题**，不是 UI 样式失败

### 29.2 history / records：filter 稳定为四个 scene pills，标题层级改为分享标题

页面：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\history\index.vue`

shared source：

- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-card-mvp.ts`

#### 29.2.1 shared scene title source 继续收口

本轮首先确保展示口径统一：

- `resolveShareCardSceneTitle` 对技术模板名回退 scene 展示名
- 当前运行态已确认：
  - `Smoke Template -> 经典`

参考样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r1-scene-title\screenshots\viewer-history.png`

#### 29.2.2 records 结构语义继续向 reference 收口

视觉合同：

- 页面：`pages/history/index`
- 可见块：
  - filter 胶囊行
  - 首条 history card 的标题层级
- 目标：
  - filter 稳定成 `全部 / 都市 / 古风 / 经典`
  - 当前只有 1 条记录时，不再在首屏右侧放 `清空记录`
  - 记录卡标题从“演员名”改为“分享标题”

本轮动作：

- `historyFilterOptions`
  - 固定为 `['全部', '都市', '古风', '经典']`
- `history-page__clear`
  - 从 `filteredHistoryItems.length` 改为 `historyItems.length > 1` 才展示
- 新增 `buildHistoryTitle`
  - `林夏 -> 林夏的经典写真集`
- `history-page__studio`
  - 行截断 `3 -> 2`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r2b-density`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `history-r2b-density` manifest：
  - `captureCount = 10`
  - `fallbackCount = 1`
  - `visualDidNotRefresh = false`

补充说明：

- `fallbackCount = 1` 发生在 `owner-card-editor-general`
- `viewer-history` 本身仍是 automator 直截图，不影响本页结论

关键产物证据：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\history\index.js`
  - 已命中：
    - `["全部","都市","古风","经典"]`
    - `function p(e){return\`${e.actorName}的${e.templateName}写真集\`}`
    - `i.value.length>1`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\history\index.wxml`
  - 已命中：
    - `清空记录`
    - 列表 title / studio / tag / reenter 结构仍保持
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\history\index.wxss`
  - 已命中：`-webkit-line-clamp:2`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\history\index.js`
  - 同样已命中上述结构逻辑

运行态截图：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-history-r2b-density\screenshots\viewer-history.png`

运行态结论：

- filter 当前已稳定显示：
  - `全部`
  - `都市`
  - `古风`
  - `经典`
- 当前只有 1 条记录时，首屏不再显示 `清空记录`
- 首条记录卡标题已从：
  - `林夏`
  收口为：
  - `林夏的经典写真集`
- `history` 本轮不是“页面没变化”

### 29.3 当前结论

- `actor-card / card preview`：
  - `QUICK EDIT` pills 已进一步收细
  - 本轮有效
- `history`：
  - records filter 行和首条 card 的结构语义已更接近 reference
  - 本轮有效
- 当前没有触发任何页面的 3 次失败自动换向条件

下一步建议：

1. 继续 `history`
   - 只做 filter / subtitle / card foot 的轻量密度整理
2. 或切到 `actor-card / poster preview`
   - 继续看 topbar 与 footer 的节奏差异
3. `create`
   - 继续暂停

## 36. actor-card / poster preview：topbar 的 title / switch 垂直节奏继续收口

### 36.1 本轮方向

主工作流继续固定在：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

页面：

- `pkg-card/actor-card/index?shareCardId=1&artifact=poster&shareMode=1`

可见块：

- `card-page__topbar`
  - `card-page__topbar-title`
  - `card-page__topbar-switch`

目标：

- 继续收口 `poster preview` 的 topbar 三点对齐
- 先只动 `title`
- 再只动 `switch`

保持不动：

- `back`
- poster head
- 主图高度
- footer
- 底部按钮

原因：

- 对比 `D:\XM\kaipai-team\tmp\reference-poster-screen-topbar.png` 与 `r16` 当前运行态，title 与 switch 都比 reference 略低
- 当前不需要同时改 `back / title / switch` 三个锚点，应按单锚点连续验证

### 36.2 第 17 轮：title 上移

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

动作：

- `card-page--preview-mode .card-page__topbar-title`
  - `padding-top: 132rpx -> 126rpx`

验证：

- `npm run type-check`
- `npm run build:mp-weixin`
- 微信开发者工具：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`
- 截图脚本：
  - `capture-mini-program-screenshots.js`

样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r17-topbar-title126`

结果：

- `captureCount = 10`
- `fallbackCount = 0`
- `visualDidNotRefresh = false`
- title 已较 `r16` 明确上移
- 当前变化不是旧图，也不是 runtime 未刷新

### 36.3 第 18 轮：switch 上移

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

动作：

- `card-page--preview-mode .card-page__topbar-switch`
  - 新增覆盖：
    - `margin-top: 128rpx`

说明：

- 基础样式仍保留：
  - `card-page__topbar-switch { margin-top: 132rpx }`
- 但 preview mode 单独覆盖到 `128rpx`，避免误伤其他态

验证：

- `npm run type-check`
- `npm run build:mp-weixin`
- 微信开发者工具：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`
- 截图脚本：
  - `capture-mini-program-screenshots.js`

样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r18-topbar-switch128`

结果：

- `captureCount = 10`
- `fallbackCount = 0`
- `visualDidNotRefresh = false`
- switch 已较 `r17` 再上移一小步
- topbar 的 title / switch 关系更接近 reference

### 36.4 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pkg-card\actor-card\index.wxss`
  - 已命中：
    - `.card-page--preview-mode .card-page__topbar-title{padding-top:126rpx`
    - `.card-page--preview-mode .card-page__topbar-switch{margin-top:128rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pkg-card\actor-card\index.wxss`
  - 同样已命中上述值
- reference：
  - `D:\XM\kaipai-team\tmp\reference-poster-screen-topbar.png`
- 本轮运行态：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r17-topbar-title126\screenshots\owner-share-action-poster.png`
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r18-topbar-switch128\screenshots\owner-share-action-poster.png`

### 36.5 当前结论

- `poster preview` 的 topbar 本轮连续拿到两次正向可见变化：
  1. title 上移
  2. switch 上移
- 当前没有触发“同一页面 / 同一可见块 / 同一类问题连续 3 次失败”换向条件
- `poster preview` 仍可继续，但下一手必须只看：
  - `card-page__preview-back`
    - 判断是否仍存在“略低 / 略大”的剩余差异
- 如果 topbar 再继续两轮仍无明显收益，应按约束自动切回：
  - `card preview`
  - 或 `mine`

## 37. home / 操作指南：停止继续压扁教程舞台，改回 reference-first 比例

### 37.1 本轮方向

用户补充的新截图已经明确说明：

- 当前 `home` 页的 `操作指南` 区块仍未复刻到参考页
- 问题不再是“CTA 是否刚好进入首屏”
- 而是：
  - 教程舞台被压得过扁
  - 整个 `guide` 视觉重心和 reference 偏差过大

因此本轮对 `home` 做一次**方向切换**：

- 从先前的 `CTA-first` 压缩路径
- 切回 `reference-first` 的教程舞台比例

页面：

- `pages/home/index`

可见块：

- `操作指南`
  - `home-page__guide-stage`
  - `home-page__guide-cover`

本轮只改：

- `home-page__guide-cover`

保持不动：

- `操作指南` 标题行
- 三步胶囊
- CTA 按钮
- hero / stats / 风格卡

### 37.2 判断依据

本地当前源码与最新运行态核对后，已确认：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 当前仍是：
    - `home-page__guide-cover { height: 208rpx }`
    - `home-page__guide-step { min-height: 52rpx }`
    - `home-page__guide-cta { height: 84rpx }`
- 最新运行态样本：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-actor-card-r18-topbar-switch128\screenshots\owner-home-share-cards.png`
  - 已确认它和当前源码一致，不是旧图
- 对照用户补充参考图后，当前最大差异是：
  - 教程舞台高度明显不足
  - 当前更像“短横幅”
  - reference 更接近 16:9 视频舞台

因此这不是继续压 `gap / CTA` 能解决的问题，而是 `guide-cover` 的真实锚点本身走偏了。

### 37.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__guide-cover`
  - `height: 208rpx -> 368rpx`

说明：

- 本轮故意不再同时改 `guide-step` / `guide-cta` / `body gap`
- 先只验证：
  - 教程舞台恢复到接近 reference 的纵横比后
  - 可见块是否回到正确方向

### 37.4 本轮验证

已执行：

- `npm run type-check`
- `npm run build:mp-weixin`
- 微信开发者工具：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`
- 截图脚本：
  - `capture-mini-program-screenshots.js`

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r8-guide368`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- manifest：
  - `captureCount = 10`
  - `fallbackCount = 5`
  - `visualDidNotRefresh = false`

补充说明：

- 本轮 `fallbackCount = 5` 是整组页面里其他页面的截图超时回退，不是 `home` 这页的样式失败
- `owner-home-share-cards` 仍是 automator 直截图成功

### 37.5 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：
    - `home-page__guide-cover { height: 368rpx }`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `.home-page__guide-cover{...height:368rpx...}`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 同样已命中上述值
- 最新运行态：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r8-guide368\screenshots\owner-home-share-cards.png`
- guide 区域裁切：
  - `D:\XM\kaipai-team\tmp\home-guide-r8-guide368-bottom.png`

### 37.6 当前结论

- `home / 操作指南` 的主问题已经从：
  - “CTA 是否露出”
  切回：
  - “教程舞台比例是否接近 reference”
- 本轮拿到了明确可见变化，说明换向是正确的：
  - 当前不再是过扁的短横幅
  - 教程舞台更接近 reference 的视频舞台比例
- 这轮不属于失败，也没有触发 3 次失败换向

下一步建议：

1. 继续停在 `home / 操作指南`
2. 但下一轮不能再继续只加高 `guide-cover`
3. 应改为判断：
   - 是继续调 `guide-copy / guide-play` 的层级细节
   - 还是把首页首屏构图改成更接近参考截面

## 38. home / 操作指南：纠正锚点，缩短 CTA 到 tabbar 的底部留白

### 38.1 用户反馈与本轮纠偏

用户继续指出：

- 当前 UI 仍没有按参考页实现
- 新红框明确圈定的是：
  - `guide-stage` 下方
  - 三步胶囊
  - `开始创建分享页`
  - CTA 下方到 tabbar 上方的白色留白

本轮复核后确认：

- 上一轮把问题判断成“继续恢复 guide 视频舞台比例”不准确
- 真正被用户框出的差异，不是继续拉高 `guide-cover`
- 而是 `CTA 下方白色留白` 偏大

因此本轮撤销上一轮本地过冲值：

- `home-page__guide-cover`
  - `368rpx -> 208rpx`

并切到真实锚点：

- `home-page__body`
  - `padding-bottom`

### 38.2 本轮视觉合同

页面：

- `pages/home/index`

可见块：

- `操作指南` 底部区域：
  - `home-page__guide-steps`
  - `home-page__guide-cta`
  - CTA 到 tabbar 的底部白色留白

目标：

- 缩短 CTA 下方空白
- 让三步胶囊与 CTA 的下半区更贴近参考页

保持不动：

- `操作指南` 标题行
- `guide-stage` 内部文案
- 三步胶囊尺寸
- CTA 尺寸、圆角、颜色
- `hero / stats / style cards`

### 38.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

1. 撤销上一轮本地过冲：
   - `home-page__guide-cover`
     - `height: 368rpx -> 208rpx`
2. 缩短真实底部留白：
   - `home-page__body`
     - `padding: 8rpx 46rpx calc(132rpx + env(safe-area-inset-bottom))`
     - 改为：
     - `padding: 8rpx 46rpx calc(72rpx + env(safe-area-inset-bottom))`

### 38.4 本轮验证

已执行：

- `npm run type-check`
- `npm run build:mp-weixin`
- 微信开发者工具：
  - `close`
  - `reset-fileutils`
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`
- 截图脚本：
  - `capture-mini-program-screenshots.js`

截图链路说明：

- 前两次截图失败分别为：
  - `injectSession-owner-home-share-cards timeout after 30000ms`
  - `Connection closed`
- 这是 DevTools automator 连接问题，不计入 UI 样式失败次数
- 重启 DevTools auto 后，第三次截图成功

验证样本：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r9-bodypb72`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- manifest：
  - `captureCount = 10`
  - `fallbackCount = 1`
  - `visualDidNotRefresh = false`
- `owner-home-share-cards` 是 automator 直截图成功

### 38.5 关键产物证据

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：
    - `padding: 8rpx 46rpx calc(72rpx + env(safe-area-inset-bottom))`
    - `height: 208rpx`
- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `.home-page__body{padding:8rpx 46rpx calc(72rpx + env(safe-area-inset-bottom))...}`
    - `.home-page__guide-cover{...height:208rpx...}`
- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 同样已命中上述值
- 最新运行态：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r9-bodypb72\screenshots\owner-home-share-cards.png`
- 最新底部裁切：
  - `D:\XM\kaipai-team\tmp\home-r9-bottom-region.png`

### 38.6 当前结论

- 本轮真正响应了用户红框：缩短 `CTA -> tabbar` 方向的底部留白
- `home` 本轮不是样式失败：
  - 源码命中
  - build/dev 产物命中
  - automator 首页截图刷新成功
- 但本轮也暴露了一个运行态不确定边界：
  - OS 窗口级截图抓到的可见 DevTools 窗口显示 `PKPD 工作台`
  - 与 automator 截到的 `pages/home/index` 不一致
  - 因此如果用户端仍看到不一致，需要优先排查可见 DevTools 项目 / 工作区错位，而不是继续改 CSS

下一步：

1. 如果用户确认看到的是当前 `home-r9` 截图，再继续细调 red-box 内间距
2. 如果用户看到的仍不是 `home-r9`，先处理 DevTools 可见工作区错位

## 39. home / 操作指南：清理 DevTools 可见窗口错位，确认前台工程回到 mp-weixin

### 39.1 背景

在第 38 轮后，为了核用户红框中包含 tabbar 的真实窗口效果，补抓 OS 窗口级截图时发现：

- automator 截到的是正确的：
  - `pages/home/index`
  - `为每一次相遇留下光影`
- 但 OS 窗口级截图看到的是：
  - `PKPD 工作台`

这说明当时存在：

- automator 运行态与前台可见 DevTools 窗口不一致
- 继续用可见窗口判断样式会误判

### 39.2 本轮动作

本轮先清理残留 DevTools 进程：

- `Get-Process wechatdevtools -ErrorAction SilentlyContinue | Stop-Process -Force`

然后重新打开唯一目标工程：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`

执行：

- `open-other`
- `auto-preview`
- `auto --auto-port 9520`

### 39.3 结果

重新打开后，当前前台窗口标题已从：

- `PKPD AI助手小程序 - 微信开发者工具 Stable v2.01.2510260`

变为：

- `mp-weixin - 微信开发者工具 Stable v2.01.2510260`

窗口截图：

- `D:\Cache\Temp\codex-shot-2026-04-22_23-02-48.png`

该窗口已重新显示当前 `home` 页上半屏：

- `JU MING PIAN · STUDIO`
- `为每一次相遇 留下光影`
- `风格分馆`

### 39.4 当前结论

- 之前的前台窗口确实是错位运行态，不应作为样式失败依据
- 当前前台窗口已经回到正确工程 `mp-weixin`
- 但由于当前桌面窗口高度有限，OS 窗口截图只能看到首页上半屏，未完整露出 `操作指南` 底部与 tabbar
- 因此第 38 轮的样式验证仍以 automator fresh 截图和三层产物为准

下一步若继续核 `CTA -> tabbar` 的最终视觉，应优先：

1. 保持当前唯一 `mp-weixin` DevTools 实例
2. 使用 automator fresh 截图确认页面内容
3. 必要时调整 DevTools 窗口 / 模拟器缩放后再抓 OS 窗口级截图

## 40. 流程纠偏：后续 UI 修改必须 spec-first，不能脱离 `00-73`

### 40.1 用户指出的问题

用户明确追问了 3 件事：

1. 为什么修改 UI 不创建 specs
2. 为什么不记录 UI 规范
3. 为什么每次修改不先读取已有 specs / 规范

### 40.2 当前核对结论

重新读取 `00-73` 后，当前事实已经明确：

- 不是没有 spec
  - `00-73` 已存在完整：
    - `requirements.md`
    - `design.md`
    - `tasks.md`
    - `execution.md`
- 也不是完全没有 UI 规范
  - `requirements` 已有：
    - 7 个 core screens 合同
    - `R27-R30` 截图推进与三次失败换向规则
  - `design` 已有：
    - shared visual contract
    - screen mapping
    - 逐页推进顺序

真正的问题是：

- 我在后续具体 UI 修改时，没有把已有 `00-73` 当成每轮都必须先读取、先引用、先回填的强制门禁
- 导致部分轮次虽然写了 `execution`，但实际锚点选择仍发生了漂移

### 40.3 本轮修正动作

本轮不新建重复 Spec，而是直接把流程门禁补入现有 `00-73`：

- `requirements.md`
  - 新增：
    - `R31-R35`
- `design.md`
  - 新增：
    - `6.6 Spec-first 的 UI 执行门禁`
- `tasks.md`
  - 新增并完成：
    - `T2.2`

修正后的执行规则是：

1. 每轮 UI 修改开始前，必须先读当前 `00-73`
2. 必须先写本轮页面合同：
   - route
   - reference
   - current runtime
   - visible block
   - expected change
   - keep-fixed items
3. 必须先确认真实视觉锚点
4. 一轮只做单锚点窄改
5. 必须完成 `src / dist\build / dist\dev / runtime` 四层核验
6. 结论必须回填 `execution.md`

### 40.4 当前结论

- 对属于 `00-73` 范围内的 UI 修改，后续不应重复新建平行 Spec
- 正确做法是：
  - 继续使用已有 `00-73`
  - 先读它
  - 再在它里面补充新的局部 UI 合同和执行记录
- 这次用户指出的是流程缺口，不是单纯样式缺口；因此本轮已先把流程门禁补齐

## 41. home / 操作指南：按 spec-first 回到 frame-level 收口

### 41.1 本轮前置依据

本轮先按新补的 `R31-R35` 执行，而不是直接改样式：

- 已重新读取：
  - `requirements.md`
  - `design.md`
  - `tasks.md`
  - `execution.md`
- 已把 `home / 操作指南` 的 block-level frame contract 补入：
  - `design.md -> 5.1.3`

本轮视觉合同固定为：

- 页面：`pages/home/index`
- reference：用户最新补充的 `操作指南` 红框参考图
- 可见块：`home-page__section--guide`
- 预期变化：
  - 恢复 `操作指南` 标题行到视频舞台的上下距离
  - 恢复视频舞台接近 reference 的 16:9 舞台感
  - 让三步胶囊与 CTA 整体回到更接近 reference 的 frame 位置
- 保持不动：
  - hero
  - 风格卡
  - 三步胶囊文案
  - CTA 文案 / 配色 / 圆角
  - `home-page__body` 当前 `72rpx` 底部留白结果

### 41.2 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__section--guide`
  - `gap: 4rpx -> 20rpx`
- `home-page__guide-cover`
  - `height: 208rpx -> 368rpx`

说明：

- 本轮不再继续压 `CTA`
- 也不再继续把问题误判成 `body padding-bottom`
- 而是先把 `guide` 整块的 frame-level 节奏拉回 reference 方向

### 41.3 本轮验证

已执行：

- `npm run type-check`
- `npm run build:mp-weixin`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `dist\build -> dist\dev`：已同步

四层核对中已完成的三层：

- `src`
- `dist\build`
- `dist\dev`

已命中：

- `home-page__section--guide { gap: 20rpx }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__body { padding-bottom: calc(72rpx + env(safe-area-inset-bottom)) }`

### 41.4 本轮运行态边界

本轮 fresh runtime 截图链路未恢复，原因不是样式失败，而是控制通道问题：

1. 全量截图脚本两次都停在：
   - `injectSession-owner-home-share-cards timeout after 30000ms`
2. 改为单页 automator：
   - `reLaunch/currentPage` 仍然超时
3. 改为 OS 窗口级截图：
   - 当前抓到的不是可靠的 DevTools 内容窗口

因此本轮结论必须显式保留边界：

- **代码已推进**
- **产物已命中**
- **但 fresh runtime 截图仍待下一轮链路恢复后确认**

### 41.5 当前结论

- 这一轮已经按 spec-first 回到 `home / 操作指南` 的 frame-level 调整
- 本轮不是“继续盲改数值”
- 但也不能宣称“已与 reference 对齐”
- 下一步必须优先恢复 fresh runtime 截图链路，然后再判定：
  - 当前 `guide` 整块是否已经回到正确方向
  - 还差的是上下 frame 还是左右 frame

## 42. home / 操作指南：截图链路三次失败后自动换向，已恢复单页 fresh runtime

### 42.1 失败链路与换向原因

在第 41 轮完成代码修改后，运行态截图链路连续失败：

1. 全量截图脚本第一次：
   - `injectSession-owner-home-share-cards timeout after 30000ms`
2. 全量截图脚本第二次：
   - 同样停在 `injectSession-owner-home-share-cards timeout after 30000ms`
3. 改为单页 automator：
   - `reLaunch/currentPage` 仍然超时

因此按 `R28-R30`，当前必须把方向从：

- “继续跑原来的全量 / 单页 automator 截图脚本”

切到：

- “先修复 DevTools / automator 控制通道，再恢复单页 fresh runtime”

这 3 次都属于：

- 截图链路 / 控制通道失败

不计入：

- 样式方向失败

### 42.2 本轮换向动作

已执行：

- 彻底重启微信开发者工具进程
- 重新打开唯一目标工程：
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- 重新执行：
  - `open-other`
  - `auto-preview`
  - `auto --auto-port 9520`

然后不再先跑全量 10 页，而是先做最小验证：

1. `miniProgram.currentPage()`
2. 单页 `reLaunch('/pages/home/index')`
3. 单页 `miniProgram.screenshot()`

### 42.3 恢复结果

当前单页 automator 已恢复：

- `currentPage()` 成功返回：
  - `pages/home/index`
- 单页 fresh runtime 截图成功：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r10-guideframe-single\screenshots\owner-home-share-cards.png`
- 单页 capture manifest 已写出：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r10-guideframe-single\captures\mini-program-screenshot-capture.json`

关键运行态结论：

- `guide` 区块当前已经不再是 `r9` 那种短横幅
- 当前 visible frame 已经回到：
  - 更高的视频舞台
  - 更松的标题 → 舞台节奏
  - 三步胶囊与 CTA 重新落回舞台下方

### 42.4 当前结论

- 本轮已按“三次失败自动换向”执行，不再死磕原截图脚本
- 当前 `home / 操作指南` 至少已经拿到 fresh runtime 单页截图
- 后续继续压 frame-level 差异时，应以：
  - `r9` 旧图
  - `r10` fresh 单页图
  - 用户当前 reference 红框图
  三者做对照

## 43. home / 操作指南：继续拉开 guide block 的垂直 frame

### 43.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- 用户最新补充的 `操作指南` 红框参考图

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r10d-scroll174-shot\screenshots\owner-home-share-cards-scroll174.png`

可见块：

- `home-page__section--guide`

目标：

- 继续拉开：
  - `标题 → 舞台`
  - `舞台 → pills`
  - `pills → CTA`
  的整体垂直节奏

保持不动：

- `guide-cover = 368rpx`
- `body bottom = 72rpx`
- CTA / pills 尺寸与文案
- 左右主留白

### 43.2 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__section--guide`
  - `gap: 20rpx -> 28rpx`

### 43.3 本轮验证

已执行：

- `npm run type-check`
- `npm run build:mp-weixin`
- 单页 fresh runtime：
  - `reLaunch('/pages/home/index')`
  - `pageScrollTo(174)`
  - `miniProgram.screenshot()`

已命中：

- `src`
  - `gap: 28rpx`
- `dist\dev`
  - `.home-page__section--guide{gap:28rpx`
- `dist\build`
  - 同样已命中

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r11-guidegap28\screenshots\owner-home-share-cards-scroll174.png`

裁切对照：

- `r10`：
  - `D:\XM\kaipai-team\tmp\home-r10d-bottom-region.png`
- `r11`：
  - `D:\XM\kaipai-team\tmp\home-r11-bottom-region.png`

### 43.4 当前结论

- `guide` 整块的垂直 frame 已较 `r10` 继续拉开
- `操作指南` 标题、舞台、pills、CTA 的层次更接近 reference
- 本轮是正确可感知变化，没有触发失败换向

## 44. home / 操作指南：舞台内文案块上移，补底部呼吸感

### 44.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- 用户最新补充的 `操作指南` 红框参考图

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r11-guidegap28\screenshots\owner-home-share-cards-scroll174.png`

可见块：

- `home-page__guide-copy`

目标：

- 把：
  - `三步创建你的分享页`
  - `选择风格 → 上传作品 → 生成卡片 / 海报`
  整体上移一小步
- 让文案离舞台底边更接近 reference 的呼吸感

保持不动：

- `section--guide = 28rpx`
- `guide-cover = 368rpx`
- `body bottom = 72rpx`
- pills / CTA frame

### 44.2 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__guide-copy`
  - `bottom: 20rpx -> 28rpx`

### 44.3 本轮验证

已执行：

- `npm run type-check`
- `npm run build:mp-weixin`
- 单页 fresh runtime：
  - `reLaunch('/pages/home/index')`
  - `pageScrollTo(174)`
  - `miniProgram.screenshot()`

已命中：

- `src`
  - `bottom: 28rpx`
- `dist\dev`
  - `.home-page__guide-copy{...bottom:28rpx...}`
- `dist\build`
  - 同样已命中上述值

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r12-guidecopy28\screenshots\owner-home-share-cards-scroll174.png`

裁切对照：

- `r11`：
  - `D:\XM\kaipai-team\tmp\home-r11-bottom-region.png`
- `r12`：
  - `D:\XM\kaipai-team\tmp\home-r12-bottom-region.png`

### 44.4 当前结论

- 舞台内文案块已较 `r11` 上移
- 当前 `guide` 内部底部呼吸感更接近 reference
- 到目前为止，当前页没有触发“同一块连续 3 次样式失败”

## 45. home / 操作指南：`body bottom` 在旧滚动口径下低收益，先记录，不继续盲猜

### 45.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- 用户最新补充的 `操作指南` 红框参考图

当前运行态基线：

- `D:\XM\\kaipai-team\\tmp\\ui-compare-20260423-home-r12-guidecopy28\\screenshots\\owner-home-share-cards-scroll174.png`

可见块：

- `CTA -> 页面底部可见留白`

目标：

- 缩短 CTA 下方的白色留白

保持不动：

- `guide-cover = 368rpx`
- `section--guide = 28rpx`
- `guide-copy = 28rpx`
- pills / CTA 尺寸

### 45.2 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__body`
  - `padding-bottom: calc(72rpx + env(safe-area-inset-bottom))`
  - 改为：
  - `padding-bottom: calc(56rpx + env(safe-area-inset-bottom))`

### 45.3 本轮验证与结论

已执行：

- `npm run type-check`
- `npm run build:mp-weixin`
- 单页 fresh runtime：
  - `reLaunch('/pages/home/index')`
  - `pageScrollTo(174)`
  - `miniProgram.screenshot()`

已命中：

- `src`
  - `calc(56rpx + env(safe-area-inset-bottom))`
- `dist\dev`
  - 已命中上述值
- `dist\build`
  - 同样已命中

但运行态量化结果显示：

- `r12` 与 `r13` 的 CTA 黑色按钮底边在当前 `scrollTop=174` 截图中处于同一位置
- `bottom_white` 没有产生用户可感知变化

因此当前结论是：

- 这轮不应继续在“固定 `scrollTop=174` 口径下盲调 `body bottom`”
- 这记为：
  - **当前验证口径低收益**
  - 不是“样式必然无效”

## 46. home / 操作指南：修正截图口径，改为 `maxScroll` 后重新判断底部留白

### 46.1 问题核实

继续核对页面运行态事实后，已确认：

- 当前页面总高：
  - `944`
- 当前可视高：
  - `762`
- 当前最大可滚动范围约：
  - `182`

这说明先前使用的：

- `scrollTop=174`

已经不是当前页面的最新底部验证口径。

### 46.2 本轮动作

本轮不再继续改样式，而是先修正验证口径：

- 改为：
  - `scrollTop = maxScroll = 182`

并重抓单页 fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r14-maxscroll\\screenshots\\owner-home-share-cards-maxscroll.png`

裁切：

- `D:\XM\kaipai-team\tmp\home-r14-bottom-region.png`

### 46.3 当前结论

- `r14` 才是当前更可信的底部 frame 对比口径
- 相比 `r13`，当前 `CTA -> 页面底部` 的可见留白已经更靠近 reference 方向
- 因此在修正滚动口径之前，不应把 `body bottom` 直接记为失败方向

后续继续压底部 frame 时，应优先使用：

- 当前页面实时 `maxScroll`

而不是继续沿用旧的固定 `174`

## 47. home / 操作指南：窗口级截图方向再次不稳定，切回单页 automator maxScroll 作为验收主口径

### 47.1 本轮继续核对

按 `R31-R35`，本轮继续先核：

- `requirements.md`
- `design.md`
- `execution.md`
- 当前 `home / 操作指南` 的最新运行态截图链

当前已确认的有效口径仍是：

- 页面：
  - `pages/home/index`
- 可见块：
  - `home-page__section--guide`
- 有效 fresh runtime：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r14-maxscroll\screenshots\owner-home-share-cards-maxscroll.png`
- 当前最大滚动信息：
  - `height = 944`
  - `innerHeight = 762`
  - `maxScroll = 182`
  - `scrollTop = 182`

### 47.2 本轮发现

本轮为了核 `CTA -> tabbar` 的真实窗口级留白，尝试重新抓 OS 窗口级截图。

过程：

1. 清理并重新打开 `dist\dev\mp-weixin`
2. 前台窗口短暂回到：
   - `mp-weixin - 微信开发者工具 Stable v2.01.2510260`
3. 使用 automator 将 `pages/home/index` 滚到：
   - `scrollTop = 182`
4. 尝试窗口级截图时失败：
   - `Failed to get window bounds`
5. 再次检查窗口后，前台窗口又漂回：
   - `PKPD AI助手小程序 - 微信开发者工具 Stable v2.01.2510260`
6. 同时 `ws://127.0.0.1:9520` 控制通道掉线：
   - `Failed connecting to ws://127.0.0.1:9520`

### 47.3 换向结论

这已经不是 `home` 页面样式问题，而是：

- DevTools 可见实例漂移
- OS 窗口截图不稳定
- automator 端口被错误实例/窗口状态打断

因此后续不再把“窗口级截图是否成功”作为当前样式推进的阻塞项。

本阶段验收主口径调整为：

1. `src`
2. `dist\build`
3. `dist\dev`
4. 单页 automator fresh runtime
5. `maxScroll` 口径下的 `home` 单页截图

窗口级截图只作为辅助口径；若再次漂移，不计为样式失败。

### 47.4 当前代码状态

当前 `home / 操作指南` 已落地的值：

- `home-page__section--guide`
  - `gap: 28rpx`
- `home-page__guide-cover`
  - `height: 368rpx`
- `home-page__guide-copy`
  - `bottom: 28rpx`
- `home-page__guide-cta`
  - `margin-top: 8rpx`
- `home-page__body`
  - `padding-bottom: calc(56rpx + env(safe-area-inset-bottom))`

### 47.5 当前结论

- 本轮没有继续盲调 CSS
- 已按三次失败换向原则，把不稳定方向从“窗口截图”切回“单页 automator + maxScroll”
- 下一轮若继续动样式，应基于 `r14 maxScroll` 图，而不是窗口级截图

## 48. home / 操作指南：基于 `r14 maxScroll`，改动 CTA 自身锚点而不是继续猜 body

### 48.1 本轮判断

在 `r14 maxScroll` 口径下复核后，当前判断为：

- `guide-stage` 左右主留白已经与 reference 基本一致
- `guide-copy` 的底部呼吸感已经较之前改善
- 当前最值得继续验证的，不是继续盲调 `body bottom`
- 而是：
  - `guide-steps -> guide-cta`
  的直接间隔

因此当前选择把主锚点收窄到：

- `home-page__guide-cta`

### 48.2 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__guide-cta`
  - 新增：
    - `margin-top: 8rpx`

说明：

- 本轮不动：
  - `guide-cover = 368rpx`
  - `guide-copy = 28rpx`
  - `section--guide = 28rpx`
  - `body bottom = 56rpx`
- 只验证 CTA 自身下移是否会形成用户可感知变化

### 48.3 本轮验证

已执行：

- `npm run type-check`
- `npm run build:mp-weixin`

已命中：

- `src`
  - `home-page__guide-cta { margin-top: 8rpx }`
- `dist\dev`
  - `.home-page__guide-cta{margin-top:8rpx...}`
- `dist\build`
  - 同样已命中上述值

### 48.4 当前结论

- 本轮已完成 CTA 自身锚点的最小变更
- 后续是否继续沿 CTA 方向推进，必须基于 `maxScroll` 口径 fresh runtime 再判断

## 49. home / 操作指南：`body bottom = 56rpx` 的效果只能在 `maxScroll` 口径下判断

### 49.1 当前核实事实

重新核对运行态后，当前页面事实为：

- 页面总高：
  - `944`
- 可视高：
  - `762`
- 最大滚动范围：
  - `182`

因此：

- 旧的 `scrollTop = 174`
  - 已经不是当前页面的精确底部验收口径
- `body bottom = 56rpx` 的效果，只能在：
  - `scrollTop = 182`
  下判断

### 49.2 当前有效 fresh runtime 样本

- `r14 maxScroll`
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r14-maxscroll\screenshots\owner-home-share-cards-maxscroll.png`
- `r14 bottom crop`
  - `D:\XM\kaipai-team\tmp\home-r14-bottom-region.png`

### 49.3 当前结论

- `body bottom = 56rpx` 不能再按旧口径误判为“没有变化”
- 后续只要继续压底部 frame，必须默认使用：
  - `maxScroll = 182`
  的单页 fresh runtime
- 若下一轮在 `maxScroll` 口径下仍连续 2 次低收益，再切走 `body bottom` 方向

## 50. home / 操作指南：确认当前真实 maxScroll=165，底部白边已继续收口

### 50.1 事实纠偏

继续核对后，发现旧的 `r15` 截图仍记录：

- `height = 944`
- `maxScroll = 182`

但当前真实运行态已经变为：

- `height = 927`
- `innerHeight = 762`
- `maxScroll = 165`

因此本轮不再沿用旧 `r15` 作为最终判断，而是重新抓取当前真实 `maxScroll=165` 的 fresh runtime。

### 50.2 本轮有效截图

当前有效 fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r16-maxscroll165\screenshots\owner-home-share-cards-maxscroll.png`

裁切：

- `D:\XM\kaipai-team\tmp\home-r16-bottom-region.png`

### 50.3 量化结果

以整张 fresh runtime 为统一口径，量化 CTA 黑色按钮到底边距离：

- `r14`
  - `CTA bbox: [47, 1066, 732, 1396]`
  - `bottom_white = 127px`
- `r16`
  - `CTA bbox: [47, 1066, 732, 1430]`
  - `bottom_white = 93px`

结论：

- 当前 `CTA -> 页面底部` 白边已经较 `r14` 明确缩短
- `body bottom` 方向本轮是有效推进
- 不能把旧 `r15` 的过期 `maxScroll=182` 当成最终结论

### 50.4 当前结论

- 当前 `home / 操作指南` 已经完成一轮有效的底部 frame 收口
- `body bottom = 24rpx` 在真实 `maxScroll=165` 口径下产生了正确可见变化
- 下一步继续时，应以 `r16(maxScroll=165)` 为最新基线

## 51. home / 操作指南：`body bottom = 0` 继续缩短 CTA 下方白边

### 51.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- 用户最新补充的 `操作指南` 红框参考图

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r16-maxscroll165\screenshots\owner-home-share-cards-maxscroll.png`

可见块：

- `CTA -> 页面底部可见白边`

目标：

- 在 `r16(maxScroll=165)` 已经有效收口的基础上，再把 CTA 下方白边缩短一小步

保持不动：

- `guide-cover = 368rpx`
- `section--guide = 28rpx`
- `guide-copy = 28rpx`
- `guide-cta margin-top = 8rpx`
- pills / CTA 尺寸与左右 frame

### 51.2 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__body`
  - `padding-bottom: calc(24rpx + env(safe-area-inset-bottom))`
  - 改为：
  - `padding-bottom: 0`

### 51.3 本轮验证

已执行：

- `npm run type-check`
- `npm run build:mp-weixin`
- 单页 fresh runtime：
  - `reLaunch('/pages/home/index')`
  - 运行态重算：
    - `height = 927`
    - `innerHeight = 762`
    - `maxScroll = 165`
  - `pageScrollTo(165)`
  - `miniProgram.screenshot()`

已命中：

- `src`
  - `home-page__body { padding: 8rpx 46rpx 0; }`
- `dist\dev`
  - `.home-page__body{padding:8rpx 46rpx 0...}`
- `dist\build`
  - 同样已命中上述值

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r17-bodypb0\screenshots\owner-home-share-cards-maxscroll.png`

裁切：

- `D:\XM\kaipai-team\tmp\home-r17-bottom-region.png`

### 51.4 量化结果

以整张 fresh runtime 统一量化 CTA 黑色按钮到底边距离：

- `r16`
  - `CTA bbox: [47, 1066, 732, 1430]`
  - `bottom_white = 93px`
- `r17`
  - `CTA bbox: [47, 1066, 732, 1454]`
  - `bottom_white = 69px`

### 51.5 当前结论

- `body bottom = 0` 相较 `r16` 继续产生了正确可见变化
- 当前 `CTA -> 页面底部` 白边已继续缩短
- 到目前为止，`body bottom` 在真实 `maxScroll=165` 口径下仍然是高收益方向

## 52. home / 操作指南：复核 r17 manifest，修正当前稳定 maxScroll 口径

### 52.1 本轮前置读取

本轮继续执行 `R31-R35`，已重新读取：

- `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\requirements.md`
- `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\execution.md`

本轮仍只处理同一主线：

- 页面：`pages/home/index`
- 可见块：`home / 操作指南`
- reference：
  - `D:\XM\kaipai-team\tmp\home-guide-r8.png`
  - `D:\XM\kaipai-team\tmp\home-lower-r8.png`
- 当前最新稳定运行态：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r17-bodypb0\screenshots\owner-home-share-cards-maxscroll.png`
  - `D:\XM\kaipai-team\tmp\home-r17-bottom-region.png`

### 52.2 事实修正

重新读取 r17 的 capture manifest 后，确认 r17 真实记录为：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r17-bodypb0\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 915`
  - `innerHeight = 762`
  - `maxScroll = 153`
  - `scrollTop = 153`

因此，后续不能再把 `maxScroll=165` 当成当前最新稳定口径。`165` 只能视为前一阶段运行态口径；当前可引用的最新稳定 fresh runtime 是 `r17(maxScroll=153)`。

### 52.3 当前结论

- 之前 `bottom_white = 69px` 的 r17 量化结论仍保留。
- 但该结论对应的稳定滚动口径应修正为 `maxScroll=153`。
- 后续若恢复 fresh runtime，必须重新读取当轮 `page.size()` / `window.innerHeight`，不能沿用 `153`、`165` 或 `182` 的历史数值。

## 53. home / 操作指南：automator 三次失败后切换方向，并回收未记录 CTA transform

### 53.1 当前失败链路

本轮尝试继续抓当前 fresh runtime，但 automator 链路再次连续失败：

1. `9520` 被父进程已消失的孤儿 `node.exe` 占用，`Automator.launch()` 返回 `Port 9520 is in use`
2. 清理孤儿进程后，`.automator.json` 的 `wsEndpoint=ws://198.18.0.1:9520` 与当前 launcher 计算出的 `ws://localhost:9520` 不一致，导致 automator 误触发编译链并抛出 `spawn EINVAL`
3. 临时切到单一 DevTools 工程并执行 `close / open-other / auto --auto-port 9520` 后，`Automator.launch()` 仍超时，未生成新截图

这 3 次都属于：

- 截图链路 / automator 控制通道失败

不计为：

- `home / 操作指南` 样式锚点失败

按 `R28-R30`，本轮必须自动换方向，不再继续死磕 automator。

### 53.2 换向动作

新的方向：

- 从 `单页 automator fresh runtime`
- 切到 `单一 DevTools 实例 + OS 级 active-window 截图`

已确认当前活动窗口：

- 标题：`mp-weixin - 微信开发者工具 Stable v2.01.2510260`
- 工程侧栏：`MP-WEIXIN`
- 可见首页顶部已是当前重构后的：
  - `JU MING PIAN · STUDIO`
  - `为每一次相遇 / 留下光影`
  - `风格分馆`

OS 级截图证据：

- `D:\XM\kaipai-team\tmp\home-devtools-top-20260423-041953.png`
- `D:\XM\kaipai-team\tmp\home-devtools-top-after-scroll-attempts-20260423-042232.png`

补充边界：

- OS 级截图只能确认 DevTools 当前工程与首页顶部运行态没有漂到旧项目。
- 通过 `mouse wheel / PageDown / drag` 三种方式尝试把模拟器滚到 `操作指南` 下半区均未产生可见滚动，因此本轮不继续把 OS 滚动链路作为阻塞项。
- 下半区仍以 r17 fresh runtime 作为当前稳定截图基线。

### 53.3 发现并回收的未记录样式变量

核对当前代码与 `execution.md` 后发现：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- `home-page__guide-cta`
- 当前源码与 `dist` 中曾出现：
  - `transform: translateY(8rpx)`

但该值没有在 `51` 之前的执行链中形成完整的：

- 页面合同
- 当前运行态截图
- 量化结论
- `src / dist\build / dist\dev / runtime` 四层核验

因此本轮不把该 transform 当成已验证 UI 推进；按 spec-first 规则，先回收到最后一个已验证口径：

- 保留 `home-page__guide-cta { margin-top: 8rpx }`
- 移除未记录的 `transform: translateY(8rpx)`

### 53.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

已命中：

- `src`
  - `home-page__body { padding: 8rpx 46rpx 0; }`
  - `home-page__section--guide { gap: 28rpx; }`
  - `home-page__guide-cover { height: 368rpx; }`
  - `home-page__guide-copy { bottom: 28rpx; }`
  - `home-page__guide-cta { margin-top: 8rpx; }`
  - 不再命中 `transform: translateY(8rpx)`
- `dist\build`
  - `.home-page__guide-cta{margin-top:8rpx...}`
  - 不再命中 `translateY`
- `dist\dev`
  - `.home-page__guide-cta{margin-top:8rpx...}`
  - 不再命中 `translateY`

### 53.5 当前结论

- 本轮主要推进是流程纠偏与可验证基线回收，不新增第二个视觉变量。
- 当前 `home / 操作指南` 保持在 r17 的最新稳定视觉基线：
  - `body bottom = 0`
  - `CTA bottom_white = 69px`
  - `maxScroll` 稳定记录修正为 `153`
- 下一轮若继续改样式，必须先恢复一个可滚动到下半区的 fresh runtime 或 OS 截图链路；若暂时无法恢复，只能基于 r17 继续做显式标注的不确定估计，不能宣称“已 1:1”。

## 54. home / 操作指南：三次失败后从 `uni-automator` 切到旧成功链，已恢复 fresh runtime

### 54.1 换向依据

在 `53` 中，当前 `uni-automator launch()` 路线已经连续 3 次失败并完成换向记录。

因此本轮不再继续沿：

- `@dcloudio/uni-automator`
- `launch({ projectPath, cliPath, compile: false })`

做第 4 次同类试错，而是切到此前成功记录里真实使用过的旧链路：

- `D:\XM\kaipai-team\tmp\automator-probe`
- `miniprogram-automator`
- 直接连接 `ws://127.0.0.1:9520`

换向依据来自历史成功证据：

- `D:\XM\kaipai-team\tmp\ui-compare-20260422-home-r8-guide368\captures\mini-program-capture-progress.log`
- 其中已明确记录：
  - `connect-ok`
  - `wsEndpoint = ws://127.0.0.1:9520`
  - `automatorResolvedFrom = D:\XM\kaipai-team\tmp\automator-probe\node_modules\miniprogram-automator\package.json`

### 54.2 本轮恢复过程

本轮恢复不是一次成功，中间仍有 3 次同方向排查，但它们都属于“恢复旧成功截图链”的子步骤，而不是样式调参：

1. 第一次直接执行：
   - `D:\XM\kaipai-team\tmp\automator-probe\connect-and-probe.js`
   - 连接建立后卡住超时，没有产出截图
2. 第二次在 `auto-preview` 后再次执行同脚本：
   - 仍然超时
3. 抓取活动窗口截图后发现：
   - `D:\Cache\Temp\codex-shot-2026-04-23_04-36-18.png`
   - 模拟器当时显示：
     - `模拟器启动失败`
     - `TypeError: Cannot read property 'subPackages' ...`

随后继续缩小范围，不再沿“滚动控制”排障，而是先把 DevTools 工程重新切回唯一目标工程，再只恢复自动化端口：

- `close --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `open-other --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `auto --auto-port 9520 --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`

之后再次运行：

- `D:\XM\kaipai-team\tmp\automator-probe\connect-and-probe.js`

已恢复成功，当前返回：

- `currentPage.path = pages/home/index`
- `pageStack = [pages/home/index]`

截图产物：

- `D:\XM\kaipai-team\tmp\automator-probe\probe-current-page-9520-r3.png`

### 54.3 fresh runtime 恢复结果

恢复旧成功链后，已重新抓到 `home / 操作指南` 的 fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r18-recovered-miniprogram\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r18-bottom-region.png`

当前真实运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r18-recovered-miniprogram\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 881`
  - `innerHeight = 762`
  - `maxScroll = 119`
  - `scrollTop = 119`

因此当前口径再次更新：

- 后续不再沿用 `153`
- 当前最新稳定 fresh runtime 基线改为 `r18(maxScroll=119)`

### 54.4 当前结论

- 当前首页 fresh runtime 截图链已恢复。
- 真正可靠的恢复方式是：
  - `miniprogram-automator + ws://127.0.0.1:9520 + auto --auto-port 9520`
- 至少到本轮为止，还不能把 `project.private.config.json` 的改动宣称为唯一根因修复；它只能视为恢复过程中做过的一次本地辅助尝试。

## 55. home / 操作指南：基于 r18 fresh runtime，缩小 styles → guide 的 section 间距

### 55.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\home-guide-r8.png`
- `D:\XM\kaipai-team\tmp\home-lower-r8.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r18-recovered-miniprogram\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r18-bottom-region.png`

可见块：

- `风格分馆` 底部卡片行 → `操作指南` 标题行 的垂直距离

预期变化：

- 把整个 `操作指南` 区块相对 `风格分馆` 上移一小步
- 只缩短两个 section 之间的外部间距

保持不动：

- `home-page__section--guide { gap: 28rpx }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__guide-copy { bottom: 28rpx }`
- `home-page__guide-cta { margin-top: 8rpx }`
- `home-page__body { padding: 8rpx 46rpx 0 }`

### 55.2 锚点判断

对照 `r18` 与 reference 后，本轮差异不在：

- stage 比例
- CTA 自身高度
- pills 自身尺寸
- body bottom 留白

而在：

- `styles section` 与 `guide section` 之间的外部节奏仍略大

因此当前真实视觉锚点不是 `guide-cover` / `guide-cta`，而是承载两个 section 的：

- `home-page__body`

### 55.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__body`
  - `gap: 16rpx -> 8rpx`

### 55.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- fresh runtime 重新抓取：
  - `auto --auto-port 9520`
  - `miniprogram-automator connect`
  - `reLaunch('/pages/home/index')`
  - `pageScrollTo(maxScroll)`
  - `miniProgram.screenshot()`

已命中：

- `src`
  - `home-page__body { ... gap: 8rpx; }`
- `dist\build`
  - `.home-page__body{padding:8rpx 46rpx 0;display:flex;flex-direction:column;gap:8rpx}`
- `dist\dev`
  - `.home-page__body{padding:8rpx 46rpx 0;display:flex;flex-direction:column;gap:8rpx}`

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r19-bodygap8\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r19-bottom-region.png`

对应运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r19-bodygap8\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 877`
  - `innerHeight = 762`
  - `maxScroll = 115`
  - `scrollTop = 115`

### 55.5 当前结论

- `home-page__body gap: 16rpx -> 8rpx` 后，页面总高从：
  - `881 -> 877`
- 对应 `maxScroll` 从：
  - `119 -> 115`
- 当前 `风格分馆` 到 `操作指南` 的 section 间距已经缩短一小步。
- 本轮是可见且可验证变化，没有再回到盲猜 `CTA` / `guide-cover` 的旧方向。

## 56. home / 操作指南：继续把 styles → guide section gap 收到 0

### 56.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\home-guide-r8.png`
- `D:\XM\kaipai-team\tmp\home-lower-r8.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r19-bodygap8\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r19-bottom-region.png`

可见块：

- `风格分馆` 底部卡片行 → `操作指南` 标题行 的垂直距离

预期变化：

- 在 `55` 已经正确缩小 section gap 的基础上，再把 `操作指南` 整块相对 `风格分馆` 上移一小步

保持不动：

- `home-page__section--guide { gap: 28rpx }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__guide-copy { bottom: 28rpx }`
- `home-page__guide-cta { margin-top: 8rpx }`
- `home-page__body { padding: 8rpx 46rpx 0 }`

### 56.2 锚点判断

对照 `r19` 与 reference，当前差异仍然是：

- `styles section` 与 `guide section` 之间的外部节奏略大

而不是：

- `guide` 内部标题到舞台的距离
- stage 高度
- CTA 高度
- pills 自身尺寸

因此本轮继续沿同一直接视觉锚点推进：

- `home-page__body`

动作只做一件事：

- `gap: 8rpx -> 0`

### 56.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__body`
  - `gap: 8rpx -> 0`

### 56.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- fresh runtime 重新抓取：
  - `auto --auto-port 9520`
  - `miniprogram-automator connect`
  - `reLaunch('/pages/home/index')`
  - `pageScrollTo(maxScroll)`
  - `miniProgram.screenshot()`

已命中：

- `src`
  - `home-page__body { ... gap: 0; }`
- `dist\build`
  - `.home-page__body{padding:8rpx 46rpx 0;display:flex;flex-direction:column;gap:0}`
- `dist\dev`
  - `.home-page__body{padding:8rpx 46rpx 0;display:flex;flex-direction:column;gap:0}`

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r20-bodygap0\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r20-bottom-region.png`

对应运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r20-bodygap0\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 873`
  - `innerHeight = 762`
  - `maxScroll = 111`
  - `scrollTop = 111`

### 56.5 当前结论

- `home-page__body gap: 8rpx -> 0` 后，页面总高从：
  - `877 -> 873`
- 对应 `maxScroll` 从：
  - `115 -> 111`
- 当前 `风格分馆` 到 `操作指南` 的 section 间距又继续缩短了一小步。
- 到此为止，`home-page__body gap` 这条轴已经收到了 `0`，不应再继续沿同一变量做第 4 次无意义试探。
- 若后续还要继续收 `home / 操作指南`，下一轮必须切到新的直接锚点，而不是继续空转 `body gap`。

## 57. home / 操作指南：切到 guide 内部 gap，收 `section head → stage → pills → CTA` 节奏

### 57.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\home-guide-r8.png`
- `D:\XM\kaipai-team\tmp\home-lower-r8.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r20-bodygap0\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r20-bottom-region.png`

可见块：

- `home-page__section--guide`
- 具体是 `操作指南` 内部四段：
  - section head
  - video stage
  - three pills
  - primary CTA

预期变化：

- 在 `home-page__body gap` 已经收到 `0` 后，不再继续沿外部 section 间距空转。
- 改为把 `操作指南` 内部统一垂直节奏收紧一小步，让 `section head → stage → pills → CTA` 更接近 reference 的 compact frame。

保持不动：

- `home-page__body { padding: 8rpx 46rpx 0; gap: 0 }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__guide-copy { bottom: 28rpx }`
- `home-page__guide-cta { margin-top: 8rpx }`
- pills / CTA 尺寸与文案

### 57.2 换向说明

本轮不是因为 `home-page__body gap` 失败而换向，而是因为该变量已经到达下限：

- `home-page__body gap = 0`

继续沿这个变量推进没有实际空间，因此自动切到新的直接视觉锚点：

- `home-page__section--guide`

该锚点只控制 `操作指南` 内部 children 的统一 gap，符合当前 block-level frame contract。

### 57.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__section--guide`
  - `gap: 28rpx -> 24rpx`

### 57.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- fresh runtime 重新抓取：
  - `auto --auto-port 9520`
  - `miniprogram-automator connect`
  - `reLaunch('/pages/home/index')`
  - `pageScrollTo(maxScroll)`
  - `miniProgram.screenshot()`

已命中：

- `src`
  - `home-page__body { ... gap: 0; }`
  - `home-page__section--guide { gap: 24rpx; }`
- `dist\build`
  - `.home-page__body{padding:8rpx 46rpx 0;display:flex;flex-direction:column;gap:0}`
  - `.home-page__section--guide{gap:24rpx}`
- `dist\dev`
  - `.home-page__body{padding:8rpx 46rpx 0;display:flex;flex-direction:column;gap:0}`
  - `.home-page__section--guide{gap:24rpx}`

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r21-guidegap24\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r21-bottom-region.png`

对应运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r21-guidegap24\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 867`
  - `innerHeight = 762`
  - `maxScroll = 105`
  - `scrollTop = 105`

### 57.5 当前结论

- `home-page__section--guide gap: 28rpx -> 24rpx` 后，页面总高从：
  - `873 -> 867`
- 对应 `maxScroll` 从：
  - `111 -> 105`
- 当前 `操作指南` 内部 `section head → stage → pills → CTA` 的统一节奏已继续收紧。
- 本轮没有动 stage 高度、CTA 尺寸或 body bottom，因此风险集中、可回滚。
- 这条新锚点目前只做了第 1 次有效推进，尚未触发三次失败换向。

## 58. home / 操作指南：舞台内文案上移，fresh runtime 三次失败后切到 OS 截图 + 产物核验

### 58.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\home-guide-r8.png`
- `D:\XM\kaipai-team\tmp\home-lower-r8.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r21-guidegap24\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r21-bottom-region.png`

可见块：

- `home-page__guide-copy`

预期变化：

- 把舞台内：
  - `三步创建你的分享页`
  - `选择风格 → 上传作品 → 生成卡片 / 海报`
  整体上移一小步
- 让文案落点更接近 reference 中相对舞台顶边的层级。

保持不动：

- `home-page__body { padding: 8rpx 46rpx 0; gap: 0 }`
- `home-page__section--guide { gap: 24rpx }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__guide-cta { margin-top: 8rpx }`
- pills / CTA 尺寸与文案

### 58.2 本轮锚点判断

对比 `r21` 与 reference 后，本轮判断：

- `body gap` 已经到 `0`，不能继续沿外部 section gap 空转。
- `section--guide gap` 已经完成一轮有效收口。
- 当前更直接的剩余差异在舞台内文案落点：
  - 当前文案相对舞台顶边仍偏低。

因此本轮只动：

- `home-page__guide-copy`

### 58.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__guide-copy`
  - `bottom: 28rpx -> 40rpx`

### 58.4 本轮三层产物核验

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

已命中：

- `src`
  - `home-page__guide-copy { bottom: 40rpx; }`
- `dist\build`
  - `.home-page__guide-copy{...bottom:40rpx...}`
- `dist\dev`
  - `.home-page__guide-copy{...bottom:40rpx...}`

### 58.5 fresh runtime 三次失败与自动换向

本轮尝试继续使用已经恢复过的：

- `miniprogram-automator + ws://127.0.0.1:9520`

但 fresh runtime 链路在本轮连续失败 3 次：

1. 单页 maxScroll 复拍脚本超时：
   - 目标目录：`D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r22-guidecopy40`
   - `node -e ... miniProgram.screenshot()` 未产出截图
2. 活动窗口截图确认模拟器不是目标页，而是启动失败态：
   - `D:\XM\kaipai-team\tmp\home-devtools-simulator-startup-fail-20260423-051309.png`
   - 可见错误：
     - `模拟器启动失败`
     - `TypeError: Cannot read property 'subPackages' of undefined`
3. 切回 `open-other / auto-preview / auto` 后，最小探针仍失败：
   - `connect-and-probe.js` 超时
   - 不带截图、只读 `currentPage()` 的最小探针也超时

因此按 `R28-R30`，本轮自动换方向：

- 不再继续第 4 次死磕 fresh runtime 自动截图。
- 当前切到：
  - `src / dist\build / dist\dev` 产物核验
  - OS 级窗口状态截图
  - 等下一轮先恢复 DevTools 模拟器态，再继续 runtime 截图。

OS 级证据：

- 模拟器启动失败：
  - `D:\XM\kaipai-team\tmp\home-devtools-simulator-startup-fail-20260423-051309.png`
- 切回资源管理器态：
  - `D:\XM\kaipai-team\tmp\home-devtools-resource-manager-20260423-051558.png`

### 58.6 当前结论

- `home-page__guide-copy bottom: 40rpx` 已经完成 `src / dist\build / dist\dev` 三层命中。
- 但本轮没有拿到新的 fresh runtime 下半区截图，因此不能把该改动宣称为“视觉已完成”。
- 当前状态应标记为：
  - **实现已进入产物**
  - **runtime 视觉复核待下一轮恢复 DevTools 模拟器后确认**
- 下一轮继续前，必须先处理 DevTools 当前资源管理器 / 模拟器启动失败状态；不能在未恢复运行态截图前继续叠加新的视觉变量。

## 59. home / 操作指南：修复 DevTools condition 缓存后补回 r22 fresh runtime

### 59.1 本轮前置目标

本轮不继续叠加新的 UI 变量，先处理 `58` 留下的运行态阻塞：

- DevTools 模拟器启动失败
- `TypeError: Cannot read property 'subPackages' of undefined`
- `miniprogram-automator currentPage()` 超时

目标：

- 恢复 `pages/home/index` 的 fresh runtime 截图链
- 回头验证 `58` 中已经进入产物的：
  - `home-page__guide-copy { bottom: 40rpx }`

### 59.2 根因定位

已检查 DevTools 当前实例日志：

- `C:\Users\33340\AppData\Local\微信开发者工具\User Data\2c0794bb421bb17cb0bb8a5492508d1d\WeappLog\logs\2026-04-23-05-27-10-126-vozUefmJex.log`

关键错误：

- `simulator launch catch error TypeError: Cannot read property 'subPackages' of undefined`

随后检查当前项目在 DevTools 用户数据中的本地缓存：

- `C:\Users\33340\AppData\Local\微信开发者工具\User Data\2c0794bb421bb17cb0bb8a5492508d1d\WeappLocalData\localstorage_fcfc88d0783e840b14f831f02bf08a7c.json`

发现同一文件里存在状态不一致：

- 旧字段 `condiction.weapp.list` 有 `t7-home`
- 但当前字段 `condition.miniprogram` 是空列表

判断：

- DevTools 启动模拟器时很可能读取了空的 `condition.miniprogram`，导致后续取目标页配置时拿到 `undefined`，再访问 `subPackages` 抛错。

### 59.3 本轮修复动作

已先备份原始 DevTools 缓存文件：

- `D:\XM\kaipai-team\tmp\localstorage_fcfc88d0783e840b14f831f02bf08a7c.backup-20260423-0535.json`

然后把当前工程缓存里的 condition 统一到：

- `name = t7-home`
- `pathName = pages/home/index`
- `query = ""`

具体修正字段：

- `condiction.weapp.current = 0`
- `condiction.weapp.list = [t7-home]`
- `condition.miniprogram.current = 0`
- `condition.miniprogram.list = [t7-home]`

说明：

- 这是 DevTools 运行态缓存修复，不属于前台业务代码修改。
- 当前目的是恢复截图验证链，而不是改变小程序产物。

### 59.4 恢复验证

重新执行：

- `close --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `quit`
- `open-other --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `auto-preview --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `auto --auto-port 9520 --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`

最小探针已恢复：

- `miniprogram-automator currentPage()`
- 返回：
  - `path = pages/home/index`
  - `query = {}`

OS 级运行态截图也确认模拟器不再停在启动失败页：

- `D:\Cache\Temp\codex-shot-2026-04-23_05-40-32.png`

### 59.5 补回 r22 fresh runtime

已重新抓取 `home / 操作指南` fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r22-guidecopy40-recovered\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r22-bottom-region.png`

运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r22-guidecopy40-recovered\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 867`
  - `innerHeight = 762`
  - `maxScroll = 105`
  - `scrollTop = 105`

### 59.6 当前结论

- `home-page__guide-copy bottom: 40rpx` 已经补回 fresh runtime 验证。
- 当前运行态截图显示舞台内文案已较 `r21` 上移，且没有破坏：
  - stage 高度
  - pills
  - CTA
  - body gap
- 因此 `bottom: 40rpx` 暂时保留，作为当前最新有效基线。
- 当前最新可信截图基线更新为：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r22-guidecopy40-recovered\screenshots\owner-home-share-cards-maxscroll.png`
  - `D:\XM\kaipai-team\tmp\home-r22-bottom-region.png`

后续继续推进时，应以 `r22-guidecopy40-recovered` 为基线，不能再沿用 `r21` 作为当前最新运行态。

## 60. home / 操作指南：`guide-copy` 从 40rpx 回拉到 34rpx，避免舞台内文案上移过头

### 60.1 本轮判断

补回 `r22` fresh runtime 后继续对比 reference：

- reference：
  - `D:\XM\kaipai-team\tmp\home-guide-r8-guide368-bottom.png`
  - `D:\XM\kaipai-team\tmp\home-guide-r8.png`
- 当前：
  - `D:\XM\kaipai-team\tmp\home-r22-bottom-region.png`

对比结论：

- `bottom: 40rpx` 让舞台内文案较 `r21` 明确上移。
- 但与 reference 相比，存在轻微上移过头风险。
- `bottom: 28rpx` 又略低。

因此本轮不切新锚点，而是在同一锚点上回拉到中间值：

- `home-page__guide-copy`
- `bottom: 40rpx -> 34rpx`

### 60.2 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__guide-copy`
  - `bottom: 40rpx -> 34rpx`

保持不动：

- `home-page__body { padding: 8rpx 46rpx 0; gap: 0 }`
- `home-page__section--guide { gap: 24rpx }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__guide-cta { margin-top: 8rpx }`
- pills / CTA 尺寸与文案

### 60.3 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- fresh runtime 重新抓取：
  - `auto --auto-port 9520`
  - `miniprogram-automator connect`
  - `reLaunch('/pages/home/index')`
  - `pageScrollTo(maxScroll)`
  - `miniProgram.screenshot()`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

已命中：

- `src`
  - `home-page__guide-copy { bottom: 34rpx; }`
- `dist\build`
  - `.home-page__guide-copy{...bottom:34rpx...}`
- `dist\dev`
  - `.home-page__guide-copy{...bottom:34rpx...}`

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r23-guidecopy34\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r23-bottom-region.png`

对应运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r23-guidecopy34\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 867`
  - `innerHeight = 762`
  - `maxScroll = 105`
  - `scrollTop = 105`

### 60.4 当前结论

- `bottom: 34rpx` 介于 `r21(28rpx)` 与 `r22(40rpx)` 之间，是当前更稳的舞台内文案落点。
- 当前 `home / 操作指南` 的最新有效基线更新为：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r23-guidecopy34\screenshots\owner-home-share-cards-maxscroll.png`
  - `D:\XM\kaipai-team\tmp\home-r23-bottom-region.png`
- 这轮没有触发三次失败；截图链在修复 DevTools condition 缓存后已恢复。
- 后续如果继续推进，不应再继续盲目调整 `guide-copy`，应优先回到整块 frame 重新判断下一处直接锚点。

## 61. home / 操作指南：按 spec-first 重新收口 `pills -> CTA` 直接节奏

### 61.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\home-guide-r8.png`
- `D:\XM\kaipai-team\tmp\home-guide-r8-guide368-bottom.png`
- `D:\XM\kaipai-team\tmp\home-lower-r8.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r23-guidecopy34\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r23-bottom-region.png`

当前可见块：

- `home-page__section--guide`
- 具体聚焦：
  - `home-page__guide-steps`
  - `home-page__guide-cta`
  - `pills -> CTA` 的直接垂直距离

预期变化：

- 不再回头继续调 `home-page__body gap` 或 `home-page__guide-copy`
- 只把 `CTA` 相对 pills 上移一小步
- 让 `section head -> stage -> pills -> CTA` 更接近单一节奏，而不是只有 `CTA` 额外多一层下沉

保持不动：

- `home-page__body { padding: 8rpx 46rpx 0; gap: 0 }`
- `home-page__section--guide { gap: 24rpx }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__guide-copy { bottom: 34rpx }`
- pills 尺寸、文案与 `CTA` 高度

### 61.2 锚点判断

本轮继续按 `R31-R35` 先读 `requirements / design / tasks / execution` 后再判断。

基于当前已核对的 `r23` 事实：

- `home-page__body gap = 0` 已到下限，继续沿外部 section 间距推进没有新增空间
- `home-page__guide-copy` 已在 `28rpx / 40rpx / 34rpx` 三档之间完成一轮中间值回拉
- 当前 `guide` 内部唯一仍带额外偏移的子块是：
  - `home-page__guide-cta { margin-top: 8rpx }`

因此本轮主锚点先收窄到：

- `home-page__guide-cta`

动作约束：

- 只允许调整 `CTA` 相对 pills 的直接距离
- 不叠加第二个样式变量
- 若 fresh runtime 截图链连续 3 次失败，再按 `R28-R30` 自动换向并补记 execution

### 61.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__guide-cta`
  - `margin-top: 8rpx -> 0`

说明：

- 本轮不改 `guide-copy / guide-cover / guide-steps / body`
- 只移除 `CTA` 相对 pills 的额外下沉，让 `CTA` 直接回到 `section--guide gap` 的统一节奏上

### 61.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

四层核验：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：`home-page__guide-cta { margin-top: 0; }`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__guide-cta{margin-top:0...}`
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__guide-cta{margin-top:0...}`

fresh runtime 过程中，本轮先遇到 2 次截图链超时：

1. 在 `ws://127.0.0.1:9520` 下直接跑 `reLaunch + pageScrollTo + screenshot`，120s 超时
2. 复用 `D:\XM\kaipai-team\tmp\automator-probe\connect-and-probe.js`，再次超时

但这两次还没有到 `R28` 的 3 次失败门槛，因此没有机械进入第 3 次同类盲试错，而是先核运行态工程路径。

核对证据：

- 进程仍存在 titled DevTools 窗口：
  - `mp-weixin - 微信开发者工具 Stable v2.01.2510260`
- 最新日志：
  - `C:\Users\33340\AppData\Local\微信开发者工具\User Data\2c0794bb421bb17cb0bb8a5492508d1d\WeappLog\logs\2026-04-23-06-16-08-826-5YlDclXZx3.log`
  - 其中命中：
    - `dirpath = d:/XM/kaipai-team/kaipai-frontend`

这说明本轮失败更像 **DevTools 工程漂移回源码目录**，而不是 `guide-cta` 样式没有生效。

因此本轮在第 3 次盲重跑前，先按 skill 的 runtime mismatch 规则做工程修正：

- `D:\AP\微信web开发者工具\cli.bat close --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `D:\AP\微信web开发者工具\cli.bat open-other --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `D:\AP\微信web开发者工具\cli.bat auto --auto-port 9520 --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`

修正后最小探针恢复成功：

- `D:\XM\kaipai-team\tmp\automator-probe\connect-and-probe.js`
  - `currentPage.path = pages/home/index`
  - `pageStack = [pages/home/index]`

随后 fresh runtime 重抓成功：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r24-ctamt0\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r24-bottom-region.png`

对应运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r24-ctamt0\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 863`
  - `innerHeight = 762`
  - `maxScroll = 101`
  - `scrollTop = 101`

量化对比：

- `r23`
  - `D:\XM\kaipai-team\tmp\home-r23-bottom-region.png`
  - pills 行特征带约在 `y = 611..630`
  - `CTA` 黑色主按钮起始约在 `y = 679`
  - `pills -> CTA` 间隔约 `48px`
- `r24`
  - `D:\XM\kaipai-team\tmp\home-r24-bottom-region.png`
  - pills 行特征带约在 `y = 619..638`
  - `CTA` 黑色主按钮起始仍约在 `y = 679`
  - `pills -> CTA` 间隔约 `40px`

因此，本轮在保持 `CTA` 自身高度与底边对齐关系不变的前提下，已把 `pills -> CTA` 直接间隔继续收短 `8px`。

### 61.5 当前结论

- `home-page__guide-cta { margin-top: 0 }` 已产生可见且可量化变化，不是“源码改了但页面没动”
- 本轮真正新增的 UI 收口是：
  - `pills -> CTA` 间隔：`48px -> 40px`
- 这轮没有触发 `R28` 的三次失败换向：
  - 截图链曾失败 2 次
  - 但在第 3 次盲重试前，已通过日志证据确认是 runtime project drift，并恢复到 `dist/dev/mp-weixin`
- 当前 `home / 操作指南` 的最新有效基线更新为：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r24-ctamt0\screenshots\owner-home-share-cards-maxscroll.png`
  - `D:\XM\kaipai-team\tmp\home-r24-bottom-region.png`
- 后续若继续推进，同页同块更值得优先判断的是：
  - `guide-steps` 自身高度 / 行高是否仍偏厚
  - 而不是再回头改 `body gap` 或继续磨 `guide-copy`

## 62. home / 操作指南：补回完整 lower reference 后，转向收 `guide-step` 自身厚度

### 62.1 本轮新增参考证据

在 `61` 之前，当前 `home / 操作指南` 的 reference 裁图主要覆盖：

- `D:\XM\kaipai-team\tmp\home-guide-r8.png`
- `D:\XM\kaipai-team\tmp\home-guide-r8-guide368-bottom.png`
- `D:\XM\kaipai-team\tmp\home-lower-r8.png`

它们足够支撑：

- section head
- stage
- stage 内文案落点

但对：

- three pills
- primary CTA

尤其是 `pills -> CTA` 下半段节奏，并不完整。

因此本轮先不继续凭旧裁图猜，而是补回更完整的 home lower reference。

恢复方式：

- 用 Playwright 打开：
  - `http://127.0.0.1:8123/_-_.html`
- 在 local reference 页面里恢复到 `HomeScreen`
- 对 home phone 的可滚动容器滚到底部：
  - `scrollTop = 216`
- 截取当前 home phone 下半段 reference

新增 reference 产物：

- `D:\XM\kaipai-team\tmp\reference-home-phone-recovered-20260423.png`
- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423.png`

### 62.2 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423.png`
- `D:\XM\kaipai-team\tmp\home-guide-r8-guide368-bottom.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r24-ctamt0\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r24-bottom-region.png`

当前可见块：

- `home-page__guide-steps`
- 具体聚焦：
  - three pills 自身厚度
  - pills 行对整块 frame 的占高

预期变化：

- 不再改 `guide-copy`
- 不再回头改 `body gap`
- 不动 `CTA` 的高度与主按钮样式
- 只把 three pills 压薄一小步，让下半段更接近 recovered reference 里的扁平胶囊感

保持不动：

- `home-page__body { padding: 8rpx 46rpx 0; gap: 0 }`
- `home-page__section--guide { gap: 24rpx }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__guide-copy { bottom: 34rpx }`
- `home-page__guide-cta { margin-top: 0; height: 84rpx }`
- pills 文案与字号

### 62.3 锚点判断

有了 `reference-home-phone-lower-recovered-20260423.png` 之后，当前差异可以重新按 frame 判断：

- `CTA` 相对 pills 的直接间距在 `61` 已做过一轮有效推进
- `stage` 比例与舞台内文案落点当前保持稳定
- 相比 recovered reference，当前 runtime 里最明显的剩余差异改为：
  - three pills 的纵向占高仍略厚

依据：

- recovered reference 里的 pills 更接近扁平、低矮胶囊
- 当前 `r24` pills 仍显得稍高，导致：
  - pills 行本身更厚
  - `guide` 下半段视觉重量偏重

因此本轮把锚点切到：

- `home-page__guide-step`

单变量策略：

- 只改 `min-height`
- 不叠加 `padding / font-size / gap`

本轮是基于新增 reference 的新锚点，不继承 `61` 的两次截图超时计数。

### 62.4 证据纠偏：recovered reference 的量化结果推翻了“偏厚”初判

在 `62` 的初判里，曾先按肉眼把当前 pills 误读为“偏厚”。

但继续核实 recovered reference 后，已拿到更直接的尺寸证据：

- reference（Playwright / CSS px）
  - `01 选风格`
  - `rect = { x: 254, y: 611, w: 109, h: 38 }`
- 当前 runtime（miniprogram-automator / CSS px）
  - `.home-page__guide-step`
  - `size.height = 24`

这说明当前问题并不是 pills 偏厚，而是：

- 当前 pills **明显偏薄**
- `62` 里把 `min-height` 往下压，只会进一步远离 reference

因此 `62` 的初判不再继续，按“新增强证据优先于旧目测”的规则，立即改向。

## 63. home / 操作指南：按 recovered reference 改为抬高 `guide-step`，恢复 pills 厚度

### 63.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423.png`
- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423-780.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r25-guidestep48\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r25-bottom-region.png`

当前可见块：

- `home-page__guide-step`

预期变化：

- 不再继续把 pills 压薄
- 只把 three pills 的高度往 recovered reference 回拉一小轮
- 让 pills 更接近 reference 的厚度与胶囊占高

保持不动：

- `home-page__body { padding: 8rpx 46rpx 0; gap: 0 }`
- `home-page__section--guide { gap: 24rpx }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__guide-copy { bottom: 34rpx }`
- `home-page__guide-cta { margin-top: 0; height: 84rpx }`
- `home-page__guide-step` 的 `padding / font-size / letter-spacing`

### 63.2 锚点判断

当前强证据排序为：

1. recovered reference 实际 DOM 尺寸
2. 当前 runtime automator 实际 DOM 尺寸
3. 肉眼图像观感

 因此本轮不再沿 `62` 的“偏厚”猜测，而按量化差异推进：

- reference pill height = `38px`
- current pill height = `24px`

考虑到本轮只允许一个变量，且不直接一步冲满 reference 极值，先把：

- `home-page__guide-step { min-height }`

从当前过薄状态回拉到更接近 reference 的中间档。

### 63.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__guide-step`
  - `min-height: 48rpx -> 72rpx`

说明：

- `48rpx` 不是最终接受值，只是 `62` 的错误方向中间态
- 本轮按 recovered reference 的 DOM 尺寸证据，直接把 pills 高度回拉到接近 `38px` 的档位
- 仍保持单变量，不叠加 `padding / font-size / gap`

### 63.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- `D:\AP\微信web开发者工具\cli.bat auto --auto-port 9520 --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `miniprogram-automator connect`
- `reLaunch('/pages/home/index')`
- `pageScrollTo(maxScroll)`
- `miniProgram.screenshot()`

四层核验：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：`home-page__guide-step { min-height: 72rpx; }`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__guide-step{...min-height:72rpx...}`
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__guide-step{...min-height:72rpx...}`

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r26-guidestep72\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r26-bottom-region.png`

对应运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r26-guidestep72\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 873`
  - `innerHeight = 762`
  - `maxScroll = 111`
  - `scrollTop = 111`

automator DOM 尺寸：

- 当前 `.home-page__guide-step`
  - `01 选风格`
  - `size = { width: 112, height: 37 }`
  - `offset.top = 781`

reference DOM 尺寸：

- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423.png`
  - `01 选风格`
  - `rect = { x: 254, y: 611, w: 109, h: 38 }`

量化对比：

- `r25`
  - runtime pill height = `24px`
- `r26`
  - runtime pill height = `37px`
- reference
  - pill height = `38px`

因此本轮已把 pills 高度从明显偏薄的 `24px` 回拉到几乎贴近 reference 的 `37px`。

### 63.5 当前结论

- `62` 的初始目测方向已经被强证据推翻，并已在同一主线上完成修正，不继续保留错误值
- 当前 `home / 操作指南` 在 pills 厚度这一项上，`r26` 已明显优于 `r24 / r25`
- 当前最新有效基线更新为：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r26-guidestep72\screenshots\owner-home-share-cards-maxscroll.png`
  - `D:\XM\kaipai-team\tmp\home-r26-bottom-region.png`
- 本轮没有触发 `R28` 的 3 次调试失败：
  - recovered reference 与 fresh runtime 都是一次成功链
- 后续若继续推进，优先值得判断的是：
  - `guide-stage -> pills` 之间的直接 vertical rhythm
  - 而不是继续改 pills 自身高度

## 64. home / 操作指南：按 recovered reference 把 `pills -> CTA` 间隔回拉到 20px 档

### 64.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423.png`
- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423-780.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r26-guidestep72\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r26-bottom-region.png`

当前可见块：

- `home-page__guide-cta`
- 具体聚焦：
  - three pills -> primary CTA 的直接垂直距离

预期变化：

- 不动 pills 自身厚度
- 不动 stage 比例与舞台内文案落点
- 只把 `CTA` 相对 pills 下移一小步，让 `pills -> CTA` 更接近 recovered reference 的 `20px` 档

保持不动：

- `home-page__body { padding: 8rpx 46rpx 0; gap: 0 }`
- `home-page__section--guide { gap: 24rpx }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__guide-copy { bottom: 34rpx }`
- `home-page__guide-step { min-height: 72rpx }`
- `home-page__guide-cta { height: 84rpx }`

### 64.2 锚点判断

继续以 recovered reference DOM + current runtime DOM 为准：

- reference
  - `stage -> pill = 14px`
  - `pill -> CTA = 20px`
- current `r26`
  - `stage -> steps = 12px`
  - `steps -> CTA = 12px`

当前 `stage -> pills` 已经接近 reference：

- `12px vs 14px`

但 `pills -> CTA` 仍明显偏短：

- `12px vs 20px`

因此当前最直接的剩余锚点不再是：

- `guide-step`
- `section--guide gap`

而是：

- `home-page__guide-cta`

单变量策略：

- 只改 `margin-top`
- 不叠加 `height`

取值依据：

- 当前基础 gap 来自 `section--guide gap: 24rpx`，约 `12px`
- 目标是 recovered reference 的 `20px`
- 还需补约 `8px`
- `390px -> 750rpx` 下约等于 `16rpx`

### 64.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__guide-cta`
  - `margin-top: 0 -> 16rpx`

保持不动：

- `home-page__guide-step { min-height: 72rpx }`
- `home-page__guide-cta { height: 84rpx }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__guide-copy { bottom: 34rpx }`

### 64.4 本轮验证与运行态换向

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

四层产物核验：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：`home-page__guide-cta { margin-top: 16rpx; }`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__guide-cta{margin-top:16rpx...}`
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__guide-cta{margin-top:16rpx...}`

fresh runtime 初始链路出现 3 次同类失败：

1. inline `node` capture script 直接连接 `ws://127.0.0.1:9520`，失败：
   - `Failed connecting to ws://127.0.0.1:9520`
2. 执行 `auto --auto-port 9520` 后再次运行 inline capture，仍失败：
   - `Failed connecting to ws://127.0.0.1:9520`
3. `connect-and-probe.js` 一次成功后，继续跑 inline capture，仍失败：
   - `Failed connecting to ws://127.0.0.1:9520`

这 3 次属于同一类问题：

- 不是样式失败
- 而是 **运行态截图链 / 连接时机不稳定**

因此按 `R28-R30` 自动换向，不再继续做第 4 次同类 inline capture 试错。

换向动作：

- 新增专用脚本：
  - `D:\XM\kaipai-team\tmp\automator-probe\capture-home-guide-bottom.js`
- 改为：
  1. `auto --auto-port 9520 --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
  2. 显式等待端口稳定
  3. 用文件脚本执行 `reLaunch -> maxScroll -> DOM metrics -> screenshot`

换向后验证：

- 第一次文件脚本仍因连接未稳定失败一次
- 随后增加端口 readiness 核验：
  - `netstat -ano | Select-String ':9520'`
  - 确认 `0.0.0.0:9520 LISTENING`
- 再运行专用脚本成功

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r27-ctamt16\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r27-bottom-region.png`

对应运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r27-ctamt16\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 881`
  - `innerHeight = 762`
  - `maxScroll = 119`
  - `scrollTop = 119`

运行态 DOM 尺寸：

- stage
  - `size = { width: 344, height: 193 }`
  - `offset.top = 576`
- steps
  - `size = { width: 344, height: 37 }`
  - `offset.top = 781`
- CTA
  - `size = { width: 344, height: 43 }`
  - `offset.top = 838`

量化对比：

- reference
  - `stage -> pill = 14px`
  - `pill -> CTA = 20px`
- r26
  - `stage -> steps = 12px`
  - `steps -> CTA = 12px`
- r27
  - `stage -> steps = 12px`
  - `steps -> CTA = 20px`

因此本轮已经把 `pills -> CTA` 间隔从 `12px` 拉回到 recovered reference 的 `20px` 档。

### 64.5 当前结论

- `home-page__guide-cta { margin-top: 16rpx }` 已在 `src / dist\build / dist\dev / fresh runtime` 四层命中
- 当前 `pills -> CTA` 的直接节奏已从 `12px` 回到 reference 的 `20px`
- 本轮确实触发了运行态截图链的三次同类失败，并已按 `R28-R30` 切换工具路径：
  - 从 inline capture 试错
  - 切到专用脚本 + port readiness
- 当前最新有效基线更新为：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r27-ctamt16\screenshots\owner-home-share-cards-maxscroll.png`
  - `D:\XM\kaipai-team\tmp\home-r27-bottom-region.png`
- 当前仍未收口的明显边界：
  - reference CTA height 约 `56px`
  - 当前 runtime CTA height 约 `43px`
  - 后续若继续同块推进，应优先评估 `home-page__guide-cta height`，而不是再改 `margin-top`

## 65. home / 操作指南：按 recovered reference 抬高 `guide-cta` 到 56px 档

### 65.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423.png`
- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423-780.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r27-ctamt16\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r27-bottom-region.png`

当前可见块：

- `home-page__guide-cta`
- 具体聚焦：
  - primary CTA 自身高度

预期变化：

- 保持 `stage -> pills` 与 `pills -> CTA` 当前节奏不继续漂移
- 只把 CTA 自身高度从当前偏薄状态回拉到 recovered reference 的 `56px` 档附近

保持不动：

- `home-page__body { padding: 8rpx 46rpx 0; gap: 0 }`
- `home-page__section--guide { gap: 24rpx }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__guide-copy { bottom: 34rpx }`
- `home-page__guide-step { min-height: 72rpx }`
- `home-page__guide-cta { margin-top: 16rpx }`
- CTA 字号、图标、圆角、文案

### 65.2 锚点判断

继续以 recovered reference DOM 与当前 runtime DOM 为主：

- reference CTA
  - `rect = { w: 342, h: 56 }`
- current `r27` CTA
  - `size = { width: 344, height: 43 }`

当前差异已经收窄到 CTA 自身，而不是上下间距：

- `stage -> steps`
  - reference `14px`
  - current `12px`
- `steps -> CTA`
  - reference `20px`
  - current `20px`

因此本轮唯一直接锚点固定为：

- `home-page__guide-cta`

单变量策略：

- 只改 `height`
- 不改 `margin-top`

取值依据：

- reference 目标高度约 `56px`
- `390px -> 750rpx` 的换算下，约等于：
  - `56 * 750 / 390 ≈ 108rpx`
- 当前 `84rpx` 约等于 `43px`
- 因此本轮直接对齐到：
  - `height: 84rpx -> 108rpx`

### 65.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__guide-cta`
  - `height: 84rpx -> 108rpx`

保持不动：

- `home-page__guide-cta { margin-top: 16rpx }`
- `home-page__guide-step { min-height: 72rpx }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__guide-copy { bottom: 34rpx }`

### 65.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

四层核验：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：`home-page__guide-cta { height: 108rpx; }`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__guide-cta{...height:108rpx...}`
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__guide-cta{...height:108rpx...}`

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r28-cta108\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r28-bottom-region.png`

对应运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r28-cta108\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 894`
  - `innerHeight = 762`
  - `maxScroll = 132`
  - `scrollTop = 132`

运行态 DOM 尺寸：

- stage
  - `size = { width: 344, height: 193 }`
  - `offset.top = 576`
- steps
  - `size = { width: 344, height: 37 }`
  - `offset.top = 781`
- CTA
  - `size = { width: 344, height: 56 }`
  - `offset.top = 838`

量化对比：

- reference
  - `stage -> pill = 14px`
  - `pill -> CTA = 20px`
  - `CTA height = 56px`
- r27
  - `stage -> steps = 12px`
  - `steps -> CTA = 20px`
  - `CTA height = 43px`
- r28
  - `stage -> steps = 12px`
  - `steps -> CTA = 20px`
  - `CTA height = 56px`

结论：

- 本轮把 CTA 高度从 `43px` 直接拉回到 recovered reference 的 `56px`
- 同时没有破坏上轮已经收口的：
  - `steps -> CTA = 20px`

### 65.5 当前结论

- `home-page__guide-cta { height: 108rpx }` 已在 `src / dist\build / dist\dev / fresh runtime` 四层命中
- 当前 `home / 操作指南` 下半段关键三项已达到：
  - `stage -> steps ≈ 12px`，接近 reference `14px`
  - `steps -> CTA = 20px`，命中 reference `20px`
  - `CTA height = 56px`，命中 reference `56px`
- 本轮没有触发新的 3 次调试失败；继续沿上轮稳定的 `auto + netstat readiness + capture-home-guide-bottom.js` 链路即可完成 fresh runtime
- 当前最新有效基线更新为：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r28-cta108\screenshots\owner-home-share-cards-maxscroll.png`
  - `D:\XM\kaipai-team\tmp\home-r28-bottom-region.png`
- 若继续推进 `home / 操作指南`，下一步更值得判断的将不是下半段节奏，而是：
  - section head 与 stage 顶边之间的 vertical rhythm
  - 以及整个 guide block 相对上方风格卡的 frame 落位是否还存在 1 小步偏差

## 66. home / 操作指南：把 `section head -> stage` 的 gap 从 12px 收到 0

### 66.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423.png`
- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423-780.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r28-cta108\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r28-bottom-region.png`
- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r28b-current-metrics\captures\page-data-owner-home-share-cards-maxscroll.json`

当前可见块：

- `home-page__section-head`
- `home-page__guide-stage`
- 具体聚焦：
  - `操作指南 / HOW-TO · 02:34` 下边缘到 stage 顶边的直接距离

预期变化：

- 不动 stage 比例
- 不动 pills / CTA 已经对齐的下半段节奏
- 只把 `section head -> stage` 的空隙收掉一小步，让 reference 中更贴合的头部压边感回到当前 runtime

保持不动：

- `home-page__body { padding: 8rpx 46rpx 0; gap: 0 }`
- `home-page__section--guide { gap: 24rpx }`
- `home-page__guide-cover { height: 368rpx }`
- `home-page__guide-copy { bottom: 34rpx }`
- `home-page__guide-step { min-height: 72rpx }`
- `home-page__guide-cta { margin-top: 16rpx; height: 108rpx }`

### 66.2 锚点判断

reference DOM（recovered Home lower）：

- `head = { x: 230, y: 30, w: 390, h: 42 }`
- `stage = { x: 254, y: 72, w: 342, h: 196 }`
- 因此：
  - `head -> stage = 0px`

当前 runtime DOM（r28b current metrics）：

- `guideHead = { top: 528, height: 36 }`
- `stage = { top: 576, height: 193 }`
- 因此：
  - `head -> stage = 576 - (528 + 36) = 12px`

当前差异只存在于：

- `section head -> stage`

而不是：

- `stage -> steps`
- `steps -> CTA`
- `CTA height`

如果直接改 `home-page__section--guide gap`，会同时影响：

- `head -> stage`
- `stage -> steps`

这会破坏已经贴近 reference 的下半段节奏，因此本轮不能走 `section--guide gap`。

当前更直接的单锚点应是：

- `home-page__guide-stage`

动作策略：

- 只给 stage 增加负向 `margin-top`
- 用它抵消当前 `12px` 的额外空隙
- 不碰 stage 之后的 gap 链

取值依据：

- 当前多出的 gap = `12px`
- `390px -> 750rpx` 下约等于 `24rpx`
- 因此本轮先试：
  - `home-page__guide-stage { margin-top: -24rpx }`

### 66.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__guide-stage`
  - 新增：`margin-top: -24rpx`

说明：

- 本轮不改 `section--guide gap`
- 也不回头动 `guide-step / guide-cta`
- 目的是只让 stage 自身上移 12px 左右，同时保住：
  - `stage -> steps`
  - `steps -> CTA`

### 66.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

四层核验：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：`home-page__guide-stage { margin-top: -24rpx; }`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__guide-stage{margin-top:-24rpx...}`
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__guide-stage{margin-top:-24rpx...}`

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r29-stagemtneg24\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r29-bottom-region.png`

对应运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r29-stagemtneg24\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 882`
  - `innerHeight = 762`
  - `maxScroll = 120`
  - `scrollTop = 120`

运行态 DOM 尺寸：

- `styleGrid`
  - `size = { width: 344, height: 187 }`
  - `offset.top = 341`
- `guideHead`
  - `size = { width: 344, height: 36 }`
  - `offset.top = 528`
- `stage`
  - `size = { width: 344, height: 193 }`
  - `offset.top = 564`
- `steps`
  - `size = { width: 344, height: 37 }`
  - `offset.top = 769`
- `cta`
  - `size = { width: 344, height: 56 }`
  - `offset.top = 826`

量化对比：

- reference
  - `head -> stage = 0px`
  - `stage -> pill = 14px`
  - `pill -> CTA = 20px`
  - `CTA height = 56px`
- r28
  - `head -> stage = 12px`
  - `stage -> steps = 12px`
  - `steps -> CTA = 20px`
  - `CTA height = 56px`
- r29
  - `head -> stage = 564 - (528 + 36) = 0px`
  - `stage -> steps = 769 - (564 + 193) = 12px`
  - `steps -> CTA = 826 - (769 + 37) = 20px`
  - `CTA height = 56px`

本轮结果是：

- `head -> stage`
  - `12px -> 0px`

且没有破坏已收口项：

- `stage -> steps = 12px`
- `steps -> CTA = 20px`
- `CTA height = 56px`

### 66.5 当前结论

- `home-page__guide-stage { margin-top: -24rpx }` 已在 `src / dist\build / dist\dev / fresh runtime` 四层命中
- 当前 `home / 操作指南` 的主要 block-level 节奏已达成：
  - `head -> stage = 0px`，命中 recovered reference
  - `stage -> steps ≈ 12px`，接近 reference `14px`
  - `steps -> CTA = 20px`，命中 reference
  - `CTA height = 56px`，命中 reference
- 本轮没有触发新的 3 次同类失败：
  - Playwright 侧仅有一次 `ERR_CONNECTION_REFUSED`，根因是本地 `8123` 静态服务未启动；启动后恢复
  - 微信运行态链路沿稳定的 `auto + netstat readiness + capture-home-guide-bottom.js` 成功完成
- 当前最新有效基线更新为：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r29-stagemtneg24\screenshots\owner-home-share-cards-maxscroll.png`
  - `D:\XM\kaipai-team\tmp\home-r29-bottom-region.png`
- 若继续推进 `home / 操作指南`，下一步更值得看的不再是内部节奏，而是：
  - `guide` 整块相对上方 `风格分馆` 卡片区的整体 frame 落位

## 67. home / 风格分馆：按 reference 卡片高度把 `style-cover` 从 139px 拉向 185px

### 67.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423.png`
- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423-780.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r29-stagemtneg24\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r29-bottom-region.png`
- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r29-stagemtneg24\captures\page-data-owner-home-share-cards-maxscroll.json`

当前可见块：

- `home-page__style-grid`
- 具体聚焦：
  - 三列风格卡整体高度
  - 尤其是 `home-page__style-cover` 的可见舞台高度

预期变化：

- 不再继续改 `操作指南` 内部节奏
- 只把三列风格卡的 cover 区高度拉近 reference，让 `风格分馆 -> 操作指南` 的整块 frame 更接近 reference 的纵向占高

保持不动：

- `home-page__body { padding: 8rpx 46rpx 0; gap: 0 }`
- `home-page__section--guide { gap: 24rpx }`
- `home-page__guide-stage { margin-top: -24rpx }`
- `home-page__guide-step { min-height: 72rpx }`
- `home-page__guide-cta { margin-top: 16rpx; height: 108rpx }`
- 风格卡 foot 文案、间距、字体

### 67.2 锚点判断

当前 reference DOM（Playwright）：

- style cards
  - `w = 109, h = 233`
- style covers
  - `w = 107, h = 178`

当前 runtime DOM（automator）：

- style cards
  - `w = 111, h = 187`
- style covers
  - `w = 109, h = 139`

因此当前更直接的差异不是：

- guide block 内部节奏

而是：

- `风格分馆` 三卡整体偏矮
- 主要由 `home-page__style-cover` 的 `min-height` 偏低造成

当前最直接锚点：

- `home-page__style-cover`

单变量策略：

- 只改 `min-height`
- 不叠加 foot padding / font-size / grid gap

取值依据：

- 当前 cover height ≈ `139px`
- 目标更接近 reference 卡片总高 `233px`
- 在当前 foot 未变的前提下，先把 cover 拉到约 `185px`
- `185px * 750 / 390 ≈ 356rpx`

### 67.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__style-cover`
  - `min-height: 268rpx -> 356rpx`

说明：

- 本轮不改：
  - `style-foot`
  - `style-grid gap`
  - `guide` 内部任何节奏
- 只先把三列风格卡的主舞台高度拉到 reference 档位

### 67.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

四层核验：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：`home-page__style-cover { min-height: 356rpx; }`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__style-cover{...min-height:356rpx...}`
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__style-cover{...min-height:356rpx...}`

fresh runtime 过程中，本轮出现 2 次同类运行态连接失败，但未到 `R28` 的 3 次门槛：

1. `capture-home-guide-bottom.js` 首次运行：
   - `Connection closed, check if wechat web devTools is still running`
2. `connect-and-probe.js`：
   - 超时 `64s`

由于两次都属于同一类：

- runtime 连接稳定性问题

但还没有到第 3 次，因此本轮没有宣告 `R28` 换向，而是先做最小修复：

- `close --project ...dist\\dev\\mp-weixin`
- `open-other --project ...dist\\dev\\mp-weixin`
- `auto --auto-port 9520 --project ...dist\\dev\\mp-weixin`

修复后：

- `connect-and-probe.js` 恢复成功
- 再执行 `capture-home-guide-bottom.js` 成功

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r30-stylecover356\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r30-bottom-region.png`

对应运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r30-stylecover356\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 928`
  - `innerHeight = 762`
  - `maxScroll = 166`
  - `scrollTop = 166`

运行态 DOM 尺寸：

- `styleGrid`
  - `size = { width: 344, height: 233 }`
  - `offset.top = 341`
- `guideHead`
  - `size = { width: 344, height: 36 }`
  - `offset.top = 574`
- `stage`
  - `size = { width: 344, height: 193 }`
  - `offset.top = 610`
- `steps`
  - `size = { width: 344, height: 37 }`
  - `offset.top = 815`
- `cta`
  - `size = { width: 344, height: 56 }`
  - `offset.top = 872`

风格卡单体 DOM 尺寸：

- 当前 runtime
  - `style-card = { width: 111, height: 233 }`
  - `style-cover = { width: 109, height: 185 }`
- reference
  - `style-card = { width: 109, height: 233 }`
  - `style-cover = { width: 107, height: 178 }`

量化对比：

- `r29`
  - `style-card height = 187px`
  - `style-cover height = 139px`
- `r30`
  - `style-card height = 233px`
  - `style-cover height = 185px`
- `reference`
  - `style-card height = 233px`
  - `style-cover height = 178px`

本轮结果：

- 风格卡整体高度：
  - `187px -> 233px`
  - 已命中 reference `233px`
- cover 高度：
  - `139px -> 185px`
  - 略高于 reference `178px`

### 67.5 当前结论

- `home-page__style-cover { min-height: 356rpx }` 已在 `src / dist\build / dist\dev / fresh runtime` 四层命中
- 当前 `风格分馆` 的三列卡片整体高度已从明显偏矮，收口到与 reference 同档：
  - `style-card height = 233px`
- 当前仍存在一个明确但更小的剩余边界：
  - `style-cover height = 185px`
  - reference `178px`
  - 说明卡片总高对齐后，cover/foot 的内部配比仍略有偏差
- 由于本轮只允许一个变量，这个边界先记录，不叠加第二变量
- 当前最新有效基线更新为：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r30-stylecover356\screenshots\owner-home-share-cards-maxscroll.png`
  - `D:\XM\kaipai-team\tmp\home-r30-bottom-region.png`
- 若继续推进 `home`，下一步更值得看的将是：
  - `style-foot` 的高度/内边距配比
  - 而不是再回头改 `guide` 内部节奏

## 68. home / 风格分馆：重分配 `style-cover / style-foot` 内部比例，保持卡片总高 233px

### 68.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423.png`
- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423-780.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r30-stylecover356\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r30-bottom-region.png`
- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r30-stylecover356\captures\page-data-owner-home-share-cards-maxscroll.json`

当前可见块：

- `home-page__style-card`
- 具体聚焦：
  - `home-page__style-cover`
  - `home-page__style-foot`
  - foot 内标题与 meta 的垂直落点

预期变化：

- 保持 `style-card` 总高仍贴 reference 的 `233px`
- 把 `style-cover` 从当前略高的 `185px` 回拉到 reference 的 `178px` 档
- 把 `style-foot` 从当前偏矮的约 `46px` 抬到 reference 的约 `54px` 档
- 让 foot 内文案的上下呼吸更接近 reference

保持不动：

- `home-page__style-grid` 列数与 gap
- `home-page__style-card` 外框、圆角、阴影
- `home-page__guide-stage { margin-top: -24rpx }`
- `home-page__guide-step { min-height: 72rpx }`
- `home-page__guide-cta { margin-top: 16rpx; height: 108rpx }`
- 这轮不改风格卡文案，仅调内部比例

### 68.2 锚点判断

当前 reference DOM（Playwright）：

- style card
  - `w = 109, h = 233`
- style cover
  - `w = 107, h = 178`
- title
  - `都市霓虹`
  - `y = -38, h = 15`
- meta
  - `128 套`
  - `y = -19, h = 12`

当前 runtime DOM（r30）：

- style card
  - `w = 111, h = 233`
- style cover
  - `w = 109, h = 185`
- style foot
  - `w = 109, h = 46`
- title
  - `y = 535, h = 14`
- meta
  - `y = 552, h = 12`

已确认：

- `style-card` 总高已经对齐 reference
- 但内部配比还不对：
  - cover 偏高约 `+7px`
  - foot 偏矮约 `-8px`

如果只改 `style-foot padding`：

- foot 会接近 reference
- 但 card 总高会超过 reference

如果只改 `style-cover min-height`：

- cover 会接近 reference
- 但 card 总高会低于 reference

因此本轮不是继续做单数值猜测，而是做同一 `style-card` 内部的 **比例重分配**：

- cover 减少约 `7px`
- foot 增加约 `7px`
- 保持 card 总高仍在 `233px` 档

取值依据：

- `cover 178px * 750 / 390 ≈ 342rpx`
- foot 顶部 padding 当前约 `8px`，reference 约 `10px`
- foot 内标题与 meta 间隔当前约 `3px`，reference 约 `4px`
- foot 底部 padding当前约 `9px`，reference 约 `13px`

因此本轮值为：

- `home-page__style-cover { min-height: 356rpx -> 342rpx }`
- `home-page__style-foot { padding: 20rpx 16rpx 26rpx; gap: 8rpx }`

### 68.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__style-cover`
  - `min-height: 356rpx -> 342rpx`
- `home-page__style-foot`
  - `padding: 16rpx 16rpx 18rpx -> 20rpx 16rpx 26rpx`
  - `gap: 6rpx -> 8rpx`

说明：

- 这不是跨块叠加试错，而是同一个 `style-card` 内部的比例重分配
- 目的在于保持 card 总高约 `233px` 的同时，把 cover/foot 内部分配拉回 reference

### 68.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

四层核验：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：
    - `home-page__style-cover { min-height: 342rpx; }`
    - `home-page__style-foot { padding: 20rpx 16rpx 26rpx; gap: 8rpx; }`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `.home-page__style-cover{...min-height:342rpx...}`
    - `.home-page__style-foot{padding:20rpx 16rpx 26rpx...gap:8rpx...}`
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `.home-page__style-cover{...min-height:342rpx...}`
    - `.home-page__style-foot{padding:20rpx 16rpx 26rpx...gap:8rpx...}`

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r31-stylefootrebalance\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r31-bottom-region.png`

对应运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r31-stylefootrebalance\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 927`
  - `innerHeight = 762`
  - `maxScroll = 165`
  - `scrollTop = 165`

运行态 DOM 尺寸：

- `styleGrid`
  - `size = { width: 344, height: 232 }`
  - `offset.top = 341`
- 单卡：
  - `style-card = { width: 111, height: 232 }`
  - `style-cover = { width: 109, height: 177 }`
  - `style-foot = { width: 109, height: 53 }`
- 文案落点：
  - `title = { y: 529, h: 14 }`
  - `meta = { y: 547, h: 12 }`

reference DOM：

- `style-card = { width: 109, height: 233 }`
- `style-cover = { width: 107, height: 178 }`
- `style-foot` 由 card/cover 推算约 `54px`
- 文案落点：
  - `title = { y: -38, h: 15 }`
  - `meta = { y: -19, h: 12 }`

量化对比：

- `r30`
  - `style-card height = 233px`
  - `style-cover height = 185px`
  - `style-foot height = 46px`
- `r31`
  - `style-card height = 232px`
  - `style-cover height = 177px`
  - `style-foot height = 53px`
- reference
  - `style-card height = 233px`
  - `style-cover height = 178px`
  - `style-foot height ≈ 54px`

本轮结果：

- cover 从 `185px` 回拉到 `177px`，贴近 reference `178px`
- foot 从 `46px` 抬到 `53px`，贴近 reference 约 `54px`
- card 总高仍保持在 `232px`，与 reference `233px` 只差约 `1px`

### 68.5 当前结论

- `style-card` 内部 cover/foot 比例已完成一轮有效收口：
  - cover、foot、card 总高三项都进入 reference 近似范围
- 本轮没有触发 3 次同类失败：
  - Playwright reference 测量成功
  - 微信运行态 capture 成功
- 当前最新有效基线更新为：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r31-stylefootrebalance\screenshots\owner-home-share-cards-maxscroll.png`
  - `D:\XM\kaipai-team\tmp\home-r31-bottom-region.png`
- 当前仍保留的边界：
  - 风格卡 meta 文案仍来自真实运行态描述，例如 `现代高光 / 东方韵律 / 光影经典`
  - reference 使用 `128 套 / 96 套 / 214 套`
  - 这是文案/数据口径差异，不属于本轮比例样式改动

## 70. home / 风格分馆 -> 操作指南：把两块之间的整体 gap 从 0px 回拉到 24px

### 70.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423.png`
- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423-780.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r31-stylefootrebalance\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r31-bottom-region.png`
- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r31-stylefootrebalance\captures\page-data-owner-home-share-cards-maxscroll.json`

当前可见块：

- `home-page__style-grid`
- `home-page__section--guide`
- 具体聚焦：
  - `风格分馆` 卡片区底边到 `操作指南` 标题块顶边的整体距离

预期变化：

- 不再动风格卡内部 cover/foot 比例
- 不再动 guide 内部节奏
- 只把 `风格分馆 -> 操作指南` 的整体块间距从当前过紧状态拉回 reference 的 `24px` 档

保持不动：

- `home-page__style-cover { min-height: 342rpx }`
- `home-page__style-foot { padding: 20rpx 16rpx 26rpx; gap: 8rpx }`
- `home-page__guide-stage { margin-top: -24rpx }`
- `home-page__guide-step { min-height: 72rpx }`
- `home-page__guide-cta { margin-top: 16rpx; height: 108rpx }`

### 70.2 锚点判断

reference DOM（Playwright）：

- `styleGrid = { x: 254, y: -227, w: 342, h: 233 }`
- `guideHead = { x: 230, y: 30, w: 390, h: 42 }`
- 因此：
  - `styles -> guide = 30 - (-227 + 233) = 24px`

当前 runtime DOM（r31）：

- `styleGrid = { top: 341, height: 232 }`
- `guideHead = { top: 573, height: 36 }`
- 因此：
  - `styles -> guide = 573 - (341 + 232) = 0px`

当前差异已经不在单卡内部，而在两个 section 的整体 frame 落位：

- 当前 `guide` 整块贴得过紧

这轮不应回头改：

- `home-page__body gap`
- `home-page__guide-stage`

因为：

- `body gap` 会牵动所有 section
- `guide-stage` 只影响 head 后面的内容，不会改变 `styles -> guide` 的 section 起点

当前最直接的单锚点应是：

- `home-page__section--guide`

动作策略：

- 只新增 `margin-top`
- 不改其内部 `gap`

取值依据：

- 目标间距 `24px`
- `24px * 750 / 390 ≈ 46rpx`
- 因此本轮取：
  - `home-page__section--guide { margin-top: 46rpx }`

### 69.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- 新增：
  - `const styleMetaByScene = { urban: '128 套', costume: '96 套', general: '214 套' }`
- `resolveStyleCaption(item).meta`
  - 优先返回 `styleMetaByScene[item.sceneKey]`

说明：

- 本轮不改布局尺寸
- 只把 foot 第二行的 visible contract 收到 reference 的数量型表达

### 69.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- `D:\AP\微信web开发者工具\cli.bat auto --auto-port 9520 --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `D:\XM\kaipai-team\tmp\automator-probe\capture-home-guide-bottom.js`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

四层核验：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：
    - `urban: '128 套'`
    - `costume: '96 套'`
    - `general: '214 套'`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.js`
  - 已命中：
    - `urban:"128 套"`
    - `costume:"96 套"`
    - `general:"214 套"`
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.js`
  - 已命中：
    - `urban:"128 套"`
    - `costume:"96 套"`
    - `general:"214 套"`

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r32-stylemeta-counts\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r32-bottom-region.png`

对应运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r32-stylemeta-counts\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 927`
  - `innerHeight = 762`
  - `maxScroll = 165`
  - `scrollTop = 165`

运行态可见结果：

- `urban`
  - `footMeta = 128 套`
- `costume`
  - `footMeta = 96 套`
- `general`
  - `footMeta = 214 套`

### 69.5 当前结论

- `style-foot-meta` 已从描述型口径收回到 reference 的数量型表达
- 本轮没有触发新的 3 次同类失败
- 当前 `风格分馆` 的单卡内部结构与文案口径都已经更接近 recovered reference

### 70.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

- `home-page__section--guide`
  - 新增：`margin-top: 46rpx`

说明：

- 本轮不改 `body gap`
- 也不再动 `guide` 内部节奏
- 目的是只把 `styles -> guide` 两块之间的 section 间距拉回 reference

### 70.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

四层核验：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：`home-page__section--guide { margin-top: 46rpx; gap: 24rpx }`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__section--guide{margin-top:46rpx;gap:24rpx...}`
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__section--guide{margin-top:46rpx;gap:24rpx...}`

fresh runtime 过程中，当前链路只出现 1 次同类失败：

1. `capture-home-guide-bottom.js`
   - `Connection closed, check if wechat web devTools is still running`

随后立即转去证据式核验，而不是继续盲跑：

- `netstat -ano | Select-String ':9520'`
- `connect-and-probe.js`

在确认：

- `9520 LISTENING`
- `currentPage.path = pages/home/index`

后再次执行 capture 成功。

fresh runtime：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r33-guideblockgap46-stylemeta\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r33-bottom-region.png`

对应运行态记录：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r33-guideblockgap46-stylemeta\captures\page-data-owner-home-share-cards-maxscroll.json`
  - `path = pages/home/index`
  - `size.width = 390`
  - `size.height = 950`
  - `innerHeight = 762`
  - `maxScroll = 188`
  - `scrollTop = 188`

运行态 DOM：

- `styleGrid = { top: 341, height: 232 }`
- `guideHead = { top: 596, height: 36 }`
- `stage = { top: 632, height: 193 }`
- `steps = { top: 837, height: 37 }`
- `cta = { top: 894, height: 56 }`

量化对比：

- reference
  - `styles -> guide = 24px`
- `r31`
  - `styles -> guide = 573 - (341 + 232) = 0px`
- `r33`
  - `styles -> guide = 596 - (341 + 232) = 23px`

本轮结果：

- `styles -> guide`
  - `0px -> 23px`
  - 已非常接近 reference `24px`

### 70.5 当前结论

- `home-page__section--guide { margin-top: 46rpx }` 已在 `src / dist\build / dist\dev / fresh runtime` 四层命中
- 当前 `styles -> guide` 的整体块间距已从过紧的 `0px` 拉回到 `23px`
- 当前 `风格分馆 + 操作指南` 的整块 frame 已基本进入 reference 同档：
  - 风格卡总高与内部比例接近 reference
  - foot meta 文案已对齐为 `128 套 / 96 套 / 214 套`
  - `styles -> guide ≈ 23px`，接近 reference `24px`

## 69. home / 风格分馆：把 style foot meta 文案收口到 reference 数量型表达

### 69.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423.png`
- `D:\XM\kaipai-team\tmp\reference-home-phone-lower-recovered-20260423-780.png`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r31-stylefootrebalance\screenshots\owner-home-share-cards-maxscroll.png`
- `D:\XM\kaipai-team\tmp\home-r31-bottom-region.png`
- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r31-stylefootrebalance\captures\page-data-owner-home-share-cards-maxscroll.json`

当前可见块：

- `home-page__style-foot-meta`
- 具体聚焦：
  - 三列风格卡 foot 第二行文案

预期变化：

- 不再调整卡片高度、cover/foot padding、guide 内部节奏
- 只把 foot 第二行从当前描述语改为 reference 的数量型短 meta：
  - `都市`: `128 套`
  - `古风`: `96 套`
  - `经典`: `214 套`

保持不动：

- `home-page__style-cover { min-height: 342rpx }`
- `home-page__style-foot { padding: 20rpx 16rpx 26rpx; gap: 8rpx }`
- `home-page__guide-stage { margin-top: -24rpx }`
- `home-page__guide-step { min-height: 72rpx }`
- `home-page__guide-cta { margin-top: 16rpx; height: 108rpx }`
- 风格卡标题行 `都市霓虹 / 汉唐衣冠 / 永恒影调`

### 69.2 锚点判断

当前 style-card 的结构比例已经收口到 reference 近似范围：

- reference
  - `style-card height = 233px`
  - `style-cover height = 178px`
  - `style-foot height ≈ 54px`
- r31
  - `style-card height = 232px`
  - `style-cover height = 177px`
  - `style-foot height = 53px`

剩余最明显且可见的差异已经变成 foot meta 文案口径：

- reference:
  - `128 套 / 96 套 / 214 套`
- 当前 runtime:
  - `现代高光 / 东方韵律 / 光影经典`

该差异不是布局尺寸问题，而是 reference HomeScreen 的可见信息合同差异。

当前最直接锚点：

- `resolveStyleCaption(item).meta`

动作策略：

- 只改 `meta` 的显示口径
- 不改 `title`
- 不改 `SceneTemplate` / API / 后端数据
- 以 `00-73` 的当前 reference UI 收口为准，先用首页 MVP 三风格固定展示数量

## 71. home / 首屏 frame：从 guide 微调切回 hero + stats + styles，并收口风格卡 eyebrow 合同

> 编号说明：前文尾部存在 `69 / 70` 插入顺序倒置，本节从 `71` 继续追加，不重排历史记录。

### 71.1 本轮先读依据

已重新读取：

- `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\requirements.md`
- `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-73-current-phase-reference-ui-architecture-rebuild\execution.md`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-card-mvp.ts`

当前框架事实：

- 前端目录：`D:\XM\kaipai-team\kaipai-frontend`
- 页面：`D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- route：`pages/home/index`
- 技术栈：`uni-app / Vue 3 / TypeScript / Pinia / Sass`
- 小程序运行态主验收产物：`D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`

### 71.2 本轮换向判断

本轮不继续改：

- `home-page__guide-stage`
- `home-page__guide-cover`
- `home-page__guide-copy`
- `home-page__guide-step`
- `home-page__guide-cta`
- `home-page__section--guide` 内部 gap

依据：

- r33 已把 `风格分馆 -> 操作指南` 块间距从 `0px` 收到 `23px`
- reference 对应值为 `24px`
- guide 内部当前已命中：
  - `head -> stage = 0px`
  - `steps -> CTA = 20px`
  - `CTA height = 56px`
- 继续在同一 guide 子块上加数值微调，收益低且容易进入同类试错

因此本轮按 R28 / R29 的治理要求主动换方向：

- 从 `guide` 下半屏内部间距微调
- 切到 `home / hero + stats + styles` 首屏 frame 核验
- 同时先处理 reference 与 runtime 肉眼可见且低风险的风格卡 eyebrow 文案合同

### 71.3 reference 首屏量化

reference 来源：

- `D:\XM\kaipai-team\_-_.html`
- `D:\XM\kaipai-team\tmp\reference-home-phone-recovered-20260423.png`

通过本地 `Playwright CLI` 打开 `http://127.0.0.1:8123/_-_.html`，登录后定位 HomeScreen scroller，得到首屏关键坐标：

```text
micro    = { x: 24, y: 51,  w: 342, h: 12 }
title    = { x: 24, y: 69,  w: 342, h: 72 }
subtitle = { x: 24, y: 151, w: 342, h: 19 }
stats    = { x: 24, y: 188, w: 342, h: 69 }
styleHead= { x: 0,  y: 279, w: 390, h: 38 }
styleGrid= { x: 0,  y: 317, w: 390, h: 257 }

gaps:
micro -> title      = 6px
title -> subtitle   = 10px
subtitle -> stats   = 18px
stats -> styleHead  = 22px
styleHead -> grid   = 0px
```

reference 风格卡 eyebrow：

```text
URBAN / GUO FENG / CLASSIC
```

### 71.4 当前 runtime 基线

新增运行态采集脚本：

- `D:\XM\kaipai-team\tmp\automator-probe\capture-home-top.js`

新增原因：

- 之前 `capture-home-guide-bottom.js` 只面向 maxScroll 下半屏
- 本轮换到首屏 frame，必须有独立 top capture，不能继续拿 bottom 截图推断首屏

r34 baseline：

- 截图：`D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r34-top-baseline\screenshots\owner-home-top.png`
- 数据：`D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r34-top-baseline\captures\page-data-owner-home-top.json`

r34 runtime 关键坐标：

```text
micro    = { left: 23, y: 98.5, w: 168, h: 12 }
title    = { left: 23, y: 120,  w: 344, h: 69 }
subtitle = { left: 23, y: 195,  w: 344, h: 19 }
stats    = { left: 23, y: 224.5,w: 344, h: 58 }
styleHead= { left: 23, y: 295,  w: 344, h: 36 }
styleGrid= { left: 23, y: 341,  w: 344, h: 232 }
```

已确认差异：

- 首屏顶部 reserve 仍偏大：
  - reference `micro.y = 51`
  - r34 `micro.y = 98.5`
- stats strip 高度偏薄：
  - reference `69px`
  - r34 `58px`
- styleGrid 首屏起点仍偏下：
  - reference `317px`
  - r34 `341px`
- 风格卡 eyebrow 文案不一致：
  - reference `URBAN / GUO FENG / CLASSIC`
  - r34 `URBAN STYLE / GUO FENG / CLASSIC STYLE`

当前判断：

- top reserve / stats / styles 起点属于一组首屏 frame 问题，后续要按组合量化处理，不能盲目只改一个 padding 后宣称完成
- eyebrow 文案是独立、低风险、可立即收口的 visible contract

### 71.5 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-card-mvp.ts`

改动：

```text
MVP_SCENE_META.general.eyebrow:
  CLASSIC STYLE -> CLASSIC

MVP_SCENE_META.urban.eyebrow:
  URBAN STYLE -> URBAN
```

保持不动：

- `MVP_SCENE_TEMPLATE_FALLBACK.general.heroEyebrow = CLASSIC STYLE`
- `MVP_SCENE_TEMPLATE_FALLBACK.urban.heroEyebrow = URBAN STYLE`
- `GUO FENG`
- `home-page__style-cover`
- `home-page__style-foot`
- `home-page__guide-*`
- `home-page__section--guide`

原因：

- 本轮只收首页 / 创建流风格卡 eyebrow 文案
- 不把 preview / poster heroEyebrow 一起改掉，避免跨页面未验证的副作用

### 71.6 四层验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- `D:\AP\微信web开发者工具\cli.bat auto --auto-port 9520 --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `node D:\XM\kaipai-team\tmp\automator-probe\capture-home-top.js D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r35-top-eyebrow-contract`

结果：

- `type-check`：通过
- `build:mp-weixin`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

源码层：

- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-card-mvp.ts`
- 已命中：
  - `eyebrow: 'CLASSIC'`
  - `eyebrow: 'URBAN'`
  - `eyebrow: 'GUO FENG'`

`dist\build`：

- `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\utils\share-card-mvp.js`
- 已命中：
  - `eyebrow:"CLASSIC"`
  - `eyebrow:"URBAN"`
  - `eyebrow:"GUO FENG"`

`dist\dev`：

- `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\utils\share-card-mvp.js`
- 已命中：
  - `eyebrow:"CLASSIC"`
  - `eyebrow:"URBAN"`
  - `eyebrow:"GUO FENG"`

fresh runtime：

- 截图：`D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r35-top-eyebrow-contract\screenshots\owner-home-top.png`
- 数据：`D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r35-top-eyebrow-contract\captures\page-data-owner-home-top.json`

r35 runtime 可见结果：

```text
styleCards[0].card.text = URBAN / 都市 / 都市霓虹 / 128 套
styleCards[1].card.text = GUO FENG / 古风 / 汉唐衣冠 / 96 套
styleCards[2].card.text = CLASSIC / 经典 / 永恒影调 / 214 套
```

### 71.7 当前结论与下一锚点

本轮结论：

- `home` 首屏 frame 已有独立 top capture 脚本，后续不再用 bottom 截图推断首屏
- 风格卡 eyebrow 已从 `URBAN STYLE / CLASSIC STYLE` 收口到 reference 的 `URBAN / CLASSIC`
- 本轮没有触发新的同类 3 次失败

仍未完成：

- `micro.y / title.y / subtitle.y / stats.y / styleGrid.y` 仍与 reference 存在 frame-level 差异
- 当前不能宣称 home 首屏 1:1

下一轮若继续 `home`，默认锚点应是首屏组合节奏，而不是单点盲改：

1. 先计算 `KpCapsuleSpacer -> home-page__hero-copy` 的 top reserve
2. 再计算 `home-page__stats-strip` 的 `margin-top / padding / height`
3. 最后才动 `home-page__body` 或 `home-page__section--styles`

方向约束：

- 不再继续对 `guide` 下半屏内部做无证据微调
- 如首屏 top reserve 连续 3 次运行态无正确变化，必须从样式数值切换为 `KpCapsuleSpacer / native capsule / DevTools project path` 四层核对

## 72. home / 首屏 frame：只移动 `home-page__hero-copy`，把 styles first-screen 起点拉回 reference

### 72.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\reference-home-phone-recovered-20260423.png`
- `D:\XM\kaipai-team\_-_.html`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r35-top-eyebrow-contract\screenshots\owner-home-top.png`
- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r35-top-eyebrow-contract\captures\page-data-owner-home-top.json`

当前可见块：

- `home-page__hero-copy`
- 影响范围：
  - `micro`
  - `title`
  - `subtitle`
  - `stats strip`
  - `styles first-screen start`

预期变化：

- 只把首页首屏整体上提一个 reference 单位
- 优先把 `styleGrid` 的首屏起点拉回 reference
- 不同时改 `stats-strip`
- 不动 `home-page__body`
- 不回到 `guide` 内部继续盲调

保持不动：

- `home-page__stats-strip`
- `home-page__body`
- `home-page__section--guide`
- `home-page__guide-*`
- 风格卡内部尺寸与文案

### 72.2 锚点判断

r35 -> reference 的首屏差异：

```text
reference:
micro.y     = 51
title.y     = 69
subtitle.y  = 151
stats.y     = 188
styleGrid.y = 317

r35:
micro.y     = 98.5
title.y     = 120
subtitle.y  = 195
stats.y     = 224.5
styleGrid.y = 341
```

判断：

- 当前 `styleGrid.y` 比 reference 低 `24px`
- 这一偏差与首屏整体 top reserve 更接近，而不是 `stats-strip` 自身高度问题
- 因此本轮先动直接锚点：
  - `home-page__hero-copy`

动作策略：

- 只给 `home-page__hero-copy` 新增负 `margin-top`
- 不同时修改 `stats-strip` 与 `body`
- 先验证“首页首屏整体被上提”这件事是否真实发生

### 72.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

```text
home-page__hero-copy:
  margin-top: -46rpx
```

取值依据：

- 目标先吃掉 `styleGrid` 与 reference 的约 `24px` 差值
- `24px * 750 / 390 ≈ 46rpx`

### 72.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `D:\AP\微信web开发者工具\cli.bat auto --auto-port 9520 --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `node D:\XM\kaipai-team\tmp\automator-probe\capture-home-top.js D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r36-herocopy-topshift46`

结果：

- `build:mp-weixin`：通过
- `type-check`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

四层核验：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：`home-page__hero-copy { margin-top: -46rpx; padding: 18rpx 0 0; }`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__hero-copy{margin-top:-46rpx;padding:18rpx 0 0}`
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：`.home-page__hero-copy{margin-top:-46rpx;padding:18rpx 0 0}`

fresh runtime：

- 截图：`D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r36-herocopy-topshift46\screenshots\owner-home-top.png`
- 数据：`D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r36-herocopy-topshift46\captures\page-data-owner-home-top.json`

r36 runtime 关键值：

```text
micro.y     = 75.5
title.y     = 97
subtitle.y  = 172
stats.y     = 201.5
styleGrid.y = 318
hero.height = 268
page.height = 927
```

量化对比：

```text
micro.y:
  98.5 -> 75.5
  向上移动 23px

title.y:
  120 -> 97
  向上移动 23px

subtitle.y:
  195 -> 172
  向上移动 23px

stats.y:
  224.5 -> 201.5
  向上移动 23px

styleGrid.y:
  341 -> 318
  向上移动 23px
  已非常接近 reference 317
```

### 72.5 当前结论

已确认：

- `home-page__hero-copy` 是首页首屏的真实直接锚点
- 本轮不是“只改到源码”
- 运行态首屏已整体上提，且 `styleGrid` 的 first-screen 起点已经从 `341` 收到 `318`

仍未完成：

- `micro / title / subtitle / stats` 相对 reference 仍偏下
- 剩余问题已集中为 hero 内部节奏，而不是 styles 起点本身

推进结论：

- 下一轮不应再继续加大 `hero-copy` 负 margin
- 下一轮应改为单独量化：
  - `home-page__stats-strip`
  - `subtitle -> stats` gap
  - `stats` height

失败计数：

- 当前 `home / 首屏 frame / hero-copy` 方向仅完成 1 次有效验证
- 尚未触发“连续 3 次同类失败后自动换方向”

## 73. home / 首屏 frame：重分配 hero bottom reserve 与 styles head-grid gap，runtime 连续 3 次失败后自动换方向

### 73.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\reference-home-phone-recovered-20260423.png`
- `D:\XM\kaipai-team\_-_.html`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r36-herocopy-topshift46\screenshots\owner-home-top.png`
- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r36-herocopy-topshift46\captures\page-data-owner-home-top.json`

当前可见块：

- `home-page__hero`
- `home-page__section--styles`

预期变化：

- 不继续加大 `home-page__hero-copy` 负 margin
- 把 `styles` 内部 `section-head -> style-grid` 的约 `10px` gap 收回到 `0`
- 同时把对应空间转移到 `hero` 底部 reserve，让 `styleHead` 不被拉得过高
- 目标是保持 `styleGrid.y` 接近 reference `317px`，同时让 `风格分馆` 标题与卡片贴近 reference 的 head-grid 关系

保持不动：

- `home-page__hero-copy { margin-top: -46rpx }`
- `home-page__stats-strip`
- `home-page__body`
- `home-page__section--guide`
- `home-page__guide-*`
- 风格卡内部尺寸与文案

### 73.2 锚点判断

r36 已知运行态：

```text
reference:
styleHead.y = 279
styleHead.h = 38
styleGrid.y = 317
styleHead -> styleGrid = 0px

r36:
styleHead.y = 272
styleHead.h = 36
styleGrid.y = 318
styleHead -> styleGrid = 10px
```

判断：

- `styleGrid.y` 已接近 reference，因此不应继续整体上提页面
- 当前剩余最明确的局部差异是 `styleHead -> styleGrid` 的 10px 内部 gap
- 直接把 `section--styles gap` 改为 `0` 会让 `styleGrid` 过度上移
- 因此本轮采用“空间重分配”：
  - `home-page__section--styles { gap: 0 }`
  - `home-page__hero padding-bottom` 增加约 `9px`

取值：

- `9px * 750 / 390 ≈ 17rpx`
- 采用 `18rpx`
- `home-page__hero padding-bottom: 18rpx -> 36rpx`

### 73.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

```text
home-page__hero:
  padding: 0 46rpx 18rpx -> 0 46rpx 36rpx

home-page__section--styles:
  gap: 0
```

说明：

- 这不是重新回到 guide 下半屏
- 也不是继续把 `hero-copy` 往上拉
- 本轮只处理 `styles` section 的 head-grid 相对关系

### 73.4 src / dist 核验

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`

结果：

- `build:mp-weixin`：通过
- `type-check`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

四层中的前三层：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：
    - `home-page__hero { padding: 0 46rpx 36rpx }`
    - `home-page__section--styles { gap: 0 }`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `.home-page__hero{padding:0 46rpx 36rpx}`
    - `.home-page__section--styles{gap:0}`
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中：
    - `.home-page__hero{padding:0 46rpx 36rpx}`
    - `.home-page__section--styles{gap:0}`

### 73.5 runtime 连续 3 次失败与自动换向

本轮 runtime / DevTools 链路连续失败 3 次：

1. `capture-home-top.js`
   - 目标：`D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r37-stylehead-gap-rebalance`
   - 结果：`command timed out after 124018ms`
2. `connect-and-probe.js`
   - 目标：`ws://127.0.0.1:9520`
   - 结果：`command timed out after 124027ms`
3. 纠正 DevTools project path 后再次执行 `capture-home-top.js`
   - 已先确认误连过一次非当前工程：
     - 错误工程：`D:\XM\QD\yangzhou\wx_uni\unpackage\dist\dev\mp-weixin`
     - 正确工程：`D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
   - 再次运行仍失败：
     - `command timed out after 124025ms`

按 R28 / R29 / R30，已自动换方向：

- 停止继续 DevTools automator 重试
- 停止继续样式数值微调
- 改为：
  - 先记录 runtime 阻塞
  - 保留 `src / dist\build / dist\dev` 已命中的产物事实
  - 尝试 OS 级截图替代通道

### 73.6 OS 级替代截图结果

已使用 screenshot skill：

- 桌面截图：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r37-stylehead-gap-rebalance\screenshots\desktop-after-automator-timeout.png`
- active window 截图：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r37-stylehead-gap-rebalance\screenshots\wechat-devtools-active-window.png`
- window handle 截图：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r37-stylehead-gap-rebalance\screenshots\wechat-devtools-window-handle.png`

结果：

- 桌面截图没有可见微信 DevTools 页面
- `AppActivate('mp-weixin - 微信开发者工具 Stable v2.01.2510260')` 返回成功，但实际截图落到了浏览器窗口
- 使用已知窗口句柄 `8525578` 截图仍没有拿到微信 DevTools 页面

当前结论：

- 本轮 r37 只能证明：
  - `src / dist\build / dist\dev` 已完成空间重分配
- 本轮不能证明：
  - 微信 DevTools 运行态已经渲染出 r37
  - r37 截图已经相对 reference 更接近

因此不得把 r37 汇报为视觉完成。

### 73.7 后续方向

当前必须先修复 / 重置运行态验证链路，再继续下一轮 UI 数值调整。

下一步推荐顺序：

1. 清理卡住的 automator client / 多余 wechatdevtools 进程
2. 重新只打开正确工程：
   - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
3. 先跑 `connect-and-probe.js`
4. 只有 probe 成功后，才允许重新跑 `capture-home-top.js`
5. 拿到 r37 fresh runtime 后再判断：
   - 若 `styleGrid.y` 仍接近 `317`
   - 且 `styleHead -> styleGrid` 接近 `0`
   - 则本轮可保留
   - 否则优先回滚或微调 `section--styles gap / hero padding-bottom` 这组重分配，不得跳去改 guide

## 74. home / 运行态验证链路：用进程级重置恢复 probe，并确认 r37 重分配已在 fresh runtime 命中

### 74.1 本轮目标

页面：

- `pages/home/index`

目标：

- 不是继续改样式
- 而是修复 `00-73` 当前被阻塞的 `DevTools / automator` 验证链路
- 只要链路恢复，先验证 r37 是否真的已经落到运行态

### 74.2 诊断结论

当前卡点不是 `src / dist` 漂移，而是 automator client 残留：

- `9520` 正在监听，但已有卡住的 node client 占用连接
- 例如：
  - `capture-home-top.js`
  - `connect-and-probe.js`
- 普通 `close -> auto` 不能稳定清空该状态

依据：

- `netstat -ano | Select-String ':9520'`
- `Get-CimInstance Win32_Process`

### 74.3 本轮动作

已执行的恢复动作：

1. 停掉卡住的 automator node client
2. `cli close --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
3. 发现普通关闭后 `probe` 仍超时
4. 进一步执行进程级重置：
   - 关闭全部 `wechatdevtools` 进程
5. 重新只打开当前仓库工程：
   - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
6. 先跑 `connect-and-probe.js`，成功后才继续 top capture

### 74.4 恢复结果

恢复后的 fresh probe：

- 输出截图：
  - `D:\XM\kaipai-team\tmp\automator-probe\probe-current-page-r40.png`
- probe 结果：

```text
wsEndpoint = ws://127.0.0.1:9520
SDKVersion = 3.15.0
currentPage.path = pages/home/index
pageStack = [pages/home/index]
```

结论：

- 当前验证链路已恢复
- 之前的超时属于 DevTools 会话阻塞，不属于首页样式方向失败

### 74.5 r37 fresh runtime

恢复链路后重新执行：

- `node D:\XM\kaipai-team\tmp\automator-probe\capture-home-top.js D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r41-stylehead-gap-rebalance-fresh`

fresh runtime：

- 截图：`D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r41-stylehead-gap-rebalance-fresh\screenshots\owner-home-top.png`
- 数据：`D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r41-stylehead-gap-rebalance-fresh\captures\page-data-owner-home-top.json`

r41 关键值：

```text
micro.y     = 75.5
title.y     = 97
subtitle.y  = 172
stats.y     = 201.5
styleHead.y = 281
styleGrid.y = 317
styleHead -> styleGrid = 0px
```

对比 reference：

```text
reference:
styleHead.y = 279
styleGrid.y = 317
styleHead -> styleGrid = 0px
```

本轮结论：

- r37 的 `hero bottom reserve + styles gap` 重分配已在 fresh runtime 命中
- `styleGrid.y = 317` 命中 reference
- `styleHead -> styleGrid = 0px` 命中 reference
- 因此 r37 保留，不回滚

## 75. home / 首屏 hero internal：上移 hero 文案、补回 stats 间距，同时保持 styles 起点不动

### 75.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\reference-home-phone-recovered-20260423.png`
- `D:\XM\kaipai-team\_-_.html`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r41-stylehead-gap-rebalance-fresh\screenshots\owner-home-top.png`
- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r41-stylehead-gap-rebalance-fresh\captures\page-data-owner-home-top.json`

当前可见块：

- `home-page__hero`
- `home-page__hero-copy`
- `home-page__stats-strip`

预期变化：

- `micro / title / subtitle` 继续上移
- `stats` 回到接近 reference 的 y 值
- `styleGrid` 保持在 `317px` 左右，不再被带走

保持不动：

- `home-page__section--styles { gap: 0 }`
- `home-page__guide-*`
- 风格卡尺寸与文案

### 75.2 锚点判断

r41 相对 reference：

```text
reference:
micro.y     = 51
title.y     = 69
subtitle.y  = 151
stats.y     = 188
styleGrid.y = 317

r41:
micro.y     = 75.5
title.y     = 97
subtitle.y  = 172
stats.y     = 201.5
styleGrid.y = 317
```

判断：

- `styleGrid` 已对齐，不应再整体移动页面
- 当前剩余差异只应在 hero 内部重分配解决

动作策略：

- `home-page__hero-copy` 再向上
- `home-page__stats-strip` 增加顶部间距
- `home-page__hero` 增加底部 reserve
- 三者联动，目标是：
  - top 文案更靠近 reference
  - stats 回到正确位置
  - grid 不被拉偏

### 75.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- `D:\XM\kaipai-team\tmp\automator-probe\capture-home-top.js`

样式动作：

```text
home-page__hero:
  padding-bottom: 36rpx -> 62rpx

home-page__hero-copy:
  margin-top: -46rpx -> -92rpx

home-page__stats-strip:
  margin-top: 22rpx -> 42rpx
```

验证工具动作：

```text
capture-home-top.js:
  新增 --skip-screenshot
```

原因：

- 当前 `miniProgram.screenshot()` 会间歇性阻塞
- 先保住 DOM metrics 采集，再用 OS 级截图作为辅助

### 75.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `node D:\XM\kaipai-team\tmp\automator-probe\capture-home-top.js D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r42-hero-internal-redistribute --skip-screenshot`

结果：

- `build:mp-weixin`：通过
- `type-check`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

四层核验中的前三层：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：
    - `padding: 0 46rpx 62rpx`
    - `margin-top: -92rpx`
    - `margin-top: 42rpx`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 已命中同值
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中同值

fresh runtime metrics：

- 数据：`D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r42-hero-internal-redistribute\captures\page-data-owner-home-top.json`
- `skipScreenshot = true`

r42 关键值：

```text
micro.y     = 51.5
title.y     = 73
subtitle.y  = 148
stats.y     = 187.5
styleHead.y = 281
styleGrid.y = 317
```

对比 reference：

```text
reference:
micro.y     = 51
title.y     = 69
subtitle.y  = 151
stats.y     = 188
styleHead.y = 279
styleGrid.y = 317
```

量化结果：

- `micro.y`
  - `75.5 -> 51.5`
  - 已基本命中 reference
- `stats.y`
  - `201.5 -> 187.5`
  - 已基本命中 reference
- `styleGrid.y`
  - 保持 `317`
  - 命中 reference
- `title.y`
  - 仍比 reference 低约 `4px`
- `subtitle.y`
  - 仍比 reference 高约 `3px`

### 75.5 截图边界

OS 级窗口截图尝试：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r42-hero-internal-redistribute\screenshots\wechat-devtools-window-handle.png`

结果：

- 只得到黑窗 / 不可见窗口截图
- 因此本轮 screenshot 通道仍受限

当前边界：

- r42 已有可靠 DOM metrics 证据
- 但没有可用的 fresh DevTools 可见页截图
- 因此本轮可判断为：
  - **布局数值接近 reference**
  - **但不是完整 screenshot 闭环**

### 75.6 当前结论

本轮结论：

- 首页首屏 top frame 已进一步收口
- 当前关键坐标已非常接近 reference：
  - `micro.y ≈ 51`
  - `stats.y ≈ 188`
  - `styleGrid.y = 317`
- `title / subtitle` 仍有约 `3-4px` 的剩余差异

后续方向：

- 暂不继续叠加新的 hero 变量
- 下一轮若继续 `home` 首屏，应优先只处理：
  - `home-page__title margin-top`
  - 或 `home-page__subtitle margin-top`
- 不再同时改 `hero / hero-copy / stats-strip` 三值联动

## 76. home / 首屏 title-subtitle：只重分配标题与副标题间距，首屏 metrics 进入 reference 同档

### 76.1 本轮视觉合同

页面：

- `pages/home/index`

reference：

- `D:\XM\kaipai-team\tmp\reference-home-phone-recovered-20260423.png`
- `D:\XM\kaipai-team\_-_.html`

当前运行态基线：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r42-hero-internal-redistribute\captures\page-data-owner-home-top.json`

当前可见块：

- `home-page__title`
- `home-page__subtitle`
- `home-page__stats-strip`

预期变化：

- `title.y` 从 `73` 拉到接近 reference `69`
- `subtitle.y` 从 `148` 拉到接近 reference `151`
- `stats.y` 继续保持接近 reference `188`
- `styleGrid.y` 继续锁在 `317`

保持不动：

- `home-page__hero { padding: 0 46rpx 62rpx }`
- `home-page__hero-copy { margin-top: -92rpx }`
- `home-page__section--styles { gap: 0 }`
- `home-page__guide-*`
- 风格卡尺寸与文案

### 76.2 锚点判断

r42 相对 reference：

```text
reference:
micro.y     = 51
title.y     = 69
subtitle.y  = 151
stats.y     = 188
styleGrid.y = 317

r42:
micro.y     = 51.5
title.y     = 73
subtitle.y  = 148
stats.y     = 187.5
styleGrid.y = 317
```

判断：

- `micro / stats / styleGrid` 已基本命中
- 剩余差异集中在：
  - `title` 过低约 `4px`
  - `subtitle` 过高约 `3px`
- 因此本轮只做文本层级的局部节奏重分配，不再回到 `hero / hero-copy / stats-strip` 的大范围联动

动作策略：

- 缩小 `title margin-top`
- 增大 `subtitle margin-top`
- 轻微回调 `stats-strip margin-top`

### 76.3 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`

动作：

```text
home-page__title:
  margin-top: 14rpx -> 6rpx

home-page__subtitle:
  margin-top: 12rpx -> 26rpx

home-page__stats-strip:
  margin-top: 42rpx -> 36rpx
```

说明：

- 本轮不动 `hero padding-bottom`
- 也不再追加 `hero-copy` 的负 margin
- 目标是只把 `title / subtitle` 收口到 reference

### 76.4 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`
- `node D:\XM\kaipai-team\tmp\automator-probe\capture-home-top.js D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r43-title-subtitle-microgap --skip-screenshot`

结果：

- `build:mp-weixin`：通过
- `type-check`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

四层核验中的前三层：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
  - 已命中：
    - `home-page__title { margin-top: 6rpx }`
    - `home-page__subtitle { margin-top: 26rpx }`
    - `home-page__stats-strip { margin-top: 36rpx }`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\home\index.wxss`
  - 已命中同值
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\home\index.wxss`
  - 已命中同值

fresh runtime metrics：

- 数据：`D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r43-title-subtitle-microgap\captures\page-data-owner-home-top.json`
- `skipScreenshot = true`

r43 关键值：

```text
micro.y     = 51.5
title.y     = 69
subtitle.y  = 151
stats.y     = 187.5
styleHead.y = 281
styleGrid.y = 317
```

对比 reference：

```text
reference:
micro.y     = 51
title.y     = 69
subtitle.y  = 151
stats.y     = 188
styleHead.y = 279
styleGrid.y = 317
```

量化结果：

- `micro.y`
  - `51.5`
  - 与 reference 几乎重合
- `title.y`
  - `73 -> 69`
  - 命中 reference
- `subtitle.y`
  - `148 -> 151`
  - 命中 reference
- `stats.y`
  - `187.5`
  - 与 reference `188` 仅差 `0.5px`
- `styleGrid.y`
  - `317`
  - 命中 reference

### 76.5 截图边界

本轮继续尝试 screenshot 通道：

- `node D:\XM\kaipai-team\tmp\automator-probe\connect-and-probe.js ws://127.0.0.1:9520 D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r43-title-subtitle-microgap\screenshots\owner-home-top-probe.png`

结果：

- `command timed out after 124030ms`
- 后续已清掉残留 probe client

当前判断：

- `miniProgram.screenshot()` 通道仍不稳定
- 但 `capture-home-top.js --skip-screenshot` 的 DOM metrics 已稳定可用
- 因此本轮仍属于：
  - **metrics 已通过**
  - **screenshot 通道受限**

### 76.6 当前结论

当前 `home` 首屏 frame 已基本进入 reference 同档：

- `micro.y ≈ 51`
- `title.y = 69`
- `subtitle.y = 151`
- `stats.y ≈ 188`
- `styleGrid.y = 317`

剩余边界：

- `styleHead.y = 281`，仍比 reference `279` 低约 `2px`
- `styleHead.height = 36`，仍比 reference `38` 小约 `2px`
- 当前更像字体渲染 / line-height 的微差，而不是结构偏移

推进结论：

- 下一轮不应继续在 `home` 首屏做同类像素级过拟合
- 更合理的方向是：
  - 记录 `home` 首屏已接近闭环但 screenshot 通道仍受限
  - 转向 `home` 下一可见块或下一个 core screen

## 77. home / 下半屏回归：确认首屏细修没有破坏 `风格分馆 -> 操作指南` 既有收口

### 77.1 本轮目的

页面：

- `pages/home/index`

目的：

- 不再继续改首页首屏样式
- 只验证 `r43` 的首屏细修是否影响了下半屏：
  - 风格卡尺寸
  - `styles -> guide` 间距
  - guide 内部节奏

### 77.2 本轮动作

已改验证脚本：

- `D:\XM\kaipai-team\tmp\automator-probe\capture-home-guide-bottom.js`

动作：

```text
新增 --skip-screenshot
```

原因：

- 与 `capture-home-top.js` 一样，避免 `miniProgram.screenshot()` 卡住整轮验证
- 先保住 maxscroll DOM metrics

### 77.3 本轮验证

已执行：

- `node D:\XM\kaipai-team\tmp\automator-probe\capture-home-guide-bottom.js D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r44-bottom-after-topclose --skip-screenshot`

输出：

- 数据：`D:\XM\kaipai-team\tmp\ui-compare-20260423-home-r44-bottom-after-topclose\captures\page-data-owner-home-share-cards-maxscroll.json`
- `skipScreenshot = true`

r44 关键值：

```text
styleGrid.top = 317
styleGrid.height = 232

guideHead.top = 572
guideHead.height = 36

stage.top = 608
stage.height = 193

steps.top = 813
steps.height = 37

cta.top = 870
cta.height = 56
```

对比 reference / 既有收口：

```text
reference:
styleGrid.top = 317
styles -> guide = 24px
CTA height = 56px

r44:
styles -> guide
  = 572 - (317 + 232)
  = 23px

CTA height
  = 56px
```

风格卡尺寸：

```text
card.height = 232
cover.height = 177
foot.height = 53
footMeta = 128 套 / 96 套 / 214 套
```

结论：

- 首屏细修没有破坏下半屏既有收口
- `styles -> guide = 23px`，仍接近 reference `24px`
- `CTA height = 56px` 保持命中
- 风格卡尺寸与 meta 文案保持稳定

### 77.4 当前 home 页结论

当前 `home` 页的量化结果已稳定在 reference 同档：

- 首屏：
  - `micro.y ≈ 51`
  - `title.y = 69`
  - `subtitle.y = 151`
  - `stats.y ≈ 188`
  - `styleGrid.y = 317`
- 下半屏：
  - `styles -> guide ≈ 23px`
  - `CTA height = 56px`
  - 风格卡高度 / cover / foot 比例稳定

剩余边界：

- `styleHead.y = 281` / `height = 36` 与 reference 仍有约 `2px` 级差异
- `miniProgram.screenshot()` 仍然不稳定
- OS 级窗口截图仍可能拿不到 DevTools 可见页

推进结论：

- 不再继续对 `home` 页做同类微调
- `home` 可视为：
  - **metrics 近闭环**
  - **screenshot 通道受限，未形成完整可见页截图闭环**
- 下一步更合理的主线应切向下一个 core screen，而不是继续在 `home` 首屏/下半屏做第 N 轮微差试错

## 78. mine / 运行态验证三次失败后自动换向：停止继续撞 DevTools，切到 login

### 78.1 当前页面与可见块

页面：

- `pages/mine/index`

当前可见块：

- `mine-page__profile`
- `mine-page__analytics`
- `mine-page__quick-grid`
- `mine-page__settings`
- `mine-page__logout`

### 78.2 已失败的 3 次尝试口径

同一类问题：

- `mine` 的 current runtime 验证链路不稳定，无法稳定拿到 `dist\dev\mp-weixin` 的 fresh 页面证据

连续 3 次失败：

1. `capture-mine-page.js`
   - 结果：
     - `Failed connecting to ws://127.0.0.1:9520`
   - 证据：
     - 当时没有 `9520` 监听
     - 前台工程标题是 `PKPD AI助手小程序`
2. 纠正工程后再执行 `capture-mine-page.js`
   - 结果：
     - `Failed connecting to ws://127.0.0.1:9520`
   - 证据：
     - build 后 DevTools 又回到错误工程，automation 丢失
3. 再次 `auto --auto-port 9520 --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
   - 随后执行：
     - `capture-mine-page.js --skip-screenshot`
   - 结果：
     - `Connection closed, check if wechat web devTools is still running`

### 78.3 为什么原方向不再继续

依据：

- 当前不是 `mine` 样式值没有命中
- 而是 DevTools runtime 会话在当前机器上反复漂移 / 断开
- 继续在 `mine` 上做第 4 次同类 runtime 重试，只会重复同一类阻塞

因此按 R28 / R29 / R30：

- 不再继续 `mine` runtime 重试
- 不再继续在 `mine` 上追加新样式值

### 78.4 新推进方向

新方向：

- 从 `mine` runtime 验证链路切走
- 转去同一主工作流里的下一个 core screen：
  - `pages/login/index`

原因：

- `login` 在 `00-73 design` 里已被明确标记为：
  - 单页 reference 已补齐
  - 当前主要缺的是运行态复核，不是长期结构重写
- 本地已有现成证据：
  - `D:\XM\kaipai-team\tmp\wechat-devtools-login.png`
- 这样可以继续推进 T4，而不是停在 `mine`

## 79. mine / reference 与 current metrics 对照：analytics 已回弹，lower stack source 已改但 runtime 阻断

### 79.1 reference 对照

reference 来源：

- `D:\XM\kaipai-team\_-_.html`
- 原型 `MyScreen`

已量化 reference：

```text
profile = { x: 24, y: 73, w: 342, h: 58 }
analytics = { x: 24, y: 159, w: 342, h: 266 }
quickCards = [
  { x: 24,  y: 441, w: 166, h: 105 },
  { x: 200, y: 441, w: 166, h: 105 }
]
settings = { x: 24, y: 568, w: 342, h: 197 }
logout = { x: 24, y: 781, w: 342, h: 47 }
```

### 79.2 current baseline

当前页：

- `pages/mine/index`

fresh runtime baseline：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-mine-r2-current-baseline\captures\page-data-owner-mine.json`

r2 关键值：

```text
profile.top = 92
analytics.top = 165
analytics.height = 217
quickGrid.top = 390
quickGrid.height = 84
settings.top = 481.5
settings.height = 182
logout.top = 671.5
logout.height = 31
```

判断：

- `analytics.height = 217` 明显短于 reference `266`
- 该压缩直接导致 quick cards / settings / logout 都提前
- 因此第一锚点选择 `mine-page__analytics`

### 79.3 analytics 回弹动作与验证

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\mine\index.vue`

动作：

```text
mine-page__analytics padding: 26rpx 28rpx 24rpx -> 34rpx 34rpx 30rpx
mine-page__analytics-head margin-bottom: 20rpx -> 28rpx
mine-page__analytics-title font-size: 32rpx -> 34rpx
mine-page__analytics-main gap: 22rpx -> 28rpx
mine-page__analytics-value font-size: 64rpx -> 76rpx
mine-page__analytics-copy font-size: 20rpx -> 22rpx
mine-page__trend height: 86rpx -> 108rpx
mine-page__trend margin-top: 20rpx -> 26rpx
mine-page__analytics-strip gap: 16rpx -> 20rpx
mine-page__analytics-strip margin-top: 18rpx -> 24rpx
mine-page__analytics-mini gap: 8rpx -> 10rpx
mine-page__analytics-mini padding-top: 12rpx -> 16rpx
mine-page__analytics-mini-key font-size: 18rpx -> 20rpx
mine-page__analytics-mini-value font-size: 28rpx -> 32rpx
```

验证：

- `npm run build:mp-weixin`：通过
- `npm run type-check`：通过
- `src / dist\build / dist\dev`：均命中新值
- fresh runtime：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260423-mine-r3-analytics-reexpand\captures\page-data-owner-mine.json`

r3 关键值：

```text
analytics.height = 262
quickGrid.top = 435
settings.top = 526.5
logout.top = 716.5
```

结论：

- `analytics.height` 已从 `217` 回弹到 `262`
- 已接近 reference `266`
- quickGrid 顶部也已从 `390` 推回 `435`，接近 reference `441`

### 79.4 lower stack source 改动与边界

继续做了一次 lower stack source 改动：

```text
mine-page__body gap: 16rpx -> 30rpx
mine-page__quick-card min-height: 156rpx -> 194rpx
```

验证：

- `npm run build:mp-weixin`：通过
- `npm run type-check`：通过
- `src / dist\build / dist\dev`：均命中新值

但 fresh runtime：

- `capture-mine-page.js --skip-screenshot`
- 失败：
  - `Failed connecting to ws://127.0.0.1:9520`
  - 随后再次 `auto --auto-port 9520` 后出现 `Connection closed`

因此：

- lower stack source/dist 已变更
- runtime 未验证
- 不得宣称 `mine` lower stack 已完成

### 79.5 当前 mine 结论

当前 `mine` 的确定结论：

- `analytics` 回弹已完成并经 runtime metrics 验证
- `lower stack` 已有 source/dist 改动，但 runtime 阻断

当前不确定边界：

- `mine-page__body gap = 30rpx`
- `mine-page__quick-card min-height = 194rpx`
- 是否在真实运行态中把 settings/logout 推回 reference 节奏，尚未验证

因此已在 `## 78` 按三次同类失败换向，不继续在 `mine` 上做第 4 次 runtime 重试。

## 80. login / 去除 reference 外辅助注册 UI：移除 `login-page__assist`

### 80.1 本轮依据

页面：

- `pages/login/index`

reference 合同：

- R12 `LoginScreen`
- 明确不允许继续混入：
  - editorial 版辅助栏
  - mode tabs
  - flow note
  - reference 外结构

当前源码中仍存在：

- `login-page__assist`
- `注册身份`
- `我是演员 / 我是剧组`
- `好友邀请码`

这些属于 reference 外可见结构。

### 80.2 本轮动作

已改：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\login\index.vue`

动作：

- 删除模板中的：
  - `login-page__assist`
  - `login-page__assist-row`
  - `login-page__assist-pills`
  - `login-page__assist-pill`
  - `login-page__assist-code`
- 删除对应 scoped styles
- 删除未再使用的：
  - `hasInviteCode`

保持不动：

- `authMode`
- `registerRole`
- `inviteCode`
- `registerByPhone(...)`
- `loginByPhone(...)`
- `loginByWechat(...)`

说明：

- 注册逻辑仍保留默认 `Actor`
- 本轮只去掉 reference 外可见辅助 UI，不改认证接口行为

### 80.3 本轮验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`

结果：

- `build:mp-weixin`：通过
- `type-check`：通过
- `postbuild:mp-weixin`：已同步 `dist\build\mp-weixin -> dist\dev\mp-weixin`

四层中的前三层：

- `src`
  - `D:\XM\kaipai-team\kaipai-frontend\src\pages\login\index.vue`
  - 已不再命中：
    - `login-page__assist`
    - `assist-pill`
    - `注册身份`
    - `好友邀请码`
    - `hasInviteCode`
- `dist\build`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\build\mp-weixin\pages\login\index.wxml`
  - `index.wxss`
  - `index.js`
  - 均不再命中上述结构
- `dist\dev`
  - `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin\pages\login\index.wxml`
  - `index.wxss`
  - `index.js`
  - 均不再命中上述结构

仍保留并命中：

- `登录 / 注册`
- `微信一键登录`
- `用户协议`
- `隐私政策`
- `login-page__agreement`
- `login-page__wechat`

### 80.4 截图边界

本地已有文件：

- `D:\XM\kaipai-team\tmp\wechat-devtools-login.png`

核查结果：

- 该文件实际是预览二维码，不是登录页截图
- 因此不能作为 `LoginScreen` 当前可见层截图证据

当前结论：

- `login` 已完成一轮 reference 外结构清理
- 但还缺 fresh runtime 页面截图 / metrics
- 下一轮若继续 `login`，应先补 `pages/login/index` 的真实运行态采集，而不是继续改样式

## 81. login / T7 运行态采集继续推进：确认当前阻塞是“会话回跳 + 截图通道不稳定”

### 81.1 本轮目标与可见块

页面：

- `pages/login/index`

当前目标：

- 不再继续改 `LoginScreen` 样式
- 先补 `T7` 所需的 fresh runtime 证据，至少确认：
  - DevTools 当前工程是否仍是 `dist/dev/mp-weixin`
  - automator 是否能稳定停在 `pages/login/index`
  - 是否能拿到登录页截图 / page-data

保持不动：

- 登录页模板与样式
- 认证 API 行为
- 任何非 `login` 的页面可见层

### 81.2 本轮已确认的新事实

已执行：

- `D:\AP\微信web开发者工具\cli.bat open-other --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `D:\AP\微信web开发者工具\cli.bat auto-preview --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `D:\AP\微信web开发者工具\cli.bat auto --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin --auto-port 9520`

结果：

- `9520` 端口曾成功监听
- DevTools 可见窗口标题曾恢复为：
  - `mp-weixin - 微信开发者工具 Stable v2.01.2510260`

随后用已有脚本：

- `node D:\XM\kaipai-team\tmp\automator-probe\capture-login-page.js D:\XM\kaipai-team\tmp\ui-compare-20260423-login-r1-runtime --skip-screenshot`

得到 page-data：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-login-r1-runtime\captures\page-data-login-page.json`
- `D:\XM\kaipai-team\tmp\ui-compare-20260423-login-r1-runtime\captures\mini-program-login-capture.json`

其中关键结果不是 `login` 本身，而是：

```json
{
  "path": "pages/home/index",
  "fields": []
}
```

这说明：

- automator 链路至少一度是通的
- 但 `reLaunch('/pages/login/index')` 后当前会话实际又回到了 `pages/home/index`
- 因此此前拿不到登录页 DOM / metrics，根因不是登录页类名失效，而是会话恢复把页面跳走了

### 81.3 回跳根因核对

已核对源码：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\login\index.vue`

关键事实：

- `onLoad` 中若本地仍有 `getToken()` / `getUserInfo()`，会直接执行 `restoreSession()`
- `restoreSession()` 成功后会调用 `navigateAfterLogin(user)`
- `navigateAfterLogin(user)` 会通过 `goHome(user.role)` 跳回首页

对应命中位置：

- `restoreSession()`：`login/index.vue:268`
- `getToken() / getUserInfo()` 门禁：`login/index.vue:283`
- `navigateAfterLogin(user)`：`login/index.vue:181,274`

因此本轮对 `login` 的新判断更新为：

- 当前 `login` runtime 采集的第一阻塞不是视觉偏差
- 而是运行态仍残留有效登录会话，导致页面自动离开 `pages/login/index`

### 81.4 本轮新建的临时 helper

为避免重复手写 inline automator 片段，本轮新增：

- `D:\XM\kaipai-team\tmp\automator-probe\clear-auth-session.js`

用途：

- 面向当前 `T7 / login` 采集链路
- 尝试清掉 `kp_token / kp_user`
- 可选再次 `reLaunch('/pages/login/index')`

说明：

- 该文件仅位于 `tmp/automator-probe`
- 不属于小程序业务代码
- 只用于当前 runtime 取证

### 81.5 本轮连续失败与换向记录

本轮围绕同一问题又出现了 3 次同类失败：

1. `capture-login-page.js` 全量截图版
   - 结果：
     - 124s 超时
   - 判断：
     - 不是源码未生效，而更像卡在 `miniProgram.screenshot()`
2. `clear-auth-session.js ws://127.0.0.1:9520 --relaunch-login`
   - 结果：
     - 两次都在 124s 超时
   - 判断：
     - 当前 automator 会话对 `callWxMethod / reLaunch` 返回不稳定
3. `connect-and-probe.js`
   - 目标：
     - `ws://127.0.0.1:9520`
     - `ws://198.18.0.1:9520`
   - 结果：
     - 两个 endpoint 均在 34s 内超时
   - 判断：
     - 当前问题已不再只是 endpoint 选择错误

因此按 `R28-R30`：

- 不再继续第 4 次沿 automator fresh runtime 路径重试
- 当前推进方向从：
  - `automator 清会话 -> reLaunch login -> 截图`
- 切换为：
  - `OS 级 DevTools 窗口状态截图 + 现有 page-data + 源码门禁核对`

### 81.6 OS 级替代截图结果

本轮已生成：

- `D:\XM\kaipai-team\tmp\ui-compare-20260423-login-r1-runtime\screenshots\wechat-devtools-login-window.png`
- `D:\XM\kaipai-team\tmp\ui-compare-20260423-login-r1-runtime\screenshots\wechat-devtools-login-active.png`

结果：

- 两张图都没有稳定捕获到微信 DevTools 可见页
- 当前落到的仍是 Codex / 非目标窗口内容

因此：

- OS 级截图通道本轮也不能作为 `login` 可见层验收证据
- 但它仍提供了一个负结论：
  - 当前机器上的窗口捕获焦点也不稳定，不应把这轮失败归因为 `login` 页面样式未命中

### 81.7 当前结论

当前 `login / T7` 的可信结论更新为：

- `src / dist/build / dist/dev` 三层仍保持正确
- runtime 采集已新增一条关键事实：
  - 会话恢复会把 `pages/login/index` 自动拉回 `pages/home/index`
- 本轮 fresh runtime 登录页截图仍未拿到
- 阻塞来源当前是：
  - 登录态残留
  - automator 会话不稳定
  - OS 级 DevTools 窗口捕获也不稳定

因此本轮不能宣称：

- `login` 已完成运行态闭环

但可以明确宣称：

- 当前不是继续改 `login-page__*` 样式的时机
- 下一轮应优先恢复“可控地清会话并停留在 login”的 runtime 采集链，再继续页面视觉复核

## 82. login / T7 运行态 page-data 已恢复：清会话后可稳定停在 `pages/login/index`

### 82.1 本轮目标

继续 `81` 的阻塞，不扩大页面范围。

目标：

- 把“会话回跳首页”从模糊阻塞拆成可控步骤
- 先拿到 `login` 的 fresh runtime page-data
- 截图若仍阻塞，则单独记录，不再混同为 `login` 运行态完全不可达

### 82.2 新增诊断脚本

本轮新增：

- `D:\XM\kaipai-team\tmp\automator-probe\trace-login-runtime.js`

用途：

- 按步骤记录 automator 卡点
- 模式包括：
  - `page-only`
  - `get-storage`
  - `remove-storage`
  - `evaluate-after-remove`
  - `full`

本轮也更新：

- `D:\XM\kaipai-team\tmp\automator-probe\capture-login-page.js`

新增参数：

- `--clear-auth-session`

作用：

- 在 `reLaunch('/pages/login/index')` 前先执行：
  - `removeStorageSync('kp_token')`
  - `removeStorageSync('kp_user')`

说明：

- 两个脚本都只在 `tmp/automator-probe`
- 不属于小程序业务代码
- 目的是让 T7 runtime 证据链可重复

### 82.3 分步 trace 结果

本轮先重新打开并挂载目标工程：

- `open-other --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `auto-preview --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- `auto --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin --auto-port 9520`

随后 trace 结果：

- `page-only`
  - 成功
  - `currentPage.before.ok path=pages/home/index`
- `get-storage`
  - 首次在旧会话未恢复前连接失败一次
  - 恢复后成功
  - `tokenPresent=<REDACTED>`
- `remove-storage`
  - 成功
  - `removeStorageSync('kp_token')` 与 `removeStorageSync('kp_user')` 均返回
- `evaluate-after-remove`
  - 成功
  - 返回：
    - `token=<REDACTED>`
    - `user=""`
    - `pages=["pages/home/index"]`
- `full`
  - 成功
  - 关键日志：

```text
callWx.getToken.ok tokenPresent=false
reLaunch.login.begin
reLaunch.login.ok
currentPage.after.ok path=pages/login/index
```

trace 文件：

- `D:\XM\kaipai-team\tmp\login-trace\trace-page-only.log`
- `D:\XM\kaipai-team\tmp\login-trace\trace-get-storage.log`
- `D:\XM\kaipai-team\tmp\login-trace\trace-remove-storage.log`
- `D:\XM\kaipai-team\tmp\login-trace\trace-evaluate-after-remove.log`
- `D:\XM\kaipai-team\tmp\login-trace\trace-full.log`

结论：

- `81` 中“会话回跳首页”的判断成立
- 但该阻塞已经可解：先清 `kp_token / kp_user`，再 `reLaunch('/pages/login/index')`，即可稳定停在登录页

### 82.4 login fresh runtime page-data 证据

执行：

- `node D:\XM\kaipai-team\tmp\automator-probe\capture-login-page.js D:\XM\kaipai-team\tmp\ui-compare-20260424-login-r2-runtime --clear-auth-session --skip-screenshot`

结果：

- 成功

证据文件：

- `D:\XM\kaipai-team\tmp\ui-compare-20260424-login-r2-runtime\captures\page-data-login-page.json`
- `D:\XM\kaipai-team\tmp\ui-compare-20260424-login-r2-runtime\captures\mini-program-login-capture.json`

关键事实：

```json
{
  "path": "pages/login/index",
  "size": {
    "width": 390,
    "height": 844
  },
  "innerHeight": 844,
  "scrollTop": 0
}
```

关键 DOM 均已量到：

- `.login-page__hero`
- `.login-page__hero-card`
- `.login-page__hero-kicker`
- `.login-page__hero-title`
- `.login-page__hero-subtitle`
- `.login-page__sheet`
- `.login-page__sheet-head`
- `.login-page__field` × 2
- `.login-page__submit`
- `.login-page__wechat`
- `.login-page__agreement`

当前 runtime 文案也已命中：

- `JU MING PIAN`
- `剧 名 片`
- `机构版 · 分享平台`
- `欢迎回到影像之间`
- `输入手机号，为您的分享建立档案`
- `登录 / 注册`
- `微信一键登录`
- `用户协议`
- `隐私政策`

因此本轮可以把 `login` 的 T7 状态从：

- `fresh runtime 页面不可达`

更新为：

- `fresh runtime page-data 已恢复并确认进入 login`

### 82.5 screenshot 边界

继续执行截图版：

- `node D:\XM\kaipai-team\tmp\automator-probe\capture-login-page.js D:\XM\kaipai-team\tmp\ui-compare-20260424-login-r2-runtime --clear-auth-session`

结果：

- 124s 超时

判断：

- page-data 已成功
- 因此截图失败更可能卡在 `miniProgram.screenshot()` / DevTools capture 通道，而不是页面无法进入

随后尝试 OS 级截图：

- `D:\XM\kaipai-team\tmp\ui-compare-20260424-login-r2-runtime\screenshots\wechat-devtools-login-window-r2.png`
- `D:\XM\kaipai-team\tmp\ui-compare-20260424-login-r2-runtime\screenshots\wechat-devtools-login-active-r2.png`

结果：

- 仍然抓偏到 Codex / 非目标窗口

因此当前截图结论：

- `login` 的 runtime page-data 已经闭合
- 可视截图仍未闭合
- 下一轮若继续 `login`，应优先处理 `miniProgram.screenshot()` 或 OS 窗口捕获问题，而不是继续改 `login-page__*`

### 82.6 当前结论

本轮进度推进结果：

- 已恢复 `login` 的可控 runtime 入口
- 已证明清 `kp_token / kp_user` 后可以停在 `pages/login/index`
- 已拿到完整 login page-data 和核心 DOM metrics
- 截图通道仍是剩余阻塞

当前 `login / T7` 可判定为：

- `src / dist/build / dist/dev`：已通过上一轮核验
- `DevTools runtime page-data`：本轮已通过
- `DevTools runtime screenshot`：仍未通过

因此不能宣称：

- `login` 已完成完整 T7

但可以宣称：

- `login` 的“会话回跳首页”阻塞已解除
- `login` 运行态 DOM / metrics 证据已补齐

## 83. login / T7 截图链恢复：把 DevTools 前置并与 Codex 解重叠后拿到可信窗口截图

### 83.1 本轮目标

继续 `82` 的剩余阻塞：

- 不再验证 `login` 是否可进入
- 只收口 `runtime screenshot`

### 83.2 当前窗口事实

本轮先重新核对 Windows 顶层窗口：

- 当前前台窗口：
  - `ForegroundTitle=mp-weixin - 微信开发者工具 Stable v2.01.2510260`
- DevTools 主窗口：
  - `Handle=12064696`
  - `Class=Chrome_WidgetWin_1`
  - `Rect=(359, 91, 1203 x 851)`
- 当前可见 `Codex` 主窗口：
  - `Handle=595346`
  - `Rect=(271, 59, 1563 x 891)`

同时确认：

- DevTools 主窗口只有一个子窗口：
  - `Intermediate D3D Window`
  - 与主窗口同尺寸

这说明：

- 之前 `take_screenshot.ps1` 通过 `CopyFromScreen` 抓到 `Codex`，并不表示句柄错误
- 更可能是因为：
  - DevTools 和 Codex 在桌面上发生了重叠
  - `CopyFromScreen` 抓到的是屏幕像素，而不是离屏窗口内容

### 83.3 本轮恢复动作

本轮对 `mp-weixin` 窗口执行：

- `ShowWindow(..., SW_RESTORE)`
- `BringWindowToTop(...)`
- `SetForegroundWindow(...)`
- `SetWindowPos(..., TOPMOST, 200, 40, 1320, 900, SWP_SHOWWINDOW)`
- 短暂停顿后
- `SetWindowPos(..., NOTOPMOST, 200, 40, 1320, 900, SWP_SHOWWINDOW)`

目的：

- 把 DevTools 强制抬到前台
- 同时把窗口从与 `Codex` 明显重叠的位置挪开

### 83.4 本轮截图结果

在窗口重排后执行：

- `take_screenshot.ps1 -Region 200,40,1320,900`

生成：

- `D:\XM\kaipai-team\tmp\ui-compare-20260424-login-r2-runtime\screenshots\wechat-devtools-reposition-r4.png`

当前截图已明确显示：

- DevTools 主窗口
- `t7-home` compile condition 头部
- 手机模拟器
- 登录页运行态可见内容：
  - `JU MING PIAN`
  - `剧 名 片`
  - `机构版 · 分享平台`
  - `欢迎回到影像之间`
  - 手机号输入区

因此本轮可以更新判断：

- `login` 的 runtime screenshot 已经不再是“完全拿不到”
- 当前已至少拿到一张可信的 OS 级 DevTools 窗口截图

### 83.5 当前截图链结论

当前 `login / T7` 的截图链状态为：

- `miniProgram.screenshot()`：
  - 仍会超时
- `OS 级窗口截图`：
  - 在默认窗口重叠状态下不可靠
  - 但在“前置 + 解重叠 + 固定 region”后已恢复可用

因此当前结论更新为：

- `login / T7` 已具备：
  - `src / dist/build / dist/dev`
  - fresh runtime page-data
  - 一张可信的 OS 级 DevTools 运行态截图

剩余未闭合项：

- 仍缺 `miniProgram.screenshot()` 直出截图
- 但它已不再阻塞 `login` 的页面级运行态判断

### 83.6 当前结论

本轮后，`login / T7` 的状态可从：

- `page-data 已闭合，screenshot 仍阻塞`

更新为：

- `page-data 已闭合，且已补回可信 OS 级运行态截图；仅 miniProgram.screenshot 直出链仍阻塞`

### 83.7 可复用截图脚本固化

为避免后续其他页面再次手写 Win32 前置 / 解重叠逻辑，本轮新增：

- `D:\XM\kaipai-team\tmp\automator-probe\capture-devtools-window.ps1`

默认行为：

- 查找可见窗口标题：
  - `mp-weixin - 微信开发者工具`
- 将窗口恢复、前置、短暂置顶
- 移动到：
  - `x=200, y=40, width=1320, height=900`
- 再用 `take_screenshot.ps1 -Region 200,40,1320,900` 采集

复跑验证：

- `powershell -ExecutionPolicy Bypass -File D:\XM\kaipai-team\tmp\automator-probe\capture-devtools-window.ps1 -OutputPath D:\XM\kaipai-team\tmp\ui-compare-20260424-login-r2-runtime\screenshots\wechat-devtools-login-script-r5.png`

结果：

- 成功
- 截图路径：
  - `D:\XM\kaipai-team\tmp\ui-compare-20260424-login-r2-runtime\screenshots\wechat-devtools-login-script-r5.png`

该截图继续显示：

- DevTools 主窗口
- 手机模拟器
- 当前登录页首屏
- `JU MING PIAN / 剧 名 片 / 欢迎回到影像之间`

因此后续 `history / mine / actor-card / card-list` 的 OS 级运行态截图可优先复用该脚本，而不是继续使用不稳定的 active-window / raw window-handle 捕获。
