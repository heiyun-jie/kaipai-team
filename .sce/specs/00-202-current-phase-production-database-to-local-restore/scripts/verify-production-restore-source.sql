SELECT CONCAT('DATABASE_NAME=', DATABASE());

SELECT CONCAT('TABLE_COUNT=', COUNT(*))
FROM information_schema.tables
WHERE table_schema = DATABASE()
  AND table_type = 'BASE TABLE';

SELECT CONCAT('ACTIVE_USER_COUNT=', COUNT(*))
FROM `user`
WHERE deleted = 0;

SELECT CONCAT('LINXIA_USER_COUNT=', COUNT(*))
FROM `user`
WHERE user_id = 10007
  AND deleted = 0
  AND status = 1
  AND real_auth_status = 2;

SELECT CONCAT(
  'LINXIA_USER=',
  user_id, '|',
  LEFT(phone, 3), '****', RIGHT(phone, 4), '|',
  COALESCE(user_name, ''), '|',
  real_auth_status
)
FROM `user`
WHERE user_id = 10007
  AND deleted = 0;

SELECT CONCAT('LINXIA_ACTOR_PROFILE_COUNT=', COUNT(*))
FROM actor_profile
WHERE user_id = 10007
  AND deleted = 0
  AND is_certified = 1;

SELECT CONCAT('LINXIA_PROFILE_NAME_MATCH_COUNT=', COUNT(*))
FROM actor_profile
WHERE user_id = 10007
  AND deleted = 0
  AND (nick_name = '林夏' OR real_name = '林夏');

SELECT CONCAT('LINXIA_IDENTITY_TOTAL_COUNT=', COUNT(*))
FROM identity_verification
WHERE user_id = 10007;

SELECT CONCAT(
  'LINXIA_IDENTITY_BUCKET=',
  COALESCE(status, -1), '|',
  COALESCE(deleted, -1), '|',
  COUNT(*)
)
FROM identity_verification
WHERE user_id = 10007
GROUP BY status, deleted
ORDER BY status, deleted;

SELECT CONCAT(
  'LINXIA_IDENTITY_TIMELINE=',
  verification_id, '|',
  COALESCE(provider_code, ''), '|',
  COALESCE(provider_result_code, ''), '|',
  COALESCE(DATE_FORMAT(provider_verified_at, '%Y-%m-%d %H:%i:%s'), ''), '|',
  COALESCE(DATE_FORMAT(reviewed_at, '%Y-%m-%d %H:%i:%s'), ''), '|',
  COALESCE(DATE_FORMAT(create_time, '%Y-%m-%d %H:%i:%s'), ''), '|',
  COALESCE(DATE_FORMAT(last_update, '%Y-%m-%d %H:%i:%s'), '')
)
FROM identity_verification
WHERE user_id = 10007
ORDER BY create_time, verification_id;

SELECT CONCAT('LINXIA_APPROVED_IDENTITY_COUNT=', COUNT(*))
FROM identity_verification
WHERE user_id = 10007
  AND deleted = 0
  AND status = 2;

SELECT CONCAT('LINXIA_IDENTITY_OWNER_COUNT=', COUNT(*))
FROM identity_verification_owner
WHERE user_id = 10007
  AND deleted = 0;

SELECT CONCAT('LINXIA_SHARE_CARD_COUNT=', COUNT(*))
FROM user_share_card
WHERE user_id = 10007
  AND deleted = 0;

SELECT CONCAT('LINXIA_VERIFY_AUDIT_COUNT=', COUNT(*))
FROM admin_operation_log
WHERE module_code = 'verify'
  AND target_type = 'identity_verification'
  AND target_id = 14
  AND deleted = 0;

SELECT CONCAT(
  'LINXIA_VERIFY_AUDIT=',
  operation_code, '|',
  operation_result, '|',
  COALESCE(DATE_FORMAT(create_time, '%Y-%m-%d %H:%i:%s'), '')
)
FROM admin_operation_log
WHERE module_code = 'verify'
  AND target_type = 'identity_verification'
  AND target_id = 14
  AND deleted = 0
ORDER BY create_time, operation_log_id;

SELECT CONCAT('REALNAME_COMPAT_COLUMN_COUNT=', COUNT(*))
FROM information_schema.columns
WHERE table_schema = DATABASE()
  AND table_name = 'identity_verification'
  AND column_name IN (
    'id_card_no_masked',
    'provider_code',
    'provider_request_id',
    'provider_result_code',
    'provider_result_message',
    'provider_verified_at'
  );
