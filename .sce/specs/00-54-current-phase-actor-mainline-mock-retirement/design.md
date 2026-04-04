# 00-54 设计说明

## 1. 设计原则

- 演员首页主入口依赖的读取链路必须单事实源
- 只退 actor 主线 API mock，不扩散清理 `mockActors` 的其他演示用途
- 文档、API 实现和 runtime capability 必须一起收口
- 当前阶段已切真的主入口，不再允许继续保留“页面级演示双轨”

## 2. 当前阶段收口边界

| 模块 | 当前阶段策略 | 本轮不做 |
|------|--------------|----------|
| `src/api/actor.ts` | 四个接口统一走真实 `/api/actor*` | 不再保留 actor API mock |
| `src/mock/service.ts` | 删除 actor API mock 函数 | 不删除依赖 `mockActors` 的 invite / AI / fortune mock |
| `src/mock/database.ts` | 保留 `mockActors` 基础数据 | 不把 actor 相关 mock 基础数据整包清空 |
| `src/utils/runtime.ts` | 删除 `actor` capability | 不改其他能力域 capability |

## 3. 实现方案

### 3.1 API 层

- `src/api/actor.ts` 删除 `useApiMock` 和 actor mock import
- `getMyActorProfile()` 直接请求 `/api/actor/profile/mine`
- `updateActorProfile()` 直接请求 `/api/actor/profile`
- `searchActors()` 直接请求 `/api/actor/search`
- `getActorDetail()` 直接请求 `/api/actor/{userId}`

### 3.2 Mock 服务层

- 删除：
  - `getActorProfileMock`
  - `updateActorProfileMock`
  - `searchActorsMock`
  - `getActorDetailMock`
- 只保留仍被其他 mock 能力域真实引用的 `mockActors` 相关辅助逻辑

### 3.3 Runtime 能力表

- `ApiCapability` 删除 `actor`
- `REMOTE_CAPABILITIES` 同步删除 `actor`
- 这样后续任何读代码的人都不会再误判“演员主线仍存在 capability 级 mock 兜底”

## 4. 风险与约束

### 4.1 明确接受真实错误暴露

- 本轮完成后，演员首页、演员详情和档案编辑遇到接口、鉴权或环境问题时，会直接暴露真实错误
- 这不是回归，而是为了避免再被本地 mock 掩盖

### 4.2 `mockActors` 仍可服务其他演示域

- invite、fortune、AI 这些仍未完全退场的 mock 演示域，当前还会读取 `mockActors`
- 因此本轮不删除 `mockActors` 数据本身，只切断 actor 主线 API 对它的运行时依赖

## 5. 影响文件

- `.sce/specs/00-54-current-phase-actor-mainline-mock-retirement/requirements.md`
- `.sce/specs/00-54-current-phase-actor-mainline-mock-retirement/design.md`
- `.sce/specs/00-54-current-phase-actor-mainline-mock-retirement/tasks.md`
- `.sce/specs/00-54-current-phase-actor-mainline-mock-retirement/execution.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/recruit-role-apply-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `kaipai-frontend/src/api/actor.ts`
- `kaipai-frontend/src/mock/service.ts`
- `kaipai-frontend/src/utils/runtime.ts`
