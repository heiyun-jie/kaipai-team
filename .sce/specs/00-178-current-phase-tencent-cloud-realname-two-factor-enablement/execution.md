# 当前阶段腾讯云身份证二要素实名认证接入 Execution

## 2026-05-29

- 用户确认已购买腾讯云身份证二要素核验。
- 已查阅 `00-176`，确认本轮应新建实现型 Spec，而不是修改调研型 Spec。
- 已核对腾讯云官方文档：
  - `IdCardOCRVerification`
  - endpoint: `faceid.tencentcloudapi.com`
  - version: `2018-03-01`
  - action: `IdCardOCRVerification`
  - 入参：`Name`、`IdCard`，本轮不传身份证图片
  - `Result=0` 一致，`Result=-1` 不一致，`-2/-3` 输入非法，`-4/-6` 偏供应商异常。
- 已核对当前代码：
  - 小程序提交页：`kaipai-frontend/src/pkg-card/verify/index.vue`
  - 前端 API：`kaipai-frontend/src/api/verify.ts`
  - 后端服务：`kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/impl/IdentityVerificationServiceImpl.java`
  - 当前 `idCardNoCipher` 实际写入脱敏值，本轮纳入修正。

## 待记录

- 单测红绿记录：
  - `TencentRealNameVerificationProviderTest` 初次运行因缺少 `TencentRealNameVerificationProvider` 编译失败，补 provider 后通过。
  - `IdentityVerificationServiceImplTest` 初次运行因缺少 `IdCardCryptoSupport` 编译失败，补状态机后通过。
- migration 文件名：
  - `kaipaile-server/src/main/resources/db/migration/V20260529_001__tencent_realname_two_factor.sql`
- 构建与类型检查结果：
  - `cd kaipaile-server && mvn -q "-Dtest=TencentRealNameVerificationProviderTest,IdentityVerificationServiceImplTest" test` 通过。
  - `cd kaipaile-server && mvn -q -DskipTests compile` 通过。
  - `cd kaipai-admin && npm run type-check` 通过。
  - `cd kaipai-frontend && npm run type-check` 通过。

## 实现摘要

- 新增后端实名 provider 模块：
  - `RealNameVerificationProvider`
  - `RoutingRealNameVerificationProvider`
  - `TencentRealNameVerificationProvider`
  - `ManualRealNameVerificationProvider`
  - `IdCardCryptoSupport`
- `IdentityVerificationServiceImpl.submit(...)` 已接入二要素状态机：
  - `matched=true` 自动通过并触发邀请资格联动。
  - `definitive=false` 进入人工审核。
  - `definitive=true / matched=false` 直接拒绝。
- 新增 migration：
  - `V20260529_001__tencent_realname_two_factor.sql`
- 后台详情抽屉已展示服务商核验摘要。

## 运行态记录

- 本机 Windows User 环境变量已配置并确认存在：
  - `KAIPAI_REALNAME_PROVIDER_CODE`
  - `TENCENT_CLOUD_SECRET_ID`
  - `TENCENT_CLOUD_SECRET_KEY`
  - `TENCENT_FACEID_ENDPOINT`
  - `TENCENT_FACEID_VERSION`
  - `KAIPAI_ID_CARD_CIPHER_KEY`
- 已对 dev 运行库执行 migration：
  - 数据库：`101.43.57.62:3306/kaipai_dev`
  - 命令：`DbMigrationRunner apply V20260529_001__tencent_realname_two_factor.sql`
  - 结果：执行 `2` 条 SQL。
- 已复查 `identity_verification` 结构：
  - `id_card_no_masked`：EXISTS
  - `provider_code`：EXISTS
  - `provider_request_id`：EXISTS
  - `provider_result_code`：EXISTS
  - `provider_result_message`：EXISTS
  - `provider_verified_at`：EXISTS
  - `idx_identity_verification_provider_code`：EXISTS
  - `idx_identity_verification_provider_verified_at`：EXISTS
