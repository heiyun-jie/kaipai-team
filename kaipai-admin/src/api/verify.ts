import request from '@/utils/request'
import type { VerifyAuditPayload, VerifyDetail, VerifyListQuery, VerifyPageResult } from '@/types/verify'

export function fetchVerifyList(params: VerifyListQuery) {
  return request.get('/admin/verify/list', { params }).then((data) => data as unknown as VerifyPageResult)
}

export function fetchVerifyDetail(id: number) {
  return request.get(`/admin/verify/${id}`).then((data) => data as unknown as VerifyDetail)
}

export function approveVerify(id: number, payload: VerifyAuditPayload) {
  return request.post(`/admin/verify/${id}/approve`, payload)
}

export function rejectVerify(id: number, payload: VerifyAuditPayload) {
  return request.post(`/admin/verify/${id}/reject`, payload)
}
