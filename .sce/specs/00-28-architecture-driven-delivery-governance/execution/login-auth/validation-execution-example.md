# 登录鉴权联调执行示例

## 1. 只创建样本目录

```powershell
powershell -ExecutionPolicy Bypass -File `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\login-auth\new-login-auth-validation-sample.ps1" `
  -EnvironmentName "dev" `
  -SampleLabel "wechat-existing-user"
```

输出目录下会预建：

- `captures/`
- `screenshots/`
- `sample-ledger.md`

## 2. 一次性准备登录联调样本

```powershell
powershell -ExecutionPolicy Bypass -File `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\login-auth\run-login-auth-validation.ps1" `
  -EnvironmentName "dev" `
  -SampleLabel "phone-register-invite"
```

脚本会自动：

- 创建样本目录
- 扫描 `kaipai-frontend/.env`、`.env.example`
- 扫描 `kaipai-admin/.env.development`
- 扫描 `kaipaile-server/src/main/resources/application.yml`
- 生成：
  - `captures/capture-results.json`
  - `runtime-summary.md`
  - `sample-ledger.md`
  - `validation-report.md`

## 2.1 一次性准备并执行真实接口预探测

```powershell
powershell -ExecutionPolicy Bypass -File `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\login-auth\run-login-auth-validation.ps1" `
  -EnvironmentName "dev" `
  -SampleLabel "live-probe" `
  -EnableLiveProbe `
  -ProbePhone "13800138000" `
  -ProbeWechatCode "dummy-code" `
  -ProbeInviteCode "TESTINVITE"
```

开启 `-EnableLiveProbe` 后，脚本会额外生成：

- `captures/live-probe-sendCode.json`
- `captures/live-probe-wechat-login.json`

适用场景：

- 快速确认“当前不是 mock，而是真接口业务报错”
- 把 `wechat-login` 的配置缺失证据写入样本目录
- 在人工微信授权前，先判断当前环境是否具备真实联调资格

## 3. 人工补证顺序

1. 打开 `runtime-summary.md`，确认当前环境是否具备真实联调前置
2. 补登录页截图，确认：
   - `inviteCode / scene`
   - 微信按钮显隐
   - 是否出现运行时阻塞提示
3. 补接口响应：
   - `sendCode`
   - `login / register / wechat-login`
   - `user.me`
   - `verify / invite / level`
4. 补数据库证据：
   - `user`
   - `referral_record`
5. 最后把结论回填到 `status/login-auth-status.md`

## 4. 当前脚本边界

- 当前脚本只预填“仓内可直接抽取的运行时事实”
- 默认不会直接请求真实后端；只有显式开启 `-EnableLiveProbe` 才会做 `sendCode / wechat-login` 预探测
- 不会代替人工完成微信授权
- 不会代替人工执行数据库查询

## 5. 适用场景

- 开始真实环境联调前，先做准入检查
- 拿到新一套环境配置后，快速建立新的登录验证样本目录
- 把“运行时阻塞”和“功能缺陷”拆开记录，避免再次误把配置问题当成功能问题
