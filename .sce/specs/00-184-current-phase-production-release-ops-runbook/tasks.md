# 00-184 当前阶段生产环境发布运维流程 - 任务拆解

## 任务列表

### T1 新增生产发布运维文档
**Validates: Requirements 3.1, 3.3**

- [x] 新增 `production-release-runbook.md`。
- [x] 覆盖后端生产发布流程。
- [x] 覆盖管理端生产发布流程。
- [x] 覆盖联合发布、smoke、回滚与记录。
- [x] 明确不新增真实密钥。

### T2 登记入口
**Validates: Requirements 3.2**

- [x] 更新 `.sce/runbooks/backend-admin-release/README.md`。
- [x] 更新 `.sce/specs/README.md`。

### T3 验证与记录
**Validates: Requirements 3.1, 3.2, 3.3**

- [x] 静态检查文档存在。
- [x] 静态检查索引登记。
- [x] 静态检查敏感值表达。
- [x] 回填 `execution.md`。

## 追溯

- T1 -> requirements.md 3.1, 3.3 / design.md §2, §3
- T2 -> requirements.md 3.2 / design.md §1
- T3 -> requirements.md 3.1, 3.2, 3.3 / design.md §4
