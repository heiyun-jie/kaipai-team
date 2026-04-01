# 00-24 后台固定列悬浮层级修复（Admin Fixed Column Hover Layer Fix）

> 状态：已完成 | 优先级：P1 | 依赖：00-23 admin-fixed-column-layer-fix
> 记录目的：修复后台表格 fixed 右侧列在鼠标悬浮态下 wrapper / patch 层级高于操作按钮，导致操作区仍被悬浮层压住的问题。

## 1. 背景

`00-23` 已补齐 fixed 右列背景层，解决了底层普通列文本穿透的问题，但当前 Element Plus 的 fixed 右侧 wrapper、patch 和 hover 相关层级仍未完全收住。鼠标移入表格后，fixed 区域会出现悬浮层压在操作按钮之上，视觉上仍像“悬浮层比操作列更高”。

## 2. 范围

### 2.1 本轮必须处理

- 后台共享表格下 fixed 右侧 wrapper、patch 与 body/header 的层级关系
- fixed 右侧操作按钮在 hover 态下的可见性与可点击性
- 保持现有 fixed 列背景和边界修复继续生效

### 2.2 本轮不处理

- 按钮文案、动作顺序与业务逻辑
- 非 fixed 列的 hover 样式改版
- 弹窗、抽屉和其他组件层级治理

## 3. 需求

### 3.1 层级要求

- **R1** 后台 fixed 右侧 wrapper 与 patch 必须低于操作按钮本身，不能在 hover 态覆盖操作区
- **R2** fixed 右列操作按钮在普通态与 hover 态下都必须保持清晰可见、可点击
- **R3** 右侧 fixed 区域的背景、边界和 hover 反馈需继续保持一致

### 3.2 收敛要求

- **R4** 修复必须落在后台共享表格样式，不在页面私有样式重复加层级补丁
- **R5** 已接入 `.table-actions` 的后台 fixed 操作列页面应自动继承本次修复

## 4. 验收标准

- [x] 已新增独立 Spec 并登记增量索引
- [x] 后台账号页 fixed 操作列 hover 态不再被悬浮层压住
- [x] 操作按钮在 hover 态下保持可见与可点击
- [x] `npm run type-check` 与 `npm run build` 通过
