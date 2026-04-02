import { computed } from 'vue'
import { defineStore } from 'pinia'
import { adminMenus } from '@/constants/menus'
import { useAuthStore } from './auth'
import { filterMenus, hasPermission } from '@/utils/permission'

export const usePermissionStore = defineStore('permission', () => {
  const authStore = useAuthStore()

  const menus = computed(() => filterMenus(adminMenus, authStore.permissionSet))
  const landingPath = computed(() => {
    const first = menus.value[0]
    if (!first) {
      return '/dashboard/index'
    }
    return first.route || first.children?.[0]?.route || '/dashboard/index'
  })

  function canAccess(permission?: string, fallbackPermissions: string[] = []) {
    return hasPermission(authStore.permissionSet, permission, fallbackPermissions)
  }

  function hasAction(permission?: string, fallbackPermissions: string[] = []) {
    return canAccess(permission, fallbackPermissions)
  }

  function hasPage(permission?: string, fallbackPermissions: string[] = []) {
    return canAccess(permission, fallbackPermissions)
  }

  return {
    menus,
    landingPath,
    canAccess,
    hasAction,
    hasPage,
  }
})
