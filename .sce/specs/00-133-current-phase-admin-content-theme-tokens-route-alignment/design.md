# 00-133 设计说明

## 1. 设计目标

`00-133` 只做一件事：

1. 把已存在真实后端列表 / 更新接口的 `theme-tokens` 补成最小 hidden tooling 页面。

## 2. 已核实事实

### 2.1 后端合同与角色授权已就绪

已确认：

- 后端 `AdminContentController.java` 已提供：
  - `GET /admin/content/theme-tokens`
  - `PUT /admin/content/theme-tokens/{templateId}`
- 当前权限为：
  - `page.content.theme-tokens`
  - `action.content.theme.edit`
- 当前 dev 登录态角色已携带这两条权限
- 当前 live API 返回真实数据，总量为 `1`

因此：

- 当前阻塞不在后端
- 当前只差前端 route / API / 容器层

### 2.2 为什么这轮做“列表 + 详情/编辑”

相比只补只读列表：

- `theme-tokens` 当前本来就有独立写接口
- JSON 字段也较单一：`baseThemeJson`
- 当前最小闭环是：
  - 看得到
  - 打得开
  - 能最小编辑

因此本轮直接补到“列表 + 详情/编辑”，不再拖到下一条 spec。

## 3. 设计策略

### 3.1 补齐前端合同

在前端新增：

- `ThemeTokenQuery`
- `ThemeTokenItem`
- `ThemeTokenPageResult`
- `ThemeTokenUpdatePayload`
- `fetchThemeTokens(...)`
- `updateThemeTokens(...)`

### 3.2 新增 hidden tooling 页面

新增：

- `D:\XM\kaipai-team\kaipai-admin\src\views\content\ThemeTokensView.vue`

页面结构保持最小：

1. 概览卡
2. 筛选区
3. 列表台账
4. 详情抽屉
5. JSON 编辑弹窗

### 3.3 最小 JSON 校验

提交前只做：

- `JSON.parse(baseThemeJson)`

若解析失败：

- 阻止提交
- 提示用户修正 JSON

不在本轮扩展 schema 校验。

### 3.4 补齐 inventory 与 IA

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
3. 编辑弹窗是否可打开
4. 非法 JSON 是否被前端拦下
