param(
  [string]$EnvironmentName = 'unknown',
  [string]$SampleLabel = 'membership'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$newSampleScript = Join-Path $scriptDir 'new-membership-validation-sample.ps1'
$collectScript = Join-Path $scriptDir 'collect-membership-evidence.ps1'

$sampleRoot = & $newSampleScript -EnvironmentName $EnvironmentName -SampleLabel $SampleLabel
& $collectScript -SampleRoot $sampleRoot -EnvironmentName $EnvironmentName

Write-Host "membership validation prepared: $sampleRoot" -ForegroundColor Green
