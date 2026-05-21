# 00-87 当前阶段后台运营动作治理动态台账对齐（Current Phase Admin Operate Actions Governance Ledger Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-86 current-phase-admin-operate-actions-first-screen-alignment
> 记录目的：在 `00-86` 完成 `operate/actions` 首屏收口后，继续把下方 `最近治理动态` 从厚卡片列表收口为更接近 reference 的轻量 ledger / table 表达。

## 1. 背景

截至 `2026-04-22`：

- `00-86` 已完成 `operate/actions` 首屏收口
- 当前 `operate/actions` 与 reference 的主要残差已收窄到下方治理动态区

真实截图对比已确认：

- reference：`D:\XM\kaipai-team\output\playwright\00-86\operate-actions-reference.png`
- 当前运行态：`D:\XM\kaipai-team\output\playwright\00-87\operate-actions-governance-before.png`

当前差异：

1. reference 下半区是更轻的 ledger / table 表达
2. 当前运行态仍是 `table-card + table-header + table-empty` 的空态大卡片
3. 当前空态高度约 `158px`，整卡高度约 `279px`，信息密度偏低

同时当前已明确：

- 当前页不能伪造 reference 中的 `RECENT CAMPAIGNS`
- 当前页只能继续复用真实 `recentItems`
- 当 `recentItems` 为空时，只能输出真实空态，不得造行

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-87`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\operate\ActionsView.vue` 下方治理动态区：
  - `table-card`
  - `table-header`
  - `campaign-list`
  - `campaign-item`
  - `table-empty`
- 用真实浏览器复核 `http://127.0.0.1:5100/operate/actions`

### 2.2 本轮不处理

- 不改首屏工具卡
- 不改动作推荐区
- 不改 overview 辅助摘要区
- 不改真实接口、字段与 route query
- 不扩到其他页面

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `ActionsView.vue` 下方治理动态区，不覆盖上方首屏结构。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 本轮不能伪造 reference 中的 campaign 数据，只能用真实 `recentItems` 或真实空态。

### 3.2 动态区结构合同

- **R4** 治理动态区需要从当前厚卡片列表/空态，收口为更接近 ledger 的轻量列表结构。
- **R5** 标题区与提示区应更紧，不再占用过多垂直空间。
- **R6** 即使 `recentItems` 为空，也应保留清晰的台账结构感，而不是继续使用厚空态卡。

### 3.3 台账表达合同

- **R7** 当 `recentItems` 存在时，行内需清晰表达：动态标题、业务线、状态、发生时间、处理入口。
- **R8** 当 `recentItems` 为空时，空态仍需保持可读、轻量，并明确说明“当前时间窗口没有 recentItems”。

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-87` 承接，不继续混入 `00-86`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-87` Spec，并明确它只处理 `operate/actions` 治理动态区
- [ ] 已完成治理动态区的 ledger/table 化轻量表达
- [ ] 已通过真实浏览器复核 `operate/actions`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
