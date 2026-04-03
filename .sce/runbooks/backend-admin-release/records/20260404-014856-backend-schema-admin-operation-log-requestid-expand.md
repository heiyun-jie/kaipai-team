# 后端 Schema 发布记录

## 1. 基本信息

- 发布批次号：`20260404-014856-backend-schema-admin-operation-log-requestid-expand`
- Schema History 发布批次号：`20260404-014856-backend-schema-admin-operation--a4443aacbe6af801`
- 发布时间：`2026-04-04 01:49:33 +0800`
- 发布范围：`backend-schema`
- 操作人：`codex`
- 执行模式：`apply`
- 关联 Spec / 需求：
  - `00-29 backend-admin-release-governance`
  - `05-09 identity-verification`

## 2. 目标环境

- 远端主机：`101.43.57.62`
- MySQL 容器：`kaipai-mysql`
- MySQL 数据库：`kaipai_dev`
- 远端 helper：`/usr/local/bin/kaipai-backend-release-helper.sh`

## 3. 执行文件

- `V20260404_001__admin_operation_log_request_id_expand.sql`
  - mode: `apply`
  - checksum: `6E577F2984216288ED7223FA3DEE43C0F49F47A57C7A1ED3506EFC55EC3A4299`
  - status: `applied`
  - remote date: `2026-04-04 01:49:32 +0800`

## 4. 结论

- 最终结论：`完成`
- 后续动作：
  - 若本批包含后端代码发布，必须在 schema 完成后再执行标准 `backend-only`
  - 后续所有涉及 `db/migration` 的后端发布，必须先走本脚本或由 `backend-only` 前置门禁拦截
