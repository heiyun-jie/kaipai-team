$ErrorActionPreference = 'Stop'

param(
  [Parameter(Mandatory = $true)]
  [string]$ApiBaseUrl,

  [string]$ActorToken,
  [string]$AdminToken,
  [string]$InviteCode,
  [string]$InviterUserId,
  [string]$InviteeUserId,
  [string]$ReferralId,
  [string]$GrantId,
  [string]$PolicyId,
  [string]$OutputDir
)

function Normalize-BaseUrl {
  param([string]$BaseUrl)
  if ($null -eq $BaseUrl) {
    return ''
  }
  $normalized = $BaseUrl.Trim().TrimEnd('/')
  if ($normalized.EndsWith('/api')) {
    return $normalized.Substring(0, $normalized.Length - 4)
  }
  return $normalized
}

function Ensure-Directory {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path | Out-Null
  }
}

function Write-JsonFile {
  param(
    [string]$Path,
    [object]$Value
  )
  $json = $Value | ConvertTo-Json -Depth 20
  Set-Content -LiteralPath $Path -Value $json -Encoding UTF8
}

function Write-TextFile {
  param(
    [string]$Path,
    [string[]]$Lines
  )
  Set-Content -LiteralPath $Path -Value $Lines -Encoding UTF8
}

function Copy-TemplateFile {
  param(
    [string]$SourcePath,
    [string]$DestinationPath
  )
  if (Test-Path -LiteralPath $SourcePath) {
    Copy-Item -LiteralPath $SourcePath -Destination $DestinationPath -Force
  }
}

function New-Headers {
  param([string]$Token)
  $headers = @{
    'Accept' = 'application/json'
  }
  if ($Token) {
    $headers['Authorization'] = "Bearer $Token"
  }
  return $headers
}

function Invoke-Capture {
  param(
    [string]$Name,
    [string]$Method,
    [string]$Url,
    [hashtable]$Headers,
    [string]$CaptureDir
  )

  $safeName = $Name -replace '[^a-zA-Z0-9._-]', '_'
  $outputPath = Join-Path $CaptureDir "$safeName.json"

  try {
    $response = Invoke-RestMethod -Method $Method -Uri $Url -Headers $Headers
    Write-JsonFile -Path $outputPath -Value $response
    return @{
      name = $Name
      status = 'ok'
      url = $Url
      output = $outputPath
    }
  } catch {
    $errorPayload = @{
      name = $Name
      url = $Url
      message = $_.Exception.Message
      detail = $_ | Out-String
    }
    Write-JsonFile -Path $outputPath -Value $errorPayload
    return @{
      name = $Name
      status = 'error'
      url = $Url
      output = $outputPath
      message = $_.Exception.Message
    }
  }
}

function Add-Endpoint {
  param(
    [System.Collections.Generic.List[hashtable]]$Targets,
    [string]$Name,
    [string]$Method,
    [string]$Url,
    [string]$TokenType
  )
  $Targets.Add(@{
      name = $Name
      method = $Method
      url = $Url
      tokenType = $TokenType
    })
}

