# 测试候选全栈运行态一致性与演员卡生成约束修复

> 状态：已完成（2026-09-01）。
>
> 上游：`00-245`、`00-246`、`00-243`；下游：`00-236` 人工验收。

## 1. 概述

Candidate `20260901-150906-v3-draft` 的冻结小程序、`dist/build/mp-weixin` 和固定 `dist/dev/mp-weixin` 已一致，但同一 Candidate 的后端 JAR 与数据库迁移尚未进入测试运行态。演员卡使用私有素材作为首图时，生成任务按 `00-245` 设计不持久化短时签名 URL，而旧测试库仍要求 `actor_ai_profile_card_task.source_image_url NOT NULL`，最终在 `pkg-actor-card/generate/index` 显示“生成失败 / 数据约束校验失败”。

本 Spec 修复的是测试候选全栈部署与准入合同，不通过修改生成页隐藏后端错误。

## 2. 用户故事

作为人工验收人员，我希望固定小程序调用的测试后端、数据库结构与冻结 Candidate 属于同一版本，避免在已声明可验收后遇到候选内已修复但测试运行态未部署的问题。

作为发布执行人员，我需要在标记 `AWAITING_MANUAL_ACCEPTANCE` 前证明候选后端 JAR 哈希、测试容器运行 JAR 哈希、测试库关键 DDL 和候选内嵌迁移合同一致。

作为生产环境维护者，我需要该修复只作用于测试容器和 `kaipai_test`，不修改生产容器、`kaipai_prod`、生产 Nginx 或正式小程序。

## 3. 功能需求

### 3.1 精确故障证据

- WHEN 演员卡生成返回“数据约束校验失败” THEN 必须从测试后端日志记录具体数据库异常，不得猜改前端。
- 本次基线异常固定为 `Field 'source_image_url' doesn't have a default value`。
- WHEN 读取数据库合同 THEN 只允许查询 `kaipai_test` 的列、索引和最小任务状态，不输出凭据或私有素材 URL。

### 3.2 全栈 Candidate 身份

- WHEN Candidate 包含后端 JAR THEN 测试容器必须运行该 JAR 的相同 SHA256。
- WHEN Candidate JAR 内含数据库迁移 THEN 测试库必须完成该 Candidate 所需迁移，并通过关键 DDL 读回。
- WHEN 小程序冻结目录、固定 dev、测试后端 JAR 或测试库合同任一不一致 THEN 状态必须为 `TEST_STACK_NOT_READY`，不得记录 `READY_FOR_MANUAL_ACCEPTANCE`。

### 3.3 测试环境修复

- 对 `kaipai_test` 执行 `V20260901_001__actor_card_internal_auto_expand.sql` 前必须生成测试库备份并记录哈希。
- 迁移必须先于 Candidate 后端启动；只允许重建 `kaipai-backend-test`，不得重建或重启生产容器。
- 修复后 `source_image_url` 必须可空，稳定来源字段与唯一索引必须存在。
- 生产容器 ID、启动时间和重启次数必须在操作前后保持不变。

### 3.4 运行验收

- 通过微信内部 MCP 在固定工程 `kaipai-frontend/dist/dev/mp-weixin` 重新触发同一演员卡生成，不重启、置顶、抢焦点或控制微信开发者工具桌面窗口。
- 生成请求不得再返回数据库约束错误；生成状态必须进入 `pending/running/done` 合同并展示结构化演员卡预览。
- 测试后端日志不得新增 `source_image_url` 约束异常。
- 修复测试运行态后，重新执行全栈准入门禁；只有所有证明通过才恢复人工验收。

## 4. 验收标准

- 基线日志精确复现两次 `Field 'source_image_url' doesn't have a default value`。
- Candidate JAR 内存在 `V20260901_001__actor_card_internal_auto_expand.sql`，候选 JAR SHA256 固定并可读回。
- `kaipai_test` 迁移后关键列、可空性和唯一索引符合 `00-245`，迁移重复验证通过。
- Candidate 后端 JAR 与测试容器运行 JAR SHA256 一致。
- MCP 对 `pkg-actor-card/generate/index?cardId=1` 的复测通过，页面不再显示“数据约束校验失败”。
- `00-236/00-243` 状态和证据同步；正式发布仍为 `NOT_AUTHORIZED`。

## 5. 兼容与约束

- 不修改演员卡生成前端以吞掉或重命名数据库异常。
- `source_image_url` 仅放宽为可空，历史 URL 任务继续兼容；新增列均可空，迁移幂等。
- 当前 Candidate 在全栈测试运行态修复完成前，人工验收状态失效。
- 未获得明确 `GO`，不执行 `00-237`，不迁移生产数据库，不切换正式 Nginx，不上传正式版本。
