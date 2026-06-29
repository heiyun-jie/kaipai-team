# 生产环境发布运维流程

> 对应 Spec：`00-184 current-phase-production-release-ops-runbook`
> 适用范围：`kaipaile-server`、`kaipai-admin`
> 本文只记录生产发布流程。执行发布前仍需同时遵守 `backend-admin-standard-release.md` 的备份、smoke、记录和回滚规则。

## 1. 核心结论

后端生产发布不是“改源码为 prod 后再打包”。当前后端采用同一份 Spring Boot JAR 多环境复用：

- 本地 / 开发默认：`SPRING_PROFILES_ACTIVE=dev`、`NACOS_ENABLED=false`
- 生产运行必须显式：`SPRING_PROFILES_ACTIVE=prod`、`NACOS_ENABLED=true`
- 生产 Nacos dataId：`kaipai-backend-prod.yml`
- 生产 API 域名：`https://api.kplyyk.com`
- 生产管理端域名：`https://kplyyk.com`

只完成本地 `prod` 打包验证，不代表线上已经切到生产环境；必须确认远端 compose/env、容器 env、Nacos dataId 和公网 smoke。

如果本轮要求“发布生产环境并保留测试环境”，必须先按 `same-host-dual-environment-runbook.md` 建立或确认测试环境独立可用，再执行本文的生产发布流程。测试环境 smoke 未通过时，不进入生产切换。

## 2. 生产环境基线

| 项 | 值 |
|----|----|
| 远端主机 | `101.43.57.62` |
| 后端运行目录 | `/opt/kaipai` |
| 后端运行 JAR | `/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar` |
| 后端容器 | `kaipai-backend` |
| 后端 profile | `prod` |
| 后端 Nacos | `enabled=true` |
| Nacos server | `101.43.57.62:8848` |
| Nacos group | `DEFAULT_GROUP` |
| Nacos prod dataId | `kaipai-backend-prod.yml` |
| API 公网 smoke | `https://api.kplyyk.com` |
| 管理端公网 smoke | `https://kplyyk.com` |

敏感值要求：

- 不在文档和发布记录中写入数据库密码、云密钥、Nacos 密码或管理员密码。
- 管理员登录 smoke 使用 `KAIPAI_ADMIN_SMOKE_PASSWORD`。
- 云厂商、微信、短信、AI token 等配置使用本机环境变量或 `.sce/config/local-secrets/` 下的 gitignored secret 文件。

## 3. 发布前门禁

每次生产发布先确定：

1. 发布批次号：建议 `YYYYMMDD-HHMM-prod-<scope>-<label>`。
2. 发布范围：`backend-only`、`admin-only`、`backend+admin`。
3. 关联 Spec：本次业务变更对应的 Spec 编号。
4. 本地 Git：主仓库和子仓库均在 `main`，且无无关脏改。
5. Nacos：`kaipai-backend-prod.yml` 可读，且包含本轮生产所需配置。
6. 远端运行环境：compose/env 计划切到 `SPRING_PROFILES_ACTIVE=prod`、`NACOS_ENABLED=true`。
7. 管理员 smoke 密码：当前 shell 已设置 `KAIPAI_ADMIN_SMOKE_PASSWORD`。
8. 测试环境保留：
   - 若本轮按 `00-185` 同机双环境治理执行，则 `https://test-api.kplyyk.com` 与 `https://test.kplyyk.com` 已通过 smoke，且测试后端未连接生产数据库。
   - 若本轮按 `00-186` 单环境切换执行，则这一条不作为门禁。

推荐本地检查：

```powershell
git status --short
git -C kaipaile-server status --short
git -C kaipai-admin status --short

$env:KAIPAI_ADMIN_SMOKE_PASSWORD
```

## 4. 后端生产发布流程

### 4.1 只读核验 Nacos prod 配置

目标：

- `dataId=kaipai-backend-prod.yml`
- `group=DEFAULT_GROUP`

要求：

- HTTP 返回成功。
- 内容中存在 `spring.datasource` / `spring.data.redis` 等生产运行所需配置。
- 记录中只写 key presence，不写真实密码。

如使用 Nacos API 只读核验，登录凭据从现有安全来源读取，不在命令或记录里展开明文。

### 4.2 本地 prod 打包验证

在 [kaipaile-server](D:/XM/kaipai-team/kaipaile-server) 执行：

```powershell
.\scripts\package-backend.ps1 -Environment prod -SkipTests
```

通过条件：

- 输出 `SPRING_PROFILES_ACTIVE=prod`
- 输出 `NACOS_ENABLED=true`
- Maven `BUILD SUCCESS`
- 生成 `target\kaipai-backend-1.0.0-SNAPSHOT.jar`

记录：

```powershell
Get-FileHash .\target\kaipai-backend-1.0.0-SNAPSHOT.jar -Algorithm SHA256
```

### 4.3 同步远端后端运行环境

生产环境必须先让远端 compose/env 具备：

```text
SPRING_PROFILES_ACTIVE=prod
NACOS_ENABLED=true
```

推荐使用现有 compose 环境同步脚本留档：

```powershell
$env:SPRING_PROFILES_ACTIVE = "prod"
$env:NACOS_ENABLED = "true"
python .sce/runbooks/backend-admin-release/scripts/run-backend-compose-env-sync.py --label prod-env-switch --from-local-env SPRING_PROFILES_ACTIVE --from-local-env NACOS_ENABLED
```

同步完成后不得直接宣告线上生效；必须继续执行 `backend-only` 发布或重建，让容器重新读取 env。

若本轮按 `00-186` 单环境切换执行，`backend-only` 还必须显式把目标库切到生产库，避免 schema history 预检继续落到开发库。

