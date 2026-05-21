# 00-70 设计说明

## 1. 设计目标

把 `00-69` 已定义好的“当前 active 架构”，进一步落成一套可见层统一原型实现：

1. 先统一前 5 个高频入口页的视觉语言
2. 再继续收口 2 个预览页
3. 整个过程不破坏当前真实接口、分享路径和状态链路

## 2. 设计原则

- 先保留真实逻辑，再重写模板和样式
- 先统一高频入口，再推进预览页
- 原型是视觉与结构参考，不是新静态页面
- 单页重做必须服从 `00-69` 的 active 路由架构
- 任何原型落地都不能回退到 mock 或假数据

## 3. 原型页与真实路由映射

| 原型页 | 真实落点 | 当前状态 | 说明 |
|--------|----------|----------|------|
| 登录 / 注册 | `pages/login/index.vue` | 已首轮落地 | 改为海报式首屏 + 浅色表单层，保留手机号 / 微信 / 协议逻辑 |
| 首页 | `pages/home/index.vue` | 已首轮落地 | 改为“三栏风格分馆 + 快速开始 + 默认卡” |
| 记录 | `pages/history/index.vue` | 已首轮落地 | 改为筛选胶囊 + 封面卡 + 再次进入 |
| 我的 | `pages/mine/index.vue` | 已首轮落地 | 改为“我的工作台 + 账号状态” |
| 创建分享页 | `pkg-card/card-list/index.vue` | 已首轮落地 | 改为风格卡管理 + 分享操作 |
| 卡片预览 | `pages/actor-profile/detail.vue` | 已首轮落地 | 已从旧演员详情叙事推进到卡片预览叙事，后续仅需按真机运行态继续微调 |
| 海报预览 | `pkg-card/actor-card/index.vue` | 已首轮落地 | 已从旧编辑器叙事推进到分享预览 / 海报预览叙事，后续仅需按真机运行态继续微调 |

### 3.1 原型外但仍需统一的页面

| 页面 | 真实落点 | 当前状态 | 说明 |
|------|----------|----------|------|
| 工具页 | `pkg-tools/webview/index.vue`、`pkg-tools/video-player/index.vue` | 已同步收口 | 不在 `_-_.html` 的 7 页里，但仍是 active 路由，必须与主链保持同一视觉系统 |
| 档案编辑 | `pages/actor-profile/edit.vue` | 已同步收口 | 不在 `_-_.html` 的 7 页里，但仍是当前 active 主链页面，必须统一视觉系统 |
| 实名认证 | `pkg-card/verify/index.vue` | 已同步收口 | 属于当前分享主链的兼容支撑页，不能继续保留旧深色玻璃拟态 |
| 身份补全兼容页 | `pages/role-select/index.vue` | 已同步收口 | 属于历史兼容页，虽非主入口，但必须保持与当前主链同一视觉语言 |

## 4. 视觉系统

### 4.1 页面基调

统一采用以下设计基线：

- 背景：暖米白渐变
- 信息层：半透明浅色卡
- 封面块：深色、高圆角、弱纹理
- 字体层级：大标题 + 细字间距 eyebrow + 低对比辅助文案
- tabbar：浅底 + 深色选中态

### 4.2 页面结构模式

#### 4.2.1 顶部

统一模式：

- 状态栏 / capsule spacer
- 微型标签（如 `SCREEN 02 · HOME`）
- 大标题
- 一段低对比说明

#### 4.2.2 中间内容区

统一使用：

- 圆角卡片分区
- 低密度信息布局
- 单个分区只承载一个清晰语义

#### 4.2.3 底部

- tab 页面统一走浅色 tabbar
- 非 tab 页统一走卡片式底部操作栏或单主按钮

## 5. 实现策略

### 5.1 首轮实现方式

首轮不改 API 和 store，只改：

- `<template>`
- `<style scoped>`
- 极少量与结构相关的 `computed` / 辅助字段

### 5.2 保持不动的运行时层

以下逻辑必须保留：

