param(
  [Parameter(Mandatory = $true)]
  [string]$SampleName,

  [Parameter(Mandatory = $true)]
  [string]$ApiBaseUrl,

  [string]$EnvironmentName,
  [string]$ActorToken,
  [string]$AdminToken,
  [string]$InviteCode,
  [string]$InviterUserId,
  [string]$InviteeUserId,
  [string]$ReferralId,
  [string]$GrantId,
  [string]$PolicyId,
  [string]$OutputDir
)

$ErrorActionPreference = 'Stop'

function Ensure-Directory {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path | Out-Null
  }
}

function Normalize-BaseUrl {
  param([string]$BaseUrl)
  if (-not $BaseUrl) {
    return ''
  }
  $normalized = $BaseUrl.Trim().TrimEnd('/')
  if ($normalized.EndsWith('/api')) {
    return $normalized.Substring(0, $normalized.Length - 4)
  }
  return $normalized
}

function Write-FileText {
  param(
    [string]$Path,
    [string]$Content
  )
  Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function Resolve-ReportValue {
  param(
    [object]$Value,
    [string]$Fallback = '--'
  )
  if ($null -eq $Value) {
    return $Fallback
  }
  if ($Value -is [DateTime]) {
    return $Value.ToString('yyyy-MM-dd HH:mm:ss')
  }
  if ($Value -is [bool]) {
    return $(if ($Value) { 'true' } else { 'false' })
  }
  if ($Value -is [System.Collections.IEnumerable] -and -not ($Value -is [string])) {
    $parts = New-Object 'System.Collections.Generic.List[string]'
    foreach ($item in $Value) {
      $resolvedItem = Resolve-ReportValue -Value $item -Fallback ''
      if (-not [string]::IsNullOrWhiteSpace($resolvedItem)) {
        $parts.Add($resolvedItem)
      }
    }
    if ($parts.Count -gt 0) {
      return ($parts -join ', ')
    }
    return $Fallback
  }
  $text = [string]$Value
  if ([string]::IsNullOrWhiteSpace($text)) {
    return $Fallback
  }
  if ($text -match '^\d{4}-\d{2}-\d{2}T') {
    try {
      return ([DateTime]$text).ToString('yyyy-MM-dd HH:mm:ss')
    } catch {
      return $text
    }
  }
  return $text
}

function Test-ObjectProperty {
  param(
    [object]$Object,
    [string]$Name
  )
  if ($null -eq $Object) {
    return $false
  }
  if ($Object -is [System.Collections.IDictionary]) {
    return $Object.Contains($Name)
  }
  return $null -ne $Object.PSObject.Properties[$Name]
}

function Get-ObjectProperty {
  param(
    [object]$Object,
    [string]$Name
  )
  if (-not (Test-ObjectProperty -Object $Object -Name $Name)) {
    return $null
  }
  if ($Object -is [System.Collections.IDictionary]) {
    return $Object[$Name]
  }
  return $Object.$Name
}

function Get-JsonFile {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    return $null
  }
  $raw = Get-Content -LiteralPath $Path -Raw
  if ([string]::IsNullOrWhiteSpace($raw)) {
    return $null
  }
  return $raw | ConvertFrom-Json
}

function New-ResultIndex {
  param([System.Collections.IEnumerable]$Results)
  $index = @{}
  foreach ($result in @($Results)) {
    if ($null -ne $result -and -not [string]::IsNullOrWhiteSpace([string]$result.name)) {
      $index[[string]$result.name] = $result
    }
  }
  return $index
}

function Test-AnyResultAttempted {
  param(
    [hashtable]$ResultIndex,
    [string[]]$Names
  )
  foreach ($name in $Names) {
    if ($ResultIndex.ContainsKey($name)) {
      return $true
    }
  }
  return $false
}

function Get-CapturedData {
  param(
    [string]$CaptureDir,
    [hashtable]$ResultIndex,
    [string]$Name
  )

  if (-not $ResultIndex.ContainsKey($Name)) {
    return $null
  }

  $result = $ResultIndex[$Name]
  if ($null -eq $result -or $result.status -ne 'ok') {
    return $null
  }

  $path = Join-Path $CaptureDir "$Name.json"
  $payload = Get-JsonFile -Path $path
  if ($null -eq $payload) {
    return $null
  }

  if (Test-ObjectProperty -Object $payload -Name 'code') {
    $code = Get-ObjectProperty -Object $payload -Name 'code'
    if ($null -ne $code -and [string]$code -ne '200') {
      return $null
    }
  }

  if (Test-ObjectProperty -Object $payload -Name 'data') {
    return Get-ObjectProperty -Object $payload -Name 'data'
  }

  return $payload
}

