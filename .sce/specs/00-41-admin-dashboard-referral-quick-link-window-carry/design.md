# 00-41 设计说明

## 1. 设计原则

- 按治理主时间轴映射，不追求“所有时间字段都一起带”
- 主操作与快捷入口统一走 `openDashboardRoute()`
- 目标页仅承接已映射的主时间轴 query

## 2. 设计策略

### 2.1 dashboard 映射

`OverviewView.buildRouteQuery()` 新增：

- `/referral/records`
  - `registeredAtFrom=dateFrom`
  - `registeredAtTo=dateTo`
- `/referral/eligibility`
  - `effectiveFrom=dateFrom`
  - `effectiveTo=dateTo`

### 2.2 目标页回填

`RecordsView`

- 读取 `route.query.registeredAtFrom/registeredAtTo`
- 回填 `filters.registeredAtFrom/registeredAtTo`
- 触发自动查询

`EligibilityView`

- 读取 `route.query.effectiveFrom/effectiveTo`
- 回填 `filters.effectiveFrom/effectiveTo`
- 触发自动查询

## 3. 影响文件

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/referral/RecordsView.vue`
- `kaipai-admin/src/views/referral/EligibilityView.vue`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
