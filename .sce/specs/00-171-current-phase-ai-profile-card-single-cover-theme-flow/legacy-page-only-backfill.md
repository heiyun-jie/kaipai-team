# 历史 page-only 数据补齐审查

> 状态：目标环境只读盘点已完成，候选数为 `0`
> 目标：只处理旧三页历史数据中 `actor_ai_profile_card_task.generated_image_url` 为空、但 `actor_ai_profile_card_page` 存在成功 `cover` 图的缺口。

## 1. 当前结论

目标环境只读盘点已执行，证据目录：

```text
.sce/runbooks/backend-admin-release/records/diagnostics/20260520-230700-ai-profile-card-page-only-inventory/
```

结论：

- `helperFinalStatus = passed`
- `pageOnlyCoverCount = 0`
- `sampleRows = 0`
- 不需要新增 forward migration。
- 不需要执行图片 re-host 运维脚本。
- 前端详情页 legacy `pages` cover fallback 已删除，成功图只依赖 task/artifact-level `generatedImageUrl`。

## 2. 候选数据盘点 SQL

```sql
SELECT COUNT(*) AS page_only_cover_count
FROM actor_ai_profile_card_task t
JOIN actor_ai_profile_card_page p
  ON p.task_id = t.task_id
WHERE t.deleted = 0
  AND p.deleted = 0
  AND t.status = 'success'
  AND t.share_card_id IS NOT NULL
  AND TRIM(COALESCE(t.generated_image_url, '')) = ''
  AND p.status = 'success'
  AND p.page_type = 'cover'
  AND p.page_no = 1
  AND TRIM(COALESCE(p.generated_image_url, '')) <> ''
  AND COALESCE(LOWER(t.provider_code), '') <> 'mock'
  AND (
    p.share_card_id IS NULL
    OR p.share_card_id = t.share_card_id
  )
  AND (
    TRIM(COALESCE(t.source_image_url, '')) = ''
    OR SUBSTRING_INDEX(TRIM(p.generated_image_url), '?', 1)
        <> SUBSTRING_INDEX(TRIM(t.source_image_url), '?', 1)
  );
```

抽样 SQL：

```sql
SELECT
  t.task_id,
  t.user_id,
  t.share_card_id AS task_share_card_id,
  p.share_card_id AS page_share_card_id,
  t.status AS task_status,
  p.status AS page_status,
  t.source_image_url,
  p.generated_image_url AS cover_generated_image_url,
  t.create_time
FROM actor_ai_profile_card_task t
JOIN actor_ai_profile_card_page p
  ON p.task_id = t.task_id
WHERE t.deleted = 0
  AND p.deleted = 0
  AND t.status = 'success'
  AND t.share_card_id IS NOT NULL
  AND TRIM(COALESCE(t.generated_image_url, '')) = ''
  AND p.status = 'success'
  AND p.page_type = 'cover'
  AND p.page_no = 1
  AND TRIM(COALESCE(p.generated_image_url, '')) <> ''
  AND COALESCE(LOWER(t.provider_code), '') <> 'mock'
  AND (
    p.share_card_id IS NULL
    OR p.share_card_id = t.share_card_id
  )
  AND (
    TRIM(COALESCE(t.source_image_url, '')) = ''
    OR SUBSTRING_INDEX(TRIM(p.generated_image_url), '?', 1)
        <> SUBSTRING_INDEX(TRIM(t.source_image_url), '?', 1)
  )
ORDER BY t.create_time DESC
LIMIT 50;
```

## 3. 只读盘点入口与证据模板

