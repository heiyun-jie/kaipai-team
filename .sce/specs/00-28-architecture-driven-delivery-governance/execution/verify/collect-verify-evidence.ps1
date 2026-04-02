param(
  [Parameter(Mandatory = $true)]
  [string]$ApiBaseUrl,

  [string]$ActorToken,
  [string]$AdminToken,
  [string]$UserId,
  [string]$VerificationId,
  [string]$RetryVerificationId,
  [string]$OutputDir
)

$ErrorActionPreference = 'Stop'

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
$captureRoot = if ($OutputDir) { Join-Path $OutputDir 'captures' } else { Join-Path $scriptDir 'captures' }
$captureRoot = [System.IO.Path]::GetFullPath($captureRoot)
Ensure-Directory -Path $captureRoot

$actorHeaders = New-Headers -Token $ActorToken
$adminHeaders = New-Headers -Token $AdminToken

$context = @{
  capturedAt = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  apiBaseUrl = $baseUrl
  userId = $UserId
  verificationId = $VerificationId
  retryVerificationId = $RetryVerificationId
  actorTokenProvided = [bool]$ActorToken
  adminTokenProvided = [bool]$AdminToken
}
Write-JsonFile -Path (Join-Path $captureRoot 'capture-context.json') -Value $context

$targets = New-Object 'System.Collections.Generic.List[hashtable]'

if ($ActorToken) {
  Add-Endpoint -Targets $targets -Name 'actor_verify_status_final' -Method 'GET' -Url "$baseUrl/api/verify/status" -TokenType 'actor'
  Add-Endpoint -Targets $targets -Name 'actor_level_info_final' -Method 'GET' -Url "$baseUrl/api/level/info" -TokenType 'actor'
  Add-Endpoint -Targets $targets -Name 'actor_user_me_final' -Method 'GET' -Url "$baseUrl/api/user/me" -TokenType 'actor'
}

if ($AdminToken -and $UserId) {
  Add-Endpoint -Targets $targets -Name 'admin_verify_list_final' -Method 'GET' -Url "$baseUrl/api/admin/verify/list?pageNo=1&pageSize=20&userId=$UserId" -TokenType 'admin'
}

if ($AdminToken -and $VerificationId) {
  Add-Endpoint -Targets $targets -Name 'admin_verify_detail_first' -Method 'GET' -Url "$baseUrl/api/admin/verify/$VerificationId" -TokenType 'admin'
}

if ($AdminToken -and $RetryVerificationId) {
  Add-Endpoint -Targets $targets -Name 'admin_verify_detail_retry' -Method 'GET' -Url "$baseUrl/api/admin/verify/$RetryVerificationId" -TokenType 'admin'
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
$summaryLines.Add("userId=$UserId")
$summaryLines.Add("verificationId=$VerificationId")
$summaryLines.Add("retryVerificationId=$RetryVerificationId")
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

Write-Host "verify evidence captured: $captureRoot" -ForegroundColor Green
