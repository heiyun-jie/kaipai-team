# 00-61 执行记录

## 1. 调查结论

- `src/api/auth.ts` 当前仍是前端最后一条完整 auth mock 主链入口
- `src/stores/user.ts` 的 `bootstrapSession()` 仍保留 mock 会话恢复分支
- `src/mock/service.ts`、`src/mock/database.ts` 当前只再服务于 auth 域
- `VITE_USE_MOCK=true` 且缺少 `VITE_API_BASE_URL` 时，现有运行时门禁还不足以阻止 auth 被误判为可演示

## 2. 本轮落地

- 新增 `00-61` Spec，单独固化当前阶段 auth 显式 mock 退场
- 删除 `kaipai-frontend/src/api/auth.ts` 中 auth mock 分支，统一改走真实 `/api/auth/*` 与 `/api/user/*`
- 删除 `kaipai-frontend/src/stores/user.ts` 中 mock 会话恢复逻辑，并同步调整登录页 / runtime 门禁
- 删除 `kaipai-frontend/src/mock/service.ts`、`kaipai-frontend/src/mock/database.ts`
- 已同步回填 `00-28/tasks.md`、`phase-01-roadmap.md`、`execution/login-auth/README.md`、`login-auth-status.md`、`overall-architecture-assessment.md`

## 3. 验证

- 已执行 `kaipai-frontend npm run type-check`，通过
- 已全文回扫前端源码，确认 `@/mock/service`、`@/mock/database`、`syncMockSession(` 已无运行时引用

## 4. Spec 回填

- 已完成 `.sce/specs/README.md` 增量登记
- 已完成 `.sce/specs/spec-code-mapping.md` 映射登记
- 已完成 `00-28` 路线图、任务、状态文档与执行入口回填
