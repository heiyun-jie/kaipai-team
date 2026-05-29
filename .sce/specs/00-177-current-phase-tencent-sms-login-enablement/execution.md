# 00-177 执行记录

## 1. 启动记录

用户要求：对接手机验证码登录，并把之前隐藏掉的手机号登录放出来。

已读取：

- `.sce/README.md`
- `.sce/steering/CURRENT_CONTEXT.md`
- `.sce/specs/README.md`
- `.sce/specs/SHARED_CONVENTIONS.md`
- `00-51-current-phase-formal-sms-capability-deferral`
- `00-173-current-phase-wechat-phone-login-enablement`
- `00-174-current-phase-login-sms-review-gate`
- `00-176-current-phase-tencent-cloud-phone-realname-integration-research`
- `kaipai-frontend/src/pages/login/index.vue`
- `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java`
- 腾讯云短信官方 `SendSms` API 文档

## 2. 边界

本轮处理：

- 腾讯云 SMS 验证码发送 provider。
- `/api/auth/sendCode` 生产态不再直返验证码。
- 恢复登录页手机号验证码登录 / 注册入口。

本轮不处理：

- 腾讯云实名认证。
- 短信发送日志表。
- 复杂频控。
- 线上腾讯云控制台签名 / 模板创建。
- 真实密钥提交。

## 3. 实现记录

### 3.1 后端

- 新增 `com.kaipai.module.server.auth.sms` 包，承接短信发送接口、配置、dev provider、Tencent provider 与 provider 路由。
- `SmsProperties` 使用 `kaipai.sms` 前缀，默认 `provider-code=tencent`，验证码 TTL 默认 10 分钟。
- 腾讯云 provider 使用 SMS `SendSms` API，复用项目内既有腾讯云 TC3 签名支持，生产态成功发送后不向前端返回验证码。
- `AuthServiceImpl.sendCode` 改为生成验证码、写 Redis、调用 provider；provider 失败时删除 Redis 验证码并抛业务错误。
- `AuthController.sendCode` 与 `AuthService` 注释同步生产态语义：腾讯云通道不返回验证码，dev 通道可显式返回。
- `application.yml` 新增 SMS 运行配置占位，真实密钥与短信模板配置只通过环境变量 / 配置中心注入。

涉及文件：

- `kaipaile-server/src/main/java/com/kaipai/module/server/auth/sms/*`
- `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/auth/AuthController.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/AuthService.java`
- `kaipaile-server/src/main/resources/application.yml`
- `kaipaile-server/src/test/java/com/kaipai/module/server/auth/service/impl/AuthServiceImplTest.java`
- `kaipaile-server/src/test/java/com/kaipai/module/server/auth/sms/TencentSmsCodeSenderTest.java`

### 3.2 前端

- 恢复 `pages/login/index` 的手机号输入、验证码输入、获取验证码与登录 / 注册主按钮。
- 微信手机号一键登录继续保留为次级入口。
- 登录页文案调整为手机号验证码登录语义。
- 调整登录 sheet 间距，避免恢复短信表单后首屏过长。

涉及文件：

- `kaipai-frontend/src/pages/login/index.vue`

## 4. 验证记录

后端：

- `cd kaipaile-server && mvn test`
- 结果：37 tests，0 failures，0 errors。

前端：

- `cd kaipai-frontend && npm run type-check`
- `cd kaipai-frontend && npm run build:mp-weixin`
- `cd kaipai-frontend && npm run audit:mp-package`
- `cd kaipai-frontend && npm run build:h5`

包体审计结果：

- main：`521.35 KB / 2.00 MB`
- pkg-card：`201.91 KB / 2.00 MB`
- pkg-tools：`28.31 KB / 2.00 MB`

微信开发者工具预览：

- AppID：`wx4dcc4e1066fd0fb9`
- 预览通过。
- package total：`1.1 MB`
- main：`785.1 KB`
- `/pkg-card/`：`310.5 KB`
- `/pkg-tools/`：`36.8 KB`

构建产物核对：

- `dist/dev/mp-weixin/pages/login/index.wxml` 包含手机号输入占位。
- `dist/dev/mp-weixin/pages/login/index.wxml` 包含验证码输入占位。
- `dist/dev/mp-weixin/pages/login/index.wxml` 保留微信 `bindgetphonenumber` 绑定。
- “获取验证码”“登录 / 注册”为运行态绑定文案，不作为静态 WXML 字面量出现。

## 5. 运行配置待办

真实腾讯云 SMS 发送仍需要线上环境补齐以下配置，并确认短信签名 / 模板已在腾讯云控制台审核通过：

- `TENCENT_CLOUD_SECRET_ID`
- `TENCENT_CLOUD_SECRET_KEY`
- `TENCENT_SMS_SDK_APP_ID`
- `TENCENT_SMS_SIGN_NAME`
- `TENCENT_SMS_LOGIN_TEMPLATE_ID`

腾讯云控制台登录信息仅保存于本地 gitignored 目录，不进入仓库；本轮未提交真实密钥。

## 6. 2026-05-28 配置尝试记录

用户要求继续进入腾讯云完成配置。

已执行：

- 使用本地保存的腾讯云子账号信息打开腾讯云控制台登录页。
- 子账号用户名 / 密码登录流程已推进到腾讯云“登录二次验证”页。
- 腾讯云要求输入腾讯云助手小程序 / Google Authenticator / Microsoft Authenticator 的 MFA 安全码。
- 页面显示该账号未绑定其他备选校验方式。
- 尝试只读连接 108 部署机 `ssh hy-backup` 查看 Docker Compose 环境变量结构；当前 SSH key 未通过认证，无法进入远端写入环境变量。

