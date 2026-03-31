import request from '@/utils/request'
import type { DashboardOverview, DashboardOverviewQuery } from '@/types/dashboard'

export function fetchDashboardOverview(params?: DashboardOverviewQuery) {
  return request.get('/admin/dashboard/overview', { params }).then((data) => data as unknown as DashboardOverview)
}
