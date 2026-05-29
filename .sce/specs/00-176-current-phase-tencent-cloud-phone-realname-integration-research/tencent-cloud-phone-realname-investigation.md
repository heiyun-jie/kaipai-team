# 腾讯云手机号与实名认证服务接入调研

> 调研日期：2026-05-28  
> 调研范围：腾讯云短信 SMS、腾讯云实名核身身份证/手机号要素核验、腾讯云实名核身小程序人脸核身。  
> 本文只形成实现前文档，不代表已开通、已配置或已发布。

## 1. 先回答三个问题

### 1.1 现在要接什么？

当前项目真正需要拆成两类服务：

1. 手机号验证码短信：用于未来恢复 `pages/login/index` 的手机号验证码登录 / 注册入口，推荐对接腾讯云短信 SMS。
2. 实名认证核验：用于把当前 `05-09` 的人工审核升级为服务商核验，推荐先接腾讯云实名核身的身份证二要素或手机号三要素；人脸核身作为更高等级能力独立排期。

不建议把腾讯云 App 号码认证当作当前微信小程序登录入口。当前小程序手机号一键登录已经由微信 `getPhoneNumber` 和 `00-173` 承接。

### 1.2 现有系统缺什么？

当前缺口不是页面或基础状态机，而是生产级供应商能力和配置门禁：

- `/api/auth/sendCode` 仍是开发态：后端生成验证码、写 Redis，并把验证码直接返回给调用方。
- `00-174` 已隐藏短信登录表单；正式短信接入完成后，还要单独恢复登录页入口。
- 实名认证已有提交、状态、后台审核和邀请联动。
- 实名认证当前第三方核验未接入；`id_card_no_cipher` 当前实际保存脱敏值，不是真正可解密密文，需要在实名服务商接入前修正。

### 1.3 推荐怎么做？

推荐分三阶段：

1. P0：接腾讯云 SMS，把 `sendCode` 改成正式短信通道，但不立即恢复登录页短信表单。
2. P1：接腾讯云实名核身二要素或三要素，把 `verify/submit` 从“提交后人工审核”升级为“服务商核验 + 人工兜底”。
3. P2：如业务必须确认本人操作，再接腾讯云小程序人脸核身。不要和 P0 / P1 混在一个 Spec 里做。

## 2. 已有 Spec 与代码事实

### 2.1 相关 Spec

| Spec | 当前结论 | 对本次影响 |
|------|----------|------------|
| `00-51 current-phase-formal-sms-capability-deferral` | 正式短信能力已被降级为 future batch；开发态 `sendCode` 不再阻塞当前登录主线。 | 腾讯云 SMS 应新建独立实现 Spec。 |
| `00-173 current-phase-wechat-phone-login-enablement` | 微信手机号一键登录已启用，前端通过 `getPhoneNumber` code 调 `/api/auth/wechat-login`。 | 不应再用腾讯云号码认证替代微信小程序手机号授权。 |
| `00-174 current-phase-login-sms-review-gate` | 验证码登录入口在审核前从登录页可见层退出。 | SMS 接入完成后，还需独立 Spec 恢复入口。 |
| `05-09 identity-verification` | 初期实名认证为姓名 + 身份证提交，后台人工审核；第三方 API 是后续扩展。 | 腾讯云实名核验应增强现有 `verify/submit` 和后台审核链。 |
| `00-131 current-phase-admin-verify-history-route-alignment` | 后台已补 `/verify/history` hidden tooling 路由。 | 第三方核验结果应能进入历史记录和后台回看。 |

### 2.2 当前登录代码事实

后端：

- 控制器：`kaipaile-server/src/main/java/com/kaipai/module/controller/auth/AuthController.java`
- 服务：`kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java`
- 当前 `sendCode(phone)`：
  - 随机生成 6 位验证码。
  - Redis key：`sms:code:{phone}`。
  - TTL：5 分钟。
  - 开发态直接返回验证码。

因此正式 SMS 接入的最小改造点是：

- 保留验证码生成、Redis TTL、`login/register` 校验。
- 替换发送通道。
- 生产态接口不返回验证码。
- 增加频控、审计和失败处理。

### 2.3 当前实名认证代码事实

后端：

- 前台接口：`/api/verify/status`、`/api/verify/submit`
- 后台接口：`/api/admin/verify/list`、`/api/admin/verify/{id}`、`approve`、`reject`
- 服务：`IdentityVerificationServiceImpl`
- 表：
  - `identity_verification`
  - `identity_verification_owner`

