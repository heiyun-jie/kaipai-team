export interface DashboardOverviewQuery {
  dateFrom?: string
  dateTo?: string
  bizLine?: string
}

export interface DashboardRecentItem {
  bizLine: string
  itemType: string
  itemId: number
  userId?: number | null
  referenceNo?: string | null
  title: string
  status?: number | null
  occurredAt?: string | null
}

export interface DashboardOverview {
  verifyPendingCount?: number | null
  referralRiskPendingCount?: number | null
  refundPendingCount?: number | null
  todayPaymentOrderCount?: number | null
  recentItems: DashboardRecentItem[]
}
