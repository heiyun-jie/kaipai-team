# 演员卡素材库与创建向导接通 - 任务清单

_Requirements: ALL_
_Design: ALL_

> 状态：T0-T5 已完成；当前下一项为 T6 构建、运行态与发布准备。每次完成一个任务后回填证据。

## T0 决策与基线

- [x] **Validates: Requirements 1, 2, 6** 用户已于 2026-08-18 确认 00-221 T0-3 中素材库选择与排序纳入本批次；帮助 / 设置 / 真实长图生成仍不在本 Spec。
- [x] **Validates: Requirements 4.3, 5** 盘点现有 `actor_card`、`actor_card_work`、`actor_media_asset`、附件 assetId 和旧 URL 数据，输出旧数据回退样本。

## T1 后端素材绑定基础

- [x] **Validates: Requirements 4.3, 4.4** 新增幂等 `actor_card_media_set` / `actor_card_media_item` 迁移，补索引、审计字段和空集合语义。
- [x] **Validates: Requirements 4.3** 新增实体、Mapper、DTO 和服务层，支持用途、作品范围、assetId / legacy URL 回退和排序。
- [x] **Validates: Requirements 4.2, 4.3** 增加批量归属 / 类型 / ready 校验，拒绝重复 asset、越权 asset 和超出用途上限的提交。
- [x] **Validates: Requirements 4.5** 扩展素材删除引用检查，覆盖绑定集合和 `attachment_asset_id`，保留既有错误码。

## T2 草稿 API 与兼容读取

- [x] **Validates: Requirements 4.3, 4.4** 实现草稿素材集合 GET / PUT，支持完整替换、空集合、排序、现签预览地址和回读。
- [x] **Validates: Requirements 4.3** 扩展 `replaceWorks` 的 `stillAssetIds` / `stillItems` 可选合同，旧 `stills` URL 合同保持可用。
- [x] **Validates: Requirements 4.5** 扩展复制创建，复制集合、item、作品映射和附件绑定并保持顺序。
- [x] **Validates: Requirements 4.5** 公开观看按新绑定集合现签资源，旧 URL 卡按回退路径继续返回原字段。
- [x] **Validates: Requirements 4.2** 扩图 API 增加 `sourceAssetId`，服务端现签给 AI provider；旧 `sourceImageUrl` 入参继续兼容。

## T3 选择模式与素材库写入

- [x] **Validates: Requirements 4.1** 在 `pkg-profile/assets/index` 增加 `card-select` 模式、媒体 / 分类过滤、多选上限和选择确认。
- [x] **Validates: Requirements 4.1, 5** 将 `asset-selection` store 改为 requestId 会话，补确认、取消、返回和 unload 清理。
- [x] **Validates: Requirements 4.2** 将选择页新上传统一接入 `uploadActorAsset`，上传结果进入当前选择会话，不直接写演员卡 URL。
- [x] **Validates: Requirements 4.6** 选择模式视觉迁移到 3.0 Token，补空态、处理中、失败重试、预览和安全区。

## T4 向导五类资源接线

- [x] **Validates: Requirements 4.2, 4.3, 4.4** `step-visual` 接通主视觉素材选择 / 上传 / 绑定 / 扩图 / 回读。
- [x] **Validates: Requirements 4.2, 4.3, 4.4** `step-works` 接通剧照素材选择 / 上传 / 替换 / 删除 / 排序 / 封面回读。
- [x] **Validates: Requirements 4.2, 4.3, 4.4** `step-photos` 接通素材库多选、手机上传入库、删除、排序、上限和回读。
- [x] **Validates: Requirements 4.2, 4.3, 4.4** `step-video` 接通视频选择 / 上传 / 预览 / 替换 / 删除 / 跳过和回读。
- [x] **Validates: Requirements 4.2, 4.3, 4.4** `step-attachment` 在 00-214 基础上增加素材库 PDF 选择，保持三态绑定、预览、重试和删除语义。
- [x] **Validates: Requirements 4.4, 4.6** 五个页面保存后统一 `draftStore.reload()`，失败阻断下一步，安全区和重复点击锁定一致。

