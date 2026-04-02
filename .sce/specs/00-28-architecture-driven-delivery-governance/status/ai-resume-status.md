# AI 简历润色闭环状态回填

## 1. 归属切片

- `../slices/ai-resume-polish-capability-slice.md`
- `../execution/ai-resume/README.md`

## 2. 当前判定

- 回填日期：`2026-04-03`
- 当前判定：`局部完成（真实 actor/admin 样本与角色矩阵已收口）`
- 一句话结论：当前仓内已经具备“编辑页发起 AI 简历润色 -> 返回 patch 草稿 -> 本地应用 -> 保存档案 -> 写入历史 -> 历史回滚 -> 名片页回流刷新”的最小闭环，且 `2026-04-03` 已通过标准样本 `execution/ai-resume/run-ai-resume-validation.py` 与 `execution/ai-resume/run-ai-role-authorization-closure.py` 在真实环境跑通 actor `quota -> polish -> save -> history -> rollback`、admin `overview -> histories -> failures -> sensitive-hits -> review -> close -> operation-logs`，并把目标环境 `ADMIN` 角色从 `fallback_only` 推进到 `ai_ready`；当前主阻塞已不再是“AI 接口仍停在 mock”或“角色尚未绑定”，而是“真机页面级证据缺失、更完整治理协同仍未补齐，以及生成器仍是规则适配器而非真实 LLM”。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pages/actor-profile/edit.vue` 已补齐 AI 入口、抽屉面板、字段级 patch 预览、单字段/整轮应用、撤销本轮应用、历史列表和回滚动作
- `kaipai-frontend/src/pages/actor-profile/edit.vue` 已把 AI 草稿与真实保存拆开：预览名片仍走既有 `PUT /api/actor/profile` 预保存，但不会上传 `aiResumeApplyMeta`；真正保存档案时才会上送 `aiResumeApplyMeta`
- `kaipai-frontend/src/pages/actor-profile/ai-resume.ts` 已沉淀 AI 上下文组装、稳定 `fieldKey` 解析与表单字段写回 helper，避免 `edit.vue` 再各自推导一套字段定位规则
- `kaipai-frontend/src/pkg-card/actor-card/index.vue` 已把旧“名片页本地 AI 文案切换”收口为跳转编辑页 AI 面板，且在返回后刷新本人档案，避免名片页继续展示旧简介/旧经历
- `kaipai-frontend/src/api/ai.ts`、`src/types/ai.ts` 已按 `patch / history / rollback` 协议接通真实 AI 接口，并补齐 `useApiMock('ai')` 下的 patch / history / rollback mock adapter；本地 mock 环境已不再直接断链

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/ai/AiController.java` 已补齐 `/ai/quota`、`/ai/polish-resume`、`/ai/resume-polish/history`、`/ai/resume-polish/history/{historyId}/rollback`，并保留空请求体场景下的旧 quota-consume 兼容分支
- `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/impl/AiResumeServiceImpl.java`、`AiResumeApplyRecorderImpl.java`、`RuleBasedResumePatchAdapter.java`、`AiResumeRedisKeys.java` 已形成最小权威链路：生成 patch 草稿、写 Redis 草稿、保存后沉淀历史、按历史快照回滚
- `kaipaile-server/src/main/java/com/kaipai/module/server/actor/service/impl/ActorProfileServiceImpl.java` 已在保存档案后记录 AI 应用历史，并在经历同步后回写稳定 `experienceId`，保证 `fieldKey -> experienceId` 映射不漂移
- `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/impl/AiQuotaServiceImpl.java` 已切到冻结错误码；`AiResumeServiceImpl` 已改为显式 `@Lazy` 构造注入，避免 `ActorProfileService -> recorder -> aiResumeService -> ActorProfileService` 的循环依赖只停留在“表面代码可编译”
- 当前 AI 生成仍是规则适配器，不是外部 LLM；历史与草稿依赖 Redis，尚未落库到专用数据表

### 3.3 后台治理

