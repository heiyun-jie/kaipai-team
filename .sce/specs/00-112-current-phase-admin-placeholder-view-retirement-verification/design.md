# 00-112 设计说明

## 1. 设计目标

`00-112` 只处理一个对象：

1. 核销 `D:\XM\kaipai-team\kaipai-admin\src\views\shared\PlaceholderView.vue`
2. 在证据充分时删除该文件
3. 不扩到 hidden tooling / fallback / 正式 8 页

## 2. 已核实事实

### 2.1 当前文件只是独立占位页

`PlaceholderView.vue` 当前内容只承接：

- 占位卡片
- `页面建设中` 文案
- `PageContainer` 包裹

它不是：

- 正式页容器
- 路由 404/403 页
- 某个共享渲染插槽
- 动态组件注册中心

### 2.2 当前运行时未发现引用

已核实：

- `kaipai-admin/src` 内搜索 `PlaceholderView` 未命中引用
- `kaipai-admin/src` 内搜索 `shared/PlaceholderView.vue` 未命中引用
- `router/index.ts` 当前只直接 import：
  - `LoginView.vue`
  - `ForbiddenView.vue`
  - `NotFoundView.vue`
  - 以及正式 / hidden tooling 页面
- `menus.ts` 中没有占位页 route
- `admin-information-architecture.ts` 中没有占位页分类依赖

### 2.3 不存在约定式自动注册前提

已核实：

- `package.json` 只使用 `vue-router + vite + @vitejs/plugin-vue`
- `vite.config.ts` 只启用 `vue()` 插件
- 当前项目不存在 `unplugin-vue-router`、pages generator 或按目录自动收集页面的机制

因此：

- 删除 `PlaceholderView.vue` 不会因为目录扫描而被隐式消费

### 2.4 文档追溯引用不构成运行时保留条件

当前 `.sce` 中仍有多处文档追溯引用 `PlaceholderView.vue`：

- `00-16`
- `00-47`
- `00-71`
- `00-110`
- `00-111`
- `spec-code-mapping.md`
- `CURRENT_CONTEXT.md`

这些引用说明：

- 它曾参与历史阶段的文案与壳层收口，且当前删除动作已被建档

但不说明：

- 当前仍有运行态依赖

## 3. 设计策略

### 3.1 删除策略

直接删除：

- `D:\XM\kaipai-team\kaipai-admin\src\views\shared\PlaceholderView.vue`

不新增替代文件。

### 3.2 为什么本轮可以删除

与 `00-111` 的两个历史 wrapper 相比，`PlaceholderView.vue` 不是“薄包装”，所以当时被延后。

但在本轮完成以下额外核销后，删除边界已经充分明确：

1. 当前无源码引用
2. 当前无 router / menu / architecture 依赖
3. 当前无约定式自动注册
4. 404/403 已由其他页面承接
5. `.sce` 剩余引用只属于历史文档

因此它已经从“可能有保留价值的占位容器”转为“无运行用途的历史文件”。

## 4. 风险与边界

### 4.1 已确认

- 删除不会改变正式 8 页
- 删除不会改变 hidden tooling
- 删除不会影响 fallback 权限兼容
- 风险低、可逆

### 4.2 待验证

- 删除后 `type-check` / `build` 是否仍完全通过

因此本轮继续以：

- 搜索核销
- `type-check`
- `build`

作为主验证手段。