function Get-PagedItems {
  param([object]$Payload)
  if ($null -eq $Payload) {
    return @()
  }
  if ($Payload -is [System.Array]) {
    return @($Payload)
  }
  if ($Payload -is [System.Collections.IEnumerable] -and -not ($Payload -is [string]) -and -not (Test-ObjectProperty -Object $Payload -Name 'list') -and -not (Test-ObjectProperty -Object $Payload -Name 'records')) {
    return @($Payload)
  }
  if (Test-ObjectProperty -Object $Payload -Name 'list') {
    return @((Get-ObjectProperty -Object $Payload -Name 'list'))
  }
  if (Test-ObjectProperty -Object $Payload -Name 'records') {
    return @((Get-ObjectProperty -Object $Payload -Name 'records'))
  }
  return @()
}

function Get-FirstPresentValue {
  param([object[]]$Values)
  foreach ($value in $Values) {
    if ($null -eq $value) {
      continue
    }
    if ($value -is [string] -and [string]::IsNullOrWhiteSpace($value)) {
      continue
    }
    return $value
  }
  return $null
}

function Get-CollectionCount {
  param([object]$Value)
  if ($null -eq $Value) {
    return $null
  }
  if ($Value -is [string]) {
    return 1
  }
  return @($Value).Count
}

function Find-FirstMatchingItem {
  param(
    [object[]]$Items,
    [hashtable]$Criteria
  )

  $filteredItems = @($Items | Where-Object { $null -ne $_ })
  foreach ($item in $filteredItems) {
    $isMatch = $true
    foreach ($key in $Criteria.Keys) {
      $expected = $Criteria[$key]
      if ($null -eq $expected) {
        continue
      }
      if ($expected -is [string] -and [string]::IsNullOrWhiteSpace($expected)) {
        continue
      }

      $actual = Get-ObjectProperty -Object $item -Name $key
      $expectedText = Resolve-ReportValue -Value $expected -Fallback ''
      $actualText = Resolve-ReportValue -Value $actual -Fallback ''
      if ($expected -is [string] -and $actual -is [string]) {
        $expectedText = $expectedText.ToUpperInvariant()
        $actualText = $actualText.ToUpperInvariant()
      }
      if ($expectedText -ne $actualText) {
        $isMatch = $false
        break
      }
    }

    if ($isMatch) {
      return $item
    }
  }

  if ($filteredItems.Count -eq 1) {
    return $filteredItems[0]
  }

  return $null
}

function Normalize-HeadingTitle {
  param([string]$Title)
  if ([string]::IsNullOrWhiteSpace($Title)) {
    return ''
  }
  return ($Title.Trim() -replace '^\d+\.\s*', '')
}

function Set-LedgerFieldInSection {
  param(
    [string[]]$Lines,
    [string[]]$SectionPath,
    [string]$Label,
    [object]$Value
  )

  $resolvedValue = Resolve-ReportValue -Value $Value -Fallback ''
  if ([string]::IsNullOrWhiteSpace($resolvedValue)) {
    return $Lines
  }

  $expectedPath = @($SectionPath | ForEach-Object { Normalize-HeadingTitle -Title $_ }) -join '|'
  $currentPath = @()
  $safeLabel = [regex]::Escape($Label)

  for ($i = 0; $i -lt $Lines.Length; $i++) {
    $line = $Lines[$i]
    if ($line -match '^(#{2,4})\s+(.+)$') {
      $level = $matches[1].Length
      $title = Normalize-HeadingTitle -Title $matches[2]
      $depth = $level - 2
      if ($depth -lt 0) {
        continue
      }

      $updatedPath = @()
      if ($depth -gt 0 -and $currentPath.Count -ge $depth) {
        $updatedPath += $currentPath[0..($depth - 1)]
      }
      $updatedPath += $title
      $currentPath = $updatedPath
      continue
    }

    if (($currentPath -join '|') -eq $expectedPath -and $line -match ("^- $safeLabel：.*$")) {
      $Lines[$i] = "- $Label：$resolvedValue"
      break
    }
  }

  return $Lines
}

