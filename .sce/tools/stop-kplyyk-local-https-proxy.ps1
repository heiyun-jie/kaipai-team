param(
  [string]$RuntimeDir = "$PSScriptRoot\..\runtime\kplyyk-local-proxy",
  [string]$Domain = "localhost"
)

$ErrorActionPreference = "Stop"

function Assert-Admin {
  $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = [Security.Principal.WindowsPrincipal]::new($identity)
  if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "需要管理员权限：清理 hosts。"
  }
}

$shouldUpdateHosts = $Domain -notin @("localhost", "127.0.0.1")
if ($shouldUpdateHosts) {
  Assert-Admin
}

$RuntimeDir = if (Test-Path -LiteralPath $RuntimeDir) { (Resolve-Path -LiteralPath $RuntimeDir).Path } else { $RuntimeDir }
$pidPath = Join-Path $RuntimeDir "proxy.pid"
if (Test-Path -LiteralPath $pidPath) {
  $rawPid = (Get-Content -LiteralPath $pidPath -ErrorAction SilentlyContinue | Select-Object -First 1)
  if ($rawPid -match '^\d+$') {
    $process = Get-Process -Id ([int]$rawPid) -ErrorAction SilentlyContinue
    if ($process) {
      Stop-Process -Id $process.Id -Force
    }
  }
  Remove-Item -LiteralPath $pidPath -Force -ErrorAction SilentlyContinue
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

if ($shouldUpdateHosts) {
  $hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
  $pattern = "^\s*127\.0\.0\.1\s+.*\b$([regex]::Escape($Domain))\b.*kplyyk-local-https-proxy"
  $lines = @(Get-Content -LiteralPath $hostsPath -ErrorAction Stop | Where-Object { $_ -notmatch $pattern })
  [System.IO.File]::WriteAllLines($hostsPath, $lines, [System.Text.Encoding]::ASCII)
  ipconfig /flushdns | Out-Null
}

[pscustomobject]@{
  status = "stopped"
  domain = $Domain
} | ConvertTo-Json
