param(
  [string]$JarPath,
  [string]$SecretFile = "$PSScriptRoot\..\config\local-secrets\wechat-miniapp.env",
  [string]$RuntimeDir = "$PSScriptRoot\..\runtime\kaipai-local-backend",
  [string]$MySqlContainer = "kaipai-mysql-local",
  [string]$RedisContainer = "kaipai-local-redis",
  [int]$Port = 8010,
  [int]$StartupTimeoutSeconds = 90,
  [int]$ReplacePid = 0,
  [switch]$Restart,
  [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Get-DotEnvValues {
  param([Parameter(Mandatory = $true)][string]$Path)

  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    throw "Local WeChat secret file is missing."
  }

  $values = @{}
  foreach ($rawLine in [System.IO.File]::ReadAllLines($Path, [System.Text.Encoding]::UTF8)) {
    $line = $rawLine.Trim()
    if (-not $line -or $line.StartsWith("#") -or -not $rawLine.Contains("=")) {
      continue
    }

    $parts = $rawLine.Split(@("="), 2, [System.StringSplitOptions]::None)
    $key = $parts[0].Trim()
    $value = $parts[1].Trim().Trim('"').Trim("'")
    if ($key) {
      $values[$key] = $value
    }
  }
  return $values
}

function Assert-WeChatConfig {
  param(
    [Parameter(Mandatory = $true)][hashtable]$Values,
    [Parameter(Mandatory = $true)][string]$ProjectConfigPath
  )

  $appId = [string]$Values["WECHAT_MINIAPP_APP_ID"]
  $appSecret = [string]$Values["WECHAT_MINIAPP_APP_SECRET"]
  if ($appId -notmatch '^wx[a-zA-Z0-9]{16}$') {
    throw "Local WeChat appId failed the format gate."
  }
  if ([string]::IsNullOrWhiteSpace($appSecret)) {
    throw "Local WeChat appSecret is missing."
  }

  $placeholderPatterns = @(
    'replace[-_ ]?with[-_ ]?real',
    'fake',
    'dummy',
    'changeme',
    'example',
    'placeholder',
    'todo',
    'test',
    'sample'
  )
  foreach ($pattern in $placeholderPatterns) {
    if ($appSecret -match $pattern) {
      throw "Local WeChat appSecret failed the placeholder gate."
    }
  }
  if ($appSecret.Length -lt 16) {
    throw "Local WeChat appSecret failed the length gate."
  }

  if (-not (Test-Path -LiteralPath $ProjectConfigPath -PathType Leaf)) {
    throw "MiniProgram project.config.json is missing."
  }
  $projectConfig = Get-Content -LiteralPath $ProjectConfigPath -Raw | ConvertFrom-Json
  if ([string]::IsNullOrWhiteSpace([string]$projectConfig.appid) -or $projectConfig.appid -cne $appId) {
    throw "Local WeChat appId does not match the MiniProgram project config."
  }
}

function Get-ContainerInspect {
  param([Parameter(Mandatory = $true)][string]$Name)

  $raw = & docker inspect $Name 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $raw) {
    throw "Required local container is unavailable: $Name"
  }
  $items = @($raw | ConvertFrom-Json)
  if ($items.Count -ne 1 -or -not $items[0].State.Running) {
    throw "Required local container is not running: $Name"
  }
  return $items[0]
}

function Assert-LocalDockerContext {
  $contextName = [string](& docker context show 2>$null)
  if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($contextName)) {
    throw "Docker context lookup failed."
  }

  $raw = & docker context inspect $contextName.Trim() 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $raw) {
    throw "Docker context inspection failed."
  }
  $contexts = @(($raw -join [Environment]::NewLine) | ConvertFrom-Json)
  $dockerHost = if ($contexts.Count -eq 1) { [string]$contexts[0].Endpoints.docker.Host } else { '' }
  if ($dockerHost -notmatch '^(?i)npipe:') {
    throw "The active Docker context is not the local Windows Docker Desktop engine."
  }
}

function Assert-LocalContainerPort {
  param(
    [Parameter(Mandatory = $true)]$Inspect,
    [Parameter(Mandatory = $true)][string]$ContainerPort,
    [Parameter(Mandatory = $true)][string]$HostPort
  )

  $bindings = @($Inspect.NetworkSettings.Ports.$ContainerPort)
  if ($bindings.Count -eq 0 -or -not ($bindings | Where-Object { $_.HostPort -eq $HostPort })) {
    throw "Required local container port mapping is not ready."
  }
}

