# 00-95 当前阶段后台账号治理首屏对齐（Current Phase Admin System Account Governance First Screen Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-94 current-phase-admin-system-settings-grouped-row-detail-alignment
> 记录目的：在 `system/settings` grouped rows 收口后，继续把 `system/admin-users` 的首屏结构收口为更接近当前 refined admin shell 的后台账号治理页。

## 1. 背景

截至 `2026-04-22`：

- `AdminUsersView.vue` 仍保留早期 hidden-tooling 承接态
- 当前页没有 direct reference 独立截图；因此本轮目标不是伪造一个 reference 子页，而是把它收口到当前 refined shell 与系统域页面语言

真实运行态截图已确认：

- 当前页：`D:\XM\kaipai-team\output\playwright\00-95\admin-users-current.png`

当前差异：

1. overview 3 卡偏厚
2. FilterPanel 高度偏大，首屏表格被明显压低
3. 表格首屏进入点偏晚
4. 当前页看起来仍像“旧治理工具页”，和已收口的系统域页面节奏不一致

### 当前量化

- overview：`1134 × 161`
- FilterPanel：`1134 × 244`
- table card：`1134 × 432`
- 首个表格行：约 `95px`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-95`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\system\AdminUsersView.vue` 的首屏：
  - overview / summary 区
  - FilterPanel 壳层
  - table header 首屏位置
- 用真实浏览器复核 `http://127.0.0.1:5100/system/admin-users`

### 2.2 本轮不处理

- 不改表格密度
- 不改详情抽屉
- 不改创建 / 编辑 / 绑定 / 重置密码 / 启停用弹窗
- 不改真实接口

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `AdminUsersView.vue` 首屏结构，不扩到表格密度和弹窗。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 本页继续只承接后台账号、角色绑定、密码处置与启停用，不扩展组织管理模型。

### 3.2 首屏结构合同

- **R4** overview 3 卡必须退场或明显压缩，不再压低表格首屏。
- **R5** FilterPanel 必须明显收紧，不再占据过高首屏。
- **R6** 表格区必须更早进入首屏，形成“工具页 + 清单”关系。

### 3.3 文案与壳层合同

- **R7** 首屏说明文案必须继续收口为更轻量的工具边界说明。
- **R8** 当前页的首屏壳层需更接近系统域当前 refined 风格，不再保留厚 overview 仪表盘感。

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-95` 承接，不继续混入 `00-94`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-95` Spec，并明确它只处理 `system/admin-users` 首屏结构
- [ ] 已完成 summary / FilterPanel / table header 首屏位置的收口
- [ ] 已通过真实浏览器复核 `system/admin-users`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
