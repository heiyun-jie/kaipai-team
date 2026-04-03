# 00-48 设计说明

## 1. 设计原则

- 不删未来能力，只调整当前阶段优先级
- 不口头绕过门禁，而是显式把门禁移出当前阶段主验收面
- 让路线图、状态页、runbook 三处口径一致

## 2. 设计策略

### 2.1 路线图降级

在 `00-28` 路线图与整体评估中：

- 删除“invite / login-auth 微信配置与真实样本”为当前阶段第一优先级的表述
- 改为将微信能力标注为“后续能力批次”
- 当前主推进顺位切回 membership / AI / verify 收尾等真实主线

### 2.2 状态页重写

对 `invite-status.md` 与 `login-auth-status.md`：

- 保留微信代码主链与门禁事实
- 但把微信相关问题从“当前阻塞项”改成“当前阶段不阻塞 / 后续能力”
- 将下一轮动作改为当前版本真正要推进的验收面

### 2.3 Runbook 保留但限域

对 `wechat-config-gate-runbook.md`：

- 不删除步骤
- 在开头新增适用范围说明：仅当某一批次明确要推进微信登录或官方 `wxacode` 时才启用

## 3. 影响文件

- `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/invite-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/login-auth-status.md`
- `.sce/runbooks/backend-admin-release/wechat-config-gate-runbook.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
