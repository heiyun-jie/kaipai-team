# 全局样式系统 - 技术设计

## 1. 架构概览

全局样式系统采用分层架构，自底向上为：

```
src/styles/
├── _tokens.scss          # Design Tokens 变量定义（全局注入）
├── _mixins.scss          # Mixin 工具库（全局注入）
├── _reset.scss           # CSS Reset + 基础样式
├── _page-layout.scss     # 深-浅双层页面骨架
├── _uview-theme.scss     # uview-plus 主题变量覆盖
└── index.scss            # 入口文件，汇总导入 reset + page-layout + uview-theme
```

注入方式：

- `_tokens.scss` 和 `_mixins.scss` 通过 `vite.config.ts` 的 `css.preprocessorOptions.scss.additionalData` 注入，所有 `.vue` / `.scss` 文件自动可用
- `index.scss` 在 `App.vue` 中通过 `@import` 引入，作为全局生效样式

## 2. 核心实现原则

_Requirements: 3.1, 3.2, 3.3, 3.4_

1. **Token 驱动**：所有视觉属性值必须引用 `$kp-*` 变量，禁止硬编码 hex/rpx 值
2. **Mixin 封装复杂性**：`backdrop-filter` 兼容性、多行截断、安全区等复杂逻辑封装为 Mixin，调用方无需关心实现细节
3. **语义化 Class**：页面骨架提供 `.kp-page`、`.kp-header`、`.kp-content`、`.kp-card` 等语义化 class，开发者按约定组合即可
4. **渐进增强**：玻璃拟态效果使用 `@supports` 检测，不支持时优雅降级为纯色背景
5. **小程序优先**：所有 CSS 特性以微信小程序支持度为基准，避免使用不兼容属性

## 3. 文件结构

```
src/
├── styles/
│   ├── _tokens.scss          # 颜色、字体、间距、圆角、阴影、动画变量
│   ├── _mixins.scss          # 玻璃拟态、文字截断、安全区、渐变等 Mixin
│   ├── _reset.scss           # 全局 Reset + 基础排版
│   ├── _page-layout.scss     # .kp-page / .kp-header / .kp-content 骨架
│   ├── _uview-theme.scss     # uview-plus 主题变量覆盖
│   └── index.scss            # @import 汇总入口
├── App.vue                   # @import '@/styles/index.scss'
vite.config.ts                # additionalData 注入 _tokens + _mixins
```

## 4. Design Tokens 完整定义

> 文件路径：`src/styles/_tokens.scss`

