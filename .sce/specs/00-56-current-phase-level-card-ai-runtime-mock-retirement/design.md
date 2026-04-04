# 00-56 设计说明

## 1. 设计原则

- 当前阶段主事实源优先单一来源，membership 统一认 `/api/card/personalization`，AI 统一认 `/api/ai/*`
- 只收口 `level / card / ai` 运行时双轨，不扩散到 `auth / upload`
- API、runtime capability、mock service、mock database 和治理文档一起收口
- 继续遵守 `00-49`：preview overlay 只保留为 session 级未保存预览态，不借本轮退场去重做后端化

## 2. 当前阶段收口边界

| 模块 | 当前阶段策略 | 本轮不做 |
|------|--------------|----------|
| `src/api/level.ts` | 统一走真实 `/api/level/info`、`/api/card/*`、`/api/ai/quota` | 不改 auth / upload |
| `src/api/ai.ts` | 统一走真实 `/api/ai/*` | 不扩 AI 治理协同边界 |
| `src/utils/personalization.ts` | 统一只消费 `/api/card/personalization`，只保留 preview overlay session helper | 不把 overlay 升级成后端事实源 |
| `src/api/personalization.ts` | 删除 fallback helper，只保留 personalization 聚合查询 | 不改分享 path / 主题 token 规则 |
| `src/mock/service.ts` / `src/mock/database.ts` | 删除已无入口的 `level / card / ai` mock 函数、helper 和数据 | 不误删 auth 仍依赖的数据 |
| `src/utils/runtime.ts` | 删除 `level / card / ai` capability | 不动 `auth / wechatAuth / userInfo / roleSwitch / upload` |

## 3. 实现方案

### 3.1 API 层

- `src/api/level.ts` 删除 `useApiMock` 与对应 mock import，统一走真实请求
- `src/api/ai.ts` 删除 `useApiMock` 与对应 mock import，统一走真实请求
- `src/api/personalization.ts` 删除只为本地 fallback 存在的 `sceneTemplates / cardConfig / fortuneReport` helper

### 3.2 Personalization 聚合层

- `src/utils/personalization.ts` 删除 `useApiMock('card')` 分支
- `resolvePersonalizationProfile(...)` 当前只接受后端 `/api/card/personalization` 返回结果，再做当前阶段 artifact 归一化
- 保留 `buildCardConfigFromPersonalization(...)` 与 preview overlay session helper，继续服务编辑态未保存预览

### 3.3 Mock 服务与数据层

- 删除已无入口的 `level / card / ai` API mock 函数
- 同步删除只服务于这些函数的私有 helper、类型导入和 mock data
- 保留 auth mock 注册 / 邀请仍依赖的用户、演员、邀请码、邀请记录基础数据

### 3.4 Runtime 能力表

- `ApiCapability` 删除：
  - `level`
  - `card`
  - `ai`
- `REMOTE_CAPABILITIES` 同步删除这三项

## 4. 风险与约束

### 4.1 真实错误会被直接暴露

- 本轮完成后，`level / card / ai` 接口、鉴权或环境问题都会直接暴露真实错误
- 这是预期行为，用来阻止 membership / AI 主线继续被前端局部 mock 或本地拼装掩盖

### 4.2 预览态边界不能被顺手扩散

- 删除 personalization fallback 不等于 preview overlay 可以继续膨胀为第二事实源
- `00-49` 已明确：overlay 只允许是当前设备 session 级未保存预览态

### 4.3 AI 治理升级仍由 00-50 承接

- 本轮只退前端 runtime mock，不混入通知回执、自动催办、SLA 或真实 LLM 接入
- AI 下一步仍以 `00-50` 为单独治理入口推进

## 5. 影响文件

- `.sce/specs/00-56-current-phase-level-card-ai-runtime-mock-retirement/requirements.md`
- `.sce/specs/00-56-current-phase-level-card-ai-runtime-mock-retirement/design.md`
- `.sce/specs/00-56-current-phase-level-card-ai-runtime-mock-retirement/tasks.md`
- `.sce/specs/00-56-current-phase-level-card-ai-runtime-mock-retirement/execution.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/membership-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/ai-resume-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `kaipai-frontend/src/api/level.ts`
- `kaipai-frontend/src/api/ai.ts`
- `kaipai-frontend/src/api/personalization.ts`
- `kaipai-frontend/src/utils/personalization.ts`
- `kaipai-frontend/src/utils/runtime.ts`
- `kaipai-frontend/src/mock/service.ts`
- `kaipai-frontend/src/mock/database.ts`
