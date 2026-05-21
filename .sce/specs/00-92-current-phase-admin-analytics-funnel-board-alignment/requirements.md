# 00-92 当前阶段后台转化漏斗板对齐（Current Phase Admin Analytics Funnel Board Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-91 current-phase-admin-analytics-retention-matrix-alignment
> 记录目的：在 `00-91` 完成 `dashboard/analytics` 留存矩阵收口后，继续把 `转化漏斗` tab 收口为更接近 reference 的单张全宽 funnel board。

## 1. 背景

截至 `2026-04-22`：

- `DashboardAnalyticsView.vue` 的 `channel` 与 `retention` tab 已完成独立精修
- `funnel` tab 仍停留在 `左漏斗 + 右解读卡` 的承接态

真实截图对比已确认：

- reference：`D:\XM\kaipai-team\output\playwright\00-92\analytics-funnel-reference.png`
- 当前运行态：`D:\XM\kaipai-team\output\playwright\00-92\analytics-funnel-current.png`

当前差异：

1. reference 是单张全宽 `CREATE FUNNEL` 漏斗板
2. 当前运行态是左侧漏斗板 + 右侧解读卡，双栏关系和 reference 差异明显
3. 当前右侧 `analytics-insight--stack` 高度约 `266px`，说明卡偏重
4. 当前左侧 funnel board 宽度约 `621px`，比 reference 的全宽横向进度表达弱

同时当前已明确：

- 当前后端没有 reference 中“首页曝光 / 点击创建 / 上传素材 / 首次分享 / 二次分享”的完整事件序列
- 当前只能使用 `/admin/dashboard/overview` 的真实主链字段构造当前阶段漏斗
- 不能伪造 reference 中的 7 步创建漏斗事件和原型数值

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-92`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardAnalyticsView.vue` 的 `funnel` tab：
  - funnel tab 首屏结构
  - 当前主链漏斗表达
  - 漏斗解读收口
- 用真实浏览器复核 `http://127.0.0.1:5100/dashboard/analytics`

### 2.2 本轮不处理

- 不扩到 `channel / retention / segment` 三个 tab
- 不新增真实漏斗接口
- 不伪造 reference 中的创建流程事件序列
- 不扩到 `AdminTopbar.vue`

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `DashboardAnalyticsView.vue` 的 `funnel` tab，不覆盖另外三个 tab。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 当前页继续只认 `/admin/dashboard/overview` 的真实主链字段，不伪造 reference 创建流程事件。

### 3.2 首屏结构合同

- **R4** `funnel` tab 必须从“左漏斗 + 右解读卡”收口为更接近 reference 的单张全宽 funnel board。
- **R5** 漏斗解读必须内联进 funnel board，不再占据单独右侧大卡。
- **R6** 首屏应直接展示完整漏斗条形关系，横向进度表达需明显增强。

### 3.3 漏斗表达合同

- **R7** 漏斗只能使用当前真实字段：分享访问、唯一访客、查看后成卡、联系方式申请、已同意联系。
- **R8** 漏斗必须显式说明它是“当前主链漏斗”，不是 reference 的完整创建流程漏斗。

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-92` 承接，不继续混入 `00-91` 或 `00-90`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-92` Spec，并明确它只处理 `dashboard/analytics` 的 `funnel` tab
- [ ] 已完成 funnel tab 从双栏说明态到单张全宽漏斗板的收口
- [ ] 已通过真实浏览器复核 `dashboard/analytics`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
