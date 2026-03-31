import request from '@/utils/request'
import type {
  AdminOperationLogDetail,
  AdminOperationLogPageResult,
  AdminOperationLogQuery,
  AdminRoleCopyPayload,
  AdminRoleItem,
  AdminRoleSavePayload,
  AdminRoleStatusChangePayload,
  AdminRolePageResult,
  AdminRoleQuery,
  AdminUserBindRolesPayload,
  AdminUserCreatePayload,
  AdminUserDetail,
  AdminUserPageResult,
  AdminUserPasswordResetPayload,
  AdminUserQuery,
  AdminUserStatusPayload,
  AdminUserUpdatePayload,
} from '@/types/system'

export function fetchAdminUsers(params: AdminUserQuery) {
  return request.get('/admin/system/admin-users', { params }).then((data) => data as unknown as AdminUserPageResult)
}

export function fetchAdminUserDetail(id: number) {
  return request.get(`/admin/system/admin-users/${id}`).then((data) => data as unknown as AdminUserDetail)
}

export function createAdminUser(payload: AdminUserCreatePayload) {
  return request.post('/admin/system/admin-users', payload).then((data) => data as unknown as AdminUserDetail)
}

export function updateAdminUser(id: number, payload: AdminUserUpdatePayload) {
  return request.put(`/admin/system/admin-users/${id}`, payload).then((data) => data as unknown as AdminUserDetail)
}

export function enableAdminUser(id: number, payload: AdminUserStatusPayload) {
  return request.post(`/admin/system/admin-users/${id}/enable`, payload)
}

export function disableAdminUser(id: number, payload: AdminUserStatusPayload) {
  return request.post(`/admin/system/admin-users/${id}/disable`, payload)
}

export function resetAdminUserPassword(id: number, payload: AdminUserPasswordResetPayload) {
  return request.post(`/admin/system/admin-users/${id}/reset-password`, payload).then((data) => data as unknown as AdminUserDetail)
}

export function bindAdminUserRoles(id: number, payload: AdminUserBindRolesPayload) {
  return request.post(`/admin/system/admin-users/${id}/bind-roles`, payload).then((data) => data as unknown as AdminUserDetail)
}

export function fetchAdminRoles(params: AdminRoleQuery) {
  return request.get('/admin/system/roles', { params }).then((data) => data as unknown as AdminRolePageResult)
}

export function fetchAdminRoleDetail(id: number) {
  return request.get(`/admin/system/roles/${id}`).then((data) => data as unknown as AdminRoleItem)
}

export function createAdminRole(payload: AdminRoleSavePayload) {
  return request.post('/admin/system/roles', payload).then((data) => data as unknown as AdminRoleItem)
}

export function updateAdminRole(id: number, payload: AdminRoleSavePayload) {
  return request.put(`/admin/system/roles/${id}`, payload).then((data) => data as unknown as AdminRoleItem)
}

export function enableAdminRole(id: number, payload: AdminRoleStatusChangePayload) {
  return request.post(`/admin/system/roles/${id}/enable`, payload).then((data) => data as unknown as AdminRoleItem)
}

export function disableAdminRole(id: number, payload: AdminRoleStatusChangePayload) {
  return request.post(`/admin/system/roles/${id}/disable`, payload).then((data) => data as unknown as AdminRoleItem)
}

export function copyAdminRole(id: number, payload: AdminRoleCopyPayload) {
  return request.post(`/admin/system/roles/${id}/copy`, payload).then((data) => data as unknown as AdminRoleItem)
}

export function fetchAdminOperationLogs(params: AdminOperationLogQuery) {
  return request.get('/admin/system/operation-logs', { params }).then((data) => data as unknown as AdminOperationLogPageResult)
}

export function fetchAdminOperationLogDetail(id: number) {
  return request.get(`/admin/system/operation-logs/${id}`).then((data) => data as unknown as AdminOperationLogDetail)
}
