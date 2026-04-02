# 剧组档案、项目、角色与投递最小连通闭环执行卡

本目录用于承接 `slices/crew-company-project-recruit-capability-slice.md` 的下一层拆分。

## 目标

把 `company / project / role / apply-manage` 这条历史剧组线，从“真实接口最小接通”继续拆成可分派、可并行、可单独验收的 4 张执行卡：

1. 前端执行卡
2. 后端执行卡
3. 后台执行卡
4. 联调执行卡

## 使用方式

每张执行卡都只负责一个交付面，但必须引用同一张能力切片卡：

- `../../slices/crew-company-project-recruit-capability-slice.md`

## 本轮规则

- 必须承认当前项目事实：`project` 仍在 `company_profile.extendedField.projects`，不是独立项目表
- 后台最小治理动作只做到项目 / 角色状态处置，不扩张成完整项目治理台
- 联调卡只负责真实环境收口，不负责补做功能
- 所有状态结论回填到 `status/crew-company-project-status.md` 与 `status/recruit-role-apply-status.md`

## 样本脚本

- 真实登录态招募闭环样本统一通过 `run-authenticated-recruit-sample.py` 执行
- 样本证据默认落到 `samples/<timestamp>-<label>/results.json` 与 `summary.md`
- 禁止再用临时 PowerShell 字符串拼接 query 参数做招募联调，避免把 `=1&size=20` 一类拼接错误误判成后端缺陷
