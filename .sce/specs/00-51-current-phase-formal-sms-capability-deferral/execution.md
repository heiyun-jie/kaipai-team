# 00-51 执行记录

## 1. 调查结论

- login-auth 当前阶段非微信主线已经具备真实样本：
  - 手机号登录 / 会话恢复
  - 手机号注册 + `inviteCode`
  - 小程序页面级证据
- 当前唯一剩余口径分歧，是 `sendCode` 仍直返开发态验证码
- 这件事属于“正式短信能力未商用”，而不是“当前阶段手机号主链没闭环”

## 2. 本轮落地

- 新增 `00-51` Spec，正式记录“正式短信能力降级出当前阶段主阻塞”
- 回写 `phase-01-roadmap.md`、`tasks.md`、`slices/login-auth-capability-slice.md`
- 回写 `status/login-auth-status.md` 与 `status/overall-architecture-assessment.md`
- 回写 `execution/login-auth/README.md`、`real-env-validation-checklist.md`、`integration-execution-card.md`
- 完成 spec 索引与映射登记

## 3. 验证

- 本轮为治理收口，不涉及运行时代码改动或发布
- 已复核当前口径与既有真实样本一致：
  - `execution/login-auth/samples/20260404-023118-dev-continue-phone-session-mainline/summary.md`
  - `execution/login-auth/samples/20260404-023737-dev-continue-register-invite-mainline/summary.md`
  - `execution/login-auth/samples/20260404-024533-continue-login-auth-mini-program-page-evidence-rerun/summary.md`
- 这说明 `00-51` 当前不是“定义一个未来需求”，而是把已经收口的当前阶段手机号主链从“被正式短信口径误卡”中解耦出来

## 4. 后续入口

- 当前阶段 login-auth 进入维护态复验，统一复用：
  - `run-login-auth-phone-session-sample.py`
  - `run-login-auth-register-invite-sample.py`
  - `run-login-auth-mini-program-page-evidence.py`
- 未来若明确推进正式短信能力，再以 `00-51` 为上位入口补真实短信通道、送达/失败治理与正式样本
