# 00-193 当前阶段 COS 存储桶轮换配置修复

## 1. 概述

生产存储桶到期后已配置新的腾讯云 COS bucket，但生产上传链路仍返回 `code=500` / `操作失败`。排查发现当前后端源码绑定的是 `tencent.cos.region / tencent.cos.bucket-name`，默认环境变量为 `TENCENT_COS_REGION / TENCENT_COS_BUCKET_NAME`；历史生产 compose/env 仍使用 `COS_REGION / COS_BUCKET_NAME`。如果只替换旧键，后端重启后仍可能读不到新桶。

本轮目标是把 COS 配置键兼容、历史对象迁移和生产配置轮换收口到一次可追溯整改：先将旧 bucket 对象只复制到新 bucket，再让代码兼容旧键，生产运行时显式同步新旧两组键，并通过真实上传 smoke 验证返回 URL 已指向新 bucket。

## 2. 用户故事

- 作为小程序用户，我上传头像、作品图、PDF 或 AI 分析图时，不应因为旧桶到期而看到「操作失败」。
- 作为小程序用户，我过往已经上传的头像、作品图、视频、PDF 转图和 AI 生成图，在 bucket 轮换后仍应具备可恢复访问的对象基础。
- 作为维护者，我希望生产 bucket 轮换后，后端配置来源清楚，后续发布/重启不会退回旧桶或空配置。
- 作为发布操作人，我希望本次配置变更有 SCE 记录、发布记录和上传 smoke 证据。

## 3. 功能需求

### 3.1 后端 COS 配置兼容

**描述**：后端 `application.yml` 必须优先读取 `TENCENT_COS_REGION / TENCENT_COS_BUCKET_NAME`，并在缺失时兜底读取历史 `COS_REGION / COS_BUCKET_NAME`。

**验收标准**：

- WHEN 运行环境只提供 `COS_REGION / COS_BUCKET_NAME` THEN `TencentCloudProperties.cos.region / bucketName` 能绑定到对应值。
- WHEN 运行环境同时提供 `TENCENT_COS_*` 与 `COS_*` THEN 优先使用 `TENCENT_COS_*`。
- WHEN 后续生产 compose/env 显式提供两组键 THEN 后端上传返回 URL 的 host 使用同一个新 bucket。

### 3.2 生产配置轮换

**描述**：使用标准 release runbook 同步生产 compose/env，而不是手工改 Nacos 控制台或手工 docker patch。生产环境必须显式包含：

- `TENCENT_COS_REGION`
- `TENCENT_COS_BUCKET_NAME`
- `COS_REGION`
- `COS_BUCKET_NAME`

**验收标准**：

- WHEN 回读生产容器 env THEN 两组 region / bucket 键均存在，且 bucket 值一致。
- WHEN 后端完成重启 / 发布 THEN `GET /api/v3/api-docs` 仍为 `200`。
- WHEN 上传一个小尺寸图片到 `/api/file/upload/photo` THEN 返回 `code=200`，URL 指向新 bucket。

### 3.3 上传 smoke 与清理

**描述**：完成配置生效后，使用登录态 smoke token 上传 1x1 PNG 到 `/api/file/upload/photo`；若返回 URL 成功，应立即调用 `/api/file/delete?url=...` 删除测试对象。

**验收标准**：

- WHEN 上传 smoke 成功 THEN 响应为 `{"code":200,...}`。
- WHEN 删除 smoke 对象 THEN 删除接口返回 `code=200`。
- WHEN 检查后端日志 THEN 最近日志中不出现 `COS 文件上传失败`、`操作失败` 或相关异常。

### 3.4 历史对象迁移

**描述**：在生产上传切换到新 bucket 前，先执行旧 bucket 到新 bucket 的同 region 服务端复制。迁移只复制对象，不删除旧 bucket 对象，不改业务数据库 URL。

**验收标准**：

- WHEN 迁移脚本读取凭据 THEN 只允许从本地安全文件、本地环境变量或生产容器 env 读取，不在日志、Spec 或记录中输出 SecretId / SecretKey。
- WHEN 执行 dry-run THEN 能列出旧 bucket 对象数量、总字节数和迁移目标 bucket，不写入新 bucket。
- WHEN 执行正式迁移 THEN 对旧 bucket 中每个对象按原 key 复制到新 bucket，目标 key 与源 key 保持一致。
- WHEN 目标 bucket 已存在同 key 且大小一致 THEN 允许跳过复制并计入 skipped。
- WHEN 迁移完成 THEN 记录 copied / skipped / failed / verified 数量和字节数；failed 必须为 0 才允许继续切换生产上传配置。

## 4. 非功能需求

- 不在源码、Spec 或发布记录中写入腾讯云 SecretId / SecretKey。
- 不修改上传文件大小、文件类型、路径规则或业务 UI。
- 迁移历史 COS 对象时只做 bucket-to-bucket copy，不删除旧 bucket，也不在本轮直接批量改业务数据库 URL。
- 发布时不得回退上一轮已上线但尚未提交的实名状态 500 修复。

## 5. 约束条件

- 生产后端当前运行在 `SPRING_PROFILES_ACTIVE=prod`、`NACOS_ENABLED=true`。
- 当前生产上传能力必须走真实 `/api/file/upload/*`，不得用 mock 或前端兜底掩盖错误。
- 配置同步必须通过 `.sce/runbooks/backend-admin-release/scripts/run-backend-compose-env-sync.py` 或标准后端发布脚本留档。
