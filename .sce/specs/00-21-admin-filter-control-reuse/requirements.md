# 00-21 后台筛选输入样式复用（Admin Filter Control Reuse）

> 状态：已完成 | 优先级：P1 | 依赖：00-20 admin-filter-inline-alignment
> 记录目的：把 `/verify/pending` 当前使用的 input/select 外观下沉为后台筛选区共享样式，统一所有后台页的输入体验。

## 1. 背景

当前 `/verify/pending` 的筛选输入框已经具备较清晰的边界、表面色和聚焦反馈，但这套样式仍留在页面私有样式里。其他后台页虽然已经统一为横向筛选布局，输入控件视觉仍未自动继承 `/verify/pending` 的表现。

## 2. 范围

### 2.1 本轮必须处理

- `FilterPanel` 内所有 input/select/date-picker 的共享样式
- 清理 `/verify/pending` 内重复的输入外观私有样式
- 保证所有后台筛选页复用同一套输入视觉规则

### 2.2 本轮不处理

- 非 `FilterPanel` 场景下的表单弹窗和详情抽屉输入
- 表格、按钮和概览卡的再次改版
- 后端查询逻辑与字段变更

## 3. 需求

### 3.1 复用要求

- **R1** 其他后台页的筛选 input/select/date-picker 必须复用 `/verify/pending` 当前这套输入外观
- **R2** 共享输入需要保持统一高度、圆角、边框、底色和聚焦阴影
- **R3** 占位文字、已选文字和图标需保持与 `/verify/pending` 一致的可见性

### 3.2 收敛要求

- **R4** `/verify/pending` 不再保留重复的输入外观私有样式
- **R5** 共享筛选壳层承担样式复用责任，避免后续页面继续单独覆盖

## 4. 验收标准

- [x] 已新增独立 Spec 并登记增量索引
- [x] `FilterPanel` 已复用 `/verify/pending` 输入样式
- [x] `/verify/pending` 私有输入样式已清理，其他后台筛选页可自动继承
- [x] `npm run type-check` 与 `npm run build` 通过
