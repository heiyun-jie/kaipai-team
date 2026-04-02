param(
  [Parameter(Mandatory = $true)]
  [string]$SampleName,

  [string]$EnvironmentName,
  [string]$ApiBaseUrl,
  [string]$ActorToken,
  [string]$AdminToken,
  [string]$UserId,
  [string]$VerificationId,
  [string]$RetryVerificationId,
  [string]$OutputDir
)

$ErrorActionPreference = 'Stop'

function Ensure-Directory {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path | Out-Null
  }
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
    [string]$UserId,
    [string]$VerificationId,
    [string]$RetryVerificationId,
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
    ('  -UserId "{0}" `' -f $UserId),
    ('  -VerificationId "{0}" `' -f $VerificationId),
    ('  -RetryVerificationId "{0}" `' -f $RetryVerificationId),
    ('  -OutputDir "{0}"' -f $OutputDir)
  )
  return ($lines -join [Environment]::NewLine)
}

function Read-JsonFile {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    return $null
  }
  return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Get-ApiData {
  param([object]$Json)
  if ($null -eq $Json) {
    return $null
  }
  if ($Json.PSObject.Properties['data']) {
    return $Json.data
  }
  return $Json
}

function Get-ValueOrDash {
  param([object]$Value)
  if ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value)) {
    return '--'
  }
  return [string]$Value
}