function Get-MySqlRootPassword {
  param([Parameter(Mandatory = $true)]$Inspect)

  $entry = @($Inspect.Config.Env | Where-Object { $_ -like 'MYSQL_ROOT_PASSWORD=*' } | Select-Object -First 1)
  if ($entry.Count -ne 1) {
    throw "Local MySQL credential lookup failed."
  }
  $password = [string]$entry[0].Substring('MYSQL_ROOT_PASSWORD='.Length)
  if ([string]::IsNullOrWhiteSpace($password)) {
    throw "Local MySQL credential lookup failed."
  }
  return $password
}

function Assert-LocalServicesReady {
  param(
    [Parameter(Mandatory = $true)][string]$MySqlName,
    [Parameter(Mandatory = $true)][string]$RedisName
  )

  $mysqlSql = "SELECT IF(COUNT(*)=1,'DATABASE_READY','DATABASE_MISSING') FROM information_schema.SCHEMATA WHERE SCHEMA_NAME='kaipai_dev'; SELECT 1;"
  $mysqlPayload = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($mysqlSql))
  $mysqlCommand = 'printf %s "$1" | base64 -d | MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N -s'
  $mysqlResult = @(& docker exec $MySqlName sh -c $mysqlCommand sh $mysqlPayload 2>$null)
  if ($LASTEXITCODE -ne 0 -or $mysqlResult.Count -ne 2 -or $mysqlResult[0].Trim() -cne 'DATABASE_READY' -or $mysqlResult[1].Trim() -cne '1') {
    throw "Local MySQL service or kaipai_dev is not ready."
  }

  $redisResult = [string](& docker exec $RedisName redis-cli PING 2>$null)
  if ($LASTEXITCODE -ne 0 -or $redisResult.Trim() -cne 'PONG') {
    throw "Local Redis service is not ready for unauthenticated localhost access."
  }
}

function Invoke-LocalMySqlQuery {
  param(
    [Parameter(Mandatory = $true)][string]$MySqlName,
    [Parameter(Mandatory = $true)][string]$DatabaseName,
    [Parameter(Mandatory = $true)][string]$Sql
  )

  if ($DatabaseName -cne 'kaipai_dev') {
    throw "Local schema queries are pinned to kaipai_dev."
  }

  $payload = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Sql))
  $mysqlCommand = 'printf %s "$1" | base64 -d | MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N -s "$2"'
  $result = @(& docker exec $MySqlName sh -c $mysqlCommand sh $payload $DatabaseName 2>$null)
  if ($LASTEXITCODE -ne 0) {
    throw "Local MySQL schema query failed."
  }
  return $result
}

