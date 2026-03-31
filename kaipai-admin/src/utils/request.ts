import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types/common'
import { clearStoredSession, clearStoredToken, getStoredToken } from './storage'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
})

let authExpiredHandler: (() => void) | null = null

export function registerAuthExpiredHandler(handler: () => void) {
  authExpiredHandler = handler
}

request.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response): any => {
    const payload = response.data as ApiResponse<unknown>
    if (payload.code !== 200) {
      if (payload.code === 401 || payload.code === 403) {
        clearStoredToken()
        clearStoredSession()
        authExpiredHandler?.()
      }
      ElMessage.error(payload.message || '请求失败')
      return Promise.reject(new Error(payload.message || 'Request failed'))
    }
    return payload.data
  },
  (error) => {
    const status = error.response?.status
    if (status === 401 || status === 403) {
      clearStoredToken()
      clearStoredSession()
      authExpiredHandler?.()
    }
    ElMessage.error(error.response?.data?.message || error.message || '网络异常')
    return Promise.reject(error)
  },
)

export default request
