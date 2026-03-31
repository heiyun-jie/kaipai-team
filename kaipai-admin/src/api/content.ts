import request from '@/utils/request'
import type {
  TemplateCreatePayload,
  TemplateListQuery,
  TemplatePageResult,
  TemplatePublishPayload,
  TemplateRollbackPayload,
  TemplateUpdatePayload,
} from '@/types/content'

export function fetchTemplates(params: TemplateListQuery) {
  return request.get('/admin/content/templates', { params }).then((data) => data as unknown as TemplatePageResult)
}

export function createTemplate(payload: TemplateCreatePayload) {
  return request.post('/admin/content/templates', payload)
}

export function updateTemplate(id: number, payload: TemplateUpdatePayload) {
  return request.put(`/admin/content/templates/${id}`, payload)
}

export function publishTemplate(id: number, payload: TemplatePublishPayload) {
  return request.post(`/admin/content/templates/${id}/publish`, payload)
}

export function rollbackTemplate(id: number, payload: TemplateRollbackPayload) {
  return request.post(`/admin/content/templates/${id}/rollback`, payload)
}