- `kaipai-admin/src/views/system/AiResumeGovernanceView.vue` 已新增最小真实治理页，并挂到 `/system/ai-resume-governance`
- 后台已可查看概览卡、本月 quota top users、历史筛选列表和 history 详情抽屉；数据来自 `GET /admin/ai/resume/overview`、`/histories`、`/histories/{historyId}`
- `kaipaile-server` 已把 AI 失败样本写入 Redis，并补齐 `GET /admin/ai/resume/failures` 与 `/admin/ai/resume/sensitive-hits`；后台已可回看最近失败样本和敏感命中样本
- AI 治理页已新增独立页面权限 `page.system.ai-resume-governance` 与动作权限 `action.system.ai-resume.review`、`action.system.ai-resume.resolve`，前后端同时保留 `page.system.operation-logs` 兼容兜底，避免旧角色立刻失去入口
- 后台已可对失败样本执行“分派处理人 / 确认接手 / 人工催办 / 人工复核 / 建议重试 / 升级处理 / 忽略 / 关闭归档”八类治理动作，并记录处理状态、备注、处理人和处理时间
- 后台已补 `GET /admin/ai/resume/collaboration-catalog`，治理页可直接拉取 AI 治理责任人候选与升级目标角色目录，不再借 `admin-users / roles` 页面权限临时兜底
- 失败样本页已支持按责任人 / 升级目标 / 协同状态筛选，并直接显示签收 SLA，可执行“分派处理人 / 确认接手”动作；处置时间线也会回看每次分派 / 签收 / 升级时的责任协同元数据
- AI 治理页已补协同状态 tag、签收 SLA 截止时间回看与协同状态筛选，可直接定位待签收 / 签收超时 / 已完成样本
- AI 治理页已补人工催办动作，可在“已分派但未签收”的失败样本上执行 `remind`，并回看最近催办时间 / 次数、催办人以及时间线 / 审计日志中的催办上下文
- AI 治理页已直接复用操作日志接口展示最近治理动作，可回看 `ai_resume_assign / ai_resume_acknowledge / ai_resume_remind / ai_resume_review / ai_resume_suggest_retry` 的处理人、时间和上下文，不必再跳操作日志页手动筛选
- `GET /admin/system/roles/ai-governance-matrix` 已补齐角色授权矩阵接口；角色管理页可直接盘点哪些角色已补齐 AI 新权限、哪些角色仍依赖旧日志 fallback
- 角色管理页已补 AI 治理建议授权包，能直接套用“AI 治理只读 / AI 治理处置”两类最小角色矩阵，不必再手工检索权限码
- `GET /admin/ai/resume/failures` 与 `/sensitive-hits` 已支持按用户、处理状态、失败类型、关键词、请求 ID 查询；失败样本页也已可回看每次人工复核 / 建议重试的备注时间线
- AI 治理动作审计区已支持按操作人、动作、结果、请求 ID 与条数筛选，不再只能裸看最近 10 条日志
- 失败样本处置已补前后端状态迁移约束，避免终态样本继续被任意切换处置状态
- `2026-04-03 07:21` 已通过标准样本把目标环境 `ADMIN` 角色补齐为 `ai_ready`，并确认重新登录后的后台会话已拿到 `page.system.ai-resume-governance`、`action.system.ai-resume.review`、`action.system.ai-resume.resolve`
- 当前仍缺通知回执 / 自动催办 / 更细 SLA 规则等更完整的人工处置协同流转；现阶段属于“可回看 + 可做最小处置 + 最小责任协同”的第一版治理，不具备完整治理闭环

### 3.4 联调现状

- 当前代码层已具备最小联调路径：`actor-card -> edit?aiResume=1 -> /api/ai/polish-resume -> 本地 apply -> PUT /api/actor/profile(aiResumeApplyMeta) -> /api/ai/resume-polish/history -> rollback -> actor-card onShow refresh`
- `2026-04-03 07:12` 已新增并执行标准真实样本 `execution/ai-resume/run-ai-resume-validation.py continue-rerun`，样本目录为 `execution/ai-resume/samples/20260403-071241-continue-rerun/`
- 同一样本已固定 actor 真实链路：
  - `GET /api/ai/quota?type=resume_polish` -> `200`
  - `POST /api/ai/polish-resume` -> `200`，返回 `draftId=airp_draft_f7b1ae4f44b04625bc078cf886766301`
  - `PUT /api/actor/profile` 携带 `aiResumeApplyMeta` -> `200`
  - `GET /api/ai/resume-polish/history` -> `200`
  - `POST /api/ai/resume-polish/history/{historyId}/rollback` -> `200`
