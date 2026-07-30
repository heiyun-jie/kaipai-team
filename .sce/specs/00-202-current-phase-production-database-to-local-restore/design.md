# 00-202 生产数据库恢复到本地 - 技术设计

## 1. 数据流

```text
production kaipai_prod (read only)
  -> controlled mysqldump + gzip + remote SHA256
  -> gitignored local backup directory
  -> local staging database kaipai_prod
  -> inventory and Linxia anchor validation
  -> stop local backend
  -> backup current local kaipai_dev
  -> rebuild kaipai_dev from validated staging database
  -> restart backend and smoke
```

## 2. 备份目录

```text
.sce/runbooks/backend-admin-release/records/local-backups/
  YYYYMMDD-HHMM-production-to-local-restore/
    remote/kaipai_prod.sql.gz
    local-before/kaipai_dev.sql.gz
    restore/kaipai_prod-to-kaipai_dev.sql.gz
    SHA256SUMS.txt
    execution-summary.md
```

该目录已被根 `.gitignore` 排除。

## 3. 远程导出

复用 `/usr/local/bin/kaipai-backend-release-helper.sh --mysql-dump`，固定：

- `--mysql-database kaipai_prod`
- `--mysql-container kaipai-mysql`
- 合法且唯一的 release id

helper 内部使用 `--single-transaction --routines --triggers --events --databases`，远程输出 dump 路径、大小和 SHA256。

## 4. 本地恢复策略

1. 在 `kaipai-mysql-local` 容器内生成当前 `kaipai_dev` dump 并 gzip，再复制到主机备份目录。
2. 把远程 dump 复制进本地容器，恢复为其原始库名 `kaipai_prod`。
3. 对暂存库执行表数、用户数、林夏账号、演员档案、实名、归属和分享卡门禁。
4. 从暂存 `kaipai_prod` 再生成不含 `CREATE DATABASE/USE` 的逻辑 dump。
5. 停止本地后端，删除并重建 `kaipai_dev`，把已验证暂存 dump 导入 `kaipai_dev`。
6. 比较两个本地库的结构和关键计数；失败时用 `local-before` dump 回滚。

## 5. 完成门禁

完成必须同时满足：

- 远程/本地生产 dump SHA256 相同。
- 本地执行前 dump 存在且 gzip 校验通过。
- 暂存库和最终 `kaipai_dev` 的表数、用户数、林夏关键资产计数及实名状态桶一致。
- 最终 `userId=10007` 有效且 `real_auth_status=2`。
- 本地后端重启后 API 文档 HTTP 200。

源库当前存在 `user.real_auth_status=2`、`actor_profile.is_certified=1`，但唯一 `identity_verification.status=1` 的历史不一致。本轮镜像恢复保持原样；是否修复本地申请单状态不属于本轮恢复事务。

## 6. 回滚

如最终导入或 smoke 失败：停止本地后端，重建 `kaipai_dev`，导入 `local-before/kaipai_dev.sql.gz`，再次启动后端并验证 API 文档。
