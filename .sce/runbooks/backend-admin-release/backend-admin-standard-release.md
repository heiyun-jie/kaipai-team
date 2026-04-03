# 后端与管理端标准发布手册

> 对应 Spec：`00-29 backend-admin-release-governance`
> 适用范围：`kaipaile-server`、`kaipai-admin`
> 当前目标环境事实基线：
> - 远端主机：`101.43.57.62`
> - 后端运行目录：`/opt/kaipai`
> - 后端运行 jar：`/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar`
> - 后端容器：`kaipai-backend`
> - 后端镜像：`kaipai-kaipai:latest`
> - 后端运行环境：`NACOS_ENABLED=true`、`SPRING_PROFILES_ACTIVE=dev`、`SERVER_PORT=8080`
> - nginx 配置目录：`/opt/kaipai/nginx/conf`
> - nginx 静态目录：`/opt/kaipai/nginx/html`
> - nginx `/api` 反代目标：`http://kaipai-backend:8080`
> - 管理端本地构建目录：`D:\XM\kaipai-team\kaipai-admin\dist`
> - 管理端本地开发地址：`http://127.0.0.1:5174`
> - 管理端本地开发代理目标：默认 `http://127.0.0.1:8010`，可通过 `VITE_API_PROXY_TARGET` 覆盖
> - 远端系统：`Ubuntu 22.04 LTS`
> - 远端包管理器：`apt-get`
> - 远端 Node.js：`v22.22.2`
> - 远端 npm：`10.9.7`

## 1. 硬规则

1. 每次发布都必须先填写发布批次号，推荐格式：`YYYYMMDD-HHMM-<scope>-<label>`。
2. 每次发布都必须先确定范围：`backend-only`、`admin-only`、`backend+admin`。
3. 每次发布都必须先备份，再替换。
4. 每次发布都必须留下产物 SHA、备份路径和 smoke 结果。
5. 若任何关键检查失败，立即中止；若关键 smoke 失败，进入回滚判断。
6. 若执行中发现当前 runbook 与实际可执行链路不一致，必须先暂停发布并更新 Spec + runbook，再继续发布。
7. 标准 `backend-only` 发布必须通过脚本 `scripts/run-backend-only-release.py` 执行；手工逐条命令只允许作为脚本故障时的应急兜底，并且必须先修正文档或脚本。
8. 标准 `admin-only` 发布必须通过脚本 `scripts/run-admin-only-release.py` 执行；手工逐条命令只允许作为脚本故障时的应急兜底，并且必须先修正文档或脚本。
9. 标准 `backend-only` 发布默认使用 `OpenSSH key auth + scp/ssh + 远端 sudo helper`；标准 `admin-only` 发布默认使用 `OpenSSH key auth + git push/ssh + 远端 sudo helper`；`password + Paramiko` 只允许用于一次性引导或修复，不再作为正式发布链路。
10. 当前标准 `admin-only` 发布已切换为“本地生成 git snapshot 仓库，push 到远端 bare repo，由服务器按 release ref 检出执行 `npm ci && npm run build`，再由 helper 完成静态替换”。
11. 当前标准 `backend-only` 发布已切换为“本地 JDK 17 构建 jar，上传到远端临时目录，再由 helper 统一完成备份、compose 重建、运行时回读与 smoke”。
11.1 若 `kaipaile-server` 当前工作树存在非 `target/` 脏改，标准 `backend-only` 不得直接从当前工作树构建；脚本必须先阻断，或显式切换为“`HEAD` 干净快照 + overlay 文件清单”构建模式。
12. 若只是补后端 compose / env source 的运行时变量，不允许手改远端 `docker-compose.yml`；必须先通过脚本 `scripts/run-backend-compose-env-sync.py` 留档，再单独执行 `backend-only` 发布。
13. 若当前运行时启用了 `NACOS_ENABLED=true`，涉及配置来源排查时不得只查 compose；必须再通过脚本 `scripts/read-backend-nacos-config.py` 只读回读当前 dataId。
13.0 若连“本地当前有没有合法微信配置输入”都还不能证明，先通过脚本 `scripts/read-local-wechat-config-inputs.py` 固化本地输入检查，不再口头争论“是不是本地根本没有值”。
13.01 若本机连 gitignored 的本地 secret 文件都还没有，先通过脚本 `scripts/init-local-wechat-secret-file.py` 初始化 `.sce/config/local-secrets/wechat-miniapp.env`，再由人工填入真实 secret；placeholder 值不得直接进入同步。
13.05 若本轮就是要正式推进微信配置来源补齐，优先通过脚本 `scripts/run-backend-wechat-config-sync-pipeline.py` 固定顺序执行 `local-input -> remote-gate -> compose sync -> nacos sync`，不再人工串多个脚本。
13.1 若业务门禁同时依赖 compose 来源、容器 env 与 Nacos 微信配置存在性，优先通过脚本 `scripts/read-backend-wechat-config-precheck.py` 一次性生成统一预检查结论，不再手工串多个诊断目录。
14. 若需要补 Nacos dataId 内容，不允许直接在 Nacos 控制台手工修改后不留档；必须先通过脚本 `scripts/run-backend-nacos-config-sync.py` 留档，再单独执行 `backend-only` 发布。
15. 若本次后端变更涉及 `kaipaile-server/src/main/resources/db/migration/*.sql`，必须先通过脚本 `scripts/run-backend-schema-migration.py` 完成 schema 发布，再允许继续 `backend-only`。

