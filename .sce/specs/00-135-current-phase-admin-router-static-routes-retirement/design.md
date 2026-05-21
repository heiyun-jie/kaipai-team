# 00-135 设计说明

## 1. 设计目标

`00-135` 只做一件事：

1. 核销并删除已无 consumer 的历史静态路由表 `static-routes.ts`。

## 2. 已核实事实

### 2.1 `static-routes.ts` 的职责已被 `index.ts` 覆盖

已确认：

- `D:\XM\kaipai-team\kaipai-admin\src\router\static-routes.ts`
  - 只导出三条静态路由
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
  - 已直接定义同一组静态路由

因此：

- 当前不存在“删除后静态路由将失效”的直接风险
- 需要验证的关键点只剩：是否还有任何其它入口消费该文件

### 2.2 当前未发现任何 consumer

已确认全仓搜索以下关键字均未命中：

- `staticRoutes`
- `router/static-routes`
- `static-routes.ts`

并且：

- `tsconfig.json` 只做常规 TypeScript include
- `vite.config.ts` 只做别名与代理配置
- 当前未发现约定式 router 文件扫描机制

因此：

- `static-routes.ts` 更像历史拆分残留，而不是运行时基础设施

## 3. 设计策略

### 3.1 单文件切片

本轮只处理：

- `D:\XM\kaipai-team\kaipai-admin\src\router\static-routes.ts`

不把 `AuditConfirmDialog` 或其它候选一起打包，保持：

- 风险最小
- 证据清晰
- 回归面可控

### 3.2 删除前门禁

删除前必须补足三层证据：

1. 文件职责只是重复静态路由导出
2. 全仓搜索无 consumer
3. 工程配置中无自动注册机制

三层都成立时，才进入真实删除。

### 3.3 删除后验证

删除后只做最必要验证：

1. `npm run type-check`
2. `npm run build`

不额外扩展到 UI 精修或大范围浏览器回归。

## 4. 风险与边界

### 4.1 已确认

- 本轮不改任何运行路由定义
- 本轮不改任何页面组件
- 本轮不碰 hidden tooling 与 fallback

### 4.2 待验证

- 当前文档是否存在路径追溯引用

若文档只作为历史追溯而不构成运行依赖，允许删除，但需要在 `execution.md` 中明确区分。
