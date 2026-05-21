# 00-83 当前阶段后台分享内容首屏对齐（Current Phase Admin Share Content First-Screen Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-74 current-phase-admin-reference-ui-architecture-rebuild
> 记录目的：在模板库连续收口后，把下一条 page-level 精修主线切到 `content/share-cards`，只处理默认卡片墙首屏的 tabs / 汇总卡 / 筛选区 / 卡片比例。

## 1. 背景

截至 `2026-04-22`：

- `00-74` 已完成后台 8 页正式 IA 回接
- `content/share-cards` 已作为正式“分享内容”页面进入运行态

当前继续核对分享内容运行态后，已确认首屏还存在一组更窄的差异：

1. tabs / 视图切换 / 汇总卡仍偏厚
2. 筛选区占高偏大
3. 卡片封面与卡体比例偏高
4. 当前 8 张卡片同时出现时，首屏整体密度仍低于 reference 的内容卡片墙表达

同时已通过真实浏览器量化确认：

- `content-shell-card__stats` 当前为 4 列
- `content-gallery` 当前为 4 列
- 首张分享内容卡高度约为 `487px`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-83`
- 只处理 `content/share-cards` 默认 `gallery` 模式首屏：
  - tabs
  - 视图切换
  - 汇总卡
  - 筛选区
  - 卡片墙
- 用真实浏览器重新验证 `http://127.0.0.1:5100/content/share-cards`

### 2.2 本轮不处理

- 不改列表视图表格
- 不改详情抽屉
- 不改底部 `治理补充动作`
- 不改真实分享卡动作和 legacy 修复链路
- 不改其他正式页

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `D:\XM\kaipai-team\kaipai-admin\src\views\content\ShareCardsView.vue` 在默认 `gallery` 模式下的首屏。
- **R2** 本轮判断必须优先服从真实运行态；当前核心证据包括：
  - `D:\XM\kaipai-team\output\playwright\00-83\share-cards-before.png`
- **R3** 本轮不改变真实分享卡事实源、详情抽屉和 legacy 修复能力。

### 3.2 首屏合同

- **R4** tabs / 视图切换 / 汇总卡 / 筛选区必须比当前更紧凑，降低首屏无效占高。
- **R5** 分享内容卡片墙应更接近 reference 的内容卡片墙气质，但仍保持当前真实 `UserShareCard` carrier。
- **R6** 当前样本较多时，卡片比例与 grid 间距需更稳定，避免封面过高导致首屏可见信息量不足。

### 3.3 治理要求

- **R7** 本轮必须通过独立 `00-83` 承接，不继续把分享内容首屏精修混入 `00-82` 或更早 spec。
- **R8** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R9** 本轮必须把修复前后的 `content/share-cards` 浏览器证据写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-83` Spec，并明确它只处理分享内容首屏
- [ ] 已完成 tabs / 汇总卡 / 筛选区 / 卡片墙的局部收口
- [ ] 已通过真实浏览器复核 `content/share-cards`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