当前能力：

- 同一用户不能重复提交待审核记录。
- 已通过后不能重复提交。
- 身份证号通过 SHA-256 哈希做跨账号占用。
- 提交前检查演员档案完成度 >= 70。
- 审核通过后同步：
  - `user.real_auth_status = 2`
  - `actor_profile.is_certified = true`
  - 邀请资格联动。

需要注意的差距：

- `identity_verification.id_card_no_cipher` 字段注释是 encrypted id card number，但当前实现写入的是脱敏身份证号。
- `05-09` 要求“身份证号后端加密存储，前端展示脱敏值”；后续接腾讯云实名前应先修正为：密文、哈希、脱敏展示三个字段或三种语义清晰的值。

## 3. 腾讯云手机号服务选择

### 3.1 腾讯云短信 SMS

适用场景：

- 发送登录 / 注册验证码。
- 未来恢复手机号验证码登录入口。
- 与当前 `/api/auth/sendCode -> /api/auth/login / register` 模型最匹配。

腾讯云 SMS `SendSms` API 的核心参数包括。注意：腾讯云短信不同 API 版本的字段大小写不同，当前国内短信 `2019-07-11` 文档使用 `SmsSdkAppid / Sign / TemplateID`；若后续改用新版本或国际短信，以最终 SDK 生成代码为准。

| 参数 | 项目含义 |
|------|----------|
| `SmsSdkAppid` | 短信应用 ID |
| `Sign` | 已审核通过的短信签名，国内短信必填 |
| `TemplateID` | 已审核通过的短信正文模板 |
| `TemplateParamSet` | 模板变量，例如验证码、有效分钟数 |
| `PhoneNumberSet` | 目标手机号，按 E.164 格式，如 `+8613812345678` |
| `SessionContext` | 可选，用于透传业务上下文 |

项目需要的运行配置：

```yaml
kaipai:
  sms:
    provider-code: tencent
    code-ttl-minutes: 5
    tencent:
      secret-id: ${TENCENT_CLOUD_SECRET_ID:}
      secret-key: ${TENCENT_CLOUD_SECRET_KEY:}
      region: ${TENCENT_SMS_REGION:ap-guangzhou}
      sms-sdk-app-id: ${TENCENT_SMS_SDK_APP_ID:}
      sign-name: ${TENCENT_SMS_SIGN_NAME:}
      login-template-id: ${TENCENT_SMS_LOGIN_TEMPLATE_ID:}
```

实现建议：

- 新增 `SmsCodeSender` 接口。
- 保留 `dev` provider：仅本地开发可返回验证码。
- 新增 `TencentSmsCodeSender`：调用腾讯云 `SendSms`。
- `AuthServiceImpl.sendCode` 改为：
  1. 生成验证码。
  2. 先做频控。
  3. 写 Redis。
  4. 调短信 provider。
  5. 生产态返回 `void` 或空 data，不返回验证码。
  6. 供应商失败时删除本次 Redis code，避免用户拿不到短信却存在可用验证码。

必须新增的风控：

- 单手机号分钟级 / 小时级频控。
- 单 IP / 设备指纹频控。
- 同一手机号每日总量。
- 失败次数过多进入冷却。
- 日志只记录手机号哈希或脱敏值，不记录验证码。

建议新增发送日志表：

