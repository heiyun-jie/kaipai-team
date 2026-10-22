# 00-232 Schema 迁移安全与校验和门禁

> 状态：Spec 完成，实施未开始
>
> 上游：`00-230`、`00-231`；下游：`00-235`、`00-237`

## 1. 概述

本 Spec 确保 14 个 Schema 迁移在测试和生产使用完全相同的文件与顺序，解决当前 5 个非幂等脚本、MySQL DDL 隐式提交和 migration runner 只按文件名跳过而未核对已登记 checksum 的风险。

## 2. 用户故事

作为数据库发布操作人，我希望脚本在“未执行、已完整执行、部分执行”三种状态下给出确定动作，而不是失败后盲目重跑。

作为发布负责人，我希望测试通过的迁移字节与生产执行的迁移字节完全一致。

## 3. 功能需求

### 3.1 锁定迁移批次

**验收标准**：

- WHEN 加载发布批次 THEN 只接受 `00-230 design §3.2` 的 14 个文件和固定顺序。
- WHEN 文件 SHA256 与 `00-231` manifest 不同 THEN 立即中止。
- WHEN 文件未被 Git 跟踪或出现未声明 migration THEN 不进入测试副本迁移。

### 3.2 强制历史校验和一致

**验收标准**：

- WHEN `schema_release_history` 已有同名脚本 THEN runner 必须比较已登记 checksum 与当前 checksum。
- WHEN checksum 相同 THEN 允许跳过并记录 `skip-same-checksum`。
- WHEN checksum 不同 THEN 输出 `NO-GO`，不得覆盖 history 中原 checksum。
- WHEN history 表不存在 THEN 只创建 history 表，不将未核实结构自动标记为已执行。

### 3.3 分类 5 个非幂等迁移的目标状态

**验收标准**：

- WHEN 执行 `V20260724_001`、`V20260726_001`、`V20260731_001/002`、`V20260810_001` 前 THEN 运行结构/数据前置断言。
- WHEN 目标处于 clean-not-applied THEN 允许原脚本执行一次。
- WHEN 目标处于 fully-applied 且 checksum 已登记 THEN 跳过。
- WHEN 目标处于 partial/ambiguous THEN 中止并使用新版本 repair migration，禁止重跑原文件。

### 3.4 验证首次执行、重复执行和部分失败

**验收标准**：

- WHEN 在 MySQL 8 fixture 首次执行 14 个迁移 THEN 全部成功且满足目标 Schema。
- WHEN runner 再次执行同批 THEN 14 个全部按相同 checksum 安全跳过。
- WHEN 注入 checksum 改变 THEN runner 必须失败。
- WHEN 模拟 DDL 已提交但 history 未写入 THEN preflight 必须识别 partial/ambiguous 并阻断。

### 3.5 输出 Schema 验证证据

**验收标准**：

- WHEN 迁移完成 THEN 验证 19 张表、全部必需字段、索引、约束和 seed。
- WHEN 验证记录生成 THEN 只输出对象名、计数、checksum 和状态，不输出业务数据。
- WHEN 生产迁移启动 THEN 必须引用测试副本同批验证记录。

## 4. 非功能需求

- 不依赖 Flyway/Liquibase 自动启动；沿用标准 schema runner。
- 不修改已经登记过且可能进入其他环境的历史 migration 字节；需要修复时新增更高版本 migration。
- Runner 错误必须在执行目标脚本前尽早失败，并留下脱敏证据。

## 5. 约束条件

- MySQL DDL 存在隐式提交，不能宣称整批事务回滚。
- 不允许通过手工 UPDATE `schema_release_history.checksum` 消除不一致。
- 生产只执行经过 `kaipai_test` 生产副本验证的同一 manifest。
