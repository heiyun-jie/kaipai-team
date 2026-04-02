param(
  [string]$EnvironmentName = 'unknown',
  [string]$SampleLabel = 'login-auth',
  [switch]$EnableLiveProbe,
  [string]$ProbeBaseUrl = '',
  [string]$ProbePhone = '13800138000',
  [string]$ProbeWechatCode = 'dummy-code',
  [string]$ProbeInviteCode = 'TESTINVITE'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$newSampleScript = Join-Path $scriptDir 'new-login-auth-validation-sample.ps1'
$collectScript = Join-Path $scriptDir 'collect-login-auth-evidence.ps1'

$sampleRoot = & $newSampleScript -EnvironmentName $EnvironmentName -SampleLabel $SampleLabel
& $collectScript `
  -SampleRoot $sampleRoot `
  -EnvironmentName $EnvironmentName `
  -EnableLiveProbe:$EnableLiveProbe `
  -ProbeBaseUrl $ProbeBaseUrl `
  -ProbePhone $ProbePhone `
  -ProbeWechatCode $ProbeWechatCode `
  -ProbeInviteCode $ProbeInviteCode

Write-Host "login-auth validation prepared: $sampleRoot" -ForegroundColor Green
