# 00-30 设计说明

## 1. 设计原则

- 优先补“治理视角”，不重写 referral 业务动作
- 优先复用共享壳层，不在页面里继续散落相同概览卡样式
- 时间筛查只接已有字段，避免把前端改成接口设计入口

## 2. 设计策略

### 2.1 治理摘要卡

- 新增共享组件，收敛以下展示结构：
  - 卡片标题
  - badge / tone
  - 主值
  - 辅助说明
- `邀请记录` 和 `异常邀请` 通过当前查询结果与当前页样本计算摘要：
  - 查询规模使用 `total`
  - 状态型指标使用当前页 `rows`
- 页面文案必须明确“当前页”与“当前查询”边界，避免误导为全量统计接口。

### 2.2 时间窗口筛查

- `邀请记录`
  - `registeredAtFrom / registeredAtTo`
  - `validatedAtFrom / validatedAtTo`
- `异常邀请`
  - `registeredAtFrom / registeredAtTo`
- `邀请资格`
  - `effectiveFrom / effectiveTo`

实现方式：

- 页面内增加时间范围计算属性，负责把日期区间与 query 字段双向映射。
- 查询请求继续直接复用已有 `fetchReferral*` API。
- `resetFilters()` 统一清空对应 query 字段。

## 3. 影响文件

- `kaipai-admin/src/components/business/GovernanceOverviewCards.vue`
- `kaipai-admin/src/views/referral/RecordsView.vue`
- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/referral/EligibilityView.vue`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
