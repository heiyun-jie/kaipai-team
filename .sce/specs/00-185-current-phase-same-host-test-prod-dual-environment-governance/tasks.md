# 00-185 当前阶段同机测试 / 生产双环境治理 - 任务拆解

## 任务列表

### T1 固化同机双环境 runbook
**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [x] 新增 `same-host-dual-environment-runbook.md`。
- [x] 写明测试 / 生产目标拓扑。
- [x] 写明测试环境优先保留顺序。
- [x] 写明生产发布顺序。
- [x] 写明 smoke、回滚与发布记录边界。

### T2 更新生产发布入口
**Validates: Requirements 3.2, 3.3**

- [x] 更新 `production-release-runbook.md`，补充生产发布前必须确认测试环境保留。
- [x] 更新 runbook README。
- [x] 更新 SCE README。

### T3 验证与记录
**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [x] 静态检查文档存在。
- [x] 静态检查索引登记。
- [x] 静态检查未新增明文密钥。
- [x] 回填 `execution.md`。

## 追溯

- T1 -> requirements.md 3.1, 3.2, 3.3, 3.4 / design.md §2, §3, §4
- T2 -> requirements.md 3.2, 3.3 / design.md §1, §3
- T3 -> requirements.md 3.1, 3.2, 3.3, 3.4 / design.md §5
