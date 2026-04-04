# 00-51 设计说明

## 1. 设计原则

- 不否认开发态 `sendCode` 仍不是正式短信能力
- 不因为正式短信尚未商用，就让当前阶段手机号主链一直停留在“局部完成”
- 让切片卡、状态页、执行卡和路线图四处口径一致

## 2. 设计策略

### 2.1 双层闭环口径显式化

本 Spec 把 login-auth 的完成定义拆成两层：

1. 当前阶段闭环
   - 手机号登录 / 注册
   - `inviteCode` 透传
   - 会话恢复
   - 登录后摘要同步
   - 页面级证据
2. 未来全量闭环
   - 正式短信网关
   - 真实短信送达与失败治理
   - 如需推进，再叠加微信真实能力批次

### 2.2 开发态事实与商用能力分离

统一口径如下：

- `sendCode` 当前直返验证码，是 dev 运行时事实
- 它可以继续作为当前阶段样本入口
- 但不能再被当成“正式短信能力 blocker”写回当前阶段状态

### 2.3 验证文档重写

后续相关文档统一按下面的结构描述：

- 当前阶段闭环完成条件
- 未来批次能力入口
- 何时必须重新进入正式短信治理

## 3. 影响文件

- `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/slices/login-auth-capability-slice.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/login-auth-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/execution/login-auth/README.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/execution/login-auth/real-env-validation-checklist.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/execution/login-auth/integration-execution-card.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`

## 4. 后续实现分层

### 4.1 后端

- 接入正式短信服务商或网关
- 固化发送失败、频控和审计口径
- 明确 dev 口径与正式口径的切换方式

### 4.2 运维 / 配置

- 明确短信通道配置、密钥来源和环境差异
- 明确真实运行时 smoke 与回滚要求

### 4.3 验证

- 在未来正式短信批次中新增独立样本入口
- 补送达/失败/限流样本
- 再决定是否把 login-auth 从“当前阶段闭环完成”升级为“全量闭环完成”
