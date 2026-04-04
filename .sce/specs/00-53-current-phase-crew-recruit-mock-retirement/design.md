# 00-53 设计说明

## 1. 设计原则

- 已有真实接口的链路优先单事实源，不保留页面级 mock 双轨
- 只退当前阶段已经真实接通的招募链路，不顺手扩散到其他能力域
- 文档、运行时能力表和实际 API 实现必须一起收口，不能只删调用点
- 保留“全局显式 mock 演示态仍存在”这一事实，但不再让它覆盖当前阶段招募主链

## 2. 当前阶段收口边界

| 模块 | 当前阶段策略 | 本轮不做 |
|------|--------------|----------|
| `src/api/company.ts` | 直接请求真实 `/api/company/*` | 不再保留公司档案 mock |
| `src/api/project.ts` | 直接请求真实 `/api/project/*` | 不再保留项目 CRUD mock |
| `src/api/role.ts` | 保留 query sanitization，直接请求真实 `/api/role/*` | 不再保留角色读写 / 查询 mock |
| `src/api/apply.ts` | 直接请求真实 `/api/apply/*` | 不再保留投递读写 mock |
| `src/mock/service.ts` | 删除无入口的 company / project / role / apply mock | 不清理其他能力域 mock |
| `src/utils/runtime.ts` | 删除无使用方 capability | 不改全局 mock 总闸 |

## 3. 实现方案

### 3.1 API 层

- `company.ts` 删除 `useApiMock` 和相关 mock import，所有方法只走真实请求
- `project.ts` 删除 `useApiMock` 和相关 mock import，所有方法只走真实请求
- `role.ts` 保留 `sanitizeRoleSearchParams()`，删除 mock 分支后统一走真实请求
- `apply.ts` 删除 mock 分支，统一走真实请求

### 3.2 Mock 服务层

- 删除以下已无入口函数：
  - `getCompanyInfoMock`
  - `updateCompanyInfoMock`
  - `getMyCompanyMock`
  - `createProjectMock`
  - `updateProjectMock`
  - `deleteProjectMock`
  - `getProjectMock`
  - `getProjectListMock`
  - `getMyProjectsMock`
  - `createRoleMock`
  - `updateRoleMock`
  - `deleteRoleMock`
  - `getRoleMock`
  - `getRolesByProjectMock`
  - `searchRolesMock`
  - `submitApplyMock`
  - `cancelApplyMock`
  - `getMyAppliesMock`
  - `getAppliesByRoleMock`
  - `approveApplyMock`
  - `rejectApplyMock`
  - `getApplyDetailMock`
- 同步删除只为这些函数服务的本地辅助函数和类型 / mock 数据 import

### 3.3 Runtime 能力表

- `ApiCapability` 不再保留：
  - `company`
  - `project`
  - `role`
  - `roleRead`
  - `apply`
- `REMOTE_CAPABILITIES` 同步移除上述 capability
- 运行时仍保留全局显式 mock 演示态和其他能力域 capability，不在本轮继续扩散

## 4. 风险与约束

### 4.1 显式 mock 演示态不再覆盖招募链路

- 本轮完成后，即使开发环境打开 `VITE_USE_MOCK=true`，这几条 API 也不会再走本地 mock 服务
- 这不是回归，而是当前阶段明确选择：已真实接通的链路不再维持演示态双轨

### 4.2 真环境错误会暴露得更早

- 若后端、token、baseUrl 或代理有问题，前端会直接返回真实错误
- 这是预期行为，目的是让问题停留在真实环境而不是继续被 mock 掩盖

## 5. 影响文件

- `.sce/specs/00-53-current-phase-crew-recruit-mock-retirement/requirements.md`
- `.sce/specs/00-53-current-phase-crew-recruit-mock-retirement/design.md`
- `.sce/specs/00-53-current-phase-crew-recruit-mock-retirement/tasks.md`
- `.sce/specs/00-53-current-phase-crew-recruit-mock-retirement/execution.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/crew-company-project-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/recruit-role-apply-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `kaipai-frontend/src/api/company.ts`
- `kaipai-frontend/src/api/project.ts`
- `kaipai-frontend/src/api/role.ts`
- `kaipai-frontend/src/api/apply.ts`
- `kaipai-frontend/src/mock/service.ts`
- `kaipai-frontend/src/utils/runtime.ts`
