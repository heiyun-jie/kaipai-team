# 00-212 当前阶段小程序导航标题与返回按钮统一收口 - 技术设计

## 1. 路由配置

本轮**不改动** `pages.json`。20 页登记、`navigationStyle: custom`、`subPackages` 结构、`tabBar` 4 项全部保持现状。

所有涉及页面均已是 `navigationStyle: custom`，自定义导航是既有前提，不需要新增配置。

_Requirements: 4, 5_

## 2. 依赖清单

### 2.1 复用既有

| 模块 | 提供能力 | 本轮角色 |
|------|---------|---------|
| `@/utils/floating-back-nav` → `getFloatingBackNavStyles()` | 由 `uni.getMenuButtonBoundingClientRect()` 派生 `navStyle.height`（胶囊底边）与 `backButtonStyle.top/height`（胶囊自身位置） | 唯一定位数据源，不改实现 |
| `@/components/KpCapsuleSpacer.vue` | 消费 `navStyle`，撑出胶囊高度占位块 | 由 `KpPageNav` 内部持有 |

### 2.2 新增

| 文件 | 说明 |
|------|------|
| `src/components/KpPageNav.vue` | 唯一导航契约组件：占位 + 胶囊带对齐 + 返回箭头 + 标题 + 右侧插槽 |
| `scripts/verify-miniapp-nav-title-unification.mjs` | §3.5 回归门禁 |

### 2.3 关键约束

`getFloatingBackNavStyles()` 内部调用 `uni.getSystemInfoSync()` 与 `uni.getMenuButtonBoundingClientRect()`，**必须在组件 setup 期同步取值**，不能提到模块顶层——模块顶层求值时机早于小程序运行时 API 可用时机。既有 `KpCapsuleSpacer` 已是此形态，`KpPageNav` 沿用。

_Requirements: 3.4_

## 3. 页面状态定义

`KpPageNav` 为无内部业务状态的展示组件。

```ts
interface Props {
  title?: string;        // 导航标题；空则不渲染标题节点
  showBack?: boolean;    // 默认 true
}
// emits: (event: 'back'): void
// slots: default —— 导航行内标题右侧的附加内容（step-visual 曾用于进度条，本轮已移出）
```

组件内部：

```ts
const { navStyle, backButtonStyle } = getFloatingBackNavStyles();
```

`navStyle` 用于占位块，`backButtonStyle` 用于导航行定位。二者取自同一次调用，保证同一帧内数值自洽。

调用方**不持有**任何定位状态。9 个 `pkg-actor-card` 页面改造后删除各自的 `getFloatingBackNavStyles` 导入与 `backButtonStyle` 局部变量。

_Requirements: 3.4_

## 4. 模板结构

### 4.1 `KpPageNav` 组件结构

```vue
<view class="kp-page-nav">
  <view class="kp-page-nav__spacer" :style="navStyle" />
  <view class="kp-page-nav__row" :style="{ top: backButtonStyle.top, height: backButtonStyle.height }">
    <text v-if="showBack" class="kp-page-nav__back" @click="emit('back')">‹</text>
    <text v-if="title" class="kp-page-nav__title">{{ title }}</text>
    <slot />
  </view>
</view>
```

外层 `.kp-page-nav` 承担 `position: relative`，把定位上下文收进组件内部——这是相对 `00-207` 做法的改进点：调用方 `__header` 不再需要记得写 `position: relative`，漏写导致定位逃逸到页面根节点的失败模式被结构性消除。

### 4.2 缺陷态 → 目标态（以 `step-visual` 为例）

改造前（模式 D，`__nav` 走流式布局，胶囊带空置）：

```vue
<view class="step-visual__header">
  <KpCapsuleSpacer />
  <view class="step-visual__nav">
    <text class="step-visual__back" @click="goBack">‹</text>
    <text class="step-visual__title">主视觉照片</text>
    <view class="step-visual__prog-bar">…</view>
  </view>
</view>
<scroll-view class="step-visual__body">
  <text class="step-visual__h1">主视觉照片</text>   <!-- 与导航标题完全重复 -->
  <text class="step-visual__sub">选择风格与背景…</text>
```

改造后：

```vue
<view class="step-visual__header">
  <KpPageNav title="主视觉照片" @back="goBack" />
  <view class="step-visual__prog-row">
    <view class="step-visual__prog-bar"><view class="step-visual__prog-fill" style="width:14.3%" /></view>
  </view>
</view>
<scroll-view class="step-visual__body">
  <text class="step-visual__sub">选择风格与背景…</text>
```

### 4.3 12 页改造映射

| 页面 | 导航标题 | 返回 | 正文 `__h1` 处置 |
|------|---------|------|-----------------|
| `pages/home/index` | `开拍了演员卡` | 无（Tab 根页） | 不涉及 |
| `pages/card-list/index` | `名片夹` | 无（Tab 根页） | 不涉及 |
| `pages/mine/index` | `个人` | 无（Tab 根页） | 不涉及 |
| `pkg-actor-card/create` | `AI 创建演员卡` | 有 | 无 `__h1`，`__progress-row` 原样保留 |
| `pkg-actor-card/step-visual` | `主视觉照片` | 有 | **删**（完全重复）+ 进度条移出导航 |
| `pkg-actor-card/step-profile` | `个人资料` | 有 | **删**（完全重复） |
| `pkg-actor-card/step-works` | `参演作品` | 有 | 保留 `选择参演作品`（措辞不同） |
| `pkg-actor-card/step-photos` | `生活照片` | 有 | 保留 `添加生活照片`（措辞不同） |
| `pkg-actor-card/step-video` | `视频简历` | 有 | **删**（完全重复） |
| `pkg-actor-card/step-attachment` | `附件简历` | 有 | **删**（完全重复） |
| `pkg-actor-card/step-settings` | `生成设置` | 有 | **删**（完全重复） |
| `pkg-actor-card/generate` | `生成演员卡` | 有（文案 `‹ 修改`） | 无 `__h1` |

