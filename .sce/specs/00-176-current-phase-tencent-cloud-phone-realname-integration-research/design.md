# 00-176 当前阶段腾讯云手机号与实名认证服务接入调研 - 技术设计

## 1. 设计结论

本轮输出一个调研型 Spec，不做运行时代码变更。核心结论：

```text
手机号登录
  当前可用入口：微信 getPhoneNumber -> /api/auth/wechat-login
  当前待补能力：腾讯云 SMS -> /api/auth/sendCode 正式短信通道
  暂不推荐：腾讯云 App 号码认证作为微信小程序登录入口

实名认证
  当前可用入口：/api/verify/submit -> 后台人工审核
  第一阶段推荐：腾讯云实名核身身份证二要素或手机号三要素，后端同步核验
  第二阶段可选：腾讯云实名核身人脸核身，小程序端发起核身流程，后端查验结果
```

_Requirements: 3.1, 3.2, 3.3_

## 2. 文档产物

本 Spec 下生成：

- `requirements.md`：调研需求和验收边界。
- `design.md`：本文件，说明文档结构和后续实施归属。
- `tasks.md`：本轮调研任务清单。
- `tencent-cloud-phone-realname-investigation.md`：正式调研文档。
- `execution.md`：本轮执行记录。

_Requirements: 3.4, 3.5_

## 3. 既有系统边界

### 3.1 登录域

当前 `/api/auth/sendCode` 仍由 `AuthServiceImpl.sendCode(...)` 生成验证码并写入 Redis，开发态把验证码返回给调用方。正式短信接入应替换发送动作，但保留：

- Redis 验证码 TTL。
- `/api/auth/login` 与 `/api/auth/register` 的验证码校验。
- 邀请码透传。
- `00-174` 登录页短信入口审核门禁。

### 3.2 实名域

当前实名认证链路已经有：

- `identity_verification` 表。
- `identity_verification_owner` 跨账号身份证哈希占用表。
- `/api/verify/status`
- `/api/verify/submit`
- `/api/admin/verify/list`
- `/api/admin/verify/{id}`
- `/api/admin/verify/{id}/approve`
- `/api/admin/verify/{id}/reject`

第三方实名接入应增强 `submit` 后的核验决策，不应绕过现有状态、后台治理和邀请资格联动。

_Requirements: 3.1_

## 4. 后续实现建议

后续不建议一个 Spec 同时实现所有能力。推荐拆成：

1. `current-phase-tencent-cloud-sms-channel-enablement`
   - 只接腾讯云 SMS。
   - 修正 `/api/auth/sendCode` 生产态不返回验证码。
   - 增加发送频控、日志和配置门禁。
2. `current-phase-tencent-cloud-realname-factor-check`
   - 接入身份证二要素或手机号三要素。
   - 改造 `verify/submit` 的自动核验和人工兜底。
   - 修正身份证密文存储语义。
3. `current-phase-tencent-cloud-faceid-miniapp-flow`
   - 仅当产品要求活体核身时启用。
   - 接小程序端核身 SDK / 插件能力和后端结果查询。
4. `current-phase-login-sms-entry-restore-after-review`
   - 只有短信审核和商用通道验证完成后，才恢复登录页短信表单。

_Requirements: 3.5_

## 5. 验证设计

本轮验证方式：

- 读取现有 Spec 与关键源码。
- 查询腾讯云官方文档。
- 生成调研文档并列出来源。
- 不执行构建，因为本轮无代码变更。

后续实现 Spec 的验证门禁应至少包含：

- 后端单测覆盖 provider 成功、失败、配置缺失。
- Redis 验证码 TTL 和消费后删除不回退。
- 生产态 `sendCode` 不返回验证码。
- 实名核验成功、失败、供应商异常、人工兜底四类样本。
- 运行时配置预检查。
- 发布后真实接口 smoke。

