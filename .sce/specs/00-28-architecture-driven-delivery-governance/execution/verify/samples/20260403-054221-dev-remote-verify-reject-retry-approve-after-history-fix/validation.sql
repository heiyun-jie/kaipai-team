SET @user_id = 10020;
SET @first_verification_id = 10;
SET @retry_verification_id = 11;

SELECT schema_release_history_id, script, checksum, applied_mode, applied_by, release_id, notes, created_at
FROM schema_release_history
WHERE script = 'V20260403_001__identity_verification_resubmit_history.sql'
ORDER BY schema_release_history_id DESC;

SELECT index_name, non_unique, seq_in_index, column_name
FROM information_schema.statistics
WHERE table_schema = DATABASE()
  AND table_name = 'identity_verification'
  AND index_name IN ('uk_identity_verification_id_card_hash', 'idx_identity_verification_id_card_hash')
ORDER BY index_name, seq_in_index;

SELECT user_id, phone, user_name, real_auth_status, create_time, last_update
FROM user
WHERE user_id = @user_id;

SELECT actor_profile_id, user_id, real_name, is_certified, create_time, last_update
FROM actor_profile
WHERE user_id = @user_id
ORDER BY actor_profile_id DESC;

SELECT verification_id, user_id, real_name, id_card_no_cipher, status, reject_reason, reviewer_id, reviewed_at, snapshot_profile_completion, create_time, last_update
FROM identity_verification
WHERE user_id = @user_id
ORDER BY verification_id DESC;

SELECT verification_id, user_id, real_name, id_card_no_cipher, status, reject_reason, reviewer_id, reviewed_at, snapshot_profile_completion, create_time, last_update
FROM identity_verification
WHERE verification_id = @first_verification_id;

SELECT verification_id, user_id, real_name, id_card_no_cipher, status, reject_reason, reviewer_id, reviewed_at, snapshot_profile_completion, create_time, last_update
FROM identity_verification
WHERE verification_id = @retry_verification_id;

SELECT owner_id, id_card_hash, user_id, create_time, last_update
FROM identity_verification_owner
WHERE user_id = @user_id
ORDER BY owner_id DESC;

SELECT operation_log_id, admin_user_id, admin_user_name, module_code, operation_code, target_type, target_id, operation_result, extra_context_json, create_time
FROM admin_operation_log
WHERE module_code = 'verify'
  AND target_type = 'identity_verification'
  AND target_id IN (@first_verification_id, @retry_verification_id)
ORDER BY operation_log_id DESC;

