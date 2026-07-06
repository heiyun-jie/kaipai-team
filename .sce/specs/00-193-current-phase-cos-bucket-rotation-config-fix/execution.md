# 00-193 执行记录

## 已确认事实

- 生产后端运行在 `101.43.57.62`，容器 `kaipai-backend`。
- 当前生产为 `SPRING_PROFILES_ACTIVE=prod`、`NACOS_ENABLED=true`。
- `kaipai-backend / kaipai-backend.yml / kaipai-backend-prod.yml` 三个 Nacos dataId 只读扫描未命中 COS bucket / region 配置。
- 生产容器 env 中存在历史 `COS_BUCKET_NAME / COS_REGION`，但源码 `application.yml` 只读取 `TENCENT_COS_BUCKET_NAME / TENCENT_COS_REGION`。
- 生产 `POST /api/file/upload/photo` 已复现返回：

```json
{"code":500,"message":"操作失败","data":null}
```

## 诊断记录

- Nacos COS 扫描：`.sce/runbooks/backend-admin-release/records/diagnostics/20260706-141852-cos-bucket-before-change`
- 运行态 COS 诊断：`.sce/runbooks/backend-admin-release/records/diagnostics/20260706-141957-cos-runtime-before-change`
- 三 dataId COS 扫描：`.sce/runbooks/backend-admin-release/records/diagnostics/20260706-142345-cos-full-config-before-change`
- 上传失败后日志诊断：`.sce/runbooks/backend-admin-release/records/diagnostics/20260706-142843-cos-upload-failure-after-smoke`

## 后续执行记录

- 已修改 `kaipaile-server/src/main/resources/application.yml`：

```yaml
tencent:
  cos:
    region: ${TENCENT_COS_REGION:${COS_REGION:}}
    bucket-name: ${TENCENT_COS_BUCKET_NAME:${COS_BUCKET_NAME:}}
```

- 本地编译验证：

```text
cd kaipaile-server && mvn -q -DskipTests compile
exit code: 0
```

- 生产 compose/env 同步记录：
  - `.sce/runbooks/backend-admin-release/records/20260706-143801-backend-env-cos-bucket-rotation.md`
  - 同步键：`TENCENT_COS_REGION / TENCENT_COS_BUCKET_NAME / COS_REGION / COS_BUCKET_NAME`

- backend-only 发布：
  - 发布批次：`20260706-143855-backend-only-cos-bucket-rotation`
  - 远端 helper 结果：`remote backend release helper completed`
  - jar SHA256：`6B94CAF259F74AB67926DE7E96DAF46C3FD7FF92E09944FE961D2F8483A47766`
  - 备注：标准脚本在远端 helper 完成后因本机未配置 `KAIPAI_ADMIN_SMOKE_PASSWORD` 于管理员公网 smoke 阶段退出；后续已执行目标 smoke。
- 发布后运行态诊断：
  - `.sce/runbooks/backend-admin-release/records/diagnostics/20260706-144049-cos-bucket-after-release`
  - 容器已重启并运行。
  - `COS_BUCKET_NAME / COS_REGION / TENCENT_COS_BUCKET_NAME / TENCENT_COS_REGION` 均存在，且两组 bucket / region 一致。
- 公网基础 smoke：

```text
GET https://api.kplyyk.com/api/v3/api-docs -> HTTP 200
```

- 上传 smoke 当前结果：

```json
{"code":400,"message":"文件上传失败","data":null}
```

- COS 直连最小 PUT 测试结果：

```text
PUT https://<configured-bucket>.cos.<configured-region>.myqcloud.com/codex-smoke/... -> 404 NoSuchBucket
```

## 当前阻断

后端配置兼容与生产 env 同步已完成，但当前配置中的 bucket / region 组合在腾讯云 COS 返回 `NoSuchBucket`。需要提供真实存在的新 bucket 名与 region；如果新 bucket 使用了不同腾讯云密钥，也需要通过本地安全来源补齐新 `TENCENT_CLOUD_SECRET_ID / TENCENT_CLOUD_SECRET_KEY`，不要写入聊天或源码。

## 范围调整：先迁移历史对象

用户已在腾讯云控制台创建新 bucket，并要求先进行图片迁移。根据控制台截图，本轮迁移目标调整为：

- source bucket: `kaipai-1412601014`
- target bucket: `kaipai-prod-1412601014`
- region: `ap-shanghai`

迁移策略：

- 先迁移对象，再做生产上传切换。
- 只复制对象，不删除旧 bucket 对象。
- 目标 key 与源 key 保持一致，便于后续按 host 替换或 URL 兼容处理。
- 迁移记录不得输出腾讯云 SecretId / SecretKey。

## 历史对象迁移执行记录

