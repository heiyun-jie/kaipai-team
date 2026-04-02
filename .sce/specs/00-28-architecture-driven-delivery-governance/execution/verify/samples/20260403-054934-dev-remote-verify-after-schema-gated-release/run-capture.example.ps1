$actorToken = 'REPLACE_ACTOR_TOKEN'
$adminToken = 'REPLACE_ADMIN_TOKEN'

powershell -ExecutionPolicy Bypass -File `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\verify\collect-verify-evidence.ps1" `
  -ApiBaseUrl "http://101.43.57.62" `
  -ActorToken $actorToken `
  -AdminToken $adminToken `
  -UserId "10021" `
  -VerificationId "12" `
  -RetryVerificationId "13" `
  -OutputDir "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\verify\samples\20260403-054934-dev-remote-verify-after-schema-gated-release"
