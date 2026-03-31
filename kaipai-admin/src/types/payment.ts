import type { PageResult } from './common'

export interface PaymentOrderQuery {
  pageNo: number
  pageSize: number
  orderNo?: string
  userId?: number
  phone?: string
  payStatus?: number
  payChannel?: string
  bizType?: string
  productId?: number
  createdAtFrom?: string
  createdAtTo?: string
  paidAtFrom?: string
  paidAtTo?: string
}

export interface PaymentOrderListItem {
  paymentOrderId: number
  orderNo: string
  userId?: number | null
  phone?: string | null
  bizType?: string | null
  bizRefId?: number | null
  productId?: number | null
  productCode?: string | null
  productName?: string | null
  amount?: number | string | null
  currencyCode?: string | null
  payStatus?: number | null
  payChannel?: string | null
  createTime?: string | null
  paidAt?: string | null
  closedAt?: string | null
}

export interface PaymentOrderDetail {
  orderInfo?: {
    paymentOrderId?: number | null
    orderNo?: string | null
    userId?: number | null
    phone?: string | null
    bizType?: string | null
    bizRefId?: number | null
    productId?: number | null
    amount?: number | string | null
    currencyCode?: string | null
    payStatus?: number | null
    payChannel?: string | null
    createTime?: string | null
    paidAt?: string | null
    closedAt?: string | null
    lastUpdate?: string | null
  } | null
  productInfo?: {
    productId?: number | null
    productCode?: string | null
    productName?: string | null
    membershipTier?: number | null
    durationDays?: number | null
  } | null
  paymentInfo?: {
    transactionCount?: number | null
    transactions?: PaymentTransactionListItem[]
  } | null
  refundSummary?: {
    totalRefundCount?: number | null
    totalRefundAmount?: number | string | null
    latestRefundOrderId?: number | null
    latestRefundNo?: string | null
    latestAuditStatus?: number | null
    latestRefundStatus?: number | null
    latestAuditedAt?: string | null
    latestRefundedAt?: string | null
  } | null
}

export interface PaymentTransactionQuery {
  pageNo: number
  pageSize: number
  paymentOrderNo?: string
  channelTradeNo?: string
  channel?: string
  status?: number
  callbackFrom?: string
  callbackTo?: string
}

export interface PaymentTransactionListItem {
  transactionId: number
  paymentOrderId?: number | null
  paymentOrderNo?: string | null
  channelTradeNo?: string | null
  channel?: string | null
  tradeType?: string | null
  amount?: number | string | null
  status?: number | null
  callbackTime?: string | null
  createTime?: string | null
}

export interface PaymentTransactionDetail {
  transactionInfo?: {
    transactionId?: number | null
    paymentOrderId?: number | null
    paymentOrderNo?: string | null
    userId?: number | null
    bizType?: string | null
    bizRefId?: number | null
    productId?: number | null
    productCode?: string | null
    productName?: string | null
    payChannel?: string | null
    payStatus?: number | null
    orderAmount?: number | string | null
    currencyCode?: string | null
    paidAt?: string | null
    channelTradeNo?: string | null
    channel?: string | null
    tradeType?: string | null
    amount?: number | string | null
    status?: number | null
    callbackTime?: string | null
    createTime?: string | null
    lastUpdate?: string | null
  } | null
  callbackPayloadSummary?: {
    hasPayload?: boolean | null
    payloadLength?: number | null
    payloadPreview?: string | null
    callbackTime?: string | null
  } | null
}

export type PaymentOrderPageResult = PageResult<PaymentOrderListItem>
export type PaymentTransactionPageResult = PageResult<PaymentTransactionListItem>
