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

  function canAccess(permission?: string) {
    return hasPermission(authStore.permissionSet, permission)
  }

  function hasAction(permission?: string) {
    return canAccess(permission)
  }

  function hasPage(permission?: string) {
    return canAccess(permission)
  }

  return {
    menus,
    landingPath,
    canAccess,
    hasAction,
    hasPage,
  }
})

