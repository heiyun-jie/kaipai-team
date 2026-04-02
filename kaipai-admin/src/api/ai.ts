import request from '@/utils/request'
import type {
  AdminAiResumeFailureActionPayload,
  AdminAiResumeFailureItem,
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

export function fetchAdminAiResumeFailures() {
  return request.get('/admin/ai/resume/failures').then((data) => data as unknown as AdminAiResumeFailureItem[])
}

export function fetchAdminAiResumeSensitiveHits() {
  return request.get('/admin/ai/resume/sensitive-hits').then((data) => data as unknown as AdminAiResumeFailureItem[])
}

export function reviewAdminAiResumeFailure(failureId: string, payload: AdminAiResumeFailureActionPayload) {
  return request.post(`/admin/ai/resume/failures/${failureId}/review`, payload).then((data) => data as unknown as AdminAiResumeFailureItem)
}

export function suggestRetryAdminAiResumeFailure(failureId: string, payload: AdminAiResumeFailureActionPayload) {
  return request.post(`/admin/ai/resume/failures/${failureId}/suggest-retry`, payload).then((data) => data as unknown as AdminAiResumeFailureItem)
}
