# 00-51 当前阶段正式短信能力降级出主阻塞（Current Phase Formal SMS Capability Deferral）

> 状态：已完成 | 优先级：P1 | 依赖：00-28 architecture-driven-delivery-governance，00-48 current-phase-wechat-capability-deferral
> 记录目的：把 login-auth 中“`sendCode` 开发态直返验证码”从当前阶段主阻塞降级为后续正式短信能力批次，避免继续把当前阶段手机号主链与商业短信接入混写。

## 1. 背景

当前仓内已经通过真实样本收口了 login-auth 当前阶段非微信主线：

- 手机号 `sendCode -> login -> /user/me -> /verify/status -> /invite/stats -> /level/info -> /card/personalization -> fresh-session restore`
- 手机号 `sendCode -> register(inviteCode) -> /user/me.invitedByUserId -> admin referral_record -> fresh-session restore`
- 小程序 `login(带inviteCode) -> mine -> membership -> invite` 页面级证据

当前剩余未闭环点，已经不再是“手机号登录 / 注册 / 会话恢复是否可跑通”，而是：

- `AuthServiceImpl.sendCode(...)` 仍处于开发态直返验证码口径
- 这能证明接口、Redis 校验和登录主链接通，但不能视为正式短信商用能力闭环

如果继续把这件事写成 login-auth 当前阶段 blocker，就会让当前阶段状态一直停在“局部完成”，与 `slices/login-auth-capability-slice.md` 中“短信网关正式商用接入本就不在本轮范围”的边界冲突。

## 2. 范围

### 2.1 本轮必须处理

- `00-28` 路线图与总体评估
- `login-auth-status.md`
- `slices/login-auth-capability-slice.md`
- `execution/login-auth/*` 中与验收口径直接相关的文档
- spec 索引、映射与 `00-28/tasks.md`

### 2.2 本轮不处理

- 接入真实短信服务商
- 补短信发送回执、模板管理、费用治理或风控运营台账
- 改造 `sendCode` 为正式商用短信实现
- 新增运行时代码或发布动作

## 3. 需求

### 3.1 当前阶段口径校正

- **R1** 当前阶段不得再把“`sendCode` 开发态直返验证码”写成 login-auth 当前阶段主阻塞。
- **R2** login-auth 当前阶段验收应以“手机号登录 / 注册、`inviteCode` 透传、会话恢复、登录后摘要同步、页面级证据”作为主口径。
- **R3** 开发态 `sendCode` 只能被记录为“当前 dev 运行时事实”，不得被误写成“正式短信能力已闭环”，也不得继续阻塞当前阶段状态升级。

### 3.2 后续能力保留

- **R4** 正式短信能力必须保留为未来能力批次，包括但不限于：真实短信网关、发送失败治理、发送频控、模板/通道配置与真实送达口径。
- **R5** 文档必须把正式短信能力描述为 future batch / deferred，而不是当前阶段 blocker。

### 3.3 治理回填

- **R6** 必须通过独立 Spec 回填本次口径变更，不得只在状态页里口头说明。
- **R7** 必须同步更新登录切片卡、执行卡、验证清单、路线图、状态页、Spec 索引与映射，保证后续能追溯“为什么 login-auth 已从当前阶段局部完成推进到当前阶段闭环完成”。

## 4. 验收标准

- [x] 已新增独立 `00-51` Spec 并登记索引与映射
- [x] `00-28` 路线图与总体评估不再把正式短信能力写成当前阶段 blocker
- [x] `login-auth-status.md` 已把当前判定收口为“当前阶段闭环完成”，并把正式短信能力改写为后续批次
- [x] `slices/login-auth-capability-slice.md` 与 `execution/login-auth/*` 已同步区分“当前阶段闭环完成”和“未来全量闭环”
