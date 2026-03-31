import type { RouteRecordRaw } from 'vue-router';

export const staticRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: {
      title: '后台登录',
    },
  },
  {
    path: '/403',
    name: 'forbidden',
    component: () => import('@/views/common/ForbiddenView.vue'),
    meta: {
      title: '无权访问',
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/shared/NotFoundView.vue'),
    meta: {
      title: '页面不存在',
    },
  },
];
