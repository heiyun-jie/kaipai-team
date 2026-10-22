# 演员卡结构化长页预览与共享渲染器 - 技术设计

_Requirements: 3.1-3.4, 4-6_

## 1. 现状根因

```text
submitGenerate
  -> ActorCardGenerateService.runGenerate
  -> previewUrl = expandedImageUrl || sourceImageUrl
  -> task success + generatedPreviewUrl=previewUrl
  -> generate/index 比较 URL 与主视觉相同
  -> placeholder 状态，禁止发布
```

该链路完成的是任务记录，不是演员卡长页。修复不能通过隐藏提示或继续展示主视觉完成。

## 2. 目标数据流

```text
生成页（卡主）
  -> POST generate / GET task status（保留兼容门禁）
  -> GET draft/{cardId}/preview（鉴权）
  -> ActorCardPublicRespDTO
  -> ActorCardRenderer

公开页（观看者）
  -> GET public/{cardId}（published 门禁）
  -> ActorCardPublicRespDTO
  -> ActorCardRenderer
```

两个入口只在权限、外壳和动作区不同，正文数据模型与渲染完全相同。

## 3. 后端设计

### 3.1 服务接口

`ActorCardPublicService` 新增：

```java
ActorCardPublicRespDTO getOwnerPreview(Long userId, Long cardId);
```

`ActorCardPublicServiceImpl` 将当前 `getPublicView` 的组装逻辑抽为私有 `buildView(ActorCard card)`：

- `getPublicView(cardId)`：存在 + published 校验后调用 `buildView`。
- `getOwnerPreview(userId, cardId)`：存在 + owner 校验后调用 `buildView`。
- `buildView` 继续统一签发主视觉、作品剧照、生活照片、视频和附件数据。

### 3.2 Controller

新增：

```text
GET /api/actor-card/draft/{cardId}/preview
Authorization: Bearer <token>
Response: R<ActorCardPublicRespDTO>
```

该路由不进入公开白名单，直接使用 `currentUserId(authentication)`。

## 4. 前端共享组件

新增分包内：

```text
src/pkg-actor-card/components/
├── ActorCardRenderer.vue
└── actor-card-render-model.ts
```

`ActorCardRenderer` 只依赖 Vue 和展示模型：

- props：`model`、`attachmentLoading`、`attachmentError`。
- emits：`previewAttachment`。
- 内部平台交互：图片预览、视频播放、单资源失败态。
- 禁止 import `@/api/*`、store 或主包业务组件。

组件根节点不持有页面滚动；`generate` 和 `view` 各自持有 `scroll-view`，以便保留生成页固定发布栏和公开页独立外壳。

### 4.1 分包共享组件媒体稳定性例外（00-229 回填）

00-228 初版曾由 `vite.config.ts` 向 `ActorCardRenderer` 产物 JSON 局部注入 `t-image`。00-229 运行态证明：组件 JSON、WXML 和 JS 属性均正确时，TDesign 图片在该分包共享 Uni 自定义组件内仍会永久停在加载态，Hero 和全部媒体无法显示。共享渲染器因此改用微信原生 `image`；固定尺寸、`aspectFill/widthFix`、失败回退和预览行为仍由组件自身维护。

这是媒体渲染稳定性例外，不影响页面表单、按钮、弹窗等通用控件继续使用 TDesign。`vite.config.ts` 中失效的局部依赖注入已删除，00-228/00-229 门禁共同保证组件产物 JSON 不再登记 `t-image`、WXML 只生成原生 `image`，并继续校验 build/dev scope hash 一致。

## 5. 页面改造

### 5.1 generate

状态收口为：

```ts
type Status = 'loading' | 'failed' | 'done';
```

- 普通生成：任务成功 -> `getDraftCardPreview` -> `done`。
- 名片夹预览：直接 `getDraftCardPreview`；若草稿尚无生成兼容标记，正文可看但主按钮为“生成演员卡”。
- 发布条件：`previewData != null && generationReady`。
- 删除 `placeholder`、`isPlaceholderPreview`、位图 `previewUrl`、`previewResourceStatus` 及相关文案。
- 加载文案改为“正在准备演员卡内容”，不再宣称 AI 正在生成整张长页。

### 5.2 view

- 保留页面加载/错误/导航/附件 API 处理。
- 将英雄区、资料和模块正文替换为 `ActorCardRenderer`。
- `getPublicCard`、草稿 403、404 和网络重试语义不变。

## 6. 验证设计

新增 `scripts/verify-00228-actor-card-structured-renderer.mjs`：

1. 后端存在鉴权草稿预览路由和 owner 校验。
2. 后端公开/草稿入口均调用同一 `buildView`。
3. 共享组件不 import API/store，且包含全部六类正文模块。
4. generate/view 均只引用一个 `ActorCardRenderer`。
5. generate 源码及 build/dev 产物无旧占位文案和 URL 等值判断。
6. build/dev 组件 WXML/WXSS/JS 存在、scope hash 一致。
7. 发布按钮受 `generationReady` 和结构化预览数据门禁。

测试命令：

```text
mvn -Dtest=ActorCardPublicServiceImplTest,ActorCardMediaBindingControllerContractTest test
npm run type-check
npm run verify:actor-card-renderer
npm run verify:tdesign-migration
uni build -p mp-weixin
powershell -File scripts/sync-mp-weixin.ps1
```

## 7. 运行态验收

- 固定 DevTools 项目：`kaipai-frontend/dist/dev/mp-weixin`。
- 打开 `pkg-actor-card/generate/index?cardId=<owned-id>&preview=1`：完整正文可见，可滚动，未生成草稿显示“生成演员卡”。
- 正常生成流程任务完成后：同一正文仍可见，主按钮切换“发布演员卡”。
- 打开已发布 `pkg-actor-card/view/index?cardId=<published-id>`：正文模块与生成预览一致。
- 使用内部模拟器截图、元素尺寸与 WXML 核验，不使用桌面坐标或整屏控制。

## 8. 实施结果（2026-08-20）

- 后端新增鉴权草稿预览接口，服务与 Controller 定向测试共 7 项通过。
- `ActorCardRenderer` 已由生成页与公开页共同使用，结构化展示资料、作品、生活照片、视频和附件。
- 未生成草稿可直接看正文，主操作显示「生成演员卡」；生成完成后切换为「发布演员卡」。
- 微信内部模拟器核验卡 7 的已生成预览与公开页，以及草稿 14 的未生成预览和生成状态切换；未执行发布。
- 证据：`.sce/evidence/wechat-devtools/00-228-generate-preview-card-7.png`、`00-228-public-view-card-7.png`、`00-228-draft-preview-card-14.png`、`00-228-generated-card-14-final.png`。
