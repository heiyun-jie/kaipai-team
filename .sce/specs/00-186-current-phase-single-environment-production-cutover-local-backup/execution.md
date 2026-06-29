# 00-186 当前阶段单环境生产切换与本地线上备份 - 执行记录

## 1. 当前决策

用户明确表示：不做双环境了，资源不够；需要先在本地进行线上备份，然后切换生产环境。

本轮因此不再以 `00-185` 的双环境完成定义作为发布前置，改为单环境生产切换。

## 2. 待执行

1. 本地备份当前线上运行态。
2. 校验备份完整性。
3. 切换后端到 `prod + Nacos`。
4. 执行后端 / 管理端发布。
5. 执行公网 smoke。
6. 回填发布记录。

## 3. 已完成

1. 已创建本地备份目录：
   - `D:\XM\kaipai-team\.sce\runbooks\backend-admin-release\records\local-backups\20260629-1620-prod-single-env-precutover`
2. 已完成远端运行时备份下载：
   - `runtime-files.tar.gz`
   - `SHA256SUMS.remote.txt`
3. 已通过远端 helper 新增 `--mysql-dump` 能力完成数据库受控导出，并下载到本地：
   - `database/kaipai_dev.sql.gz`
   - `database/kaipai_prod.sql.gz`
4. 已完成数据库 gzip 校验：
   - `kaipai_dev.sql.gz` 解压字节数：`4067065985`
   - `kaipai_prod.sql.gz` 解压字节数：`103031`
5. 已生成本地全量校验文件：
   - `SHA256SUMS.txt`
6. 已补充本地备份 manifest：
   - `backup-manifest.md`
7. 已修正发布工具链缺陷：
   - `run-backend-only-release.py` 之前将 schema history 预检写死到 `kaipai_dev`
   - 现已支持通过 `--mysql-database` 指定目标数据库，避免生产切换时误校验开发库

## 4. 当前事实

1. 当前线上容器仍未切正式：
   - `SPRING_PROFILES_ACTIVE=dev`
   - `NACOS_ENABLED=false`
   - `SPRING_DATASOURCE_URL` 仍指向 `kaipai_dev`
2. 当前远端 compose 源文件仍存在历史残留：
   - `NACOS_ENABLED=falset`
3. 当前 `kaipai-backend-prod.yml` 已存在，但其 `spring.datasource.url` 指向 `kaipai`，与本 Spec 目标 `kaipai_prod` 不一致。
4. 当前三套库事实：
   - `kaipai_dev`：有真实业务数据，`schema_release_history=45`
   - `kaipai_prod`：有完整表结构与最小种子，`schema_release_history=0`
   - `kaipai`：有完整表结构但几乎为空，`schema_release_history=0`
5. 当前管理员登录 smoke 密码已确认可用：
   - 公网 `https://api.kplyyk.com/api/admin/auth/login`
   - 使用本机已配置的管理员 smoke 凭据返回 `code=200`

## 5. 下一步

1. 统一生产目标库口径：
   - 要么将 `kaipai-backend-prod.yml` 对齐到 `kaipai_prod`
   - 要么明确本轮正式环境实际目标库改为 `kaipai`
2. 同步远端 compose：
   - `SPRING_PROFILES_ACTIVE=prod`
   - `NACOS_ENABLED=true`
   - `SPRING_DATASOURCE_URL` 指向最终确认的生产库
3. 执行 `backend-only` 与 `admin-only` 标准发布。
4. 执行公网 smoke 并补发布记录。

## 6. 实际执行结果

1. 已按本 Spec 目标统一到 `kaipai_prod`：
   - `kaipai-backend-prod.yml` 已将 `spring.datasource.url` 从 `kaipai` 改为 `kaipai_prod`
   - 远端 compose 已同步到：
     - `SPRING_PROFILES_ACTIVE=prod`
     - `NACOS_ENABLED=true`
     - `SPRING_DATASOURCE_URL=.../kaipai_prod`
2. 已为 `kaipai_prod` 完成 `schema_release_history` baseline：
   - 记录：`20260629-172551-backend-schema-prod-single-env-baseline.md`
   - 共登记当前仓内 41 个 migration 脚本
3. 首次 `backend-only` 切换后发现真实生产阻塞：
   - 容器已按 `prod + Nacos + kaipai_prod` 启动
   - 但 `https://api.kplyyk.com/api/admin/auth/login` 返回 `code=500`
   - 根因：`kaipai-backend-prod.yml` 使用 `kaipai_prod_user`
   - MySQL 中该用户只有 `localhost` 账户，且授权仍指向旧库 `kaipai`
4. 已执行最小修复：
   - 新增 `kaipai_prod_user@'%'`
   - 授予 `kaipai_prod` 必要权限
   - 修复后公网后台登录立即恢复 `code=200`
5. 管理端首次公网 smoke 又发现根域名证书阻塞：
   - `kplyyk.com` 没有独立证书
   - 443 返回的是 `api.kplyyk.com` 证书
   - 导致 `run-admin-only-release.py` 在 TLS 校验阶段中止
6. 已执行根域名证书修复：
   - 通过 `certbot --webroot -w /var/www/letsencrypt -d kplyyk.com` 成功签发 `kplyyk.com`
   - 重跑 `admin-only` 后已通过公网 smoke

## 7. 最终状态

1. 后端生产切换完成：
   - 容器 env 回读包含：
     - `SPRING_PROFILES_ACTIVE=prod`
     - `NACOS_ENABLED=true`
     - `SPRING_DATASOURCE_URL=.../kaipai_prod`
2. 管理端生产发布完成：
   - `https://kplyyk.com/` 返回 `200`
   - 静态资源入口返回 `200`
3. 公网 smoke 完成：
   - `https://api.kplyyk.com/api/v3/api-docs`：`200`
   - `https://api.kplyyk.com/api/admin/auth/login`：`HTTP 200 + code=200`
   - `https://kplyyk.com/`：`200`
   - `https://kplyyk.com/api/admin/auth/login`：`HTTP 200 + code=200`

## 8. 相关记录

1. 本地备份：
   - `local-backups/20260629-1620-prod-single-env-precutover/backup-manifest.md`
2. Nacos 生产 dataId 对齐：
   - `20260629-172551-backend-nacos-prod-single-env-cutover.md`
3. `kaipai_prod` schema baseline：
   - `20260629-172551-backend-schema-prod-single-env-baseline.md`
4. Compose 生产环境切换：
   - `20260629-173317-backend-env-prod-single-env-cutover.md`
5. 根域名证书后代理同步尝试：
   - `20260629-175413-domain-api-proxy-prod-single-env-root-cert.md`
6. 管理端最终发布：
   - `20260629-175413-admin-only-prod-single-env-cutover-r2.md`

## 9. 结论

- 本轮 `00-186` 已完成。
- 当前单环境线上已从 `dev + kaipai_dev` 切换到 `prod + Nacos + kaipai_prod`。
- 本地备份已保留，可作为后续回滚基线。
