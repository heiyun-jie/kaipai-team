# 演员卡分享详情旧版结构与 3.0 视觉对齐 - 技术设计

_Requirements: 3.1-3.5, 4-6_

## 1. 视觉合同

| 路由 | 可见块 | 目标变化 | 必须保持 |
|---|---|---|---|
| `pkg-actor-card/generate/index` | 共享演员卡正文 | Hero 从滚动区顶部开始，返回按钮悬浮其上 | 生成/发布状态机、底部发布栏 |
| `pkg-actor-card/view/index` | 共享演员卡正文 | 与生成预览同构，返回按钮悬浮其上 | published/403/404/重试语义、分享/联系栏 |
| `ActorCardRenderer` | Hero、资料与媒体模块 | 精确复刻旧分享页坐标结构，只替换界面颜色 | 显隐、媒体预览、原生 `image` 稳定性 |

多加载点真因：TDesign `t-image` 的 `loading="default"` 会为 Hero、剧照和照片分别渲染 dots。初次修正已在源码和生成 JS 显式传入 `loading="slot"`、`error="slot"`，组件 JSON 也正确登记依赖，但微信运行态仍让全部媒体永久停在 `isLoading`，真实图片不显示。该故障只发生在 `ActorCardRenderer` 这类分包共享 Uni 自定义组件内；因此本组件媒体使用微信原生 `image` 作为稳定性例外。页面外壳承担唯一业务加载态，媒体内部只有无动画的固定容器和错误块。

## 2. 目标结构

```text
页面外壳（generate 或 view）
  -> 导航 / 页面级 loading / error
  -> ActorCardRenderer
       -> 750 × 1334 沉浸主视觉 Hero
          -> identity  (81, 203, 233, 291)
          -> facts     (83, 579, 285, 184)
          -> skills    (420, 579, 255, 184)
          -> works     (84, 802, 582, 112)
          -> photos    (80, 929, 591, 116)
          -> intro     (81, 1077, 281, 159)
          -> video     (416, 1077, 263, 159)
       -> 统计摘要
       -> 基础信息
       -> 形象与语言
       -> 技能特长
       -> 个人简介
       -> 拍摄经历
       -> 照片展示（两列）
       -> 视频简历
       -> PDF 简历（页图内嵌）
  -> 页面专属固定操作栏
```

## 3. 后端兼容扩展

`ActorCardPublicRespDTO` 顶层新增可选 `backgroundImageUrl`，值直接来自 `actor_card.background_image_url`。这是向后兼容的响应扩展，不新增表字段，不修改旧 `previewImageUrl` 语义。

`ActorCardPublicRespDTO.ProfileVO` 新增：

```text
gender / age / weight / bodyType / hairStyle
languages[] / skills[] / certified
```

字段合并优先级：

```text
profile_snapshot_json 显式字段
  -> actor_profile 当前档案补齐
  -> null / empty（前端显示待完善）
```

`AttachmentVO` 新增 `pageImages[]`。`buildView(card)` 使用卡主 `userId` 调用既有 `ActorMediaAssetService.listPages` 签发页图 URL；读取失败时返回空数组，保留附件文件名和 assetId。

后端只增加响应字段和依赖，不增加端点、不改白名单、不改数据库。

## 4. 前端展示模型

`ActorCardRenderModel` 与 `ActorCardPublicVO` 同步增加 `backgroundImageUrl`、可选丰富字段和 `attachment.pageImages`。Hero 图片优先级为 `backgroundImageUrl -> previewImageUrl -> 无动画占位`；旧后端未返回新字段时继续用 `previewImageUrl` 降级。

共享渲染器只接收 model：

- 本地 computed 生成 meta、facts、skills、stats 和 style label。
- 图片预览、视频播放继续作为组件内部平台交互。
- 附件有 `pageImages` 时直接展示并预览；没有时 emit `previewAttachment`，供 owner 预览兼容。
- 不 import API 或 store。

分享详情正文使用固定阅读顺序，不消费 `settings.order` 重排模块。开关只负责显隐：隐藏视频或附件时跳过对应模块，其余模块保持相对顺序不变。

Hero 采用相对定位画布，七个 slot 直接使用上述 rpx 坐标和尺寸。画布背景使用完整分享视觉 `aspectFill`；面板保留旧页半透明层次，只将旧纸色、棕色描边和红棕标签映射为 `$kp-color-canvas`、`$kp-color-border`、`$kp-color-brand-soft`、`$kp-color-brand` 等语义 Token。背景图片是用户内容资产，不应用滤镜或重新着色。

## 5. 页面导航与公开页操作栏

