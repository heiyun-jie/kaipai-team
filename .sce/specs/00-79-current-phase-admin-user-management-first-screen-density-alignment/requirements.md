# 00-79 当前阶段后台用户管理首屏密度对齐（Current Phase Admin User Management First-Screen Density Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-74 current-phase-admin-reference-ui-architecture-rebuild，00-75 current-phase-admin-reference-shell-density-alignment
> 记录目的：在 dashboard 连续收口后，把下一条 page-level 精修主线切到 `users/index`，只处理用户管理首屏的密度问题，不扩到表格深层或其他页面。

## 1. 背景

截至 `2026-04-22`：

- `00-74` 已完成后台 8 页 IA 回接
- `00-75 ~ 00-78` 已完成 dashboard 的整页首轮收口

当前切到 `users/index` 后，已通过真实浏览器重新核实到以下问题：

1. 顶部 4 张 KPI 卡实际仍是 `3 + 1` 断行
2. segment + 快速筛选区仍偏厚，首屏纵向密度偏松
3. 高级筛选区仍然占高较大，与 reference 的更紧凑首屏有差距

同时已确认：

- 当前问题仍然只属于 `UserCenterView.vue`
- 不需要回到共享顶控
- 也不应直接把全局 `page-overview` 或 `FilterPanel` 做无证据重构

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-79`
- 只处理 `users/index` 首屏：
  - KPI 概览卡
  - segment + 快筛区
  - 筛选区密度
- 用真实浏览器重新验证 `http://127.0.0.1:5100/users/index`

### 2.2 本轮不处理

- 不改 `AdminTopbar.vue`
- 不改用户表格深层列结构
- 不改详情抽屉结构
- 不改其他正式页
- 不改全局 `page-overview`
- 不改全局 `FilterPanel`

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `D:\XM\kaipai-team\kaipai-admin\src\views\user\UserCenterView.vue` 的首屏区域。
- **R2** 本轮判断必须优先服从真实运行态；当前核心证据包括：
  - `D:\XM\kaipai-team\output\playwright\00-79\users-index-before.png`
- **R3** 已通过真实浏览器 computed style 核实：`.user-overview` 当前仍被共享样式压成 3 列，因此本轮需要做局部覆盖，但不得外溢到其他页面。

### 3.2 KPI 区合同

- **R4** 用户管理顶部 4 张 KPI 卡在桌面宽度下必须恢复单行 4 卡表达，不再出现 `3 + 1`。
- **R5** KPI 卡继续只认当前真实用户管理页已有指标，不新增伪统计。
- **R6** KPI 卡的高度、padding、说明文案允许只在用户管理页局部收紧。

### 3.3 segment / 快筛 / 筛选区合同

- **R7** segment 区与快速筛选区必须比当前更紧凑，减少首屏无效留白。
- **R8** 高级筛选区必须保持真实筛选能力不变，但允许通过：
  - header 压缩
  - body gap 收紧
  - 表单控件密度局部覆盖
  让首屏更接近 reference 的信息密度。
- **R9** 本轮不要求新增“新建用户”或其他 reference 动作，因为当前未核实对应真实业务入口。

### 3.4 治理要求

- **R10** 本轮必须通过独立 `00-79` 承接，不继续把用户管理首屏精修混入 dashboard 系列 spec。
- **R11** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R12** 本轮必须把修复前后的 `users/index` 浏览器证据写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-79` Spec，并明确它只处理用户管理首屏
- [ ] 已确认当前问题不需要外溢成全局 `page-overview / FilterPanel` 重构
- [ ] 已完成 KPI 单行 4 卡、segment/快筛收紧、筛选区密度收口
- [ ] 已通过真实浏览器复核 `users/index`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
