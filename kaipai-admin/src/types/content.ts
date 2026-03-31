import type { PageResult } from './common'

export interface TemplateListQuery {
  sceneKey?: string
  status?: number
  tier?: string
  pageNo: number
  pageSize: number
}

export interface TemplateItem {
  templateId: number
  templateCode: string
  sceneKey: string
  templateName: string
  tier?: string
  requiredLevel?: number
  membershipRequired?: boolean
  status: number
  sortNo?: number
  updateTime?: string
}

export interface TemplateCreatePayload {
  templateCode: string
  sceneKey: string
  templateName: string
  description?: string
  layoutVariant?: string
  tier?: string
  requiredLevel?: number
  membershipRequired?: boolean
  baseThemeJson?: string
  artifactPresetJson?: string
}

export interface TemplateUpdatePayload extends Partial<TemplateCreatePayload> {
  status?: number
  sortNo?: number
}

export interface TemplatePublishPayload {
  publishVersion?: string
  publishNote?: string
}

export interface TemplateRollbackPayload {
  sourceVersion: string
  publishNote?: string
}

export type TemplatePageResult = PageResult<TemplateItem>
export type TemplateQuery = TemplateListQuery
export type CreateTemplatePayload = TemplateCreatePayload
export type UpdateTemplatePayload = TemplateUpdatePayload
export type PublishTemplatePayload = TemplatePublishPayload
export type RollbackTemplatePayload = TemplateRollbackPayload
