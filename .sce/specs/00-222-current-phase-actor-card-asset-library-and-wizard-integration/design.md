# 演员卡素材库与创建向导接通 - 技术设计

_Requirements: 4.1-4.6, 5, 6_

## 1. 设计原则与边界

1. **素材库是用户资源事实源**：上传、分类、处理状态和原始文件由 `actor_media_asset` 维护。
2. **演员卡是展示绑定事实源**：卡片只记录“哪个 asset 用于哪个用途、顺序是什么”，不复制签名 URL。
3. **旧 URL 是兼容回退，不是新数据入口**：旧字段继续读取和接受旧客户端写入，但新客户端不再把私有素材签名地址写进 URL 字段。
4. **选择页和管理页分离**：原生 Tab 只管理素材；带 query 的分包页只负责选择和返回，避免破坏 Tab 状态。
5. **完整替换优先于增量猜测**：生活照片和剧照使用当前完整列表提交，后端事务内替换该用途绑定集合，避免删除 / 排序状态漂移。
6. **服务端决定可用性**：所有 assetId 必须检查用户归属、媒体类型、处理状态和用途限制，前端状态不能作为安全边界。

## 2. 页面与选择会话

### 2.1 管理页

继续使用 `pages/assets/index` 作为四项 Tab 中的 `assets` 根页。它不接受创建上下文，不持有卡片绑定状态，只操作用户素材：

- `mediaType`: `photo | video | pdf`。
- `categoryCode`: 复用后端正式分类：照片 `portrait_candidate | model_card | portrait | lifestyle | production | costume | other`；视频 `self_intro | work_clip | performance_clip | other`；PDF `resume`。
- `processStatus`: `uploading | processing | ready | failed`。
- 预览：图片使用现取 `access-url`，视频进入既有播放器，PDF 使用已有页图接口。

### 2.2 选择模式

继续使用 `pkg-profile/assets/index`，新增 `mode=card-select`，不新增路由。

选择上下文由 `requestId` 在 `asset-selection` Pinia store 中隔离：

```ts
interface CardAssetSelectionRequest {
  requestId: string;
  usage: 'source_image' | 'work_still' | 'life_photo' | 'video_resume' | 'attachment';
  mediaType: 'photo' | 'video' | 'pdf';
  multiple: boolean;
  maxCount: number;
  workId?: number;
  selectedAssetIds: number[];
}

interface CardAssetSelectionItem {
  assetId: number;
  mediaType: 'photo' | 'video' | 'pdf';
  categoryCode: string | null;
  originalName: string;
  processStatus: 'ready' | 'processing' | 'failed';
  sortOrder: number;
}
```

进入选择页前创建会话；确认时写入结果并回退；父页只消费一次并清理会话。选择结果不包含可持久化的 `accessUrl`。需要预览时由选择页或父页按 assetId 现取，地址过期重新取。

选择页规则：

- `source_image`：单选照片；2026-10-22 起由 00-262 覆盖原四类限制，默认“全部照片”（不发送 categoryCode），可切换全部七个照片分类；保留历史/未分类 ready 照片可见，不强制用户迁移旧分类。
- `work_still`：多选照片，最多 3 张；默认筛选 `production`，允许用户切换到其他照片分类。
- `life_photo`：多选照片，最多 12 张；默认筛选 `lifestyle`。
- `video_resume`：单选视频；默认筛选 `self_intro`，允许 `work_clip` / `performance_clip`。
- `attachment`：单选 ready PDF；固定 `resume`。

取消、系统返回、上传失败和页面卸载都必须清除指定 `requestId`，不能沿用既有头像 / 作品选择的全局裸状态。

## 3. 数据模型

### 3.1 演员卡素材集合

新增幂等迁移：`kaipaile-server/src/main/resources/db/migration/V20260818_001__actor_card_media_binding.sql`。实际执行前按迁移目录复核编号，不覆盖已经存在的版本。

新增 `actor_card_media_set`：

| 字段 | 说明 |
|---|---|
| `set_id` | 主键 |
| `card_id` | 演员卡 id |
| `card_work_id` | 作品剧照集合关联的 `actor_card_work.id`，其他用途为空 |
| `usage_code` | `source_image` / `work_still` / `life_photo` / `video_resume` |
| `version` / `deleted` / 审计字段 | 复用项目公共审计口径 |

同一 `card_id + card_work_id + usage_code` 只允许一个 active 集合；由于 MySQL NULL 唯一索引语义不适合直接表达该约束，服务层在事务内使用 `SELECT ... FOR UPDATE` 保证。

新增 `actor_card_media_item`：

