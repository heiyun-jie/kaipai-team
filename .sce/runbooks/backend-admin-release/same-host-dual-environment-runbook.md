# 同机测试 / 生产双环境治理流程

> 对应 Spec：`00-185 current-phase-same-host-test-prod-dual-environment-governance`
> 适用范围：同一台服务器上保留测试环境并发布生产环境。
> 本文是生产发布前的环境治理流程，不替代 `production-release-runbook.md`。

## 1. 核心策略

采用同机双环境：

- 生产环境承接正式域名：`api.kplyyk.com`、`kplyyk.com`
- 测试环境新增测试域名：`test-api.kplyyk.com`、`test.kplyyk.com`
- 测试与生产使用不同容器、端口、Nacos dataId、数据库和管理端静态目录
- 同一份后端 JAR 多环境复用，运行时通过 `SPRING_PROFILES_ACTIVE` 和 `NACOS_ENABLED` 选择配置

生产发布前必须先让测试环境独立可用；测试环境不可用时，不进入生产切换。

## 2. 目标拓扑

| 项 | 测试环境 | 生产环境 |
|----|----|----|
| API 域名 | `test-api.kplyyk.com` | `api.kplyyk.com` |
| 管理端域名 | `test.kplyyk.com` | `kplyyk.com` |
| 后端 profile | `test` | `prod` |
| Nacos dataId | `kaipai-backend-test.yml` | `kaipai-backend-prod.yml` |
| 后端容器 | `kaipai-backend-test` | `kaipai-backend` |
| 后端内部端口 | `18080` | `8080` |
| 后端运行目录 | `/opt/kaipai/test/backend` 或 compose 内独立挂载 | `/opt/kaipai` |
| 管理端静态目录 | `/opt/kaipai/nginx/html-test` | `/opt/kaipai/nginx/html` |
| 数据库 | `kaipai_test` | `kaipai_prod` |
| Redis | 独立 DB index 或独立实例 | 独立 DB index 或独立实例 |

命名原则：

- 生产环境保留正式名字，避免正式域名和容器语义混乱。
- 测试环境统一追加 `test` 后缀。
- 测试环境不得写入生产数据库。

## 3. 发布前只读盘点

执行任何远端修改前，先盘点并留档：

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-backend-runtime-logs.py --label dual-env-precheck --since 15m
python .sce/runbooks/backend-admin-release/scripts/read-backend-nacos-config.py --label dual-env-nacos-precheck
```

至少确认：

- 当前 compose 中后端服务名、容器名、端口、env。
- 当前 Nginx 的 `api.kplyyk.com` 与 `kplyyk.com` 路由。
- 当前 Nacos 已有哪些 dataId。
- 当前数据库是否已经存在 `kaipai_test` 和 `kaipai_prod`。
- 当前管理端静态目录是否只有一套。

### 3.1 测试域名 DNS 前置

当前 `kplyyk.com` 的权威 NS 为阿里云万网：

```text
dns23.hichina.com
dns24.hichina.com
```

因此测试域名解析必须在阿里云云解析中新增，腾讯云 DNSPod 凭据不能操作该域名。

目标记录：

```text
test-api.kplyyk.com A 101.43.57.62
test.kplyyk.com     A 101.43.57.62
```

若本机已具备阿里云 DNS API 权限，可执行：

```powershell
$env:ALIBABA_CLOUD_ACCESS_KEY_ID="..."
$env:ALIBABA_CLOUD_ACCESS_KEY_SECRET="..."
python .sce/runbooks/backend-admin-release/scripts/sync-aliyun-alidns-records.py `
  --domain kplyyk.com `
  --record test-api=101.43.57.62 `
  --record test=101.43.57.62 `
  --dry-run `
  --json

python .sce/runbooks/backend-admin-release/scripts/sync-aliyun-alidns-records.py `
  --domain kplyyk.com `
  --record test-api=101.43.57.62 `
  --record test=101.43.57.62 `
  --json
```

安全边界：

- 脚本只从环境变量读取 AK，不把密钥写入仓库。
- 脚本先查询现有记录；记录不存在才新增。
- 同名 A 记录已存在但指向不同 IP 时中止，不自动覆盖。
- 新增后必须执行 `Resolve-DnsName test-api.kplyyk.com` 与 `Resolve-DnsName test.kplyyk.com` 验证。

## 4. 先保留测试环境

### 4.1 准备测试 Nacos

目标 dataId：

```text
kaipai-backend-test.yml
```

要求：

- 配置连接 `kaipai_test`，不得连接 `kaipai_prod`。
- Redis 使用测试 DB index 或独立 Redis。
- COS / 短信 / 微信 / AI 等外部资源优先使用测试 bucket、测试回调或明确的测试前缀。
- 不在记录中写明文密钥。

### 4.1.1 准备测试 / 生产数据库

目标数据库：

```text
kaipai_test
kaipai_prod
```

要求：