function Resolve-CheckValue {
  param([object]$Value)
  if ($null -eq $Value) {
    return $null
  }
  return $(if ([bool]$Value) { '是' } else { '否' })
}

function Compare-Values {
  param(
    [object]$Left,
    [object]$Right
  )
  $leftText = Resolve-ReportValue -Value $Left -Fallback ''
  $rightText = Resolve-ReportValue -Value $Right -Fallback ''
  if ([string]::IsNullOrWhiteSpace($leftText) -or [string]::IsNullOrWhiteSpace($rightText)) {
    return $null
  }
  if ($Left -is [string] -and $Right -is [string]) {
    $leftText = $leftText.ToUpperInvariant()
    $rightText = $rightText.ToUpperInvariant()
  }
  return $(if ($leftText -eq $rightText) { '是' } else { '否' })
}

function Add-ReportSection {
  param(
    [System.Collections.Generic.List[string]]$Lines,
    [string]$Title,
    [hashtable]$Items
  )

  $Lines.Add("### $Title")
  $Lines.Add('')

  $count = 0
  foreach ($key in $Items.Keys) {
    $value = Resolve-ReportValue -Value $Items[$key] -Fallback ''
    if ([string]::IsNullOrWhiteSpace($value)) {
      continue
    }
    $Lines.Add(("{0}: {1}" -f "- $key", $value))
    $count++
  }

  if ($count -eq 0) {
    $Lines.Add('- None')
  }

  $Lines.Add('')
}

