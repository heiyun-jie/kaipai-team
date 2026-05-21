# 00-93 当前阶段后台用户分群板对齐（Current Phase Admin Analytics Segment Board Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-92 current-phase-admin-analytics-funnel-board-alignment
> 记录目的：在 `00-92` 完成 `dashboard/analytics` 转化漏斗板收口后，继续把 `用户分群` tab 收口为更接近 reference 的全宽 3×2 分群卡阵列。

## 1. 背景

截至 `2026-04-22`：

- `DashboardAnalyticsView.vue` 的 `channel / retention / funnel` 三个 tab 已完成独立精修
- `segment` tab 仍停留在 `左 6 卡 + 右侧大说明盒` 的承接态

真实截图对比已确认：

- reference：`D:\XM\kaipai-team\output\playwright\00-93\analytics-segment-reference.png`
- 当前运行态：`D:\XM\kaipai-team\output\playwright\00-93\analytics-segment-current.png`

当前差异：

1. reference 是全宽 3×2 分群卡阵列
2. 当前运行态是左侧小卡阵列 + 右侧说明盒
3. 当前 `segment-grid` 宽度只有约 `509px`，卡片仍偏小
4. 当前右侧 `analytics-insight--spacious` 仍占一整张说明卡

同时当前已明确：

- 当前后端没有独立 cohort / profile segmentation / 标签系统
- 当前页只能用 `/admin/dashboard/overview` 的真实主链聚合字段做“运营近似分群”
- 不能伪造 reference 中的机构归属、用户标签、运营等级和原型计数

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-93`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardAnalyticsView.vue` 的 `segment` tab：
  - segment tab 首屏结构
  - 近似分群卡阵列表达
  - 边界说明收口
- 用真实浏览器复核 `http://127.0.0.1:5100/dashboard/analytics`

### 2.2 本轮不处理

- 不扩到 `channel / retention / funnel` 三个 tab
- 不新增真实用户画像接口
- 不伪造 reference 的用户标签 / 机构归属 / 活跃层级
- 不扩到 `AdminTopbar.vue`

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `DashboardAnalyticsView.vue` 的 `segment` tab，不覆盖另外三个 tab。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只认 `/admin/dashboard/overview` 的真实聚合字段做近似分群，不伪造用户画像事实。

### 3.2 首屏结构合同

- **R4** `segment` tab 必须从“左卡阵列 + 右说明盒”收口为更接近 reference 的全宽单板。
- **R5** 分群卡必须形成完整 3×2 阵列，不再被压缩在左半区。
- **R6** 边界说明必须收进分群板内部，不再占据独立右侧大卡。

### 3.3 分群表达合同

- **R7** 分群卡只能使用当前真实字段：活跃供给、触达访客、成卡意向、联系完成、待跟进、支付治理。
- **R8** 分群板必须显式说明它是“当前主链近似分群”，不是正式用户画像系统。

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-93` 承接，不继续混入 `00-92` 或 `00-91`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-93` Spec，并明确它只处理 `dashboard/analytics` 的 `segment` tab
- [ ] 已完成 segment tab 从双栏说明态到全宽分群板的收口
- [ ] 已通过真实浏览器复核 `dashboard/analytics`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
