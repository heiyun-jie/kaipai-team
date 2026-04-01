$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

$corePath = Join-Path $repoRoot '.sce\steering\CORE_PRINCIPLES.md'
$envPath = Join-Path $repoRoot '.sce\steering\ENVIRONMENT.md'
$contextPath = Join-Path $repoRoot '.sce\steering\CURRENT_CONTEXT.md'
$rulesPath = Join-Path $repoRoot '.sce\steering\RULES_GUIDE.md'
$claudePath = Join-Path $repoRoot 'CLAUDE.md'

$errors = New-Object System.Collections.Generic.List[string]

function Add-Error {
  param([string]$Message)
  $script:errors.Add($Message)
}

function Assert-FileExists {
  param([string]$Path, [string]$Label)
  if (-not (Test-Path $Path)) {
    Add-Error "$Label 缺失: $Path"
  }
}

function Get-FileText {
  param([string]$Path)
  if (-not (Test-Path $Path)) {
    return ''
  }
  return Get-Content -Raw $Path
}

Assert-FileExists $corePath 'CORE_PRINCIPLES'
Assert-FileExists $envPath 'ENVIRONMENT'
Assert-FileExists $contextPath 'CURRENT_CONTEXT'
Assert-FileExists $rulesPath 'RULES_GUIDE'
Assert-FileExists $claudePath 'CLAUDE'

$coreText = Get-FileText $corePath
$envText = Get-FileText $envPath
$contextText = Get-FileText $contextPath
$rulesText = Get-FileText $rulesPath
$claudeText = Get-FileText $claudePath

$headingMatches = [regex]::Matches($coreText, '(?m)^##\s+(\d+)\.')
$headingNumbers = @()
foreach ($match in $headingMatches) {
  $headingNumbers += [int]$match.Groups[1].Value
}

if ($headingNumbers.Count -eq 0) {
  Add-Error 'CORE_PRINCIPLES.md 未找到编号二级标题。'
} else {
  $uniqueNumbers = $headingNumbers | Select-Object -Unique
  if ($uniqueNumbers.Count -ne $headingNumbers.Count) {
    Add-Error "CORE_PRINCIPLES.md 存在重复编号: $($headingNumbers -join ', ')"
  }

  $expected = 1
  foreach ($number in $headingNumbers) {
    if ($number -ne $expected) {
      Add-Error "CORE_PRINCIPLES.md 编号不连续，期望 $expected，实际 $number。"
      break
    }
    $expected++
  }
}

if ($coreText -notmatch 'cd kaipai-frontend && npm run audit:steering') {
  Add-Error 'CORE_PRINCIPLES.md 未声明统一治理审计命令。'
}

if ($rulesText -notmatch 'cd kaipai-frontend && npm run audit:steering') {
  Add-Error 'RULES_GUIDE.md 未声明统一治理审计命令。'
}

if ($envText -notmatch '治理审计') {
  Add-Error 'ENVIRONMENT.md 未收录治理审计命令。'
}

if ($contextText -notmatch '05-05') {
  Add-Error 'CURRENT_CONTEXT.md 未标明 05-05 当前主线。'
}

if ($contextText -notmatch '不再围绕信用积分') {
  Add-Error 'CURRENT_CONTEXT.md 未声明信用主线已切换。'
}

$staleMarkers = @(
  '21 个 Spec',
  '16+ 页面',
  'KpCreditBadge',
  'KpLevelTag',
  'V1.1 新增 credit',
  '05-03 credit-score | 信用积分（0→100 叠加）与演员等级（LV.1-7） | 预留'
)

foreach ($marker in $staleMarkers) {
  if ($claudeText.Contains($marker)) {
    Add-Error "CLAUDE.md 仍包含过期描述: $marker"
  }
}

if ($claudeText -notmatch '当前产品主线：演员名片分享 \+ 会员分层') {
  Add-Error 'CLAUDE.md 未更新为当前产品主线。'
}

if ($errors.Count -gt 0) {
  Write-Host 'steering audit failed:' -ForegroundColor Red
  foreach ($error in $errors) {
    Write-Host " - $error" -ForegroundColor Red
  }
  exit 1
}

Write-Host 'steering audit passed' -ForegroundColor Green
