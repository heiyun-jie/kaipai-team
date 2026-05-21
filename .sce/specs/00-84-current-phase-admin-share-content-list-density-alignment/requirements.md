# 00-84 当前阶段后台分享内容列表视图密度对齐（Current Phase Admin Share Content List Density Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-83 current-phase-admin-share-content-first-screen-alignment
> 记录目的：在 `00-83` 已完成 `content/share-cards` 默认卡片墙首屏收口后，继续把同页的列表视图表格区收窄成独立后续线，只处理表格行高、stacked cell 与固定操作列密度。

## 1. 背景

截至 `2026-04-22`：

- `00-83` 已完成 `content/share-cards` 默认卡片墙首屏收口

但切换到 `列表视图` 后，仍可合理预期存在一组更窄的表格区差异：

1. 表格行高偏厚
2. `卡片信息 / 持卡人 / 实例绑定 / 互动统计` 的 stacked cell 层级仍可能偏松
3. 固定右侧操作列仍可能偏宽

同时当前已明确：

- 这类问题属于同一页面的列表视图表格区
- 不需要回到 gallery 首屏
- 也不需要提前动详情抽屉或底部治理补充动作

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-84`
- 只处理 `content/share-cards` 在 `viewMode === 'table'` 时的表格区：
  - table header
  - row density
  - stacked cell 层级
  - 固定操作列
  - 分页区密度
- 用真实浏览器重新验证 `content/share-cards` 列表视图

### 2.2 本轮不处理

- 不再改默认 gallery 首屏
- 不改详情抽屉
- 不改底部 `治理补充动作`
- 不改真实分享卡详情与 legacy 修复能力
- 不扩到其他页面

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `D:\XM\kaipai-team\kaipai-admin\src\views\content\ShareCardsView.vue` 在 `viewMode === 'table'` 时的表格区。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 本轮不改变分享内容字段语义、详情抽屉链路和底部治理动作，只处理视觉密度与布局。

### 3.2 表格区合同

- **R4** 表格 header、row padding 与 cell 层级需明显收紧，使列表视图更接近 reference 风格下的高密度治理表。
- **R5** `卡片信息 / 持卡人 / 实例绑定 / 互动统计` 四类 stacked cell 需要局部样式收口，避免默认文本堆叠松散。
- **R6** 分享卡 ID、默认卡、问题数、更新时间等信息在收紧后仍需保持可读。

### 3.3 固定操作列合同

- **R7** 固定右侧操作列宽度应适度收紧，避免当前操作区过宽。
- **R8** `查看详情` 仍必须保持可点击、可读，不得因压缩影响可用性。

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-84` 承接，不继续把列表视图精修混入 `00-83`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-84` Spec，并明确它只处理分享内容列表视图表格区
- [ ] 已完成表格行高、stacked cell 与固定操作列收口
- [ ] 已通过真实浏览器复核 `content/share-cards` 列表视图
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