- 已确认本地默认 `127.0.0.1:3309/kaipai_dev` 未监听；为保证本机 `8010` 与已迁移库一致，后端已使用显式 `SPRING_DATASOURCE_URL` 指向 `101.43.57.62:3306/kaipai_dev` 重启。
- 本机 `8010` 运行态 smoke：
  - `GET http://127.0.0.1:8010/api/card/scene-templates` 返回 `200`。
  - `GET http://127.0.0.1:8010/api/verify/status` 未登录返回 `401`，认证门禁未放开。
  - `java` 进程已与 `101.43.57.62:3306` 建立 MySQL 连接。
- 用户补充 `D:\XM\kaipai-team\SecretKey.csv`，文件已被 `.gitignore` 忽略，包含 `SecretId,SecretKey,name,id` 一行测试数据。
- 已读取 CSV 做格式检查：
  - `name` 存在。
  - `id` 长度为 `18`。
  - 未在日志或回复中输出姓名、完整身份证号或密钥。
- 已用 CSV 第一行发起腾讯云 `IdCardOCRVerification` 受控 smoke，结果未进入二要素比对；另一次使用 CSV 内 `SecretId/SecretKey` 的同 action 请求返回 `AuthFailure.SecretIdNotFound`。
  - 腾讯云返回 `Response.Error.Code = AuthFailure.SecretIdNotFound`。
  - 错误含义：SecretId 未找到，请确认 SecretId 是否正确。
  - CSV 中 `SecretId/SecretKey` 与当前 Windows User 环境变量中的 `TENCENT_CLOUD_SECRET_ID / TENCENT_CLOUD_SECRET_KEY` 不一致。
  - 当前结论：测试样本格式可用，但 CSV 中这组腾讯云访问密钥无法通过腾讯云鉴权。
- 已改用当前后端 Windows User 环境变量中的 `TENCENT_CLOUD_SECRET_ID / TENCENT_CLOUD_SECRET_KEY`，继续使用 CSV 的 `name/id` 样本发起受控 smoke：
  - 签名请求已到达腾讯云并返回 HTTP `200`。
  - 腾讯云返回 `Response.Error.Code = UnauthorizedOperation.Nonactivated`。
  - 错误消息：`未开通服务。`
  - 当前结论：当前后端使用的密钥可完成腾讯云鉴权签名，但腾讯云返回 `UnauthorizedOperation.Nonactivated`，尚未进入姓名 / 身份证二要素比对。
- 用户补充 API Explorer 链接：`https://console.cloud.tencent.com/api/explorer?Product=faceid&Version=2018-03-01&Action=IdCardOCRVerification`。
- 已将后端 provider action 从 `IdCardVerification` 切换为 `IdCardOCRVerification`，并新增单测断言请求头 `X-TC-Action=IdCardOCRVerification`。
- `IdCardOCRVerification` 受控 smoke 结果：
  - 使用当前后端 Windows User 环境变量密钥 + CSV `name/id`：HTTP `200`，`Response.Error.Code = UnauthorizedOperation.Nonactivated`，错误消息 `未开通服务。`
  - 使用 CSV 内 `SecretId/SecretKey + name/id`：HTTP `200`，`Response.Error.Code = AuthFailure.SecretIdNotFound`。
  - 当前结论：代码 action 已对齐 API Explorer；当前可被腾讯云识别的后端环境变量密钥所属账号仍未开通 / 激活该服务，CSV 内密钥不是有效腾讯云 SecretId。

## 2026-06-01

- 用户确认腾讯云身份证二要素服务已开通后，已重新发起 `IdCardOCRVerification` 受控 smoke：
  - 密钥来源：当前后端 Windows User / Process 环境变量中的 `TENCENT_CLOUD_SECRET_ID`、`TENCENT_CLOUD_SECRET_KEY`。
  - 测试样本来源：`D:\XM\kaipai-team\SecretKey.csv` 的 `name/id`，日志与记录只保留身份证脱敏值 `411***********8415`。
  - Action：`IdCardOCRVerification`。
  - HTTP 状态：`200`。
  - `Response.Error`：无。
  - `Result`：`0`。
  - `Description`：`姓名和身份证号一致`。
  - `RequestId`：`bfef32de-4958-48aa-90ef-f2260e4e3709`。
- 当前结论：腾讯云身份证二要素 provider/API 级受控 smoke 已跑通；此前的 `UnauthorizedOperation.Nonactivated` 已解除。后续若要验证小程序完整提交链路，还需要使用有效登录态调用 `/api/verify/submit`。
