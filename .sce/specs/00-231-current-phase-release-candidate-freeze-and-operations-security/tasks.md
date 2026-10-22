# 00-231 发布候选冻结与运维安全前置 - 任务拆解

## T1 候选盘点

- [x] 记录四个仓库/项目的 commit、branch 和工作树状态。
- [x] 明确全部 overlay 路径及 SHA256。
- [x] 确认 `V20260818_001` 已被 Git 跟踪；SQL 与对应 MySQL 8 迁移测试均已加入后端 Git 索引。

**Validates: Requirements 3.1**

## T2 Manifest 与产物

- [x] 生成候选号和 `DRAFT` candidate manifest。
- [x] 写入 14 个迁移的固定顺序与 SHA256。
- [x] 从 commit + manifest overlay 隔离快照构建并记录 JAR、管理端、小程序 test/release 产物。
- [x] 从小程序运行产物扫描并证明 test/release API Base URL，且双方均不含另一环境或本地 Base URL。
- [x] 完成生产依赖兼容性评估：管理端运行时告警修复为 0；小程序运行时/构建链分层并固化过期门禁。

**Validates: Requirements 3.2**

## T3 运维安全

- [x] 运行 helper 脱敏测试（本地 `10/10` 通过）。
- [x] 移除 helper 同步器中的连接信息回退，缺参或未固定远端主机密钥时 fail closed。
- [x] 固化本地 T3 证据：`execution/t3-local-helper-safety-evidence.json`，明确未执行远端操作。
- [ ] 经授权后同步远端 helper。
- [ ] 验证远端诊断只输出安全字段。
- [ ] 检查记录目录不存在新泄露内容。

**Validates: Requirements 3.3**

## T4 凭据风险

- [x] 建立不含秘密的凭据类别清单：`execution/credential-risk-register.json`。
- [x] 为每类凭据记录轮换/接受风险结论；当前未执行轮换，生产切流保持阻断。
- [x] 固化 T4 本地证据：`execution/t4-credential-risk-evidence.json`，包含 fail-closed dry-run 和线上无变更证明。
- [ ] 经授权执行必要轮换并在测试环境验证。

**Validates: Requirements 3.4**

## T5 阶段签收

- [x] 计算 `DRAFT` manifest SHA256；正式冻结后必须重新计算。
- [x] 当前输出 `NO-GO`。
- [x] 在 `00-230 execution-plan.md` 回填候选号、证据路径和状态。

**Validates: Requirements 3.5**

## 当前状态

- [x] Spec 三件套已创建。
- [x] 候选清单生成器与单元测试已创建，固定迁移顺序、未跟踪迁移阻断和删除 overlay 哈希均已覆盖。
- [ ] `20260825-1915-v3-draft`、`20260826-1535-v3-draft`、`20260826-1545-v3-draft`、`20260826-1610-v3-draft`、`20260826-1615-v3-draft` 与 `20260826-1620-v3-draft` 已因后续安全/状态文档变化失效；当前批次使用新候选号 `20260826-1625-v3-draft`，禁止继续引用旧 manifest。
- [x] `ActorCardMediaBindingSchemaMigrationTest` 已在 MySQL 8.0.36 容器通过，结果为 2 tests / 0 failures / 0 errors。
- [x] T2 基线构建已证明 4 类产物可生成，小程序 test/release API 目标扫描均通过，构建未操作 DevTools 或线上运行态。
- [x] 小程序绝对快照路径导致的 `u-i` 非确定性已按相对 WXML 路径稳定化，T2 使用两个不同快照根目录复核四类产物哈希。
- [x] 生产依赖审计已完成：后台由 `7` 项收敛为 production `0`；小程序原始 `48` 项均归属于已复核构建链，发布运行时 i18n 为 `9.14.5`，326 个产物文件无 source map、Node 包清单或工具链标记，构建链风险接受至 `2026-09-30T23:59:59+08:00`。
- [x] `20260825-1900-v3-draft` 的两条独立路径曾证明四类产物哈希一致，但候选随后因状态文档变化失效；`1915` 的最终 manifest SHA256 只记录在候选记录目录，避免签收回填再次改变候选输入。
- [x] 完成生产目标只读解析：`api.kplyyk.com` 当前指向 `101.43.57.62`；`192.168.1.108` 未发现 KaiPai 运行态。证据：`execution/remote-target-resolution-evidence.json`。
- [x] 旧生产主机只读 helper 核对完成：admin helper 哈希匹配，backend helper 哈希不匹配；直接 helper healthcheck 为 `helper-ok`，sudo 门禁仍未验证。证据：候选目录 `remote-helper-readonly-verification.json`。
- [ ] 当前候选 `20260826-1625-v3-draft` 仍为 `DRAFT / NO-GO`：仅剩远端 helper 安全验证和凭据风险处置，依赖审计不再是阻断。
- [ ] 未停止、重启或修改任何线上运行服务；冻结仅针对候选内容。
