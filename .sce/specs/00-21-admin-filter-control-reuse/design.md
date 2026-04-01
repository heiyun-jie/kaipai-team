# 00-21 设计说明

## 1. 设计原则

- 样式下沉到共享层，不靠页面复制
- 以 `/verify/pending` 当前输入为视觉基准
- 保持输入控件清晰，但不改变现有页面字段结构

## 2. 设计策略

### 2.1 共享输入样式

- 把 `/verify/pending` 的 input/select 包裹层样式迁移到 `FilterPanel`
- 覆盖 `el-input__wrapper`、`el-select__wrapper`、`el-date-editor` 与占位文本样式

### 2.2 页面清理

- `VerificationBoard.vue` 仅保留该页特有宽度与布局控制
- 去掉重复的输入框边框、背景、聚焦和 placeholder 样式

## 3. 影响文件

- `kaipai-admin/src/components/business/FilterPanel.vue`
- `kaipai-admin/src/views/verify/VerificationBoard.vue`
