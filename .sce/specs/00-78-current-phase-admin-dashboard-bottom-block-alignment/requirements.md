# 00-78 当前阶段后台仪表盘底部区块对齐（Current Phase Admin Dashboard Bottom Block Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-74 current-phase-admin-reference-ui-architecture-rebuild，00-77 current-phase-admin-dashboard-secondary-block-alignment
> 记录目的：在 `00-77` 已完成 dashboard 中上区块收口后，继续把 dashboard 剩余差异收窄到底部两块：`正式页面矩阵` 与 `治理动态`。

## 1. 背景

截至 `2026-04-22`：

- `00-74` 已完成后台 reference 8 页 IA 回接
- `00-75` 已完成共享顶控收口
- `00-76` 已完成 dashboard 首屏 `4 KPI + 漏斗/趋势` 收口
- `00-77` 已完成 dashboard 次级三块 `留存 / 风格偏好 / 渠道分布` 收口

当前 dashboard 剩余主要差异落在底部两块：

1. 左侧 `正式页面矩阵`
   - 当前是 8 张较厚的卡片矩阵
   - 与 reference 左侧 `TOP CONTENT` 的高密度表格关系差距较大
2. 右侧 `治理动态`
   - 当前保留概览卡 + 空态，但与 reference `ACTIVITY FEED` 的密度和层次仍有差异

同时已明确：

- 当前不能伪造 reference 的 `TOP CONTENT`
- 因为此前已核实：
  - 当前缺少稳定排序字段
  - 也缺少真实分享总次数 / 进入率等榜单事实

因此，本轮只能做：

- 正式页面矩阵的表格化压缩表达
- 治理动态向 reference 的 activity-feed 壳层靠近

而不能硬做内容榜。

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-78`
- 只处理 dashboard 底部两块：
  - `正式页面矩阵`
  - `治理动态`
- 让左侧块更接近 reference 的紧凑列表 / 表格感
- 让右侧块更接近 reference 的 activity feed 感
- 用真实浏览器重新验证 `dashboard/index` full-page

### 2.2 本轮不处理

- 不再改 dashboard 顶部 KPI
- 不再改 `漏斗 / 趋势`
- 不再改 `留存 / 风格偏好 / 渠道分布`
- 不补伪造 `TOP CONTENT`
- 不扩展真实排序事实源或内容热度字段
- 不扩到其他正式页

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue` 中的 `dashboard-grid--bottom` 区域。
- **R2** 本轮判断必须优先服从真实对比证据：
  - `D:\XM\kaipai-team\output\playwright\00-74-reference\reference-dashboard.png`
  - `D:\XM\kaipai-team\output\playwright\00-77\dashboard-index-secondary-full.png`
- **R3** 本轮不得把 `正式页面矩阵` 伪装成真实 `TOP CONTENT` 内容榜。

### 3.2 页面矩阵合同

- **R4** 页面矩阵应继续保留为“正式 8 页入口”的真实承接，不得回退到 shrink-phase 或伪造内容榜。
- **R5** 页面矩阵的视觉结构应从当前厚卡片矩阵收成更紧凑的 ledger / list / table-like 表达，使其更接近 reference 左侧块的高密度承载方式。
- **R6** 页面矩阵内继续允许显示：
  - 区域
  - 页面名
  - 指标
  - 事实说明
  - 进入动作
  但必须减少过厚卡片感与过多留白。

### 3.3 治理动态合同

- **R7** 治理动态应继续只认当前 `overview` 里的待办聚合与 `recentItems`，不得新造治理流。
- **R8** 治理动态应更接近 reference 的 activity feed 层次：
  - 上方轻量摘要
  - 下方列表或空态
- **R9** 当 `recentItems` 为空时，空态仍必须保留，但表达应更轻，不得继续占过大空间。

### 3.4 治理要求

- **R10** 本轮必须通过独立 `00-78` 承接，不继续把底部两块精修混入 `00-77`。
- **R11** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R12** 本轮必须把修复前后的 dashboard full-page 证据写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-78` Spec，并明确它只处理 dashboard 底部两块
- [ ] 已确认当前不能伪造 `TOP CONTENT` 内容榜
- [ ] 已完成页面矩阵的表格化压缩与治理动态轻量化
- [ ] 已通过真实浏览器复核 `dashboard/index` full-page
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
