# AI 简历润色闭环状态回填

## 1. 归属切片

- `../slices/ai-resume-polish-capability-slice.md`
- `../execution/ai-resume/README.md`

## 2. 当前判定

- 回填日期：`2026-04-02`
- 当前判定：`局部完成（最小权威接口已落位）`
- 一句话结论：当前仓内仍然没有“编辑页发起 AI 简历润色 -> 返回 patch 草稿 -> 本地应用 -> 保存档案 -> 下游同步”的真实能力，但服务端已经补齐 `/ai/quota`、`/ai/polish-resume` 最小权威接口，小程序名片页也已切到真实配额口径；当前仍不能视为 AI 简历闭环。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pages/actor-profile/edit.vue` 当前没有 AI 面板、diff 预览、字段级应用、撤销或历史回滚能力
- `kaipai-frontend/src/pkg-card/actor-card/index.vue` 已存在 “AI 润色” 区块，但实际走的是本地 `polishActorCardCopy` 文案切换
- `kaipai-frontend/src/api/level.ts` 已消费 `/api/ai/quota`、`/api/ai/polish-resume`
- `kaipai-frontend/src/api/ai.ts`、`src/types/ai.ts` 已补齐 AI 简历 patch / history / rollback 最小 type 与 API 骨架，但编辑页尚未接入
- `kaipai-frontend/src/utils/runtime.ts` 已放开 `ai` 真接口能力，名片页与会员页已开始读取真实配额

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/ai/AiController.java` 已补齐 `/ai/quota`、`/ai/polish-resume` 最小公开接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/AiQuotaService.java`、`impl/AiQuotaServiceImpl.java` 已补齐月度 AI 配额查询与消费最小实现
- `kaipaile-server/src/main/java/com/kaipai/module/model/ai/dto/` 已补齐 `AiResumePolishReqDTO / RespDTO / HistoryItemDTO / RollbackDTO / ApplyMetaDTO` 最小契约骨架
- 当前虽已冻结 `05-04-ai-resume-polish/contract.md` 契约基线，并补齐前后端最小 DTO / type 骨架，但字段级 patch、错误码、历史快照与回滚仍未落成真实接口

### 3.3 后台治理

- 当前后台没有 AI 简历专用治理页、样本回看页或异常处理页
- 现阶段只能借用通用操作日志能力，尚未形成 AI 调用治理入口

### 3.4 联调现状

- 当前不能确认任何真实的三端联调路径
- 现有“AI”现在可以证明最小真配额链路已存在，但仍只能证明名片页演示态交互，不证明简历润色闭环

## 4. 联调结论

- 当前是否具备三端联调条件：`仍不具备`
- 已确认走通的链路：名片页本地文案润色演示、真实 `/ai/quota` 查询和 `/ai/polish-resume` 配额消费
- 当前不能宣告闭环的原因：编辑页无 AI 入口、真实文本生成仍不存在、后台无治理入口、契约虽已冻结但未落成代码

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已完成 AI 简历切片和执行卡 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 最小 quota / consume 接口已落地，且 patch / history / rollback 契约与 DTO / type 骨架已补齐，但真实接口与状态流转仍未落地 |
| 后台治理入口可操作 | 未满足 | 后台没有 AI 调用治理专属入口 |
| 小程序或前台用户侧落点可验证 | 部分满足 | 名片页已切到真实配额，但编辑页真实落点仍不存在 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 真实配额与认证前置已开始接入，但失败兜底、历史回滚和治理日志仍未形成完整能力 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已建立 AI 简历状态基线 |

## 6. 当前阻塞项

- 字段级 patch 协议、错误码和历史回滚模型已在文档冻结，且前后端最小 DTO / type 骨架已补齐，但 controller / service / 页面仍未接通
- 服务端虽已补齐最小 quota / consume 接口，但没有真实 AI / LLM 生成与 patch 封装
- 编辑页 UI、应用确认、撤销 / 回滚和后台治理入口均未开始真实实现

## 7. 下一轮最小动作

1. 按 `05-04-ai-resume-polish/contract.md` 把前后端 DTO / TS type 落地，避免协议继续漂移
2. 在服务端把 `quota / consume` 扩展成真实生成 / patch 适配层，而不是只做配额扣减
3. 在编辑页补 AI 面板和 patch 应用流程，并把“本地应用 -> 保存档案”链路接通，再跑一次“编辑页 -> 名片页 / 公开详情页”联调回填

## 8. 回填记录

### 2026-04-01

- 当前判定：`局部完成（演示态）`
- 备注：明确把现有名片页 AI 能力降格为演示态记录，避免后续把 mock 润色误当成 AI 简历闭环

### 2026-04-02

- 当前判定：`局部完成（最小权威接口已落位）`
- 备注：`kaipaile-server` 已补齐 `/ai/quota`、`/ai/polish-resume` 最小接口，并在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过；`kaipai-frontend` 已放开 `ai` 真接口分支，`npm run type-check` 通过，当前仍缺真实生成、patch 协议、编辑页入口和后台治理
- 追加备注：已补 `05-04-ai-resume-polish/contract.md`，明确 `draftId -> actor/profile save -> history/rollback` 契约，冻结可写字段白名单、数值错误码和稳定 `fieldKey` 口径
- 追加备注：`kaipai-frontend` 已补 `src/api/ai.ts`、`src/types/ai.ts`，`kaipaile-server` 已补 AI 简历 DTO 骨架和 `ActorProfileSaveDTO.aiResumeApplyMeta` 预留位，为下一轮 controller / service / edit.vue 接线做准备
- 追加备注：本轮已再次执行 `kaipai-frontend` `npm run type-check` 通过，并在切换本机 `JDK 21` 后执行 `kaipaile-server` `mvn -q -DskipTests compile` 通过
