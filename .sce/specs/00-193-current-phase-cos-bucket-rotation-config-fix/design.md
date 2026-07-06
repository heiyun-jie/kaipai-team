# 00-193 当前阶段 COS 存储桶轮换配置修复 - 技术设计

## 1. 范围

_Requirements: 3.1, 3.2, 3.3_

本轮处理 COS bucket 历史对象迁移、配置轮换与后端配置键兼容：

| 层 | 文件 / 入口 | 策略 |
|----|-------------|------|
| 后端配置 | `kaipaile-server/src/main/resources/application.yml` | `TENCENT_COS_*` 优先，`COS_*` fallback |
| 对象迁移 | `.sce/runbooks/backend-admin-release/scripts/migrate-cos-bucket-objects.py` | 旧 bucket 到新 bucket 同 key 服务端复制，只复制不删除 |
| 生产配置 | `run-backend-compose-env-sync.py` | 同步 `TENCENT_COS_*` 与 `COS_*` 两组键 |
| 后端发布 | `run-backend-only-release.py` | 发布配置兼容变更，并保留上一轮实名修复 overlay |
| 验证 | `/api/file/upload/photo`、`/api/file/delete` | 上传 1x1 PNG 后删除 |

不修改 `CosUtil` 的上传规则，不改变前端上传工具。历史对象迁移只建立新 bucket 中的对象副本，不删除旧对象，不直接改数据库中已保存的旧 URL。

## 2. 对象迁移设计

_Requirements: 3.4_

迁移在生产上传切换前执行，默认源与目标为：

- source bucket: `kaipai-1412601014`
- target bucket: `kaipai-prod-1412601014`
- region: `ap-shanghai`

迁移脚本使用腾讯云 COS XML API：

1. 从本地环境变量、本地安全文件或生产容器 env 读取 `TENCENT_CLOUD_SECRET_ID / TENCENT_CLOUD_SECRET_KEY`，兼容历史 `COS_SECRET_ID / COS_SECRET_KEY`。
2. 对 source bucket 执行 `List Objects V2` 分页统计。
3. 对 target bucket 执行 `HEAD Bucket` / 小对象写入前置校验。
4. 对每个对象先 `HEAD Object` 检查 target 是否已存在同 key 且大小一致；一致则跳过。
5. 对缺失或大小不一致对象执行 `PUT Object - Copy`，保持原 key。
6. 每个复制对象再执行 `HEAD Object` 校验大小。
7. 输出脱敏迁移记录到 `.sce/runbooks/backend-admin-release/records/`。

迁移不下载对象内容到本地或服务器磁盘，降低耗时与中间存储风险。

## 3. 配置兼容设计

_Requirements: 3.1_

`application.yml` 当前写法：

```yaml
tencent:
  cos:
    region: ${TENCENT_COS_REGION:}
    bucket-name: ${TENCENT_COS_BUCKET_NAME:}
```

改为嵌套 placeholder：

```yaml
tencent:
  cos:
    region: ${TENCENT_COS_REGION:${COS_REGION:}}
    bucket-name: ${TENCENT_COS_BUCKET_NAME:${COS_BUCKET_NAME:}}
```

这样满足：

- 新标准键 `TENCENT_COS_*` 存在时优先生效。
- 历史运行环境只提供 `COS_*` 时仍能绑定。
- 后续删除历史键前，有一段安全兼容窗口。

## 4. 生产同步设计

_Requirements: 3.2_

生产当前实际上传配置来源不在 Nacos dataId，而在容器环境。使用标准 compose/env 同步脚本将新 bucket 同步为：

- `TENCENT_COS_REGION=<new-region>`
- `TENCENT_COS_BUCKET_NAME=<new-bucket>`
- `COS_REGION=<new-region>`
- `COS_BUCKET_NAME=<new-bucket>`

`COS_SECRET_ID / COS_SECRET_KEY / TENCENT_CLOUD_SECRET_ID / TENCENT_CLOUD_SECRET_KEY` 不在本轮变更范围内；除非上传 smoke 显示权限仍失败，才另开配置补齐。

## 5. 发布设计

_Requirements: 3.1, 3.2_

由于 `application.yml` 变更需要进入 jar，必须执行后端发布。当前工作树仍有上一轮实名状态 500 修复的未提交改动，但该修复已发布到生产；本轮 backend-only overlay 必须同时包含：

- 本轮 `application.yml`
- 上一轮实名状态兼容源码与迁移文件
- 上一轮实名测试文件

否则干净 HEAD 构建会回退 `/api/verify/status` 生产修复。

## 6. 验证设计

_Requirements: 3.2, 3.3, 3.4_

验证顺序：

1. 本地后端编译：`cd kaipaile-server && mvn -q -DskipTests compile`
2. COS 对象迁移 dry-run 返回旧 bucket 对象数量与字节数。
3. COS 对象正式迁移完成，failed 为 0。
4. 生产 compose/env sync 记录生成。
5. backend-only 发布完成。
6. 回读容器 env，仅确认键存在、长度和两组 bucket 一致，不输出密钥。
7. `GET https://api.kplyyk.com/api/v3/api-docs` 返回 `200`。
8. `POST https://api.kplyyk.com/api/file/upload/photo` 上传 1x1 PNG 返回 `code=200`。
9. 上传返回 URL host 指向新 bucket。
10. `DELETE https://api.kplyyk.com/api/file/delete?url=...` 删除测试对象返回 `code=200`。
11. 最近日志过滤 `COS 文件上传失败|操作失败|Exception` 为空。
