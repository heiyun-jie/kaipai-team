# 00-176 执行记录

## 1. 启动记录

用户要求：查看已有 Specs，现在需要对接腾讯云的手机号服务和实名认证服务，先调查所需内容并生成文档。

本轮按 SCE 执行，只做调研与文档，不改运行时代码。

已读取：

- `.sce/README.md`
- `.sce/steering/CURRENT_CONTEXT.md`
- `.sce/specs/README.md`
- `.sce/specs/SHARED_CONVENTIONS.md`
- `00-51-current-phase-formal-sms-capability-deferral`
- `00-173-current-phase-wechat-phone-login-enablement`
- `00-174-current-phase-login-sms-review-gate`
- `05-09-identity-verification`

## 2. 代码事实核对

已核对：

- `kaipaile-server/src/main/java/com/kaipai/module/controller/auth/AuthController.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/verify/VerifyController.java`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/verify/AdminVerifyController.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/impl/IdentityVerificationServiceImpl.java`
- `kaipaile-server/src/main/resources/db/migration/V20260331_001__platform_admin_baseline.sql`
- `kaipaile-server/src/main/resources/db/migration/V20260403_001__identity_verification_resubmit_history.sql`

结论：

- `/api/auth/sendCode` 当前仍是开发态直返验证码。
- Redis 验证码 key 前缀为 `sms:code:`，TTL 为 5 分钟。
- 实名认证当前已具备提交、状态、后台列表、详情、通过、拒绝。
- `identity_verification_owner` 已用于身份证哈希跨账号占用。
- 当前 `id_card_no_cipher` 实际写入脱敏身份证，不是真正密文。

## 3. 腾讯云官方资料核对

已查询腾讯云官方文档：

- 腾讯云短信 `SendSms` API
- 腾讯云短信 Java SDK / 快速接入
- 腾讯云短信签名和模板控制台流程
- 腾讯云实名核身 `DetectAuth`
- 腾讯云实名核身 `GetDetectInfoEnhanced`
- 腾讯云实名核身小程序接入说明
- 腾讯云实名核身 API 索引

## 4. 输出文档

已新增：

- `requirements.md`
- `design.md`
- `tasks.md`
- `tencent-cloud-phone-realname-investigation.md`
- `execution.md`

核心建议：

1. 手机号验证码优先接腾讯云 SMS。
2. 微信小程序手机号一键登录继续沿用 `00-173` 微信 `getPhoneNumber`，不引入腾讯云 App 号码认证作为当前入口。
3. 实名认证先接身份证二要素或手机号三要素；人脸核身独立排期。
4. 接实名前必须修正身份证字段密文 / 哈希 / 脱敏值语义。
5. 短信正式通道接入完成后，不等于立即恢复登录页短信表单；恢复入口应另起 Spec。

## 5. 验证记录

本轮无代码变更，未执行构建。

已执行静态核对：

```powershell
Test-Path .sce\specs\00-176-current-phase-tencent-cloud-phone-realname-integration-research
```

结果：创建前不存在，避免覆盖既有 Spec。

未改：

- `kaipai-frontend`
- `kaipaile-server`
- `kaipai-admin`
- 数据库 migration
- 运行时配置

## 6. 已知项目文档漂移

接管时已存在：

- `.sce/specs/README.md` 有未提交修改，内容为 `05-14` 登记。
- `.sce/specs/05-14-actor-profile-mojibake-recovery-guard/` 是未跟踪目录。
- `00-175` 已有完整 Spec，但尚未登记到 `spec-code-mapping.md`。
- `CURRENT_CONTEXT.md` 仍停在 `00-145`，滞后于当前真实 Spec 目录。
- `npm run audit:steering` 当前因 `CORE_PRINCIPLES.md` 编号重复 / 不连续失败。

本轮没有修复这些漂移，避免把调研文档与既有治理清理混成一个变更。

