# 00-134 当前阶段后台 content share-artifacts 路由对齐（Current Phase Admin Content Share Artifacts Route Alignment）

> 状态：已完成 | 优先级：中 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-124 current-phase-admin-content-permission-registry-alignment、00-133 current-phase-admin-content-theme-tokens-route-alignment
> 记录目的：在 `00-133` 已补齐 `theme-tokens` hidden tooling 页面后，继续把已存在后端列表/更新接口、角色授权和前端权限登记的 `page.content.share-artifacts` 做成独立最小落地切片。

## 1. 背景

截至 `2026-04-23`：

- 前端当前已登记：
  - `page.content.share-artifacts`
  - `action.content.artifact.edit`
- 后端当前已提供：
  - `GET /admin/content/share-artifacts`
  - `PUT /admin/content/share-artifacts/{templateId}`
- 当前 dev 运行态已确认：
  - 前端 `http://127.0.0.1:5100/login` 可访问
  - 后端 `http://127.0.0.1:8010/api` 在当前机器可达
- 后端 DTO 已确认返回：
  - `templateId`
  - `templateCode`
  - `sceneKey`
  - `templateName`
  - `status`
  - `artifactPresetJson`
  - `updateTime`

本轮核实到：

- 前端当前仍缺：
  - `/content/share-artifacts` route
  - `fetchShareArtifacts(...)`
  - `updateShareArtifacts(...)`
  - `ShareArtifactQuery / ShareArtifactItem / ShareArtifactUpdatePayload`
  - 独立页面容器

当前判断：

- 这不是新增业务能力
- 只是把已存在分享产物配置列表 / 更新能力补成 hidden tooling 页面
- 当前更合理的最小方式是：
  - 列表
  - 详情
  - JSON 编辑

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-134`
- 新增 `/content/share-artifacts` route
- 新增分享产物页面容器
- 新增前端 API / type 装配：
  - `ShareArtifactQuery`
  - `ShareArtifactItem`
  - `ShareArtifactPageResult`
  - `ShareArtifactUpdatePayload`
  - `fetchShareArtifacts(...)`
  - `updateShareArtifacts(...)`
- 在 `adminMenus` 中补齐 hidden tooling 能力库存登记
- 在 `admin-information-architecture.ts` 中补齐该页 tooling 前缀与说明
- 页面支持最小 JSON 编辑提交流程
- 通过前端 `type-check` / `build`
- 真实浏览器复核 `/content/share-artifacts`

### 2.2 本轮不处理

- 不同时补 `payment.transactions`
- 不同时补 `refund.logs`
- 不改 `TemplatesView.vue` 主页面结构
- 不新增分享产物 schema 校验器
- 不改后端接口合同
- 不把该页加入正式 8 页侧栏

## 3. 需求

### 3.1 路由与 IA 要求

- **R1** `/content/share-artifacts` 必须作为 hidden tooling 接入，不得进入正式 8 页侧栏。
- **R2** route meta 必须使用：
  - `page.content.share-artifacts`
  - `architectureLayer = 'tooling'`
  - `architectureArea = 'tooling'`
- **R3** `adminMenus` 必须补齐该页的能力库存登记，保持 hidden tooling inventory 与 router 一致。

### 3.2 页面要求

- **R4** 页面只承接分享产物配置的筛选、台账回看和最小 JSON 编辑，不扩展新的模板治理能力。
- **R5** 页面必须只消费：
  - `GET /admin/content/share-artifacts`
  - `PUT /admin/content/share-artifacts/{templateId}`
- **R6** 编辑提交前必须做最小 JSON 合法性校验，避免把明显非法 JSON 直接发到后端。

### 3.3 验证要求

- **R7** 必须通过：
  - `kaipai-admin` 的 `npm run type-check`
  - `kaipai-admin` 的 `npm run build`
- **R8** 必须基于真实浏览器复核：
  - `http://127.0.0.1:5100/content/share-artifacts`
- **R9** 截图产物必须落到：
  - `D:\XM\kaipai-team\output\playwright\00-134\`

## 4. 验收标准

- [x] 已新增独立 `00-134`
- [x] `/content/share-artifacts` route 已接入
- [x] 前端 API / type 已补齐 `share-artifacts` 合同
- [x] 页面容器已能展示真实分享产物配置列表
- [x] 页面已支持最小 JSON 编辑
- [x] `adminMenus` / IA tooling 元数据已对齐
- [x] 前端 `type-check` / `build` 已通过
- [x] 真实浏览器已复核 `/content/share-artifacts`
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
