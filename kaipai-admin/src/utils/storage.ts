import type { AdminSessionInfo } from '@/types/admin'

const TOKEN_KEY = 'kaipai-admin-token'
const SESSION_KEY = 'kaipai-admin-session'

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY) ?? ''
}

export function setStoredToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearStoredToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export function getStoredSession() {
  const raw = localStorage.getItem(SESSION_KEY)
  if (!raw) {
    return null
  }
  try {
    return JSON.parse(raw) as AdminSessionInfo
  } catch {
    localStorage.removeItem(SESSION_KEY)
    return null
  }
}

export function setStoredSession(session: AdminSessionInfo) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

export function clearStoredSession() {
  localStorage.removeItem(SESSION_KEY)
}

export function getToken() {
  return getStoredToken()
}

export function setToken(token: string) {
  setStoredToken(token)
}

export function clearToken() {
  clearStoredToken()
}