## T5 门禁与后端测试

- [x] **Validates: Requirements 4.1-4.6** 新增并接入 `verify:v3-asset-wizard`，覆盖正向合同和反向注入自检。
- [x] **Validates: Requirements 4.3, 4.5** 完成后端绑定、归属、类型、排序、旧 URL 回退、复制隔离和删除引用测试。
- [x] **Validates: Requirements 5** migration 通过空库、已有库、重复执行和缺表防御验证；不执行远端生产迁移。
- [x] **Validates: Requirements 4.6** 复跑 `type-check`、既有 00-221 门禁、`verify:nav-title`、`verify:actor-card-attachment` 和 legacy 色彩门禁。

## T6 构建、运行态与发布准备

- [ ] **Validates: Requirements 4.6, 5** 关闭微信开发者工具后构建，核对 `src`、`dist/build/mp-weixin`、`dist/dev/mp-weixin` 和 scoped hash 三件套。
- [ ] **Validates: Requirements 4.1-4.4** 采集素材库管理页、选择页、主视觉、作品、生活照片、视频、附件七个页面的空 / 成功 / 失败 / 回读截图和点击证据。
- [ ] **Validates: Requirements 4.5, 5** 验证旧 URL 草稿、新绑定草稿、复制创建、公开观看、删除被引用素材和多设备排序。
- [ ] **Validates: Requirements 4.5, 6** 在 T1-T5 和本地运行态闭环后完成发版兼容评估：迁移编号、生产预置、旧客户端字段、发布顺序、回滚和删除引用策略。
- [ ] **Validates: Requirements 4.5** 执行 `build:mp-weixin:release` 和 `audit:mp-package`，记录开发 URL 与生产 URL 审计结果。
- [ ] **Validates: Requirements 5, 6** 回填 `CURRENT_CONTEXT.md`、`spec-code-mapping.md`、`docs/product-design.md` 和本 Spec，确认前后端同批次发布条件。

## 完成定义

本 Spec 只有在 T0-T6 全部关闭、素材管理与选择模式运行态证据齐全、旧 URL 与新 assetId 数据均可读、迁移和发布兼容检查通过后，才能宣称“素材库已与创建流程完整打通”。仅完成选择页、上传或静态构建，不等同于完成。

## 执行记录

### 2026-08-18：T0 当前数据基线

- 已完成本地 `kaipai_dev` 聚合只读盘点，证据见 `status/current-data-baseline.md`；临时启动的 `kaipai-mysql-local` 已恢复为 `exited`，未连接生产库、未执行 migration、未修改业务数据。
- 有效演员卡 `10`（草稿 `9` / 已发布 `1`），未软删除作品行 `5`（其中 `1` 行父卡已软删除），有效素材 `4`；素材全部为 `pdf / resume / ready`，photo / video 均为 `0`。
- 旧 URL 仍覆盖主视觉、扩图、生活照与作品剧照；附件已有 `5` 张卡绑定 `2` 个不同 assetId，另有纯 URL、URL + assetId 混合和空卡回退样本。
- 发现并登记两个实现门禁：`1` 条未软删除作品行的父卡已软删除；现有素材删除检查未覆盖 `actor_card.attachment_asset_id`，当前 `2` 个被演员卡引用的附件素材均可绕过既有引用检查。
- 本轮只关闭数据盘点任务；T1 migration 与全部实现任务仍未开始。

### 2026-08-18：执行顺序纠正

- 用户明确裁决“开发还没有闭环，不要先做发布基线”。已撤回提前生成的 `status/release-compatibility.md`。
- 发版兼容评估移至 T6：只有 T1-T5 和本地运行态闭环后才执行，不再占用当前开发阶段。
- 当前下一项恢复为 T1 绑定表 migration；未执行本地或生产 migration，未连接生产库。

### 2026-08-18：T1 绑定表 migration

