SELECT
  TABLE_NAME,
  COLUMN_NAME,
  IS_NULLABLE,
  COLUMN_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND (
    (TABLE_NAME = 'actor_ai_profile_card_task' AND COLUMN_NAME IN (
      'source_image_url', 'actor_card_id', 'source_asset_id', 'source_fingerprint'
    ))
    OR (TABLE_NAME = 'actor_card' AND COLUMN_NAME = 'expanded_source_fingerprint')
  )
ORDER BY TABLE_NAME, ORDINAL_POSITION;

SELECT
  INDEX_NAME,
  NON_UNIQUE,
  SEQ_IN_INDEX,
  COLUMN_NAME
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'actor_ai_profile_card_task'
  AND INDEX_NAME = 'uk_actor_card_expand_source'
ORDER BY SEQ_IN_INDEX;
