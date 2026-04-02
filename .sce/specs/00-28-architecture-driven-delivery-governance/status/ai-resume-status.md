# AI 简历润色闭环状态回填

## 1. 归属切片

- `../slices/ai-resume-polish-capability-slice.md`
- `../execution/ai-resume/README.md`

## 2. 当前判定

- 回填日期：`2026-04-02`
- 当前判定：`局部完成（前后端最小闭环已打通）`
- 一句话结论：当前仓内已经具备“编辑页发起 AI 简历润色 -> 返回 patch 草稿 -> 本地应用 -> 保存档案 -> 写入历史 -> 历史回滚 -> 名片页回流刷新”的最小代码级闭环，且 `kaipai-frontend` `npm run type-check` 与 `kaipaile-server` `mvn -q -DskipTests compile` 已于 `2026-04-02` 通过；但 AI 生成仍是规则适配器，后台专用治理入口和 mock adapter 仍未补齐，暂不能判定为完整生产闭环。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pages/actor-profile/edit.vue` 已补齐 AI 入口、抽屉面板、字段级 patch 预览、单字段/整轮应用、撤销本轮应用、历史列表和回滚动作
- `kaipai-frontend/src/pages/actor-profile/edit.vue` 已把 AI 草稿与真实保存拆开：预览名片仍走既有 `PUT /api/actor/profile` 预保存，但不会上传 `aiResumeApplyMeta`；真正保存档案时才会上送 `aiResumeApplyMeta`
- `kaipai-frontend/src/pages/actor-profile/ai-resume.ts` 已沉淀 AI 上下文组装、稳定 `fieldKey` 解析与表单字段写回 helper，避免 `edit.vue` 再各自推导一套字段定位规则
- `kaipai-frontend/src/pkg-card/actor-card/index.vue` 已把旧“名片页本地 AI 文案切换”收口为跳转编辑页 AI 面板，且在返回后刷新本人档案，避免名片页继续展示旧简介/旧经历
- `kaipai-frontend/src/api/ai.ts`、`src/types/ai.ts` 已按 `patch / history / rollback` 协议接通真实 AI 接口；当前 mock 仍未补齐，若运行环境启用 `useApiMock('ai')`，AI 面板会直接失败

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/ai/AiController.java` 已补齐 `/ai/quota`、`/ai/polish-resume`、`/ai/resume-polish/history`、`/ai/resume-polish/history/{historyId}/rollback`，并保留空请求体场景下的旧 quota-consume 兼容分支
- `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/impl/AiResumeServiceImpl.java`、`AiResumeApplyRecorderImpl.java`、`RuleBasedResumePatchAdapter.java`、`AiResumeRedisKeys.java` 已形成最小权威链路：生成 patch 草稿、写 Redis 草稿、保存后沉淀历史、按历史快照回滚
- `kaipaile-server/src/main/java/com/kaipai/module/server/actor/service/impl/ActorProfileServiceImpl.java` 已在保存档案后记录 AI 应用历史，并在经历同步后回写稳定 `experienceId`，保证 `fieldKey -> experienceId` 映射不漂移
- `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/impl/AiQuotaServiceImpl.java` 已切到冻结错误码；`AiResumeServiceImpl` 已改为显式 `@Lazy` 构造注入，避免 `ActorProfileService -> recorder -> aiResumeService -> ActorProfileService` 的循环依赖只停留在“表面代码可编译”
- 当前 AI 生成仍是规则适配器，不是外部 LLM；历史与草稿依赖 Redis，尚未落库到专用数据表

### 3.3 后台治理

- 当前后台没有 AI 简历专用治理页、样本回看页或异常处理页
- 现阶段只能借用通用操作日志和接口错误信息排障，尚未形成 AI 调用治理入口

### 3.4 联调现状

- 当前代码层已具备最小联调路径：`actor-card -> edit?aiResume=1 -> /api/ai/polish-resume -> 本地 apply -> PUT /api/actor/profile(aiResumeApplyMeta) -> /api/ai/resume-polish/history -> rollback -> actor-card onShow refresh`
- 当前已确认的验证证据仍以本地编译/类型检查为主，尚未形成真机或远端环境的三端联调记录

## 4. 联调结论

- 当前是否具备三端联调条件：`前后端已具备最小联调条件，后台治理仍不具备`
- 已确认走通的链路：代码级 `编辑页 AI patch -> 本地应用 -> 保存档案 -> 历史回滚` 闭环，以及 `actor-card -> edit` 的入口回流
- 当前不能宣告完整闭环的原因：后台无治理入口、mock adapter 缺失、AI 生成仍为规则适配器、尚无真机/远端联调记录

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已完成 AI 简历切片和执行卡 |
| 数据模型、接口、状态流转清楚 | 已满足 | `draftId -> actor/profile save(aiResumeApplyMeta) -> history/rollback` 最小状态流已按冻结契约落成代码 |
| 后台治理入口可操作 | 未满足 | 后台没有 AI 调用治理专属入口 |
| 小程序或前台用户侧落点可验证 | 已满足 | 编辑页、名片页入口、历史与回滚 UI 均已存在，且本地类型校验通过 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 登录态、实名认证、配额、历史回滚和错误码已接入，但后台日志/治理入口仍缺 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已建立 AI 简历状态基线 |

## 6. 当前阻塞项

- 后台没有 AI 简历专用治理页，当前无法做“按用户/请求/错误码”维度的运营与排障
- `kaipai-frontend/src/api/ai.ts` 的 mock 适配器仍未补齐；在 mock 环境下只能查 quota，不能验证 patch/history/rollback
- 服务端当前是规则适配器，不是外部 LLM；若后续要提升文案质量，还需要补模型接入、超时治理和审计策略
- 当前还缺真机或远端环境联调记录，不能只凭本地编译通过就视为交付完成

## 6.1 已知风险

- `POST /api/ai/polish-resume` 当前为了兼容旧调用仍保留“空请求体只消费 quota”的双响应形态，而冻结契约主口径已经转为 patch-only；后续需要决定是彻底拆旧兼容，还是在契约中单列 legacy 分支
- `work_experience:{experienceKey}:description` 当前只稳支持已持久化的服务端经历 `id`；未保存的新经历不会进入 `editableFields`
- `profileVersion` 已进入前后端 DTO，但当前实现仍以透传为主，尚未真正生效为 stale patch 强校验
- AI 草稿/历史依赖 Redis，档案保存与历史状态写入不是同一物理存储事务，当前只具备最小一致性约束

## 7. 下一轮最小动作

1. 为 `src/api/ai.ts` 补 mock adapter，或明确测试环境必须切真 `ai` 接口，避免前端联调直接被 mock reject 卡死
2. 补后台 AI 治理入口，至少能查看 requestId、用户、错误码、最近 patch / rollback 记录
3. 在真机或目标环境补一轮“编辑页 -> 保存 -> 历史 -> 回滚 -> 名片页 / 详情页刷新”的联调回填
4. 评估是否把规则适配器升级为真实 LLM 接入，并同步补超时、审计与回补策略

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
- 追加备注：当前仍未补后台治理入口、mock adapter 和真机联调记录，因此本轮只可认定为“最小代码级闭环”，不能认定为完整生产闭环
