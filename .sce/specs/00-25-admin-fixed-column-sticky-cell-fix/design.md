# 00-25 设计说明

## 1. 设计原则

- 继续在后台共享表格层收敛，不回退到页面局部补丁
- 直接命中 Element Plus sticky fixed cell，而不是重复抬高外围 wrapper
- hover 反馈可以保留，但 fixed 操作列必须始终是最稳定的视觉锚点

## 2. 设计策略

### 2.1 Sticky 单元格抬升

- 以 `.el-table__body-wrapper/.el-table__header-wrapper` 中的 `td/th.el-table-fixed-column--right` 为核心修复对象
- 为 fixed sticky 单元格提供更明确的层级、背景与必要的隔离，确保它高于普通单元格 hover 层

### 2.2 Inner Cell 与操作区收口

- 为 fixed sticky 单元格内部 `.cell` 提供独立承托层，避免继续作为默认 `overflow: hidden` 的低层容器
- 保持 `.table-actions` 与链接按钮在 fixed 单元格内作为最上层交互内容展示

## 3. 影响文件

- `kaipai-admin/src/styles/index.scss`
