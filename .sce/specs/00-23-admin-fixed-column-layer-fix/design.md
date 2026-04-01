# 00-23 设计说明

## 1. 设计原则

- 优先修共享 fixed 列层，不回退到页面私有补丁
- 保持当前后台表格的浅色玻璃风格，但 fixed 区域必须有稳定承托面
- hover 态、表头和表体统一处理，避免局部样式不一致

## 2. 设计策略

### 2.1 fixed 右列背景层

- 为 `.el-table-fixed-column--right` 和对应 header cell 增加独立背景色
- 为 fixed 列补充左侧 inset 阴影或边界线，明确冻结区起点
- 保留普通列透明背景，不影响当前表格整体观感

### 2.2 hover 同步

- 表格行 hover 时同步覆盖 fixed 列背景
- 保证 hover 反馈仍然是一整行，而不是 fixed 区和普通区断开

## 3. 影响文件

- `kaipai-admin/src/styles/index.scss`
