# 00-85 当前阶段后台分享内容详情抽屉密度对齐（Current Phase Admin Share Content Detail Drawer Density Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-84 current-phase-admin-share-content-list-density-alignment
> 记录目的：在 `00-84` 完成 `content/share-cards` 列表视图表格区收口后，继续把同页详情抽屉的首屏信息密度、字段块层级和抽屉壳层收口为独立后续线。

## 1. 背景

截至 `2026-04-22`：

- `00-83` 已完成 `content/share-cards` 默认卡片墙首屏收口
- `00-84` 已完成 `content/share-cards` 列表视图表格区收口

但从真实浏览器点击 `查看详情` 后，详情抽屉仍暴露一组更窄的视觉问题：

1. 抽屉宽度与 header / body padding 偏厚
2. hero 与 section 卡片仍沿用默认重卡片语义，首屏有效信息量偏低
3. `detail-block` 字段块高度约 `92px`，字段值短时仍占用过多垂直空间
4. `卡片概览 / 持卡人信息 / 绑定状态 / 互动统计` 四组信息仍需要更接近 reference 的轻量治理详情表达

当前已明确：

- 详情抽屉仍是 `ShareCardsView.vue` 内部详情 carrier
- 本轮不改变详情接口、字段语义和 legacy 修复能力
- 不回退已完成的 gallery 与 table 收口

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-85`
- 只处理 `content/share-cards` 详情抽屉：
  - `el-drawer` 壳层尺寸与 padding
  - `drawer-hero`
  - `detail-card`
  - `detail-grid`
  - `detail-block`
  - `issue-section`
- 用真实浏览器重新验证点击 `查看详情` 后的详情抽屉运行态

### 2.2 本轮不处理

- 不改默认卡片墙
- 不改列表视图表格区
- 不改底部 `治理补充动作`
- 不改详情接口与字段组合
- 不新增详情操作能力
- 不扩到其他页面

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `D:\XM\kaipai-team\kaipai-admin\src\views\content\ShareCardsView.vue` 的详情抽屉视觉密度。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 本轮不改变分享内容详情字段语义、详情 API、legacy 修复能力和列表 / 卡片视图。

### 3.2 抽屉壳层合同

- **R4** 抽屉宽度、header 高度和 body padding 应适度收紧，避免详情打开后显得脱离当前 reference 壳层节奏。
- **R5** 详情 hero 应保持内容身份与状态可读，同时降低垂直占高。

### 3.3 详情字段合同

- **R6** `detail-card` 的 header / body padding 需局部收紧，不再沿用默认重卡片节奏。
- **R7** `detail-grid` 与 `detail-block` 需明显降低字段块高度，并保持 label / value 层级清楚。
- **R8** `卡片概览 / 持卡人信息 / 绑定状态 / 互动统计` 四组信息在收紧后仍必须可读、可扫视。

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-85` 承接，不继续混入 `00-84`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-85` Spec，并明确它只处理分享内容详情抽屉
- [ ] 已完成抽屉壳层、hero、detail-card、detail-grid、detail-block 的局部收口
- [ ] 已通过真实浏览器复核 `content/share-cards` 详情抽屉
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