- 新增 `kaipaile-server/src/main/resources/db/migration/V20260818_001__actor_card_media_binding.sql`。
- 新增 `actor_card_media_set`：卡片 / 作品范围、用途白名单、软删除和审计字段；作品用途必须带 `card_work_id`，其他用途禁止带作品范围。
- 新增 `actor_card_media_item`：`asset_id` / `legacy_url` 二选一、顺序、软删除和审计字段；active asset 通过 generated column + unique index 防止同集合重复绑定。
- migration 仅使用 `CREATE TABLE IF NOT EXISTS`，不删除旧 URL 字段、不写入签名 URL、不改变 00-214 附件字段。
- 新增 `ActorCardMediaBindingSchemaMigrationTest`，临时 MySQL 8 验证表、生成列、索引、约束、无 destructive DDL 和 runner 语句格式；`mvn -q -Dtest=ActorCardMediaBindingSchemaMigrationTest test` 通过。
- 本轮未执行本地 `kaipai_dev` migration；迁移也未执行到生产环境。

### 2026-08-18：T1 后端素材绑定基础

- 新增 `ActorCardMediaSet` / `ActorCardMediaItem` 实体与 Mapper；写入事务先锁定所属草稿，再按 `cardId + workId + usage` 查询集合，避免 `NULL` 唯一索引语义造成并发重复集合。
- 新增素材绑定请求 / 响应 DTO 和 `ActorCardMediaBindingService`：支持 `source_image`、`work_still`、`life_photo`、`video_resume`，分别限制 1 / 3 / 12 / 1 个素材，并校验排序从 0 连续、无重复 asset。
- 写入前批量锁定素材，统一校验当前用户归属、媒体类型和 `ready` 状态；他人或不存在素材继续返回 `PROFILE_ASSET_NOT_FOUND`，类型或状态不符返回 `PROFILE_ASSET_NOT_READY`。
- 读取时 active 集合优先；集合不存在才从 `source_image_url`、`photos_json`、`video_url`、`stills_json` 生成只读 legacy 条目；active 空集合会抑制旧 URL 回退，避免删除后复活。
- `ActorMediaAssetService.delete` 已增加 `actor_card.attachment_asset_id` 与 `actor_card_media_item.asset_id` 引用检查，继续复用 `PROFILE_ASSET_IN_USE`，关闭当前 2 个附件素材可绕过删除检查的风险。
- 验证：`ActorCardMediaBindingServiceImplTest` 6 组通过；`ActorMediaAssetServiceImplTest` 含新增附件 / 绑定引用删除测试通过；`ActorCardMediaBindingSchemaMigrationTest` 通过；`mvn -q -DskipTests compile` 通过。
- 当前下一项为 T2 GET / PUT 草稿素材集合 API；本阶段仍未执行本地或生产 migration，也未修改前端。

### 2026-08-18：T2 草稿 API 与兼容读取

- 新增 `GET /actor-card/draft/{cardId}/media?usage=&workId=` 与同路径 PUT；PUT 只接受 `assetId + sortOrder`，支持完整替换和 active 空集合，响应为当前所有者现签 `previewUrl / expiresAt`。
- `replaceWorks` 增加可选 `stillAssetIds`，新合同在创建作品行后同事务写入 `work_still` 集合；旧客户端只传 `stills` URL 继续可用，响应新增 `stillItems` 并继续回填旧 `stills` 字段。
- 替换作品前清理旧作品的 active 集合和 item，避免逻辑删除作品留下永久素材引用；作品集合按新作品 id 创建。
- 复制演员卡时复制 active 集合和 item，作品剧照通过 old work id -> new work id 映射重绑；素材实体不复制、排序保持不变。
- 公开观看的主视觉、作品剧照、生活照片和视频优先消费 active 绑定并现签；无集合时由绑定服务回退旧 URL，原公开响应字段结构不变。
- 扩图请求增加可选 `sourceAssetId`：服务端验证 owned / photo / ready 后现签给 provider；签名 URL 只保留在本次异步调用内，不写入任务表；旧 `sourceImageUrl` 请求继续兼容。
- 验证：绑定 service/controller、作品替换、公开读取/复制、扩图、素材删除相关测试全部通过；`mvn -q -DskipTests test-compile` 与 `git diff --check` 通过。
- 仍未执行本地 `kaipai_dev` 或生产 migration；当前下一项为 T3 `pkg-profile/assets` 的 `card-select` 模式与 requestId 会话。

