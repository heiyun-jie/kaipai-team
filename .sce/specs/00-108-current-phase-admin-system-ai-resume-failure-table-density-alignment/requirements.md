# 00-108 当前阶段后台 AI 简历治理失败样本双表密度对齐（Current Phase Admin System AI Resume Failure Table Density Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-50 ai-resume-governance-collaboration-upgrade，00-107 current-phase-admin-system-roles-permission-orchestration-density-alignment
> 记录目的：在 `system/roles` 连续收口完成后，把后台 `system/ai-resume-governance` 中 `Failure Samples / Sensitive Hits` 两张失败治理表从超长厚表收口为当前 refined admin shell 可读的治理台账。

## 1. 背景

截至 `2026-04-22`：

- `00-107` 已完成 `system/roles` 权限编排区密度收口，角色治理页已进入可验收阶段
- 当前后台仍保留 `system/ai-resume-governance` 作为 AI 简历治理 capability carrier
- `00-50` 已明确 AI 简历治理协同需要展示通知、回执、自动催办、SLA 与审计链，但当前运行态 UI 仍明显偏厚

真实运行态截图已确认：

- 当前页：`D:\XM\kaipai-team\output\playwright\00-108\ai-governance-before.png`

当前差异：

1. `notice-grid` 仍是两列布局，但每张表都带宽表与 fixed 操作列，单卡宽度只有约 `559px`
2. `Failure Samples / Sensitive Hits` 两张卡整体高度均约 `8409px`
3. 失败样本首行高度约 `417px`，第二行约 `440px`
4. `责任协同` cell 内部堆叠完整投递链、诊断、SLA、催办、升级目标，首行 stack cell 约 `196 × 400`
5. 操作列动作数量多，当前操作区约 `476 × 64`，需要局部压缩但不能减少动作能力

### 当前量化

- `overviewGrid`：`1134 × 154`
- `boardGrid`：`1134 × 581`
- `filterPanel`：`1134 × 380`
- `noticeGrid`：`1134 × 8409`
- `Failure Samples` card：`559 × 8409`
- `Sensitive Hits` card：`559 × 8409`
- failure first row：`2100 × 417`
- failure second row：`2100 × 440`
- first collaboration stack：`196 × 400`
- first action wrapper：`476 × 64`
- `loadingMasks = 0`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-108`
- 只处理 `system/ai-resume-governance` 的失败治理双表区：
  - `Failure Samples`
  - `Sensitive Hits`
  - 两张表内的 `责任协同` cell
  - 两张表内的最近处置与操作列局部密度
  - `notice-grid` 宽表布局
- 用真实浏览器复核 `http://127.0.0.1:5100/system/ai-resume-governance`

### 2.2 本轮不处理

- 不改 AI 简历治理事实模型
- 不改失败样本查询接口、处置动作、权限按钮与状态流转
- 不改 `Quota Top Users / Recent Histories`
- 不改上方筛选项语义与筛选字段
- 不修复当前 `Governance Audit` 依赖的 operation logs 接口返回错误；只记录为运行态边界
- 不新增真实通知渠道、自动催办任务或真实 LLM 能力

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `system/ai-resume-governance` 的失败治理双表密度，不扩到其它系统治理页。
- **R2** 本轮判断必须优先服从真实运行态；修复前后截图与量化都必须来自真实浏览器。
- **R3** 当前页继续承接 AI 简历治理协同，不扩展新的 AI 业务能力或后端状态。

### 3.2 双表密度合同

- **R4** `Failure Samples / Sensitive Hits` 不应继续以两列窄卡承载宽表，必须恢复为更适合治理台账阅读的宽表容器。
- **R5** `责任协同` cell 必须保留责任人、协同状态、通知状态、回执状态、催办阶段、SLA 与升级目标的关键可见信息。
- **R6** 过长的投递链、诊断、催办、签收截止等完整文本必须继续可追溯，但不得继续全部撑开表格行高。
- **R7** 最近处置 cell 必须保留处理人、处理时间、处置记录数量和最近备注，不得丢失追溯语义。
- **R8** 操作列必须保留所有现有治理动作，且权限控制、禁用状态与点击行为不变。

### 3.3 治理要求

- **R9** 本轮必须保持失败样本列表、敏感命中列表、处置记录抽屉、处置弹窗、查询参数与 API 调用不变。
- **R10** 本轮必须通过独立 `00-108` 承接，不继续混入 `00-50` 或 `00-107`。
- **R11** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R12** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [x] 已新增独立 `00-108` Spec，并明确它只处理 AI 简历治理失败样本双表密度
- [x] 已完成 `notice-grid` 宽表容器、`责任协同` compact cell、最近处置与操作列局部收口
- [x] 已通过真实浏览器复核 `system/ai-resume-governance`
- [x] 已回填 README / mapping / CURRENT_CONTEXT / execution
