# 后端 Schema 发布记录

## 1. 基本信息

- 发布批次号：`20260403-054130-backend-schema-verify-resubmit-history-fix`
- 发布时间：`2026-04-03 05:42:02 +0800`
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

- `V20260403_001__identity_verification_resubmit_history.sql`
  - mode: `apply`
  - checksum: `A25D2B032DBAA86CA41BE64C90233CCBCE919040559CE3ED30E0BAFB285D6DA1`
  - status: `applied`
  - remote date: `2026-04-03 05:42:01 +0800`

## 4. 结论

- 最终结论：`完成`
- 后续动作：
  - 若本批包含后端代码发布，必须在 schema 完成后再执行标准 `backend-only`
  - 后续所有涉及 `db/migration` 的后端发布，必须先走本脚本或由 `backend-only` 前置门禁拦截
