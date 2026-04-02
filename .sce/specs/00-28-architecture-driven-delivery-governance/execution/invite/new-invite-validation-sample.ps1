$ErrorActionPreference = 'Stop'

param(
  [Parameter(Mandatory = $true)]
  [string]$SampleName,

  [string]$EnvironmentName,
  [string]$ApiBaseUrl,
  [string]$InviteCode,
  [string]$InviterUserId,
  [string]$InviteeUserId,
  [string]$ReferralId,
  [string]$GrantId,
  [string]$PolicyId,
  [string]$OutputDir
)

function Ensure-Directory {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path | Out-Null
  }
}

function Get-FileText {
  param([string]$Path)
  return Get-Content -LiteralPath $Path -Raw
}

function Write-FileText {
  param(
    [string]$Path,
    [string]$Content
  )
  Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function Escape-SqlString {
  param([string]$Value)
  if ($null -eq $Value) {
    return ''
  }
  return $Value.Replace("'", "''")
}

function Normalize-BaseUrl {
  param([string]$BaseUrl)
  if (-not $BaseUrl) {
    return ''
  }
  $normalized = $BaseUrl.Trim().TrimEnd('/')
  if ($normalized.EndsWith('/api')) {
    return $normalized.Substring(0, $normalized.Length - 4)
  }
  return $normalized
}

function Set-LedgerField {
  param(
    [string]$Content,
    [string]$Label,
    [string]$Value
  )
  $safeLabel = [regex]::Escape($Label)
  return [regex]::Replace($Content, "(?m)^- $safeLabel：.*$", "- $Label：$Value")
}

function Set-SqlVariable {
  param(
    [string]$Content,
    [string]$VariableName,
    [string]$Value,
    [switch]$Quote
  )

  $replacementValue = if ([string]::IsNullOrWhiteSpace($Value)) {
    'NULL'
  } elseif ($Quote.IsPresent) {
    "'" + (Escape-SqlString -Value $Value) + "'"
  } else {
    $Value
  }

  $pattern = "(?m)^SET @$([regex]::Escape($VariableName)) = .*;$"
  $replacement = "SET @$VariableName = $replacementValue;"
  return [regex]::Replace($Content, $pattern, $replacement)
}

function Resolve-TemplateValue {
  param(
    [string]$Value,
    [string]$Fallback
  )
  if ([string]::IsNullOrWhiteSpace($Value)) {
    return $Fallback
  }
  return $Value
}

function Build-CaptureCommand {
  param(
    [string]$CollectScriptPath,
    [string]$ApiBaseUrl,
    [string]$InviteCode,
    [string]$InviterUserId,
    [string]$InviteeUserId,
    [string]$ReferralId,
    [string]$GrantId,
    [string]$PolicyId,
    [string]$OutputDir
  )

  $lines = @(
    '$actorToken = ''REPLACE_ACTOR_TOKEN''',
    '$adminToken = ''REPLACE_ADMIN_TOKEN''',
    '',
    'powershell -ExecutionPolicy Bypass -File `',
    ('  "{0}" `' -f $CollectScriptPath),
    ('  -ApiBaseUrl "{0}" `' -f $ApiBaseUrl),
    '  -ActorToken $actorToken `',
    '  -AdminToken $adminToken `',
    ('  -InviteCode "{0}" `' -f $InviteCode),
    ('  -InviterUserId "{0}" `' -f $InviterUserId),
    ('  -InviteeUserId "{0}" `' -f $InviteeUserId),
    ('  -ReferralId "{0}" `' -f $ReferralId),
    ('  -GrantId "{0}" `' -f $GrantId),
    ('  -PolicyId "{0}" `' -f $PolicyId),
    ('  -OutputDir "{0}"' -f $OutputDir)
  )
  return ($lines -join [Environment]::NewLine)
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$safeSampleName = ($SampleName.Trim() -replace '[^a-zA-Z0-9._-]+', '-').Trim('-')
if (-not $safeSampleName) {
  throw 'SampleName 不能为空。'
}

$sampleRoot = if ($OutputDir) {
  $OutputDir
} else {
  Join-Path $scriptDir ("captures\invite-{0}-{1}" -f $timestamp, $safeSampleName)
}
$sampleRoot = [System.IO.Path]::GetFullPath($sampleRoot)

$ledgerTemplatePath = Join-Path $scriptDir 'validation-sample-ledger-template.md'
$sqlTemplatePath = Join-Path $scriptDir 'invite-validation-template.sql'
$collectScriptPath = Join-Path $scriptDir 'collect-invite-evidence.ps1'

Ensure-Directory -Path $sampleRoot
Copy-Item -LiteralPath $ledgerTemplatePath -Destination (Join-Path $sampleRoot 'sample-ledger.md') -Force
Copy-Item -LiteralPath $sqlTemplatePath -Destination (Join-Path $sampleRoot 'validation.sql') -Force

$normalizedBaseUrl = Normalize-BaseUrl -BaseUrl $ApiBaseUrl
$ledgerPath = Join-Path $sampleRoot 'sample-ledger.md'
$sqlPath = Join-Path $sampleRoot 'validation.sql'
$runCapturePath = Join-Path $sampleRoot 'run-capture.example.ps1'
$metadataPath = Join-Path $sampleRoot 'sample-metadata.json'

$ledgerText = Get-FileText -Path $ledgerPath
$ledgerText = Set-LedgerField -Content $ledgerText -Label '验证日期' -Value (Get-Date -Format 'yyyy-MM-dd')
$ledgerText = Set-LedgerField -Content $ledgerText -Label '环境' -Value (Resolve-TemplateValue -Value $EnvironmentName -Fallback 'REPLACE_ENVIRONMENT')
$ledgerText = Set-LedgerField -Content $ledgerText -Label '操作人' -Value 'REPLACE_OPERATOR'
$ledgerText = Set-LedgerField -Content $ledgerText -Label 'inviterUserId' -Value (Resolve-TemplateValue -Value $InviterUserId -Fallback 'REPLACE_INVITER_USER_ID')
$ledgerText = Set-LedgerField -Content $ledgerText -Label 'inviteCode' -Value (Resolve-TemplateValue -Value $(if ($InviteCode) { $InviteCode.ToUpper() } else { '' }) -Fallback 'REPLACE_INVITE_CODE')
$ledgerText = Set-LedgerField -Content $ledgerText -Label 'inviteeUserId' -Value (Resolve-TemplateValue -Value $InviteeUserId -Fallback 'REPLACE_INVITEE_USER_ID')
$ledgerText = Set-LedgerField -Content $ledgerText -Label 'referralId' -Value (Resolve-TemplateValue -Value $ReferralId -Fallback 'REPLACE_REFERRAL_ID')
$ledgerText = Set-LedgerField -Content $ledgerText -Label 'grantId' -Value (Resolve-TemplateValue -Value $GrantId -Fallback 'REPLACE_GRANT_ID')
$ledgerText = Set-LedgerField -Content $ledgerText -Label 'policyId' -Value (Resolve-TemplateValue -Value $PolicyId -Fallback 'REPLACE_POLICY_ID')
Write-FileText -Path $ledgerPath -Content $ledgerText

$sqlText = Get-FileText -Path $sqlPath
$sqlText = Set-SqlVariable -Content $sqlText -VariableName 'invite_code' -Value $(if ($InviteCode) { $InviteCode.ToUpper() } else { '' }) -Quote
$sqlText = Set-SqlVariable -Content $sqlText -VariableName 'inviter_user_id' -Value $InviterUserId
$sqlText = Set-SqlVariable -Content $sqlText -VariableName 'invitee_user_id' -Value $InviteeUserId
$sqlText = Set-SqlVariable -Content $sqlText -VariableName 'referral_id' -Value $ReferralId
$sqlText = Set-SqlVariable -Content $sqlText -VariableName 'grant_id' -Value $GrantId
$sqlText = Set-SqlVariable -Content $sqlText -VariableName 'policy_id' -Value $PolicyId
Write-FileText -Path $sqlPath -Content $sqlText

$runCaptureText = Build-CaptureCommand `
  -CollectScriptPath $collectScriptPath `
  -ApiBaseUrl (Resolve-TemplateValue -Value $normalizedBaseUrl -Fallback 'http://127.0.0.1:8010') `
  -InviteCode $(if ($InviteCode) { $InviteCode.ToUpper() } else { '' }) `
  -InviterUserId $InviterUserId `
  -InviteeUserId $InviteeUserId `
  -ReferralId $ReferralId `
  -GrantId $GrantId `
  -PolicyId $PolicyId `
  -OutputDir $sampleRoot
Write-FileText -Path $runCapturePath -Content $runCaptureText

$metadata = @{
  createdAt = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  sampleName = $safeSampleName
  environmentName = $EnvironmentName
  apiBaseUrl = $normalizedBaseUrl
  inviteCode = if ($InviteCode) { $InviteCode.ToUpper() } else { $null }
  inviterUserId = $InviterUserId
  inviteeUserId = $InviteeUserId
  referralId = $ReferralId
  grantId = $GrantId
  policyId = $PolicyId
  sampleRoot = $sampleRoot
}
$metadata | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $metadataPath -Encoding UTF8

Write-Host "invite sample initialized: $sampleRoot" -ForegroundColor Green
