# 00-57 执行记录

## 1. 调查结论

- `src/api/auth.ts` 当前仍把 `getUserInfo / updateUserRole` 建模为 `userInfo / roleSwitch` 两个独立 runtime capability
- `src/utils/upload.ts` 当前仍把上传能力建模为独立 `upload` capability
- `login-auth-status.md` 已明确 `/api/user/me` 当前阶段闭环完成，`crew-company-project-status.md` 也已明确 `upload.ts` 可直接走后端文件上传接口
- 因此当前问题已不再是“这些接口是否存在”，而是“前端 runtime 是否还在把它们误解为独立 mock 能力”

## 2. 本轮落地

- 新增 `00-57` Spec，单独固化当前阶段会话摘要 / 身份切换 / 上传运行时边界
- `kaipai-frontend/src/api/auth.ts` 已把 `getUserInfo / updateUserRole` 收口为：
  - `useMock()` 时继续走本地 auth 演示态
  - 非显式 mock 环境统一走真实 `/api/user/me`、`/api/user/role`
- `kaipai-frontend/src/utils/upload.ts` 已把上传收口为：
  - `useMock()` 时继续走本地 filePath 回显
  - 非显式 mock 环境统一走真实 `/api/file/upload/*`
- `kaipai-frontend/src/utils/runtime.ts` 已删除 `userInfo / roleSwitch / upload` capability
- 已同步回填 `00-28/tasks.md`、`phase-01-roadmap.md`、`login-auth-status.md`、`crew-company-project-status.md`、`membership-status.md`、`overall-architecture-assessment.md`

## 3. 验证

- 已执行 `kaipai-frontend npm run type-check`，通过
- 已全文回扫前端源码，确认以下独立 runtime 能力引用已不存在：
  - `useApiMock('userInfo')`
  - `useApiMock('roleSwitch')`
  - `useApiMock('upload')`

## 4. Spec 回填

- 已完成 `.sce/specs/README.md` 增量登记
- 已完成 `.sce/specs/spec-code-mapping.md` 映射登记
- 已完成 `00-28` 路线图、任务与状态文档回填
