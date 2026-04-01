# 00-24 设计说明

## 1. 设计原则

- 优先修 shared fixed-right 结构层，不回到页面局部覆盖
- 让 fixed 区 hover 反馈存在，但不允许压过操作按钮
- 保持前两轮 fixed 列治理的连续性，不推翻已生效样式

## 2. 设计策略

### 2.1 fixed-right 结构层

- 为 `.el-table__fixed-right`、`.el-table__fixed-right-patch` 和内部 wrapper 指定明确层级
- 让固定列背景层承担承托作用，而不是抢占按钮上层

### 2.2 操作区提升

- `.table-actions` 和 fixed 操作单元格内按钮提升到 hover 层之上
- 保证按钮文字、点击区域和 hover 态都稳定展示

## 3. 影响文件

- `kaipai-admin/src/styles/index.scss`
