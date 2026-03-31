import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { fetchAdminSession, loginAdmin } from '@/api/auth'
import type { AdminSessionInfo } from '@/types/admin'
import {
  clearStoredSession,
  clearStoredToken,
  getStoredSession,
  getStoredToken,
  setStoredSession,
  setStoredToken,
} from '@/utils/storage'
import { registerAuthExpiredHandler } from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(getStoredToken())
  const session = ref<AdminSessionInfo | null>(getStoredSession())
  const initialized = ref(false)

  const isAuthed = computed(() => Boolean(token.value))
  const isAuthenticated = computed(() => Boolean(token.value))
  const permissionSet = computed(() => [
    ...(session.value?.menuPermissions ?? []),
    ...(session.value?.pagePermissions ?? []),
    ...(session.value?.actionPermissions ?? []),
  ])

  function applySession(nextToken: string, nextSession: AdminSessionInfo) {
    token.value = nextToken
    session.value = nextSession
    setStoredToken(nextToken)
    setStoredSession(nextSession)
  }

  async function login(account: string, password: string) {
    const result = await loginAdmin({ account, password })
    applySession(result.accessToken, result.adminUserInfo)
    initialized.value = true
  }

  async function signIn(payload: { account: string; password: string }) {
    await login(payload.account, payload.password)
    return session.value
  }

  async function bootstrap() {
    registerAuthExpiredHandler(() => logout())

    if (!token.value) {
      initialized.value = true
      return
    }

    try {
      session.value = await fetchAdminSession()
    } catch {
      logout()
    } finally {
      initialized.value = true
    }
  }

  function logout() {
    token.value = ''
    session.value = null
    clearStoredToken()
    clearStoredSession()
  }

  return {
    token,
    session,
    initialized,
    isAuthed,
    isAuthenticated,
    permissionSet,
    login,
    signIn,
    bootstrap,
    logout,
  }
})
