# 演员卡步骤 6 附件简历端到端接通 - 执行步骤

> 一次只做一个任务，做完停下等用户审核。
> 前置：`00-213` T5 尚未提交，T6/T7/T8 未开工。本 Spec 与 `00-213` 的边界见 `design.md` §6。

## 任务列表

### A1 数据库迁移与实体字段
新增 `attachment_asset_id` 迁移 + `ActorCard` 实体字段 + `attachment_url` 停写注释。
迁移执行方式须先确认（仓库无 Flyway 依赖），不得擅自在环境上跑。
**Validates: Requirements 4.1**

### A2 归属校验扩展
`ActorMediaAssetOwnershipVerifier` 增 `requireOwnedReadyPdf`，复用既有错误码。
补单测：非本人资产 / 非 pdf / 非 ready 三条拒绝路径。
**Validates: Requirements 4.1**

### A3 saveStep 三态语义与判据切换
`ActorCardStepSaveReqDTO` 嵌套 `attachment`；`ActorCardDraftServiceImpl:60` 改三态并验权；
`:187` 响应填充派生字段；`:229-230` 步骤标签与 `ActorCardPublishService:125` 完成度判据同步切换。
**漏改判据会导致步骤 6 永远显示「未添加」，这是本任务的主要风险点。**
**Validates: Requirements 4.1, 4.2**

### A4 页图读取接口
`GET /api/actor/assets/{id}/pages`，验归属、拒非 ready、逐页签发 10 分钟签名 URL。
**Validates: Requirements 4.5**

### A5 后端联调核验
真机 token 实测：上传 PDF → 绑定 → 回读派生字段 → 页图接口 → 越权用例（他人 assetId）→
清空语义（不传键 / 显式 null）。须先重新打包并确认运行态 jar 是新的（`00-213` 曾因三天前的旧
jar 误判 404）。
**Validates: Requirements 4.1, 4.2, 4.5**

### A6 前端 API 层
`api/actor-card.ts` 类型扩展；`api/actor-asset.ts` 新增 `listActorAssetPages`。
**Validates: Requirements 4.1**

### A7 step-attachment 页面重构
三态模板 + 选择/上传/轮询/重试/替换/删除 + 取消不报错 + 重试改绑新 assetId +
读取失败阻断下一步。
**Validates: Requirements 4.2, 4.3, 4.4**

### A8 预览
逐页渲染，每次进入重新签发地址，不缓存。
**Validates: Requirements 4.5**

### A9 文案纠正
`create/index.vue:70` 去掉 PPT/PPTX；步骤 6 约束说明按实际能力措辞，不写「从手机选择」。
**Validates: Requirements 4.3**

### A10 回归门禁脚本
7 组断言（`design.md` §5），收集全部失败项后非零退出，接入 `package.json`，反向注入验非空转。
**Validates: Requirements 4.1, 4.3**

### A11 构建与产物核验
`npm run build:mp-weixin`，`grep` 核对改动关键字进入 `dist/dev` 产物；跑包体审计确认分包未劣化。
**Validates: 非功能需求**

### A12 文档同步与缺口登记
`.sce/specs/README.md`、`spec-code-mapping.md`、`CURRENT_CONTEXT.md`；重写 `00-206` G4 登记；
登记两条显式缺口：`showAttachment` 无消费方、附件未进已发布卡渲染。
**Validates: Requirements 4.6**

## 执行约束

- **本 Spec 全程只在本地验证，不发布远端**（2026-08-10 用户裁决）。数据库迁移只走
  `DbMigrationRunner apply-local`（`127.0.0.1:3309/kaipai_dev`）。
- runbook 的 `run-backend-schema-migration.py` 默认 host 是 `101.43.57.62`、容器 `kaipai-mysql`，
  是**远端** SSH 执行器，本地容器为 `kaipai-mysql-local`，两者不可混用。
- 远端 schema 发布与后端发布均为独立动作，须用户另行下令；
  不得把「本地 DDL 已执行」当成「后端已发布」。

## 执行记录

### A1 已完成（本地）
- 新增 `V20260810_001__actor_card_attachment_asset_binding.sql`：`actor_card` 加
  `attachment_asset_id BIGINT` + `idx_actor_card_attachment_asset`。
- `ActorCard.attachmentUrl` 标 `@Deprecated` 停写只读，新增 `attachmentAssetId`。
- 经 `DbMigrationRunner apply-local` 应用到本地 dev 库，exit 0；已按远端 runner 的格式登记
  `schema_release_history`（`release_id=...-local-schema-00-214`，checksum 为文件 sha256），
  避免后续发布因本地脚本未登记而中止。
- 类型对齐：`attachment_asset_id` 与 `actor_media_asset.asset_id` 同为 `bigint`；
  `actor_card` 无显式 mapper XML，MyBatis-Plus 驼峰映射自动生效。
- 已知遗留：旧 `attachment_url` 列注释在库中是双重编码乱码（`C3A9E284A2` = `é™„`），
  本次新列注释为正确 UTF-8。纯元数据、不影响功能，未动。

### A2 已完成
- `ActorMediaAssetOwnershipVerifier` 新增 `requireOwnedReadyPdf`。**刻意不给 default 实现**：
  该接口原为单方法函数式接口，加抽象方法会让所有实现点编译失败，这正是想要的效果——
  新增素材类型时逼每个实现显式表态，而不是默认放行或默认抛错掩盖原因。
