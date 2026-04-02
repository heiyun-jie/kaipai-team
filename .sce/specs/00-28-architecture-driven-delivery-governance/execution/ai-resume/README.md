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
- 当前必须承认真实现状：编辑页 patch 流程、后台治理页、治理动作审计、角色页授权矩阵与建议授权包都已落地，且目标环境角色矩阵已通过标准样本收口；仓内也已移除 `operation-logs` 对 AI 治理的权限兜底，但真机联调、退场后的目标环境发布复验和真实 LLM 仍未完成

## 当前标准样本入口

- 真实联调脚本：`run-ai-resume-validation.py`
- 角色收口脚本：`run-ai-role-authorization-closure.py`
- 最新样本：`samples/20260403-071241-continue-rerun/summary.md`
- 最新角色收口样本：`samples/20260403-072120-continue-ai-role-closure/summary.md`
- 当前已固定的真实链路：
  - actor `quota -> polish-resume -> actor/profile save(aiResumeApplyMeta) -> history -> rollback`
  - admin `overview -> histories -> failures -> sensitive-hits -> review -> close -> operation-logs`
- 当前未闭环边界：
  - 目标环境 AI 角色矩阵已收口为 `aiReadyRoleCount=1 / fallbackRoleCount=0 / canRetireFallback=true`
  - 真机页面级证据、fallback 退场后的目标环境发布复验与真实 LLM 仍未补齐
