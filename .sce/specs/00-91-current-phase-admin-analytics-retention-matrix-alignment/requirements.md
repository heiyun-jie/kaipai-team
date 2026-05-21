# 00-91 当前阶段后台留存矩阵首屏对齐（Current Phase Admin Analytics Retention Matrix Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-90 current-phase-admin-analytics-channel-first-screen-alignment
> 记录目的：在 `00-90` 完成 `dashboard/analytics` 默认渠道分析首屏收口后，继续把 `留存分析` tab 收口为更接近 reference 的单张 retention matrix 板。

## 1. 背景

截至 `2026-04-22`：

- `DashboardAnalyticsView.vue` 默认 `channel` tab 已进入独立 page-level 精修线
- `retention` tab 仍停留在 `左 6 卡 + 右说明盒` 的承接态

真实截图对比已确认：

- reference：`D:\XM\kaipai-team\output\playwright\00-91\analytics-retention-reference-clicked.png`
- 当前运行态：`D:\XM\kaipai-team\output\playwright\00-91\analytics-retention-current.png`

当前差异：

1. reference 是单张 retention cohort matrix 板
2. 当前运行态是左 6 张代理指标卡 + 右侧大说明盒
3. 当前 `retention-grid` 卡片厚度偏大，首屏块关系与 reference 差异明显
4. 当前右侧 `analytics-insight--spacious` 高度偏大，说明感太重

同时当前已明确：

- 当前后端没有真实 D1 / D7 / cohort 留存接口
- 只能使用 `/admin/dashboard/overview` 里的真实聚合字段做“当前窗口留存代理矩阵”
- 不能伪造 reference 中的周 cohort 行和连续留存百分比

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-91`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardAnalyticsView.vue` 的 `retention` tab：
  - retention tab 首屏结构
  - 代理矩阵表达
  - 边界说明收口
- 用真实浏览器复核 `http://127.0.0.1:5100/dashboard/analytics`

### 2.2 本轮不处理

- 不扩到 `channel / funnel / segment` 三个 tab
- 不新增真实留存接口
- 不伪造 week cohort、D1/D7/D14/D30 留存序列
- 不扩到 `AdminTopbar.vue`

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `DashboardAnalyticsView.vue` 的 `retention` tab，不覆盖另外三个 tab。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只认 `/admin/dashboard/overview` 的真实聚合字段做代理矩阵，不伪造 cohort 留存事实。

### 3.2 首屏结构合同

- **R4** `retention` tab 必须从“左多卡 + 右说明盒”收口为更接近 reference 的单张 retention matrix 板。
- **R5** 边界说明必须明显收紧，不能再占据一整张右侧大卡。
- **R6** 首屏应直接进入 retention matrix 核心区，而不是先进入多块说明卡。

### 3.3 代理矩阵表达合同

- **R7** 代理矩阵只能使用当前真实字段：活跃分享卡、持卡用户、分享访问、唯一访客、查看后成卡、已同意联系，以及必要的治理边界信号。
- **R8** 代理矩阵必须显式说明它是“当前窗口代理矩阵”，不是正式 cohort 留存系统。

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-91` 承接，不继续混入 `00-90` 或 `00-74`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-91` Spec，并明确它只处理 `dashboard/analytics` 的 `retention` tab
- [ ] 已完成 retention tab 从多卡说明态到单张代理矩阵板的收口
- [ ] 已通过真实浏览器复核 `dashboard/analytics`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
