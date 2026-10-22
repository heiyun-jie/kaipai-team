SELECT
  task_id,
  generation_mode,
  status,
  source_image_url IS NULL AS source_image_url_is_null,
  failure_reason IS NULL AS failure_reason_is_null,
  create_time,
  last_update
FROM actor_ai_profile_card_task
WHERE generation_mode = 'actor_card_generate'
ORDER BY create_time DESC
LIMIT 3;
