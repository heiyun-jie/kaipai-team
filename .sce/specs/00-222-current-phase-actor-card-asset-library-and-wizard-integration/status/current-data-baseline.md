# 00-222 当前演员卡素材数据基线

_盘点日期：2026-08-18_
_对应任务：T0 / Requirements 4.3、5_

## 1. 盘点边界与取证方式

- 数据源：本地开发库 `kaipai_dev`，容器 `kaipai-mysql-local`。
- 取证方式：临时启动原本处于 `exited` 状态的本地容器，只执行聚合只读 SQL；取证完成后已恢复为 `exited`。
- 未连接或修改生产库，未执行 migration，未新增、更新或删除任何业务数据。
- 输出只保留计数、状态、协议分类和脱敏占位符；不记录 URL、对象 key、文件名、用户 id、卡片 id 或个人信息。
- 快照新鲜度：`actor_card` 最新更新时间为 `2026-08-14 11:30:48`，`actor_card_work` 为 `2026-08-14 10:05:43`，`actor_media_asset` 为 `2026-08-13 14:11:40`。本文件代表该本地快照，不代替发布前生产只读预检。

## 2. 结论

1. 当前有效演员卡共 10 张，其中草稿 9 张、已发布 1 张；另有软删除草稿 6 张。
2. 演员卡主视觉、扩图、生活照和作品剧照仍由 URL 字段承载；当前没有视频 URL，也没有历史 `attachment_url` 值。
3. 当前素材库有效素材只有 4 条，全部为 `pdf / resume / ready`；没有 photo 或 video 素材，证明主视觉、剧照、生活照和视频尚未接入素材库。
4. 有效演员卡中 5 张已使用 `attachment_asset_id`，共引用 2 个不同素材；归属、类型、ready 状态和软删除状态均一致。其余 2 个有效 PDF 素材未被引用。
5. 现有删除服务没有检查 `actor_card.attachment_asset_id`。当前被演员卡引用的 2 个素材也没有被 `actor_profile`、`actor_profile_asset`、`actor_work_asset` 或 `share_card_asset` 引用，因此均可绕过现有“素材使用中”检查。这是 T1 删除引用扩展的现存数据风险，不是未来模型才会出现的风险。
6. 当前存在 5 条未软删除的 `actor_card_work` 行，其中 1 条的父演员卡已软删除。后续绑定回填或复制查询必须以有效父卡为边界，不能只按子表 `deleted = 0` 扫描。

## 3. 当前数据矩阵

### 3.1 演员卡字段覆盖

| 范围 | 卡片数 | source URL | expanded URL | photos JSON | video URL | attachment URL | attachment assetId |
|---|---:|---:|---:|---:|---:|---:|---:|
| 有效卡 | 10 | 5 | 4 | 4 | 0 | 0 | 5 |
| 软删除卡 | 6 | 1 | 1 | 1 | 0 | 0 | 1 |

- 4 个非空 `photos_json` 均为合法 JSON 数组，每个数组 1 项。
- 5 条未软删除作品行均有合法 `stills_json` 数组，每个数组 1 项。
- 作品行不存在负数 `sort_order`；但有 1 条未软删除作品行挂在软删除父卡下。

### 3.2 素材库覆盖

| 维度 | 结果 |
|---|---:|
| 有效素材 | 4 |
| 软删除素材 | 2 |
| 有效 `pdf / resume / ready` | 4 |
| 有效 photo | 0 |
| 有效 video | 0 |
| 有效 PDF 页图 | 29，全部 ready |
| 被有效演员卡附件引用的素材 | 2 个素材、5 个卡片绑定 |
| 有效但未引用素材 | 2 |

`actor_profile_asset`、`actor_work_asset`、`share_card_asset` 当前有效关系数均为 0；`actor_profile.avatar_asset_id` 和 `actor_profile.current_resume_asset_id` 当前也均无有效引用。

### 3.3 URL 分类

这里只保留协议 / 存储类别，不保留 host、路径和查询参数。

| 字段 / 数组项 | `http` | `https_other` | `https_cos` | `wxfile` | 其他 |
|---|---:|---:|---:|---:|---:|
| `source_image_url` | 4 | 1 | 0 | 0 | 0 |
| `expanded_image_url` | 4 | 0 | 0 | 0 | 0 |
| `photos_json` 项 | 4 | 0 | 0 | 0 | 0 |
| `actor_card_work.stills_json` 项 | 5 | 0 | 0 | 0 | 0 |
| `video_url` | 0 | 0 | 0 | 0 | 0 |
| `attachment_url` | 0 | 0 | 0 | 0 | 0 |

当前快照没有 `wxfile://` 残留，但 18 个有效 URL 项中 17 个仍为明文 `http`，另有 1 个为其他 `https` 地址。00-222 不应在迁移阶段擅自抓取、转存或改写这些旧地址；兼容读取必须继续保留，是否可访问应在 T6 运行态逐项验证。

## 4. 非重叠状态分布

| 视觉 / 视频旧 URL | attachment URL | attachment assetId | 有效卡数 | 含义 |
|---:|---:|---:|---:|---|
| 否 | 否 | 否 | 4 | 空素材卡 |
| 否 | 否 | 是 | 1 | 仅 assetId 附件 |
| 是 | 否 | 否 | 1 | 纯旧 URL 素材卡 |
| 是 | 否 | 是 | 4 | 旧 URL 视觉素材 + assetId 附件混合卡 |

