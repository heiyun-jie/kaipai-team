param(
  [Parameter(Mandatory = $true)]
  [string]$SampleRoot,

  [string]$EnvironmentName = 'unknown',

  [string]$FrontendEnvPath = 'D:\XM\kaipai-team\kaipai-frontend\.env',

  [string]$FrontendEnvExamplePath = 'D:\XM\kaipai-team\kaipai-frontend\.env.example',

  [string]$AdminEnvPath = 'D:\XM\kaipai-team\kaipai-admin\.env.development',

  [string]$ServerAppPath = 'D:\XM\kaipai-team\kaipaile-server\src\main\resources\application.yml',

  [string]$LocalWechatSecretEnvPath = 'D:\XM\kaipai-team\.sce\config\local-secrets\wechat-miniapp.env',

  [switch]$EnableLiveProbe,

  [string]$ProbeBaseUrl = '',

  [string]$ProbePhone = '13800138000',

  [string]$ProbeWechatCode = 'dummy-code',

  [string]$ProbeInviteCode = 'TESTINVITE'
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

function Write-Utf8Text {
  param(
    [string]$Path,
    [string]$Text
  )

  [System.IO.File]::WriteAllText($Path, $Text, [System.Text.UTF8Encoding]::new($false))
}

function Normalize-BaseUrl {
  param([string]$BaseUrl)

  if ($null -eq $BaseUrl) {
    return ''
  }

  return $BaseUrl.Trim().TrimEnd('/')
}

function Test-WechatSecretValidity {
  param([string]$Value)

  $normalized = [string]$Value
  if ([string]::IsNullOrWhiteSpace($normalized)) {
    return $false
  }

  $trimmed = $normalized.Trim()
  if ($trimmed.Length -lt 12) {
    return $false
  }

  $invalidPatterns = @(
    '^replace-with-real-app-secret$',
    '^fake[-_].*',
    '^example.*',
    '^dummy.*',
    '^sample.*',
    '^placeholder.*'
  )

  foreach ($pattern in $invalidPatterns) {
    if ($trimmed -match $pattern) {
      return $false
    }
  }

  return $true
}

function Get-ObjectPropertyValue {
  param(
    [object]$Object,
    [string]$Name
  )

  if ($null -eq $Object) {
    return $null
  }

  $property = $Object.PSObject.Properties[$Name]
  if ($null -eq $property) {
    return $null
  }

  return $property.Value
}

function Repair-Utf8Text {
  param([string]$Text)

  if ([string]::IsNullOrEmpty($Text)) {
    return $Text
  }

  $latin1 = [System.Text.Encoding]::GetEncoding('ISO-8859-1')
  return [System.Text.Encoding]::UTF8.GetString($latin1.GetBytes($Text))
}

function Invoke-LiveProbe {
  param(
    [string]$Name,
    [string]$Method,
    [string]$Url,
    [hashtable]$Payload
  )

  $result = [ordered]@{
    name = $Name
    method = $Method
    url = $Url
    requestedAt = (Get-Date).ToString('s')
    requestBody = $Payload
    transportOk = $false
    statusCode = $null
    json = $null
    rawBody = $null
    error = $null
  }

  try {
    $jsonBody = $Payload | ConvertTo-Json -Depth 6
    $response = Invoke-WebRequest -Uri $Url -Method $Method -ContentType 'application/json; charset=utf-8' -Body $jsonBody -TimeoutSec 12 -UseBasicParsing
    $body = Repair-Utf8Text -Text ([string]$response.Content)
    $result.transportOk = $true
    $result.statusCode = [int]$response.StatusCode
    $result.rawBody = $body
    try {
      $result.json = $body | ConvertFrom-Json
    } catch {
      $result.error = "Response is not valid JSON: $($_.Exception.Message)"
    }
  } catch {
    $result.error = $_.Exception.Message
    $responseProperty = $_.Exception.PSObject.Properties['Response']
    if ($responseProperty -and $responseProperty.Value) {
      $response = $responseProperty.Value
      $result.statusCode = [int]$response.StatusCode
      $stream = $response.GetResponseStream()
      if ($stream) {
        $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8)
        try {
          $body = Repair-Utf8Text -Text ($reader.ReadToEnd())
          $result.rawBody = $body
          try {
            $result.json = $body | ConvertFrom-Json
          } catch {
            if (-not $result.error) {
              $result.error = "Response is not valid JSON: $($_.Exception.Message)"
            }
          }
        } finally {
          $reader.Dispose()
          $stream.Dispose()
        }
      }
    }
  }

  return $result
}

