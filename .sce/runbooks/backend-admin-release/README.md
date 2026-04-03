# 后端与管理端发布手册

本目录承接 `00-29 backend-admin-release-governance` 的执行手册与记录。

## 当前文档

- `backend-admin-standard-release.md`
- `backend-admin-release-evidence-template.md`
- `wechat-config-gate-runbook.md`
- `scripts/bootstrap-admin-release.py`
- `scripts/sync-release-helper-baseline.py`
- `scripts/run-backend-only-release.py`
- `scripts/run-backend-schema-migration.py`
- `scripts/run-admin-only-release.py`
- `scripts/run-backend-compose-env-sync.py`
- `scripts/read-backend-runtime-logs.py`
- `scripts/read-backend-nacos-config.py`
- `scripts/read-backend-wechat-config-precheck.py`
- `scripts/read-local-wechat-config-inputs.py`
- `scripts/init-local-wechat-secret-file.py`
- `scripts/run-backend-wechat-config-sync-pipeline.py`
- `scripts/run-backend-nacos-config-sync.py`
- `scripts/kaipai-backend-release-helper.sh`
- `scripts/kaipai-admin-release-helper.sh`
- `records/`

## 使用方式

1. 发版前先看 `00-29` Spec
2. 再按 `backend-admin-standard-release.md` 选择对应发布分支
3. 首次切换到标准发布链路时，先执行：
   `python .sce/runbooks/backend-admin-release/scripts/bootstrap-admin-release.py --operator <name>`
4. 若 runbook/helper 已更新，且需要把远端 helper/sudoers 基线重装到当前仓版本，执行：
   `python .sce/runbooks/backend-admin-release/scripts/sync-release-helper-baseline.py --operator <name>`
5. 标准 `backend-only` 发布必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-backend-only-release.py --label <label> --operator <name>`
6. 若本次后端涉及 `db/migration/*.sql`，必须先执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-backend-schema-migration.py --label <label> --operator <name> --migration-file <script> ...`
7. 标准 `admin-only` 发布必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-admin-only-release.py --label <label> --operator <name>`
8. 发版完成后确认记录已落到 `records/`
9. 若发布后需要排查真实环境 `400/500`，必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/read-backend-runtime-logs.py --label <label> --since 15m`
10. 若业务 Spec 需要执行远端容器内只读 MySQL 校验，必须通过标准 helper 入口调用，不再直接散点 `sudo docker exec`
11. 当前标准只读诊断产物，除 `docker ps / env / logs` 外，还必须包含：
   - 远端 `/opt/kaipai/docker-compose.yml` 的后端服务来源摘录
   - `docker compose config` 渲染后的后端服务定义摘录
12. 若需要补后端 compose / env source 的运行时变量，必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-backend-compose-env-sync.py --label <label> --from-local-env <KEY> ...`
13. `run-backend-compose-env-sync.py` 只负责同步 `docker-compose.yml` 的后端环境变量来源，不替代正式 `backend-only` 发布；变量写入后仍必须再走一次标准发布与 smoke
14. 若问题涉及 `dev + Nacos` 运行时配置来源，必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/read-backend-nacos-config.py --label <label>`
15. `read-backend-nacos-config.py` 只负责只读回读 Nacos dataId 内容和目标键存在性，不替代正式配置变更或发布
16. 若还不确定本地是否具备合法微信配置输入，先执行：
   `python .sce/runbooks/backend-admin-release/scripts/read-local-wechat-config-inputs.py --label <label>`
16. 若本机还没有 gitignored 的本地 secret 文件，可先初始化：
   `python .sce/runbooks/backend-admin-release/scripts/init-local-wechat-secret-file.py`
17. `init-local-wechat-secret-file.py` 会创建 `.sce/config/local-secrets/wechat-miniapp.env`，自动预填当前小程序 `appId` 和 placeholder secret；未替换真实 secret 前，门禁仍会保持 blocked
18. `read-local-wechat-config-inputs.py` 默认也会检查本地 secret 文件 `.sce/config/local-secrets/wechat-miniapp.env`；当前模板在 `.sce/config/wechat-miniapp.env.example`
19. `read-local-wechat-config-inputs.py` 只负责本地只读证明：当前机器是否已有可用的 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`，以及前端 `project.config.json` 是否已固定 appId；placeholder / fake secret 会被判定为 not ready
19.5 若当前要推进 invite / login-auth 的微信门禁，优先直接看单页入口：
   `wechat-config-gate-runbook.md`
20. 若希望固定执行顺序，避免手工串 `local-input -> remote-gate -> compose sync -> nacos sync`，执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-backend-wechat-config-sync-pipeline.py --label <label> [--dry-run]`
21. `run-backend-wechat-config-sync-pipeline.py` 默认也会读取 `.sce/config/local-secrets/wechat-miniapp.env`；拿到真实 secret 后无需先手工导环境变量
22. `run-backend-wechat-config-sync-pipeline.py` 会固定顺序执行本地输入检查、远端门禁预检查、compose 来源同步和 Nacos 同步；任一前置失败都会直接中止并生成总控记录
23. 若业务问题同时依赖 compose 来源、容器 env 与 Nacos 微信配置门禁，优先执行：
   `python .sce/runbooks/backend-admin-release/scripts/read-backend-wechat-config-precheck.py --label <label>`
24. `read-backend-wechat-config-precheck.py` 会一次性固化 compose 来源摘录、compose 渲染结果、容器 env 与 Nacos dataId presence summary，适合作为 `wxacode / login-auth` 的统一只读门禁入口
25. 原子脚本 `run-backend-compose-env-sync.py`、`run-backend-nacos-config-sync.py` 当前也默认支持 `.sce/config/local-secrets/wechat-miniapp.env`，拿到 secret 后不必先手工导环境变量；若输入仍是 placeholder / fake secret，会被脚本拒绝
26. 若需要补 Nacos 配置来源，必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-backend-nacos-config-sync.py --label <label> --nacos-data-id <dataId> --from-local-env <KEY> ...`
27. `run-backend-nacos-config-sync.py` 只负责同步单个 dataId 的配置内容并留档，不替代正式 `backend-only` 发布；写入后仍必须再走一次标准发布与 smoke

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
