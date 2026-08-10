# 演员卡步骤 6 附件简历端到端接通 - 技术设计

## 1. 现状证据链

全链路六段，逐段实测结论：

| 段 | 现状 | 证据 |
|---|---|---|
| 选择 | 无入口。T4 已删空控件 | `step-attachment/index.vue:18-24` |
| 上传 | **能力已存在，卡侧未调用** | `api/actor-asset.ts:28` `uploadActorAsset` |
| 后端收口 | **已支持 PDF 全生命周期** | `ActorMediaAssetServiceImpl.java:14-53`；白名单 `photo/video/pdf`，`pdf` 分类仅 `resume`（`:247-250`） |
| 落库 | 字段模型错位：存 URL，但 URL 10 分钟失效 | `actor_card.attachment_url VARCHAR(1024)`（`V20260731_001:20`）vs `Duration.ofMinutes(10)`（`ActorMediaAssetServiceImpl.java:128`） |
| 回读 | 仅回填自身页面 | `step-attachment/index.vue:58` |
| 消费 | **零消费方** | 生成 `ActorCardGenerateService.java:89-91` TODO 占位；发布 `toListItem` 无附件；`settingsJson` 服务端从不解析 |

`attachment_url` 的两处现有读取都只取布尔：步骤标签
`hasAttachment = StringUtils.hasText(...)`（`ActorCardDraftServiceImpl.java:229-230`）、
完成度 `if (hasText) done++`（`ActorCardPublishService.java:125`）。改绑 assetId 后这两处判据须一并切换，
否则步骤 6 会永远显示「未添加」、完成度永远少 1。这是最容易漏的连带改动。

## 2. 核心设计决策

### 2.1 存 assetId，不存 URL

```
actor_card.attachment_asset_id BIGINT NULL  →  actor_media_asset.asset_id
```

理由不是「更规范」，而是存 URL **在私有桶下不可能正确**。素材键形如
`actor-private/{userId}/{mediaType}/yyyy/MM/dd/{uuid}{ext}`（`CosPrivateActorMediaStorage.java:76-85`），
只能通过预签名 GET 读取（`:64-69`）。持久化任何一个签名结果都会在 10 分钟后变成死链。

同时这解决了越权面：assetId 可验归属，裸 URL 无法验。

### 2.2 预览走「页图接口」，不走 openDocument

两个可选方案：

| 方案 | 做法 | 取舍 |
|---|---|---|
| A | 签名 URL + `uni.downloadFile` + `uni.openDocument` | 需要把 COS 域名加进 **downloadFile 合法域名**白名单；依赖运维配置，且 10 分钟 URL 与下载重试叠加易踩坑 |
| B **（选定）** | 新增页图列表接口，返回逐页签名 URL，用 `<image>` 渲染 | 复用 `actor_media_asset_page` 里**已经转好**的 JPEG；小程序 `<image src>` 不受合法域名白名单约束（白名单只管 `request`/`downloadFile`/`uploadFile`/`connectSocket`），不引入运维前置 |

选 B 的决定性理由是 B 不新增运维依赖，且页图本来就已生成（72 DPI、宽≤1200、q=0.86、≤20 页，
`ActorPrivatePdfProcessorImpl.java:27-41`），当前只是**没有接口暴露**——补一个读接口即可，属最小增量。

顺带说明：这个页图接口对个人资料侧同样是缺口（`pkg-profile/assets/index.vue:265-268` 的 PDF
预览是假的）。本轮把接口建出来，个人资料侧接不接由后续决定，本 Spec 不改那一页。

### 2.3 清空语义用嵌套对象表达，不引入三态标志位

`saveStep` 的困境是「`null` = 不变」与「清空」无法用同一个标量字段区分。既有 `!= null` 写法把
「跳过时提交空串」当成了清空意图，这是缺陷来源。

选定做法：`ActorCardStepSaveReqDTO` 增加嵌套对象

```java
private AttachmentBinding attachment;   // null = 本次不涉及附件
// AttachmentBinding { Long assetId; }  // assetId = null 表示显式清空
```

