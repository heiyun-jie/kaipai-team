import request from '@/utils/request'
import type {
  AdminAiResumeHistoryItem,
  AdminAiResumeHistoryPageResult,
  AdminAiResumeHistoryQuery,
  AdminAiResumeOverview,
} from '@/types/ai'

export function fetchAdminAiResumeOverview() {
  return request.get('/admin/ai/resume/overview').then((data) => data as unknown as AdminAiResumeOverview)
}

export function fetchAdminAiResumeHistories(params: AdminAiResumeHistoryQuery) {
  return request.get('/admin/ai/resume/histories', { params }).then((data) => data as unknown as AdminAiResumeHistoryPageResult)
}

export function fetchAdminAiResumeHistoryDetail(historyId: string) {
  return request.get(`/admin/ai/resume/histories/${historyId}`).then((data) => data as unknown as AdminAiResumeHistoryItem)
}