当前快照不存在 `attachment_url` 单独存在或与 `attachment_asset_id` 同时存在的卡片，但后端和前端仍保留历史附件 URL 读取 / 删除兼容，不能据此删除该回退合同。

## 5. 脱敏回退样本

以下是由真实状态组合抽象出的合同样本，不是原始数据行。

### 5.1 纯旧 URL 素材卡

```json
{
  "sourceImageUrl": "<redacted-http-url>",
  "expandedImageUrl": "<redacted-http-url>",
  "photos": ["<redacted-http-url>"],
  "works": [{ "stills": ["<redacted-http-url>"] }],
  "videoUrl": null,
  "attachmentUrl": null,
  "attachmentAssetId": null
}
```

回退要求：新绑定集合为空时继续读取原 URL 字段；不得把旧 URL 误判为素材库 asset，也不得在无上传动作时清空。

### 5.2 仅 assetId 附件卡

```json
{
  "sourceImageUrl": null,
  "photos": [],
  "works": [],
  "videoUrl": null,
  "attachmentUrl": null,
  "attachmentAssetId": "<redacted-asset-id>"
}
```

回退要求：附件只按 assetId 校验归属 / PDF / ready 并现签访问地址，不能把签名 URL 写回演员卡。

### 5.3 旧 URL 与 assetId 混合卡

```json
{
  "sourceImageUrl": "<redacted-url>",
  "photos": ["<redacted-url>"],
  "works": [{ "stills": ["<redacted-url>"] }],
  "attachmentUrl": null,
  "attachmentAssetId": "<redacted-asset-id>"
}
```

回退要求：五类资源按用途独立选择新绑定或旧字段，不能因附件已经升级到 assetId 就屏蔽其他旧 URL。

### 5.4 空素材卡

```json
{
  "sourceImageUrl": null,
  "photos": [],
  "works": [],
  "videoUrl": null,
  "attachmentUrl": null,
  "attachmentAssetId": null
}
```

回退要求：GET 返回稳定空集合 / null；PUT 空集合只清目标用途，不影响其他步骤。

### 5.5 历史 attachment URL 合同样本

```json
{
  "attachmentUrl": "<redacted-legacy-url>",
  "attachmentAssetId": null
}
```

当前本地快照数量为 0，但代码合同仍支持展示和显式删除。该样本必须保留在兼容测试中，直至 00-110 完成物理退场门禁。

## 6. 当前结构与读写路径

| 用途 | 当前落库 | 当前写入入口 | 当前读取 / 消费 | 00-222 结论 |
|---|---|---|---|---|
| 主视觉 | `actor_card.source_image_url` / `expanded_image_url` | `step-visual` 使用公有文件上传后 `saveStep` 写 URL | 草稿、扩图、公开观看、复制创建 | 新上传改入素材库；旧 URL 只读回退 |
| 作品剧照 | `actor_card_work.stills_json` | `step-works` 公有上传后 `replaceWorks` 写 URL 数组 | 草稿作品、公开观看、复制创建 | 增加作品范围绑定并保留 stills 回退 |
| 生活照片 | `actor_card.photos_json` | `step-photos` 公有上传后 `saveStep` 写 JSON URL 数组 | 草稿、公开观看、复制创建 | 新上传改入素材库；旧 JSON 回退 |
| 视频简历 | `actor_card.video_url` | `step-video` 公有上传后 `saveStep` 写 URL | 草稿、公开观看、复制创建 | 新上传改入素材库；旧 URL 回退 |
| PDF 附件 | `actor_card.attachment_asset_id`；`attachment_url` 停写 | `step-attachment` 已使用 `uploadActorAsset`，保存时验 owned / pdf / ready | 草稿、页图预览、公开观看、复制创建 | 保持 assetId 语义，增加素材库选择入口 |

当前库不存在 `actor_card_media_set` / `actor_card_media_item`。`actor_media_asset` 保存私有对象元数据，访问地址由后端按 10 分钟有效期现签；签名 URL 不得进入任何演员卡持久化字段。

## 7. 后续任务的硬门禁

1. T1 迁移 / 回填只处理有效父卡；软删除父卡下的有效作品必须单独记录，不可生成孤立绑定。
2. 素材删除引用检查必须同时覆盖现有 `actor_card.attachment_asset_id` 和新增集合 item；当前 2 个附件素材可绕过旧检查，需优先补测试。
3. 新上传 photo / video 后，`actor_media_asset` 的媒体类型、分类、ready 状态和 owner 必须可批量校验；当前库没有这两类真实素材样本，T5 必须补测试数据。
4. 旧 URL 与新 assetId / item 必须允许按用途混合存在；读取优先新绑定，缺失时回退旧字段，禁止一次性破坏式回填。
5. 复制创建必须复制绑定关系和顺序，但不得复制素材实体；旧 URL 字段继续原样复制以保持旧客户端合同。
6. 发布前需要对目标生产库重复同一组只读聚合预检。本地计数只能作为开发基线，不能作为生产迁移断言。

## 8. 本轮未执行

- 未创建或应用 `V20260818_001__actor_card_media_binding.sql`。
- 未创建绑定实体、Mapper、DTO、服务或 API。
- 未修改素材库页面、选择会话或五个向导步骤。
- 未修改或清理任何旧 URL、软删除作品或未引用素材。
