import type { PageResult } from './common'

export interface AdminRoleBrief {
  adminRoleId: number
  roleCode: string
  roleName: string
  status: number
}

export interface AdminUserQuery {
  pageNo: number
  pageSize: number
  account?: string
  userName?: string
  phone?: string
  status?: number
  roleCode?: string
}

export interface AdminUserListItem {
  adminUserId: number
  account: string
  userName: string
  phone?: string | null
  email?: string | null
  status: number
  lastLoginTime?: string | null
  lastLoginIp?: string | null
  createTime?: string | null
  roles: AdminRoleBrief[]
}

export interface AdminUserDetail {
  adminUserId: number
  account: string
  userName: string
  phone?: string | null
  email?: string | null
  status: number
  lastLoginTime?: string | null
  lastLoginIp?: string | null
  createUserName?: string | null
  createTime?: string | null
  updateUserName?: string | null
  lastUpdate?: string | null
  roles: AdminRoleBrief[]
}

export interface AdminUserCreatePayload {
  account: string
  password: string
  userName: string
  phone?: string
  email?: string
  roleCodes: string[]
}

export interface AdminUserUpdatePayload {
  account: string
  userName: string
  phone?: string
  email?: string
}

export interface AdminUserStatusPayload {
  status?: number
  reason?: string
}

export interface AdminUserPasswordResetPayload {
  newPassword: string
  credentialDeliveryMode?: string
  reason?: string
  resetResult?: string
}

export interface AdminUserBindRolesPayload {
  roleCodes: string[]
  reason?: string
}

export interface AdminRoleQuery {
  pageNo: number
  pageSize: number
  roleCode?: string
  roleName?: string
  status?: number
}

export interface AdminRoleItem {
  adminRoleId: number
  roleCode: string
  roleName: string
  status: number
  remark?: string | null
  menuPermissions?: string[]
  pagePermissions?: string[]
  actionPermissions?: string[]
  createUserName?: string | null
  createTime?: string | null
  updateUserName?: string | null
  lastUpdate?: string | null
}

export type AdminUserPageResult = PageResult<AdminUserListItem>
export type AdminRolePageResult = PageResult<AdminRoleItem>
