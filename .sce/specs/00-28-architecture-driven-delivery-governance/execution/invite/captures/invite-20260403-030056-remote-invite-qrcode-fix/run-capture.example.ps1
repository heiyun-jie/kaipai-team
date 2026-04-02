$actorToken = 'REPLACE_ACTOR_TOKEN'
$adminToken = 'REPLACE_ADMIN_TOKEN'

powershell -ExecutionPolicy Bypass -File `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\invite\collect-invite-evidence.ps1" `
  -ApiBaseUrl "http://101.43.57.62" `
  -ActorToken $actorToken `
  -AdminToken $adminToken `
  -InviteCode "SMK100" `
  -InviterUserId "10000" `
  -InviteeUserId "10014" `
  -ReferralId "8" `
  -GrantId "" `
  -PolicyId "1" `
  -OutputDir "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\invite\captures\invite-20260403-030056-remote-invite-qrcode-fix"
