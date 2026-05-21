# 00-140 设计说明

## 1. 设计目标

`00-140` 处理用户最新反馈中的三条高优先级 UI / IA / 配置问题：

1. 固定左侧菜单高度。
2. 机构管理退出正式架构。
3. 风格模板从 JSON 主交互切到可视化配置。

## 2. 已核实事实

### 2.1 侧栏增高根因

当前：

- `AdminLayout.vue` 是横向 flex
- `AdminSidebar.vue` 是普通 flex item
- `AdminSidebar.vue` 未设置 `height: 100vh / position: sticky / overflow hidden`

因此当右侧内容很长时，父级高度被内容撑高，左侧侧栏也会被拉伸。

### 2.2 机构管理仍出现的根因

当前以下位置仍保留机构管理正式页口径：

- `constants/menus.ts`
  - `adminSidebarMenus` 中有 `/users/orgs`
- `router/index.ts`
  - `/users/orgs` 仍是 `mainline / growth`
- `constants/admin-information-architecture.ts`
  - `adminGrowthRoutes` 包含 `/users/orgs`
- `OverviewView.vue`
  - 正式页面矩阵中有机构管理卡

因此后台仍能看到该模块不是缓存问题，而是代码仍把它当正式模块。

### 2.3 风格模板 JSON 暴露根因

当前 `TemplatesView.vue` 的编辑弹窗直接暴露：

- `baseThemeJson`
- `artifactPresetJson`

这与用户期望的“模拟小程序页面配置 -> 生成 JSON -> 保存后端 -> 前端映射 JSON”不一致。

## 3. 设计策略

### 3.1 侧栏固定高度

在 `AdminSidebar.vue` 中：

- 设置 `position: sticky`
- 设置 `top: 0`
- 设置 `height: 100vh`
- 设置 `overflow: hidden`
- 设置 scroll 区 `min-height: 0`

移动端再回退为普通高度。

### 3.2 机构管理先从正式架构退场

本轮不直接删除 `OrganizationsView.vue`，原因：

- 当前它仍有真实后端事实源
- 直接删除 route 风险高
- 需要后续独立 spec 核销

本轮先完成：

- 正式侧栏退场
- 仪表盘矩阵退场
- IA growth 退场
- route meta 降级为 `retire-candidate`

### 3.3 模板编辑第一批可视化配置

本轮只改 `TemplatesView.vue`：

- 把 `主题 JSON` textarea 改成颜色配置：
  - primary
  - accent
  - background
  - text
  - heroText
- 把 `分享产物 JSON` textarea 改成可视化配置：
  - heroEyebrow
  - coverImage
  - contentFocus
  - shareCard / poster enabled + ratio
- 增加小程序卡片预览。
- 保存时生成：
  - `baseThemeJson`
  - `artifactPresetJson`

### 3.4 后端合同保持不变

本轮继续调用：

- `createTemplate(...)`
- `updateTemplate(...)`

不改后端 DTO，不做数据库迁移。

## 4. 风险与边界

### 4.1 已确认

- 机构管理本轮只是正式架构退场，不删除页面。
- 模板配置本轮只是第一批可视化表单，不做完整小程序渲染器。
- Hidden tooling 的 `theme-tokens / share-artifacts` 仍保留 JSON 低层治理能力。

### 4.2 待验证

- 现有模板 JSON 中是否存在大量未建模字段。

设计处理：

- 解析时保留原 JSON root
- 生成时只覆盖已建模字段，尽量避免丢失未建模字段