- 同一样本也已固定 admin 真实治理链路：
  - `GET /api/admin/system/roles/ai-governance-matrix` -> `200`
  - `GET /api/admin/ai/resume/overview`、`/histories`、`/failures`、`/sensitive-hits` -> `200`
  - 对同一条敏感命中失败样本执行 `review`、`close` -> `200`
  - `GET /api/admin/system/operation-logs?operationCode=ai_resume_close&requestId=20260403-071241-continue-rerun-close` -> `200`
- `2026-04-03 07:21` 已新增并执行标准角色收口样本 `execution/ai-resume/run-ai-role-authorization-closure.py continue-ai-role-closure`，样本目录为 `execution/ai-resume/samples/20260403-072120-continue-ai-role-closure/`
- 同一样本已固定目标环境角色矩阵真实收口结果：
  - `matrix-before`: `ADMIN.rolloutStage='fallback_only'`，缺失 `page.system.ai-resume-governance`、`action.system.ai-resume.review`、`action.system.ai-resume.resolve`
  - `role-update`: `PUT /api/admin/system/roles/1` -> `200`
  - `matrix-after`: `aiReadyRoleCount=1`、`fallbackRoleCount=0`、`canRetireFallback=true`
  - `session-permissions-refreshed`: 重新登录后当前会话已拿到独立 AI 页面 / 动作权限
  - `role-update-operation-log-visible`: 可按显式 `X-Request-Id=20260403-072120-continue-ai-role-closure-update-role` 回看角色更新审计
- 当前最新真实样本已不再停留在“只有本地编译/类型检查”，但仍未补齐真机页面级证据与真实 LLM 样本

## 4. 联调结论

- 当前是否具备三端联调条件：`部分具备`
- 已确认走通的链路：真实环境 `quota -> polish -> actor/profile save(aiResumeApplyMeta) -> history -> rollback -> admin overview/histories/failures/sensitive-hits -> review -> close -> operation-logs`
- 已新增的后台治理能力：`overview -> histories -> detail -> collaboration-catalog -> failures(filter) -> sensitive-hits(filter) -> assign / acknowledge / remind / review / suggest-retry / escalate / ignore / close -> handling timeline -> governance audit(filter)` 可回看 quota 消耗、最近历史、patch / snapshot 详情、失败样本、敏感命中、责任人目录、升级目标目录、签收 SLA、催办次数 / 最近催办时间与治理动作，并做最小人工处置、责任分派、人工催办与责任人签收
- 当前不能宣告完整闭环的原因：治理动作仍缺通知回执 / 自动催办 / 更细 SLA 规则、仓内虽已移除 `page.system.operation-logs` 兼容兜底但目标环境尚未完成发布复验、AI 生成仍为规则适配器、且尚无真机页面级联调记录

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已完成 AI 简历切片和执行卡 |
| 数据模型、接口、状态流转清楚 | 已满足 | `draftId -> actor/profile save(aiResumeApplyMeta) -> history/rollback` 最小状态流已按冻结契约落成代码 |
| 后台治理入口可操作 | 部分满足 | 后台已新增最小 AI 治理页，可查看概览、历史、详情、失败样本和敏感命中，按责任人 / 升级目标 / 协同状态筛选，并支持分派处理人 / 确认接手 / 人工催办、人工复核 / 建议重试 / 升级处理 / 忽略 / 关闭归档；但仍缺更完整协同与真环境验证 |
| 小程序或前台用户侧落点可验证 | 已满足 | 编辑页、名片页入口、历史与回滚 UI 均已存在，且本地类型校验通过 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 登录态、实名认证、配额、历史回滚、失败样本、敏感命中、独立 AI 权限、角色页授权矩阵 / 建议授权包、失败样本筛选、责任人 / 升级目标目录、协同状态 / 签收 SLA / 人工催办回看、处置时间线、最小人工处理动作和治理动作审计视图已接入；但真机页面级验证、fallback 退场后的目标环境发布复验与更完整治理协同仍缺 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已建立 AI 简历状态基线 |

