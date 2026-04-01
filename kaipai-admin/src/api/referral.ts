import request from '@/utils/request'
import type {
  ReferralEligibilityDetail,
  ReferralEligibilityExtendPayload,
  ReferralEligibilityGrantPayload,
  ReferralEligibilityPageResult,
  ReferralEligibilityQuery,
  ReferralEligibilityRevokePayload,
  ReferralPolicyDetail,
  ReferralPolicyPageResult,
  ReferralPolicyQuery,
  ReferralPolicySavePayload,
  ReferralPolicyStatusPayload,
  ReferralRecordDetail,
  ReferralRecordPageResult,
  ReferralRecordQuery,
  ReferralRiskDecisionPayload,
  ReferralRiskDetail,
  ReferralRiskPageResult,
  ReferralRiskQuery,
} from '@/types/referral'

export function fetchReferralRecords(params: ReferralRecordQuery) {
  return request.get('/admin/referral/records', { params }).then((data) => data as unknown as ReferralRecordPageResult)
}

export function fetchReferralRecordDetail(id: number) {
  return request.get(`/admin/referral/records/${id}`).then((data) => data as unknown as ReferralRecordDetail)
}

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

export function fetchReferralPolicies(params: ReferralPolicyQuery) {
  return request.get('/admin/referral/policies', { params }).then((data) => data as unknown as ReferralPolicyPageResult)
}

export function fetchReferralPolicyDetail(id: number) {
  return request.get(`/admin/referral/policies/${id}`).then((data) => data as unknown as ReferralPolicyDetail)
}

export function createReferralPolicy(payload: ReferralPolicySavePayload) {
  return request.post('/admin/referral/policies', payload).then((data) => data as unknown as ReferralPolicyDetail)
}

export function updateReferralPolicy(id: number, payload: ReferralPolicySavePayload) {
  return request.put(`/admin/referral/policies/${id}`, payload).then((data) => data as unknown as ReferralPolicyDetail)
}

export function enableReferralPolicy(id: number, payload: ReferralPolicyStatusPayload) {
  return request.post(`/admin/referral/policies/${id}/enable`, payload).then((data) => data as unknown as ReferralPolicyDetail)
}

export function disableReferralPolicy(id: number, payload: ReferralPolicyStatusPayload) {
  return request.post(`/admin/referral/policies/${id}/disable`, payload).then((data) => data as unknown as ReferralPolicyDetail)
}

export function fetchReferralEligibilityList(params: ReferralEligibilityQuery) {
  return request.get('/admin/referral/eligibility', { params }).then((data) => data as unknown as ReferralEligibilityPageResult)
}

export function fetchReferralEligibilityDetail(id: number) {
  return request.get(`/admin/referral/eligibility/${id}`).then((data) => data as unknown as ReferralEligibilityDetail)
}

export function grantReferralEligibility(payload: ReferralEligibilityGrantPayload) {
  return request.post('/admin/referral/eligibility/grant', payload)
}

export function revokeReferralEligibility(payload: ReferralEligibilityRevokePayload) {
  return request.post('/admin/referral/eligibility/revoke', payload)
}

export function extendReferralEligibility(payload: ReferralEligibilityExtendPayload) {
  return request.post('/admin/referral/eligibility/extend', payload)
}
