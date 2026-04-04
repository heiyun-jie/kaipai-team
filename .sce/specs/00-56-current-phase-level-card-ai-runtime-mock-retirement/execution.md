# 00-56 执行记录

## 1. 调查结论

- `src/api/level.ts` 当前仍保留 `useApiMock('level' | 'card' | 'ai')` 双轨分支
- `src/api/ai.ts` 当前仍保留 `useApiMock('ai')` 双轨分支
- `src/utils/personalization.ts` 当前仍保留 `useApiMock('card')` 下的本地拼装 fallback，会把 `scene-templates / card-config / fortune-report` 重新组装为个性化摘要
- `src/api/personalization.ts` 中的 `getPersonalizationSceneTemplates / getPersonalizationCardConfig / getPersonalizationFortuneReport` 只服务于这条 fallback
- `src/mock/service.ts`、`src/mock/database.ts` 中对应 `level / card / ai` mock 函数、helper 和数据在本轮退场后将失去全部运行时入口

## 2. 本轮落地

- 新增 `00-56` Spec，单独固化当前阶段 `level / card / ai` 运行时 mock 退场范围与边界
- `kaipai-frontend/src/api/level.ts` 已删除 `useApiMock('level' | 'card' | 'ai')` 分支，统一走真实 `/api/level/info`、`/api/card/*`、`/api/ai/quota`
- `kaipai-frontend/src/api/ai.ts` 已删除 `useApiMock('ai')` 分支，统一走真实 `/api/ai/*`
- `kaipai-frontend/src/utils/personalization.ts` 已删除本地拼装 fallback，`resolvePersonalizationProfile(...)` 当前统一只认 `/api/card/personalization`
- `kaipai-frontend/src/api/personalization.ts` 已删除只为 fallback 服务的三个 helper
- `kaipai-frontend/src/mock/service.ts` 已删除无运行时入口的 `level / card / ai` mock 函数与私有 helper
- `kaipai-frontend/src/mock/database.ts` 已删除已无引用的 `sceneTemplates / actorCardConfigs / aiQuota / aiDraft / aiHistory` mock 数据与类型
- `kaipai-frontend/src/utils/runtime.ts` 已删除 `level / card / ai` capability
- 已同步回填 `00-28/tasks.md`、`phase-01-roadmap.md`、`membership-status.md`、`ai-resume-status.md`、`overall-architecture-assessment.md`

## 3. 验证

- 已执行 `kaipai-frontend npm run type-check`，通过
- 已全文回扫前端源码，确认以下内容无剩余运行时引用：
  - `useApiMock('level' | 'card' | 'ai')`
  - `getLevelInfoMock / getSceneTemplatesMock / getActorCardConfigMock / saveActorCardConfigMock`
  - `getAiQuotaMock / consumeAiPolishQuotaMock / polishAiResumeMock / getAiResumeHistoryMock / rollbackAiResumeHistoryMock`
  - `getPersonalizationSceneTemplates / getPersonalizationCardConfig / getPersonalizationFortuneReport`
  - `mockSceneTemplates / mockActorCardConfigs / mockAiQuotas / mockAiResumeDrafts / mockAiResumeHistories`

## 4. Spec 回填

- 已完成 `.sce/specs/README.md` 增量登记
- 已完成 `.sce/specs/spec-code-mapping.md` 映射登记
- 已完成 `00-28` 路线图、任务与状态文档回填
