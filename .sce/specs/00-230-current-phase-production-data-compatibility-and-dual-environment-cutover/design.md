# 00-230 生产数据兼容验证与双环境正式切流 - 技术设计

_Requirements: 4.1-4.8, 5, 6_

## 1. 目标架构

同一台服务器可以复用 MySQL、Redis、Nacos 和 Nginx 实例，但运行时必须逻辑隔离：

| 项 | 测试 | 正式 |
|---|---|---|
| API | `test-api.kplyyk.com` | `api.kplyyk.com` |
| 后端容器 | `kaipai-backend-test` | `kaipai-backend` / 切流候选 |
| 后端端口 | `18080` | `8080`，候选临时端口另设 |
| profile | `test` | `prod` |
| Nacos dataId | `kaipai-backend-test.yml` | `kaipai-backend-prod.yml` |
| MySQL 实例 | 同一实例 | 同一实例 |
| schema | `kaipai_test` | `kaipai_prod` |
| Redis | 独立 DB index | 独立 DB index |
| COS | 独立测试 bucket，至少独立且不可碰撞的测试前缀 | 正式私有 bucket |
| 小程序 | 开发版 / 体验版指向 test API | 正式版指向 prod API |

`kaipai_test` 在每个发布候选验证周期开始时由 `kaipai_prod` 完整重建。人工测试产生的数据只存在测试 schema。

## 2. 发布候选冻结

发布清单至少记录：

- 根仓库提交和所有子仓库提交。
- 必要 overlay 文件清单；未列入 overlay 的脏改不进入构建。
- 后端 JAR SHA256。
- 管理端静态产物 SHA256。
- 小程序 test / release 构建对应提交和 API Base URL 证明。
- 14 个迁移文件名和 SHA256。
- 历史素材兼容程序版本、批次号和只读/写入模式。

测试通过后不得继续修改候选。任何代码或迁移变化都视为新候选，必须重新克隆生产副本并重跑门禁。

## 3. Schema 差异和迁移批次

### 3.1 当前缺口

`kaipai_prod` 缺少 19 张候选代码依赖表：

```text
actor_profile_representative_work
actor_media_asset
actor_media_asset_page
actor_profile_asset
actor_work_asset
share_card_work
share_card_asset
share_card_favorite
ai_profile_import_config
ai_profile_import_config_audit
ai_profile_import_request_audit
ai_profile_import_prompt_template
ai_profile_import_prompt_version
ai_profile_import_prompt_audit
actor_card
actor_card_work
actor_card_background
actor_card_media_set
actor_card_media_item
```

`actor_profile` 缺少 `avatar_asset_id`、`current_resume_asset_id`、拆分生日、籍贯、院校专业、四组标签和 `work_library_version`；`actor_experience` 缺少发布状态、作品/角色规范码、同期声、合作人、成绩、规范化名称、去重键和来源类型。

### 3.2 固定迁移顺序

测试和生产必须严格执行以下顺序：

1. `V20260723_001__career_profile_domain_foundation.sql`
2. `V20260723_002__actor_media_asset_relations.sql`
3. `V20260723_003__share_card_favorite.sql`
4. `V20260723_004__ai_profile_import_governance.sql`
5. `V20260723_005__ai_profile_import_permission_alignment.sql`
6. `V20260724_001__ai_profile_import_request_scene.sql`
7. `V20260726_001__ai_profile_import_prompt_template_governance.sql`
8. `V20260726_002__ai_profile_import_prompt_permission_alignment.sql`
9. `V20260731_001__actor_card_tables.sql`
10. `V20260731_002__actor_card_background_seed.sql`
11. `V20260810_001__actor_card_attachment_asset_binding.sql`
12. `V20260814_001__actor_card_background_style_cleanup.sql`
13. `V20260814_002__actor_card_background_provision.sql`
14. `V20260818_001__actor_card_media_binding.sql`

必须使用 `.sce/runbooks/backend-admin-release/scripts/run-backend-schema-migration.py` 维护 `schema_release_history`，不得手工执行后再漏登记。

### 3.3 非幂等风险

以下 5 个脚本不能在未知部分成功状态下直接重跑：

| 脚本 | 风险 |
|---|---|
| `V20260724_001` | 无条件 ADD / MODIFY `scene` |
| `V20260726_001` | 无条件建表、加列、加外键和插入 seed |
| `V20260731_001` | 无条件创建三张表 |
| `V20260731_002` | 无条件插入 10 行 seed |
| `V20260810_001` | 无条件增加列和索引 |

生产前必须完成其一：

1. 把 5 个脚本改成 INFORMATION_SCHEMA 守卫的幂等形式，并在 MySQL 8 上验证“首次执行 + 重复执行”；或
2. 保持文件不变，但在全新生产副本上验证一次性完整成功，生产执行期间逐文件登记；若失败，先按 INFORMATION_SCHEMA 判断实际状态，再由专门修复 SQL 收口，禁止盲重跑。

推荐方案 1。当前 Schema runner 把 migration SQL 和 history 写入拼成一个脚本，但 MySQL DDL 会隐式提交，不能把它当成完整事务回滚。

