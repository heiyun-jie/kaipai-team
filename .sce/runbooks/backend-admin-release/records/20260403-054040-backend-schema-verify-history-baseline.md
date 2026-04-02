# 后端 Schema 发布记录

## 1. 基本信息

- 发布批次号：`20260403-054040-backend-schema-verify-history-baseline`
- 发布时间：`2026-04-03 05:41:23 +0800`
- 发布范围：`backend-schema`
- 操作人：`codex`
- 执行模式：`baseline-existing`
- 关联 Spec / 需求：
  - `00-29 backend-admin-release-governance`
  - `05-09 identity-verification`

## 2. 目标环境

- 远端主机：`101.43.57.62`
- MySQL 容器：`kaipai-mysql`
- MySQL 数据库：`kaipai_dev`
- 远端 helper：`/usr/local/bin/kaipai-backend-release-helper.sh`

## 3. 执行文件

- `V20260331_001__platform_admin_baseline.sql`
  - mode: `baseline`
  - checksum: `2F551ECF05D4CDC3CF29E04B9F325AB078FB17D0787499D8306AD4A8590C5AC9`
  - status: `applied`
  - remote date: `2026-04-03 05:41:12 +0800`
- `V20260331_002__platform_admin_governance_alignment.sql`
  - mode: `baseline`
  - checksum: `FE45B01726F7019860FF34902A36CD90B5A6BD0CDCC4DDED0147C83C0E63D316`
  - status: `applied`
  - remote date: `2026-04-03 05:41:21 +0800`

## 4. 结论

- 最终结论：`完成`
- 后续动作：
  - 若本批包含后端代码发布，必须在 schema 完成后再执行标准 `backend-only`
  - 后续所有涉及 `db/migration` 的后端发布，必须先走本脚本或由 `backend-only` 前置门禁拦截