## 6. 当前阻塞项

- `2026-04-03 07:21` 最新角色收口样本已确认目标环境矩阵结果为：
  - `totalRoleCount=1`
  - `aiReadyRoleCount=1`
  - `fallbackRoleCount=0`
  - `canRetireFallback=true`
  - 唯一启用角色 `ADMIN.rolloutStage='ai_ready'`
- 仓内已移除 `page.system.operation-logs` 兼容兜底，但尚未完成“按 runbook 发布到目标环境后，再复验一轮治理入口 / 动作 / 审计”的真正退场验证
- 失败样本当前已支持筛选、备注时间线、责任人分派、责任人签收、人工催办、协同状态 / 签收 SLA / 催办次数与最近催办时间回看、升级目标角色与 `ignore / escalate / close` 状态迁移约束；但仍未形成通知回执、自动催办和更细 SLA 规则等更完整协同流转
- 服务端当前是规则适配器，不是外部 LLM；若后续要提升文案质量，还需要补模型接入、超时治理和审计策略
- 当前 actor/admin 真实接口样本虽已补齐，但仍缺真机页面级联调记录，不能只凭 API 样本就视为交付完成

## 6.1 已知风险

- `POST /api/ai/polish-resume` 当前为了兼容旧调用仍保留“空请求体只消费 quota”的双响应形态，而冻结契约主口径已经转为 patch-only；后续需要决定是彻底拆旧兼容，还是在契约中单列 legacy 分支
- `work_experience:{experienceKey}:description` 当前只稳支持已持久化的服务端经历 `id`；未保存的新经历不会进入 `editableFields`
- `profileVersion` 已进入前后端 DTO，但当前实现仍以透传为主，尚未真正生效为 stale patch 强校验
- AI 草稿/历史依赖 Redis，档案保存与历史状态写入不是同一物理存储事务，当前只具备最小一致性约束

## 7. 下一轮最小动作

1. 基于 `20260403-072120-continue-ai-role-closure` 样本结果，按 runbook 发布当前仓的 fallback 退场改动，再补一轮“移除 fallback 后”的真实治理页入口 / 动作 / 审计复验
2. 在真机或目标环境补一轮“编辑页 -> 保存 -> 历史 -> 回滚 -> 名片页 / 详情页刷新”的联调回填
3. 评估是否把规则适配器升级为真实 LLM 接入，并同步补超时、审计与回补策略
4. 视运营诉求决定是否补“通知回执 / SLA 自动催办 / 升级提醒”等更完整责任协同流转

## 8. 回填记录

### 2026-04-01

- 当前判定：`局部完成（演示态）`
- 备注：明确把现有名片页 AI 能力降格为演示态记录，避免后续把 mock 润色误当成 AI 简历闭环

### 2026-04-03

- 当前判定：`局部完成（真实 actor/admin 样本已补齐）`
- 备注：
  - 已新增标准真实样本脚本：`execution/ai-resume/run-ai-resume-validation.py`
  - 最新样本目录：`execution/ai-resume/samples/20260403-071241-continue-rerun/summary.md`
  - 同一样本已真实跑通：
    - actor `quota -> polish-resume -> actor/profile(aiResumeApplyMeta) -> history -> rollback`
    - admin `ai-governance-matrix -> overview -> histories -> failures -> sensitive-hits -> review -> close -> operation-logs`
  - 同一样本也已固定一条敏感命中失败样本：`failureId=airp_fail_e65454af8350411b93bad6ef82abaca0`，并确认 `review`、`close` 后能在操作日志中按显式 `X-Request-Id` 回看 `ai_resume_close`
  - 随后 `07:21` 又已通过标准角色收口样本 `execution/ai-resume/samples/20260403-072120-continue-ai-role-closure/summary.md` 把 `ADMIN` 从 `fallback_only` 推进到 `ai_ready`，并确认重新登录后的后台会话已拿到独立 AI 页面 / 动作权限
  - 因此 AI 当前主阻塞已从“缺真实环境样本 / 角色尚未绑定”收口为：
    - 真机页面级证据未补齐
    - fallback 已在仓内退场，但目标环境仍待按样本发布复验
    - 生成器仍是规则适配器，尚未接入真实 LLM

