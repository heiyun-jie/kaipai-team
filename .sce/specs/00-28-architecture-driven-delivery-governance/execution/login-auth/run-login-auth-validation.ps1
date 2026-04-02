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
$metadataPath = Join-Path $sampleRoot 'sample-metadata.json'
$metadata = @{
  createdAt = (Get-Date).ToString('s')
  environmentName = $EnvironmentName
  sampleLabel = $SampleLabel
  sampleRoot = $sampleRoot
  enableLiveProbe = [bool]$EnableLiveProbe
  probeBaseUrl = $ProbeBaseUrl
  probePhone = $ProbePhone
  probeWechatCode = $ProbeWechatCode
  probeInviteCode = $ProbeInviteCode
}
$metadata | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $metadataPath -Encoding UTF8

& $collectScript `
  -SampleRoot $sampleRoot `
  -EnvironmentName $EnvironmentName `
  -EnableLiveProbe:$EnableLiveProbe `
  -ProbeBaseUrl $ProbeBaseUrl `
  -ProbePhone $ProbePhone `
  -ProbeWechatCode $ProbeWechatCode `
  -ProbeInviteCode $ProbeInviteCode

Write-Host "login-auth validation prepared: $sampleRoot" -ForegroundColor Green