正常内容态的 `generate/index`、`view/index` 使用自包含 `KpFloatingBackButton`，绝对定位覆盖在页面外壳顶部；滚动区不渲染 `KpPageNav`，因此 Hero 从 `y=0` 开始。加载/错误状态仍保留悬浮返回能力。`00-212` 导航门禁将这两页登记为创建/公开页的模式 C 例外，防止后续自动治理重新加回白色导航。

`view/index` 使用自包含 `KpBottomActionBar`：

- 页面注册 `onShareAppMessage`，路径固定 `/pkg-actor-card/view/index?cardId={id}`。
- 分享图只在 `previewImageUrl` 为可持久 http(s) URL 时返回。
- 联系按钮调用 `uni.makePhoneCall`；无电话时 disabled。
- scroll 内容底部预留操作栏 + safe-area 空间。

两页外壳均使用 `height: 100vh; min-height: 0; overflow: hidden`，直接滚动容器使用 `height: 0; min-height: 0; flex: 1`。只写 `min-height: 100vh` 会让微信把 `scroll-view` 展开到完整正文高度，内部无法滚动。底部避让必须放在滚动内容内的显式 spacer；微信不会把 `scroll-view` 自身的 `padding-bottom` 稳定计入 `scrollHeight`，会让最后的提示或媒体仍被操作栏遮住。

## 6. 门禁

新增 `scripts/verify-00229-actor-card-share-detail-alignment.mjs`：

1. Spec 三件套存在且已加入索引。
2. DTO 与前端模型含丰富资料字段和附件 `pageImages`。
3. 后端快照优先、档案补齐、PDF 页图降级逻辑存在。
4. Renderer 含旧页全部区块、两列照片、PDF 页图、稳定媒体容器。
5. Renderer 所有媒体均编译为原生 `image`，组件 JSON 不再注入 `t-image`，页面无逐图点状加载。
6. generate/view 各只引用一次共享渲染器。
7. view 含固定分享/联系操作栏和 `onShareAppMessage`。
8. generate/view 的长页滚动容器都有明确视口约束。
9. build/dev WXML/WXSS/JS/JSON 与 scope hash 一致。
10. Hero 画布为 `750 × 1334rpx`，七个经典 slot 的坐标和尺寸完整存在。
11. generate/view 使用 `KpFloatingBackButton`，源码与产物均无白色 `KpPageNav`。
12. 正文模块源码顺序固定为统计、基础、形象语言、技能、简介、经历、照片、视频、PDF，不再由 `settings.order` 排序。
13. 后端、前端模型和产物都含兼容字段 `backgroundImageUrl`，Hero 按完整背景优先。

## 7. 验证命令

```text
mvn -Dtest=ActorCardPublicServiceImplTest test
npm run type-check
npm run verify:actor-card-renderer
npm run verify:actor-card-share-detail
npm run verify:tdesign-migration
npm run build:mp-weixin
```

微信运行态固定使用 `kaipai-frontend/dist/dev/mp-weixin`，只通过内部 MCP 截图和元素接口核验，不操作桌面坐标、键鼠或窗口置顶。

## 8. 首轮实施结果与纠偏（2026-08-20）

- 首轮实现已经解决多图 loading、长页滚动、PDF 页图和共享渲染器问题，这些稳定性结果继续保留。
- 首轮 Hero 被重新编排为白导航、头像全铺和白卡叠层，没有保留旧页精确坐标，原“视觉对齐完成”结论无效。
- 纠偏已按旧页 `750 × 1334` 画布和七个 slot 坐标完成；后端公开模型新增 `backgroundImageUrl`，卡 7 在运行态使用原水墨完整背景，普通头像不再冒充 Hero。
- generate/view 已删除白色 `KpPageNav`，改为 Hero 上的 `KpFloatingBackButton`；正文恢复固定旧页阅读顺序，显隐开关继续生效。
- 后端 7 项定向测试通过；前端类型检查、00-212 的 101 项门禁、00-228 的 68 项门禁、00-229 的 91 项门禁和 TDesign 的 1325 项门禁通过。
- build/dev 双侧产物一致；Renderer 媒体编译为原生 `image`，Hero、6 张摘要图、两列照片和 13 页 PDF 在微信运行态真实显示，页面无逐图 dots。
- 当前模拟器 generate 滚动视口实测 `390 × 844px`、内容高度 `6112px`；首屏、固定正文顺序、两列照片、视频、13 页 PDF 和末尾提示均可达，底栏不遮挡末尾内容。
- 本轮运行证据：`.sce/evidence/wechat-devtools/00-229-reference-correction-public-top.png`、`00-229-reference-correction-generate-top.png`、`00-229-reference-correction-generate-flow.png`、`00-229-reference-correction-generate-photos.png`、`00-229-reference-correction-generate-bottom.png`。