- 迁移脚本：
  - `.sce/runbooks/backend-admin-release/scripts/migrate-cos-bucket-objects.py`
- dry-run 统计记录：
  - `.sce/runbooks/backend-admin-release/records/20260706-163618-cos-bucket-object-migration-dry-run.md`
  - 结果：source bucket 可访问，target bucket 可访问，旧 bucket 共 `332` 个对象，`372.21MB`，failed `0`。
- 单对象正式复制探针：
  - `.sce/runbooks/backend-admin-release/records/20260706-163638-cos-bucket-object-migration-execute.md`
  - 结果：target bucket write/delete smoke passed，复制 `1` 个对象，verified `1`，failed `0`。
- 全量正式迁移记录：
  - `.sce/runbooks/backend-admin-release/records/20260706-164017-cos-bucket-object-migration-execute.md`
  - 结果：listed `332` (`372.21MB`)，copied `331`，skipped `1`，verified `332`，failed `0`。
- 目标 bucket 独立统计记录：
  - `.sce/runbooks/backend-admin-release/records/20260706-164034-cos-bucket-object-migration-dry-run.md`
  - 结果：新 bucket `kaipai-prod-1412601014` 共 `332` 个对象，`372.21MB`。

结论：历史对象已按原 key 从 `kaipai-1412601014` 复制到 `kaipai-prod-1412601014`，源对象未删除。下一步可以继续执行生产 bucket 配置同步、backend-only 发布和 `/api/file/upload/photo` smoke。

## 生产上传最终验证

前序生产配置同步与 backend-only 发布已经完成，生产运行态已指向：

- `TENCENT_COS_BUCKET_NAME=kaipai-prod-1412601014`
- `TENCENT_COS_REGION=ap-shanghai`
- `COS_BUCKET_NAME=kaipai-prod-1412601014`
- `COS_REGION=ap-shanghai`

本轮新 bucket 创建完成并完成对象迁移后，无需再次发布 jar；直接执行生产上传 smoke：

```text
POST https://api.kplyyk.com/api/file/upload/photo -> code=200
returned host: kaipai-prod-1412601014.cos.ap-shanghai.myqcloud.com
DELETE https://api.kplyyk.com/api/file/delete?url=<uploaded-url> -> code=200
GET https://api.kplyyk.com/api/v3/api-docs -> HTTP 200
```

上传 smoke 返回 URL：

```text
https://kaipai-prod-1412601014.cos.ap-shanghai.myqcloud.com/photo/2026/07/06/44971382664c414eae36f6f4268217a5.png
```

该测试对象已通过删除接口清理，删除响应 `code=200`。

日志诊断：

- `.sce/runbooks/backend-admin-release/records/diagnostics/20260706-164342-cos-upload-after-migration`
- 对 `docker-logs.txt` 过滤 `COS 文件上传失败|操作失败|Exception|NoSuchBucket|AccessDenied|Signature`，无匹配结果。

最终结论：

- 历史对象迁移完成：`332` 个对象，`372.21MB`，failed `0`。
- 生产新上传已进入 `kaipai-prod-1412601014`。
- 当前 `NoSuchBucket` / `文件上传失败` 问题已通过新 bucket 创建、对象迁移和运行态 smoke 验证闭环。

## 生产发布：cos-bucket-rotation-final

用户要求发布到生产后，执行标准 backend-only 发布：

- 发布批次：`20260706-165648-backend-only-cos-bucket-rotation-final`
- 发布记录：`.sce/runbooks/backend-admin-release/records/20260706-165648-backend-only-cos-bucket-rotation-final.md`
- jar SHA256：`12D87F19073C92314A1071663032B1962EFDD197A2C512E6A21B6F45718F6588`
- 目标数据库预检：`kaipai_prod`
- 远端 helper 结果：`remote backend release helper completed`

标准脚本在远端 helper 完成后，因本机未配置 `KAIPAI_ADMIN_SMOKE_PASSWORD` 于内置公网 admin smoke 阶段退出；该退出不代表远端部署失败。随后已手工执行目标 smoke：

```text
GET https://api.kplyyk.com/api/v3/api-docs -> HTTP 200
POST https://api.kplyyk.com/api/file/upload/photo -> code=200
returned host: kaipai-prod-1412601014.cos.ap-shanghai.myqcloud.com
DELETE https://api.kplyyk.com/api/file/delete?url=<uploaded-url> -> code=200
GET https://api.kplyyk.com/api/verify/status -> code=200
```

日志诊断：

- `.sce/runbooks/backend-admin-release/records/diagnostics/20260706-165913-cos-bucket-production-release-post-smoke`
- 对 `docker-logs.txt` 过滤 `COS 文件上传失败|操作失败|Exception|NoSuchBucket|AccessDenied|Signature`，无匹配结果。
