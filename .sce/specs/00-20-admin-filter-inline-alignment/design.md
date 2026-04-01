# 00-20 设计说明

## 1. 设计原则

- 优先修共享筛选壳层，不单点修页面
- 让筛选项更像“工作台工具条”，而不是表单录入页
- 横向对齐只解决布局问题，不削弱输入对比度

## 2. 设计策略

### 2.1 共享筛选壳层

- `FilterPanel` 对 `el-form--inline` 统一加上行内对齐约束
- 标签改为固定右侧间距，和输入容器处于同一基线
- 输入框、下拉框保持统一高度与垂直居中

### 2.2 实名认证审核页

- 去掉该页上置标签布局，改回 inline form
- 保留当前页概览卡、空态和详情区优化，只回收筛选结构

## 3. 影响文件

- `kaipai-admin/src/components/business/FilterPanel.vue`
- `kaipai-admin/src/views/verify/VerificationBoard.vue`
