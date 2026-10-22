# 00-234 隔离测试环境基础设施 - 任务拆解

> 执行记录：`execution.md`（2026-08-27，当前 `INFRA_READY`）

## T1 DNS、TLS 与微信域名

- [x] 配置两个测试域名 DNS。
- [x] 签发并安装测试域名证书。
- [ ] 配置微信 request/upload/download 合法域名。
- [x] 从公网验证解析和 TLS。

**Validates: Requirements 3.1**

执行入口：`scripts/provision-test-environment.sh`。证书申请只在测试 SAN（`test-api.kplyyk.com`、`test.kplyyk.com`）范围内进行；缺少 root 或 certbot 时 fail-closed。

## T2 测试配置与容器

- [x] 修正 test Nacos dataId 指向 `kaipai_test`，并隔离 Redis index / COS bucket code。
- [x] 配置 `test + Nacos + 18080` 容器。
- [x] 增加启动前 DB/Redis/COS 环境目标检查。
- [x] 证明生产容器未重建、未停机。

执行入口：`scripts/provision-test-environment.sh`。脚本固定使用 `kaipai-backend-test:18080`、`kaipai_test`、Redis DB `1`、COS `kaipai-test`，并在前后回读正式容器 ID/status。

**Validates: Requirements 3.2, 3.3**

## T3 外部能力隔离

- [x] 配置独立 Redis DB。
- [x] 配置独立 test private bucket并执行探针。
- [x] 固化短信/实名/AI/DeepSeek/回调策略。
- [x] 验证缺配置时不回退 prod provider。

**Validates: Requirements 3.3, 3.4**

## T4 Nginx、管理端和测试小程序

- [x] 配置 test API upstream 和 html-test。
- [x] 通过 `nginx -t` 后 reload。
- [x] 部署测试管理端。
- [x] 生成并扫描 test 小程序产物。

执行入口：`scripts/provision-test-environment.sh`；测试侧回滚入口：`scripts/rollback-test-environment.sh`。

**Validates: Requirements 3.1, 3.5**

## T5 阶段签收

- [x] 运行不带 `--allow-fail` 的双环境 preflight。
- [x] 运行不带 `--allow-fail` 的标准双环境 preflight；DNS/Nacos/DB 基础门禁通过，但它不覆盖 TLS/容器运行态。
- [x] 保存隔离矩阵和证据 SHA256。
- [x] 在完整运行态门禁通过后标记当前阶段为 `INFRA_READY`。
- [x] 回填 `00-230 execution-plan.md`。

**Validates: Requirements 3.6**

## 当前状态

- [x] Spec 三件套已创建。
- [x] DNS 和测试 Nacos 隔离已实施并留档。
- [x] 测试环境 root 级 provision/rollback 入口已固化并完成远端实施与回读。
- [x] TLS、测试后端容器、测试 Nginx 和 `html-test` 已完成。
- [ ] 微信公众平台 request/upload/download 合法域名需由平台账号侧人工复核；不阻断当前固定 DevTools 工程的人工测试。
