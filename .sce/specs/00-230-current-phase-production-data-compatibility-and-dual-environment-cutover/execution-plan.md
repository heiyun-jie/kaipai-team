# 00-230 双环境发布总控执行矩阵

> 本文件是 `00-230` 的阶段状态板。阶段必须按顺序推进，后一个阶段不得在前一个阶段没有证据和签收时开始。
>
> 当前状态：`00-236 READY / AWAITING_MANUAL_ACCEPTANCE`。测试环境和生产副本兼容门禁已通过；正式发布仍未授权，现有生产持续运行。

## 1. 阶段顺序

```text
00-231 候选冻结与运维安全
    ↓
00-232 Schema 迁移安全
    ↓
00-233 历史媒体兼容工具
    ↓
00-234 隔离测试基础设施
    ↓
00-235 生产副本测试库
    ↓
00-236 人工验收 GO
    ↓
00-237 正式迁移与原子切流
    ↓
00-238 发布后观察与旧运行时退场
```

## 2. 阶段矩阵

| 阶段 | 输入门禁 | 主要动作 | 必须输出 | GO 条件 | 当前 |
|---|---|---|---|---|---|
| `00-231` | 代码/迁移工作树可盘点 | 冻结候选、manifest、helper 安全和凭据风险 | candidate manifest + SHA256 | 候选可复现、脱敏通过、风险已处置 | `PASSED` |
| `00-232` | 00-231 manifest | migration checksum、preflight、partial 修复、MySQL 8 演练 | migration safety evidence | 14 文件首次/重复/partial 场景明确 | `PASSED` |
| `00-233` | 00-231 工具版本、00-232 Schema | 历史 URL dry-run/apply、对象复制、关系回填 | media migration report | 所有可读历史媒体 linked，重跑幂等 | `PASSED` |
| `00-234` | 00-231 配置候选 | DNS/TLS/Nacos/容器/Redis/COS/外部能力隔离 | infra matrix | test/prod 目标无重叠，`INFRA_READY` | `PASSED / INFRA_READY` |
| `00-235` | 00-234 INFRA_READY | 备份、重建 test、迁移、回填、数据断言、API smoke | test-copy evidence bundle | `TEST_DATA_READY` | `PASSED / TEST_DATA_READY` |
| `00-236` | 00-235 TEST_DATA_READY | 历史/新账号、后台、分享和小程序人工核验 | manual acceptance record | 用户明确签署 `GO` | `READY / AWAITING_MANUAL_ACCEPTANCE` |
| `00-237` | 00-236 GO | prod 备份、同批迁移、候选后端、Nginx 切流、小程序 release | production cutover bundle | `CUTOVER_OK` | `LOCKED / PENDING` |
| `00-238` | 00-237 CUTOVER_OK | 观察、回归、异常回切、旧容器退场 | post-release record | `STABLE` 或有记录的 `ROLLED_BACK` | `PENDING` |

## 3. 状态流转规则

允许状态：

```text
PENDING -> IN_PROGRESS -> PASSED -> SIGNED
                      \-> FAILED
                      \-> BLOCKED
```

- `PASSED`：自动证据已通过。
- `SIGNED`：责任人/用户已明确签收，可解锁下游。
- `FAILED`：存在需要修复的失败，不得下游推进。
- `BLOCKED`：缺少外部前置或授权，不代表通过。

候选 hash、migration hash、目标环境或回填工具变化时，当前阶段及所有下游阶段自动回到 `PENDING`。

## 4. 证据命名

所有证据按以下规则命名：

```text
<candidate-id>/<phase-id>/<timestamp>-<evidence-name>.(json|md|txt|sha256)
```

证据必须：

- 引用 candidateId 和 manifest SHA256。
- 记录命令/脚本版本和环境名。
- 只写脱敏聚合数据。
- 生成 SHA256，并在阶段记录中回填。

## 5. 阶段签收模板

每阶段完成时补充：

```text
Phase: 00-23X
Candidate: <candidate-id>
Status: PASSED / FAILED / BLOCKED
Evidence: <path>
Evidence SHA256: <hash>
Owner: <operator alias>
Decision: GO / NO-GO / AWAITING_APPROVAL
Notes: <no secrets, no PII>
```

## 6. 当前门禁

- 当前候选：`20260826-1625-v3-draft`；manifest SHA256 为 `7282a9bb75e8d05d80b299e91a96dfa8735854220b8ab48246f95937bc19b9a1`。
- 测试环境：`test-api.kplyyk.com` / `test.kplyyk.com`、`kaipai-backend-test:18080`、`kaipai_test`、Redis DB `1`、测试 COS 均已启用并通过门禁。
- 正式环境：`kaipai-backend:8080` 持续运行，未停止、未重建、未迁移；正式 API smoke 为 `HTTP 200`。
- 数据兼容：58 个历史媒体完成测试桶回填，幂等重跑新建数为 0，旧 URL 哈希不变，孤儿素材为 0。
- 固定微信开发者工具工程已经切到冻结 test 产物；当前工具会话要求重新登录后才能继续模拟器人工验收。
- 唯一解锁条件是用户完成 `00-236` 人工验收并明确签署 `GO`。在此之前 `00-237` 保持锁定，不执行生产迁移、切流或正式小程序发布。
- 统一证据：`.sce/evidence/20260827-test-full-access/VERIFICATION.txt`。
