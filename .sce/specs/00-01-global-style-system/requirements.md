# 全局样式系统

## 1. 概述

为"开拍了"(KaiPai) 小程序建立统一的全局样式系统，设计风格为 **Cinematic Glassmorphism（电影感沉浸式玻璃拟态）**。该系统基于 uni-app 3.0 + Vue 3.4 + TypeScript + uview-plus + SCSS 技术栈，提供完整的 Design Tokens、页面骨架结构、玻璃拟态 Mixin 库和全局基础样式，确保全应用视觉一致性与开发效率。

核心视觉特征：
- 深色沉浸式头部 (#121214) + 浅色内容区 (#F8F9FA) 的双层页面结构
- 品牌色 Spotlight Orange #FF6B35 贯穿交互焦点
- 玻璃拟态效果：backdrop-filter 模糊 + 半透明背景
- 超椭圆大圆角 (24-40rpx)
- 深色头部与浅色内容区之间的负边距重叠过渡
- 电影海报级排版对比度（Display 48rpx Black 900）

## 2. 用户故事

- 作为前端开发者，我希望通过引入一套 SCSS 变量文件即可获得完整的颜色、字体、间距 Token，避免硬编码魔法值。
- 作为前端开发者，我希望使用预定义的页面骨架 class 快速搭建深-浅双层页面结构，无需每个页面重复编写布局代码。
- 作为前端开发者，我希望通过 `@include` 调用玻璃拟态 Mixin，一行代码实现毛玻璃卡片效果。
- 作为 UI 设计师，我希望所有页面遵循统一的 Design Tokens，确保设计稿与实现的一致性。
- 作为产品经理，我希望应用具备电影感沉浸式视觉体验，提升用户对品牌的感知质量。

## 3. 功能需求

### 3.1 Design Tokens SCSS 变量体系

**描述**

定义完整的 SCSS 变量体系作为全局 Design Tokens，涵盖颜色、排版、间距、圆角、阴影、动画等维度。所有变量以 `$kp-` 为命名前缀，按语义分组组织。变量文件通过 `vite.config.ts` 的 `css.preprocessorOptions.scss.additionalData` 全局注入，任何 SCSS 文件中均可直接使用。

**验收标准**

- WHEN 开发者在任意 `.vue` 或 `.scss` 文件中引用 `$kp-color-primary` THEN 编译正常且值为 `#FF6B35`
- WHEN 开发者查阅变量文件 THEN 可找到以下完整分组：颜色（深色系、品牌色、内容区、语义色、文字色、分割线）、排版（7 级字号 + 字重）、间距（页面边距、卡片内距、元素间距）、圆角（卡片、输入框、标签、全圆）、阴影（卡片阴影、浮层阴影）、动画（过渡时长、缓动函数）
- WHEN 变量值被修改 THEN 所有引用该变量的组件样式同步更新，无需逐文件修改

### 3.2 深-浅双层页面结构

**描述**

实现"开拍了"标志性的深色沉浸式头部 + 浅色内容区双层页面骨架。深色头部区域 (#121214) 高度 320-400rpx，用于放置页面标题、关键数据展示；浅色内容区 (#F8F9FA) 通过 -40rpx 负边距向上重叠深色区域，形成自然过渡。提供 `.kp-page`、`.kp-header`、`.kp-content` 等语义化 class。

**验收标准**

- WHEN 开发者为页面根元素添加 `.kp-page` class THEN 页面自动获得 `min-height: 100vh` 和 `#F8F9FA` 背景色
- WHEN 开发者使用 `.kp-header` THEN 该区域背景色为 `#121214`，最小高度 320rpx，内边距符合设计规范
- WHEN 开发者使用 `.kp-content` THEN 该区域自动应用 `-40rpx` 的 `margin-top`、`24rpx` 圆角（左上 + 右上）、`#F8F9FA` 背景色、`32rpx` 水平内边距
- WHEN 页面内容不足一屏 THEN `.kp-content` 区域通过 `flex: 1` 自动撑满剩余空间，无底部空白

### 3.3 玻璃拟态 Mixin 库

**描述**

提供一组 SCSS Mixin 封装玻璃拟态（Glassmorphism）效果，包括毛玻璃卡片、毛玻璃导航栏、毛玻璃浮层等变体。Mixin 内部处理 `backdrop-filter` 兼容性前缀，并提供不支持时的优雅降级方案。同时提供品牌渐变、文字截断、安全区适配等通用 Mixin。

**验收标准**

- WHEN 开发者调用 `@include kp-glass-card()` THEN 元素获得白色半透明背景 `rgba(255,255,255,0.7)`、`backdrop-filter: blur(20px)`、`24rpx` 圆角和卡片阴影
- WHEN 运行环境不支持 `backdrop-filter` THEN 自动降级为不透明白色背景 `#FFFFFF`，不出现视觉异常
- WHEN 开发者调用 `@include kp-glass-card($blur: 30px, $opacity: 0.5)` THEN 可自定义模糊程度和透明度
- WHEN 开发者调用 `@include kp-text-ellipsis(2)` THEN 文本超过 2 行时显示省略号
- WHEN 开发者调用 `@include kp-safe-area-bottom()` THEN 在有底部安全区的设备上自动添加对应 padding

### 3.4 全局基础样式

**描述**

定义全局 CSS Reset 和基础样式，包括盒模型统一 (`box-sizing: border-box`)、默认字体栈、滚动行为、图片默认样式、uview-plus 主题变量覆盖等。确保所有页面和组件在一致的基础样式之上构建。

**验收标准**

- WHEN 应用启动 THEN 所有元素默认 `box-sizing: border-box`，`margin: 0`，`padding: 0`
- WHEN 页面渲染 THEN 默认字体为系统字体栈，行高 1.5，字色 `#1A1A1A`，背景色 `#F8F9FA`
- WHEN 使用 uview-plus 组件 THEN 组件主题色为 `#FF6B35`，与全局 Design Tokens 一致
- WHEN 使用 `<image>` 标签 THEN 默认 `display: block`、`width: 100%`，无额外间距

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- **性能**：全局样式文件 gzip 后不超过 5KB；避免过度使用 `backdrop-filter` 导致低端机型卡顿，提供降级方案
- **兼容性**：`backdrop-filter` 需添加 `-webkit-` 前缀
- **可维护性**：所有样式值通过 Design Tokens 变量引用，禁止硬编码；变量命名遵循 `$kp-{category}-{property}-{variant}` 规范
- **可扩展性**：Mixin 支持参数化自定义，新增主题色只需修改变量文件

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 小程序限制：微信小程序不支持部分 CSS 特性（如 `position: sticky` 在某些场景下的表现），需针对性处理
- 设计规范：所有视觉参数以本文档定义的 Design Tokens 为准，不得自行定义偏离值