function Assert-LocalSchemaCompatible {
  param(
    [Parameter(Mandatory = $true)][string]$MySqlName,
    [Parameter(Mandatory = $true)][string]$DatabaseName,
    [Parameter(Mandatory = $true)][string]$MigrationDirectory
  )

  if (-not (Test-Path -LiteralPath $MigrationDirectory -PathType Container)) {
    throw "Backend migration directory is missing."
  }

  $migrationFiles = @(
    Get-ChildItem -LiteralPath $MigrationDirectory -File -Filter 'V*.sql' |
      Sort-Object Name
  )
  if ($migrationFiles.Count -eq 0) {
    throw "Backend migration directory contains no migration files."
  }

  $historyTableSql = @"
SELECT COUNT(*)
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'schema_release_history';
"@
  $historyTableResult = @(Invoke-LocalMySqlQuery -MySqlName $MySqlName -DatabaseName $DatabaseName -Sql $historyTableSql)
  if ($historyTableResult.Count -ne 1 -or $historyTableResult[0].Trim() -cne '1') {
    throw "Local database schema is incompatible: table schema_release_history is missing."
  }

  $historySql = "SELECT script, UPPER(checksum) FROM schema_release_history ORDER BY script;"
  $historyRows = @(Invoke-LocalMySqlQuery -MySqlName $MySqlName -DatabaseName $DatabaseName -Sql $historySql)
  $historyByScript = @{}
  foreach ($row in $historyRows) {
    $parts = ([string]$row) -split "`t", 2
    if ($parts.Count -eq 2 -and -not [string]::IsNullOrWhiteSpace($parts[0])) {
      $historyByScript[$parts[0]] = $parts[1]
    }
  }

  $issues = @()
  foreach ($migration in $migrationFiles) {
    $expectedHash = (Get-FileHash -LiteralPath $migration.FullName -Algorithm SHA256).Hash
    if (-not $historyByScript.ContainsKey($migration.Name)) {
      $issues += "migration:$($migration.Name)"
      continue
    }
    if ([string]$historyByScript[$migration.Name] -cne $expectedHash) {
      $issues += "checksum:$($migration.Name)"
    }
  }

  $requiredTables = @(
    'actor_profile_representative_work',
    'actor_media_asset',
    'actor_media_asset_page',
    'actor_profile_asset',
    'actor_work_asset',
    'share_card_work',
    'share_card_asset',
    'share_card_favorite',
    'ai_profile_import_config',
    'ai_profile_import_config_audit',
    'ai_profile_import_request_audit',
    'ai_profile_import_prompt_template',
    'ai_profile_import_prompt_version',
    'ai_profile_import_prompt_audit'
  )
  $tableSql = @"
SELECT TABLE_NAME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME IN ('$($requiredTables -join "','")');
"@
  $presentTables = @(
    Invoke-LocalMySqlQuery -MySqlName $MySqlName -DatabaseName $DatabaseName -Sql $tableSql |
      ForEach-Object { ([string]$_).Trim() }
  )
  foreach ($tableName in $requiredTables) {
    if ($tableName -notin $presentTables) {
      $issues += "table:$tableName"
    }
  }

  $requiredColumns = @(
    'actor_profile.avatar_asset_id',
    'actor_profile.weight',
    'actor_profile.current_resume_asset_id',
    'actor_profile.birth_year',
    'actor_profile.birth_month',
    'actor_profile.birth_day',
    'actor_profile.birth_precision',
    'actor_profile.origin_place',
    'actor_profile.school_name',
    'actor_profile.major_name',
    'actor_profile.language_tags_json',
    'actor_profile.specialty_tags_json',
    'actor_profile.role_type_tags_json',
    'actor_profile.professional_ability_tags_json',
    'actor_profile.work_library_version',
    'actor_experience.publish_status',
    'actor_experience.work_type_code',
    'actor_experience.role_level_code',
    'actor_experience.sync_sound_status',
    'actor_experience.collaborators_json',
    'actor_experience.achievement_text',
    'actor_experience.normalized_drama_name',
    'actor_experience.normalized_role_name',
    'actor_experience.dedupe_key',
    'actor_experience.source_type',
    'ai_profile_import_request_audit.scene',
    'ai_profile_import_request_audit.prompt_template_code',
    'ai_profile_import_request_audit.prompt_version_id',
    'ai_profile_import_request_audit.prompt_version_no',
    'ai_profile_import_request_audit.prompt_schema_version',
    'ai_profile_import_request_audit.prompt_contract_version',
    'ai_profile_import_request_audit.prompt_runtime_sha256'
  )
  $columnSql = @"
SELECT CONCAT(TABLE_NAME, '.', COLUMN_NAME)
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND CONCAT(TABLE_NAME, '.', COLUMN_NAME) IN ('$($requiredColumns -join "','")');
"@
  $presentColumns = @(
    Invoke-LocalMySqlQuery -MySqlName $MySqlName -DatabaseName $DatabaseName -Sql $columnSql |
      ForEach-Object { ([string]$_).Trim() }
  )
  foreach ($columnName in $requiredColumns) {
    if ($columnName -notin $presentColumns) {
      $issues += "column:$columnName"
    }
  }

  if ($issues.Count -gt 0) {
    $summary = $issues -join ', '
    throw "Local database schema is incompatible with the repository migration baseline: $summary. Apply pending db/migration files in filename order before starting the backend."
  }
}

function Get-PortListeners {
  param([Parameter(Mandatory = $true)][int]$LocalPort)

  return @(
    Get-NetTCPConnection -LocalPort $LocalPort -State Listen -ErrorAction SilentlyContinue |
      Select-Object -ExpandProperty OwningProcess -Unique
  )
}

