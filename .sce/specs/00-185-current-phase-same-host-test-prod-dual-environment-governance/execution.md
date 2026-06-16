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

## 6. 2026-06-16 继续推进记录

### 6.1 重新核验

- 正式域名仍已解析：
  - `api.kplyyk.com -> 101.43.57.62`
  - `kplyyk.com -> 101.43.57.62`
- 测试域名仍未解析：
  - `test-api.kplyyk.com` 未返回公网 A 记录。
  - `test.kplyyk.com` 未返回公网 A 记录。
- Nacos 只读核验：
  - `kaipai-backend-prod.yml` 返回 HTTP 200，包含 Spring / datasource / redis 配置。
  - `kaipai-backend-test.yml` 当前不可读或不存在，未证明可用。
- 远端普通 `sudo docker` 不可直接执行，必须继续通过标准 release helper。

### 6.2 已执行 dry-run

已执行生产 env 同步 dry-run：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-compose-env-sync.py --label dual-env-prod-env-dry-run --set SPRING_PROFILES_ACTIVE=prod --set NACOS_ENABLED=true --dry-run
```

结果：

- SSH key auth 可用。
- release helper / sudoers 可用。
- 当前 compose 可读。
- dry-run 候选显示会把当前单后端服务从：
  - `SPRING_PROFILES_ACTIVE=dev` 改为 `prod`
  - `NACOS_ENABLED=false` 改为 `true`

该 dry-run 只验证“把现有单后端服务切成 prod”的可行性，不会创建测试环境，也不会保留当前测试运行态。

### 6.3 安全处理

`run-backend-compose-env-sync.py --dry-run` 会在 `tmp/backend-compose-env-sync/` 生成完整候选 compose。该候选文件包含远端敏感环境变量，已在本地删除，只保留不含密钥的 dry-run 记录摘要。

### 6.4 当前阻断

继续执行真实远端变更仍然阻断，原因：

1. 测试域名未解析，无法完成公网 smoke。
2. `kaipai-backend-test.yml` 未就绪，测试后端没有独立配置源。
3. 当前只有单后端服务；真实执行 prod env sync 会把现有运行态切成生产，不能保留测试环境。
4. 当前发布 helper 没有“新增第二套后端服务 + 测试 Nginx + 测试静态目录”的一键安全入口。

### 6.5 下一步断点

继续落地前必须完成以下外部 / 基础设施前置：

1. DNS 增加 A 记录：
   - `test-api.kplyyk.com -> 101.43.57.62`
   - `test.kplyyk.com -> 101.43.57.62`
2. Nacos 创建并核验：
   - `kaipai-backend-test.yml`
3. 数据库隔离确认：
   - `kaipai_test`
   - `kaipai_prod`
4. 新增受控脚本或 helper 能力：
   - 生成测试后端 compose service
   - 生成测试 Nginx server block
   - 创建 `/opt/kaipai/nginx/html-test`
   - 默认脱敏诊断输出

在上述前置未完成前，不执行生产切换。

## 7. 2026-06-16 DNS 增加尝试与权限结论

### 7.1 已执行核验

- 已确认正式域名权威 NS：
  - `dns23.hichina.com`
  - `dns24.hichina.com`
- 已确认测试域名当前仍未解析：
  - `test-api.kplyyk.com` 无 A 记录。
  - `test.kplyyk.com` 无 A 记录。
- 已确认当前不存在可用通配解析，随机子域名未解析。
- 已用本机腾讯云 API 凭据尝试 DNSPod dry-run，返回结论为该账号下不存在或无权操作 `kplyyk.com`。
- 已检查本机阿里云相关权限入口：
  - 未发现 `aliyun` CLI。
  - 未发现阿里云 CLI 配置目录。
  - 未发现 `ALIBABA_CLOUD_ACCESS_KEY_ID / ALIBABA_CLOUD_ACCESS_KEY_SECRET` 或兼容环境变量。

### 7.2 已补工具

新增阿里云云解析同步脚本：

```text
.sce/runbooks/backend-admin-release/scripts/sync-aliyun-alidns-records.py
```

脚本行为：

- 从环境变量读取阿里云 AK，不保存密钥。
- 支持 dry-run。
- 先查现有记录，缺失时新增。
- 同名 A 记录存在但目标 IP 不一致时中止，避免误覆盖。

目标执行命令：

```powershell
python .sce/runbooks/backend-admin-release/scripts/sync-aliyun-alidns-records.py `
  --domain kplyyk.com `
  --record test-api=101.43.57.62 `
  --record test=101.43.57.62 `
  --dry-run `
  --json
```

真实新增命令：

