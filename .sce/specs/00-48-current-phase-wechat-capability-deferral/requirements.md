# 00-48 当前阶段微信能力降级出主阻塞（Current Phase WeChat Capability Deferral）

> 状态：已完成 | 优先级：P1 | 依赖：00-28 architecture-driven-delivery-governance，00-29 backend-admin-release-governance
> 记录目的：把 invite `wxacode` 与 login-auth 微信登录从“当前阶段主阻塞”降级为“后续能力批次”，避免继续错误占用当前版本主推进顺位。

## 1. 背景

当前仓内已经为两类微信能力补齐了代码主链与门禁 runbook：

- invite 官方小程序码 `wxacode`
- login-auth 微信登录 `wechat-login`

但当前版本实际主线并不要求这两项能力作为发布前置。继续把“缺合法 `WECHAT_MINIAPP_APP_SECRET` 来源”写成当前阶段第一优先级阻塞，会导致路线图、状态页和执行顺序偏离真实产品范围。

## 2. 范围

### 2.1 本轮必须处理

- `00-28` 路线图与总体评估
- `invite-status.md`
- `login-auth-status.md`
- 微信门禁 runbook 顶部适用范围说明
- spec 索引与代码映射

### 2.2 本轮不处理

- 删除微信登录或 `wxacode` 相关代码
- 删除 `00-29` 微信配置同步脚本
- 重新定义未来微信能力批次的详细验收规则

## 3. 需求

### 3.1 当前阶段口径校正

- **R1** 当前阶段不得再把 invite `wxacode` 与 login-auth 微信登录写成主阻塞或第一优先级工作流。
- **R2** invite 当前阶段验收应以“邀请码承接、注册链接/二维码、注册绑定、资格链与前后台一致性”作为主口径，不以官方 `wxacode` 为前置。
- **R3** login-auth 当前阶段验收应以“手机号验证码登录/注册、会话恢复、`inviteCode` 透传”作为主口径，不以微信登录为前置。

### 3.2 后续能力保留

- **R4** 微信门禁 runbook、同步脚本与执行卡必须保留，但要明确只在显式推进微信能力批次时启用。
- **R5** 文档必须把微信能力描述为 deferred / future batch，而不是当前阶段 blocker。

### 3.3 治理回填

- **R6** 必须通过独立 Spec 回填本次口径变更，不得只改状态页。
- **R7** 必须同步更新 spec 索引与映射，保证后续能追溯“为什么微信门禁不再卡当前阶段”。

## 4. 验收标准

- [x] 已新增独立 `00-48` Spec 并登记索引与映射
- [x] `00-28` 路线图与总体评估不再把微信门禁写成当前阶段第一优先级阻塞
- [x] `invite-status.md` 与 `login-auth-status.md` 已把微信能力降级为后续能力批次
- [x] 微信门禁 runbook 已明确仅在显式推进微信能力批次时启用
