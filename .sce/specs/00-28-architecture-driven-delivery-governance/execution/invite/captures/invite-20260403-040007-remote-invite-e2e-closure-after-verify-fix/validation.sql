-- Invite validation template
-- Usage:
-- 1. Replace the placeholder values below.
-- 2. Execute only against the target validation environment.
-- 3. Keep the result set together with the sample ledger.

SET @invite_code = 'SMK100';
SET @inviter_user_id = 10000;
SET @invitee_user_id = 10017;
SET @referral_id = 11;
SET @grant_id = 2;
SET @policy_id = 1;

-- 1) Invite code master record
SELECT
  invite_code_id,
  user_id,
  code,
  status,
  create_time,
  last_update
FROM invite_code
WHERE code = UPPER(@invite_code);

-- 2) Inviter user snapshot
SELECT
  user_id,
  user_name,
  phone,
  real_auth_status,
  valid_invite_count,
  register_device_fingerprint,
  create_time,
  last_login_time
FROM user
WHERE (@inviter_user_id IS NOT NULL AND user_id = @inviter_user_id)
   OR (@invite_code <> '' AND user_id IN (
        SELECT user_id
        FROM invite_code
        WHERE code = UPPER(@invite_code)
      ));

-- 3) Invitee user snapshot
SELECT
  user_id,
  user_name,
  phone,
  invited_by_user_id,
  valid_invite_count,
  register_device_fingerprint,
  real_auth_status,
  create_time,
  last_login_time
FROM user
WHERE (@invitee_user_id IS NOT NULL AND user_id = @invitee_user_id);

-- 4) Referral records bound to the sample chain
SELECT
  referral_id,
  inviter_user_id,
  invitee_user_id,
  invite_code_id,
  invite_code_snapshot,
  register_device_fingerprint,
  status,
  risk_flag,
  risk_reason,
  registered_at,
  validated_at,
  create_time,
  last_update
FROM referral_record
WHERE (@referral_id IS NOT NULL AND referral_id = @referral_id)
   OR (@invitee_user_id IS NOT NULL AND invitee_user_id = @invitee_user_id)
   OR (@inviter_user_id IS NOT NULL AND inviter_user_id = @inviter_user_id)
   OR (@invite_code <> '' AND invite_code_snapshot = UPPER(@invite_code))
ORDER BY referral_id DESC;

-- 5) Referral status aggregation for the inviter
SELECT
  inviter_user_id,
  invite_code_snapshot,
  COUNT(*) AS total_count,
  SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) AS pending_count,
  SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) AS valid_count,
  SUM(CASE WHEN status = 2 THEN 1 ELSE 0 END) AS invalid_count,
  SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END) AS review_count,
  SUM(CASE WHEN risk_flag = 1 THEN 1 ELSE 0 END) AS flagged_count
FROM referral_record
WHERE (@inviter_user_id IS NOT NULL AND inviter_user_id = @inviter_user_id)
   OR (@invite_code <> '' AND invite_code_snapshot = UPPER(@invite_code))
GROUP BY inviter_user_id, invite_code_snapshot
ORDER BY inviter_user_id, invite_code_snapshot;

-- 6) Entitlement grants tied to the invitee or referral source
SELECT
  grant_id,
  user_id,
  grant_type,
  grant_code,
  status,
  effective_time,
  expire_time,
  source_type,
  source_ref_id,
  remark,
  create_user_id,
  create_user_name,
  create_time,
  update_user_id,
  update_user_name,
  last_update
FROM user_entitlement_grant
WHERE (@grant_id IS NOT NULL AND grant_id = @grant_id)
   OR (@invitee_user_id IS NOT NULL AND user_id = @invitee_user_id)
   OR (@referral_id IS NOT NULL AND source_ref_id = @referral_id)
ORDER BY grant_id DESC;

-- 7) Policy records
SELECT
  policy_id,
  policy_name,
  enabled,
  require_real_auth,
  require_profile_completion,
  profile_completion_threshold,
  same_device_limit,
  hourly_invite_limit,
  auto_grant_enabled,
  grant_rule_json,
  create_user_id,
  create_user_name,
  create_time,
  update_user_id,
  update_user_name,
  last_update
FROM referral_policy
WHERE (@policy_id IS NOT NULL AND policy_id = @policy_id)
ORDER BY policy_id DESC;

-- 8) Referral operation logs
SELECT
  operation_log_id,
  admin_user_id,
  admin_user_name,
  module_code,
  operation_code,
  target_type,
  target_id,
  operation_result,
  before_snapshot_json,
  after_snapshot_json,
  extra_context_json,
  create_time
FROM admin_operation_log
WHERE module_code = 'referral'
  AND (
    (@referral_id IS NOT NULL AND target_type = 'referral_record' AND target_id = @referral_id)
    OR (@grant_id IS NOT NULL AND target_type = 'user_entitlement_grant' AND target_id = @grant_id)
    OR (@policy_id IS NOT NULL AND target_type = 'referral_policy' AND target_id = @policy_id)
  )
ORDER BY operation_log_id DESC;
