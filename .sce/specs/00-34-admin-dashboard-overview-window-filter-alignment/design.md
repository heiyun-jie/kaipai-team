# 00-34 设计说明

## 1. 设计原则

- 前端严格遵循后端真实边界
- 把筛查层放在工作台 hero 之后、统计卡之前，作为全页观察工具条
- 不为了“看起来统一”而虚构错误的统计口径

## 2. 设计策略

### 2.1 筛查项

- 时间窗口：`dateFrom/dateTo`
- 业务线：`bizLine`

业务线可选值：

- `verify`
- `referral`
- `refund`
- `payment`

### 2.2 页面说明

在筛查面板说明中明确：

- 时间窗口影响统计和最近事项
- 业务线筛查仅影响最近事项

### 2.3 请求装配

`loadOverview()` 按当前筛查条件调用：

- `fetchDashboardOverview({ dateFrom, dateTo, bizLine })`

刷新按钮也复用当前筛查条件。

## 3. 影响文件

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