$baseUrl = Normalize-BaseUrl -BaseUrl $ApiBaseUrl
if (-not $baseUrl) {
  throw 'ApiBaseUrl 不能为空。'
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$captureRoot = if ($OutputDir) { $OutputDir } else { Join-Path $scriptDir "captures\invite-$timestamp" }
$captureRoot = [System.IO.Path]::GetFullPath($captureRoot)
$ledgerTemplatePath = Join-Path $scriptDir 'validation-sample-ledger-template.md'
$sqlTemplatePath = Join-Path $scriptDir 'invite-validation-template.sql'

Ensure-Directory -Path $captureRoot
Copy-TemplateFile -SourcePath $ledgerTemplatePath -DestinationPath (Join-Path $captureRoot 'sample-ledger.md')
Copy-TemplateFile -SourcePath $sqlTemplatePath -DestinationPath (Join-Path $captureRoot 'validation.sql')

$actorHeaders = New-Headers -Token $ActorToken
$adminHeaders = New-Headers -Token $AdminToken

$context = @{
  capturedAt = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  apiBaseUrl = $baseUrl
  inviteCode = $InviteCode
  inviterUserId = $InviterUserId
  inviteeUserId = $InviteeUserId
  referralId = $ReferralId
  grantId = $GrantId
  policyId = $PolicyId
  actorTokenProvided = [bool]$ActorToken
  adminTokenProvided = [bool]$AdminToken
  outputDir = $captureRoot
}
Write-JsonFile -Path (Join-Path $captureRoot 'capture-context.json') -Value $context

$targets = New-Object 'System.Collections.Generic.List[hashtable]'

if ($ActorToken) {
  Add-Endpoint -Targets $targets -Name 'actor_invite_code' -Method 'GET' -Url "$baseUrl/api/invite/code" -TokenType 'actor'
  Add-Endpoint -Targets $targets -Name 'actor_invite_stats' -Method 'GET' -Url "$baseUrl/api/invite/stats" -TokenType 'actor'
  Add-Endpoint -Targets $targets -Name 'actor_invite_records' -Method 'GET' -Url "$baseUrl/api/invite/records" -TokenType 'actor'
  Add-Endpoint -Targets $targets -Name 'actor_invite_qrcode' -Method 'GET' -Url "$baseUrl/api/invite/qrcode" -TokenType 'actor'
  Add-Endpoint -Targets $targets -Name 'actor_level_info' -Method 'GET' -Url "$baseUrl/api/level/info" -TokenType 'actor'
}

if ($AdminToken) {
  Add-Endpoint -Targets $targets -Name 'admin_referral_policies' -Method 'GET' -Url "$baseUrl/api/admin/referral/policies?pageNo=1&pageSize=20" -TokenType 'admin'

  if ($InviteCode) {
    $encodedInviteCode = [System.Uri]::EscapeDataString($InviteCode.Trim().ToUpper())
    Add-Endpoint -Targets $targets -Name 'admin_referral_records_by_invite_code' -Method 'GET' -Url "$baseUrl/api/admin/referral/records?pageNo=1&pageSize=20&inviteCode=$encodedInviteCode" -TokenType 'admin'
    Add-Endpoint -Targets $targets -Name 'admin_referral_risk_by_invite_code' -Method 'GET' -Url "$baseUrl/api/admin/referral/risk/list?pageNo=1&pageSize=20&inviteCode=$encodedInviteCode" -TokenType 'admin'
  }

  if ($InviterUserId) {
    Add-Endpoint -Targets $targets -Name 'admin_referral_records_by_inviter' -Method 'GET' -Url "$baseUrl/api/admin/referral/records?pageNo=1&pageSize=20&inviterUserId=$InviterUserId" -TokenType 'admin'
  }

  if ($InviteeUserId) {
    Add-Endpoint -Targets $targets -Name 'admin_referral_records_by_invitee' -Method 'GET' -Url "$baseUrl/api/admin/referral/records?pageNo=1&pageSize=20&inviteeUserId=$InviteeUserId" -TokenType 'admin'
    Add-Endpoint -Targets $targets -Name 'admin_referral_eligibility_by_user' -Method 'GET' -Url "$baseUrl/api/admin/referral/eligibility?pageNo=1&pageSize=20&userId=$InviteeUserId" -TokenType 'admin'
  }

  if ($ReferralId) {
    Add-Endpoint -Targets $targets -Name 'admin_referral_record_detail' -Method 'GET' -Url "$baseUrl/api/admin/referral/records/$ReferralId" -TokenType 'admin'
    Add-Endpoint -Targets $targets -Name 'admin_referral_risk_detail' -Method 'GET' -Url "$baseUrl/api/admin/referral/risk/$ReferralId" -TokenType 'admin'
  }

  if ($GrantId) {
    Add-Endpoint -Targets $targets -Name 'admin_referral_eligibility_detail' -Method 'GET' -Url "$baseUrl/api/admin/referral/eligibility/$GrantId" -TokenType 'admin'
  }

  if ($PolicyId) {
    Add-Endpoint -Targets $targets -Name 'admin_referral_policy_detail' -Method 'GET' -Url "$baseUrl/api/admin/referral/policies/$PolicyId" -TokenType 'admin'
  }
}

$results = New-Object 'System.Collections.Generic.List[hashtable]'
foreach ($target in $targets) {
  $headers = if ($target.tokenType -eq 'admin') { $adminHeaders } else { $actorHeaders }
  $result = Invoke-Capture -Name $target.name -Method $target.method -Url $target.url -Headers $headers -CaptureDir $captureRoot
  $results.Add($result)
}

$summaryLines = New-Object 'System.Collections.Generic.List[string]'
$summaryLines.Add("captureDir=$captureRoot")
$summaryLines.Add("capturedAt=$($context.capturedAt)")
$summaryLines.Add("apiBaseUrl=$baseUrl")
$summaryLines.Add("inviteCode=$InviteCode")
$summaryLines.Add("inviterUserId=$InviterUserId")
$summaryLines.Add("inviteeUserId=$InviteeUserId")
$summaryLines.Add("referralId=$ReferralId")
$summaryLines.Add("grantId=$GrantId")
$summaryLines.Add("policyId=$PolicyId")
$summaryLines.Add('')

foreach ($result in $results) {
  $line = "[{0}] {1} -> {2}" -f $result.status.ToUpperInvariant(), $result.name, $result.url
  if ($result.ContainsKey('message') -and $result.message) {
    $line = "$line | $($result.message)"
  }
  $summaryLines.Add($line)
}

Write-TextFile -Path (Join-Path $captureRoot 'capture-summary.txt') -Lines $summaryLines
Write-JsonFile -Path (Join-Path $captureRoot 'capture-results.json') -Value $results

Write-Host "invite evidence captured: $captureRoot" -ForegroundColor Green
