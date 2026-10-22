# 00-232 Schema 迁移安全与校验和门禁 - 任务拆解

## T1 Runner checksum 门禁

- [ ] 将 history 加载从脚本名集合改为 script/checksum 映射。
- [ ] 相同 checksum 才允许 skip。
- [ ] checksum mismatch 中止且不覆盖原记录。
- [ ] 增加定向单元测试。

**Validates: Requirements 3.1, 3.2**

## T2 非幂等 migration preflight

- [ ] 为 5 个 migration 定义 clean/fully/partial 断言。
- [ ] 在执行前聚合运行全部 preflight。
- [ ] partial state 输出差异并阻断。

**Validates: Requirements 3.3**

## T3 MySQL 8 迁移测试

- [ ] 建立生产旧 Schema fixture。
- [ ] 验证首次执行 14 文件。
- [ ] 验证相同 manifest 重跑。
- [ ] 注入 checksum mismatch。
- [ ] 注入 DDL/history partial state。

**Validates: Requirements 3.4**

## T4 Schema 断言

- [ ] 实现 19 表和必需字段断言。
- [ ] 实现索引、约束、seed 和 history 断言。
- [ ] 输出不含业务数据的证据文件。

**Validates: Requirements 3.5**

## T5 阶段签收

- [ ] 记录测试命令、MySQL 版本和结果。
- [ ] 输出 `GO / NO-GO` 和证据 SHA256。
- [ ] 回填 `00-230 execution-plan.md`。

**Validates: Requirements 3.1-3.5**

## 当前状态

- [x] Spec 三件套已创建。
- [ ] 实施未开始。