当前阻塞：

- 腾讯云控制台配置阻塞于 MFA 安全码，无法创建 / 查看 SMS 应用、签名、模板和 API 密钥。
- 108 服务器环境变量落地阻塞于 SSH 认证，无法更新 compose / 容器环境。

继续所需输入：

- 腾讯云登录二次验证安全码，或由账号管理员临时关闭 / 调整登录保护。
- 可用的 108 服务器 SSH 凭据，或由有权限的人把 SMS 环境变量写入部署环境。

## 7. 2026-05-29 真实发送与运营商回执记录

已补齐本地运行配置并完成真实腾讯云 SMS 调用验证：

- `SmsSdkAppId`：`1401122459`。
- 短信签名：`杭州余杭开拍了`。
- 登录验证码模板 ID：`2641016`。
- 当前模板内容只有 `{1}` 一个变量，因此运行参数模式使用 `TENCENT_SMS_TEMPLATE_PARAM_MODE=code`。
- 后端验证码 TTL 为 10 分钟；当前腾讯云模板文案仍写“5分钟内有效”，上线前需在腾讯云控制台调整模板文案，或把运行 TTL 改回 5 分钟以保持一致。

真实发送验证：

- `13800138000` 测试号：`SendSms` 返回 `Ok`，本地后端日志记录 `provider=tencent`，生产态响应 `data=null`。
- 用户手机号测试：`SendSms` 返回 `Ok`，腾讯云生成 `SerialNo=99:191014622217800204440339673`。
- 通过 `PullSmsSendStatusByPhoneNumber` 查询该 `SerialNo`，运营商回执为 `ReportStatus=FAIL`、`Description=SUBFAIL`。
- 用户在腾讯云控制台进一步确认失败原因为“运营商网关拦截”。

结论：

- 后端 SMS provider、腾讯云签名认证、短信应用、签名、模板、参数模式均已通过真实调用验证。
- `137****6737` 未收到短信不是后端代码失败，也不是腾讯云 API 拒绝，而是下游运营商网关在投递阶段拦截。
- 后续若仍需覆盖该号码，应通过腾讯云工单或运营商侧查询底层拦截原因；系统侧只能记录并向用户展示发送失败/重试/换号建议。

## 8. 2026-05-29 单手机号日限额定位记录

用户在小程序请求验证码时观察到：

```text
Request URL: https://api.kplyyk.com/api/auth/sendCode
Request Method: POST
Status Code: 200
Response body: {"code":400,"message":"腾讯云短信发送失败：the number of sms messages sent from a single mobile number every day exceeds the upper limit","data":null}
```

定位结论：

- HTTP `200` 表示请求已到达后端并返回统一 JSON 包体；业务失败以 `body.code=400` 表达。
- 失败不是小程序请求地址、HTTPS、腾讯云签名、短信应用、签名或模板配置问题。
- 腾讯云真实通道已启用，线上容器环境确认包含：
  - `KAIPAI_SMS_PROVIDER_CODE=tencent`
  - `KAIPAI_SMS_CODE_EXPIRE_MINUTES=10`
  - `TENCENT_SMS_TEMPLATE_PARAM_MODE=code`
  - `TENCENT_SMS_SDK_APP_ID=1401122459`
  - `TENCENT_SMS_SIGN_NAME=杭州余杭开拍了`
  - `TENCENT_SMS_LOGIN_TEMPLATE_ID=2641016`
- 线上后端日志确认 `137****6737` 在 `2026-05-29 11:41:47 +0800` 已成功调用腾讯云发送，`SerialNo=99:108653675017800261072819673`。
- 只读查询腾讯云回执确认最近两条同号记录：
  - `2026-05-29 10:08:55 +0800`，`SerialNo=99:191014622217800204440339673`，`ReportStatus=FAIL`，`Description=SUBFAIL`。
  - `2026-05-29 11:41:51 +0800`，`SerialNo=99:108653675017800261072819673`，`ReportStatus=SUCCESS`，`Description=DELIVRD`。
- 后续再次请求同一号码时，腾讯云返回单手机号日发送上限错误，即当前 message 中的 `the number of sms messages sent from a single mobile number every day exceeds the upper limit`。

代码路径确认：

- `AuthServiceImpl.sendCode` 先写入 Redis 验证码，再调用 `SmsCodeSender`；provider 抛错时删除本次 Redis 验证码。
- `TencentSmsCodeSender` 读取腾讯云 `SendStatusSet[0].Code`，当 Code 非 `Ok/OK` 时抛出 `BizException("腾讯云短信发送失败：" + message)`。
- `GlobalExceptionHandler.handleBizException` 将业务异常包装为统一响应体，因此浏览器 Network 面板会看到 HTTP `200` + body `code=400`。
- 前端 `request.ts` 按响应体 `code` 判断业务成功或失败，失败时展示后端 message。

后续治理建议：

- 新增服务端 Redis 频控，至少包含：
  - `sms:cooldown:{phone}`：60 秒内只允许一次请求。
  - `sms:daily:{phone}:{yyyyMMdd}`：单手机号单日请求上限。
- 对仍在有效期内的验证码优先复用或提示“验证码仍在有效期内”，避免重复消耗腾讯云额度。
- 将腾讯云英文限额错误映射为用户可理解的中文文案，例如“该手机号今日验证码请求次数已达上限，请明天再试或更换手机号”。
- 后续测试不再反复使用同一个真实手机号；重复链路优先通过单测、mock provider 或未触达腾讯云的本地限流测试覆盖。
