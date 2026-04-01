# 公共样式壳层抽离 - 技术设计

_Requirements: 00-09 全部_

## 1. 现状

当前样式重复热点集中在两类：

- 多个页面重复定义悬浮返回按钮：按钮容器、箭头、文字几乎一致
- 多个页面重复定义底部固定操作栏：固定定位、安全区 padding、渐变背景、主按钮壳层高度与圆角高度接近

这些重复样式目前散落在多个页面内，问题是：

- 调整返回按钮或操作栏视觉时需要跨文件同步
- 页面样式块体积持续膨胀
- 已完成的样式入口治理无法继续向页面级减负传导

## 2. 方案

### 2.1 在 `_mixins.scss` 中新增公共壳层 mixin

计划新增：

- `kp-floating-back-button-shell`
- `kp-floating-back-chevron`
- `kp-floating-back-text`
- `kp-fixed-action-bar`
- `kp-fixed-action-tip`
- `kp-primary-action-button-shell`

所有 mixin 默认提供当前主线最常见视觉参数，并保留必要参数入口给个别页面做微调。

### 2.2 页面回接策略

优先回接下列页面中的重复样式：

- `pages/apply-confirm/index.vue`
- `pages/apply-detail/index.vue`
- `pages/role-detail/index.vue`
- `pages/project/create.vue`
- `pages/project/role-create.vue`
- `pages/company-profile/edit.vue`
- `pages/my-applies/index.vue`
- `pages/apply-manage/index.vue`
- `pkg-tools/webview/index.vue`
- `pages/actor-profile/edit.vue`

对于 `actor-card` 等存在轻微视觉差异的页面，仅在参数可兼容时回接公共 mixin；不强行统一视觉。

## 3. 风险控制

- 不改模板结构，只改样式声明
- 优先抽离视觉壳层，不抽业务布局
- 对有轻微差异的页面使用 mixin 参数，不做全局强制统一

## 4. 非目标

- 不在本轮引入新的 UI 组件
- 不改动路由、分享、业务逻辑
- 不逐页做样式美化
