# 00-111 当前阶段后台历史 wrapper 退场第一批（Current Phase Admin Legacy Wrapper Retirement First Pass）

> 状态：已完成 | 优先级：最高 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit
> 记录目的：在 `00-110` 完成旧路由 / 旧代码 / fallback 审计矩阵后，先处理第一批低风险历史 wrapper：`DashboardView.vue` 与 `ReferralRiskView.vue`。

## 1. 背景

截至 `2026-04-22`：

- `00-110` 已把 `DashboardView.vue` 与 `ReferralRiskView.vue` 列为 `Retire candidate`
- 两个文件当前都只是薄包装：
  - `DashboardView.vue` -> `OverviewView.vue`
  - `ReferralRiskView.vue` -> `RiskView.vue`
- 当前在 `kaipai-admin/src` 内对以下关键字做搜索均未命中引用：
  - `DashboardView`
  - `ReferralRiskView`
- 当前进一步做全仓精确路径搜索，在排除 `.sce/`、`output/`、reference html 后，也未命中代码侧依赖

当前判断：

- 这两个文件属于低风险历史 wrapper
- 相比 `PlaceholderView.vue`，它们的删除边界更明确，适合作为第一批真实退场对象

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-111`
- 只删除以下两个历史 wrapper 文件：
  - `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardView.vue`
  - `D:\XM\kaipai-team\kaipai-admin\src\views\referral\ReferralRiskView.vue`
- 通过代码搜索与 `type-check/build` 验证它们删除后无回归

### 2.2 本轮不处理

- 不删除 `PlaceholderView.vue`
- 不删除任何 hidden tooling 页
- 不调整 router、menus、permission、fallback 逻辑
- 不做新的 UI 精修

## 3. 需求

### 3.1 删除边界

- **R1** 本 spec 只处理 `DashboardView.vue` 与 `ReferralRiskView.vue` 两个低风险 wrapper，不扩到其它候删对象。
- **R2** 只有在代码侧搜索未命中引用、且文件本身仅为薄包装时，才允许进入本轮删除。
- **R3** 本轮删除不得改变正式 8 页导航或 hidden tooling 路由的运行态行为。

### 3.2 验证合同

- **R4** 删除前必须记录搜索证据。
- **R5** 删除后必须通过：
  - `npm run type-check`
  - `npm run build`
- **R6** 若删除导致构建或类型失败，本轮必须回退判断，不继续扩大删除范围。

### 3.3 回填要求

- **R7** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R8** 本轮必须在 `execution.md` 中记录删除前搜索证据与删除后验证结果。

## 4. 验收标准

- [x] 已新增独立 `00-111` spec，并明确它只处理两张低风险历史 wrapper
- [x] `DashboardView.vue` 与 `ReferralRiskView.vue` 已删除
- [x] `type-check` 与 `build` 通过
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
