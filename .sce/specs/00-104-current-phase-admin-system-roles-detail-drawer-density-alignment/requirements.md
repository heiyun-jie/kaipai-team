# 00-104 当前阶段后台角色治理详情抽屉密度对齐（Current Phase Admin System Roles Detail Drawer Density Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-103 current-phase-admin-system-roles-directory-table-density-alignment
> 记录目的：在 `00-103` 完成 `system/roles` 底部角色清单表格收口后，继续把 `角色详情` 抽屉的壳层、hero、字段块与权限 tag 密度收口到当前 refined admin shell。

## 1. 背景

截至 `2026-04-22`：

- `00-100` 已完成 `system/roles` 首屏结构收口
- `00-101` 已完成首张 AI 授权矩阵表格收口
- `00-102` 已完成第二张招募治理授权矩阵卡片收口
- `00-103` 已完成底部角色清单表格收口
- 当前 residual 已收窄到 `角色详情` 抽屉

真实运行态截图已确认：

- 当前页：`D:\XM\kaipai-team\output\playwright\00-104\roles-detail-drawer-before.png`

当前差异：

1. 抽屉宽度为 `760px`，本轮临时试验证明单纯加宽不是主要收益点
2. header 仍约 `77px`
3. hero 仍约 `85px`
4. detail grid 仍约 `516px`
5. `detail-block` 仍约 `92px`
6. permission grid 仍约 `2166px`
7. 权限 tag 直接展示“中文 + 权限码”，导致三组 tag list 分别约 `106 / 448 / 1132px`

### 当前量化

- drawer：`760 × 1100`
- header：`758 × 77`
- body：`758 × 1021`
- close button：`34 × 34`
- hero：`706 × 85`
- detail grid：`706 × 516`
- `detail-block`：`346 × 92`
- permission grid：`706 × 2166`
- detail cards：`255 / 597 / 1281`
- tag lists：`106 / 448 / 1132`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-104`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue` 的 `角色详情` 抽屉：
  - drawer header / body / close button
  - drawer hero
  - detail grid / detail block
  - permission card / tag list
  - 权限 tag 的抽屉内紧凑展示
- 用真实浏览器复核 `http://127.0.0.1:5100/system/roles`

### 2.2 本轮不处理

- 不改顶部 shell card
- 不改 FilterPanel
- 不改三张主卡和表格
- 不改创建 / 编辑 / 复制 / 启停用弹窗
- 不改角色模型、权限模型与真实接口

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `RolesView.vue` 的 `角色详情` 抽屉，不扩到维护弹窗和其它页面。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只承接后台角色、AI 授权收口和招募治理授权，不扩展新的角色体系。

### 3.2 抽屉密度合同

- **R4** drawer header、close button 与 body padding 必须明显收紧。
- **R5** hero 高度必须下降，但仍保留角色名、编码、创建人和状态。
- **R6** detail grid 与 `detail-block` 必须收紧，不再维持当前约 `92px` 的字段块高度。
- **R7** permission card 与 tag list 必须明显收紧。
- **R8** 权限 tag 可在详情抽屉内使用“中文标签”紧凑展示，但必须保留完整权限语义的可追溯性。

### 3.3 治理要求

- **R9** 本轮必须保持详情字段语义、权限数组与接口调用不变。
- **R10** 本轮必须通过独立 `00-104` 承接，不继续混入 `00-103`。
- **R11** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R12** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-104` Spec，并明确它只处理 `system/roles` 角色详情抽屉密度
- [ ] 已完成 drawer shell、hero、detail block、permission card 与 tag list 的局部收口
- [ ] 已通过真实浏览器复核 `system/roles`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
