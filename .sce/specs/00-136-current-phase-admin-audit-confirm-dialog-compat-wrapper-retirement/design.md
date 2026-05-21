# 00-136 设计说明

## 1. 设计目标

`00-136` 只做一件事：

1. 删除已无 consumer 的 `AuditConfirmDialog` 顶层兼容 wrapper。

## 2. 已核实事实

### 2.1 顶层组件当前只是 compat wrapper

已确认：

- `D:\XM\kaipai-team\kaipai-admin\src\components\AuditConfirmDialog.vue`

当前只做：

- import canonical dialog
- 透传 props
- 透传 `update:modelValue / confirm`

因此：

- 它不是独立实现
- 只是历史兼容入口

### 2.2 运行时代码已经统一消费 canonical dialog

已确认：

- `VerificationBoard.vue`
- `Refund/OrdersView.vue`
- `RolesView.vue`
- `Recruit/RolesView.vue`
- `Recruit/ProjectsView.vue`
- `AdminUsersView.vue`
- `Referral/PoliciesView.vue`
- `Referral/RiskView.vue`
- `TemplatesView.vue`

都直接引用：

- `@/components/dialogs/AuditConfirmDialog.vue`

因此：

- 当前运行链已经不依赖顶层 compat wrapper

### 2.3 文档引用不构成运行时保留理由

已确认 `.sce` 中仍存在对 `AuditConfirmDialog.vue` 的提及，但语义属于：

- 历史兼容改造记录
- 样式对齐历史
- 当前候删说明

因此：

- 文档引用需要保留追溯
- 但不应阻止运行时兼容 wrapper 退场

## 3. 设计策略

### 3.1 单文件切片

本轮只处理：

- `D:\XM\kaipai-team\kaipai-admin\src\components\AuditConfirmDialog.vue`

不顺手改：

- `dialogs/AuditConfirmDialog.vue`
- 任何业务页 import
- 任何 dialog 行为或样式

### 3.2 删除前门禁

删除前只验证三件事：

1. 顶层文件只是 compat wrapper
2. 源码 consumer 已全部转向 canonical dialog
3. 文档引用只是历史追溯

三条同时成立时，进入真实删除。

### 3.3 删除后验证

删除后只做最必要闭环：

1. `npm run type-check`
2. `npm run build`

不扩展到 UI 或浏览器回归，因为 canonical dialog 及其 consumer 都不变。

## 4. 风险与边界

### 4.1 已确认

- 本轮不改 dialog canonical 实现
- 本轮不改任意 consumer
- 本轮只影响一个无人消费的 compat wrapper

### 4.2 待验证

- `.sce` 中是否存在“必须保留 compat 入口”的明确文字

若只有历史追溯而无运行时保留口径，则允许删除。
