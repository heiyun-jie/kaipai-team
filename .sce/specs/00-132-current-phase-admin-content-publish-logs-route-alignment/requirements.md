# 00-132 当前阶段后台 content publish-logs 路由对齐（Current Phase Admin Content Publish Logs Route Alignment）

> 状态：进行中 | 优先级：中 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-124 current-phase-admin-content-permission-registry-alignment
> 记录目的：在 `00-110` 审计线下，把当前已存在后端独立列表接口、前端权限登记与角色授权，但仍缺少前端 route / API 容器的 `page.content.publish-logs` 做成独立最小落地切片。

## 1. 背景

截至 `2026-04-23`：

- 前端当前已登记：
  - `page.content.publish-logs`
- 后端当前已提供：
  - `GET /admin/content/publish-logs`
- 当前 dev 登录态角色已携带：
  - `page.content.publish-logs`
- 当前 live API 已返回真实数据：
  - `total = 26`
- 但前端当前仍缺：
  - `/content/publish-logs` route
  - `fetchTemplatePublishLogs(...)` API 装配
  - 独立页面容器

当前判断：

- 这不是新增业务能力
- 只是把已存在的模板发布记录独立事实源补成 hidden tooling 页面
- 与同时补 theme-tokens / share-artifacts 相比，`publish-logs` 的列表接口最单纯、字段最稳定，适合作为当前最小对象

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-132`
- 新增 `/content/publish-logs` route
- 新增模板发布记录页面容器
- 新增前端 API / type 装配：
  - `TemplatePublishLogQuery`
  - `TemplatePublishLogItem`
  - `fetchTemplatePublishLogs(...)`
- 在 `adminMenus` 中补齐 hidden tooling 能力库存登记
- 在 `admin-information-architecture.ts` 中补齐该页 tooling 前缀与说明
- 通过前端 `type-check` / `build`
- 真实浏览器复核 `/content/publish-logs`

### 2.2 本轮不处理

- 不同时补 `theme-tokens`
- 不同时补 `share-artifacts`
- 不改 `TemplatesView.vue` 主页面结构
- 不改后端接口合同
- 不把该页加入正式 8 页侧栏

## 3. 需求

### 3.1 路由与 IA 要求

- **R1** `/content/publish-logs` 必须作为 hidden tooling 接入，不得进入正式 8 页侧栏。
- **R2** route meta 必须使用：
  - `page.content.publish-logs`
  - `architectureLayer = 'tooling'`
  - `architectureArea = 'tooling'`
- **R3** `adminMenus` 必须补齐该页的能力库存登记，保持 hidden tooling inventory 与 router 一致。

### 3.2 页面要求

- **R4** 页面只承接模板发布记录的筛选、台账回看和单条详情查看，不扩展新的模板治理能力。
- **R5** 页面必须只消费：
  - `GET /admin/content/publish-logs`
  不新增伪事实源。
- **R6** 页面可以直接用列表项数据构建详情抽屉，不要求新增独立 detail API。

### 3.3 验证要求

- **R7** 必须通过：
  - `kaipai-admin` 的 `npm run type-check`
  - `kaipai-admin` 的 `npm run build`
- **R8** 必须基于真实浏览器复核：
  - `http://127.0.0.1:5100/content/publish-logs`
- **R9** 截图产物必须落到：
  - `D:\XM\kaipai-team\output\playwright\00-132\`

## 4. 验收标准

- [ ] 已新增独立 `00-132`
- [ ] `/content/publish-logs` route 已接入
- [ ] 前端 API / type 已补齐 `publish-logs` 合同
- [ ] 页面容器已能展示真实发布记录列表
- [ ] `adminMenus` / IA tooling 元数据已对齐
- [ ] 前端 `type-check` / `build` 已通过
- [ ] 真实浏览器已复核 `/content/publish-logs`
- [ ] README / mapping / CURRENT_CONTEXT / execution 已回填