- 登录 / 注册 / 微信登录
- `shareCardId-first` 路由和 helper
- 分享卡列表读取与建卡
- 历史读取与再次进入
- 分享海报生成
- 用户会话同步

### 5.3 预览页后续实现方式

卡片预览与海报预览不直接新建页面，而是在现有页面上改叙事层：

- `pages/actor-profile/detail.vue`
  - 当前是公开详情页
  - 后续需要增强“卡片预览”语义
- `pkg-card/actor-card/index.vue`
  - 当前偏编辑页
  - 后续需要把“分享预览 / 海报切换 / 快速编辑”表达提升为主视觉

## 6. 与 00-69 的边界

### 6.1 00-69 负责什么

- 定义 active 架构
- 定义旧页面删除边界
- 定义后台 / 后端收口方向

### 6.2 00-70 负责什么

- 把 `00-69` 允许保留的 active 页面真正改成原型视觉
- 明确“7 页原型 -> 真实页面”的实现关系
- 记录本轮已经落地到什么程度

因此：

- 00-69 是“架构边界”
- 00-70 是“可见层落地”

## 7. 当前影响文件

### 已落地

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\login\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\history\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\mine\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\edit.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\verify\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\role-select\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-tools\webview\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-tools\video-player\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages.json`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\contacts\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\my-applies\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\role-detail\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\apply-confirm\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\apply-detail\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\apply-manage\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\project\create.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\project\role-create.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\company-profile\edit.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\membership\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\invite\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\fortune\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpButton.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpEmpty.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpInviteSummaryCard.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpShareArtifactTabs.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpPillSelector.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpConfirmDialog.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpCapabilityMatrixCard.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpThemePreviewCard.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpLevelProgressCard.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpStatusTag.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpFilterBar.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpTag.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\styles\_tokens.scss`
- `D:\XM\kaipai-team\kaipai-frontend\src\styles\_mixins.scss`
- `D:\XM\kaipai-team\kaipai-frontend\src\utils\level.ts`
- `D:\XM\kaipai-team\kaipai-frontend\src\utils\personalization.ts`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpStatusTag.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpTag.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpColorPalettePicker.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpMineMenuItem.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpSectionHead.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-poster.ts`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpCard.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpInput.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpTextarea.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\history\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\mine\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\detail.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`

### 剩余边界

- 当前仓内 page 文件已经全部完成 source-level UI 收口。
- 当前高频共享组件也已完成 source-level 视觉收口，不再继续把旧橙色品牌按钮 / 胶囊 / 空状态卡片带回新页面。
- 当前全局 token、通用 mixin 和个性化卡片默认 theme fallback 也已切到同一套暖米白 / 深色封面块体系。
- 当前 success / warning / danger / info 也已切到低饱和辅助色，不再保留系统绿红蓝黄的强烈跳色。
- 当前冷蓝灰辅助色也已继续暖化，默认 side chip / palette input / mine menu 箭头不再跳出参考稿色系。
- 当前主文字色也已从冷黑切到深棕黑，页面正文与卡片默认主题进一步贴近 `_-_.html`。
- 当前全局暗色 header、暗色卡片和通用输入组件的底色也已暖化，不再残留冷黑工具风。
- 当前 active 页面本身也在继续从“信息卡管理页”往“编辑感预览页”推进，section head / 场景状态 / 默认卡提示 / 公开卡片说明都更接近原型稿。
- 但 `pages.json` 当前只保留 active 路由与必要分包，因此 `contacts / apply-* / project/* / company-profile/edit / membership / invite / fortune` 这批旧页面不会进入当前微信小程序构建产物。
- 因此这批旧页面的本轮验证边界是：源码样式收口 + `vue-tsc` 通过；真正的 `dist/build` / `dist/dev` 可视化验证仍只覆盖当前 active 页面。

## 8. 风险控制

- 不允许为了视觉对齐而删掉真实交互逻辑
- 不允许为了快速还原原型而绕开当前路由 / helper / API
- 旧页面若当前未挂入 `pages.json`，不得为了做 UI 复核而直接回挂到 active 架构
