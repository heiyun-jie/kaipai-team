# 00-103 当前阶段后台角色治理角色清单表格密度对齐（Current Phase Admin System Roles Directory Table Density Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-102 current-phase-admin-system-roles-recruit-matrix-card-alignment
> 记录目的：在 `00-102` 完成 `system/roles` 第二张招募矩阵卡片收口后，继续把底部 `角色清单` 的表格行高、权限概览 cell、操作列与分页区密度收口到当前 refined admin shell。

## 1. 背景

截至 `2026-04-22`：

- `00-100` 已完成 `system/roles` 首屏结构收口
- `00-101` 已完成首张 AI 授权矩阵表格收口
- `00-102` 已完成第二张招募治理授权矩阵卡片收口
- 当前 residual 已收窄到底部 `角色清单`

真实运行态截图已确认：

- 当前页：`D:\XM\kaipai-team\output\playwright\00-103\roles-directory-before.png`

当前差异：

1. role directory card 仍约 `1134 × 323`
2. 首个表格行仍约 `1380 × 81`
3. 权限概览 stacked cell 仍约 `196 × 50`
4. 操作区仍约 `256 × 28`
5. fixed 操作列仍约 `280 × 81`

### 当前量化

- role directory card：`1134 × 323`
- table header：`1084 × 53`
- table：`1084 × 133`
- 首个表格行：`1380 × 81`
- 权限概览 stacked cell：`196 × 50`
- 操作区：`256 × 28`
- fixed 操作列：`280 × 81`
- pager：`1084 × 49`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-103`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue` 底部 `角色清单`：
  - card header
  - 表格 row height / cell padding
  - 权限概览 stacked cell
  - fixed 操作列
  - pager / pagination 间距
- 用真实浏览器复核 `http://127.0.0.1:5100/system/roles`

### 2.2 本轮不处理

- 不改顶部 shell card
- 不改 FilterPanel
- 不改首张 AI 授权矩阵
- 不改第二张招募治理授权矩阵
- 不改详情抽屉和维护弹窗
- 不改角色模型与真实接口

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `RolesView.vue` 底部 `角色清单` 表格密度，不扩到底部以外的 card 和弹层。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只承接后台角色、AI 授权收口和招募治理授权，不扩展新的角色体系。

### 3.2 表格密度合同

- **R4** 首个角色清单行高度必须明显下降，不再维持当前约 `81px` 的厚重观感。
- **R5** 权限概览 stacked cell 必须收紧主副文本 gap、字号与行高。
- **R6** 固定操作列必须更轻，不再维持当前约 `280 × 81` 的厚列观感。
- **R7** 分页区必须继续保持单行可读，但上下占高应更轻。
- **R8** `查看详情 / 编辑 / 复制 / 禁用(启用)` 的动作语义必须保持不变。

### 3.3 治理要求

- **R9** 本轮必须保持角色清单字段语义、跳转动作与接口调用不变。
- **R10** 本轮必须通过独立 `00-103` 承接，不继续混入 `00-102`。
- **R11** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R12** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-103` Spec，并明确它只处理 `system/roles` 底部角色清单表格密度
- [ ] 已完成 row height、权限概览 stacked cell、fixed 操作列与 pager 的局部收口
- [ ] 已通过真实浏览器复核 `system/roles`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