```sql
CREATE TABLE auth_sms_send_log (
  sms_log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  phone_hash CHAR(64) NOT NULL,
  phone_masked VARCHAR(32) NOT NULL,
  scene VARCHAR(32) NOT NULL,
  provider_code VARCHAR(32) NOT NULL,
  request_id VARCHAR(128),
  serial_no VARCHAR(128),
  send_status VARCHAR(64),
  error_code VARCHAR(128),
  error_message VARCHAR(512),
  client_ip VARCHAR(64),
  device_fingerprint VARCHAR(128),
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 腾讯云 App 号码认证

腾讯云号码认证通常用于 App 端本机号码校验 / 一键登录。当前项目的主平台是微信小程序，且 `00-173` 已使用微信 `getPhoneNumber` 获取手机号授权 code。

本项目当前不推荐把它作为登录入口主线，原因：

- 小程序已有微信原生手机号授权入口。
- 当前登录页已经按微信能力审核和短信门禁治理。
- 再接 App 号码认证会产生第三条登录通道，增加审核、运行态和用户态复杂度。

保留判断：

- 如果后续发布独立 App，而不是微信小程序，再重新评估腾讯云号码认证。
- 如果只是微信小程序，不进入当前接入范围。

### 3.3 腾讯云实名核身手机号要素核验

手机号三要素核验不是短信服务。它通常用于核验手机号、姓名、身份证是否匹配，可作为实名认证增强项。

适用场景：

- 用户已登录且手机号已绑定。
- 实名提交时要求“当前登录手机号与身份证姓名一致”。
- 比身份证二要素多一层手机号归属一致性。

不适用：

- 不用于发送验证码。
- 不替代 `/api/auth/sendCode`。
- 不替代微信 `getPhoneNumber`。

## 4. 腾讯云实名认证服务选择

### 4.1 方案 A：身份证二要素核验

流程：

```text
用户提交 realName + idCardNo
  -> 后端本地格式校验
  -> 后端调用腾讯云身份证二要素核验
  -> 通过：写入实名通过状态
  -> 不通过：写入失败状态或转人工复核
  -> 供应商异常：保留待审核，由后台人工处理
```

优点：

- 接入改动小。
- 不需要前端增加人脸核身流程。
- 与当前 `05-09` 表单模型最贴合。

缺点：

- 只能证明姓名和身份证信息匹配，不能证明当前操作者本人活体。
- 对高风险业务可能不够。

建议作为 P1 首选，前提是产品接受“非活体实名”。

### 4.2 方案 B：手机号三要素核验

流程：

```text
用户已登录，系统已知 phone
  -> 用户提交 realName + idCardNo
  -> 后端调用手机号 + 姓名 + 身份证三要素核验
  -> 通过：实名通过
  -> 不通过：失败或人工复核
```

优点：

- 能把登录手机号和实名身份绑定起来。
- 对邀请、名片、联系请求这类平台信任链更有意义。

缺点：

- 依赖当前账号手机号真实、可用。
- 对微信手机号授权失败、手机号变更等场景要额外设计。
- 仍不等于活体核身。

建议：

- 如果成本和产品规则允许，P1 可直接选择三要素替代二要素。
- 若需要兼容非手机号账号或历史数据，先二要素，再逐步增加三要素。

### 4.3 方案 C：小程序人脸核身

腾讯云实名核身支持小程序端发起核身流程，通常是：

```text
前端请求后端创建核身任务
  -> 后端调用腾讯云 DetectAuth 获取 BizToken
  -> 小程序端使用 BizToken 调起核身流程
  -> 用户完成活体 / 人脸 / 证件核验
  -> 后端调用 GetDetectInfoEnhanced 查询结果
  -> 写入实名状态
```

优点：

- 能证明本人活体参与，信任等级最高。
- 适合高风险身份、提现、商务联系等场景。

缺点：

- 前端、小程序授权、域名、资质、用户体验和失败恢复都更复杂。
- 需要处理用户中途退出、SDK 错误、结果轮询或回跳。
- 可能需要更长审核和配置周期。

建议：

- 不和短信 SMS 同批实现。
- 只有当产品明确要求“活体实名”时新建独立 Spec。
- 当前演员名片与邀请体系可先从二要素 / 三要素开始。

## 5. 推荐落地路线

### 5.1 P0：腾讯云 SMS 正式短信通道

目标：

- `/api/auth/sendCode` 不再开发态直返验证码。
- 能真实发送验证码短信。
- 保留 `00-174` 登录页短信入口隐藏，直到短信模板和小程序审核都闭环。

后续 Spec 范围：

- 后端 SMS provider。
- 配置门禁。
- 发送频控。
- 发送日志。
- 单测和真实 smoke。

不包含：

- 恢复登录页短信入口。
- 改实名。
- 改微信登录。

### 5.2 P1：腾讯云实名核身二要素 / 三要素

目标：

- `verify/submit` 接服务商核验。
- 通过时自动认证。
- 不通过时明确失败原因或进入人工复核。
- 供应商异常时保留人工审核兜底。
- 修正身份证密文存储语义。

推荐状态机：

| 场景 | 记录状态 | 用户态 | 后台 |
|------|----------|--------|------|
| 供应商通过 | approved | `realAuthStatus=2` | 记录 provider result |
| 供应商明确不一致 | rejected | `realAuthStatus=3` | 可查看错误码和脱敏原因 |
| 供应商异常 / 超时 | pending | `realAuthStatus=1` | 人工审核处理 |
| 命中重复身份证 | 拒绝提交 | 不变 | 不新增记录或记录风控事件 |

新增字段建议：

```sql
ALTER TABLE identity_verification
  ADD COLUMN provider_code VARCHAR(32) DEFAULT NULL COMMENT 'tencent/manual',
  ADD COLUMN provider_request_id VARCHAR(128) DEFAULT NULL,
  ADD COLUMN provider_result_code VARCHAR(64) DEFAULT NULL,
  ADD COLUMN provider_result_message VARCHAR(255) DEFAULT NULL,
  ADD COLUMN provider_verified_at DATETIME DEFAULT NULL,
  ADD COLUMN id_card_no_cipher_v2 VARCHAR(1024) DEFAULT NULL COMMENT 'real encrypted id card';
