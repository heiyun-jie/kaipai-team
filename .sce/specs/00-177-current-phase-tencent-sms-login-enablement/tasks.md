# 00-177 任务

## Phase 1: Spec

- [x] 新增腾讯云短信验证码登录启用 Spec。
- [x] 明确本轮只做 SMS 和登录页恢复，不接实名认证。

## Phase 2: Backend

- [x] 新增 SMS provider 配置与接口。
- [x] 新增 dev SMS provider。
- [x] 新增 Tencent SMS provider。
- [x] 改造 `AuthServiceImpl.sendCode`。
- [x] 更新 `AuthController.sendCode` 生产态不返回验证码。
- [x] 补后端单测。

## Phase 3: Frontend

- [x] 恢复登录页手机号输入框。
- [x] 恢复验证码输入框与获取验证码按钮。
- [x] 恢复登录 / 注册主按钮。
- [x] 保留微信一键登录作为次级入口。
- [x] 调整登录页文案和首屏密度。

## Phase 4: Verification

- [x] `kaipaile-server` 测试通过。
- [x] `kaipai-frontend` type-check 通过。
- [x] `kaipai-frontend` `build:mp-weixin` 通过。
- [x] `kaipai-frontend` 包体审计通过。
- [x] 登录页构建产物包含短信入口和微信入口。
