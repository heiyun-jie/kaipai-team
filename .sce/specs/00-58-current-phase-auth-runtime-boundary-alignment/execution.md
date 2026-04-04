# 00-58 执行记录

## 1. 调查结论

- `src/utils/runtime.ts` 当前只剩 `auth / wechatAuth` 两个 capability
- `src/api/auth.ts` 当前仍用 `useApiMock('auth') / useApiMock('wechatAuth')`
- 但 `login-auth-status.md` 已明确：手机号主链当前阶段闭环完成，微信是否可用由显式门禁控制
- 因此当前真正应该保留的是“显式 mock 演示态总闸 + 微信配置门禁”，而不是 capability 表

## 2. 本轮落地

- 新增 `00-58` Spec，单独固化当前阶段 auth runtime 边界
- `kaipai-frontend/src/utils/runtime.ts` 已删除 `ApiCapability`、`REMOTE_CAPABILITIES` 与 `useApiMock(...)`
- `kaipai-frontend/src/api/auth.ts` 已把 `sendSmsCode / loginByPhone / registerByPhone / loginByWechat` 统一收口为 `useMock()` 或真实 `/api/auth/*`
- 已同步回填 `00-28/tasks.md`、`phase-01-roadmap.md`、`login-auth-status.md`、`membership-status.md`、`overall-architecture-assessment.md`

## 3. 验证

- 已执行 `kaipai-frontend npm run type-check`，通过
- 已全文回扫前端源码，确认 `useApiMock(` 已无运行时引用

## 4. Spec 回填

- 已完成 `.sce/specs/README.md` 增量登记
- 已完成 `.sce/specs/spec-code-mapping.md` 映射登记
- 已完成 `00-28` 路线图、任务与状态文档回填
