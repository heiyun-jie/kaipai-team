# 00-89 当前阶段后台机构目录首屏对齐（Current Phase Admin Organization Directory First Screen Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-74 current-phase-admin-reference-ui-architecture-rebuild
> 记录目的：在 `system/settings` 首屏收口后，继续把 `机构管理` 页的首屏结构、目录区密度和目录表达方式收口为更接近 reference 的机构目录页。

## 1. 背景

截至 `2026-04-22`：

- `OrganizationsView.vue` 已完成真实机构目录页回接
- 但尚未进入独立 page-level 精修线

真实截图对比已确认：

- reference：`D:\XM\kaipai-team\output\playwright\00-89\orgs-reference.png`
- 当前运行态：`D:\XM\kaipai-team\output\playwright\00-89\orgs-before.png`

当前差异：

1. 首屏 4 张 KPI 当前呈现为 `3 + 1` 断行，而 reference 为单行 4 卡
2. 当前边界提示、segment 卡、FilterPanel 共同把目录区压到首屏以下
3. 首个机构卡当前顶部约 `y=1092`，reference 首屏已进入机构列表
4. 当前目录区是卡片墙表达，而 reference 更接近机构目录表 / ledger

同时当前已明确：

- 当前页只承接已进入招募链路的机构 / 剧组样本
- 不等于完整组织主数据中心
- 不能伪造 reference 中的会员等级、到期日或其他无事实源字段

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-89`
- 只处理 `D:\XM\kaipai-team\kaipai-admin\src\views\user\OrganizationsView.vue` 的首屏和目录区：
  - KPI 概览
  - 边界提示
  - segment / 快筛壳层
  - 目录表达（cards -> ledger / list）
  - 高级筛选区在页面中的位置和密度
- 用真实浏览器复核 `http://127.0.0.1:5100/users/orgs`

### 2.2 本轮不处理

- 不改详情抽屉
- 不改 `/admin/recruit/projects`、`/admin/recruit/roles`、`/admin/recruit/applies` 与 `/company/{userId}` 事实源
- 不伪装成完整组织主数据中心
- 不扩到其他页面

## 3. 需求

### 3.1 证据与边界

- **R1** 本 Spec 只覆盖 `OrganizationsView.vue` 首屏和目录区，不覆盖详情抽屉。
- **R2** 本轮判断必须优先服从真实运行态；修复前后证据都必须来自真实浏览器。
- **R3** 本轮继续明确机构页边界：只承接招募链路机构目录，不伪造完整组织主数据。

### 3.2 首屏结构合同

- **R4** KPI 区在桌面宽度下必须恢复单行 4 卡。
- **R5** 边界提示、segment 和筛选壳层需明显收紧，不再把机构目录压到首屏以下。
- **R6** 机构目录必须重新成为首屏可见的核心区域。

### 3.3 目录表达合同

- **R7** 目录区需从当前厚卡片网格收口为更接近 reference 的机构目录 ledger / table 表达。
- **R8** 目录表达只能使用当前真实事实：机构名、用户 / 档案、项目 / 角色 / 投递统计、状态与治理入口。

### 3.4 治理要求

- **R9** 本轮必须通过独立 `00-89` 承接，不继续混入 `00-88`。
- **R10** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R11** 本轮必须把修复前后的运行态截图与量化结果写入 `execution.md`。

## 4. 验收标准

- [ ] 已新增独立 `00-89` Spec，并明确它只处理 `机构管理` 首屏和目录区
- [ ] 已完成单行 4 KPI、边界 / segment / 筛选区收紧以及目录区 ledger 化
- [ ] 已通过真实浏览器复核 `users/orgs`
- [ ] 已回填 README / mapping / CURRENT_CONTEXT / execution
