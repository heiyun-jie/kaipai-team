# AI 简历润色闭环联调执行卡

## 1. 执行卡名称

AI 简历润色闭环 - 联调与回归执行卡

## 2. 归属切片

- `../../slices/ai-resume-polish-capability-slice.md`

## 3. 负责范围

- 串联编辑页、后端 AI 模块、下游展示页、后台治理入口的联调顺序
- 定义 AI 简历闭环的端到端验证矩阵
- 收口 patch 协议、配额策略、失败兜底与历史回滚
- 明确“局部完成”和“闭环完成”的验收边界

## 4. 不负责范围

- 单独补做编辑页 UI
- 单独补做后端 AI 模块
- 单独补做后台 AI 运维页
- 脱离闭环目标的模型能力扩展

## 5. 关键输入

- 上位切片：
  - `../../slices/ai-resume-polish-capability-slice.md`
- 执行卡：
  - `frontend-execution-card.md`
  - `backend-execution-card.md`
  - `admin-execution-card.md`
- 关键链路文件：
  - `kaipai-frontend/src/pages/actor-profile/edit.vue`
  - `kaipai-frontend/src/pkg-card/actor-card/index.vue`
  - `kaipai-frontend/src/pages/actor-profile/detail.vue`
  - `kaipai-frontend/src/api/level.ts`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/actor/ActorProfileController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/actor/service/impl/ActorProfileServiceImpl.java`
  - `kaipai-admin/src/views/system/OperationLogsView.vue`

## 6. 目标交付物

- 一条可重复执行的“编辑页发起 AI -> 返回 patch -> 本地应用 -> 保存档案 -> 下游展示更新 -> 后台可回看”联调路径
- 一份问题清单模板：前端 / 后端 / 后台分别归因
- 一份回归清单：配额、认证 gating、patch 应用、历史回滚、失败兜底、日志
- 一次明确的“AI 简历润色闭环完成度”验收结论

## 7. 关键任务

1. 先冻结 patch 协议
   - 字段名
   - diff 结构
   - `draftId / historyId` 语义
   - 错误码与失败原因
2. 建立主场景矩阵
   - 成功返回 patch
   - 按字段应用
   - 整批应用
   - 保存档案
   - 撤销
   - 历史回滚
3. 建立 gating 与异常矩阵
   - 未认证不可用
   - 配额用尽
   - 超时
   - 敏感内容命中
   - 不可解析响应
4. 建立下游验证矩阵
   - 编辑页应用后刷新名片页
   - 编辑页应用后刷新公开详情页
   - 等级中心 / 名片页配额展示一致
5. 建立治理回看矩阵
   - 后台能回看调用结果或异常样本
   - AI 规则调整后前台提示和 gating 同步变化

## 8. 依赖项

- 后端 AI 模块和 patch 协议必须先稳定
- 编辑页 AI 面板与字段应用能力必须具备
- 至少要准备一组正常样本、一组配额耗尽样本、一组敏感词样本、一组超时样本
- 若要补页面级真实证据，默认走 `run-ai-mini-program-page-evidence.py` 与 `run-ai-admin-page-evidence.py`，不得回退到手工零散截图

## 9. 验证方式

- 场景 1：编辑页成功拿到 patch
  - 用户可预览 diff
  - 可按字段应用或整批应用
- 场景 2：应用后验证下游
  - 用户执行保存档案
  - 名片页文本更新
  - 公开详情页文本更新
- 场景 3：撤销与回滚
  - 撤销最近一次应用
  - 历史回滚到指定版本
- 场景 4：配额与 gating
  - 未认证提示一致
  - 配额耗尽提示一致
  - 成功调用后配额正确扣减
- 场景 5：异常与治理
  - 超时 / 敏感内容 / 解析失败有明确提示
  - 后台可回看异常样本或日志
  - 协同链至少要复验 `assign -> acknowledge` 与 `assign -> remind`

## 10. 完成定义

- 编辑页、后端、后台治理、下游展示页的联调路径可重复执行
- patch 协议和错误码口径稳定
- 成功、失败、回滚、配额、认证五类核心场景全部走通
- 缺陷能够明确归因到前端 / 后端 / 后台
- 可以给出“AI 简历润色闭环已完成”或“仍停留在演示态”的明确结论

## 11. 风险与备注

- `2026-04-03` 最新真实样本 `samples/20260403-071241-continue-rerun/summary.md` 已不再是“名片页本地切文案 + mock 配额”；actor/admin 真接口与治理动作已形成一条可重复执行的远端样本链
- `2026-04-03 16:41` 已新增并执行最小协同样本 `run-ai-resume-collaboration-validation.py`，样本 `samples/20260403-164135-continue-ai-collaboration-closure/summary.md` 已固定 `assign -> acknowledge`、`assign -> remind`、协同状态筛选与 `ai_resume_assign / ai_resume_acknowledge / ai_resume_remind` 审计回看
- `2026-04-03 16:50` 已新增并执行业务回归汇总样本 `run-ai-resume-business-regression-summary.py`，样本 `samples/20260403-165026-continue-ai-business-regression-summary/summary.md` 已把同一轮主链样本 `20260403-164852-continue-ai-business-regression-main` 与页面样本 `20260403-164932-ai-business-regression-page-evidence` 固化成一条标准回归记录
- `2026-04-03` 已补页面级证据脚本入口：
  - `run-ai-mini-program-page-evidence.py`
  - `run-ai-admin-page-evidence.py`
  当前后续缺口已从“没有标准采证入口”收口为“已实际产出前后台页面样本，后续继续复用标准脚本增量采证”
- `2026-04-03 16:17` 已通过官方 `cli auto --project ... --auto-port 9421` 恢复 DevTools 自动化；首轮小程序采证样本 `samples/20260403-161829-ai-mini-program-page-evidence/summary.md` 出现 2 张窗口兜底白图后，`16:22` 复跑样本 `samples/20260403-162122-ai-mini-program-page-evidence-rerun/summary.md` 已确认 4/4 页面全部走 `automator`
- 若没有冻结字段级 patch 协议，前后端会在 diff 结构上持续拉扯
- 若只验证 actor/admin API，不补编辑页、名片页和公开详情页的页面级真实证据，AI 简历能力仍然只是局部完成
