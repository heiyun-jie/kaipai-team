import request from '@/utils/request'
import type {
  RefundApprovePayload,
  RefundOrderDetail,
  RefundOrderPageResult,
  RefundOrderQuery,
  RefundRejectPayload,
} from '@/types/refund'

export function fetchRefundOrders(params: RefundOrderQuery) {
  return request.get('/admin/refund/orders', { params }).then((data) => data as unknown as RefundOrderPageResult)
}

export function fetchRefundOrderDetail(id: number) {
  return request.get(`/admin/refund/orders/${id}`).then((data) => data as unknown as RefundOrderDetail)
}

export function approveRefundOrder(id: number, payload: RefundApprovePayload) {
  return request.post(`/admin/refund/${id}/approve`, payload)
}

export function rejectRefundOrder(id: number, payload: RefundRejectPayload) {
  return request.post(`/admin/refund/${id}/reject`, payload)
}