正式入口：

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-ai-profile-card-page-only-inventory.py --operator <operator> --mysql-database <target_database> --mysql-container <target_mysql_container>
```

执行前必须先建立目标环境的批准会话；不得在未确认会话/权限边界前请求或粘贴受保护行数据。

脚本默认数据库参数仅是开发环境便利值；开发库结果不能关闭 Phase 5 的线上/准线上盘点项，也不能批准移除前端 fallback。

`--template-only` 只生成查询和记录骨架，不生成 `remote-helper-command.txt`、`raw-mysql-output.txt`、`result-count.txt` 或 `sample.tsv`，不能作为执行证据。

执行记录目录：

```text
.sce/runbooks/backend-admin-release/records/diagnostics/<timestamp>-ai-profile-card-page-only-inventory/
```

证据文件要求：

- `query-count.sql`：候选 count SQL。
- `query-sample.sql`：与 count 条件一致的抽样 SQL。
- `query-inventory.sql`：脚本实际上传执行的只读 marker SQL。
- `remote-helper-command.txt`：实际调用的标准 helper 命令。
- `raw-mysql-output.txt`：远端 MySQL 原始输出。
- `result-count.txt`：候选 count。
- `sample.tsv`：抽样行，不需要提交敏感字段到对话上下文。
- `summary.json`：环境、操作人、时间、count 和样本数量。
- `README.md`：人工审查结论和完成门禁。

人工审查字段必须包含批准会话、审查人、抽样是否已审、审查结论和是否批准移除 fallback；脚本状态 `executed` 只表示只读盘点已执行，不表示完成门禁已通过。

## 4. 执行门槛

只有满足以下任一条件时，才能关闭 Phase 5 最后一项：

1. 线上或准线上候选数为 `0`，并已记录盘点证据。
2. 候选数大于 `0`，已通过 forward migration 或运维脚本补齐，补齐后候选数为 `0`，并抽样确认 API 返回 task-level `generatedImageUrl`。

## 5. 可选 SQL Backfill

如果抽样确认历史 cover page 的 `generated_image_url` 是稳定可用的受管 URL，可以使用新的 forward migration 或受控运维脚本执行：

```sql
UPDATE actor_ai_profile_card_task t
JOIN actor_ai_profile_card_page p
  ON p.task_id = t.task_id
SET
  t.generated_image_url = TRIM(p.generated_image_url),
  t.version = t.version + 1
WHERE t.deleted = 0
  AND p.deleted = 0
  AND t.status = 'success'
  AND t.share_card_id IS NOT NULL
  AND TRIM(COALESCE(t.generated_image_url, '')) = ''
  AND p.status = 'success'
  AND p.page_type = 'cover'
  AND p.page_no = 1
  AND TRIM(COALESCE(p.generated_image_url, '')) <> ''
  AND COALESCE(LOWER(t.provider_code), '') <> 'mock'
  AND (
    p.share_card_id IS NULL
    OR p.share_card_id = t.share_card_id
  )
  AND (
    TRIM(COALESCE(t.source_image_url, '')) = ''
    OR SUBSTRING_INDEX(TRIM(p.generated_image_url), '?', 1)
        <> SUBSTRING_INDEX(TRIM(t.source_image_url), '?', 1)
  );
```

该 SQL 不得修改任务状态，不得创建分享卡，不得从 `resume / gallery` 回推封面，不得覆盖已有 task-level `generated_image_url`。

如果历史 cover page URL 可能是 provider 临时 URL，则不能只做 SQL copy，应使用后端运维脚本先 re-host 图片，再更新 task。

## 6. 前端 Fallback 移除门禁

前端详情页的 legacy `pages` cover fallback 只能在以下条件之一满足后移除：

1. 线上或准线上 page-only 候选数为 `0`，且证据目录已记录。
2. 已完成 forward migration 或 re-host 运维脚本，post-count 为 `0`，并抽样确认 artifact API 返回 task-level `generatedImageUrl`。

本轮已满足第 1 条：目标环境 page-only 候选数为 `0`，且证据目录已记录。前端详情页的 legacy `pages` cover fallback 已删除。

如果后续其它环境 count 未执行、count 大于 `0`、或仅有静态代码审查结论，前端 fallback 不得在对应环境提前移除。

`tasks.md` 中“新增只读盘点脚本/runbook”被勾选只代表仓库内入口和模板已补齐，不是线上/准线上数据盘点完成证据。

## 7. 验证要求

执行前：

1. 记录候选 count。
2. 抽样检查 cover URL、task 状态和 share card 关联。

执行后：

1. 候选 count 必须为 `0`。
2. 前端详情页不再读取 `pages` cover fallback，成功图只来自 task/artifact-level `generatedImageUrl`。
3. 回归前端类型检查和小程序构建。
