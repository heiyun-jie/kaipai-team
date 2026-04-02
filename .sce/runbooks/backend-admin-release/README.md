# 后端与管理端发布手册

本目录承接 `00-29 backend-admin-release-governance` 的执行手册与记录。

## 当前文档

- `backend-admin-standard-release.md`
- `backend-admin-release-evidence-template.md`
- `scripts/bootstrap-admin-release.py`
- `scripts/run-backend-only-release.py`
- `scripts/run-admin-only-release.py`
- `scripts/read-backend-runtime-logs.py`
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
5. 标准 `admin-only` 发布必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/run-admin-only-release.py --label <label> --operator <name>`
6. 发版完成后确认记录已落到 `records/`
7. 若发布后需要排查真实环境 `400/500`，必须执行：
   `python .sce/runbooks/backend-admin-release/scripts/read-backend-runtime-logs.py --label <label> --since 15m`

当前 `backend-only` 标准主链路：

- 本地选择 `JDK 17` 并构建 `kaipaile-server/target/kaipai-backend-1.0.0-SNAPSHOT.jar`
- `scp` 上传 jar 到远端临时目录
- 远端 helper 备份当前 jar / compose 定义 / 容器信息
- helper 执行 `docker compose build kaipai && docker compose up -d --force-recreate kaipai`
- 脚本执行内外网 smoke 并落发布记录

当前 `admin-only` 标准主链路：

- 本地生成 `kaipai-admin` git snapshot 临时仓库
- `git push` 到远端 bare repo `/home/kaipaile/kaipai-admin-release.git`
- 远端 helper 按 release ref 检出并执行 `npm ci && npm run build`
- helper 备份并替换 `/opt/kaipai/nginx/html`
- 脚本执行 smoke 并落发布记录
