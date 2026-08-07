# 00-198 当前阶段 AI 分享图腾讯 OCR 无文字质检修复 - 执行记录

## 当前状态

- 状态：`completed-production-verified`
- 日期：`2026-07-21`
- 范围：后端 Tencent OCR 质量门语义修复与生产 backend-only 发布。

## 生产问题证据

- 用户：`userId=4`
- 任务：`aipf_a11b4df10cf349f7a9104d245344e4de`
- 创建时间：`2026-07-21 20:46:24 +0800`
- 完成时间：`2026-07-21 20:46:49 +0800`
- provider/model：`tencent-hunyuan / hunyuan-image-3.0`
- 终态：`failed`
- failure reason：`FailedOperation.ImageNoText / 照片中未检测到文本`
- `generated_image_url=NULL`
- `share_card_id=NULL`

## 根因

- 新腾讯生产密钥和 Provider 测试已成功，排除鉴权和混元生图故障。
- `resolveGeneratedImageUrl(...)` 在 OCR 前已经把生成图上传 COS。
- `TencentOcrAiProfileCardImageQualityInspector.callTencent(...)` 把所有 `/Response/Error` 统一抛异常。
- `inspectCover(...)` 只识别 `UnOpenError`，没有识别 `ImageNoText`。
- 异常进入 `AiProfileCardServiceImpl` 普通质量重试，默认最多 3 次，最终 markFailed。

## 目标修复

只把结构化 Error.Code 精确等于 `FailedOperation.ImageNoText` 的响应映射为 `accept()`；其他 OCR 行为保持不变。

## 实现与验证证据

- TDD 红灯：inspector 定向测试共 `6` 条，结果为 `2 failures / 1 error`；3 条新合同用例均精确失败于 `inspectTencentResponse(JsonNode)` 尚不存在。
- 精确映射：新增 `inspectTencentResponse(...)`，仅 `FailedOperation.ImageNoText` 返回 `accept()`；Message、相邻错误码和近似错误码均不参与放行。
- 正常响应保护：空 `TextDetections` 继续 accepted/non-retryable；高置信文字继续 rejected/retryable。
- 定向绿灯：`TencentOcrAiProfileCardImageQualityInspectorTest` 共 `8/8` 通过。
- 相关回归：inspector `8` 条 + `AiProfileCardServiceImplTest` `6` 条，共 `14/14` 通过。
- 构建：`mvn -q -DskipTests clean package` 退出码为 `0`。
- 本地候选 JAR：`target/kaipai-backend-1.0.0-SNAPSHOT.jar`，大小 `92175737` bytes。
- 本地候选 JAR SHA-256：`94A27F80E76BD741F42F3036DDE2049EEB069B6D8E3D17BA64A7488D3CEB3980`。
- 审查：TDD 规格、TDD 质量、实现规格、实现质量和最终 bug/security/scope 审查均通过；未发现凭据写入或宽泛 `FailedOperation` 放行。

## 发布门禁

- SSH key、远端 helper、生产容器、`prod` profile 和 `kaipai_prod` 数据源已只读核验。
- 标准发布命令必须显式传 `--mysql-database kaipai_prod`。
- 当前环境未设置 `KAIPAI_ADMIN_SMOKE_PASSWORD`，因此未直接运行会在部署后失败的标准脚本。
- 用户已明确授权复用当前已登录 Chrome 后台会话执行 browser-authenticated UI smoke 偏差；后台已只读确认正式导航、`admin` 登录态、腾讯混元当前主模型、配置完整、密钥已配置和最近一次测试生成成功。
- 偏差发布仍必须复用标准脚本的 precheck/build/upload/helper 函数，且不得读取或输出密码、token、cookie、SecretId 或 SecretKey。

## 待执行

- 无。本 Spec 已完成实现、发布和真实用户任务验收。

## 生产发布

- release id：`20260721-220846-backend-only-tencent-ocr-image-no-text-fix`
- release record：`.sce/runbooks/backend-admin-release/records/20260721-220846-backend-only-tencent-ocr-image-no-text-fix.md`
- source mode：`git_head_snapshot_with_overlay`
- 数据库：`kaipai_prod`
- helper：`passed`
- 发布/上传/运行时/容器 JAR SHA-256：`B794FE114CA2A6CC03863972AF43C4B6B20177EF2068A74F752C154D253411A8`，四处一致。
- 备份：`/opt/kaipai/backups/releases/20260721-220846-backend-only-tencent-ocr-image-no-text-fix/backend`
- 运行态：`prod / NACOS_ENABLED=true / SERVER_PORT=8080`，容器 running、restart count 0。
- API smoke：内外网 docs `200`；招聘/演员角色 `401` 且 non-5xx。
- browser smoke：发布后 Chrome 保持 admin 登录态；AI 生图配置页仍显示腾讯混元当前主模型、配置完整、密钥已配置；分享内容鉴权页成功加载 10 条数据。
- 偏差：未执行 password credential login smoke，未读取任何浏览器凭据；详见 release record。
- 诊断：`.sce/runbooks/backend-admin-release/records/diagnostics/20260721-221355-tencent-ocr-image-no-text-post-release/`。

## 发布后业务验收

- 新任务：`aipf_6ea0d362ed7d409ebd66ac50fa4f0263`
- 用户：`userId=4`
- 创建/完成：`2026-07-21 22:24:41 / 22:24:50 +0800`
- 终态：`success`
- provider/model：`tencent-hunyuan / hunyuan-image-3.0`
- failure reason：空。
- generated image URL：非空；HEAD `200`、Range GET `206`、`image/png`、PNG signature 正确、大小 `2771360` bytes。
- share card：`share_card_id=24`，记录存在、属于 `userId=4`、状态 active。
- actor card config：`config_id=19`，记录存在，配置包含本次生成图。
- share preference：`preference_id=16 / poster`。
- 图片视觉检查：非空、主体正常、无可读文字覆盖。
- 业务日志窗口原始日志为空，未作为成功证明；最终判断以数据库关联和真实图片响应为准。
- 历史失败任务 `aipf_a11b4df10cf349f7a9104d245344e4de` 保持不变。