## 1.1 环境基线变更

当前已允许的环境基线增强动作：

1. 在远端 `Ubuntu 22.04` 上通过系统包源安装 `node/npm`
2. 安装完成后必须记录版本
3. 当前已完成版本基线：`Node.js v22.22.2`、`npm 10.9.7`
4. 当前标准主链路已完成切换：`git snapshot -> bare repo -> 服务端检出构建 -> helper 发布`
5. `tar.gz` 仍保留为 helper 产物归档与故障回退链路，不再作为默认正式上传入口

本节目的：

- 给后续服务端构建能力预留基础
- 避免把“装了工具”误判成“已经切换发布方案”

## 2. 发布前通用检查

每次发布都先完成以下检查：

1. 确认本次变更对应的 Spec / 需求 / 样本记录。
2. 确认本次范围是否需要联合发布。
3. 确认目标环境还是当前这套：
   - `/api` 仍由 nginx 反代到 `kaipai-backend:8080`
   - 后端仍走 `NACOS_ENABLED=true + SPRING_PROFILES_ACTIVE=dev`
   - 管理端静态目录仍是 `/opt/kaipai/nginx/html`
   - 若当前访问的是本地 `http://127.0.0.1:5174`，要明确它只是本地 Vite dev server，不是线上访问入口；它默认通过 `VITE_API_PROXY_TARGET` 代理到本机后端
4. 创建本次发布记录文件：
   - `.sce/runbooks/backend-admin-release/records/<release-id>.md`
5. 在记录文件里先写清：
   - 发布批次号
   - 发布范围
   - 操作人
   - 关联 Spec / 需求

## 3. backend-only 发布

### 3.0 标准入口

首次引导入口：

```powershell
python .sce/runbooks/backend-admin-release/scripts/bootstrap-admin-release.py --operator <name>
```

引导脚本职责：

- 生成或复用本地专用发布 key
- 把公钥安装到远端 `~/.ssh/authorized_keys`
- 安装远端 helper：
  - `/usr/local/bin/kaipai-admin-release-helper.sh`
  - `/usr/local/bin/kaipai-backend-release-helper.sh`
- 安装最小 sudo 授权：`/etc/sudoers.d/kaipai-admin-release`
- 初始化远端 bare repo：`/home/kaipaile/kaipai-admin-release.git`
- 验证正式发布所需的 `ssh/scp`、`git push` 与 `sudo -n helper` 全部可用

若本地 helper / sudoers 已更新，但不需要重建 bare repo 或重复做完整引导，执行独立修复入口：

```powershell
python .sce/runbooks/backend-admin-release/scripts/sync-release-helper-baseline.py --operator <name>
```

职责：

- 复用当前仓内 `kaipai-admin-release-helper.sh` 与 `kaipai-backend-release-helper.sh`
- 通过密码登录 + `sudo` 重装远端 helper
- 重装 `/etc/sudoers.d/kaipai-admin-release`
- 重新验证 `sudo -n helper --healthcheck`

标准 `backend-only` 发布入口：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py --label <label> --operator <name>
```

若 `kaipaile-server` 当前存在与本轮无关的非 `target/` 脏改，标准入口改为：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py --label <label> --operator <name> --overlay-path <relative-path> --overlay-path <relative-path>
```

脚本职责：

