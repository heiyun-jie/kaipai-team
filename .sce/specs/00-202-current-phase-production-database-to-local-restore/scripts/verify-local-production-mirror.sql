SET SESSION group_concat_max_len = 1000000;
USE kaipai_dev;

SELECT CONCAT('SOURCE_BASE_TABLE_COUNT=', COUNT(*))
FROM information_schema.tables
WHERE table_schema = 'kaipai_prod'
  AND table_type = 'BASE TABLE';

SELECT CONCAT('TARGET_BASE_TABLE_COUNT=', COUNT(*))
FROM information_schema.tables
WHERE table_schema = 'kaipai_dev'
  AND table_type = 'BASE TABLE';

SELECT CONCAT('TABLE_NAME_MISMATCH_COUNT=', COUNT(*))
FROM (
  SELECT source.table_name
  FROM information_schema.tables source
  LEFT JOIN information_schema.tables target
    ON target.table_schema = 'kaipai_dev'
   AND target.table_type = source.table_type
   AND target.table_name = source.table_name
  WHERE source.table_schema = 'kaipai_prod'
    AND target.table_name IS NULL
  UNION ALL
  SELECT target.table_name
  FROM information_schema.tables target
  LEFT JOIN information_schema.tables source
    ON source.table_schema = 'kaipai_prod'
   AND source.table_type = target.table_type
   AND source.table_name = target.table_name
  WHERE target.table_schema = 'kaipai_dev'
    AND source.table_name IS NULL
) mismatch;

SELECT CONCAT('COLUMN_DEFINITION_MISMATCH_COUNT=', COUNT(*))
FROM (
  SELECT source.table_name, source.column_name
  FROM information_schema.columns source
  LEFT JOIN information_schema.columns target
    ON target.table_schema = 'kaipai_dev'
   AND target.table_name = source.table_name
   AND target.column_name = source.column_name
  WHERE source.table_schema = 'kaipai_prod'
    AND (
      target.column_name IS NULL
      OR NOT (source.column_type <=> target.column_type)
      OR NOT (source.is_nullable <=> target.is_nullable)
      OR NOT (source.column_default <=> target.column_default)
      OR NOT (source.extra <=> target.extra)
      OR NOT (source.collation_name <=> target.collation_name)
    )
  UNION ALL
  SELECT target.table_name, target.column_name
  FROM information_schema.columns target
  LEFT JOIN information_schema.columns source
    ON source.table_schema = 'kaipai_prod'
   AND source.table_name = target.table_name
   AND source.column_name = target.column_name
  WHERE target.table_schema = 'kaipai_dev'
    AND source.column_name IS NULL
) mismatch;

CREATE TEMPORARY TABLE mirror_row_counts (
  table_name VARCHAR(128) NOT NULL,
  source_count BIGINT NOT NULL,
  target_count BIGINT NOT NULL
);

SELECT CONCAT(
  'INSERT INTO mirror_row_counts (table_name, source_count, target_count) ',
  GROUP_CONCAT(
    CONCAT(
      'SELECT ''', REPLACE(table_name, '''', ''''''), ''', ',
      '(SELECT COUNT(*) FROM `kaipai_prod`.`', REPLACE(table_name, '`', '``'), '`), ',
      '(SELECT COUNT(*) FROM `kaipai_dev`.`', REPLACE(table_name, '`', '``'), '`)'
    )
    ORDER BY table_name
    SEPARATOR ' UNION ALL '
  )
)
INTO @row_count_sql
FROM information_schema.tables
WHERE table_schema = 'kaipai_prod'
  AND table_type = 'BASE TABLE';

PREPARE row_count_stmt FROM @row_count_sql;
EXECUTE row_count_stmt;
DEALLOCATE PREPARE row_count_stmt;

SELECT CONCAT('ROW_COUNT_MISMATCH_COUNT=', COUNT(*))
FROM mirror_row_counts
WHERE source_count <> target_count;

SELECT CONCAT('ROW_COUNT_MISMATCH=', table_name, '|', source_count, '|', target_count)
FROM mirror_row_counts
WHERE source_count <> target_count
ORDER BY table_name;

SELECT CONCAT('SOURCE_VIEW_COUNT=', COUNT(*))
FROM information_schema.views
WHERE table_schema = 'kaipai_prod';

SELECT CONCAT('TARGET_VIEW_COUNT=', COUNT(*))
FROM information_schema.views
WHERE table_schema = 'kaipai_dev';

SELECT CONCAT('SOURCE_ROUTINE_COUNT=', COUNT(*))
FROM information_schema.routines
WHERE routine_schema = 'kaipai_prod';

SELECT CONCAT('TARGET_ROUTINE_COUNT=', COUNT(*))
FROM information_schema.routines
WHERE routine_schema = 'kaipai_dev';

SELECT CONCAT('SOURCE_TRIGGER_COUNT=', COUNT(*))
FROM information_schema.triggers
WHERE trigger_schema = 'kaipai_prod';

SELECT CONCAT('TARGET_TRIGGER_COUNT=', COUNT(*))
FROM information_schema.triggers
WHERE trigger_schema = 'kaipai_dev';

SELECT CONCAT('SOURCE_EVENT_COUNT=', COUNT(*))
FROM information_schema.events
WHERE event_schema = 'kaipai_prod';

SELECT CONCAT('TARGET_EVENT_COUNT=', COUNT(*))
FROM information_schema.events
WHERE event_schema = 'kaipai_dev';

SELECT CONCAT('LINXIA_USER_COUNT=', COUNT(*))
FROM kaipai_dev.`user`
WHERE user_id = 10007
  AND deleted = 0
  AND status = 1
  AND real_auth_status = 2;

SELECT CONCAT('LINXIA_ACTOR_PROFILE_COUNT=', COUNT(*))
FROM kaipai_dev.actor_profile
WHERE user_id = 10007
  AND deleted = 0
  AND is_certified = 1;

SELECT CONCAT('LINXIA_IDENTITY_BUCKET=', status, '|', deleted, '|', COUNT(*))
FROM kaipai_dev.identity_verification
WHERE user_id = 10007
GROUP BY status, deleted;

SELECT CONCAT('LINXIA_IDENTITY_OWNER_COUNT=', COUNT(*))
FROM kaipai_dev.identity_verification_owner
WHERE user_id = 10007
  AND deleted = 0;

SELECT CONCAT('LINXIA_SHARE_CARD_COUNT=', COUNT(*))
FROM kaipai_dev.user_share_card
WHERE user_id = 10007
  AND deleted = 0;
