param(
  [Parameter(Mandatory = $true)]
  [string]$SampleRoot,

  [string]$EnvironmentName = 'unknown',

  [string]$FrontendEnvPath = 'D:\XM\kaipai-team\kaipai-frontend\.env',

  [string]$FrontendEnvExamplePath = 'D:\XM\kaipai-team\kaipai-frontend\.env.example',

  [string]$AdminEnvPath = 'D:\XM\kaipai-team\kaipai-admin\.env.development',

  [string]$ServerAppPath = 'D:\XM\kaipai-team\kaipaile-server\src\main\resources\application.yml'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Read-KeyValueFile {
  param([string]$Path)

  $values = @{}
  if (-not (Test-Path -LiteralPath $Path)) {
    return $values
  }

  foreach ($line in Get-Content -LiteralPath $Path) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith('#')) {
      continue
    }
    $parts = $trimmed -split '=', 2
    if ($parts.Count -ne 2) {
      continue
    }
    $values[$parts[0].Trim()] = $parts[1].Trim()
  }

  return $values
}

function Ensure-Directory {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path | Out-Null
  }
}

function Write-Utf8File {
  param(
    [string]$Path,
    [string[]]$Lines
  )

  [System.IO.File]::WriteAllLines($Path, $Lines, [System.Text.UTF8Encoding]::new($false))
}

Ensure-Directory -Path $SampleRoot

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ledgerTemplatePath = Join-Path $scriptDir 'validation-sample-ledger-template.md'
$captureRoot = Join-Path $SampleRoot 'captures'
Ensure-Directory -Path $captureRoot

$frontendEnv = Read-KeyValueFile -Path $FrontendEnvPath
$frontendExampleEnv = Read-KeyValueFile -Path $FrontendEnvExamplePath
$adminEnv = Read-KeyValueFile -Path $AdminEnvPath
$serverConfigText = if (Test-Path -LiteralPath $ServerAppPath) { Get-Content -LiteralPath $ServerAppPath -Raw } else { '' }

$frontendBaseUrl = [string]($frontendEnv['VITE_API_BASE_URL'])
$frontendUseMock = [string]($frontendEnv['VITE_USE_MOCK'])
$adminBaseUrl = [string]($adminEnv['VITE_API_BASE_URL'])

$requiredMembershipApis = @(
  '/api/level/info',
  '/api/card/personalization',
  '/api/card/scene-templates',
  '/api/card/config',
  '/api/fortune/report',
  '/api/ai/quota'
)

$blockers = New-Object System.Collections.Generic.List[string]
if (-not $frontendBaseUrl) {
  $blockers.Add('Missing frontend VITE_API_BASE_URL in current .env')
}
if ($frontendUseMock -ne 'false') {
  $blockers.Add('Frontend VITE_USE_MOCK is not false; membership real-environment conclusion may still fall back to mock')
}
if (-not $adminBaseUrl) {
  $blockers.Add('Missing admin VITE_API_BASE_URL in current env file')
}
$hasApiContextPath = $serverConfigText -match '(?m)^\s*context-path:\s*/api\s*$'
if (-not $hasApiContextPath) {
  $blockers.Add('Server application.yml does not clearly expose /api context path in local scan')
}

$result = [ordered]@{
  generatedAt = (Get-Date).ToString('s')
  environmentName = $EnvironmentName
  frontend = [ordered]@{
    envPath = $FrontendEnvPath
    envExamplePath = $FrontendEnvExamplePath
    VITE_API_BASE_URL = $frontendBaseUrl
    VITE_USE_MOCK = $frontendUseMock
    example = $frontendExampleEnv
  }
  admin = [ordered]@{
    envPath = $AdminEnvPath
    VITE_API_BASE_URL = $adminBaseUrl
  }
  server = [ordered]@{
    applicationPath = $ServerAppPath
    exposeApiContextPath = $hasApiContextPath
    requiredMembershipApis = $requiredMembershipApis
  }
  blockers = $blockers
}

$jsonPath = Join-Path $captureRoot 'capture-results.json'
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $jsonPath -Encoding utf8

$runtimeSummaryPath = Join-Path $SampleRoot 'runtime-summary.md'
$runtimeSummary = @(
  '# Membership Runtime Summary',
  '',
  "- Environment: $EnvironmentName",
  "- Frontend VITE_API_BASE_URL: $frontendBaseUrl",
  "- Frontend VITE_USE_MOCK: $frontendUseMock",
  "- Admin VITE_API_BASE_URL: $adminBaseUrl",
  "- Server exposes /api context path: $($result.server.exposeApiContextPath)",
  "- Required API set: $($requiredMembershipApis -join ', ')",
  ''
)

if ($blockers.Count -gt 0) {
  $runtimeSummary += '- Blockers:'
  foreach ($item in $blockers) {
    $runtimeSummary += "  - $item"
  }
} else {
  $runtimeSummary += '- Blockers: none from local file scan'
}

Write-Utf8File -Path $runtimeSummaryPath -Lines $runtimeSummary

$ledgerPath = Join-Path $SampleRoot 'sample-ledger.md'
if (-not (Test-Path -LiteralPath $ledgerPath) -and (Test-Path -LiteralPath $ledgerTemplatePath)) {
  Copy-Item -LiteralPath $ledgerTemplatePath -Destination $ledgerPath -Force
}

$reportPath = Join-Path $SampleRoot 'validation-report.md'
$reportLines = @(
  '# Membership Validation Report',
  '',
  "- Generated At: $((Get-Date).ToString('s'))",
  "- Environment: $EnvironmentName",
  '',
  '## Local Runtime Scan',
  '',
  "- Frontend baseURL: $frontendBaseUrl",
  "- Frontend mock flag: $frontendUseMock",
  "- Admin baseURL: $adminBaseUrl",
  "- Server exposes /api context path: $($result.server.exposeApiContextPath)",
  '',
  '## Blockers',
  ''
)

if ($blockers.Count -gt 0) {
  foreach ($item in $blockers) {
    $reportLines += "- [ ] $item"
  }
} else {
  $reportLines += '- [x] No blocker detected from local file scan'
}

$reportLines += @(
  '',
  '## Manual Evidence To Add',
  '',
  '- [ ] Membership accounts admin screenshot',
  '- [ ] Templates admin screenshot',
  '- [ ] level.info / card.personalization capture',
  '- [ ] membership / actor-card / detail / invite / fortune screenshots',
  '- [ ] DB query result for membership_account / card_scene_template / template_publish_log',
  '',
  '## Output Files',
  '',
  '- captures/capture-results.json',
  '- runtime-summary.md',
  '- sample-ledger.md',
  '- validation-report.md'
)

Write-Utf8File -Path $reportPath -Lines $reportLines

Write-Host "membership evidence prepared: $SampleRoot" -ForegroundColor Green
