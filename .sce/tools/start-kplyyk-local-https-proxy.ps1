param(
  [string]$RuntimeDir = "$PSScriptRoot\..\runtime\kplyyk-local-proxy",
  [string]$Domain = "localhost",
  [string]$TargetHost = "127.0.0.1",
  [int]$TargetPort = 18080,
  [int]$ListenPort = 18443,
  [string]$RemoteHost = "192.168.1.108",
  [string]$RemoteUser = "zeno-deocker",
  [string]$IdentityFile = "$env:USERPROFILE\.ssh\id_ed25519",
  [string]$RemoteForwardHost = "127.0.0.1",
  [int]$RemoteForwardPort = 8010,
  [switch]$UseSshTunnel = $true,
  [switch]$SkipHosts
)

$ErrorActionPreference = "Stop"

function Assert-Admin {
  $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = [Security.Principal.WindowsPrincipal]::new($identity)
  if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "需要管理员权限：绑定 443 端口并写入 hosts。"
  }
}

function Resolve-OpenSsl {
  $candidates = @(
    "C:\Program Files\Git\mingw64\bin\openssl.exe",
    "C:\Program Files\Git\usr\bin\openssl.exe"
  )
  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) {
      return $candidate
    }
  }
  $command = Get-Command openssl -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }
  throw "未找到 openssl.exe，无法生成本地 HTTPS 证书。"
}

function Set-HostsRecord {
  param(
    [Parameter(Mandatory = $true)][string]$HostName,
    [Parameter(Mandatory = $true)][string]$IpAddress
  )

  $hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
  $backupPath = Join-Path $RuntimeDir "hosts.$(Get-Date -Format 'yyyyMMdd-HHmmss').before"
  Copy-Item -LiteralPath $hostsPath -Destination $backupPath -Force

  $lines = @(Get-Content -LiteralPath $hostsPath -ErrorAction Stop)
  $pattern = "^\s*\S+\s+.*\b$([regex]::Escape($HostName))\b"
  $filtered = @($lines | Where-Object { $_ -notmatch $pattern })
  $filtered += "$IpAddress $HostName # kplyyk-local-https-proxy"
  [System.IO.File]::WriteAllLines($hostsPath, $filtered, [System.Text.Encoding]::ASCII)
  ipconfig /flushdns | Out-Null
  return $backupPath
}

