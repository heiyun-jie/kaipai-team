# 当前阶段腾讯云身份证二要素实名认证接入 - 技术设计

## 1. 设计结论

本轮采用“后端 provider 接管 + 现有提交接口不变 + 人工审核兜底”的最小方案。

```text
pkg-card/verify/index
  -> POST /api/verify/submit
  -> IdentityVerificationServiceImpl.submit
  -> RealNameVerificationProvider.verify(Name, IdCard)
      -> tencent IdCardOCRVerification
      -> matched: auto approve
      -> definitive mismatch: rejected
      -> uncertain/error: pending manual review
```

不新增小程序页面，不引入腾讯云前端 SDK，不接人脸核身。

_Requirements: 3.1, 3.2, 3.5_

## 2. 腾讯云接口

官方接口：腾讯云人脸核身 `IdCardOCRVerification`

- Endpoint：`https://faceid.tencentcloudapi.com`
- Service：`faceid`
- Version：`2018-03-01`
- Action：`IdCardOCRVerification`
- 入参：`Name`、`IdCard`
- 本轮不传 `ImageBase64` / `ImageUrl`，只使用姓名和身份证号做二要素一致性核验。
- 关键出参：
  - `Result = "0"`：姓名和身份证号一致
  - `Result = "-1"`：姓名和身份证号不一致
  - `Result = "-2"`：非法身份证号
  - `Result = "-3"`：非法姓名
  - `Result = "-4"`：证件库服务异常
  - `Result = "-5"`：证件库中无此身份证记录
  - `Result = "-6"`：权威比对系统升级中
  - `Result = "-7"`：认证次数超过当日限制

_Requirements: 3.1_

## 3. 后端模块

新增模块放在 `com.kaipai.module.server.verify.realname`：

| 文件 | 职责 |
|------|------|
| `RealNameVerificationProperties` | 读取 `kaipai.realname` 配置 |
| `RealNameVerificationProvider` | provider 接口 |
| `RealNameVerificationCommand` | 传入 userId、姓名、身份证号 |
| `RealNameVerificationResult` | 标准化结果，区分 matched / definitive / manual review |
| `ManualRealNameVerificationProvider` | 不调用供应商，返回人工兜底 |
| `TencentRealNameVerificationProvider` | 调腾讯云 `IdCardOCRVerification` |
| `RoutingRealNameVerificationProvider` | 根据 providerCode 路由 |
| `IdCardCryptoSupport` | 最小身份证密文 / 脱敏 / hash 支撑 |

`TencentRealNameVerificationProvider` 复用现有 `TencentCloudApiSupport.sign(...)`，不引入新 SDK。

_Requirements: 3.1, 3.3, 3.5_

## 4. 数据库变更

新增 migration：

```sql
ALTER TABLE identity_verification
  ADD COLUMN id_card_no_masked VARCHAR(32) DEFAULT NULL COMMENT 'masked id card number' AFTER id_card_no_cipher,
  ADD COLUMN provider_code VARCHAR(32) DEFAULT NULL COMMENT 'manual/tencent' AFTER snapshot_profile_completion,
  ADD COLUMN provider_request_id VARCHAR(128) DEFAULT NULL AFTER provider_code,
  ADD COLUMN provider_result_code VARCHAR(64) DEFAULT NULL AFTER provider_request_id,
  ADD COLUMN provider_result_message VARCHAR(255) DEFAULT NULL AFTER provider_result_code,
  ADD COLUMN provider_verified_at DATETIME DEFAULT NULL AFTER provider_result_message,
  ADD KEY idx_identity_verification_provider_code (provider_code),
  ADD KEY idx_identity_verification_provider_verified_at (provider_verified_at);
```

兼容旧数据：

- 旧 `id_card_no_cipher` 中保存的是脱敏值；migration 将 `id_card_no_masked = id_card_no_cipher`，避免读链断裂。
- 新提交记录把 `id_card_no_cipher` 写为密文，把 `id_card_no_masked` 写为脱敏值。

_Requirements: 3.3, 3.4_

## 5. 状态机改造

`submit(...)` 继续执行现有前置检查：

1. 用户存在。
2. 姓名非空。
3. 身份证格式合法。
4. 不存在待审核或已通过记录。
5. 身份证哈希未被其他账号占用。
6. 档案完成度 >= 70。

通过后创建认证记录并调用 provider：

| Provider 结果 | 记录状态 | 用户状态 | 档案状态 | 后续动作 |
|---------------|----------|----------|----------|----------|
| matched | `2` | `2` | `isCertified=true` | 触发 `reconcileInviteeReferral` |
| definitive mismatch | `3` | `3` | `isCertified=false` | 返回拒绝状态 |
| manual review / provider error | `1` | `1` | `isCertified=false` | 后台人工审核 |

后台 `approve/reject` 仍只允许处理 `status=1` 的记录。

_Requirements: 3.1, 3.4_

## 6. 配置

新增配置：

```yaml
kaipai:
  realname:
    provider-code: ${KAIPAI_REALNAME_PROVIDER_CODE:tencent}
    tencent:
      endpoint: ${TENCENT_FACEID_ENDPOINT:https://faceid.tencentcloudapi.com}
      version: ${TENCENT_FACEID_VERSION:2018-03-01}
      secret-id: ${TENCENT_CLOUD_SECRET_ID:}
      secret-key: ${TENCENT_CLOUD_SECRET_KEY:}
      connect-timeout-ms: ${TENCENT_FACEID_CONNECT_TIMEOUT_MS:5000}
      read-timeout-ms: ${TENCENT_FACEID_READ_TIMEOUT_MS:10000}
```

身份证密文使用后端配置密钥：

```yaml
kaipai:
  identity:
    id-card-cipher-key: ${KAIPAI_ID_CARD_CIPHER_KEY:}
```

如果密钥缺失，后端不得把明文或脱敏值写入 `id_card_no_cipher`。实现上用受控的本地开发 fallback 生成不可逆占位密文，避免泄露明文；生产环境必须配置真实密钥后再验收。

_Requirements: 3.3, 3.5_

## 7. 前端与后台

小程序：

- `kaipai-frontend/src/pkg-card/verify/index.vue` 不改接口。
- 文案可从“人工核验”调整为“平台实名认证核验”，但不是本轮核心。

后台：

- `VerifyDetail` 增加 provider 字段。
- `VerificationBoard.vue` 详情抽屉展示服务商、结果码、结果摘要和核验时间。
- 列表不新增筛选，避免扩大范围。

_Requirements: 3.2, 3.4_

## 8. 测试设计

后端单测：

1. `TencentRealNameVerificationProviderTest`
   - 配置缺失抛出业务异常。
   - `Result=0` 解析为 matched。
   - `Result=-1` 解析为 definitive mismatch。
   - `Response.Error` 抛出业务异常，由 service 兜底。
2. `IdentityVerificationServiceImplTest`
   - provider matched 时自动通过，并触发用户/档案状态更新。
   - provider mismatch 时直接拒绝。
   - provider 异常时进入待审核。

验证命令：

```text
cd kaipaile-server && mvn -q -Dtest=TencentRealNameVerificationProviderTest,IdentityVerificationServiceImplTest test
cd kaipaile-server && mvn -q -DskipTests compile
cd kaipai-frontend && npm run type-check
```

_Requirements: 6_
