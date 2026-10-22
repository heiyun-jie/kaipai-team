# 00-231 发布候选冻结与运维安全前置 - 技术设计

_Requirements: 3.1-3.5, 4, 5_

## 1. 候选状态机

```text
DRAFT -> FROZEN -> CONSUMED
   |        |
   +------> INVALIDATED
```

- `DRAFT`：清单生成中，不能部署。
- `FROZEN`：全部哈希已记录并通过安全门禁。
- `CONSUMED`：已被测试副本验证或生产发布引用。
- `INVALIDATED`：任一代码、迁移、配置模板或 overlay 变化。

状态只前进，不把失效候选重新改回冻结态。

## 2. 候选 Manifest

建议记录路径：

```text
.sce/runbooks/backend-admin-release/records/<candidate-id>/candidate-manifest.json
```

最小结构：

```json
{
  "candidateId": "YYYYMMDD-HHMM-v3",
  "createdAt": "ISO-8601",
  "repositories": [],
  "overlays": [],
  "migrations": [],
  "artifacts": [],
  "testApiBaseUrl": "https://test-api.kplyyk.com",
  "releaseApiBaseUrl": "https://api.kplyyk.com",
  "securityGate": {},
  "status": "FROZEN"
}
```

`repositories` 记录仓库名、commit、branch、dirty 状态；存在脏改时必须由 `overlays` 完整解释。Manifest 本身生成 SHA256，所有下游记录只引用 candidateId + manifest SHA256。

## 3. 迁移清单

迁移清单必须精确包含 `00-230 design §3.2` 的 14 个文件，不从目录通配符自动扩大批次。每项记录：

- 序号。
- 文件名。
- SHA256。
- Git tracked 状态。
- 所属后端 commit 或 overlay。

出现额外 migration 文件时不自动加入；先判断是否属于本候选，再重新冻结。

## 4. 构建可复现证明

- 后端：从 commit + overlay 临时快照构建，不直接把未声明脏改打入 JAR。
- 管理端：记录 lockfile 和静态文件清单哈希。
- 小程序：test 和 release 使用同一代码候选，只改变显式 API Base URL；产物分别扫描，不允许 test/local URL 进入 release。
- 二次构建的关键产物哈希不同，需要先解释时间戳或非确定性来源，不能直接宣称可复现。
- uni-app 会把快照绝对路径混入部分 `u-i` 组件实例前缀；候选构建必须在安全的 `ArtifactOnly` 后处理中按 WXML 相对路径稳定化该 8 位前缀，并同时更新同页 WXML/JS。不得借此改写业务字段、scopeId 或组件序号。
- 可复现验收必须至少使用两个不同快照根目录构建；JAR 文件 SHA256、后台/小程序目录树 SHA256 均一致后才能通过。

### 4.1 生产依赖审计判定

- 管理端是浏览器运行时，`npm audit --omit=dev` 的 high/critical 必须为 0；不得仅凭“前端风险较低”接受可修复告警。
- 小程序的 uni-app 多平台包把 Vite、esbuild、Jimp、ZIP、WebSocket 等本地编译能力声明在 production 依赖树中，原始告警数量不能直接等同于客户端漏洞数量。
- 小程序剩余告警仅在以下条件同时成立时可判定 `CONTROLLED_BUILD_TOOLCHAIN_ONLY`：告警叶子包属于本 Spec 已复核集合；发布运行时 `vue-i18n` 和其 `@intlify/core-base` 不低于 `9.14.5`；最终包不含 `.map`、Node 包清单、`node_modules` 路径或已知工具链标记；critical 为 0。
- 该例外必须输出 `RISK_ACCEPTED_WITH_EXPIRY`、到期时间和操作约束。任何未知 advisory、依赖输入变化、过期或产物可达性证明失败均恢复 `REVIEW_REQUIRED / NO-GO`。

## 5. Helper 安全门禁

本地先执行：

```powershell
python .sce/runbooks/backend-admin-release/scripts/tests/test_backend_runtime_diagnostics.py
```

通过后，远端同步仍需用户授权：

```powershell
python .sce/runbooks/backend-admin-release/scripts/sync-release-helper-baseline.py --operator <name>
```

同步器不得在仓库内保留主机、用户或密码回退。连接信息由 `KAIPAI_RELEASE_HOST`、`KAIPAI_RELEASE_USER`、`KAIPAI_RELEASE_PASSWORD` 显式注入；远端主机密钥必须先写入并人工核验 `KAIPAI_RELEASE_KNOWN_HOSTS_FILE`（默认 `~/.ssh/known_hosts`）。缺少任一连接输入、缺少 known_hosts 文件或主机密钥未知时，必须在生成 key、连接网络或写入远端前失败。

同步后只允许回读安全字段：profile、Nacos enabled、server port、目标 schema 标识。任何未知字段值必须显示 `[REDACTED]`。

## 6. 凭据风险登记

只登记凭据类别、影响环境、owner、轮换状态和验证结果，不登记秘密。至少评估：

- 数据库账号。
- Nacos 账号。
- 腾讯云/COS 密钥。
- 微信 AppSecret。
- 短信、实名和 AI provider Token。
- 后台 smoke 账号凭据。

高风险凭据状态仅允许 `ROTATED`、`ROTATION_SCHEDULED`、`RISK_ACCEPTED_WITH_EXPIRY`；第三种必须有明确失效时间，不能无限期接受。

## 7. 门禁输出

`GO` 必须同时满足：

1. 候选代码和 overlay 完整。
2. 14 个迁移全部 tracked 且哈希固定。
3. test/release API 目标可证明。
4. helper 脱敏测试通过，远端旧 helper 不再被使用。
5. 凭据风险已有可审计处置。

任一失败输出 `NO-GO`，下游 `00-235` 和 `00-237` 不接受口头豁免。

## 8. 回滚边界

本阶段不触碰业务运行态。撤销候选仅将 manifest 标为 `INVALIDATED`，不删除代码、构建产物或用户工作树。