function Get-KaipaiBackendProcessDescriptor {
  param([Parameter(Mandatory = $true)][int]$ProcessId)

  $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
  $cim = Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId" -ErrorAction SilentlyContinue
  if (-not $process -or -not $cim -or $process.ProcessName -ine 'java') {
    throw "Port $Port is owned by a process that this script will not stop."
  }

  $jarMatch = [regex]::Match([string]$cim.CommandLine, '(?i)(?:^|\s)-jar\s+(?:"(?<quoted>[^"]+)"|(?<plain>\S+))')
  if (-not $jarMatch.Success) {
    throw "Port $Port is owned by a Java process that is not a KaiPai backend jar."
  }
  $jarArgument = if ($jarMatch.Groups['quoted'].Success) { $jarMatch.Groups['quoted'].Value } else { $jarMatch.Groups['plain'].Value }
  if (-not [System.IO.Path]::IsPathRooted($jarArgument)) {
    throw "The running backend jar path is not absolute; replacement is blocked."
  }
  $runningJarPath = [System.IO.Path]::GetFullPath($jarArgument)
  $runningJarName = [System.IO.Path]::GetFileName($runningJarPath)
  if ($runningJarName -notmatch '(?i)^kaipai-backend(?:-[a-z0-9._-]+)?\.jar$' -or -not (Test-Path -LiteralPath $runningJarPath -PathType Leaf)) {
    throw "The actual -jar argument is not an existing KaiPai backend jar."
  }

  return [pscustomobject]@{
    processId = $ProcessId
    startTimeUtcTicks = $process.StartTime.ToUniversalTime().Ticks
    jarPath = $runningJarPath
  }
}

function Stop-VerifiedBackendProcess {
  param(
    [Parameter(Mandatory = $true)]$Descriptor,
    [Parameter(Mandatory = $true)][int]$LocalPort
  )

  $owners = @(Get-PortListeners -LocalPort $LocalPort)
  if ($owners.Count -ne 1 -or $owners[0] -ne $Descriptor.processId) {
    throw "Port ownership changed after preflight; replacement is blocked."
  }
  $current = Get-KaipaiBackendProcessDescriptor -ProcessId $Descriptor.processId
  if ($current.startTimeUtcTicks -ne $Descriptor.startTimeUtcTicks -or $current.jarPath -ine $Descriptor.jarPath) {
    throw "Backend process identity changed after preflight; replacement is blocked."
  }

  Stop-Process -Id $Descriptor.processId -Force -ErrorAction Stop
  $deadline = (Get-Date).AddSeconds(15)
  while (Get-Process -Id $Descriptor.processId -ErrorAction SilentlyContinue) {
    if ((Get-Date) -ge $deadline) {
      throw "The existing backend did not stop within the timeout."
    }
    Start-Sleep -Milliseconds 200
  }
}

function Set-TemporaryProcessEnvironment {
  param(
    [Parameter(Mandatory = $true)][hashtable]$Values,
    [Parameter(Mandatory = $true)][hashtable]$OriginalValues
  )

  foreach ($key in $Values.Keys) {
    $OriginalValues[$key] = [pscustomobject]@{
      present = Test-Path -LiteralPath "Env:$key"
      value = [Environment]::GetEnvironmentVariable($key, [EnvironmentVariableTarget]::Process)
    }
    $temporaryValue = if ($null -eq $Values[$key]) { $null } else { [string]$Values[$key] }
    [Environment]::SetEnvironmentVariable($key, $temporaryValue, [EnvironmentVariableTarget]::Process)
  }
}

function Assert-RuntimeDirectoryWritable {
  param([Parameter(Mandatory = $true)][string]$Path)

  New-Item -ItemType Directory -Path $Path -Force | Out-Null
  $probePath = Join-Path $Path (".write-probe-{0}-{1}.tmp" -f $PID, [guid]::NewGuid().ToString('N'))
  try {
    [System.IO.File]::WriteAllText($probePath, "ready`r`n", [System.Text.Encoding]::ASCII)
  }
  finally {
    Remove-Item -LiteralPath $probePath -Force -ErrorAction SilentlyContinue
  }
}