- 不传 `attachment` 键 → 不动该字段（跳过 / 下一步走这条）
- 传 `attachment: { assetId: 123 }` → 绑定并验权
- 传 `attachment: { assetId: null }` → 显式清空（仅「删除」按钮触发）

比加 `clearAttachment: true` 标志位更好的地方在于：清空意图和赋值意图共用一个字段，
不存在「同时传了 assetId 和 clear=true」这种自相矛盾的入参。该口径可作为 `00-213` T8 收敛
`photosJson` / `videoUrl` 同类问题的样板，但本轮只落附件一份，不扩散。

## 3. 后端改动清单

### 3.1 迁移

`src/main/resources/db/migration/V{当日}_{NNN}__actor_card_attachment_asset_binding.sql`

```sql
ALTER TABLE `actor_card`
  ADD COLUMN `attachment_asset_id` BIGINT DEFAULT NULL COMMENT '附件简历素材 id（步骤 6，指向 actor_media_asset）' AFTER `attachment_url`,
  ADD KEY `idx_actor_card_attachment_asset` (`attachment_asset_id`);
```

`attachment_url` 保留、停写，注释追加「已停写，退场见 00-110」。仓库内未见 Flyway 依赖，
迁移执行方式须按现行运维流程确认后再执行。

### 3.2 实体与 DTO

| 文件 | 改动 |
|---|---|
| `entity/ActorCard.java:56` | 新增 `attachmentAssetId`；`attachmentUrl` 注释标停写 |
| `dto/ActorCardStepSaveReqDTO.java:31` | 新增嵌套 `attachment`（见 §2.3）；`attachmentUrl` 标 `@Deprecated` |
| `dto/ActorCardRespDTO.java:24` | 新增 `attachmentAssetId` + 派生只读 `attachmentName` / `attachmentPageCount` / `attachmentStatus` |

派生字段由服务端 join 资产表填充，避免前端为渲染一张文件卡再发一次请求。

### 3.3 服务层

- `ActorCardDraftServiceImpl:60` — 用 §2.3 三态替换 `if (dto.getAttachmentUrl() != null)`。
  绑定前必须验权（见 §3.4）。
- `ActorCardDraftServiceImpl:187` — 响应填充改为 `attachmentAssetId` + 派生字段；
  历史 `attachment_url` 非空时仍回填，供删除。
- `ActorCardDraftServiceImpl:229-230` — 步骤 6 标签判据改为
  `attachmentAssetId != null || hasText(attachmentUrl)`。
- `ActorCardPublishService:125` — 完成度判据同上口径。

### 3.4 归属校验扩展

现有 `ActorMediaAssetOwnershipVerifier` 只有一个方法 `requireOwnedReadyPhoto`（`:4`）。
新增 `requireOwnedReadyPdf(Long userId, Long assetId)`，语义：归属当前用户 +
`mediaType == 'pdf'` + `processStatus == 'ready'`，否则抛既有 `PROFILE_ASSET_NOT_READY` /
`PROFILE_ASSET_NOT_FOUND`，不新造错误码。

### 3.5 页图读取接口

```
GET /api/actor/assets/{id}/pages  →  R<List<ActorAssetPageRespDTO>>
ActorAssetPageRespDTO { Integer pageNo; String accessUrl; Instant expiresAt; }
```

实现要点：`require(userId, assetId)` 验归属 → 拒非 `ready` → 按
`idx_actor_media_asset_page_order (asset_id, deleted, page_no)` 取活跃页 → 逐页
`storage.issueAccessUrl(bucket, imageObjectKey, Duration.ofMinutes(10))`。
上限沿用 20 页，无需分页。签名结果不缓存、不入库、不打日志。

## 4. 前端改动清单

### 4.1 `api/actor-card.ts`

`ActorCardDTO` 增 `attachmentAssetId: number | null` 与三个派生只读字段；
`attachmentUrl` 保留并标注仅供历史草稿删除。`saveStep` 入参类型支持嵌套 `attachment`。

### 4.2 `api/actor-asset.ts`