```

如果要彻底修正语义，建议改为：

- `id_card_no_cipher`：真正密文。
- `id_card_masked`：脱敏展示值。
- `id_card_hash`：不可逆去重。

### 5.3 P2：腾讯云小程序人脸核身

目标：

- 用户端完成活体核身。
- 后端只信任腾讯云结果查询，不信任前端自报成功。

后续 Spec 应覆盖：

- 小程序端核身 SDK / 插件接入方式。
- `DetectAuth` 创建任务接口。
- `BizToken` 生命周期。
- `GetDetectInfoEnhanced` 结果查询。
- 用户中断 / 拒绝 / 超时恢复。
- 后台回看核身结果。

## 6. 配置清单

### 6.1 通用腾讯云配置

```text
TENCENT_CLOUD_SECRET_ID
TENCENT_CLOUD_SECRET_KEY
```

约束：

- 只能存在于服务器环境变量、Nacos 或 gitignored 本地 secret 文件。
- 不进入前端。
- 不进入仓库。
- 不写入日志。

### 6.2 SMS 配置

```text
TENCENT_SMS_REGION=ap-guangzhou
TENCENT_SMS_SDK_APP_ID
TENCENT_SMS_SIGN_NAME
TENCENT_SMS_LOGIN_TEMPLATE_ID
TENCENT_SMS_CODE_TTL_MINUTES=5
```

上线前必须确认：

- 短信应用已创建。
- 签名已审核通过。
- 登录验证码模板已审核通过。
- 模板变量顺序与代码参数顺序一致。
- 发送频控已启用。
- 测试手机号真实收到短信。

### 6.3 实名核身配置

```text
TENCENT_FACEID_REGION=ap-guangzhou
TENCENT_FACEID_MODE=id-card-two-factor | phone-three-factor | faceid-miniapp
TENCENT_FACEID_RULE_ID
TENCENT_FACEID_REDIRECT_URL
TENCENT_FACEID_RESULT_TTL_MINUTES=30
```

具体字段以最终选择的腾讯云实名核身产品和控制台配置为准。

上线前必须确认：

- 腾讯云实名核身服务已开通。
- 主体资质、使用场景、合同和计费已确认。
- 若使用人脸核身，小程序端所需域名、SDK / 插件、类目或授权条件已确认。
- 已准备测试身份证样本和失败样本，且不得写入仓库。

## 7. 数据安全与合规要求

手机号、姓名、身份证号都属于敏感个人信息。本项目后续实现必须满足：

- 前端不接触腾讯云密钥。
- 后端调用腾讯云时只在内存中短暂使用明文身份证号。
- 明文身份证号不写日志、不进 operation log、不进 error message。
- 数据库存储拆分为密文、哈希、脱敏值。
- 后台页面默认只展示脱敏身份证；只有确有权限的审核动作才允许查看必要信息，且应留痕。
- 供应商 request id、错误码可以记录，供应商返回的敏感原文需要过滤。
- 导出、截图、测试样本不得包含真实身份证号。
- 本地调试不得直连线上库回写真实用户敏感字段。

当前必须修正的项目差距：

- `id_card_no_cipher` 字段名和注释表示密文，但当前实际写入脱敏值。后续实现腾讯云实名前必须先确认是否需要 migration 补 `id_card_masked` 和真实 cipher。

## 8. 后端接口设计草案

### 8.1 SMS provider

```java
public interface SmsCodeSender {
    SmsSendResult sendCode(SmsCodeCommand command);
}