### 2026-04-02

- 当前判定：`局部完成（前后端最小闭环已打通）`
- 备注：`kaipaile-server` 已补齐 `/ai/quota`、`/ai/polish-resume`、`/ai/resume-polish/history`、`rollback` 最小接口与服务链路，并在本机 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过；项目 `pom.xml` 的 `java.version` 仍是 `17`。`kaipai-frontend` 已在 `edit.vue` 接通 AI 面板、patch 应用、保存/回滚语义，并再次执行 `npm run type-check` 通过
- 追加备注：已补 `05-04-ai-resume-polish/contract.md`，明确 `draftId -> actor/profile save -> history/rollback` 契约，冻结可写字段白名单、数值错误码和稳定 `fieldKey` 口径
- 追加备注：`kaipai-frontend` 已补 `src/api/ai.ts`、`src/types/ai.ts`，`kaipaile-server` 已补 AI 简历 DTO 骨架和 `ActorProfileSaveDTO.aiResumeApplyMeta` 预留位，为下一轮 controller / service / edit.vue 接线做准备
- 追加备注：`src/pages/actor-profile/ai-resume.ts` 已沉淀 AI 上下文与字段 helper；`src/pkg-card/actor-card/index.vue` 已把旧名片页 AI 演示收口为“跳编辑页使用 AI”，并在返回时刷新本人档案
- 追加备注：`kaipai-admin` 已补 `src/views/system/AiResumeGovernanceView.vue` 与 `/admin/ai/resume/*` 最小治理入口，可查看 quota 概览、历史列表、详情、失败样本和敏感命中；当前已补独立页面/动作权限，并可执行人工复核与建议重试
- 追加备注：`kaipai-admin` 已在 AI 治理页复用操作日志接口展示最近治理动作，可直接回看 `review / suggest-retry / remind` 的责任人与上下文
- 追加备注：`kaipaile-server` 已补 `/admin/system/roles/ai-governance-matrix`；`kaipai-admin/src/views/system/RolesView.vue` 已补 AI 授权矩阵与建议授权包；`execution/ai-resume/role-authorization-closure.md` 已明确角色矩阵、环境收口步骤与 fallback 下线条件
- 追加备注：`kaipaile-server` 已补失败样本查询条件、备注时间线、`ignore / escalate / close` 处置状态与迁移约束；`kaipai-admin/src/views/system/AiResumeGovernanceView.vue` 已支持按条件筛选失败样本 / 敏感命中、执行升级处理 / 忽略 / 关闭归档，并直接回看每次人工处置记录
- 追加备注：`kaipaile-server` 已补 `/admin/ai/resume/collaboration-catalog`、失败样本责任人分派、责任人签收与升级目标角色目录；`kaipai-admin/src/views/system/AiResumeGovernanceView.vue` 已支持按责任人 / 升级目标筛选失败样本、执行分派处理人 / 确认接手，并在时间线中回看每次责任协同元数据
- 追加备注：`kaipai-admin/src/views/system/AiResumeGovernanceView.vue` 已补协同状态 tag、签收 SLA 截止时间回看和协同状态筛选，当前可直接定位待签收 / 签收超时样本；当前剩余协同缺口为通知回执、自动催办与更细 SLA 规则
- 追加备注：`kaipaile-server` 已补 `/admin/ai/resume/failures/{failureId}/remind`，`kaipai-admin/src/views/system/AiResumeGovernanceView.vue` 已支持“人工催办”动作、最近催办时间 / 次数展示与 `ai_resume_remind` 审计回看；当前剩余协同缺口已收敛为通知回执、自动催办与更细 SLA 规则
- 追加备注：`kaipai-frontend` 已补 `src/mock/service.ts`、`src/mock/database.ts` 下的 AI mock adapter，`useApiMock('ai')` 已可本地验证 patch/history/rollback
- 追加备注：当前角色矩阵已完成真实回填，仓内也已移除 fallback 代码，但仍缺更完整责任协同流转、目标环境发布复验和真机联调记录，因此本轮只可认定为“最小代码级闭环 + 第一版治理入口”，不能认定为完整生产闭环