- 自动选择可用的本地 `JDK 17`
- 若工作树干净，自动在当前工作树执行 `mvn -q -DskipTests clean package`
- 若工作树存在非 `target/` 脏改且已显式提供 `--overlay-path`，自动创建 `HEAD` 干净快照，并只把 overlay 清单覆盖到快照后再构建
- 若工作树存在非 `target/` 脏改但未提供 `--overlay-path`，脚本直接中止
- 自动计算本地 jar SHA256
- 自动通过原生 `scp` 上传 jar 到远端临时目录
- 自动通过原生 `ssh` 调用远端 helper 完成备份、替换、`docker compose build/up`、运行时回读和 smoke
- 自动在正式发版前校验目标库 `schema_release_history`，若本地 migration 脚本未执行到目标库则直接中止
- 自动把 compose 原始后端服务来源摘录与 `docker compose config` 渲染结果一并固化到记录
- 自动把工作树脏改清单、overlay 清单和实际构建根目录写入发布记录
- 自动生成发布记录到 `records/`

以下 `3.1` 到 `3.5` 是脚本必须遵循的标准链路，也是脚本异常时才允许人工接管的兜底步骤。

禁止事项：

- 不允许继续手写 `docker build && docker rm && docker run` 作为标准正式发布链路
- 不允许在本地仍运行 JDK 8 的情况下继续宣告后端构建已准备就绪
- 若远端 helper、sudoers 或 compose 入口不可用，先执行引导或修复脚本，再继续当前批次

### 3.0.1 compose 来源同步

当需求只涉及后端运行时变量来源，例如补 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`，但本轮还没有进入 jar 变更或容器重建时，必须先走标准 compose 来源同步脚本：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-compose-env-sync.py --label <label> --from-local-env WECHAT_MINIAPP_APP_ID --from-local-env WECHAT_MINIAPP_APP_SECRET
```

脚本职责：

- 通过标准 `OpenSSH key auth`
- 回读远端当前 `/opt/kaipai/docker-compose.yml`
- 只更新 `services.kaipai.environment` 下的目标变量
- 远端 helper 先备份现有 compose，再校验候选 compose 的 `docker compose config`
- 自动生成一份独立配置同步记录到 `records/`

门禁要求：

- `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET` 必须成组提供，不能只补其一
- 若输入值命中 placeholder / fake secret 校验，脚本会直接拒绝继续写 compose
- compose 来源同步完成后，不得口头宣告“线上已生效”；必须再走标准 `backend-only` 发布 / 重建
- 发布后必须再用标准诊断确认 compose 来源摘录与容器 env 都包含目标变量

### 3.0.2 Nacos 配置源回读

当后端当前运行在 `NACOS_ENABLED=true`，且问题涉及配置缺失、环境漂移或“compose 已补但运行时仍不生效”时，必须补一轮标准 Nacos 配置源回读：

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-backend-nacos-config.py --label <label>
```

脚本职责：

- 通过标准 `OpenSSH key auth`
- 由远端 helper 使用 Nacos 标准登录接口只读回读 `kaipai-backend`、`kaipai-backend.yml`、`kaipai-backend-dev.yml`
- 输出目标键是否存在的 presence summary
- 对目标关键字匹配内容做过滤回读，并对敏感值打码
- 自动生成诊断目录到 `records/diagnostics/`

门禁要求：

- 当前启用了 `NACOS_ENABLED=true` 时，不允许只凭 compose 证据宣告配置链已闭环
- 若 compose 与 Nacos 两侧都缺变量，先补合法配置来源，再做正式发布
- 若 compose 已有变量但 Nacos 覆盖层缺失或冲突，先确认权威来源，再允许继续改线上

### 3.0.2A 微信配置组合门禁（只读）

当业务问题直接依赖微信小程序配置是否在运行时成组就位，例如 invite `wxacode` 或 login-auth 微信登录，默认先走统一门禁脚本，而不是人工串 `runtime diagnostics + nacos scan`：

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-backend-wechat-config-precheck.py --label <label>
```

脚本职责：

- 通过标准 `OpenSSH key auth`
- 只读回读 compose 来源摘录、`docker compose config` 渲染结果、容器当前 env
- 只读回读 `kaipai-backend`、`kaipai-backend.yml`、`kaipai-backend-dev.yml` 的微信键存在性
- 自动生成单一诊断目录到 `records/diagnostics/`
- 自动给出门禁结论：当前是否允许进入微信真实样本验证

