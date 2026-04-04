# 00-55 执行记录

## 1. 调查结论

- `src/api/invite.ts`、`src/api/verify.ts`、`src/api/fortune.ts` 当前仍保留 `useApiMock(...)` 双轨分支
- 对应真实接口 `/api/invite/*`、`/api/verify/*`、`/api/fortune/*` 已存在，且 `00-28` 状态页已将它们记录为当前阶段真实主线
- `src/mock/service.ts` 中对应 API mock 函数当前只被这三组 API 模块使用
- `mockInviteCodes / mockReferralRecords` 仍被 auth mock 注册流程使用，不宜误删
- `mockIdentityVerifications / mockFortuneReports` 若移除 verify / fortune API mock 后将失去全部引用，可一并清理

## 2. 本轮落地

- 新增 `00-55` Spec，单独固化当前阶段 invite / verify / fortune 前端 mock 退场范围与边界
- `kaipai-frontend/src/api/invite.ts` 已删除 `useApiMock('invite')` 分支，统一走真实 `/api/invite/*`
- `kaipai-frontend/src/api/verify.ts` 已删除 `useApiMock('verify')` 分支，统一走真实 `/api/verify/*`
- `kaipai-frontend/src/api/fortune.ts` 已删除 `useApiMock('fortune')` 分支，统一走真实 `/api/fortune/*`
- `kaipai-frontend/src/mock/service.ts` 已删除无运行时入口的 invite / verify / fortune API mock 函数
- `kaipai-frontend/src/mock/database.ts` 已删除已无引用的 `mockIdentityVerifications / mockFortuneReports`
- `kaipai-frontend/src/utils/runtime.ts` 已删除 `invite / verify / fortune` capability
- 已同步回填 `00-28/tasks.md`、`phase-01-roadmap.md`、`invite-status.md`、`verify-status.md`、`membership-status.md`、`overall-architecture-assessment.md`

## 3. 验证

- 已执行 `kaipai-frontend npm run type-check`，通过
- 已全文回扫前端源码，确认以下内容无剩余运行时引用：
  - `useApiMock('invite' | 'verify' | 'fortune')`
  - `getInviteInfoMock / getInviteStatsMock / getInviteRecordsMock`
  - `getVerifyStatusMock / submitVerifyMock`
  - `getFortuneReportMock / applyLuckyColorMock`
  - `mockIdentityVerifications / mockFortuneReports`

## 4. Spec 回填

- 已完成 `.sce/specs/README.md` 增量登记
- 已完成 `.sce/specs/spec-code-mapping.md` 映射登记
- 已完成 `00-28` 路线图、任务与状态文档回填