新增 `listActorAssetPages(assetId)` 对应 §3.5。上传/重试/签名三个既有函数直接复用，不改。

### 4.3 `pkg-actor-card/step-attachment/index.vue` 重构

状态：`assetId` / `assetName` / `pageCount` / `status` / `failureMessage` /
`uploading` / `pollAttempts` / `legacyUrl`。

模板三态：

1. **未上传** — 「选择 PDF 简历」按钮 + 约束说明「PDF 单份，≤20MB，≤20 页」。
   文案不得写「从手机选择」（`chooseMessageFile` 只能取会话内文件）。
2. **已上传** — 文件卡：文件名 / 页数 / 状态；操作「预览」「替换」「删除」。
   `processing` 显示处理中并轮询；`failed` 显示 `failureMessage` + 「重新上传」。
3. **历史遗留** — 仅 `legacyUrl` 非空且无 assetId 时出现，只提供「删除」，明示为历史数据。

交互要点：
- 取消选择不报错 —— 需从 `chooseMessageFile` 的 `fail` 中识别取消（`errMsg` 含 `cancel`），
  避免复刻 `pkg-profile/assets/index.vue:403-405` 把取消显示成错误横幅的问题。
- 轮询沿用参考实现的量级（2500ms、上限 24 次）并在 `onHide`/`onUnload` 停止。
- **重试后必须改绑新 assetId** —— `retry` 新建资产行，不改原行。
- 「下一步」不再提交附件字段（无变更语义）；「跳过」同理。清空只由「删除」触发。
- 草稿读取失败时阻断「下一步」，与 `00-213` T7/T8 的 store 层修复衔接，本页不自行兜底。

### 4.4 预览

新增预览态：调 `listActorAssetPages` → `<swiper>` 或纵向 `<image mode="widthFix">` 逐页渲染。
每次进入预览重新取地址，不缓存。

### 4.5 文案纠正

`pkg-actor-card/create/index.vue:70`「支持PDF、PPT、PPTX，最多1份」→ 与实际能力一致的 PDF 口径。

## 5. 回归门禁

沿用 `00-212`/`00-213` 既有脚本模式，新增断言组（须收集全部失败项后再非零退出，
且必须接入 `package.json`）：

1. `step-attachment/index.vue` 不含「暂未开放」「即将接入」类文案。
2. 该页确实引用 `uploadActorAsset` 与 `listActorAssetPages`。
3. 全仓不存在向 `saveStep` 提交 `attachmentUrl` 新值的调用点。
4. 「下一步」/「跳过」的提交体不含 `attachment` 键。
5. `create/index.vue` 不含 `PPT` / `PPTX` 字样。
6. 后端 `saveStep` 附件分支存在归属校验调用。
7. 断言须反向注入验证非空转（`00-211` 教训）。

## 6. 与其他 Spec 的边界

| Spec | 关系 |
|---|---|
| `00-213` T6 | 上传通道复用同一批 API。T6 管主视觉/生活照/剧照，本 Spec 管附件。**assetId 化的口径由本 Spec 先行落地**，T6 可沿用 §2.3 三态写法 |
| `00-213` T7/T8 | store 静默失败与 `saveStep` 守卫口径统一由 T7/T8 修；本 Spec 只落附件字段这一份，不重复实现 |
| `00-206` | G4 已知缺口登记须重写：原文「文件选择通道未接入」已过时（`uploadActorAsset` 与个人资料侧实现均已存在），真实缺口是「卡侧未复用既有 asset 通道 + 字段模型与 asset-id 模型不同构」 |
| `00-110` | `attachment_url` 停写后的物理退场归入删除门禁基线 |
| 生成/发布主线 | 附件进入已发布卡渲染的阻塞项是长页渲染占位与观看者页面缺失，须独立立项 |

## 7. 明确不做

- PPT / PPTX 支持。
- 个人资料侧 PDF 预览接线（本轮只把接口建出来）。
- 附件渲染进已发布演员卡。
- `attachment_url` 物理删除。
- `settingsJson` 服务端解析与 `showAttachment` 生效（无渲染方，先登记）。
