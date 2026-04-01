# 00-25 后台固定列 Sticky 单元格层级修复（Admin Fixed Column Sticky Cell Fix）

> 状态：待界面复核 | 优先级：P1 | 依赖：00-24 admin-fixed-column-hover-layer-fix
> 记录目的：修复后台表格 fixed 右侧操作列在 hover 态下仍被列表内容或悬浮层压住的问题，明确根因落在 sticky 固定单元格及其内部 `.cell`，而不再只停留在 wrapper 层。

## 1. 背景

`00-23` 与 `00-24` 已分别补齐 fixed 右列背景层和 wrapper / patch 层级，但后台账号页在鼠标悬浮时仍出现操作按钮被列表内容或 hover 层压住的问题。结合 Element Plus 表格实现，fixed 右列真实承载层是 body/header wrapper 内部的 sticky `td/th.el-table-fixed-column--right`，hover 反馈也直接落在 `td.el-table__cell` 上，因此仅调整 wrapper 不能彻底解决遮挡。

## 2. 范围

### 2.1 本轮必须处理

- 后台共享表格 fixed 右侧 sticky 单元格的层级、背景和 hover 态承托关系
- fixed 单元格内部 `.cell` 与 `.table-actions` 的显示层级和可点击性
- 保持现有按钮组换行能力与固定列分隔边界继续生效

### 2.2 本轮不处理

- 业务按钮文案、权限和动作顺序调整
- 非 fixed 列的整体 hover 视觉重做
- 其他非表格组件的层级治理

## 3. 需求

### 3.1 Sticky 固定列要求

- **R1** 后台 fixed 右侧 sticky `td/th` 在普通态与 hover 态下都必须稳定高于同排普通单元格的悬浮反馈
- **R2** fixed 单元格内部 `.cell` 不能继续成为操作按钮的裁切层或低层承托层
- **R3** `.table-actions` 内按钮在 hover 态下必须保持完整可见、可点击，不能被列表内容或 hover 层盖住

### 3.2 收敛要求

- **R4** 修复必须继续落在后台共享表格样式，避免页面私有补丁
- **R5** 已接入 `.table-actions` 的后台 fixed 操作列页面应自动继承本次修复

## 4. 验收标准

- [x] 已新增独立 Spec 并登记增量索引
- [ ] 后台账号页 fixed 操作列 hover 态不再被列表内容或悬浮层压住
- [ ] 操作按钮在 hover 态下保持完整可见与可点击
- [x] `npm run type-check` 与 `npm run build` 通过
