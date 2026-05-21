# 00-132 设计说明

## 1. 设计目标

`00-132` 只做一件事：

1. 把已存在真实后端列表接口的 `publish-logs` 补成一个最小 hidden tooling 页面。

## 2. 已核实事实

### 2.1 后端合同与角色授权已就绪

已确认：

- 后端 `AdminContentController.java` 已提供：
  - `GET /admin/content/publish-logs`
- 当前权限为：
  - `page.content.publish-logs`
- 当前 dev 登录态角色已携带该权限
- 当前 live API 返回真实数据，总量为 `26`

因此：

- 当前阻塞不在后端
- 当前只差前端 route / API / 容器层

### 2.2 为什么先做 publish-logs

相比：

- `theme-tokens`
- `share-artifacts`

`publish-logs` 更适合当前最小切片，因为：

- DTO 更简单
- 列表事实源已直接可用
- 不需要额外编辑动作
- 可以只做只读台账页

## 3. 设计策略

### 3.1 补齐前端合同

在前端新增：

- `TemplatePublishLogQuery`
- `TemplatePublishLogItem`
- `TemplatePublishLogPageResult`
- `fetchTemplatePublishLogs(...)`

### 3.2 新增 hidden tooling 页面

新增：

- `D:\XM\kaipai-team\kaipai-admin\src\views\content\PublishLogsView.vue`

页面结构保持最小：

1. 概览卡
2. 筛选区
3. 列表台账
4. 详情抽屉

### 3.3 补齐 inventory 与 IA

为了保持审计线一致，需要同时补：

- `adminMenus` hidden tooling child
- `router/index.ts`
- `admin-information-architecture.ts`

这三层一致后，`/content/publish-logs` 才算是完整接入，而不是仅靠硬编码 route 存活。

## 4. 风险与边界

### 4.1 已确认

- 本轮只读，不新增编辑 / 回滚动作
- 本轮不改后端接口
- 本轮不进入正式 8 页侧栏

### 4.2 验证重点

本轮重点看：

1. 路由是否可访问
2. 列表是否返回真实数据
3. tooling 页壳层是否正确
4. 详情抽屉是否可读
