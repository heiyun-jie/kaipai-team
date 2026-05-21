# 00-81 当前阶段后台模板库首屏对齐（Current Phase Admin Template Library First-Screen Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-74 current-phase-admin-reference-ui-architecture-rebuild
> 记录目的：在 dashboard 与用户管理连续收口后，把下一条 page-level 精修主线切到 `content/templates`，只处理默认模板库首屏的 tabs / 汇总卡 / 筛选区 / 模板卡片。

## 1. 背景

截至 `2026-04-22`：

- `00-74` 已完成后台 8 页正式 IA 回接
- `content/templates` 已作为正式“风格模板”页面进入运行态

当前继续核对模板库运行态后，已确认首屏还存在一组更窄的差异：

1. tabs + 视图切换区仍偏厚
2. 汇总卡与筛选区占高偏大
3. 模板卡片封面与卡体高度偏高
4. 当前只有 1 张真实模板时，首屏空白感较强

同时已确认：

- 当前主表达就是默认模板库卡片网格
- 列表视图只是治理排查辅助视图
- 本轮不需要去动弹窗与发布/回滚链路

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-81`
- 只处理 `content/templates` 默认首屏：
  - 顶部 tabs
  - 视图切换
  - 汇总卡
  - 筛选区
  - 模板卡片网格
- 用真实浏览器重新验证 `http://127.0.0.1:5100/content/templates`

### 2.2 本轮不处理

- 不改列表视图的表格列结构
- 不改编辑 / 发布 / 回滚弹窗
- 不改真实模板动作能力
- 不改其他正式页

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `D:\XM\kaipai-team\kaipai-admin\src\views\content\TemplatesView.vue` 在默认 `gallery` 模式下的首屏。
- **R2** 本轮判断必须优先服从真实运行态；当前核心证据包括：
  - `D:\XM\kaipai-team\output\playwright\00-81-templates-current-before.png`
- **R3** 本轮不改变真实模板数据、启停用、发布、回滚与编辑链路。

### 3.2 首屏合同

- **R4** tabs / 视图切换 / 汇总卡 / 筛选区必须比当前更紧凑，降低首屏无效占高。
- **R5** 模板卡片区应更接近 reference 的模板库气质，但仍保持当前真实模板 carrier。
- **R6** 当当前模板样本很少时，不应把单张卡片无约束拉得过宽；首屏需保持更稳定的卡片宽度与网格观感。

### 3.3 治理要求

- **R7** 本轮必须通过独立 `00-81` 承接，不继续把模板库首屏精修混入 `00-80` 或更早 spec。
- **R8** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R9** 本轮必须把修复前后的 `content/templates` 浏览器证据写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-81` Spec，并明确它只处理模板库首屏
- [ ] 已完成 tabs / 汇总卡 / 筛选区 / 卡片区的局部收口
- [ ] 已通过真实浏览器复核 `content/templates`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
