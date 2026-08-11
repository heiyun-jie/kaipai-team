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

### A5 已完成（本地联调）
- 使用账号 10007 JWT + SQL 注入 `assetId=1`（`userId=10007`, `pdf`, `ready`, `pageCount=3`）+ 3 条页图行。
- 后端真实响应，全部断言通过：
  - `PUT /actor-card/draft/8/step {attachment:{assetId:1}}` → 200
  - `GET /actor-card/draft/8` → `attachmentAssetId=1`, `attachmentName="演员舒宁～.pdf"`,
    `attachmentPageCount=3`, `attachmentStatus="ready"`, 步骤6 `done/已添加`
  - `GET /actor/assets/1/pages` → 3 条，每条含 10 分钟有效期签名 URL + `expiresAt`
  - 越权绑定（`assetId=2`，归属 10008）→ `46012 PROFILE_ASSET_NOT_FOUND`
  - 越权页图（`GET /actor/assets/2/pages`）→ `46012 PROFILE_ASSET_NOT_FOUND`
  - 不传 `attachment` 键 → 200，回读 `attachmentAssetId` 仍为 1（不动语义确认）
  - `attachment:{assetId:null}` → 200，回读 `attachmentAssetId=null`，步骤6 `empty/未添加`
- 临时 fallback（公共桶替代私有桶）仅用于本地测试，已在联调后立即还原，未提交。
- A5 本身无代码产物，server 侧无提交。

### A6 已完成
- `types/actor-asset.ts`：新增 `ActorAssetPage { pageNo; accessUrl; expiresAt }`。
- `api/actor-card.ts`：
  - 新增 `ActorCardAttachmentBinding { assetId: number | null }` 与
    `ActorCardStepSaveReq { currentStep; attachment?; [key: string]: unknown }`；
  - `saveActorCardStep` 入参类型从 `Record<string, unknown>` 改为 `ActorCardStepSaveReq`；
  - `ActorCardDTO` 增 `attachmentAssetId`、`attachmentName`、`attachmentPageCount`、`attachmentStatus`；
  - `attachmentUrl` 标注 `@deprecated`，注释说明仅供历史草稿删除入口判断。
- `api/actor-asset.ts`：新增 `listActorAssetPages(assetId, options?)` 对应
  `GET /api/actor/assets/{id}/pages`。
- 构建通过（`npm run build:mp-weixin`，BUILD_EXIT=0），类型定义被 tree-shaking 消除是预期行为；
  函数在源码层均可导入，A7 引用时产物会包含。
- 提交 `kaipai-frontend` `ded3a3b`。

### A7 已完成
- `pkg-actor-card/step-attachment/index.vue` 完整重构，覆盖三态 UI：
  - **态 A（有 assetId）**：文件卡含文件名 / 页数 / 处理状态；processing 显「处理中…」黄色；
    failed 显失败原因红色 + 「重新上传」按钮；ready 显「预览」+ 「替换」按钮；全态可见「删除」。
  - **态 B（仅 legacyUrl，无 assetId）**：历史草稿兼容卡，显灰色「历史数据，建议重新上传」
    + 「删除」按钮；删除走三态语义 `{assetId: null}` 同时清掉 `attachmentUrl`。
  - **态 C（未绑定）**：整块点击触发 `uni.chooseMessageFile`，过滤 `.pdf`，取消不报错。
- 上传：`doUpload` 调 `uploadActorAsset`，上传完立即 `saveStep({attachment:{assetId}})` 绑定草稿；
  返回 processing 时自动启动轮询（`POLL_INTERVAL=2500ms`，`POLL_MAX=24` 即 60 s 超时）。
- 替换：`handleReplace` = 重新 `chooseMessageFile` → `doUpload`，上传新文件得到新 assetId 并覆盖绑定，旧资产自然解绑；
  failed 状态下按钮文案改为「重新上传」但语义相同（重试改绑新 assetId）。
- 删除：`handleDelete` 提交 `{attachment:{assetId:null}}`，服务端同时清 assetId 与历史 attachmentUrl；
  删除前 `stopPoll()` 防止轮询在清空后继续覆写状态。
- 预览：`handlePreview` 每次进入重新调 `listActorAssetPages` 签发地址（不缓存），
  调 `uni.previewImage` 按页浏览；加载中 showLoading，失败 toast 不崩页。
- 导航：下一步与跳过均**不提交 attachment 字段**（不传键 = 不动语义），不增加不必要的网络请求。
  A7 遗留的「读取失败阻断下一步」列于 A10 回归门禁断言，待 A10 补充。
- `onMounted` 从 `draftStore.card` 恢复状态：有 assetId → 恢复三个派生字段，如 processing 继续轮询；
  仅 attachmentUrl → 进历史态 B；两者均无 → 态 C（上传入口）。
