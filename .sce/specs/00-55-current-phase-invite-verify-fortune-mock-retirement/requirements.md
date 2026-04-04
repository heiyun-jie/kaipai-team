# 00-55 当前阶段邀请 / 实名 / 命理前端 Mock 退场（Current Phase Invite Verify Fortune Mock Retirement）

> 状态：已完成 | 优先级：P1 | 依赖：00-28 architecture-driven-delivery-governance，00-52 current-phase-invite-record-page-boundary-alignment，00-49 membership-preview-overlay-fact-source-boundary
> 记录目的：把 `invite / verify / fortune` 三条当前阶段已稳定接通的辅助能力，从前端 `useApiMock(...)` 双轨推进到只认真实接口，避免当前阶段继续把邀请记录、实名认证和命理报告保留为局部 mock 兜底。

## 1. 背景

当前 `00-28` 已经明确：

- invite 当前阶段以“登录承接邀请码 + 邀请记录页 + 资格链闭环”为主验收面
- verify 当前阶段已闭环完成
- membership 已把 `/fortune/*` 与 `/level / card / personalization` 并入真实样本

但前端以下 API 仍保留双轨 mock：

- `src/api/invite.ts`
- `src/api/verify.ts`
- `src/api/fortune.ts`

如果继续保留，会导致：

- 已闭环或已稳定的当前阶段能力仍停留在前端假事实源
- 当前环境问题可能继续被局部 mock 掩盖
- `src/utils/runtime.ts` 的 capability 表继续暗示这些链路支持 mock 兜底

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-55` Spec，固化 invite / verify / fortune 前端 mock 退场边界
- 移除 `src/api/invite.ts`、`src/api/verify.ts`、`src/api/fortune.ts` 中的 `useApiMock(...)` 分支
- 清理 `src/mock/service.ts` 中对应 API mock 函数
- 清理 `src/mock/database.ts` 中已无引用的 verify / fortune mock 数据
- 清理 `src/utils/runtime.ts` 中已无使用方的 `invite / verify / fortune` capability
- 回填 `00-28` 状态文档、路线图 / 任务和总体评估
- 更新 Spec 索引与映射

### 2.2 本轮不处理

- 删除 auth mock 主链
- 删除 level / card / ai 相关 mock 分支
- 删除 invite / verify / fortune 历史样本、历史文档或未来批次入口
- 处理 `wxacode`、preview overlay 或真实 LLM 接入

## 3. 需求

### 3.1 当前阶段真实接口口径

- **R1** 当前阶段 invite API 不得继续保留 `useApiMock('invite')` 双轨分支，必须统一调用：
  - `GET /api/invite/code`
  - `GET /api/invite/stats`
  - `GET /api/invite/records`
- **R2** 当前阶段 verify API 不得继续保留 `useApiMock('verify')` 双轨分支，必须统一调用：
  - `GET /api/verify/status`
  - `POST /api/verify/submit`
- **R3** 当前阶段 fortune API 不得继续保留 `useApiMock('fortune')` 双轨分支，必须统一调用：
  - `GET /api/fortune/report`
  - `POST /api/fortune/apply-lucky-color`
- **R4** 当前阶段若这些接口、鉴权或环境有问题，页面必须直接暴露真实错误，不得再由前端局部 mock 掩盖。

### 3.2 Mock 退场边界

- **R5** `src/mock/service.ts` 中以下无入口函数必须删除：
  - `getInviteStatsMock`
  - `getInviteInfoMock`
  - `getInviteRecordsMock`
  - `getVerifyStatusMock`
  - `submitVerifyMock`
  - `getFortuneReportMock`
  - `applyLuckyColorMock`
- **R6** 如果 `src/mock/database.ts` 中 `mockIdentityVerifications / mockFortuneReports` 已无任何运行时引用，必须同步删除。
- **R7** invite 相关基础数据如 `mockInviteCodes / mockReferralRecords` 若仍被 auth mock 注册流程使用，可继续保留，不在本轮误删。
- **R8** `src/utils/runtime.ts` 中已无使用方的 `invite / verify / fortune` capability 必须同步删除。

### 3.3 治理回填

- **R9** 必须通过独立 Spec 固化这次 invite / verify / fortune mock 退场，不得只改代码。
- **R10** 必须同步回填 `00-28`，让后续读文档的人能直接看到：这三条当前阶段能力已不再保留前端 mock 双轨。

## 4. 验收标准

- [x] 已新增独立 `00-55` Spec 并登记索引与映射
- [x] `src/api/invite.ts`、`src/api/verify.ts`、`src/api/fortune.ts` 已不再保留 `useApiMock(...)` 分支
- [x] `src/mock/service.ts` 已删除对应无入口 mock 函数
- [x] `src/utils/runtime.ts` 已删除无使用方的 `invite / verify / fortune` capability
- [x] `src/mock/database.ts` 已删除已无引用的 verify / fortune mock 数据
- [x] `kaipai-frontend npm run type-check` 通过
- [x] `00-28` 状态页和总体评估已明确回填“invite / verify / fortune 前端 mock 已退场”