function New-InviteValidationFacts {
  param(
    [hashtable]$Context,
    [System.Collections.IEnumerable]$Results,
    [string]$CaptureDir
  )

  $resultIndex = New-ResultIndex -Results $Results
  $contextInviteCode = if ($Context['inviteCode']) { [string]$Context['inviteCode'] } else { $null }

  $actorInviteInfo = Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'actor_invite_code'
  $actorInviteStats = Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'actor_invite_stats'
  $actorInviteRecords = Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'actor_invite_records'
  $actorInviteQrCode = Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'actor_invite_qrcode'
  $actorLevelInfo = Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'actor_level_info'

  $recordItems = @()
  $recordItems += Get-PagedItems -Payload (Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'admin_referral_records_by_invite_code')
  $recordItems += Get-PagedItems -Payload (Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'admin_referral_records_by_inviter')
  $recordItems += Get-PagedItems -Payload (Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'admin_referral_records_by_invitee')
  $recordCriteria = [ordered]@{
    referralId = $Context['referralId']
    inviteCode = $contextInviteCode
    inviteeUserId = $Context['inviteeUserId']
    inviterUserId = $Context['inviterUserId']
  }
  $recordListItem = Find-FirstMatchingItem -Items $recordItems -Criteria $recordCriteria
  $recordDetail = Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'admin_referral_record_detail'

  $riskItems = Get-PagedItems -Payload (Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'admin_referral_risk_by_invite_code')
  $riskCriteria = [ordered]@{
    referralId = $Context['referralId']
    inviteCode = $contextInviteCode
  }
  $riskListItem = Find-FirstMatchingItem -Items $riskItems -Criteria $riskCriteria
  $riskDetail = Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'admin_referral_risk_detail'

  $grantItems = Get-PagedItems -Payload (Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'admin_referral_eligibility_by_user')
  $grantCriteria = [ordered]@{
    grantId = $Context['grantId']
    userId = $Context['inviteeUserId']
    sourceRefId = $Context['referralId']
  }
  $grantListItem = Find-FirstMatchingItem -Items $grantItems -Criteria $grantCriteria
  $grantDetail = Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'admin_referral_eligibility_detail'

  $policyItems = Get-PagedItems -Payload (Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'admin_referral_policies')
  $policyCriteria = [ordered]@{
    policyId = $Context['policyId']
  }
  $policyListItem = Find-FirstMatchingItem -Items $policyItems -Criteria $policyCriteria
  if ($null -eq $policyListItem) {
    $policyListItem = Find-FirstMatchingItem -Items $policyItems -Criteria ([ordered]@{ enabled = 1 })
  }
  $policyDetail = Get-CapturedData -CaptureDir $CaptureDir -ResultIndex $resultIndex -Name 'admin_referral_policy_detail'

  $recordData = Get-FirstPresentValue @($recordDetail.recordInfo, $recordListItem)
  $riskData = Get-FirstPresentValue @($riskDetail.recordInfo, $riskListItem)
  $grantData = Get-FirstPresentValue @($grantDetail.grantInfo, $grantListItem)
  $policyData = Get-FirstPresentValue @($policyDetail, $policyListItem, $grantDetail.relatedPolicy)

  $riskLatestLog = $null
  if ($riskDetail -and $riskDetail.historyLogs) {
    $sortedRiskLogs = @($riskDetail.historyLogs | Sort-Object -Property createTime -Descending)
    if ($sortedRiskLogs.Count -gt 0) {
      $riskLatestLog = $sortedRiskLogs[0]
    }
  }

  $recordAttempted = Test-AnyResultAttempted -ResultIndex $resultIndex -Names @(
    'admin_referral_record_detail',
    'admin_referral_records_by_invite_code',
    'admin_referral_records_by_inviter',
    'admin_referral_records_by_invitee'
  )
  $riskAttempted = Test-AnyResultAttempted -ResultIndex $resultIndex -Names @(
    'admin_referral_risk_detail',
    'admin_referral_risk_by_invite_code'
  )
  $grantAttempted = Test-AnyResultAttempted -ResultIndex $resultIndex -Names @(
    'admin_referral_eligibility_detail',
    'admin_referral_eligibility_by_user'
  )
  $policyAttempted = Test-AnyResultAttempted -ResultIndex $resultIndex -Names @(
    'admin_referral_policy_detail',
    'admin_referral_policies'
  )

  $actorInviteCode = Get-FirstPresentValue @($actorInviteInfo.inviteCode, $contextInviteCode)
  $actorValidInviteCount = Get-FirstPresentValue @($actorInviteInfo.validInviteCount, $actorInviteStats.validInviteCount)
  $actorTotalInviteCount = Get-FirstPresentValue @($actorInviteInfo.totalInviteCount, $actorInviteStats.totalInviteCount)
  $actorPendingInviteCount = Get-FirstPresentValue @($actorInviteInfo.pendingInviteCount, $actorInviteStats.pendingInviteCount)
  $actorFlaggedInviteCount = Get-FirstPresentValue @($actorInviteInfo.flaggedInviteCount, $actorInviteStats.flaggedInviteCount)
  $actorQrCodeValue = Get-FirstPresentValue @($actorInviteQrCode, $actorInviteInfo.qrCodeUrl)

  $facts = [ordered]@{
    actor = [ordered]@{
      inviteCode = $actorInviteCode
      validInviteCount = $actorValidInviteCount
      totalInviteCount = $actorTotalInviteCount
      pendingInviteCount = $actorPendingInviteCount
      flaggedInviteCount = $actorFlaggedInviteCount
      inviteRecordCount = Get-CollectionCount -Value $actorInviteRecords
      qrCode = $actorQrCodeValue
    }
    level = [ordered]@{
      inviteCount = if ($actorLevelInfo) { $actorLevelInfo.inviteCount } else { $null }
      level = if ($actorLevelInfo) { $actorLevelInfo.level } else { $null }
      profileCompletion = if ($actorLevelInfo) { $actorLevelInfo.profileCompletion } else { $null }
      membershipTier = if ($actorLevelInfo) { $actorLevelInfo.membershipTier } else { $null }
      isCertified = if ($actorLevelInfo) { $actorLevelInfo.isCertified } else { $null }
      nextLevelRequirement = if ($actorLevelInfo) { $actorLevelInfo.nextLevelRequirement } else { $null }
    }
    adminRecord = [ordered]@{
      found = if ($null -ne $recordData) { $true } elseif ($recordAttempted) { $false } else { $null }
      referralId = if ($recordData) { $recordData.referralId } else { $Context['referralId'] }
      inviteCode = if ($recordData) { $recordData.inviteCode } else { $actorInviteCode }
      inviteCodeId = if ($recordData) { $recordData.inviteCodeId } else { $null }
      status = if ($recordData) { $recordData.status } else { $null }
      riskFlag = Get-FirstPresentValue @(
        $(if ($recordData) { $recordData.riskFlag } else { $null }),
        $(if ($riskData) { $riskData.riskFlag } else { $null })
      )
      riskReason = Get-FirstPresentValue @(
        $(if ($recordData) { $recordData.riskReason } else { $null }),
        $(if ($riskDetail) { $riskDetail.riskInfo.riskReason } else { $null }),
        $(if ($riskListItem) { $riskListItem.riskReason } else { $null })
      )
      registerDeviceFingerprint = Get-FirstPresentValue @(
        $(if ($recordData) { $recordData.registerDeviceFingerprint } else { $null }),
        $(if ($riskDetail) { $riskDetail.recordInfo.registerDeviceFingerprint } else { $null }),
        $(if ($riskDetail) { $riskDetail.deviceHitSummary.deviceFingerprint } else { $null })
      )
      registeredAt = if ($recordData) { $recordData.registeredAt } else { $null }
      validatedAt = if ($recordData) { $recordData.validatedAt } else { $null }
    }
    adminRisk = [ordered]@{
      found = if ($null -ne $riskData -or $null -ne $riskDetail) { $true } elseif ($riskAttempted) { $false } else { $null }
      riskReason = Get-FirstPresentValue @(
        $(if ($riskDetail) { $riskDetail.riskInfo.riskReason } else { $null }),
        $(if ($riskData) { $riskData.riskReason } else { $null })
      )
      action = if ($riskLatestLog) { $riskLatestLog.operationCode } else { $null }
      actionStatus = Get-FirstPresentValue @(
        $(if ($riskDetail) { $riskDetail.riskInfo.currentStatus } else { $null }),
        $(if ($riskData) { $riskData.status } else { $null })
      )
      sameDeviceHitCount = if ($riskDetail) { $riskDetail.deviceHitSummary.hitCount } else { $null }
      deviceFingerprint = if ($riskDetail) { $riskDetail.deviceHitSummary.deviceFingerprint } else { $null }
    }
    adminPolicy = [ordered]@{
      found = if ($null -ne $policyData) { $true } elseif ($policyAttempted) { $false } else { $null }
      policyId = Get-FirstPresentValue @(
        $(if ($policyData) { $policyData.policyId } else { $null }),
        $Context['policyId']
      )
      policyName = if ($policyData) { $policyData.policyName } else { $null }
      enabled = if ($policyData) { $policyData.enabled } else { $null }
      requireRealAuth = if ($policyData) { $policyData.requireRealAuth } else { $null }
      requireProfileCompletion = if ($policyData) { $policyData.requireProfileCompletion } else { $null }
      profileCompletionThreshold = if ($policyData) { $policyData.profileCompletionThreshold } else { $null }
      sameDeviceLimit = if ($policyData) { $policyData.sameDeviceLimit } else { $null }
      hourlyInviteLimit = if ($policyData) { $policyData.hourlyInviteLimit } else { $null }
      autoGrantEnabled = if ($policyData) { $policyData.autoGrantEnabled } else { $null }
    }
    adminGrant = [ordered]@{
      found = if ($null -ne $grantData -or $null -ne $grantDetail) { $true } elseif ($grantAttempted) { $false } else { $null }
      grantId = Get-FirstPresentValue @(
        $(if ($grantData) { $grantData.grantId } else { $null }),
        $Context['grantId']
      )
      status = if ($grantData) { $grantData.status } else { $null }
      sourceType = if ($grantData) { $grantData.sourceType } else { $null }
      sourceRefId = if ($grantData) { $grantData.sourceRefId } else { $null }
      effectiveTime = if ($grantData) { $grantData.effectiveTime } else { $null }
      expireTime = if ($grantData) { $grantData.expireTime } else { $null }
      grantCode = if ($grantData) { $grantData.grantCode } else { $null }
      relatedPolicyId = if ($grantDetail) { $grantDetail.relatedPolicy.policyId } else { $null }
      relatedPolicyName = if ($grantDetail) { $grantDetail.relatedPolicy.policyName } else { $null }
    }
  }

  $facts['crossChecks'] = [ordered]@{
    'Actor inviteCode = context inviteCode' = Compare-Values -Left $facts.actor.inviteCode -Right $Context['inviteCode']
    'Actor validInviteCount = level inviteCount' = Compare-Values -Left $facts.actor.validInviteCount -Right $facts.level.inviteCount
    'Admin referral inviteCode = actor inviteCode' = Compare-Values -Left $facts.adminRecord.inviteCode -Right $facts.actor.inviteCode
    'Grant sourceRefId = referralId' = Compare-Values -Left $facts.adminGrant.sourceRefId -Right $facts.adminRecord.referralId
    'Grant policyId = expected policyId' = Compare-Values -Left $facts.adminGrant.relatedPolicyId -Right $facts.adminPolicy.policyId
  }

  return $facts
}

