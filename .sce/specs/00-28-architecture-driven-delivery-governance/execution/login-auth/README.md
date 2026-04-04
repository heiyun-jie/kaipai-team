# 登录鉴权与前台会话闭环执行卡

本目录用于承接 `slices/login-auth-capability-slice.md` 的下一层拆分。

## 目标

把“登录鉴权与前台会话闭环”从能力切片继续拆成可分派、可并行推进、可单独验收的 4 张执行卡：

1. 前端执行卡
2. 后端执行卡
3. 后台 / 运行配置执行卡
4. 联调执行卡

补充一组用于真实环境验收收口的执行资产：

5. `real-env-runtime-inventory.md`
6. `real-env-validation-checklist.md`
7. `real-env-evidence-pack.md`
8. `validation-sample-ledger-template.md`
9. `collect-login-auth-evidence.ps1`
10. `new-login-auth-validation-sample.ps1`
11. `run-login-auth-validation.ps1`
12. `run-login-auth-phone-session-sample.py`
13. `run-login-auth-register-invite-sample.py`
14. `capture-mini-program-screenshots.js`
15. `run-login-auth-mini-program-page-evidence.py`
16. `validation-execution-example.md`
17. `../../../runbooks/backend-admin-release/wechat-config-gate-runbook.md`

## 使用方式

每张执行卡都只负责一个交付面，但必须引用同一张能力切片卡：

- `../../slices/login-auth-capability-slice.md`

## 本轮规则

- 每张卡都要写清楚负责范围，不得跨层级抢活
- 每张卡都要标明依赖项和交付物
- 联调卡不负责补做功能，只负责收口验证、问题清单和回归要求
- 当前必须把“微信登录已接后端契约，但真实环境配置仍可能缺失”写清楚，避免再次把代码接线误判成闭环
- 当前也必须把“`sendCode` 仍是开发态直返验证码”与“正式短信能力 future batch”写清楚，避免再把正式短信能力混进当前阶段闭环判断
- 运行时开关、后端配置和前台按钮显隐必须成组确认，不能只看某一端

## 工具补充

- `run-login-auth-validation.ps1` 会自动创建一次登录联调样本目录，并调用 `collect-login-auth-evidence.ps1` 预填运行时台账、样本台账和验证报告；随后再统一回填 `sample-ledger.md / validation-report.md`
- `run-login-auth-validation.ps1 -EnableLiveProbe` 会在本地扫描基础上，额外请求当前 `VITE_API_BASE_URL` 或显式传入的 `-ProbeBaseUrl`，把 `sendCode / wechat-login` 真实返回写入样本目录
- `run-login-auth-phone-session-sample.py` 用于当前阶段非微信主线的标准样本：直接固化 `sendCode -> login -> user.me -> verify / invite / level / personalization -> fresh-session restore`，不再把微信门禁混入手机号闭环判断
- `run-login-auth-register-invite-sample.py` 用于当前阶段注册主线的标准样本：自动生成新手机号，固化 `inviter login -> inviteCode -> sendCode -> register(inviteCode) -> user.me -> admin referral record -> fresh-session restore`
- `run-login-auth-mini-program-page-evidence.py` 与 `capture-mini-program-screenshots.js` 用于当前阶段页面级证据：固定 `login(带inviteCode) -> mine -> membership -> invite` 四页真实 route/query/screenshot/page-data
- 当前阶段手机号主链已由 `run-login-auth-phone-session-sample.py`、`run-login-auth-register-invite-sample.py` 与 `run-login-auth-mini-program-page-evidence.py` 三类样本收口；若只剩 `sendCode` 开发态直返验证码，不再把它记为当前阶段 blocker，正式短信能力统一转入 `00-51 current-phase-formal-sms-capability-deferral`
- `collect-login-auth-evidence.ps1` 现在会同时区分三层事实：后端源码是否暴露微信配置位、本地 gitignored secret 文件是否存在、以及本地 `WECHAT_MINIAPP_APP_SECRET` 是否通过合法输入门禁
- 自动回填默认只覆盖仓内可直接抽取的运行时与阻塞事实；开启 `-EnableLiveProbe` 后会把“接口已接通但被配置阻塞”的样本台账与验证报告统一落盘，但真实微信报文、页面截图和数据库结果仍需要人工补回同一份样本目录
- 当 login-auth 需要进入微信真实验证时，必须先走 `.sce/runbooks/backend-admin-release/wechat-config-gate-runbook.md`，不允许因为“源码里有 placeholder”或“本地 secret 文件存在”就跳过门禁
