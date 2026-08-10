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

## 执行记录

（按任务追加）