门禁要求：

- 该脚本默认要求 compose 来源、compose 渲染结果、容器 env 与目标 Nacos dataId 同时具备 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`
- 若任一侧缺失，则本轮只能先补配置来源，不能把“接口已上线但显式降级”误写成“微信链路已可验证”
- 如需保留失败样本而不让命令返回失败，可显式加 `--no-fail-on-missing`

### 3.0.2B 本地微信输入检查（只读）

当当前批次甚至无法证明“本地是否已经持有可合法使用的微信配置值”时，先走本地输入检查，而不是直接远端同步失败后再回头补解释：

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-local-wechat-config-inputs.py --label <label>
```

脚本职责：

- 只读检查当前机器环境变量中的 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`
- 只读检查本地 secret 文件 `.sce/config/local-secrets/wechat-miniapp.env`
- 只读检查 `kaipai-frontend/project.config.json` 中的固定 `appid`
- 只读检查仓内最小候选 `.env` 文件是否包含目标键
- 自动生成本地诊断目录到 `records/diagnostics/`

门禁要求：

- 若本地都不存在成组 `appId + appSecret` 输入，则不得直接进入 `run-backend-compose-env-sync.py` 或 `run-backend-nacos-config-sync.py`
- 当前推荐做法是把真实值写入被 `.gitignore` 排除的 `.sce/config/local-secrets/wechat-miniapp.env`，模板文件为 `.sce/config/wechat-miniapp.env.example`
- 若本地 secret 文件中的 `appSecret` 仍是 `replace-with-real-app-secret`、`fake-*`、`example` 等 placeholder / fake 值，仍判定为 not ready，不得继续同步
- `project.config.json` 中存在 `appid` 只能证明前端目标小程序已固定，不能替代后端 `appSecret`
- 本地输入检查当前至少会校验“是否为非空且非 placeholder 的可用输入”；但它仍不负责证明“值是否属于正确环境”
- 当前原子同步脚本 `run-backend-compose-env-sync.py`、`run-backend-nacos-config-sync.py` 也默认支持同一 secret 文件，不要求先手工 export 环境变量

初始化脚本：

```powershell
python .sce/runbooks/backend-admin-release/scripts/init-local-wechat-secret-file.py
```

职责：

- 创建被 `.gitignore` 排除的 `.sce/config/local-secrets/wechat-miniapp.env`
- 自动从 `kaipai-frontend/project.config.json` 预填当前小程序 `appId`
- 写入显式 placeholder secret，避免误以为文件存在就代表门禁已通过

### 3.0.2C 微信配置同步总控

当目标是把微信配置来源补齐流程本身脚本化，而不是只执行单个原子动作时，默认使用总控脚本：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-wechat-config-sync-pipeline.py --label <label> [--dry-run]
```

脚本职责：

- 固定按 `local-input -> remote-gate -> compose sync -> nacos sync` 顺序执行
- 默认从当前 shell 环境和 `.sce/config/local-secrets/wechat-miniapp.env` 解析本地输入
- 任一前置失败立即中止，并生成总控记录
- 若本地没有成组且可用的 `appId + appSecret` 输入，则在第 1 步直接中止，不再继续打远端
- 总控完成后，仍只代表配置来源已同步；不代表后端运行时已生效

门禁要求：

- 总控不替代正式 `backend-only` 发布；同步完成后仍必须执行重建
- 总控中的远端门禁预检查用于固定“同步前”的远端事实，不要求该步先通过才允许进入同步
- 若需要只看当前状态而不做同步，继续使用 `read-local-wechat-config-inputs.py` 与 `read-backend-wechat-config-precheck.py`

### 3.0.3 Nacos 配置源同步

