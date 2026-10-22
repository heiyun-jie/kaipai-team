# 00-235 生产副本测试库迁移验证 - 任务拆解

## T1 授权与备份

- [x] 获取重建 `kaipai_test` 明确授权。
- [x] 停止测试后端并检查连接。
- [x] 备份 prod/test 并验证远端/本地 SHA256。
- [x] 生成生产 PII-free baseline。

**Validates: Requirements 3.1**

## T2 重建与恢复

- [x] 通过 destructive target guard。
- [x] 精确重建 `kaipai_test`。
- [x] 恢复生产 dump。
- [x] 验证恢复 baseline 完全一致。

**Validates: Requirements 3.2**

## T3 Schema 与媒体

- [x] 按 manifest 执行 14 个迁移。
- [x] 运行完整 Schema/history 断言。
- [x] 运行媒体 dry-run、裁决异常、执行 apply。
- [x] 重跑媒体 apply 验证幂等。

**Validates: Requirements 3.3, 3.4**

## T4 数据兼容断言

- [x] 比较关键业务计数和旧字段哈希。
- [x] 检查全部孤儿关系。
- [x] 检查生产 bucket 无变更。
- [x] 记录每个迁移耗时和锁影响。

**Validates: Requirements 3.5**

## T5 后端与旧合同 smoke

- [x] 启动 test backend 并回读目标 schema。
- [x] 执行新 API smoke。
- [x] 执行后台 smoke。
- [x] 执行旧客户端合同 smoke。

**Validates: Requirements 3.6**

## T6 阶段签收

- [x] 生成完整证据包和 SHA256。
- [x] 输出 `TEST_DATA_READY`。
- [x] 回填 `00-230 execution-plan.md`。

**Validates: Requirements 3.7**

## 当前状态

- [x] Spec 三件套已创建。
- [x] `kaipai_test` 已完成生产副本兼容演练；`kaipai_prod` 本轮保持只读且未迁移。