function Get-VerifyStatusLabel {
  param([object]$Status)
  switch ([string]$Status) {
    '0' { return 'unsubmitted' }
    '1' { return 'pending' }
    '2' { return 'approved' }
    '3' { return 'rejected' }
    default { return Get-ValueOrDash -Value $Status }
  }
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$newSampleScript = Join-Path $scriptDir 'new-verify-validation-sample.ps1'
$collectScriptPath = Join-Path $scriptDir 'collect-verify-evidence.ps1'
$ledgerTemplatePath = Join-Path $scriptDir 'validation-sample-ledger-template.md'
$sqlTemplatePath = Join-Path $scriptDir 'verify-validation-template.sql'
$syncArtifactsScriptPath = Join-Path $scriptDir 'sync-verify-validation-artifacts.py'

$sampleRoot = if ($OutputDir) {
  [System.IO.Path]::GetFullPath($OutputDir)
} else {
  & $newSampleScript -EnvironmentName $EnvironmentName -SampleLabel $SampleName
}

Ensure-Directory -Path $sampleRoot

$ledgerPath = Join-Path $sampleRoot 'sample-ledger.md'
$sqlPath = Join-Path $sampleRoot 'validation.sql'
$runCapturePath = Join-Path $sampleRoot 'run-capture.example.ps1'
$metadataPath = Join-Path $sampleRoot 'sample-metadata.json'
$reportPath = Join-Path $sampleRoot 'validation-report.md'

if (-not (Test-Path -LiteralPath $ledgerPath)) {
  Copy-Item -LiteralPath $ledgerTemplatePath -Destination $ledgerPath -Force
}
if (-not (Test-Path -LiteralPath $sqlPath)) {
  Copy-Item -LiteralPath $sqlTemplatePath -Destination $sqlPath -Force
}

$normalizedBaseUrl = Normalize-BaseUrl -BaseUrl $ApiBaseUrl

$ledgerText = Get-FileText -Path $ledgerPath
$ledgerText = Set-LedgerField -Content $ledgerText -Label '验证日期' -Value (Get-Date -Format 'yyyy-MM-dd')
$ledgerText = Set-LedgerField -Content $ledgerText -Label '环境' -Value (Resolve-TemplateValue -Value $EnvironmentName -Fallback 'REPLACE_ENVIRONMENT')
$ledgerText = Set-LedgerField -Content $ledgerText -Label '操作人' -Value 'REPLACE_OPERATOR'
$ledgerText = Set-LedgerField -Content $ledgerText -Label 'userId' -Value (Resolve-TemplateValue -Value $UserId -Fallback 'REPLACE_USER_ID')
$ledgerText = Set-LedgerField -Content $ledgerText -Label 'firstVerificationId' -Value (Resolve-TemplateValue -Value $VerificationId -Fallback 'REPLACE_FIRST_VERIFICATION_ID')
$ledgerText = Set-LedgerField -Content $ledgerText -Label 'retryVerificationId' -Value (Resolve-TemplateValue -Value $RetryVerificationId -Fallback 'REPLACE_RETRY_VERIFICATION_ID')
Write-FileText -Path $ledgerPath -Content $ledgerText

$sqlText = Get-FileText -Path $sqlPath
$sqlText = Set-SqlVariable -Content $sqlText -VariableName 'user_id' -Value $UserId
$sqlText = Set-SqlVariable -Content $sqlText -VariableName 'first_verification_id' -Value $VerificationId
$sqlText = Set-SqlVariable -Content $sqlText -VariableName 'retry_verification_id' -Value $RetryVerificationId
Write-FileText -Path $sqlPath -Content $sqlText

$runCaptureText = Build-CaptureCommand `
  -CollectScriptPath $collectScriptPath `
  -ApiBaseUrl (Resolve-TemplateValue -Value $normalizedBaseUrl -Fallback 'http://127.0.0.1:8010') `
  -UserId $UserId `
  -VerificationId $VerificationId `
  -RetryVerificationId $RetryVerificationId `
  -OutputDir $sampleRoot
Write-FileText -Path $runCapturePath -Content $runCaptureText

$metadata = @{
  createdAt = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  sampleName = $SampleName
  environmentName = $EnvironmentName
  apiBaseUrl = $normalizedBaseUrl
  userId = $UserId
  verificationId = $VerificationId
  retryVerificationId = $RetryVerificationId
  sampleRoot = $sampleRoot
}
$metadata | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $metadataPath -Encoding UTF8

if ($ActorToken -or $AdminToken) {
  powershell -ExecutionPolicy Bypass -File $collectScriptPath `
    -ApiBaseUrl $normalizedBaseUrl `
    -ActorToken $ActorToken `
    -AdminToken $AdminToken `
    -UserId $UserId `
    -VerificationId $VerificationId `
    -RetryVerificationId $RetryVerificationId `
    -OutputDir $sampleRoot
}

$captureRoot = Join-Path $sampleRoot 'captures'
$statusFinal = Get-ApiData -Json (Read-JsonFile -Path (Join-Path $captureRoot 'actor_verify_status_final.json'))
$levelFinal = Get-ApiData -Json (Read-JsonFile -Path (Join-Path $captureRoot 'actor_level_info_final.json'))
$userFinal = Get-ApiData -Json (Read-JsonFile -Path (Join-Path $captureRoot 'actor_user_me_final.json'))
$listFinal = Get-ApiData -Json (Read-JsonFile -Path (Join-Path $captureRoot 'admin_verify_list_final.json'))
$detailFirst = Get-ApiData -Json (Read-JsonFile -Path (Join-Path $captureRoot 'admin_verify_detail_first.json'))
$detailRetry = Get-ApiData -Json (Read-JsonFile -Path (Join-Path $captureRoot 'admin_verify_detail_retry.json'))
$captureResults = Read-JsonFile -Path (Join-Path $captureRoot 'capture-results.json')

$listItems = @()
if ($listFinal -and $listFinal.PSObject.Properties['list']) {
  $listItems = @($listFinal.list)
}
$okCount = 0
$errorCount = 0
if ($captureResults) {
  foreach ($item in $captureResults) {
    if ($item.status -eq 'ok') {
      $okCount++
    } else {
      $errorCount++
    }
  }
}

$firstRejected = ($detailFirst -and [string]$detailFirst.status -eq '3')
$retryApproved = ($detailRetry -and [string]$detailRetry.status -eq '2')
$recordIdsDifferent = ([string]$VerificationId) -and ([string]$RetryVerificationId) -and ([string]$VerificationId -ne [string]$RetryVerificationId)
$actorApproved = ($statusFinal -and [string]$statusFinal.status -eq '2')
$levelCertified = $false
if ($levelFinal -and $levelFinal.PSObject.Properties['isCertified']) {
  $levelCertified = [bool]$levelFinal.isCertified
}

$ledgerText = Get-FileText -Path $ledgerPath
$ledgerText = Set-LedgerField -Content $ledgerText -Label 'phone' -Value (Get-ValueOrDash -Value $(if ($userFinal) { $userFinal.phone } else { $null }))
$ledgerText = Set-LedgerField -Content $ledgerText -Label '初始 `verify/status`' -Value '见 action captures'
$ledgerText = Set-LedgerField -Content $ledgerText -Label '首次提交返回状态' -Value (Get-VerifyStatusLabel -Status $(if ($detailFirst) { $detailFirst.status } else { $null }))
$ledgerText = Set-LedgerField -Content $ledgerText -Label '拒绝后 `verify/status`' -Value (Get-VerifyStatusLabel -Status $(if ($detailFirst) { $detailFirst.status } else { $null }))
$ledgerText = Set-LedgerField -Content $ledgerText -Label '二次提交返回状态' -Value (Get-VerifyStatusLabel -Status $(if ($detailRetry) { $detailRetry.status } else { $null }))
$ledgerText = Set-LedgerField -Content $ledgerText -Label '最终 `verify/status`' -Value (Get-VerifyStatusLabel -Status $(if ($statusFinal) { $statusFinal.status } else { $null }))
$ledgerText = Set-LedgerField -Content $ledgerText -Label '最终 `rejectReason`' -Value (Get-ValueOrDash -Value $(if ($statusFinal) { $statusFinal.rejectReason } else { $null }))
$ledgerText = Set-LedgerField -Content $ledgerText -Label '最终 `level/info.isCertified`' -Value (Get-ValueOrDash -Value $(if ($levelFinal) { $levelFinal.isCertified } else { $null }))
$ledgerText = Set-LedgerField -Content $ledgerText -Label '最终 `profileCompletion`' -Value (Get-ValueOrDash -Value $(if ($levelFinal) { $levelFinal.profileCompletion } else { $null }))
$ledgerText = Set-LedgerField -Content $ledgerText -Label '首次申请单是否查到' -Value $(if ($detailFirst) { '是' } else { '否' })
$ledgerText = Set-LedgerField -Content $ledgerText -Label '首次申请单状态' -Value (Get-VerifyStatusLabel -Status $(if ($detailFirst) { $detailFirst.status } else { $null }))
$ledgerText = Set-LedgerField -Content $ledgerText -Label '首次拒绝备注' -Value (Get-ValueOrDash -Value $(if ($detailFirst) { $detailFirst.rejectReason } else { $null }))
$ledgerText = Set-LedgerField -Content $ledgerText -Label '重提申请单是否查到' -Value $(if ($detailRetry) { '是' } else { '否' })
$ledgerText = Set-LedgerField -Content $ledgerText -Label '重提申请单状态' -Value (Get-VerifyStatusLabel -Status $(if ($detailRetry) { $detailRetry.status } else { $null }))
$ledgerText = Set-LedgerField -Content $ledgerText -Label '申请单总数' -Value (Get-ValueOrDash -Value $listItems.Count)
$ledgerText = Set-LedgerField -Content $ledgerText -Label '是否保留首条拒绝记录' -Value $(if ($firstRejected) { '是' } else { '否' })
$ledgerText = Set-LedgerField -Content $ledgerText -Label '是否生成新申请单' -Value $(if ($recordIdsDifferent) { '是' } else { '否' })
Write-FileText -Path $ledgerPath -Content $ledgerText

$reportLines = @(
  '# Verify Validation Report',
  '',
  '## Sample',
  '',
  "- SampleName: $SampleName",
  "- Environment: $EnvironmentName",
  "- ApiBaseUrl: $normalizedBaseUrl",
  "- UserId: $UserId",
  "- FirstVerificationId: $VerificationId",
  "- RetryVerificationId: $RetryVerificationId",
  '',
  '## Extracted Facts',
  '',
  '### Final Actor Snapshot',
  '',
  "- status: $(Get-VerifyStatusLabel -Status $(if ($statusFinal) { $statusFinal.status } else { $null }))",
  "- realName: $(Get-ValueOrDash -Value $(if ($statusFinal) { $statusFinal.realName } else { $null }))",
  "- rejectReason: $(Get-ValueOrDash -Value $(if ($statusFinal) { $statusFinal.rejectReason } else { $null }))",
  "- submittedAt: $(Get-ValueOrDash -Value $(if ($statusFinal) { $statusFinal.submittedAt } else { $null }))",
  "- reviewedAt: $(Get-ValueOrDash -Value $(if ($statusFinal) { $statusFinal.reviewedAt } else { $null }))",
  '',
  '### Final Level Snapshot',
  '',
  "- isCertified: $(Get-ValueOrDash -Value $(if ($levelFinal) { $levelFinal.isCertified } else { $null }))",
  "- level: $(Get-ValueOrDash -Value $(if ($levelFinal) { $levelFinal.level } else { $null }))",
  "- profileCompletion: $(Get-ValueOrDash -Value $(if ($levelFinal) { $levelFinal.profileCompletion } else { $null }))",
  "- membershipTier: $(Get-ValueOrDash -Value $(if ($levelFinal) { $levelFinal.membershipTier } else { $null }))",
  '',
  '### Admin Record Snapshot',
  '',
  "- verifyRecordCount: $($listItems.Count)",
  "- firstRecordStatus: $(Get-VerifyStatusLabel -Status $(if ($detailFirst) { $detailFirst.status } else { $null }))",
  "- firstRejectReason: $(Get-ValueOrDash -Value $(if ($detailFirst) { $detailFirst.rejectReason } else { $null }))",
  "- retryRecordStatus: $(Get-VerifyStatusLabel -Status $(if ($detailRetry) { $detailRetry.status } else { $null }))",
  "- retryReviewedAt: $(Get-ValueOrDash -Value $(if ($detailRetry) { $detailRetry.reviewedAt } else { $null }))",
  '',
  '## Cross Checks',
  '',
  "- First record rejected: $(if ($firstRejected) { '是' } else { '否' })",
  "- Retry record approved: $(if ($retryApproved) { '是' } else { '否' })",
  "- Two verification IDs differ: $(if ($recordIdsDifferent) { '是' } else { '否' })",
  "- Final actor status is approved: $(if ($actorApproved) { '是' } else { '否' })",
  "- Final level/info isCertified: $(if ($levelCertified) { '是' } else { '否' })",
  '',
  '## Capture Summary',
  '',
  "- OK endpoints: $okCount",
  "- Error endpoints: $errorCount",
  "- Capture directory: $sampleRoot"
)

Write-FileText -Path $reportPath -Content ($reportLines -join [Environment]::NewLine)

python $syncArtifactsScriptPath --sample-dir $sampleRoot

Write-Host "verify validation prepared: $sampleRoot" -ForegroundColor Green