function Update-SampleLedger {
  param(
    [string]$Path,
    [hashtable]$Context,
    [hashtable]$Facts
  )

  $lines = Get-Content -LiteralPath $Path

  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('样本信息', '基础信息') -Label '环境' -Value $Context['environmentName']
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('样本信息', '样本主键') -Label 'inviterUserId' -Value $Context['inviterUserId']
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('样本信息', '样本主键') -Label 'inviteCode' -Value $Facts.actor.inviteCode
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('样本信息', '样本主键') -Label 'inviteCodeId' -Value $Facts.adminRecord.inviteCodeId
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('样本信息', '样本主键') -Label 'inviteeUserId' -Value $Context['inviteeUserId']
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('样本信息', '样本主键') -Label 'referralId' -Value $Facts.adminRecord.referralId
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('样本信息', '样本主键') -Label 'grantId' -Value $Facts.adminGrant.grantId
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('样本信息', '样本主键') -Label 'policyId' -Value $Facts.adminPolicy.policyId

  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('小程序证据', 'invite 页') -Label '`inviteCode`' -Value $Facts.actor.inviteCode
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('小程序证据', 'invite 页') -Label '`validInviteCount`' -Value $Facts.actor.validInviteCount
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('小程序证据', 'invite 页') -Label '`totalInviteCount`' -Value $Facts.actor.totalInviteCount
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('小程序证据', 'invite 页') -Label '`pendingInviteCount`' -Value $Facts.actor.pendingInviteCount
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('小程序证据', 'invite 页') -Label '`flaggedInviteCount`' -Value $Facts.actor.flaggedInviteCount
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('小程序证据', 'invite 页') -Label '邀请记录数量' -Value $Facts.actor.inviteRecordCount
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('小程序证据', 'invite 页') -Label '二维码返回值' -Value $Facts.actor.qrCode

  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('小程序证据', 'level/info') -Label '`inviteCount`' -Value $Facts.level.inviteCount
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('小程序证据', 'level/info') -Label '`level`' -Value $Facts.level.level
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('小程序证据', 'level/info') -Label '`profileCompletion`' -Value $Facts.level.profileCompletion
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('小程序证据', 'level/info') -Label '`membershipTier`' -Value $Facts.level.membershipTier

  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请记录页') -Label '页面是否查到样本' -Value (Resolve-CheckValue -Value $Facts.adminRecord.found)
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请记录页') -Label '`referralId`' -Value $Facts.adminRecord.referralId
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请记录页') -Label '`inviteCode`' -Value $Facts.adminRecord.inviteCode
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请记录页') -Label '`status`' -Value $Facts.adminRecord.status
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请记录页') -Label '`riskFlag`' -Value $Facts.adminRecord.riskFlag
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请记录页') -Label '`registeredAt`' -Value $Facts.adminRecord.registeredAt
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请记录页') -Label '`validatedAt`' -Value $Facts.adminRecord.validatedAt

  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '异常邀请页') -Label '页面是否查到样本' -Value (Resolve-CheckValue -Value $Facts.adminRisk.found)
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '异常邀请页') -Label '`riskReason`' -Value $Facts.adminRisk.riskReason
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '异常邀请页') -Label '风控动作' -Value $Facts.adminRisk.action
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '异常邀请页') -Label '动作后状态' -Value $Facts.adminRisk.actionStatus

  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请规则页') -Label '当前生效 `policyId`' -Value $Facts.adminPolicy.policyId
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请规则页') -Label '`policyName`' -Value $Facts.adminPolicy.policyName
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请规则页') -Label '`enabled`' -Value $Facts.adminPolicy.enabled
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请规则页') -Label '`sameDeviceLimit`' -Value $Facts.adminPolicy.sameDeviceLimit
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请规则页') -Label '`hourlyInviteLimit`' -Value $Facts.adminPolicy.hourlyInviteLimit
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请规则页') -Label '`autoGrantEnabled`' -Value $Facts.adminPolicy.autoGrantEnabled

  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请资格页') -Label '页面是否查到样本' -Value (Resolve-CheckValue -Value $Facts.adminGrant.found)
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请资格页') -Label '`grantId`' -Value $Facts.adminGrant.grantId
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请资格页') -Label '`status`' -Value $Facts.adminGrant.status
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请资格页') -Label '`sourceType`' -Value $Facts.adminGrant.sourceType
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请资格页') -Label '`sourceRefId`' -Value $Facts.adminGrant.sourceRefId
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请资格页') -Label '`effectiveTime`' -Value $Facts.adminGrant.effectiveTime
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('后台证据', '邀请资格页') -Label '`expireTime`' -Value $Facts.adminGrant.expireTime

  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('一致性检查') -Label '小程序 `validInviteCount` = `/api/level/info inviteCount`' -Value $Facts.crossChecks['Actor validInviteCount = level inviteCount']
  $lines = Set-LedgerFieldInSection -Lines $lines -SectionPath @('一致性检查') -Label '`grant.source_ref_id` 是否指向当前样本链' -Value $Facts.crossChecks['Grant sourceRefId = referralId']

  Write-FileText -Path $Path -Content ($lines -join [Environment]::NewLine)
}

