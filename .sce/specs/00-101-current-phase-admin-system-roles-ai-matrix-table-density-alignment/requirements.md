# 00-101 当前阶段后台角色治理 AI 矩阵表格密度对齐（Current Phase Admin System Roles AI Matrix Table Density Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-100 current-phase-admin-system-roles-first-screen-alignment
> 记录目的：在 `00-100` 完成 `system/roles` 首屏结构收口后，继续把第一张 `AI 授权收口矩阵` 的表格行高、tag list 层级与操作列密度收口到当前 refined admin shell。

## 1. 背景

截至 `2026-04-22`：

- `00-100` 已完成 `system/roles` 的首屏 shell、筛选区和首张 AI 矩阵壳层收口
- 当前 residual 已收窄到首张 AI 授权矩阵的表格区
- 当前页没有 direct reference 子页；因此本轮目标不是伪造 reference 新页面，而是把角色治理矩阵表继续收口为更轻的治理 ledger

真实运行态截图已确认：

- 当前页：`D:\XM\kaipai-team\output\playwright\00-101\roles-ai-matrix-before.png`

当前差异：

1. 首个矩阵行高度仍约 `99px`
2. 角色 stacked cell 约 `50px`
3. 权限覆盖 tag list 约 `68px`，是当前行高的主要来源
4. 操作区约 `146 × 28`

### 当前量化

- 首个矩阵行：`1420 × 99`
- 角色 stacked cell：`196 × 50`
- 权限覆盖 tag list：`336 × 68`
- 待补权限 tag list：`276 × 23`
- 操作区：`146 × 28`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-101`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue` 的首张 `AI 授权收口矩阵` 表格区：
  - row height / cell padding
  - stacked cell
  - tag list
  - fixed 操作列
- 用真实浏览器复核 `http://127.0.0.1:5100/system/roles`

### 2.2 本轮不处理

- 不改顶部 shell card
- 不改 FilterPanel
- 不改首张 AI 矩阵的 summary / alert
- 不改第二张 `招募治理授权矩阵`
- 不改底部 `角色清单`
- 不改详情抽屉和弹窗
- 不改权限模型与真实接口

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `RolesView.vue` 首张 AI 授权矩阵表格密度，不扩到第二矩阵和角色清单。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只承接后台角色、AI 授权收口和招募治理授权，不扩展新的角色体系。

### 3.2 表格密度合同

- **R4** 首张 AI 矩阵首行高度必须明显下降，不再维持当前约 `99px` 的厚重观感。
- **R5** 角色 stacked cell 必须收紧主副文本 gap、字号与行高。
- **R6** 权限覆盖 tag list 必须更轻，避免多行厚标签继续主导行高。
- **R7** 操作列必须更轻，但不得改变 `查看详情 / 补权限` 的动作语义。

### 3.3 治理要求

- **R8** 本轮必须保持 AI 矩阵字段语义、跳转动作与接口调用不变。
- **R9** 本轮必须通过独立 `00-101` 承接，不继续混入 `00-100`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-101` Spec，并明确它只处理 `system/roles` 首张 AI 授权矩阵表格密度
- [ ] 已完成 row height、stacked cell、tag list 与操作列的局部收口
- [ ] 已通过真实浏览器复核 `system/roles`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