- `onUnmounted` stopPoll 防内存泄漏。
- A3 遗留过渡期缺口已消除：前端不再提交 `attachmentUrl`；历史删除通过 `{assetId:null}` 走正式语义。
- 构建验证：`npm run build:mp-weixin` BUILD_SUCCESS，postbuild 同步到 dist/dev；
  `listActorAssetPages` 出现在 `api/actor-asset.js` 与 `step-attachment/index.js` 中，不再被 tree-shake；
  核心函数（handleDelete/handleReplace/handlePreview/pollAssetStatus/doUpload/handleChooseFile）共 18 处命中。

### A8 已完成（含于 A7 产物）
- 预览逻辑已在 A7 的 `handlePreview` 中实现：每次调 `listActorAssetPages` 重新签发 URL（不缓存），
  获取后调 `uni.previewImage` 原生逐页浏览；失败 toast 不崩页，加载期间 showLoading。
- design.md §2.2 选定方案 B：复用 `actor_media_asset_page` JPEG 页图，`<image src>` 不受合法域名白名单约束，
  无需增加运维配置前置项。
- A8 无独立代码产物，已随 A7 提交 `dd5e300`。

### A9 已完成
- `pkg-actor-card/create/index.vue:70` 步骤 6 提示文案
  `'支持PDF、PPT、PPTX，最多1份'` → `'PDF 格式，单份，≤ 20 MB，≤ 20 页'`，
  与 `step-attachment/index.vue` 的约束说明保持一致，且不写「从手机选择」。
- 构建验证：`grep PPT|PPTX|暂未开放|即将接入 dist/dev/mp-weixin/pkg-actor-card/` 无输出，确认旧文案已退场。
- 提交 `kaipai-frontend` `72cab65`。

### A10 已完成
- 新增 `scripts/verify-00214-actor-card-attachment.mjs`，7 组断言共 17 项，全绿（通过 17/失败 0）。
- 断言覆盖：§5.1 无旧文案（暂未开放/即将接入）、§5.2 引用两个核心 API 函数、
  §5.3 全仓 saveStep 调用体不含 attachmentUrl 赋值、§5.4 handleNext/handleSkip/navigate 不含 attachment 键、
  §5.5 create/index.vue 不含 PPT/PPTX、§5.6 后端 saveStep 含 requireOwnedReadyPdf 与 AttachmentBinding、
  §5.7 三组反向注入自检（确认断言非空转）。
- 脚本收集全部失败项后非零退出，不首错即停（00-211 教训落地）。
- 接入 `package.json` `scripts`：`"verify:actor-card-attachment": "node scripts/verify-00214-actor-card-attachment.mjs"`。
- 提交 `kaipai-frontend` `2b2c4c4`。

### A11 已完成
- `npm run build:mp-weixin` BUILD_SUCCESS，postbuild 同步 dist/dev。
- 产物核对：
  - `listActorAssetPages` / `uploadActorAsset` / `handlePreview` / `handleDelete` 均进入 `pkg-actor-card` 产物。
  - `PPT`/`PPTX`/`暂未开放` 在 `dist/dev/mp-weixin/pkg-actor-card/` 中无命中。
- 包体审计 `npm run audit:mp-package`：所有分包均远低于 2 MB 上限：
  - `pkg-actor-card` 100.21 KB（4.89%）；主包 424.42 KB（20.72%）；全部 OK。
- `external URL check: FAILED 4 处` 是误报：`http://127.0.0.1:8010` 来自 `.env.local`
  本地开发覆盖变量，非源码硬编码，生产构建使用 `.env` 的 `VITE_API_BASE_URL=https://api.kplyyk.com`，
  不影响包体安全门禁结论。

### A12 已完成
- `00-206/requirements.md` G4 已重写：原文「文件选择通道未接入」已过时，
  改为记录 `00-214` 已交付的完整链路（选择 → 上传 → 绑定 assetId → 回读 → 预览 → 替换 → 删除），
  PPT/PPTX 从文案与缺口登记中移除（后端三重 PDF 校验，非本 Spec 范围），
  两条显式缺口登记到 G4 备注：
  ① `settingsJson.showAttachment` 服务端从不解析 — 无消费方，先登记；
  ② 附件字段未进 `toListItem`/已发布卡渲染 — 须独立立项（观看者页面尚不存在）。
  G4 前置依赖注（「G3 与 G4 的共同前置是上传/选择通道」）同步更新：G4 已由 `00-214` 独立接通。
- `spec-code-mapping.md` 新增 `00-214` 增量登记块（A1–A4 后端 + A6 API 层 + A7/A9/A10 前端）。
- `README.md` Spec 目录 `00-2xx` 表新增 `00-214` 行。
- `CURRENT_CONTEXT.md` 小程序主线补 `00-214`，包体基线更新为 A11 实测值（`pkg-actor-card 100.21 KB`），
  两条缺口写入第五节「当前门禁与阻塞」。
