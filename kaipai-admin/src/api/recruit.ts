import request from '@/utils/request'
import type {
  AdminRecruitApplyPageResult,
  AdminRecruitApplyQuery,
  AdminRecruitProjectPageResult,
  AdminRecruitProjectQuery,
  AdminRecruitProjectStatusPayload,
  AdminRecruitRolePageResult,
  AdminRecruitRoleQuery,
  AdminRecruitRoleStatusPayload,
} from '@/types/recruit'

function sanitizeRecruitQuery<T extends object>(params: T): Partial<T> {
  return Object.fromEntries(
    Object.entries(params as Record<string, unknown>).filter(([, value]) => {
      if (value === undefined || value === null || value === '') {
        return false
      }
      if (typeof value === 'number' && Number.isNaN(value)) {
        return false
      }
      return true
    }),
  ) as Partial<T>
}

export function fetchAdminRecruitProjects(params: AdminRecruitProjectQuery) {
  return request
    .get('/admin/recruit/projects', { params: sanitizeRecruitQuery(params) })
    .then((data) => data as unknown as AdminRecruitProjectPageResult)
}

export function fetchAdminRecruitRoles(params: AdminRecruitRoleQuery) {
  return request
    .get('/admin/recruit/roles', { params: sanitizeRecruitQuery(params) })
    .then((data) => data as unknown as AdminRecruitRolePageResult)
}

export function fetchAdminRecruitApplies(params: AdminRecruitApplyQuery) {
  return request
    .get('/admin/recruit/applies', { params: sanitizeRecruitQuery(params) })
    .then((data) => data as unknown as AdminRecruitApplyPageResult)
}

export function updateAdminRecruitProjectStatus(projectId: number, payload: AdminRecruitProjectStatusPayload) {
  return request.post(`/admin/recruit/projects/${projectId}/status`, payload)
}

export function updateAdminRecruitRoleStatus(roleId: number, payload: AdminRecruitRoleStatusPayload) {
  return request.post(`/admin/recruit/roles/${roleId}/status`, payload)
}