### 2026-08-18：T3 选择模式与素材库写入

- `asset-selection` store 新增 requestId 会话：`begin / get / complete / consume / cancel`，请求与结果深拷贝隔离；保留既有头像和作品选择 API，避免破坏旧入口。
- `pkg-profile/assets/index` 新增 `mode=card-select&requestId=...`：会话控制标题、固定媒体类型、允许分类、默认分类、单选 / 多选上限与初始已选项。
- 选择页新增分类筛选、选中态和固定底部“确认选择 x / n”操作栏；确认保留结果供父页一次性消费，取消、返回、无效会话和未完成 unload 均清理当前 requestId。
- 新上传继续统一使用 `uploadActorAsset`；ready 素材立即加入当前选择，processing 素材轮询到 ready 后加入，未把签名 URL 或 `wxfile://` 写进选择结果。
- 视觉锚点保持为现有 3.0 素材列表，只新增筛选条、单列媒体 Tab 和安全区确认栏；头像 / 作品旧模式和普通管理模式未改结构。
- 验证：`npm run type-check`、`npm run build:mp-weixin` 通过；postbuild 报告 build/dev scoped hash 均一致；`pkg-profile/assets` build/dev 的 WXML/WXSS/JS SHA256 分别相同，`card-select` / requestId / 确认栏 / 筛选样式双侧均存在。
- 回归：`verify:nav-title` 101/101、`verify:actor-card-attachment` 17/17、`verify:v3-ui-legacy-colors` 通过。当前下一项为 T4 五类向导页面接入新选择会话和草稿 media GET / PUT。

### 2026-08-18：本地 Docker migration 验证

- 已确认本地数据库运行于 Docker 容器 `kaipai-mysql-local`（MySQL `8.0.44`），宿主端口 `3309`，目标库为 `kaipai_dev`；迁移前容器为 `exited`，验证结束后已恢复为 `exited (0)`。
- 已通过 `DbMigrationRunner apply-local V20260818_001__actor_card_media_binding.sql` 执行本地 migration，并在同一已有库再次执行；两次均完成 2 条 `CREATE TABLE IF NOT EXISTS` 语句，重复执行无报错、无副作用。
- 已从 `information_schema` 核实 `actor_card_media_set` / `actor_card_media_item` 均为 InnoDB + `utf8mb4_0900_ai_ci`；3 个 CHECK、`uk_actor_card_media_item_active_asset` 唯一索引、排序 / 引用索引和 `active_asset_id` STORED generated column 均存在。
- 本轮只操作 `127.0.0.1:3309/kaipai_dev`；未调用远端 `apply`，未连接或修改生产数据库。生产仍须在 T6 发版准备阶段经用户明确授权后按“migration → 后端 → 前端”顺序执行。

### 2026-08-18：T4 五类向导资源接线

