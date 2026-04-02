# AI 简历润色闭环状态回填

## 1. 归属切片

- `../slices/ai-resume-polish-capability-slice.md`
- `../execution/ai-resume/README.md`

## 2. 当前判定

- 回填日期：`2026-04-02`
- 当前判定：`局部完成（前后端最小闭环已打通）`
- 一句话结论：当前仓内已经具备“编辑页发起 AI 简历润色 -> 返回 patch 草稿 -> 本地应用 -> 保存档案 -> 写入历史 -> 历史回滚 -> 名片页回流刷新”的最小代码级闭环，且 `kaipai-frontend` 与 `kaipai-admin` `npm run type-check`、`kaipaile-server` `mvn -q -DskipTests compile` 已于 `2026-04-02` 通过；后台治理页、治理动作审计、角色页授权矩阵 / 建议授权包，以及失败样本筛选 / 处置时间线也已落位，但 AI 生成仍是规则适配器，目标环境角色绑定与真机联调仍未补齐，暂不能判定为完整生产闭环。

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
- 后台已可对失败样本执行“人工复核 / 建议重试”两类最小治理动作，并记录处理状态、备注、处理人和处理时间
- AI 治理页已直接复用操作日志接口展示最近治理动作，可回看 `ai_resume_review / ai_resume_suggest_retry` 的处理人、时间和上下文，不必再跳操作日志页手动筛选
- `GET /admin/system/roles/ai-governance-matrix` 已补齐角色授权矩阵接口；角色管理页可直接盘点哪些角色已补齐 AI 新权限、哪些角色仍依赖旧日志 fallback
- 角色管理页已补 AI 治理建议授权包，能直接套用“AI 治理只读 / AI 治理处置”两类最小角色矩阵，不必再手工检索权限码
- `GET /admin/ai/resume/failures` 与 `/sensitive-hits` 已支持按用户、处理状态、失败类型、关键词、请求 ID 查询；失败样本页也已可回看每次人工复核 / 建议重试的备注时间线
- 当前仍缺目标环境角色绑定回填和更细的人工处置状态流转，现阶段属于“可回看 + 可做最小处置”的第一版治理，不具备完整治理闭环

### 3.4 联调现状

- 当前代码层已具备最小联调路径：`actor-card -> edit?aiResume=1 -> /api/ai/polish-resume -> 本地 apply -> PUT /api/actor/profile(aiResumeApplyMeta) -> /api/ai/resume-polish/history -> rollback -> actor-card onShow refresh`
- 当前已确认的验证证据仍以本地编译/类型检查为主，尚未形成真机或远端环境的三端联调记录

## 4. 联调结论

- 当前是否具备三端联调条件：`前后端与后台最小联调路径已具备，后台治理与角色授权建议也已落位，但目标环境验证仍未完成`
- 已确认走通的链路：代码级 `编辑页 AI patch -> 本地应用 -> 保存档案 -> 历史回滚` 闭环，以及 `actor-card -> edit` 的入口回流
- 已新增的后台治理能力：`overview -> histories -> detail -> failures(filter) -> sensitive-hits(filter) -> review / suggest-retry -> handling timeline -> governance audit` 可回看 quota 消耗、最近历史、patch / snapshot 详情、失败样本、敏感命中、治理动作，并做最小人工处置
- 当前不能宣告完整闭环的原因：新旧权限仍处于兼容过渡、目标环境角色绑定尚未回填、治理动作仍缺更多处置状态流转、AI 生成仍为规则适配器、尚无真机/远端联调记录

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已完成 AI 简历切片和执行卡 |
| 数据模型、接口、状态流转清楚 | 已满足 | `draftId -> actor/profile save(aiResumeApplyMeta) -> history/rollback` 最小状态流已按冻结契约落成代码 |
| 后台治理入口可操作 | 部分满足 | 后台已新增最小 AI 治理页，可查看概览、历史、详情、失败样本和敏感命中，并支持人工复核 / 建议重试；但仍缺更细治理动作与真环境验证 |
| 小程序或前台用户侧落点可验证 | 已满足 | 编辑页、名片页入口、历史与回滚 UI 均已存在，且本地类型校验通过 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 登录态、实名认证、配额、历史回滚、失败样本、敏感命中、独立 AI 权限、角色页授权矩阵 / 建议授权包、失败样本筛选、处置时间线、最小人工处理动作和治理动作审计视图已接入，但目标环境角色绑定与真环境验证仍缺 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已建立 AI 简历状态基线 |

## 6. 当前阻塞项