- 数据库必须存在且互相独立。
- 不得把测试数据直接复制进生产库。
- 不得只创建空库后直接认为环境可用。
- 当前 `db/migration` 不是完整空库初始化基线：早期 baseline 会 `ALTER TABLE user / actor_profile`，依赖更早的基础表已存在。
- 若要从当前 `kaipai_dev` 生成测试 / 生产库，必须单独制定 schema/data 初始化批次：
  - 测试库可按需要复制脱敏或当前验证数据。
  - 生产库只允许导入必要系统种子数据，不导入测试业务数据。
  - 初始化完成后再执行后续增量迁移和 smoke。

### 4.2 准备测试后端

测试后端运行环境：

```text
SPRING_PROFILES_ACTIVE=test
NACOS_ENABLED=true
SERVER_PORT=18080
```

建议 compose 服务：

```text
service: kaipai-test
container_name: kaipai-backend-test
```

要求：

- 测试后端容器与生产后端容器同时存在。
- 测试后端不占用 `8080`。
- 测试后端使用同一份 JAR，但运行时 profile 为 `test`。

### 4.3 准备测试管理端

测试管理端静态目录：

```text
/opt/kaipai/nginx/html-test
```

测试管理端 API 指向：

```text
https://test-api.kplyyk.com
```

要求：

- 测试管理端构建产物与生产管理端构建产物分目录存放。
- 测试域名不复用 `kplyyk.com`。

### 4.4 准备测试 Nginx

目标路由：

```text
test-api.kplyyk.com -> kaipai-backend-test:18080
test.kplyyk.com     -> /opt/kaipai/nginx/html-test
test.kplyyk.com/api -> test-api 或 kaipai-backend-test:18080
```

证书：

- 测试域名必须有对应 HTTPS 证书。
- 若证书未就绪，测试环境只能记为“部署未完成”，不能进入生产发布。

### 4.5 测试环境 smoke

最低 smoke：

```text
GET  https://test-api.kplyyk.com/api/v3/api-docs
POST https://test-api.kplyyk.com/api/admin/auth/login
GET  https://test.kplyyk.com
```

通过条件：

- 测试后端容器稳定运行。
- 测试后端 env 回读为 `SPRING_PROFILES_ACTIVE=test`、`NACOS_ENABLED=true`。
- 测试 API 和测试管理端域名均可访问。
- 测试环境记录已写入 `records/`。

## 5. 再发布生产环境

测试环境 smoke 通过后，按生产发布流程执行：

1. 核验 `kaipai-backend-prod.yml`。
2. 确认生产数据库为 `kaipai_prod`。
3. 确认生产后端 env：
   ```text
   SPRING_PROFILES_ACTIVE=prod
   NACOS_ENABLED=true
   SERVER_PORT=8080
   ```
4. 执行 `backend-only` 发布。
5. 执行 `admin-only` 发布。
6. 执行生产公网 smoke。

生产 smoke：

```text
GET  https://api.kplyyk.com/api/v3/api-docs
POST https://api.kplyyk.com/api/admin/auth/login
GET  https://kplyyk.com
```

生产发布记录必须额外写入：

- 测试环境 smoke 结果。
- 生产容器 env 回读。
- 生产 Nacos dataId 核验结果。
- 测试与生产数据库隔离结论。

## 6. 发布记录命名

测试环境：

```text
YYYYMMDD-HHMM-test-backend-<label>.md
YYYYMMDD-HHMM-test-admin-<label>.md
YYYYMMDD-HHMM-test-backend-admin-<label>.md
```

生产环境：

```text
YYYYMMDD-HHMM-prod-backend-<label>.md
YYYYMMDD-HHMM-prod-admin-<label>.md
YYYYMMDD-HHMM-prod-backend-admin-<label>.md
```

生产记录必须引用同批或最近一次测试环境保留记录。

## 7. 回滚边界

### 7.1 测试环境回滚

测试环境回滚只影响：

- `kaipai-backend-test`
- `/opt/kaipai/nginx/html-test`
- `test-api.kplyyk.com`
- `test.kplyyk.com`
- `kaipai-backend-test.yml`
- `kaipai_test`

不得改动生产容器、生产域名和生产数据库。

### 7.2 生产环境回滚

生产环境回滚只影响：

- `kaipai-backend`
- `/opt/kaipai/nginx/html`
- `api.kplyyk.com`
- `kplyyk.com`
- `kaipai-backend-prod.yml`
- `kaipai_prod`

生产回滚后必须再次确认测试环境仍可访问。

## 8. 中止条件

出现以下任一情况，停止推进：

1. `kaipai-backend-test.yml` 或 `kaipai-backend-prod.yml` 不可读。
2. 测试和生产连接同一个数据库。
3. 测试和生产容器端口冲突。
4. 测试域名证书不可用。
5. 测试 smoke 不通过。
6. 生产 env 回读不是 `prod + Nacos`。
7. 生产公网 smoke 不通过。

## 9. 完成定义

同机双环境完成必须同时满足：

1. 测试 API 域名可用。
2. 测试管理端域名可用。
3. 生产 API 域名可用。
4. 生产管理端域名可用。
5. 测试和生产容器同时稳定运行。
6. 测试和生产 Nacos dataId 不同。
7. 测试和生产数据库不同。
8. 测试和生产发布记录均已落档。
