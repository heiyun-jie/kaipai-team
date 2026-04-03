# 00-45 后台邀请资格治理页结构对齐（Admin Referral Eligibility Governance Structure Alignment）

> 状态：进行中 | 优先级：P1 | 依赖：00-44 admin-referral-governance-cross-nav-context-carry
> 记录目的：把 `EligibilityView` 对齐到 referral 其他治理页的页面结构，补齐概览卡，并提升页级主操作层级。

## 1. 背景

referral 四页已经具备统一治理导航，但结构层级仍不完全一致：

- `RiskView`、`RecordsView`、`PoliciesView` 都有治理概览卡
- `EligibilityView` 目前缺少概览卡
- `EligibilityView` 的“手工发放”还放在 `FilterPanel` actions 内
- `PoliciesView` 的“新建规则”已经放在 `PageContainer` 页级 actions 中

这会导致 eligibility 页面在治理主链中层级偏低，主操作埋得过深，也不利于形成统一的治理页结构认知。

## 2. 范围

### 2.1 本轮必须处理

- `kaipai-admin/src/views/referral/EligibilityView.vue`

### 2.2 本轮不处理

- eligibility 业务字段和接口改造
- 其他 referral 页概览卡指标调整
- 详情抽屉信息结构改造

## 3. 需求

### 3.1 页面结构对齐

- **R1** `EligibilityView` 必须补齐与其他 referral 治理页一致的概览卡区域。
- **R2** 页面结构应调整为：页级 actions -> 治理导航 -> 概览卡 -> 筛选区 -> 来源提示 -> 列表。

### 3.2 主操作层级

- **R3** “手工发放”必须提升到 `PageContainer` 的页级 actions 中。
- **R4** `FilterPanel` actions 中不再保留“手工发放”，只保留筛选相关操作。

### 3.3 指标约束

- **R5** 概览卡至少应覆盖当前查询规模、当前页生效中资格、当前页已失效资格、当前页手工来源资格。
- **R6** 本轮不得破坏 dashboard 来源提示、筛选回填和治理导航行为。

## 4. 验收标准

- [ ] 已新增独立 Spec 并登记索引与代码映射
- [ ] `EligibilityView` 已补齐概览卡并提升页级主操作
- [ ] `npm run build` 在 `kaipai-admin` 通过
