# 00-45 设计说明

## 1. 设计原则

- referral 四页的治理页面层级尽量一致
- 主操作与筛选操作分层，不把治理动作埋进筛选区
- 本轮只补结构和展示层，不动业务接口

## 2. 设计策略

### 2.1 页面层级

`EligibilityView` 对齐为：

- `PageContainer #actions`
- `ReferralGovernanceNav`
- `GovernanceOverviewCards`
- `FilterPanel`
- dashboard 来源提示
- 列表 / 详情 / 操作弹窗

### 2.2 概览卡指标

使用当前列表数据计算：

- 查询规模：`total`
- 当前页生效中资格：`status === 1`
- 当前页已失效资格：`status === 2 || status === 3`
- 当前页手工来源资格：`sourceType === 'manual'`

### 2.3 主操作

把“手工发放”从 `FilterPanel` actions 移到 `PageContainer` 的 `#actions`，与 `PoliciesView` 的“新建规则”保持同一层级。

## 3. 影响文件

- `kaipai-admin/src/views/referral/EligibilityView.vue`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
