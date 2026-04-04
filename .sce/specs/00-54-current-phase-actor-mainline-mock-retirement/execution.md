# 00-54 执行记录

## 1. 调查结论

- `src/api/actor.ts` 当前仍保留 `useApiMock('actor')` 双轨分支
- 后端 `/actor/search`、`/actor/{userId}`、`/actor/profile/mine`、`PUT /actor/profile` 已存在
- 演员首页主入口已切到 `searchActors -> actor-profile/detail`
- `src/mock/service.ts` 中 actor API mock 函数当前只有 `src/api/actor.ts` 在使用
- `mockActors` 仍被 invite / AI / fortune 等其他 mock 演示域引用，因此本轮不能整包删除

## 2. 本轮落地

- 新增 `00-54` Spec，单独固化当前阶段演员主线前端 mock 退场范围与边界
- `kaipai-frontend/src/api/actor.ts` 已删除 `useApiMock('actor')` 分支，`getMyActorProfile / updateActorProfile / searchActors / getActorDetail` 统一走真实 `/api/actor*`
- `kaipai-frontend/src/mock/service.ts` 已删除无运行时入口的 actor API mock 函数
- `kaipai-frontend/src/utils/runtime.ts` 已删除 `actor` capability
- 已同步回填 `00-28/tasks.md`、`phase-01-roadmap.md`、`recruit-role-apply-status.md`、`overall-architecture-assessment.md`

## 3. 验证

- 已执行 `kaipai-frontend npm run type-check`，通过
- 已全文回扫前端源码，确认以下内容无剩余运行时引用：
  - `useApiMock('actor')`
  - `getActorProfileMock / updateActorProfileMock / searchActorsMock / getActorDetailMock`

## 4. Spec 回填

- 已完成 `.sce/specs/README.md` 增量登记
- 已完成 `.sce/specs/spec-code-mapping.md` 映射登记
- 已完成 `00-28` 路线图、任务与状态文档回填