function Stop-StartedProcessAfterFailure {
  param([System.Diagnostics.Process]$Process)

  if (-not $Process) {
    return
  }
  $running = Get-Process -Id $Process.Id -ErrorAction SilentlyContinue
  if (-not $running) {
    return
  }

  Stop-Process -Id $Process.Id -Force -ErrorAction Stop
  $deadline = (Get-Date).AddSeconds(15)
  while (Get-Process -Id $Process.Id -ErrorAction SilentlyContinue) {
    if ((Get-Date) -ge $deadline) {
      throw "The failed replacement process could not be stopped."
    }
    Start-Sleep -Milliseconds 200
  }
}

function Restore-ProcessEnvironment {
  param([Parameter(Mandatory = $true)][hashtable]$OriginalValues)

  foreach ($key in $OriginalValues.Keys) {
    $original = $OriginalValues[$key]
    $value = if ($original.present) { [string]$original.value } else { $null }
    [Environment]::SetEnvironmentVariable($key, $value, [EnvironmentVariableTarget]::Process)
  }
}

$repoRoot = (Resolve-Path -LiteralPath "$PSScriptRoot\..\..").Path
$projectConfigPath = Join-Path $repoRoot "kaipai-frontend\project.config.json"
$migrationDirectory = Join-Path $repoRoot "kaipaile-server\src\main\resources\db\migration"
$resolvedRuntimeDir = [System.IO.Path]::GetFullPath($RuntimeDir)
$resolvedSecretFile = (Resolve-Path -LiteralPath $SecretFile).Path

if ([string]::IsNullOrWhiteSpace($JarPath)) {
  $jarCandidates = @()
  $repositoryJarPath = Join-Path $repoRoot "kaipaile-server\target\kaipai-backend-1.0.0-SNAPSHOT.jar"
  if (Test-Path -LiteralPath $repositoryJarPath -PathType Leaf) {
    $jarCandidates += Get-Item -LiteralPath $repositoryJarPath
  }
  if (Test-Path -LiteralPath $resolvedRuntimeDir -PathType Container) {
    $jarCandidates += Get-ChildItem -LiteralPath $resolvedRuntimeDir -Filter 'kaipai-backend-*.jar' -File
  }
  $selectedJar = $jarCandidates | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
  if (-not $selectedJar) {
    throw "No local KaiPai backend jar is available. Build one or pass -JarPath."
  }
  $resolvedJarPath = $selectedJar.FullName
}
else {
  $resolvedJarPath = (Resolve-Path -LiteralPath $JarPath).Path
}

if ($Port -ne 8010) {
  throw "This local backend entry is pinned to port 8010."
}
if ($MySqlContainer -cne 'kaipai-mysql-local' -or $RedisContainer -cne 'kaipai-local-redis') {
  throw "This local backend entry is pinned to kaipai-mysql-local and kaipai-local-redis."
}
if ($StartupTimeoutSeconds -lt 10) {
  throw "Startup timeout must be at least 10 seconds."
}
if ($ReplacePid -lt 0 -or ($ReplacePid -gt 0 -and -not $Restart)) {
  throw "-ReplacePid requires -Restart and a positive process id."
}

$secretValues = Get-DotEnvValues -Path $resolvedSecretFile
Assert-WeChatConfig -Values $secretValues -ProjectConfigPath $projectConfigPath

Assert-LocalDockerContext
$mysqlInspect = Get-ContainerInspect -Name $MySqlContainer
$redisInspect = Get-ContainerInspect -Name $RedisContainer
Assert-LocalContainerPort -Inspect $mysqlInspect -ContainerPort '3306/tcp' -HostPort '3309'
Assert-LocalContainerPort -Inspect $redisInspect -ContainerPort '6379/tcp' -HostPort '6379'
$mysqlPassword = Get-MySqlRootPassword -Inspect $mysqlInspect
Assert-LocalServicesReady -MySqlName $MySqlContainer -RedisName $RedisContainer
Assert-LocalSchemaCompatible -MySqlName $MySqlContainer -DatabaseName 'kaipai_dev' -MigrationDirectory $migrationDirectory

$java = (Get-Command java -ErrorAction Stop).Source
$jarHash = (Get-FileHash -LiteralPath $resolvedJarPath -Algorithm SHA256).Hash
$pidPath = Join-Path $resolvedRuntimeDir "backend.pid"
Assert-RuntimeDirectoryWritable -Path $resolvedRuntimeDir

if ($ValidateOnly) {
  [pscustomobject]@{
    pid = $null
    port = $Port
    logPath = $resolvedRuntimeDir
    jarSha256 = $jarHash
    configReady = $true
  } | ConvertTo-Json -Compress | Write-Output
  exit 0
}

