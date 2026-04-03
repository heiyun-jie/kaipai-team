# 00-30 后台邀请治理结构优化 - 执行记录

> 执行日期：2026-04-03
> 范围：`kaipai-admin` referral 模块治理摘要卡与时间窗口筛查

## 1. 本轮结论

- `邀请记录` 已补齐治理摘要卡、注册时间筛查、生效时间筛查。
- `异常邀请` 已补齐治理摘要卡、注册时间筛查。
- `邀请资格` 已补齐生效时间筛查。
- 治理摘要卡已收口到共享组件，未在页面内重复复制样式。

## 2. 落地文件

- `kaipai-admin/src/components/business/GovernanceOverviewCards.vue`
- `kaipai-admin/src/views/referral/RecordsView.vue`
- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/referral/EligibilityView.vue`

## 3. 结构调整说明

### 3.1 治理摘要卡

- `RecordsView.vue`
  - 新增 `查询规模 / 当前页有效记录 / 当前页风险命中` 三张摘要卡。
- `RiskView.vue`
  - 新增 `查询规模 / 当前页待处置 / 当前页已处理` 三张摘要卡。
- 共享组件统一承担：
  - label
  - badge
  - tone
  - value
  - hint

### 3.2 时间窗口筛查

- `RecordsView.vue`
  - `registeredAtFrom / registeredAtTo`
  - `validatedAtFrom / validatedAtTo`
- `RiskView.vue`
  - `registeredAtFrom / registeredAtTo`
- `EligibilityView.vue`
  - `effectiveFrom / effectiveTo`

## 4. 交互边界确认

- 未新增后端接口参数。
- 未修改 referral API 路径。
- 未修改 referral 状态流转与审核动作。
- 重置操作已同步清空新增时间窗口字段。

## 5. 验证结果

- 已执行：`cd kaipai-admin && npm run build`
- 结果：通过
- 保留告警：
  - Vite chunk size warning
  - Sass legacy JS API deprecation warning

这两项属于现存工程告警，本轮未新增阻塞错误。
