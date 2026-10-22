# 测试小程序候选单一事实源与人工验收准入

> 状态：已完成（2026-09-01）。

## 1. 概述

历史构建流程会产生工作区 `dist/build/mp-weixin`、冻结候选 `mini-program-test` 和微信开发者工具固定工程 `dist/dev/mp-weixin`。三个目录职责不同，但缺少统一准入命令，导致工作区 build 已变化、固定 dev 仍是旧候选时仍可能被表述为“可以人工验收”。本 Spec 将带 Candidate ID 的冻结 `mini-program-test` 固定为唯一候选事实源，并由 00-252 将日常测试运行、审计和 MCP 入口收口到 `dist/dev/mp-weixin`。

## 2. 用户故事

作为人工验收人员，我只测试一个明确 Candidate ID 对应的冻结小程序，不需要判断 `dist/build` 和 `dist/dev` 哪个更新。

作为发布执行人员，我需要一条只读命令证明候选完整、实现输入未变化、固定 dev 与候选一致、编译缓存和实时请求均指向测试环境；隔离构建目录只在显式传入时作为发布诊断。

作为生产环境维护者，我需要该门禁只检查本地和测试候选，不迁移生产数据库、不切换生产 Nginx、不上传正式小程序。

## 3. 功能需求

### 3.1 冻结候选是唯一事实源

- WHEN 指定 Candidate ID THEN 门禁只从 `records/<Candidate>/00-231` 读取 `candidate-manifest.json`、`artifact-evidence.json` 和 `artifacts/mini-program-test`。
- WHEN manifest、sidecar SHA256、artifact evidence 或冻结目录任一不完整或被修改 THEN 返回 `INVALID_CANDIDATE`，不得进入人工验收。
- 新冻结的 `mini-program-test` 必须包含确定性的 `project.private.config.json`（仅 `urlCheck=false`），避免微信开发者工具首次打开后新增本地文件破坏完整目录等价；`mini-program-release` 不包含该测试私有配置。
- `dist/build/mp-weixin` 只作为候选生成或工作区漂移检测对象，不能单独证明候选可以验收。

### 3.2 候选输入与工作区 build 漂移

- WHEN backend、admin 或 frontend 的 commit、branch、tracked/untracked overlay 与候选清单不同 THEN 返回 `CANDIDATE_REFREEZE_REQUIRED`。
- WHEN 显式传入隔离 `--build-dir` 且该目录与冻结 `mini-program-test` 的文件数、总字节或目录树 SHA256 不同或不存在 THEN 返回 `CANDIDATE_REFREEZE_REQUIRED`。
- WHEN 未显式传入 `--build-dir` THEN 门禁不读取工作区 `dist/build/mp-weixin`，只检查冻结候选和固定 `dist/dev/mp-weixin`，避免把第二个目录误当测试入口。
- WHEN 返回该状态 THEN 旧 Candidate 保持不可变；任何新修复必须生成新的 Candidate ID，不能覆盖旧候选。

### 3.3 固定运行镜像和环境目标

- WHEN `dist/dev/mp-weixin` 与冻结候选不完全一致 THEN 返回 `RUNTIME_NOT_SWITCHED`。
- WHEN运行镜像未命中测试 API，或命中本地/正式 API THEN 返回 `RUNTIME_NOT_SWITCHED`。
- WHEN 结构化运行证明未绑定同一 Candidate ID、同一固定工程目录树 SHA256，或项目级编译缓存/实时请求未证明测试环境 THEN 返回 `RUNTIME_NOT_SWITCHED`。

### 3.4 人工验收准入

- 只有候选完整、候选输入当前、dev 等价、测试 API 目标正确和运行证明全部通过时，命令才返回 `READY_FOR_MANUAL_ACCEPTANCE` 且退出码为 `0`。显式传入隔离 `--build-dir` 时再附加 build 等价检查。
- `INVALID_CANDIDATE` 退出码为 `2`，`CANDIDATE_REFREEZE_REQUIRED` 为 `3`，`RUNTIME_NOT_SWITCHED` 为 `4`。
- `00-236/00-243` 只有在该命令退出 `0` 后才允许记录 `AWAITING_MANUAL_ACCEPTANCE`。

## 4. 非功能需求

- 门禁使用 Python 标准库和现有候选 manifest helper，不引入新依赖。
- 默认只读，不复制候选、不覆盖 `dist/dev`、不清缓存、不控制微信开发者工具。
- 输出为稳定 JSON，包含 Candidate ID、状态、退出码和各检查项摘要。

## 5. 发布兼容与约束

- 不改变候选构建格式、后端接口、数据库合同或小程序运行代码。
- 不执行 `00-237`，正式发布状态保持 `NOT_AUTHORIZED`。
- 任何未来的运行证明必须包含 Candidate ID、固定工程绝对路径、运行目录树 SHA256、测试/本地/正式 API 缓存命中数以及实时测试请求结果。