## 4. 生产副本测试流程

### 4.1 备份和克隆

1. 停止测试后端，保证没有连接写 `kaipai_test`。
2. 对 `kaipai_prod` 执行一致性备份：`--single-transaction --routines --triggers --hex-blob`。
3. 对旧 `kaipai_test` 单独备份，便于恢复历史测试数据。
4. 计算本地和远端 SHA256，二者必须一致。
5. 删除并重建的目标只能是解析后的精确 schema `kaipai_test`；操作前再次回读目标名。
6. 将生产备份恢复到 `kaipai_test`。
7. 在迁移前保存结构和业务计数快照。

恢复过程只改变 `kaipai_test`。任何命令解析出 `kaipai_prod` 时立即中止。

### 4.2 测试环境隔离

- `kaipai-backend-test.yml` 数据源改为 `kaipai_test`。
- Redis 使用测试 DB，并在启动前确认与生产 DB index 不同。
- 短信只允许白名单手机号，或改为固定验证码提供器。
- 实名、AI 生图、DeepSeek 导入默认禁用真实计费调用；需要验证时使用白名单和额度上限。
- 测试上传必须使用独立测试 bucket。当前 `CosPrivateActorMediaStorage` 的 key 没有环境前缀，因此仅复用正式 bucket 不满足完全隔离。
- 微信支付/回调若不在本次范围应关闭；所有测试 callback 指向测试域名。

## 5. 历史素材兼容设计

### 5.1 为什么不能只做 DDL

新资料编辑页要求 `avatarAssetId`，新素材库只查询 `actor_media_asset`。历史 `avatar_url`、`photo_urls`、`video_url` 即使原值仍在，用户仍会看到素材库为空，资料编辑也可能要求重新选择头像。

### 5.2 推荐回填策略

采用“复制对象 + 新建素材元数据 + 保留旧字段”的一次性兼容程序，不使用纯 SQL 猜 URL：

1. 只读扫描非空的 `avatar_url`、`photo_urls`、`video_url`。
2. 解析 JSON，规范化并去重 URL；只接受 HTTPS 和受信任 COS host。
3. HEAD/GET 验证对象存在、内容类型和大小。
4. 将对象复制到当前环境的 actor private bucket：测试写测试 bucket，生产写正式 private bucket。
5. 按用户、原 URL 哈希和媒体类型幂等创建 `actor_media_asset`，设置 `process_status=ready`、`source_type=migration`。
6. 头像写 `actor_profile.avatar_asset_id`；照片写 `actor_profile_asset(public_photo)` 并保留排序；视频写 `actor_profile_asset(public_video)`。
7. 旧 URL 字段保持原值，旧前端和旧分享页继续读取。
8. 输出异常清单；任一有效历史 URL 未成功回填即 NO-GO。

必须给迁移行增加稳定幂等键。现表没有独立 `migration_key`，实现时可复用唯一 `(storage_provider,bucket_code,object_key)`，并在迁移记录中保存 `legacy URL SHA256 -> asset_id` 映射；不得在日志记录完整 URL。

直接把旧对象元数据指向原公有 bucket 不推荐：素材删除会调用 `cosClient.deleteObject(bucketCode, objectKey)`，可能删除仍被旧 URL 字段引用的原对象。

## 6. 数据兼容断言

迁移前后至少保存以下聚合值，记录只含计数和哈希，不含 PII：

| 断言 | 通过条件 |
|---|---|
| 有效用户数 | 不减少 |
| 有效演员档案数 | 不减少，且仍一一归属用户 |
| 有效演艺经历数 | 不减少，旧名称/角色字段非空值不被覆盖 |
| 旧分享卡与演员卡数 | 旧分享卡不减少；新增 actor_card 初始可为 0 |
| 浏览历史和收藏 | 既有记录不减少 |
| 实名状态 | 各状态计数一致，证件密文/脱敏字段不输出 |
| 旧媒体 URL | 原字段非空计数不减少 |
| 新媒体回填 | 每个可读取旧媒体都有对应 ready asset 和关系 |
| Schema | 19 张表和全部必需列存在 |
| 迁移历史 | 14 个文件名和 SHA256 与候选清单一致 |

新增列默认值重点：历史 `actor_experience.source_type=manual`；规范化名称和去重键初始可能为空字符串，不得据此删除或合并旧作品；后续只有用户编辑或专门规范化批次才回填。

## 7. 人工验收矩阵

人工测试使用两类账号：生产副本中的历史账号、测试环境新注册账号。

| 模块 | 历史账号 | 新账号 |
|---|---|---|
| 登录/会话恢复 | 登录、退出、重新进入 | 注册、验证码、登录 |
| 个人资料 | 旧头像可见、保存不清空旧字段 | 新增头像和资料 |
| 演艺经历 | 旧作品可读写、新字段默认兼容 | 新增/编辑/删除 |
| 自我介绍 | 旧 intro 可见 | 新增并回读 |
| 素材库 | 旧照片/视频回填后可见 | 上传、预览、删除 |
| 演员卡向导 | 旧素材可选择，7 步可完成 | 全新创建 |
| 生成/发布/分享 | 生成、预览、公开页 | 同左 |
| 旧分享页 | 历史卡仍可打开 | 新卡不破坏旧入口 |
| 实名 | 历史状态一致，不重新提交 | 测试能力按白名单验证 |
| 后台 | 登录、角色权限、新页面 | 配置和审计可读 |