`generate` 的返回文案为 `‹ 修改` 且 `__title` 原本 `text-align: center`。改造时返回文案通过 `showBack` + 页面侧自定义处理，或保留其局部返回节点；居中语义在 `KpPageNav` 内不作为默认行为，避免与其余 11 页左对齐标题冲突。**该页作为唯一特例，实现时需单独确认视觉未回归。**

_Requirements: 3.1, 3.2, 3.3, 3.4_

## 5. 交互逻辑

### 5.1 返回

`KpPageNav` 只 `emit('back')`，不自行调用 `uni.navigateBack()`。理由：`actor-profile/edit` 一类页面存在「离开前确认」拦截（`requestLeave`），把导航动作固化进组件会剥夺调用方的拦截能力。9 个 `pkg-actor-card` 页面的 `goBack` 实现保持原样。

### 5.2 定位计算

不引入新计算。`right: 200rpx` 的胶囊避让沿用 `00-207 §3.1` 已验证数值，收敛进组件样式，页面侧不再出现该魔数。

### 5.3 脱离文档流后的间距补偿

导航行 `position: absolute` 后不再占据高度，垂直空间由 `.kp-page-nav__spacer` 的 `navStyle.height`（= 胶囊底边）承担。原先写在页面 `__nav` 上的 `padding: 8rpx 24rpx 16rpx` 中的**下内边距**随节点一起消失，必须由紧随其后的元素补回：

| 页面 | 补偿承担者 |
|------|-----------|
| `step-visual` | 新增 `__prog-row` 的 `padding` |
| `create` | 既有 `__progress-row` 的 `margin-top` |
| 其余 7 页 | `__header` 的 `padding-bottom` |

这与 `00-207 §3.1` 对 `home` / `card-list` / `mine` 的处理同构（分别由 `__greeting` / `__tabs` 的 `margin-top` 与 `__header` 的 `padding-bottom` 承担）。

_Requirements: 3.1, 3.2, 3.3_

## 6. 生命周期

不改动任何页面的 `onMounted` / `onShow` / `onPullDownRefresh`。`KpPageNav` 在 setup 期一次性取定位值，无监听、无定时器、无清理需求。

横屏旋转与字号无障碍缩放场景下胶囊位置变化不会触发重算——此为 `getFloatingBackNavStyles()` 的既有行为，本轮不扩大范围，记录为已知边界。

_Requirements: 4_

## 7. 页面跳转关系

不变。9 个向导页的 `uni.navigateTo` 链路（`create` → `step-visual` → `step-profile` → … → `generate`）与各页 `uni.navigateBack()` 行为完全保持。

_Requirements: 4_

## 8. 关键样式

```scss
.kp-page-nav {
  position: relative;                 // 定位上下文收进组件，调用方无需感知
  width: 100%;

  &__spacer { width: 100%; pointer-events: none; }

  &__row {
    position: absolute;
    left: 32rpx;
    right: 200rpx;                    // 胶囊避让，沿用 00-207 已验证值
    display: flex;
    align-items: center;
    gap: 12rpx;
  }

  &__back { font-size: 44rpx; color: #20242c; padding: 0 8rpx; }
  &__title { font-size: 32rpx; font-weight: 600; color: #171a21; }
}
```

页面侧删除的样式：9 页各自的 `&__nav` / `&__back` / `&__title`，5 页的 `&__h1`，`step-visual` 的 `__title { flex: 1 }`。

**不得删除**：`step-works` / `step-photos` 的 `&__h1`（措辞不同，仍在使用）。

_Requirements: 3.1, 3.2, 3.3, 3.4_

## 9. 本轮不改动的边界

| 对象 | 原因 |
|------|------|
| 模式 B 三页（`actor-profile/edit` / `pkg-profile/import-review` / `pkg-profile/assets`） | 采用 `KpFloatingBackButton`（`position: fixed`）+ `__nav-title` 绝对居中（`left/right: 160rpx`）+ `__nav` `position: sticky`。居中语义与 sticky 吸顶均与 `KpPageNav` 的左对齐、非吸顶模型不同构，合并需独立视觉评估 |
| 模式 C 三页（`pkg-card/verify` / `pkg-tools/webview` / `pkg-tools/video-player`） | 深色 Hero 页，标题在 Hero 正文内，导航行本就不承载标题；属 `SHARED_CONVENTIONS.md` 页面类型 A 的既有策略 |
| `pages/login/index` | 使用 `KpCapsuleSpacer` + `backButtonStyle`，但无导航标题行，不在缺陷面内 |
| `pages/assets/index` | 纯 `redirectTo` 跳板页，无渲染内容 |
| `KpFloatingBackButton` 组件本体 | 模式 B / C 共 6 页在用，本轮不动 |
| 后端、数据库、`pages.json` | 本轮无授权改动 |

_Requirements: 3.4, 5_

## 10. 文档同步项

落地后必须同步：

- `SHARED_CONVENTIONS.md:22` — `KpNavBar` 在 `00-209` 后已不存在，校正为 `KpPageNav`
- `SHARED_CONVENTIONS.md:85-93` — 「页面本地实现，不依赖共享导航组件」需限定为仅适用深色 Hero 页；胶囊带标题型页面改为统一走 `KpPageNav`
- `.sce/specs/README.md` — 登记 `00-212`
- `.sce/specs/spec-code-mapping.md` — 登记 `KpPageNav` 与 12 页映射
- `.sce/steering/CURRENT_CONTEXT.md` — 主线追加 `00-212`

_Requirements: 5_
