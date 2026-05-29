# 00-177 当前阶段腾讯云短信验证码登录启用 - 技术设计

## 1. 设计结论

本轮做两件事：

```text
后端:
  AuthServiceImpl.sendCode
    -> 生成 code
    -> Redis 写入 10 min
    -> SmsCodeSender.sendCode(...)
    -> 腾讯云成功：返回 null
    -> 腾讯云失败：删除 Redis code + 抛业务错误

前端:
  pages/login/index
    -> 恢复手机号 / 验证码表单
    -> 恢复获取验证码
    -> 恢复登录 / 注册按钮
    -> 保留微信一键登录为次级入口
```

_Requirements: 3.1, 3.2, 3.3, 3.4_

## 2. 后端模块设计

新增包：

```text
com.kaipai.module.server.auth.sms
  SmsCodeSender
  SmsCodeSendCommand
  SmsCodeSendResult
  SmsProperties
  DevSmsCodeSender
  TencentSmsCodeSender
```

### 2.1 `SmsCodeSender`

```java
public interface SmsCodeSender {
    SmsCodeSendResult sendCode(SmsCodeSendCommand command);
}
```

### 2.2 `SmsProperties`

配置前缀：

```yaml
kaipai:
  sms:
    provider-code: ${KAIPAI_SMS_PROVIDER_CODE:tencent}
    code-expire-minutes: ${KAIPAI_SMS_CODE_EXPIRE_MINUTES:10}
    tencent:
      endpoint: ${TENCENT_SMS_ENDPOINT:https://sms.tencentcloudapi.com}
      region: ${TENCENT_SMS_REGION:ap-guangzhou}
      version: ${TENCENT_SMS_VERSION:2021-01-11}
      secret-id: ${TENCENT_CLOUD_SECRET_ID:}
      secret-key: ${TENCENT_CLOUD_SECRET_KEY:}
      sms-sdk-app-id: ${TENCENT_SMS_SDK_APP_ID:}
      sign-name: ${TENCENT_SMS_SIGN_NAME:}
      template-id: ${TENCENT_SMS_LOGIN_TEMPLATE_ID:}
      connect-timeout-ms: ${TENCENT_SMS_CONNECT_TIMEOUT_MS:5000}
      read-timeout-ms: ${TENCENT_SMS_READ_TIMEOUT_MS:10000}
```

### 2.3 腾讯云调用

使用腾讯云 API 3.0 TC3-HMAC-SHA256 签名，同项目已有腾讯云 AI provider 签名模式一致。

请求：

- endpoint：`https://sms.tencentcloudapi.com`
- service：`sms`
- action：`SendSms`
- version：`2021-01-11`

payload：

```json
{
  "SmsSdkAppId": "...",
  "SignName": "...",
  "TemplateId": "...",
  "TemplateParamSet": ["123456"],
  "PhoneNumberSet": ["+8613800138000"],
  "SessionContext": "login"
}
```

模板参数是否只传验证码，还是验证码 + 有效分钟数，由 `template-param-mode` 配置控制，避免模板审核后变量数量不一致。

_Requirements: 3.1, 3.5_

## 3. 前端设计

恢复原有表单结构：

```text
sheet head
phone field
sms field + get code
submit
wechat one-click secondary
agreement
```

视觉策略：

- 保持 `00-175` 的 hero 和整体居中偏上基线。
- 登录 sheet 内部增加短信表单后，降低微信按钮顶边距，避免首屏过长。
- 按钮和输入框沿用既有 `.login-page__field / submit / wechat` 样式。

_Requirements: 3.3, 3.4_

## 4. 本轮不做

- 不新增短信发送日志表。
- 不做复杂 IP / 设备频控。
- 不接实名认证。
- 不发布腾讯云配置。
- 不登录腾讯云控制台创建签名模板。

以上必须在后续运行配置 / 风控 Spec 中处理。

## 5. 验证设计

后端：

1. 新增单测覆盖 dev provider 返回验证码。
2. 新增单测覆盖 tencent provider 配置缺失。
3. 新增单测覆盖 tencent provider 成功解析。
4. `mvn test`。

前端：

1. `npm run type-check`
2. `npm run build:mp-weixin`
3. `npm run audit:mp-package`
4. 核对 `dist/build/mp-weixin/pages/login/index.wxml` 包含手机号 / 验证码表单与微信登录绑定。
