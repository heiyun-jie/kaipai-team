# 00-186 当前阶段单环境生产切换与本地线上备份 - 技术设计

## 1. 改动范围

| 层 | 文件 / 目录 | 改动 |
|----|----|----|
| Spec | `.sce/specs/00-186-current-phase-single-environment-production-cutover-local-backup/` | 新增单环境切换治理 |
| SCE 索引 | `.sce/specs/README.md` | 登记 `00-186` |
| 本地备份 | `.sce/runbooks/backend-admin-release/records/local-backups/<batch>/` | 存放本地线上备份，目录已被 `.gitignore` 排除 |
| 发布记录 | `.sce/runbooks/backend-admin-release/records/` | 记录备份、切换、发布与 smoke 结果 |

_Requirements: 3.1, 3.2, 3.3_

## 2. 本地备份范围

备份批次目录：

```text
.sce/runbooks/backend-admin-release/records/local-backups/YYYYMMDD-HHMM-prod-single-env-precutover/
```

备份对象：

1. 后端运行 JAR：`/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar`
2. 后端 compose：`/opt/kaipai/docker-compose.yml`
3. 后端 Dockerfile：`/opt/kaipai/Dockerfile`
4. Nginx 宿主机配置：`/etc/nginx/sites-available/default`、`/etc/nginx/sites-enabled/default`
5. 项目 Nginx 静态目录：`/opt/kaipai/nginx/html`
6. 当前线上数据库 dump：`kaipai_dev`
7. 当前目标生产数据库 dump：`kaipai_prod`，用于切换前对照
8. 容器状态摘要与运行 env 脱敏诊断

备份后生成：

```text
SHA256SUMS.txt
backup-manifest.md
```

_Requirements: 3.1_

## 3. 生产切换顺序

1. 执行本地线上备份。
2. 校验备份文件存在和 SHA256 清单。
3. 确认 `KAIPAI_ADMIN_SMOKE_PASSWORD` 是否可用；缺失时不得声称登录 smoke 已通过。
4. 通过 `run-backend-compose-env-sync.py` 同步：
   - `SPRING_PROFILES_ACTIVE=prod`
   - `NACOS_ENABLED=true`
   - 必要时同步 `SPRING_DATASOURCE_URL` 到 `kaipai_prod`
5. 执行 `run-backend-only-release.py --public-base-url https://api.kplyyk.com`。
6. 执行 `run-admin-only-release.py --public-base-url https://kplyyk.com`。
7. 执行生产 smoke。
8. 更新发布记录与 SCE execution。

_Requirements: 3.2, 3.3_

## 4. 回滚边界

如生产切换失败：

1. 优先使用标准发布脚本生成的远端备份回滚。
2. 若远端备份不可用，使用本地备份上传恢复。
3. 回滚后必须确认：
   - 后端容器恢复运行。
   - API docs 可访问。
   - 管理端首页可访问。

_Requirements: 3.3_
