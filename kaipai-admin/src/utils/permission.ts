import type { AdminMenuItem } from '@/types/admin'

export function hasPermission(source: string[], target?: string, fallbacks: string[] = []) {
  if (!target && !fallbacks.length) {
    return true
  }
  const candidates = [target, ...fallbacks].filter(Boolean) as string[]
  if (!candidates.length) {
    return true
  }
  return candidates.some((code) => source.includes(code))
}

export function filterMenus(menus: AdminMenuItem[], permissions: string[]): AdminMenuItem[] {
  return menus
    .map((item): AdminMenuItem | null => {
      const visibleByMenu = !item.menuPermission || permissions.includes(item.menuPermission)
      const visibleByPage = hasPermission(permissions, item.pagePermission, item.pagePermissionFallbacks || [])
      const children: AdminMenuItem[] | undefined = item.children ? filterMenus(item.children, permissions) : undefined
      const visible =
        visibleByMenu &&
        (visibleByPage || Boolean(children?.length) || (!item.pagePermission && Boolean(item.route)))

      if (!visible) {
        return null
      }

      return {
        ...item,
        children,
      }
    })
    .filter((item): item is AdminMenuItem => Boolean(item))
}
