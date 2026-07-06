# 00-190 当前阶段小程序登录返回与个人中心复核补充 - 技术设计

## 1. 设计结论

本轮采用最小补充：

```text
登录页本地返回按钮
  -> 与微信胶囊按钮共用顶部导航层
  -> backButtonStyle 复用胶囊 top / height
  -> navigateBack 优先，失败或无历史栈则 reLaunch 首页

个人中心复核
  -> 复用 00-189 已生成的 mine 流程与截图证据
  -> 在 00-190 execution 中明确记录查看范围
  -> 未登录点击底部“我的”停留在个人中心
  -> 游客态展示登录卡 + 数据区 + 快捷入口 + 设置项，点击账号功能再登录

验收脚本
  -> 源码 + dist/build + dist/dev 三层检查登录返回按钮
  -> 检查 mine 页未登录可浏览、00-189 mine 流程矩阵和截图证据
```

_Requirements: 3.1, 3.2, 3.3_

## 2. 文件边界

- `kaipai-frontend/src/pages/login/index.vue`
  - 新增本地 `.login-page__topbar` 与 `.login-page__back`。
  - 新增 `handleBack()`。
  - 复用 `getFloatingBackNavStyles()` 的 `backButtonStyle`，让返回按钮与右侧微信胶囊保持同一横向导航层。
  - 不引入共享 `KpFloatingBackButton`，避免深色浮动按钮样式直接进入登录入口页。
- `kaipai-frontend/src/pages/mine/index.vue`
  - 移除页面展示阶段的 `ensureUserSessionReady()` 强登录守卫。
  - 使用 `userStore.bootstrapSession()` 只恢复已有会话；无 token / 无用户时停留游客态。
  - 新增 `isVisitor`、`showMineContent`、`resetVisitorMinePage()` 与 `requireLoginForMineAction()`。
  - 游客态展示 `mine-page__login-card`，并继续展示数据区、快捷入口和设置项；账号功能点击时再调用 `goLogin()`。
- `.sce/specs/00-190-current-phase-miniapp-login-back-and-mine-review-supplement/scripts/verify-miniapp-login-back-and-mine-supplement.mjs`
  - 作为本轮 TDD 验收脚本。
- `00-190 execution.md`
  - 记录红灯、实现、构建和个人中心复核范围。

_Requirements: 3.1, 3.2, 3.3_

## 3. 登录页模板结构

顶部导航层包住 `KpCapsuleSpacer` 和本地返回按钮：

```vue
<view class="login-page__topbar">
  <KpCapsuleSpacer />
  <view class="login-page__back" :style="backButtonStyle" aria-label="返回" @click="handleBack">
    <view class="login-page__back-icon" />
    <text class="login-page__back-text">返回</text>
  </view>
</view>
```

`KpCapsuleSpacer` 继续撑开顶部安全区，返回按钮在该 topbar 内绝对定位到左侧，`top / height` 与胶囊按钮来自同一个 `getFloatingBackNavStyles()` 计算结果。按钮只占左侧区域，不覆盖右侧胶囊按钮。

_Requirements: 3.1_

## 4. 个人中心游客态结构

`pages/mine/index` 的根因是 `onShow -> hydrateMinePage -> ensureUserSessionReady()`，未登录时该工具函数会立即 `reLaunch('/pages/login/index')`。本轮改为：

```ts
async function hydrateMinePage(): Promise<void> {
  const user = await userStore.bootstrapSession();
  if (!user) {
    resetVisitorMinePage();
    return;
  }
  // 已登录后再同步演员运行态和账号数据
}
```

游客态模板先展示登录卡片，但不把后续个人中心内容排除掉：

```vue
<template v-if="isVisitor">
  <view class="mine-page__login-card" @click="goLogin">
    <text class="mine-page__login-title">登录后查看账号数据</text>
    <text class="mine-page__login-desc">可继续管理作品集、联系申请、收藏内容和偏好设置。</text>
    <view class="mine-page__login-action">
      <text>登录 / 注册</text>
    </view>
  </view>
</template>
```

后续主内容使用 `showMineContent` 控制：

```ts
const showMineContent = computed(() => isVisitor.value || userStore.isActor);
```

