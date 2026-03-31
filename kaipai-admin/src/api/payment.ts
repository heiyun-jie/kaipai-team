import request from '@/utils/request'
import type {
  PaymentOrderDetail,
  PaymentOrderPageResult,
  PaymentOrderQuery,
  PaymentTransactionDetail,
  PaymentTransactionPageResult,
  PaymentTransactionQuery,
} from '@/types/payment'

export function fetchPaymentOrders(params: PaymentOrderQuery) {
  return request.get('/admin/payment/orders', { params }).then((data) => data as unknown as PaymentOrderPageResult)
}

export function fetchPaymentOrderDetail(id: number) {
  return request.get(`/admin/payment/orders/${id}`).then((data) => data as unknown as PaymentOrderDetail)
}

export function fetchPaymentTransactions(params: PaymentTransactionQuery) {
  return request.get('/admin/payment/transactions', { params }).then((data) => data as unknown as PaymentTransactionPageResult)
}

export function fetchPaymentTransactionDetail(id: number) {
  return request.get(`/admin/payment/transactions/${id}`).then((data) => data as unknown as PaymentTransactionDetail)
}
