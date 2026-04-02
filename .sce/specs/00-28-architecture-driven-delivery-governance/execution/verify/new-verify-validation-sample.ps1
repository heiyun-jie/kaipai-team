param(
  [string]$EnvironmentName = 'unknown',
  [string]$SampleLabel = 'verify'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Sanitize-Name {
  param([string]$Value)

  $raw = if ($null -eq $Value) { '' } else { [string]$Value }
  $trimmed = $raw.Trim()
  if (-not $trimmed) {
    return 'sample'
  }

  return ($trimmed -replace '[^a-zA-Z0-9._-]', '-')
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$safeLabel = Sanitize-Name -Value $SampleLabel
$safeEnv = Sanitize-Name -Value $EnvironmentName
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$samplesRoot = Join-Path $scriptDir 'samples'

if (-not (Test-Path -LiteralPath $samplesRoot)) {
  New-Item -ItemType Directory -Path $samplesRoot | Out-Null
}

$sampleRoot = Join-Path $samplesRoot "$timestamp-$safeEnv-$safeLabel"
New-Item -ItemType Directory -Path $sampleRoot | Out-Null
New-Item -ItemType Directory -Path (Join-Path $sampleRoot 'captures') | Out-Null
New-Item -ItemType Directory -Path (Join-Path $sampleRoot 'screenshots') | Out-Null

$ledgerTemplatePath = Join-Path $scriptDir 'validation-sample-ledger-template.md'
if (Test-Path -LiteralPath $ledgerTemplatePath) {
  Copy-Item -LiteralPath $ledgerTemplatePath -Destination (Join-Path $sampleRoot 'sample-ledger.md') -Force
}

Write-Output $sampleRoot
