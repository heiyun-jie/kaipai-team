import type { PageResult } from './common'

export interface AdminRecruitProjectQuery {
  pageNo: number
  pageSize: number
  projectId?: number
  crewUserId?: number
  status?: number
  keyword?: string
  location?: string
}

export interface AdminRecruitProjectItem {
  projectId: number
  crewUserId: number
  companyProfileId?: number | null
  companyName?: string | null
  contactName?: string | null
  contactPhone?: string | null
  title?: string | null
  description?: string | null
  location?: string | null
  status?: number | null
  type?: string | null
  shootingDate?: string | null
  roleCount?: number | null
  coverImage?: string | null
  sourceUpdatedAt?: string | null
  sourceCreatedAt?: string | null
}

export interface AdminRecruitProjectStatusPayload {
  status: 1 | 2
  reason?: string
}

export interface AdminRecruitRoleQuery {
  pageNo: number
  pageSize: number
  roleId?: number
  crewUserId?: number
  projectId?: number
  status?: 'recruiting' | 'paused' | 'closed' | ''
  keyword?: string
}

export interface AdminRecruitRoleItem {
  roleId: number
  crewUserId: number
  companyProfileId?: number | null
  projectId?: number | null
  projectTitle?: string | null
  companyName?: string | null
  roleName?: string | null
  gender?: string | null
  minAge?: number | null
  maxAge?: number | null
  requirement?: string | null
  fee?: string | null
  status?: 'recruiting' | 'paused' | 'closed' | string | null
  deadline?: string | null
  applyCount?: number | null
  location?: string | null
  contactName?: string | null
  contactPhone?: string | null
  publishTime?: string | null
  coverImage?: string | null
  tags?: string[]
}

export interface AdminRecruitRoleStatusPayload {
  status: 'recruiting' | 'paused' | 'closed'
  reason?: string
}

export interface AdminRecruitApplyQuery {
  pageNo: number
  pageSize: number
  applyId?: number
  roleId?: number
  actorUserId?: number
  crewUserId?: number
  status?: number
  keyword?: string
}

export interface AdminRecruitApplyItem {
  applyId: number
  roleId: number
  actorUserId: number
  crewUserId: number
  projectId?: number | null
  projectTitle?: string | null
  companyName?: string | null
  roleName?: string | null
  roleStatus?: 'recruiting' | 'paused' | 'closed' | string | null
  actorName?: string | null
  actorPhone?: string | null
  actorAvatar?: string | null
  status?: number | null
  remark?: string | null
  applyTime?: string | null
}

export type AdminRecruitProjectPageResult = PageResult<AdminRecruitProjectItem>
export type AdminRecruitRolePageResult = PageResult<AdminRecruitRoleItem>
export type AdminRecruitApplyPageResult = PageResult<AdminRecruitApplyItem>
