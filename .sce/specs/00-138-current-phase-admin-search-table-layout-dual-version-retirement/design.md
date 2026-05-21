# 00-138 设计说明

## 1. 设计目标

`00-138` 只做一件事：

1. 删除当前源码无 consumer 的 `SearchTableLayout` 双版本历史实现。

## 2. 已核实事实

### 2.1 当前有两份历史实现

已确认存在：

- `src/components/SearchTableLayout.vue`
- `src/components/tables/SearchTableLayout.vue`

两者职责都属于：

- 列表页筛选 + 表格 + 分页壳层

但 API 细节不同：

- 一个使用 `update:pageNo / update:pageSize`
- 一个使用 `page-change / page-size-change`

因此：

- 它们更像历史并存实现
- 不是当前统一运行壳层

### 2.2 当前源码侧零 consumer

已确认：

- `kaipai-admin/src`
- `.sce`
- `docs`

中未发现任何指向当前文件路径的 consumer。

### 2.3 `00-11` 只构成历史设计追溯

已确认 `00-11-platform-admin-console/design.md` 中有：

- `SearchTableLayout | 列表页筛选 + 表格 + 分页`

但该命中只说明：

- 历史设计阶段曾定义过这一类组件名

并不说明：

- 当前这两个文件仍被运行时消费
- 或必须保留这两个具体实现文件

## 3. 设计策略

### 3.1 双文件一起退场

本轮同时删除：

1. `src/components/SearchTableLayout.vue`
2. `src/components/tables/SearchTableLayout.vue`

原因：

- 两者都零 consumer
- 都属于同一历史概念的并存实现
- 分开删没有额外收益

### 3.2 不扩到其它组件

本轮不处理：

- business canonical 组件
- layout 组件
- 页面级容器

保持单一主线，只做双文件退场。

### 3.3 删除后验证

删除后只做：

1. `npm run type-check`
2. `npm run build`

不做浏览器回归，因为运行态 consumer 已为 0。

## 4. 风险与边界

### 4.1 已确认

- 当前不存在自动注册组件机制
- 当前不存在源码路径 consumer

### 4.2 待验证

- 删除后是否存在隐藏的 TypeScript / Vite 解析依赖

该风险通过 `type-check / build` 闭环。
