# 00-186 当前阶段单环境生产切换与本地线上备份

## 1. 概述

由于同机双环境资源不足，本阶段放弃同机测试 / 生产双运行态，改为单环境生产切换：先将当前线上运行态完整备份到本地，再把现有后端运行环境从 `dev + NACOS_ENABLED=false + kaipai_dev` 切换为 `prod + NACOS_ENABLED=true + kaipai_prod`，并执行后端 / 管理端标准发布与公网 smoke。

本 Spec 只适用于本轮资源不足下的单环境生产切换，不代表长期架构目标。后续如资源恢复，仍可重新启用 `00-185` 的双环境治理。

## 2. 用户故事

作为发布操作人，我希望在资源不足不能保留测试环境时，至少先把当前线上完整备份到本地，然后再切正式环境。

作为维护者，我希望单环境切换前能明确备份范围、切换动作、smoke 和回滚边界，避免直接覆盖当前运行态后无法恢复。

## 3. 功能需求

### 3.1 本地线上备份

**描述**：生产切换前，必须把当前线上运行态备份到本地 gitignored 目录。

**验收标准**：

- WHEN 执行生产切换前 THEN 本地必须存在当前后端 JAR 备份。
- WHEN 执行生产切换前 THEN 本地必须存在当前 compose / Nginx 配置备份。
- WHEN 执行生产切换前 THEN 本地必须存在当前管理端静态目录备份。
- WHEN 执行生产切换前 THEN 本地必须存在当前线上数据库 dump。
- WHEN 备份完成 THEN 必须生成 SHA256 清单。

### 3.2 单环境生产切换

**描述**：备份完成后，将现有单环境后端切到生产配置。

**验收标准**：

- WHEN 后端发布完成 THEN 容器 env 回读必须包含 `SPRING_PROFILES_ACTIVE=prod`。
- WHEN 后端发布完成 THEN 容器 env 回读必须包含 `NACOS_ENABLED=true`。
- WHEN 后端发布完成 THEN 生产 Nacos dataId 必须为 `kaipai-backend-prod.yml`。
- WHEN 后端发布完成 THEN 不再连接 `kaipai_dev`。

### 3.3 生产 smoke 与记录

**描述**：生产切换后必须执行后端和管理端公网 smoke，并写入发布记录。

**验收标准**：

- WHEN 发布完成 THEN `https://api.kplyyk.com/api/v3/api-docs` 必须通过。
- WHEN 发布完成 THEN `https://kplyyk.com/` 必须通过。
- WHEN 管理员 smoke 密码可用 THEN 后台登录 smoke 必须通过。
- WHEN 任一关键 smoke 失败 THEN 发布记录必须标记中止或回滚。

## 4. 非功能需求

- 本地备份目录必须位于 gitignored 路径。
- 不把数据库 dump、明文配置、密钥提交到仓库。
- 不再要求测试环境保留门禁。
- 切换前必须明确当前线上 `kaipai_dev` 数据不会自动进入 `kaipai_prod`，除非另行执行受控数据迁移。

## 5. 约束条件

- 本轮不再执行 `00-185` 双环境完成定义。
- 本轮仍必须遵守 `00-184` 生产发布 runbook 的备份、env、smoke 和记录要求。
