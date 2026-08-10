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
