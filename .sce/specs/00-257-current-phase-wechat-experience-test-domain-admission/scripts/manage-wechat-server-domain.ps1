param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Get', 'Add')]
    [string]$Mode,

    [Parameter(Mandatory = $true)]
    [string]$SecretFile,

    [string]$OutputPath,

    [string]$TargetDomain = 'https://test-api.kplyyk.com',

    [string]$ExpectedAppId = 'wx4dcc4e1066fd0fb9'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Read-DotEnv {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Secret file does not exist: $Path"
    }

    $values = @{}
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match '^\s*#' -or [string]::IsNullOrWhiteSpace($line)) {
            continue
        }
        if ($line -notmatch '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$') {
            continue
        }
        $name = $Matches[1]
        $value = $Matches[2].Trim()
        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or
            ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        $values[$name] = $value
    }
    return $values
}

function Assert-WeChatSuccess {
    param(
        [object]$Response,
        [string]$Operation
    )

    if ($null -ne $Response.PSObject.Properties['errcode'] -and [int]$Response.errcode -ne 0) {
        throw "$Operation failed: errcode=$($Response.errcode), errmsg=$($Response.errmsg)"
    }
}

function ConvertTo-NormalizedDomainConfig {
    param(
        [object]$Response,
        [string]$AppId
    )

    $domains = [ordered]@{}
    $domainProperties = @(
        $Response.PSObject.Properties |
            Where-Object { $_.Name -match 'domain$' } |
            Sort-Object Name
    )
    foreach ($property in $domainProperties) {
        $values = @($property.Value | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
        $domains[$property.Name] = @($values | ForEach-Object { [string]$_ } | Sort-Object -Unique)
    }

    return [ordered]@{
        appId = $AppId
        domains = $domains
    }
}

$secrets = Read-DotEnv -Path $SecretFile
$appId = [string]$secrets['WECHAT_MINIAPP_APP_ID']
$appSecret = [string]$secrets['WECHAT_MINIAPP_APP_SECRET']

if ([string]::IsNullOrWhiteSpace($appId) -or [string]::IsNullOrWhiteSpace($appSecret)) {
    throw 'WECHAT_MINIAPP_APP_ID and WECHAT_MINIAPP_APP_SECRET must both be present.'
}
if ($appId -ne $ExpectedAppId) {
    throw "Resolved AppID does not match the expected AppID: $appId"
}

$tokenUri = 'https://api.weixin.qq.com/cgi-bin/token' +
    '?grant_type=client_credential' +
    '&appid=' + [uri]::EscapeDataString($appId) +
    '&secret=' + [uri]::EscapeDataString($appSecret)
$tokenResponse = Invoke-RestMethod -Uri $tokenUri -Method Get -TimeoutSec 30
Assert-WeChatSuccess -Response $tokenResponse -Operation 'client_credential token'
$accessToken = [string]$tokenResponse.access_token
if ([string]::IsNullOrWhiteSpace($accessToken)) {
    throw 'client_credential token endpoint returned no access token.'
}

$domainUri = "https://api.weixin.qq.com/wxa/modify_domain?access_token=$accessToken"

if ($Mode -eq 'Get') {
    if ([string]::IsNullOrWhiteSpace($OutputPath)) {
        throw 'OutputPath is required for Get mode.'
    }
    $response = Invoke-RestMethod `
        -Uri $domainUri `
        -Method Post `
        -ContentType 'application/json; charset=utf-8' `
        -Body '{"action":"get"}' `
        -TimeoutSec 30
    Assert-WeChatSuccess -Response $response -Operation 'modify_domain/get'
    $normalized = ConvertTo-NormalizedDomainConfig -Response $response -AppId $appId
    $parent = Split-Path -Parent $OutputPath
    if (-not [string]::IsNullOrWhiteSpace($parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $normalized | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    $fieldCount = @($normalized.domains.Keys).Count
    $domainCount = 0
    foreach ($field in $normalized.domains.Keys) {
        $domainCount += @($normalized.domains[$field]).Count
    }
    [ordered]@{
        result = 'DOMAIN_BASELINE_READ'
        appId = $appId
        fieldCount = $fieldCount
        domainCount = $domainCount
        outputPath = $OutputPath
    } | ConvertTo-Json -Compress
    exit 0
}

if ($TargetDomain -notmatch '^https://[A-Za-z0-9.-]+(?::\d+)?$') {
    throw "TargetDomain must be an HTTPS origin without a path: $TargetDomain"
}

$addRequest = [ordered]@{
    action = 'add'
    requestdomain = @($TargetDomain)
    uploaddomain = @($TargetDomain)
    downloaddomain = @($TargetDomain)
} | ConvertTo-Json -Depth 5 -Compress
$addResponse = Invoke-RestMethod `
    -Uri $domainUri `
    -Method Post `
    -ContentType 'application/json; charset=utf-8' `
    -Body $addRequest `
    -TimeoutSec 30
Assert-WeChatSuccess -Response $addResponse -Operation 'modify_domain/add'
[ordered]@{
    result = 'DOMAIN_ADD_ACCEPTED'
    appId = $appId
    targetDomain = $TargetDomain
    changedFields = @('requestdomain', 'uploaddomain', 'downloaddomain')
    errcode = if ($null -ne $addResponse.PSObject.Properties['errcode']) { [int]$addResponse.errcode } else { 0 }
    errmsg = if ($null -ne $addResponse.PSObject.Properties['errmsg']) { [string]$addResponse.errmsg } else { 'ok' }
} | ConvertTo-Json -Compress
