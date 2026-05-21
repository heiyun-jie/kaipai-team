# 00-106 当前阶段后台角色治理状态确认弹窗对齐（Current Phase Admin System Roles Status Confirm Dialog Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-105 current-phase-admin-system-roles-maintenance-dialog-density-alignment
> 记录目的：在 `00-105` 完成 `system/roles` 维护弹窗收口后，继续把 `启用 / 禁用` 状态确认弹窗的壳层、intro、meta 区与原因输入区收口到当前 refined admin shell。

## 1. 背景

截至 `2026-04-22`：

- `00-100` 到 `00-105` 已连续收口 `system/roles` 的首屏、矩阵、角色清单、详情抽屉和维护弹窗
- 当前剩余高感知 UI 已收窄到状态确认弹窗

真实运行态截图已确认：

- 当前页：`D:\XM\kaipai-team\output\playwright\00-106\roles-status-before.png`

当前差异：

1. 状态确认弹窗约 `520 × 687`
2. header 仍约 `67px`
3. body 仍约 `511px`
4. footer 仍约 `75px`
5. `dialog-intro` 仍约 `117px`
6. `dialog-meta` 仍约 `434 × 204`
7. textarea 仍约 `434 × 96`

### 当前量化

- 弹窗：`520 × 687`
- header：`67px`
- body：`511px`
- footer：`75px`
- intro：`117px`
- meta：`434 × 204`
- meta item：`45px`
- textarea：`434 × 96`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-106`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue` 的启用 / 禁用确认弹窗
- 通过 `AuditConfirmDialog` 的 page-local 扩展入口完成：
  - dialog width
  - dialog shell
  - `dialog-content`
  - `dialog-intro`
  - `dialog-meta`
  - `textarea`
  - `dialog-tip`
- 用真实浏览器复核 `http://127.0.0.1:5100/system/roles`

### 2.2 本轮不处理

- 不改首屏与三张主卡
- 不改角色清单表格
- 不改详情抽屉
- 不改新建 / 编辑 / 复制维护弹窗
- 不改 `AuditConfirmDialog` 其它页面的默认表现
- 不改角色模型与真实接口

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `RolesView.vue` 的状态确认弹窗，不扩到维护弹窗和其它页面。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只承接后台角色、AI 授权收口和招募治理授权，不扩展新的角色体系。

### 3.2 弹窗密度合同

- **R4** 状态确认弹窗必须不再维持当前约 `520 × 687` 的厚重观感。
- **R5** header、footer 与 `dialog-intro` 必须明显收紧。
- **R6** `dialog-meta` 与 meta item 必须更轻。
- **R7** textarea 和 tip 区必须更紧，但仍保留可填写空间。
- **R8** 维持 `查看详情 / 编辑 / 复制 / 禁用(启用)` 之后的操作语义不变。

### 3.3 治理要求

- **R9** 本轮必须保持启用 / 禁用动作语义、meta 字段与提交链路不变。
- **R10** 本轮必须通过独立 `00-106` 承接，不继续混入 `00-105`。
- **R11** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R12** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-106` Spec，并明确它只处理 `system/roles` 状态确认弹窗
- [ ] 已完成 dialog shell、intro、meta、textarea 与 tip 的局部收口
- [ ] 已通过真实浏览器复核 `system/roles`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