- 后台已补独立页面/动作权限、角色页授权矩阵 / 建议授权包与最小人工处理动作，但新旧权限仍处于兼容过渡，目标环境角色绑定还未完成一次真实回填
- 失败样本当前已支持筛选与备注时间线，但仍只支持“人工复核 / 建议重试”两类最小动作，尚未形成更细的处置状态流转
- 服务端当前是规则适配器，不是外部 LLM；若后续要提升文案质量，还需要补模型接入、超时治理和审计策略
- 当前还缺真机或远端环境联调记录，不能只凭本地编译通过就视为交付完成

## 6.1 已知风险

- `POST /api/ai/polish-resume` 当前为了兼容旧调用仍保留“空请求体只消费 quota”的双响应形态，而冻结契约主口径已经转为 patch-only；后续需要决定是彻底拆旧兼容，还是在契约中单列 legacy 分支
- `work_experience:{experienceKey}:description` 当前只稳支持已持久化的服务端经历 `id`；未保存的新经历不会进入 `editableFields`
- `profileVersion` 已进入前后端 DTO，但当前实现仍以透传为主，尚未真正生效为 stale patch 强校验
- AI 草稿/历史依赖 Redis，档案保存与历史状态写入不是同一物理存储事务，当前只具备最小一致性约束

## 7. 下一轮最小动作

1. 在目标环境按“AI 治理只读 / AI 治理处置”完成一次真实角色绑定与登录验证，再决定何时下线 `operation-logs` 兼容兜底
2. 在真机或目标环境补一轮“编辑页 -> 保存 -> 历史 -> 回滚 -> 名片页 / 详情页刷新”的联调回填
3. 评估是否把规则适配器升级为真实 LLM 接入，并同步补超时、审计与回补策略
4. 视运营诉求决定是否补“忽略 / 升级 / 关闭”等更细治理处置状态流转

## 8. 回填记录

### 2026-04-01

- 当前判定：`局部完成（演示态）`
- 备注：明确把现有名片页 AI 能力降格为演示态记录，避免后续把 mock 润色误当成 AI 简历闭环

### 2026-04-02

- 当前判定：`局部完成（前后端最小闭环已打通）`
- 备注：`kaipaile-server` 已补齐 `/ai/quota`、`/ai/polish-resume`、`/ai/resume-polish/history`、`rollback` 最小接口与服务链路，并在本机 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过；项目 `pom.xml` 的 `java.version` 仍是 `17`。`kaipai-frontend` 已在 `edit.vue` 接通 AI 面板、patch 应用、保存/回滚语义，并再次执行 `npm run type-check` 通过
- 追加备注：已补 `05-04-ai-resume-polish/contract.md`，明确 `draftId -> actor/profile save -> history/rollback` 契约，冻结可写字段白名单、数值错误码和稳定 `fieldKey` 口径
- 追加备注：`kaipai-frontend` 已补 `src/api/ai.ts`、`src/types/ai.ts`，`kaipaile-server` 已补 AI 简历 DTO 骨架和 `ActorProfileSaveDTO.aiResumeApplyMeta` 预留位，为下一轮 controller / service / edit.vue 接线做准备
- 追加备注：`src/pages/actor-profile/ai-resume.ts` 已沉淀 AI 上下文与字段 helper；`src/pkg-card/actor-card/index.vue` 已把旧名片页 AI 演示收口为“跳编辑页使用 AI”，并在返回时刷新本人档案
- 追加备注：`kaipai-admin` 已补 `src/views/system/AiResumeGovernanceView.vue` 与 `/admin/ai/resume/*` 最小治理入口，可查看 quota 概览、历史列表、详情、失败样本和敏感命中；当前已补独立页面/动作权限，并可执行人工复核与建议重试
- 追加备注：`kaipai-admin` 已在 AI 治理页复用操作日志接口展示最近治理动作，可直接回看 `review / suggest-retry` 的责任人与上下文
- 追加备注：`kaipaile-server` 已补 `/admin/system/roles/ai-governance-matrix`；`kaipai-admin/src/views/system/RolesView.vue` 已补 AI 授权矩阵与建议授权包；`execution/ai-resume/role-authorization-closure.md` 已明确角色矩阵、环境收口步骤与 fallback 下线条件
- 追加备注：`kaipaile-server` 已补失败样本查询条件与备注时间线；`kaipai-admin/src/views/system/AiResumeGovernanceView.vue` 已支持按条件筛选失败样本 / 敏感命中，并直接回看每次人工处置记录
- 追加备注：`kaipai-frontend` 已补 `src/mock/service.ts`、`src/mock/database.ts` 下的 AI mock adapter，`useApiMock('ai')` 已可本地验证 patch/history/rollback
- 追加备注：当前仍缺目标环境角色绑定回填、更细治理处置流转和真机联调记录，因此本轮只可认定为“最小代码级闭环 + 第一版治理入口”，不能认定为完整生产闭环