```scss
// ============================================================
// KaiPai Design Tokens — Cinematic Glassmorphism
// ============================================================

// ------------------------------------------------------------
// 1. 颜色 — 深色系 (Dark Palette)
// ------------------------------------------------------------
$kp-color-dark-primary:    #121214;   // 沉浸式黑 — 头部/主区域
$kp-color-dark-secondary:  #1A1A1E;   // 深色辅助
$kp-color-dark-tertiary:   #2C2C30;   // 深色三级（分割/描边）

// ------------------------------------------------------------
// 2. 颜色 — 品牌色 (Brand)
// ------------------------------------------------------------
$kp-color-primary:         #FF6B35;   // Spotlight Orange
$kp-color-primary-light:   rgba(255, 107, 53, 0.1);  // Orange 浅底
$kp-color-primary-dark:    #E55A2B;   // Orange 按压态

// ------------------------------------------------------------
// 3. 颜色 — 内容区 (Content Area)
// ------------------------------------------------------------
$kp-color-bg:              #F8F9FA;   // 页面/内容区背景
$kp-color-card:            #FFFFFF;   // 卡片背景
$kp-color-glass:           rgba(255, 255, 255, 0.7);  // 玻璃拟态背景

// ------------------------------------------------------------
// 4. 颜色 — 语义色 (Semantic)
// ------------------------------------------------------------
$kp-color-success:         #52C41A;
$kp-color-warning:         #FAAD14;
$kp-color-danger:          #FF4D4F;

// ------------------------------------------------------------
// 5. 颜色 — 文字 (Typography Colors)
// ------------------------------------------------------------
// 深色背景上的文字
$kp-color-text-dark-primary:   #FFFFFF;
$kp-color-text-dark-secondary: rgba(255, 255, 255, 0.6);

// 浅色背景上的文字
$kp-color-text-primary:    #1A1A1A;
$kp-color-text-secondary:  #666666;
$kp-color-text-tertiary:   #999999;

// ------------------------------------------------------------
// 6. 颜色 — 分割线 / 边框
// ------------------------------------------------------------
$kp-color-divider:         #EEEEEE;
$kp-color-border:          #E8E8E8;

// ------------------------------------------------------------
// 7. 排版 — 字号 (Font Size)
// ------------------------------------------------------------
$kp-font-size-display:     48rpx;   // 金额、关键数据
$kp-font-size-h1:          40rpx;
$kp-font-size-h2:          34rpx;
$kp-font-size-h3:          30rpx;
$kp-font-size-body:        28rpx;
$kp-font-size-caption:     24rpx;
$kp-font-size-mini:        22rpx;

// ------------------------------------------------------------
// 8. 排版 — 字重 (Font Weight)
// ------------------------------------------------------------
$kp-font-weight-black:     900;     // Display
$kp-font-weight-bold:      700;     // H1, H2
$kp-font-weight-medium:    500;     // H3
$kp-font-weight-regular:   400;     // Body, Caption, Mini

// ------------------------------------------------------------
// 9. 排版 — 行高 (Line Height)
// ------------------------------------------------------------
$kp-line-height-tight:     1.2;     // Display / 标题
$kp-line-height-normal:    1.5;     // 正文
$kp-line-height-loose:     1.8;     // 长文本

// ------------------------------------------------------------
// 10. 排版 — 字体栈
// ------------------------------------------------------------
$kp-font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue",
  "PingFang SC", "Microsoft YaHei", sans-serif;

// ------------------------------------------------------------
// 11. 间距 (Spacing)
// ------------------------------------------------------------
$kp-spacing-page:          32rpx;   // 页面水平内边距
$kp-spacing-card:          28rpx;   // 卡片内边距
$kp-spacing-gap:           24rpx;   // 卡片间距 / 元素间距
$kp-spacing-sm:            16rpx;   // 小间距
$kp-spacing-xs:            12rpx;   // 极小间距
$kp-spacing-lg:            40rpx;   // 大间距
$kp-spacing-xl:            56rpx;   // 超大间距

// ------------------------------------------------------------
// 12. 页面结构 (Page Layout)
// ------------------------------------------------------------
$kp-header-min-height:     320rpx;  // 深色头部最小高度
$kp-content-overlap:       -40rpx;  // 内容区负边距重叠

// ------------------------------------------------------------
// 13. 圆角 (Border Radius)
// ------------------------------------------------------------
$kp-radius-card:           24rpx;   // 卡片 / 内容区顶部
$kp-radius-button:         24rpx;   // 按钮
$kp-radius-input:          16rpx;   // 输入框
$kp-radius-tag:            999rpx;  // 标签/胶囊
$kp-radius-full:           999rpx;  // 全圆（胶囊按钮/头像）
$kp-radius-lg:             40rpx;   // 超大圆角

// ------------------------------------------------------------
// 14. 阴影 (Box Shadow)
// ------------------------------------------------------------
$kp-shadow-card:           0 4rpx 24rpx rgba(0, 0, 0, 0.06);
$kp-shadow-float:          0 8rpx 40rpx rgba(0, 0, 0, 0.12);
$kp-shadow-glass:          0 4rpx 30rpx rgba(0, 0, 0, 0.08);

// ------------------------------------------------------------
// 15. 动画 (Animation)
// ------------------------------------------------------------
$kp-duration-fast:         150ms;
$kp-duration-normal:       300ms;
$kp-duration-slow:         500ms;
$kp-easing-default:        cubic-bezier(0.4, 0, 0.2, 1);

// ------------------------------------------------------------
// 16. 玻璃拟态参数 (Glassmorphism)
// ------------------------------------------------------------
$kp-glass-blur:            20px;
$kp-glass-border:          rgba(255, 255, 255, 0.35);
// 玻璃背景色复用上方的 $kp-color-glass token
```

## 5. Mixin 库完整定义

> 文件路径：`src/styles/_mixins.scss`

