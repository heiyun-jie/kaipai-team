# 演员卡步骤 6 附件简历端到端接通

## 1. 概述

演员卡向导步骤 6「附件简历」当前运行态为一句「暂未开放」的静态说明。该文案是 `00-213` T4 的
有意产出（见 `00-213/design.md:435`）：原实现点「添加附件」只弹 toast「文件选择即将接入」，
是一个点了会骗人的空控件（A7，已 CONFIRMED），故删控件、改为明示不可用。

本 Spec 的触发证据是用户追问「附件简历为什么未开放」，并裁决「创建 specs 把整个步骤都需要进行接通」。

审计后确认：**能力不缺，是演员卡侧从未接线，且现有字段模型无法承载该能力。**三条根因：

1. **`attachment_url` 这个字段模型在私有存储下不成立。** 素材存于腾讯云私有桶
   （`CosPrivateActorMediaStorage.getPrivateBucketName()`），唯一读取方式是
   `POST /api/actor/assets/{id}/access-url`，返回 **10 分钟** 有效的预签名 URL
   （`ActorMediaAssetServiceImpl.java:128`，`Duration.ofMinutes(10)`）。任何被写进
   `actor_card.attachment_url VARCHAR(1024)` 的地址 10 分钟后即失效。该字段不是「还没填」，
   是**填了也没用**。必须改为绑定 `asset_id`。
2. **`attachmentUrl` 目前没有任何消费方。** 全仓审计（前端 5 文件命中、后端 8 行命中）结果：
   写入只有 `ActorCardDraftServiceImpl.java:60`；读取只有 `step-attachment/index.vue:58` 自身回填，
   加两处布尔计数（`ActorCardDraftServiceImpl.java:229-230` 步骤标签、
   `ActorCardPublishService.java:125` 完成度 +1）。生成不读它
   （`ActorCardGenerateService.java:89-91` 仍是 `TODO`，预览图直接取主视觉 URL）、发布不带它
   （`toListItem` 映射 9 字段无附件）、`settingsJson` 里的 `showAttachment` 开关服务端从不解析。
   即「接通」不能只接上传口，否则仍是写进去没人看。
3. **需求文案本身失效。** `create/index.vue:70` 与 `00-206/requirements.md:191` 写「支持 PDF、PPT、PPTX」，
   后端只收 PDF：内容类型白名单 + 文件名后缀 + `%PDF-` 魔数三重校验、≤20MB、1–20 页、加密 PDF 拒收
   （`CosPrivateActorMediaStorage.java:29,87-104`、`ActorPrivatePdfProcessorImpl.java:35-37`）。
   PPT/PPTX 需要另一套转换器，本轮不做，文案须先纠正。

个人资料侧（`pkg-profile/assets/index.vue`）已有可用的 PDF 上传实现，是本轮的复用基线，
但它自身的「预览」也是假的（`:265-268` 取到签名 URL 后只弹一个说明弹窗就丢掉），不能整段照抄。

## 2. 范围边界

**在范围内**：步骤 6 在**卡主自己视角**下的全链路可用 —— 选择 → 上传 → 校验 → 绑定到演员卡 →
回读 → 预览 → 替换 → 删除，含失败可重试与状态可见。

**不在范围内**：把附件渲染进「已发布演员卡」。原因是运行态**根本不存在观看者视角的演员卡页面**
（`pages.json:46-72` 全量路由为 9 个向导页 + `pkg-card/verify` 实名认证页），且长页渲染引擎仍是
`ActorCardGenerateService.java:89-91` 的占位实现。这一段属于生成/发布主线，须独立立项，
本 Spec 只负责把数据备好并登记该缺口，不假装已闭环。

## 3. 用户故事

- 作为演员，我想在步骤 6 选一份 PDF 简历传上去，并且能看到它到底传成功了没有。
- 作为演员，我想在传完后翻看这份 PDF 的内容，确认我传的是对的那一份。
- 作为演员，我想替换或删除已传的附件，而不是只能重建整张卡。
- 作为演员，当我传的文件超限、格式不对或处理失败时，我想知道具体原因和下一步怎么办。
- 作为演员，当我只是想跳过这一步时，我不希望它悄悄把我上次传的附件清掉。

## 4. 功能需求

### 4.1 卡侧字段模型改为绑定 assetId

**描述**：`actor_card` 新增 `attachment_asset_id BIGINT`，指向 `actor_media_asset.asset_id`。
`attachment_url` 停止写入。私有桶签名 URL 只有 10 分钟寿命，持久化 URL 在架构上不可行。

**验收标准**：
- WHEN 步骤 6 保存附件 THEN 落库的是 `attachment_asset_id`，`attachment_url` 不再被写入新值。
- WHEN 读取草稿 THEN 响应带 `attachmentAssetId` 及派生只读字段 `attachmentName` /
  `attachmentPageCount` / `attachmentStatus`，前端无需二次请求即可渲染文件卡。
- WHEN 绑定的 assetId 不属于当前用户，或 `mediaType != 'pdf'`，或 `processStatus != 'ready'`
  THEN 拒绝保存并返回明确错误，不得静默落库。当前 `saveStep` 对 `attachmentUrl` 无任何校验，
  这是本轮必须补上的越权面。
- WHEN 历史草稿只有 `attachment_url` 无 `attachment_asset_id` THEN 步骤 6 仍能展示并删除该历史值，
  不得因改模型而丢掉历史数据的删除能力。

### 4.2 清空语义必须显式，且不得由跳过误触

