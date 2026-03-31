import type { PageResult } from './common'

export interface VerifyListQuery {
  userId?: number
  status?: number
  pageNo: number
  pageSize: number
}

export interface VerifyListItem {
  verificationId: number
  userId: number
  userName?: string
  phone?: string
  realName: string
  status: number
  submitTime?: string
}

export interface VerifyDetail {
  verificationId: number
  userId: number
  userName?: string
  phone?: string
  realName: string
  idCardNoCipher: string
  status: number
  rejectReason?: string
  submitTime?: string
  reviewedAt?: string
  actorCertified?: boolean
}

export interface VerifyAuditPayload {
  remark: string
}

export type VerifyPageResult = PageResult<VerifyListItem>
export type VerifyQuery = VerifyListQuery