$listeners = @(Get-PortListeners -LocalPort $Port)
if ($listeners.Count -gt 1) {
  throw "Port $Port has multiple listener owners; replacement is blocked."
}
if ($listeners.Count -gt 0 -and -not $Restart) {
  throw "Port $Port is already in use. Pass -Restart after confirming the current local backend should be replaced."
}
$processDescriptors = @()
foreach ($listenerPid in $listeners) {
  $processDescriptors += Get-KaipaiBackendProcessDescriptor -ProcessId ([int]$listenerPid)
}

if ($listeners.Count -eq 1) {
  if (Test-Path -LiteralPath $pidPath -PathType Leaf) {
    $managedPidText = ([string](Get-Content -LiteralPath $pidPath -ErrorAction Stop | Select-Object -First 1)).Trim()
    if ($managedPidText -notmatch '^\d+$' -or [int]$managedPidText -ne [int]$listeners[0]) {
      throw "The managed PID file does not match the port owner; replacement is blocked."
    }
    $managedJar = $processDescriptors[0].jarPath
    $managedJarDirectory = [System.IO.Path]::GetDirectoryName($managedJar)
    if ($managedJarDirectory -ine $resolvedRuntimeDir -or [System.IO.Path]::GetFileName($managedJar) -notmatch '(?i)^kaipai-backend-[a-f0-9]{64}\.jar$') {
      throw "The managed backend is not running the checksum-addressed runtime jar."
    }
    if ($ReplacePid -gt 0) {
      throw "-ReplacePid is only valid for the one-time adoption of an unmanaged backend."
    }
  }
  elseif ($ReplacePid -ne [int]$listeners[0]) {
    throw "The current backend is unmanaged. Rerun with -Restart -ReplacePid $($listeners[0]) after reviewing its actual -jar path."
  }
}
elseif ($ReplacePid -gt 0) {
  throw "-ReplacePid was provided, but port $Port has no listener."
}

$runtimeJarPath = Join-Path $resolvedRuntimeDir "kaipai-backend-$jarHash.jar"
if (-not (Test-Path -LiteralPath $runtimeJarPath -PathType Leaf)) {
  Copy-Item -LiteralPath $resolvedJarPath -Destination $runtimeJarPath
}
if ((Get-FileHash -LiteralPath $runtimeJarPath -Algorithm SHA256).Hash -cne $jarHash) {
  throw "Runtime jar checksum verification failed."
}

