# 当前阶段腾讯云身份证二要素实名认证接入 Requirements

> 状态：执行中 | 优先级：P0 | 依赖：`00-176`、`05-09`

## 1. 概述

腾讯云身份证二要素核验已购买，本轮把小程序现有实名认证提交链路从“提交后纯人工审核”升级为“后端调用腾讯云 `IdCardOCRVerification` 自动核验 + 人工审核兜底”。

本轮只接入身份证二要素核验，不接手机号三要素，不接小程序人脸核身，不恢复短信登录能力。

## 2. 用户故事

- 作为演员，我提交真实姓名和身份证号后，希望平台能自动完成权威核验，通过后立即获得实名状态。
- 作为运营人员，我希望腾讯云异常或配置未就绪时，现有后台人工审核链路仍可处理申请。
- 作为平台维护者，我希望身份证明文不进入日志或前端，数据库同时具备密文、哈希和脱敏展示值。

## 3. 功能需求

### 3.1 腾讯云二要素自动核验

**描述**：`POST /api/verify/submit` 在通过本地校验、重复身份证检查、档案完成度检查后，调用腾讯云实名核身 `IdCardOCRVerification`。本轮只传 `Name + IdCard` 做身份证二要素一致性核验，不上传身份证图片。

**验收标准**：

1. WHEN 腾讯云返回 `Result = "0"` THEN 本次认证记录直接置为通过，用户 `realAuthStatus=2`，演员档案 `isCertified=true`，并触发现有邀请资格联动。
2. WHEN 腾讯云返回 `Result = "-1"` THEN 本次认证记录置为拒绝，用户 `realAuthStatus=3`，返回用户可理解的认证失败状态。
3. WHEN 腾讯云返回 `Result = "-2"` 或 `"-3"` THEN 后端按明确失败处理，不进入待审核。
4. WHEN 腾讯云返回 `Result = "-4"`、`"-5"`、`"-6"`、`"-7"` 或调用异常 THEN 本次认证记录保留为待审核，用户 `realAuthStatus=1`，由后台人工兜底。
5. WHEN 腾讯云配置缺失且 provider mode 为 `tencent` THEN 本次认证记录保留为待审核，不把配置错误暴露给小程序用户。

### 3.2 保持小程序接口不变

**描述**：小程序继续提交 `realName + idCardNo` 到现有 `/api/verify/submit`。

**验收标准**：

1. WHEN 前端提交认证 THEN 不直接调用腾讯云 API。
2. WHEN 提交成功 THEN 前端仍使用现有 `IdentityVerification` 状态模型展示 `status=1/2/3`。
3. WHEN 自动通过 THEN 小程序刷新实名状态后可看到已认证。
4. WHEN 进入人工兜底 THEN 小程序继续展示审核中。

### 3.3 身份证存储语义修正

**描述**：修正当前 `id_card_no_cipher` 实际保存脱敏值的问题，新增脱敏字段并让 `id_card_no_cipher` 保存后端加密值。

**验收标准**：

1. WHEN 新提交认证 THEN `identity_verification.id_card_no_cipher` 不再保存可读身份证号或脱敏身份证号。
2. WHEN 新提交认证 THEN `identity_verification.id_card_no_masked` 保存前 3 后 4 的脱敏身份证号。
3. WHEN 新提交认证 THEN `identity_verification.id_card_hash` 继续作为去重哈希，不可逆。
4. WHEN 前端和后台读取认证状态 THEN 只返回脱敏身份证号。
5. WHEN 日志、operation log 或异常信息记录认证结果 THEN 不出现完整身份证号。

### 3.4 服务商结果留痕

**描述**：实名认证记录保存腾讯云核验结果，支持后台回看和排障。

**验收标准**：

1. WHEN 调用腾讯云成功或失败 THEN 记录 `provider_code`、`provider_request_id`、`provider_result_code`、`provider_result_message`、`provider_verified_at`。
2. WHEN 记录进入人工审核兜底 THEN 后台详情可看到服务商结果摘要。
3. WHEN 运营执行人工通过或拒绝 THEN 现有后台审核权限和操作留痕仍生效。

### 3.5 配置与降级

**描述**：实名 provider 由后端配置控制，默认保留人工兜底安全边界。

**验收标准**：

1. WHEN `KAIPAI_REALNAME_PROVIDER_CODE=tencent` 且腾讯云配置完整 THEN 调用腾讯云二要素。
2. WHEN `KAIPAI_REALNAME_PROVIDER_CODE=manual` THEN 不调用腾讯云，保持现有人工审核模式。
3. WHEN 腾讯云 API HTTP 非 2xx、返回 `Response.Error` 或请求超时 THEN 不抛出完整供应商错误给小程序，记录摘要后进入人工兜底。

## 4. 非功能需求

- 前端不得保存或暴露腾讯云密钥。
- 后端日志不得打印完整身份证号、腾讯云 SecretId 或 SecretKey。
- 供应商调用超时必须有限制，不能阻塞提交接口过久。
- 新增代码必须有单测覆盖腾讯云成功、不一致、异常兜底和配置缺失。
- 本轮不引入人脸核身 SDK 或小程序插件。

## 5. 约束条件

- 继续遵守 `05-09`：档案完成度小于 70% 不允许提交。
- 继续遵守身份证号后端加密存储、前端只展示脱敏值。
- `identity_verification_owner` 的跨账号身份证占用逻辑继续基于哈希保留。
- 腾讯云真实密钥只能来自服务器环境变量、Nacos 或 gitignored 本地 secret，不进入仓库。

## 6. 验收总则

1. 腾讯云二要素一致样本可自动通过实名认证。
2. 腾讯云二要素不一致样本不会进入人工待审核。
3. 腾讯云异常样本仍进入人工审核兜底。
4. 小程序接口和主要页面无需改造即可展示新状态。
5. 后端编译、后端单测、小程序类型检查通过。