```scss
// ============================================================
// KaiPai Mixin Library — Cinematic Glassmorphism
// ============================================================

// ------------------------------------------------------------
// 1. 玻璃拟态 — 卡片 (Glass Card)
// ------------------------------------------------------------
@mixin kp-glass-card($blur: $kp-glass-blur, $opacity: 0.7, $radius: $kp-radius-card) {
  background: rgba(255, 255, 255, $opacity);
  border-radius: $radius;
  box-shadow: $kp-shadow-glass;
  border: 1rpx solid $kp-glass-border;

  // 支持 backdrop-filter 时启用毛玻璃
  @supports (backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px)) {
    -webkit-backdrop-filter: blur($blur);
    backdrop-filter: blur($blur);
  }

  // 不支持时降级为纯白背景
  @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
    background: $kp-color-card;
  }
}

// ------------------------------------------------------------
// 2. 玻璃拟态 — 深色毛玻璃 (Dark Glass)
// ------------------------------------------------------------
@mixin kp-glass-dark($blur: $kp-glass-blur, $opacity: 0.6) {
  background: rgba(18, 18, 20, $opacity);
  border-radius: $kp-radius-card;
  border: 1rpx solid rgba(255, 255, 255, 0.1);

  @supports (backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px)) {
    -webkit-backdrop-filter: blur($blur);
    backdrop-filter: blur($blur);
  }

  @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
    background: $kp-color-dark-primary;
  }
}

// ------------------------------------------------------------
// 3. 玻璃拟态 — 导航栏 (Glass Navbar)
// ------------------------------------------------------------
@mixin kp-glass-navbar($blur: 30px) {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.85);
  border-bottom: 1rpx solid $kp-color-divider;

  @supports (backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px)) {
    -webkit-backdrop-filter: saturate(180%) blur($blur);
    backdrop-filter: saturate(180%) blur($blur);
  }

  @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
    background: $kp-color-card;
  }
}

// ------------------------------------------------------------
// 4. 品牌渐变 (Brand Gradient)
// ------------------------------------------------------------
@mixin kp-gradient-brand($direction: 135deg) {
  background: linear-gradient($direction, $kp-color-primary, #FF8F5E);
}

@mixin kp-gradient-dark($direction: 180deg) {
  background: linear-gradient($direction, $kp-color-dark-primary, $kp-color-dark-secondary);
}

// ------------------------------------------------------------
// 5. 文字截断 (Text Ellipsis)
// ------------------------------------------------------------
@mixin kp-text-ellipsis($lines: 1) {
  overflow: hidden;
  text-overflow: ellipsis;

  @if $lines == 1 {
    white-space: nowrap;
  } @else {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: $lines;
    white-space: normal;
    word-break: break-all;
  }
}

// ------------------------------------------------------------
// 6. 安全区适配 (Safe Area)
// ------------------------------------------------------------
@mixin kp-safe-area-bottom($extra: 0rpx) {
  padding-bottom: calc(env(safe-area-inset-bottom) + #{$extra});
}

@mixin kp-safe-area-top($extra: 0rpx) {
  padding-top: calc(env(safe-area-inset-top) + #{$extra});
}

// ------------------------------------------------------------
// 7. Flex 布局快捷 (Flex Shortcuts)
// ------------------------------------------------------------
@mixin kp-flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

@mixin kp-flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

@mixin kp-flex-column {
  display: flex;
  flex-direction: column;
}

// ------------------------------------------------------------
// 8. 卡片基础 (Card Base)
// ------------------------------------------------------------
@mixin kp-card-base {
  background: $kp-color-card;
  border-radius: $kp-radius-card;
  padding: $kp-spacing-card;
  box-shadow: $kp-shadow-card;
}

// ------------------------------------------------------------
// 9. 按钮基础 (Button Base)
// ------------------------------------------------------------
@mixin kp-button-primary {
  @include kp-flex-center;
  @include kp-gradient-brand;
  color: #FFFFFF;
  font-size: $kp-font-size-body;
  font-weight: $kp-font-weight-medium;
  border-radius: $kp-radius-button;
  border: none;
  transition: opacity $kp-duration-fast $kp-easing-default;

  &:active {
    opacity: 0.85;
  }
}

// ------------------------------------------------------------
// 10. 过渡动画 (Transition)
// ------------------------------------------------------------
@mixin kp-transition($property: all, $duration: $kp-duration-normal) {
  transition: $property $duration $kp-easing-default;
}

// ------------------------------------------------------------
// 11. 排版快捷 (Typography Shortcuts)
// ------------------------------------------------------------
@mixin kp-text-display {
  font-size: $kp-font-size-display;
  font-weight: $kp-font-weight-black;
  line-height: $kp-line-height-tight;
}

@mixin kp-text-h1 {
  font-size: $kp-font-size-h1;
  font-weight: $kp-font-weight-bold;
  line-height: $kp-line-height-tight;
}

@mixin kp-text-h2 {
  font-size: $kp-font-size-h2;
  font-weight: $kp-font-weight-bold;
  line-height: $kp-line-height-tight;
}

@mixin kp-text-h3 {
  font-size: $kp-font-size-h3;
  font-weight: $kp-font-weight-medium;
  line-height: $kp-line-height-normal;
}

@mixin kp-text-body {
  font-size: $kp-font-size-body;
  font-weight: $kp-font-weight-regular;
  line-height: $kp-line-height-normal;
}

@mixin kp-text-caption {
  font-size: $kp-font-size-caption;
  font-weight: $kp-font-weight-regular;
  line-height: $kp-line-height-normal;
}

@mixin kp-text-mini {
  font-size: $kp-font-size-mini;
  font-weight: $kp-font-weight-regular;
  line-height: $kp-line-height-normal;
}
```