function Stop-ExistingProxy {
  $pidPath = Join-Path $RuntimeDir "proxy.pid"
  if (Test-Path -LiteralPath $pidPath) {
    $rawPid = (Get-Content -LiteralPath $pidPath -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($rawPid -match '^\d+$') {
      $process = Get-Process -Id ([int]$rawPid) -ErrorAction SilentlyContinue
      if ($process) {
        Stop-Process -Id $process.Id -Force
      }
    }
  }

  $tunnelPidPath = Join-Path $RuntimeDir "ssh-tunnel.pid"
  if (Test-Path -LiteralPath $tunnelPidPath) {
    $rawTunnelPid = (Get-Content -LiteralPath $tunnelPidPath -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($rawTunnelPid -match '^\d+$') {
      $tunnelProcess = Get-Process -Id ([int]$rawTunnelPid) -ErrorAction SilentlyContinue
      if ($tunnelProcess) {
        Stop-Process -Id $tunnelProcess.Id -Force
      }
    }
    Remove-Item -LiteralPath $tunnelPidPath -Force -ErrorAction SilentlyContinue
  }
}

function Start-SshTunnel {
  if (-not $UseSshTunnel) {
    return $null
  }

  if (-not (Test-Path -LiteralPath $IdentityFile)) {
    throw "SSH identity file not found: $IdentityFile"
  }

  $ssh = (Get-Command ssh -ErrorAction Stop).Source
  $tunnelLogPath = Join-Path $RuntimeDir "ssh-tunnel.log"
  $tunnelErrorLogPath = Join-Path $RuntimeDir "ssh-tunnel-error.log"
  $tunnelPidPath = Join-Path $RuntimeDir "ssh-tunnel.pid"
  $forwardSpec = "${TargetHost}:$TargetPort`:$RemoteForwardHost`:$RemoteForwardPort"

  $existingTunnelPort = Get-NetTCPConnection -LocalAddress $TargetHost -LocalPort $TargetPort -State Listen -ErrorAction SilentlyContinue
  if ($existingTunnelPort) {
    throw "${TargetHost}:$TargetPort 已被占用，无法建立 SSH 隧道。"
  }

  $tunnelProcess = Start-Process `
    -FilePath $ssh `
    -ArgumentList @(
      "-N",
      "-o", "ExitOnForwardFailure=yes",
      "-o", "ServerAliveInterval=30",
      "-o", "ServerAliveCountMax=3",
      "-L", $forwardSpec,
      "-i", $IdentityFile,
      "-o", "BatchMode=yes",
      "-o", "IdentitiesOnly=yes",
      "-o", "StrictHostKeyChecking=accept-new",
      "$RemoteUser@$RemoteHost"
    ) `
    -WindowStyle Hidden `
    -PassThru `
    -RedirectStandardOutput $tunnelLogPath `
    -RedirectStandardError $tunnelErrorLogPath

  [System.IO.File]::WriteAllText($tunnelPidPath, "$($tunnelProcess.Id)`n", [System.Text.Encoding]::ASCII)

  $deadline = (Get-Date).AddSeconds(10)
  do {
    Start-Sleep -Milliseconds 300
    $listener = Get-NetTCPConnection -LocalAddress $TargetHost -LocalPort $TargetPort -State Listen -ErrorAction SilentlyContinue
    if ($listener) {
      return [pscustomobject]@{
        pid = $tunnelProcess.Id
        local = "http://${TargetHost}:$TargetPort"
        remote = "http://${RemoteForwardHost}:$RemoteForwardPort"
        logPath = $tunnelLogPath
        errorLogPath = $tunnelErrorLogPath
      }
    }
  } while ((Get-Date) -lt $deadline)

  Stop-Process -Id $tunnelProcess.Id -Force -ErrorAction SilentlyContinue
  throw "SSH 隧道启动超时，详见 $tunnelErrorLogPath"
}

New-Item -ItemType Directory -Path $RuntimeDir -Force | Out-Null
$RuntimeDir = (Resolve-Path -LiteralPath $RuntimeDir).Path

$shouldUpdateHosts = -not $SkipHosts -and $Domain -notin @("localhost", "127.0.0.1")
if ($shouldUpdateHosts -or $ListenPort -eq 443) {
  Assert-Admin
}

$node = (Get-Command node -ErrorAction Stop).Source
$openssl = Resolve-OpenSsl
$certName = $Domain -replace '[^a-zA-Z0-9.-]', '_'
$keyPath = Join-Path $RuntimeDir "$certName.local.key"
$certPath = Join-Path $RuntimeDir "$certName.local.crt"
$confPath = Join-Path $RuntimeDir "openssl-kplyyk.cnf"
$proxyScript = Resolve-Path -LiteralPath "$PSScriptRoot\kplyyk-local-https-proxy.js"
$logPath = Join-Path $RuntimeDir "proxy.log"
$errorLogPath = Join-Path $RuntimeDir "proxy-error.log"
$opensslLogPath = Join-Path $RuntimeDir "openssl.log"
$opensslErrorPath = Join-Path $RuntimeDir "openssl-error.log"

if (-not (Test-Path -LiteralPath $keyPath) -or -not (Test-Path -LiteralPath $certPath)) {
  @"
[req]
distinguished_name = dn
x509_extensions = v3_req
prompt = no

[dn]
CN = $Domain

[v3_req]
subjectAltName = @alt_names
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = $Domain
"@ | Set-Content -LiteralPath $confPath -Encoding ASCII

  $opensslProcess = Start-Process `
    -FilePath $openssl `
    -ArgumentList @("req", "-x509", "-nodes", "-days", "30", "-newkey", "rsa:2048", "-keyout", $keyPath, "-out", $certPath, "-config", $confPath) `
    -Wait `
    -PassThru `
    -RedirectStandardOutput $opensslLogPath `
    -RedirectStandardError $opensslErrorPath `
    -WindowStyle Hidden
  if ($opensslProcess.ExitCode -ne 0) {
    throw "openssl 生成本地证书失败，详见 $opensslLogPath"
  }
}

Stop-ExistingProxy
$tunnel = Start-SshTunnel
$hostsBackup = $null
if ($shouldUpdateHosts) {
  $hostsBackup = Set-HostsRecord -HostName $Domain -IpAddress "127.0.0.1"
}

$env:KPLYYK_LOCAL_PROXY_RUNTIME_DIR = $RuntimeDir
$env:KPLYYK_LOCAL_PROXY_DOMAIN = $Domain
$env:KPLYYK_LOCAL_PROXY_PORT = "$ListenPort"
$env:KPLYYK_LOCAL_PROXY_TARGET_HOST = $TargetHost
$env:KPLYYK_LOCAL_PROXY_TARGET_PORT = "$TargetPort"

$existing443 = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $ListenPort -State Listen -ErrorAction SilentlyContinue
if ($existing443) {
  throw "127.0.0.1:$ListenPort 已被占用，无法启动本地 HTTPS 代理。"
}

$process = Start-Process `
  -FilePath $node `
  -ArgumentList "`"$proxyScript`"" `
  -WindowStyle Hidden `
  -PassThru `
  -RedirectStandardOutput $logPath `
  -RedirectStandardError $errorLogPath

Start-Sleep -Seconds 2

$bodyFile = Join-Path $RuntimeDir "probe-send-code.json"
[System.IO.File]::WriteAllText($bodyFile, '{"phone":"13800138000"}', [System.Text.UTF8Encoding]::new($false))
$localBaseUrl = if ($ListenPort -eq 443) { "https://$Domain" } else { "https://${Domain}:$ListenPort" }
$health = & curl.exe --noproxy "*" -k -sS --max-time 10 "$localBaseUrl/__proxy_health"
$sendCode = & curl.exe --noproxy "*" -k -sS --max-time 10 -H "Content-Type: application/json" --data-binary "@$bodyFile" "$localBaseUrl/api/auth/sendCode"

[pscustomobject]@{
  status = "started"
  pid = $process.Id
  hostsBackup = $hostsBackup
  domain = $Domain
  localUrl = $localBaseUrl
  listenUrl = "https://127.0.0.1:$ListenPort"
  target = "http://${TargetHost}:$TargetPort"
  sshTunnel = $tunnel
  logPath = $logPath
  errorLogPath = $errorLogPath
  health = $health
  sendCode = $sendCode
} | ConvertTo-Json -Depth 4
