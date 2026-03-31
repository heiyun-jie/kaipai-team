import type { AdminMenuItem } from '@/types/admin'

export function hasPermission(source: string[], target?: string) {
  if (!target) {
    return true
  }
  return source.includes(target)
}

export function filterMenus(menus: AdminMenuItem[], permissions: string[]): AdminMenuItem[] {
  return menus
    .map((item): AdminMenuItem | null => {
      const visibleByMenu = !item.menuPermission || permissions.includes(item.menuPermission)
      const visibleByPage = !item.pagePermission || permissions.includes(item.pagePermission)
      const children: AdminMenuItem[] | undefined = item.children ? filterMenus(item.children, permissions) : undefined
      const visible = visibleByMenu && (visibleByPage || Boolean(children?.length) || Boolean(item.route))

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