## 6. 页面骨架 CSS 实现

### 6.1 CSS Reset + 基础样式

> 文件路径：`src/styles/_reset.scss`

```scss
// ============================================================
// KaiPai Global Reset
// ============================================================

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

page {
  font-family: $kp-font-family;
  font-size: $kp-font-size-body;
  font-weight: $kp-font-weight-regular;
  line-height: $kp-line-height-normal;
  color: $kp-color-text-primary;
  background-color: $kp-color-bg;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

image {
  display: block;
  width: 100%;
  height: auto;
}

button {
  padding: 0;
  margin: 0;
  background: none;
  border: none;
  outline: none;
  font-family: inherit;

  &::after {
    border: none;
  }
}

scroll-view {
  -webkit-overflow-scrolling: touch;
}
```

### 6.2 深-浅双层页面骨架

> 文件路径：`src/styles/_page-layout.scss`

```scss
// ============================================================
// KaiPai Page Layout — Dark Header + Light Content
// ============================================================

// 页面根容器
.kp-page {
  min-height: 100vh;
  background-color: $kp-color-bg;
  @include kp-flex-column;
}

// 深色沉浸式头部
.kp-header {
  position: relative;
  min-height: $kp-header-min-height;
  background-color: $kp-color-dark-primary;
  padding: $kp-spacing-lg $kp-spacing-page $kp-spacing-xl;
  overflow: hidden;

  // 头部标题 — 白色大字
  &__title {
    @include kp-text-h1;
    color: $kp-color-text-dark-primary;
  }

  // 头部副标题
  &__subtitle {
    @include kp-text-body;
    color: $kp-color-text-dark-secondary;
    margin-top: $kp-spacing-xs;
  }

  // 头部关键数据展示（电影海报级）
  &__display {
    @include kp-text-display;
    color: $kp-color-text-dark-primary;
  }

  // 渐变变体
  &--gradient {
    @include kp-gradient-dark;
  }
}

// 浅色内容区 — 负边距重叠
.kp-content {
  position: relative;
  flex: 1;
  margin-top: $kp-content-overlap;
  padding: $kp-spacing-page;
  padding-top: $kp-spacing-card;
  background-color: $kp-color-bg;
  border-radius: $kp-radius-card $kp-radius-card 0 0;
  z-index: 1;
}

// 通用卡片
.kp-card {
  @include kp-card-base;

  & + & {
    margin-top: $kp-spacing-gap;
  }

  // 玻璃拟态卡片变体
  &--glass {
    @include kp-glass-card;
  }
}

// 分割线
.kp-divider {
  height: 1rpx;
  background-color: $kp-color-divider;
  margin: $kp-spacing-gap 0;
}
```

### 6.3 uview-plus 主题覆盖

> 文件路径：`src/styles/_uview-theme.scss`

```scss
// ============================================================
// uview-plus Theme Override
// ============================================================

// 主题色覆盖
$u-primary: $kp-color-primary;
$u-success: $kp-color-success;
$u-warning: $kp-color-warning;
$u-error:   $kp-color-danger;

// 文字色覆盖
$u-main-color:    $kp-color-text-primary;
$u-content-color: $kp-color-text-secondary;
$u-tips-color:    $kp-color-text-tertiary;

// 边框 / 背景
$u-border-color:  $kp-color-border;
$u-bg-color:      $kp-color-bg;
```

### 6.4 入口文件

> 文件路径：`src/styles/index.scss`

```scss
// 注意：_tokens.scss 和 _mixins.scss 通过 vite.config.ts additionalData 全局注入
// 此处无需 @import

@import './reset';
@import './uview-theme';
@import './page-layout';
```

### 6.5 Vite 配置注入

> 文件路径：`vite.config.ts`（相关片段）

```typescript
// vite.config.ts
export default defineConfig({
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @import "@/styles/_tokens.scss";
          @import "@/styles/_mixins.scss";
        `,
      },
    },
  },
});
```

### 6.6 页面使用示例

```vue
<template>
  <view class="kp-page">
    <!-- 深色沉浸式头部 -->
    <view class="kp-header">
      <text class="kp-header__title">我的项目</text>
      <text class="kp-header__subtitle">共 12 个进行中</text>
    </view>

    <!-- 浅色内容区（自动负边距重叠） -->
    <view class="kp-content">
      <view class="kp-card">
        <text>普通卡片内容</text>
      </view>
      <view class="kp-card kp-card--glass">
        <text>玻璃拟态卡片</text>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
// Tokens 和 Mixins 已全局注入，直接使用
.custom-element {
  @include kp-glass-card($blur: 30px, $opacity: 0.5);
  @include kp-text-ellipsis(2);
  padding: $kp-spacing-card;
}
</style>
```
