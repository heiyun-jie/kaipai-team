$ErrorActionPreference = 'Stop'

param(
  [Parameter(Mandatory = $true)]
  [string]$SampleName,

  [Parameter(Mandatory = $true)]
  [string]$ApiBaseUrl,

  [string]$EnvironmentName,
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

function Write-FileText {
  param(
    [string]$Path,
    [string]$Content
  )
  Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function Resolve-ReportValue {
  param(
    [object]$Value,
    [string]$Fallback = '--'
  )
  if ($null -eq $Value) {
    return $Fallback
  }
  $text = [string]$Value
  if ([string]::IsNullOrWhiteSpace($text)) {
    return $Fallback
  }
  return $text
}

function Build-Report {
  param(
    [hashtable]$Context,
    [System.Collections.IEnumerable]$Results,
    [string]$CaptureDir
  )

  $okResults = @($Results | Where-Object { $_.status -eq 'ok' })
  $errorResults = @($Results | Where-Object { $_.status -ne 'ok' })
  $lines = New-Object 'System.Collections.Generic.List[string]'

  $lines.Add('# Invite Validation Report')
  $lines.Add('')
  $lines.Add('## Sample')
  $lines.Add('')
  $lines.Add('- SampleName: ' + (Resolve-ReportValue $Context.sampleName))
  $lines.Add('- Environment: ' + (Resolve-ReportValue $Context.environmentName))
  $lines.Add('- CapturedAt: ' + (Resolve-ReportValue $Context.capturedAt))
  $lines.Add('- ApiBaseUrl: ' + (Resolve-ReportValue $Context.apiBaseUrl))
  $lines.Add('- InviteCode: ' + (Resolve-ReportValue $Context.inviteCode))
  $lines.Add('- InviterUserId: ' + (Resolve-ReportValue $Context.inviterUserId))
  $lines.Add('- InviteeUserId: ' + (Resolve-ReportValue $Context.inviteeUserId))
  $lines.Add('- ReferralId: ' + (Resolve-ReportValue $Context.referralId))
  $lines.Add('- GrantId: ' + (Resolve-ReportValue $Context.grantId))
  $lines.Add('- PolicyId: ' + (Resolve-ReportValue $Context.policyId))
  $lines.Add('')
  $lines.Add('## Capture Summary')
  $lines.Add('')
  $lines.Add('- OK endpoints: ' + $okResults.Count)
  $lines.Add('- Error endpoints: ' + $errorResults.Count)
  $lines.Add('- Capture directory: ' + $CaptureDir)
  $lines.Add('')

  $lines.Add('## OK Endpoints')
  $lines.Add('')
  if ($okResults.Count -eq 0) {
    $lines.Add('- None')
  } else {
    foreach ($result in $okResults) {
      $lines.Add('- ' + $result.name + ' -> ' + $result.output)
    }
  }
  $lines.Add('')

  $lines.Add('## Error Endpoints')
  $lines.Add('')
  if ($errorResults.Count -eq 0) {
    $lines.Add('- None')
  } else {
    foreach ($result in $errorResults) {
      $message = Resolve-ReportValue $result.message 'unknown error'
      $lines.Add('- ' + $result.name + ' -> ' + $message)
    }
  }
  $lines.Add('')

  $lines.Add('## DB Checklist')
  $lines.Add('')
  $lines.Add('- [ ] Execute validation.sql against the same environment')
  $lines.Add('- [ ] Save the result as validation-result.txt or screenshots')
  $lines.Add('- [ ] Fill sample-ledger.md with API and DB evidence')
  $lines.Add('- [ ] Backfill invite-status.md with the conclusion')
  $lines.Add('')

  $lines.Add('## Generated Files')
  $lines.Add('')
  $lines.Add('- sample-ledger.md')
  $lines.Add('- validation.sql')
  $lines.Add('- capture-summary.txt')
  $lines.Add('- capture-results.json')
  $lines.Add('- validation-report.md')

  return ($lines -join [Environment]::NewLine)
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$normalizedBaseUrl = Normalize-BaseUrl -BaseUrl $ApiBaseUrl
if (-not $normalizedBaseUrl) {
  throw 'ApiBaseUrl 不能为空。'
}

$safeSampleName = ($SampleName.Trim() -replace '[^a-zA-Z0-9._-]+', '-').Trim('-')
if (-not $safeSampleName) {
  throw 'SampleName 不能为空。'
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$sampleRoot = if ($OutputDir) {
  [System.IO.Path]::GetFullPath($OutputDir)
} else {
  [System.IO.Path]::GetFullPath((Join-Path $scriptDir ("captures\invite-{0}-{1}" -f $timestamp, $safeSampleName)))
}

Ensure-Directory -Path $sampleRoot

$newSampleScript = Join-Path $scriptDir 'new-invite-validation-sample.ps1'
$collectScript = Join-Path $scriptDir 'collect-invite-evidence.ps1'

& $newSampleScript `
  -SampleName $safeSampleName `
  -EnvironmentName $EnvironmentName `
  -ApiBaseUrl $normalizedBaseUrl `
  -InviteCode $InviteCode `
  -InviterUserId $InviterUserId `
  -InviteeUserId $InviteeUserId `
  -ReferralId $ReferralId `
  -GrantId $GrantId `
  -PolicyId $PolicyId `
  -OutputDir $sampleRoot

& $collectScript `
  -ApiBaseUrl $normalizedBaseUrl `
  -ActorToken $ActorToken `
  -AdminToken $AdminToken `
  -InviteCode $InviteCode `
  -InviterUserId $InviterUserId `
  -InviteeUserId $InviteeUserId `
  -ReferralId $ReferralId `
  -GrantId $GrantId `
  -PolicyId $PolicyId `
  -OutputDir $sampleRoot

$captureContextPath = Join-Path $sampleRoot 'capture-context.json'
$captureResultsPath = Join-Path $sampleRoot 'capture-results.json'
$reportPath = Join-Path $sampleRoot 'validation-report.md'

$context = Get-Content -LiteralPath $captureContextPath -Raw | ConvertFrom-Json -AsHashtable
$results = Get-Content -LiteralPath $captureResultsPath -Raw | ConvertFrom-Json
$context['sampleName'] = $safeSampleName
$context['environmentName'] = $EnvironmentName

$reportContent = Build-Report -Context $context -Results $results -CaptureDir $sampleRoot
Write-FileText -Path $reportPath -Content $reportContent

Write-Host "invite validation prepared: $sampleRoot" -ForegroundColor Green