Ensure-Directory -Path $SampleRoot

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ledgerTemplatePath = Join-Path $scriptDir 'validation-sample-ledger-template.md'
$syncArtifactsScriptPath = Join-Path $scriptDir 'sync-login-auth-validation-artifacts.py'
$captureRoot = Join-Path $SampleRoot 'captures'
Ensure-Directory -Path $captureRoot

$frontendEnv = Read-KeyValueFile -Path $FrontendEnvPath
$frontendExampleEnv = Read-KeyValueFile -Path $FrontendEnvExamplePath
$adminEnv = Read-KeyValueFile -Path $AdminEnvPath
$localWechatSecretEnv = Read-KeyValueFile -Path $LocalWechatSecretEnvPath
$serverConfigText = if (Test-Path -LiteralPath $ServerAppPath) { Get-Content -LiteralPath $ServerAppPath -Raw } else { '' }

$wechatAppIdConfigured = $serverConfigText -match 'WECHAT_MINIAPP_APP_ID'
$wechatAppSecretConfigured = $serverConfigText -match 'WECHAT_MINIAPP_APP_SECRET'
$localWechatAppId = [string]($localWechatSecretEnv['WECHAT_MINIAPP_APP_ID'])
$localWechatAppSecret = [string]($localWechatSecretEnv['WECHAT_MINIAPP_APP_SECRET'])
$localWechatAppIdReady = -not [string]::IsNullOrWhiteSpace($localWechatAppId)
$localWechatAppSecretReady = Test-WechatSecretValidity -Value $localWechatAppSecret
$frontendBaseUrl = [string]($frontendEnv['VITE_API_BASE_URL'])
$frontendUseMock = [string]($frontendEnv['VITE_USE_MOCK'])
$frontendWechatAuth = [string]($frontendEnv['VITE_ENABLE_WECHAT_AUTH'])
$adminBaseUrl = [string]($adminEnv['VITE_API_BASE_URL'])
$resolvedProbeBaseUrl = if ($ProbeBaseUrl) { Normalize-BaseUrl -BaseUrl $ProbeBaseUrl } else { Normalize-BaseUrl -BaseUrl $frontendBaseUrl }

$blockers = New-Object System.Collections.Generic.List[string]
$observations = New-Object System.Collections.Generic.List[string]

if (-not $frontendBaseUrl) {
  $blockers.Add('Missing frontend VITE_API_BASE_URL in current .env')
}
if (-not $frontendUseMock) {
  $blockers.Add('Missing frontend VITE_USE_MOCK in current .env')
}
if ($frontendWechatAuth -ne 'true') {
  $blockers.Add('Frontend VITE_ENABLE_WECHAT_AUTH is not true; real WeChat path cannot be validated')
}
if (-not $wechatAppIdConfigured -or -not $wechatAppSecretConfigured) {
  $blockers.Add('Server application.yml does not expose both WECHAT_MINIAPP_APP_ID and WECHAT_MINIAPP_APP_SECRET placeholders')
}
if (-not $localWechatAppIdReady -or -not $localWechatAppSecretReady) {
  $blockers.Add("Local WeChat secret input is not ready; follow .sce/runbooks/backend-admin-release/wechat-config-gate-runbook.md and replace placeholder/fake secret in $LocalWechatSecretEnvPath")
} else {
  $observations.Add('Local WeChat secret file is present and passes the current legal-input gate')
}

