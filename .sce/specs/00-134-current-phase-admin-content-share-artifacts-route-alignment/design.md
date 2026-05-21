# 00-134 设计说明

## 1. 设计目标

`00-134` 只做一件事：

1. 把已存在真实后端列表 / 更新接口的 `share-artifacts` 补成最小 hidden tooling 页面。

## 2. 已核实事实

### 2.1 后端合同与权限登记已就绪

已确认：

- 后端 `AdminContentController.java` 已提供：
  - `GET /admin/content/share-artifacts`
  - `PUT /admin/content/share-artifacts/{templateId}`
- 当前权限已登记：
  - `page.content.share-artifacts`
  - `action.content.artifact.edit`
- `ShareArtifactItemDTO` 当前返回字段包括：
  - `templateId`
  - `templateCode`
  - `sceneKey`
  - `templateName`
  - `status`
  - `artifactPresetJson`
  - `updateTime`

因此：

- 当前阻塞不在后端
- 当前只差前端 route / API / 容器层

### 2.2 为什么这轮做“列表 + 详情/编辑”

相比只补只读列表：

- `share-artifacts` 当前本来就有独立写接口
- JSON 字段也较单一：`artifactPresetJson`
- `00-133` 已形成可直接平移的最小闭环

因此本轮直接补到“列表 + 详情/编辑”，不再拆成两条 spec。

## 3. 设计策略

### 3.1 补齐前端合同

在前端新增：

- `ShareArtifactQuery`
- `ShareArtifactItem`
- `ShareArtifactPageResult`
- `ShareArtifactUpdatePayload`
- `fetchShareArtifacts(...)`
- `updateShareArtifacts(...)`

### 3.2 新增 hidden tooling 页面

新增：

- `D:\XM\kaipai-team\kaipai-admin\src\views\content\ShareArtifactsView.vue`

页面结构保持最小：

1. 概览卡
2. 筛选区
3. 列表台账
4. 详情抽屉
5. JSON 编辑弹窗

### 3.3 最小 JSON 校验

提交前只做：

- `JSON.parse(artifactPresetJson)`

若解析失败：

- 阻止提交
- 提示用户修正 JSON

不在本轮扩展 schema 校验。

### 3.4 复用 `00-133` 的实现模式

本轮优先平移 `ThemeTokensView.vue` 的已有结构：

- 同样使用 `GovernanceOverviewCards / FilterPanel / PageContainer`
- 同样保持一屏可见的表格 + 抽屉 + 弹窗
- 只把字段从 `baseThemeJson` 换成 `artifactPresetJson`
- 动作权限从 `action.content.theme.edit` 换成 `action.content.artifact.edit`

### 3.5 补齐 inventory 与 IA

同时补：

- `adminMenus`
- `router/index.ts`
- `admin-information-architecture.ts`

保证 hidden tooling inventory、route 和 topbar 文案一致。

## 4. 风险与边界

### 4.1 已确认

- 本轮只改前端
- 本轮不改后端接口
- 本轮不进入正式 8 页侧栏

### 4.2 验证重点

本轮重点看：

1. 路由是否可访问
2. 列表是否返回真实 JSON
3. 详情抽屉是否可打开
4. 编辑弹窗是否可打开
5. 非法 JSON 是否被前端拦下
