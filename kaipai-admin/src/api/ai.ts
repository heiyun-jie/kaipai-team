import request from '@/utils/request'
import type {
  AdminAiResumeFailureActionPayload,
  AdminAiResumeFailureCollaborationCatalog,
  AdminAiResumeFailureItem,
  AdminAiResumeFailureQuery,
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

export function fetchAdminAiResumeFailures(params?: AdminAiResumeFailureQuery) {
  return request.get('/admin/ai/resume/failures', { params }).then((data) => data as unknown as AdminAiResumeFailureItem[])
}

export function fetchAdminAiResumeSensitiveHits(params?: AdminAiResumeFailureQuery) {
  return request.get('/admin/ai/resume/sensitive-hits', { params }).then((data) => data as unknown as AdminAiResumeFailureItem[])
}

export function fetchAdminAiResumeFailureCollaborationCatalog() {
  return request.get('/admin/ai/resume/collaboration-catalog').then((data) => data as unknown as AdminAiResumeFailureCollaborationCatalog)
}

export function reviewAdminAiResumeFailure(failureId: string, payload: AdminAiResumeFailureActionPayload) {
  return request.post(`/admin/ai/resume/failures/${failureId}/review`, payload).then((data) => data as unknown as AdminAiResumeFailureItem)
}

export function suggestRetryAdminAiResumeFailure(failureId: string, payload: AdminAiResumeFailureActionPayload) {
  return request.post(`/admin/ai/resume/failures/${failureId}/suggest-retry`, payload).then((data) => data as unknown as AdminAiResumeFailureItem)
}

export function closeAdminAiResumeFailure(failureId: string, payload: AdminAiResumeFailureActionPayload) {
  return request.post(`/admin/ai/resume/failures/${failureId}/close`, payload).then((data) => data as unknown as AdminAiResumeFailureItem)
}

export function ignoreAdminAiResumeFailure(failureId: string, payload: AdminAiResumeFailureActionPayload) {
  return request.post(`/admin/ai/resume/failures/${failureId}/ignore`, payload).then((data) => data as unknown as AdminAiResumeFailureItem)
}

export function assignAdminAiResumeFailure(failureId: string, payload: AdminAiResumeFailureActionPayload) {
  return request.post(`/admin/ai/resume/failures/${failureId}/assign`, payload).then((data) => data as unknown as AdminAiResumeFailureItem)
}

export function escalateAdminAiResumeFailure(failureId: string, payload: AdminAiResumeFailureActionPayload) {
  return request.post(`/admin/ai/resume/failures/${failureId}/escalate`, payload).then((data) => data as unknown as AdminAiResumeFailureItem)
}
