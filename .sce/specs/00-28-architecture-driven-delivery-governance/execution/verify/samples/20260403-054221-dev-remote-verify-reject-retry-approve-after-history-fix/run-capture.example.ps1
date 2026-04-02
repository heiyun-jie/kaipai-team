$actorToken = 'REPLACE_ACTOR_TOKEN'
$adminToken = 'REPLACE_ADMIN_TOKEN'

powershell -ExecutionPolicy Bypass -File `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\verify\collect-verify-evidence.ps1" `
  -ApiBaseUrl "http://101.43.57.62" `
  -ActorToken $actorToken `
  -AdminToken $adminToken `
  -UserId "10020" `
  -VerificationId "10" `
  -RetryVerificationId "11" `
  -OutputDir "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\verify\samples\20260403-054221-dev-remote-verify-reject-retry-approve-after-history-fix"
