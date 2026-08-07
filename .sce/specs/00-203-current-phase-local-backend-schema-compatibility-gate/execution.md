# 00-203 本地后端 Schema 兼容性门禁 - 执行记录

## 1. 根因

`2026-07-28 11:13:55 +08:00` 本地后端日志记录：

```text
BadSqlGrammarException
Caused by: SQLSyntaxErrorException: Unknown column 'avatar_asset_id' in 'field list'
```

`/api/level/info` 会通过 `CapabilityAccountServiceImpl` 读取 `ActorProfile`。MyBatis-Plus
`BaseMapper.selectOne` 按实体映射投影全部列，因此只要当前实体的任意列未进入数据库，
等级、职业资料及其他复用该读取链的接口都会失败。`00-202` 记录的 12 个职业字段不含
两个素材引用字段；当前 `ActorProfile` 对 `V20260723_001` 的完整新增依赖实际为 14 列。

恢复后的本地 `schema_release_history` 仅到 `V20260705_001`，而当前仓库和 JAR 已包含
`V20260723_001` 及后续迁移。原启动门禁只验证数据库连通与 `/api/doc.html=200`，没有
验证 schema 兼容性，因此产生了“后端启动成功，业务接口运行时 500”的假健康状态。

## 2. 数据库修复

### 2.1 执行前备份

- 目录：`.sce/runbooks/backend-admin-release/records/local-backups/20260728-113009-00-203-local-schema-compatibility/`
- dump：`kaipai_dev-before.sql.gz`
- gzip 完整性：通过
- SHA256：`F6D8F1295BAFE9D4A9967E3D9C8940016DD6A30777C147D9DC65436D6DFD4F08`
- 目录由根 `.gitignore` 排除，不提交 dump。

### 2.2 已执行迁移

批次：`20260728-113141-local-schema-00-203`

1. `V20260723_001__career_profile_domain_foundation.sql`
2. `V20260723_002__actor_media_asset_relations.sql`
3. `V20260723_003__share_card_favorite.sql`
4. `V20260723_004__ai_profile_import_governance.sql`
5. `V20260723_005__ai_profile_import_permission_alignment.sql`
6. `V20260724_001__ai_profile_import_request_scene.sql`
7. `V20260726_001__ai_profile_import_prompt_template_governance.sql`
8. `V20260726_002__ai_profile_import_prompt_permission_alignment.sql`

每个脚本执行成功后才写入 `schema_release_history`，登记仓库文件 SHA256、`apply` 模式
和本地批次号。最终仓库迁移文件与本地历史为 `50 / 50`，缺失数和哈希不一致数均为 0。

## 3. 启动门禁

`.sce/tools/start-kaipai-local-backend.ps1` 新增：

- 仓库 `V*.sql` 与 `schema_release_history` 的脚本名全量比对；
- 已登记脚本 SHA256 与仓库文件 SHA256 比对；
- `actor_profile` 14 个新增列、`actor_experience` 10 个新增列检查；
- 职业资料素材关系、收藏、AI 导入和 Prompt 治理关键表 / 列检查；
- 任一缺项时在 Java 启动或旧进程替换前失败，并输出缺失对象；
- `-ValidateOnly` 复用同一门禁。

门禁首次集成验证发现 MySQL CLI 会转义 `CONCAT(..., CHAR(9), ...)` 的内嵌分隔符；
实现已改为直接查询 `script, checksum` 两列，并增加回归断言。

## 4. 验证结果

| 验证项 | 结果 |
|---|---|
| 门禁单元测试 | `3 tests / OK` |
| 未登记迁移负向探针 | `-ValidateOnly` 启动前拒绝并精确报告脚本名；探针已删除且未执行 SQL |
| `CareerProfileSchemaMigrationTest` | `5 tests / PASS` |
| `start-kaipai-local-backend.ps1 -ValidateOnly` | `configReady=true` |
| 受控 `-Restart` | 新 PID `38336`，`/api/doc.html=200` |
| 本地一次性验证码登录 | 业务码 `200`，锚点用户匹配 |
| `GET /api/level/info` | 业务码 `200`，data 存在 |
| `GET /api/actor/profile/mine` | 业务码 `200`，data 存在 |
| 新进程日志 schema 异常 | `0` |

登录态 smoke 仅在固定本地 Redis 中写入 60 秒一次性验证码，由登录接口消费并在 finally
中删除；执行记录未保存手机号、验证码或 JWT。

## 5. 后续规则

- 从生产恢复本地数据只代表镜像完成；启动当前仓库 JAR 前还必须通过当前仓库迁移门禁。
- 后端发布保持 `schema before JAR`，本地恢复保持 `restore -> ordered migrations -> start`。
- 不再用 `/api/doc.html=200` 单独证明业务运行态健康。
