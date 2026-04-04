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
- 自动回填 `sample-ledger.md / validation-report.md`
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
- 并把 live probe 结论自动回填到 `sample-ledger.md / validation-report.md`

适用场景：

- 快速确认“当前不是 mock，而是真接口业务报错”
- 把 `wechat-login` 的配置缺失证据写入样本目录
- 在人工微信授权前，先判断当前环境是否具备真实联调资格

## 2.2 当前阶段手机号主链样本

```powershell
python .sce/specs/00-28-architecture-driven-delivery-governance/execution/login-auth/run-login-auth-phone-session-sample.py `
  --environment dev `
  --label phone-session-mainline
```

脚本会直接固化：

- `sendCode -> login`
- `user.me -> verify.status -> invite.stats -> level.info -> card.personalization`
- fresh session 下复用 Bearer token 的恢复结果

适用场景：

- 当前阶段只验“手机号登录 / 会话恢复”主线
- 不希望把微信门禁混进手机号主线判断
- 需要把 `userId / level / inviteCount / membershipTier / reasonCodes` 固定到同一份真实样本

## 2.3 当前阶段注册链样本

```powershell
python .sce/specs/00-28-architecture-driven-delivery-governance/execution/login-auth/run-login-auth-register-invite-sample.py `
  --environment dev `
  --label register-invite-mainline
```

脚本会直接固化：

- 邀请人登录并获取 `inviteCode`
- 新手机号 `sendCode -> register(inviteCode)`
- `user.me` 回读 `invitedByUserId`
- 后台 `referral_record` 回读
- fresh session 下复用 Bearer token 的恢复结果

适用场景：

- 当前阶段要补 `手机号注册 + inviteCode` 样本
- 不希望继续手工拼未注册手机号或手工翻后台记录
- 需要把 login-auth 注册链和 invite 事实链收口到同一份样本

## 2.4 当前阶段页面级证据样本

```powershell
python .sce/specs/00-28-architecture-driven-delivery-governance/execution/login-auth/run-login-auth-mini-program-page-evidence.py `
  20260404-023118-dev-continue-phone-session-mainline `
  continue-login-auth-mini-program-page-evidence
```

脚本会直接固化：

- `pages/login/index?inviteCode=...`
- `pages/mine/index`
- `pkg-card/membership/index`
- `pkg-card/invite/index`

并为每页落盘：

- `route + query`
- `screenshot`
- `page-data`

注意：

- 登录页采证前脚本会主动清理 `kp_token / kp_user`，避免旧会话把未登录页重定向到首页
- `role-select` 当前不在这条真实样本里，因为现网手机号样本已是明确身份用户

## 2.5 微信门禁先行

若目标是继续推进 `wechat-login`，在任何 live probe 或真实微信授权前，先执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-local-wechat-config-inputs.py --label login-auth-wechat-gate
```

若仍是 placeholder / fake secret，再执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-wechat-config-sync-pipeline.py --label login-auth-wechat-gate --dry-run
```

用途：

- 固定当前 blocker 是否仍是 `local_input_not_ready`
- 避免把“后端源码有 placeholder”误写成“已具备真实微信输入”
- 保证 login-auth 与 invite 使用同一套 `00-29` 门禁口径

## 3. 人工补证顺序

1. 打开 `runtime-summary.md`，确认当前环境是否具备真实联调前置
   - 若目标包含微信链路，再对照 `.sce/runbooks/backend-admin-release/wechat-config-gate-runbook.md`
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