| 字段 | 说明 |
|---|---|
| `item_id` | 主键 |
| `set_id` | 所属集合 |
| `asset_id` | 新素材绑定，可空 |
| `legacy_url` | 历史 URL 回退条目，可空；只能由服务端从旧字段导入 |
| `sort_order` | 从 0 开始，越小越靠前 |
| `version` / `deleted` / 审计字段 | 复用项目公共审计口径 |

约束：`asset_id` 和 `legacy_url` 必须且只能有一个非空；新客户端不能提交任意 `legacy_url`。集合可以没有 item，用于表达“新合同下的显式空列表”，防止旧 URL 回退复活。

附件不重复建集合，继续使用 00-214 已落地的 `actor_card.attachment_asset_id` 和 `attachment: { assetId }` 三态合同。

### 3.2 旧数据兼容

- 没有 `actor_card_media_set` 的卡：按现有 `source_image_url`、`photos_json`、`video_url`、`actor_card_work.stills_json` 读取。
- 新版本第一次读取旧数据时，服务端可以在内存中转换成只读 `legacy_url` 条目；第一次保存该用途时，事务内创建集合并保留用户没有删除的 legacy 条目。
- 新集合一旦存在，即使 item 为空，也优先于旧字段，保证显式删除不会被旧字段复活。
- 旧 URL 字段保留给旧客户端和历史公开卡；新绑定的私有 asset 不要求旧客户端展示，但不得改变旧客户端接口响应结构或导致启动失败。

## 4. API 与服务端合同

### 4.1 草稿素材集合

新增接口：

```text
GET /api/actor-card/draft/{cardId}/media
  query: usage, workId?

PUT /api/actor-card/draft/{cardId}/media
  body: {
    usage: 'source_image' | 'work_still' | 'life_photo' | 'video_resume',
    workId?: number,
    items: Array<{
      itemId?: number,
      assetId?: number,
      sortOrder: number
    }>
  }
```

响应条目包含 `itemId`、`assetId`、文件名、媒体类型、处理状态、`sortOrder`；若是当前演员卡所有者读取，可以额外包含短时 `previewUrl` 和 `expiresAt`。签名 URL 不写入数据库和 Pinia 长期状态。

PUT 的事务步骤：

1. 锁定并验证当前用户拥有 `cardId`，状态允许编辑。
2. 校验 usage、`workId` 归属和数量上限。
3. 对所有 `assetId` 批量 `SELECT ... FOR UPDATE`，验证 `user_id`、`media_type`、`process_status=ready`；他人资源统一返回不存在 / 不可用错误，不泄漏资源存在性。
4. 校验无重复 asset、排序连续且从 0 开始。
5. 替换对应 active 集合，空数组创建空集合。
6. 返回保存后的集合和最新签名预览地址。

旧 `saveStep`、`replaceWorks` 接口保留。`replaceWorks` DTO 增加可选 `stillAssetIds` / `stillItems` 字段；旧客户端只传 `stills` 时按历史 URL 路径处理，新客户端在同一事务中创建 / 替换作品和剧照集合，并返回完整作品 DTO。

### 4.2 上传和 AI 扩图

- 向导新上传统一调用 `POST /api/actor/assets`（照片 / 视频）或既有 PDF 上传接口，返回 `assetId` 后再调用绑定接口。
- `step-visual` 的扩图请求新增可选 `sourceAssetId`。服务端验证 owner + ready photo 后，通过 `PrivateActorMediaStorage.issueAccessUrl` 现取签名地址传给 AI provider；旧 `sourceImageUrl` 入参继续兼容。
- 既有 `/api/file/upload/photo|video` 不删除、不改变响应；它只服务历史前端和旧 URL 数据路径，不作为新向导的素材库写入路径。

### 4.3 公开观看、复制和删除

- `ActorCardPublicService` 读取 active 集合时按 `sortOrder` 返回内容；对已发布卡的 asset 生成短时访问地址，未发布 / 草稿仍拒绝公开读取。
- 公开响应保留现有 `photos`、`video`、`works[].stills` 字段，新增字段只用于后续客户端需要时的元数据，不改变旧观看页结构。
- `copyActorCard` 在同一用户范围内复制集合、item、作品映射和附件绑定；复制后新卡集合与原卡隔离，排序保持一致。
- `ActorMediaAssetService.delete` 增加演员卡集合和 `attachment_asset_id` 引用检查；被引用时返回既有 `PROFILE_ASSET_IN_USE`，不软删资源，不留下公开卡死链。

## 5. 前端接线设计

### 5.1 共享选择入口

新增轻量的选择会话 helper（可放在现有 `asset-selection` store 内，不新建跨包业务组件）：

- `beginCardAssetSelection(request)`：创建 requestId。
- `completeCardAssetSelection(requestId, items)`：写入结果。
- `consumeCardAssetSelection(requestId)`：父页一次性读取并清理。
- `cancelCardAssetSelection(requestId)`：取消 / unload 清理。

