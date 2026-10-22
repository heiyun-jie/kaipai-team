# 00-233 历史媒体数据兼容回填 - 技术设计

_Requirements: 3.1-3.6, 4, 5_

## 1. 来源优先级

| 新用途 | 历史来源 | 优先级 |
|---|---|---|
| 头像 | `actor_profile.avatar_url` | 1 |
| 头像 | `user.avatar_url` | 2，profile 为空时使用 |
| 生活照片 | `actor_profile.photo_urls` | 按 JSON 顺序 |
| 公开视频 | `actor_profile.video_url` | 单项 |

旧演员卡和旧分享卡内的 URL 继续由其兼容读取逻辑负责，本批不改写历史快照。

## 2. 稳定迁移键

每个来源项生成：

```text
sourceKey = SHA256(userId | sourceField | normalizedUrl)
```

记录中不保存 normalizedUrl 明文。本阶段不新增第 15 张数据库迁移表，避免破坏 `00-230/00-232` 固定的 14 文件批次。断点状态由脱敏的批次证据文件保存；数据库幂等性依靠确定性目标 key、`actor_media_asset` 的对象唯一键和 profile asset 关系唯一键保证。

| 字段 | 说明 |
|---|---|
| `migration_key` | sourceKey，唯一 |
| `batch_id` | 候选/执行批次 |
| `user_id` / `actor_profile_id` | 内部归属 |
| `source_field` / `media_type` | 来源和类型 |
| `source_url_sha256` | URL 哈希 |
| `target_bucket_code` / `target_object_key` | 新对象定位 |
| `asset_id` | 新素材 id |
| `status` / `failure_code` | pending/copied/linked/failed |

证据文件不保存完整旧 URL；工具每次仍从受控旧字段读取并按 hash 重算目标 key。证据丢失后可通过目标 key 和关系查询重建，不替代数据库唯一约束。

## 3. 对象验证与复制

1. 解析 URL，拒绝非 HTTPS、userinfo、非白名单 host 和异常 path。
2. 使用服务端云存储能力读取元数据；必要时执行受限 GET 检查魔数。
3. 验证照片/视频 MIME 与大小上限。
4. 目标 key 使用 `actor-private/migration/<userId>/<mediaType>/<sourceKey>.<ext>`。
5. 先检查目标对象；存在且元数据一致则复用，不一致则标记冲突。
6. 复制成功后才创建数据库素材记录。

测试/生产目标 bucket 由显式环境参数选择，工具启动时回读并拒绝 test->prod bucket 或 prod->test bucket 组合。

## 4. 数据库事务边界

每个媒体项一个短事务：

1. 读取脱敏批次状态；数据库状态以目标 key 和关系为准。
2. 按目标 bucket/object key 查询已有 asset。
3. 不存在则插入 `actor_media_asset`。
4. 头像更新 `avatar_asset_id`；照片/视频插入关系。
5. 在批次证据中写入 `linked` 状态。

对象复制不放进数据库长事务。若对象已复制但事务失败，重跑通过稳定 key 复用对象。

## 5. 关系规则

- `actor_media_asset.storage_provider=cos`。
- `process_status=ready`，`source_type=migration`。
- 头像素材 category 使用兼容的 portrait 类别。
- 生活照片使用 `actor_profile_asset.usage_code=public_photo`，`sort_no` 对应原数组顺序。
- 视频使用 `usage_code=public_video`，每个 profile 当前最多一个 active 历史视频关系。
- 新关系建立前验证 asset 和 profile 属于同一 user。

## 6. Dry-run 与 Apply

Dry-run 不写 COS、数据库和本地 secret 文件，输出：

- source item count。
- unique URL hash count。
- trusted/readable/invalid/missing count。
- photo/video/avatar 分项。
- 预计复制字节数。
- 异常内部 id + source hash + failure code。

Apply 必须携带 `--candidate-id`、`--manifest-sha256`、`--environment test|prod` 和显式目标 bucket code。工具版本由 `00-231` manifest 固定。

## 7. 兼容断言

- 旧字段非空计数前后相等。
- 每个 readable sourceKey 都有 `linked` map、ready asset 和目标关系。
- asset owner 与 profile owner 一致。
- 不存在重复 active relation。
- 新 UI 能签发访问地址，旧 URL 仍可读取。
- apply 重跑创建计数为 0，skip/verified 计数等于已完成项。

## 8. 失败策略

- 网络临时失败：有限指数退避，超过阈值记 `retryable`。
- 对象不存在、host 不可信、类型错误：永久异常，需人工裁决。
- DB/COS 目标环境不匹配：立即全局中止。
- 单项失败不删除已复制对象；最终存在任何未裁决有效媒体则 `NO-GO`。

## 9. 回滚边界

正常应用回滚保留新 asset 和关系，旧字段仍是安全回退。清理 migration 对象或 map 必须另立删除 Spec，并证明无新 UI/卡片引用；本阶段不提供批量删除命令。
