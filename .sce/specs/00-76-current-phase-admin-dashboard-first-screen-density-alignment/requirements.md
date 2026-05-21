# 00-76 当前阶段后台仪表盘首屏密度对齐（Current Phase Admin Dashboard First-Screen Density Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-74 current-phase-admin-reference-ui-architecture-rebuild，00-75 current-phase-admin-reference-shell-density-alignment
> 记录目的：在 `00-75` 已完成共享顶控单行对齐后，把当前后台与 reference 剩余差异继续收口到 dashboard 首屏本身，避免把 `OverviewView.vue` 的局部密度问题误做成全局 `page-overview` 样式改造。

## 1. 背景

截至 `2026-04-22`：

- `00-74` 已完成后台 reference 8 页 IA 回接
- `00-75` 已完成桌面顶控与标题单行对齐

但把最新 dashboard 运行态与 reference 继续对比后，又确认出一组更窄的 dashboard 首屏差异：

1. 当前 KPI 区仍是 `3 + 1` 断行，而 reference 是单行 4 卡
2. 当前漏斗 / 趋势区的首屏横向分配与 reference 仍不够接近
3. 当前 dashboard 首屏纵向密度仍偏松，首屏可见信息量低于 reference

同时已核实：

- 这些问题并不是 `AdminTopbar.vue` 造成的
- 也不是正式信息架构再次偏航
- 而是 `OverviewView.vue` 与 dashboard 本地布局的 page-level 密度问题

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-76`，把 dashboard 首屏密度问题从 `00-75` 之后继续收口
- 让 `OverviewView.vue` 的首屏更接近 reference：
  - 4 张 KPI 卡单行排列
  - 漏斗 / 趋势双卡首屏布局更稳定
  - 首屏纵向密度更紧
- 用真实浏览器重新验证 `dashboard/index` 最新首屏运行态

### 2.2 本轮不处理

- 不再改后台正式导航或页面职责
- 不改 `AdminTopbar.vue`
- 不做全局 `page-overview` 共享样式重构
- 不扩展 `TOP CONTENT`、留存、渠道的真实数据边界
- 不同时扩到用户管理、风格模板或其他页面

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue` 的桌面首屏密度，不覆盖其他正式页。
- **R2** 本轮判断必须优先服从真实运行态与 reference 对比，当前核心证据包括：
  - `D:\XM\kaipai-team\output\playwright\00-74-reference\reference-dashboard.png`
  - `D:\XM\kaipai-team\output\playwright\00-75\dashboard-index-topbar.png`
- **R3** 若当前问题来自 dashboard 本地布局，则不得把修复外溢成全局 `page-overview` 样式改动。

### 3.2 首屏 KPI 合同

- **R4** dashboard 顶部 4 张 KPI 卡在桌面宽度下必须恢复成单行 4 卡表达，不再出现 `3 + 1` 断行。
- **R5** 当前 KPI 卡仍必须继续使用真实 overview 聚合字段，不得为了贴 reference 补伪指标。
- **R6** KPI 卡的高度、padding、字号和说明文案允许为 dashboard 单独收紧，但不得影响其他页面的共享概览卡。

### 3.3 漏斗 / 趋势首屏合同

- **R7** `转化漏斗` 与 `主链热度曲线` 的双卡布局需要更接近 reference 的首屏横向关系，避免趋势卡标题继续被横向空间压缩。
- **R8** 首屏双卡的纵向密度需要收紧，使 dashboard 首屏可见信息量更接近 reference。
- **R9** 当前提示文案与事实边界说明可以保留，但应通过更紧的布局表达，不能继续主导首屏空间。

### 3.4 治理要求

- **R10** 本轮必须通过独立 `00-76` 承接 dashboard 首屏 page-level 精修，不继续把它混入 `00-75` 的共享顶控主线。
- **R11** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R12** 本轮必须把修复前后的 dashboard 首屏截图回填到 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-76` Spec，并明确它只处理 dashboard 首屏密度
- [ ] 已确认当前问题不是共享顶控，也不是全局 `page-overview` 必然缺陷
- [ ] 已完成 `OverviewView.vue` 的首屏 4 卡单行与双卡布局收紧
- [ ] 已通过真实浏览器复核 `dashboard/index`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
