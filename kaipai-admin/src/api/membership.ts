import request from '@/utils/request'
import type {
  MembershipAccountClosePayload,
  MembershipAccountExtendPayload,
  MembershipAccountOpenPayload,
  MembershipAccountPageResult,
  MembershipAccountQuery,
  MembershipProductCreatePayload,
  MembershipProductPageResult,
  MembershipProductQuery,
} from '@/types/membership'

export function fetchMembershipProducts(params: MembershipProductQuery) {
  return request.get('/admin/membership/products', { params }).then((data) => data as unknown as MembershipProductPageResult)
}

export function createMembershipProduct(payload: MembershipProductCreatePayload) {
  return request.post('/admin/membership/products', payload)
}

export function fetchMembershipAccounts(params: MembershipAccountQuery) {
  return request.get('/admin/membership/accounts', { params }).then((data) => data as unknown as MembershipAccountPageResult)
}

export function openMembershipAccount(userId: number, payload: MembershipAccountOpenPayload) {
  return request.post(`/admin/membership/accounts/${userId}/open`, payload)
}

export function extendMembershipAccount(userId: number, payload: MembershipAccountExtendPayload) {
  return request.post(`/admin/membership/accounts/${userId}/extend`, payload)
}

export function closeMembershipAccount(userId: number, payload: MembershipAccountClosePayload) {
  return request.post(`/admin/membership/accounts/${userId}/close`, payload)
}
