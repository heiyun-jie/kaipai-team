# 00-98 当前阶段后台账号治理维护弹窗密度对齐（Current Phase Admin System Account Governance Maintenance Dialog Density Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-97 current-phase-admin-system-account-governance-detail-drawer-density-alignment
> 记录目的：在 `00-97` 完成 `system/admin-users` 详情抽屉收口后，继续把新建 / 编辑、绑定角色、重置密码三个维护弹窗的壳层与表单密度收口到当前 refined admin shell。

## 1. 背景

截至 `2026-04-22`：

- `00-95` 已完成 `system/admin-users` 首屏结构收口
- `00-96` 已完成主表密度收口
- `00-97` 已完成详情抽屉收口
- 当前页剩余最明显的视觉残差已收窄到三个维护弹窗：
  - 新建 / 编辑后台账号
  - 绑定后台账号角色
  - 重置后台账号密码

真实运行态截图已确认：

- 新建账号：`D:\XM\kaipai-team\output\playwright\00-98\admin-users-create-before.png`
- 绑定角色：`D:\XM\kaipai-team\output\playwright\00-98\admin-users-bind-before.png`
- 重置密码：`D:\XM\kaipai-team\output\playwright\00-98\admin-users-reset-before.png`

当前差异：

1. 三个弹窗都仍沿用较厚的共享 dialog shell
2. `dialog-intro` 高度仍约 `117px`
3. footer 高度仍约 `75px`
4. 单个表单项高度普遍仍约 `78px`
5. 绑定角色 / 重置密码中的 textarea 区域进一步拉高整体高度

### 当前量化

- 新建账号弹窗：`720 × 743`
  - body：`686 × 567`
  - intro：`634 × 117`
  - 6 个表单项：均约 `78px`
- 绑定角色弹窗：`560 × 599`
  - body：`526 × 423`
  - intro：`474 × 117`
  - 表单项：`78px / 126px`
- 重置密码弹窗：`560 × 674`
  - body：`526 × 498`
  - intro：`474 × 117`
  - 表单项：`78px / 78px / 105px`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-98`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\system\AdminUsersView.vue` 中三个维护弹窗：
  - 新建 / 编辑后台账号
  - 绑定后台账号角色
  - 重置后台账号密码
- 用真实浏览器复核 `http://127.0.0.1:5100/system/admin-users`

### 2.2 本轮不处理

- 不改首屏 shell card
- 不改主表
- 不改详情抽屉
- 不改启用 / 禁用确认弹窗
- 不改真实接口与账号角色模型

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `AdminUsersView.vue` 的三个维护弹窗，不扩到主表、详情抽屉和共享 `AuditConfirmDialog`。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只承接后台账号、角色绑定、密码处置与启停用，不扩展新的组织或权限模型。

### 3.2 弹窗密度合同

- **R4** 三个维护弹窗的 header / body / footer 必须明显收紧，不再维持当前偏厚的 shell。
- **R5** `dialog-intro` 必须明显收口，不再维持当前约 `117px` 的占高。
- **R6** 表单项高度必须明显下降，不再普遍维持当前约 `78px` 的节奏。
- **R7** textarea 与角色选择区必须更轻，但不能牺牲可读和可操作性。

### 3.3 治理要求

- **R8** 本轮必须保持字段语义、表单校验、提交动作与接口调用不变。
- **R9** 本轮必须通过独立 `00-98` 承接，不继续混入 `00-97`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-98` Spec，并明确它只处理 `system/admin-users` 三个维护弹窗密度
- [ ] 已完成 header/body/footer、dialog-intro、表单项与 textarea / 角色选择区的局部收口
- [ ] 已通过真实浏览器复核 `system/admin-users`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