- `src/api/actor-card.ts` 已补草稿 media GET / PUT、素材绑定响应类型、作品 `stillAssetIds / stillItems` 和扩图 `sourceAssetId` 合同；`pkg-actor-card/utils/card-asset.ts` 只在页面内现取预览地址，绑定请求仍只提交 `assetId + sortOrder`。
- `step-visual` 已支持素材库 / 手机上传两入口，上传先进入 `actor_media_asset`，选择后立即绑定 `source_image`；AI 扩图优先提交 `sourceAssetId`，旧 URL 草稿继续提交 `sourceImageUrl`。主视觉 asset 变化会在后端同事务清理旧扩图，避免新首图与旧扩图串用。
- `step-works` 已支持每部作品最多 3 张素材剧照、手机上传入库、素材库整组选取、替换、删除、上移 / 下移和首张封面；保存通过 `replaceWorks.stillAssetIds` 同事务重建作品与绑定，历史 URL 剧照未编辑时继续走旧合同。
- `step-photos` 已支持素材库多选和 `photo / lifestyle` 手机上传，严格限制 12 张；删除与上移 / 下移提交连续 `sortOrder`。`step-video` 已支持 `video / self_intro` 选择、上传、预览、替换、删除和空集合抑制旧 URL。
- `step-attachment` 在 00-214 三态基础上增加 ready PDF 素材库单选；手机上传、素材库绑定、删除和下一步均改为显式 `saveActorCardStep + draftStore.reload()`，不改变“跳过不清空、删除才清空”的合同。
- 五页均使用 requestId 会话并在确认、取消、导航失败和 unload 路径清理；读取 / 保存 / 回读失败会保留当前页面并阻断下一步，上传、绑定、保存和导航期间锁定重复动作。
- 后端草稿步骤 1 / 4 / 5 已改为按有效 binding 集合派生完成态，active 空集合压住旧 URL；生成门禁接受 owned source asset，但不把签名预览写入任务表，migration 缺失时旧 URL 生成合同继续降级可用。
- 验证：前端 `type-check`、`build:mp-weixin`、`verify:nav-title` 101/101、`verify:actor-card-attachment` 17/17、`verify:v3-step-works` 12/12、`verify:v3-step-photos` 11/11、legacy 色彩门禁均通过；后端草稿 / 绑定 / 生成 / 扩图专项测试通过。
- 产物：五个向导页的 WXML / WXSS / JS 在 `dist/build/mp-weixin` 与 `dist/dev/mp-weixin` 逐文件 SHA256 一致；素材选择页 build/dev 的 scoped hash 均为 `data-v-9cde29e0` 且 WXML / WXSS / JS 三件套一致。
- 发版兼容：本地 Docker migration 已执行；生产 migration、后端发布和小程序发布均未执行。当前下一项为 T5 `verify:v3-asset-wizard`、反向注入自检和后端测试矩阵收口，运行态截图与发布评估仍在 T6。

### 2026-08-18：T5 门禁与后端测试

- 新增并接入 `npm run verify:v3-asset-wizard`：68 项正向合同断言覆盖 requestId 选择会话、五种 usage 的媒体类型 / 分类 / 上限 / 上传、assetId + `sortOrder` 写入、回读阻断、公开读取 / 复制 / 删除引用和幂等 migration；脚本收集全部失败后非零退出。
- 反向注入不写工作区文件，直接在内存替换错误媒体类型、移除 `sortOrder`、向绑定请求注入 `previewUrl`、移除取消清理；四种变异均会命中指定断言，证明门禁非空转。
- 补充 `ActorCardMediaBindingServiceImplTest`：不存在或他人 asset 返回非泄漏 `46012`、`processing` asset 返回 `46013`、非连续排序和超过 12 张均在加锁写入前拒绝；复制测试确认新 item 未复用源 item 身份并保持排序。
- 补充 `ActorCardDraftServiceImplTest`：绑定表缺失时 `BadSqlGrammarException` 被降级为旧 URL 步骤状态，旧客户端读取不白屏。专项后端矩阵（schema / binding / draft / public / asset delete / generate / expand / controller）通过。
- 空库：`ActorCardMediaBindingSchemaMigrationTest` 通过 Testcontainers `mysql:8.0.36` 建表与生成列 / 索引核验。已有库与重复执行：仅对本地 Docker `kaipai-mysql-local` 的 `kaipai_dev` 执行 `apply-local V20260818_001__actor_card_media_binding.sql` 两次，均成功；`information_schema` 核实 InnoDB、`utf8mb4_0900_ai_ci`、3 个 CHECK、5 个目标索引与 `active_asset_id` STORED GENERATED。容器已恢复为停止状态；未连接、未修改远端生产库。
- 前端回归通过：`type-check`、`verify:v3-asset-wizard`（68/68）、`verify:nav-title`（101/101）、`verify:actor-card-attachment`（17/17）、`verify:v3-step-works`（12/12）、`verify:v3-step-photos`（11/11）、`verify:v3-ui-legacy-colors`。`build:mp-weixin` 通过，素材选择页及五个向导页的 WXML / WXSS / JS 在 `dist/build` 和 `dist/dev` SHA256 逐文件一致，scoped hash 集合一致。
