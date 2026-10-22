# 00-235 生产副本测试库迁移验证 - 技术设计

_Requirements: 3.1-3.7, 4, 5_

## 1. 执行状态机

```text
AUTHORIZED
  -> BACKUPS_VERIFIED
  -> TEST_RESTORED
  -> SCHEMA_MIGRATED
  -> MEDIA_BACKFILLED
  -> ASSERTIONS_PASSED
  -> TEST_DATA_READY
```

任何阶段失败都停止，不自动跨过失败阶段。

## 2. 备份设计

生产和测试分别使用一致性 dump，至少包含：

```text
--single-transaction --routines --triggers --hex-blob
```

备份记录：环境、schema、安全表数量、dump size、开始/结束时间、远端 SHA256、本地 SHA256。密码通过安全 helper/环境输入，不出现在命令记录。

备份完成后做最低可恢复性检查：gzip/SQL 可读取、包含建表语句、非零表数量。全量恢复演练由测试库本身完成。

## 3. Destructive Target Guard

重建前必须同时满足：

- 操作参数字面值为 `kaipai_test`。
- helper 解析结果为 `kaipai_test`。
- 当前 test 容器停止。
- production schema 为 `kaipai_prod` 且与 target 不同。
- 备份 SHA256 已验证。

任何变量未解析、空值或多目标都拒绝操作。命令不得跨 PowerShell/cmd/bash 拼接删除目标。

## 4. 恢复一致性证明

生产备份时生成 PII-free baseline：

- schema 表数量和总大小。
- 关键表有效行数。
- 按主键、状态、时间等非敏感字段形成稳定聚合哈希。
- 旧媒体字段非空计数和 URL SHA256 集合哈希。

恢复后在 `kaipai_test` 生成同口径结果，必须完全一致。使用聚合哈希而不是导出原始行。

## 5. 迁移执行

调用 `00-232` runner，显式目标：

```text
--mysql-database kaipai_test
```

逐 migration 记录 preflight、执行耗时、验证、history 写入和结果。失败后不恢复整个测试库来掩盖 partial DDL；先留存实际状态证据，再决定修复或从备份重建重新演练。

## 6. 媒体回填

先执行 `00-233 dry-run`。永久异常必须分类为：

- 历史源本来已失效，产品接受降级。
- URL/JSON 数据异常，需要定点修复。
- 工具或环境错误，需要修复后重跑。

只有用户明确签收第一类、其余为 0 时才 apply。Apply 只写 `kaipai_test` 和 test bucket。

## 7. 数据断言矩阵

| 域 | 前后比较 | 孤儿断言 |
|---|---|---|
| 用户 | 有效数不减少 | - |
| 演员档案 | 有效数、旧字段哈希不变 | profile.user_id 存在 |
| 演艺经历 | 有效数、旧名称/角色哈希不变 | experience 的 user/profile 存在 |
| 分享 | 旧卡、浏览历史数不减少 | card/user/profile 归属存在 |
| 实名 | 状态分布哈希不变 | verification.user_id 存在 |
| 媒体 | 旧 URL 哈希不变，新 ready asset 完整 | asset/profile relation owner 一致 |
| Actor card | 新表可空但结构完整 | card work/media set/item 归属存在 |

所有断言记录只输出 count/hash/status。

## 8. API Smoke

自动 smoke 顺序：

1. API docs/health。
2. 后台登录和权限读取。
3. 历史账号会话/资料只读。
4. 新资料、经历、素材、演员卡 API。
5. 公开旧分享和新演员卡读取。
6. 旧客户端请求/响应 contract tests。

产生写入的 smoke 使用专用测试账号，完成后不需要清除生产副本原数据，只记录测试新增行范围。

## 9. 证据包

建议路径：

```text
.sce/runbooks/backend-admin-release/records/<candidate-id>/test-prod-copy-validation/
```

包含备份 manifest、restore summary、migration record、media reports、before/after assertions、API smoke 和最终 decision。证据包生成总 SHA256。

## 10. 回滚边界

失败时停止 test backend。可删除并从旧 test 备份恢复 `kaipai_test`，但每次 destructive 操作都重新走 guard。生产 schema 和生产容器不在本阶段回滚范围。
