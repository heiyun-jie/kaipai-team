# 00-82 当前阶段后台模板库列表视图密度对齐（Current Phase Admin Template Library List Density Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-81 current-phase-admin-template-library-first-screen-alignment
> 记录目的：在 `00-81` 已完成模板库默认首屏收口后，继续把同一页面的列表视图表格区收窄成独立后续线，只处理表格行高、列宽与操作区密度。

## 1. 背景

截至 `2026-04-22`：

- `00-81` 已完成 `content/templates` 默认模板库首屏收口

但切换到 `列表视图` 后，又核实出一组更窄的问题：

1. 表格行高仍偏厚
2. 模板编码列在当前宽度下断行，观感偏弱
3. 右侧操作区宽度偏大、按钮间距偏松

同时已通过真实浏览器量化确认：

- 当前列表首行高度约为 `77px`
- 当前操作区宽度约为 `236px`

这说明当前差异已经从模板库首屏，收窄到列表视图的表格区本身。

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-82`
- 只处理 `content/templates` 在 `table` 视图下的表格区：
  - table header
  - row density
  - 编码/名称等 cell 观感
  - 固定操作列与按钮间距
  - 分页区密度
- 用真实浏览器重新验证 `content/templates` 列表视图

### 2.2 本轮不处理

- 不再改默认 gallery 首屏
- 不改筛选字段语义
- 不改编辑 / 发布 / 回滚弹窗
- 不改其他正式页

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `D:\XM\kaipai-team\kaipai-admin\src\views\content\TemplatesView.vue` 在 `viewMode === 'table'` 时的表格区。
- **R2** 本轮判断必须优先服从真实运行态；当前核心证据包括：
  - `D:\XM\kaipai-team\output\playwright\00-81\templates-list-before.png`
- **R3** 本轮不改变真实模板动作语义，只处理视觉密度与布局。

### 3.2 表格区合同

- **R4** 表格 header、row padding 与 cell 层级需明显收紧，使列表视图更接近 reference 风格下的高密度治理表。
- **R5** 模板编码、模板名称、场景、层级等信息需在更紧密布局下保持可读，不得因收紧造成过度截断。
- **R6** 如模板编码在当前列宽下断行影响观感，本轮允许通过局部列宽与 cell 表达优化解决，但不改变字段语义。

### 3.3 操作区合同

- **R7** 固定右侧操作列宽度应收紧，避免当前操作区过宽。
- **R8** 操作按钮间距与字号允许收紧，但：
  - 仍需保留“基础编辑 / 发布 / 回滚”的真实动作表达
  - 不得压缩到不可点或不可读

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-82` 承接，不继续把列表视图表格区精修混入 `00-81`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-82` Spec，并明确它只处理模板库列表视图表格区
- [ ] 已完成表格行高、编码列观感与操作区密度收口
- [ ] 已通过真实浏览器复核 `content/templates` 列表视图
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
