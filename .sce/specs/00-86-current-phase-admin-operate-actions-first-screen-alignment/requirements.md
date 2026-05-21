# 00-86 当前阶段后台运营动作首屏对齐（Current Phase Admin Operate Actions First Screen Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-74 current-phase-admin-reference-ui-architecture-rebuild
> 记录目的：在 `content/share-cards` 同页三轮收口完成后，继续推进 `operate/actions` 正式页首屏对齐，只处理首屏结构、密度和动作推荐层级，不把下方最近治理动态混入本轮。

## 1. 背景

截至 `2026-04-22`：

- `ShareCardsView.vue` 已完成 `00-83 / 00-84 / 00-85`
- 当前后台下一个尚未进入独立 page-level 精修的正式页是 `operate/actions`

真实截图对比已确认：

- reference：`D:\XM\kaipai-team\output\playwright\00-86\operate-actions-reference.png`
- 当前运行态：`D:\XM\kaipai-team\output\playwright\00-86\operate-actions-before.png`

当前差异主要集中在首屏：

1. 顶部工具卡偏厚，`AI-RECOMMENDED ACTIONS` 仍占较高首屏高度
2. 4 张 overview 卡片当前位于动作推荐之前，压低了首屏动作推荐的第一语义
3. `action-recommendation` 行高、字号和间距偏厚，导致首屏可见动作数明显少于 reference
4. 当前首个动作卡顶部约在 `y=674`，而 reference 的首个动作行明显更早进入首屏

同时当前已明确：

- 当前页只能重组现有真实统计与现有治理入口
- 不能新增伪运营能力
- 不能伪造 reference 中的 campaign 数据

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-86`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\operate\ActionsView.vue` 的首屏：
  - 顶部工具卡
  - 动作推荐列表
  - overview 辅助统计卡
- 用真实浏览器复核 `http://127.0.0.1:5100/operate/actions`

### 2.2 本轮不处理

- 不改下方 `最近治理动态`
- 不改 route query 逻辑
- 不改真实接口与数据字段
- 不扩到其他页面

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `ActionsView.vue` 的首屏结构与密度，不覆盖最近治理动态区。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 本轮不能伪造 reference 中的运营 campaign 数据，仍只能重组当前真实统计与现有治理入口。

### 3.2 首屏结构合同

- **R4** 动作推荐必须提升为 `operate/actions` 首屏的第一语义，不再被大块概览卡压到下方。
- **R5** 顶部工具卡需要收紧为更接近 reference 的轻量标题 + 控件壳层。
- **R6** overview 统计卡需要降为辅助信息层，不再主导首屏。

### 3.3 动作推荐合同

- **R7** `action-recommendation` 需要明显降低行高、字号和间距，使首屏能看到更多动作项。
- **R8** 标题、目标页、提示、指标和按钮在收紧后仍需保持可读、可点击。

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-86` 承接，不继续混入 `00-85`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-86` Spec，并明确它只处理 `operate/actions` 首屏
- [ ] 已完成工具卡、动作推荐和 overview 辅助统计卡的首屏收口
- [ ] 已通过真实浏览器复核 `operate/actions`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