function Build-Report {
  param(
    [hashtable]$Context,
    [System.Collections.IEnumerable]$Results,
    [string]$CaptureDir,
    [hashtable]$Facts
  )

  $okResults = @($Results | Where-Object { $_.status -eq 'ok' })
  $errorResults = @($Results | Where-Object { $_.status -ne 'ok' })
  $lines = New-Object 'System.Collections.Generic.List[string]'

  $lines.Add('# Invite Validation Report')
  $lines.Add('')
  $lines.Add('## Sample')
  $lines.Add('')
  $lines.Add('- SampleName: ' + (Resolve-ReportValue $Context.sampleName))
  $lines.Add('- Environment: ' + (Resolve-ReportValue $Context.environmentName))
  $lines.Add('- CapturedAt: ' + (Resolve-ReportValue $Context.capturedAt))
  $lines.Add('- ApiBaseUrl: ' + (Resolve-ReportValue $Context.apiBaseUrl))
  $lines.Add('- InviteCode: ' + (Resolve-ReportValue $Context.inviteCode))
  $lines.Add('- InviterUserId: ' + (Resolve-ReportValue $Context.inviterUserId))
  $lines.Add('- InviteeUserId: ' + (Resolve-ReportValue $Context.inviteeUserId))
  $lines.Add('- ReferralId: ' + (Resolve-ReportValue $Context.referralId))
  $lines.Add('- GrantId: ' + (Resolve-ReportValue $Context.grantId))
  $lines.Add('- PolicyId: ' + (Resolve-ReportValue $Context.policyId))
  $lines.Add('')
  $lines.Add('## Extracted Facts')
  $lines.Add('')
  Add-ReportSection -Lines $lines -Title 'Actor Invite Snapshot' -Items $Facts.actor
  Add-ReportSection -Lines $lines -Title 'Level Snapshot' -Items $Facts.level
  Add-ReportSection -Lines $lines -Title 'Admin Referral Snapshot' -Items $Facts.adminRecord
  Add-ReportSection -Lines $lines -Title 'Admin Risk Snapshot' -Items $Facts.adminRisk
  Add-ReportSection -Lines $lines -Title 'Admin Policy Snapshot' -Items $Facts.adminPolicy
  Add-ReportSection -Lines $lines -Title 'Admin Grant Snapshot' -Items $Facts.adminGrant

  $lines.Add('## API Cross Checks')
  $lines.Add('')
  Add-ReportSection -Lines $lines -Title 'Cross Surface Consistency' -Items $Facts.crossChecks

  $lines.Add('## Capture Summary')
  $lines.Add('')
  $lines.Add('- OK endpoints: ' + $okResults.Count)
  $lines.Add('- Error endpoints: ' + $errorResults.Count)
  $lines.Add('- Capture directory: ' + $CaptureDir)
  $lines.Add('')

  $lines.Add('## OK Endpoints')
  $lines.Add('')
  if ($okResults.Count -eq 0) {
    $lines.Add('- None')
  } else {
    foreach ($result in $okResults) {
      $lines.Add('- ' + $result.name + ' -> ' + $result.output)
    }
  }
  $lines.Add('')

  $lines.Add('## Error Endpoints')
  $lines.Add('')
  if ($errorResults.Count -eq 0) {
    $lines.Add('- None')
  } else {
    foreach ($result in $errorResults) {
      $message = Resolve-ReportValue $result.message 'unknown error'
      $lines.Add('- ' + $result.name + ' -> ' + $message)
    }
  }
  $lines.Add('')

  $lines.Add('## DB Checklist')
  $lines.Add('')
  $lines.Add('- [ ] Execute validation.sql against the same environment')
  $lines.Add('- [ ] Save the result as validation-result.txt or screenshots')
  $lines.Add('- [ ] Fill sample-ledger.md with API and DB evidence')
  $lines.Add('- [ ] Backfill invite-status.md with the conclusion')
  $lines.Add('')

  $lines.Add('## Generated Files')
  $lines.Add('')
  $lines.Add('- sample-ledger.md')
  $lines.Add('- validation.sql')
  $lines.Add('- capture-summary.txt')
  $lines.Add('- capture-results.json')
  $lines.Add('- validation-report.md')

  return ($lines -join [Environment]::NewLine)
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$normalizedBaseUrl = Normalize-BaseUrl -BaseUrl $ApiBaseUrl
if (-not $normalizedBaseUrl) {
  throw 'ApiBaseUrl 不能为空。'
}

$safeSampleName = ($SampleName.Trim() -replace '[^a-zA-Z0-9._-]+', '-').Trim('-')
if (-not $safeSampleName) {
  throw 'SampleName 不能为空。'
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$sampleRoot = if ($OutputDir) {
  [System.IO.Path]::GetFullPath($OutputDir)
} else {
  [System.IO.Path]::GetFullPath((Join-Path $scriptDir ("captures\invite-{0}-{1}" -f $timestamp, $safeSampleName)))
}

Ensure-Directory -Path $sampleRoot

$newSampleScript = Join-Path $scriptDir 'new-invite-validation-sample.ps1'
$collectScript = Join-Path $scriptDir 'collect-invite-evidence.ps1'

& $newSampleScript `
  -SampleName $safeSampleName `
  -EnvironmentName $EnvironmentName `
  -ApiBaseUrl $normalizedBaseUrl `
  -InviteCode $InviteCode `
  -InviterUserId $InviterUserId `
  -InviteeUserId $InviteeUserId `
  -ReferralId $ReferralId `
  -GrantId $GrantId `
  -PolicyId $PolicyId `
  -OutputDir $sampleRoot

& $collectScript `
  -ApiBaseUrl $normalizedBaseUrl `
  -ActorToken $ActorToken `
  -AdminToken $AdminToken `
  -InviteCode $InviteCode `
  -InviterUserId $InviterUserId `
  -InviteeUserId $InviteeUserId `
  -ReferralId $ReferralId `
  -GrantId $GrantId `
  -PolicyId $PolicyId `
  -OutputDir $sampleRoot

$captureContextPath = Join-Path $sampleRoot 'capture-context.json'
$captureResultsPath = Join-Path $sampleRoot 'capture-results.json'
$reportPath = Join-Path $sampleRoot 'validation-report.md'

$contextObject = Get-Content -LiteralPath $captureContextPath -Raw | ConvertFrom-Json
$context = @{}
foreach ($property in $contextObject.PSObject.Properties) {
  $context[$property.Name] = $property.Value
}
$results = Get-Content -LiteralPath $captureResultsPath -Raw | ConvertFrom-Json
$context['sampleName'] = $safeSampleName
$context['environmentName'] = $EnvironmentName

$facts = New-InviteValidationFacts -Context $context -Results $results -CaptureDir $sampleRoot
Update-SampleLedger -Path (Join-Path $sampleRoot 'sample-ledger.md') -Context $context -Facts $facts

$reportContent = Build-Report -Context $context -Results $results -CaptureDir $sampleRoot -Facts $facts
Write-FileText -Path $reportPath -Content $reportContent

Write-Host "invite validation prepared: $sampleRoot" -ForegroundColor Green
