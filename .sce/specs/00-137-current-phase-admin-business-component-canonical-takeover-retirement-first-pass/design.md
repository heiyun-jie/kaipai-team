# 00-137 设计说明

## 1. 设计目标

`00-137` 只做一件事：

1. 删除已被 `components/business/*` 完全接管、且当前无 consumer 的第一批旧组件入口。

## 2. 已核实事实

### 2.1 业务侧 canonical 组件已接管运行态

已确认当前运行页大量直接使用：

- `@/components/business/PageContainer.vue`
- `@/components/business/FilterPanel.vue`
- `@/components/business/PermissionButton.vue`
- `@/components/business/StatusTag.vue`

因此：

- 对应旧入口不应继续作为运行态组件来源
- 若旧入口无 consumer，可按旧代码退场处理

### 2.2 旧入口当前无运行时 consumer

已确认以下旧入口在 `kaipai-admin/src` 内无 import / dynamic import consumer：

- `src/components/PageContainer.vue`
- `src/components/PermissionButton.vue`
- `src/components/StatusTag.vue`
- `src/components/layout/PageContainer.vue`
- `src/components/layout/FilterPanel.vue`

并且：

- `.sce / docs` 当前未发现上述路径追溯引用

### 2.3 为什么不处理 SearchTableLayout

当前也核实到：

- `src/components/SearchTableLayout.vue`
- `src/components/tables/SearchTableLayout.vue`

未发现 consumer。

但本轮不处理它们，原因是：

- 它们没有被 `components/business/*` 的明确 canonical 组件接管证据
- 适合后续单独起 spec 做“SearchTableLayout 双版本核销”

## 3. 设计策略

### 3.1 第一批只删已被 business 接管的旧入口

本轮删除：

1. 顶层 `PageContainer`
2. 顶层 `PermissionButton`
3. 顶层 `StatusTag`
4. layout `PageContainer`
5. layout `FilterPanel`

### 3.2 不改变 canonical 实现

本轮不修改：

- `components/business/PageContainer.vue`
- `components/business/FilterPanel.vue`
- `components/business/PermissionButton.vue`
- `components/business/StatusTag.vue`

### 3.3 删除后验证

删除后只做必要闭环：

1. `npm run type-check`
2. `npm run build`

不做浏览器回归，因为运行时 consumer 不改，canonical 组件不改。

## 4. 风险与边界

### 4.1 已确认

- 本轮不改页面 import
- 本轮不改 business canonical 组件
- 本轮不碰 SearchTableLayout

### 4.2 待验证

- 删除后是否存在隐藏的 TypeScript / Vite 解析引用

该风险通过 `type-check / build` 闭环。
