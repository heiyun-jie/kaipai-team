# 00-133 当前阶段后台 content theme-tokens 路由对齐（Current Phase Admin Content Theme Tokens Route Alignment）

> 状态：已完成 | 优先级：中 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-124 current-phase-admin-content-permission-registry-alignment
> 记录目的：在 `00-132` 已补齐 `publish-logs` hidden tooling 页面后，继续把已存在后端列表/更新接口、角色授权和前端权限登记的 `page.content.theme-tokens` 做成独立最小落地切片。

## 1. 背景

截至 `2026-04-23`：

- 前端当前已登记：
  - `page.content.theme-tokens`
  - `action.content.theme.edit`
- 后端当前已提供：
  - `GET /admin/content/theme-tokens`
  - `PUT /admin/content/theme-tokens/{templateId}`
- 当前 dev 登录态角色已携带：
  - `page.content.theme-tokens`
  - `action.content.theme.edit`
- 当前 live API 已返回真实数据：
  - `total = 1`
  - `baseThemeJson` 为真实主题 JSON

本轮核实到：

- 前端当前仍缺：
  - `/content/theme-tokens` route
  - `fetchThemeTokens(...)`
  - `updateThemeTokens(...)`
  - `ThemeTokenQuery / ThemeTokenItem / ThemeTokenUpdatePayload`
  - 独立页面容器

当前判断：

- 这不是新增业务能力
- 只是把已存在主题 Token 列表 / 更新能力补成 hidden tooling 页面
- 当前更合理的最小方式是：
  - 列表
  - 详情
  - JSON 编辑

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-133`
- 新增 `/content/theme-tokens` route
- 新增主题 Token 页面容器
- 新增前端 API / type 装配：
  - `ThemeTokenQuery`
  - `ThemeTokenItem`
  - `ThemeTokenPageResult`
  - `ThemeTokenUpdatePayload`
  - `fetchThemeTokens(...)`
  - `updateThemeTokens(...)`
- 在 `adminMenus` 中补齐 hidden tooling 能力库存登记
- 在 `admin-information-architecture.ts` 中补齐该页 tooling 前缀与说明
- 页面支持最小 JSON 编辑提交流程
- 通过前端 `type-check` / `build`
- 真实浏览器复核 `/content/theme-tokens`

### 2.2 本轮不处理

- 不同时补 `share-artifacts`
- 不改 `TemplatesView.vue` 主页面结构
- 不新增模板发布动作
- 不改后端接口合同
- 不把该页加入正式 8 页侧栏

## 3. 需求

### 3.1 路由与 IA 要求

- **R1** `/content/theme-tokens` 必须作为 hidden tooling 接入，不得进入正式 8 页侧栏。
- **R2** route meta 必须使用：
  - `page.content.theme-tokens`
  - `architectureLayer = 'tooling'`
  - `architectureArea = 'tooling'`
- **R3** `adminMenus` 必须补齐该页的能力库存登记，保持 hidden tooling inventory 与 router 一致。

### 3.2 页面要求

- **R4** 页面只承接主题 Token 的筛选、台账回看和最小 JSON 编辑，不扩展新的模板治理能力。
- **R5** 页面必须只消费：
  - `GET /admin/content/theme-tokens`
  - `PUT /admin/content/theme-tokens/{templateId}`
- **R6** 编辑提交前必须做最小 JSON 合法性校验，避免把明显非法 JSON 直接发到后端。

### 3.3 验证要求

- **R7** 必须通过：
  - `kaipai-admin` 的 `npm run type-check`
  - `kaipai-admin` 的 `npm run build`
- **R8** 必须基于真实浏览器复核：
  - `http://127.0.0.1:5100/content/theme-tokens`
- **R9** 截图产物必须落到：
  - `D:\XM\kaipai-team\output\playwright\00-133\`

## 4. 验收标准

- [x] 已新增独立 `00-133`
- [x] `/content/theme-tokens` route 已接入
- [x] 前端 API / type 已补齐 `theme-tokens` 合同
- [x] 页面容器已能展示真实主题 Token 列表
- [x] 页面已支持最小 JSON 编辑
- [x] `adminMenus` / IA tooling 元数据已对齐
- [x] 前端 `type-check` / `build` 已通过
- [x] 真实浏览器已复核 `/content/theme-tokens`
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
