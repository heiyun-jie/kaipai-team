# 00-40 设计说明

## 1. 设计原则

- 来源提示必须是显性状态，不埋在筛选说明里
- 清空上下文要同时清掉 query 和筛查回填，不只改页面文字
- 只对“最近事项”入口生效，不影响模块入口

## 2. 设计策略

### 2.1 dashboard 来源标记

最近事项跳转追加：

- `source=dashboard_recent_item`

模块入口与快捷入口不带该标记。

### 2.2 目标页提示

在目标页筛选面板后新增上下文提示条，展示：

- 当前来自工作台最近事项
- 当前自动带入的关键筛查条件摘要
- “清空上下文”按钮

### 2.3 清空动作

点击“清空上下文”后：

- `router.replace({ path: route.path })`
- 目标页依赖现有 `watch(route.fullPath)` 重新回填默认筛查并加载列表

## 3. 影响文件

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/verify/VerificationBoard.vue`
- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/refund/OrdersView.vue`
- `kaipai-admin/src/views/payment/OrdersView.vue`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
