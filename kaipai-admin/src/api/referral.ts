import request from '@/utils/request'
import type {
  ReferralRiskDecisionPayload,
  ReferralRiskDetail,
  ReferralRiskPageResult,
  ReferralRiskQuery,
} from '@/types/referral'

export function fetchReferralRiskList(params: ReferralRiskQuery) {
  return request.get('/admin/referral/risk/list', { params }).then((data) => data as unknown as ReferralRiskPageResult)
}

export function fetchReferralRiskDetail(id: number) {
  return request.get(`/admin/referral/risk/${id}`).then((data) => data as unknown as ReferralRiskDetail)
}

export function approveReferralRisk(id: number, payload: ReferralRiskDecisionPayload) {
  return request.post(`/admin/referral/risk/${id}/approve`, payload)
}

export function invalidateReferralRisk(id: number, payload: ReferralRiskDecisionPayload) {
  return request.post(`/admin/referral/risk/${id}/invalidate`, payload)
}

export function resolveReferralRisk(id: number, payload: ReferralRiskDecisionPayload) {
  return request.post(`/admin/referral/risk/${id}/resolve`, payload)
}
