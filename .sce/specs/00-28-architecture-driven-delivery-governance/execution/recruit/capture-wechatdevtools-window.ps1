param(
  [Parameter(Mandatory = $true)]
  [string]$OutputPath,
  [string]$WindowTitlePattern = '*微信开发者工具*',
  [int]$ForegroundDelayMs = 800
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;

public static class WechatDevtoolsWindowCapture {
  [DllImport("user32.dll")]
  public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

  [DllImport("user32.dll")]
  public static extern bool SetForegroundWindow(IntPtr hWnd);

  [DllImport("user32.dll")]
  public static extern bool IsIconic(IntPtr hWnd);

  [DllImport("user32.dll")]
  public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);

  [DllImport("user32.dll")]
  public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);

  [StructLayout(LayoutKind.Sequential)]
  public struct RECT {
    public int Left;
    public int Top;
    public int Right;
    public int Bottom;
  }
}
'@

$windowProcess = Get-Process wechatdevtools |
  Where-Object { $_.MainWindowTitle -like $WindowTitlePattern } |
  Select-Object -First 1

if (-not $windowProcess) {
  throw "wechatdevtools main window not found for pattern: $WindowTitlePattern"
}

if ([WechatDevtoolsWindowCapture]::IsIconic($windowProcess.MainWindowHandle)) {
  [WechatDevtoolsWindowCapture]::ShowWindowAsync($windowProcess.MainWindowHandle, 9) | Out-Null
}

[WechatDevtoolsWindowCapture]::SetForegroundWindow($windowProcess.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds $ForegroundDelayMs

$rect = New-Object WechatDevtoolsWindowCapture+RECT
if (-not [WechatDevtoolsWindowCapture]::GetWindowRect($windowProcess.MainWindowHandle, [ref]$rect)) {
  throw "GetWindowRect failed for handle: $($windowProcess.MainWindowHandle)"
}

$width = $rect.Right - $rect.Left
$height = $rect.Bottom - $rect.Top

if ($width -le 0 -or $height -le 0) {
  throw "invalid window bounds width=$width height=$height"
}

$outputDir = Split-Path -Parent $OutputPath
if ($outputDir) {
  New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

$bitmap = New-Object System.Drawing.Bitmap $width, $height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)

try {
  $hdc = $graphics.GetHdc()
  try {
    $printed = [WechatDevtoolsWindowCapture]::PrintWindow($windowProcess.MainWindowHandle, $hdc, 2)
  } finally {
    $graphics.ReleaseHdc($hdc)
  }

  if (-not $printed) {
    throw "PrintWindow failed for handle: $($windowProcess.MainWindowHandle)"
  }

  $bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
} finally {
  $graphics.Dispose()
  $bitmap.Dispose()
}

[pscustomobject]@{
  outputPath = $OutputPath
  width = $width
  height = $height
  processId = $windowProcess.Id
  windowTitle = $windowProcess.MainWindowTitle
  captureMode = 'PrintWindow'
} | ConvertTo-Json -Compress
