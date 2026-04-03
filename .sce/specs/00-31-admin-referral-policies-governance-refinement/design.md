# 00-31 设计说明

## 1. 设计原则

- 规则页优先表达“治理态势”，而不是一进页就直接操作表格
- 不改变 policy 模型，只提升信息层次
- 与 `00-30` 使用同一套治理摘要视觉语言

## 2. 设计策略

### 2.1 治理摘要卡

基于当前查询结果与当前页 `rows` 计算：

- 查询规模：`total`
- 当前页启用规则：`enabled === 1`
- 当前页自动发放：`autoGrantEnabled === 1`
- 当前页频控覆盖：`sameDeviceLimit != null || hourlyInviteLimit != null`

说明文案必须明确“当前页”边界，避免误导为全量接口统计。

### 2.2 列表语义头

在表格前加入结构头：

- eyebrow
- 标题
- 提示说明

用于说明当前列表主要阅读以下三类字段：

- 资格门槛
- 频控约束
- 自动发放

### 2.3 空态

表格空态改成治理配置语义：

- 标题：当前条件下没有邀请规则
- 说明：提示切换启用状态或清空规则名称继续查看

## 3. 影响文件

- `kaipai-admin/src/views/referral/PoliciesView.vue`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