- `ActorMediaAssetServiceImpl`：photo/pdf 两个校验收敛到私有 `requireOwnedReady(userId,assetId,expectedMediaType)`，
  避免两份平行的类型判断日后漂移。
- 两处 lambda 实现改匿名类：`ActorMediaAssetOwnershipVerifierConfiguration`（兜底 bean，
  两个方法都抛 `PROFILE_ASSET_NOT_FOUND`）、`ProfileImportApplyMySqlIntegrationTest`（works_only 桩）。
- 错误码复用既有口径：不存在/非本人 → `46012 PROFILE_ASSET_NOT_FOUND`（不泄漏他人素材是否存在）；
  非 pdf / 非 ready → `46013 PROFILE_ASSET_NOT_READY`。
- 单测 4 条：加锁协议正常路径、他人素材越权、非 pdf、processing/failed 两种未就绪。
  `ActorMediaAssetServiceImplTest` 48 项全绿。
- 反向注入验证：把 pdf 校验错写成 photo，2 项断言失败，确认新断言非空转，已还原复跑绿。
- 连带回归：`ActorProfileWriteServiceImplTest` / `ActorProfileImportWriterTest` /
  `ActorMediaAssetControllerTest` 共 19 项全绿。

### A3 已完成
- `ActorCardStepSaveReqDTO` 新增嵌套 `attachment`（`AttachmentBinding{assetId}`），
  `attachmentUrl` 标 `@Deprecated`；服务端不再采纳其新值。
- `saveStep` 附件写入改三态：不传键 → 不动；`assetId != null` → 验权后绑定；
  `assetId == null` → 显式清空。旧 `if (getAttachmentUrl() != null)` 把「跳过提交空串」
  当成清空意图，是原缺陷来源，本次彻底移除。
- **判据没有在两处各改一遍**：抽出 `service/actor/support/ActorCardAttachmentCriterion.hasAttachment(card)`
  作为唯一判据，`ActorCardDraftServiceImpl`（步骤标签）与 `ActorCardPublishService`（完成度）共用。
  两处各写一份 `hasText(attachmentUrl)` 正是本缺陷的成因，判据只是实体状态的函数，
  不应存在两份。刻意没做成实体计算 getter，避免 Jackson / MyBatis-Plus 当成字段。
  口径：`attachmentAssetId != null || hasText(attachmentUrl)`，兼容老草稿的删除入口。
- **踩到一个只在运行时才炸的陷阱**：`requireOwnedReadyPdf` 是 `Propagation.MANDATORY`
  + `SELECT ... FOR UPDATE`，而 `saveStep` 原本无 `@Transactional`，直接调会抛
  `IllegalTransactionStateException`。已按另两个调用方
  （`ActorProfileWriteServiceImpl.saveMine` / `ActorProfileImportWriter.applyImport`）
  的同一口径给 `saveStep` 补 `@Transactional(rollbackFor = Exception.class)`。
- 清空时连历史 `attachmentUrl` 一起清：否则 `assetId` 清了、历史 URL 还在，
  判据仍为真，页面永远停在「已添加」且再也删不掉。
- 响应新增 `attachmentAssetId` + 派生只读 `attachmentName` / `attachmentPageCount` /
  `attachmentStatus`，服务端 join 资产表填充。查询按 `userId` 一起过滤，
  历史脏数据（卡上残留他人 assetId）不会把别人的文件名回读出去；
  素材已删除时派生字段留空、不抛错，避免整张卡读不出来。
- 测试 15 条（`ActorCardDraftServiceImplTest` 12 + `ActorCardPublishServiceTest` 3），
  此前这两个服务无任何测试。反向注入：把判据改回旧 `hasText(attachmentUrl)`，
  两个服务共 3 项失败，确认断言非空转，已还原。
- 全量套件 674 项全绿。

#### A3 遗留的过渡期缺口（A7 必须覆盖）
前端 `step-attachment/index.vue:47,51` 仍在提交 `attachmentUrl`，后端已停止采纳。
即从 A3 落地到 A7 落地之间，历史草稿的「删除」按钮实际失效
（前端只改本地 ref，后端忽略该字段）。A7 重构该页时连带修掉。

### A4 已完成
- 新增 `ActorAssetPageRespDTO`（`pageNo` + 10 分钟签名 `accessUrl` + `expiresAt`）。
- `ActorMediaAssetService` 接口新增 `listPages(userId, assetId)`。
- `ActorMediaAssetServiceImpl` 实现：校验归属（`require` 按 `userId` 过滤）、
  拒非 pdf（46013）、拒非 ready（46013）、查 `actor_media_asset_page` 按 `pageNo` 升序、
  逐页调 `storage.issueAccessUrl(bucketCode, imageObjectKey, Duration.ofMinutes(10))`。
- `ActorMediaAssetController` 新增 `GET /actor/assets/{id}/pages`，返回 `R<List<ActorAssetPageRespDTO>>`。
- 测试 2 条：正常路径（2 页 PDF，验证 pageNo 与签名 URL）、越权/非 pdf 拒绝、无页 PDF 返回空列表。
- 全量测试套件 676 项全绿（A3 新增的 2 项计入），BUILD SUCCESS。
- 已提交 `kaipaile-server` `9e7d0af`（误把 A4 的 DTO 文件算进 A3 提交，但功能完整）。
