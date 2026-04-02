# 后端与管理端发布手册

本目录承接 `00-29 backend-admin-release-governance` 的执行手册与记录。

## 当前文档

- `backend-admin-standard-release.md`
- `backend-admin-release-evidence-template.md`
- `scripts/bootstrap-admin-release.py`
- `scripts/run-backend-only-release.py`
- `scripts/run-backend-schema-migration.py`
- `scripts/run-admin-only-release.py`
- `scripts/run-backend-compose-env-sync.py`
- `scripts/read-backend-runtime-logs.py`
- `scripts/read-backend-nacos-config.py`
- `scripts/run-backend-nacos-config-sync.py`
- `scripts/kaipai-backend-release-helper.sh`
- `scripts/kaipai-admin-release-helper.sh`
- `records/`

## 使用方式

1. 发版前先看 `00-29` Spec
2. 再按 `backend-admin-standard-release.md` 选择对应发布分支
3. 首次切换到标准发布链路时，先执行：
   `python .sce/runbooks/backend-admin-release/scripts/bootstrap-admin-release.py --operator <name>`
4. 标准 `backend-only` 发布必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py --label <label> --operator <name>`
5. 若本次后端涉及 `db/migration/*.sql`，必须先执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-backend-schema-migration.py --label <label> --operator <name> --migration-file <script> ...`
6. 标准 `admin-only` 发布必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-admin-only-release.py --label <label> --operator <name>`
7. 发版完成后确认记录已落到 `records/`
8. 若发布后需要排查真实环境 `400/500`，必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/read-backend-runtime-logs.py --label <label> --since 15m`
9. 若业务 Spec 需要执行远端容器内只读 MySQL 校验，必须通过标准 helper 入口调用，不再直接散点 `sudo docker exec`
10. 当前标准只读诊断产物，除 `docker ps / env / logs` 外，还必须包含：
   - 远端 `/opt/kaipai/docker-compose.yml` 的后端服务来源摘录
   - `docker compose config` 渲染后的后端服务定义摘录
11. 若需要补后端 compose / env source 的运行时变量，必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-backend-compose-env-sync.py --label <label> --from-local-env <KEY> ...`
12. `run-backend-compose-env-sync.py` 只负责同步 `docker-compose.yml` 的后端环境变量来源，不替代正式 `backend-only` 发布；变量写入后仍必须再走一次标准发布与 smoke
13. 若问题涉及 `dev + Nacos` 运行时配置来源，必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/read-backend-nacos-config.py --label <label>`
14. `read-backend-nacos-config.py` 只负责只读回读 Nacos dataId 内容和目标键存在性，不替代正式配置变更或发布
15. 若需要补 Nacos 配置来源，必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-backend-nacos-config-sync.py --label <label> --nacos-data-id <dataId> --from-local-env <KEY> ...`
16. `run-backend-nacos-config-sync.py` 只负责同步单个 dataId 的配置内容并留档，不替代正式 `backend-only` 发布；写入后仍必须再走一次标准发布与 smoke

当前 `backend-only` 标准主链路：

- 若包含 `db/migration` 变更，先执行 `run-backend-schema-migration.py`
- 本地选择 `JDK 17` 并构建 `kaipaile-server/target/kaipai-backend-1.0.0-SNAPSHOT.jar`
- `scp` 上传 jar 到远端临时目录
- 远端 helper 备份当前 jar / compose 定义 / 容器信息
- helper 执行 `docker compose build kaipai && docker compose up -d --force-recreate kaipai`
- `run-backend-only-release.py` 会在正式发版前校验目标库 `schema_release_history`，若本地 migration 脚本未执行到目标库会直接中止
- 脚本执行内外网 smoke 并落发布记录

当前 `admin-only` 标准主链路：

- 本地生成 `kaipai-admin` git snapshot 临时仓库
- `git push` 到远端 bare repo `/home/kaipaile/kaipai-admin-release.git`
- 远端 helper 按 release ref 检出并执行 `npm ci && npm run build`
- helper 备份并替换 `/opt/kaipai/nginx/html`
- 脚本执行 smoke 并落发布记录