public record SmsCodeCommand(
    String phone,
    String code,
    String scene,
    Duration ttl,
    String clientIp,
    String deviceFingerprint
) {}

public record SmsSendResult(
    boolean success,
    String providerCode,
    String requestId,
    String serialNo,
    String errorCode,
    String errorMessage
) {}
```

### 8.2 Real-name provider

```java
public interface RealNameVerificationProvider {
    RealNameVerificationResult verify(RealNameVerificationCommand command);
}

public record RealNameVerificationCommand(
    Long userId,
    String phone,
    String realName,
    String idCardNo,
    String mode
) {}

public record RealNameVerificationResult(
    boolean matched,
    boolean definitive,
    String providerCode,
    String requestId,
    String resultCode,
    String resultMessage
) {}
```

解释：

- `matched=true`：服务商确认一致。
- `matched=false, definitive=true`：服务商明确不一致，可以拒绝。
- `matched=false, definitive=false`：供应商异常、超时、未知，转人工待审核。

## 9. 测试与验收门禁

### 9.1 SMS

单测：

- 配置缺失时阻断发送。
- 腾讯云成功返回时写发送日志。
- 腾讯云失败时删除 Redis code。
- 频控命中时不调用腾讯云。
- 生产态不返回验证码。

真实样本：

- 一个已注册手机号：`sendCode -> login -> user.me`。
- 一个未注册手机号：`sendCode -> register(inviteCode) -> user.me`。
- 一个频控样本。
- 一个供应商失败样本。

发布门禁：

- 服务器环境变量 / Nacos 成组存在。
- 控制台签名和模板已审核通过。
- 公网 API smoke 使用真实域名。
- 登录页短信入口是否恢复，由后续 `00-174` 后继 Spec 决定。

### 9.2 Real-name

单测：

- 二要素 / 三要素通过。
- 不一致。
- 腾讯云配置缺失。
- 腾讯云超时 / 错误。
- 重复身份证哈希占用。
- 档案完成度不足。

真实样本：

- 通过样本。
- 姓名和身份证不一致样本。
- 供应商异常或配置缺失样本。
- 后台人工审核兜底样本。

发布门禁：

- 不在日志中出现完整身份证号。
- `identity_verification` 写入 provider request id。
- 后台详情页只展示脱敏信息。
- 审核通过后邀请资格联动仍正常。

## 10. 后续待确认问题

上线前需要人工确认：

1. 腾讯云短信签名和模板是否已审核通过。
2. 短信验证码模板变量顺序：只传验证码，还是验证码 + 有效分钟数。
3. 腾讯云实名核身购买的是身份证二要素、手机号三要素，还是人脸核身。
4. 实名核验通过后是否允许自动通过，还是仍要后台人工二次确认。
5. 供应商明确不一致时，是否立即 `rejected`，还是进入人工复核。
6. 是否需要给用户展示供应商失败原因，或统一展示“信息核验未通过”。
7. 当前生产环境 Nacos 是否已经具备安全注入腾讯云密钥的流程。
8. 身份证密文字段修正是否需要历史数据 migration。
9. 是否需要短信和实名的后台治理页。
10. 预算、日调用上限、告警阈值和供应商费用负责人。

## 11. 官方资料来源

- 腾讯云短信 `SendSms` API：<https://cloud.tencent.com/document/api/382/38778>
- 腾讯云短信 Java SDK / 快速接入：<https://cloud.tencent.com/document/product/382/56057>
- 腾讯云短信国内短信控制台与签名模板流程：<https://cloud.tencent.com/document/product/382/37745>
- 腾讯云实名核身 `DetectAuth` API：<https://cloud.tencent.com/document/api/1007/31816>
- 腾讯云实名核身 `GetDetectInfoEnhanced` API：<https://cloud.tencent.com/document/api/1007/41957>
- 腾讯云实名核身小程序接入说明：<https://cloud.tencent.com/document/product/1007/112653>
- 腾讯云实名核身身份信息认证（二要素核验）API：<https://cloud.tencent.com/document/api/1007/33188>
- 腾讯云实名核身手机号三要素核验 API：<https://cloud.tencent.com/document/product/1007/39765>
- 腾讯云实名核身实名信息核验产品说明：<https://cloud.tencent.com/document/product/1007/56775>
