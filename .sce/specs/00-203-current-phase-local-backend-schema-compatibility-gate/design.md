# 00-203 本地后端 Schema 兼容性门禁 - 技术设计

## 1. 根因链

```text
production mirror restored locally
  -> schema history ends at V20260705_001
  -> current jar contains career-profile entities and services
  -> startup smoke checks only /api/doc.html
  -> /api/level/info loads actor_profile
  -> generated SELECT includes avatar_asset_id
  -> MySQL Unknown column
  -> GlobalExceptionHandler returns generic 500
```

## 2. 本地迁移流程

1. 对 `kaipai_dev` 执行带 routines/triggers/events 的一致性 gzip dump。
2. 计算并保存 dump SHA256。
3. 从 `schema_release_history` 读取已执行脚本。
4. 按文件名顺序选择当前仓库中未记录的 `V20260723_*` 到 `V20260726_*` 文件。
5. 每个文件独立执行；成功后写入 `schema_release_history`，失败立即停止。
6. 用 `INFORMATION_SCHEMA` 验证职业资料关键列、表和索引。

## 3. 启动门禁

在 `.sce/tools/start-kaipai-local-backend.ps1` 的数据库连通检查之后、Java 进程选择和
替换之前增加 `Assert-LocalSchemaCompatible`：

- 检查 `schema_release_history` 中声明的当前本地必需迁移；
- 检查 `actor_profile` / `actor_experience` 的关键列；
- 检查职业资料、素材关系和 AI 导入主链关键表；
- 聚合全部缺项后一次性抛错，错误不得包含凭据。

`-ValidateOnly` 复用同一门禁，因此数据库恢复后可在启动 Java 前独立验收。

## 4. 验证

- PowerShell 静态/行为测试覆盖完整 schema 与缺项 schema 两种输出。
- `start-kaipai-local-backend.ps1 -ValidateOnly` 返回 `configReady=true`。
- 重启后端后 `/api/doc.html=200`。
- 使用本地有效会话调用 `/api/level/info`，响应业务码为 200。
- 日志增量中不存在本次缺列异常。

## 5. 回滚

若迁移或回归失败，停止本地后端，重建 `kaipai_dev`，导入本批执行前 gzip dump，
再按 `00-202` 的本地启动流程恢复。生产环境不参与本轮回滚。

_Requirements: 3.1, 3.2, 3.3_
