# 00-47 设计说明

## 1. 设计原则

- 延续 `00-46` 的共享收口结果，不回退介绍模块
- 只清理死参，不改业务页正文结构
- 清理调用点的同时删掉对应无用脚本，保持页面最小噪音

## 2. 设计策略

### 2.1 共享组件边界

`PageContainer` 继续保持当前轻量结构：

- 可选 `actions` 行
- 内容区 `slot`

本轮不重新引入任何页头 props，也不为残留字段做兼容兜底。

### 2.2 调用点清理

对所有后台视图中的 `PageContainer` 调用执行统一处理：

- 删除 `title`
- 删除 `eyebrow`
- 删除 `description`
- 保留 `actions` 插槽与正文内容

### 2.3 脚本收尾

若页面中存在仅服务于 `PageContainer` 顶部介绍区的变量或导入：

- 删除未使用的 `computed`
- 删除未使用的 `useRoute` / 文案常量
- 保持页面业务逻辑不受影响

## 3. 影响文件

- `kaipai-admin/src/components/business/PageContainer.vue`
- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/payment/OrdersView.vue`
- `kaipai-admin/src/views/payment/TransactionsView.vue`
- `kaipai-admin/src/views/system/RolesView.vue`
- `kaipai-admin/src/views/system/OperationLogsView.vue`
- `kaipai-admin/src/views/system/AiResumeGovernanceView.vue`
- `kaipai-admin/src/views/system/AdminUsersView.vue`
- `kaipai-admin/src/views/membership/ProductsView.vue`
- `kaipai-admin/src/views/membership/AccountsView.vue`
- `kaipai-admin/src/views/refund/OrdersView.vue`
- `kaipai-admin/src/views/refund/LogsView.vue`
- `kaipai-admin/src/views/referral/EligibilityView.vue`
- `kaipai-admin/src/views/referral/PoliciesView.vue`
- `kaipai-admin/src/views/referral/RecordsView.vue`
- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/recruit/AppliesView.vue`
- `kaipai-admin/src/views/recruit/RolesView.vue`
- `kaipai-admin/src/views/recruit/ProjectsView.vue`
- `kaipai-admin/src/views/shared/PlaceholderView.vue`
- `kaipai-admin/src/views/verify/VerificationBoard.vue`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