```powershell
python .sce/runbooks/backend-admin-release/scripts/sync-aliyun-alidns-records.py `
  --domain kplyyk.com `
  --record test-api=101.43.57.62 `
  --record test=101.43.57.62 `
  --json
```

### 7.3 当前结论

本轮不能直接新增测试域名 DNS，原因不是缺少服务器权限，而是 `kplyyk.com` 的权威 DNS 在阿里云，当前本机没有阿里云云解析 API 权限。

继续推进 DNS 需要满足以下任一条件：

1. 在当前 shell 设置阿里云 DNS 可用 AK：
   - `ALIBABA_CLOUD_ACCESS_KEY_ID`
   - `ALIBABA_CLOUD_ACCESS_KEY_SECRET`
2. 用户登录阿里云控制台并手工新增：
   - `test-api.kplyyk.com A 101.43.57.62`
   - `test.kplyyk.com A 101.43.57.62`

DNS 未完成前，继续阻断公网测试环境 smoke，不进入生产切换。

## 8. 2026-06-16 数据库隔离只读核验

### 8.1 已执行核验

通过远端 release helper 的 `--mysql-validation` 只读执行 `SELECT DATABASE()`，未使用普通 `docker` 权限，未输出数据库密码。

结果：

- `kaipai_dev`：存在。
- `kaipai_test`：不存在或当前 helper 无法连接。
- `kaipai_prod`：不存在或当前 helper 无法连接。

同时确认：

- 远端普通用户无 Docker socket 权限。
- `sudo -n docker` 需要密码，不在当前 sudoers 范围。
- 后续数据库操作仍必须通过标准 release helper 或新增受控 helper 能力完成。

### 8.2 Schema 初始化判断

当前后端未接入 Flyway / Liquibase 运行时自动迁移。

`kaipaile-server/src/main/resources/db/migration/README.md` 明确当前迁移策略为手动按文件顺序执行；但首个 baseline 脚本 `V20260331_001__platform_admin_baseline.sql` 以 `ALTER TABLE user` / `ALTER TABLE actor_profile` 开始，说明它依赖更早的基础业务表已存在，不是完整空库初始化脚本。

因此：

- 不能只创建空的 `kaipai_test` / `kaipai_prod` 后直接认为环境可用。
- 不能直接把 `kaipai_dev` 全量数据复制到 `kaipai_prod`，否则会把测试 / 历史验证数据带入生产。
- 需要新增独立 schema/data 初始化批次：
  - 测试库可从当前验证库复制脱敏或可接受的验证数据。
  - 生产库只导入必要系统表、角色、权限、模板等种子数据。
  - 初始化后再执行后续增量迁移并进行后端 smoke。

### 8.3 当前阻断更新

除 DNS 外，数据库层也尚未满足同机双环境前置：

1. `kaipai_test` 尚未就绪。
2. `kaipai_prod` 尚未就绪。
3. 当前迁移脚本不足以直接初始化空库。

在数据库初始化方案未明确前，不执行测试后端容器创建和生产切换。

## 9. 2026-06-16 标准预检脚本与最新门禁结果

### 9.1 已补工具

新增同机双环境标准预检脚本：

```text
.sce/runbooks/backend-admin-release/scripts/check-dual-env-preflight.py
```

新增单元测试：

```text
.sce/runbooks/backend-admin-release/scripts/tests/test_check_dual_env_preflight.py
```

脚本能力：

- DNS：检查 `test-api.kplyyk.com` / `test.kplyyk.com` 是否解析到 `101.43.57.62`。
- Remote：检查 SSH key auth 与 release helper healthcheck。
- Nacos：通过 release helper 只读导出目标 dataId，在内存中做脱敏摘要，不落原始配置文件。
- Database：通过 release helper 的 MySQL validation 执行只读 `SELECT DATABASE()`，检查目标库是否可连接。
- Schema：通过 `information_schema.tables` 检查核心表是否齐全，避免空库被误判为可发布。

验证：

- 已先写测试并确认因目标脚本不存在失败。
- 实现后执行：

```powershell
python -m unittest discover -s .sce/runbooks/backend-admin-release/scripts/tests -p test_check_dual_env_preflight.py
```

结果：`Ran 3 tests ... OK`

### 9.2 最新预检结果

命令：

```powershell
python .sce/runbooks/backend-admin-release/scripts/check-dual-env-preflight.py --allow-fail
```

脱敏结论：

- 总体：`passed=false`
- DNS：
  - `test-api.kplyyk.com` 未解析。
  - `test.kplyyk.com` 未解析。
- Remote：
  - SSH key auth 可用。
  - release helper healthcheck 通过。
- Nacos：
  - `kaipai-backend-test.yml` 可读但未包含 `spring / datasource / redis` 关键片段，也未指向 `kaipai_test`。
  - `kaipai-backend-prod.yml` 可读，包含 `spring / datasource / redis` 关键片段，并指向 `kaipai_prod`。
