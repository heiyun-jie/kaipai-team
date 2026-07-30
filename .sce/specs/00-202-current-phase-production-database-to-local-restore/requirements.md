# 00-202 当前阶段生产数据库恢复到本地

## 1. 概述

本地小程序连接 `127.0.0.1:8010`，后端连接本机 Docker MySQL `kaipai_dev`。只读诊断确认，本地尾号 6737 的账号是 `userId=8` 空壳用户，而生产 `kaipai_prod` 中同一手机号已经绑定到林夏 `userId=10007`，并具有演员档案、实名记录和分享资产。

本 Spec 将生产 `kaipai_prod` 做一致性只读导出，经过 SHA256、gzip 和暂存库验证后，全量恢复为本地 `kaipai_dev`。远程生产库不得发生写操作；本地原库必须先生成可恢复 dump。

## 2. 用户故事

作为本地开发者，我希望本地数据库与当前生产数据一致，以便尾号 6737 登录后访问林夏账号、实名状态和相关资产。

作为运维人员，我希望替换本地数据库前保留原库备份，并能在导入失败时恢复到执行前状态。

## 3. 功能需求

### 3.1 远程来源唯一性预检

- WHEN 执行导出前 THEN 远程主机必须为 `101.43.57.62`，MySQL 容器必须为 `kaipai-mysql`，源库必须为 `kaipai_prod`。
- WHEN 预检林夏锚点 THEN `userId=10007`、用户实名标志 `2`、已认证演员档案、实名申请和实名归属必须唯一存在。
- WHEN 源库实名申请状态与用户 / 演员认证状态不一致 THEN 必须记录原始状态；纯镜像恢复可以继续，但不得宣称该不一致已修复。
- WHEN 任一来源门禁失败 THEN 不得生成替换本地库的恢复动作。

### 3.2 双备份与完整性

- WHEN 替换本地库前 THEN 当前本地 `kaipai_dev` 必须导出为 gzip dump。
- WHEN 远程导出完成 THEN 必须下载生产 gzip dump，并校验远程/本地 SHA256 一致。
- WHEN 任一 gzip 校验失败 THEN 不得导入。
- WHEN 生成备份 THEN dump、日志和哈希清单必须位于 gitignored 的本地备份目录。

### 3.3 暂存恢复与本地替换

- WHEN 生产 dump 下载完成 THEN 先恢复到本地暂存库 `kaipai_prod` 并执行计数和林夏锚点验证。
- WHEN 暂存验证通过 THEN 停止本地后端，重建本地 `kaipai_dev` 并从已验证暂存库复制完整 schema、数据、视图、触发器、存储过程和事件。
- WHEN 本地替换失败 THEN 使用执行前本地 dump 恢复 `kaipai_dev`。

### 3.4 恢复后验证

- WHEN 本地恢复完成 THEN `kaipai_dev` 的表数、用户数及关键业务计数必须与本地暂存 `kaipai_prod` 一致。
- WHEN 查询尾号 6737 账号 THEN 唯一有效用户必须为 `userId=10007`，实名状态必须为 `2`。
- WHEN 查询林夏资产 THEN 有效演员档案、实名申请、实名归属和分享卡必须存在，状态桶必须与源库一致。
- WHEN 源库实名申请为待审状态 THEN 最终本地镜像必须先保持同一状态；任何本地一致性修复必须独立备份、独立记录，不得混入镜像恢复。
- WHEN 本地后端重启 THEN `/api/doc.html` 必须返回 HTTP 200。
- WHEN 旧小程序 token 仍指向 `userId=8` THEN 必须清理本地登录态并重新登录，不得把旧 token 当作恢复失败。

## 4. 非功能需求

- 生产库只读，使用 `mysqldump --single-transaction --routines --triggers --events`。
- 不在 Spec、执行日志或聊天中记录完整手机号、身份证号、密文、JWT、验证码或数据库密码。
- 不直接执行单字段 `real_auth_status=2` 修补；实名用户、申请、归属和演员档案必须保持一致。
- 本地恢复期间允许短暂停止本地后端，但不得影响生产运行态。

## 5. 约束条件

- 源：`kaipaile@101.43.57.62` / `kaipai-mysql` / `kaipai_prod`。
- 目标：本机 Docker `kaipai-mysql-local` / `kaipai_dev`。
- 本轮不修改前端、管理端或后端源码。
- 本轮不提交任何数据库 dump。
