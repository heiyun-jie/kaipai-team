import request from '@/utils/request'
import type { AdminLoginResponse, AdminSessionInfo } from '@/types/admin'

export function loginAdmin(payload: { account: string; password: string }) {
  return request.post('/admin/auth/login', payload).then((data) => data as unknown as AdminLoginResponse)
}

export function fetchAdminSession() {
  return request.get('/admin/auth/me').then((data) => data as unknown as AdminSessionInfo)
}
