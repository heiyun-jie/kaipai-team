# 00-198 当前阶段 AI 分享图腾讯 OCR 无文字质检修复

## 1. 概述

生产 `userId=4` 在腾讯混元 Provider 与新生产密钥均已验证成功后，于 `2026-07-21 20:46:24 +0800` 创建任务 `aipf_a11b4df10cf349f7a9104d245344e4de`。任务已完成混元生图、图片下载和 COS 持久化，但后置腾讯 OCR 返回：

```text
FailedOperation.ImageNoText
照片中未检测到文本
```

当前代码把所有 `/Response/Error` 统一抛为异常，导致“未检测到文字”被误判为质检失败，并进入默认最多 3 次的封面重新生成，最终任务失败且不创建分享卡。

本 Spec 只修复腾讯 OCR 精确错误码的语义映射：`FailedOperation.ImageNoText` 表示图片没有可读文字，恰好满足 AI 分享图背景质量门，应直接通过且不得重试。

## 2. 用户故事

- 作为演员用户，我希望没有文字的 AI 分享图通过质检并形成可分享作品，而不是被错误判定为失败。
- 作为维护者，我希望只放行腾讯 OCR 的精确“无文字”错误码，其他 OCR 错误继续 fail-closed。
- 作为维护者，我希望无文字结果不触发额外混元调用和 COS 上传，避免重复成本与孤立图片。
- 作为维护者，我希望历史失败任务保持原样，新代码只影响发布后的新任务。

## 3. 功能需求

### 3.1 精确无文字语义

**描述**：腾讯 OCR `/Response/Error/Code` 精确等于 `FailedOperation.ImageNoText` 时，质量门必须把结果解释为没有检测到可读文字。

**验收标准**：

1. WHEN Error.Code 精确等于 `FailedOperation.ImageNoText` THEN 返回 `accepted=true`。
2. WHEN 结果因无文字通过 THEN `retryable=false`。
3. WHEN Error.Message 文案变化但 Error.Code 不变 THEN 仍按精确 Code 通过。
4. WHEN 只出现相似 Message、相邻错误码或其他 `FailedOperation.*` THEN 不得放行。

### 3.2 其他 OCR 语义保持

**描述**：本轮不得放宽既有文字拦截和服务异常边界。

**验收标准**：

1. WHEN 正常响应包含高置信中文或 ASCII 单词 THEN 继续返回 rejected，并允许既有受控重试。
2. WHEN Error.Code 为 `FailedOperation.UnOpenError` 或明确表示服务未开通 THEN 继续返回 unavailable、non-retryable。
3. WHEN 腾讯返回其他业务错误、HTTP 非 2xx、响应解析异常或调用异常 THEN 继续 fail-closed。
4. WHEN 正常响应的 `TextDetections` 为空 THEN 继续通过。

### 3.3 任务成功链路

**描述**：无文字质检通过后，任务必须继续执行单封面成功链路。

**验收标准**：

1. WHEN 第一张生成图得到 `ImageNoText` THEN 不得再次调用混元生图。
2. WHEN 无文字质检通过 THEN 继续保存 `generated_image_url`。
3. WHEN 无文字质检通过 THEN 继续创建或复用分享卡并写入 `share_card_id`。
4. WHEN 后续保存成功 THEN 任务状态更新为 `success`，不得保留 OCR 错误为 failure_reason。

### 3.4 历史与数据边界

**描述**：本轮只修复发布后的运行态，不改历史失败数据。

**验收标准**：

1. 不修改 `aipf_a11b4df10cf349f7a9104d245344e4de` 或更早失败任务。
2. 不伪造历史 `generated_image_url`、`share_card_id` 或 success 状态。
3. 不在本轮删除质检误判期间可能产生的孤立 COS 对象。
4. 不修改腾讯混元 Provider、密钥、endpoint、model 或 active 状态。

### 3.5 发布与生产验证

**描述**：修复必须通过后端测试、构建、标准生产发布和真实用户任务验证。

**验收标准**：

1. Tencent OCR inspector 定向测试通过。
2. AI 分享图 service 相关测试通过。
3. 后端 clean package 通过。
4. backend-only 发布到 `101.43.57.62`，目标数据库门禁显式使用 `kaipai_prod`。
5. 发布后 `userId=4` 新任务使用 `tencent-hunyuan / hunyuan-image-3.0` 并最终 success。
6. 新任务 `generated_image_url` 与 `share_card_id` 非空，关联分享卡和演员卡配置存在，图片 URL 可访问。

## 4. 非功能需求

- 只按结构化 Error.Code 判定，不依赖中英文 Message 模糊匹配。
- 不新增重试次数、不关闭质量门、不放宽文字置信度阈值。
- 不改变实名门禁、源图门禁、Provider 路由或分享卡 DTO 合同。
- 生产发布必须保留发布前 JAR 备份和可回滚路径。

## 5. 验收总则

- `FailedOperation.ImageNoText` 被视为无文字通过。
- 其他腾讯 OCR 错误仍然失败或 unavailable。
- 无文字结果只生成一次并继续完成分享卡成功链路。
- 定向测试、相关测试、构建、发布和真实生产任务证据完整。