foreach ($descriptor in $processDescriptors) {
  Stop-VerifiedBackendProcess -Descriptor $descriptor -LocalPort $Port
}
Remove-Item -LiteralPath $pidPath -Force -ErrorAction SilentlyContinue
$portReleaseDeadline = (Get-Date).AddSeconds(15)
while (@(Get-PortListeners -LocalPort $Port).Count -gt 0) {
  if ((Get-Date) -ge $portReleaseDeadline) {
    throw "Timed out waiting for port $Port to be released."
  }
  Start-Sleep -Milliseconds 250
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$stdoutPath = Join-Path $resolvedRuntimeDir "$timestamp-backend.log"
$stderrPath = Join-Path $resolvedRuntimeDir "$timestamp-backend-error.log"
$pidTempPath = Join-Path $resolvedRuntimeDir ("backend.pid.tmp-{0}-{1}" -f $PID, [guid]::NewGuid().ToString('N'))
$wechatEnvVersion = if ([string]::IsNullOrWhiteSpace([string]$secretValues['WECHAT_MINIAPP_ENV_VERSION'])) { $null } else { [string]$secretValues['WECHAT_MINIAPP_ENV_VERSION'] }
$environmentValues = @{
  SPRING_APPLICATION_JSON = $null
  SPRING_CONFIG_LOCATION = $null
  SPRING_CONFIG_ADDITIONAL_LOCATION = $null
  SPRING_CONFIG_IMPORT = $null
  SPRING_CONFIG_NAME = $null
  JAVA_TOOL_OPTIONS = $null
  JDK_JAVA_OPTIONS = $null
  _JAVA_OPTIONS = $null
  SPRING_PROFILES_ACTIVE = 'dev'
  SPRING_PROFILES_INCLUDE = $null
  SPRING_APPLICATION_NAME = 'kaipai-backend'
  NACOS_ENABLED = 'false'
  SPRING_CLOUD_BOOTSTRAP_ENABLED = 'false'
  SPRING_CLOUD_NACOS_CONFIG_ENABLED = 'false'
  SPRING_CLOUD_NACOS_DISCOVERY_ENABLED = 'false'
  SERVER_PORT = [string]$Port
  SERVER_SERVLET_CONTEXT_PATH = '/api'
  SPRING_DATASOURCE_URL = 'jdbc:mysql://127.0.0.1:3309/kaipai_dev?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true&useSSL=false&connectTimeout=3000&socketTimeout=3000'
  SPRING_DATASOURCE_USERNAME = 'root'
  SPRING_DATASOURCE_PASSWORD = $mysqlPassword
  SPRING_DATA_REDIS_HOST = '127.0.0.1'
  SPRING_DATA_REDIS_PORT = '6379'
  SPRING_DATA_REDIS_PASSWORD = ''
  SPRING_DATA_REDIS_DATABASE = '0'
  SPRING_FLYWAY_ENABLED = 'false'
  SPRING_LIQUIBASE_ENABLED = 'false'
  SPRING_SQL_INIT_MODE = 'never'
  WECHAT_MINIAPP_APP_ID = [string]$secretValues['WECHAT_MINIAPP_APP_ID']
  WECHAT_MINIAPP_APP_SECRET = [string]$secretValues['WECHAT_MINIAPP_APP_SECRET']
  WECHAT_MINIAPP_ENV_VERSION = $wechatEnvVersion
}

$backendProcess = $null
try {
  $originalEnvironment = @{}
  try {
    Set-TemporaryProcessEnvironment -Values $environmentValues -OriginalValues $originalEnvironment
    $backendProcess = Start-Process `
      -FilePath $java `
      -ArgumentList @('-jar', ('"{0}"' -f $runtimeJarPath)) `
      -WindowStyle Hidden `
      -PassThru `
      -RedirectStandardOutput $stdoutPath `
      -RedirectStandardError $stderrPath
  }
  finally {
    Restore-ProcessEnvironment -OriginalValues $originalEnvironment
  }

  $ready = $false
  $startupDeadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)
  while ((Get-Date) -lt $startupDeadline) {
    if ($backendProcess.HasExited) {
      break
    }
    try {
      $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/api/doc.html" -UseBasicParsing -TimeoutSec 2
      $owners = @(Get-PortListeners -LocalPort $Port)
      if ($response.StatusCode -eq 200 -and $owners.Count -eq 1 -and $owners[0] -eq $backendProcess.Id) {
        $ready = $true
        break
      }
    }
    catch {
      # The endpoint is expected to fail until Spring has finished starting.
    }
    Start-Sleep -Milliseconds 300
  }

  if (-not $ready) {
    throw "Local backend failed to become ready. Review the runtime log directory."
  }

  [System.IO.File]::WriteAllText($pidTempPath, "$($backendProcess.Id)`r`n", [System.Text.Encoding]::ASCII)
  Move-Item -LiteralPath $pidTempPath -Destination $pidPath -Force
}
catch {
  $startupError = $_
  $cleanupError = $null
  try {
    Stop-StartedProcessAfterFailure -Process $backendProcess
  }
  catch {
    $cleanupError = $_
  }
  Remove-Item -LiteralPath $pidTempPath -Force -ErrorAction SilentlyContinue
  if ($backendProcess -and (Test-Path -LiteralPath $pidPath -PathType Leaf)) {
    $currentPidText = ([string](Get-Content -LiteralPath $pidPath -ErrorAction SilentlyContinue | Select-Object -First 1)).Trim()
    if ($currentPidText -eq [string]$backendProcess.Id -and -not (Get-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue)) {
      Remove-Item -LiteralPath $pidPath -Force -ErrorAction SilentlyContinue
    }
  }
  if ($cleanupError) {
    throw "Local backend replacement failed, and the replacement process could not be cleaned up. Review the runtime logs and port 8010."
  }
  throw $startupError
}

[pscustomobject]@{
  pid = $backendProcess.Id
  port = $Port
  logPath = $resolvedRuntimeDir
  jarSha256 = $jarHash
  configReady = $true
} | ConvertTo-Json -Compress | Write-Output