当当前运行时为 `dev + Nacos`，且目标变量需要写入某个 Nacos dataId 时，必须先走标准 Nacos 同步脚本：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-nacos-config-sync.py --label <label> --nacos-data-id kaipai-backend-dev.yml --from-local-env WECHAT_MINIAPP_APP_ID --from-local-env WECHAT_MINIAPP_APP_SECRET
```

脚本职责：

- 通过标准 `OpenSSH key auth`
- 先只读导出目标 dataId 当前原文
- 在本地只修改目标键并生成候选配置
- 远端 helper 先备份发布前原文，再通过 Nacos 标准接口发布候选配置
- 自动生成一份独立配置同步记录到 `records/`

门禁要求：

- 对微信官方码场景，`WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET` 必须成组提供
- 若输入值命中 placeholder / fake secret 校验，脚本会直接拒绝继续写入 dataId
- 当前 active profile 为 `dev` 时，默认先改 `kaipai-backend-dev.yml`，不得无依据同时改多个 dataId
- Nacos 写入完成后，不得口头宣告“线上已生效”；必须再走标准 `backend-only` 发布 / 重建与运行时回读

### 3.0.4 schema 发布

当本次后端改动涉及 `kaipaile-server/src/main/resources/db/migration/*.sql`，必须先走标准 schema 发布脚本：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-schema-migration.py --label <label> --operator <name> --migration-file <script> ...
```

脚本职责：

- 通过标准 `OpenSSH key auth`
- 通过远端 helper 在目标 MySQL 容器执行 schema SQL
- 自动维护 `schema_release_history`
- 若生成的 schema 发布批次号超过 `schema_release_history.release_id` 当前库宽，自动先归一化到可写长度，并把归一化后的值写回发布记录
- 自动生成独立 `backend-schema` 发布记录

门禁要求：

- 若目标库尚未建立 `schema_release_history`，必须先用 `--mode baseline-existing` 为历史已存在 schema 建基线，再允许继续标准 `backend-only`
- 若本地存在未登记到目标库的 migration 脚本，`run-backend-only-release.py` 会直接中止
- schema 发布完成后，仍必须再走正式 `backend-only` 发布或至少完成本轮业务样本回归，不得把“DDL 已执行”误判成“后端已发布”

### 3.1 本地构建

在 `D:\XM\kaipai-team\kaipaile-server` 执行：

```powershell
mvn -q -DskipTests clean package
Get-FileHash .\target\kaipai-backend-1.0.0-SNAPSHOT.jar -Algorithm SHA256
```

要求：

- 构建成功
- 构建使用 `JDK 17`
- 记录本地 jar SHA256

### 3.2 远端备份

备份建议目录：

- `/opt/kaipai/backups/releases/<release-id>/backend/`

至少备份：

- 当前运行 jar
- `Dockerfile`
- `docker-compose.yml`
- `docker inspect kaipai-backend`
- `docker ps` 摘要
- `docker logs --tail 200 kaipai-backend`

### 3.3 上传与替换

将本地 jar 先上传到：

- `/home/kaipaile/backend-release-uploads/<release-id>/kaipai-backend-1.0.0-SNAPSHOT.jar`

然后在远端执行：

1. helper 比对上传后 SHA256
2. helper 将该 jar 归档到 `/opt/kaipai/builds/<release-id>/kaipai-backend-1.0.0-SNAPSHOT.jar`
3. helper 将该 jar 覆盖到 `/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar`

### 3.4 容器重建

在远端 `/opt/kaipai` 执行 compose 重建：

```bash
docker compose build kaipai
docker compose up -d --force-recreate kaipai
```

注意：

- 不允许只重启容器而不重新确认 compose 定义和环境变量
- 若当前线上残留同名旧容器但未受 compose 接管，helper 必须先清理旧容器，再执行 `compose up`
- 不允许漏核对 `nginx /api -> kaipai-backend:8080`

### 3.5 发布后检查

至少执行：

```bash
docker compose ps
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker inspect kaipai-backend
docker exec kaipai-backend sh -lc 'sha256sum /app/app.jar'
curl http://127.0.0.1:8080/api/v3/api-docs
curl -X POST http://127.0.0.1:8080/api/admin/auth/login -H 'Content-Type: application/json' -d '{"account":"admin","password":"admin123"}'
curl "http://127.0.0.1:8080/api/admin/recruit/roles?pageNo=1&pageSize=1&keyword="
curl "http://127.0.0.1:8080/api/role/search?page=1&size=1&keyword=&gender="
```

当前标准脚本会把上面 4 条后端 smoke 一并固化；若本次变更还涉及其他业务域，再追加对应 smoke。
其中基础入口探活必须使用“带超时的就绪轮询”，不能再用固定 8 秒等待替代。

记录要求：

- compose 版本与 compose ps
- compose 原始后端服务来源摘录
- `docker compose config` 渲染后的后端服务定义摘录
- 容器状态
- 运行时环境变量
- 容器内 `/app/app.jar` SHA256
- 基础入口结果
- 业务 smoke 结果

### 3.6 发布后异常排查

若 `backend-only` 发布完成后，真实环境仍出现 `400/500`、联调脚本卡在单个接口、或本地因 Nacos / DB / Redis 环境差异无法等价复现，必须先走标准只读诊断入口：

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-backend-runtime-logs.py --label <label> --since 15m
```

脚本职责：

- 复用标准发布的 `OpenSSH key auth`
- 先验证远端 helper / sudoers 基线
- 只读回读 `docker ps`、容器状态摘要（`status / StartedAt / FinishedAt / RestartCount / OOMKilled / restartPolicy`）、容器环境变量、`docker logs`
- 只读回读远端 `/opt/kaipai/docker-compose.yml` 的后端服务来源摘录
- 只读回读 `docker compose config` 渲染后的后端服务定义摘录
- 将诊断结果落到 `.sce/runbooks/backend-admin-release/records/diagnostics/<capture-id>/`

使用要求：

1. 先用业务 Spec 脚本复现一次真实问题
2. 再立即执行诊断脚本读取同一时间窗内日志
3. 若诊断产物显示是代码问题，再进入修复与重新发布
4. 若诊断产物显示是运行时基线漂移，先更新 00-29 Spec / runbook，再继续处理
5. 若问题涉及缺失环境变量，必须先用 compose 证据确认变量来源与缺失层级，再允许改线上
6. 若当前为 `dev + Nacos` 运行时，缺失环境变量还必须再补 Nacos 配置源回读，不能只看 compose

补充说明：

- 当问题表象是公网 `502 Bad Gateway` 时，先用同一入口把 `--container` 切到 `kaipai-nginx` 抓代理层日志，再回读 `kaipai-backend`
- 推荐顺序：
  - `python .sce/runbooks/backend-admin-release/scripts/read-backend-runtime-logs.py --label <label>-nginx --container kaipai-nginx --since 15m`
  - `python .sce/runbooks/backend-admin-release/scripts/read-backend-runtime-logs.py --label <label>-backend --container kaipai-backend --since 15m`

## 4. admin-only 发布

### 4.0 标准入口

首次引导入口：

```powershell
python .sce/runbooks/backend-admin-release/scripts/bootstrap-admin-release.py --operator <name>
```

引导脚本职责：

- 生成或复用本地专用发布 key
- 把公钥安装到远端 `~/.ssh/authorized_keys`
- 安装远端 helper：
  - `/usr/local/bin/kaipai-admin-release-helper.sh`
  - `/usr/local/bin/kaipai-backend-release-helper.sh`
- 安装最小 sudo 授权：`/etc/sudoers.d/kaipai-admin-release`
- 初始化远端 bare repo：`/home/kaipaile/kaipai-admin-release.git`
- 验证正式发布所需的 `ssh/scp`、`git push` 与 `sudo -n helper` 全部可用

标准 `admin-only` 发布入口：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-admin-only-release.py --label <label> --operator <name>
```

脚本职责：

- 自动生成 `kaipai-admin` 临时 git snapshot 仓库
- 自动将 release ref push 到远端 bare repo
- 自动通过原生 `ssh` 调用远端 helper 在服务器按 release ref 完成 `npm ci && npm run build`
- 自动由 helper 完成备份、替换与回读
- 自动执行公网与内网 smoke
- 自动生成发布记录到 `records/`

以下 `4.1` 到 `4.4` 是脚本必须遵循的标准链路，也是脚本异常时才允许人工接管的兜底步骤。

禁止事项：

- 不允许继续把 `password + Paramiko sftp/exec_command` 当作标准正式发布链路
- 若正式发布发现 key auth、helper 或 sudoers 不可用，先执行引导或修复脚本，再继续当前批次

### 4.1 本地快照

在临时目录 `D:\XM\kaipai-team\tmp\admin-git-snapshot-<release-id>` 生成 git snapshot：

```powershell
git init --initial-branch=release
git config user.name "Codex Release"
git config user.email "codex-release@local"
git config core.autocrlf false
git add .
git commit -m "release <release-id>"
git remote add origin "ssh://kaipaile@101.43.57.62/home/kaipaile/kaipai-admin-release.git"
$env:GIT_SSH_COMMAND='"C:\Windows\System32\OpenSSH\ssh.exe" -i "C:\Users\33340\.ssh\kaipai_release_ed25519" -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new'
git push --force origin HEAD:refs/heads/release/<release-id>
```

要求：

- 临时发布仓库来自 `kaipai-admin/` 当前工作区快照，不直接污染当前主仓
- 记录 release branch 与 commit
- push 成功后，远端 bare repo 可见对应 release ref

禁止事项：

- 不允许直接把 Windows 生成的 `zip` 包交给 Linux `unzip` 作为标准发布链路
- 若发现当前上传格式会在远端产生路径或文件名异常，必须先更新 runbook，再继续当前批次发布

### 4.2 远端备份

备份建议目录：

- `/opt/kaipai/backups/releases/<release-id>/admin-html/`

发布前先备份：

- `/opt/kaipai/nginx/html`
- `/opt/kaipai/nginx/conf/default.conf`
- 远端 helper 与 sudoers 基线：
  - `/usr/local/bin/kaipai-admin-release-helper.sh`
  - `/usr/local/bin/kaipai-backend-release-helper.sh`
  - `/etc/sudoers.d/kaipai-admin-release`

### 4.3 push 与替换

本地 release ref 先 push 到远端 bare repo：

- `/home/kaipaile/kaipai-admin-release.git`

然后执行：

1. helper 创建 `/opt/kaipai/builds/<release-id>/`、备份目录和源码工作目录
2. helper 备份当前 `/opt/kaipai/nginx/html` 与 `default.conf`
3. helper 从 bare repo 检出 `release/<release-id>` 到 `/opt/kaipai/repos/kaipai-admin-releases/<release-id>/src`
4. helper 在服务器执行 `npm ci && npm run build`
5. helper 将服务端生成的 `dist/` 归档到 `/opt/kaipai/builds/<release-id>/admin-dist.tar.gz`
6. helper 清理当前 `/opt/kaipai/nginx/html` 内容
7. helper 将本次 `dist/` 内容同步到 `/opt/kaipai/nginx/html`
8. helper 回读 `index.html`

标准远端调用：

```bash
git push origin HEAD:refs/heads/release/<release-id>
ssh -i ~/.ssh/kaipai_release_ed25519 kaipaile@101.43.57.62 "sudo -n /usr/local/bin/kaipai-admin-release-helper.sh --release-id <release-id> --git-branch release/<release-id> --git-commit <commit> --operator-user kaipaile"
```

### 4.4 发布后检查

至少执行：

```bash
ls -la /opt/kaipai/nginx/html
curl http://127.0.0.1/
curl http://127.0.0.1/api/v3/api-docs
```

然后补一条后台页面人工验证：

- 登录页可打开
- 至少一个本次改动页面可进入

记录要求：

- 远端静态目录回读
- release branch / commit
- 远端 bare repo 与远端检出 commit
- 服务端 `node/npm` 版本
- 服务端构建日志尾部
- helper 检出路径与 dist 落地路径
- 首页访问结果
- `/api` 反代结果
- 实际静态入口资源访问结果
- 人工页面验证结果

## 5. backend+admin 联合发布

默认顺序：

1. 先走 `backend-only`
2. 后端 smoke 通过后，再走 `admin-only`
3. 最后补一轮串联 smoke

串联 smoke 至少包含：

1. 管理端首页可打开
2. 管理端至少一个改动页面可进入
3. 该页面依赖的 `/api` 接口返回成功

## 6. 回滚

### 6.1 后端回滚

使用发布前备份的 jar 恢复：

1. 将备份 jar 覆盖回 `/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar`
2. 按当前同样的 compose 命令重新 `build/up -d --force-recreate`
3. 再做一轮后端 smoke

### 6.2 管理端回滚

使用发布前备份的静态目录恢复：

1. 将备份目录恢复到 `/opt/kaipai/nginx/html`
2. 再访问 `/` 与一个后台关键页
3. 确认 `/api` 仍通

## 7. 中止条件

遇到以下任一情况，必须中止当前发布：

1. 本地产物构建失败
2. 产物 SHA、git 检出 commit 或目录回读异常
3. 运行时集合与预期不一致
4. 后端容器无法稳定启动
5. 管理端首页不可访问
6. `/api` 反代失败

## 8. 发布完成定义

只有以下条件同时满足，才能写“发布完成”：

1. 备份完成
2. 新产物落地完成
3. 运行时集合回读完成
4. smoke 通过
5. 发布记录已补齐

## 9. 记录要求

每次发布完成后，必须把结果回填到：

- `.sce/runbooks/backend-admin-release/records/<release-id>.md`

记录模板：

- `backend-admin-release-evidence-template.md`
