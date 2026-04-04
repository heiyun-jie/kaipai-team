# 00-55 设计说明

## 1. 设计原则

- 已闭环或已稳定的当前阶段能力优先单事实源
- 只退 invite / verify / fortune 三条辅助能力，不扩散到 level / card / ai
- API、runtime capability、mock service 和状态文档一起收口
- 保留未来批次入口和其余 mock 演示域，不做范围外清理

## 2. 当前阶段收口边界

| 模块 | 当前阶段策略 | 本轮不做 |
|------|--------------|----------|
| `src/api/invite.ts` | 统一走真实 `/api/invite/*` | 不再保留 invite API mock |
| `src/api/verify.ts` | 统一走真实 `/api/verify/*` | 不再保留 verify API mock |
| `src/api/fortune.ts` | 统一走真实 `/api/fortune/*` | 不再保留 fortune API mock |
| `src/mock/service.ts` | 删除对应 API mock 函数 | 不删除 auth mock 仍依赖的 invite 基础数据逻辑 |
| `src/mock/database.ts` | 删除 verify / fortune 无引用数据 | 保留仍被 auth mock 使用的 invite 数据 |
| `src/utils/runtime.ts` | 删除 `invite / verify / fortune` capability | 不改 `level / card / ai / auth` 等其余 capability |

## 3. 实现方案

### 3.1 API 层

- `invite.ts` 删除 `useApiMock` 和 mock import，统一走真实请求
- `verify.ts` 删除 `useApiMock` 和 mock import，统一走真实请求
- `fortune.ts` 删除 `useApiMock` 和 mock import，统一走真实请求

### 3.2 Mock 服务层

- 删除 7 个已无入口 API mock 函数
- 同步删除只服务于这些函数的私有 helper、类型导入和工具导入
- invite 基础统计与注册 mock 依赖保留，不误伤 auth mock

### 3.3 Mock 数据层

- 若 `mockIdentityVerifications`、`mockFortuneReports` 失去全部引用，则连同其局部 interface 一起删除
- `mockInviteCodes`、`mockReferralRecords` 继续保留给 auth mock 注册 / 邀请统计模拟使用

### 3.4 Runtime 能力表

- `ApiCapability` 删除：
  - `invite`
  - `verify`
  - `fortune`
- `REMOTE_CAPABILITIES` 同步删除这三项

## 4. 风险与约束

### 4.1 真实错误将被直接暴露

- 本轮完成后，invite / verify / fortune 遇到接口、鉴权或环境问题时，会直接暴露真实错误
- 这是预期行为，用来阻止局部 mock 继续掩盖真实环境问题

### 4.2 membership 主线仍不在本轮继续扩大

- `/fortune/*` 已切真，不代表 `/level / card / ai` 要在同一轮一并退场
- membership 相关更大事实源问题继续留在 `00-49` 与后续 spec

## 5. 影响文件

- `.sce/specs/00-55-current-phase-invite-verify-fortune-mock-retirement/requirements.md`
- `.sce/specs/00-55-current-phase-invite-verify-fortune-mock-retirement/design.md`
- `.sce/specs/00-55-current-phase-invite-verify-fortune-mock-retirement/tasks.md`
- `.sce/specs/00-55-current-phase-invite-verify-fortune-mock-retirement/execution.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/invite-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/verify-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/membership-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `kaipai-frontend/src/api/invite.ts`
- `kaipai-frontend/src/api/verify.ts`
- `kaipai-frontend/src/api/fortune.ts`
- `kaipai-frontend/src/utils/runtime.ts`
- `kaipai-frontend/src/mock/service.ts`
- `kaipai-frontend/src/mock/database.ts`