```vue
<template v-if="showMineContent">
  <view class="mine-page__analytics">...</view>
  <view class="mine-page__quick-grid">...</view>
  <view class="mine-page__settings">...</view>
</template>
```

需要账号的交互统一先过：

```ts
function requireLoginForMineAction(): boolean {
  if (!userStore.isLoggedIn || !userStore.userInfo) {
    goLogin();
    return false;
  }
  return true;
}
```

覆盖范围包括头像/编辑入口、登录卡、创建分享、我的二维码、作品集、联系申请、收藏、通知和偏好设置。退出登录只在已登录时展示。

_Requirements: 3.2_

## 5. 返回逻辑

```ts
function handleBack(): void {
  const pages = getCurrentPages();
  if (pages.length > 1) {
    uni.navigateBack({
      fail: () => {
        uni.reLaunch({ url: '/pages/home/index' });
      },
    });
    return;
  }
  uni.reLaunch({ url: '/pages/home/index' });
}
```

该逻辑保证从首页进入登录页时返回上一页；如果登录页作为冷启动 / 分享参数直达页打开，则回首页。

_Requirements: 3.1_

## 6. 样式设计

- `.login-page__topbar`：顶部导航相对定位容器，内部保留 `KpCapsuleSpacer` 的安全区高度。
- `.login-page__back`：绝对定位在 `left: 32rpx`，`top / height` 由 `backButtonStyle` 注入，与胶囊按钮同一行；浅色半透明底，圆形左箭头 + “返回”文本。
- `.login-page__stage`：顶部 padding 保持 `2vh`，登录内容从顶部导航层之后开始，不再被额外返回按钮行向下挤压。
- `.mine-page__login-card`：复用个人中心卡片语义，展示游客态说明和“登录 / 注册”按钮。
- 游客态页面继续渲染 `.mine-page__analytics`、`.mine-page__quick-grid` 和 `.mine-page__settings`，避免登录卡下方出现大块空白。
- 颜色沿用登录页当前黑白米色系，不引入平台品牌色。

_Requirements: 3.1, 3.2_

## 7. 个人中心复核口径

`00-189` 已覆盖：

- 目标：`11-pages-mine-index-default`
- 页面：`pages/mine/index`
- 流程：`mine`
- 截图：`screenshots/11-pages-mine-index-default.png`

`00-190` 只补明确说明，不重复截图全量页面。复核区域包括：

- 个人资料：头像 / 昵称 / ID / 编辑入口。
- 我的数据：分享数、打开数、趋势条、卡片 / 海报 / 再进入摘要。
- 快捷入口：创建分享、我的二维码。
- 设置项：作品集、联系申请、收藏、通知、偏好设置。
- 账号操作：退出登录。

_Requirements: 3.2_

## 8. 验证设计

必须执行：

1. 红灯：`node .sce/specs/00-190-current-phase-miniapp-login-back-and-mine-review-supplement/scripts/verify-miniapp-login-back-and-mine-supplement.mjs`，预期在实现前失败。
2. 实现登录页返回按钮。
3. `cd kaipai-frontend && npm run type-check`
4. `cd kaipai-frontend && npm run build:mp-weixin`
5. 绿灯：执行 00-190 验收脚本。
6. 执行 00-187 登录门禁脚本。
7. 执行 00-188 复审合规脚本。
8. `cd kaipai-frontend && npm run audit:mp-package`

用户截图补充后，00-190 验收脚本继续检查返回按钮必须在 `login-page__topbar` 内，并通过 `backButtonStyle` 与胶囊行对齐；不允许回退成 `KpCapsuleSpacer` 下方另起一行。

用户补充“点击底部我的不应直接跳登录”后，00-190 验收脚本继续检查：

- `pages/mine/index` 不再导入或调用 `ensureUserSessionReady`。
- 源码和构建产物包含 `mine-page__login-card`、“登录后查看账号数据”和“登录 / 注册”。
- 源码和构建产物在游客登录卡之后仍包含 `mine-page__analytics`、`mine-page__quick-grid` 与 `mine-page__settings`。
- 构建产物 mine JS 不再在页面展示阶段调用强登录守卫，仅保留账号动作触发 `goLogin()`。

_Requirements: 3.3_
