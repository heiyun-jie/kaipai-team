# 00-140 当前阶段后台壳层 / 架构 / 模板配置对齐（Current Phase Admin Shell IA and Template Config Alignment）

> 状态：已完成 | 优先级：最高 | 依赖：00-74 current-phase-admin-reference-ui-architecture-rebuild、00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-139 current-phase-admin-missing-backend-notice-retirement
> 记录目的：针对当前用户反馈，收口三类问题：左侧菜单高度随右侧内容增长、机构管理仍作为正式模块出现、风格模板仍暴露 JSON 编辑而非可视化配置。

## 1. 背景

截至 `2026-04-23`：

- 当前后台左侧菜单由 `AdminSidebar.vue` 承接，布局父级 `AdminLayout.vue` 使用横向 flex。
- 当前 `AdminSidebar.vue` 未设置固定视口高度，作为 flex item 会随右侧内容高度拉伸。
- 当前正式侧栏仍在 `adminSidebarMenus` 中暴露：
  - `机构管理`
  - `/users/orgs`
- 当前 `/users/orgs` route meta 仍是：
  - `architectureLayer = mainline`
  - `architectureArea = growth`
- 当前 `OverviewView.vue` 的正式页面矩阵仍包含 `机构管理`。
- 当前 `TemplatesView.vue` 的模板编辑弹窗仍直接暴露：
  - `主题 JSON`
  - `分享产物 JSON`

用户最新反馈明确要求：

1. 左侧菜单栏固定高度，不再随右侧内容高度增加。
2. 最新架构中机构相关信息已删除，后台不应继续看到机构管理模块。
3. 风格模板应该是配置，不是直接编辑 JSON；需要模拟小程序页面配置，再生成 JSON 保存到后端，前端按 JSON 映射。

当前判断：

- 侧栏高度属于壳层 CSS 缺口，可直接修。
- 机构管理当前出现在后台，是因为旧 `00-74` 主线仍将其保留为正式 8 页之一；用户最新反馈覆盖该旧口径，本轮应先从正式导航和正式矩阵退场，并将直达 route 降为 `retire-candidate`。
- 风格模板配置改造属于交互模型变化，本轮先做 `TemplatesView.vue` 的第一批可视化配置，不改后端接口合同，继续生成现有 `baseThemeJson / artifactPresetJson` 保存。

## 2. 范围

### 2.1 本轮必须处理

- 修复 `AdminSidebar.vue`：
  - 固定视口高度
  - 内部菜单独立滚动
  - 不随右侧内容增高
- 从正式后台导航退场机构管理：
  - 从 `adminSidebarMenus` 移除 `/users/orgs`
  - 从 `OverviewView.vue` 正式矩阵移除机构管理卡
  - 从 `adminGrowthRoutes` 移除 `/users/orgs`
  - 将 `/users/orgs` route meta 从 `mainline` 改为 `retire-candidate`
- 风格模板编辑弹窗改造：
  - 不再直接展示 `主题 JSON / 分享产物 JSON` textarea
  - 增加主题色可视化配置
  - 增加小程序分享卡预览
  - 增加分享产物可视化配置
  - 保存时仍生成 `baseThemeJson / artifactPresetJson` 并调用现有后端接口
- 通过：
  - `npm run type-check`
  - `npm run build`

### 2.2 本轮不处理

- 不删除 `OrganizationsView.vue`
- 不删除 `/users/orgs` route
- 不改后端模板接口合同
- 不改小程序前台映射逻辑
- 不重构 `ThemeTokensView.vue / ShareArtifactsView.vue` 两个 hidden tooling 页面

## 3. 需求

### 3.1 侧栏高度要求

- **R1** 左侧菜单必须固定为视口高度，不得随右侧内容高度增长。
- **R2** 当菜单内容超出视口高度时，应由左侧菜单内部滚动承接。
- **R3** 移动端布局仍可回到纵向结构，不强制固定侧栏。

### 3.2 机构管理退场要求

- **R4** 正式侧栏不得继续出现 `机构管理`。
- **R5** 仪表盘正式页面矩阵不得继续展示 `机构管理` 卡片。
- **R6** `/users/orgs` 本轮不直接删除，但必须退出 `mainline/growth`，改为 `retire-candidate`，为后续独立核销做准备。

### 3.3 风格模板配置要求

- **R7** 模板编辑弹窗不得再直接暴露 `主题 JSON / 分享产物 JSON` textarea 作为主交互。
- **R8** 模板编辑必须提供可视化主题配置，生成 `baseThemeJson`。
- **R9** 模板编辑必须提供小程序分享卡预览和产物配置，生成 `artifactPresetJson`。
- **R10** 本轮不得改变后端保存合同，仍使用既有 `createTemplate / updateTemplate`。

### 3.4 验证要求

- **R11** 本轮必须通过 `type-check / build`。
- **R12** 本轮必须回填 `README.md / spec-code-mapping.md / CURRENT_CONTEXT.md / execution.md`。

## 4. 验收标准

- [x] 左侧菜单固定视口高度并内部滚动
- [x] 正式侧栏不再出现机构管理
- [x] 仪表盘正式页面矩阵不再出现机构管理
- [x] `/users/orgs` route 降为 retire-candidate
- [x] 风格模板编辑弹窗不再直接展示 JSON textarea
- [x] 风格模板编辑支持主题配置、分享产物配置与小程序样式预览
- [x] 保存前能生成 `baseThemeJson / artifactPresetJson`
- [x] `type-check / build` 通过
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
