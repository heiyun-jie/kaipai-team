# 登录鉴权真实环境闭环验证清单

## 1. 目标

把当前“局部完成”的登录链路，收口成一条可重复验证的真实环境样本链：

`sendCode -> login / register -> token + user session -> user.me -> verify / invite / level 同步`

如果启用了微信登录，则扩展为：

`getPhoneNumber code -> wechat-login -> 老用户登录 / 新用户自动注册 -> inviteCode 透传 -> user.me`

## 2. 验证前置

### 2.1 运行时确认

- 小程序、后台、后端必须确认同一环境
- 必查项：
  - profile
  - 反向代理
  - `VITE_API_BASE_URL`
  - `VITE_USE_MOCK`
  - `VITE_ENABLE_WECHAT_AUTH`
  - `WECHAT_MINIAPP_APP_ID`
  - `WECHAT_MINIAPP_APP_SECRET`
- 若要验证微信真实链路，必须先按 `00-29` 单页门禁 runbook 固定顺序执行：
  - `.sce/runbooks/backend-admin-release/wechat-config-gate-runbook.md`
- 当前“可进入微信真实验证”的最小门槛不是“secret 文件存在”，而是：
  - `read-local-wechat-config-inputs.py` 明确给出 `Release Ready: yes`
  - 当前 secret 不是 `replace-with-real-app-secret`、`fake-*`、`example`、`dummy`、`sample` 等 placeholder/fake 值
  - `read-backend-wechat-config-precheck.py` 在发布后复检通过
- 建议先执行一次：
  - `run-login-auth-validation.ps1 -EnableLiveProbe`
  - 用于把 `sendCode / wechat-login` 的真实返回先固化到样本目录，避免把配置问题继续误判成 mock 或代码未发布

### 2.2 账号与样本

- 准备 1 个已注册手机号样本
- 准备 1 个未注册手机号样本
- 准备 1 组可追踪的邀请码样本
- 若验证微信真实链路，再准备：
  - 1 个微信老用户样本
  - 1 个微信新用户自动注册样本

### 2.3 记录规范

- 每次验证必须固定记录：
  - 环境名
  - phone
  - inviteCode
  - userId
  - token 截断值
  - 是否走微信链路
- 每次至少保留 4 类证据：
  - 小程序页面截图
  - API 响应
  - 后台或日志截图
  - `user / referral_record` 查询结果

## 3. 主链路验证

### 3.1 短信验证码发送

- 接口：
  - `POST /api/auth/sendCode`
- 需要确认：
  - 接口可返回验证码
  - 报错口径稳定
- 当前不能误判：
  - 这只能证明接口接通，不能证明短信商用完成

### 3.2 手机号登录

- 接口：
  - `POST /api/auth/login`
  - `GET /api/user/me`
- 需要确认：
  - 返回 token
  - `user.me` 与登录返回用户摘要一致
  - 前端会话建立后才同步 `verify / invite / level`

### 3.3 手机号注册 + inviteCode

- 接口：
  - `POST /api/auth/register`
- 需要确认：
  - 登录页正确承接 `inviteCode`
  - 注册成功后 `invitedByUserId` 不丢失
  - 同一样本可在 `referral_record` 中追到

### 3.4 微信老用户登录

- 前提：
  - `VITE_ENABLE_WECHAT_AUTH=true`
  - 后端微信配置齐全
- 需要确认：
  - 登录页显示微信按钮
  - 授权后进入老用户登录链
  - `user.me` 可恢复同一用户

### 3.5 微信新用户自动注册 + inviteCode

- 前提：
  - 同 3.4
- 需要确认：
  - 自动创建用户
  - `inviteCode` 与 `deviceFingerprint` 不丢失
  - 同样本能追到 `referral_record`

### 3.6 会话恢复

- 入口：
  - 重新进入小程序或刷新页面
- 需要确认：
  - `bootstrapSession` 可恢复会话
  - 再同步 `verify / invite / level`
  - 不提前请求受保护数据

## 4. 配置阻塞验证

### 4.1 小程序阻塞

- 需要确认：
  - 缺少 `VITE_API_BASE_URL` 时会提示运行时阻塞
  - `VITE_USE_MOCK=false` 但缺少 base URL 时会提示运行时阻塞

### 4.2 微信阻塞

- 需要确认：
  - `VITE_ENABLE_WECHAT_AUTH=false` 时页面展示降级提示而非微信按钮
  - 后端缺 `WECHAT_MINIAPP_APP_ID / SECRET` 时明确返回阻塞错误
  - placeholder / fake secret 不会被误判成“已具备真实微信配置”
  - 本地 `secret` 文件已存在但仍是 placeholder 时，标准总控会以 `local_input_not_ready` 中止

## 5. 判定标准

### 5.1 仍只能判定“局部完成”

满足以下任一条，即不能宣告 login-auth 闭环完成：

- 没有同一样本链的真实环境证据
- 微信按钮显隐与配置台账不一致
- `login/register/wechat-login` 与 `user.me` 口径不一致
- `inviteCode` 在注册或微信自动注册链路中丢失
- 登录后 `verify / invite / level` 没有按正确时序同步
- `00-29` 微信配置总控仍处于 `blocked`，包括“secret 文件存在但仍是 placeholder/fake secret”的场景

### 5.2 可以升级为“闭环完成”

- 手机号登录 / 注册真实链路走通
- 微信老用户登录走通
- 微信新用户自动注册 + `inviteCode` 走通
- 配置缺失时前后端阻塞口径一致
- 同一样本在前端、接口、数据库三端口径一致

## 6. 回填模板

每次验证结束后，按下面结构回填到 `status/login-auth-status.md`：

```md
### YYYY-MM-DD（联调回填）

- 当前判定：`局部完成` / `闭环完成`
- 样本：
  - phone:
  - inviteCode:
  - userId:
  - wechatPath:
- 已确认：
  - 
- 未确认：
  - 
- 缺陷归因：
  - 前端：
  - 后端：
  - 配置：
```