$liveProbe = $null
if ($EnableLiveProbe) {
  if (-not $resolvedProbeBaseUrl) {
    $blockers.Add('Live probe requested but no probe base URL is available')
  } else {
    $sendCodeProbe = Invoke-LiveProbe `
      -Name 'sendCode' `
      -Method 'Post' `
      -Url "$resolvedProbeBaseUrl/api/auth/sendCode" `
      -Payload @{ phone = $ProbePhone }
    $wechatProbe = Invoke-LiveProbe `
      -Name 'wechatLogin' `
      -Method 'Post' `
      -Url "$resolvedProbeBaseUrl/api/auth/wechat-login" `
      -Payload @{
        code = $ProbeWechatCode
        inviteCode = $ProbeInviteCode
        deviceFingerprint = 'login-auth-live-probe'
      }

    $liveProbe = [ordered]@{
      baseUrl = $resolvedProbeBaseUrl
      sendCode = $sendCodeProbe
      wechatLogin = $wechatProbe
    }

    Write-Utf8Text -Path (Join-Path $captureRoot 'live-probe-sendCode.json') -Text (($sendCodeProbe | ConvertTo-Json -Depth 8))
    Write-Utf8Text -Path (Join-Path $captureRoot 'live-probe-wechat-login.json') -Text (($wechatProbe | ConvertTo-Json -Depth 8))

    $sendCodeCode = Get-ObjectPropertyValue -Object $sendCodeProbe.json -Name 'code'
    $wechatCode = Get-ObjectPropertyValue -Object $wechatProbe.json -Name 'code'
    $wechatMessage = [string](Get-ObjectPropertyValue -Object $wechatProbe.json -Name 'message')

    if ($null -ne $sendCodeCode -and $sendCodeCode -eq 200) {
      $observations.Add('Live probe confirms POST /api/auth/sendCode returns code=200 and still exposes a development verification code')
    } elseif ($sendCodeProbe.error) {
      $blockers.Add("Live probe failed for /api/auth/sendCode: $($sendCodeProbe.error)")
    }

    if ($null -ne $wechatCode -and $wechatCode -ne 200) {
      if ($wechatMessage -like '*appId/appSecret*') {
        $blockers.Add("Live probe confirms /api/auth/wechat-login is blocked by missing miniapp appId/appSecret: $wechatMessage")
      } else {
        $blockers.Add("Live probe confirms /api/auth/wechat-login returns business error: $wechatMessage")
      }
    } elseif ($wechatProbe.error) {
      $blockers.Add("Live probe failed for /api/auth/wechat-login: $($wechatProbe.error)")
    }
  }
}

$result = [ordered]@{
  generatedAt = (Get-Date).ToString('s')
  environmentName = $EnvironmentName
  frontend = [ordered]@{
    envPath = $FrontendEnvPath
    envExamplePath = $FrontendEnvExamplePath
    VITE_API_BASE_URL = $frontendBaseUrl
    VITE_USE_MOCK = $frontendUseMock
    VITE_ENABLE_WECHAT_AUTH = $frontendWechatAuth
    example = $frontendExampleEnv
  }
  admin = [ordered]@{
    envPath = $AdminEnvPath
    VITE_API_BASE_URL = $adminBaseUrl
  }
  server = [ordered]@{
    applicationPath = $ServerAppPath
    exposeWechatMiniappAppId = $wechatAppIdConfigured
    exposeWechatMiniappAppSecret = $wechatAppSecretConfigured
  }
  localWechatInput = [ordered]@{
    path = $LocalWechatSecretEnvPath
    hasAppId = $localWechatAppIdReady
    hasLegalAppSecret = $localWechatAppSecretReady
  }
  liveProbe = $liveProbe
  observations = $observations
  blockers = $blockers
}

$jsonPath = Join-Path $captureRoot 'capture-results.json'
Write-Utf8Text -Path $jsonPath -Text (($result | ConvertTo-Json -Depth 8))

$runtimeSummaryPath = Join-Path $SampleRoot 'runtime-summary.md'
$runtimeSummary = @(
  '# Login Auth Runtime Summary',
  '',
  "- Environment: $EnvironmentName",
  "- Frontend VITE_API_BASE_URL: $frontendBaseUrl",
  "- Frontend VITE_USE_MOCK: $frontendUseMock",
  "- Frontend VITE_ENABLE_WECHAT_AUTH: $frontendWechatAuth",
  "- Admin VITE_API_BASE_URL: $adminBaseUrl",
  "- Server exposes WECHAT_MINIAPP_APP_ID placeholder: $wechatAppIdConfigured",
  "- Server exposes WECHAT_MINIAPP_APP_SECRET placeholder: $wechatAppSecretConfigured",
  "- Local WeChat secret path: $LocalWechatSecretEnvPath",
  "- Local WECHAT_MINIAPP_APP_ID ready: $localWechatAppIdReady",
  "- Local WECHAT_MINIAPP_APP_SECRET legal-input ready: $localWechatAppSecretReady",
  ''
)

