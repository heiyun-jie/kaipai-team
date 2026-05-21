# 00-96 当前阶段后台账号治理表格密度对齐（Current Phase Admin System Account Governance Table Density Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-95 current-phase-admin-system-account-governance-first-screen-alignment
> 记录目的：在 `00-95` 完成 `system/admin-users` 首屏结构收口后，继续把主表的行高、单元格层级与操作列密度收口到当前 refined admin shell。

## 1. 背景

截至 `2026-04-22`：

- `00-95` 已完成 `system/admin-users` 首屏结构收口
- 当前残余已经收窄到主表区，不再是 page-level 首屏占高问题
- 当前页没有 direct reference 子页；因此本轮目标不是伪造 reference 新页面，而是把表格区继续收口为更轻、更稳的系统域治理清单

真实运行态截图已确认：

- 当前页：`D:\XM\kaipai-team\output\playwright\00-96\admin-users-table-before.png`

当前差异：

1. 首行高度仍约 `95px`
2. 联系方式 stacked cell 层级偏松
3. 角色标签仍偏厚
4. 操作列仍偏重，导致行高被进一步拉高

### 当前量化

- table card：`1134 × 424`
- 首个表格行：约 `95px`
- 首个联系方式 stacked cell：约 `50px`
- 首个角色 tag list：约 `30px`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-96`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\system\AdminUsersView.vue` 的主表区：
  - table header / body 局部密度
  - 联系方式 stacked cell
  - 角色 tag list
  - 操作列布局与列宽
- 用真实浏览器复核 `http://127.0.0.1:5100/system/admin-users`

### 2.2 本轮不处理

- 不改首屏 shell card
- 不改 FilterPanel
- 不改详情抽屉
- 不改创建 / 编辑 / 绑定 / 重置密码 / 启停用弹窗
- 不改真实接口与账号角色模型

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `AdminUsersView.vue` 主表密度，不扩到首屏 shell、弹窗和接口。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只承接后台账号、角色绑定、密码处置与启停用，不扩展新的组织或权限模型。

### 3.2 表格密度合同

- **R4** 表格首行高度必须明显下降，不再维持当前约 `95px` 的厚重观感。
- **R5** 联系方式 stacked cell 必须收紧主副文本 gap、字号与行高。
- **R6** 角色 tag list 必须更轻，避免标签壳层继续抬高行高。
- **R7** 操作列必须更轻，优先通过列宽、gap、按钮字号与换行策略收口，而不是改成交互完全不同的新组件。

### 3.3 治理要求

- **R8** 本轮必须保持表格字段语义、详情动作与状态动作不变。
- **R9** 本轮必须通过独立 `00-96` 承接，不继续混入 `00-95`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-96` Spec，并明确它只处理 `system/admin-users` 主表密度
- [ ] 已完成行高、stacked cell、tag list 与操作列的局部收口
- [ ] 已通过真实浏览器复核 `system/admin-users`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