- Database：
  - `kaipai_test` 不存在或当前 helper 无法连接，核心表门禁 `0/6`。
  - `kaipai_prod` 不存在或当前 helper 无法连接，核心表门禁 `0/6`。
  - 当前核心表门禁：
    - `user`
    - `actor_profile`
    - `admin_user`
    - `admin_role`
    - `card_scene_template`
    - `identity_verification`

### 9.3 当前推进边界

当前可进入下一步的部分：

- 生产 Nacos dataId 基本就绪。
- 远端标准 helper 通道可用。
- 预检脚本已能稳定输出门禁状态。

当前仍阻断的部分：

1. 测试域名 DNS 仍需阿里云云解析权限或手工新增。
2. `kaipai-backend-test.yml` 需要创建并明确指向 `kaipai_test`。
3. `kaipai_test` / `kaipai_prod` 数据库需要按受控初始化批次创建和填充必要 schema / seed。
4. 数据库初始化策略必须先区分测试数据与生产种子数据，不能把 `kaipai_dev` 全量复制到生产。

## 10. 2026-06-16 空数据库创建

### 10.1 已执行动作

通过远端 release helper 执行空库创建：

```sql
CREATE DATABASE IF NOT EXISTS `kaipai_test` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE IF NOT EXISTS `kaipai_prod` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
```

执行边界：

- 未修改 `kaipai_dev` 现有表结构。
- 未复制 `kaipai_dev` 数据。
- 未初始化 schema。
- 未切换后端容器、Nacos 或 Nginx。

运维记录：

```text
.sce/runbooks/backend-admin-release/records/20260616-235250-dual-env-empty-databases.md
```

### 10.2 创建后预检

命令：

```powershell
python .sce/runbooks/backend-admin-release/scripts/check-dual-env-preflight.py --allow-fail
```

脱敏结论：

- 总体：`passed=false`
- DNS：
  - `test-api.kplyyk.com` 未解析。
  - `test.kplyyk.com` 未解析。
- Nacos：
  - `kaipai-backend-test.yml` 仍未通过测试配置门禁。
  - `kaipai-backend-prod.yml` 仍通过生产配置门禁。
- Database：
  - `kaipai_test` 已存在，核心表门禁 `0/6`。
  - `kaipai_prod` 已存在，核心表门禁 `0/6`。

### 10.3 当前阻断更新

空库创建只解除“数据库不存在”这一层阻断，不解除发布阻断。

继续推进必须完成：

1. 阿里云 DNS 新增测试域名解析。
2. 创建并核验 `kaipai-backend-test.yml`。
3. 为 `kaipai_test` / `kaipai_prod` 初始化 schema。
4. 为生产库导入必要系统种子数据，不导入测试业务数据。

## 11. 2026-06-16 测试 Nacos dataId 创建

### 11.1 已执行动作

通过 release helper 完成 `kaipai-backend-test.yml` 发布：

- 发布批次：`20260616-235638-backend-nacos-dual-env-test`
- 来源：只读导出 `kaipai-backend-prod.yml`
- 变更：仅将数据库标记从 `kaipai_prod` 替换为 `kaipai_test`
- 目标 dataId：`kaipai-backend-test.yml`
- 未修改：`kaipai-backend-prod.yml`
- 未切换：后端容器 / Nginx / DNS

安全处理：

- 未在本地记录 Nacos 原文。
- 未在终端输出 Nacos 原文。
- 临时上传目录已清理。

风险说明：

- 该 test dataId 解决了“测试 Nacos 缺失”问题。
- 该 test dataId 仍可能继承 prod 外部资源配置，例如 COS、短信、微信、AI provider 等。
- 后续测试容器真正启动前，仍需补外部资源隔离策略或明确接受测试环境复用生产外部资源的边界。

### 11.2 发布后预检

命令：

```powershell
python .sce/runbooks/backend-admin-release/scripts/check-dual-env-preflight.py --allow-fail
```

脱敏结论：

- 总体：`passed=false`
- DNS：
  - `test-api.kplyyk.com` 未解析。
  - `test.kplyyk.com` 未解析。
- Nacos：
  - `kaipai-backend-test.yml` 通过摘要门禁，包含 `spring / datasource / redis`，并指向 `kaipai_test`。
  - `kaipai-backend-prod.yml` 通过摘要门禁，包含 `spring / datasource / redis`，并指向 `kaipai_prod`。
- Database：
  - `kaipai_test` 已存在，核心表门禁 `0/6`。
  - `kaipai_prod` 已存在，核心表门禁 `0/6`。

### 11.3 当前阻断更新

已解除：

