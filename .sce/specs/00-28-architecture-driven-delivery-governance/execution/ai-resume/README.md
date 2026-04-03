# AI 简历润色闭环执行卡

本目录用于承接 `slices/ai-resume-polish-capability-slice.md` 的下一层拆分。

## 目标

把“AI 简历润色闭环”从能力切片继续拆成可分派、可并行推进、可单独验收的 4 张执行卡，并补一份角色授权收口说明：

1. 前端执行卡
2. 后端执行卡
3. 后台执行卡
4. 联调执行卡
5. 角色授权收口说明

## 使用方式

每张执行卡都只负责一个交付面，但必须引用同一张能力切片卡：

- `../../slices/ai-resume-polish-capability-slice.md`
- `role-authorization-closure.md`

## 本轮规则

- 每张卡都要写清楚负责范围，不得跨层级抢活
- 每张卡都要标明依赖项和交付物
- 联调卡不负责补做功能，只负责收口验证、问题清单和回归要求
- 当前必须承认真实现状：编辑页 patch 流程、后台治理页、治理动作审计、角色页授权矩阵与建议授权包都已落地，且目标环境角色矩阵已通过标准样本收口；仓内与目标环境后台静态入口也都已移除 `operation-logs` 对 AI 治理的权限兜底，最小责任协同也已通过标准样本复验，但真实 LLM 与更完整治理协同仍未完成

## 当前标准样本入口

- 真实联调脚本：`run-ai-resume-validation.py`
- 治理协同脚本：`run-ai-resume-collaboration-validation.py`
- 业务回归汇总脚本：`run-ai-resume-business-regression-summary.py`
- 角色收口脚本：`run-ai-role-authorization-closure.py`
- 小程序页面证据脚本：`run-ai-mini-program-page-evidence.py`
- 后台页面证据脚本：`run-ai-admin-page-evidence.py`
- 最新主链样本：`samples/20260403-071241-continue-rerun/summary.md`
- 最新协同样本：`samples/20260403-164135-continue-ai-collaboration-closure/summary.md`
- 最新业务回归样本：`samples/20260403-165026-continue-ai-business-regression-summary/summary.md`
- 最新角色收口样本：`samples/20260403-072120-continue-ai-role-closure/summary.md`
- 最新小程序页面样本：`samples/20260403-162122-ai-mini-program-page-evidence-rerun/summary.md`
- 最新后台页面样本：`samples/20260403-161131-ai-admin-page-evidence/summary.md`
- 最新 DevTools 恢复样本：`samples/20260403-161755-ai-mini-program-devtools-replay/cli-auto-output.txt`
- 最新目标环境发布复验记录：`../../../../runbooks/backend-admin-release/records/20260403-162902-admin-only-ai-fallback-retirement-static-sync.md`
- 当前已固定的真实链路：
  - actor `quota -> polish-resume -> actor/profile save(aiResumeApplyMeta) -> history -> rollback`
  - admin `overview -> histories -> failures -> sensitive-hits -> review -> close -> operation-logs`
  - collaboration `collaboration-catalog -> assign -> acknowledge / remind -> operation-logs`
  - regression-summary `validation sample -> mini-program page evidence -> business regression summary`
- 当前页面级证据入口：
  - `run-ai-mini-program-page-evidence.py` 会基于最新 AI 样本回放 `actor-card -> actor-profile/edit -> actor-profile/edit?aiResume=1 -> actor-profile/detail`
  - `run-ai-admin-page-evidence.py` 会基于最新 AI 样本回放 `/system/ai-resume-governance` 的 overview、history detail、failure detail
- 当前未闭环边界：
  - 目标环境 AI 角色矩阵已收口为 `aiReadyRoleCount=1 / fallbackRoleCount=0 / canRetireFallback=true`
  - `2026-04-03 16:17` 已通过官方 `cli auto --project ... --auto-port 9421` 恢复 DevTools 自动化；`16:22` 又已通过 `run-ai-mini-program-page-evidence.py` 产出 `actor-card -> actor-profile/edit -> actor-profile/edit?aiResume=1 -> actor-profile/detail` 四页真机页面证据，当前前后台页面级证据均已补齐
  - `2026-04-03 16:29` 已按 `00-29` 标准 `admin-only` 脚本完成目标环境后台静态资源发布，发布记录为 `../../../../runbooks/backend-admin-release/records/20260403-162902-admin-only-ai-fallback-retirement-static-sync.md`；公网首页已切到 `index-bd3NuCPI.js`，且 bundle 内不再包含 `pagePermissionFallbacks:["page.system.operation-logs"]`
  - `2026-04-03 16:41` 已通过 `run-ai-resume-collaboration-validation.py` 固定最小协同样本：当前真实环境已可复验 `assign -> acknowledge`、`assign -> remind`、协同状态筛选与 `ai_resume_assign / acknowledge / remind` 审计回看
  - `2026-04-03 16:50` 已通过 `run-ai-resume-business-regression-summary.py` 固定一条标准业务回归记录：同一轮样本已串起 `quota -> polish -> save -> history -> rollback` 与 `actor-card / actor-profile-edit / actor-profile-edit?aiResume=1 / actor-profile-detail` 四页真机页面证据
  - 真实 LLM 与通知回执 / 自动催办 / 更细 SLA 等更完整治理协同仍未补齐
