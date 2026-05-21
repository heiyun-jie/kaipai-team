# 00-90 当前阶段后台数据分析首屏对齐（Current Phase Admin Analytics Channel First Screen Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-74 current-phase-admin-reference-ui-architecture-rebuild
> 记录目的：在 `00-89` 完成机构目录首屏收口后，继续把 `dashboard/analytics` 默认 `渠道分析` 首屏收口为更接近 reference 的双栏数据分析页。

## 1. 背景

截至 `2026-04-22`：

- `DashboardAnalyticsView.vue` 已完成正式页回接
- 但仍停留在 `00-74` 首轮承接态，还没进入独立 page-level 精修线

真实截图对比已确认：

- reference：`D:\XM\kaipai-team\output\playwright\00-90\analytics-reference.png`
- 当前运行态：`D:\XM\kaipai-team\output\playwright\00-90\analytics-current-authenticated.png`

当前差异：

1. 默认 `渠道分析` 首屏虽然已有 tabs + 左表 + 右 donut，但整体结构仍偏“说明页”
2. 左侧 `el-table` 在当前双栏布局下被拉成高卡，底部出现明显空白
3. 右侧 donut 卡说明块偏重，和 reference 的紧凑统计卡关系仍有差异
4. 当前渠道明细仍是通用表格，而 reference 更接近轻量 ledger + progress 表达

同时当前已明确：

- 当前后端没有微信好友 / 朋友圈 / 企业微信等真实渠道字段
- 当前页只能使用 `/admin/dashboard/overview` 里的真实 scene 聚合字段近似承接 reference 渠道块
- 不能伪造 reference 中的渠道口径和高体量数值

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-90`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardAnalyticsView.vue` 默认 `channel` tab 首屏：
  - tabs strip
  - 左侧 channel breakdown 卡
  - 右侧 channel mix / donut 卡
  - 首屏双栏高度关系
- 用真实浏览器复核 `http://127.0.0.1:5100/dashboard/analytics`

### 2.2 本轮不处理

- 不扩到 `retention / funnel / segment` 三个 tab
- 不新增真实渠道接口
- 不伪造 reference 中的微信好友 / 朋友圈 / 企业微信真实渠道字段
- 不扩到 `AdminTopbar.vue` 的共享壳层重构，除非出现当前页局部无法落地的阻塞

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `DashboardAnalyticsView.vue` 默认 `channel` tab 首屏，不覆盖另外三个 tab。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只认 `/admin/dashboard/overview` 的真实 scene 聚合字段，不伪造 reference 渠道口径。

### 3.2 首屏结构合同

- **R4** tabs strip 需继续收紧为更接近 reference 的轻量切换条，不保留厚重壳层。
- **R5** 左右双栏必须恢复更接近 reference 的首屏关系，不再出现左卡被右卡高度拉伸后的大块空白。
- **R6** 右侧 donut / legend / insight 必须收紧成一组紧凑统计卡，不再占据过高首屏。

### 3.3 渠道区表达合同

- **R7** 左侧渠道区需从当前厚 `el-table` 收口为更接近 reference 的轻量 ledger / board 表达。
- **R8** 渠道表达只能使用当前真实事实：scene 标签、分享访问、查看后成卡、占比与 fact-boundary note。

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-90` 承接，不继续混入 `00-74` 或 `00-89`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-90` Spec，并明确它只处理 `dashboard/analytics` 默认 `channel` 首屏
- [ ] 已完成 tabs strip、左侧渠道区和右侧 donut 区的首屏收口
- [ ] 已通过真实浏览器复核 `dashboard/analytics`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
