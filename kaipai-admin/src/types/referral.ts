import type { PageResult } from './common'

export interface ReferralRiskQuery {
  pageNo: number
  pageSize: number
  inviteCode?: string
  inviterUserId?: number
  inviteeUserId?: number
  riskReason?: string
  status?: number
  riskFlag?: number
  registeredAtFrom?: string
  registeredAtTo?: string
}

export interface ReferralRiskItem {
  referralId: number
  inviteCode?: string | null
  inviterUserId?: number | null
  inviterName?: string | null
  inviteeUserId?: number | null
  inviteeName?: string | null
  riskReason?: string | null
  status?: number | null
  riskFlag?: number | null
  registeredAt?: string | null
}

export interface ReferralRiskDecisionPayload {
  remark?: string
}

export interface ReferralRiskDetail {
  recordInfo?: {
    referralId?: number | null
    inviteCode?: string | null
    inviteCodeId?: number | null
    inviterUserId?: number | null
    inviteeUserId?: number | null
    status?: number | null
    riskFlag?: number | null
    riskReason?: string | null
    registerDeviceFingerprint?: string | null
    registeredAt?: string | null
    validatedAt?: string | null
  } | null
  inviterInfo?: ReferralRiskUserInfo | null
  inviteeInfo?: ReferralRiskUserInfo | null
  riskInfo?: {
    currentStatus?: number | null
    riskFlag?: number | null
    riskReason?: string | null
  } | null
  deviceHitSummary?: {
    deviceFingerprint?: string | null
    hitCount?: number | null
    relatedReferralIds?: number[] | null
  } | null
  sameHourHitSummary?: {
    inviteCode?: string | null
    hourStart?: string | null
    hourEnd?: string | null
    hitCount?: number | null
    relatedReferralIds?: number[] | null
  } | null
  historyLogs?: ReferralRiskHistoryLog[] | null
}

export interface ReferralRiskUserInfo {
  userId?: number | null
  userName?: string | null
  phone?: string | null
  nickname?: string | null
  realAuthStatus?: number | null
  validInviteCount?: number | null
}

export interface ReferralRiskHistoryLog {
  operationLogId?: number | null
  adminUserId?: number | null
  adminUserName?: string | null
  operationCode?: string | null
  operationResult?: number | null
  extraContextJson?: string | null
  createTime?: string | null
}

export type ReferralRiskPageResult = PageResult<ReferralRiskItem>
