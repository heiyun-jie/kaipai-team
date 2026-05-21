# 00-159 后台内容治理 UI 与审批补齐需求

## 开头先回答三个问题

1. 这次解决什么：修复后台 `content/templates` 模板编辑报 `shareCard 缺失或格式错误`、所有表格固定操作列 hover 透层、联系方式申请待处理缺少同意/拒绝按钮、用户详情抽屉展示无关资金信息。
2. 为什么现在做：这些问题都发生在当前线上后台主链路，影响运营配置模板、审批联系方式申请和查看用户详情，属于后台可用性缺口。
3. 不做什么：不新增资金、订单、退款业务能力；不把联系方式审批做成新的小程序流程；不扩大模板配置合同，只做旧数据兼容和当前可视化编辑可用性恢复。

## 目标

- 风格模板编辑可以打开已有线上模板，即使历史 `artifactPresetJson` 缺少 `miniProgramCard` / 旧 `shareCard`、`poster` 或 `pageConfig` 节点，也使用当前默认配置补齐可视化编辑态。
- 后台所有 Element Plus 表格的右侧固定操作列必须是稳定、不可透层的独立层，hover 时不能露出左侧单元格内容。
- `/content/contact-requests` 待处理记录必须提供后台同意和拒绝操作，并调用后台管理接口完成状态变更。
- 用户管理详情抽屉删除资金概览模块，不再展示支付订单数、支付总额、退款单数、退款总额、成功退款等当前系统不需要的信息。

## 范围

- 后台前端：`kaipai-admin/src/views/content/TemplatesView.vue`、`ContactRequestsView.vue`、`UserCenterView.vue`、`src/styles/index.scss`、权限常量和接口封装。
- 后端：`AdminContentController`、`ShareCardContactRequestService` 和实现类，补后台联系方式审批接口。
- 数据库迁移：补齐当前 `ADMIN` 角色的联系方式审批动作权限，避免上线后按钮因权限缺失不可见。

## 验收标准

- 点击 `http://kplyyk.com/content/templates` 中已有模板的“基础编辑”不再出现 `shareCard 缺失或格式错误`；保存时仍写当前后端合同 `miniProgramCard`。
- 任一带 `fixed="right"` 操作列的表格，鼠标 hover 行时右侧操作列背景不透明，不再看到被覆盖列的文字、标签或 hover 色块。
- 联系方式申请列表中 `pending` 行展示“同意”和“拒绝”按钮；点击后接口成功，列表刷新，详情抽屉状态同步。
- 非 `pending` 行不展示同意/拒绝动作，只保留查看详情。
- 用户详情抽屉不再出现“资金概览”卡片和资金相关字段。
- `kaipai-admin` 类型检查和构建通过。
- `kaipaile-server` 编译通过。