**描述**：现有 `ActorCardDraftServiceImpl.java:60` 用 `if (dto.getAttachmentUrl() != null)`，
配合 `step-attachment/index.vue:47` 跳过时提交 `attachmentUrl: ''`，等于**跳过即清空**。
叠加 `00-213` D2（`reload` 静默失败使 `card` 为 `null`、回填全空）后会真实清零历史附件。

**验收标准**：
- WHEN 请求未携带附件字段 THEN 服务端不改动该字段（无变更语义）。
- WHEN 请求显式表达清空 THEN 才置空，且该意图必须来自用户点「删除」，不能来自点「下一步」或「跳过」。
- WHEN 草稿读取失败 THEN 步骤 6 的「下一步」必须被阻断，不允许以空值覆盖已存附件。
  该守卫口径与 `00-213` T7/T8 同源，本 Spec 只负责附件字段这一份，不重复实现 store 层修复。

### 4.3 文件选择与上传接通

**描述**：复用既有 `uploadActorAsset(filePath, 'pdf', 'resume')`（`api/actor-asset.ts:28`），
选择沿用 `uni.chooseMessageFile({ count: 1, type: 'file', extension: ['pdf'] })`。

**验收标准**：
- WHEN 用户点「选择 PDF 简历」THEN 拉起微信文件选择器，仅可选 PDF，单份。
- WHEN 用户取消选择 THEN 不得报错。`chooseMessageFile` 的 `fail` 回调把「取消」和「真失败」
  混在一起（参考实现 `pkg-profile/assets/index.vue:403-405` 即把取消显示为错误横幅），本轮须区分。
- WHEN 上传中 THEN 有明确进行中态，且按钮不可重复点击。
- WHEN 上传成功 THEN 立即展示文件名、页数、状态，并把 assetId 绑定到当前草稿。
- WHEN 文件超 20MB / 非 PDF / 加密 / 页数超 20 THEN 展示后端返回的具体原因，而不是笼统「上传失败」。
- WHEN 页面提示可选格式 THEN 文案只写 PDF。`create/index.vue:70` 的「支持PDF、PPT、PPTX，最多1份」
  与 `00-206/requirements.md:191` 须同步纠正为 PDF 单份 ≤20MB ≤20 页。

### 4.4 PDF 处理状态与失败重试

**描述**：后端 PDF 上传是同步转页图（`ActorMediaAssetServiceImpl.java:23-52`），
响应通常已是 `ready` 或 `failed`，但 `processing` 态在契约上存在，须可收敛。

**验收标准**：
- WHEN 资产处于 `processing` THEN 显示处理中并轮询至终态，不得无限轮询（须有次数上限）。
- WHEN 资产为 `failed` THEN 展示 `failureMessage`，并提供「重新上传」入口。
- WHEN 用户重试 THEN 走 `POST /api/actor/assets/{id}/retry`。注意该接口会**新建一条资产行**
  而非修正原行（`ActorMediaAssetServiceImpl.java:54` 委托回 `upload`），故重试成功后
  必须把草稿绑定改指向新 assetId，否则卡上仍挂着那条 failed 资产。
- WHEN 资产非 `ready` THEN 不允许绑定进演员卡。

### 4.5 附件可预览

**描述**：这是全链路里唯一两侧都缺的能力。个人资料侧对 PDF 只弹说明弹窗
（`pkg-profile/assets/index.vue:265-268`），签名 URL 取到即丢弃。PDF 已转好的页图存在
`actor_media_asset_page`（`imageObjectKey`），但**没有任何接口暴露它**。

**验收标准**：
- WHEN 用户点已上传的附件 THEN 能逐页看到该 PDF 的内容。
- WHEN 预览地址过期 THEN 重新签发，不得展示失效图。签名 URL 仅 10 分钟，不可持久化、不可缓存复用。
- WHEN 请求他人资产的页图 THEN 必须拒绝。

### 4.6 展示开关与消费缺口如实登记

**描述**：`step-settings/index.vue:52` 已有 `attachment` 开关，序列化为
`settingsJson.showAttachment`，但服务端从不解析 `settingsJson`，也没有渲染方读它。

**验收标准**：
- WHEN 本轮结束 THEN `showAttachment` 的真实状态（已存储、未被任何渲染方消费）必须在 Spec 与
  `00-206` 已知缺口表中如实登记，不得因步骤 6 可用就宣称展示开关生效。
- WHEN 本轮结束 THEN 「附件未进入已发布卡渲染」必须作为显式缺口留档，并指明其阻塞项是
  长页渲染引擎占位（`ActorCardGenerateService.java:89-91`）与观看者页面缺失。

## 5. 非功能需求

- 私有桶签名 URL 一律现取现用，不落库、不写缓存、不进日志。
- 越权面收口：凡接受 assetId 的写入路径都必须验归属，不能依赖前端只传自己的 id。
- 复用既有 `uploadActorAsset` / `retryActorPdfAsset` / `requestAssetAccessUrl`，不新造上传通道。
- 主包体积：步骤 6 属 `pkg-actor-card` 分包，本轮不得把新增逻辑写进主包。

## 6. 约束条件

- 只用 PDF。PPT/PPTX 需新转换器，明确不在本轮。
- `uni.chooseMessageFile` 只能选**微信会话里已有的文件**，无法浏览手机文件系统。这是平台限制，
  文案须据此措辞（不能写「从手机选择」），并作为已知体验约束留档。
- 不改 `pages.json` 路由。
- 数据库变更走 `src/main/resources/db/migration/V{yyyyMMdd}_{NNN}__{name}.sql`；仓库内未见 Flyway
  依赖，迁移执行方式须按现行运维流程确认，不得假设自动执行。
- `attachment_url` 本轮只停写、不物理删除，退场归 `00-110` 门禁基线。