### 4.4 执行 backend-only 标准发布

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py --label prod-backend-<label> --operator <operator> --public-base-url https://api.kplyyk.com --mysql-database kaipai_prod
```

注意：

- 现有 `run-backend-only-release.py` 构建的是同一份 JAR，不靠打包阶段写死 profile。
- 现有 `run-backend-only-release.py` 默认仍使用 `KAIPAI_RELEASE_MYSQL_DATABASE=kaipai_dev`；生产切换时必须显式覆盖为 `kaipai_prod`，或在 shell 里先导出 `KAIPAI_RELEASE_MYSQL_DATABASE=kaipai_prod`。
- 远端 helper 执行 MySQL dump / schema history 预检时不允许在仓库或命令行参数写死 root 密码；如容器内没有 `MYSQL_ROOT_PASSWORD`，必须在远端执行环境注入 `KAIPAI_RELEASE_MYSQL_ROOT_PASSWORD` 或 `MYSQL_ROOT_PASSWORD`。
- 真正的生产 profile 来自远端 compose/env。
- 发布记录中必须回读 `DOCKER_INSPECT_ENV`，确认容器内存在 `SPRING_PROFILES_ACTIVE=prod` 和 `NACOS_ENABLED=true`。

### 4.5 后端生产 smoke

发布脚本必须至少确认：

```text
GET  https://api.kplyyk.com/api/v3/api-docs
POST https://api.kplyyk.com/api/admin/auth/login
```

业务相关改动必须追加对应 smoke。例如 AI 分享图、实名、模板、分享卡等接口，不允许只用基础 API docs 代表业务通过。

发布记录必须包含：

- 本地 JAR SHA256
- 远端 JAR 备份路径
- 容器内 `/app/app.jar` SHA256
- Docker compose 状态
- 容器运行环境变量回读
- 公网 API smoke 结果
- Nacos prod dataId 只读核验结论

## 5. 管理端生产发布流程

### 5.1 本地检查

在 [kaipai-admin](D:/XM/kaipai-team/kaipai-admin) 执行：

```powershell
npm run type-check
npm run build
```

通过条件：

- TypeScript 检查通过。
- Vite build 成功。

### 5.2 执行 admin-only 标准发布

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-admin-only-release.py --label prod-admin-<label> --operator <operator> --public-base-url https://kplyyk.com
```

发布记录必须包含：

- release branch / commit
- 远端 bare repo 检出结果
- 服务端 Node / npm 版本
- 远端 dist 归档路径
- `https://kplyyk.com` 首页 smoke
- 管理端登录页或本次改动页面人工验证

## 6. backend+admin 联合发布顺序

联合发布必须按顺序执行：

1. 后端 Nacos prod 配置只读核验。
2. 后端远端 compose/env 切到 `prod + Nacos`。
3. 后端 `backend-only` 发布。
4. 后端公网 API smoke 通过。
5. 管理端 `admin-only` 发布。
6. 管理端公网 smoke 通过。
7. 追加业务端到端 smoke。

任何一步失败，停止后续步骤并按第 8 节判断回滚。

## 7. 生产发布记录模板

每次生产发布在 `.sce/runbooks/backend-admin-release/records/` 下新增记录，建议文件名：

```text
YYYYMMDD-HHMM-prod-<scope>-<label>.md
```

最小内容：

```markdown
# 生产发布记录

## 基本信息

- 发布批次号：
- 发布时间：
- 发布范围：
- 操作人：
- 关联 Spec：

## 生产环境门禁

- Git 工作区：
- Nacos prod dataId：
- 远端 compose/env：
- 管理员 smoke 密码环境变量：

## 后端发布

- 本地构建命令：
- 本地 JAR：
- 本地 JAR SHA256：
- 远端备份路径：
- 容器内 JAR SHA256：
- 容器 env 回读：
- API smoke：
- 业务 smoke：

## 管理端发布

- 构建命令：
- release ref：
- 远端 dist：
- 首页 smoke：
- 页面验证：

## 结论

- 最终结论：完成 / 中止 / 回滚
- 问题：
- 后续动作：
```

## 8. 回滚流程

### 8.1 后端回滚

使用 `backend-only` 发布记录中的远端备份路径：

1. 恢复上一版 JAR 到 `/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar`。
2. 使用远端 helper 或 compose 重建 `kaipai` 服务。
3. 回读容器 env，确认是否仍需保持 `prod + Nacos`。
4. 重跑公网 API smoke。
5. 在同一发布记录中写明回滚时间、回滚产物和 smoke 结果。

### 8.2 管理端回滚

使用 `admin-only` 发布记录中的静态目录备份：

1. 恢复 `/opt/kaipai/nginx/html`。
2. 重载 nginx。
3. 访问 `https://kplyyk.com`。
4. 验证至少一个后台页面。
5. 在同一发布记录中写明回滚结果。

## 9. 中止条件

出现以下任一情况，停止生产发布：

1. `kaipai-backend-prod.yml` 不可读或缺关键配置。
2. 本地构建失败。
3. 远端 compose/env 无法确认 `SPRING_PROFILES_ACTIVE=prod`、`NACOS_ENABLED=true`。
4. 容器启动失败或反复重启。
5. `https://api.kplyyk.com` 公网 smoke 失败。
6. `https://kplyyk.com` 管理端 smoke 失败。
7. 发布记录无法落档。

## 10. 发布完成定义

只有以下条件全部满足，才能写“生产发布完成”：

1. 生产 Nacos dataId 已核验。
2. 远端运行环境已回读为 `prod + Nacos`。
3. 后端 / 管理端对应产物已备份并替换。
4. 公网 smoke 通过。
5. 业务 smoke 通过。
6. 发布记录已写入 `records/`。

未满足任一条件时，本轮只能记录为“发布中止”或“发布动作已执行但审查未通过”。
