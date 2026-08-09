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
  -> 当前 mine-v2 展示资料卡 + 完整度 + 统计 + 两组入口
  -> 资料卡等账号入口先检查全局 Session，游客直接 navigateTo 登录页
  -> 不先创建 actor-profile/edit，避免与页面守卫 reLaunch 形成导航竞态

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
  - 保持页面展示阶段不调用 `ensureUserSessionReady()`，游客可以直接查看个人中心。
  - 使用 `userStore.hasStoredSession / currentUser` 派生 `isVisitor`、账号名称、头像与认证状态。
  - 使用 `formatPhone()` 作为已登录无昵称时的账号名称 fallback。
  - 新增 `requireLoginForMineAction()` 与 `openAccountCapability()`，六个账号入口统一先门禁再导航。
  - 游客登录分支只调用一次 `uni.navigateTo('/pages/login/index')`，不使用会清空页面栈的 `goLogin() / reLaunch`。
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

## 4. 个人中心游客态与入口门禁

当前 `mine-v2` 页面没有独立登录卡，游客与已登录用户共用资料卡、完整度、统计区、演员资料和账户与服务结构。页面头部直接消费全局 Session：

```ts
const currentUser = computed(() => userStore.currentUser);
const isVisitor = computed(() => !userStore.hasStoredSession);
const displayName = computed(() => {
  if (isVisitor.value) return '未登录用户';
  return currentUser.value?.nickname
    || formatPhone(currentUser.value?.phone || '')
    || '演员用户';
});
```

需要账号的交互统一先过 Mine 入口门禁：

```ts
function requireLoginForMineAction(): boolean {
  if (isVisitor.value) {
    uni.navigateTo({ url: '/pages/login/index' });
    return false;
  }
  return true;
}

function openAccountCapability(url: string): void {
  if (!requireLoginForMineAction()) return;
  uni.navigateTo({ url });
}
```

覆盖范围包括 `.mine-v2__profile-card`、“继续完善”、“个人资料”、“演艺经历”、“自我介绍”和“实名认证”。点击处理函数返回 `void`，不把 `uni.navigateTo()` Promise 暴露给 Vue 原生事件处理器。

受保护页仍保留 `ensureUserSessionReady()` 作为直接深链兜底。Mine 常规游客点击必须在创建受保护页之前截断，页面栈由 `pages/mine/index` 直接变为 `pages/login/index`。

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
- `.mine-v2__profile-card`：游客显示“未登录用户”，整卡保持可点击；不改变用户已指定的头部胶囊对齐和页面布局。
- 游客态页面继续渲染 `.mine-v2__completeness-card`、`.mine-v2__stats-row` 和两组 `.mine-v2__section-group`。
- 颜色沿用登录页当前黑白米色系，不引入平台品牌色。

_Requirements: 3.1, 3.2_

## 7. 个人中心复核口径

`00-189` 已覆盖：

- 目标：`11-pages-mine-index-default`
- 页面：`pages/mine/index`
- 流程：`mine`
- 截图：`screenshots/11-pages-mine-index-default.png`

`00-190` 只补明确说明，不重复截图全量页面。复核区域包括：

- 个人资料：头像、昵称 / 脱敏手机号 fallback、角色与认证状态、整卡编辑入口。
- 完整度：百分比、进度条和“继续完善”。
- 统计区：演员卡、素材和浏览。
- 演员资料：个人资料、演艺经历、自我介绍。
- 账户与服务：实名认证、帮助与反馈、设置；退出登录仅已登录展示。

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
- 源码和构建产物包含当前 `.mine-v2__profile-card / __completeness-card / __stats-row / __section-group` 结构。
- Mine 消费 `hasStoredSession / currentUser`，已登录无昵称时使用 `formatPhone()`，游客才显示“未登录用户”。
- 六个受保护入口统一调用 `openAccountCapability()`；不得存在写死受保护 URL 的直接 `uni.navigateTo()`。
- 游客登录分支使用单次 `navigateTo('/pages/login/index')`，不调用 `goLogin() / reLaunch`。
- 构建产物 Mine JS 不包含 `ensureUserSessionReady`，但必须包含全局 Session 状态和直接登录门禁语义。

_Requirements: 3.3_
