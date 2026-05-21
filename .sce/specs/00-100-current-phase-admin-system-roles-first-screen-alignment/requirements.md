# 00-100 当前阶段后台角色治理首屏对齐（Current Phase Admin System Roles First Screen Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-99 current-phase-admin-system-account-governance-status-confirm-dialog-alignment
> 记录目的：在 `system/admin-users` 完成连续收口后，切到 `system/roles`，先把角色治理页的首屏结构、筛选区和首张 AI 授权矩阵壳层收口到当前 refined admin shell。

## 1. 背景

截至 `2026-04-22`：

- `system/admin-users` 已完成 `00-95` 到 `00-99` 的首屏、主表、详情抽屉、维护弹窗和状态确认弹窗收口
- 当前按单一主线自然切到 `system/roles`
- `system/roles` 没有 direct reference 子页；本轮目标不是伪造 reference 新页面，而是把隐藏治理工具页继续收口到当前系统域 refined shell

真实运行态截图已确认：

- 当前页：`D:\XM\kaipai-team\output\playwright\00-100\roles-before.png`

当前差异：

1. 顶部 `console-overview` 3 卡仍是厚 overview 态，约 `1134 × 161`
2. FilterPanel 仍约 `1134 × 176`
3. 首张 `AI 授权收口矩阵` 卡顶部约 `y=581`
4. AI 矩阵 summary blocks 仍约 `105px`
5. 第一张矩阵表首行约在 `y=946`，首屏有效表格信息进入偏晚

### 当前量化

- overview：`1134 × 161`
- FilterPanel：`1134 × 176`
- AI matrix card：`1134 × 489`
- AI matrix summary：`1084 × 105`
- AI matrix alert：`1084 × 63`
- AI matrix table：`1084 × 151`
- 首个矩阵行顶部：约 `y=946`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-100`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue` 的首屏：
  - 顶部 overview / summary 区
  - FilterPanel 壳层
  - 首张 AI 授权收口矩阵卡的 header / summary / alert / table 进入关系
- 用真实浏览器复核 `http://127.0.0.1:5100/system/roles`

### 2.2 本轮不处理

- 不改第二张 `招募治理授权矩阵`
- 不改底部 `角色清单`
- 不改详情抽屉
- 不改创建 / 编辑 / 复制 / 启停用弹窗
- 不改权限模型与真实接口

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `RolesView.vue` 首屏结构和首张 AI 矩阵壳层，不扩到其它区块。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只承接后台角色、AI 授权收口和招募治理授权，不扩展新的角色体系。

### 3.2 首屏结构合同

- **R4** 顶部 overview 3 卡必须退场或明显压缩，不再维持厚仪表盘感。
- **R5** FilterPanel 必须局部收紧，不再以共享默认节奏压低首张矩阵卡。
- **R6** 首张 AI 授权矩阵卡必须更早呈现表格主体，summary / alert 不得继续占用过高首屏。
- **R7** 本轮可以压缩首张 AI 矩阵壳层，但不得改变 AI 授权矩阵字段语义。

### 3.3 治理要求

- **R8** 本轮必须保持角色列表、AI 矩阵、招募矩阵接口调用与数据语义不变。
- **R9** 本轮必须通过独立 `00-100` 承接，不继续混入 `00-99`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-100` Spec，并明确它只处理 `system/roles` 首屏与首张 AI 矩阵壳层
- [ ] 已完成 overview、FilterPanel、AI matrix card header / summary / alert 的局部收口
- [ ] 已通过真实浏览器复核 `system/roles`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
