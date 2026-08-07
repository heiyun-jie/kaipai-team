# 00-198 当前阶段 AI 分享图腾讯 OCR 无文字质检修复 - 技术设计

## 1. 设计结论

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

采用精确错误码映射，不关闭 OCR，不改变重试框架：

```text
Tencent GeneralBasicOCR response
  -> HTTP / JSON transport
  -> inspectTencentResponse(root)
     -> Error.Code == FailedOperation.ImageNoText: accept
     -> other Error: existing BizException
     -> blocked TextDetections: rejected / retryable
     -> no blocked text: accept
```

`FailedOperation.ImageNoText` 不归入 unavailable。`unavailable` 的现有合同是 `accepted=false / retryable=false`，仍会让任务失败；本错误必须直接返回 `accept()`。

## 2. 根因与数据流

当前链路：

```text
promptAgent.generate
  -> resolveGeneratedImageUrl
  -> upload to COS
  -> TencentOcrAiProfileCardImageQualityInspector.inspectCover
  -> callTencent sees /Response/Error
  -> throws BizException(ImageNoText)
  -> AiProfileCardServiceImpl treats it as retryable runtime error
  -> up to 3 cover generations
  -> markFailed
```

目标链路：

```text
promptAgent.generate
  -> upload to COS
  -> OCR Error.Code=FailedOperation.ImageNoText
  -> accept
  -> createOrGetGeneratedShareCard
  -> saveGeneratedShareCardConfig
  -> markSuccess(generatedImageUrl, shareCardId)
```

## 3. 后端实现

### 3.1 响应解释边界

修改：

`kaipaile-server/src/main/java/com/kaipai/service/ai/profilecard/TencentOcrAiProfileCardImageQualityInspector.java`

新增单一职责方法：

```java
private AiProfileCardImageQualityInspection inspectTencentResponse(JsonNode root)
```

该方法负责：

1. 读取 `/Response/Error`。
2. 精确读取 `error.path("Code").asText("")`。
3. Code 为 `FailedOperation.ImageNoText` 时返回 `AiProfileCardImageQualityInspection.accept()`。
4. 其他 Error 保持既有 `BizException("腾讯 OCR API 错误：...")`。
5. 无 Error 时复用 `extractBlockedSnippets(root)`，有文字 rejected，无文字 accept。

`callTencent(...)` 只保留 HTTP、签名、响应状态和 JSON 解析，不再解释腾讯业务错误。

### 3.2 错误矩阵

| 腾讯结果 | inspection | retry | 任务结果 |
|---|---|---|---|
| `FailedOperation.ImageNoText` | accepted | 否 | 继续成功链路 |
| 正常响应、无文字 | accepted | 否 | 继续成功链路 |
| 正常响应、高置信文字 | rejected | 是 | 受控重新生成 |
| `FailedOperation.UnOpenError` | unavailable | 否 | fail-closed |
| 其他 Error | exception | 既有规则 | fail-closed / 重试耗尽 |

### 3.3 非改动边界

- 不修改 `AiProfileCardImageQualityInspection` 的 accepted/retryable 合同。
- 不修改 `AiProfileCardServiceImpl` 的重试循环。
- 不修改默认 `cover-quality-max-attempts=3`。
- 不修改 Provider、密钥、COS 或分享卡持久化实现。

## 4. 测试设计

修改：

`kaipaile-server/src/test/java/com/kaipai/module/server/ai/profilecard/TencentOcrAiProfileCardImageQualityInspectorTest.java`

新增测试：

1. `imageNoTextResponseShouldBeAccepted()`：精确 Code 返回 accepted 且 non-retryable。
2. `otherTencentApiErrorShouldRemainFailure()`：相邻/未知错误继续抛 `BizException`。
3. `emptyTextDetectionsShouldBeAccepted()`：正常空检测结果继续通过。

保留既有：

- OCR 未配置 unavailable。
- 高置信中文/ASCII 文字拦截。
- `UnOpenError` unavailable。

执行：

```powershell
cd kaipaile-server
mvn -q -Dtest=TencentOcrAiProfileCardImageQualityInspectorTest test
mvn -q -Dtest=TencentOcrAiProfileCardImageQualityInspectorTest,AiProfileCardServiceImplTest test
mvn -q -DskipTests clean package
```

## 5. 发布设计

使用标准 backend-only 发布脚本，显式覆盖生产数据库与本轮文件：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py `
  --label tencent-ocr-image-no-text-fix `
  --operator codex `
  --host 101.43.57.62 `
  --public-base-url https://api.kplyyk.com `
  --mysql-database kaipai_prod `
  --overlay-path src/main/java/com/kaipai/service/ai/profilecard/TencentOcrAiProfileCardImageQualityInspector.java `
  --overlay-path src/test/java/com/kaipai/module/server/ai/profilecard/TencentOcrAiProfileCardImageQualityInspectorTest.java
```

发布前默认必须确认 `KAIPAI_ADMIN_SMOKE_PASSWORD` 已通过安全环境变量配置；若缺失，必须在上传/部署前停止，不允许直接运行标准脚本并在部署后形成 release record 缺失的半完成状态。

本批次用户于 `2026-07-21` 明确授权复用已登录 Chrome 后台会话。作为一次性、留档的 browser-smoke 偏差，可执行以下等价门禁：

1. 不读取浏览器密码、cookie、local storage、token 或任何腾讯/后台密钥。
2. 复用标准脚本的 DNS、SSH key、helper、clean HEAD + overlay、`kaipai_prod` schema history、构建、上传和 `deploy_backend_only(...)` 函数。
3. 不调用依赖密码的 `public_smoke(...)`，也不调用会宣称标准登录 smoke 已通过的 `write_record(...)`。
4. 公网实际执行 API Docs、招聘角色和演员角色非 5xx 探针，并在已登录 Chrome 中重新加载生产后台，验证正式导航、AI 生图配置和腾讯混元配置数据正常。
5. 单独生成 browser-authenticated UI smoke 偏差发布记录，明确 `POST /api/admin/auth/login` 未重放，不得伪造 status 或回包。
6. helper、runtime 和 container JAR SHA 必须一致，且必须保留备份路径和回滚入口。

## 6. 生产验收与回滚

发布后：

1. 回读容器/JAR SHA 和基础 smoke。
2. 用户重新创建 AI 分享图任务。
3. 查询 `userId=4` 最新任务、分享卡和演员卡配置。
4. HEAD/GET 验证生成图 URL 可访问。
5. 日志中不得再出现该任务的 `FailedOperation.ImageNoText` 失败栈。

如发布后出现回归，使用发布记录中的备份 JAR 通过同一 helper 受控恢复，并重新执行 smoke；不得修改历史任务状态作为回滚手段。
