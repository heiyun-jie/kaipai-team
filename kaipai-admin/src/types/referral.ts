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

export interface ReferralRecordQuery {
  pageNo: number
  pageSize: number
  inviteCode?: string
  inviterUserId?: number
  inviteeUserId?: number
  status?: number
  riskFlag?: number
  registeredAtFrom?: string
  registeredAtTo?: string
  validatedAtFrom?: string
  validatedAtTo?: string
}

export interface ReferralRecordItem {
  referralId: number
  inviterUserId?: number | null
  inviterName?: string | null
  inviteCode?: string | null
  inviteeUserId?: number | null
  inviteeName?: string | null
  status?: number | null
  riskFlag?: number | null
  registeredAt?: string | null
  validatedAt?: string | null
}

export interface ReferralRecordDetail {
  recordInfo?: {
    referralId?: number | null
    inviteCode?: string | null
    inviteCodeId?: number | null
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
    status?: number | null
    riskFlag?: number | null
    riskReason?: string | null
    registerDeviceFingerprint?: string | null
    sameDeviceHitCount?: number | null
    relatedGrantCodes?: string[] | null
  } | null
}

export type ReferralRecordPageResult = PageResult<ReferralRecordItem>

export interface ReferralEligibilityQuery {
  pageNo: number
  pageSize: number
  userId?: number
  phone?: string
  grantType?: string
  grantCode?: string
  status?: number
  sourceType?: string
  effectiveFrom?: string
  effectiveTo?: string
  expireFrom?: string
  expireTo?: string
}

export interface ReferralEligibilityItem {
  grantId: number
  userId?: number | null
  nickname?: string | null
  phone?: string | null
  grantType?: string | null
  grantCode?: string | null
  status?: number | null
  effectiveTime?: string | null
  expireTime?: string | null
  sourceType?: string | null
  sourceRefId?: number | null
  remark?: string | null
}

export interface ReferralEligibilityDetail {
  grantInfo?: {
    grantId?: number | null
    userId?: number | null
    userName?: string | null
    nickname?: string | null
    phone?: string | null
    userType?: number | null
    realAuthStatus?: number | null
    validInviteCount?: number | null
    grantType?: string | null
    grantCode?: string | null
    status?: number | null
    effectiveTime?: string | null
    expireTime?: string | null
    sourceType?: string | null
    sourceRefId?: number | null
    remark?: string | null
    createUserId?: number | null
    createUserName?: string | null
    createTime?: string | null
    updateUserId?: number | null
    updateUserName?: string | null
    lastUpdate?: string | null
  } | null
  sourceInfo?: {
    sourceType?: string | null
    sourceRefId?: number | null
    sourceTitle?: string | null
    sourceStatus?: string | null
    relatedBizType?: string | null
    relatedBizId?: number | null
  } | null
  relatedOrder?: {
    paymentOrderId?: number | null
    orderNo?: string | null
    bizType?: string | null
    bizRefId?: number | null
    amount?: number | null
    payStatus?: number | null
    payChannel?: string | null
    paidAt?: string | null
  } | null
  relatedPolicy?: {
    policyId?: number | null
    policyName?: string | null
    enabled?: number | null
    autoGrantEnabled?: number | null
    updateUserName?: string | null
    lastUpdate?: string | null
  } | null
  operatorLogSummary?: {
    totalCount?: number | null
    recentLogs?: ReferralEligibilityOperatorLog[] | null
  } | null
}

export interface ReferralEligibilityOperatorLog {
  operationLogId?: number | null
  adminUserId?: number | null
  adminUserName?: string | null
  operationCode?: string | null
  operationResult?: number | null
  beforeSnapshotJson?: string | null
  afterSnapshotJson?: string | null
  extraContextJson?: string | null
  createTime?: string | null
}

export interface ReferralEligibilityGrantPayload {
  userId: number
  grantType: string
  grantCode: string
  effectiveTime?: string
  expireTime?: string
  sourceType: string
  sourceRefId?: number
  remark?: string
}

export interface ReferralEligibilityRevokePayload {
  grantId: number
  remark?: string
}

export interface ReferralEligibilityExtendPayload {
  grantId: number
  expireTime?: string
  remark?: string
}

export type ReferralEligibilityPageResult = PageResult<ReferralEligibilityItem>