测试版小程序需要独立 API 构建变量。正式线上版本在人工测试期间不变，仍访问生产 API。

## 8. 生产切流设计

1. 宣布发布窗口，冻结 Schema 和候选产物。
2. 再次备份 `kaipai_prod` 并校验 SHA256。
3. 在旧后端仍运行时执行 14 个扩展式迁移和历史素材回填。
4. 重跑数据断言；任一计数减少立即 NO-GO。
5. 以候选端口启动新生产后端，连接 `kaipai_prod`，不接公网上游。
6. 对候选执行健康检查、后台登录、历史账号读写和旧前端合同 smoke。
7. `nginx -t` 成功后 reload，把正式 API 上游切到候选。
8. 观察错误率、500、登录、数据库连接池和外部调用。
9. 构建并上传 `build:mp-weixin:release`，确认只包含 `https://api.kplyyk.com`，再提交微信发布。
10. 小程序发布成功后继续观察；稳定后停止旧后端容器，但保留可恢复产物和测试环境。

此顺序保证“后端先兼容，前端后发布”：微信旧版本仍在线时，新后端必须继续兼容旧合同。

## 9. 回滚设计

- Schema 为扩展式，应用回滚时保留新表、新列和回填行。
- Nginx 上游回切旧容器是第一响应；不执行数据库全量恢复。
- 小程序使用微信后台版本回退；后端继续同时兼容旧、新客户端。
- 若仅少量回填异常，按批次标识定点修复，不删除旧 URL。
- 只有发生数据库物理损坏且已停止全部写入时，才考虑全库恢复。

## 10. 主要风险

| 风险 | 等级 | 处置 |
|---|---|---|
| 新 JAR 早于 Schema | 高 | Schema 门禁先行，候选启动前验证 19 表和字段 |
| 非幂等迁移部分提交 | 高 | 优先硬化 5 个脚本；逐文件 history；失败先查实际结构 |
| 历史素材新 UI 不可见 | 高 | 对生产副本执行对象复制和 asset 关系回填 |
| 测试写正式库/正式 COS | 高 | schema、Redis、bucket 三重隔离；启动前回读配置 |
| 微信体验版域名不可用 | 中 | 提前完成 DNS、HTTPS、合法域名白名单 |
| 发布后直接恢复备份丢新写入 | 高 | 回滚应用和流量，不覆盖数据库 |
| 运维文档主机信息冲突 | 中 | 以只读运行态和 00-185 为准，发布前校正旧文档 |
| 旧 helper 泄露敏感 env | 高 | 先同步脱敏 helper；旧版诊断禁用并评估凭据轮换 |

## 11. 预计时间

在 DNS、证书、微信合法域名权限都已具备时：

- 测试环境基础设施：1-2 小时。
- 生产库备份、克隆、14 个迁移和自动断言：30-60 分钟。
- 历史素材回填验证：30-60 分钟，取决于视频下载/上传耗时。
- 人工核心流程：1-2 小时。
- 正式迁移、候选 smoke、切流：30-60 分钟。
- 发布后观察：至少 1-2 小时。

技术执行可在同一天完成；DNS、证书或微信域名审核未准备好时，它们是关键路径。

## 12. 分阶段 Spec 与不可跳过门禁

本 Spec 由以下阶段 Spec 执行，阶段状态和证据统一回填 `execution-plan.md`：

| 阶段 | 职责 | 解锁条件 |
|---|---|---|
| `00-231` | 候选冻结、产物/迁移 manifest、helper 脱敏和凭据风险 | 候选 `FROZEN` |
| `00-232` | migration checksum、非幂等 preflight、partial DDL 和 MySQL 8 演练 | Schema `PASSED` |
| `00-233` | 历史媒体 dry-run、对象复制、asset/关系幂等回填 | Media `PASSED` |
| `00-234` | 测试域名、TLS、Nacos、容器、Redis、COS 和外部能力隔离 | `INFRA_READY` |
| `00-235` | 生产副本重建、14 个迁移、回填、数据断言和旧合同 smoke | `TEST_DATA_READY` |
| `00-236` | 历史/新账号、后台、分享和体验版人工测试 | 用户签署 `GO` |
| `00-237` | 生产同批迁移、候选后端、Nginx 原子切流和 release | `CUTOVER_OK` |
| `00-238` | 发布后观察、回切和旧运行时退场 | `STABLE` 或有记录的 `ROLLED_BACK` |

任何候选 hash、迁移 hash、回填工具版本、目标环境或配置变化都会使当前阶段及下游阶段失效，必须回到 `00-231` 重新冻结。
