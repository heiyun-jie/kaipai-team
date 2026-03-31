import type { Router } from 'vue-router';
import type { Pinia } from 'pinia';
import { useAuthStore } from '@/stores/auth';
import { usePermissionStore } from '@/stores/permission';

const WHITE_LIST = new Set(['/login']);

export function installRouterGuard(router: Router, pinia: Pinia) {
  router.beforeEach(async (to) => {
    const authStore = useAuthStore(pinia);
    const permissionStore = usePermissionStore(pinia);

    document.title = to.meta.title ? `${to.meta.title} | 开拍了后台` : '开拍了后台';

    if (!authStore.initialized) {
      await authStore.bootstrap();
    }

    if (WHITE_LIST.has(to.path)) {
      if (authStore.isAuthenticated) {
        return permissionStore.landingPath || '/dashboard/index';
      }
      return true;
    }

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      return {
        path: '/login',
        query: {
          redirect: to.fullPath,
        },
      };
    }

    const pageCode = (to.meta.pageCode || to.meta.pagePermission) as string | undefined;
    if (pageCode && !permissionStore.hasPage(pageCode)) {
      return '/403';
    }

    return true;
  });
}
