# 00-77 当前阶段后台仪表盘次级区块对齐（Current Phase Admin Dashboard Secondary Block Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-74 current-phase-admin-reference-ui-architecture-rebuild，00-76 current-phase-admin-dashboard-first-screen-density-alignment
> 记录目的：在 `00-76` 已完成 dashboard 首屏 `4 KPI + 漏斗/趋势` 收口后，继续把 dashboard 剩余差异收窄到次级三块本身：`留存 / 风格偏好 / 渠道分布`。

## 1. 背景

截至 `2026-04-22`：

- `00-74` 已完成后台 reference 8 页 IA 回接
- `00-75` 已完成共享顶控单行对齐
- `00-76` 已完成 dashboard 首屏 `4 KPI + 漏斗/趋势` 首轮密度收口

但对照 reference 与当前最新 full-page 运行态后，又确认出 dashboard 次级三块的剩余偏差：

1. `留存承接`
   - 当前标题被压成多行
   - 当前采用纵向 stacked 代理卡，信息密度与 reference 差距较大
2. `风格偏好`
   - 当前 donut 与 legend 关系仍偏“下堆叠”，不够接近 reference 的横向组织
3. `渠道分布`
   - 当前仍是 bar board，不是更接近 reference 的 donut + legend 组织
   - 但数据仍只能继续用 scene 分布近似承接

同时已核实：

- 这类问题仍然只属于 `OverviewView.vue`
- 不需要回到共享顶控或全局 `page-overview`
- 也不涉及新的事实源扩张

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-77`
- 只处理 dashboard 次级三块：
  - 留存承接
  - 风格偏好
  - 渠道分布
- 让上述三块在保持真实事实边界不变的前提下，更接近 reference 的结构表达
- 用真实浏览器重新验证 `dashboard/index` 最新 full-page 运行态

### 2.2 本轮不处理

- 不再改 dashboard 顶部 4 KPI
- 不再改 漏斗 / 趋势首屏双卡
- 不改 `AdminTopbar.vue`
- 不改全局 `page-overview` 或共享 `table-card`
- 不补伪造 `TOP CONTENT`
- 不扩展真实留存或真实渠道归因事实源

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue` 中的 `dashboard-grid--secondary` 区域。
- **R2** 本轮判断必须优先服从真实对比证据：
  - `D:\XM\kaipai-team\output\playwright\00-74-reference\reference-dashboard.png`
  - `D:\XM\kaipai-team\output\playwright\00-76\dashboard-index-full.png`
- **R3** 本轮不得引入任何超出当前 `overview` 聚合字段的新事实源或伪数据。

### 3.2 留存区合同

- **R4** `留存承接` 当前不得继续使用过重的纵向 stacked card 表达；应改成更接近 reference 的轻量代理结构。
- **R5** 留存区不得伪造次日、7日或 cohort 曲线，但允许使用现有真实代理指标做：
  - 轻量底部指标条
  - 轻量摘要带
  - 轻量说明区
- **R6** 留存区标题与 hint 的空间分配需要收紧，避免标题继续被压成多行。

### 3.3 风格偏好 / 渠道分布合同

- **R7** `风格偏好` 应继续使用现有 scene 聚合字段，但布局应更接近 reference 的：
  - donut 主体
  - 右侧或侧向 legend
- **R8** `渠道分布` 在继续只认 scene 近似承接的前提下，应从当前 bar board 收口到更接近 reference 的 donut + legend 表达。
- **R9** 渠道区必须继续显式说明它仍是近似承接，不得被误读成真实微信渠道归因系统。

### 3.4 治理要求

- **R10** 本轮必须通过独立 `00-77` 承接，不继续把次级三块精修混入 `00-76`。
- **R11** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R12** 本轮必须把修复前后的 dashboard full-page 证据写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-77` Spec，并明确它只处理 dashboard 次级三块
- [ ] 已确认当前问题不需要外溢到全局样式
- [ ] 已完成 `留存承接 / 风格偏好 / 渠道分布` 的局部对齐
- [ ] 已通过真实浏览器复核 `dashboard/index` full-page
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
