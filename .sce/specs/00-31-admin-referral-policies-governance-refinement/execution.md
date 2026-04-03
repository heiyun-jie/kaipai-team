# 00-31 后台邀请规则治理页优化 - 执行记录

> 执行日期：2026-04-03
> 范围：`kaipai-admin/src/views/referral/PoliciesView.vue`

## 1. 本轮结论

- `PoliciesView` 已补规则治理摘要卡。
- `PoliciesView` 已补规则清单语义头。
- `PoliciesView` 已补治理配置语义空态。
- 规则编辑、启停和详情流程保持不变。

## 2. 落地文件

- `kaipai-admin/src/views/referral/PoliciesView.vue`

## 3. 结构调整说明

### 3.1 规则治理摘要卡

基于当前查询结果与当前页样本，补齐四张摘要卡：

- 查询规模
- 当前页启用规则
- 当前页自动发放
- 当前页频控覆盖

说明文案均显式标注为当前查询 / 当前页口径，避免误导为独立统计接口。

### 3.2 列表语义头

表格前已新增规则清单语义头，明确本区块用于核对：

- 资格门槛
- 频控约束
- 自动发放

### 3.3 空态

空态从默认表格空白改为治理配置语义：

- 标题：`当前条件下没有邀请规则`
- 说明：`可以清空规则名称或切换启用状态，继续查看其他治理配置。`

## 4. 交互边界确认

- 未新增筛选参数。
- 未修改后端 policy API。
- 未修改规则编辑弹窗字段。
- 未修改启用 / 停用 / 保存动作。

## 5. 验证结果

- 已执行：`cd kaipai-admin && npm run build`
- 结果：通过
- 保留告警：
  - Vite chunk size warning
  - Sass legacy JS API deprecation warning

本轮未新增阻塞错误。
