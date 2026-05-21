# 00-102 当前阶段后台角色治理招募矩阵卡片对齐（Current Phase Admin System Roles Recruit Matrix Card Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-101 current-phase-admin-system-roles-ai-matrix-table-density-alignment
> 记录目的：在 `00-101` 完成 `system/roles` 首张 AI 授权矩阵表格收口后，继续把第二张 `招募治理授权矩阵` 的卡片壳层、表格密度与长权限标签收口到当前 refined admin shell。

## 1. 背景

截至 `2026-04-22`：

- `00-100` 已完成 `system/roles` 的首屏 shell、筛选区和首张 AI 矩阵壳层收口
- `00-101` 已完成首张 AI 授权矩阵的表格密度收口
- 当前 residual 已收窄到第二张 `招募治理授权矩阵`

真实运行态截图已确认：

- 当前页：`D:\XM\kaipai-team\output\playwright\00-102\roles-recruit-matrix-before.png`

当前差异：

1. 第二张矩阵卡整体仍约 `1134 × 567`
2. 首个矩阵行仍约 `1500 × 213`
3. 角色 stacked cell 仍约 `196 × 50`
4. 权限覆盖 tag list 仍约 `396 × 106`
5. 待补权限 tag list 因长权限文案被撑到约 `296 × 182`
6. 操作区仍约 `146 × 28`

### 当前量化

- second card：`1134 × 567`
- header：`1132 × 80`
- body：`1132 × 485`
- matrix summary：`1084 × 85`
- alert：`1084 × 63`
- table：`1084 × 265`
- 首个矩阵行：`1500 × 213`
- 角色 stacked cell：`196 × 50`
- 权限覆盖 tag list：`396 × 106`
- 待补权限 tag list：`296 × 182`
- 操作区：`146 × 28`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-102`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue` 的第二张 `招募治理授权矩阵`：
  - card header / body padding
  - alert / table 进入关系
  - row height / cell padding
  - stacked cell / tag list / fixed 操作列
  - 待补权限标签的页面内紧凑文案表达
- 用真实浏览器复核 `http://127.0.0.1:5100/system/roles`

### 2.2 本轮不处理

- 不改顶部 shell card
- 不改 FilterPanel
- 不改首张 AI 授权矩阵的密度策略
- 不改底部 `角色清单`
- 不改详情抽屉和弹窗视觉
- 不改权限模型与真实接口

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `RolesView.vue` 第二张招募治理授权矩阵卡片，不扩到底部角色清单和其他弹层。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只承接后台角色、AI 授权收口和招募治理授权，不扩展新的角色体系。

### 3.2 卡片与表格密度合同

- **R4** 第二张矩阵卡的整体高度必须明显下降，不再维持当前约 `567px` 的厚卡观感。
- **R5** 首个矩阵行高度必须显著下降，不再被长权限标签撑到约 `213px`。
- **R6** 角色 stacked cell 必须收紧主副文本 gap、字号与行高。
- **R7** 权限覆盖与待补权限 tag list 必须更轻；其中待补权限允许使用页面内紧凑标签文案，但不得丢失原有权限语义。
- **R8** 操作列必须更轻，但不得改变 `查看详情 / 补权限` 的动作语义。

### 3.3 治理要求

- **R9** 本轮必须保持招募矩阵字段语义、跳转动作与接口调用不变。
- **R10** 本轮必须通过独立 `00-102` 承接，不继续混入 `00-101`。
- **R11** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R12** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-102` Spec，并明确它只处理 `system/roles` 第二张招募治理授权矩阵卡片
- [ ] 已完成 recruit matrix card 的 card shell、row height、tag list 与操作列的局部收口
- [ ] 已通过真实浏览器复核 `system/roles`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
