import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: {
      public: true,
      title: '后台登录',
    },
  },
  {
    path: '/',
    component: () => import('@/layouts/AdminLayout.vue'),
    redirect: '/dashboard/index',
    children: [
      {
        path: 'dashboard/index',
        name: 'dashboard',
        component: () => import('@/views/dashboard/OverviewView.vue'),
        meta: {
          title: '工作台',
          pagePermission: 'page.dashboard.index',
        },
      },
      {
        path: 'verify/pending',
        name: 'verify-pending',
        component: () => import('@/views/verify/PendingView.vue'),
        meta: {
          title: '实名认证待审核',
          pagePermission: 'page.verify.pending',
        },
      },
      {
        path: 'verify/history',
        name: 'verify-history',
        component: () => import('@/views/verify/HistoryView.vue'),
        meta: {
          title: '实名认证历史',
          pagePermission: 'page.verify.history',
        },
      },
      {
        path: 'referral/risk',
        name: 'referral-risk',
        component: () => import('@/views/referral/RiskView.vue'),
        meta: {
          title: '异常邀请',
          pagePermission: 'page.referral.risk',
        },
      },
      {
        path: 'membership/products',
        name: 'membership-products',
        component: () => import('@/views/membership/ProductsView.vue'),
        meta: {
          title: '会员产品',
          pagePermission: 'page.membership.products',
        },
      },
      {
        path: 'membership/accounts',
        name: 'membership-accounts',
        component: () => import('@/views/membership/AccountsView.vue'),
        meta: {
          title: '会员账户',
          pagePermission: 'page.membership.accounts',
        },
      },
      {
        path: 'content/templates',
        name: 'content-templates',
        component: () => import('@/views/content/TemplatesView.vue'),
        meta: {
          title: '场景模板',
          pagePermission: 'page.content.templates',
        },
      },
      {
        path: 'system/admin-users',
        name: 'system-admin-users',
        component: () => import('@/views/system/AdminUsersView.vue'),
        meta: {
          title: '后台账号',
          pagePermission: 'page.system.admin-users',
        },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('@/views/shared/NotFoundView.vue'),
    meta: {
      public: true,
      title: '页面不存在',
    },
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  const permissionStore = usePermissionStore()
  document.title = `${to.meta.title || '平台后台'} | ${import.meta.env.VITE_APP_TITLE || '开拍了平台后台'}`

  if (!to.meta.public && !authStore.isAuthed) {
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    }
  }

  if (authStore.isAuthed && !authStore.session) {
    await authStore.bootstrap()
  }

  const pagePermission = to.meta.pagePermission as string | undefined
  if (pagePermission && !permissionStore.canAccess(pagePermission)) {
    ElMessage.warning('当前账号没有该页面权限')
    return authStore.isAuthed ? '/dashboard/index' : '/login'
  }

  if (to.path === '/login' && authStore.isAuthed) {
    return '/dashboard/index'
  }

  return true
})

export default router
