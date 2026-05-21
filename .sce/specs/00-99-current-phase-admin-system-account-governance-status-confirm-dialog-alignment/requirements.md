# 00-99 当前阶段后台账号治理状态确认弹窗密度对齐（Current Phase Admin System Account Governance Status Confirm Dialog Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-98 current-phase-admin-system-account-governance-maintenance-dialog-density-alignment
> 记录目的：在 `00-98` 完成 `system/admin-users` 维护弹窗收口后，继续把启用 / 禁用确认弹窗的壳层、meta 区与原因输入区收口到当前 refined admin shell。

## 1. 背景

截至 `2026-04-22`：

- `00-95` 已完成 `system/admin-users` 首屏结构收口
- `00-96` 已完成主表密度收口
- `00-97` 已完成详情抽屉收口
- `00-98` 已完成新建 / 编辑、绑定角色、重置密码三个维护弹窗收口
- 当前页剩余最明显的视觉残差已收窄到启用 / 禁用确认弹窗

真实运行态截图已确认：

- 当前页：`D:\XM\kaipai-team\output\playwright\00-99\admin-users-status-before.png`

当前差异：

1. 状态确认弹窗仍约 `520 × 716`
2. `dialog-intro` 仍约 `117px`
3. `dialog-meta` 仍约 `204px`
4. `textarea` 仍约 `96px`
5. footer 仍约 `75px`

### 当前量化

- 弹窗：`520 × 716`
- header：`67px`
- body：`540px`
- footer：`75px`
- intro：`117px`
- meta：`434 × 204`
- meta item：`45px`
- textarea：`434 × 96`
- tip：`434 × 15`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-99`
- 只处理 `system/admin-users` 中启用 / 禁用确认弹窗的视觉密度
- 允许为 `AuditConfirmDialog` 增加**可选**局部扩展参数，但不得改变其它页面默认行为
- 用真实浏览器复核 `http://127.0.0.1:5100/system/admin-users`

### 2.2 本轮不处理

- 不改首屏 shell card
- 不改主表
- 不改详情抽屉
- 不改新建 / 编辑、绑定角色、重置密码三个维护弹窗
- 不改真实接口与启停用逻辑

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `system/admin-users` 的状态确认弹窗，不扩到 `AuditConfirmDialog` 的其它使用页默认表现。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只承接后台账号、角色绑定、密码处置与启停用，不扩展新的组织或权限模型。

### 3.2 弹窗密度合同

- **R4** 状态确认弹窗的 header / body / footer 必须明显收紧。
- **R5** `dialog-intro` 必须明显收口，不再维持当前约 `117px` 的占高。
- **R6** `dialog-meta` 与 meta item 必须更轻，不再维持当前约 `204px / 45px` 的厚度。
- **R7** 原因输入区与 tip 必须更轻，但不能影响必填原因的可读与可填性。

### 3.3 治理要求

- **R8** 本轮必须保持启用 / 禁用确认链路、meta 字段语义与提交动作不变。
- **R9** 本轮必须通过独立 `00-99` 承接，不继续混入 `00-98`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-99` Spec，并明确它只处理 `system/admin-users` 状态确认弹窗
- [ ] 已完成 header/body/footer、dialog-intro、dialog-meta 与原因输入区的局部收口
- [ ] 已通过真实浏览器复核 `system/admin-users`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