选择页只依赖 `getActorAssets`、`requestAssetAccessUrl`、`uploadActorAsset` 等现有素材 API；不把 `pages/assets` Tab 根页 redirect 到选择页。

### 5.2 各向导页

- `step-visual`：已有首图回填优先显示 asset item；选择 / 上传后绑定 `source_image`，扩图提交 `sourceAssetId`；旧 URL 只作为历史只读回退。
- `step-works`：作品保存和剧照绑定同一提交事务；管理剧照同时支持素材库多选、手机上传、替换、删除和拖拽排序，第一张封面规则保持不变。
- `step-photos`：将手机上传改为 `uploadActorAsset(..., 'photo', 'lifestyle')`，上传成功自动加入素材库；素材选择和本地上传结果都进入同一有序列表，最多 12 张。
- `step-video`：选择或上传 `video/self_intro`，保存 `video_resume` 绑定；预览使用现取访问地址，替换前确认并保留旧资源。
- `step-attachment`：复用 00-214 已完成的选择、上传、处理中、失败重试、预览、替换、删除和 `attachment_asset_id` 三态；只新增“从素材库选择 PDF”入口。
- 所有页面保存后调用 `draftStore.reload()`，下一步期间锁定重复点击；读取失败时阻断继续，不用空值覆盖旧绑定。

### 5.3 排序交互

优先复用小程序长按拖拽能力；若基础库 / 自动化环境不稳定，第一阶段使用明确的“上移 / 下移”按钮，仍然提交相同 `sortOrder` 合同，不把排序降级为只读文案。按钮必须有可访问名称，且不能用 Emoji 表达。

## 6. 验证与门禁设计

新增 `kaipai-frontend/scripts/verify-v3-asset-wizard.mjs`，收集全部失败后统一非零退出，至少断言：

1. `pkg-profile/assets` 存在 `card-select`、requestId 会话隔离、确认 / 取消清理。
2. 五个向导用途均有正确媒体类型、分类、上限和真实 handler。
3. 新向导上传使用 `uploadActorAsset`，不再把新素材保存到旧 `uploadImageFile` / `uploadVideoFile` URL 路径。
4. 绑定请求只提交 assetId / itemId / sortOrder，不提交签名 URL。
5. 生活照片最多 12 张、作品剧照每部最多 3 张、第一张封面和排序保存存在。
6. 附件继续使用 00-214 的 `attachment_asset_id` 三态；跳过不清空、删除才显式清空。
7. 公开观看和复制接口保留旧字段，同时消费新绑定集合。
8. 删除素材前存在演员卡引用检查；迁移 SQL 具备幂等写法。
9. 反向注入：交换 media type / 删除排序提交 / 注入签名 URL / 移除取消清理后，门禁必须失败。

后端补充：绑定归属、类型、状态、排序上限、旧 URL 回退、复制隔离和删除引用的单元 / 集成测试；migration 在空库、本地已有库和重复执行三种场景验证。

## 7. 发版与运行态顺序

1. 关闭微信开发者工具，执行幂等迁移；生产迁移必须由用户明确下令，使用现有 `DbMigrationRunner` 流程。
2. 先发布后端和迁移，再发布包含选择页和向导绑定的新小程序；旧前端继续使用旧 URL 合同。
3. 执行 `type-check`、后端测试、`verify:v3-asset-wizard`、已有 00-221 门禁、`build:mp-weixin` 和双侧 scoped hash 检查。
4. 在微信开发者工具依次验证素材管理、主视觉、作品剧照、生活照片、视频、附件和返回回读；至少覆盖游客 / 登录、空素材、处理中、失败重试、已有旧 URL 卡和多设备。
5. 发布构建使用 `build:mp-weixin:release`，确认产物无本地 URL；`dist/dev` 只用于联调。

## 8. 风险与处理

| 风险 | 处置 |
|---|---|
| 私有签名 URL 过期 | 不落库；草稿 / 公开 / AI 调用时按 assetId 现签 |
| 旧 URL 和新绑定同时存在 | 每个用途以“是否存在新集合”决定优先级；集合可为空，显式删除不会复活旧字段 |
| 素材被删除导致已发布卡死链 | 删除前检查所有演员卡 / 附件 / 作品引用，使用中拒绝删除 |
| 迁移未先执行 | 新接口返回可识别的能力未部署错误；旧接口继续可用；发布门禁把迁移版本列为前置 |
| 选择会话残留 | requestId 隔离，确认 / 取消 / 返回 / unload 都清理；不复用头像和作品的裸单例状态 |
| 选择页进入分包后跨包模块异常 | 选择页仅依赖稳定 API、store 和自包含 UI；不 require 外部业务页面模块，遵守 00-219 经验 |
