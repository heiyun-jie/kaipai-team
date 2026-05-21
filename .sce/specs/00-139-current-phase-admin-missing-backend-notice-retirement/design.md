# 00-139 设计说明

## 1. 设计目标

`00-139` 只做一件事：

1. 删除当前零 consumer 的 `MissingBackendNotice.vue`。

## 2. 已核实事实

### 2.1 组件职责单一且独立

已确认：

- `src/components/business/MissingBackendNotice.vue`

当前只承接：

- 标题
- 描述
- endpoint hint

它本质上是一张静态提示卡，而不是运行时基础设施。

### 2.2 当前源码侧零 consumer

已确认：

- `kaipai-admin/src`

中未发现任何 `MissingBackendNotice` consumer。

### 2.3 当前文档侧零路径引用

已确认：

- `.sce / docs`

中未发现当前文件路径或组件名追溯引用。

因此：

- 它不受“历史文档仍需保留路径追溯”的门禁影响

## 3. 设计策略

### 3.1 单文件切片

本轮只处理：

- `src/components/business/MissingBackendNotice.vue`

不顺手扩大到其它 business 组件。

### 3.2 删除后验证

删除后只做：

1. `npm run type-check`
2. `npm run build`

不做浏览器回归，因为当前运行时 consumer 为 0。

## 4. 风险与边界

### 4.1 已确认

- 当前没有源码 consumer
- 当前没有文档路径引用
- 当前不是 hidden tooling / fallback / menu / route 入口

### 4.2 待验证

- 删除后是否存在隐藏的 TypeScript / Vite 解析依赖

该风险通过 `type-check / build` 闭环。
