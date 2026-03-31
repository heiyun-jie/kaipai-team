import type { PageResult } from './common'

export interface RefundOrderQuery {
  pageNo: number
  pageSize: number
  refundNo?: string
  paymentOrderNo?: string
  userId?: number
  auditStatus?: number
  refundStatus?: number
  createdAtFrom?: string
  createdAtTo?: string
  auditedAtFrom?: string
  auditedAtTo?: string
}

export interface RefundOrderItem {
  refundOrderId: number
  refundNo: string
  paymentOrderId?: number | null
  userId?: number | null
  refundAmount?: number | string | null
  auditStatus?: number | null
  refundStatus?: number | null
  refundReason?: string | null
  auditRemark?: string | null
  auditedAt?: string | null
  channelRefundNo?: string | null
  refundedAt?: string | null
}

export interface RefundOperateLogItem {
  logId?: number | null
  refundOrderId?: number | null
  operatorId?: number | null
  actionType?: string | null
  remark?: string | null
  createTime?: string | null
}

export interface RefundOrderDetail {
  refundOrderId: number
  refundNo: string
  paymentOrderId?: number | null
  paymentOrderNo?: string | null
  userId?: number | null
  refundAmount?: number | string | null
  refundReason?: string | null
  auditStatus?: number | null
  refundStatus?: number | null
  auditRemark?: string | null
  auditorId?: number | null
  auditedAt?: string | null
  channelRefundNo?: string | null
  refundedAt?: string | null
  paymentAmount?: number | string | null
  paymentStatus?: number | null
  payChannel?: string | null
  paidAt?: string | null
  operateLogs?: RefundOperateLogItem[]
}

export interface RefundApprovePayload {
  auditRemark?: string
}

export interface RefundRejectPayload {
  auditRemark: string
}

export interface RefundOperateLogQuery {
  pageNo: number
  pageSize: number
  refundOrderId?: number
  refundNo?: string
  operatorId?: number
  actionType?: string
  dateFrom?: string
  dateTo?: string
}

export type RefundOrderPageResult = PageResult<RefundOrderItem>
export type RefundOperateLogPageResult = PageResult<RefundOperateLogItem>
