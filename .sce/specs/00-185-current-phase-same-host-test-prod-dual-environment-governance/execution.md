# 00-185 当前阶段同机测试 / 生产双环境治理 - 执行记录

## 1. 改动摘要

- 新增 `.sce/runbooks/backend-admin-release/same-host-dual-environment-runbook.md`
  - 固化同机双环境策略。
  - 生产环境使用 `api.kplyyk.com / kplyyk.com`。
  - 测试环境使用 `test-api.kplyyk.com / test.kplyyk.com`。
  - 明确测试 / 生产容器、端口、Nacos dataId、数据库和静态目录隔离。
- 更新 `.sce/runbooks/backend-admin-release/production-release-runbook.md`
  - 生产发布前新增“测试环境保留”门禁。
  - 测试 smoke 未通过时，不进入生产切换。
- 更新 `.sce/runbooks/backend-admin-release/README.md`
  - 登记 `same-host-dual-environment-runbook.md`。
- 更新 `.sce/specs/README.md`
  - 登记 `00-185 current-phase-same-host-test-prod-dual-environment-governance`。

## 2. 当前假设

- 正式生产域名保留为 `api.kplyyk.com` 与 `kplyyk.com`。
- 测试环境新增域名为 `test-api.kplyyk.com` 与 `test.kplyyk.com`。
- 生产后端保留正式容器名 `kaipai-backend` 与端口 `8080`。
- 测试后端新增容器名 `kaipai-backend-test` 与端口 `18080`。
- 本轮只写治理方案和运维流程，不执行远端修改。

## 3. 验证记录

### 3.1 文档存在性

命令：

```powershell
Test-Path .sce\runbooks\backend-admin-release\same-host-dual-environment-runbook.md
```

结果：`True`

### 3.2 入口登记

命令：

```powershell
Select-String -Path .sce\runbooks\backend-admin-release\README.md -Pattern "same-host-dual-environment-runbook"
Select-String -Path .sce\specs\README.md -Pattern "00-185"
```

结果：

- Runbook README 已登记 `same-host-dual-environment-runbook.md`。
- SCE README 已登记 `00-185`。

### 3.3 敏感值扫描

命令：对新增 runbook 与 `00-185` Spec 执行常见明文密钥模式扫描。

结果：无命中。

## 4. 结论

同机双环境治理方案已落档。下一步若要真实落地，应先执行远端只读盘点，再按 runbook 顺序建立测试环境，测试 smoke 通过后才切生产。

## 5. 2026-06-16 远端只读盘点结果

### 5.1 已执行动作

- 已提交并推送生产发布与同机双环境 runbook：`7a2e9ac docs: add production dual environment release runbooks`。
- 已执行远端 key auth 与 helper healthcheck，只读诊断入口可用。
- 已执行后端运行时只读盘点。
- 已执行 Nacos prod/test dataId 只读盘点。
- 已执行正式 / 测试域名 DNS 本地解析检查。

### 5.2 脱敏结论

- 当前远端后端容器仍为单环境：
  - 容器名：`kaipai-backend`
  - `SERVER_PORT=8080`
  - `SPRING_PROFILES_ACTIVE=dev`
  - `NACOS_ENABLED=false`
- 当前远端 compose 来源仍配置：
  - `SPRING_PROFILES_ACTIVE=dev`
  - `NACOS_ENABLED=false`
  - `SERVER_PORT=8080`
- 当前正式域名解析：
  - `api.kplyyk.com -> 101.43.57.62`
  - `kplyyk.com -> 101.43.57.62`
- 当前测试域名解析：
  - `test-api.kplyyk.com` 未解析到公网 A 记录。
  - `test.kplyyk.com` 未解析到公网 A 记录。
- Nacos 只读盘点：
  - `kaipai-backend-prod.yml` 可访问并包含 Spring 配置片段。
  - `kaipai-backend-test.yml` 未显示有效匹配内容，测试 dataId 尚未证明可用。
  - 当前只读脚本的默认 presence summary 仍按微信键检查，不能等价证明 prod/test 数据源完整性。

### 5.3 阻断判断

第 3 步“先建立并 smoke 测试环境，再切生产”当前不可直接执行，原因：

1. 测试域名 `test-api.kplyyk.com` 与 `test.kplyyk.com` 尚无 DNS 解析，无法完成公网 smoke。
2. 测试 Nacos dataId `kaipai-backend-test.yml` 尚未证明可用。
3. 当前远端只有单后端容器运行态，尚未具备 `kaipai-backend-test` 独立测试容器。
4. 当前远端仍为 `dev + NACOS_ENABLED=false`，直接切生产会覆盖现有测试运行态。

### 5.4 安全处理

原始只读诊断目录包含容器环境变量回读，已删除本地原始诊断目录，只保留本脱敏结论：

- `.sce/runbooks/backend-admin-release/records/diagnostics/20260616-214934-dual-env-precheck`
- `.sce/runbooks/backend-admin-release/records/diagnostics/20260616-214934-dual-env-nacos-precheck`

后续应改造或新增诊断脚本，使环境变量回读默认脱敏后再落盘。
