# 00-53 执行记录

## 1. 调查结论

- `company / project / role / apply` 四条前端 API 当前仍保留 `useApiMock(...)` 分支
- 对应真实接口已在后端控制器存在，并且 `00-28` 状态页已把这条链路记录为真实联通主线
- `src/mock/service.ts` 仍保留整套剧组招募 mock 服务，且当前只有上述 API 模块在使用
- `src/utils/runtime.ts` 仍把 `company / project / role / roleRead / apply` 作为 mock capability 暴露，容易继续误导为“当前阶段仍允许这些链路退回 mock”

## 2. 本轮落地

- 新增 `00-53` Spec，单独固化当前阶段剧组招募链路前端 mock 退场范围与边界
- `kaipai-frontend/src/api/company.ts` 已删除 `useApiMock('company')` 分支，统一走真实 `/api/company/*`
- `kaipai-frontend/src/api/project.ts` 已删除 `useApiMock('project')` 分支，统一走真实 `/api/project/*`
- `kaipai-frontend/src/api/role.ts` 已删除 `useApiMock('role'/'roleRead')` 分支，保留 query sanitization 后统一走真实 `/api/role/*`
- `kaipai-frontend/src/api/apply.ts` 已删除 `useApiMock('apply')` 分支，统一走真实 `/api/apply/*`
- `kaipai-frontend/src/mock/service.ts` 已删除无运行时入口的 company / project / role / apply mock 服务与对应辅助函数
- `kaipai-frontend/src/mock/database.ts` 已删除已无引用的剧组招募 mock 假数据
- `kaipai-frontend/src/utils/runtime.ts` 已删除 `company / project / role / roleRead / apply` capability
- 已同步回填 `00-28/tasks.md`、`phase-01-roadmap.md`、`crew-company-project-status.md`、`recruit-role-apply-status.md`、`overall-architecture-assessment.md`

## 3. 验证

- 已执行 `kaipai-frontend npm run type-check`，通过
- 已全文回扫前端源码，确认以下内容无剩余运行时引用：
  - `useApiMock('company' | 'project' | 'role' | 'roleRead' | 'apply')`
  - `getCompanyInfoMock / createProjectMock / searchRolesMock / getApplyDetailMock`
  - `mockCompanies / mockProjects / mockRoles / mockApplies`

## 4. Spec 回填

- 已完成 `.sce/specs/README.md` 增量登记
- 已完成 `.sce/specs/spec-code-mapping.md` 映射登记
- 已完成 `00-28` 路线图、任务与状态文档回填
