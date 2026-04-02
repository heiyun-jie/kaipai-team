import type { PageResult } from './common'

export interface AdminAiResumePatch {
  patchId: string
  fieldType: string
  fieldKey: string
  label: string
  targetId?: string | null
  beforeValue?: string | null
  afterValue?: string | null
  reason?: string | null
  status?: string | null
}

export interface AdminAiResumeFieldSnapshot {
  fieldKey: string
  value?: string | null
}

export interface AdminAiResumeHistoryItem {
  historyId: string
  userId: number
  userName: string
  phone?: string | null
  realAuthStatus?: number | null
  level?: number | null
  membershipTier?: string | null
  draftId: string
  requestId: string
  conversationId: string
  instruction: string
  reply: string
  status: string
  patchCount: number
  patches: AdminAiResumePatch[]
  beforeSnapshot: AdminAiResumeFieldSnapshot[]
  afterSnapshot: AdminAiResumeFieldSnapshot[]
  createdAt?: string | null
  appliedAt?: string | null
  rolledBackAt?: string | null
}

export interface AdminAiResumeFailureItem {
  failureId: string
  userId: number
  userName: string
  phone?: string | null
  realAuthStatus?: number | null
  level?: number | null
  membershipTier?: string | null
  requestId?: string | null
  conversationId?: string | null
  instruction?: string | null
  errorCode?: number | null
  errorMessage?: string | null
  failureType?: string | null
  hitKeyword?: string | null
  handlingStatus?: string | null
  handlingNote?: string | null
  handledByAdminId?: number | null
  handledByAdminName?: string | null
  handledAt?: string | null
  createdAt?: string | null
}

export interface AdminAiResumeFailureActionPayload {
  reason?: string
}

export interface AdminAiResumeQuotaUser {
  userId: number
  userName: string
  phone?: string | null
  realAuthStatus?: number | null
  level?: number | null
  membershipTier?: string | null
  totalQuota?: number | null
  usedCount: number
}

export interface AdminAiResumeOverview {
  totalHistoryCount: number
  appliedHistoryCount: number
  rolledBackHistoryCount: number
  historyUserCount: number
  currentMonthHistoryCount: number
  currentMonthQuotaUserCount: number
  currentMonthQuotaUsageTotal: number
  topQuotaUsers: AdminAiResumeQuotaUser[]
  recentHistories: AdminAiResumeHistoryItem[]
}

export interface AdminAiResumeHistoryQuery {
  pageNo: number
  pageSize: number
  userId?: number
  status?: string
  keyword?: string
  requestId?: string
}

export type AdminAiResumeHistoryPageResult = PageResult<AdminAiResumeHistoryItem>
