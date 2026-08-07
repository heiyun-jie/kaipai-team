# 00-203 当前阶段本地后端 Schema 兼容性门禁

## 1. 概述

`00-202` 将生产 `kaipai_prod` 原样恢复为本地 `kaipai_dev`。该镜像只包含到
`V20260705_001` 的迁移，而当前后端已经依赖 `V20260723_001` 及后续职业资料域
schema。现有本地启动检查只验证数据库可连接和 `/api/doc.html=200`，导致后端能够
启动，但登录态调用 `/api/level/info` 时因 `actor_profile.avatar_asset_id` 等字段缺失
返回通用 500。

本 Spec 补齐本地镜像的当前仓库迁移，并把 schema 兼容性检查前置到本地后端启动
门禁。

## 2. 用户故事

作为本地开发者，我希望后端启动前就能确认数据库与当前代码兼容，避免进入小程序后
才通过业务接口发现 schema 漂移。

作为维护者，我希望本地迁移按仓库文件顺序执行、可追溯且可回滚，不通过临时单列
修补掩盖后续缺项。

## 3. 功能需求

### 3.1 本地迁移修复

- WHEN 修改 `kaipai_dev` 前 THEN 必须先生成可恢复的本地数据库备份及 SHA256。
- WHEN 检测到 `schema_release_history` 只到 `V20260705_001` THEN 必须按文件名顺序
  应用当前仓库中尚未记录的 `V20260723_*` 到 `V20260726_*` 迁移。
- WHEN 单个迁移成功 THEN 必须将脚本名、SHA256、执行模式和批次写入
  `schema_release_history`。
- WHEN 任一迁移失败 THEN 必须停止后续迁移，不得把失败脚本写为成功。

### 3.2 启动前兼容性门禁

- WHEN 启动或验证本地后端 THEN 必须检查当前职业资料主链依赖的迁移记录、关键列和
  关键表。
- WHEN 任一依赖缺失 THEN 启动脚本必须在启动 Java 进程前失败，并列出缺失对象。
- WHEN schema 满足当前基线 THEN `-ValidateOnly` 和正常启动流程必须继续通过。

### 3.3 运行态回归

- WHEN 修复完成 THEN `/api/doc.html` 必须返回 HTTP 200。
- WHEN 使用有效登录态调用 `/api/level/info` THEN 必须返回业务码 200，后端日志不得再
  出现 `Unknown column 'avatar_asset_id'`。
- WHEN职业资料接口读取同一用户 THEN 不得因本批迁移中的其他缺列或缺表返回 500。

## 4. 非功能需求

- 本轮只修改本地 `kaipai_dev`，不得修改生产数据库。
- 不在 Spec、日志或聊天中记录数据库密码、JWT、手机号、身份证号等敏感值。
- 启动门禁不得依赖业务样本数据，只检查 schema 与迁移元数据。
- 迁移和门禁必须可重复执行；已执行迁移不得重复产生破坏性效果。

## 5. 约束条件

- 目标容器固定为 `kaipai-mysql-local`，目标库固定为 `kaipai_dev`。
- 迁移事实源固定为 `kaipaile-server/src/main/resources/db/migration`。
- 不通过修改实体映射或忽略缺失字段绕过 schema 升级。
