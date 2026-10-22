# 00-235 生产副本测试库迁移验证

> 状态：`TEST_DATA_READY`（2026-08-27 生产副本兼容、历史媒体和新旧合同门禁通过）
>
> 上游：`00-231`、`00-232`、`00-233`、`00-234`；下游：`00-236`、`00-237`

## 1. 概述

本 Spec 使用 `kaipai_prod` 的完整一致性副本重建 `kaipai_test`，在隔离测试环境中执行冻结的 Schema 迁移和历史媒体回填，并通过迁移前后计数、哈希、孤儿关系和旧客户端 smoke 验证真实生产数据兼容性。

## 2. 用户故事

作为发布负责人，我希望生产迁移前已经在完全相同的历史数据上演练成功，而不是只在空库或开发库上测试。

作为数据负责人，我希望任何数据减少、关系断裂或旧字段被覆盖都能自动阻断发布。

## 3. 功能需求

### 3.1 安全备份生产和现有测试库

**验收标准**：

- WHEN 开始重建 THEN 测试后端已停止并确认无连接写 `kaipai_test`。
- WHEN 备份 THEN 分别生成 `kaipai_prod` 和旧 `kaipai_test` 一致性 dump。
- WHEN 备份完成 THEN 远端/本地 SHA256 一致，dump 可读取且目标 schema 名已记录。
- WHEN 任一备份失败 THEN 不执行测试库重建。

### 3.2 精确重建 `kaipai_test`

**验收标准**：

- WHEN 执行 destructive 操作 THEN 解析后的精确目标只能是 `kaipai_test`。
- WHEN 目标为 `kaipai_prod`、空值、通配符或未知变量 THEN 立即中止。
- WHEN 恢复完成 THEN 测试库的结构、关键有效行数和聚合哈希与备份时生产快照一致。
- WHEN 需要回退本阶段 THEN 可用旧测试库备份恢复 `kaipai_test`，不触碰生产库。

### 3.3 执行冻结的迁移批次

**验收标准**：

- WHEN 执行迁移 THEN 使用 `00-231` candidateId/manifest SHA256 和 `00-232` 同一 runner。
- WHEN 14 个文件任一 checksum、顺序或 preflight 不一致 THEN 中止。
- WHEN 迁移结束 THEN Schema assertion 和 history assertion 全部通过。

### 3.4 执行历史媒体回填

**验收标准**：

- WHEN 回填测试副本 THEN 使用 `00-233` 冻结工具版本和 test private bucket。
- WHEN dry-run 存在未裁决永久异常 THEN 不执行 apply。
- WHEN apply 后重跑 THEN 新建对象、asset 和关系数量均为 0。
- WHEN 生产 bucket 有任何写入/删除变化 THEN 立即 `NO-GO`。

### 3.5 验证结构化历史数据

**验收标准**：

- WHEN 比较迁移前后 THEN 用户、档案、经历、旧分享卡、浏览历史、实名记录有效行数不减少。
- WHEN 新字段有默认值 THEN 不得覆盖旧作品名、角色名、intro、媒体 URL 或实名状态。
- WHEN 检查关系 THEN 不存在新增孤儿用户档案、经历、分享卡、实名、asset 或 profile asset。
- WHEN 规范化字段为空 THEN 不据此删除、合并或隐藏历史作品。

### 3.6 验证旧、新应用合同

**验收标准**：

- WHEN 候选后端连接迁移后测试库 THEN 核心 API、后台登录和新素材接口 smoke 通过。
- WHEN 使用旧客户端合同请求 THEN 既有响应结构、旧 URL 和鉴权语义仍可用。
- WHEN 测试服务运行 THEN 再次证明数据源为 `kaipai_test`。

### 3.7 输出生产可复用证据

**验收标准**：

- WHEN 全部门禁通过 THEN 输出迁移耗时、锁影响、数据断言、回填统计和 `GO`。
- WHEN 任一计数减少、孤儿增加、checksum drift 或旧合同失败 THEN 输出 `NO-GO`。
- WHEN `00-237` 启动 THEN 必须引用本阶段证据 SHA256，生产不得使用不同批次。

## 4. 非功能需求

- 备份和验证记录不得包含 dump 内容、PII 或完整媒体 URL。
- 记录每个 DDL 实际耗时，用作生产窗口估算。
- 测试副本包含生产数据，访问权限、日志和截图按生产敏感级别控制。

## 5. 约束条件

- 重建 `kaipai_test` 是破坏性操作，需要用户明确授权。
- 不允许把旧测试业务数据合并进生产副本。
- 本阶段只读 `kaipai_prod`；除一致性备份外不在生产 schema 执行 SQL。
