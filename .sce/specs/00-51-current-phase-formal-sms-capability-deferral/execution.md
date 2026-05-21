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
- `2026-04-05` 又已新增 `execution/login-auth/formal-sms-validation-gate.md`，明确什么情况下才允许把 `sendCode` 从“开发态直返验证码”推进到“正式短信能力验证”
- 同日 `execution/login-auth/run-login-auth-phone-session-sample.py` 又已修正为 `shareCardId-first`，并产出桥接样本 `execution/login-auth/samples/20260405-233350-dev-share-card-sms-bridge/summary.md`
- 同日 `execution/share-card-mvp/sms-capability-bridge.md` 也已把 share-card 当前剩余的 `sendCode` 口径显式桥接到 `00-51 + login-auth`，避免后续再把正式短信能力误写成 share-card 主链未闭环
- `2026-04-05` 又已新增 `execution/login-auth/formal-sms-validation-sample-template.md`，把未来正式短信批次所需的成功 / 失败 / 配置来源 / 登录回归证据结构提前模板化，避免正式进入商用验证时再临时拼样本
- `2026-04-06` 又已把未来 formal-sms 发布后总控结构默认接到 `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`，后续该批次若进入真实发布回归，默认仍先读 `releaseGoNoGoCard -> operatorRunCard`

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
- 当前若要判断“是否已具备正式短信验证前提”，固定先看：
  - `execution/login-auth/formal-sms-validation-gate.md`
- 当前若要真正创建 future batch 样本，固定先从：
  - `execution/login-auth/formal-sms-validation-sample-template.md`
- 当前若后续要创建 formal-sms 发布后总控卡，固定先从：
  - `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\release-post-control-card-template.md`