if ($EnableLiveProbe) {
  $sendCodeCode = if ($liveProbe) { Get-ObjectPropertyValue -Object $liveProbe.sendCode.json -Name 'code' } else { $null }
  $sendCodeMessage = if ($liveProbe) { [string](Get-ObjectPropertyValue -Object $liveProbe.sendCode.json -Name 'message') } else { '' }
  $wechatCode = if ($liveProbe) { Get-ObjectPropertyValue -Object $liveProbe.wechatLogin.json -Name 'code' } else { $null }
  $wechatMessage = if ($liveProbe) { [string](Get-ObjectPropertyValue -Object $liveProbe.wechatLogin.json -Name 'message') } else { '' }
  $runtimeSummary += @(
    '## Live Probe',
    '',
    "- Probe base URL: $resolvedProbeBaseUrl"
  )

  if ($liveProbe -and $liveProbe.sendCode) {
    $runtimeSummary += "- sendCode transport/code: $($liveProbe.sendCode.statusCode) / $sendCodeCode"
    $runtimeSummary += "- sendCode message: $sendCodeMessage"
  }
  if ($liveProbe -and $liveProbe.wechatLogin) {
    $runtimeSummary += "- wechat-login transport/code: $($liveProbe.wechatLogin.statusCode) / $wechatCode"
    $runtimeSummary += "- wechat-login message: $wechatMessage"
  }
  $runtimeSummary += ''
}

if ($observations.Count -gt 0) {
  $runtimeSummary += '- Observations:'
  foreach ($item in $observations) {
    $runtimeSummary += "  - $item"
  }
  $runtimeSummary += ''
}

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
  '# Login Auth Validation Report',
  '',
  "- Generated At: $((Get-Date).ToString('s'))",
  "- Environment: $EnvironmentName",
  '',
  '## Local Runtime Scan',
  '',
  "- Frontend baseURL: $frontendBaseUrl",
  "- Frontend mock flag: $frontendUseMock",
  "- Frontend WeChat flag: $frontendWechatAuth",
  "- Admin baseURL: $adminBaseUrl",
  "- Server exposes WeChat placeholders: appId=$wechatAppIdConfigured, appSecret=$wechatAppSecretConfigured",
  "- Local WeChat secret gate: appId=$localWechatAppIdReady, legalSecret=$localWechatAppSecretReady",
  '',
  '## Live Probe',
  ''
)

if ($EnableLiveProbe -and $liveProbe) {
  $sendCodeCode = Get-ObjectPropertyValue -Object $liveProbe.sendCode.json -Name 'code'
  $sendCodeMessage = [string](Get-ObjectPropertyValue -Object $liveProbe.sendCode.json -Name 'message')
  $wechatCode = Get-ObjectPropertyValue -Object $liveProbe.wechatLogin.json -Name 'code'
  $wechatMessage = [string](Get-ObjectPropertyValue -Object $liveProbe.wechatLogin.json -Name 'message')
  $reportLines += "- Probe baseURL: $resolvedProbeBaseUrl"
  $reportLines += "- sendCode: transport=$($liveProbe.sendCode.statusCode), code=$sendCodeCode, message=$sendCodeMessage"
  $reportLines += "- wechat-login: transport=$($liveProbe.wechatLogin.statusCode), code=$wechatCode, message=$wechatMessage"
} else {
  $reportLines += '- [ ] Live probe not executed'
}

$reportLines += @(
  '',
  '## Observations',
  ''
)

if ($observations.Count -gt 0) {
  foreach ($item in $observations) {
    $reportLines += "- [x] $item"
  }
} else {
  $reportLines += '- [ ] No live observation recorded'
}

$reportLines += @(
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
  '- [ ] Login page screenshot',
  '- [ ] Auth API capture',
  '- [ ] user.me / verify / invite / level capture',
  '- [ ] DB query result for user / referral_record',
  '- [ ] WeChat error or success evidence when enabled',
  '',
  '## Output Files',
  '',
  '- captures/capture-results.json',
  '- captures/live-probe-sendCode.json (if live probe enabled)',
  '- captures/live-probe-wechat-login.json (if live probe enabled)',
  '- runtime-summary.md',
  '- sample-ledger.md',
  '- validation-report.md'
)

Write-Utf8File -Path $reportPath -Lines $reportLines

python $syncArtifactsScriptPath --sample-dir $SampleRoot

Write-Host "login-auth evidence prepared: $SampleRoot" -ForegroundColor Green
