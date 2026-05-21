# 00-159 设计

## 开头先回答三个问题

1. 这次改哪里：前端修复模板配置解析、表格固定列样式、联系方式申请动作和用户详情抽屉；后端只补后台联系方式审批接口。
2. 为什么这样改：模板 JSON 历史数据已经在线上存在，直接强制报错会阻断编辑；联系方式审批是后台治理动作，不能只靠用户端持卡人接口代替。
3. 不改哪里：不改小程序联系方式申请流程，不重构模板 JSON schema，不删除后端已有 payment/refund DTO 字段，只移除当前后台抽屉展示。

## 模板配置兼容

`TemplatesView.vue` 当前 `hydrateArtifactConfig` 把 `shareCard`、`poster`、`pageConfig` 都当成强必填节点读取。后端当前分享产物合同使用 `miniProgramCard`，线上历史模板可能没有 `shareCard`，因此编辑时会直接抛错。

本轮策略：

- 保留 `parseRequiredObjectJson` 对根 JSON 的对象校验。
- 读取时优先识别 `miniProgramCard`，兼容旧 `shareCard`，缺失时使用当前 `initializeArtifactConfig` 默认值作为单一默认来源。
- 节点缺失时沿用默认值；节点存在但字段缺失时只补缺失字段。
- 枚举值非法时沿用当前默认枚举，避免旧数据阻断运营保存。
- 保存时仍由 `buildArtifactJson` 写出完整 `miniProgramCard` 新合同，后续保存后的模板会补齐完整结构。

## 表格固定操作列

当前全局样式对 Element Plus 固定右列使用半透明背景，并允许 `overflow: visible`。在横向滚动和 hover 状态下，底层单元格内容会透到固定操作列下方。

本轮策略：

- 在 `src/styles/index.scss` 统一处理所有 `.table-card` 下的 `el-table-fixed-column--right`。
- 固定右列、header、body、footer、patch 均使用不透明背景色。
- 固定右列 cell 关闭透出式 overflow，按钮仍通过内部 flex 换行展示。
- 保留固定列阴影，继续表达操作列浮在右侧。

## 联系方式申请后台审批

用户端接口 `/card/contact-requests/{id}/approve|reject` 需要持卡人身份，后台不能伪装成持卡人调用。

本轮后端新增：

- `POST /admin/content/contact-requests/{requestId}/approve`
- `POST /admin/content/contact-requests/{requestId}/reject`

权限：

- `action.content.contact-request.approve`
- `action.content.contact-request.reject`

服务层新增后台审批方法，只校验申请存在且状态为 `pending`，不校验持卡人身份。审批结果继续写入 `status`、`decisionNote`、`decidedAt`，复用同一张 `share_card_contact_request` 表作为事实源。

前端：

- `ContactRequestsView.vue` 为 pending 行展示“同意”和“拒绝”。
- 使用确认弹窗收集处理备注；拒绝要求备注，同意备注可选。
- 成功后刷新列表；若详情抽屉打开则刷新详情。

## 用户详情抽屉资金信息退场

当前系统没有资金相关运营闭环时，用户详情抽屉展示资金概览会误导运营。

本轮只移除展示层：

- 删除“资金概览”卡片。
- 删除 `commerceBlocks` 计算属性和 `formatCurrency` 导入。
- 不改后端 `UserCenterDetail` 响应结构，避免影响其它页面或后续历史审计。
