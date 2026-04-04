# 00-56 当前阶段等级 / 名片 / AI 运行时 Mock 退场（Current Phase Level Card AI Runtime Mock Retirement）

> 状态：已完成 | 优先级：P1 | 依赖：00-28 architecture-driven-delivery-governance，00-49 membership-preview-overlay-fact-source-boundary，00-50 ai-resume-governance-collaboration-upgrade，00-55 current-phase-invite-verify-fortune-mock-retirement
> 记录目的：把当前阶段已稳定接通的 `level / card / ai` 前端运行时双轨彻底退场，并删除 `src/utils/personalization.ts` 中残留的本地拼装 fallback，避免会员主线与 AI 主线继续保留隐藏的第二事实源。

## 1. 背景

`00-53`、`00-54`、`00-55` 已经分批把 recruit、actor、invite / verify / fortune 的前端 mock 双轨退场，但当前前端仍残留三块运行时双轨：

- `src/api/level.ts`
- `src/api/ai.ts`
- `src/utils/personalization.ts` 中的 `useApiMock('card')` 本地拼装 fallback

这会继续带来三个问题：

- membership 主线看起来已经消费 `/api/card/personalization`，但运行时代码仍允许回退到 `scene-templates + card-config + fortune-report` 的本地拼装事实源
- AI 简历主线看起来已经走真实 `/api/ai/*`，但源码仍保留 `useApiMock('ai')` 双轨
- `src/utils/runtime.ts` 仍通过 `level / card / ai` capability 暗示这些当前阶段主能力支持 mock 兜底

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-56` Spec，固化当前阶段 `level / card / ai` 运行时 mock 退场边界
- 移除 `src/api/level.ts`、`src/api/ai.ts` 中的 `useApiMock(...)` 分支
- 移除 `src/utils/personalization.ts` 中基于 `useApiMock('card')` 的本地拼装 fallback
- 清理 `src/api/personalization.ts` 中只为 fallback 服务的辅助函数
- 清理 `src/mock/service.ts`、`src/mock/database.ts` 中已无入口的 `level / card / ai` mock 函数、helper 和数据
- 清理 `src/utils/runtime.ts` 中已无使用方的 `level / card / ai` capability
- 回填 `00-28` 路线图、任务、状态文档、Spec 索引与映射

### 2.2 本轮不处理

- 删除 `auth` mock 主链
- 删除 `upload` mock 主链
- 把 preview overlay 升级为后端事实源
- 重做 AI 治理协同、通知回执、自动催办或真实 LLM 接入
- 处理微信能力、正式短信能力或上传能力的后续治理

## 3. 需求

### 3.1 当前阶段真实接口口径

- **R1** 当前阶段 `level` API 不得继续保留 `useApiMock('level' | 'card' | 'ai')` 双轨分支，必须统一调用：
  - `GET /api/level/info`
  - `GET /api/card/scene-templates`
  - `GET /api/card/config`
  - `POST /api/card/config`
  - `GET /api/ai/quota`
- **R2** 当前阶段 `ai` API 不得继续保留 `useApiMock('ai')` 双轨分支，必须统一调用：
  - `GET /api/ai/quota`
  - `POST /api/ai/polish-resume`
  - `GET /api/ai/resume-polish/history`
  - `POST /api/ai/resume-polish/history/{historyId}/rollback`
- **R3** 当前阶段个性化主链不得继续在 `src/utils/personalization.ts` 中本地拼装 `templates / card-config / fortune-report` 作为主事实源，必须统一以 `GET /api/card/personalization` 为基线。
- **R4** 当前阶段若这些接口、鉴权或环境有问题，页面必须直接暴露真实错误，不得再由前端 `level / card / ai` 局部 mock 或本地拼装掩盖。

### 3.2 Mock 退场边界

- **R5** `src/api/personalization.ts` 中只为本地 fallback 服务的以下 helper 必须删除：
  - `getPersonalizationSceneTemplates`
  - `getPersonalizationCardConfig`
  - `getPersonalizationFortuneReport`
- **R6** `src/mock/service.ts` 中以下已无运行时入口的函数 / helper 必须删除：
  - `getLevelInfoMock`
  - `getSceneTemplatesMock`
  - `getActorCardConfigMock`
  - `saveActorCardConfigMock`
  - `getAiQuotaMock`
  - `consumeAiPolishQuotaMock`
  - `polishAiResumeMock`
  - `getAiResumeHistoryMock`
  - `rollbackAiResumeHistoryMock`
  - 以及只服务于上述函数的私有 helper
- **R7** `src/mock/database.ts` 中以下数据或类型若失去全部运行时引用，必须同步删除：
  - `mockSceneTemplates`
  - `mockActorCardConfigs`
  - `mockAiQuotas`
  - `mockAiResumeDrafts`
  - `mockAiResumeHistories`
  - `MockAiResumeDraftRecord`
  - `MockAiResumeHistoryRecord`
- **R8** `src/utils/runtime.ts` 中已无使用方的 `level / card / ai` capability 必须同步删除，避免继续暗示当前阶段主能力支持 mock 兜底。

### 3.3 治理回填

- **R9** 必须通过独立 Spec 固化这次 `level / card / ai` 运行时 mock 退场，不得只改代码。
- **R10** 必须同步回填 `00-28`，让后续读文档的人能直接看到：membership 与 AI 当前阶段主链已不再保留前端 `level / card / ai` 双轨或 personalization 本地拼装 fallback。

## 4. 验收标准

- [x] 已新增独立 `00-56` Spec 并登记索引与映射
- [x] `src/api/level.ts`、`src/api/ai.ts` 已不再保留 `useApiMock(...)` 分支
- [x] `src/utils/personalization.ts` 已删除本地拼装 fallback，统一只认 `/api/card/personalization`
- [x] `src/api/personalization.ts` 已删除只为 fallback 服务的 helper
- [x] `src/mock/service.ts`、`src/mock/database.ts` 已删除无入口 `level / card / ai` mock 数据与 helper
- [x] `src/utils/runtime.ts` 已删除无使用方的 `level / card / ai` capability
- [x] `kaipai-frontend npm run type-check` 通过
- [x] `00-28` 状态页和总体评估已明确回填“level / card / ai 前端 mock 已退场”
