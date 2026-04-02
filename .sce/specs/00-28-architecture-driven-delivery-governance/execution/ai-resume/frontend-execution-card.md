# AI 简历润色闭环前端执行卡

## 1. 执行卡名称

AI 简历润色闭环 - 小程序前端执行卡

## 2. 归属切片

- `../../slices/ai-resume-polish-capability-slice.md`

## 3. 负责范围

- 演员档案编辑页的 AI 入口、对话面板、patch 预览与应用交互
- 字段级应用、整批应用、撤销、历史回看与回滚交互
- AI 配额、认证前置、等级能力在前端的统一展示
- AI 应用结果回写到编辑表单，并联动验证名片页与公开详情页
- AI 失败、超时、敏感内容的前端兜底交互

## 4. 不负责范围

- 大模型封装、prompt、安全策略、敏感词与配额扣减服务端实现
- 后台 AI 策略配置、失败样本回看和成本监控
- 任何前端直连模型的实现
- 未经用户确认自动覆盖档案字段

## 5. 关键输入

- 上位 Spec：
  - `00-27 mini-program-frontend-architecture`
  - `03-04 page-actor-profile-edit`
  - `05-02 actor-profile-enhance`
  - `05-04 ai-resume-polish`
  - `05-04 ai-resume-polish/contract.md`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipai-frontend/src/pages/actor-profile/edit.vue`
  - `kaipai-frontend/src/pages/actor-profile/profile-enhance.ts`
  - `kaipai-frontend/src/pkg-card/actor-card/index.vue`
  - `kaipai-frontend/src/pages/actor-profile/detail.vue`
  - `kaipai-frontend/src/api/ai.ts`
  - `kaipai-frontend/src/types/ai.ts`
  - `kaipai-frontend/src/api/level.ts`
  - `kaipai-frontend/src/types/level.ts`
  - `kaipai-frontend/src/utils/actor-card.ts`
  - `kaipai-frontend/src/stores/user.ts`
  - `kaipai-frontend/src/mock/service.ts`

## 6. 目标交付物

- AI 入口从当前名片页本地“润色语气”能力，升级为编辑页真实的字段级 patch 工作流
- 编辑页具备对话、patch diff、按字段应用、整批应用、撤销与历史回看
- AI 配额、实名认证前置、等级能力与等级中心口径一致
- 应用后的档案结果可立即联动到名片页与公开详情页验证
- 前端不再把“切换文案 tone 并扣配额”误当成 AI 简历闭环

## 7. 关键任务

1. 把 AI 主入口回收到编辑页
   - 当前 `pages/actor-profile/edit.vue` 没有 AI 面板
   - 当前 `pkg-card/actor-card/index.vue` 的 `applyAiPolish` 只是本地切换 `appliedTone` 并调用配额接口
   - 需要把真正的 AI 交互放回编辑页，而不是继续停留在名片页
2. 定义前端 AI 状态模型
   - 对话消息
   - patch 预览
   - 字段应用状态
   - 撤销 / 历史状态
   - 超时 / 失败状态
3. 定义字段级 patch 回写交互
   - 预览修改前后差异
   - 按字段应用
   - 整批应用
   - 撤销最近一次应用
   - 历史回滚
   - patch 的 `fieldKey` 必须使用稳定 key，不能用数组下标
   - 本地应用 patch 后，只更新 `form`，不直接视为保存成功
4. 对齐配额与 gating
   - `api/level.ts` 当前只暴露 `getAiQuota` 与 `consumeAiPolishQuota`
   - 前端要改成消费真实 AI patch 接口，不把“扣配额”本身当成功结果
   - 认证状态、等级能力、配额文案与等级中心一致
5. 对齐 AI 保存语义
   - AI patch 只是草稿
   - 真正入库仍走 `PUT /api/actor/profile`
   - 保存时要附带 `aiResumeApplyMeta`
6. 做应用结果联动验证
   - 应用后刷新 `actor-card` 与 `actor-profile/detail`
   - 确认档案摘要、公开页文本与编辑页最新结果一致

## 8. 依赖项

- 后端必须先提供结构化 patch 协议和真实 AI 接口
- 配额、敏感词、超时和失败原因必须由服务端给出权威结果
- 档案字段映射需要先冻结，否则前端 diff 和应用逻辑会反复返工
- `draftId / appliedPatchIds / requestId` 与档案保存的衔接方式必须固定，否则前端无法稳定做历史与回滚入口

## 9. 验证方式

- 编辑页可打开 AI 面板并发送自然语言指令
- AI 返回字段级 patch 后，前端可展示修改前后对比
- 用户可按字段应用、整批应用、撤销并看到表单同步变化
- AI patch 应用后，仍需通过“保存档案”动作完成真实入库
- 配额扣减只在真实调用成功后发生，失败 / 超时有清晰提示
- 应用后的结果在名片页和公开详情页可见，且口径一致

## 10. 完成定义

- 编辑页具备真实 AI 入口和结构化 patch 交互
- 前端不再把名片页语气切换当成 AI 简历能力
- 配额、认证、等级 gating 与等级中心一致
- 应用结果可联动验证到下游展示页
- 前端可以明确指出当前 AI 是闭环完成还是仍停留在 mock / 演示态

## 11. 风险与备注

- `pkg-card/actor-card/index.vue` 的旧本地 tone 切换已被收口；当前真实前端主线已迁入 `pages/actor-profile/edit.vue` 的 AI 面板与 patch 交互
- `2026-04-03` 最新真实样本 `run-ai-resume-validation.py` 已证明前端消费的 actor API 链路可在目标环境走通；前端当前剩余重点已不是“有没有 AI 面板”，而是“页面级真机证据、公开详情页回流验证，以及 mock adapter 何时继续收边”
- 若继续让部分环境静默走 `useApiMock('ai')`，仍可能把演示态误判成真实联调；因此后续页面验收必须绑定真实样本目录，而不是只看页面能否打开
