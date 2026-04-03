# 登录鉴权与前台会话闭环后端执行卡

## 1. 执行卡名称

登录鉴权与前台会话闭环 - 后端执行卡

## 2. 归属切片

- `../../slices/login-auth-capability-slice.md`

## 3. 负责范围

- 短信验证码发送、登录、注册
- 微信手机号一键登录
- `user.me` 与身份切换
- 自动注册内的邀请码透传与邀请落库
- 微信运行时配置校验与错误返回

## 4. 不负责范围

- 登录页视觉和按钮交互
- 后台账号登录
- 商用短信供应商接入
- 独立 OAuth 平台建设

## 5. 关键输入

- 上位 Spec：
  - `00-10 platform-admin-backend-architecture`
  - `01-01 page-login`
  - `05-10 invite-referral`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/auth/AuthController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/user/UserController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/AuthService.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/model/auth/dto/WechatLoginReqDTO.java`
  - `kaipaile-server/src/main/resources/application.yml`

## 6. 目标交付物

- `sendCode / login / register / wechat-login / user.me / user.role` 契约稳定
- 微信登录能区分已注册用户登录和未注册用户自动注册
- 自动注册可稳定消费 `inviteCode`
- 缺微信配置时后端显式返回阻塞错误
- 返回 DTO 能支撑前端登录后统一同步

## 7. 关键任务

1. 固化短信登录链路
   - 验证码缓存、校验、失效
   - 注册与登录返回统一 DTO
2. 固化微信登录链路
   - 消费 `getPhoneNumber code`
   - 换取手机号
   - 老用户登录 / 新用户自动注册
3. 固化邀请透传
   - 自动注册复用注册事务
   - `inviteCode` 与 `deviceFingerprint` 不丢失
4. 固化会话摘要
   - `buildLoginResp`
   - `user.me`
   - `user.role`
5. 固化配置阻塞口径
   - `WECHAT_MINIAPP_APP_ID`
   - `WECHAT_MINIAPP_APP_SECRET`
   - 配置缺失时明确报错

## 8. 依赖项

- 微信小程序后台配置必须先通过 `00-29` 单页门禁 runbook，而不是只在源码或本地文件里存在占位值
- 邀请注册链路必须先稳定，才能验证微信自动注册透传
- 前端必须同步收口错误提示，不能继续假装成功

## 9. 验证方式

- `POST /api/auth/sendCode` 可返回验证码
- `POST /api/auth/login`、`/register` 返回稳定登录态
- `POST /api/auth/wechat-login` 可完成老用户登录或新用户自动注册
- `GET /api/user/me` 与 `PUT /api/user/role` 能返回统一用户摘要
- `mvn -q -DskipTests compile` 在 JDK 21 环境通过

## 10. 完成定义

- 后端登录契约稳定可用
- 微信登录能力具备真实接入基础
- 自动注册和邀请码消费口径一致
- 配置缺失时能显式阻塞
- 可支撑前端和联调卡的真实验证

## 11. 风险与备注

- 当前 `sendCode` 仍是开发期直返验证码，只能说明后端契约已接通，不能误写成短信商用已完成
- 若微信登录把配置缺失吞掉，前端会继续误判为“按钮可点即能力可用”
- 若 `buildLoginResp`、`user.me` 与邀请 / 等级摘要口径不一致，会把登录后同步做成第二套事实源