1. 测试 Nacos dataId 缺失。
2. 测试 / 生产数据库不存在。

仍阻断：

1. 阿里云 DNS 未新增测试域名解析。
2. `kaipai_test` / `kaipai_prod` schema 未初始化。
3. 测试 Nacos 外部资源隔离尚未最终确认。

## 13. 2026-06-17 最小系统 seed 同步

### 13.1 已执行动作

通过 release helper 将当前运行库 `kaipai_dev` 的最小系统 seed 同步到 `kaipai_test` 和 `kaipai_prod`：

- `admin_role`
- `admin_user`
- `admin_user_role`
- `card_scene_template`

执行方式：

- `INSERT IGNORE INTO target.table SELECT * FROM kaipai_dev.table ...`
- 只复制后台登录、角色授权与模板配置相关系统数据。
- 未复制演员、用户、订单、审核、支付、分享卡等业务数据。
- 未输出后台账号密码 hash。
- 未切换任何运行服务。

### 13.2 seed 后预检

命令：

```powershell
python .sce/runbooks/backend-admin-release/scripts/check-dual-env-preflight.py --allow-fail
```

脱敏结论：

- 总体：`passed=false`
- DNS：
  - `test-api.kplyyk.com` 未解析。
  - `test.kplyyk.com` 未解析。
- Nacos：
  - `kaipai-backend-test.yml` 通过。
  - `kaipai-backend-prod.yml` 通过。
- Database：
  - `kaipai_test`：`exists=true`，`schemaReady=true`，`seedReady=true`
  - `kaipai_prod`：`exists=true`，`schemaReady=true`，`seedReady=true`

### 13.3 当前阻断更新

已解除：

1. 测试 / 生产数据库 schema 缺失。
2. 后台最小登录 seed 缺失。
3. 测试 / 生产 Nacos dataId 摘要门禁。

仍阻断：

1. 阿里云 DNS 未新增测试域名解析。
2. 测试 Nacos 外部资源隔离尚未最终确认。
3. 测试后端容器、测试 Nginx server block 和测试管理端静态目录尚未创建。

## 12. 2026-06-17 Schema-only 初始化与 seed 门禁

### 12.1 基础 schema 来源核验

已检查仓库中现有 SQL：

- `.sce/specs/00-10-platform-admin-backend-architecture/mysql-ddl-v1.sql`
- `kaipaile-server/src/main/resources/db/migration/*.sql`
- timeline snapshot 中的 `kaipai_dev-local-full.sql`

结论：

- `mysql-ddl-v1.sql` 和当前 migration 不是完整空库初始化基线，仍依赖更早基础表。
- timeline snapshot 的 `kaipai_dev-local-full.sql` 含历史数据与验收用户，不适合直接导入生产。
- 最安全的当前方案是基于远端现有 `kaipai_dev` 做 schema-only 克隆，不复制行数据。

### 12.2 已执行 schema-only 克隆

先通过 release helper 查询 `kaipai_dev` 非备份业务表：

- 表数量：`40`
- 排除：`zz_%` 备份表

随后执行：

```sql
CREATE TABLE IF NOT EXISTS `kaipai_test`.`<table>` LIKE `kaipai_dev`.`<table>`;
CREATE TABLE IF NOT EXISTS `kaipai_prod`.`<table>` LIKE `kaipai_dev`.`<table>`;
```

执行边界：

- 未复制 `kaipai_dev` 业务数据。
- 未导入 timeline dump。
- 未切换服务。
- 未修改 Nginx / DNS。

### 12.3 预检脚本增强

`check-dual-env-preflight.py` 已新增 seed 门禁：

- `admin_user`
- `admin_role`
- `admin_user_role`

单元测试：

```powershell
python -m unittest discover -s .sce/runbooks/backend-admin-release/scripts/tests -p test_check_dual_env_preflight.py
```

结果：`Ran 5 tests ... OK`

### 12.4 Schema 克隆后预检

命令：

```powershell
python .sce/runbooks/backend-admin-release/scripts/check-dual-env-preflight.py --allow-fail
```

脱敏结论：

- 总体：`passed=false`
- DNS：测试域名仍未解析。
- Nacos：test / prod dataId 均通过摘要门禁。
- Database：
  - `kaipai_test`：`exists=true`，`schemaReady=true`，`seedReady=false`
  - `kaipai_prod`：`exists=true`，`schemaReady=true`，`seedReady=false`

### 12.5 当前阻断更新

已解除：

1. 测试 / 生产数据库不存在。
2. 测试 / 生产核心表结构缺失。
3. 测试 Nacos dataId 缺失。

仍阻断：

1. 测试域名 DNS 未解析。
2. 后台最小登录种子未初始化。
3. 测试 Nacos 外部资源隔离尚未最终确认。
