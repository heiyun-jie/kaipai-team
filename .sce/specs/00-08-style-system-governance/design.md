# 样式体系减负和升级治理 - 技术设计

_Requirements: 00-08 全部_

## 1. 现状

当前告警来源有两层：

- `vite.config.ts` 通过 `additionalData` 给所有样式块注入 `@import "@/styles/_mixins.scss";`
- `App.vue` 和 `src/styles/index.scss` 仍在用 `@import`

这会导致：

- 所有页面 / 组件样式块都触发 `@import` 弃用告警
- 样式依赖边界不清晰
- 后续升级 Sass 时风险持续累积

## 2. 升级策略

本轮采用“桥接层 + 模块化入口”方案：

### 2.1 新增桥接层

新增：

```scss
src/styles/_inject.scss
```

职责：

- `@forward './tokens'`
- `@forward './mixins'`

这样页面和组件继续通过单一入口拿到变量和 mixin。

### 2.2 模块依赖调整

- `_mixins.scss` 改为 `@use './tokens' as *;`
- `_reset.scss` 改为 `@use './inject' as *;`
- `_page-layout.scss` 改为 `@use './inject' as *;`
- `index.scss` 改为 `@use './reset'; @use './page-layout';`
- `App.vue` 改为 `@use '@/styles/index.scss' as *;`
- `vite.config.ts` 的 `additionalData` 改为 `@use "@/styles/_inject.scss" as *;`

## 3. 风险控制

- 保持页面 / 组件样式写法不变
- 只调整底层依赖链和入口写法
- 通过构建日志验证 `@import` 告警变化

## 4. 非目标

- 本轮不处理 `legacy-js-api` 告警
- 本轮不迁移到 CSS 变量体系
- 本轮不逐页重写 BEM 或样式结构
